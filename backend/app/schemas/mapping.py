from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.import_batch import MappingType

CANONICAL_FIELDS = [
    "name",
    "email",
    "phone",
    "username",
    "member_id",
    "address",
    "company",
    "ignore"
]

class MappingProposal(BaseModel):
    raw_column_name: str
    suggested_canonical_field: Optional[str] = None
    confidence: float = 1.0
    reason: str = "Deterministic rule match"
    mapping_type: MappingType = MappingType.RULE
    is_approved: bool = False
    sample_values: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class MappingUpdateRequest(BaseModel):
    raw_column_name: str
    canonical_field: str
    is_approved: bool = True

class SourceMappingOverview(BaseModel):
    source_id: str
    source_name: str
    status: str
    is_fully_approved: bool
    proposals: List[MappingProposal]

    model_config = ConfigDict(from_attributes=True)
