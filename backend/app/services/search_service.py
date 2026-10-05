from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session, joinedload

from app.models.entity import (
    MasterEntity, 
    EntityIdentifier, 
    EntityAttribute, 
    EntitySourceLink, 
    EntityStatus
)
from app.models.record import SourceRecord
from app.models.source import Source
from app.schemas.search import (
    SearchEntityResult, 
    DiscoveredIdentifier, 
    SourceTraceabilityItem, 
    SearchResponse
)
from app.services.normalization_service import NormalizationService

class SearchService:
    @staticmethod
    def search_entities(db: Session, query_string: str) -> SearchResponse:
        """
        Progressive Entity Enrichment Algorithm (BFS Queue):
        Input query (e.g. john@gmail.com)
            ↓
        Find Entity #1001 via Email
            ↓
        Discover Phone 9876543210
            ↓
        Search remaining datasets via Phone
            ↓
        Discover Username johndoe & Address Mumbai
            ↓
        Discover Member ID M-1024
            ↓
        Unified Master Entity Profile with 1-to-N Source Traceability
        """
        clean_query = query_string.strip()
        if not clean_query:
            return SearchResponse(query=query_string, total_results=0, entities=[])

        # Try normalizing as email, phone, or text
        normalized_query = (
            NormalizationService.normalize_email(clean_query) or
            NormalizationService.normalize_phone(clean_query) or
            clean_query.lower()
        )

        identifier_queue: List[str] = [normalized_query, clean_query.lower()]
        visited_identifiers: Set[str] = set()
        matched_entity_ids: Set[str] = set()
        enrichment_chain: List[str] = [f"Initial Query: {clean_query}"]

        # BFS Identifier Queue Expansion
        while identifier_queue:
            curr_id = identifier_queue.pop(0)
            if not curr_id or curr_id in visited_identifiers:
                continue

            visited_identifiers.add(curr_id)

            # Query EntityIdentifier table for matching normalized values
            matching_identifiers = (
                db.query(EntityIdentifier)
                .filter(EntityIdentifier.normalized_value == curr_id)
                .all()
            )

            # If no direct identifier match, try attribute search (e.g. name search)
            if not matching_identifiers and len(matched_entity_ids) == 0:
                attr_matches = (
                    db.query(EntityAttribute)
                    .filter(EntityAttribute.normalized_value.ilike(f"%{curr_id}%"))
                    .all()
                )
                for am in attr_matches:
                    matched_entity_ids.add(am.entity_id)

            for match in matching_identifiers:
                matched_entity_ids.add(match.entity_id)

                # Extract ALL identifiers for this entity to enrich search queue
                all_entity_ids = (
                    db.query(EntityIdentifier)
                    .filter(EntityIdentifier.entity_id == match.entity_id)
                    .all()
                )

                for eid in all_entity_ids:
                    if eid.normalized_value not in visited_identifiers:
                        identifier_queue.append(eid.normalized_value)
                        chain_msg = f"Discovered {eid.identifier_type.upper()}: {eid.normalized_value}"
                        if chain_msg not in enrichment_chain:
                            enrichment_chain.append(chain_msg)

        # Build Unified Master Entity Results
        entity_results: List[SearchEntityResult] = []

        for entity_id in matched_entity_ids:
            master_entity = db.query(MasterEntity).filter(MasterEntity.id == entity_id).first()
            if not master_entity or master_entity.status != EntityStatus.ACTIVE:
                continue

            profile = master_entity.canonical_profile or {}

            # Fetch all discovered identifiers for this entity
            entity_ids = db.query(EntityIdentifier).filter(EntityIdentifier.entity_id == entity_id).all()
            discovered_ids = [
                DiscoveredIdentifier(type=e.identifier_type, value=e.normalized_value)
                for e in entity_ids
            ]

            # Fetch source traceability links
            links = (
                db.query(EntitySourceLink)
                .join(SourceRecord, EntitySourceLink.source_record_id == SourceRecord.id)
                .join(Source, EntitySourceLink.source_id == Source.id)
                .filter(EntitySourceLink.entity_id == entity_id)
                .all()
            )

            traceability_items = []
            for link in links:
                traceability_items.append(SourceTraceabilityItem(
                    source_name=link.source_record.source.source_name if link.source_record and link.source_record.source else "Source DB",
                    source_type=link.source_record.source.source_type if link.source_record and link.source_record.source else "csv",
                    table_name=link.source_record.table_name or "default",
                    row_identifier=link.source_record.row_identifier,
                    match_type=link.match_type or "exact_match",
                    confidence=link.confidence,
                    raw_data=link.source_record.raw_data or {},
                    normalized_data=link.source_record.normalized_data or {},
                    linked_at=link.linked_at
                ))

            # Derive display attributes
            entity_results.append(SearchEntityResult(
                entity_id=master_entity.id,
                status=master_entity.status,
                name=profile.get("name", "Unknown"),
                email=profile.get("email"),
                phone=profile.get("phone"),
                username=profile.get("username"),
                member_id=profile.get("member_id"),
                address=profile.get("address"),
                company=profile.get("company"),
                matched_sources_count=len(traceability_items),
                discovered_identifiers=discovered_ids,
                source_traceability=traceability_items,
                enrichment_chain=enrichment_chain
            ))

        return SearchResponse(
            query=query_string,
            total_results=len(entity_results),
            entities=entity_results
        )
