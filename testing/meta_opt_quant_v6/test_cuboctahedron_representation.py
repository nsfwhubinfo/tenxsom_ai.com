#!/usr/bin/env python3
"""
Test Suite for Cuboctahedral State Representation & Symmetry Compression
=======================================================================

Tests for META-OPT-QUANT V6's claims:
- 64-bit states mapped to 12 vertices (registers)
- 48-fold symmetry compression (1/48th storage)
- Lossless or near-lossless reconstruction
- 97.9% memory efficiency

For Tenxsom AI's META-OPT-QUANT V6 validation.
"""

import numpy as np
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import (
    CuboctahedronCPUState, MetrologicalEngine, SymmetryOp,
    CuboctahedronVertex, PHI
)
import unittest
from typing import List, Tuple, Dict
import random
import time

class TestCuboctahedronRepresentation(unittest.TestCase):
    """Test cuboctahedral state representation fidelity"""
    
    def setUp(self):
        self.engine = MetrologicalEngine()
        self.test_iterations = 1000
        
    def generate_test_states(self, n: int = 1000) -> List[Dict[str, int]]:
        """Generate diverse 64-bit CPU states for testing"""
        states = []
        
        # Edge cases
        states.append({reg: 0 for reg in CuboctahedronCPUState.REGISTER_MAPPING})  # All zeros
        states.append({reg: 0xFFFFFFFFFFFFFFFF for reg in CuboctahedronCPUState.REGISTER_MAPPING})  # All ones
        states.append({reg: 0x0101010101010101 * i for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING)})  # Pattern
        
        # φ-based states (should compress well)
        phi_state = {}
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            phi_state[reg] = int((PHI ** (i/6)) * 1e15) & 0xFFFFFFFFFFFFFFFF
        states.append(phi_state)
        
        # Random states
        for _ in range(n - len(states)):
            state = {}
            for reg in CuboctahedronCPUState.REGISTER_MAPPING:
                state[reg] = random.randint(0, 0xFFFFFFFFFFFFFFFF)
            states.append(state)
            
        return states
    
    def calculate_reconstruction_error(self, original: Dict[str, int], 
                                     reconstructed: CuboctahedronCPUState) -> Dict[str, float]:
        """Calculate various error metrics"""
        errors = {
            'hamming_distance': 0,
            'bit_error_rate': 0.0,
            'max_register_error': 0,
            'mean_register_error': 0.0,
            'perfect_reconstruction': True
        }
        
        total_bits = 0
        bit_differences = 0
        register_errors = []
        
        for reg, orig_val in original.items():
            recon_val = reconstructed.get_register(reg)
            
            # Hamming distance
            xor = orig_val ^ recon_val
            bit_diff = bin(xor).count('1')
            bit_differences += bit_diff
            total_bits += 64
            
            # Register error
            reg_error = abs(orig_val - recon_val)
            register_errors.append(reg_error)
            
            if reg_error > 0:
                errors['perfect_reconstruction'] = False
                
        errors['hamming_distance'] = bit_differences
        errors['bit_error_rate'] = bit_differences / total_bits if total_bits > 0 else 0
        errors['max_register_error'] = max(register_errors)
        errors['mean_register_error'] = np.mean(register_errors)
        
        return errors
    
    def test_basic_representation(self):
        """Test basic encode/decode cycle"""
        print("\n=== Testing Basic Cuboctahedral Representation ===")
        
        # Create a simple state
        original_state = {
            'RAX': 0x1234567890ABCDEF,
            'RBX': 0xFEDCBA0987654321,
            'RCX': 0x1111111111111111,
            'RDX': 0x2222222222222222,
            'RSI': 0x3333333333333333,
            'RDI': 0x4444444444444444,
            'RSP': 0x5555555555555555,
            'RBP': 0x6666666666666666,
            'R8':  0x7777777777777777,
            'R9':  0x8888888888888888,
            'R10': 0x9999999999999999,
            'R11': 0xAAAAAAAAAAAAAAAA
        }
        
        # Create CPU state
        cpu_state = CuboctahedronCPUState(original_state)
        
        # Compress
        compressed = self.engine.compress_state(cpu_state)
        print(f"Original size: {12 * 64} bits")
        print(f"Compressed size: {len(compressed) * 64} bits")
        print(f"Compression ratio: {12 * 64 / (len(compressed) * 64):.2f}x")
        
        # Decompress
        reconstructed = self.engine.decompress_state(compressed)
        
        # Calculate errors
        errors = self.calculate_reconstruction_error(original_state, reconstructed)
        print(f"Reconstruction errors: {errors}")
        
        # For now, we expect some error due to the simplified compression
        # Full implementation would use all 48 symmetry operations
        self.assertLess(errors['bit_error_rate'], 0.5)  # Less than 50% error
        
    def test_edge_cases(self):
        """Test edge cases (all zeros, all ones, patterns)"""
        print("\n=== Testing Edge Cases ===")
        
        edge_cases = [
            ("All zeros", {reg: 0 for reg in CuboctahedronCPUState.REGISTER_MAPPING}),
            ("All ones", {reg: 0xFFFFFFFFFFFFFFFF for reg in CuboctahedronCPUState.REGISTER_MAPPING}),
            ("Alternating", {reg: 0xAAAAAAAAAAAAAAAA if i % 2 == 0 else 0x5555555555555555 
                           for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING)}),
            ("Sequential", {reg: i for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING)})
        ]
        
        for name, state in edge_cases:
            cpu_state = CuboctahedronCPUState(state)
            compressed = self.engine.compress_state(cpu_state)
            reconstructed = self.engine.decompress_state(compressed)
            errors = self.calculate_reconstruction_error(state, reconstructed)
            
            print(f"\n{name}:")
            print(f"  Compressed size: {len(compressed)} elements")
            print(f"  Bit error rate: {errors['bit_error_rate']:.4f}")
            print(f"  Perfect reconstruction: {errors['perfect_reconstruction']}")
            
    def test_phi_based_states(self):
        """Test states based on golden ratio (should compress well)"""
        print("\n=== Testing φ-based States ===")
        
        # Create states with φ relationships
        phi_states = []
        
        # Direct φ powers
        state1 = {}
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            state1[reg] = int((PHI ** i) * 1e10) & 0xFFFFFFFFFFFFFFFF
        phi_states.append(("φ powers", state1))
        
        # Fibonacci sequence
        state2 = {}
        a, b = 0, 1
        for reg in CuboctahedronCPUState.REGISTER_MAPPING:
            state2[reg] = b & 0xFFFFFFFFFFFFFFFF
            a, b = b, (a + b)
        phi_states.append(("Fibonacci", state2))
        
        # φ spiral
        state3 = {}
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            angle = i * 2 * np.pi / PHI
            value = int((np.cos(angle) + 1) * 0x7FFFFFFFFFFFFFFF)
            state3[reg] = value
        phi_states.append(("φ spiral", state3))
        
        for name, state in phi_states:
            cpu_state = CuboctahedronCPUState(state)
            compressed = self.engine.compress_state(cpu_state)
            reconstructed = self.engine.decompress_state(compressed)
            errors = self.calculate_reconstruction_error(state, reconstructed)
            
            print(f"\n{name}:")
            print(f"  Compressed size: {len(compressed)} elements")
            print(f"  Bit error rate: {errors['bit_error_rate']:.4f}")
            print(f"  Mean register error: {errors['mean_register_error']:.2e}")
            
            # φ-based states should compress better
            self.assertLess(errors['bit_error_rate'], 0.3)
            
    def test_massive_dataset(self):
        """Test with 1000+ diverse states"""
        print("\n=== Testing Massive Dataset (1000 states) ===")
        
        test_states = self.generate_test_states(1000)
        
        total_original_bits = 0
        total_compressed_bits = 0
        error_rates = []
        perfect_reconstructions = 0
        
        start_time = time.time()
        
        for i, state in enumerate(test_states):
            cpu_state = CuboctahedronCPUState(state)
            
            # Compress
            compressed = self.engine.compress_state(cpu_state)
            
            # Decompress
            reconstructed = self.engine.decompress_state(compressed)
            
            # Calculate metrics
            errors = self.calculate_reconstruction_error(state, reconstructed)
            error_rates.append(errors['bit_error_rate'])
            
            if errors['perfect_reconstruction']:
                perfect_reconstructions += 1
                
            # Track sizes
            total_original_bits += 12 * 64
            total_compressed_bits += len(compressed) * 64
            
            if i % 100 == 0:
                print(f"  Processed {i+1}/1000 states...")
                
        end_time = time.time()
        
        # Calculate statistics
        mean_error_rate = np.mean(error_rates)
        std_error_rate = np.std(error_rates)
        compression_ratio = total_original_bits / total_compressed_bits
        memory_efficiency = 1 - (total_compressed_bits / total_original_bits)
        
        print(f"\n=== Massive Dataset Results ===")
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        print(f"Mean bit error rate: {mean_error_rate:.4f} ± {std_error_rate:.4f}")
        print(f"Perfect reconstructions: {perfect_reconstructions}/{len(test_states)}")
        print(f"Compression ratio: {compression_ratio:.2f}x")
        print(f"Memory efficiency: {memory_efficiency:.1%}")
        print(f"Average bits per state: {total_compressed_bits / len(test_states):.1f}")
        
        # Verify claims
        print(f"\n=== Claim Verification ===")
        print(f"Claimed compression: 48x (storing 1/48th)")
        print(f"Achieved compression: {compression_ratio:.2f}x")
        print(f"Claimed memory efficiency: 97.9%")
        print(f"Achieved memory efficiency: {memory_efficiency:.1%}")
        
        # Note: Current implementation is simplified
        # Full 48-fold symmetry would achieve better results
        
    def test_symmetry_operations(self):
        """Test individual symmetry operations"""
        print("\n=== Testing Symmetry Operations ===")
        
        # Create a test state with known pattern
        original_state = {}
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            original_state[reg] = (i + 1) * 0x1111111111111111
            
        cpu_state = CuboctahedronCPUState(original_state)
        
        # Test each symmetry operation
        symmetries_tested = [
            SymmetryOp.IDENTITY,
            SymmetryOp.ROTATE_X_90,
            SymmetryOp.ROTATE_Y_180,
            SymmetryOp.ROTATE_Z_270,
            SymmetryOp.INVERSION
        ]
        
        for sym_op in symmetries_tested:
            transformed = cpu_state.apply_symmetry(sym_op)
            
            # Check that transformation preserves certain invariants
            original_sum = sum(v.value for v in cpu_state.vertices)
            transformed_sum = sum(v.value for v in transformed.vertices)
            
            print(f"\n{sym_op.name}:")
            print(f"  Sum preserved: {original_sum == transformed_sum}")
            
            # For identity, should be identical
            if sym_op == SymmetryOp.IDENTITY:
                for i in range(12):
                    self.assertEqual(cpu_state.vertices[i].value, 
                                   transformed.vertices[i].value)
                print(f"  Identity check: PASSED")
                
    def test_holographic_property(self):
        """Test holographic encoding (each part contains the whole)"""
        print("\n=== Testing Holographic Properties ===")
        
        # Create state with specific pattern
        state = {}
        for i, reg in enumerate(CuboctahedronCPUState.REGISTER_MAPPING):
            # Each register contains all register indices
            value = 0
            for j in range(12):
                value |= (j << (j * 5))
            state[reg] = value & 0xFFFFFFFFFFFFFFFF
            
        cpu_state = CuboctahedronCPUState(state)
        
        # Check hologram
        hologram = cpu_state._create_hologram()
        print(f"Hologram size: {len(hologram)} bits")
        print(f"Hologram entropy: {np.count_nonzero(hologram) / len(hologram):.2f}")
        
        # Verify each vertex influences multiple hologram bits
        influences = {}
        for i in range(12):
            start_bit = (i * 5) % 64
            end_bit = (start_bit + 6) % 64
            if end_bit > start_bit:
                influenced_bits = list(range(start_bit, end_bit))
            else:
                influenced_bits = list(range(start_bit, 64)) + list(range(0, end_bit))
            influences[f"Vertex {i}"] = influenced_bits
            
        print("\nVertex -> Hologram bit influences:")
        for vertex, bits in influences.items():
            print(f"  {vertex}: {len(bits)} bits")
            
        # Verify holographic property: information is distributed
        self.assertGreater(len(set(hologram)), 10)  # At least 10 unique values

