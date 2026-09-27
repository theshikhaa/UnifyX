import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

def utc_now():
    return datetime.now(timezone.utc)

class BatchStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MappingType(str, enum.Enum):
    RULE = "rule"
    AI = "ai"
    MANUAL = "manual"

class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(BatchStatus), nullable=False, default=BatchStatus.PENDING)
    
    total_records = Column(Integer, default=0, nullable=False)
    processed_records = Column(Integer, default=0, nullable=False)
    matched_records = Column(Integer, default=0, nullable=False)
    new_entities = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    source = relationship("Source", back_populates="batches")
    records = relationship("SourceRecord", back_populates="batch", cascade="all, delete-orphan")

class SourceMapping(Base):
    __tablename__ = "source_mappings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    
    raw_column_name = Column(String(255), nullable=False)
    canonical_field = Column(String(255), nullable=True)  # e.g., 'email', 'phone', 'name'
    confidence = Column(Float, default=1.0, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    mapping_type = Column(SQLEnum(MappingType), default=MappingType.RULE, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


    # Relationships
    source = relationship("Source", back_populates="mappings")
