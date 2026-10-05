from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.source import Source
from app.models.import_batch import ImportBatch, BatchStatus
from app.models.record import SourceRecord
from app.models.entity import MasterEntity, EntitySourceLink, EntityStatus

router = APIRouter(prefix="/statistics", tags=["System Statistics"])

@router.get("")
def get_system_statistics(db: Session = Depends(get_db)):
    """
    Returns platform-wide metrics:
    - Total Data Sources
    - Total Import Batches
    - Total Raw Records Ingested
    - Total Master Entities
    - Total Matched Records
    - Total Enriched Entities
    - Overall Match Rate Percentage
    - Breakdown by Data Source
    """
    total_sources = db.query(func.count(Source.id)).scalar() or 0
    total_batches = db.query(func.count(ImportBatch.id)).scalar() or 0
    total_records = db.query(func.count(SourceRecord.id)).scalar() or 0
    total_entities = db.query(func.count(MasterEntity.id)).filter(MasterEntity.status == EntityStatus.ACTIVE).scalar() or 0
    
    # Calculate matched vs new records across import batches
    batch_stats = db.query(
        func.sum(ImportBatch.processed_records),
        func.sum(ImportBatch.matched_records),
        func.sum(ImportBatch.new_entities),
        func.sum(ImportBatch.error_count)
    ).filter(ImportBatch.status == BatchStatus.COMPLETED).first()

    processed = batch_stats[0] or 0
    matched = batch_stats[1] or 0
    new_ents = batch_stats[2] or 0
    errors = batch_stats[3] or 0

    match_rate = round((matched / processed * 100), 2) if processed > 0 else 0.0

    # Source level breakdown
    sources_breakdown = []
    sources = db.query(Source).all()
    for s in sources:
        s_records = db.query(func.count(SourceRecord.id)).filter(SourceRecord.source_id == s.id).scalar() or 0
        s_batches = db.query(ImportBatch).filter(ImportBatch.source_id == s.id).all()
        s_matched = sum(b.matched_records for b in s_batches)
        s_new = sum(b.new_entities for b in s_batches)
        
        sources_breakdown.append({
            "source_id": s.id,
            "source_name": s.source_name,
            "source_type": s.source_type,
            "status": s.status,
            "total_records": s_records,
            "matched_records": s_matched,
            "new_entities": s_new,
            "created_at": s.created_at
        })

    return {
        "total_sources": total_sources,
        "total_batches": total_batches,
        "total_records": total_records,
        "total_master_entities": total_entities,
        "processed_records": processed,
        "matched_records": matched,
        "new_entities": new_ents,
        "error_count": errors,
        "match_rate_percentage": match_rate,
        "sources_breakdown": sources_breakdown
    }
