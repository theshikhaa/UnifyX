import re
from typing import List, Dict, Any
from app.models.import_batch import MappingType
from app.schemas.mapping import MappingProposal, CANONICAL_FIELDS

ALIAS_RULES: Dict[str, List[str]] = {
    "email": [
        "email", "email_id", "email_address", "mail", "user_email", "contact_email"
    ],
    "phone": [
        "phone", "mobile_number", "contact_no", "telephone", "mobile", "phone_no", 
        "phone_number", "cell", "cellphone"
    ],
    "name": [
        "full_name", "name", "customer_name", "employee_name", "user_name", 
        "first_name", "last_name", "person_name"
    ],
    "member_id": [
        "employee_id", "customer_id", "member_id", "user_id", "user_code", 
        "account_id", "client_id"
    ],
    "username": [
        "username", "user_handle", "login", "handle"
    ],
    "address": [
        "address", "street_address", "location", "residence", "city", "street"
    ],
    "company": [
        "company", "organization", "employer", "business_name", "org"
    ]
}

# Regex patterns for sample value pattern analysis
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")

class MappingService:
    @staticmethod
    def suggest_mapping(column_name: str, sample_values: List[str]) -> MappingProposal:
        clean_col = column_name.strip().lower()

        # 1. Deterministic Rule / Alias Match
        for canonical_field, aliases in ALIAS_RULES.items():
            if clean_col in aliases:
                return MappingProposal(
                    raw_column_name=column_name,
                    suggested_canonical_field=canonical_field,
                    confidence=1.0,
                    reason=f"Matched exact column alias rule '{clean_col}' -> '{canonical_field}'",
                    mapping_type=MappingType.RULE,
                    is_approved=True,
                    sample_values=sample_values
                )

        # 2. Substring Alias Match
        for canonical_field, aliases in ALIAS_RULES.items():
            for alias in aliases:
                if alias in clean_col:
                    return MappingProposal(
                        raw_column_name=column_name,
                        suggested_canonical_field=canonical_field,
                        confidence=0.92,
                        reason=f"Matched substring alias '{alias}' in '{clean_col}' -> '{canonical_field}'",
                        mapping_type=MappingType.RULE,
                        is_approved=True,
                        sample_values=sample_values
                    )

        # 3. AI Pattern Analysis on Sample Values
        valid_samples = [str(v).strip() for v in sample_values if v and str(v).strip().lower() not in ["n/a", "null", "none", ""]]
        
        if valid_samples:
            # Test Email pattern
            email_matches = sum(1 for s in valid_samples if EMAIL_REGEX.match(s))
            if email_matches / len(valid_samples) >= 0.5:
                return MappingProposal(
                    raw_column_name=column_name,
                    suggested_canonical_field="email",
                    confidence=0.98,
                    reason="AI Pattern Detection: Sample values match email format (contains '@' and valid domain)",
                    mapping_type=MappingType.AI,
                    is_approved=False,
                    sample_values=sample_values
                )

            # Test Phone pattern
            phone_matches = sum(1 for s in valid_samples if PHONE_REGEX.match(s) and any(c.isdigit() for c in s))
            if phone_matches / len(valid_samples) >= 0.5:
                return MappingProposal(
                    raw_column_name=column_name,
                    suggested_canonical_field="phone",
                    confidence=0.95,
                    reason="AI Pattern Detection: Sample values contain numeric phone number patterns",
                    mapping_type=MappingType.AI,
                    is_approved=False,
                    sample_values=sample_values
                )

        # Default fallback: Ignore / Unmapped
        return MappingProposal(
            raw_column_name=column_name,
            suggested_canonical_field="ignore",
            confidence=0.50,
            reason="Unrecognized column name. Please select canonical field manually.",
            mapping_type=MappingType.MANUAL,
            is_approved=False,
            sample_values=sample_values
        )

    @classmethod
    def generate_all_proposals(cls, columns_info: List[Any]) -> List[MappingProposal]:
        proposals = []
        for col in columns_info:
            col_name = getattr(col, "column_name", col.get("column_name") if isinstance(col, dict) else str(col))
            samples = getattr(col, "sample_values", col.get("sample_values") if isinstance(col, dict) else [])
            proposals.append(cls.suggest_mapping(col_name, samples))
        return proposals
