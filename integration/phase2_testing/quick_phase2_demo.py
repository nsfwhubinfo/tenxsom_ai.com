#!/usr/bin/env python3
"""
Quick Phase 2 Demo - No External Dependencies
============================================

Demonstrates Phase 2 functionality without psutil or other external packages.
Uses built-in Python modules for basic system monitoring.

For Tenxsom AI Phase 2 validation.
"""

import time
import gc
import os
import sys
import json
import traceback
from datetime import datetime
import resource  # Built-in resource monitoring

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integration.meta_chronosonic_bridge import (
    MetaChronosonicBridge,
    IntegrationConfig,
    PHI
)


class SimpleSystemMonitor:
    """Simple system monitor using built-in modules"""
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB"""
        # Using resource module (built-in)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return usage.ru_maxrss / 1024  # Convert to MB (Linux)
    
    @staticmethod
    def get_time_stats():
        """Get CPU time statistics"""
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return {
            'user_time': usage.ru_utime,
            'system_time': usage.ru_stime
        }


def demo_extended_validation():
    """Demonstrate extended validation concepts"""
    print("\n" + "="*60)
    print("DEMO: Extended Validation (Simplified)")
    print("="*60)
    
    # Test configurations
    configs = [
        {
            'name': 'balanced',
            'weights': {'optimization': 0.4, 'phi_discovery': 0.3, 'coherence': 0.3}
        },
        {
            'name': 'phi_focused',
            'weights': {'optimization': 0.2, 'phi_discovery': 0.6, 'coherence': 0.2}
        }
    ]
    
    results = []
    
    for config in configs:
        print(f"\nTesting configuration: {config['name']}")
        print(f"Weights: {config['weights']}")
        
        # Create bridge
        bridge_config = IntegrationConfig(
            v6_max_iterations=20,
            objective_weights=config['weights']
        )
        bridge = MetaChronosonicBridge(bridge_config)
        
        # Test objective
        def test_objective(params):
            # Rosenbrock with φ bias
            values = list(params.values())
            rosenbrock = sum(100*(values[i+1] - values[i]**2)**2 + (1-values[i])**2 
                           for i in range(len(values)-1))
            
            # φ bonus
            phi_bonus = 0
            for i in range(len(values)-1):
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    phi_bonus -= 5 * abs(ratio - PHI)
            
            return rosenbrock + phi_bonus
        
        # Initial parameters
        initial = {f'x{i}': 1.0 + i*0.2 for i in range(6)}
        
        # Record memory before
        mem_before = SimpleSystemMonitor.get_memory_usage()
        
        # Run optimization
        start_time = time.time()
        try:
            best, scores = bridge.optimize_integrated(
                test_objective,
                initial,
                max_iterations=20
            )
            runtime = time.time() - start_time
            
            # Analyze results
            improvement = (scores[0] - scores[-1]) / (scores[0] + 1e-10) * 100
            
            # φ discovery
            values = list(best.values())
            phi_count = 0
            for i in range(len(values)-1):
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    if abs(ratio - PHI) < 0.1:
                        phi_count += 1
            
            phi_score = phi_count / max(1, len(values)-1) * 100
            
            result = {
                'config': config['name'],
                'runtime': runtime,
                'improvement': improvement,
                'phi_score': phi_score,
                'memory_delta': SimpleSystemMonitor.get_memory_usage() - mem_before
            }
            
            results.append(result)
            
            print(f"  Runtime: {runtime:.2f}s")
            print(f"  Improvement: {improvement:.1f}%")
            print(f"  φ discovery: {phi_score:.1f}%")
            
        except Exception as e:
            print(f"  Error: {e}")
            results.append({'config': config['name'], 'error': str(e)})
    
    # Summary
    print("\nValidation Summary:")
    successful = sum(1 for r in results if 'error' not in r)
    print(f"  Configurations tested: {len(configs)}")
    print(f"  Successful: {successful}/{len(configs)}")
    
    if successful == len(configs):
        print("  ✅ Extended validation concepts working!")
    
    return results


def demo_stability_test():
    """Demonstrate stability testing concepts"""
    print("\n" + "="*60)
    print("DEMO: Stability Testing (Simplified)")
    print("="*60)
    
    # Simulate different stress scenarios
    scenarios = [
        {
            'name': 'continuous_optimization',
            'iterations': 5,
            'n_params': 8
        },
        {
            'name': 'memory_stress',
            'iterations': 3,
            'n_params': 20
        }
    ]
    
    stability_events = []
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        
        try:
            # Create bridge
            config = IntegrationConfig(v6_max_iterations=10)
            bridge = MetaChronosonicBridge(config)
            
            # Track memory
            initial_memory = SimpleSystemMonitor.get_memory_usage()
            
            # Run multiple optimizations
            for i in range(scenario['iterations']):
                # Random objective
                def random_objective(params):
                    import numpy as np
                    values = np.array(list(params.values()))
                    return np.sum(values**2 * np.random.rand())
                
                initial = {f'x{j}': 1.0 for j in range(scenario['n_params'])}
                
                best, scores = bridge.optimize_integrated(
                    random_objective,
                    initial,
                    max_iterations=10
                )
                
                print(f"  Run {i+1}: Score improvement: {(scores[0]-scores[-1])/scores[0]*100:.1f}%")
            
            # Check memory growth
            final_memory = SimpleSystemMonitor.get_memory_usage()
            memory_growth = final_memory - initial_memory
            
            print(f"  Memory growth: {memory_growth:.1f} MB")
            
            if memory_growth < 100:  # Arbitrary threshold
                print("  ✅ Memory stable")
            else:
                print("  ⚠️ Excessive memory growth")
                stability_events.append({
                    'scenario': scenario['name'],
                    'issue': 'memory_growth',
                    'value': memory_growth
                })
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            stability_events.append({
                'scenario': scenario['name'],
                'issue': 'exception',
                'error': str(e)
            })
    
    # Summary
    print("\nStability Summary:")
    print(f"  Scenarios tested: {len(scenarios)}")
    print(f"  Stability events: {len(stability_events)}")
    
    if len(stability_events) == 0:
        print("  ✅ System stable under stress!")
    
    return stability_events


def demo_performance_optimization():
    """Demonstrate performance optimization concepts"""
    print("\n" + "="*60)
    print("DEMO: Performance Optimization")
    print("="*60)
    
    import numpy as np
    
    # Compare standard vs optimized operations
    print("\n1. φ Calculation Performance:")
    
    params = {f'x{i}': PHI**i for i in range(10)}
    values = list(params.values())
    
    # Standard implementation
    start = time.time()
    for _ in range(1000):
        phi_errors = []
        for i in range(len(values) - 1):
            if values[i] > 0:
                ratio = values[i+1] / values[i]
                error = abs(ratio - PHI)
                phi_errors.append(error)
        score = sum(phi_errors) / len(phi_errors) if phi_errors else 0
    standard_time = time.time() - start
    
    # Optimized implementation
    start = time.time()
    values_array = np.array(values)
    for _ in range(1000):
        ratios = values_array[1:] / values_array[:-1]
        errors = np.abs(ratios - PHI)
        score = np.mean(errors)
    optimized_time = time.time() - start
    
    speedup = standard_time / optimized_time
    
    print(f"  Standard: {standard_time:.3f}s")
    print(f"  Optimized: {optimized_time:.3f}s")
    print(f"  Speedup: {speedup:.2f}x")
    
    # Caching demonstration
    print("\n2. Caching Performance:")
    
    cache = {}
    cache_hits = 0
    
    def cached_calculation(key, func):
        nonlocal cache_hits
        if key in cache:
            cache_hits += 1
            return cache[key]
        result = func()
        cache[key] = result
        return result
    
    # Simulate repeated calculations
    start = time.time()
    for i in range(1000):
        key = f"calc_{i % 10}"  # Only 10 unique calculations
        result = cached_calculation(key, lambda: sum(range(1000)))
    cached_time = time.time() - start
    
    print(f"  Cache hits: {cache_hits}/1000 ({cache_hits/10:.0f}%)")
    print(f"  Time with caching: {cached_time:.3f}s")
    
    # Performance summary
    print("\nPerformance Optimization Summary:")
    print(f"  Vectorization speedup: {speedup:.2f}x")
    print(f"  Cache efficiency: {cache_hits/10:.0f}%")
    
    if speedup > 1.5 and cache_hits > 800:
        print("  ✅ Performance optimizations effective!")
    
    return {
        'vectorization_speedup': speedup,
        'cache_hits': cache_hits
    }


def run_phase2_demo():
    """Run complete Phase 2 demonstration"""
    print("=" * 80)
    print("PHASE 2 DEMONSTRATION - No External Dependencies")
    print("=" * 80)
    print(f"Start time: {datetime.now()}")
    
    results = {
        'demo_id': f'phase2_demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'tests': {}
    }
    
    # Run demos
    try:
        # Extended validation
        validation_results = demo_extended_validation()
        results['tests']['validation'] = {
            'success': len([r for r in validation_results if 'error' not in r]) > 0,
            'results': validation_results
        }
        
        # Stability testing
        stability_events = demo_stability_test()
        results['tests']['stability'] = {
            'success': len(stability_events) == 0,
            'events': stability_events
        }
        
        # Performance optimization
        perf_results = demo_performance_optimization()
        results['tests']['performance'] = {
            'success': perf_results['vectorization_speedup'] > 1.5,
            'results': perf_results
        }
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 80)
    print("PHASE 2 DEMO SUMMARY")
    print("=" * 80)
    
    total_tests = len(results['tests'])
    passed_tests = sum(1 for t in results['tests'].values() if t.get('success', False))
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    
    for test_name, test_result in results['tests'].items():
        status = "PASS" if test_result.get('success', False) else "FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n✅ All Phase 2 concepts demonstrated successfully!")
        print("\nPhase 2 capabilities verified:")
        print("  - Extended validation with multiple configurations")
        print("  - Stability testing under stress scenarios")
        print("  - Performance optimization techniques")
        print("\nReady to proceed with full Phase 2 testing when dependencies are available.")
    else:
        print("\n⚠️ Some demos failed. Review output above.")
    
    # Save results
    filename = f"phase2_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {filename}")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_phase2_demo()
    sys.exit(0 if success else 1)