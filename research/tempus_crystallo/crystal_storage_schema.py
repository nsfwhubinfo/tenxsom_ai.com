#!/usr/bin/env python3
"""
TEMPUS-CRYSTALLO Phase 0.3: Crystal Storage Schema Design and Validation
Addresses TC.2.1 design gaps for storage scalability and archiving strategies.
"""

import json
import sqlite3
import time
import zlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import random
import math

@dataclass
class CrystalStorageMetrics:
    """Performance metrics for crystal storage operations"""
    storage_size_bytes: int
    compression_ratio: float
    write_time_ms: float
    read_time_ms: float
    query_time_ms: float
    index_efficiency: float

class TemporalCrystalStorage:
    """
    Advanced storage schema for Temporal Crystal Signatures (TCS)
    Implements hierarchical archiving, compression, and query optimization
    """
    
    def __init__(self, storage_path: str = "crystal_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.active_db = self.storage_path / "active_crystals.db"
        self.archive_db = self.storage_path / "archived_crystals.db"
        
        self._init_databases()
        self._create_indices()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _init_databases(self):
        """Initialize SQLite databases with optimized schema"""
        
        # Active crystals schema (high-frequency access)
        active_schema = """
        CREATE TABLE IF NOT EXISTS active_crystals (
            crystal_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            archetype_classification TEXT NOT NULL,
            
            -- Core 17D lattice structure (compressed JSON)
            lattice_structure_compressed BLOB NOT NULL,
            
            -- Key metrics for fast querying
            fractal_dimension REAL NOT NULL,
            quantum_coherence REAL NOT NULL,
            success_probability REAL NOT NULL,
            
            -- Fundamental constants
            h_cognitive REAL NOT NULL,
            c_thought REAL NOT NULL,
            k_b_info REAL NOT NULL,
            g_semantic REAL NOT NULL,
            
            -- Performance metadata
            calculation_time_ms REAL,
            storage_size_bytes INTEGER,
            
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        );
        """
        
        # Archive crystals schema (long-term storage)
        archive_schema = """
        CREATE TABLE IF NOT EXISTS archived_crystals (
            crystal_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            archetype_classification TEXT NOT NULL,
            
            -- Highly compressed full crystal data
            full_crystal_data_compressed BLOB NOT NULL,
            
            -- Summary statistics only
            fractal_dimension REAL NOT NULL,
            quantum_coherence REAL NOT NULL,
            success_probability REAL NOT NULL,
            
            -- Archive metadata
            archived_at INTEGER DEFAULT (strftime('%s', 'now')),
            compression_ratio REAL,
            original_size_bytes INTEGER
        );
        """
        
        with sqlite3.connect(self.active_db) as conn:
            conn.execute(active_schema)
        
        with sqlite3.connect(self.archive_db) as conn:
            conn.execute(archive_schema)
    
    def _create_indices(self):
        """Create optimized indices for crystal queries"""
        
        active_indices = [
            "CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON active_crystals(agent_id, timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_archetype ON active_crystals(archetype_classification);",
            "CREATE INDEX IF NOT EXISTS idx_success_prob ON active_crystals(success_probability);",
            "CREATE INDEX IF NOT EXISTS idx_fractal_dim ON active_crystals(fractal_dimension);",
            "CREATE INDEX IF NOT EXISTS idx_quantum_coh ON active_crystals(quantum_coherence);"
        ]
        
        archive_indices = [
            "CREATE INDEX IF NOT EXISTS idx_arch_agent_timestamp ON archived_crystals(agent_id, timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_arch_archetype ON archived_crystals(archetype_classification);",
            "CREATE INDEX IF NOT EXISTS idx_arch_success_prob ON archived_crystals(success_probability);"
        ]
        
        with sqlite3.connect(self.active_db) as conn:
            for idx in active_indices:
                conn.execute(idx)
        
        with sqlite3.connect(self.archive_db) as conn:
            for idx in archive_indices:
                conn.execute(idx)
    
    def compress_crystal_data(self, crystal_data: Dict) -> bytes:
        """Compress crystal lattice structure using zlib"""
        json_str = json.dumps(crystal_data, separators=(',', ':'))
        return zlib.compress(json_str.encode('utf-8'))
    
    def decompress_crystal_data(self, compressed_data: bytes) -> Dict:
        """Decompress crystal lattice structure"""
        json_str = zlib.decompress(compressed_data).decode('utf-8')
        return json.loads(json_str)
    
    def store_crystal(self, crystal_signature: Dict) -> CrystalStorageMetrics:
        """Store temporal crystal signature with performance tracking"""
        start_time = time.time()
        
        # Compress lattice structure
        lattice_compressed = self.compress_crystal_data(
            crystal_signature['lattice_structure']
        )
        
        # Calculate compression metrics
        original_size = len(json.dumps(crystal_signature['lattice_structure']))
        compressed_size = len(lattice_compressed)
        compression_ratio = original_size / compressed_size
        
        # Store in active database
        with sqlite3.connect(self.active_db) as conn:
            conn.execute("""
                INSERT INTO active_crystals (
                    crystal_id, agent_id, timestamp, archetype_classification,
                    lattice_structure_compressed, fractal_dimension, quantum_coherence,
                    success_probability, h_cognitive, c_thought, k_b_info, g_semantic,
                    calculation_time_ms, storage_size_bytes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crystal_signature['crystal_id'],
                crystal_signature['agent_id'],
                crystal_signature['timestamp'],
                crystal_signature['archetype_classification'],
                lattice_compressed,
                crystal_signature['fractal_dimension'],
                crystal_signature['quantum_coherence'],
                crystal_signature['success_probability'],
                crystal_signature['fundamental_constants']['h_cognitive'],
                crystal_signature['fundamental_constants']['c_thought'],
                crystal_signature['fundamental_constants']['k_b_info'],
                crystal_signature['fundamental_constants']['g_semantic'],
                crystal_signature.get('calculation_time_ms', 0),
                compressed_size
            ))
        
        write_time = (time.time() - start_time) * 1000
        
        return CrystalStorageMetrics(
            storage_size_bytes=compressed_size,
            compression_ratio=compression_ratio,
            write_time_ms=write_time,
            read_time_ms=0,
            query_time_ms=0,
            index_efficiency=1.0
        )
    
    def retrieve_crystal(self, crystal_id: str) -> Optional[Dict]:
        """Retrieve crystal signature by ID with decompression"""
        start_time = time.time()
        
        # Check active database first
        with sqlite3.connect(self.active_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM active_crystals WHERE crystal_id = ?
            """, (crystal_id,))
            
            row = cursor.fetchone()
            if row:
                # Decompress lattice structure
                lattice_structure = self.decompress_crystal_data(
                    row['lattice_structure_compressed']
                )
                
                crystal = {
                    'crystal_id': row['crystal_id'],
                    'agent_id': row['agent_id'],
                    'timestamp': row['timestamp'],
                    'archetype_classification': row['archetype_classification'],
                    'lattice_structure': lattice_structure,
                    'fractal_dimension': row['fractal_dimension'],
                    'quantum_coherence': row['quantum_coherence'],
                    'success_probability': row['success_probability'],
                    'fundamental_constants': {
                        'h_cognitive': row['h_cognitive'],
                        'c_thought': row['c_thought'],
                        'k_b_info': row['k_b_info'],
                        'g_semantic': row['g_semantic']
                    }
                }
                
                read_time = (time.time() - start_time) * 1000
                return crystal
        
        # Check archive database
        with sqlite3.connect(self.archive_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM archived_crystals WHERE crystal_id = ?
            """, (crystal_id,))
            
            row = cursor.fetchone()
            if row:
                # Decompress full crystal data
                crystal = self.decompress_crystal_data(
                    row['full_crystal_data_compressed']
                )
                return crystal
        
        return None
    
    def query_crystals(self, 
                      agent_id: Optional[str] = None,
                      archetype: Optional[str] = None,
                      min_success_prob: Optional[float] = None,
                      time_range: Optional[tuple] = None,
                      limit: int = 100) -> List[Dict]:
        """Query crystals with optimized filtering"""
        start_time = time.time()
        
        conditions = []
        params = []
        
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        
        if archetype:
            conditions.append("archetype_classification = ?")
            params.append(archetype)
        
        if min_success_prob:
            conditions.append("success_probability >= ?")
            params.append(min_success_prob)
        
        if time_range:
            conditions.append("timestamp BETWEEN ? AND ?")
            params.extend(time_range)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT crystal_id, agent_id, timestamp, archetype_classification,
                   fractal_dimension, quantum_coherence, success_probability
            FROM active_crystals 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        
        with sqlite3.connect(self.active_db) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute(query, params).fetchall()
        
        query_time = (time.time() - start_time) * 1000
        
        return [dict(row) for row in results]
    
    def archive_old_crystals(self, days_threshold: int = 30) -> Dict:
        """Archive crystals older than threshold to compressed storage"""
        cutoff_timestamp = int(time.time()) - (days_threshold * 24 * 60 * 60)
        
        # Find crystals to archive
        with sqlite3.connect(self.active_db) as conn:
            conn.row_factory = sqlite3.Row
            old_crystals = conn.execute("""
                SELECT * FROM active_crystals WHERE timestamp < ?
            """, (cutoff_timestamp,)).fetchall()
        
        archived_count = 0
        total_compression_ratio = 0
        
        for crystal_row in old_crystals:
            # Reconstruct full crystal data
            lattice_structure = self.decompress_crystal_data(
                crystal_row['lattice_structure_compressed']
            )
            
            full_crystal = {
                'crystal_id': crystal_row['crystal_id'],
                'agent_id': crystal_row['agent_id'],
                'timestamp': crystal_row['timestamp'],
                'archetype_classification': crystal_row['archetype_classification'],
                'lattice_structure': lattice_structure,
                'fractal_dimension': crystal_row['fractal_dimension'],
                'quantum_coherence': crystal_row['quantum_coherence'],
                'success_probability': crystal_row['success_probability'],
                'fundamental_constants': {
                    'h_cognitive': crystal_row['h_cognitive'],
                    'c_thought': crystal_row['c_thought'],
                    'k_b_info': crystal_row['k_b_info'],
                    'g_semantic': crystal_row['g_semantic']
                }
            }
            
            # Compress full crystal data
            original_size = len(json.dumps(full_crystal))
            compressed_data = self.compress_crystal_data(full_crystal)
            compression_ratio = original_size / len(compressed_data)
            
            # Store in archive
            with sqlite3.connect(self.archive_db) as conn:
                conn.execute("""
                    INSERT INTO archived_crystals (
                        crystal_id, agent_id, timestamp, archetype_classification,
                        full_crystal_data_compressed, fractal_dimension, 
                        quantum_coherence, success_probability,
                        compression_ratio, original_size_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    crystal_row['crystal_id'],
                    crystal_row['agent_id'],
                    crystal_row['timestamp'],
                    crystal_row['archetype_classification'],
                    compressed_data,
                    crystal_row['fractal_dimension'],
                    crystal_row['quantum_coherence'],
                    crystal_row['success_probability'],
                    compression_ratio,
                    original_size
                ))
            
            # Remove from active storage
            with sqlite3.connect(self.active_db) as conn:
                conn.execute("DELETE FROM active_crystals WHERE crystal_id = ?", 
                           (crystal_row['crystal_id'],))
            
            archived_count += 1
            total_compression_ratio += compression_ratio
        
        avg_compression = (total_compression_ratio / archived_count) if archived_count > 0 else 0
        
        return {
            'archived_count': archived_count,
            'average_compression_ratio': avg_compression,
            'cutoff_timestamp': cutoff_timestamp
        }
    
    def get_storage_statistics(self) -> Dict:
        """Get comprehensive storage statistics"""
        stats = {}
        
        # Active database stats
        with sqlite3.connect(self.active_db) as conn:
            active_count = conn.execute("SELECT COUNT(*) FROM active_crystals").fetchone()[0]
            active_size = conn.execute("SELECT SUM(storage_size_bytes) FROM active_crystals").fetchone()[0] or 0
            
            archetype_dist = conn.execute("""
                SELECT archetype_classification, COUNT(*) as count
                FROM active_crystals
                GROUP BY archetype_classification
            """).fetchall()
        
        # Archive database stats
        with sqlite3.connect(self.archive_db) as conn:
            archive_count = conn.execute("SELECT COUNT(*) FROM archived_crystals").fetchone()[0]
            avg_compression = conn.execute("SELECT AVG(compression_ratio) FROM archived_crystals").fetchone()[0] or 0
        
        stats = {
            'active_crystals': {
                'count': active_count,
                'total_size_bytes': active_size,
                'avg_size_bytes': active_size / active_count if active_count > 0 else 0,
                'archetype_distribution': dict(archetype_dist)
            },
            'archived_crystals': {
                'count': archive_count,
                'average_compression_ratio': avg_compression
            },
            'total_crystals': active_count + archive_count,
            'storage_efficiency': {
                'compression_benefit': avg_compression,
                'active_to_archive_ratio': active_count / archive_count if archive_count > 0 else float('inf')
            }
        }
        
        return stats

def run_storage_validation():
    """Validate storage schema with performance testing"""
    print("=== TEMPUS-CRYSTALLO Phase 0.3: Storage Schema Validation ===\n")
    
    storage = TemporalCrystalStorage("test_crystal_storage")
    
    # Generate test crystal signatures
    test_crystals = []
    archetypes = ['Stable', 'Growth', 'Decay']
    
    for i in range(1000):
        crystal = {
            'crystal_id': f"crystal_{i:04d}",
            'agent_id': f"agent_{i % 10}",
            'timestamp': int(time.time()) - (i * 3600),  # One hour intervals
            'archetype_classification': archetypes[i % 3],
            'lattice_structure': {
                f'dim_{j}': random.random() for j in range(17)
            },
            'fractal_dimension': 2.0 + random.random(),
            'quantum_coherence': random.random(),
            'success_probability': random.random(),
            'fundamental_constants': {
                'h_cognitive': 1.054e-34 * (1 + 0.1 * random.gauss(0, 1)),
                'c_thought': 2.998e8 * (1 + 0.1 * random.gauss(0, 1)),
                'k_b_info': 1.381e-23 * (1 + 0.1 * random.gauss(0, 1)),
                'g_semantic': 6.674e-11 * (1 + 0.1 * random.gauss(0, 1))
            },
            'calculation_time_ms': 10 + 5 * random.random()
        }
        test_crystals.append(crystal)
    
    # Performance testing
    print("1. Storage Performance Testing...")
    storage_metrics = []
    
    for crystal in test_crystals[:100]:  # Test with 100 crystals
        metrics = storage.store_crystal(crystal)
        storage_metrics.append(metrics)
    
    avg_storage_time = sum(m.write_time_ms for m in storage_metrics) / len(storage_metrics)
    avg_compression = sum(m.compression_ratio for m in storage_metrics) / len(storage_metrics)
    avg_size = sum(m.storage_size_bytes for m in storage_metrics) / len(storage_metrics)
    
    print(f"   Average storage time: {avg_storage_time:.2f} ms")
    print(f"   Average compression ratio: {avg_compression:.2f}x")
    print(f"   Average storage size: {avg_size:.0f} bytes")
    
    # Query performance testing
    print("\n2. Query Performance Testing...")
    
    query_tests = [
        {'agent_id': 'agent_0'},
        {'archetype': 'Growth'},
        {'min_success_prob': 0.7},
        {'agent_id': 'agent_1', 'archetype': 'Stable'}
    ]
    
    for i, query_params in enumerate(query_tests):
        start_time = time.time()
        results = storage.query_crystals(**query_params)
        query_time = (time.time() - start_time) * 1000
        
        print(f"   Query {i+1} ({query_params}): {len(results)} results in {query_time:.2f} ms")
    
    # Archive testing
    print("\n3. Archive Performance Testing...")
    archive_result = storage.archive_old_crystals(days_threshold=1)
    
    print(f"   Archived {archive_result['archived_count']} crystals")
    print(f"   Average compression ratio: {archive_result['average_compression_ratio']:.2f}x")
    
    # Storage statistics
    print("\n4. Storage Statistics...")
    stats = storage.get_storage_statistics()
    
    print(f"   Total crystals: {stats['total_crystals']}")
    print(f"   Active crystals: {stats['active_crystals']['count']}")
    print(f"   Archived crystals: {stats['archived_crystals']['count']}")
    print(f"   Total storage: {stats['active_crystals']['total_size_bytes']} bytes")
    print(f"   Average crystal size: {stats['active_crystals']['avg_size_bytes']:.0f} bytes")
    
    # Production estimates
    print("\n5. Production Deployment Estimates...")
    
    crystals_per_agent_per_day = 100
    agents_count = 50
    daily_crystals = crystals_per_agent_per_day * agents_count
    yearly_crystals = daily_crystals * 365
    
    yearly_storage_gb = (yearly_crystals * avg_size) / (1024**3)
    compressed_storage_gb = yearly_storage_gb / avg_compression
    
    print(f"   Daily crystal generation: {daily_crystals:,}")
    print(f"   Yearly crystal generation: {yearly_crystals:,}")
    print(f"   Yearly storage (uncompressed): {yearly_storage_gb:.2f} GB")
    print(f"   Yearly storage (compressed): {compressed_storage_gb:.2f} GB")
    print(f"   Storage savings: {((yearly_storage_gb - compressed_storage_gb) / yearly_storage_gb) * 100:.1f}%")
    
    # Performance requirements validation
    print("\n6. Performance Requirements Validation...")
    max_acceptable_storage_time = 50  # ms
    max_acceptable_query_time = 100   # ms
    min_compression_ratio = 2.0
    
    storage_passed = avg_storage_time <= max_acceptable_storage_time
    compression_passed = avg_compression >= min_compression_ratio
    
    print(f"   Storage time requirement (<{max_acceptable_storage_time}ms): {'✓ PASS' if storage_passed else '✗ FAIL'}")
    print(f"   Compression requirement (>{min_compression_ratio}x): {'✓ PASS' if compression_passed else '✗ FAIL'}")
    
    # Cleanup
    import shutil
    shutil.rmtree("test_crystal_storage", ignore_errors=True)
    
    print(f"\n=== Phase 0.3 Storage Schema Validation Complete ===")
    
    return {
        'storage_performance': {
            'avg_storage_time_ms': avg_storage_time,
            'avg_compression_ratio': avg_compression,
            'avg_storage_size_bytes': avg_size
        },
        'production_estimates': {
            'yearly_storage_compressed_gb': compressed_storage_gb,
            'storage_savings_percent': ((yearly_storage_gb - compressed_storage_gb) / yearly_storage_gb) * 100
        },
        'requirements_validation': {
            'storage_time_passed': storage_passed,
            'compression_passed': compression_passed
        }
    }

if __name__ == "__main__":
    run_storage_validation()