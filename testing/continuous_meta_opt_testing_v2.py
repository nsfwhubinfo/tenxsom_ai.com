#!/usr/bin/env python3
"""
Continuous Testing Framework V2 for META-OPT-QUANT
With improved bounds and golden ratio tracking
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

from enhanced_meta_optimizer_v2 import EnhancedMetaOptimizerV2
from global_cache_manager import get_global_cache

class ContinuousTestingFrameworkV2:
    """Improved 24/7 testing framework with better objectives"""
    
    def __init__(self, results_dir: str = "./continuous_test_results_v2"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Test queue
        self.test_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Control flags
        self.running = False
        self.threads = []
        
        # Statistics
        self.stats = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_iterations': 0,
            'total_time': 0.0,
            'golden_ratio_discoveries': 0,
            'best_performance_gain': 0.0,
            'best_golden_error': float('inf'),
            'start_time': None,
            'positive_accelerations': 0
        }
        
        # Load improved test datasets
        self.test_datasets = self._load_improved_datasets()
        
    def setup_logging(self):
        """Configure logging"""
        log_file = self.results_dir / f"continuous_test_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('MetaOptTestV2')
        
    def _load_improved_datasets(self) -> List[Dict[str, Any]]:
        """Load improved test datasets with bounded objectives"""
        datasets = []
        
        # 1. Bounded Rosenbrock
        datasets.append({
            'name': 'rosenbrock_bounded',
            'type': 'continuous',
            'dimensions': 5,
            'objective': self._bounded_rosenbrock,
            'optimal_value': 0.0,
            'initial_range': (-2, 2)  # Smaller range
        })
        
        # 2. Bounded Rastrigin
        datasets.append({
            'name': 'rastrigin_bounded',
            'type': 'multimodal',
            'dimensions': 5,  # Reduced dimension
            'objective': self._bounded_rastrigin,
            'optimal_value': 0.0,
            'initial_range': (-3, 3)  # Smaller range
        })
        
        # 3. Golden Ratio Seeker V2
        datasets.append({
            'name': 'golden_seeker_v2',
            'type': 'golden_seeking',
            'dimensions': 6,
            'objective': self._golden_ratio_objective_v2,
            'optimal_value': 100.0,
            'initial_range': (0.5, 2.5)  # Near golden ratio
        })
        
        # 4. COS-EXP Bounded
        datasets.append({
            'name': 'cos_exp_bounded',
            'type': 'cos_exp',
            'dimensions': 7,
            'objective': self._cos_exp_bounded,
            'optimal_value': None,
            'initial_range': (0.5, 2.0)
        })
        
        # 5. Fibonacci Sequence
        datasets.append({
            'name': 'fibonacci_optimizer',
            'type': 'sequence',
            'dimensions': 8,
            'objective': self._fibonacci_objective,
            'optimal_value': 100.0,
            'initial_range': (0.5, 3.0)
        })
        
        # 6. Harmonic Oscillator
        datasets.append({
            'name': 'harmonic_golden',
            'type': 'harmonic',
            'dimensions': 6,
            'objective': self._harmonic_golden_objective,
            'optimal_value': 50.0,
            'initial_range': (0.1, 2.0)
        })
        
        return datasets
    
    # Improved Objective Functions
    
    def _bounded_rosenbrock(self, state: Dict[str, Any]) -> float:
        """Bounded Rosenbrock to prevent overflow"""
        score = 0.0
        dims = [v for k, v in sorted(state.items()) if k.startswith('x') and isinstance(v, (int, float))]
        
        for i in range(len(dims) - 1):
            # Bound individual terms
            term1 = min((1 - dims[i])**2, 1000)
            term2 = min(100 * (dims[i+1] - dims[i]**2)**2, 10000)
            score -= (term1 + term2)
        
        return max(score, -1e6)  # Lower bound
    
    def _bounded_rastrigin(self, state: Dict[str, Any]) -> float:
        """Bounded Rastrigin"""
        A = 10
        score = 0.0
        dims = [v for k, v in sorted(state.items()) if k.startswith('x') and isinstance(v, (int, float))]
        
        for x in dims:
            # Bound x to reasonable range
            x_bounded = np.clip(x, -10, 10)
            score -= (x_bounded**2 - A * np.cos(2 * np.pi * x_bounded))
        
        return max(-(A * len(dims) + score), -1e6)
    
    def _golden_ratio_objective_v2(self, state: Dict[str, Any]) -> float:
        """Improved golden ratio objective with multiple paths"""
        phi = 1.618033988749895
        score = 0.0
        
        # Path 1: F-V-E golden ratio
        F = np.clip(abs(state.get('frequency', 1.0)), 0.1, 10)
        V = np.clip(abs(state.get('vibration', 1.0)), 0.1, 10)
        E = np.clip(abs(state.get('energy', 1.0)), 0.1, 10)
        
        fve_ratio = F * V / E
        score += 25 * np.exp(-((fve_ratio - phi)**2 / 0.1))  # Sharper peak
        
        # Path 2: Sequential ratios
        params = sorted([v for k, v in state.items() if k.startswith('x') and isinstance(v, (int, float))])
        for i in range(len(params) - 1):
            if params[i] > 0.1:
                ratio = params[i+1] / params[i]
                if 0.5 < ratio < 3.0:  # Reasonable range
                    score += 15 * np.exp(-((ratio - phi)**2 / 0.1))
        
        # Path 3: Fibonacci-like sequence
        if len(params) >= 3:
            for i in range(len(params) - 2):
                if params[i] > 0 and params[i+1] > 0:
                    fib_ratio = (params[i] + params[i+1]) / params[i+2] if params[i+2] > 0 else 0
                    score += 10 * np.exp(-((fib_ratio - 1.0)**2 / 0.1))
        
        # Penalty for extreme values
        penalty = sum(max(0, abs(p) - 10)**2 for p in params)
        score -= penalty * 0.1
        
        return min(score, 100)  # Cap maximum
    
    def _cos_exp_bounded(self, state: Dict[str, Any]) -> float:
        """Bounded COS-EXP objective"""
        score = 0.0
        
        # Particle constants
        alpha, beta, gamma, phi = 0.223, 1.344, 1.075, 1.618
        
        # Extract bounded values
        coherence = np.clip(state.get('coherence', 0.5), 0, 1)
        F = np.clip(abs(state.get('frequency', 1.0)), 0.1, 5)
        V = np.clip(abs(state.get('vibration', 1.0)), 0.1, 5)
        E = np.clip(abs(state.get('energy', 1.0)), 0.1, 5)
        
        # Coherence alignment
        score += 10 * np.exp(-((coherence - alpha)**2 / 0.05))
        
        # Resonance condition
        resonance = V / (F * beta)
        score += 10 * np.exp(-((resonance - 1.0)**2 / 0.05))
        
        # Golden ratio
        fve_ratio = F * V / E
        score += 20 * np.exp(-((fve_ratio - phi)**2 / 0.05))
        
        # Quantum superposition (bounded)
        superposition = np.sin(F * np.pi) * np.cos(V * np.pi) * E
        score += 5 * np.clip(superposition, -5, 5)
        
        return min(score, 50)  # Cap score
    
    def _fibonacci_objective(self, state: Dict[str, Any]) -> float:
        """Optimize for Fibonacci sequence relationships"""
        score = 0.0
        phi = 1.618033988749895
        
        # Get sorted parameters
        params = sorted([(k, v) for k, v in state.items() 
                        if k.startswith('x') and isinstance(v, (int, float))],
                       key=lambda x: x[0])
        
        if len(params) >= 3:
            # Reward Fibonacci relationships
            for i in range(len(params) - 2):
                a, b, c = params[i][1], params[i+1][1], params[i+2][1]
                if a > 0 and b > 0 and c > 0:
                    # Check if c ≈ a + b
                    fib_error = abs(c - (a + b)) / c
                    score += 10 * np.exp(-fib_error)
                    
                    # Check golden ratio
                    if a > 0:
                        ratio = b / a
                        score += 5 * np.exp(-((ratio - phi)**2 / 0.1))
        
        # F-V-E bonus
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        if E > 0:
            fve_ratio = F * V / E
            score += 15 * np.exp(-((fve_ratio - phi)**2 / 0.1))
        
        return min(score, 100)
    
    def _harmonic_golden_objective(self, state: Dict[str, Any]) -> float:
        """Harmonic oscillator with golden ratio frequency"""
        phi = 1.618033988749895
        score = 0.0
        
        # Natural frequency should approach golden ratio
        freq = abs(state.get('frequency', 1.0))
        score += 20 * np.exp(-((freq - phi)**2 / 0.05))
        
        # Amplitude ratios
        params = [v for k, v in sorted(state.items()) 
                 if k.startswith('x') and isinstance(v, (int, float))]
        
        if len(params) >= 2:
            # Harmonic amplitudes decay by golden ratio
            for i in range(len(params) - 1):
                if params[i] > 0:
                    ratio = params[i+1] / params[i]
                    target = 1 / phi  # Decay ratio
                    score += 10 * np.exp(-((ratio - target)**2 / 0.05))
        
        # Energy conservation
        total_energy = sum(p**2 for p in params)
        score -= max(0, total_energy - 10) * 0.5  # Penalty for too much energy
        
        return min(score, 50)
    
    def run_single_test(self, dataset: Dict[str, Any], test_id: str) -> Dict[str, Any]:
        """Run a single optimization test"""
        self.logger.info(f"Starting test {test_id} on {dataset['name']}")
        
        # Generate initial state
        initial_state = {}
        for i in range(dataset['dimensions']):
            if i < 3 and dataset['type'] in ['golden_seeking', 'cos_exp', 'harmonic']:
                # Special parameters
                param_names = ['frequency', 'vibration', 'energy']
                if i < len(param_names):
                    initial_state[param_names[i]] = np.random.uniform(*dataset['initial_range'])
            
            # Regular parameters
            initial_state[f'x{i}'] = np.random.uniform(*dataset['initial_range'])
        
        # Add special parameters
        if dataset['type'] == 'cos_exp':
            initial_state['coherence'] = np.random.uniform(0.1, 0.5)
        
        # Problem signature
        problem_signature = {
            'type': dataset['type'],
            'dimensions': dataset['dimensions'],
            'objective_type': dataset['name']
        }
        
        # Run optimization
        try:
            optimizer = EnhancedMetaOptimizerV2()
            
            start_time = time.time()
            result = optimizer.meta_optimize_enhanced(
                initial_state=initial_state,
                objective_function=dataset['objective'],
                problem_signature=problem_signature,
                max_iterations=min(100, dataset['dimensions'] * 10)
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
                'golden_ratio_error': result['best_golden_ratio_error'],
                'golden_discoveries': result['golden_discoveries'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Update statistics
            if test_result['golden_ratio_error'] < 0.1:
                self.stats['golden_ratio_discoveries'] += 1
                self.logger.info(f"🌟 Golden ratio discovered in test {test_id}! Error: {test_result['golden_ratio_error']:.6f}")
            
            if test_result['golden_ratio_error'] < self.stats['best_golden_error']:
                self.stats['best_golden_error'] = test_result['golden_ratio_error']
            
            if result['acceleration_percentage'] > 0:
                self.stats['positive_accelerations'] += 1
            
            self.logger.info(f"Test {test_id} completed: {result['iterations']} iterations, "
                           f"{result['acceleration_percentage']:.1f}% acceleration, "
                           f"φ-error: {result['best_golden_ratio_error']:.4f}")
            
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
                # Get test from queue
                dataset = self.test_queue.get(timeout=1.0)
                
                # Generate test ID
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
                
                # Queue result
                self.results_queue.put(result)
                
                # Mark done
                self.test_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}")
    
    def results_writer(self):
        """Thread for writing results"""
        results_buffer = []
        last_write = time.time()
        
        while self.running or not self.results_queue.empty():
            try:
                result = self.results_queue.get(timeout=1.0)
                results_buffer.append(result)
                
                # Write every 10 results or 60 seconds
                if len(results_buffer) >= 10 or (time.time() - last_write) > 60:
                    self._write_results(results_buffer)
                    results_buffer = []
                    last_write = time.time()
                
            except queue.Empty:
                if results_buffer and (time.time() - last_write) > 60:
                    self._write_results(results_buffer)
                    results_buffer = []
                    last_write = time.time()
                continue
        
        # Final write
        if results_buffer:
            self._write_results(results_buffer)
    
    def _write_results(self, results: List[Dict[str, Any]]):
        """Write results to file"""
        if not results:
            return
            
        filename = self.results_dir / f"results_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Load existing
        existing = []
        if filename.exists():
            with open(filename, 'r') as f:
                existing = json.load(f)
        
        # Append
        existing.extend(results)
        
        # Write
        with open(filename, 'w') as f:
            json.dump(existing, f, indent=2)
        
        self.logger.info(f"Wrote {len(results)} results")
    
    def test_scheduler(self):
        """Schedule tests"""
        self.logger.info("Test scheduler started")
        
        test_counts = {dataset['name']: 0 for dataset in self.test_datasets}
        
        while self.running:
            try:
                # Prioritize golden ratio tests
                for dataset in self.test_datasets:
                    if self.test_queue.qsize() < 20:
                        # More golden ratio tests
                        if 'golden' in dataset['name'] or 'fibonacci' in dataset['name']:
                            self.test_queue.put(dataset)
                            self.test_queue.put(dataset)  # Double frequency
                        else:
                            self.test_queue.put(dataset)
                        test_counts[dataset['name']] += 1
                
                # Log progress
                if sum(test_counts.values()) % 50 == 0:
                    self.logger.info(f"Scheduled: {test_counts}")
                
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
    
    def generate_report(self):
        """Generate detailed report"""
        if not self.stats['start_time']:
            return
            
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        report = f"""
META-OPT-QUANT V2 Continuous Testing Report
==========================================
Runtime: {runtime/3600:.1f} hours
Total Tests: {self.stats['total_tests']}
Successful: {self.stats['successful_tests']}
Failed: {self.stats['failed_tests']}
Success Rate: {self.stats['successful_tests']/max(1, self.stats['total_tests'])*100:.1f}%

