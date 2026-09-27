import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text, Enum as SQLEnum, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

def utc_now():
    return datetime.now(timezone.utc)

class EntityStatus(str, enum.Enum):
    ACTIVE = "active"
    MERGED = "merged"
    ARCHIVED = "archived"

class MasterEntity(Base):
    __tablename__ = "master_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(SQLEnum(EntityStatus), nullable=False, default=EntityStatus.ACTIVE)
    
    # Quick access consolidated master attributes snapshot
    canonical_profile = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    attributes = relationship("EntityAttribute", back_populates="entity", cascade="all, delete-orphan")
    identifiers = relationship("EntityIdentifier", back_populates="entity", cascade="all, delete-orphan")
    source_links = relationship("EntitySourceLink", back_populates="entity", cascade="all, delete-orphan")

class EntityAttribute(Base):
    """
    Stores every attribute value for an entity with source attribution.
    Allows new canonical fields to be added dynamically.
    """
    __tablename__ = "entity_attributes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("master_entities.id", ondelete="CASCADE"), nullable=False)
    source_record_id = Column(String(36), ForeignKey("source_records.id", ondelete="SET NULL"), nullable=True)

    attribute_name = Column(String(100), nullable=False)   # e.g., 'email', 'phone', 'address'
    raw_value = Column(Text, nullable=True)                 # Original raw value
    normalized_value = Column(Text, nullable=True)          # Cleaned & normalized value
    is_primary = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    entity = relationship("MasterEntity", back_populates="attributes")

    __table_args__ = (
        Index("idx_entity_attr_lookup", "entity_id", "attribute_name"),
    )

class EntityIdentifier(Base):
    """
    Indexed table for exact & fast identifier search during matching & enrichment.
    Types: 'email', 'phone', 'username', 'member_id'
    """
    __tablename__ = "entity_identifiers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("master_entities.id", ondelete="CASCADE"), nullable=False)
    
    identifier_type = Column(String(50), nullable=False)     # 'email', 'phone', 'username', 'member_id'
    normalized_value = Column(String(255), nullable=False)  # e.g., 'john@gmail.com', '9876543210'
    source_record_id = Column(String(36), ForeignKey("source_records.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    entity = relationship("MasterEntity", back_populates="identifiers")

    __table_args__ = (
        Index("idx_identifier_type_value", "identifier_type", "normalized_value"),
        Index("idx_identifier_value_only", "normalized_value"),
    )

class EntitySourceLink(Base):
    """
    Explicit source-level traceability:
    Master Entity #1001 <-> Source DB, Table, Row, Batch, Timestamp
    """
    __tablename__ = "entity_source_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("master_entities.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(String(36), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False)
    source_record_id = Column(String(36), ForeignKey("source_records.id", ondelete="CASCADE"), nullable=False)

    match_type = Column(String(100), nullable=True) # e.g. 'exact_email', 'exact_phone', 'new_entity'
    confidence = Column(Float, default=1.0, nullable=False)

    linked_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    entity = relationship("MasterEntity", back_populates="source_links")
    source_record = relationship("SourceRecord", back_populates="entity_links")

