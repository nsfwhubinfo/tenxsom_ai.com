#!/usr/bin/env python3
"""
Enhanced Meta-Optimizer with Global Cache Integration
Implements advanced meta-learning with cross-session pattern transfer
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

from quantized_feedback_processor import QuantizedFeedbackProcessor
from parallel_pre_instruction_engine_simple import ParallelPreInstructionEngine
from global_cache_manager import get_global_cache, GlobalCacheManager

class EnhancedMetaOptimizer:
    """
    Enhanced meta-optimizer with global cache integration and
    advanced meta-learning capabilities
    """
    
    def __init__(self, session_cache_dir: str = "./session_cache"):
        self.quantizer = QuantizedFeedbackProcessor()
        self.pre_engine = ParallelPreInstructionEngine(session_cache_dir)
        
        # Global cache for cross-session learning
        self.global_cache = get_global_cache()
        self.session_id = self.global_cache.start_session()
        
        # Session-specific metrics
        self.iteration_count = 0
        self.performance_history = []
        self.patterns_used = set()
        self.convergence_accelerations = []
        
        # Enhanced parameters
        self.adaptive_exploration_rate = 0.2
        self.pattern_trust_threshold = 0.7
        self.golden_ratio_bonus = 2.0
        
    def meta_optimize_enhanced(self, 
                             initial_state: Dict[str, Any],
                             objective_function: Callable,
                             problem_signature: Dict[str, Any] = None,
                             max_iterations: int = None,
                             convergence_threshold: float = None) -> Dict[str, Any]:
        """
        Enhanced meta-optimization with global pattern learning
        
        Args:
            initial_state: Starting state
            objective_function: Function to optimize
            problem_signature: Problem description for cache warming
            max_iterations: Maximum iterations (auto-suggested if None)
            convergence_threshold: Convergence criteria (auto-suggested if None)
        """
        
        # Get problem type from signature
        problem_type = problem_signature.get('type', 'unknown') if problem_signature else 'unknown'
        
        # Get hyperparameter suggestions if not provided
        if max_iterations is None or convergence_threshold is None:
            suggestions = self.global_cache.suggest_hyperparameters(problem_type)
            max_iterations = max_iterations or suggestions['suggested_max_iterations']
            convergence_threshold = convergence_threshold or suggestions['suggested_convergence_threshold']
            self.adaptive_exploration_rate = suggestions.get('suggested_exploration_rate', 0.2)
        
        # Warm cache with relevant patterns
        if problem_signature:
            warm_patterns = self.global_cache.warm_cache(problem_signature)
            print(f"Warmed cache with {len(warm_patterns)} relevant patterns")
            
            # Pre-load high-performance patterns into session cache
            for pattern in warm_patterns[:10]:  # Top 10 patterns
                self.pre_engine.cache.store_pattern(
                    symbol_hash=pattern['symbol_hash'],
                    F=pattern['F'],
                    V=pattern['V'],
                    E=pattern['E'],
                    trajectory=pattern['trajectory'],
                    performance=pattern['performance']
                )
        
        # Track baseline performance without meta-optimization
        baseline_iterations = self._estimate_baseline_iterations(
            initial_state, objective_function, convergence_threshold
        )
        
        # Run enhanced optimization
        current_state = initial_state.copy()
        best_state = current_state.copy()
        best_score = objective_function(current_state)
        
        print(f"Starting Enhanced META-OPT-QUANT")
        print(f"Initial score: {best_score:.6f}")
        print(f"Estimated baseline iterations: {baseline_iterations}")
        
        convergence_history = []
        no_improvement_count = 0
        
        for iteration in range(max_iterations):
            self.iteration_count += 1
            start_time = time.time()
            
            # 1. Generate enhanced pre-instructions
            pre_instructions = self._generate_enhanced_instructions(
                current_state, iteration, max_iterations
            )
            
            # 2. Execute instructions with pattern tracking
            results = self._execute_with_tracking(
                current_state, pre_instructions, objective_function
            )
            
            if results:
                best_result = max(results, key=lambda x: x['score'])
                improvement = best_result['score'] - best_score
                
                if improvement > 0:
                    # Track pattern evolution
                    if best_result.get('parent_pattern'):
                        self.global_cache.track_evolution(
                            parent_pattern=best_result['parent_pattern'],
                            child_pattern={
                                'symbol_hash': best_result['symbol_hash'],
                                'F': best_result['F'],
                                'V': best_result['V'],
                                'E': best_result['E'],
                                'performance': best_result['score'],
                                'trajectory': best_result['trajectory']
                            },
                            mutation_type=best_result.get('mutation_type', 'optimization')
                        )
                    
                    # Update best state
                    previous_best = best_score
                    best_state = best_result['state']
                    best_score = best_result['score']
                    current_state = best_state.copy()
                    no_improvement_count = 0
                    
                    # Store in both caches
                    self._store_successful_pattern(best_result)
                    
                    # Check for golden ratio
                    self._check_golden_ratio(best_result)
                    
                    print(f"Iteration {iteration}: New best score: {best_score:.6f} "
                          f"(improvement: {improvement:.6f})")
                else:
                    no_improvement_count += 1
                    
                    # Adaptive exploration
                    if no_improvement_count > 3:
                        self.adaptive_exploration_rate = min(0.5, self.adaptive_exploration_rate * 1.2)
                        current_state = self._intelligent_explore(current_state, best_state)
                
                # Track convergence
                convergence_history.append({
                    'iteration': iteration,
                    'score': best_score,
                    'improvement': improvement,
                    'time': time.time() - start_time,
                    'patterns_used': len(self.patterns_used)
                })
                
                # Enhanced convergence check
                if self._check_enhanced_convergence(convergence_history, convergence_threshold):
                    print(f"Enhanced convergence achieved after {iteration} iterations")
                    break
            
            # Periodic analysis
            if iteration % 10 == 0:
                self._analyze_meta_learning_progress()
        
        # Record convergence improvement
        actual_iterations = self.iteration_count
        self.global_cache.record_convergence(
            session_id=self.session_id,
            problem_type=problem_type,
            initial_iterations=baseline_iterations,
            optimized_iterations=actual_iterations,
            patterns_used=len(self.patterns_used)
        )
        
        # Final analysis
        final_symbol = self.quantizer.quantize(best_state)
        F = final_symbol.frequency_band / 10.0 * 2.0
        V = {'low': 0.125, 'medium': 0.5, 'high': 0.85, 'resonant': 1.0}.get(
            final_symbol.vibration_class, 0.5)
        E = final_symbol.energy_level / 10.0 * 2.0
        
        acceleration = ((baseline_iterations - actual_iterations) / baseline_iterations * 100 
                       if baseline_iterations > 0 else 0)
        
        return {
            'optimized_state': best_state,
            'final_score': best_score,
            'iterations': actual_iterations,
            'baseline_iterations': baseline_iterations,
            'acceleration_percentage': acceleration,
            'patterns_used': len(self.patterns_used),
            'symbol': {
                'hash': final_symbol.symbol_id,
                'F': F,
                'V': V,
                'E': E,
                'fve_ratio': F * V / E if E > 0 else 0
            },
            'convergence_history': convergence_history,
            'global_insights': self.global_cache.get_evolution_insights()
        }
    
    def _estimate_baseline_iterations(self, initial_state: Dict[str, Any],
                                    objective_function: Callable,
                                    threshold: float) -> int:
        """Estimate iterations without meta-optimization"""
        # Simple gradient estimation
        test_state = initial_state.copy()
        initial_score = objective_function(test_state)
        
        # Perturb and measure gradient
        gradients = []
        for key in test_state:
            if isinstance(test_state[key], (int, float)):
                perturbed = test_state.copy()
                perturbed[key] *= 1.01
                gradient = abs(objective_function(perturbed) - initial_score)
                gradients.append(gradient)
        
        avg_gradient = np.mean(gradients) if gradients else 0.001
        
        # Rough estimation based on gradient
        estimated = int(1.0 / (avg_gradient + threshold))
        return min(max(estimated, 20), 500)  # Bounded estimate
    
    def _generate_enhanced_instructions(self, state: Dict[str, Any],
                                      iteration: int, max_iterations: int) -> List[Dict[str, Any]]:
        """Generate instructions with meta-learning enhancements"""
        # Base instructions from pre-engine
        base_instructions = self.pre_engine.generate_parallel(state, top_k=3)
        
        # Add globally successful patterns
        symbol = self.quantizer.quantize(state)
        F = symbol.frequency_band / 10.0 * 2.0
        V = {'low': 0.125, 'medium': 0.5, 'high': 0.85, 'resonant': 1.0}.get(
            symbol.vibration_class, 0.5)
        E = symbol.energy_level / 10.0 * 2.0
        
        global_patterns = self.global_cache.cache.find_similar_patterns(
            F=F, V=V, E=E, tolerance=0.3, limit=3
        )
        
        enhanced_instructions = base_instructions.copy()
        
        # Add instructions from global patterns
        for pattern in global_patterns:
            if pattern['performance'] > self.pattern_trust_threshold:
                instruction = {
                    'instruction_id': f"global_{pattern['symbol_hash'][:8]}",
                    'trajectory': pattern['trajectory'],
                    'expected_improvement': pattern['performance'] * (1 - pattern['distance']),
                    'source': 'global_cache',
                    'confidence': 0.9,
                    'parent_pattern': pattern
                }
                enhanced_instructions.append(instruction)
                self.patterns_used.add(pattern['symbol_hash'])
        
        # Add golden ratio seeking instruction
        if iteration < max_iterations * 0.5:  # First half of optimization
            golden_instruction = self._generate_golden_ratio_instruction(state)
            enhanced_instructions.append(golden_instruction)
        
        return enhanced_instructions
    
    def _generate_golden_ratio_instruction(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate instruction targeting golden ratio"""
        phi = 1.618033988749895
        
        # Extract F-V-E if available
        F = state.get('frequency', 1.0)
        V = state.get('vibration', 1.0)
        E = state.get('energy', 1.0)
        
        # Calculate adjustments to approach golden ratio
        current_ratio = F * V / E if E > 0 else 0
        adjustment_factor = phi / current_ratio if current_ratio > 0 else phi
        
        # Create trajectory pushing toward golden ratio
        trajectory = np.zeros(10)
        trajectory[0] = np.log(adjustment_factor) * 0.1  # Frequency adjustment
        trajectory[1] = np.log(adjustment_factor) * 0.05  # Vibration adjustment
        trajectory[2] = -np.log(adjustment_factor) * 0.05  # Energy adjustment
        
        return {
            'instruction_id': f"golden_{np.random.randint(1000)}",
            'trajectory': trajectory,
            'expected_improvement': 0.2,
            'source': 'golden_ratio_seeking',
            'confidence': 0.6,
            'mutation_type': 'golden_ratio'
        }
    
    def _execute_with_tracking(self, state: Dict[str, Any],
                             instructions: List[Dict[str, Any]],
                             objective_function: Callable) -> List[Dict[str, Any]]:
        """Execute instructions with enhanced tracking"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for instruction in instructions:
                future = executor.submit(
                    self._execute_single_instruction,
                    state, instruction, objective_function
                )
                futures.append((future, instruction))
            
            results = []
            for future, instruction in futures:
                try:
                    result = future.result()
                    # Add metadata
                    result['source'] = instruction.get('source', 'unknown')
                    result['parent_pattern'] = instruction.get('parent_pattern')
                    result['mutation_type'] = instruction.get('mutation_type', 'standard')
                    results.append(result)
                except Exception as e:
                    print(f"Instruction execution failed: {e}")
            
            return results
    
    def _execute_single_instruction(self, state: Dict[str, Any],
                                  instruction: Dict[str, Any],
                                  objective_function: Callable) -> Dict[str, Any]:
        """Execute a single instruction with tracking"""
        new_state = state.copy()
        trajectory = instruction.get('trajectory', np.zeros(10))
        
        # Apply trajectory
        param_keys = [k for k in new_state if isinstance(new_state[k], (int, float))]
        for i, delta in enumerate(trajectory):
            if i < len(param_keys):
                key = param_keys[i]
                new_state[key] = new_state[key] * (1 + delta)
        
        # Evaluate
        score = objective_function(new_state)
        
        # Quantize for tracking
        symbol = self.quantizer.quantize(new_state)
        F = symbol.frequency_band / 10.0 * 2.0
        V = {'low': 0.125, 'medium': 0.5, 'high': 0.85, 'resonant': 1.0}.get(
            symbol.vibration_class, 0.5)
        E = symbol.energy_level / 10.0 * 2.0
        
        return {
            'state': new_state,
            'score': score,
            'instruction': instruction,
            'trajectory': trajectory,
            'symbol_hash': symbol.symbol_id,
            'F': F,
            'V': V,
            'E': E
        }
    
    def _store_successful_pattern(self, result: Dict[str, Any]):
        """Store successful pattern in both caches"""
        # Store in session cache
        self.pre_engine.cache.store_pattern(
            symbol_hash=result['symbol_hash'],
            F=result['F'],
            V=result['V'],
            E=result['E'],
            trajectory=result['trajectory'],
            performance=result['score']
        )
        
        # Store in global cache
        self.global_cache.cache.store_pattern(
            symbol_hash=result['symbol_hash'],
            F=result['F'],
            V=result['V'],
            E=result['E'],
            trajectory=result['trajectory'],
            performance=result['score']
        )
    
    def _check_golden_ratio(self, result: Dict[str, Any]):
        """Check and reward golden ratio emergence"""
        phi = 1.618033988749895
        ratio = result['F'] * result['V'] / result['E'] if result['E'] > 0 else 0
        
        if abs(ratio - phi) < 0.1:
            print(f"  🌟 Golden ratio detected! F*V/E = {ratio:.6f}")
            # Bonus score for golden ratio
            result['score'] *= self.golden_ratio_bonus
    
    def _intelligent_explore(self, current_state: Dict[str, Any],
                           best_state: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent exploration based on meta-learning insights"""
        insights = self.global_cache.get_evolution_insights()
        avg_deltas = insights['average_successful_deltas']
        
        new_state = current_state.copy()
        
        # Apply successful delta patterns
        if 'frequency' in new_state:
            new_state['frequency'] *= (1 + avg_deltas['F'])
        if 'vibration' in new_state:
            new_state['vibration'] *= (1 + avg_deltas['V'])
        if 'energy' in new_state:
            new_state['energy'] *= (1 + avg_deltas['E'])
        
        # Random exploration for other parameters
        for key, value in new_state.items():
            if isinstance(value, (int, float)) and np.random.random() < self.adaptive_exploration_rate:
                perturbation = np.random.normal(0, 0.1)
                new_state[key] = value * (1 + perturbation)
        
        return new_state
    
    def _check_enhanced_convergence(self, history: List[Dict[str, Any]],
                                  threshold: float) -> bool:
        """Enhanced convergence checking with pattern analysis"""
        if len(history) < 5:
            return False
        
        # Check recent improvements
        recent_improvements = [h['improvement'] for h in history[-5:]]
        
        # Standard convergence
        if all(abs(imp) < threshold for imp in recent_improvements):
            return True
        
        # Pattern-based convergence
        recent_patterns = [h['patterns_used'] for h in history[-5:]]
        if len(set(recent_patterns)) == 1 and recent_patterns[0] > 10:
            # Stable pattern usage with many patterns
            return True
        
        return False
    
    def _analyze_meta_learning_progress(self):
        """Analyze and report meta-learning progress"""
        insights = self.global_cache.get_evolution_insights()
        stats = self.global_cache.cache.get_cache_stats()
        
        print(f"\nMeta-Learning Progress:")
        print(f"  Global patterns: {insights['total_patterns']}")
        print(f"  Session patterns used: {len(self.patterns_used)}")
        print(f"  Golden ratio discoveries: {insights['golden_ratio_discoveries']}")
        print(f"  Avg convergence improvement: {self.global_cache.stats['average_convergence_improvement']:.1f}%")


if __name__ == "__main__":
    # Test enhanced optimizer
    from meta_optimizer import example_objective_function
    
    print("Testing Enhanced Meta-Optimizer")
    print("=" * 50)
    
    optimizer = EnhancedMetaOptimizer()
    
    initial_state = {
        'param_0': 1.0,
        'param_1': 1.2,
        'param_2': 1.5,
        'frequency': 1.0,
        'vibration': 1.0,
        'energy': 1.0
    }
    
    problem_signature = {
        'type': 'golden_ratio_seeking',
        'dimensions': 6,
        'objective_type': 'cos_exp'
    }
    
    result = optimizer.meta_optimize_enhanced(
        initial_state=initial_state,
        objective_function=example_objective_function,
        problem_signature=problem_signature,
        max_iterations=50
    )
    
    print(f"\nOptimization Complete!")
    print(f"Final score: {result['final_score']:.6f}")
    print(f"Iterations: {result['iterations']} (baseline: {result['baseline_iterations']})")
    print(f"Acceleration: {result['acceleration_percentage']:.1f}%")
    print(f"F*V/E ratio: {result['symbol']['fve_ratio']:.6f}")