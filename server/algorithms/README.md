# Algorithm Documentation

This directory contains the core optimization algorithms used in OptiRoute.

## Algorithms Overview

### 1. Dijkstra's Algorithm (`dijkstra.py`)
- **Purpose**: Shortest path between two nodes
- **Time Complexity**: O(V² + E) with adjacency list
- **Space Complexity**: O(V)
- **Best for**: Guaranteed optimal paths, non-negative weights

### 2. A* Search (`astar.py`)
- **Purpose**: Heuristic-based shortest path
- **Time Complexity**: O(b^d) where b is branching factor, d is depth
- **Space Complexity**: O(b^d)
- **Best for**: Faster pathfinding with admissible heuristic

### 3. Bellman-Ford (`bellman_ford.py`)
- **Purpose**: Shortest path with negative edge detection
- **Time Complexity**: O(VE)
- **Space Complexity**: O(V)
- **Best for**: Graphs with negative weights, cycle detection

### 4. TSP Solver (`tsp_solver.py`)
- **Purpose**: Traveling Salesman Problem with time windows
- **Time Complexity**: O(n!) for brute force, O(n²) for heuristic
- **Space Complexity**: O(n)
- **Best for**: Multi-stop optimization with constraints

### 5. Knapsack Algorithm (`knapsack.py`)
- **Purpose**: Capacity-constrained selection
- **Time Complexity**: O(nW) for 0/1, O(n log n) for fractional
- **Space Complexity**: O(nW)
- **Best for**: Delivery selection with capacity limits

### 6. Scheduler (`scheduler.py`)
- **Purpose**: Adaptive algorithm selection
- **Time Complexity**: Depends on chosen algorithm
- **Space Complexity**: O(n)
- **Best for**: Dynamic optimization based on problem size

## Usage Examples

Each algorithm module provides both individual functions and integrated solutions for the OptiRoute system.