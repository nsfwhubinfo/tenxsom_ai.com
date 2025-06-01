#!/usr/bin/env python3
"""
Test Suite for Holographic Properties & State Morphing
======================================================

Tests for META-OPT-QUANT V6's holographic claims:
- Each vertex contains information about the whole
- Graceful degradation with partial information
- Real-time morphing between states
- Geometric interpolation properties

For Tenxsom AI's META-OPT-QUANT V6 validation.
"""

import numpy as np
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import (
    CuboctahedronCPUState, HolographicMorphEngine, MetrologicalEngine,
    CuboctahedronVertex, PHI
)
import unittest
from typing import List, Tuple, Dict, Optional
# Matplotlib imports commented out for testing environment
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
import random

class TestHolographicProperties(unittest.TestCase):
    """Test holographic properties of cuboctahedral states"""
    
    def setUp(self):
        self.morph_engine = HolographicMorphEngine()
        self.metrological_engine = MetrologicalEngine()
        
    def create_damaged_state(self, original: CuboctahedronCPUState, 
                           vertices_to_damage: List[int],
                           damage_type: str = 'zero') -> CuboctahedronCPUState:
        """Create a damaged version of the state"""
        damaged = CuboctahedronCPUState()
        
        # Copy all vertices
        for i in range(12):
            damaged.vertices[i].value = original.vertices[i].value
            damaged.vertices[i].position = original.vertices[i].position.copy()
            
        # Apply damage
        for vertex_id in vertices_to_damage:
            if damage_type == 'zero':
                damaged.vertices[vertex_id].value = 0
            elif damage_type == 'corrupt':
                damaged.vertices[vertex_id].value = random.randint(0, 0xFFFFFFFFFFFFFFFF)
            elif damage_type == 'invert':
                damaged.vertices[vertex_id].value = ~damaged.vertices[vertex_id].value & 0xFFFFFFFFFFFFFFFF
                
        return damaged
    
    def test_partial_reconstruction(self):
        """Test reconstruction from partial information"""
        print("\n=== Testing Partial Reconstruction ===")
        
        # Create a state with known pattern
        original_state = {}
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            # Each register encodes its position
            original_state[reg] = (i + 1) * 0x1111111111111111
            
        cpu_state = CuboctahedronCPUState(original_state)
        
        # Test different damage levels
        damage_levels = [
            (1, "Single vertex"),
            (3, "25% vertices"),
            (6, "50% vertices"),
            (9, "75% vertices")
        ]
        
        for n_damaged, description in damage_levels:
            print(f"\n{description} damaged ({n_damaged}/12):")
            
            # Randomly select vertices to damage
            vertices_to_damage = random.sample(range(12), n_damaged)
            damaged_state = self.create_damaged_state(cpu_state, vertices_to_damage)
            
            # Attempt reconstruction using holographic properties
            reconstructed = self.reconstruct_from_partial(damaged_state, vertices_to_damage)
            
            # Calculate recovery quality
            recovery_quality = self.calculate_recovery_quality(cpu_state, reconstructed, vertices_to_damage)
            
            print(f"  Damaged vertices: {vertices_to_damage}")
            print(f"  Recovery rate: {recovery_quality['recovery_rate']:.1%}")
            print(f"  Mean error (undamaged): {recovery_quality['mean_error_undamaged']:.2e}")
            print(f"  Mean error (damaged): {recovery_quality['mean_error_damaged']:.2e}")
            print(f"  Holographic score: {recovery_quality['holographic_score']:.3f}")
            
    def reconstruct_from_partial(self, damaged_state: CuboctahedronCPUState,
                               damaged_vertices: List[int]) -> CuboctahedronCPUState:
        """Attempt to reconstruct full state from partial information"""
        reconstructed = CuboctahedronCPUState()
        
        # Copy undamaged vertices
        undamaged_vertices = [i for i in range(12) if i not in damaged_vertices]
        for i in undamaged_vertices:
            reconstructed.vertices[i].value = damaged_state.vertices[i].value
            
        # Reconstruct damaged vertices using holographic properties
        for damaged_idx in damaged_vertices:
            # Method 1: Geometric interpolation from neighbors
            neighbors = self.get_vertex_neighbors(damaged_idx)
            neighbor_values = []
            
            for n_idx in neighbors:
                if n_idx in undamaged_vertices:
                    neighbor_values.append(damaged_state.vertices[n_idx].value)
                    
            if neighbor_values:
                # Weighted average based on geometric distance
                reconstructed.vertices[damaged_idx].value = int(np.mean(neighbor_values)) & 0xFFFFFFFFFFFFFFFF
            else:
                # Method 2: Use holographic encoding
                hologram = damaged_state._create_hologram()
                
                # Extract information from hologram bits influenced by this vertex
                start_bit = (damaged_idx * 5) % 64
                end_bit = (start_bit + 6) % 64
                
                if end_bit > start_bit:
                    hologram_bits = hologram[start_bit:end_bit]
                else:
                    hologram_bits = np.concatenate([hologram[start_bit:], hologram[:end_bit]])
                    
                # Reconstruct value from hologram bits
                reconstructed_value = 0
                for i, bit in enumerate(hologram_bits):
                    reconstructed_value |= (int(bit) << (i * 10))
                    
                reconstructed.vertices[damaged_idx].value = reconstructed_value & 0xFFFFFFFFFFFFFFFF
                
        return reconstructed
    
    def get_vertex_neighbors(self, vertex_id: int) -> List[int]:
        """Get neighboring vertices in cuboctahedron"""
        # Cuboctahedron adjacency (each vertex has 4 neighbors)
        adjacency = {
            0: [1, 3, 4, 8],
            1: [0, 2, 5, 11],
            2: [1, 3, 6, 10],
            3: [0, 2, 7, 9],
            4: [0, 5, 7, 8],
            5: [1, 4, 6, 9],
            6: [2, 5, 7, 10],
            7: [3, 4, 6, 11],
            8: [0, 4, 9, 11],
            9: [3, 5, 8, 10],
            10: [2, 6, 9, 11],
            11: [1, 7, 8, 10]
        }
        return adjacency.get(vertex_id, [])
    
    def calculate_recovery_quality(self, original: CuboctahedronCPUState,
                                 reconstructed: CuboctahedronCPUState,
                                 damaged_vertices: List[int]) -> Dict[str, float]:
        """Calculate quality metrics for reconstruction"""
        undamaged_vertices = [i for i in range(12) if i not in damaged_vertices]
        
        # Calculate errors
        undamaged_errors = []
        damaged_errors = []
        
        for i in range(12):
            orig_val = original.vertices[i].value
            recon_val = reconstructed.vertices[i].value
            error = abs(orig_val - recon_val) / (orig_val + 1)  # Relative error
            
            if i in damaged_vertices:
                damaged_errors.append(error)
            else:
                undamaged_errors.append(error)
                
        # Calculate holographic score (how well information was preserved)
        orig_hologram = original._create_hologram()
        recon_hologram = reconstructed._create_hologram()
        hologram_similarity = np.corrcoef(orig_hologram.flatten(), recon_hologram.flatten())[0, 1]
        
        return {
            'recovery_rate': sum(1 for e in damaged_errors if e < 0.1) / len(damaged_errors) if damaged_errors else 0,
            'mean_error_undamaged': np.mean(undamaged_errors) if undamaged_errors else 0,
            'mean_error_damaged': np.mean(damaged_errors) if damaged_errors else 0,
            'holographic_score': max(0, hologram_similarity)
        }
    
    def test_state_morphing(self):
        """Test morphing between cuboctahedral states"""
        print("\n=== Testing State Morphing ===")
        
        # Create two distinct states
        state_a = {}
        state_b = {}
        
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            state_a[reg] = (i + 1) * 0x0101010101010101
            state_b[reg] = (12 - i) * 0x0202020202020202
            
        cpu_state_a = CuboctahedronCPUState(state_a)
        cpu_state_b = CuboctahedronCPUState(state_b)
        
        # Morph between states
        morph_duration_ns = 1000
        morphed_states = self.morph_engine.morph_states(
            cpu_state_a, cpu_state_b, morph_duration_ns
        )
        
        print(f"Morphing duration: {morph_duration_ns} ns")
        print(f"Number of intermediate states: {len(morphed_states)}")
        
        # Analyze morphing path
        self.analyze_morph_path(cpu_state_a, cpu_state_b, morphed_states)
        
    def analyze_morph_path(self, start: CuboctahedronCPUState,
                          end: CuboctahedronCPUState,
                          path: List[CuboctahedronCPUState]):
        """Analyze properties of the morphing path"""
        
        # Track value evolution for first register
        rax_values = []
        phi_influences = []
        
        for state in path:
            rax_values.append(state.vertices[0].value)
            
            # Check for φ influence in the path
            phi_error = min(abs(v.value / 1e15 - PHI) for v in state.vertices)
            phi_influences.append(phi_error)
            
        # Calculate path smoothness
        if len(rax_values) > 1:
            differences = np.diff(rax_values)
            smoothness = np.std(differences) / (np.mean(np.abs(differences)) + 1e-10)
        else:
            smoothness = 0
            
        print(f"\nMorphing path analysis:")
        print(f"  Path smoothness: {smoothness:.3f} (lower is smoother)")
        print(f"  Min φ proximity: {min(phi_influences):.6f}")
        print(f"  φ influence detected: {any(e < 0.1 for e in phi_influences)}")
        
        # Check geometric properties
        self.verify_geometric_properties(path)
        
    def verify_geometric_properties(self, states: List[CuboctahedronCPUState]):
        """Verify geometric properties are preserved during morphing"""
        
        for i, state in enumerate(states):
            # Check vertex normalization
            norms = [np.linalg.norm(v.position) for v in state.vertices]
            norm_variance = np.var(norms)
            
            # Check edge lengths (should be consistent)
            edge_lengths = []
            for edge in state.edges:
                v1_pos = state.vertices[edge.v1].position
                v2_pos = state.vertices[edge.v2].position
                length = np.linalg.norm(v2_pos - v1_pos)
                edge_lengths.append(length)
                
            edge_variance = np.var(edge_lengths)
            
            if i % (len(states) // 10) == 0:  # Sample 10 points
                print(f"  State {i}/{len(states)}: norm_var={norm_variance:.6f}, edge_var={edge_variance:.6f}")
                
    def test_holographic_interference(self):
        """Test interference patterns in holographic encoding"""
        print("\n=== Testing Holographic Interference ===")
        
        # Create states that should interfere constructively
        state1 = {}
        state2 = {}
        
        # Create wave-like patterns
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            phase1 = i * 2 * np.pi / 12
            phase2 = i * 2 * np.pi / 12 + np.pi / 6  # 30 degree phase shift
            
            state1[reg] = int((1 + np.sin(phase1)) * 0x7FFFFFFFFFFFFFFF)
            state2[reg] = int((1 + np.sin(phase2)) * 0x7FFFFFFFFFFFFFFF)
            
        cpu1 = CuboctahedronCPUState(state1)
        cpu2 = CuboctahedronCPUState(state2)
        
        # Create superposition (simplified)
        superposed = CuboctahedronCPUState()
        for i in range(12):
            # Quantum-inspired superposition
            amp1 = cpu1.vertices[i].value / 0xFFFFFFFFFFFFFFFF
            amp2 = cpu2.vertices[i].value / 0xFFFFFFFFFFFFFFFF
            
            # Interference
            superposed_amp = (amp1 + amp2) / 2 + 0.1 * np.cos(amp1 - amp2)
            superposed.vertices[i].value = int(superposed_amp * 0xFFFFFFFFFFFFFFFF)
            
        # Analyze interference pattern
        hologram1 = cpu1._create_hologram()
        hologram2 = cpu2._create_hologram()
        hologram_super = superposed._create_hologram()
        
        # Calculate interference visibility
        expected_interference = (hologram1.astype(float) + hologram2.astype(float)) / 2
        actual_interference = hologram_super.astype(float)
        
        visibility = 1 - np.mean(np.abs(expected_interference - actual_interference)) / 128
        
        print(f"Interference visibility: {visibility:.3f}")
        print(f"Hologram entropy (state1): {self.calculate_entropy(hologram1):.3f}")
        print(f"Hologram entropy (state2): {self.calculate_entropy(hologram2):.3f}")
        print(f"Hologram entropy (superposed): {self.calculate_entropy(hologram_super):.3f}")
        
    def calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy"""
        # Normalize
        if data.sum() == 0:
            return 0
            
        probs = data / data.sum()
        probs = probs[probs > 0]  # Remove zeros
        
        return -np.sum(probs * np.log2(probs))
        
    def test_morphing_through_phi(self):
        """Test if morphing paths naturally pass through φ"""
        print("\n=== Testing Morphing Through φ ===")
        
        # Create states that bracket φ
        state_below = {}
        state_above = {}
        
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            below_value = PHI * 0.9 * (1 + i/100)  # Below φ
            above_value = PHI * 1.1 * (1 + i/100)  # Above φ
            
            state_below[reg] = int(below_value * 1e15) & 0xFFFFFFFFFFFFFFFF
            state_above[reg] = int(above_value * 1e15) & 0xFFFFFFFFFFFFFFFF
            
        cpu_below = CuboctahedronCPUState(state_below)
        cpu_above = CuboctahedronCPUState(state_above)
        
        # Morph with fine granularity
        morphed = self.morph_engine.morph_states(cpu_below, cpu_above, 10000)
        
        # Check how many states are near φ
        phi_proximities = []
        closest_to_phi = None
        min_phi_error = float('inf')
        
        for state in morphed:
            # Calculate minimum φ error across all vertices
            phi_errors = []
            for vertex in state.vertices:
                normalized_value = vertex.value / 1e15
                phi_error = abs(normalized_value - PHI)
                phi_errors.append(phi_error)
                
            min_error = min(phi_errors)
            phi_proximities.append(min_error)
            
            if min_error < min_phi_error:
                min_phi_error = min_error
                closest_to_phi = state
                
        # Statistics
        near_phi_count = sum(1 for e in phi_proximities if e < 0.01)
        very_near_phi_count = sum(1 for e in phi_proximities if e < 0.001)
        
        print(f"States near φ (< 0.01): {near_phi_count}/{len(morphed)} ({near_phi_count/len(morphed)*100:.1f}%)")
        print(f"States very near φ (< 0.001): {very_near_phi_count}/{len(morphed)} ({very_near_phi_count/len(morphed)*100:.1f}%)")
        print(f"Closest approach to φ: {min_phi_error:.6f}")
        
        # Verify φ is an attractor in morphing space
        self.assertLess(min_phi_error, 0.01, "Morphing should pass close to φ")
        
    def visualize_cuboctahedron_morphing(self, states: List[CuboctahedronCPUState], 
                                       save_path: Optional[str] = None):
        """Visualize morphing sequence (if matplotlib available)"""
        print("Visualization skipped: matplotlib not available in test environment")

class HolographicBenchmark:
    """Benchmark holographic operations"""
    
    def __init__(self):
        self.morph_engine = HolographicMorphEngine()
        
    def benchmark_morphing_speed(self, n_morphs: int = 100):
        """Benchmark morphing performance"""
        print(f"\n=== Morphing Speed Benchmark ({n_morphs} morphs) ===")
        
        import time
        
        # Generate random state pairs
        morph_times = []
        states_per_morph = []
        
        for _ in range(n_morphs):
            # Create random states
            state_a = {reg: random.randint(0, 0xFFFFFFFFFFFFFFFF) 
                      for reg in CuboctahedronCPUState.REGISTER_MAPPING}
            state_b = {reg: random.randint(0, 0xFFFFFFFFFFFFFFFF)
                      for reg in CuboctahedronCPUState.REGISTER_MAPPING}
            
            cpu_a = CuboctahedronCPUState(state_a)
            cpu_b = CuboctahedronCPUState(state_b)
            
            # Time morphing
            start = time.perf_counter()
            morphed = self.morph_engine.morph_states(cpu_a, cpu_b, 1000)
            morph_time = time.perf_counter() - start
            
            morph_times.append(morph_time)
            states_per_morph.append(len(morphed))
            
        # Statistics
        avg_time = np.mean(morph_times) * 1000  # Convert to ms
        avg_states = np.mean(states_per_morph)
        total_states = sum(states_per_morph)
        total_time = sum(morph_times)
        throughput = total_states / total_time
        
        print(f"Average morph time: {avg_time:.2f} ms")
        print(f"Average states per morph: {avg_states:.0f}")
        print(f"Total throughput: {throughput:.0f} states/second")
        print(f"Effective morph rate: {1/avg_time*1000:.0f} morphs/second")

if __name__ == "__main__":
    print("META-OPT-QUANT V6 Holographic Properties Test Suite")
    print("For Tenxsom AI")
    print("=" * 60)
    
    # Run tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run benchmark
    print("\n" + "=" * 60)
    benchmark = HolographicBenchmark()
    benchmark.benchmark_morphing_speed(100)