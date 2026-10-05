import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db

def test_search_api_progressive_enrichment():
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
        # 1. Ingest Database A (HR)
        csv_a = "employee_id,full_name,email,mobile_number\nE-1001,John Doe,john@gmail.com,+91 98765-43210\n"
        res_a = client.post("/api/v1/sources", data={"source_name": "DB A - HR", "source_type": "csv"}, files={"file": ("hr.csv", csv_a, "text/csv")})
        src_a_id = res_a.json()["id"]
        client.post(f"/api/v1/mappings/{src_a_id}/approve", json=[
            {"raw_column_name": "employee_id", "canonical_field": "member_id", "is_approved": True},
            {"raw_column_name": "full_name", "canonical_field": "name", "is_approved": True},
            {"raw_column_name": "email", "canonical_field": "email", "is_approved": True},
            {"raw_column_name": "mobile_number", "canonical_field": "phone", "is_approved": True},
        ])
        client.post(f"/api/v1/imports/{src_a_id}/process")

        # 2. Ingest Database C (Business - username & phone, no email!)
        csv_c = "username,phone,company,city\njohndoe,+919876543210,ABC Pvt Ltd,Mumbai\n"
        res_c = client.post("/api/v1/sources", data={"source_name": "DB C - Business", "source_type": "csv"}, files={"file": ("business.csv", csv_c, "text/csv")})
        src_c_id = res_c.json()["id"]
        client.post(f"/api/v1/mappings/{src_c_id}/approve", json=[
            {"raw_column_name": "username", "canonical_field": "username", "is_approved": True},
            {"raw_column_name": "phone", "canonical_field": "phone", "is_approved": True},
            {"raw_column_name": "company", "canonical_field": "company", "is_approved": True},
            {"raw_column_name": "city", "canonical_field": "address", "is_approved": True},
        ])
        client.post(f"/api/v1/imports/{src_c_id}/process")

        # 3. Test Search by Email
        search_res = client.get("/api/v1/search?q=john@gmail.com")
        assert search_res.status_code == 200
        data = search_res.json()
        assert data["total_results"] == 1
        entity = data["entities"][0]

        # Verify progressive enrichment fields (email from DB A + username/company from DB C)
        assert entity["email"] == "john@gmail.com"
        assert entity["phone"] == "9876543210"
        assert entity["username"] == "johndoe"
        assert entity["company"] == "ABC Pvt Ltd"
        assert entity["matched_sources_count"] == 2

        # 4. Test Search by Phone
        search_phone = client.get("/api/v1/search?q=9876543210")
        assert search_phone.status_code == 200
        assert search_phone.json()["entities"][0]["entity_id"] == entity["entity_id"]

        # 5. Test Search by Username
        search_uname = client.get("/api/v1/search?q=johndoe")
        assert search_uname.status_code == 200
        assert search_uname.json()["entities"][0]["entity_id"] == entity["entity_id"]

    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
