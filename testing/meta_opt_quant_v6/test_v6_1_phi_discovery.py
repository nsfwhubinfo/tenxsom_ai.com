#!/usr/bin/env python3
"""
Unit tests for META-OPT-QUANT V6.1 φ discovery fix
Tests the Symmetry-Modulated Geometric Optimization
"""

import sys
import os
import unittest
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.meta_opt_quant.enhanced_meta_optimizer_v6_1_phi_fix import (
    SymmetryModulatedGeometricOptimizer,
    EnhancedMetaOptimizerV6_1
)
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI, CuboctahedronCPUState
from phi_discovery_validator import PhiDiscoveryValidator


class TestSymmetryModulation(unittest.TestCase):
    """Test the symmetry modulation component"""
    
    def setUp(self):
        self.optimizer = SymmetryModulatedGeometricOptimizer()
        self.validator = PhiDiscoveryValidator()
    
    def test_diversity_measurement(self):
        """Test diversity measurement function"""
        # All same values - diversity should be 0
        same_values = [1.0] * 12
        diversity = self.optimizer._measure_diversity(same_values)
        self.assertAlmostEqual(diversity, 0.0, places=3)
        
        # Different values - diversity should be > 0
        diff_values = [1.0, 1.5, 2.0, 1.2, 1.8, 1.1, 1.9, 1.3, 1.7, 1.4, 1.6, 1.25]
        diversity = self.optimizer._measure_diversity(diff_values)
        self.assertGreater(diversity, 0.1)
    
    def test_symmetry_measurement(self):
        """Test symmetry measurement function"""
        # Perfect symmetry
        symmetric_values = [1.5] * 12
        symmetry = self.optimizer._measure_symmetry(symmetric_values)
        self.assertGreater(symmetry, 0.95)
        
        # Broken symmetry
        asymmetric_values = list(range(12))
        symmetry = self.optimizer._measure_symmetry(asymmetric_values)
        self.assertLess(symmetry, 0.5)
    
    def test_symmetry_breaking(self):
        """Test that symmetry actually gets broken"""
        # Start with symmetric state
        cpu_state = CuboctahedronCPUState()
        for i in range(12):
            cpu_state.vertices[i].value = int(1.0 * 1e15)
        
        # Apply optimization multiple times
        initial_values = [v.value / 1e15 for v in cpu_state.vertices]
        initial_diversity = self.optimizer._measure_diversity(initial_values)
        
        for _ in range(10):
            self.optimizer.apply_geometric_optimization(cpu_state, strength=0.5)
        
        # Check that diversity increased
        final_values = [v.value / 1e15 for v in cpu_state.vertices]
        final_diversity = self.optimizer._measure_diversity(final_values)
        
        self.assertGreater(final_diversity, initial_diversity + 0.01,
                          "Diversity should increase after optimization")
    
    def test_diversity_forces(self):
        """Test diversity-promoting forces"""
        # Uniform values
        uniform_values = [1.0] * 12
        forces = self.optimizer._calculate_diversity_forces(uniform_values)
        
        # Forces should push values in different directions
        positive_forces = sum(1 for f in forces if f > 0)
        negative_forces = sum(1 for f in forces if f < 0)
        
        self.assertGreater(positive_forces, 0)
        self.assertGreater(negative_forces, 0)
        self.assertNotEqual(positive_forces, negative_forces)


