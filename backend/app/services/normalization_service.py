import re
from typing import Any, Dict, Optional

# Null sentinel string values to normalize to None
NULL_SENTINELS = {
    "", " ", "null", "none", "n/a", "na", "-", "--", "undefined", "nil", "nan"
}

# Regex to strip non-digit characters for phone normalization
PHONE_DIGITS_REGEX = re.compile(r"\D")

class NormalizationService:
    @staticmethod
    def normalize_null(value: Any) -> Optional[str]:
        """
        Normalizes empty, whitespace-only, and sentinel null values ("N/A", "null", "") to None.
        """
        if value is None:
            return None
        val_str = str(value).strip()
        if val_str.lower() in NULL_SENTINELS or not val_str:
            return None
        return val_str

    @classmethod
    def normalize_email(cls, value: Any) -> Optional[str]:
        """
        Normalizes email:
        - " JOHN@GMAIL.COM " -> "john@gmail.com"
        - Strips whitespace, converts to lowercase.
        """
        val_str = cls.normalize_null(value)
        if not val_str:
            return None
        
        email_clean = val_str.strip().lower()
        # Basic email format check
        if "@" in email_clean and "." in email_clean.split("@")[-1]:
            return email_clean
        return email_clean

    @classmethod
    def normalize_name(cls, value: Any) -> Optional[str]:
        """
        Normalizes name/text:
        - "  John    Doe " -> "John Doe"
        - Collapses internal spaces and title-cases if uppercase/lowercase.
        """
        val_str = cls.normalize_null(value)
        if not val_str:
            return None
        
        # Collapse multiple internal spaces
        clean_text = re.sub(r"\s+", " ", val_str).strip()
        
        # Title case if all caps or all lowercase
        if clean_text.isupper() or clean_text.islower():
            return clean_text.title()
        return clean_text

    @classmethod
    def normalize_phone(cls, value: Any) -> Optional[str]:
        """
        Normalizes phone numbers:
        - "+91 98765-43210" -> "9876543210"
        - "+1-555-0199" -> "15550199" or last 10 digits
        - Extracts digit sequence.
        """
        val_str = cls.normalize_null(value)
        if not val_str:
            return None
        
        # Extract digits
        digits = PHONE_DIGITS_REGEX.sub("", val_str)
        if not digits:
            return None

        # Standardize 10-digit Indian/US local formats if country code prefix (e.g. 919876543210 -> 9876543210)
        if len(digits) == 12 and digits.startswith("91"):
            return digits[2:]
        elif len(digits) == 11 and digits.startswith("1"):
            return digits[1:]
            
        return digits

    @classmethod
    def normalize_text(cls, value: Any) -> Optional[str]:
        """General text normalization stripping leading/trailing whitespace."""
        val_str = cls.normalize_null(value)
        if not val_str:
            return None
        return re.sub(r"\s+", " ", val_str).strip()

    @classmethod
    def normalize_canonical_field(cls, canonical_field: str, raw_value: Any) -> Optional[str]:
        """
        Dispatches raw_value to the appropriate field normalizer.
        """
        if not canonical_field or canonical_field == "ignore":
            return None

        if canonical_field == "email":
            return cls.normalize_email(raw_value)
        elif canonical_field == "phone":
            return cls.normalize_phone(raw_value)
        elif canonical_field == "name":
            return cls.normalize_name(raw_value)
        elif canonical_field in ["username", "member_id"]:
            val_str = cls.normalize_null(raw_value)
            return val_str.strip().lower() if val_str else None
        else:
            return cls.normalize_text(raw_value)

    @classmethod
    def normalize_record_dict(
        cls, 
        raw_record: Dict[str, Any], 
        column_mappings: Dict[str, str]
    ) -> Dict[str, Optional[str]]:
        """
        Given a raw CSV row record and column mappings dict:
        {"email_id": "email", "contact_no": "phone"}
        
        Returns normalized canonical dictionary:
        {"email": "john@gmail.com", "phone": "9876543210"}
        """
        normalized_data = {}
        for raw_col, raw_val in raw_record.items():
            canonical_field = column_mappings.get(raw_col)
            if canonical_field and canonical_field != "ignore":
                norm_val = cls.normalize_canonical_field(canonical_field, raw_val)
                if norm_val is not None:
                    normalized_data[canonical_field] = norm_val
        return normalized_data
