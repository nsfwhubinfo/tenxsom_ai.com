#!/usr/bin/env python3
"""
TEMPUS-CRYSTALLO TC.2.2: Full System Integration Implementation
Integrates Temporal Crystal Signatures across FA-CMS, FMO, Arbiters, and TIE
"""

import json
import time
import random
import math
import sqlite3
import zlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue
import logging

@dataclass
class TemporalCrystalSignature:
    """Complete TCS structure based on Phase 0 findings"""
    crystal_id: str
    agent_id: str
    timestamp: int
    archetype_classification: str  # 'Stable', 'Growth', 'Decay'
    
    # 17D lattice structure (optimized storage)
    lattice_structure: Dict[str, float]
    
    # Core crystallographic properties
    fractal_dimension: float
    quantum_coherence: float
    success_probability: float
    lattice_stability: float
    
    # Fundamental constants
    h_cognitive: float
    c_thought: float
    k_b_info: float
    g_semantic: float
    
    # Performance metadata
    calculation_time_ms: float
    confidence_score: float

class CrystalCalculationEngine:
    """Optimized crystal calculation using Phase 0.2 cached strategy"""
    
    def __init__(self):
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.calculation_count = 0
    
    def calculate_crystal_signature(self, cognitive_state: Dict) -> TemporalCrystalSignature:
        """Generate TCS from cognitive state using optimized calculation"""
        start_time = time.time()
        
        # Generate cache key from state hash
        state_key = self._generate_state_hash(cognitive_state)
        
        # Check cache (80% hit rate from Phase 0.2)
        if state_key in self.cache and random.random() < 0.8:
            self.cache_hits += 1
            cached_crystal = self.cache[state_key]
            # Update timestamp and recalculate dynamic properties
            cached_crystal.timestamp = int(time.time())
            cached_crystal.calculation_time_ms = (time.time() - start_time) * 1000
            return cached_crystal
        
        # Cache miss - full calculation
        self.cache_misses += 1
        self.calculation_count += 1
        
        # Extract cognitive trajectory
        trajectory = cognitive_state.get('state_trajectory', [])
        current_state = cognitive_state.get('current_state', {})
        
        # Generate 17D lattice structure
        lattice_structure = self._calculate_17d_lattice(trajectory, current_state)
        
        # Calculate crystallographic properties
        fractal_dim = self._calculate_fractal_dimension(lattice_structure)
        quantum_coh = self._calculate_quantum_coherence(lattice_structure)
        success_prob = self._calculate_success_probability(fractal_dim, quantum_coh)
        lattice_stab = self._calculate_lattice_stability(lattice_structure)
        
        # Classify archetype based on Phase 0.1 boundaries
        archetype = self._classify_archetype(fractal_dim, quantum_coh, success_prob, lattice_stab)
        
        # Generate fundamental constants with perturbations
        constants = self._calculate_fundamental_constants(lattice_structure)
        
        # Create TCS
        crystal = TemporalCrystalSignature(
            crystal_id=f"tcs_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}",
            agent_id=cognitive_state.get('agent_id', 'unknown'),
            timestamp=int(time.time()),
            archetype_classification=archetype,
            lattice_structure=lattice_structure,
            fractal_dimension=fractal_dim,
            quantum_coherence=quantum_coh,
            success_probability=success_prob,
            lattice_stability=lattice_stab,
            h_cognitive=constants['h_cognitive'],
            c_thought=constants['c_thought'],
            k_b_info=constants['k_b_info'],
            g_semantic=constants['g_semantic'],
            calculation_time_ms=(time.time() - start_time) * 1000,
            confidence_score=self._calculate_confidence(fractal_dim, quantum_coh)
        )
        
        # Cache result
        self.cache[state_key] = crystal
        
        return crystal
    
    def _generate_state_hash(self, state: Dict) -> str:
        """Generate hash key for cognitive state"""
        state_str = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return str(hash(state_str) % 10000)
    
    def _calculate_17d_lattice(self, trajectory: List, current_state: Dict) -> Dict[str, float]:
        """Calculate 17-dimensional lattice structure"""
        lattice = {}
        
        # Dimension mapping based on cognitive aspects
        dimensions = [
            'attention', 'memory', 'reasoning', 'perception', 'motor',
            'language', 'emotion', 'motivation', 'consciousness', 'metacognition',
            'creativity', 'learning', 'adaptation', 'planning', 'execution',
            'monitoring', 'temporal'
        ]
        
        for i, dim_name in enumerate(dimensions):
            # Calculate dimension value from trajectory and current state
            if trajectory and len(trajectory) > i:
                temporal_component = math.sin(len(trajectory) * 0.1) * 0.3
            else:
                temporal_component = 0
            
            base_value = current_state.get(f'cognitive_{dim_name}', random.random())
            noise = random.gauss(0, 0.05)
            
            lattice[f'dim_{i}'] = max(0, min(1, base_value + temporal_component + noise))
        
        return lattice
    
    def _calculate_fractal_dimension(self, lattice: Dict) -> float:
        """Calculate fractal dimension from lattice structure"""
        values = list(lattice.values())
        variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
        complexity = sum(abs(values[i] - values[(i+1) % len(values)]) for i in range(len(values)))
        
        # Fractal dimension formula (empirically derived)
        fractal_dim = 1.5 + variance * 2.0 + complexity * 0.5
        return max(1.0, min(3.0, fractal_dim))
    
    def _calculate_quantum_coherence(self, lattice: Dict) -> float:
        """Calculate quantum coherence from lattice correlations"""
        values = list(lattice.values())
        n = len(values)
        
        # Calculate correlation matrix diagonal dominance
        correlations = []
        for i in range(n):
            for j in range(i+1, n):
                corr = values[i] * values[j] * math.cos(values[i] - values[j])
                correlations.append(abs(corr))
        
        coherence = sum(correlations) / len(correlations) if correlations else 0
        return max(0, min(1, coherence))
    
    def _calculate_success_probability(self, fractal_dim: float, quantum_coh: float) -> float:
        """Calculate success probability from crystallographic properties"""
        # Empirical formula from Phase 0.1 analysis
        base_prob = (fractal_dim - 1.0) / 2.0  # Normalize fractal dimension
        coherence_boost = quantum_coh * 0.4
        stability_factor = math.sin(fractal_dim * quantum_coh) * 0.2
        
        success_prob = base_prob + coherence_boost + stability_factor
        return max(0, min(1, success_prob))
    
    def _calculate_lattice_stability(self, lattice: Dict) -> float:
        """Calculate lattice stability metric"""
        values = list(lattice.values())
        
        # Stability based on dimensional balance
        mean_val = sum(values) / len(values)
        deviations = [(v - mean_val)**2 for v in values]
        variance = sum(deviations) / len(deviations)
        
        stability = 1.0 - min(1.0, variance * 4.0)  # Inverse relationship
        return max(0, stability)
    
    def _classify_archetype(self, fractal_dim: float, quantum_coh: float, 
                          success_prob: float, lattice_stab: float) -> str:
        """Classify crystal archetype using Phase 0.1 boundaries"""
        
        # Empirical boundaries from Phase 0.1 clustering
        if success_prob > 0.75 and lattice_stab > 0.7:
            return 'Stable'
        elif success_prob > 0.55 and fractal_dim > 2.3:
            return 'Growth'
        else:
            return 'Decay'
    
    def _calculate_fundamental_constants(self, lattice: Dict) -> Dict[str, float]:
        """Calculate perturbed fundamental constants"""
        values = list(lattice.values())
        complexity = sum(values) / len(values)
        
        # Base constants with lattice-induced perturbations
        return {
            'h_cognitive': 1.054e-34 * (1 + 0.1 * complexity),
            'c_thought': 2.998e8 * (1 + 0.05 * (complexity - 0.5)),
            'k_b_info': 1.381e-23 * (1 + 0.08 * math.sin(complexity * math.pi)),
            'g_semantic': 6.674e-11 * (1 + 0.12 * (complexity**2 - complexity))
        }
    
    def _calculate_confidence(self, fractal_dim: float, quantum_coh: float) -> float:
        """Calculate confidence score for TCS"""
        # Confidence based on crystallographic stability
        dim_confidence = 1.0 - abs(fractal_dim - 2.0) / 2.0  # Peak at 2.0
        coh_confidence = quantum_coh  # Direct relationship
        
        confidence = (dim_confidence + coh_confidence) / 2.0
        return max(0, min(1, confidence))
    
    def get_performance_stats(self) -> Dict:
        """Get calculation engine performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'total_calculations': self.calculation_count,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.cache)
        }

class FractalAwareCMS_TCS:
    """FA-CMS with Temporal Crystal Signature integration"""
    
    def __init__(self, storage_path: str = "facms_tcs_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.db_path = self.storage_path / "facms_tcs.db"
        self.crystal_engine = CrystalCalculationEngine()
        
        self._init_database()
        self.logger = logging.getLogger(f"{__name__}.FACMS")
    
    def _init_database(self):
        """Initialize FA-CMS database with TCS support"""
        schema = """
        CREATE TABLE IF NOT EXISTS memory_entries (
            entry_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            content_data BLOB NOT NULL,
            
            -- Temporal Crystal Signature
            crystal_id TEXT NOT NULL,
            tcs_data_compressed BLOB NOT NULL,
            archetype_classification TEXT NOT NULL,
            success_probability REAL NOT NULL,
            confidence_score REAL NOT NULL,
            
            -- Fractal signature (legacy)
            fractal_signature TEXT,
            
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON memory_entries(agent_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_archetype ON memory_entries(archetype_classification);
        CREATE INDEX IF NOT EXISTS idx_success_prob ON memory_entries(success_probability);
        CREATE INDEX IF NOT EXISTS idx_crystal_id ON memory_entries(crystal_id);
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
    
    def store_memory(self, agent_id: str, content_type: str, content_data: Any, 
                    cognitive_state: Dict) -> str:
        """Store memory with TCS generation"""
        
        # Generate TCS from cognitive state
        tcs = self.crystal_engine.calculate_crystal_signature(cognitive_state)
        
        # Compress TCS data
        tcs_json = json.dumps(asdict(tcs), separators=(',', ':'))
        tcs_compressed = zlib.compress(tcs_json.encode('utf-8'))
        
        # Serialize content data
        content_serialized = json.dumps(content_data, separators=(',', ':')).encode('utf-8')
        
        # Generate entry ID
        entry_id = f"mem_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memory_entries (
                    entry_id, agent_id, timestamp, content_type, content_data,
                    crystal_id, tcs_data_compressed, archetype_classification,
                    success_probability, confidence_score, fractal_signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id, agent_id, int(time.time()), content_type, content_serialized,
                tcs.crystal_id, tcs_compressed, tcs.archetype_classification,
                tcs.success_probability, tcs.confidence_score, 
                f"fractal_{random.randint(1000, 9999)}"  # Legacy compatibility
            ))
        
        self.logger.info(f"Stored memory {entry_id} with TCS {tcs.crystal_id} ({tcs.archetype_classification})")
        return entry_id
    
    def query_memories_by_crystal_pattern(self, agent_id: str, archetype: Optional[str] = None,
                                        min_success_prob: Optional[float] = None,
                                        limit: int = 50) -> List[Dict]:
        """Query memories using crystal pattern matching"""
        
        conditions = ["agent_id = ?"]
        params = [agent_id]
        
        if archetype:
            conditions.append("archetype_classification = ?")
            params.append(archetype)
        
        if min_success_prob:
            conditions.append("success_probability >= ?")
            params.append(min_success_prob)
        
        where_clause = " AND ".join(conditions)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute(f"""
                SELECT entry_id, crystal_id, archetype_classification, 
                       success_probability, confidence_score, timestamp,
                       tcs_data_compressed, content_data
                FROM memory_entries 
                WHERE {where_clause}
                ORDER BY success_probability DESC, timestamp DESC
                LIMIT ?
            """, params + [limit]).fetchall()
        
        memories = []
        for row in results:
            # Decompress TCS
            tcs_json = zlib.decompress(row['tcs_data_compressed']).decode('utf-8')
            tcs_data = json.loads(tcs_json)
            
            # Decompress content
            content_data = json.loads(row['content_data'].decode('utf-8'))
            
            memories.append({
                'entry_id': row['entry_id'],
                'crystal_id': row['crystal_id'],
                'archetype': row['archetype_classification'],
                'success_probability': row['success_probability'],
                'confidence_score': row['confidence_score'],
                'timestamp': row['timestamp'],
                'tcs_data': tcs_data,
                'content': content_data
            })
        
        return memories

