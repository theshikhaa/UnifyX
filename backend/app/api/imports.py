from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.import_batch import ImportBatch
from app.schemas.import_batch import ImportBatchResponse, BatchProcessResult
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/imports", tags=["Ingestion & Batch Processing"])

@router.post("/{source_id}/process", response_model=BatchProcessResult)
def process_source_import(source_id: str, db: Session = Depends(get_db)):
    """
    Triggers the full synchronous ingestion pipeline for a dataset:
    Upload -> Inspect -> Map -> Normalize -> Store -> Match -> Enrich Entities
    """
    try:
        batch = IngestionService.process_source_ingestion(db, source_id)
        return BatchProcessResult(
            batch_id=batch.id,
            source_id=batch.source_id,
            status=batch.status,
            total_records=batch.total_records,
            processed_records=batch.processed_records,
            matched_records=batch.matched_records,
            new_entities=batch.new_entities,
            message=f"Successfully processed {batch.processed_records} records ({batch.matched_records} matched, {batch.new_entities} new master entities)."
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion processing failed: {str(e)}")

@router.get("/{source_id}/batches", response_model=List[ImportBatchResponse])
def get_source_batches(source_id: str, db: Session = Depends(get_db)):
    """Retrieves all historical import batches for a dataset source."""
    batches = db.query(ImportBatch).filter(ImportBatch.source_id == source_id).order_by(ImportBatch.created_at.desc()).all()
    return batches
