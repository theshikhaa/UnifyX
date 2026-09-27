import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.source import Source, SourceStatus
from app.models.import_batch import SourceMapping, MappingType
from app.schemas.mapping import (
    MappingProposal, 
    MappingUpdateRequest, 
    SourceMappingOverview, 
    CANONICAL_FIELDS
)
from app.services.ingestion_service import IngestionService
from app.services.mapping_service import MappingService

router = APIRouter(prefix="/mappings", tags=["Field Mappings"])

@router.get("/canonical-fields", response_model=List[str])
def get_canonical_fields():
    """Returns the list of system-wide supported canonical fields."""
    return CANONICAL_FIELDS

@router.get("/{source_id}", response_model=SourceMappingOverview)
def get_source_mappings(source_id: str, db: Session = Depends(get_db)):
    """
    Retrieves existing mappings for a source from database.
    If no saved mappings exist, runs automatic rule & AI mapping proposal engine.
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    if not source.file_path or not os.path.exists(source.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source file not found")

    # Fetch stored mappings from DB
    existing_mappings = db.query(SourceMapping).filter(SourceMapping.source_id == source_id).all()
    inspection = IngestionService.inspect_csv_file(source.file_path)

    samples_map = {col.column_name: col.sample_values for col in inspection["columns"]}

    if existing_mappings:
        proposals = []
        all_approved = True
        for m in existing_mappings:
            if not m.is_approved:
                all_approved = False
            proposals.append(MappingProposal(
                raw_column_name=m.raw_column_name,
                suggested_canonical_field=m.canonical_field,
                confidence=m.confidence,
                reason="Saved database mapping",
                mapping_type=m.mapping_type,
                is_approved=m.is_approved,
                sample_values=samples_map.get(m.raw_column_name, [])
            ))
        return SourceMappingOverview(
            source_id=source.id,
            source_name=source.source_name,
            status=source.status,
            is_fully_approved=all_approved,
            proposals=proposals
        )

    # Generate proposals dynamically
    proposals = MappingService.generate_all_proposals(inspection["columns"])
    all_approved = all(p.is_approved for p in proposals)

    return SourceMappingOverview(
        source_id=source.id,
        source_name=source.source_name,
        status=source.status,
        is_fully_approved=all_approved,
        proposals=proposals
    )

@router.post("/{source_id}/approve", response_model=SourceMappingOverview)
def approve_mappings(
    source_id: str, 
    updates: List[MappingUpdateRequest], 
    db: Session = Depends(get_db)
):
    """
    Saves user-reviewed/approved mappings into the database and updates source status to MAPPED.
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    # Clear existing stored mappings for this source
    db.query(SourceMapping).filter(SourceMapping.source_id == source_id).delete()

    for item in updates:
        db_mapping = SourceMapping(
            id=str(uuid.uuid4()),
            source_id=source_id,
            raw_column_name=item.raw_column_name,
            canonical_field=item.canonical_field if item.canonical_field != "ignore" else None,
            confidence=1.0,
            is_approved=item.is_approved,
            mapping_type=MappingType.MANUAL
        )
        db.add(db_mapping)

    source.status = SourceStatus.MAPPED
    db.commit()

    return get_source_mappings(source_id, db)
