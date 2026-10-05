from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class DiscoveredIdentifier(BaseModel):
    type: str
    value: str

class SourceTraceabilityItem(BaseModel):
    source_name: str
    source_type: str
    table_name: str
    row_identifier: str
    match_type: str
    confidence: float
    raw_data: Dict[str, Any]
    normalized_data: Dict[str, Any]
    linked_at: datetime

class SearchEntityResult(BaseModel):
    entity_id: str
    status: str
    name: Optional[str] = "Unknown"
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    member_id: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    matched_sources_count: int
    discovered_identifiers: List[DiscoveredIdentifier]
    source_traceability: List[SourceTraceabilityItem]
    enrichment_chain: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class SearchResponse(BaseModel):
    query: str
    total_results: int
    entities: List[SearchEntityResult]
