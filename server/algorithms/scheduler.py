from typing import List, Dict, Tuple
import heapq

def greedy_scheduler(deliveries: List[Dict], capacity: int) -> Tuple[List[Dict], Dict]:
    """
    Greedy scheduling algorithm for delivery optimization.
    
    Args:
        deliveries: List of delivery objects
        capacity: Vehicle capacity
    
    Returns:
        Tuple of (scheduled_deliveries, metrics)
    """
    if not deliveries:
        return [], {'total_deliveries': 0, 'capacity_used': 0, 'efficiency': 0}
    
    # Sort by priority and time window start
    priority_map = {'High': 3, 'Normal': 2, 'Low': 1}
    sorted_deliveries = sorted(deliveries, 
                              key=lambda d: (priority_map.get(d['priority'], 1), 
                                           d['timeWindow']['start']),
                              reverse=True)
    
    scheduled = []
    current_capacity = 0
    current_time = 0
    
    for delivery in sorted_deliveries:
        # Check if delivery fits in capacity
        if current_capacity + delivery['load'] <= capacity:
            # Check if we can deliver within time window
            if current_time <= delivery['timeWindow']['end']:
                # Schedule delivery
                start_time = max(current_time, delivery['timeWindow']['start'])
                delivery['scheduled_time'] = start_time
                delivery['status'] = 'scheduled'
                
                scheduled.append(delivery)
                current_capacity += delivery['load']
                current_time = start_time + 0.5  # Add 30 minutes service time
            else:
                delivery['status'] = 'missed_window'
        else:
            delivery['status'] = 'capacity_exceeded'
    
    # Calculate metrics
    total_value = sum(d['profit'] for d in scheduled)
    capacity_utilization = (current_capacity / capacity) * 100 if capacity > 0 else 0
    
    metrics = {
        'total_deliveries': len(scheduled),
        'capacity_used': current_capacity,
        'capacity_utilization': capacity_utilization,
        'total_value': total_value,
        'efficiency': capacity_utilization * 0.6 + (len(scheduled) / len(deliveries)) * 40
    }
    
    return scheduled, metrics

def priority_scheduler(deliveries: List[Dict], time_limit: int) -> List[Dict]:
    """
    Priority-based scheduling with time constraints.
    
    Args:
        deliveries: List of delivery objects
        time_limit: Maximum time available
    
    Returns:
        List of scheduled deliveries
    """
    if not deliveries:
        return []
    
    # Create priority queue (min-heap, so negate priorities)
    priority_map = {'High': -3, 'Normal': -2, 'Low': -1}
    pq = []
    
    for delivery in deliveries:
        priority = priority_map.get(delivery['priority'], -1)
        # Use negative time window end for tiebreaking (earlier deadlines first)
        heapq.heappush(pq, (priority, -delivery['timeWindow']['end'], delivery))
    
    scheduled = []
    current_time = 0
    
    while pq and current_time < time_limit:
        _, _, delivery = heapq.heappop(pq)
        
        # Check if we can complete this delivery
        service_time = 0.5  # 30 minutes
        if current_time + service_time <= delivery['timeWindow']['end']:
            # Schedule delivery
            start_time = max(current_time, delivery['timeWindow']['start'])
            if start_time + service_time <= time_limit:
                delivery['scheduled_time'] = start_time
                delivery['completion_time'] = start_time + service_time
                delivery['status'] = 'scheduled'
                
                scheduled.append(delivery)
                current_time = start_time + service_time
        else:
            delivery['status'] = 'missed_deadline'
    
    return scheduled

def dp_scheduler(deliveries: List[Dict], capacity: int, time_limit: int) -> Tuple[List[Dict], int]:
    """
    Dynamic programming scheduler for optimal delivery selection.
    
    Args:
        deliveries: List of delivery objects
        capacity: Vehicle capacity
        time_limit: Maximum time available
    
    Returns:
        Tuple of (scheduled_deliveries, total_value)
    """
    if not deliveries:
        return [], 0
    
    n = len(deliveries)
    
    # Create DP table: dp[i][c][t] = max value using first i deliveries, capacity c, time t
    # For efficiency, we'll use a simplified 2D approach
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        delivery = deliveries[i-1]
        weight = delivery['load']
        value = delivery['profit']
        time_needed = 1  # Simplified: each delivery takes 1 time unit
        
        for c in range(capacity + 1):
            # Don't take this delivery
            dp[i][c] = dp[i-1][c]
            
            # Take this delivery if possible
            if weight <= c:
                dp[i][c] = max(dp[i][c], dp[i-1][c-weight] + value)
    
    # Backtrack to find selected deliveries
    selected = []
    c = capacity
    
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i-1][c]:
            selected.append(deliveries[i-1])
            c -= deliveries[i-1]['load']
    
    selected.reverse()
    
    # Add scheduling information
    current_time = 0
    for delivery in selected:
        start_time = max(current_time, delivery['timeWindow']['start'])
        delivery['scheduled_time'] = start_time
        delivery['status'] = 'scheduled'
        current_time = start_time + 0.5
    
    return selected, dp[n][capacity]

def adaptive_scheduler(deliveries: List[Dict], constraints: Dict) -> Dict:
    """
    Adaptive scheduler that chooses the best algorithm based on problem size.
    
    Args:
        deliveries: List of delivery objects
        constraints: Dictionary of constraints (capacity, time_limit, etc.)
    
    Returns:
        Dictionary with scheduling results
    """
    if not deliveries:
        return {
            'scheduled_deliveries': [],
            'algorithm_used': 'none',
            'total_value': 0,
            'metrics': {}
        }
    
    n = len(deliveries)
    capacity = constraints.get('capacity', 100)
    time_limit = constraints.get('time_limit', 480)  # 8 hours in minutes
    
    # Choose algorithm based on problem size
    if n <= 20:
        # Small problem: use DP for optimal solution
        scheduled, total_value = dp_scheduler(deliveries, capacity, time_limit)
        algorithm_used = 'dynamic_programming'
    elif n <= 100:
        # Medium problem: use greedy with good performance
        scheduled, metrics = greedy_scheduler(deliveries, capacity)
        total_value = metrics['total_value']
        algorithm_used = 'greedy'
    else:
        # Large problem: use priority-based for speed
        scheduled = priority_scheduler(deliveries, time_limit)
        total_value = sum(d['profit'] for d in scheduled)
        algorithm_used = 'priority_based'
    
    # Calculate final metrics
    total_load = sum(d['load'] for d in scheduled)
    capacity_utilization = (total_load / capacity) * 100 if capacity > 0 else 0
    
    final_metrics = {
        'total_deliveries': len(scheduled),
        'capacity_used': total_load,
        'capacity_utilization': capacity_utilization,
        'total_value': total_value,
        'algorithm_used': algorithm_used,
        'efficiency': min(100, capacity_utilization * 0.6 + (len(scheduled) / len(deliveries)) * 40)
    }
    
    return {
        'scheduled_deliveries': scheduled,
        'algorithm_used': algorithm_used,
        'total_value': total_value,
        'metrics': final_metrics
    }
