import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

def utc_now():
    return datetime.now(timezone.utc)

class SourceType(str, enum.Enum):
    CSV = "csv"
    SQL_DUMP = "sql_dump"
    DATABASE = "database"

class SourceStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    INSPECTED = "inspected"
    MAPPED = "mapped"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name = Column(String(255), nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False, default=SourceType.CSV)
    file_name = Column(String(255), nullable=True)
    file_path = Column(Text, nullable=True)
    status = Column(SQLEnum(SourceStatus), nullable=False, default=SourceStatus.UPLOADED)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


    # Relationships
    batches = relationship("ImportBatch", back_populates="source", cascade="all, delete-orphan")
    mappings = relationship("SourceMapping", back_populates="source", cascade="all, delete-orphan")
    records = relationship("SourceRecord", back_populates="source", cascade="all, delete-orphan")