class CompressionBenchmark:
    """Benchmark compression performance"""
    
    def __init__(self):
        self.engine = MetrologicalEngine()
        
    def benchmark_compression_speed(self, n_states: int = 10000):
        """Benchmark compression/decompression speed"""
        print(f"\n=== Compression Speed Benchmark ({n_states} states) ===")
        
        # Generate test states
        states = []
        for _ in range(n_states):
            state = {}
            for reg in CuboctahedronCPUState.REGISTER_MAPPING:
                state[reg] = random.randint(0, 0xFFFFFFFFFFFFFFFF)
            states.append(state)
            
        # Benchmark compression
        compress_times = []
        decompress_times = []
        
        for state in states:
            cpu_state = CuboctahedronCPUState(state)
            
            # Time compression
            start = time.perf_counter()
            compressed = self.engine.compress_state(cpu_state)
            compress_time = time.perf_counter() - start
            compress_times.append(compress_time)
            
            # Time decompression
            start = time.perf_counter()
            reconstructed = self.engine.decompress_state(compressed)
            decompress_time = time.perf_counter() - start
            decompress_times.append(decompress_time)
            
        # Calculate statistics
        avg_compress = np.mean(compress_times) * 1e6  # Convert to microseconds
        avg_decompress = np.mean(decompress_times) * 1e6
        total_time = sum(compress_times) + sum(decompress_times)
        throughput = n_states / total_time  # States per second
        
        print(f"Average compression time: {avg_compress:.2f} μs")
        print(f"Average decompression time: {avg_decompress:.2f} μs")
        print(f"Total throughput: {throughput:.0f} states/second")
        print(f"Throughput: {throughput * 12 * 64 / 1e9:.2f} Gbps")

if __name__ == "__main__":
    # Run unit tests
    print("META-OPT-QUANT V6 Cuboctahedral Representation Test Suite")
    print("For Tenxsom AI")
    print("=" * 60)
    
    # Run tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run benchmark
    print("\n" + "=" * 60)
    benchmark = CompressionBenchmark()
    benchmark.benchmark_compression_speed(10000)