#!/usr/bin/env python3
"""
TEMPUS-CRYSTALLO TC.2.2: Complete System Integration
Full implementation across FA-CMS, FMO, Arbiters, and TIE with crystallographic consciousness
"""

import json
import time
import random
import math
import sqlite3
import zlib
import threading
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from collections import defaultdict, deque

# Import from previous implementation
from TC_2_2_Implementation import (
    TemporalCrystalSignature, CrystalCalculationEngine, 
    FractalAwareCMS_TCS, CognitiveArbiterEnhanced_TCS
)

class FractalMetaOntology_TCS:
    """FMO with Temporal Crystal Signature integration for knowledge representation"""
    
    def __init__(self, storage_path: str = "fmo_tcs_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.db_path = self.storage_path / "fmo_tcs.db"
        self.crystal_engine = CrystalCalculationEngine()
        
        # Knowledge graph with crystallographic annotations
        self.knowledge_graph = {}
        self.concept_crystals = {}  # concept_id -> TCS
        self.relation_crystals = {}  # (concept1, concept2) -> TCS
        
        self._init_database()
        self.logger = logging.getLogger(f"{__name__}.FMO")
    
    def _init_database(self):
        """Initialize FMO database with TCS support"""
        schema = """
        CREATE TABLE IF NOT EXISTS concepts (
            concept_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            definition TEXT,
            concept_type TEXT NOT NULL,
            
            -- Temporal Crystal Signature
            crystal_id TEXT NOT NULL,
            tcs_data_compressed BLOB NOT NULL,
            archetype_classification TEXT NOT NULL,
            epistemic_confidence REAL NOT NULL,
            
            -- Knowledge graph properties
            parent_concepts TEXT,  -- JSON list
            child_concepts TEXT,   -- JSON list
            related_concepts TEXT, -- JSON list
            
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now'))
        );
        
        CREATE TABLE IF NOT EXISTS relations (
            relation_id TEXT PRIMARY KEY,
            concept1_id TEXT NOT NULL,
            concept2_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            strength REAL NOT NULL,
            
            -- Relational Crystal Signature
            crystal_id TEXT NOT NULL,
            tcs_data_compressed BLOB NOT NULL,
            archetype_classification TEXT NOT NULL,
            coherence_score REAL NOT NULL,
            
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_concept_archetype ON concepts(archetype_classification);
        CREATE INDEX IF NOT EXISTS idx_relation_archetype ON relations(archetype_classification);
        CREATE INDEX IF NOT EXISTS idx_concept_confidence ON concepts(epistemic_confidence);
        CREATE INDEX IF NOT EXISTS idx_relation_coherence ON relations(coherence_score);
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
    
    def add_concept(self, name: str, definition: str, concept_type: str,
                   knowledge_context: Dict) -> str:
        """Add concept with crystallographic knowledge representation"""
        
        # Generate TCS for concept
        concept_state = {
            'agent_id': 'fmo_system',
            'current_state': {
                'concept_complexity': len(definition.split()) / 100.0,
                'abstraction_level': self._calculate_abstraction_level(definition),
                'semantic_density': self._calculate_semantic_density(name, definition),
                'cognitive_reasoning': 0.8,  # FMO is reasoning-heavy
                'cognitive_language': 0.9,   # Language processing
                'cognitive_memory': 0.7      # Knowledge storage
            },
            'state_trajectory': [asdict(tcs) for tcs in list(self.concept_crystals.values())[-5:]]  # Recent concepts
        }
        
        tcs = self.crystal_engine.calculate_crystal_signature(concept_state)
        
        # Generate concept ID
        concept_id = f"concept_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
        
        # Store concept with TCS
        tcs_compressed = zlib.compress(json.dumps(asdict(tcs), separators=(',', ':')).encode('utf-8'))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO concepts (
                    concept_id, name, definition, concept_type,
                    crystal_id, tcs_data_compressed, archetype_classification,
                    epistemic_confidence, parent_concepts, child_concepts, related_concepts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                concept_id, name, definition, concept_type,
                tcs.crystal_id, tcs_compressed, tcs.archetype_classification,
                tcs.confidence_score, "[]", "[]", "[]"
            ))
        
        # Update knowledge graph
        self.knowledge_graph[concept_id] = {
            'name': name,
            'definition': definition,
            'type': concept_type,
            'tcs': tcs,
            'relations': {}
        }
        self.concept_crystals[concept_id] = tcs
        
        self.logger.info(f"Added concept '{name}' with TCS {tcs.crystal_id} ({tcs.archetype_classification})")
        return concept_id
    
    def add_relation(self, concept1_id: str, concept2_id: str, relation_type: str,
                    strength: float) -> str:
        """Add relation with crystallographic coherence analysis"""
        
        # Get concept TCS data
        concept1_tcs = self.concept_crystals.get(concept1_id)
        concept2_tcs = self.concept_crystals.get(concept2_id)
        
        if not concept1_tcs or not concept2_tcs:
            raise ValueError("Both concepts must exist before creating relation")
        
        # Generate relational TCS
        relation_state = {
            'agent_id': 'fmo_system',
            'current_state': {
                'concept1_coherence': concept1_tcs.quantum_coherence,
                'concept2_coherence': concept2_tcs.quantum_coherence,
                'archetype_compatibility': self._calculate_archetype_compatibility(
                    concept1_tcs.archetype_classification, 
                    concept2_tcs.archetype_classification
                ),
                'relation_strength': strength,
                'cognitive_reasoning': 0.9,
                'cognitive_language': 0.8
            }
        }
        
        relation_tcs = self.crystal_engine.calculate_crystal_signature(relation_state)
        
        # Generate relation ID
        relation_id = f"rel_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
        
        # Store relation
        tcs_compressed = zlib.compress(json.dumps(asdict(relation_tcs), separators=(',', ':')).encode('utf-8'))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO relations (
                    relation_id, concept1_id, concept2_id, relation_type, strength,
                    crystal_id, tcs_data_compressed, archetype_classification, coherence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relation_id, concept1_id, concept2_id, relation_type, strength,
                relation_tcs.crystal_id, tcs_compressed, relation_tcs.archetype_classification,
                relation_tcs.quantum_coherence
            ))
        
        # Update knowledge graph
        if concept1_id in self.knowledge_graph:
            self.knowledge_graph[concept1_id]['relations'][concept2_id] = {
                'type': relation_type,
                'strength': strength,
                'tcs': relation_tcs
            }
        
        self.relation_crystals[(concept1_id, concept2_id)] = relation_tcs
        
        self.logger.info(f"Added relation {relation_type} between concepts with coherence {relation_tcs.quantum_coherence:.2f}")
        return relation_id
    
    def query_concepts_by_crystal_properties(self, archetype: Optional[str] = None,
                                           min_confidence: Optional[float] = None,
                                           limit: int = 20) -> List[Dict]:
        """Query concepts using crystallographic properties"""
        
        conditions = []
        params = []
        
        if archetype:
            conditions.append("archetype_classification = ?")
            params.append(archetype)
        
        if min_confidence:
            conditions.append("epistemic_confidence >= ?")
            params.append(min_confidence)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute(f"""
                SELECT concept_id, name, definition, concept_type,
                       crystal_id, archetype_classification, epistemic_confidence,
                       tcs_data_compressed
                FROM concepts 
                WHERE {where_clause}
                ORDER BY epistemic_confidence DESC
                LIMIT ?
            """, params + [limit]).fetchall()
        
        concepts = []
        for row in results:
            # Decompress TCS
            tcs_json = zlib.decompress(row['tcs_data_compressed']).decode('utf-8')
            tcs_data = json.loads(tcs_json)
            
            concepts.append({
                'concept_id': row['concept_id'],
                'name': row['name'],
                'definition': row['definition'],
                'concept_type': row['concept_type'],
                'crystal_id': row['crystal_id'],
                'archetype': row['archetype_classification'],
                'epistemic_confidence': row['epistemic_confidence'],
                'tcs_data': tcs_data
            })
        
        return concepts
    
    def _calculate_abstraction_level(self, definition: str) -> float:
        """Calculate concept abstraction level"""
        abstract_words = ['concept', 'idea', 'principle', 'theory', 'abstract', 'meta']
        concrete_words = ['object', 'physical', 'tangible', 'specific', 'instance']
        
        words = definition.lower().split()
        abstract_count = sum(1 for word in words if any(abs_word in word for abs_word in abstract_words))
        concrete_count = sum(1 for word in words if any(con_word in word for con_word in concrete_words))
        
        if abstract_count + concrete_count == 0:
            return 0.5  # Neutral
        
        return abstract_count / (abstract_count + concrete_count)
    
    def _calculate_semantic_density(self, name: str, definition: str) -> float:
        """Calculate semantic density of concept"""
        unique_words = set(definition.lower().split())
        total_words = len(definition.split())
        
        if total_words == 0:
            return 0.0
        
        density = len(unique_words) / total_words
        return min(1.0, density * 1.5)  # Scale factor
    
    def _calculate_archetype_compatibility(self, archetype1: str, archetype2: str) -> float:
        """Calculate compatibility between concept archetypes"""
        compatibility_matrix = {
            ('Stable', 'Stable'): 0.9,
            ('Stable', 'Growth'): 0.7,
            ('Stable', 'Decay'): 0.3,
            ('Growth', 'Growth'): 0.8,
            ('Growth', 'Decay'): 0.5,
            ('Decay', 'Decay'): 0.6
        }
        
        key = (archetype1, archetype2)
        reverse_key = (archetype2, archetype1)
        
        return compatibility_matrix.get(key, compatibility_matrix.get(reverse_key, 0.5))

class TenxsomIntelligenceEngine_TCS:
    """TIE with Temporal Crystal Signature monitoring and anomaly detection"""
    
    def __init__(self):
        self.crystal_engine = CrystalCalculationEngine()
        self.monitoring_buffer = deque(maxlen=1000)  # Rolling buffer of TCS
        self.anomaly_threshold = 0.3  # Quantum coherence threshold
        self.anomaly_history = []
        
        # System health metrics
        self.system_metrics = {
            'total_crystals_processed': 0,
            'anomalies_detected': 0,
            'avg_quantum_coherence': 0.0,
            'archetype_distribution': defaultdict(int)
        }
        
        self.logger = logging.getLogger(f"{__name__}.TIE")
    
    def monitor_system_state(self, system_states: Dict[str, Dict]) -> Dict:
        """Monitor system state using crystallographic analysis"""
        
        # Generate system-wide TCS
        combined_state = {
            'agent_id': 'tie_monitor',
            'current_state': self._aggregate_system_states(system_states),
            'state_trajectory': [asdict(tcs) for tcs in list(self.monitoring_buffer)[-10:]]
        }
        
        system_tcs = self.crystal_engine.calculate_crystal_signature(combined_state)
        
        # Add to monitoring buffer
        self.monitoring_buffer.append(system_tcs)
        
        # Update metrics
        self.system_metrics['total_crystals_processed'] += 1
        self.system_metrics['archetype_distribution'][system_tcs.archetype_classification] += 1
        
        # Calculate rolling average coherence
        recent_coherences = [tcs.quantum_coherence for tcs in list(self.monitoring_buffer)[-50:]]
        self.system_metrics['avg_quantum_coherence'] = sum(recent_coherences) / len(recent_coherences)
        
        # Anomaly detection
        anomaly_detected = self._detect_anomalies(system_tcs)
        
        if anomaly_detected:
            self.system_metrics['anomalies_detected'] += 1
            self._handle_anomaly(system_tcs, system_states)
        
        # Generate monitoring report
        monitoring_report = {
            'system_tcs': asdict(system_tcs),
            'anomaly_detected': anomaly_detected,
            'system_health': self._calculate_system_health(),
            'recommendations': self._generate_system_recommendations(system_tcs),
            'timestamp': int(time.time())
        }
        
        self.logger.info(f"System monitoring: {system_tcs.archetype_classification} archetype, "
                        f"coherence={system_tcs.quantum_coherence:.2f}, "
                        f"anomaly={'YES' if anomaly_detected else 'NO'}")
        
        return monitoring_report
    
    def _aggregate_system_states(self, system_states: Dict[str, Dict]) -> Dict:
        """Aggregate states from all system components"""
        aggregated = {
            'facms_health': 0.0,
            'fmo_health': 0.0,
            'arbiter_health': 0.0,
            'overall_load': 0.0,
            'cognitive_reasoning': 0.0,
            'cognitive_memory': 0.0,
            'cognitive_language': 0.0
        }
        
        # FA-CMS metrics
        if 'facms' in system_states:
            facms_state = system_states['facms']
            aggregated['facms_health'] = facms_state.get('memory_utilization', 0.5)
            aggregated['cognitive_memory'] = facms_state.get('access_efficiency', 0.7)
        
        # FMO metrics
        if 'fmo' in system_states:
            fmo_state = system_states['fmo']
            aggregated['fmo_health'] = fmo_state.get('knowledge_coherence', 0.6)
            aggregated['cognitive_language'] = fmo_state.get('semantic_processing', 0.8)
        
        # Arbiter metrics
        if 'arbiter' in system_states:
            arbiter_state = system_states['arbiter']
            aggregated['arbiter_health'] = arbiter_state.get('decision_confidence', 0.7)
            aggregated['cognitive_reasoning'] = arbiter_state.get('reasoning_quality', 0.8)
        
        # Overall system load
        component_loads = [aggregated['facms_health'], aggregated['fmo_health'], aggregated['arbiter_health']]
        aggregated['overall_load'] = sum(component_loads) / len(component_loads)
        
        return aggregated
    
    def _detect_anomalies(self, current_tcs: TemporalCrystalSignature) -> bool:
        """Detect anomalies using crystallographic patterns"""
        
        if len(self.monitoring_buffer) < 10:
            return False  # Need baseline
        
        # Quantum coherence anomaly
        recent_coherences = [tcs.quantum_coherence for tcs in list(self.monitoring_buffer)[-10:]]
        avg_coherence = sum(recent_coherences) / len(recent_coherences)
        
        if current_tcs.quantum_coherence < avg_coherence - 0.3:
            return True
        
        # Archetype shift anomaly
        recent_archetypes = [tcs.archetype_classification for tcs in list(self.monitoring_buffer)[-5:]]
        if all(arch != current_tcs.archetype_classification for arch in recent_archetypes):
            return True
        
        # Success probability drop
        if current_tcs.success_probability < 0.3:
            return True
        
        return False
    
    def _handle_anomaly(self, anomaly_tcs: TemporalCrystalSignature, system_states: Dict):
        """Handle detected anomaly"""
        anomaly_record = {
            'timestamp': int(time.time()),
            'tcs_id': anomaly_tcs.crystal_id,
            'archetype': anomaly_tcs.archetype_classification,
            'quantum_coherence': anomaly_tcs.quantum_coherence,
            'success_probability': anomaly_tcs.success_probability,
            'system_states': system_states,
            'severity': self._calculate_anomaly_severity(anomaly_tcs)
        }
        
        self.anomaly_history.append(anomaly_record)
        
        self.logger.warning(f"ANOMALY DETECTED: {anomaly_record['severity']} severity, "
                           f"TCS {anomaly_tcs.crystal_id}, coherence={anomaly_tcs.quantum_coherence:.2f}")
    
    def _calculate_anomaly_severity(self, tcs: TemporalCrystalSignature) -> str:
        """Calculate anomaly severity level"""
        if tcs.quantum_coherence < 0.2 or tcs.success_probability < 0.2:
            return 'CRITICAL'
        elif tcs.quantum_coherence < 0.4 or tcs.success_probability < 0.4:
            return 'HIGH'
        elif tcs.quantum_coherence < 0.6:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_system_health(self) -> Dict:
        """Calculate overall system health metrics"""
        if not self.monitoring_buffer:
            return {'overall_score': 0.0, 'status': 'UNKNOWN'}
        
        recent_tcs = list(self.monitoring_buffer)[-20:]  # Last 20 measurements
        
        avg_coherence = sum(tcs.quantum_coherence for tcs in recent_tcs) / len(recent_tcs)
        avg_success = sum(tcs.success_probability for tcs in recent_tcs) / len(recent_tcs)
        
        # Archetype stability (prefer stable or growth)
        stable_count = sum(1 for tcs in recent_tcs if tcs.archetype_classification in ['Stable', 'Growth'])
        archetype_health = stable_count / len(recent_tcs)
        
        # Overall health score
        health_score = (avg_coherence * 0.4 + avg_success * 0.4 + archetype_health * 0.2)
        
        if health_score > 0.8:
            status = 'EXCELLENT'
        elif health_score > 0.6:
            status = 'GOOD'
        elif health_score > 0.4:
            status = 'FAIR'
        else:
            status = 'POOR'
        
        return {
            'overall_score': health_score,
            'status': status,
            'avg_coherence': avg_coherence,
            'avg_success_probability': avg_success,
            'archetype_stability': archetype_health
        }
    
    def _generate_system_recommendations(self, current_tcs: TemporalCrystalSignature) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        if current_tcs.quantum_coherence < 0.5:
            recommendations.append("Reduce system cognitive load to improve coherence")
        
        if current_tcs.archetype_classification == 'Decay':
            recommendations.append("Investigate system degradation patterns")
        
        if current_tcs.success_probability < 0.6:
            recommendations.append("Review recent decision patterns and knowledge updates")
        
        if len(self.anomaly_history) > 5:  # Recent anomalies
            recent_anomalies = [a for a in self.anomaly_history if a['timestamp'] > time.time() - 3600]
            if len(recent_anomalies) > 2:
                recommendations.append("Consider system maintenance - multiple recent anomalies detected")
        
        return recommendations

def run_complete_integration_demo():
    """Demonstrate complete TEMPUS-CRYSTALLO system integration"""
    print("=== TEMPUS-CRYSTALLO Complete System Integration Demo ===\n")
    
    # Initialize all systems
    print("1. Initializing Complete Integrated System...")
    facms = FractalAwareCMS_TCS("complete_facms_storage")
    fmo = FractalMetaOntology_TCS("complete_fmo_storage")
    arbiter = CognitiveArbiterEnhanced_TCS()
    tie = TenxsomIntelligenceEngine_TCS()
    
    agent_id = "integration_agent_001"
    
    print("2. Building Knowledge Base with Crystallographic Annotations...")
    
    # Add concepts to FMO
    concepts = [
        ("Consciousness", "The state of being aware and able to think", "abstract"),
        ("Learning", "The process of acquiring knowledge through experience", "process"),
        ("Memory", "The faculty by which information is stored and retrieved", "cognitive_function"),
        ("Decision", "A conclusion reached after consideration", "process"),
        ("Pattern", "A repeated decorative design or sequence", "structure")
    ]
    
    concept_ids = []
    for name, definition, concept_type in concepts:
        concept_id = fmo.add_concept(name, definition, concept_type, {})
        concept_ids.append(concept_id)
    
    # Add relations between concepts
    relations = [
        (0, 1, "enables", 0.8),  # Consciousness enables Learning
        (1, 2, "requires", 0.9),  # Learning requires Memory
        (2, 3, "supports", 0.7),  # Memory supports Decision
        (3, 4, "creates", 0.6),   # Decision creates Pattern
        (4, 0, "influences", 0.5) # Pattern influences Consciousness
    ]
    
    for i, j, rel_type, strength in relations:
        fmo.add_relation(concept_ids[i], concept_ids[j], rel_type, strength)
    
    print("3. Running Integrated Cognitive Scenarios...")
    
    scenarios = [
        {
            'name': 'Knowledge Integration Task',
            'context': {
                'task_type': 'knowledge_integration',
                'complexity': 0.8,
                'concepts_involved': 3,
                'cognitive_reasoning': 0.9,
                'cognitive_memory': 0.8,
                'cognitive_language': 0.7
            },
            'system_states': {
                'facms': {'memory_utilization': 0.7, 'access_efficiency': 0.8},
                'fmo': {'knowledge_coherence': 0.9, 'semantic_processing': 0.8},
                'arbiter': {'decision_confidence': 0.8, 'reasoning_quality': 0.9}
            }
        },
        {
            'name': 'Pattern Recognition Task',
            'context': {
                'task_type': 'pattern_recognition',
                'complexity': 0.6,
                'data_volume': 0.9,
                'cognitive_perception': 0.8,
                'cognitive_attention': 0.9,
                'cognitive_reasoning': 0.7
            },
            'system_states': {
                'facms': {'memory_utilization': 0.9, 'access_efficiency': 0.7},
                'fmo': {'knowledge_coherence': 0.8, 'semantic_processing': 0.9},
                'arbiter': {'decision_confidence': 0.7, 'reasoning_quality': 0.8}
            }
        },
        {
            'name': 'Creative Problem Solving',
            'context': {
                'task_type': 'creative_problem_solving',
                'complexity': 1.0,
                'novelty': 0.9,
                'cognitive_creativity': 0.9,
                'cognitive_reasoning': 0.8,
                'cognitive_emotion': 0.6
            },
            'system_states': {
                'facms': {'memory_utilization': 0.6, 'access_efficiency': 0.9},
                'fmo': {'knowledge_coherence': 0.7, 'semantic_processing': 0.7},
                'arbiter': {'decision_confidence': 0.6, 'reasoning_quality': 0.7}
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['name']}")
        print("-" * 50)
        
        # Make decision using integrated arbiter
        decision = arbiter.make_decision(scenario['context'], agent_id)
        
        # Monitor system state with TIE
        monitoring_report = tie.monitor_system_state(scenario['system_states'])
        
        # Query related knowledge from FMO
        related_concepts = fmo.query_concepts_by_crystal_properties(
            archetype=decision['reasoning']['tcs_archetype'],
            min_confidence=0.5,
            limit=3
        )
        
        print(f"Decision: {decision['action']} (confidence: {decision['confidence']:.2f})")
        print(f"TCS Archetype: {decision['reasoning']['tcs_archetype']}")
        print(f"System Health: {monitoring_report['system_health']['status']} "
              f"(score: {monitoring_report['system_health']['overall_score']:.2f})")
        print(f"Related Concepts: {len(related_concepts)} found")
        
        if monitoring_report['anomaly_detected']:
            print("⚠️  ANOMALY DETECTED")
        
        if monitoring_report['recommendations']:
            print("Recommendations:")
            for rec in monitoring_report['recommendations']:
                print(f"  • {rec}")
    
    print("\n4. Crystallographic Knowledge Analysis...")
    
    # Analyze concept archetypes
    for archetype in ['Stable', 'Growth', 'Decay']:
        concepts = fmo.query_concepts_by_crystal_properties(archetype=archetype, limit=5)
        print(f"\n{archetype} Concepts ({len(concepts)}):")
        for concept in concepts:
            print(f"  • {concept['name']}: confidence={concept['epistemic_confidence']:.2f}")
    
    print("\n5. System Performance Summary...")
    
    # Crystal engine performance
    crystal_stats = arbiter.crystal_engine.get_performance_stats()
    print(f"\nCrystal Engine Performance:")
    print(f"  Total calculations: {crystal_stats['total_calculations']}")
    print(f"  Cache efficiency: {crystal_stats['cache_hit_rate']:.1%}")
    
    # System health summary
    health = tie._calculate_system_health()
    print(f"\nSystem Health Summary:")
    print(f"  Overall status: {health['status']}")
    print(f"  Health score: {health['overall_score']:.2f}")
    print(f"  Average coherence: {health['avg_coherence']:.2f}")
    print(f"  Anomalies detected: {tie.system_metrics['anomalies_detected']}")
    
    # Archetype distribution
    print(f"\nArchetype Distribution:")
    total_crystals = sum(tie.system_metrics['archetype_distribution'].values())
    for archetype, count in tie.system_metrics['archetype_distribution'].items():
        percentage = (count / total_crystals) * 100 if total_crystals > 0 else 0
        print(f"  {archetype}: {count} ({percentage:.1f}%)")
    
    # Cleanup demo storage
    import shutil
    for storage_dir in ["complete_facms_storage", "complete_fmo_storage", "arbiter_facms_storage"]:
        shutil.rmtree(storage_dir, ignore_errors=True)
    
    print(f"\n✓ Complete System Integration Demo Finished")
    print(f"✓ All TEMPUS-CRYSTALLO systems successfully integrated")
    print(f"✓ Crystallographic consciousness framework operational")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    run_complete_integration_demo()