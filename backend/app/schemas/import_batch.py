from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.import_batch import BatchStatus

class ImportBatchResponse(BaseModel):
    id: str
    source_id: str
    status: BatchStatus
    total_records: int
    processed_records: int
    matched_records: int
    new_entities: int
    error_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BatchProcessResult(BaseModel):
    batch_id: str
    source_id: str
    status: BatchStatus
    total_records: int
    processed_records: int
    matched_records: int
    new_entities: int
    message: str
