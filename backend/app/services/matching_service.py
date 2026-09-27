from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entity import MasterEntity, EntityIdentifier, EntityStatus

# Matching Priority Order
MATCH_PRIORITIES = ["email", "phone", "username", "member_id"]

class MatchResult:
    def __init__(
        self, 
        matched: bool, 
        entity_id: Optional[str] = None, 
        match_type: Optional[str] = None, 
        confidence: float = 0.0,
        matched_identifier: Optional[str] = None
    ):
        self.matched = matched
        self.entity_id = entity_id
        self.match_type = match_type
        self.confidence = confidence
        self.matched_identifier = matched_identifier

class MatchingEngine:
    @staticmethod
    def find_match(db: Session, normalized_data: Dict[str, str]) -> MatchResult:
        """
        Searches existing master entity identifiers in priority order:
        1. Email exact match (Confidence: 1.0)
        2. Phone exact match (Confidence: 1.0)
        3. Username exact match (Confidence: 0.95)
        4. Member ID exact match (Confidence: 0.95)
        """
        if not normalized_data:
            return MatchResult(matched=False)

        for id_type in MATCH_PRIORITIES:
            norm_val = normalized_data.get(id_type)
            if not norm_val:
                continue

            # Query EntityIdentifier table
            identifier_record = (
                db.query(EntityIdentifier)
                .join(MasterEntity, EntityIdentifier.entity_id == MasterEntity.id)
                .filter(
                    EntityIdentifier.identifier_type == id_type,
                    EntityIdentifier.normalized_value == norm_val,
                    MasterEntity.status == EntityStatus.ACTIVE
                )
                .first()
            )

            if identifier_record:
                confidence = 1.0 if id_type in ["email", "phone"] else 0.95
                return MatchResult(
                    matched=True,
                    entity_id=identifier_record.entity_id,
                    match_type=f"exact_{id_type}",
                    confidence=confidence,
                    matched_identifier=norm_val
                )

        return MatchResult(matched=False)