Performance Metrics:
- Average Iterations: {self.stats['total_iterations']/max(1, self.stats['successful_tests']):.1f}
- Average Time/Test: {self.stats['total_time']/max(1, self.stats['successful_tests']):.2f}s
- Best Acceleration: {self.stats['best_performance_gain']:.1f}%
- Positive Accelerations: {self.stats['positive_accelerations']} ({self.stats['positive_accelerations']/max(1, self.stats['successful_tests'])*100:.1f}%)
- Tests per Hour: {self.stats['total_tests']/(runtime/3600):.1f}

Golden Ratio Discovery:
- Total Discoveries: {self.stats['golden_ratio_discoveries']}
- Discovery Rate: {self.stats['golden_ratio_discoveries']/max(1, self.stats['successful_tests'])*100:.1f}%
- Best φ Error: {self.stats['best_golden_error']:.6f}

Global Cache Statistics:
{self._get_cache_stats()}
"""
        
        report_file = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Report saved to {report_file}")
        return report
    
    def _get_cache_stats(self):
        """Get cache statistics"""
        try:
            cache = get_global_cache()
            insights = cache.get_evolution_insights()
            stats = cache.cache.get_cache_stats()
            
            return f"""- Total Patterns: {stats['pattern_count']}
- Avg Performance: {min(stats['avg_performance'], 1e6):.4f}
- Max Performance: {min(stats['max_performance'], 1e6):.4f}
- Golden Discoveries (Global): {insights['golden_ratio_discoveries']}
- Max Generation: {insights['max_generation_depth']}"""
        except:
            return "- Cache stats unavailable"
    
    def start(self, num_workers: int = 4):
        """Start testing"""
        self.logger.info(f"Starting V2 testing with {num_workers} workers")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Start workers
        for i in range(num_workers):
            t = threading.Thread(target=self.test_worker, args=(i,))
            t.start()
            self.threads.append(t)
        
        # Start results writer
        t = threading.Thread(target=self.results_writer)
        t.start()
        self.threads.append(t)
        
        # Start scheduler
        t = threading.Thread(target=self.test_scheduler)
        t.start()
        self.threads.append(t)
        
        self.logger.info("All threads started")
    
    def stop(self):
        """Stop testing"""
        self.logger.info("Stopping testing...")
        self.running = False
        
        # Wait for threads
        for t in self.threads:
            t.join(timeout=5.0)
        
        # Final report
        self.generate_report()
        
        self.logger.info("Testing stopped")


def signal_handler(signum, frame):
    """Handle shutdown"""
    global framework
    print("\nShutdown signal received...")
    framework.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create framework
    framework = ContinuousTestingFrameworkV2()
    
    # Worker count
    num_workers = min(4, os.cpu_count() or 4)
    
    print(f"Starting META-OPT-QUANT V2 continuous testing with {num_workers} workers")
    print("Press Ctrl+C to stop")
    
    framework.start(num_workers)
    
    # Run with periodic reports
    try:
        while True:
            time.sleep(300)  # Report every 5 minutes
            report = framework.generate_report()
            print("\n" + report)
    except KeyboardInterrupt:
        pass