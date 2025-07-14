from typing import Dict, List, Tuple, Optional

def bellman_ford(graph: Dict[str, Dict[str, float]], start: str) -> Tuple[Dict[str, float], Dict[str, str], bool]:
    """
    Bellman-Ford algorithm for finding shortest paths (handles negative weights).
    
    Args:
        graph: Adjacency dictionary {node: {neighbor: weight}}
        start: Starting node
    
    Returns:
        Tuple of (distances, previous_nodes, has_negative_cycle)
    """
    # Initialize distances and previous nodes
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {}
    
    # Get all nodes and edges
    nodes = list(graph.keys())
    edges = []
    for node in graph:
        for neighbor, weight in graph[node].items():
            edges.append((node, neighbor, weight))
    
    # Relax edges V-1 times
    for _ in range(len(nodes) - 1):
        for u, v, weight in edges:
            if distances[u] != float('infinity') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                previous[v] = u
    
    # Check for negative cycles
    has_negative_cycle = False
    for u, v, weight in edges:
        if distances[u] != float('infinity') and distances[u] + weight < distances[v]:
            has_negative_cycle = True
            break
    
    return distances, previous, has_negative_cycle

def get_path_bellman_ford(previous: Dict[str, str], start: str, end: str) -> List[str]:
    """
    Reconstruct path from Bellman-Ford results.
    
    Args:
        previous: Dictionary of previous nodes
        start: Starting node
        end: Ending node
    
    Returns:
        List of nodes representing the shortest path
    """
    if end not in previous and end != start:
        return []
    
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous.get(current)
    
    path.reverse()
    
    if path[0] != start:
        return []
    
    return path

def bellman_ford_with_path(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Tuple[List[str], float, bool]:
    """
    Find shortest path using Bellman-Ford algorithm.
    
    Args:
        graph: Adjacency dictionary
        start: Starting node
        end: Ending node
    
    Returns:
        Tuple of (path, total_distance, has_negative_cycle)
    """
    distances, previous, has_negative_cycle = bellman_ford(graph, start)
    path = get_path_bellman_ford(previous, start, end)
    total_distance = distances.get(end, float('infinity'))
    
    return path, total_distance, has_negative_cycle

def detect_negative_cycle(graph: Dict[str, Dict[str, float]]) -> Tuple[bool, List[str]]:
    """
    Detect if the graph contains any negative cycles.
    
    Args:
        graph: Adjacency dictionary
    
    Returns:
        Tuple of (has_negative_cycle, cycle_nodes)
    """
    if not graph:
        return False, []
    
    # Run Bellman-Ford from first node
    start_node = next(iter(graph))
    distances, previous, has_negative_cycle = bellman_ford(graph, start_node)
    
    if not has_negative_cycle:
        return False, []
    
    # Find nodes in negative cycle
    cycle_nodes = []
    edges = []
    for node in graph:
        for neighbor, weight in graph[node].items():
            edges.append((node, neighbor, weight))
    
    # Find a node that's part of negative cycle
    affected_node = None
    for u, v, weight in edges:
        if distances[u] != float('infinity') and distances[u] + weight < distances[v]:
            affected_node = v
            break
    
    if affected_node:
        # Trace back to find cycle
        visited = set()
        current = affected_node
        while current not in visited:
            visited.add(current)
            cycle_nodes.append(current)
            current = previous.get(current)
            if current is None:
                break
    
    return True, cycle_nodes
