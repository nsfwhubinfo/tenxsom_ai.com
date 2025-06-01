#!/usr/bin/env python3
"""
Continuous Testing Framework for META-OPT-QUANT
Runs 24/7 dataset training and optimization tests
"""

import os
import sys
import time
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from typing import Dict, List, Any, Tuple
import threading
import queue
import signal

# Add meta_opt_quant to path
sys.path.append(str(Path(__file__).parent.parent / "research" / "meta_opt_quant"))

from enhanced_meta_optimizer import EnhancedMetaOptimizer
from global_cache_manager import get_global_cache

class ContinuousTestingFramework:
    """24/7 testing framework for META-OPT-QUANT optimization"""
    
    def __init__(self, results_dir: str = "./continuous_test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Test queue for continuous processing
        self.test_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Control flags
        self.running = False
        self.threads = []
        
        # Statistics tracking
        self.stats = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_iterations': 0,
            'total_time': 0.0,
            'golden_ratio_discoveries': 0,
            'best_performance_gain': 0.0,
            'start_time': None
        }
        
        # Test datasets
        self.test_datasets = self._load_test_datasets()
        
    def setup_logging(self):
        """Configure logging for 24/7 operation"""
        log_file = self.results_dir / f"continuous_test_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('ContinuousMetaOptTest')
        
    def _load_test_datasets(self) -> List[Dict[str, Any]]:
        """Load or generate test datasets"""
        datasets = []
        
        # 1. Standard Optimization Benchmarks
        datasets.append({
            'name': 'rosenbrock',
            'type': 'continuous',
            'dimensions': 5,
            'objective': self._rosenbrock,
            'optimal_value': 0.0,
            'initial_range': (-5, 5)
        })
        
        datasets.append({
            'name': 'rastrigin',
            'type': 'multimodal',
            'dimensions': 10,
            'objective': self._rastrigin,
            'optimal_value': 0.0,
            'initial_range': (-5.12, 5.12)
        })
        
        datasets.append({
            'name': 'sphere',
            'type': 'convex',
            'dimensions': 20,
            'objective': self._sphere,
            'optimal_value': 0.0,
            'initial_range': (-10, 10)
        })
        
        # 2. Golden Ratio Seeking Problems
        datasets.append({
            'name': 'golden_ratio_direct',
            'type': 'golden_seeking',
            'dimensions': 6,
            'objective': self._golden_ratio_objective,
            'optimal_value': 100.0,  # Maximum when all ratios are φ
            'initial_range': (0.1, 3.0)
        })
        
        # 3. COS-EXP Inspired Problems
        datasets.append({
            'name': 'cos_exp_alignment',
            'type': 'cos_exp',
            'dimensions': 7,
            'objective': self._cos_exp_objective,
            'optimal_value': None,  # Complex multi-objective
            'initial_range': (0.1, 2.0)
        })
        
        # 4. Dynamic/Adaptive Problems
        datasets.append({
            'name': 'dynamic_landscape',
            'type': 'dynamic',
            'dimensions': 8,
            'objective': self._dynamic_objective,
            'optimal_value': None,
            'initial_range': (-3, 3)
        })
        
        # 5. High-Dimensional Problems
        datasets.append({
            'name': 'high_dim_quadratic',
            'type': 'high_dimensional',
            'dimensions': 100,
            'objective': self._high_dim_quadratic,
            'optimal_value': 0.0,
            'initial_range': (-1, 1)
        })
        
        return datasets
    
    # Objective Functions
    
    def _rosenbrock(self, state: Dict[str, Any]) -> float:
        """Rosenbrock function"""
        score = 0.0
        dims = [v for k, v in state.items() if k.startswith('x') and isinstance(v, (int, float))]
        for i in range(len(dims) - 1):
            score -= (100 * (dims[i+1] - dims[i]**2)**2 + (1 - dims[i])**2)
        return score
    
    def _rastrigin(self, state: Dict[str, Any]) -> float:
        """Rastrigin function"""
        A = 10
        score = 0.0
        dims = [v for k, v in state.items() if k.startswith('x') and isinstance(v, (int, float))]
        n = len(dims)
        for x in dims:
            score -= (x**2 - A * np.cos(2 * np.pi * x))
        return -(A * n + score)  # Negative because we maximize
    
    def _sphere(self, state: Dict[str, Any]) -> float:
        """Sphere function"""
        score = 0.0
        for key, value in state.items():
            if key.startswith('x') and isinstance(value, (int, float)):
                score -= value**2
        return score
    
    def _golden_ratio_objective(self, state: Dict[str, Any]) -> float:
        """Golden ratio seeking objective"""
        phi = 1.618033988749895
        score = 0.0
        
        # Check F-V-E ratio
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        
        if E > 0:
            fve_ratio = F * V / E
            score += 20 * np.exp(-((fve_ratio - phi)**2))
        
        # Check sequential ratios
        dims = sorted([v for k, v in state.items() if k.startswith('x') and isinstance(v, (int, float))])
        for i in range(len(dims) - 1):
            if dims[i] > 0:
                ratio = dims[i+1] / dims[i]
                score += 10 * np.exp(-((ratio - phi)**2))
        
        return score
    
    def _cos_exp_objective(self, state: Dict[str, Any]) -> float:
        """COS-EXP inspired objective"""
        score = 0.0
        
        # Particle constants
        alpha, beta, gamma, phi = 0.223, 1.344, 1.075, 1.618
        
        # Coherence alignment
        coherence = state.get('coherence', 0.5)
        score += 10 * np.exp(-((coherence - alpha)**2))
        
        # F-V-E dynamics
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        
        # Resonance condition
        if F > 0:
            resonance = V / (F * beta)
            score += 10 * np.exp(-((resonance - 1.0)**2))
        
        # Golden ratio bonus
        if E > 0:
            fve_ratio = F * V / E
            score += 20 * np.exp(-((fve_ratio - phi)**2))
        
        # Quantum superposition
        score += 5 * np.sin(F * np.pi) * np.cos(V * np.pi) * E
        
        return score
    
    def _dynamic_objective(self, state: Dict[str, Any]) -> float:
        """Dynamic objective that changes over time"""
        # Use iteration count to change landscape
        iteration = state.get('_iteration', 0)
        phase = (iteration % 100) / 100.0
        
        # Shift optimum based on phase
        shifted_optimum = [np.sin(phase * 2 * np.pi) * 2, 
                          np.cos(phase * 2 * np.pi) * 2]
        
        score = 0.0
        dims = [v for k, v in sorted(state.items()) if k.startswith('x') and isinstance(v, (int, float))]
        
        for i, x in enumerate(dims[:2]):
            score -= (x - shifted_optimum[i % 2])**2
        
        # Add remaining dimensions
        for x in dims[2:]:
            score -= x**2
        
        return score
    
    def _high_dim_quadratic(self, state: Dict[str, Any]) -> float:
        """High-dimensional quadratic for scalability testing"""
        score = 0.0
        for key, value in state.items():
            if key.startswith('x') and isinstance(value, (int, float)):
                # Different weights for different dimensions
                weight = hash(key) % 10 / 10.0 + 0.5
                score -= weight * value**2
        return score
    
    def run_single_test(self, dataset: Dict[str, Any], test_id: str) -> Dict[str, Any]:
        """Run a single optimization test"""
        self.logger.info(f"Starting test {test_id} on {dataset['name']}")
        
        # Generate initial state
        initial_state = {}
        for i in range(dataset['dimensions']):
            if i < 3 and dataset['type'] in ['golden_seeking', 'cos_exp']:
                # Special parameters for F-V-E problems
                param_names = ['frequency', 'vibration', 'energy']
                initial_state[param_names[i]] = np.random.uniform(0.5, 2.0)
            initial_state[f'x{i}'] = np.random.uniform(*dataset['initial_range'])
        
        # Add special parameters for COS-EXP problems
        if dataset['type'] == 'cos_exp':
            initial_state['coherence'] = np.random.uniform(0.1, 0.5)
        
        # Create problem signature
        problem_signature = {
            'type': dataset['type'],
            'dimensions': dataset['dimensions'],
            'objective_type': dataset['name']
        }
        
        # Run optimization
        try:
            optimizer = EnhancedMetaOptimizer()
            
            start_time = time.time()
            result = optimizer.meta_optimize_enhanced(
                initial_state=initial_state,
                objective_function=dataset['objective'],
                problem_signature=problem_signature,
                max_iterations=min(200, dataset['dimensions'] * 10)
            )
            elapsed = time.time() - start_time
            
            # Extract results
            test_result = {
                'test_id': test_id,
                'dataset': dataset['name'],
                'success': True,
                'iterations': result['iterations'],
                'time': elapsed,
                'initial_score': dataset['objective'](initial_state),
                'final_score': result['final_score'],
                'improvement': result['final_score'] - dataset['objective'](initial_state),
                'acceleration_percentage': result['acceleration_percentage'],
                'patterns_used': result['patterns_used'],
                'fve_ratio': result['symbol']['fve_ratio'],
                'golden_ratio_error': abs(result['symbol']['fve_ratio'] - 1.618),
                'timestamp': datetime.now().isoformat()
            }
            
            # Check for golden ratio emergence
            if test_result['golden_ratio_error'] < 0.1:
                self.stats['golden_ratio_discoveries'] += 1
                self.logger.info(f"🌟 Golden ratio discovered in test {test_id}!")
            
            self.logger.info(f"Test {test_id} completed: {result['iterations']} iterations, "
                           f"{result['acceleration_percentage']:.1f}% acceleration")
            
        except Exception as e:
            self.logger.error(f"Test {test_id} failed: {str(e)}")
            test_result = {
                'test_id': test_id,
                'dataset': dataset['name'],
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        return test_result
    
    def test_worker(self, worker_id: int):
        """Worker thread for continuous testing"""
        self.logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get test from queue (timeout to check running flag)
                dataset = self.test_queue.get(timeout=1.0)
                
                # Generate unique test ID
                test_id = f"{dataset['name']}_{int(time.time()*1000)}_{worker_id}"
                
                # Run test
                result = self.run_single_test(dataset, test_id)
                
                # Update statistics
                self.stats['total_tests'] += 1
                if result['success']:
                    self.stats['successful_tests'] += 1
                    self.stats['total_iterations'] += result['iterations']
                    self.stats['total_time'] += result['time']
                    
                    if result['acceleration_percentage'] > self.stats['best_performance_gain']:
                        self.stats['best_performance_gain'] = result['acceleration_percentage']
                else:
                    self.stats['failed_tests'] += 1
                
                # Queue result for storage
                self.results_queue.put(result)
                
                # Mark task done
                self.test_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}")
    
    def results_writer(self):
        """Thread for writing results to disk"""
        results_buffer = []
        last_write = time.time()
        
        while self.running or not self.results_queue.empty():
            try:
                # Get result from queue
                result = self.results_queue.get(timeout=1.0)
                results_buffer.append(result)
                
                # Write to disk every 10 results or 60 seconds
                if len(results_buffer) >= 10 or (time.time() - last_write) > 60:
                    self._write_results(results_buffer)
                    results_buffer = []
                    last_write = time.time()
                
            except queue.Empty:
                # Write any remaining results
                if results_buffer and (time.time() - last_write) > 60:
                    self._write_results(results_buffer)
                    results_buffer = []
                    last_write = time.time()
                continue
        
        # Final write
        if results_buffer:
            self._write_results(results_buffer)
    
    def _write_results(self, results: List[Dict[str, Any]]):
        """Write results to JSON file"""
        if not results:
            return
            
        filename = self.results_dir / f"results_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Load existing results
        existing = []
        if filename.exists():
            with open(filename, 'r') as f:
                existing = json.load(f)
        
        # Append new results
        existing.extend(results)
        
        # Write back
        with open(filename, 'w') as f:
            json.dump(existing, f, indent=2)
        
        self.logger.info(f"Wrote {len(results)} results to {filename}")
    
    def test_scheduler(self):
        """Schedule tests for continuous execution"""
        self.logger.info("Test scheduler started")
        
        test_counts = {dataset['name']: 0 for dataset in self.test_datasets}
        
        while self.running:
            try:
                # Add tests to queue, rotating through datasets
                for dataset in self.test_datasets:
                    if self.test_queue.qsize() < 50:  # Keep queue reasonably sized
                        self.test_queue.put(dataset)
                        test_counts[dataset['name']] += 1
                
                # Log progress every hour
                if sum(test_counts.values()) % 100 == 0:
                    self.logger.info(f"Scheduled tests: {test_counts}")
                
                # Sleep briefly to avoid overwhelming the queue
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
    
    def generate_report(self):
        """Generate performance report"""
        if not self.stats['start_time']:
            return
            
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        report = f"""
META-OPT-QUANT Continuous Testing Report
========================================
Runtime: {runtime/3600:.1f} hours
Total Tests: {self.stats['total_tests']}
Successful: {self.stats['successful_tests']}
Failed: {self.stats['failed_tests']}
Success Rate: {self.stats['successful_tests']/max(1, self.stats['total_tests'])*100:.1f}%

Performance Metrics:
- Average Iterations: {self.stats['total_iterations']/max(1, self.stats['successful_tests']):.1f}
- Average Time/Test: {self.stats['total_time']/max(1, self.stats['successful_tests']):.2f}s
- Best Acceleration: {self.stats['best_performance_gain']:.1f}%
- Golden Ratios Found: {self.stats['golden_ratio_discoveries']}
- Tests per Hour: {self.stats['total_tests']/(runtime/3600):.1f}

Global Cache Statistics:
{self._get_cache_stats()}
"""
        
        report_file = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Report saved to {report_file}")
        return report
    
    def _get_cache_stats(self):
        """Get global cache statistics"""
        try:
            cache = get_global_cache()
            insights = cache.get_evolution_insights()
            stats = cache.cache.get_cache_stats()
            
            return f"""- Total Patterns: {stats['pattern_count']}
- Avg Performance: {stats['avg_performance']:.4f}
- Max Performance: {stats['max_performance']:.4f}
- Golden Discoveries: {insights['golden_ratio_discoveries']}
- Max Generation: {insights['max_generation_depth']}"""
        except:
            return "- Cache stats unavailable"
    
    def start(self, num_workers: int = 4):
        """Start continuous testing"""
        self.logger.info(f"Starting continuous testing with {num_workers} workers")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Start worker threads
        for i in range(num_workers):
            t = threading.Thread(target=self.test_worker, args=(i,))
            t.start()
            self.threads.append(t)
        
        # Start results writer
        t = threading.Thread(target=self.results_writer)
        t.start()
        self.threads.append(t)
        
        # Start test scheduler
        t = threading.Thread(target=self.test_scheduler)
        t.start()
        self.threads.append(t)
        
        self.logger.info("All threads started")
    
    def stop(self):
        """Stop continuous testing"""
        self.logger.info("Stopping continuous testing...")
        self.running = False
        
        # Wait for threads to finish
        for t in self.threads:
            t.join(timeout=5.0)
        
        # Generate final report
        self.generate_report()
        
        self.logger.info("Continuous testing stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global framework
    print("\nShutdown signal received...")
    framework.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start framework
    framework = ContinuousTestingFramework()
    
    # Number of worker threads (adjust based on CPU cores)
    num_workers = min(4, os.cpu_count() or 4)
    
    print(f"Starting META-OPT-QUANT continuous testing with {num_workers} workers")
    print("Press Ctrl+C to stop")
    
    framework.start(num_workers)
    
    # Run until interrupted
    try:
        while True:
            time.sleep(3600)  # Generate report every hour
            report = framework.generate_report()
            print("\n" + report)
    except KeyboardInterrupt:
        pass