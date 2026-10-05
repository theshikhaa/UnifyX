from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.entity import (
    MasterEntity, 
    EntityIdentifier, 
    EntityAttribute, 
    EntitySourceLink, 
    EntityStatus
)
from app.models.record import SourceRecord
from app.models.source import Source

router = APIRouter(prefix="/entities", tags=["Master Entities"])

@router.get("")
def list_entities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves paginated list of Master Entities."""
    query = db.query(MasterEntity).filter(MasterEntity.status == EntityStatus.ACTIVE)
    all_entities = query.order_by(MasterEntity.updated_at.desc()).all()

    if search:
        st = search.strip().lower()
        filtered = []
        for e in all_entities:
            prof = e.canonical_profile or {}
            combined_text = f"{prof.get('name', '')} {prof.get('email', '')} {prof.get('phone', '')} {prof.get('username', '')} {prof.get('company', '')}".lower()
            if st in combined_text:
                filtered.append(e)
        all_entities = filtered

    total = len(all_entities)
    start = (page - 1) * limit
    entities = all_entities[start:start + limit]

    items = []
    for e in entities:
        # Get count of linked sources
        sources_count = db.query(func.count(EntitySourceLink.id)).filter(EntitySourceLink.entity_id == e.id).scalar() or 0
        identifiers = db.query(EntityIdentifier).filter(EntityIdentifier.entity_id == e.id).all()
        
        items.append({
            "id": e.id,
            "status": e.status,
            "canonical_profile": e.canonical_profile or {},
            "matched_sources_count": sources_count,
            "identifiers_count": len(identifiers),
            "created_at": e.created_at,
            "updated_at": e.updated_at
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
        "entities": items
    }

@router.get("/{entity_id}")
def get_entity_detail(entity_id: str, db: Session = Depends(get_db)):
    """
    Returns deep inspection for a Master Entity:
    - Canonical Profile
    - All Discovered Identifiers
    - Source Traceability Links & Raw Records
    - Detected Attribute Conflicts (if different sources report conflicting values)
    - Relationship Graph (Nodes & Edges for visual graph layout)
    - Entity Enrichment Audit Trail History
    """
    master_entity = db.query(MasterEntity).filter(MasterEntity.id == entity_id).first()
    if not master_entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Master Entity not found")

    # 1. Identifiers
    identifiers = db.query(EntityIdentifier).filter(EntityIdentifier.entity_id == entity_id).all()
    id_list = [{"type": i.identifier_type, "value": i.normalized_value, "created_at": i.created_at} for i in identifiers]

    # 2. Attributes & Conflict Detection
    attributes = db.query(EntityAttribute).filter(EntityAttribute.entity_id == entity_id).all()
    attr_map: Dict[str, List[Dict[str, Any]]] = {}
    for a in attributes:
        if a.attribute_name not in attr_map:
            attr_map[a.attribute_name] = []
        attr_map[a.attribute_name].append({
            "raw_value": a.raw_value,
            "normalized_value": a.normalized_value,
            "source_record_id": a.source_record_id,
            "is_primary": a.is_primary,
            "created_at": a.created_at
        })

    conflicts = []
    for attr_name, vals in attr_map.items():
        unique_norm_vals = set(v["normalized_value"] for v in vals)
        if len(unique_norm_vals) > 1:
            conflicts.append({
                "attribute_name": attr_name,
                "values": vals,
                "status": "conflict_detected"
            })

    # 3. Source Traceability
    links = (
        db.query(EntitySourceLink)
        .filter(EntitySourceLink.entity_id == entity_id)
        .all()
    )

    traceability = []
    graph_nodes = [{"id": master_entity.id, "label": f"Master #{master_entity.id[:6]}", "type": "master", "data": master_entity.canonical_profile or {}}]
    graph_edges = []

    # Map for graph node uniqueness
    added_nodes = {master_entity.id}

    for link in links:
        src_rec = db.query(SourceRecord).filter(SourceRecord.id == link.source_record_id).first()
        src_info = db.query(Source).filter(Source.id == link.source_id).first() if link.source_id else None

        src_name = src_info.source_name if src_info else "Unknown Source"
        src_type = src_info.source_type if src_info else "csv"

        traceability.append({
            "link_id": link.id,
            "source_name": src_name,
            "source_type": src_type,
            "match_type": link.match_type,
            "confidence": link.confidence,
            "linked_at": link.linked_at,
            "record": {
                "record_id": src_rec.id if src_rec else None,
                "table_name": src_rec.table_name if src_rec else "default",
                "row_identifier": src_rec.row_identifier if src_rec else None,
                "raw_data": src_rec.raw_data if src_rec else {},
                "normalized_data": src_rec.normalized_data if src_rec else {}
            }
        })

        # Add Source node to Graph
        if src_info and src_info.id not in added_nodes:
            graph_nodes.append({
                "id": src_info.id,
                "label": src_info.source_name,
                "type": "source",
                "source_type": src_info.source_type
            })
            added_nodes.add(src_info.id)

        # Add Edge from Master Entity to Source
        if src_info:
            graph_edges.append({
                "from": master_entity.id,
                "to": src_info.id,
                "label": link.match_type or "link",
                "confidence": link.confidence
            })

    # Add Identifiers to Graph Nodes & Edges
    for idx, ident in enumerate(identifiers):
        ident_node_id = f"ident_{idx}_{ident.normalized_value}"
        if ident_node_id not in added_nodes:
            graph_nodes.append({
                "id": ident_node_id,
                "label": f"{ident.identifier_type}: {ident.normalized_value}",
                "type": "identifier",
                "identifier_type": ident.identifier_type,
                "value": ident.normalized_value
            })
            added_nodes.add(ident_node_id)
            graph_edges.append({
                "from": master_entity.id,
                "to": ident_node_id,
                "label": "has_identifier"
            })

    # Audit Trail History
    audit_history = [
        {
            "timestamp": master_entity.created_at,
            "action": "ENTITY_CREATED",
            "detail": f"Master entity initialized from primary ingestion record."
        }
    ]
    for link in links:
        audit_history.append({
            "timestamp": link.linked_at,
            "action": "ENTITY_ENRICHED",
            "detail": f"Enriched with record from {link.source_id} via {link.match_type} (confidence: {link.confidence})."
        })
    audit_history.sort(key=lambda x: str(x["timestamp"]))

    return {
        "id": master_entity.id,
        "status": master_entity.status,
        "canonical_profile": master_entity.canonical_profile or {},
        "identifiers": id_list,
        "attribute_conflicts": conflicts,
        "source_traceability": traceability,
        "relationship_graph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "audit_history": audit_history,
        "created_at": master_entity.created_at,
        "updated_at": master_entity.updated_at
    }
