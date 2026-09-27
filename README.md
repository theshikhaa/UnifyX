# Multi-Database Entity Resolution & Unified Data Repository

A web-based platform for multi-database ingestion, schema inspection, automatic AI/rule-based field mapping, normalization, batch entity matching, and **Progressive Entity Enrichment**.

## Architecture Stack

- **Frontend**: React + Vite, Axios, Modern CSS
- **Backend**: Python FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database**: PostgreSQL
- **Caching & Async Tasks**: Redis + Background Worker (Celery/RQ)

## Project Structure

```
├── backend/            # FastAPI application
├── frontend/           # React + Vite application
├── datasets/           # Sample CSV and SQL datasets
├── docker-compose.yml  # Local services infrastructure (PostgreSQL, Redis)
└── .env                # Environment configuration
```

## Getting Started

### 1. Start Infrastructure Services
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