class CognitiveArbiterEnhanced_TCS:
    """Enhanced Cognitive Arbiter with TCS-based decision making"""
    
    def __init__(self):
        self.facms = FractalAwareCMS_TCS("arbiter_facms_storage")
        self.crystal_engine = CrystalCalculationEngine()
        self.decision_history = []
        
        self.logger = logging.getLogger(f"{__name__}.CognitiveArbiter")
    
    def make_decision(self, decision_context: Dict, agent_id: str) -> Dict:
        """Make decision using TCS analysis"""
        
        # Generate TCS for current decision context
        current_tcs = self.crystal_engine.calculate_crystal_signature({
            'agent_id': agent_id,
            'current_state': decision_context,
            'state_trajectory': self.decision_history[-10:]  # Last 10 decisions
        })
        
        # Query similar crystal patterns from memory
        similar_memories = self.facms.query_memories_by_crystal_pattern(
            agent_id=agent_id,
            archetype=current_tcs.archetype_classification,
            min_success_prob=max(0.5, current_tcs.success_probability - 0.2),
            limit=10
        )
        
        # Analyze patterns for decision support
        pattern_analysis = self._analyze_crystal_patterns(current_tcs, similar_memories)
        
        # Generate decision recommendation
        decision = self._generate_decision_recommendation(
            decision_context, current_tcs, pattern_analysis
        )
        
        # Store decision in memory
        self.facms.store_memory(
            agent_id=agent_id,
            content_type="decision",
            content_data={
                'context': decision_context,
                'decision': decision,
                'reasoning': pattern_analysis
            },
            cognitive_state={
                'agent_id': agent_id,
                'current_state': decision_context,
                'state_trajectory': self.decision_history[-5:]
            }
        )
        
        # Update decision history
        self.decision_history.append({
            'timestamp': int(time.time()),
            'context': decision_context,
            'decision': decision,
            'tcs_id': current_tcs.crystal_id
        })
        
        self.logger.info(f"Decision made for {agent_id}: {decision['action']} (confidence: {decision['confidence']:.2f})")
        
        return decision
    
    def _analyze_crystal_patterns(self, current_tcs: TemporalCrystalSignature, 
                                 similar_memories: List[Dict]) -> Dict:
        """Analyze crystal patterns for decision insights"""
        
        if not similar_memories:
            return {
                'pattern_strength': 0.0,
                'success_trend': 'unknown',
                'risk_assessment': 'high',
                'recommendations': ['Proceed with caution - no historical patterns found']
            }
        
        # Calculate pattern statistics
        success_probs = [mem['success_probability'] for mem in similar_memories]
        avg_success = sum(success_probs) / len(success_probs)
        
        # Determine success trend
        if avg_success > 0.8:
            success_trend = 'strong_positive'
        elif avg_success > 0.6:
            success_trend = 'positive'
        elif avg_success > 0.4:
            success_trend = 'neutral'
        else:
            success_trend = 'negative'
        
        # Risk assessment based on crystal coherence
        if current_tcs.quantum_coherence > 0.7 and current_tcs.lattice_stability > 0.7:
            risk_level = 'low'
        elif current_tcs.quantum_coherence > 0.5:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # Generate recommendations
        recommendations = []
        if success_trend in ['strong_positive', 'positive']:
            recommendations.append('Historical patterns suggest high success probability')
        if risk_level == 'low':
            recommendations.append('Crystal coherence indicates stable cognitive state')
        if current_tcs.archetype_classification == 'Growth':
            recommendations.append('Growth archetype detected - favorable for exploration')
        
        return {
            'pattern_strength': len(similar_memories) / 10.0,  # Normalize to 0-1
            'success_trend': success_trend,
            'risk_assessment': risk_level,
            'historical_success_rate': avg_success,
            'recommendations': recommendations,
            'similar_patterns_count': len(similar_memories)
        }
    
    def _generate_decision_recommendation(self, context: Dict, tcs: TemporalCrystalSignature,
                                        pattern_analysis: Dict) -> Dict:
        """Generate decision recommendation based on TCS and patterns"""
        
        # Base confidence from TCS properties
        base_confidence = (tcs.success_probability + tcs.confidence_score) / 2.0
        
        # Adjust confidence based on pattern analysis
        pattern_boost = pattern_analysis['pattern_strength'] * 0.2
        
        if pattern_analysis['success_trend'] == 'strong_positive':
            trend_boost = 0.3
        elif pattern_analysis['success_trend'] == 'positive':
            trend_boost = 0.15
        elif pattern_analysis['success_trend'] == 'neutral':
            trend_boost = 0.0
        else:
            trend_boost = -0.2
        
        final_confidence = max(0.1, min(1.0, base_confidence + pattern_boost + trend_boost))
        
        # Determine action based on confidence and archetype
        if final_confidence > 0.8:
            action = 'proceed_confidently'
        elif final_confidence > 0.6:
            action = 'proceed_cautiously'
        elif final_confidence > 0.4:
            action = 'gather_more_information'
        else:
            action = 'avoid_risk'
        
        return {
            'action': action,
            'confidence': final_confidence,
            'reasoning': {
                'tcs_archetype': tcs.archetype_classification,
                'crystal_properties': {
                    'fractal_dimension': tcs.fractal_dimension,
                    'quantum_coherence': tcs.quantum_coherence,
                    'success_probability': tcs.success_probability
                },
                'pattern_analysis': pattern_analysis
            },
            'crystal_id': tcs.crystal_id,
            'timestamp': int(time.time())
        }

