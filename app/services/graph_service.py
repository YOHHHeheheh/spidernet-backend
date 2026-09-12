from app.core.database import db_conn
from app.models.schemas import CytoscapeElements, CytoscapeNode, CytoscapeNodeData, CytoscapeEdge, CytoscapeEdgeData

def _parse_neo4j_to_cytoscape(nodes_record, edges_record) -> CytoscapeElements:
    cyto_nodes = []
    cyto_edges = []
    
    seen_nodes = set()
    seen_edges = set()
    
    for node in nodes_record:
        labels = list(node.labels)
        node_type = labels[0] if labels else "Unknown"
        node_id = f"{node_type}_{node.id}"
        
        if node_id in seen_nodes:
            continue
        seen_nodes.add(node_id)
        
        props = dict(node)
        
        # Determine label based on type
        label = "Unknown"
        if node_type == "PhoneNumber":
            label = props.get("number", "")
        elif node_type == "BankAccount":
            label = props.get("account_number", "")
        elif node_type == "UpiID":
            label = props.get("vpa", "")
        elif node_type == "Email":
            label = props.get("address", "")
        elif node_type == "Person":
            label = props.get("name", props.get("cctns_id", ""))
            
        risk_level = props.pop("risk_level", "NORMAL")
        
        cyto_nodes.append(CytoscapeNode(
            data=CytoscapeNodeData(
                id=node_id,
                label=label,
                type=node_type,
                risk_level=risk_level,
                metadata=props
            )
        ))
        
    for edge in edges_record:
        if edge is None:
            continue
            
        edge_id = f"edge_{edge.id}"
        if edge_id in seen_edges:
            continue
        seen_edges.add(edge_id)
        
        start_node = edge.start_node
        end_node = edge.end_node
        
        start_type = list(start_node.labels)[0] if start_node.labels else "Unknown"
        end_type = list(end_node.labels)[0] if end_node.labels else "Unknown"
        
        source_id = f"{start_type}_{start_node.id}"
        target_id = f"{end_type}_{end_node.id}"
        
        cyto_edges.append(CytoscapeEdge(
            data=CytoscapeEdgeData(
                id=edge_id,
                source=source_id,
                target=target_id,
                label=edge.type,
                details=dict(edge)
            )
        ))
        
    return CytoscapeElements(nodes=cyto_nodes, edges=cyto_edges)

def execute_spider_search(query: str, depth: int) -> CytoscapeElements:
    def _tx_func(tx):
        cypher_query = """
        MATCH (start)
        WHERE (start:PhoneNumber AND start.number = $query)
           OR (start:Email AND start.address = $query)
           OR (start:UpiID AND start.vpa = $query)
           OR (start:Person AND start.cctns_id = $query)
           OR (start:Person AND start.name = $query)
           OR (start:FIR AND start.id = $query)
           OR (start:BankAccount AND start.account_number = $query)
        MATCH path = (start)-[*1..%d]-(target)
        RETURN collect(distinct start) + collect(distinct target) AS nodes,
               collect(distinct last(relationships(path))) AS edges
        """ % depth
        result = tx.run(cypher_query, parameters={"query": query})
        record = result.single()
        if not record:
            return CytoscapeElements(nodes=[], edges=[])
        return _parse_neo4j_to_cytoscape(record["nodes"], record["edges"])
        
    with db_conn.get_session() as session:
        return session.execute_read(_tx_func)

def execute_shortest_path(source: str, target: str) -> CytoscapeElements:
    cypher_query = """
    MATCH (a), (b)
    WHERE (a.number = $source OR a.vpa = $source OR a.cctns_id = $source OR a.account_number = $source OR a.address = $source)
      AND (b.number = $target OR b.vpa = $target OR b.cctns_id = $target OR b.account_number = $target OR b.address = $target)
    MATCH path = shortestPath((a)-[*]-(b))
    RETURN nodes(path) AS nodes, relationships(path) AS edges
    """
    
    with db_conn.get_session() as session:
        result = session.run(cypher_query, source=source, target=target)
        record = result.single()
        
        if not record:
            return CytoscapeElements(nodes=[], edges=[])
            
        return _parse_neo4j_to_cytoscape(record["nodes"], record["edges"])

def execute_node_expansion(node_id: str, current_visible_ids: list, limit: int) -> CytoscapeElements:
    # node_id is in format "Type_InternalID" (e.g., "PhoneNumber_123")
    parts = node_id.split("_", 1)
    if len(parts) != 2:
        return CytoscapeElements(nodes=[], edges=[])
        
    internal_id = int(parts[1])
    
    # Exclude already visible nodes using their internal IDs
    visible_internal_ids = []
    for vid in current_visible_ids:
        v_parts = vid.split("_", 1)
        if len(v_parts) == 2 and v_parts[1].isdigit():
            visible_internal_ids.append(int(v_parts[1]))
            
    cypher_query = """
    MATCH (n)-[r]-(neighbor)
    WHERE id(n) = $internal_id
      AND NOT id(neighbor) IN $visible_internal_ids
    RETURN collect(distinct n) + collect(distinct neighbor)[0..$limit] AS nodes,
           collect(distinct r)[0..$limit] AS edges
    """
    
    with db_conn.get_session() as session:
        result = session.run(cypher_query, internal_id=internal_id, visible_internal_ids=visible_internal_ids, limit=limit)
        record = result.single()
        
        if not record:
            return CytoscapeElements(nodes=[], edges=[])
            
        return _parse_neo4j_to_cytoscape(record["nodes"], record["edges"])
