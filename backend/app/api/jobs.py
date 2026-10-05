from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.import_batch import ImportBatch
from app.schemas.import_batch import ImportBatchResponse

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])

@router.get("", response_model=List[ImportBatchResponse])
def list_jobs(db: Session = Depends(get_db)):
    """Lists all background/batch import processing jobs."""
    jobs = db.query(ImportBatch).order_by(ImportBatch.created_at.desc()).all()
    return jobs

@router.get("/{job_id}", response_model=ImportBatchResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Retrieves real-time execution status of a background job."""
    job = db.query(ImportBatch).filter(ImportBatch.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
