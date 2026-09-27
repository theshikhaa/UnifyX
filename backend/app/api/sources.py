import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.source import Source, SourceType, SourceStatus
from app.schemas.source import SourceResponse, SourceSchemaInfo, ColumnInfo
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/sources", tags=["Data Sources"])

@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_source(
    source_name: str = Form(...),
    source_type: SourceType = Form(SourceType.CSV),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    1. Upload CSV file.
    2. Store metadata in database.
    3. Save file locally.
    4. Inspect CSV structure & detect columns.
    """
    if not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV files are currently supported."
        )

    # Generate source ID
    source_id = str(uuid.uuid4())
    
    # Save file to disk
    original_name, saved_path = await IngestionService.save_uploaded_file(file, source_id)

    # Inspect CSV structure
    try:
        inspection_result = IngestionService.inspect_csv_file(saved_path)
        detected_cols = inspection_result["detected_column_names"]
    except Exception as e:
        # If inspection fails, clean up file and raise error
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to inspect CSV file structure: {str(e)}"
        )

    # Create Source DB Record
    source = Source(
        id=source_id,
        source_name=source_name,
        source_type=source_type,
        file_name=original_name,
        file_path=saved_path,
        status=SourceStatus.INSPECTED
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)

    response_data = SourceResponse(
        id=source.id,
        source_name=source.source_name,
        source_type=source.source_type,
        file_name=source.file_name,
        status=source.status,
        created_at=source.created_at,
        updated_at=source.updated_at,
        total_columns=len(detected_cols),
        detected_columns=detected_cols
    )

    return response_data

@router.get("", response_model=List[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """Retrieve list of all data sources."""
    sources = db.query(Source).order_by(Source.created_at.desc()).all()
    
    results = []
    for s in sources:
        detected_cols = []
        if s.file_path and os.path.exists(s.file_path):
            try:
                insp = IngestionService.inspect_csv_file(s.file_path)
                detected_cols = insp["detected_column_names"]
            except Exception:
                pass

        results.append(SourceResponse(
            id=s.id,
            source_name=s.source_name,
            source_type=s.source_type,
            file_name=s.file_name,
            status=s.status,
            created_at=s.created_at,
            updated_at=s.updated_at,
            total_columns=len(detected_cols),
            detected_columns=detected_cols
        ))
        
    return results

@router.get("/{source_id}", response_model=SourceSchemaInfo)
def get_source_detail(source_id: str, db: Session = Depends(get_db)):
    """Get detailed schema and sample values for a specific source."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    if not source.file_path or not os.path.exists(source.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source file not found on server storage")

    inspection = IngestionService.inspect_csv_file(source.file_path, preview_rows=10)

    return SourceSchemaInfo(
        source_id=source.id,
        source_name=source.source_name,
        total_columns=len(inspection["columns"]),
        columns=inspection["columns"],
        sample_records=inspection["sample_records"]
    )

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: str, db: Session = Depends(get_db)):
    """Delete a source and remove its stored file."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    # Remove file from disk
    if source.file_path and os.path.exists(source.file_path):
        try:
            os.remove(source.file_path)
        except Exception:
            pass

    db.delete(source)
    db.commit()
    return None
