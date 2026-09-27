import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db
from app.models.entity import MasterEntity, EntityIdentifier, EntitySourceLink

def test_progressive_entity_enrichment_across_4_datasets():
    # Setup isolated test database
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
        # ----------------------------------------------------
        # Step 1: Upload & Process Database A (HR Database)
        # ----------------------------------------------------
        csv_a = "employee_id,full_name,email,mobile_number\nE-1001,John Doe,john@gmail.com,+91 98765-43210\n"
        res_a = client.post("/api/v1/sources", data={"source_name": "DB A - HR", "source_type": "csv"}, files={"file": ("hr.csv", csv_a, "text/csv")})
        src_a_id = res_a.json()["id"]

        # Approve mappings for DB A
        client.post(f"/api/v1/mappings/{src_a_id}/approve", json=[
            {"raw_column_name": "employee_id", "canonical_field": "member_id", "is_approved": True},
            {"raw_column_name": "full_name", "canonical_field": "name", "is_approved": True},
            {"raw_column_name": "email", "canonical_field": "email", "is_approved": True},
            {"raw_column_name": "mobile_number", "canonical_field": "phone", "is_approved": True},
        ])

        # Process DB A
        proc_a = client.post(f"/api/v1/imports/{src_a_id}/process")
        assert proc_a.status_code == 200
        assert proc_a.json()["new_entities"] == 1
        assert proc_a.json()["matched_records"] == 0

        # ----------------------------------------------------
        # Step 2: Upload & Process Database B (Customer Database)
        # ----------------------------------------------------
        csv_b = 'customer_id,name,email_id,contact_no,address\nC-8812,John Doe , JOHN@GMAIL.COM ,9876543210,"124 Marine Drive, Mumbai"\n'

        res_b = client.post("/api/v1/sources", data={"source_name": "DB B - Customer", "source_type": "csv"}, files={"file": ("customer.csv", csv_b, "text/csv")})
        src_b_id = res_b.json()["id"]

        client.post(f"/api/v1/mappings/{src_b_id}/approve", json=[
            {"raw_column_name": "customer_id", "canonical_field": "member_id", "is_approved": True},
            {"raw_column_name": "name", "canonical_field": "name", "is_approved": True},
            {"raw_column_name": "email_id", "canonical_field": "email", "is_approved": True},
            {"raw_column_name": "contact_no", "canonical_field": "phone", "is_approved": True},
            {"raw_column_name": "address", "canonical_field": "address", "is_approved": True},
        ])

        proc_b = client.post(f"/api/v1/imports/{src_b_id}/process")
        assert proc_b.status_code == 200
        assert proc_b.json()["matched_records"] == 1
        assert proc_b.json()["new_entities"] == 0

        # ----------------------------------------------------
        # Step 3: Upload & Process Database C (Business Database - No Email!)
        # ----------------------------------------------------
        csv_c = "username,phone,company,city\njohndoe,+919876543210,ABC Pvt Ltd,Mumbai\n"
        res_c = client.post("/api/v1/sources", data={"source_name": "DB C - Business", "source_type": "csv"}, files={"file": ("business.csv", csv_c, "text/csv")})
        src_c_id = res_c.json()["id"]

        client.post(f"/api/v1/mappings/{src_c_id}/approve", json=[
            {"raw_column_name": "username", "canonical_field": "username", "is_approved": True},
            {"raw_column_name": "phone", "canonical_field": "phone", "is_approved": True},
            {"raw_column_name": "company", "canonical_field": "company", "is_approved": True},
            {"raw_column_name": "city", "canonical_field": "address", "is_approved": True},
        ])

        proc_c = client.post(f"/api/v1/imports/{src_c_id}/process")
        assert proc_c.status_code == 200
        assert proc_c.json()["matched_records"] == 1
        assert proc_c.json()["new_entities"] == 0

        # ----------------------------------------------------
        # Step 4: Upload & Process Database D (Membership Database)
        # ----------------------------------------------------
        csv_d = "member_id,email,username\nM-1024,john@gmail.com,johndoe\n"
        res_d = client.post("/api/v1/sources", data={"source_name": "DB D - Membership", "source_type": "csv"}, files={"file": ("membership.csv", csv_d, "text/csv")})
        src_d_id = res_d.json()["id"]

        client.post(f"/api/v1/mappings/{src_d_id}/approve", json=[
            {"raw_column_name": "member_id", "canonical_field": "member_id", "is_approved": True},
            {"raw_column_name": "email", "canonical_field": "email", "is_approved": True},
            {"raw_column_name": "username", "canonical_field": "username", "is_approved": True},
        ])

        proc_d = client.post(f"/api/v1/imports/{src_d_id}/process")
        assert proc_d.status_code == 200
        assert proc_d.json()["matched_records"] == 1
        assert proc_d.json()["new_entities"] == 0

        # ----------------------------------------------------
        # VERIFICATION OF PROGRESSIVE ENTITY ENRICHMENT
        # ----------------------------------------------------
        db = TestingSessionLocal()
        try:
            # 1. Total Master Entities in DB should be EXACTLY 1 (No duplicates created!)
            master_entities = db.query(MasterEntity).all()
            assert len(master_entities) == 1
            john_master = master_entities[0]

            # 2. Verify all attributes were progressively enriched into master entity profile
            profile = john_master.canonical_profile
            assert profile["email"] == "john@gmail.com"
            assert profile["phone"] == "9876543210"
            assert profile["username"] == "johndoe"
            assert profile["member_id"] in ["e-1001", "m-1024"]

            assert profile["address"] == "124 Marine Drive, Mumbai"
            assert profile["company"] == "ABC Pvt Ltd"

            # 3. Verify Source Traceability Links count (linked to all 4 databases!)
            links = db.query(EntitySourceLink).filter(EntitySourceLink.entity_id == john_master.id).all()
            assert len(links) == 4

            print("\nSUCCESS: Progressive Entity Enrichment & Source Traceability verified across all 4 datasets!")
        finally:
            db.close()

    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
