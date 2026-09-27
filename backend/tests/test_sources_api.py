import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db

def test_source_upload_list_detail_delete():
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
        # 1. Prepare sample CSV content
        csv_content = "customer_id,name,email_id,contact_no,address\nC-101,John Doe,john@gmail.com,9876543210,Mumbai\n"
        file_tuple = ("customer_database.csv", csv_content, "text/csv")

        # 2. Test POST /api/v1/sources (Upload CSV)
        response = client.post(
            "/api/v1/sources",
            data={"source_name": "Customer Database Test", "source_type": "csv"},
            files={"file": file_tuple}
        )
        assert response.status_code == 201
        source_data = response.json()
        assert source_data["source_name"] == "Customer Database Test"
        assert source_data["total_columns"] == 5
        assert "email_id" in source_data["detected_columns"]
        source_id = source_data["id"]

        # 3. Test GET /api/v1/sources (List Sources)
        list_res = client.get("/api/v1/sources")
        assert list_res.status_code == 200
        sources_list = list_res.json()
        assert len(sources_list) == 1
        assert sources_list[0]["id"] == source_id

        # 4. Test GET /api/v1/sources/{source_id} (Source Detail & Schema)
        detail_res = client.get(f"/api/v1/sources/{source_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["total_columns"] == 5
        assert len(detail_data["sample_records"]) == 1
        assert detail_data["sample_records"][0]["email_id"] == "john@gmail.com"

        # 5. Test DELETE /api/v1/sources/{source_id}
        del_res = client.delete(f"/api/v1/sources/{source_id}")
        assert del_res.status_code == 204

        # Verify deleted
        get_del = client.get(f"/api/v1/sources/{source_id}")
        assert get_del.status_code == 404
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
