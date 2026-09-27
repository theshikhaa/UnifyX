import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.entity import (
    MasterEntity, 
    EntityAttribute, 
    EntityIdentifier, 
    EntitySourceLink, 
    EntityStatus
)
from app.models.record import SourceRecord
from app.services.matching_service import MatchResult

def utc_now():
    return datetime.now(timezone.utc)

IDENTIFIER_FIELDS = {"email", "phone", "username", "member_id"}

class EnrichmentService:
    @staticmethod
    def process_record(
        db: Session,
        source_id: str,
        batch_id: str,
        source_record: SourceRecord,
        normalized_data: Dict[str, str],
        match_result: MatchResult
    ) -> MasterEntity:
        """
        Main entry point for Master Entity Creation & Progressive Enrichment:
        - If matched: Enriches existing entity with new attributes & identifiers.
        - If not matched: Creates a new Master Entity.
        - Preserves source-level traceability link.
        """
        if match_result.matched and match_result.entity_id:
            master_entity = db.query(MasterEntity).filter(MasterEntity.id == match_result.entity_id).first()
            is_new = False
        else:
            master_entity = MasterEntity(
                id=str(uuid.uuid4()),
                status=EntityStatus.ACTIVE,
                canonical_profile={},
                created_at=utc_now(),
                updated_at=utc_now()
            )
            db.add(master_entity)
            db.flush()
            is_new = True

        # Existing profile snapshot
        profile = dict(master_entity.canonical_profile or {})

        # Populate or Enrich attributes & identifiers
        for field_name, norm_val in normalized_data.items():
            if not norm_val:
                continue

            # Update consolidated canonical profile if not present or primary
            if field_name not in profile or is_new:
                profile[field_name] = norm_val

            # 1. Add to EntityAttribute if attribute doesn't already exist for this entity from this source record
            existing_attr = (
                db.query(EntityAttribute)
                .filter(
                    EntityAttribute.entity_id == master_entity.id,
                    EntityAttribute.attribute_name == field_name,
                    EntityAttribute.normalized_value == norm_val
                )
                .first()
            )
            if not existing_attr:
                attr = EntityAttribute(
                    id=str(uuid.uuid4()),
                    entity_id=master_entity.id,
                    source_record_id=source_record.id,
                    attribute_name=field_name,
                    raw_value=str(source_record.raw_data.get(field_name, norm_val)),
                    normalized_value=norm_val,
                    is_primary=True,
                    created_at=utc_now()
                )
                db.add(attr)

            # 2. Add to EntityIdentifier if identifier field
            if field_name in IDENTIFIER_FIELDS:
                existing_id = (
                    db.query(EntityIdentifier)
                    .filter(
                        EntityIdentifier.entity_id == master_entity.id,
                        EntityIdentifier.identifier_type == field_name,
                        EntityIdentifier.normalized_value == norm_val
                    )
                    .first()
                )
                if not existing_id:
                    identifier = EntityIdentifier(
                        id=str(uuid.uuid4()),
                        entity_id=master_entity.id,
                        identifier_type=field_name,
                        normalized_value=norm_val,
                        source_record_id=source_record.id,
                        created_at=utc_now()
                    )
                    db.add(identifier)

        # Update profile snapshot & updated_at timestamp
        master_entity.canonical_profile = profile
        master_entity.updated_at = utc_now()

        # 3. Create Source Traceability Link
        link = EntitySourceLink(
            id=str(uuid.uuid4()),
            entity_id=master_entity.id,
            source_id=source_id,
            batch_id=batch_id,
            source_record_id=source_record.id,
            match_type=match_result.match_type if not is_new else "new_entity",
            confidence=match_result.confidence if not is_new else 1.0,
            linked_at=utc_now()
        )
        db.add(link)

        db.flush()
        return master_entity
