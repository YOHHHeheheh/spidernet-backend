import networkx as nx
from app.models.schemas import CytoscapeElements

def compute_betweenness_centrality(elements: CytoscapeElements) -> CytoscapeElements:
    """
    Computes Betweenness Centrality on the current graph elements and flags chokepoints.
    """
    if not elements.nodes or not elements.edges:
        return elements
        
    G = nx.DiGraph()
    
    # Add nodes
    for node in elements.nodes:
        G.add_node(node.data.id)
        
    # Add edges
    for edge in elements.edges:
        amount = edge.data.details.get("amount", 1.0)
        # Using 1/amount as weight so larger transfers = shorter path distance in NetworkX
        weight = 1.0 / float(amount) if float(amount) > 0 else 1.0
        G.add_edge(edge.data.source, edge.data.target, weight=weight)
        
    try:
        # Compute centrality
        centrality = nx.betweenness_centrality(G, weight="weight")
        
        # Find max centrality for normalization
        max_c = max(centrality.values()) if centrality else 0
        
        # Update node payloads
        for node in elements.nodes:
            raw_score = centrality.get(node.data.id, 0.0)
            norm_score = (raw_score / max_c) if max_c > 0 else 0.0
            node.data.centrality_score = round(norm_score, 4)
            
            # Highlight chokepoints (e.g. > 0.4 normalized centrality)
            if norm_score > 0.4 and len(G) > 5:
                node.data.is_chokepoint = True
                node.data.risk_level = "CRITICAL"
                
    except Exception as e:
        print(f"Error computing centrality: {e}")
        
    return elements

def compute_louvain_communities(elements: CytoscapeElements) -> CytoscapeElements:
    """
    Partitions the network into communities using Louvain modularity.
    """
    if not elements.nodes or not elements.edges:
        return elements
        
    G = nx.Graph() # Louvain generally works better on undirected
    
    for node in elements.nodes:
        G.add_node(node.data.id)
        
    for edge in elements.edges:
        G.add_edge(edge.data.source, edge.data.target)
        
    try:
        communities = nx.community.louvain_communities(G)
        
        # Map node to community ID
        comm_map = {}
        for idx, comm in enumerate(communities):
            for node_id in comm:
                comm_map[node_id] = idx
                
        # Update node payloads
        for node in elements.nodes:
            node.data.community_id = comm_map.get(node.data.id, 0)
            
    except Exception as e:
        print(f"Error computing communities: {e}")
        
    return elements
