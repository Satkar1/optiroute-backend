import heapq
from typing import Dict, List, Tuple, Callable
import math

def heuristic_euclidean(node1: str, node2: str, coordinates: Dict[str, Tuple[float, float]]) -> float:
    """
    Euclidean distance heuristic for A* algorithm.
    
    Args:
        node1: First node
        node2: Second node
        coordinates: Dictionary mapping nodes to (x, y) coordinates
    
    Returns:
        Euclidean distance between the nodes
    """
    if node1 not in coordinates or node2 not in coordinates:
        return 0
    
    x1, y1 = coordinates[node1]
    x2, y2 = coordinates[node2]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def astar(graph: Dict[str, Dict[str, float]], start: str, end: str, 
          coordinates: Dict[str, Tuple[float, float]], 
          heuristic: Callable = heuristic_euclidean) -> Tuple[List[str], float, int]:
    """
    A* algorithm for finding shortest path with heuristic.
    
    Args:
        graph: Adjacency dictionary {node: {neighbor: weight}}
        start: Starting node
        end: Ending node
        coordinates: Node coordinates for heuristic calculation
        heuristic: Heuristic function
    
    Returns:
        Tuple of (path, total_distance, nodes_explored)
    """
    # Initialize data structures
    open_set = [(0, start)]  # (f_score, node)
    came_from = {}
    g_score = {node: float('infinity') for node in graph}
    g_score[start] = 0
    f_score = {node: float('infinity') for node in graph}
    f_score[start] = heuristic(start, end, coordinates)
    
    open_set_hash = {start}
    closed_set = set()
    nodes_explored = 0
    
    while open_set:
        # Get node with lowest f_score
        current_f, current = heapq.heappop(open_set)
        open_set_hash.discard(current)
        
        # If we reached the goal, reconstruct path
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, g_score[end], nodes_explored
        
        closed_set.add(current)
        nodes_explored += 1
        
        # Check all neighbors
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in closed_set:
                continue
            
            tentative_g_score = g_score[current] + weight
            
            if neighbor not in open_set_hash:
                open_set_hash.add(neighbor)
            elif tentative_g_score >= g_score[neighbor]:
                continue
            
            # This path is better than previous one
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + heuristic(neighbor, end, coordinates)
            heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # No path found
    return [], float('infinity'), nodes_explored

def astar_multi_goal(graph: Dict[str, Dict[str, float]], start: str, goals: List[str],
                     coordinates: Dict[str, Tuple[float, float]]) -> Tuple[List[str], float, int]:
    """
    A* algorithm to find shortest path to any of multiple goals.
    
    Args:
        graph: Adjacency dictionary
        start: Starting node
        goals: List of goal nodes
        coordinates: Node coordinates
    
    Returns:
        Tuple of (path, total_distance, nodes_explored)
    """
    if not goals:
        return [], float('infinity'), 0
    
    best_path = []
    best_distance = float('infinity')
    total_nodes_explored = 0
    
    for goal in goals:
        path, distance, nodes_explored = astar(graph, start, goal, coordinates)
        total_nodes_explored += nodes_explored
        
        if distance < best_distance:
            best_distance = distance
            best_path = path
    
    return best_path, best_distance, total_nodes_explored
