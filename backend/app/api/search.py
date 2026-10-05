from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Unified Search"])

@router.get("", response_model=SearchResponse)
def search_repository(
    q: str = Query(..., min_length=1, description="Search query by email, phone, username, member ID, or name"),
    db: Session = Depends(get_db)
):
    """
    Unified Repository Search API:
    Executes the Progressive Entity Enrichment BFS algorithm to discover all associated identifiers,
    attributes, and source-level traceability records across all ingested datasets.
    """
    try:
        results = SearchService.search_entities(db, q)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search execution failed: {str(e)}"
        )