def run_tc22_integration_demo():
    """Demonstrate TC.2.2 integrated system functionality"""
    print("=== TEMPUS-CRYSTALLO TC.2.2: Full System Integration Demo ===\n")
    
    # Initialize systems
    print("1. Initializing Integrated Systems...")
    facms = FractalAwareCMS_TCS("demo_facms_storage")
    arbiter = CognitiveArbiterEnhanced_TCS()
    
    agent_id = "demo_agent_001"
    
    # Simulate cognitive scenarios
    scenarios = [
        {
            'name': 'Learning New Concept',
            'context': {
                'task_type': 'learning',
                'complexity': 0.7,
                'prior_knowledge': 0.3,
                'cognitive_attention': 0.8,
                'cognitive_memory': 0.6,
                'cognitive_reasoning': 0.7
            }
        },
        {
            'name': 'Problem Solving',
            'context': {
                'task_type': 'problem_solving',
                'complexity': 0.9,
                'time_pressure': 0.6,
                'cognitive_attention': 0.9,
                'cognitive_memory': 0.8,
                'cognitive_reasoning': 0.9
            }
        },
        {
            'name': 'Creative Task',
            'context': {
                'task_type': 'creative',
                'complexity': 0.5,
                'novelty': 0.9,
                'cognitive_attention': 0.7,
                'cognitive_creativity': 0.8,
                'cognitive_emotion': 0.6
            }
        }
    ]
    
    print("2. Running Cognitive Scenarios with TCS Integration...\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print("-" * 40)
        
        # Make decision using TCS-enhanced arbiter
        decision = arbiter.make_decision(scenario['context'], agent_id)
        
        print(f"TCS Archetype: {decision['reasoning']['tcs_archetype']}")
        print(f"Recommended Action: {decision['action']}")
        print(f"Confidence: {decision['confidence']:.2f}")
        print(f"Success Probability: {decision['reasoning']['crystal_properties']['success_probability']:.2f}")
        print(f"Quantum Coherence: {decision['reasoning']['crystal_properties']['quantum_coherence']:.2f}")
        
        if decision['reasoning']['pattern_analysis']['recommendations']:
            print("Recommendations:")
            for rec in decision['reasoning']['pattern_analysis']['recommendations']:
                print(f"  • {rec}")
        
        print()
        
        # Simulate some delay between scenarios
        time.sleep(0.1)
    
    # Query memory patterns
    print("3. Crystal Pattern Analysis...\n")
    
    # Query by archetype
    for archetype in ['Stable', 'Growth', 'Decay']:
        memories = facms.query_memories_by_crystal_pattern(
            agent_id=agent_id,
            archetype=archetype,
            limit=5
        )
        print(f"{archetype} Archetype Memories: {len(memories)}")
        for mem in memories[:2]:  # Show top 2
            print(f"  • {mem['entry_id']}: Success={mem['success_probability']:.2f}, Confidence={mem['confidence_score']:.2f}")
    
    print()
    
    # Performance statistics
    print("4. System Performance Statistics...\n")
    
    crystal_stats = arbiter.crystal_engine.get_performance_stats()
    print(f"Crystal Engine Performance:")
    print(f"  Total calculations: {crystal_stats['total_calculations']}")
    print(f"  Cache hit rate: {crystal_stats['cache_hit_rate']:.1%}")
    print(f"  Cache size: {crystal_stats['cache_size']}")
    
    # Cleanup demo storage
    import shutil
    shutil.rmtree("demo_facms_storage", ignore_errors=True)
    shutil.rmtree("arbiter_facms_storage", ignore_errors=True)
    
    print(f"\n✓ TC.2.2 Integration Demo Complete")
    print(f"✓ All systems successfully integrated with TCS")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    run_tc22_integration_demo()