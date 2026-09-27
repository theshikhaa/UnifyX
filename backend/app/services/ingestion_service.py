import os
import shutil
import pandas as pd
from typing import Dict, Any, List, Tuple
from fastapi import UploadFile
from app.schemas.source import ColumnInfo, SourceSchemaInfo

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestionService:
    @staticmethod
    async def save_uploaded_file(file: UploadFile, source_id: str) -> Tuple[str, str]:
        """Saves an uploaded file safely to disk and returns (file_name, file_path)."""
        file_extension = os.path.splitext(file.filename)[1]
        saved_filename = f"{source_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file.filename, file_path

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
