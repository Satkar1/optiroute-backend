#!/usr/bin/env python3
"""
Database module for OptiRoute - SQLite support with JSON fallback
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class DatabaseManager:
    """Manages SQLite database operations with JSON fallback"""
    
    def __init__(self, db_path: str = "optistore.db"):
        self.db_path = db_path
        self.use_db = self._init_database()
    
    def _init_database(self) -> bool:
        """Initialize SQLite database, return True if successful"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create deliveries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deliveries (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    time_window_start INTEGER NOT NULL,
                    time_window_end INTEGER NOT NULL,
                    priority TEXT NOT NULL,
                    load INTEGER NOT NULL,
                    profit INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create routes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_list TEXT NOT NULL,
                    total_distance REAL NOT NULL,
                    algorithm TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    capacity_used INTEGER NOT NULL,
                    efficiency REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            # Database initialization failed, fall back to JSON
            return False
    
    def save_delivery(self, delivery: Dict[str, Any]) -> bool:
        """Save delivery to database"""
        if not self.use_db:
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO deliveries 
                (id, name, location, time_window_start, time_window_end, priority, load, profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                delivery['id'],
                delivery['name'],
                delivery['location'],
                delivery['timeWindow']['start'],
                delivery['timeWindow']['end'],
                delivery['priority'],
                delivery['load'],
                delivery['profit']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            # Failed to save delivery, continue with JSON fallback
            return False
    
    def get_deliveries(self) -> List[Dict[str, Any]]:
        """Get all deliveries from database"""
        if not self.use_db:
            return self._load_json_deliveries()
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM deliveries ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            deliveries = []
            for row in rows:
                deliveries.append({
                    'id': row[0],
                    'name': row[1],
                    'location': row[2],
                    'timeWindow': {
                        'start': row[3],
                        'end': row[4]
                    },
                    'priority': row[5],
                    'load': row[6],
                    'profit': row[7]
                })
            
            conn.close()
            return deliveries
            
        except Exception as e:
            # Failed to get deliveries from DB, use JSON fallback
            return self._load_json_deliveries()
    
    def save_route(self, route_data: Dict[str, Any]) -> Optional[int]:
        """Save optimized route to database"""
        if not self.use_db:
            return None
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO routes 
                (route_list, total_distance, algorithm, execution_time, capacity_used, efficiency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                json.dumps(route_data['optimizedRoute']),
                route_data['metrics']['totalDistance'],
                route_data['algorithm'],
                route_data['executionTime'],
                route_data['metrics']['capacityUsed'],
                route_data['metrics']['efficiency']
            ))
            
            route_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return route_id
            
        except Exception as e:
            # Failed to save route to database
            return None
    
    def get_route_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get route optimization history"""
        if not self.use_db:
            return []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, route_list, total_distance, algorithm, execution_time, 
                       capacity_used, efficiency, created_at
                FROM routes 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            history = []
            
            for row in rows:
                history.append({
                    'id': row[0],
                    'route': json.loads(row[1]),
                    'totalDistance': row[2],
                    'algorithm': row[3],
                    'executionTime': row[4],
                    'capacityUsed': row[5],
                    'efficiency': row[6],
                    'createdAt': row[7]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            # Failed to get route history from database
            return []
    
    def _load_json_deliveries(self) -> List[Dict[str, Any]]:
        """Fallback to JSON file loading"""
        try:
            with open('data/deliveries.json', 'r') as f:
                data = json.load(f)
                return data.get('deliveries', [])
        except Exception as e:
            # Failed to load JSON deliveries
            return []

# Global database manager instance
db_manager = DatabaseManager()