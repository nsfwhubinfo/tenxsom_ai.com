#!/usr/bin/env python3
"""
Global Cache Manager for META-OPT-QUANT
Implements persistent cross-session pattern learning with cache warming
"""

import os
import json
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime, timedelta
import threading
import hashlib

from holographic_cache_manager import HolographicCacheManager

class GlobalCacheManager:
    """
    Singleton cache manager that maintains global optimization patterns
    across all META-OPT-QUANT sessions
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, global_cache_dir: str = "./global_meta_opt_cache"):
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
            
        self.global_cache_dir = Path(global_cache_dir)
        self.global_cache_dir.mkdir(exist_ok=True)
        
        # Main global cache
        self.cache = HolographicCacheManager(str(self.global_cache_dir))
        
        # Meta-learning statistics
        self.stats_file = self.global_cache_dir / "meta_learning_stats.json"
        self.pattern_evolution_db = self.global_cache_dir / "pattern_evolution.db"
        
        self._init_stats()
        self._init_evolution_tracking()
        
        # Cache warming parameters
        self.warm_cache_size = 100  # Number of top patterns to keep warm
        self.evolution_threshold = 0.8  # Minimum fitness for evolution tracking
        
        self._initialized = True
    
    def _init_stats(self):
        """Initialize or load meta-learning statistics"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                'total_sessions': 0,
                'total_optimizations': 0,
                'patterns_discovered': 0,
                'average_convergence_improvement': 0.0,
                'golden_ratio_discoveries': 0,
                'session_history': []
            }
            self._save_stats()
    
    def _init_evolution_tracking(self):
        """Initialize pattern evolution database"""
        conn = sqlite3.connect(self.pattern_evolution_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_hash TEXT,
                child_hash TEXT,
                generation INTEGER,
                mutation_type TEXT,
                fitness_improvement REAL,
                discovered_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                F_delta REAL,
                V_delta REAL,
                E_delta REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS convergence_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                problem_type TEXT,
                initial_iterations INTEGER,
                optimized_iterations INTEGER,
                improvement_percentage REAL,
                patterns_used INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _save_stats(self):
        """Save statistics to file"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def start_session(self, session_id: str = None) -> str:
        """Start a new optimization session"""
        if not session_id:
            session_id = hashlib.sha256(
                f"session_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
        
        self.stats['total_sessions'] += 1
        self.stats['session_history'].append({
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'patterns_at_start': self.cache.get_cache_stats()['pattern_count']
        })
        
        # Keep only last 100 sessions
        if len(self.stats['session_history']) > 100:
            self.stats['session_history'] = self.stats['session_history'][-100:]
        
        self._save_stats()
        return session_id
    
    def warm_cache(self, problem_signature: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Warm cache with relevant patterns for a given problem
        
        Args:
            problem_signature: Dictionary describing the optimization problem
            
        Returns:
            List of relevant cached patterns
        """
        # Extract problem characteristics
        dimensions = problem_signature.get('dimensions', 1)
        objective_type = problem_signature.get('objective_type', 'unknown')
        constraints = problem_signature.get('constraints', [])
        
        # Find similar problems in convergence history
        conn = sqlite3.connect(self.pattern_evolution_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT session_id, patterns_used
            FROM convergence_history
            WHERE problem_type = ?
            ORDER BY improvement_percentage DESC
            LIMIT 10
        """, (objective_type,))
        
        similar_sessions = cursor.fetchall()
        conn.close()
        
        # Get top patterns from similar successful sessions
        relevant_patterns = []
        
        # First, get patterns from similar problems
        if similar_sessions:
            pattern_limit = self.warm_cache_size // len(similar_sessions)
            for session_id, patterns_used in similar_sessions:
                patterns = self.cache.get_top_patterns(limit=pattern_limit)
                relevant_patterns.extend(patterns)
        
        # Then, get globally top patterns
        global_top = self.cache.get_top_patterns(limit=self.warm_cache_size // 2)
        relevant_patterns.extend(global_top)
        
        # Deduplicate by symbol_hash
        seen = set()
        unique_patterns = []
        for pattern in relevant_patterns:
            if pattern['symbol_hash'] not in seen:
                seen.add(pattern['symbol_hash'])
                unique_patterns.append(pattern)
        
        return unique_patterns[:self.warm_cache_size]
    
    def track_evolution(self, parent_pattern: Dict[str, Any], 
                       child_pattern: Dict[str, Any],
                       mutation_type: str = "optimization"):
        """Track pattern evolution for meta-learning"""
        if child_pattern['performance'] < self.evolution_threshold:
            return
            
        conn = sqlite3.connect(self.pattern_evolution_db)
        cursor = conn.cursor()
        
        # Calculate deltas
        F_delta = child_pattern['F'] - parent_pattern['F']
        V_delta = child_pattern['V'] - parent_pattern['V']
        E_delta = child_pattern['E'] - parent_pattern['E']
        fitness_improvement = child_pattern['performance'] - parent_pattern['performance']
        
        # Determine generation
        cursor.execute("""
            SELECT MAX(generation) FROM pattern_evolution
            WHERE child_hash = ?
        """, (parent_pattern['symbol_hash'],))
        
        parent_gen = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            INSERT INTO pattern_evolution
            (parent_hash, child_hash, generation, mutation_type, 
             fitness_improvement, F_delta, V_delta, E_delta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (parent_pattern['symbol_hash'], child_pattern['symbol_hash'],
              parent_gen + 1, mutation_type, fitness_improvement,
              F_delta, V_delta, E_delta))
        
        conn.commit()
        conn.close()
        
        # Check for golden ratio emergence
        phi = 1.618033988749895
        if abs(child_pattern['F'] * child_pattern['V'] / child_pattern['E'] - phi) < 0.1:
            self.stats['golden_ratio_discoveries'] += 1
            self._save_stats()
    
    def record_convergence(self, session_id: str, problem_type: str,
                          initial_iterations: int, optimized_iterations: int,
                          patterns_used: int):
        """Record convergence improvement for meta-learning analysis"""
        improvement_percentage = (
            (initial_iterations - optimized_iterations) / initial_iterations * 100
            if initial_iterations > 0 else 0
        )
        
        conn = sqlite3.connect(self.pattern_evolution_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO convergence_history
            (session_id, problem_type, initial_iterations, 
             optimized_iterations, improvement_percentage, patterns_used)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, problem_type, initial_iterations,
              optimized_iterations, improvement_percentage, patterns_used))
        
        conn.commit()
        conn.close()
        
        # Update global statistics
        self.stats['total_optimizations'] += 1
        
        # Update rolling average
        current_avg = self.stats['average_convergence_improvement']
        n = self.stats['total_optimizations']
        self.stats['average_convergence_improvement'] = (
            (current_avg * (n - 1) + improvement_percentage) / n
        )
        self._save_stats()
    
    def get_evolution_insights(self) -> Dict[str, Any]:
        """Analyze pattern evolution for insights"""
        conn = sqlite3.connect(self.pattern_evolution_db)
        cursor = conn.cursor()
        
        # Most successful mutation types
        cursor.execute("""
            SELECT mutation_type, AVG(fitness_improvement) as avg_improvement,
                   COUNT(*) as count
            FROM pattern_evolution
            WHERE fitness_improvement > 0
            GROUP BY mutation_type
            ORDER BY avg_improvement DESC
        """)
        
        mutation_success = cursor.fetchall()
        
        # Average F-V-E deltas for successful evolutions
        cursor.execute("""
            SELECT AVG(F_delta), AVG(V_delta), AVG(E_delta)
            FROM pattern_evolution
            WHERE fitness_improvement > 0.1
        """)
        
        avg_deltas = cursor.fetchone()
        
        # Generation depth statistics
        cursor.execute("""
            SELECT MAX(generation), AVG(generation)
            FROM pattern_evolution
        """)
        
        gen_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'successful_mutations': [
                {'type': m[0], 'avg_improvement': m[1], 'count': m[2]}
                for m in mutation_success
            ],
            'average_successful_deltas': {
                'F': avg_deltas[0] if avg_deltas[0] else 0,
                'V': avg_deltas[1] if avg_deltas[1] else 0,
                'E': avg_deltas[2] if avg_deltas[2] else 0
            },
            'max_generation_depth': gen_stats[0] if gen_stats[0] else 0,
            'avg_generation_depth': gen_stats[1] if gen_stats[1] else 0,
            'total_patterns': self.cache.get_cache_stats()['pattern_count'],
            'golden_ratio_discoveries': self.stats['golden_ratio_discoveries']
        }
    
    def suggest_hyperparameters(self, problem_type: str) -> Dict[str, Any]:
        """Suggest hyperparameters based on historical performance"""
        conn = sqlite3.connect(self.pattern_evolution_db)
        cursor = conn.cursor()
        
        # Get best performing sessions for this problem type
        cursor.execute("""
            SELECT patterns_used, optimized_iterations
            FROM convergence_history
            WHERE problem_type = ?
            ORDER BY improvement_percentage DESC
            LIMIT 5
        """, (problem_type,))
        
        best_sessions = cursor.fetchall()
        conn.close()
        
        if best_sessions:
            avg_patterns = sum(s[0] for s in best_sessions) / len(best_sessions)
            avg_iterations = sum(s[1] for s in best_sessions) / len(best_sessions)
            
            return {
                'suggested_max_iterations': int(avg_iterations * 1.2),
                'suggested_top_k': min(int(avg_patterns * 1.5), 10),
                'suggested_exploration_rate': 0.2 if avg_patterns > 5 else 0.3,
                'suggested_convergence_threshold': 0.001
            }
        else:
            # Default suggestions
            return {
                'suggested_max_iterations': 100,
                'suggested_top_k': 5,
                'suggested_exploration_rate': 0.3,
                'suggested_convergence_threshold': 0.001
            }
    
    def export_best_patterns(self, output_file: str, top_n: int = 50):
        """Export best patterns for analysis or transfer learning"""
        patterns = self.cache.get_top_patterns(limit=top_n)
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'meta_stats': self.stats,
            'evolution_insights': self.get_evolution_insights(),
            'patterns': []
        }
        
        for pattern in patterns:
            export_data['patterns'].append({
                'symbol_hash': pattern['symbol_hash'],
                'F': pattern['F'],
                'V': pattern['V'],
                'E': pattern['E'],
                'performance': pattern['performance'],
                'trajectory': pattern['trajectory'].tolist()
            })
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return len(patterns)


# Singleton instance getter
def get_global_cache() -> GlobalCacheManager:
    """Get the global cache manager instance"""
    return GlobalCacheManager()


if __name__ == "__main__":
    # Test global cache manager
    print("Testing Global Cache Manager")
    print("=" * 50)
    
    cache = get_global_cache()
    
    # Start a session
    session_id = cache.start_session()
    print(f"Started session: {session_id}")
    
    # Get insights
    insights = cache.get_evolution_insights()
    print(f"\nEvolution Insights:")
    print(f"  Total patterns: {insights['total_patterns']}")
    print(f"  Golden ratio discoveries: {insights['golden_ratio_discoveries']}")
    
    # Suggest hyperparameters
    suggestions = cache.suggest_hyperparameters("rosenbrock")
    print(f"\nSuggested hyperparameters for Rosenbrock:")
    for key, value in suggestions.items():
        print(f"  {key}: {value}")