from typing import Dict, List, Tuple
import itertools
import math

def nearest_neighbor_tsp(graph: Dict[str, Dict[str, float]], start: str, 
                        nodes_to_visit: List[str]) -> Tuple[List[str], float]:
    """
    Solve TSP using Nearest Neighbor heuristic.
    
    Args:
        graph: Adjacency dictionary {node: {neighbor: weight}}
        start: Starting node
        nodes_to_visit: List of nodes to visit
    
    Returns:
        Tuple of (path, total_distance)
    """
    if not nodes_to_visit:
        return [start], 0
    
    # Include start node in the tour
    all_nodes = [start] + [node for node in nodes_to_visit if node != start]
    
    current_node = start
    unvisited = set(all_nodes) - {start}
    path = [start]
    total_distance = 0
    
    while unvisited:
        # Find nearest unvisited node
        nearest_node = None
        min_distance = float('infinity')
        
        for node in unvisited:
            if node in graph.get(current_node, {}):
                distance = graph[current_node][node]
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node
        
        if nearest_node is None:
            # No direct connection found, break
            break
        
        # Move to nearest node
        path.append(nearest_node)
        total_distance += min_distance
        current_node = nearest_node
        unvisited.remove(nearest_node)
    
    # Return to start
    if current_node != start and start in graph.get(current_node, {}):
        path.append(start)
        total_distance += graph[current_node][start]
    
    return path, total_distance

def brute_force_tsp(graph: Dict[str, Dict[str, float]], start: str, 
                   nodes_to_visit: List[str]) -> Tuple[List[str], float]:
    """
    Solve TSP using brute force (for small instances).
    
    Args:
        graph: Adjacency dictionary
        start: Starting node
        nodes_to_visit: List of nodes to visit
    
    Returns:
        Tuple of (best_path, min_distance)
    """
    if len(nodes_to_visit) > 10:
        # Too many nodes for brute force, use nearest neighbor
        return nearest_neighbor_tsp(graph, start, nodes_to_visit)
    
    # Generate all permutations of nodes to visit
    best_path = []
    min_distance = float('infinity')
    
    for perm in itertools.permutations(nodes_to_visit):
        # Calculate total distance for this permutation
        current_distance = 0
        current_node = start
        path = [start]
        
        valid_path = True
        for next_node in perm:
            if next_node in graph.get(current_node, {}):
                current_distance += graph[current_node][next_node]
                path.append(next_node)
                current_node = next_node
            else:
                valid_path = False
                break
        
        # Return to start
        if valid_path and start in graph.get(current_node, {}):
            current_distance += graph[current_node][start]
            path.append(start)
            
            if current_distance < min_distance:
                min_distance = current_distance
                best_path = path
    
    return best_path, min_distance

def tsp_with_time_windows(graph: Dict[str, Dict[str, float]], start: str,
                         deliveries: List[Dict]) -> Tuple[List[str], float, List[Dict]]:
    """
    TSP solver considering time windows and priorities.
    
    Args:
        graph: Adjacency dictionary
        start: Starting node
        deliveries: List of delivery objects with location, time_window, priority
    
    Returns:
        Tuple of (path, total_distance, scheduled_deliveries)
    """
    if not deliveries:
        return [start], 0, []
    
    # Sort deliveries by priority (High=3, Normal=2, Low=1) and time window start
    priority_map = {'High': 3, 'Normal': 2, 'Low': 1}
    deliveries_sorted = sorted(deliveries, 
                              key=lambda d: (priority_map.get(d['priority'], 1), 
                                           d['timeWindow']['start']))
    
    # Use nearest neighbor with time window consideration
    current_node = start
    current_time = 0  # Start at time 0
    path = [start]
    total_distance = 0
    scheduled_deliveries = []
    unvisited = deliveries_sorted.copy()
    
    while unvisited:
        best_delivery = None
        best_distance = float('infinity')
        best_arrival_time = None
        
        for delivery in unvisited:
            location = delivery['location']
            if location in graph.get(current_node, {}):
                distance = graph[current_node][location]
                travel_time = distance / 50  # Assume 50 km/h average speed
                arrival_time = current_time + travel_time
                
                # Check if we can make it within time window
                if arrival_time <= delivery['timeWindow']['end']:
                    # Wait if we arrive too early
                    service_start = max(arrival_time, delivery['timeWindow']['start'])
                    
                    # Prefer deliveries with higher priority and earlier time windows
                    score = distance - (priority_map.get(delivery['priority'], 1) * 10)
                    
                    if score < best_distance:
                        best_distance = score
                        best_delivery = delivery
                        best_arrival_time = service_start
        
        if best_delivery is None:
            # No feasible delivery found, break
            break
        
        # Move to best delivery location
        location = best_delivery['location']
        actual_distance = graph[current_node][location]
        path.append(location)
        total_distance += actual_distance
        current_node = location
        current_time = best_arrival_time + 0.5  # Add 30 minutes service time
        
        # Add to scheduled deliveries
        scheduled_deliveries.append({
            **best_delivery,
            'scheduled_time': best_arrival_time,
            'distance_from_previous': actual_distance
        })
        
        unvisited.remove(best_delivery)
    
    # Return to start
    if current_node != start and start in graph.get(current_node, {}):
        path.append(start)
        total_distance += graph[current_node][start]
    
    return path, total_distance, scheduled_deliveries

def optimize_delivery_sequence(deliveries: List[Dict], graph: Dict[str, Dict[str, float]], 
                             start: str) -> List[Dict]:
    """
    Optimize the sequence of deliveries considering constraints.
    
    Args:
        deliveries: List of delivery objects
        graph: Adjacency dictionary
        start: Starting location
    
    Returns:
        List of optimized delivery sequence
    """
    if not deliveries:
        return []
    
    # Use TSP with time windows
    path, total_distance, scheduled_deliveries = tsp_with_time_windows(graph, start, deliveries)
    
    # Add sequence numbers and ETA
    for i, delivery in enumerate(scheduled_deliveries):
        delivery['sequence'] = i + 1
        delivery['eta'] = f"{int(delivery['scheduled_time'])}:{int((delivery['scheduled_time'] % 1) * 60):02d}"
    
    return scheduled_deliveries
