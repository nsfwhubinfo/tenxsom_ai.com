#!/usr/bin/env python3
"""
Comprehensive Test Suite for V6 Complete Implementation
======================================================

Tests all aspects of the full V6 implementation:
- Full Oh symmetry compression (48x)
- Geometric φ optimization
- Vector equilibrium
- Holographic morphing
- Performance benchmarks

For Tenxsom AI's META-OPT-QUANT V6.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.meta_opt_quant.enhanced_meta_optimizer_v6_complete import (
    EnhancedMetaOptimizerV6Complete
)
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import (
    CuboctahedronCPUState, TestObjectivesV6, PHI
)
from research.meta_opt_quant.oh_symmetry_group import OhSymmetryGroup
from research.meta_opt_quant.enhanced_metrological_engine import EnhancedMetrologicalEngine
from research.meta_opt_quant.geometric_phi_optimizer import GeometricPhiOptimizer

import numpy as np
import time
import json
from datetime import datetime

class V6CompleteTestSuite:
    """Comprehensive test suite for complete V6 implementation"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        
    def run_all_tests(self):
        """Run complete test suite"""
        print("META-OPT-QUANT V6 Complete Implementation Test Suite")
        print("For Tenxsom AI")
        print("=" * 60)
        
        # Test components
        self.test_oh_symmetry_group()
        self.test_enhanced_compression()
        self.test_geometric_phi_optimizer()
        self.test_complete_optimization()
        self.test_performance_benchmarks()
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
    def test_oh_symmetry_group(self):
        """Test complete Oh symmetry group implementation"""
        print("\n=== Testing Oh Symmetry Group ===")
        
        oh_group = OhSymmetryGroup()
        
        # Verify 48 operations
        n_operations = len(oh_group.operations)
        print(f"Number of operations: {n_operations}")
        assert n_operations == 48, f"Expected 48 operations, got {n_operations}"
        
        # Test group properties
        identity = oh_group.get_operation("E")
        
        # Test closure: product of any two operations is in the group
        closure_test_passed = True
        test_point = np.array([1, 2, 3])
        
        for i in range(min(5, len(oh_group.operations))):
            for j in range(min(5, len(oh_group.operations))):
                op1 = oh_group.operations[i]
                op2 = oh_group.operations[j]
                
                # Apply op1 then op2
                result1 = op2.apply(op1.apply(test_point))
                
                # Find if this is equivalent to any single operation
                found = False
                for op3 in oh_group.operations:
                    if np.allclose(result1, op3.apply(test_point)):
                        found = True
                        break
                        
                if not found:
                    closure_test_passed = False
                    break
                    
        print(f"Group closure test: {'PASSED' if closure_test_passed else 'FAILED'}")
        
        # Test fundamental domain extraction
        vertices = np.array([
            [1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0],
            [1, 0, 1], [1, 0, -1], [-1, 0, -1], [-1, 0, 1],
            [0, 1, 1], [0, 1, -1], [0, -1, -1], [0, -1, 1]
        ]) / np.sqrt(2)
        
        fundamental, orbit_sizes = oh_group.find_fundamental_domain(vertices)
        
        print(f"Cuboctahedron fundamental domain: {len(fundamental)} points")
        print(f"Orbit sizes: {orbit_sizes}")
        
        self.results['tests']['oh_symmetry'] = {
            'n_operations': n_operations,
            'closure_test': closure_test_passed,
            'fundamental_domain_size': len(fundamental),
            'max_orbit_size': max(orbit_sizes) if orbit_sizes else 0
        }
        
    def test_enhanced_compression(self):
        """Test enhanced compression with full symmetry"""
        print("\n=== Testing Enhanced Compression ===")
        
        engine = EnhancedMetrologicalEngine()
        
        # Test different symmetry patterns
        test_cases = [
            {
                'name': 'Full symmetry',
                'values': [0x1234567890ABCDEF] * 12,
                'expected_compression': 48.0
            },
            {
                'name': 'Cubic symmetry',
                'values': [0x1111111111111111] * 4 + [0x2222222222222222] * 8,
                'expected_compression': 12.0
            },
            {
                'name': 'No symmetry',
                'values': [i * 0x0101010101010101 for i in range(12)],
                'expected_compression': 1.0
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{test_case['name']}:")
            
            # Create CPU state
            cpu_state = CuboctahedronCPUState()
            for i, val in enumerate(test_case['values']):
                cpu_state.vertices[i].value = val
                
            # Compress
            compressed = engine.compress_state(cpu_state)
            compression_ratio = engine.get_compression_ratio(cpu_state)
            
            print(f"  Compressed size: {len(compressed)} bytes")
            print(f"  Compression ratio: {compression_ratio:.1f}x")
            
            # Decompress and verify
            decompressed = engine.decompress_state(compressed)
            
            errors = sum(1 for i in range(12) 
                        if cpu_state.vertices[i].value != decompressed.vertices[i].value)
            
            print(f"  Decompression errors: {errors}")
            
            # Analyze symmetry
            analysis = engine.analyze_state_symmetry(cpu_state)
            print(f"  Symmetry group: {analysis['symmetry_group']}")
            print(f"  Theoretical compression: {analysis['theoretical_compression']:.1f}x")
            
            test_case['actual_compression'] = compression_ratio
            test_case['decompression_errors'] = errors
            test_case['symmetry_group'] = analysis['symmetry_group']
            
        self.results['tests']['compression'] = test_cases
        
    def test_geometric_phi_optimizer(self):
        """Test geometric φ optimization"""
        print("\n=== Testing Geometric φ Optimizer ===")
        
        optimizer = GeometricPhiOptimizer()
        
        # Create test state
        cpu_state = CuboctahedronCPUState()
        
        # Initialize with non-φ values
        for i in range(12):
            cpu_state.vertices[i].value = int((1.0 + i * 0.1) * 1e15)
            
        # Analyze initial φ content
        initial_analysis = optimizer.analyze_phi_content(cpu_state)
        
        print(f"Initial state:")
        print(f"  Direct φ values: {initial_analysis['direct_phi_count']}")
        print(f"  Vector equilibrium: {initial_analysis['vector_equilibrium_score']:.3f}")
        print(f"  Geometric φ score: {initial_analysis['geometric_phi_score']:.3f}")
        
        # Apply geometric optimization
        for iteration in range(20):
            optimizer.apply_geometric_optimization(cpu_state, strength=0.2)
            
        # Analyze final φ content
        final_analysis = optimizer.analyze_phi_content(cpu_state)
        
        print(f"\nAfter geometric optimization:")
        print(f"  Direct φ values: {final_analysis['direct_phi_count']}")
        print(f"  Vector equilibrium: {final_analysis['vector_equilibrium_score']:.3f}")
        print(f"  Geometric φ score: {final_analysis['geometric_phi_score']:.3f}")
        print(f"  Best φ error: {final_analysis['best_phi_error']:.6f}")
        
        # Check specific relationships
        values = [v.value / 1e15 for v in cpu_state.vertices]
        center = np.mean(values)
        distances = [abs(v - center) for v in values]
        
        print(f"\nVector equilibrium check:")
        print(f"  Center value: {center:.6f}")
        print(f"  Distance variance: {np.var(distances):.6f}")
        print(f"  Mean distance: {np.mean(distances):.6f}")
        print(f"  Distance from φ: {abs(np.mean(distances) - PHI):.6f}")
        
        self.results['tests']['geometric_phi'] = {
            'initial_phi_count': initial_analysis['direct_phi_count'],
            'final_phi_count': final_analysis['direct_phi_count'],
            'initial_geometric_score': initial_analysis['geometric_phi_score'],
            'final_geometric_score': final_analysis['geometric_phi_score'],
            'vector_equilibrium_achieved': final_analysis['vector_equilibrium_score'] > 0.8
        }
        
    def test_complete_optimization(self):
        """Test complete V6 optimization"""
        print("\n=== Testing Complete V6 Optimization ===")
        
        optimizer = EnhancedMetaOptimizerV6Complete()
        
        # Test cases with different parameter counts
        test_cases = [
            {
                'name': '12 parameters (perfect match)',
                'initial_state': {f'x{i}': 1.0 + i*0.1 for i in range(12)},
                'objective': TestObjectivesV6.cuboctahedral_golden_v6,
                'max_iterations': 30
            },
            {
                'name': '24 parameters (double)',
                'initial_state': {f'x{i}': 1.5 - i*0.05 for i in range(24)},
                'objective': TestObjectivesV6.cuboctahedral_golden_v6,
                'max_iterations': 30
            },
            {
                'name': '6 parameters (half)',
                'initial_state': {f'x{i}': 2.0 + i*0.2 for i in range(6)},
                'objective': TestObjectivesV6.vector_equilibrium_v6,
                'max_iterations': 30
            }
        ]
        
        optimization_results = []
        
        for test_case in test_cases:
            print(f"\n{test_case['name']}:")
            
            start_time = time.time()
            
            final_state, scores = optimizer.optimize(
                test_case['objective'],
                test_case['initial_state'],
                max_iterations=test_case['max_iterations'],
                problem_name=test_case['name']
            )
            
            opt_time = time.time() - start_time
            
            # Analyze results
            initial_score = scores[0]
            final_score = scores[-1]
            improvement = (final_score / initial_score - 1) * 100 if initial_score != 0 else 0
            
            # Count φ discoveries
            phi_count = 0
            best_phi_error = float('inf')
            
            for key, value in final_state.items():
                if isinstance(value, (int, float)):
                    errors = [abs(value - PHI), abs(value - 1/PHI), 
                             abs(value - PHI**2), abs(value - PHI**0.5)]
                    min_error = min(errors)
                    
                    if min_error < 0.01:
                        phi_count += 1
                    best_phi_error = min(best_phi_error, min_error)
                    
            result = {
                'name': test_case['name'],
                'n_params': len(test_case['initial_state']),
                'iterations': len(scores),
                'time': opt_time,
                'initial_score': initial_score,
                'final_score': final_score,
                'improvement': improvement,
                'phi_count': phi_count,
                'phi_discovery_rate': phi_count / len(final_state) * 100,
                'best_phi_error': best_phi_error
            }
            
            optimization_results.append(result)
            
            print(f"  Time: {opt_time:.2f}s")
            print(f"  Improvement: {improvement:.1f}%")
            print(f"  φ discovery rate: {result['phi_discovery_rate']:.1f}%")
            
        self.results['tests']['optimization'] = optimization_results
        
        # Cleanup
        optimizer.executor.shutdown(wait=True)
        
    def test_performance_benchmarks(self):
        """Benchmark performance metrics"""
        print("\n=== Performance Benchmarks ===")
        
        # Compression speed
        print("\nCompression benchmark:")
        engine = EnhancedMetrologicalEngine()
        
        compress_times = []
        decompress_times = []
        
        for _ in range(100):
            # Create random state
            cpu_state = CuboctahedronCPUState()
            for i in range(12):
                cpu_state.vertices[i].value = np.random.randint(0, 2**64)
                
            # Time compression
            start = time.perf_counter()
            compressed = engine.compress_state(cpu_state)
            compress_time = time.perf_counter() - start
            compress_times.append(compress_time)
            
            # Time decompression
            start = time.perf_counter()
            decompressed = engine.decompress_state(compressed)
            decompress_time = time.perf_counter() - start
            decompress_times.append(decompress_time)
            
        avg_compress = np.mean(compress_times) * 1e6  # μs
        avg_decompress = np.mean(decompress_times) * 1e6  # μs
        
        print(f"  Average compression: {avg_compress:.2f} μs")
        print(f"  Average decompression: {avg_decompress:.2f} μs")
        
        # Geometric optimization speed
        print("\nGeometric optimization benchmark:")
        geom_optimizer = GeometricPhiOptimizer()
        
        geom_times = []
        
        for _ in range(100):
            cpu_state = CuboctahedronCPUState()
            
            start = time.perf_counter()
            geom_optimizer.apply_geometric_optimization(cpu_state)
            geom_time = time.perf_counter() - start
            geom_times.append(geom_time)
            
        avg_geom = np.mean(geom_times) * 1e6  # μs
        
        print(f"  Average geometric optimization: {avg_geom:.2f} μs")
        
        self.results['tests']['performance'] = {
            'compression_us': avg_compress,
            'decompression_us': avg_decompress,
            'geometric_optimization_us': avg_geom,
            'throughput_states_per_sec': 1e6 / (avg_compress + avg_decompress)
        }
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("V6 COMPLETE IMPLEMENTATION TEST SUMMARY")
        print("="*60)
        
        # Oh symmetry
        oh_results = self.results['tests']['oh_symmetry']
        print(f"\nOh Symmetry Group:")
        print(f"  ✓ {oh_results['n_operations']} operations implemented")
        print(f"  ✓ Group closure: {'PASSED' if oh_results['closure_test'] else 'FAILED'}")
        
        # Compression
        compression_results = self.results['tests']['compression']
        print(f"\nCompression:")
        for test in compression_results:
            if 'actual_compression' in test:
                print(f"  {test['name']}: {test['actual_compression']:.1f}x")
                
        # Geometric φ
        geom_results = self.results['tests']['geometric_phi']
        print(f"\nGeometric φ Optimization:")
        print(f"  Initial φ values: {geom_results['initial_phi_count']}/12")
        print(f"  Final φ values: {geom_results['final_phi_count']}/12")
        print(f"  Geometric score: {geom_results['initial_geometric_score']:.3f} → "
              f"{geom_results['final_geometric_score']:.3f}")
        
        # Complete optimization
        opt_results = self.results['tests']['optimization']
        print(f"\nComplete Optimization:")
        for result in opt_results:
            print(f"  {result['name']}:")
            print(f"    φ discovery: {result['phi_discovery_rate']:.1f}%")
            print(f"    Improvement: {result['improvement']:.1f}%")
            
        # Performance
        perf_results = self.results['tests']['performance']
        print(f"\nPerformance:")
        print(f"  Compression: {perf_results['compression_us']:.1f} μs")
        print(f"  Decompression: {perf_results['decompression_us']:.1f} μs")
        print(f"  Throughput: {perf_results['throughput_states_per_sec']:.0f} states/sec")
        
        # Overall assessment
        all_passed = all([
            oh_results['n_operations'] == 48,
            oh_results['closure_test'],
            max(test.get('actual_compression', 0) for test in compression_results) > 40,
            geom_results['final_phi_count'] > geom_results['initial_phi_count'],
            all(r['phi_discovery_rate'] > 80 for r in opt_results)
        ])
        
        print(f"\n{'='*60}")
        print(f"OVERALL RESULT: {'ALL TESTS PASSED ✅' if all_passed else 'SOME TESTS FAILED ❌'}")
        print(f"{'='*60}")
        
        self.results['summary'] = {
            'all_passed': all_passed,
            'oh_symmetry_valid': oh_results['n_operations'] == 48,
            'max_compression_achieved': max(test.get('actual_compression', 0) 
                                          for test in compression_results),
            'geometric_phi_improvement': geom_results['final_phi_count'] - 
                                       geom_results['initial_phi_count'],
            'avg_phi_discovery_rate': np.mean([r['phi_discovery_rate'] 
                                              for r in opt_results]),
            'performance_throughput': perf_results['throughput_states_per_sec']
        }
        
    def save_results(self):
        """Save test results"""
        filename = f"v6_complete_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"/home/golde/Tenxsom_AI/testing/meta_opt_quant_v6/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    # Run complete test suite
    test_suite = V6CompleteTestSuite()
    test_suite.run_all_tests()