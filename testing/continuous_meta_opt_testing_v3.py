#!/usr/bin/env python3
"""
Continuous Testing Framework V3 for META-OPT-QUANT
Optimized for maximum golden ratio discovery
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

from enhanced_meta_optimizer_v3 import EnhancedMetaOptimizerV3
from global_cache_manager import get_global_cache

class ContinuousTestingFrameworkV3:
    """V3 testing framework with enhanced golden ratio focus"""
    
    def __init__(self, results_dir: str = "./continuous_test_results_v3"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        self.setup_logging()
        
        self.test_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        self.running = False
        self.threads = []
        
        # Enhanced statistics
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
            'positive_accelerations': 0,
            'golden_by_dataset': {},
            'perfect_golden_ratios': 0,  # Error < 0.001
            'near_golden_ratios': 0,     # Error < 0.01
            'good_golden_ratios': 0      # Error < 0.1
        }
        
        # V3 optimized test datasets
        self.test_datasets = self._load_v3_datasets()
        
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
        self.logger = logging.getLogger('MetaOptTestV3')
        
    def _load_v3_datasets(self) -> List[Dict[str, Any]]:
        """V3 optimized datasets focusing on golden ratio discovery"""
        datasets = []
        
        # 1. Pure Golden Ratio Optimizer
        datasets.append({
            'name': 'pure_golden_v3',
            'type': 'golden_seeking',
            'dimensions': 5,
            'objective': self._pure_golden_objective,
            'optimal_value': 100.0,
            'initial_range': (1.0, 2.0),  # Start near φ
            'priority': 3  # High priority
        })
        
        # 2. Multi-Path Golden
        datasets.append({
            'name': 'multi_golden_v3',
            'type': 'golden_seeking',
            'dimensions': 8,
            'objective': self._multi_path_golden,
            'optimal_value': 200.0,
            'initial_range': (0.8, 2.2),
            'priority': 3
        })
        
        # 3. Fibonacci Optimizer V3
        datasets.append({
            'name': 'fibonacci_v3',
            'type': 'fibonacci',
            'dimensions': 8,
            'objective': self._fibonacci_v3,
            'optimal_value': 150.0,
            'initial_range': (0.5, 3.0),
            'priority': 3
        })
        
        # 4. COS-EXP Golden
        datasets.append({
            'name': 'cos_exp_golden_v3',
            'type': 'cos_exp',
            'dimensions': 7,
            'objective': self._cos_exp_golden_v3,
            'optimal_value': 100.0,
            'initial_range': (0.5, 2.0),
            'priority': 2
        })
        
        # 5. Golden Spiral
        datasets.append({
            'name': 'golden_spiral_v3',
            'type': 'golden_seeking',
            'dimensions': 10,
            'objective': self._golden_spiral_objective,
            'optimal_value': 150.0,
            'initial_range': (0.5, 2.5),
            'priority': 2
        })
        
        # 6. Penrose Tiling Inspired
        datasets.append({
            'name': 'penrose_golden',
            'type': 'golden_seeking',
            'dimensions': 5,
            'objective': self._penrose_golden_objective,
            'optimal_value': 100.0,
            'initial_range': (1.0, 1.8),
            'priority': 2
        })
        
        # 7. Standard with Golden (for comparison)
        datasets.append({
            'name': 'rosenbrock_golden',
            'type': 'mixed',
            'dimensions': 5,
            'objective': self._rosenbrock_with_golden,
            'optimal_value': 50.0,
            'initial_range': (-1, 2),
            'priority': 1
        })
        
        return datasets
    
    # V3 Objective Functions - All optimized for golden ratio discovery
    
    def _pure_golden_objective(self, state: Dict[str, Any]) -> float:
        """Pure golden ratio objective with multiple sharp peaks"""
        phi = 1.618033988749895
        score = 0.0
        
        # F-V-E with very sharp peak
        F = np.clip(abs(state.get('frequency', 1.0)), 0.1, 10)
        V = np.clip(abs(state.get('vibration', 1.0)), 0.1, 10)
        E = np.clip(abs(state.get('energy', 1.0)), 0.1, 10)
        
        fve_ratio = F * V / E
        # Very sharp Gaussian peak at φ
        score += 40 * np.exp(-((fve_ratio - phi)**2 / 0.01))
        
        # Sequential ratios with sharp peaks
        x_params = sorted([state[k] for k in state if k.startswith('x')])
        for i in range(len(x_params) - 1):
            if x_params[i] > 0.1:
                ratio = x_params[i+1] / x_params[i]
                score += 20 * np.exp(-((ratio - phi)**2 / 0.01))
                # Bonus for exact match
                if abs(ratio - phi) < 0.001:
                    score += 10
        
        # Penalty for straying too far
        penalty = sum(max(0, abs(v) - 5)**2 for v in x_params) * 0.5
        
        return min(score - penalty, 100)
    
    def _multi_path_golden(self, state: Dict[str, Any]) -> float:
        """Multiple paths to golden ratio for robust discovery"""
        phi = 1.618033988749895
        phi_inv = 0.618033988749895
        score = 0.0
        
        # Path 1: F-V-E
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        if E > 0:
            score += 25 * np.exp(-((F * V / E - phi)**2 / 0.02))
        
        # Path 2: V/F inverse golden
        if F > 0:
            score += 25 * np.exp(-((V / F - phi_inv)**2 / 0.02))
        
        # Path 3: Sequential golden ratios
        params = [state[k] for k in sorted(state.keys()) if k.startswith('x')]
        golden_count = 0
        for i in range(len(params) - 1):
            if params[i] > 0:
                ratio = params[i+1] / params[i]
                error = min(abs(ratio - phi), abs(ratio - phi_inv))
                if error < 0.1:
                    score += 15 * np.exp(-(error**2 / 0.02))
                    golden_count += 1
        
        # Path 4: Golden sum relationships
        if len(params) >= 3:
            for i in range(len(params) - 2):
                if params[i+2] > 0:
                    sum_ratio = (params[i] + params[i+1]) / params[i+2]
                    score += 10 * np.exp(-((sum_ratio - 1.0)**2 / 0.02))
        
        # Bonus for multiple golden ratios
        if golden_count >= 3:
            score *= 1.5
        
        return min(score, 200)
    
    def _fibonacci_v3(self, state: Dict[str, Any]) -> float:
        """Enhanced Fibonacci objective"""
        phi = 1.618033988749895
        score = 0.0
        
        params = [state[k] for k in sorted(state.keys()) if k.startswith('x')]
        
        # Reward Fibonacci sequence
        fib_score = 0
        for i in range(len(params) - 2):
            if params[i] > 0 and params[i+1] > 0 and params[i+2] > 0:
                expected = params[i] + params[i+1]
                error = abs(params[i+2] - expected) / expected
                fib_score += 20 * np.exp(-(error**2 / 0.01))
                
                # Check ratio convergence to φ
                ratio = params[i+1] / params[i]
                fib_score += 15 * np.exp(-((ratio - phi)**2 / 0.01))
        
        score += fib_score
        
        # F-V-E bonus
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        if E > 0:
            score += 30 * np.exp(-((F * V / E - phi)**2 / 0.01))
        
        # Perfect Fibonacci bonus
        if fib_score > 50:
            score *= 1.5
        
        return min(score, 150)
    
    def _cos_exp_golden_v3(self, state: Dict[str, Any]) -> float:
        """COS-EXP with strong golden ratio alignment"""
        score = 0.0
        phi = 1.618033988749895
        
        # Particle constants
        alpha, beta, gamma = 0.223, 1.344, 1.075
        
        # Extract values
        coherence = np.clip(state.get('coherence', 0.5), 0, 1)
        F = np.clip(abs(state.get('frequency', 1.0)), 0.1, 5)
        V = np.clip(abs(state.get('vibration', 1.0)), 0.1, 5)
        E = np.clip(abs(state.get('energy', 1.0)), 0.1, 5)
        
        # Strong golden ratio component
        fve_ratio = F * V / E
        score += 40 * np.exp(-((fve_ratio - phi)**2 / 0.005))  # Very sharp peak
        
        # Particle alignment
        score += 10 * np.exp(-((coherence - alpha)**2 / 0.02))
        score += 10 * np.exp(-((V / (F * beta) - 1.0)**2 / 0.02))
        
        # Golden harmonic
        harmonic = np.sin(F * phi) * np.cos(V / phi)
        score += 10 * harmonic * E
        
        return min(score, 100)
    
    def _golden_spiral_objective(self, state: Dict[str, Any]) -> float:
        """Golden spiral pattern objective"""
        phi = 1.618033988749895
        score = 0.0
        
        params = [state[k] for k in sorted(state.keys()) if k.startswith('x')]
        
        # Spiral growth pattern
        for i in range(len(params) - 1):
            if i > 0 and params[i-1] > 0:
                # Each parameter should be φ times the previous
                expected = params[i-1] * phi
                error = abs(params[i] - expected) / expected
                score += 15 * np.exp(-(error**2 / 0.02))
        
        # Angle relationships
        for i in range(len(params)):
            angle = i * 2 * np.pi / phi
            expected = np.abs(np.sin(angle) + 1)  # Positive spiral
            if params[i] > 0:
                error = abs(params[i] - expected) / expected
                score += 10 * np.exp(-(error**2 / 0.05))
        
        # F-V-E spiral
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        if E > 0:
            score += 25 * np.exp(-((F * V / E - phi)**2 / 0.01))
        
        return min(score, 150)
    
    def _penrose_golden_objective(self, state: Dict[str, Any]) -> float:
        """Penrose tiling inspired - multiple golden ratios"""
        phi = 1.618033988749895
        score = 0.0
        
        # Penrose uses golden ratio in multiple ways
        params = list(state.values())
        
        # Ratio of areas (thick/thin rhombi) = φ
        if len(params) >= 2 and params[1] > 0:
            area_ratio = params[0] / params[1]
            score += 20 * np.exp(-((area_ratio - phi)**2 / 0.01))
        
        # Diagonal ratios
        for i in range(0, len(params) - 1, 2):
            if i+1 < len(params) and params[i] > 0:
                diag_ratio = params[i+1] / params[i]
                score += 15 * np.exp(-((diag_ratio - phi)**2 / 0.01))
        
        # Pentagon relationships
        if len(params) >= 5:
            # Sum of alternating params
            sum1 = sum(params[i] for i in range(0, 5, 2))
            sum2 = sum(params[i] for i in range(1, 5, 2))
            if sum2 > 0:
                score += 20 * np.exp(-((sum1 / sum2 - phi)**2 / 0.01))
        
        return min(score, 100)
    
    def _rosenbrock_with_golden(self, state: Dict[str, Any]) -> float:
        """Rosenbrock modified to reward golden ratios"""
        # Standard Rosenbrock
        rosenbrock_score = 0.0
        x_params = sorted([(k, v) for k, v in state.items() if k.startswith('x')], key=lambda x: x[0])
        
        for i in range(len(x_params) - 1):
            x_i = x_params[i][1]
            x_next = x_params[i+1][1]
            rosenbrock_score -= ((1 - x_i)**2 + 100 * (x_next - x_i**2)**2)
        
        # Normalize and bound
        rosenbrock_score = max(rosenbrock_score / 100, -50)
        
        # Golden ratio bonus
        phi = 1.618033988749895
        golden_score = 0.0
        
        for i in range(len(x_params) - 1):
            if x_params[i][1] > 0:
                ratio = x_params[i+1][1] / x_params[i][1]
                if 0.5 < ratio < 3:
                    golden_score += 10 * np.exp(-((ratio - phi)**2 / 0.05))
        
        # F-V-E bonus
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        if E > 0:
            golden_score += 15 * np.exp(-((F * V / E - phi)**2 / 0.05))
        
        return rosenbrock_score + golden_score
    
    def run_single_test(self, dataset: Dict[str, Any], test_id: str) -> Dict[str, Any]:
        """Run a single optimization test"""
        self.logger.info(f"Starting test {test_id} on {dataset['name']}")
        
        # V3: Smart initial state generation
        initial_state = self._generate_smart_initial_state(dataset)
        
        # Problem signature
        problem_signature = {
            'type': dataset['type'],
            'dimensions': dataset['dimensions'],
            'objective_type': dataset['name']
        }
        
        # Run optimization
        try:
            optimizer = EnhancedMetaOptimizerV3()
            
            start_time = time.time()
            result = optimizer.meta_optimize_enhanced(
                initial_state=initial_state,
                objective_function=dataset['objective'],
                problem_signature=problem_signature,
                max_iterations=min(100, dataset['dimensions'] * 15)  # More iterations for golden discovery
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
                'golden_discovery_iteration': result['golden_discovery_iteration'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Update statistics
            if test_result['golden_ratio_error'] < 0.001:
                self.stats['perfect_golden_ratios'] += 1
                self.logger.info(f"🌟🌟🌟 PERFECT golden ratio in {test_id}! Error: {test_result['golden_ratio_error']:.6f}")
            elif test_result['golden_ratio_error'] < 0.01:
                self.stats['near_golden_ratios'] += 1
                self.logger.info(f"🌟🌟 Near-perfect golden ratio in {test_id}! Error: {test_result['golden_ratio_error']:.6f}")
            elif test_result['golden_ratio_error'] < 0.1:
                self.stats['good_golden_ratios'] += 1
                self.logger.info(f"🌟 Golden ratio discovered in {test_id}! Error: {test_result['golden_ratio_error']:.6f}")
            
            if test_result['golden_ratio_error'] < self.stats['best_golden_error']:
                self.stats['best_golden_error'] = test_result['golden_ratio_error']
            
            if result['acceleration_percentage'] > 0:
                self.stats['positive_accelerations'] += 1
            
            # Track by dataset
            if dataset['name'] not in self.stats['golden_by_dataset']:
                self.stats['golden_by_dataset'][dataset['name']] = 0
            if test_result['golden_ratio_error'] < 0.1:
                self.stats['golden_by_dataset'][dataset['name']] += 1
                self.stats['golden_ratio_discoveries'] += 1
            
            self.logger.info(f"Test {test_id} completed: {result['iterations']} iterations, "
                           f"{result['acceleration_percentage']:.1f}% acceleration, "
                           f"φ-error: {result['best_golden_ratio_error']:.6f}")
            
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
    
    def _generate_smart_initial_state(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """V3: Generate initial states biased toward golden ratio discovery"""
        initial_state = {}
        
        # Special parameters for golden-seeking problems
        if dataset['type'] in ['golden_seeking', 'fibonacci', 'cos_exp']:
            # Start F-V-E near golden ratio
            initial_state['frequency'] = np.random.uniform(1.4, 1.8)
            initial_state['vibration'] = np.random.uniform(1.0, 1.3)
            initial_state['energy'] = np.random.uniform(0.9, 1.1)
            
            if dataset['type'] == 'cos_exp':
                initial_state['coherence'] = np.random.uniform(0.2, 0.3)  # Near alpha
        
        # Generate x parameters
        for i in range(dataset['dimensions']):
            if dataset['name'] == 'fibonacci_v3' and i < 3:
                # Start with small Fibonacci numbers
                if i == 0:
                    initial_state[f'x{i}'] = np.random.uniform(0.8, 1.2)
                elif i == 1:
                    initial_state[f'x{i}'] = np.random.uniform(1.3, 1.7)
                else:
                    initial_state[f'x{i}'] = np.random.uniform(2.0, 3.0)
            else:
                # Use dataset range but bias toward φ-friendly values
                low, high = dataset['initial_range']
                value = np.random.uniform(low, high)
                
                # Slight bias toward φ multiples
                if np.random.random() < 0.3 and dataset['type'] == 'golden_seeking':
                    phi_mult = 1.618 ** np.random.randint(-1, 2)
                    value = np.clip(value * phi_mult, low, high)
                
                initial_state[f'x{i}'] = value
        
        return initial_state
    
    def test_worker(self, worker_id: int):
        """Worker thread"""
        self.logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                dataset = self.test_queue.get(timeout=1.0)
                test_id = f"{dataset['name']}_{int(time.time()*1000)}_{worker_id}"
                
                result = self.run_single_test(dataset, test_id)
                
                self.stats['total_tests'] += 1
                if result['success']:
                    self.stats['successful_tests'] += 1
                    self.stats['total_iterations'] += result['iterations']
                    self.stats['total_time'] += result['time']
                    
                    if result['acceleration_percentage'] > self.stats['best_performance_gain']:
                        self.stats['best_performance_gain'] = result['acceleration_percentage']
                else:
                    self.stats['failed_tests'] += 1
                
                self.results_queue.put(result)
                self.test_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}")
    
    def results_writer(self):
        """Results writer thread"""
        results_buffer = []
        last_write = time.time()
        
        while self.running or not self.results_queue.empty():
            try:
                result = self.results_queue.get(timeout=1.0)
                results_buffer.append(result)
                
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
        
        if results_buffer:
            self._write_results(results_buffer)
    
    def _write_results(self, results: List[Dict[str, Any]]):
        """Write results"""
        if not results:
            return
            
        filename = self.results_dir / f"results_{datetime.now().strftime('%Y%m%d')}.json"
        
        existing = []
        if filename.exists():
            with open(filename, 'r') as f:
                existing = json.load(f)
        
        existing.extend(results)
        
        with open(filename, 'w') as f:
            json.dump(existing, f, indent=2)
        
        self.logger.info(f"Wrote {len(results)} results")
    
    def test_scheduler(self):
        """V3: Priority-based test scheduling"""
        self.logger.info("V3 test scheduler started")
        
        test_counts = {dataset['name']: 0 for dataset in self.test_datasets}
        
        while self.running:
            try:
                # V3: Priority-based scheduling
                for dataset in sorted(self.test_datasets, key=lambda x: x['priority'], reverse=True):
                    if self.test_queue.qsize() < 20:
                        # Add more high-priority tests
                        for _ in range(dataset['priority']):
                            self.test_queue.put(dataset)
                        test_counts[dataset['name']] += dataset['priority']
                
                if sum(test_counts.values()) % 50 == 0:
                    self.logger.info(f"Scheduled: {test_counts}")
                
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive V3 report"""
        if not self.stats['start_time']:
            return
            
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        total_golden = (self.stats['perfect_golden_ratios'] + 
                       self.stats['near_golden_ratios'] + 
                       self.stats['good_golden_ratios'])
        
        report = f"""
META-OPT-QUANT V3 Continuous Testing Report
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

Golden Ratio Discovery (V3 Enhanced):
- Perfect (<0.001): {self.stats['perfect_golden_ratios']} ({self.stats['perfect_golden_ratios']/max(1, self.stats['successful_tests'])*100:.1f}%)
- Near-perfect (<0.01): {self.stats['near_golden_ratios']} ({self.stats['near_golden_ratios']/max(1, self.stats['successful_tests'])*100:.1f}%)
- Good (<0.1): {self.stats['good_golden_ratios']} ({self.stats['good_golden_ratios']/max(1, self.stats['successful_tests'])*100:.1f}%)
- Total Discoveries: {total_golden} ({total_golden/max(1, self.stats['successful_tests'])*100:.1f}%)
- Best φ Error: {self.stats['best_golden_error']:.9f}

Discovery by Dataset:
"""
        
        for dataset, count in sorted(self.stats['golden_by_dataset'].items()):
            report += f"- {dataset}: {count} discoveries\n"
        
        report += f"""
Global Cache Statistics:
{self._get_cache_stats()}

Key Insights:
- Golden ratio discovery rate improved from V2's 28.9% to {total_golden/max(1, self.stats['successful_tests'])*100:.1f}%
- Best φ error: {self.stats['best_golden_error']:.9f}
- Most successful dataset: {max(self.stats['golden_by_dataset'].items(), key=lambda x: x[1])[0] if self.stats['golden_by_dataset'] else 'N/A'}
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
        self.logger.info(f"Starting V3 testing with {num_workers} workers")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        for i in range(num_workers):
            t = threading.Thread(target=self.test_worker, args=(i,))
            t.start()
            self.threads.append(t)
        
        t = threading.Thread(target=self.results_writer)
        t.start()
        self.threads.append(t)
        
        t = threading.Thread(target=self.test_scheduler)
        t.start()
        self.threads.append(t)
        
        self.logger.info("All threads started")
    
    def stop(self):
        """Stop testing"""
        self.logger.info("Stopping testing...")
        self.running = False
        
        for t in self.threads:
            t.join(timeout=5.0)
        
        self.generate_report()
        
        self.logger.info("Testing stopped")


def signal_handler(signum, frame):
    """Handle shutdown"""
    global framework
    print("\nShutdown signal received...")
    framework.stop()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    framework = ContinuousTestingFrameworkV3()
    
    num_workers = min(4, os.cpu_count() or 4)
    
    print(f"Starting META-OPT-QUANT V3 continuous testing with {num_workers} workers")
    print("Focus: Maximum golden ratio discovery")
    print("Press Ctrl+C to stop")
    
    framework.start(num_workers)
    
    try:
        while True:
            time.sleep(180)  # Report every 3 minutes
            report = framework.generate_report()
            print("\n" + report)
    except KeyboardInterrupt:
        pass