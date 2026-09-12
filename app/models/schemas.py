from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    type: str
    risk_level: Optional[str] = "NORMAL"
    centrality_score: Optional[float] = 0.0
    metadata: Dict[str, Any] = {}
    is_chokepoint: Optional[bool] = False
    community_id: Optional[int] = None

class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData

class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str
    details: Dict[str, Any] = {}

class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData

class CytoscapeElements(BaseModel):
    nodes: List[CytoscapeNode] = []
    edges: List[CytoscapeEdge] = []

class GraphResponseMeta(BaseModel):
    query: Optional[str] = None
    depth: Optional[int] = None
    total_nodes: int
    total_edges: int

class GraphResponse(BaseModel):
    status: str = "success"
    meta: GraphResponseMeta
    elements: CytoscapeElements

class ExpandRequest(BaseModel):
    node_id: str
    current_visible_ids: List[str] = []
    limit: int = 25
