import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base, Source, SourceType, SourceStatus,
    ImportBatch, SourceMapping, BatchStatus, MappingType,
    SourceRecord, MasterEntity, EntityAttribute, EntityIdentifier,
    EntitySourceLink, EntityStatus
)

def test_database_models_schema():
    # Use SQLite in-memory database for quick ORM validation
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Create a Data Source
        source = Source(
            source_name="Customer Database A",
            source_type=SourceType.CSV,
            file_name="customers.csv",
            status=SourceStatus.COMPLETED
        )
        session.add(source)
        session.commit()
        assert source.id is not None

        # 2. Create an Import Batch
        batch = ImportBatch(
            source_id=source.id,
            status=BatchStatus.COMPLETED,
            total_records=1,
            processed_records=1,
            matched_records=1,
            new_entities=1
        )
        session.add(batch)
        session.commit()
        assert batch.id is not None

        # 3. Create Source Column Mapping
        mapping = SourceMapping(
            source_id=source.id,
            raw_column_name="email_id",
            canonical_field="email",
            confidence=0.99,
            is_approved=True,
            mapping_type=MappingType.AI
        )
        session.add(mapping)
        session.commit()

        # 4. Create Source Record
        record = SourceRecord(
            source_id=source.id,
            batch_id=batch.id,
            row_identifier="101",
            raw_data={"email_id": "JOHN@GMAIL.COM", "contact_no": "9876543210"},
            normalized_data={"email": "john@gmail.com", "phone": "9876543210"}
        )
        session.add(record)
        session.commit()
        assert record.id is not None

        # 5. Create Master Entity & Attributes
        master_entity = MasterEntity(
            status=EntityStatus.ACTIVE,
            canonical_profile={
                "name": "John Doe",
                "email": "john@gmail.com",
                "phone": "9876543210"
            }
        )
        session.add(master_entity)
        session.commit()

        attr_email = EntityAttribute(
            entity_id=master_entity.id,
            source_record_id=record.id,
            attribute_name="email",
            raw_value="JOHN@GMAIL.COM",
            normalized_value="john@gmail.com",
            is_primary=True
        )
        session.add(attr_email)

        identifier_email = EntityIdentifier(
            entity_id=master_entity.id,
            identifier_type="email",
            normalized_value="john@gmail.com",
            source_record_id=record.id
        )
        session.add(identifier_email)

        link = EntitySourceLink(
            entity_id=master_entity.id,
            source_id=source.id,
            batch_id=batch.id,
            source_record_id=record.id,
            match_type="exact_email",
            confidence=1.0
        )
        session.add(link)
        session.commit()

        # 6. Verify Relationships
        queried_entity = session.query(MasterEntity).filter_by(id=master_entity.id).first()
        assert queried_entity is not None
        assert len(queried_entity.attributes) == 1
        assert queried_entity.attributes[0].normalized_value == "john@gmail.com"
        assert len(queried_entity.identifiers) == 1
        assert queried_entity.identifiers[0].normalized_value == "john@gmail.com"
        assert len(queried_entity.source_links) == 1
        assert queried_entity.source_links[0].source_record.raw_data["email_id"] == "JOHN@GMAIL.COM"

        print("SUCCESS: All ORM Models and Database Schema Relationships verified!")
    finally:
        session.close()

if __name__ == "__main__":
    test_database_models_schema()
