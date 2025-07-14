from typing import List, Dict, Tuple

def knapsack_01(items: List[Dict], capacity: int) -> Tuple[List[Dict], int, int]:
    """
    0/1 Knapsack algorithm for delivery selection.
    
    Args:
        items: List of delivery items with 'load', 'profit', and other data
        capacity: Maximum capacity
    
    Returns:
        Tuple of (selected_items, total_value, total_weight)
    """
    if not items or capacity <= 0:
        return [], 0, 0
    
    n = len(items)
    
    # Create DP table
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            item = items[i-1]
            weight = item['load']
            value = item['profit']
            
            if weight <= w:
                # Can include this item
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)
            else:
                # Cannot include this item
                dp[i][w] = dp[i-1][w]
    
    # Backtrack to find selected items
    selected_items = []
    w = capacity
    total_value = dp[n][capacity]
    total_weight = 0
    
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            # This item was selected
            selected_items.append(items[i-1])
            total_weight += items[i-1]['load']
            w -= items[i-1]['load']
    
    selected_items.reverse()
    return selected_items, total_value, total_weight

def fractional_knapsack(items: List[Dict], capacity: int) -> Tuple[List[Dict], float, int]:
    """
    Fractional knapsack algorithm for delivery selection.
    
    Args:
        items: List of delivery items with 'load', 'profit', and other data
        capacity: Maximum capacity
    
    Returns:
        Tuple of (selected_items, total_value, total_weight)
    """
    if not items or capacity <= 0:
        return [], 0.0, 0
    
    # Calculate value-to-weight ratio
    for item in items:
        item['ratio'] = item['profit'] / item['load'] if item['load'] > 0 else 0
    
    # Sort by ratio in descending order
    sorted_items = sorted(items, key=lambda x: x['ratio'], reverse=True)
    
    selected_items = []
    total_value = 0.0
    total_weight = 0
    remaining_capacity = capacity
    
    for item in sorted_items:
        if remaining_capacity >= item['load']:
            # Take the whole item
            selected_items.append({**item, 'fraction': 1.0})
            total_value += item['profit']
            total_weight += item['load']
            remaining_capacity -= item['load']
        elif remaining_capacity > 0:
            # Take fraction of the item
            fraction = remaining_capacity / item['load']
            selected_items.append({**item, 'fraction': fraction})
            total_value += item['profit'] * fraction
            total_weight += item['load'] * fraction
            remaining_capacity = 0
            break
    
    return selected_items, total_value, total_weight

def optimize_delivery_selection(deliveries: List[Dict], capacity: int, 
                               algorithm: str = "01") -> Dict:
    """
    Optimize delivery selection based on capacity constraints.
    
    Args:
        deliveries: List of delivery objects
        capacity: Vehicle capacity
        algorithm: "01" for 0/1 knapsack, "fractional" for fractional knapsack
    
    Returns:
        Dictionary with optimization results
    """
    if not deliveries:
        return {
            'selected_deliveries': [],
            'total_value': 0,
            'total_weight': 0,
            'capacity_utilization': 0.0
        }
    
    # Prepare items for knapsack
    items = []
    for delivery in deliveries:
        items.append({
            'id': delivery['id'],
            'name': delivery['name'],
            'location': delivery['location'],
            'load': delivery['load'],
            'profit': delivery['profit'],
            'priority': delivery['priority'],
            'timeWindow': delivery['timeWindow']
        })
    
    if algorithm == "fractional":
        selected_items, total_value, total_weight = fractional_knapsack(items, capacity)
    else:
        selected_items, total_value, total_weight = knapsack_01(items, capacity)
    
    capacity_utilization = (total_weight / capacity) * 100 if capacity > 0 else 0
    
    return {
        'selected_deliveries': selected_items,
        'total_value': total_value,
        'total_weight': total_weight,
        'capacity_utilization': capacity_utilization,
        'remaining_capacity': capacity - total_weight
    }

def multi_constraint_knapsack(items: List[Dict], constraints: Dict) -> Tuple[List[Dict], float]:
    """
    Multi-constraint knapsack for complex delivery optimization.
    
    Args:
        items: List of delivery items
        constraints: Dictionary of constraint types and limits
    
    Returns:
        Tuple of (selected_items, total_value)
    """
    if not items or not constraints:
        return [], 0.0
    
    # For simplicity, use greedy approach for multi-constraint
    # In practice, this would need more sophisticated algorithms
    
    # Calculate efficiency score considering all constraints
    for item in items:
        score = item['profit']
        
        # Penalize based on constraint violations
        for constraint_type, limit in constraints.items():
            if constraint_type in item:
                utilization = item[constraint_type] / limit
                score *= (1 - utilization * 0.5)  # Penalize high utilization
        
        item['efficiency_score'] = score
    
    # Sort by efficiency score
    sorted_items = sorted(items, key=lambda x: x['efficiency_score'], reverse=True)
    
    selected_items = []
    total_value = 0.0
    current_usage = {constraint: 0 for constraint in constraints}
    
    for item in sorted_items:
        # Check if item fits within all constraints
        can_add = True
        for constraint_type, limit in constraints.items():
            if constraint_type in item:
                if current_usage[constraint_type] + item[constraint_type] > limit:
                    can_add = False
                    break
        
        if can_add:
            selected_items.append(item)
            total_value += item['profit']
            for constraint_type in constraints:
                if constraint_type in item:
                    current_usage[constraint_type] += item[constraint_type]
    
    return selected_items, total_value
