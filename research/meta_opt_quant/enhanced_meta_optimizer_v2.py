#!/usr/bin/env python3
"""
Enhanced Meta-Optimizer V2 with Improved Bounds and Golden Ratio Emergence
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

from quantized_feedback_processor import QuantizedFeedbackProcessor
from parallel_pre_instruction_engine_simple import ParallelPreInstructionEngine
from global_cache_manager import get_global_cache, GlobalCacheManager

class EnhancedMetaOptimizerV2:
    """
    Enhanced meta-optimizer with improved numerical stability and golden ratio emergence
    """
    
    def __init__(self, session_cache_dir: str = "./session_cache"):
        self.quantizer = QuantizedFeedbackProcessor()
        self.pre_engine = ParallelPreInstructionEngine(session_cache_dir)
        self.global_cache = get_global_cache()
        self.session_id = self.global_cache.start_session()
        
        # Session metrics
        self.iteration_count = 0
        self.performance_history = []
        self.patterns_used = set()
        self.golden_discoveries = []
        
        # Improved parameters
        self.adaptive_exploration_rate = 0.1  # Start more conservative
        self.pattern_trust_threshold = 0.8
        self.golden_ratio_bonus = 1.5  # Reduced from 2.0
        self.phi = 1.618033988749895
        
        # Numerical stability
        self.max_param_value = 1e6  # Prevent overflow
        self.min_param_value = -1e6
        self.gradient_clip = 10.0
        
    def meta_optimize_enhanced(self, 
                             initial_state: Dict[str, Any],
                             objective_function: Callable,
                             problem_signature: Dict[str, Any] = None,
                             max_iterations: int = None,
                             convergence_threshold: float = None) -> Dict[str, Any]:
        """
        Enhanced meta-optimization with better numerical stability
        """
        
        problem_type = problem_signature.get('type', 'unknown') if problem_signature else 'unknown'
        
        # Improved hyperparameter suggestions
        if max_iterations is None or convergence_threshold is None:
            suggestions = self.global_cache.suggest_hyperparameters(problem_type)
            max_iterations = max_iterations or min(suggestions['suggested_max_iterations'], 100)
            convergence_threshold = convergence_threshold or max(suggestions['suggested_convergence_threshold'], 0.001)
            self.adaptive_exploration_rate = suggestions.get('suggested_exploration_rate', 0.1)
        
        # Normalize initial state to prevent overflow
        initial_state = self._normalize_state(initial_state)
        
        # Warm cache
        if problem_signature:
            warm_patterns = self.global_cache.warm_cache(problem_signature)
            if warm_patterns:
                # Pre-load only stable patterns
                for pattern in warm_patterns[:5]:
                    if abs(pattern['performance']) < 1e10:  # Filter out overflow patterns
                        self.pre_engine.cache.store_pattern(
                            symbol_hash=pattern['symbol_hash'],
                            F=pattern['F'],
                            V=pattern['V'],
                            E=pattern['E'],
                            trajectory=pattern['trajectory'],
                            performance=min(pattern['performance'], 1e6)  # Cap performance
                        )
        
        # Better baseline estimation
        baseline_iterations = self._estimate_baseline_iterations_v2(
            initial_state, objective_function, convergence_threshold
        )
        
        # Initialize optimization
        current_state = initial_state.copy()
        best_state = current_state.copy()
        best_score = objective_function(current_state)
        
        # Check for invalid initial score
        if not np.isfinite(best_score):
            best_score = -1e10
        
        print(f"Starting Enhanced META-OPT-QUANT V2")
        print(f"Initial score: {best_score:.6f}")
        print(f"Estimated baseline iterations: {baseline_iterations}")
        
        convergence_history = []
        no_improvement_count = 0
        best_golden_ratio_error = float('inf')
        
        for iteration in range(max_iterations):
            self.iteration_count += 1
            start_time = time.time()
            
            # Adaptive exploration decay
            if iteration > max_iterations // 2:
                self.adaptive_exploration_rate *= 0.95
            
            # Generate instructions with bounds
            pre_instructions = self._generate_bounded_instructions(
                current_state, iteration, max_iterations
            )
            
            # Execute with numerical safety
            results = self._execute_with_bounds(
                current_state, pre_instructions, objective_function
            )
            
            if results:
                # Filter out invalid results
                valid_results = [r for r in results if np.isfinite(r['score']) and abs(r['score']) < 1e10]
                
                if valid_results:
                    best_result = max(valid_results, key=lambda x: x['score'])
                    improvement = best_result['score'] - best_score
                    
                    # Only accept reasonable improvements
                    if 0 < improvement < best_score * 10:  # Max 10x improvement per step
                        # Track evolution
                        if best_result.get('parent_pattern'):
                            self.global_cache.track_evolution(
                                parent_pattern=best_result['parent_pattern'],
                                child_pattern={
                                    'symbol_hash': best_result['symbol_hash'],
                                    'F': best_result['F'],
                                    'V': best_result['V'],
                                    'E': best_result['E'],
                                    'performance': min(best_result['score'], 1e6),
                                    'trajectory': best_result['trajectory']
                                },
                                mutation_type=best_result.get('mutation_type', 'optimization')
                            )
                        
                        # Update state
                        best_state = best_result['state']
                        best_score = best_result['score']
                        current_state = best_state.copy()
                        no_improvement_count = 0
                        
                        # Store pattern with bounded performance
                        self._store_bounded_pattern(best_result)
                        
                        # Check golden ratio with better detection
                        golden_error = self._check_golden_ratio_v2(best_result)
                        if golden_error < best_golden_ratio_error:
                            best_golden_ratio_error = golden_error
                        
                        print(f"Iteration {iteration}: score: {best_score:.6f} "
                              f"(+{improvement:.6f}) φ-error: {golden_error:.4f}")
                    else:
                        no_improvement_count += 1
                        
                        # Intelligent exploration with bounds
                        if no_improvement_count > 3:
                            self.adaptive_exploration_rate = min(0.3, self.adaptive_exploration_rate * 1.1)
                            current_state = self._bounded_explore(current_state, best_state)
                else:
                    no_improvement_count += 1
                
                # Track convergence
                convergence_history.append({
                    'iteration': iteration,
                    'score': best_score,
                    'improvement': improvement if 'improvement' in locals() else 0,
                    'time': time.time() - start_time,
                    'patterns_used': len(self.patterns_used),
                    'golden_ratio_error': best_golden_ratio_error
                })
                
                # Convergence check
                if self._check_convergence_v2(convergence_history, convergence_threshold):
                    print(f"Converged after {iteration} iterations")
                    break
            
            # Periodic analysis
            if iteration % 20 == 0 and iteration > 0:
                self._analyze_progress_v2()
        
        # Record results
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
        
        fve_ratio = F * V / E if E > 0 else 0
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
                'fve_ratio': fve_ratio
            },
            'convergence_history': convergence_history,
            'best_golden_ratio_error': best_golden_ratio_error,
            'golden_discoveries': len(self.golden_discoveries)
        }
    
    def _normalize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize state values to prevent overflow"""
        normalized = {}
        for key, value in state.items():
            if isinstance(value, (int, float)):
                normalized[key] = np.clip(value, self.min_param_value, self.max_param_value)
            else:
                normalized[key] = value
        return normalized
    
    def _estimate_baseline_iterations_v2(self, initial_state: Dict[str, Any],
                                       objective_function: Callable,
                                       threshold: float) -> int:
        """Better baseline estimation"""
        # More realistic baseline based on problem dimension
        dimensions = len([k for k in initial_state if isinstance(initial_state[k], (int, float))])
        
        # Base iterations scaled by dimension
        base_iterations = max(20, dimensions * 5)
        
        # Adjust based on initial gradient
        test_state = initial_state.copy()
        initial_score = objective_function(test_state)
        
        if np.isfinite(initial_score):
            # Sample gradient
            gradients = []
            for key in test_state:
                if isinstance(test_state[key], (int, float)):
                    perturbed = test_state.copy()
                    perturbed[key] *= 1.01 if test_state[key] != 0 else 0.01
                    perturbed_score = objective_function(perturbed)
                    if np.isfinite(perturbed_score):
                        gradient = abs(perturbed_score - initial_score)
                        gradients.append(min(gradient, 1000))  # Cap gradient
            
            if gradients:
                avg_gradient = np.mean(gradients)
                # More conservative estimate
                gradient_factor = min(2.0, 1.0 / (avg_gradient + 0.1))
                base_iterations = int(base_iterations * gradient_factor)
        
        return min(max(base_iterations, 10), 200)  # Bounded estimate
    
    def _generate_bounded_instructions(self, state: Dict[str, Any],
                                     iteration: int, max_iterations: int) -> List[Dict[str, Any]]:
        """Generate instructions with proper bounds"""
        # Base instructions
        base_instructions = self.pre_engine.generate_parallel(state, top_k=3)
        
        # Add bounded golden ratio instruction
        if iteration < max_iterations * 0.7:  # More iterations for golden ratio
            golden_instruction = self._generate_golden_ratio_instruction_v2(state)
            base_instructions.append(golden_instruction)
        
        # Add conservative exploration
        if np.random.random() < self.adaptive_exploration_rate:
            explore_instruction = self._generate_conservative_exploration(state)
            base_instructions.append(explore_instruction)
        
        # Bound all trajectories
        for instruction in base_instructions:
            if 'trajectory' in instruction:
                instruction['trajectory'] = np.clip(
                    instruction['trajectory'], 
                    -self.gradient_clip, 
                    self.gradient_clip
                )
        
        return base_instructions
    
    def _generate_golden_ratio_instruction_v2(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Improved golden ratio seeking"""
        # Multiple strategies for golden ratio
        strategies = []
        
        # Strategy 1: Direct F-V-E tuning
        F = abs(state.get('frequency', 1.0))
        V = abs(state.get('vibration', 1.0))
        E = abs(state.get('energy', 1.0))
        
        if E > 0:
            current_ratio = F * V / E
            error = current_ratio - self.phi
            
            # Gentle adjustments
            f_adj = -np.sign(error) * min(0.1, abs(error) * 0.1)
            v_adj = -np.sign(error) * min(0.05, abs(error) * 0.05)
            e_adj = np.sign(error) * min(0.05, abs(error) * 0.05)
            
            strategies.append(('fve', [f_adj, v_adj, e_adj]))
        
        # Strategy 2: Sequential ratios
        numeric_params = sorted([(k, v) for k, v in state.items() 
                               if k.startswith('x') and isinstance(v, (int, float))],
                               key=lambda x: x[0])
        
        if len(numeric_params) >= 2:
            for i in range(len(numeric_params) - 1):
                if numeric_params[i][1] != 0:
                    ratio = numeric_params[i+1][1] / numeric_params[i][1]
                    error = ratio - self.phi
                    if abs(error) < 2.0:  # Only adjust if somewhat close
                        adj = -np.sign(error) * min(0.1, abs(error) * 0.05)
                        strategies.append((f'ratio_{i}', [0] * i + [adj, -adj]))
        
        # Select best strategy
        if strategies:
            strategy_name, adjustments = min(strategies, 
                                           key=lambda s: abs(sum(s[1])))
        else:
            strategy_name, adjustments = 'explore', np.random.randn(10) * 0.01
        
        # Create bounded trajectory
        trajectory = np.zeros(10)
        for i, adj in enumerate(adjustments[:10]):
            trajectory[i] = np.clip(adj, -0.2, 0.2)
        
        return {
            'instruction_id': f"golden_v2_{strategy_name}_{np.random.randint(1000)}",
            'trajectory': trajectory,
            'expected_improvement': 0.1,
            'source': 'golden_ratio_seeking_v2',
            'confidence': 0.7,
            'mutation_type': 'golden_ratio'
        }
    
    def _generate_conservative_exploration(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Conservative exploration to avoid divergence"""
        # Small random perturbations
        trajectory = np.random.randn(10) * 0.05  # Much smaller than before
        
        # Bias toward reducing large values
        for i, (k, v) in enumerate(state.items()):
            if isinstance(v, (int, float)) and i < 10:
                if abs(v) > 100:
                    # Shrink large values
                    trajectory[i] = -np.sign(v) * 0.1
        
        return {
            'instruction_id': f"conservative_explore_{np.random.randint(1000)}",
            'trajectory': np.clip(trajectory, -0.1, 0.1),
            'expected_improvement': 0.05,
            'source': 'conservative_exploration',
            'confidence': 0.5,
            'mutation_type': 'exploration'
        }
    
    def _execute_with_bounds(self, state: Dict[str, Any],
                           instructions: List[Dict[str, Any]],
                           objective_function: Callable) -> List[Dict[str, Any]]:
        """Execute instructions with bounds checking"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for instruction in instructions:
                future = executor.submit(
                    self._execute_bounded_instruction,
                    state, instruction, objective_function
                )
                futures.append((future, instruction))
            
            results = []
            for future, instruction in futures:
                try:
                    result = future.result(timeout=2.0)  # 2 second timeout
                    if result and np.isfinite(result['score']):
                        results.append(result)
                except Exception as e:
                    pass  # Skip failed instructions
            
            return results
    
    def _execute_bounded_instruction(self, state: Dict[str, Any],
                                   instruction: Dict[str, Any],
                                   objective_function: Callable) -> Dict[str, Any]:
        """Execute single instruction with bounds"""
        new_state = state.copy()
        trajectory = instruction.get('trajectory', np.zeros(10))
        
        # Apply bounded changes
        param_keys = sorted([k for k in new_state if isinstance(new_state[k], (int, float))])
        for i, delta in enumerate(trajectory):
            if i < len(param_keys):
                key = param_keys[i]
                old_value = new_state[key]
                
                # Multiplicative update with bounds
                if abs(old_value) > 0.01:
                    new_value = old_value * (1 + delta)
                else:
                    new_value = old_value + delta * 0.1
                
                # Apply bounds
                new_state[key] = np.clip(new_value, self.min_param_value, self.max_param_value)
        
        # Evaluate with safety
        try:
            score = objective_function(new_state)
            if not np.isfinite(score):
                score = -1e10
            score = np.clip(score, -1e10, 1e10)
        except:
            score = -1e10
        
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
            'E': E,
            'source': instruction.get('source', 'unknown'),
            'parent_pattern': instruction.get('parent_pattern'),
            'mutation_type': instruction.get('mutation_type', 'standard')
        }
    
    def _store_bounded_pattern(self, result: Dict[str, Any]):
        """Store pattern with bounded values"""
        bounded_score = np.clip(result['score'], -1e6, 1e6)
        
        # Store in both caches
        self.pre_engine.cache.store_pattern(
            symbol_hash=result['symbol_hash'],
            F=result['F'],
            V=result['V'],
            E=result['E'],
            trajectory=result['trajectory'],
            performance=bounded_score
        )
        
        self.global_cache.cache.store_pattern(
            symbol_hash=result['symbol_hash'],
            F=result['F'],
            V=result['V'],
            E=result['E'],
            trajectory=result['trajectory'],
            performance=bounded_score
        )
    
    def _check_golden_ratio_v2(self, result: Dict[str, Any]) -> float:
        """Improved golden ratio detection"""
        errors = []
        
        # Check F*V/E ratio
        if result['E'] > 0:
            fve_ratio = result['F'] * result['V'] / result['E']
            errors.append(abs(fve_ratio - self.phi))
        
        # Check state parameter ratios
        state = result['state']
        numeric_params = sorted([(k, v) for k, v in state.items() 
                               if isinstance(v, (int, float)) and abs(v) > 0.01],
                               key=lambda x: x[0])
        
        for i in range(len(numeric_params) - 1):
            if numeric_params[i][1] != 0:
                ratio = numeric_params[i+1][1] / numeric_params[i][1]
                if 0.5 < ratio < 3.0:  # Reasonable range
                    errors.append(abs(ratio - self.phi))
        
        # Best error
        best_error = min(errors) if errors else float('inf')
        
        # Track discovery
        if best_error < 0.1:
            self.golden_discoveries.append({
                'iteration': self.iteration_count,
                'error': best_error,
                'fve_ratio': result['F'] * result['V'] / result['E'] if result['E'] > 0 else 0
            })
            print(f"  🌟 Golden ratio approached! Error: {best_error:.6f}")
        
        return best_error
    
    def _bounded_explore(self, current_state: Dict[str, Any],
                        best_state: Dict[str, Any]) -> Dict[str, Any]:
        """Bounded exploration"""
        new_state = current_state.copy()
        
        # Mix with best state
        for key, value in new_state.items():
            if isinstance(value, (int, float)) and key in best_state:
                # Weighted average with small random perturbation
                new_state[key] = (0.7 * value + 0.3 * best_state[key] + 
                                 np.random.randn() * 0.1 * abs(value))
                # Apply bounds
                new_state[key] = np.clip(new_state[key], 
                                       self.min_param_value, 
                                       self.max_param_value)
        
        return new_state
    
    def _check_convergence_v2(self, history: List[Dict[str, Any]], 
                            threshold: float) -> bool:
        """Improved convergence checking"""
        if len(history) < 5:
            return False
        
        # Check recent improvements
        recent = history[-5:]
        improvements = [h['improvement'] for h in recent]
        
        # Standard convergence
        if all(abs(imp) < threshold for imp in improvements):
            return True
        
        # Golden ratio convergence
        if recent[-1]['golden_ratio_error'] < 0.01:
            return True
        
        # Stagnation with good enough result
        if (len(history) > 20 and 
            all(abs(imp) < threshold * 10 for imp in improvements) and
            recent[-1]['golden_ratio_error'] < 0.2):
            return True
        
        return False
    
    def _analyze_progress_v2(self):
        """Analyze optimization progress"""
        insights = self.global_cache.get_evolution_insights()
        
        print(f"\nProgress Analysis:")
        print(f"  Patterns used: {len(self.patterns_used)}")
        print(f"  Golden discoveries: {len(self.golden_discoveries)}")
        print(f"  Exploration rate: {self.adaptive_exploration_rate:.4f}")
        
        if self.golden_discoveries:
            best_discovery = min(self.golden_discoveries, key=lambda x: x['error'])
            print(f"  Best φ error: {best_discovery['error']:.6f}")


if __name__ == "__main__":
    # Test the improved optimizer
    from meta_optimizer import example_objective_function
    
    print("Testing Enhanced Meta-Optimizer V2")
    print("=" * 50)
    
    optimizer = EnhancedMetaOptimizerV2()
    
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
    print(f"Iterations: {result['iterations']}")
    print(f"Acceleration: {result['acceleration_percentage']:.1f}%")
    print(f"Best φ error: {result['best_golden_ratio_error']:.6f}")
    print(f"Golden discoveries: {result['golden_discoveries']}")