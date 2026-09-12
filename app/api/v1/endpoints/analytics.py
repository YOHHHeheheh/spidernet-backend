from fastapi import APIRouter, Depends
from app.models.schemas import GraphResponse, CytoscapeElements, GraphResponseMeta
from app.api.v1.endpoints.search import get_current_user_badge
from app.services.analytics_service import compute_betweenness_centrality, compute_louvain_communities

router = APIRouter()

@router.post("/analyze/chokepoints", response_model=GraphResponse)
def analyze_chokepoints(
    elements: CytoscapeElements,
    officer_badge: str = Depends(get_current_user_badge)
):
    enriched_elements = compute_betweenness_centrality(elements)
    
    meta = GraphResponseMeta(
        query="Chokepoint Analysis",
        total_nodes=len(enriched_elements.nodes),
        total_edges=len(enriched_elements.edges)
    )
    
    return GraphResponse(status="success", meta=meta, elements=enriched_elements)

@router.post("/analyze/communities", response_model=GraphResponse)
def analyze_communities(
    elements: CytoscapeElements,
    officer_badge: str = Depends(get_current_user_badge)
):
    enriched_elements = compute_louvain_communities(elements)
    
    meta = GraphResponseMeta(
        query="Community Detection",
        total_nodes=len(enriched_elements.nodes),
        total_edges=len(enriched_elements.edges)
    )
    
    return GraphResponse(status="success", meta=meta, elements=enriched_elements)
