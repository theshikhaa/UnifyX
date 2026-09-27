from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.models.source import SourceType, SourceStatus


class ColumnInfo(BaseModel):
    column_name: str
    data_type: str = "string"
    sample_values: List[Any] = []

class SourceSchemaInfo(BaseModel):
    source_id: str
    source_name: str
    total_columns: int
    columns: List[ColumnInfo]
    sample_records: List[Dict[str, Any]] = []

class SourceResponse(BaseModel):
    id: str
    source_name: str
    source_type: SourceType
    file_name: Optional[str] = None
    status: SourceStatus
    created_at: datetime
    updated_at: datetime
    total_columns: int = 0
    detected_columns: List[str] = []

    model_config = ConfigDict(from_attributes=True)

