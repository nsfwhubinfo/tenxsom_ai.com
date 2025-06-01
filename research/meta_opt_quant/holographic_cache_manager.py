#!/usr/bin/env python3
"""
Holographic Cache Manager for META-OPT-QUANT
Implements persistent storage and retrieval of F-V-E optimization patterns
"""

import json
import hashlib
import sqlite3
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path

class HolographicCacheManager:
    """Manages holographic caching of optimization patterns"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "holographic_cache.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for pattern storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_hash TEXT UNIQUE NOT NULL,
                frequency REAL NOT NULL,
                vibration REAL NOT NULL,
                energy REAL NOT NULL,
                trajectory_data TEXT NOT NULL,
                performance_score REAL NOT NULL,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_hash TEXT NOT NULL,
                child_hash TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL NOT NULL,
                FOREIGN KEY (parent_hash) REFERENCES optimization_patterns(symbol_hash),
                FOREIGN KEY (child_hash) REFERENCES optimization_patterns(symbol_hash)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_hash ON optimization_patterns(symbol_hash);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_performance ON optimization_patterns(performance_score DESC);
        """)
        
        conn.commit()
        conn.close()
        
    def store_pattern(self, symbol_hash: str, F: float, V: float, E: float,
                     trajectory: np.ndarray, performance: float) -> bool:
        """Store an optimization pattern in the holographic cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert trajectory to JSON
            trajectory_json = json.dumps(trajectory.tolist())
            
            cursor.execute("""
                INSERT OR REPLACE INTO optimization_patterns 
                (symbol_hash, frequency, vibration, energy, trajectory_data, performance_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (symbol_hash, F, V, E, trajectory_json, performance))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing pattern: {e}")
            return False
            
    def retrieve_pattern(self, symbol_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific pattern by symbol hash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT frequency, vibration, energy, trajectory_data, performance_score
                FROM optimization_patterns
                WHERE symbol_hash = ?
            """, (symbol_hash,))
            
            row = cursor.fetchone()
            if row:
                # Update access count and timestamp
                cursor.execute("""
                    UPDATE optimization_patterns
                    SET access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE symbol_hash = ?
                """, (symbol_hash,))
                conn.commit()
                
                result = {
                    'F': row[0],
                    'V': row[1],
                    'E': row[2],
                    'trajectory': np.array(json.loads(row[3])),
                    'performance': row[4]
                }
                conn.close()
                return result
                
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error retrieving pattern: {e}")
            return None
            
    def find_similar_patterns(self, F: float, V: float, E: float, 
                            tolerance: float = 0.1, limit: int = 5) -> List[Dict[str, Any]]:
        """Find patterns similar to given F-V-E values"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate similarity using Euclidean distance in F-V-E space
            cursor.execute("""
                SELECT symbol_hash, frequency, vibration, energy, trajectory_data, performance_score,
                       SQRT(POW(frequency - ?, 2) + POW(vibration - ?, 2) + POW(energy - ?, 2)) as distance
                FROM optimization_patterns
                WHERE distance < ?
                ORDER BY performance_score DESC, distance ASC
                LIMIT ?
            """, (F, V, E, tolerance, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'symbol_hash': row[0],
                    'F': row[1],
                    'V': row[2],
                    'E': row[3],
                    'trajectory': np.array(json.loads(row[4])),
                    'performance': row[5],
                    'distance': row[6]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error finding similar patterns: {e}")
            return []
            
    def get_top_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top performing patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT symbol_hash, frequency, vibration, energy, trajectory_data, performance_score
                FROM optimization_patterns
                ORDER BY performance_score DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'symbol_hash': row[0],
                    'F': row[1],
                    'V': row[2],
                    'E': row[3],
                    'trajectory': np.array(json.loads(row[4])),
                    'performance': row[5]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting top patterns: {e}")
            return []
            
    def establish_relationship(self, parent_hash: str, child_hash: str,
                             relationship_type: str, strength: float) -> bool:
        """Establish a relationship between two patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pattern_relationships 
                (parent_hash, child_hash, relationship_type, strength)
                VALUES (?, ?, ?, ?)
            """, (parent_hash, child_hash, relationship_type, strength))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error establishing relationship: {e}")
            return False
            
    def get_related_patterns(self, symbol_hash: str, 
                           relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get patterns related to a given pattern"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if relationship_type:
                cursor.execute("""
                    SELECT p.symbol_hash, p.frequency, p.vibration, p.energy, 
                           p.trajectory_data, p.performance_score, r.relationship_type, r.strength
                    FROM optimization_patterns p
                    JOIN pattern_relationships r ON p.symbol_hash = r.child_hash
                    WHERE r.parent_hash = ? AND r.relationship_type = ?
                    ORDER BY r.strength DESC
                """, (symbol_hash, relationship_type))
            else:
                cursor.execute("""
                    SELECT p.symbol_hash, p.frequency, p.vibration, p.energy, 
                           p.trajectory_data, p.performance_score, r.relationship_type, r.strength
                    FROM optimization_patterns p
                    JOIN pattern_relationships r ON p.symbol_hash = r.child_hash
                    WHERE r.parent_hash = ?
                    ORDER BY r.strength DESC
                """, (symbol_hash,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'symbol_hash': row[0],
                    'F': row[1],
                    'V': row[2],
                    'E': row[3],
                    'trajectory': np.array(json.loads(row[4])),
                    'performance': row[5],
                    'relationship_type': row[6],
                    'relationship_strength': row[7]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting related patterns: {e}")
            return []
            
    def prune_cache(self, max_age_days: int = 30, min_access_count: int = 2):
        """Prune old or rarely accessed patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM optimization_patterns
                WHERE julianday('now') - julianday(last_accessed) > ?
                AND access_count < ?
            """, (max_age_days, min_access_count))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error pruning cache: {e}")
            return 0
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM optimization_patterns")
            pattern_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM pattern_relationships")
            relationship_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(performance_score) FROM optimization_patterns")
            avg_performance = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MAX(performance_score) FROM optimization_patterns")
            max_performance = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(access_count) FROM optimization_patterns")
            avg_access_count = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'pattern_count': pattern_count,
                'relationship_count': relationship_count,
                'avg_performance': avg_performance,
                'max_performance': max_performance,
                'avg_access_count': avg_access_count,
                'cache_size_mb': (self.db_path.stat().st_size / 1024 / 1024) if self.db_path.exists() else 0
            }
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    cache = HolographicCacheManager()
    
    # Test storing a pattern
    test_hash = hashlib.sha256(b"test_pattern").hexdigest()
    test_trajectory = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    
    success = cache.store_pattern(
        symbol_hash=test_hash,
        F=1.5,
        V=2.3,
        E=0.8,
        trajectory=test_trajectory,
        performance=0.95
    )
    
    print(f"Pattern stored: {success}")
    
    # Test retrieving
    pattern = cache.retrieve_pattern(test_hash)
    if pattern:
        print(f"Retrieved pattern: F={pattern['F']}, V={pattern['V']}, E={pattern['E']}")
    
    # Find similar patterns
    similar = cache.find_similar_patterns(F=1.4, V=2.2, E=0.9, tolerance=0.5)
    print(f"Found {len(similar)} similar patterns")
    
    # Get cache statistics
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")