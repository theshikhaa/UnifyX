import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from app.database.connection import Base

def utc_now():
    return datetime.now(timezone.utc)

class SourceRecord(Base):
    __tablename__ = "source_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(String(36), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False)
    
    table_name = Column(String(255), nullable=True, default="default")
    row_identifier = Column(String(255), nullable=False)  # Row number or source PK (e.g. "182")
    
    # Store complete original key-value pairs
    raw_data = Column(JSON, nullable=False)
    
    # Store normalized canonical fields (e.g., {"email": "john@gmail.com", "phone": "9876543210"})
    normalized_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


    # Relationships
    source = relationship("Source", back_populates="records")
    batch = relationship("ImportBatch", back_populates="records")
    entity_links = relationship("EntitySourceLink", back_populates="source_record", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_source_records_source_row", "source_id", "row_identifier"),
    )
