import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db
from app.services.mapping_service import MappingService

def test_rule_and_ai_mapping_logic():
    # Test Email Alias
    prop_email = MappingService.suggest_mapping("email_id", ["john@gmail.com"])
    assert prop_email.suggested_canonical_field == "email"
    assert prop_email.confidence == 1.0

    # Test Phone Alias
    prop_phone = MappingService.suggest_mapping("contact_no", ["9876543210"])
    assert prop_phone.suggested_canonical_field == "phone"
    assert prop_phone.confidence == 1.0

    # Test AI Pattern Fallback for unknown column name with phone sample values
    prop_ai_phone = MappingService.suggest_mapping("col_x", ["+91 98765-43210", "9876500001"])
    assert prop_ai_phone.suggested_canonical_field == "phone"
    assert prop_ai_phone.confidence >= 0.90

def test_mappings_api_flow():
    # Setup isolated DB Engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        # 1. Upload Source
        csv_content = "customer_id,name,email_id,contact_no,address\nC-101,John Doe,john@gmail.com,9876543210,Mumbai\n"
        response = client.post(
            "/api/v1/sources",
            data={"source_name": "Customer DB Mapping Test", "source_type": "csv"},
            files={"file": ("customer.csv", csv_content, "text/csv")}
        )
        assert response.status_code == 201
        source_id = response.json()["id"]

        # 2. Get Auto Mappings Proposal
        res_mappings = client.get(f"/api/v1/mappings/{source_id}")
        assert res_mappings.status_code == 200
        overview = res_mappings.json()
        assert overview["source_name"] == "Customer DB Mapping Test"
        assert len(overview["proposals"]) == 5

        # Verify auto-suggestions
        prop_map = {p["raw_column_name"]: p["suggested_canonical_field"] for p in overview["proposals"]}
        assert prop_map["email_id"] == "email"
        assert prop_map["contact_no"] == "phone"
        assert prop_map["name"] == "name"
        assert prop_map["customer_id"] == "member_id"

        # 3. Approve Mappings
        updates = [
            {"raw_column_name": "customer_id", "canonical_field": "member_id", "is_approved": True},
            {"raw_column_name": "name", "canonical_field": "name", "is_approved": True},
            {"raw_column_name": "email_id", "canonical_field": "email", "is_approved": True},
            {"raw_column_name": "contact_no", "canonical_field": "phone", "is_approved": True},
            {"raw_column_name": "address", "canonical_field": "address", "is_approved": True},
        ]

        approve_res = client.post(f"/api/v1/mappings/{source_id}/approve", json=updates)
        assert approve_res.status_code == 200
        approved_overview = approve_res.json()
        assert approved_overview["status"] == "mapped"
        assert approved_overview["is_fully_approved"] is True
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