class TestV6_1Optimizer(unittest.TestCase):
    """Test the full V6.1 optimizer"""
    
    def setUp(self):
        self.optimizer = EnhancedMetaOptimizerV6_1()
        self.validator = PhiDiscoveryValidator()
    
    def test_direction_detection(self):
        """Test automatic optimization direction detection"""
        # Minimization objective
        def min_objective(params):
            return sum(v**2 for v in params.values())
        
        state = {'x0': 1.0, 'x1': 2.0, 'x2': 3.0}
        self.optimizer._detect_optimization_direction(min_objective, state)
        self.assertEqual(self.optimizer.optimization_direction, 'minimize')
        
        # Maximization objective
        def max_objective(params):
            return -sum(v**2 for v in params.values())
        
        self.optimizer.direction_detected = False
        self.optimizer._detect_optimization_direction(max_objective, state)
        self.assertEqual(self.optimizer.optimization_direction, 'maximize')
    
    def test_diverse_initialization(self):
        """Test that initialization creates diversity"""
        initial = {f'x{i}': 1.0 for i in range(12)}
        initialized = self.optimizer._geometric_initialization_v6_1(initial)
        
        values = list(initialized.values())
        diversity = np.std(values) / np.mean(values)
        
        self.assertGreater(diversity, 0.05,
                          "Initialization should create diverse values")
    
    def test_phi_ratio_discovery(self):
        """Test φ discovery for ratio-based objective"""
        def ratio_objective(params):
            """Objective that rewards φ ratios"""
            score = 0
            keys = sorted(params.keys())
            for i in range(len(keys)-1):
                if params[keys[i]] > 0:
                    ratio = params[keys[i+1]] / params[keys[i]]
                    score += (ratio - PHI)**2
            return score
        
        initial = {f'x{i}': 1.0 + i * 0.05 for i in range(6)}
        
        hints = {
            'direction': 'minimize',
            'requires_diversity': True
        }
        
        final, scores = self.optimizer.optimize(
            ratio_objective,
            initial,
            max_iterations=50,
            problem_name="test_ratio_discovery",
            optimization_hints=hints
        )
        
        # Check improvement
        self.assertLess(scores[-1], scores[0],
                       "Objective should improve")
        
        # Check φ discovery
        phi_score = self.validator.get_phi_score(final)
        self.assertGreater(phi_score, 10.0,
                          f"φ discovery should be > 10%, got {phi_score:.1f}%")
        
        # Check at least one ratio is close to φ
        keys = sorted(final.keys())
        ratios = []
        for i in range(len(keys)-1):
            if final[keys[i]] > 0:
                ratio = final[keys[i+1]] / final[keys[i]]
                ratios.append(ratio)
        
        min_error = min(abs(r - PHI) for r in ratios)
        self.assertLess(min_error, 0.2,
                       f"At least one ratio should be close to φ, best error: {min_error:.3f}")
    
    def test_direct_phi_objective(self):
        """Test φ discovery for direct φ objective"""
        def phi_objective(params):
            """Direct φ objective"""
            return sum((v - PHI)**2 for v in params.values())
        
        initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(12)}
        
        final, scores = self.optimizer.optimize(
            phi_objective,
            initial,
            max_iterations=50,
            problem_name="test_direct_phi"
        )
        
        # Check that it found some φ values
        phi_validation = self.validator.validate_phi_discovery(final)
        individual_phi = phi_validation['details']['individual_values']['rate']
        
        self.assertGreater(individual_phi, 20.0,
                          f"Should find individual φ values, got {individual_phi:.1f}%")
    
    def test_symmetry_preservation_option(self):
        """Test that symmetry can be preserved when not seeking diversity"""
        def symmetric_objective(params):
            """Objective that benefits from symmetry"""
            mean_val = np.mean(list(params.values()))
            return sum((v - mean_val)**2 for v in params.values())
        
        initial = {f'x{i}': np.random.uniform(0.8, 1.2) for i in range(12)}
        
        hints = {
            'direction': 'minimize',
            'requires_diversity': False  # Don't force diversity
        }
        
        final, scores = self.optimizer.optimize(
            symmetric_objective,
            initial,
            max_iterations=30,
            problem_name="test_symmetry_preservation",
            optimization_hints=hints
        )
        
        # Check that values converged to similar values
        values = list(final.values())
        diversity = np.std(values) / np.mean(values)
        
        self.assertLess(diversity, 0.1,
                       "Should maintain low diversity for symmetric objective")


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_complete_phi_discovery_pipeline(self):
        """Test the complete pipeline for φ discovery"""
        optimizer = EnhancedMetaOptimizerV6_1()
        validator = PhiDiscoveryValidator()
        
        # Test multiple objectives
        test_cases = [
            {
                'name': 'edge_ratios',
                'objective': lambda p: sum((p[f'x{i+1}']/(p[f'x{i}']+1e-10) - PHI)**2 
                                         for i in range(len(p)-1)),
                'size': 8,
                'target_phi': 15.0
            },
            {
                'name': 'mixed_phi',
                'objective': lambda p: sum((p[f'x{i}'] - [PHI, 1/PHI][i%2])**2 
                                         for i in range(len(p))),
                'size': 6,
                'target_phi': 25.0
            }
        ]
        
        for test in test_cases:
            with self.subTest(test=test['name']):
                initial = {f'x{i}': np.random.uniform(0.5, 2.5) 
                          for i in range(test['size'])}
                
                final, scores = optimizer.optimize(
                    test['objective'],
                    initial,
                    max_iterations=50,
                    problem_name=test['name']
                )
                
                phi_score = validator.get_phi_score(final)
                
                self.assertGreater(phi_score, test['target_phi'],
                                 f"{test['name']}: φ discovery {phi_score:.1f}% < target {test['target_phi']}%")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)