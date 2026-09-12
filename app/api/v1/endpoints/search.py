from fastapi import APIRouter, HTTPException, Depends, Query, Request
from app.models.schemas import GraphResponse, GraphResponseMeta, ExpandRequest
from app.services.graph_service import execute_spider_search, execute_shortest_path, execute_node_expansion
from app.core.security import validate_query_input, log_audit_event
from typing import Optional

router = APIRouter()

# Mock Dependency for Authentication - In a real scenario, this would be a real token validator
def get_current_user_badge(request: Request):
    # Retrieve from JWT token context
    return "DELHI-CYBER-884"

@router.get("/search", response_model=GraphResponse)
def spider_search(
    request: Request,
    query: str = Query(..., description="Phone number, Email, UPI ID, or CCTNS ID"),
    depth: int = Query(2, ge=1, le=4, description="Depth of traversal"),
    officer_badge: str = Depends(get_current_user_badge)
):
    if not validate_query_input(query):
        raise HTTPException(status_code=422, detail="Input does not match allowed security patterns.")
        
    client_ip = request.client.host if request.client else "127.0.0.1"
    log_audit_event(officer_badge, client_ip, "GRAPH_TRAVERSAL_SEARCH", query)
    
    try:
        elements = execute_spider_search(query, depth)
    except Exception as e:
        import traceback
        err_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        raise HTTPException(status_code=500, detail=f"Database execution failed: {err_msg}")
    
    meta = GraphResponseMeta(
        query=query,
        depth=depth,
        total_nodes=len(elements.nodes),
        total_edges=len(elements.edges)
    )
    
    return GraphResponse(status="success", meta=meta, elements=elements)


@router.get("/shortest-path", response_model=GraphResponse)
def shortest_path(
    request: Request,
    source: str = Query(..., description="Source ID"),
    target: str = Query(..., description="Target ID"),
    officer_badge: str = Depends(get_current_user_badge)
):
    if not validate_query_input(source) or not validate_query_input(target):
        raise HTTPException(status_code=422, detail="Input does not match allowed security patterns.")
        
    client_ip = request.client.host if request.client else "127.0.0.1"
    log_audit_event(officer_badge, client_ip, "SHORTEST_PATH_SEARCH", f"{source}->{target}")
    
    elements = execute_shortest_path(source, target)
    
    meta = GraphResponseMeta(
        query=f"{source} to {target}",
        depth=None,
        total_nodes=len(elements.nodes),
        total_edges=len(elements.edges)
    )
    
    return GraphResponse(status="success", meta=meta, elements=elements)


@router.post("/expand", response_model=GraphResponse)
def expand_node(
    request: Request,
    expand_req: ExpandRequest,
    officer_badge: str = Depends(get_current_user_badge)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    log_audit_event(officer_badge, client_ip, "NODE_EXPANSION", expand_req.node_id)
    
    elements = execute_node_expansion(expand_req.node_id, expand_req.current_visible_ids, expand_req.limit)
    
    meta = GraphResponseMeta(
        query=f"Expand {expand_req.node_id}",
        depth=1,
        total_nodes=len(elements.nodes),
        total_edges=len(elements.edges)
    )
    
    return GraphResponse(status="success", meta=meta, elements=elements)
