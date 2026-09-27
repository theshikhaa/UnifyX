import os
import shutil
import uuid
from datetime import datetime, timezone
import pandas as pd
from typing import Dict, Any, List, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.schemas.source import ColumnInfo, SourceSchemaInfo
from app.models.source import Source, SourceStatus
from app.models.import_batch import ImportBatch, BatchStatus, SourceMapping
from app.models.record import SourceRecord
from app.services.normalization_service import NormalizationService
from app.services.matching_service import MatchingEngine
from app.services.enrichment_service import EnrichmentService


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestionService:
    @staticmethod
    async def save_uploaded_file(file: UploadFile, source_id: str) -> Tuple[str, str]:
        """Saves an uploaded file safely to disk and returns (file_name, file_path)."""
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".csv"
        saved_filename = f"{source_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
            
        return file.filename or "uploaded.csv", file_path


    @staticmethod
    def inspect_csv_file(file_path: str, preview_rows: int = 5) -> Dict[str, Any]:
        """
        Inspects CSV structure without reading entire large file into RAM.
        Returns detected columns, column sample values, data types, and total row estimation.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        # Read only top N rows for schema inspection to avoid memory overflow
        df_preview = pd.read_csv(file_path, nrows=preview_rows)
        
        columns_info = []
        for col_name in df_preview.columns:
            # Clean string column names
            clean_col = str(col_name).strip()
            # Extract sample values, filtering out NaN
            raw_samples = df_preview[col_name].dropna().tolist()
            samples = [str(val).strip() for val in raw_samples[:3]]
            
            # Simple infer type
            col_type = str(df_preview[col_name].dtype)
            
            columns_info.append(ColumnInfo(
                column_name=clean_col,
                data_type=col_type,
                sample_values=samples
            ))

        # Preview records as dict list
        records_preview = df_preview.fillna("").to_dict(orient="records")

        return {
            "columns": columns_info,
            "detected_column_names": [c.column_name for c in columns_info],
            "sample_records": records_preview
        }

    @staticmethod
    def process_source_ingestion(db: Session, source_id: str) -> ImportBatch:

        """
        Full Ingestion & Matching Pipeline Execution:
        Upload -> Inspect -> Map -> Normalize -> Store -> Match -> Enrich Entities
        """
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.file_path or not os.path.exists(source.file_path):
            raise ValueError(f"Source file not found for source_id: {source_id}")

        # Fetch approved column mappings
        mappings = db.query(SourceMapping).filter(SourceMapping.source_id == source_id).all()
        if not mappings:
            raise ValueError("No column mappings found. Please map and approve columns first.")

        column_mappings_dict = {
            m.raw_column_name: m.canonical_field 
            for m in mappings 
            if m.canonical_field and m.canonical_field != "ignore"
        }

        # Create ImportBatch
        batch = ImportBatch(
            id=str(uuid.uuid4()),
            source_id=source_id,
            status=BatchStatus.PROCESSING,
            started_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        db.add(batch)
        db.commit()

        # Read CSV file
        df = pd.read_csv(source.file_path)
        batch.total_records = len(df)
        
        matched_count = 0
        new_entities_count = 0
        processed_count = 0

        # Process row by row
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            # Clean string keys and values
            raw_record_data = {str(k).strip(): (None if pd.isna(v) else str(v).strip()) for k, v in row_dict.items()}

            # 1. Create SourceRecord
            record_id = str(uuid.uuid4())
            source_rec = SourceRecord(
                id=record_id,
                source_id=source_id,
                batch_id=batch.id,
                table_name="default",
                row_identifier=str(idx + 1),
                raw_data=raw_record_data,
                created_at=datetime.now(timezone.utc)
            )

            # 2. Normalize Canonical Fields
            normalized = NormalizationService.normalize_record_dict(raw_record_data, column_mappings_dict)
            source_rec.normalized_data = normalized
            db.add(source_rec)
            db.flush()

            # 3. Match against existing Master Entities
            match_result = MatchingEngine.find_match(db, normalized)

            if match_result.matched:
                matched_count += 1
            else:
                new_entities_count += 1

            # 4. Enrich or Create Master Entity
            EnrichmentService.process_record(
                db=db,
                source_id=source_id,
                batch_id=batch.id,
                source_record=source_rec,
                normalized_data=normalized,
                match_result=match_result
            )

            processed_count += 1

        # Update Batch and Source status
        batch.processed_records = processed_count
        batch.matched_records = matched_count
        batch.new_entities = new_entities_count
        batch.status = BatchStatus.COMPLETED
        batch.completed_at = datetime.now(timezone.utc)

        source.status = SourceStatus.COMPLETED
        db.commit()
        db.refresh(batch)

        return batch

