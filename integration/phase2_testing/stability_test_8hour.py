#!/usr/bin/env python3
"""
Phase 2: 8-Hour Stability Test
==============================

Extended stability test for META-CHRONOSONIC integration focusing on:
- Long-term stability
- Memory leak detection
- Performance consistency
- Error recovery
- Continuous optimization quality

For Tenxsom AI production readiness validation.
"""

import numpy as np
import time
import psutil
import json
import gc
import threading
import queue
from datetime import datetime, timedelta
import traceback
from typing import Dict, List, Optional, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integration.meta_chronosonic_bridge import (
    MetaChronosonicBridge,
    IntegrationConfig,
    PHI
)


class StabilityMonitor:
    """Continuous monitoring of system health"""
    
    def __init__(self, interval: float = 60.0):
        self.interval = interval
        self.running = False
        self.thread = None
        self.metrics_queue = queue.Queue()
        self.process = psutil.Process()
        
    def start(self):
        """Start monitoring thread"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = {
                    'timestamp': time.time(),
                    'memory_mb': self.process.memory_info().rss / 1024 / 1024,
                    'cpu_percent': self.process.cpu_percent(interval=1),
                    'threads': self.process.num_threads(),
                    'open_files': len(self.process.open_files()),
                }
                
                # System-wide metrics
                metrics['system_memory_percent'] = psutil.virtual_memory().percent
                metrics['system_cpu_percent'] = psutil.cpu_percent(interval=1)
                
                self.metrics_queue.put(metrics)
                
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(self.interval)
    
    def get_metrics(self) -> List[Dict]:
        """Get all collected metrics"""
        metrics = []
        while not self.metrics_queue.empty():
            try:
                metrics.append(self.metrics_queue.get_nowait())
            except queue.Empty:
                break
        return metrics


class StabilityTest8Hour:
    """8-hour stability test for production validation"""
    
    def __init__(self, duration_hours: float = 8.0):
        self.duration = duration_hours * 3600
        self.monitor = StabilityMonitor(interval=30)  # Monitor every 30s
        
        # Test scenarios
        self.scenarios = [
            {
                'name': 'continuous_optimization',
                'description': 'Continuous optimization with varied objectives',
                'duration_ratio': 0.3,  # 30% of total time
                'config': IntegrationConfig(
                    v6_max_iterations=100,
                    cs_use_simplified=False,
                    param_mapping_mode="geometric"
                )
            },
            {
                'name': 'stress_test',
                'description': 'High-frequency operations and large parameter sets',
                'duration_ratio': 0.2,
                'config': IntegrationConfig(
                    v6_max_iterations=50,
                    state_sync_interval=1,  # Stress synchronization
                    cs_use_simplified=False
                )
            },
            {
                'name': 'memory_stress',
                'description': 'Large parameter sets to test memory management',
                'duration_ratio': 0.2,
                'config': IntegrationConfig(
                    v6_max_iterations=150,
                    cs_use_simplified=False
                )
            },
            {
                'name': 'recovery_test',
                'description': 'Error injection and recovery validation',
                'duration_ratio': 0.15,
                'config': IntegrationConfig(
                    v6_max_iterations=80
                )
            },
            {
                'name': 'endurance_test',
                'description': 'Long-running single optimization',
                'duration_ratio': 0.15,
                'config': IntegrationConfig(
                    v6_max_iterations=500,
                    cs_use_simplified=True
                )
            }
        ]
        
        # Results tracking
        self.results = {
            'test_id': f'stability_8h_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'duration_hours': duration_hours,
            'scenarios': {},
            'monitoring_data': [],
            'errors': [],
            'recovery_events': [],
            'summary': {}
        }
    
    def run_test(self):
        """Run the complete 8-hour stability test"""
        print("=" * 80)
        print("META-CHRONOSONIC 8-HOUR STABILITY TEST")
        print("=" * 80)
        print(f"Start time: {datetime.now()}")
        print(f"Duration: {self.duration / 3600:.1f} hours")
        print(f"Scenarios: {len(self.scenarios)}")
        print()
        
        self.start_time = time.time()
        self.results['start_time'] = datetime.now().isoformat()
        
        # Start monitoring
        self.monitor.start()
        print("System monitoring started...")
        
        try:
            # Run each scenario
            for scenario in self.scenarios:
                scenario_duration = self.duration * scenario['duration_ratio']
                self._run_scenario(scenario, scenario_duration)
                
                # Check if we've exceeded time limit
                if time.time() - self.start_time > self.duration:
                    print("\nTime limit reached.")
                    break
            
            # Final endurance run if time remains
            remaining_time = self.duration - (time.time() - self.start_time)
            if remaining_time > 600:  # At least 10 minutes
                print(f"\nRunning final endurance test for {remaining_time/60:.1f} minutes...")
                self._run_endurance_test(remaining_time)
        
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user.")
        except Exception as e:
            print(f"\n\nCritical error: {e}")
            self.results['errors'].append({
                'time': time.time() - self.start_time,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        
        finally:
            # Stop monitoring
            self.monitor.stop()
            
            # Collect final metrics
            self.results['monitoring_data'] = self.monitor.get_metrics()
            
            # Final analysis
            self._final_analysis()
            
            # Save results
            self._save_results()
    
    def _run_scenario(self, scenario: Dict, duration: float):
        """Run a specific test scenario"""
        scenario_name = scenario['name']
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario_name}")
        print(f"{'='*60}")
        print(f"Description: {scenario['description']}")
        print(f"Duration: {duration/60:.1f} minutes")
        
        scenario_results = {
            'name': scenario_name,
            'start_time': time.time() - self.start_time,
            'runs': [],
            'errors': [],
            'metrics': []
        }
        
        scenario_start = time.time()
        
        if scenario_name == 'continuous_optimization':
            self._continuous_optimization(scenario, duration, scenario_results)
        elif scenario_name == 'stress_test':
            self._stress_test(scenario, duration, scenario_results)
        elif scenario_name == 'memory_stress':
            self._memory_stress_test(scenario, duration, scenario_results)
        elif scenario_name == 'recovery_test':
            self._recovery_test(scenario, duration, scenario_results)
        elif scenario_name == 'endurance_test':
            self._endurance_test(scenario, duration, scenario_results)
        
        scenario_results['end_time'] = time.time() - self.start_time
        scenario_results['total_duration'] = time.time() - scenario_start
        
        # Collect monitoring metrics during scenario
        scenario_results['monitoring_snapshot'] = self.monitor.get_metrics()
        
        self.results['scenarios'][scenario_name] = scenario_results
        
        # Force garbage collection between scenarios
        gc.collect()
        time.sleep(2)
    
    def _continuous_optimization(self, scenario: Dict, duration: float, results: Dict):
        """Run continuous optimization with varied objectives"""
        bridge = MetaChronosonicBridge(scenario['config'])
        
        objectives = [
            ('quadratic', lambda p: sum(v**2 for v in p.values())),
            ('phi_seeking', lambda p: sum((p[f'x{i+1}']/(p[f'x{i}']+1e-10) - PHI)**2 
                                        for i in range(len(p)-1))),
            ('coherence', lambda p: np.var(list(p.values())))
        ]
        
        run_count = 0
        scenario_start = time.time()
        
        while time.time() - scenario_start < duration:
            run_count += 1
            
            # Rotate objectives
            obj_name, objective = objectives[(run_count - 1) % len(objectives)]
            
            # Random parameters
            n_params = np.random.randint(6, 13)
            initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(n_params)}
            
            print(f"\n  Run {run_count} ({obj_name}, {n_params} params):")
            
            try:
                start = time.time()
                best, scores = bridge.optimize_integrated(
                    objective,
                    initial,
                    max_iterations=scenario['config'].v6_max_iterations
                )
                
                runtime = time.time() - start
                improvement = (scores[0] - scores[-1]) / (scores[0] + 1e-10) * 100
                
                results['runs'].append({
                    'run': run_count,
                    'objective': obj_name,
                    'runtime': runtime,
                    'improvement': improvement,
                    'n_params': n_params
                })
                
                print(f"    Runtime: {runtime:.1f}s, Improvement: {improvement:.1f}%")
                
            except Exception as e:
                print(f"    Error: {e}")
                results['errors'].append({
                    'run': run_count,
                    'error': str(e)
                })
            
            # Brief pause
            time.sleep(0.5)
    
    def _stress_test(self, scenario: Dict, duration: float, results: Dict):
        """High-frequency operations stress test"""
        bridge = MetaChronosonicBridge(scenario['config'])
        
        def stress_objective(params):
            # Complex calculation to stress CPU
            values = np.array(list(params.values()))
            return np.sum(np.sin(values) * np.cos(values**2)) + np.sum(values**2)
        
        operations = 0
        scenario_start = time.time()
        
        while time.time() - scenario_start < duration:
            # Rapid small optimizations
            n_params = np.random.randint(15, 25)  # Larger parameter sets
            initial = {f'x{i}': np.random.randn() for i in range(n_params)}
            
            try:
                # Quick optimization
                best, scores = bridge.optimize_integrated(
                    stress_objective,
                    initial,
                    max_iterations=scenario['config'].v6_max_iterations
                )
                
                operations += 1
                
                if operations % 10 == 0:
                    print(f"\n  Operations completed: {operations}")
                    
                    # Check system health
                    memory_mb = bridge.process.memory_info().rss / 1024 / 1024
                    print(f"    Memory usage: {memory_mb:.1f} MB")
                
            except Exception as e:
                results['errors'].append({
                    'operation': operations,
                    'error': str(e)
                })
        
        results['total_operations'] = operations
        results['ops_per_minute'] = operations / (duration / 60)
        print(f"\n  Total operations: {operations} ({results['ops_per_minute']:.1f} ops/min)")
    
    def _memory_stress_test(self, scenario: Dict, duration: float, results: Dict):
        """Test memory management with large parameter sets"""
        
        def memory_objective(params):
            # Create temporary large arrays
            values = np.array(list(params.values()))
            temp = np.outer(values, values)  # Memory intensive
            return np.sum(temp)
        
        memory_samples = []
        scenario_start = time.time()
        run = 0
        
        while time.time() - scenario_start < duration:
            run += 1
            
            # Progressively larger parameter sets
            n_params = min(50, 20 + run * 2)
            
            print(f"\n  Memory test run {run} ({n_params} parameters):")
            
            # Measure memory before
            gc.collect()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            
            try:
                bridge = MetaChronosonicBridge(scenario['config'])
                initial = {f'x{i}': np.random.rand() for i in range(n_params)}
                
                best, scores = bridge.optimize_integrated(
                    memory_objective,
                    initial,
                    max_iterations=50
                )
                
                # Measure memory after
                memory_after = psutil.Process().memory_info().rss / 1024 / 1024
                memory_delta = memory_after - memory_before
                
                memory_samples.append({
                    'run': run,
                    'n_params': n_params,
                    'memory_before': memory_before,
                    'memory_after': memory_after,
                    'delta': memory_delta
                })
                
                print(f"    Memory: {memory_before:.1f} → {memory_after:.1f} MB (Δ{memory_delta:+.1f})")
                
                # Cleanup
                del bridge
                gc.collect()
                
            except Exception as e:
                print(f"    Error: {e}")
                results['errors'].append({
                    'run': run,
                    'n_params': n_params,
                    'error': str(e)
                })
            
            time.sleep(2)  # Allow GC
        
        results['memory_samples'] = memory_samples
        
        # Analyze memory growth
        if memory_samples:
            growth = memory_samples[-1]['memory_after'] - memory_samples[0]['memory_before']
            print(f"\n  Total memory growth: {growth:.1f} MB")
    
    def _recovery_test(self, scenario: Dict, duration: float, results: Dict):
        """Test error recovery capabilities"""
        recovery_events = []
        scenario_start = time.time()
        
        while time.time() - scenario_start < duration:
            test_type = np.random.choice(['nan_injection', 'invalid_params', 'resource_limit'])
            
            print(f"\n  Testing recovery from: {test_type}")
            
            try:
                if test_type == 'nan_injection':
                    # Inject NaN values
                    def nan_objective(params):
                        if np.random.rand() < 0.3:
                            return np.nan
                        return sum(v**2 for v in params.values())
                    
                    bridge = MetaChronosonicBridge(scenario['config'])
                    initial = {f'x{i}': 1.0 for i in range(6)}
                    
                    best, scores = bridge.optimize_integrated(
                        nan_objective,
                        initial,
                        max_iterations=30
                    )
                    
                    # Check if it handled NaN
                    valid_scores = [s for s in scores if not np.isnan(s)]
                    recovery_events.append({
                        'type': test_type,
                        'success': len(valid_scores) > 0,
                        'details': f"{len(valid_scores)}/{len(scores)} valid scores"
                    })
                
                elif test_type == 'invalid_params':
                    # Test with invalid parameter ranges
                    def constrained_objective(params):
                        # Penalize invalid ranges heavily
                        penalty = sum(1000 if v < 0 or v > 10 else 0 for v in params.values())
                        return sum(v**2 for v in params.values()) + penalty
                    
                    bridge = MetaChronosonicBridge(scenario['config'])
                    initial = {f'x{i}': np.random.uniform(-5, 15) for i in range(8)}
                    
                    best, scores = bridge.optimize_integrated(
                        constrained_objective,
                        initial,
                        max_iterations=50
                    )
                    
                    # Check if converged to valid range
                    all_valid = all(0 <= v <= 10 for v in best.values())
                    recovery_events.append({
                        'type': test_type,
                        'success': all_valid,
                        'details': f"Converged to valid range: {all_valid}"
                    })
                
                else:  # resource_limit
                    # Test with resource-intensive objective
                    def expensive_objective(params):
                        values = np.array(list(params.values()))
                        # Expensive matrix operations
                        for _ in range(100):
                            temp = np.linalg.svd(np.random.randn(50, 50))[1]
                        return np.sum(values**2)
                    
                    bridge = MetaChronosonicBridge(scenario['config'])
                    initial = {f'x{i}': 1.0 for i in range(10)}
                    
                    start = time.time()
                    best, scores = bridge.optimize_integrated(
                        expensive_objective,
                        initial,
                        max_iterations=20
                    )
                    
                    runtime = time.time() - start
                    recovery_events.append({
                        'type': test_type,
                        'success': runtime < 300,  # Should complete in 5 minutes
                        'details': f"Runtime: {runtime:.1f}s"
                    })
                
                print(f"    Recovery: {'SUCCESS' if recovery_events[-1]['success'] else 'FAILED'}")
                
            except Exception as e:
                print(f"    Exception during recovery test: {e}")
                recovery_events.append({
                    'type': test_type,
                    'success': False,
                    'details': f"Exception: {str(e)}"
                })
            
            time.sleep(5)
        
        results['recovery_events'] = recovery_events
        self.results['recovery_events'].extend(recovery_events)
        
        # Summary
        successful = sum(1 for e in recovery_events if e['success'])
        print(f"\n  Recovery success rate: {successful}/{len(recovery_events)}")
    
    def _endurance_test(self, scenario: Dict, duration: float, results: Dict):
        """Single long-running optimization"""
        print("\n  Starting endurance optimization...")
        
        # Complex multi-modal objective
        def endurance_objective(params):
            values = np.array(list(params.values()))
            
            # Multiple components
            quadratic = np.sum(values**2)
            sinusoidal = np.sum(np.sin(5 * values))
            exponential = np.sum(np.exp(-np.abs(values - PHI)))
            
            return quadratic + 0.1 * sinusoidal - exponential
        
        bridge = MetaChronosonicBridge(scenario['config'])
        initial = {f'x{i}': np.random.uniform(0, 3) for i in range(12)}
        
        start_time = time.time()
        checkpoint_interval = 60  # Report every minute
        last_checkpoint = start_time
        
        try:
            # Custom optimization loop for progress tracking
            state = initial.copy()
            iteration = 0
            max_iter = int(duration / 10)  # Rough estimate
            
            while time.time() - start_time < duration:
                # Single optimization step
                state, iter_scores = bridge.optimize_integrated(
                    endurance_objective,
                    state,
                    max_iterations=10
                )
                
                iteration += 10
                
                # Progress checkpoint
                if time.time() - last_checkpoint > checkpoint_interval:
                    elapsed = time.time() - start_time
                    current_score = endurance_objective(state)
                    
                    print(f"    [{elapsed/60:.1f}m] Iteration {iteration}, Score: {current_score:.4f}")
                    
                    # Check system health
                    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                    cpu_percent = psutil.Process().cpu_percent(interval=0.1)
                    coherence = bridge.chronosonic.get_system_state()['chakra_coherence']
                    
                    print(f"      Memory: {memory_mb:.1f} MB, CPU: {cpu_percent:.1f}%, Coherence: {coherence:.3f}")
                    
                    last_checkpoint = time.time()
            
            # Final results
            final_score = endurance_objective(state)
            initial_score = endurance_objective(initial)
            improvement = (initial_score - final_score) / (initial_score + 1e-10) * 100
            
            results['endurance_metrics'] = {
                'total_iterations': iteration,
                'runtime': time.time() - start_time,
                'initial_score': initial_score,
                'final_score': final_score,
                'improvement': improvement
            }
            
            print(f"\n  Endurance test completed:")
            print(f"    Iterations: {iteration}")
            print(f"    Improvement: {improvement:.1f}%")
            
        except Exception as e:
            print(f"    Endurance test error: {e}")
            results['errors'].append({
                'iteration': iteration,
                'error': str(e)
            })
    
    def _run_endurance_test(self, duration: float):
        """Final endurance test with remaining time"""
        scenario = {
            'name': 'final_endurance',
            'config': IntegrationConfig(
                v6_max_iterations=100,
                cs_use_simplified=False,
                param_mapping_mode="geometric"
            )
        }
        
        results = {
            'name': 'final_endurance',
            'start_time': time.time() - self.start_time,
            'runs': [],
            'errors': []
        }
        
        self._endurance_test(scenario, duration, results)
        
        results['end_time'] = time.time() - self.start_time
        self.results['scenarios']['final_endurance'] = results
    
    def _final_analysis(self):
        """Comprehensive final analysis"""
        print("\n" + "=" * 80)
        print("8-HOUR STABILITY TEST - FINAL ANALYSIS")
        print("=" * 80)
        
        total_runtime = time.time() - self.start_time
        self.results['end_time'] = datetime.now().isoformat()
        self.results['total_runtime_hours'] = total_runtime / 3600
        
        print(f"\nTotal Runtime: {total_runtime/3600:.2f} hours")
        
        # Scenario summary
        print("\nScenario Summary:")
        for name, scenario in self.results['scenarios'].items():
            errors = len(scenario.get('errors', []))
            print(f"  {name}: {errors} errors")
        
        # Error analysis
        total_errors = sum(len(s.get('errors', [])) for s in self.results['scenarios'].values())
        total_errors += len(self.results['errors'])
        
        print(f"\nTotal Errors: {total_errors}")
        
        # Recovery analysis
        if self.results['recovery_events']:
            successful_recoveries = sum(1 for e in self.results['recovery_events'] if e['success'])
            recovery_rate = successful_recoveries / len(self.results['recovery_events']) * 100
            print(f"Recovery Success Rate: {recovery_rate:.1f}%")
        
        # Memory analysis
        if self.results['monitoring_data']:
            memory_data = [m['memory_mb'] for m in self.results['monitoring_data']]
            initial_memory = memory_data[0]
            final_memory = memory_data[-1]
            peak_memory = max(memory_data)
            
            print(f"\nMemory Analysis:")
            print(f"  Initial: {initial_memory:.1f} MB")
            print(f"  Final: {final_memory:.1f} MB")
            print(f"  Peak: {peak_memory:.1f} MB")
            print(f"  Growth: {final_memory - initial_memory:.1f} MB")
            
            # Check for memory leaks
            memory_growth_rate = (final_memory - initial_memory) / (total_runtime / 3600)
            print(f"  Growth rate: {memory_growth_rate:.1f} MB/hour")
            
            memory_stable = memory_growth_rate < 50  # Less than 50MB/hour
        else:
            memory_stable = False
        
        # Performance consistency
        all_runtimes = []
        for scenario in self.results['scenarios'].values():
            if 'runs' in scenario:
                all_runtimes.extend([r['runtime'] for r in scenario['runs'] if 'runtime' in r])
        
        if all_runtimes:
            runtime_stability = np.std(all_runtimes) / np.mean(all_runtimes)
            print(f"\nPerformance Consistency:")
            print(f"  Runtime stability: {runtime_stability:.3f}")
            print(f"  Average runtime: {np.mean(all_runtimes):.1f}s")
            
            performance_stable = runtime_stability < 0.5
        else:
            performance_stable = False
        
        # Success criteria
        print("\n" + "-" * 60)
        print("Stability Criteria Evaluation:")
        print("-" * 60)
        
        criteria = {
            'Total errors < 10': total_errors < 10,
            'Recovery rate > 80%': recovery_rate > 80 if 'recovery_rate' in locals() else False,
            'Memory growth < 50MB/hour': memory_stable,
            'Performance stability < 0.5': performance_stable,
            'Completed full duration': total_runtime >= self.duration * 0.95
        }
        
        passed = 0
        for criterion, result in criteria.items():
            status = "PASS" if result else "FAIL"
            print(f"  {criterion}: {status}")
            if result:
                passed += 1
        
        success_rate = passed / len(criteria) * 100
        print(f"\nSuccess Rate: {passed}/{len(criteria)} ({success_rate:.0f}%)")
        
        self.results['summary'] = {
            'total_errors': total_errors,
            'recovery_rate': recovery_rate if 'recovery_rate' in locals() else 0,
            'memory_growth_mb_per_hour': memory_growth_rate if 'memory_growth_rate' in locals() else 0,
            'runtime_stability': runtime_stability if 'runtime_stability' in locals() else 0,
            'criteria_passed': passed,
            'success_rate': success_rate
        }
        
        if success_rate >= 80:
            print("\n✅ 8-HOUR STABILITY TEST PASSED!")
            print("The META-CHRONOSONIC integration is stable for production use.")
            print("Ready for 24-hour stress test or deployment.")
        else:
            print("\n⚠️ 8-HOUR STABILITY TEST NEEDS ATTENTION")
            print("Review failed criteria and error logs.")
    
    def _save_results(self):
        """Save comprehensive test results"""
        filename = f"stability_8h_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Clean up for JSON serialization
        def clean_for_json(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(v) for v in obj]
            elif hasattr(obj, '__dict__'):
                return str(obj)
            return obj
        
        results_json = clean_for_json(self.results)
        
        with open(filename, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        print(f"\nDetailed results saved to: {filename}")


def main():
    """Run the 8-hour stability test"""
    import argparse
    
    parser = argparse.ArgumentParser(description='8-Hour Stability Test')
    parser.add_argument('--duration', type=float, default=8.0,
                       help='Test duration in hours (default: 8.0)')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick 30-minute test instead')
    
    args = parser.parse_args()
    
    if args.quick:
        duration = 0.5  # 30 minutes
        print("Running quick 30-minute stability test...")
    else:
        duration = args.duration
    
    # Create and run test
    test = StabilityTest8Hour(duration_hours=duration)
    
    try:
        test.run_test()
    except Exception as e:
        print(f"\n\nCritical failure: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())