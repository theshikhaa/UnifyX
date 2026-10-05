import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db

def test_statistics_and_entities_endpoints():
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
        # Test Statistics endpoint
        response = client.get("/api/v1/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_sources" in data
        assert "total_master_entities" in data
        assert "match_rate_percentage" in data
        assert "sources_breakdown" in data

        # Test Entities list endpoint
        ent_res = client.get("/api/v1/entities")
        assert ent_res.status_code == 200
        ent_data = ent_res.json()
        assert "entities" in ent_data
        assert ent_data["total"] == 0

        # Test Entities detail 404
        detail_res = client.get("/api/v1/entities/non-existent-id")
        assert detail_res.status_code == 404

        # Test Jobs list endpoint
        jobs_res = client.get("/api/v1/jobs")
        assert jobs_res.status_code == 200
        assert isinstance(jobs_res.json(), list)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
