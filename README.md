# UnifyX — Multi-Database Entity Resolution & Unified Data Repository

UnifyX is an enterprise-grade platform built for multi-database data ingestion, schema column inspection, automatic rule and AI-assisted field mapping, data normalization, batch record matching, and Progressive Entity Enrichment.

The core objective of UnifyX is to discover implicit real-world entities across decoupled, heterogeneous datasets without relying on pre-joined tables, while maintaining complete source-level traceability and zero duplicate master records.

---

## Key Features

1. Multi-Format Data Ingestion: Ingest CSV datasets and database dumps with automatic table structure detection.
2. Schema Inspection: Analyze data types, unique record counts, null representation rates, and sample previews.
3. Automatic Field Mapping: Deterministic alias mapping rules and AI proposals for canonical field resolution (`name`, `email`, `phone`, `username`, `member_id`, `address`, `company`) with confidence scoring.
4. Data Normalization Pipeline: Standardize emails, phone numbers, and text while preserving raw un-mutated values for 100% auditability.
5. Progressive Entity Enrichment (Core Engine): Breadth-First Search (BFS) Queue algorithm that recursively discovers identifiers across datasets (`Email` -> `Phone` -> `Username` -> `Member ID` -> `Master Profile`).
6. Source Traceability: Complete 1-to-N linkage displaying source database, table name, row identifier, raw values, and normalized canonical attributes.
7. Conflict Detection: Automatically flags differing attribute values reported across contributing sources.
8. Relationship Network Graph: Visual node-edge graph representation linking Master Entities to Data Sources and Identifiers.
9. System Analytics Dashboard: Real-time KPI tracking for ingested records, matched records, new entities created, and overall resolution efficiency.
10. Scalable Chunk Processing: High-throughput stream chunking to process datasets exceeding 100,000 records under low memory footprints.

---

## Architecture Stack

### Frontend
- Framework: React 18, Vite
- Styling: Modern CSS with dark-mode executive sidebar layout
- Icons & Visuals: Lucide React
- HTTP Client: Axios with automatic backend health polling

### Backend
- Framework: Python 3.11+, FastAPI (ASGI)
- Validation: Pydantic v2
- ORM: SQLAlchemy 2.0
- Migrations: Alembic
- Testing: Pytest, HTTPX

### Database & Caching
- Primary Database: PostgreSQL 15
- In-Memory Cache & Queue: Redis 7
- Test Database: SQLite in-memory with static pooling

### Deployment & Infrastructure
- Containerization: Docker, Docker Compose

---

## Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker & Docker Compose

---

### Step 1: Start Infrastructure Services

Spin up PostgreSQL and Redis containers using Docker Compose:

```bash
docker-compose up -d postgres redis
```

Note: PostgreSQL runs on host port `5433` to prevent conflicts with pre-existing local database installations.

---

### Step 2: Backend Setup

Navigate to the `backend` directory, create a virtual environment, install dependencies, and start the FastAPI server:

#### On Windows (Git Bash):
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

#### On Linux / macOS:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The Backend API will run at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

---

### Step 3: Frontend Setup

Open a new terminal, navigate to the `frontend` directory, install dependencies, and start the Vite development server:

```bash
cd frontend
npm install
npm run dev
```

The Web Application will run at `http://localhost:5173`.

---

## How to Test & Demonstrate Progressive Entity Resolution

1. Data Sources (`Data Sources` tab):
   - Click `+ Add Data Source`.
   - Upload the 4 demonstration CSV files in `datasets/` (`hr_database.csv`, `customer_database.csv`, `business_database.csv`, `membership_database.csv`).
   - Click `Inspect Schema` to verify detected columns.

2. Field Mapping (`Field Mapping` tab):
   - Select each dataset from the dropdown.
   - Review rule and AI suggested mappings (e.g. `email_id` -> `email`, `contact_no` -> `phone`).
   - Click `Approve Field Mapping` for each source.

3. Ingestion Pipeline (`Ingestion Pipeline` tab):
   - Click `Run Ingestion Pipeline` for each dataset.
   - Watch the multi-stage progress execution stepper (`Uploaded` -> `Inspect` -> `Map` -> `Clean` -> `Index` -> `Match` -> `Enriched`).

4. Progressive Entity Search (`Unified Search` tab):
   - Click the preset demo search chip `john@gmail.com` or search by email, phone, or username.
   - Observe the BFS enrichment queue discover identifiers across all 4 databases:
     `Email: john@gmail.com` -> `Phone: 9876543210` -> `Username: johndoe` -> `Member ID: M-1024`.
   - View the unified Master Entity profile combining Name, Email, Phone, Username, Member ID, Address (Mumbai), and Company (ABC Pvt Ltd).
   - Click `View Traceability` to inspect raw source records vs normalized values.
   - Click `Inspect Graph & Lineage` to open the 5-tab detail modal (Overview, Source Traceability, Attribute Conflicts, Relationship Graph, Audit History).

---

## Running Backend Test Suite

To run the complete Pytest integration test suite:

```bash
cd backend
python -m pytest
```

All 12 unit and integration tests cover:
- Source upload, metadata parsing, and deletion logic
- Field mapping proposal generator & user approval
- Normalization algorithms (email, phone, name formatting, null handling)
- Progressive Entity Enrichment BFS chain
- System statistics aggregation
- Entity listing, conflict detection, and 404 error handling

---

## Full Containerized Deployment (Docker)

To deploy the entire stack (PostgreSQL, Redis, FastAPI Backend, and Nginx Frontend) via Docker:

```bash
docker-compose up --build -d
```

Access points:
- Frontend Web App: `http://localhost:3000`
- Backend REST API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

---

## License

This project is licensed under the MIT License.
