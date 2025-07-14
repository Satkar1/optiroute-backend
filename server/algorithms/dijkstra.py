import heapq
from typing import Dict, List, Tuple, Optional

def dijkstra(graph: Dict[str, Dict[str, float]], start: str, end: Optional[str] = None) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Dijkstra's algorithm for finding shortest paths.
    
    Args:
        graph: Adjacency dictionary {node: {neighbor: weight}}
        start: Starting node
        end: Optional end node (if None, finds distances to all nodes)
    
    Returns:
        Tuple of (distances, previous_nodes)
    """
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {}
    visited = set()
    
    # Priority queue: (distance, node)
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Skip if we've already visited this node
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        # If we're looking for a specific end node and found it, we can stop
        if end and current_node == end:
            break
            
        # Check all neighbors
        for neighbor, weight in graph.get(current_node, {}).items():
            if neighbor not in visited:
                new_distance = current_distance + weight
                
                # If we found a shorter path, update it
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_distance, neighbor))
    
    return distances, previous

def get_shortest_path(previous: Dict[str, str], start: str, end: str) -> List[str]:
    """
    Reconstruct the shortest path from start to end using previous nodes.
    
    Args:
        previous: Dictionary of previous nodes from dijkstra
        start: Starting node
        end: Ending node
    
    Returns:
        List of nodes representing the shortest path
    """
    if end not in previous and end != start:
        return []  # No path found
    
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous.get(current)
    
    path.reverse()
    
    # Verify the path starts with the start node
    if path[0] != start:
        return []
    
    return path

def dijkstra_with_path(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Tuple[List[str], float]:
    """
    Find shortest path and distance between two nodes.
    
    Args:
        graph: Adjacency dictionary
        start: Starting node
        end: Ending node
    
    Returns:
        Tuple of (path, total_distance)
    """
    distances, previous = dijkstra(graph, start, end)
    path = get_shortest_path(previous, start, end)
    total_distance = distances.get(end, float('infinity'))
    
    return path, total_distance
