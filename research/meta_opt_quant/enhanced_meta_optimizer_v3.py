#!/usr/bin/env python3
"""
Enhanced Meta-Optimizer V3 - Optimized for Golden Ratio Discovery
Building on V2's 28.9% success rate to achieve even better results
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

from quantized_feedback_processor import QuantizedFeedbackProcessor
from parallel_pre_instruction_engine_simple import ParallelPreInstructionEngine
from global_cache_manager import get_global_cache, GlobalCacheManager

class EnhancedMetaOptimizerV3:
    """
    V3 optimizer with problem-aware strategies and enhanced golden ratio discovery
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
        
        # V3 Enhanced parameters
        self.phi = 1.618033988749895
        self.phi_inverse = 0.618033988749895
        self.sqrt_5 = 2.23606797749979
        
        # Problem-aware settings
        self.problem_type = 'unknown'
        self.dimension_factor = 1.0
        
        # Adaptive parameters
        self.exploration_rate = 0.15
        self.golden_bonus = 1.2  # Reduced for stability
        self.pattern_trust = 0.85
        
        # Numerical bounds
        self.max_value = 1e4
        self.min_value = -1e4
        self.gradient_clip = 5.0
        
        # Golden ratio targeting
        self.golden_focus_mode = False
        self.golden_strategies = []
        
    def meta_optimize_enhanced(self, 
                             initial_state: Dict[str, Any],
                             objective_function: Callable,
                             problem_signature: Dict[str, Any] = None,
                             max_iterations: int = None,
                             convergence_threshold: float = None) -> Dict[str, Any]:
        """
        V3 meta-optimization with problem-aware strategies
        """
        
        # Analyze problem type
        self.problem_type = problem_signature.get('type', 'unknown') if problem_signature else 'unknown'
        problem_name = problem_signature.get('objective_type', '') if problem_signature else ''
        
        # V3: Problem-specific configuration
        self._configure_for_problem(problem_name, initial_state)
        
        # Get suggestions
        if max_iterations is None or convergence_threshold is None:
            suggestions = self.global_cache.suggest_hyperparameters(self.problem_type)
            max_iterations = max_iterations or min(suggestions['suggested_max_iterations'], 100)
            convergence_threshold = convergence_threshold or max(suggestions['suggested_convergence_threshold'], 0.0001)
        
        # Normalize and prepare initial state
        initial_state = self._prepare_initial_state(initial_state)
        
        # Warm cache with golden-ratio biased patterns
        if problem_signature:
            warm_patterns = self.global_cache.warm_cache(problem_signature)
            # Prioritize patterns with good golden ratios
            golden_patterns = [p for p in warm_patterns if 1.4 < p.get('F', 0) * p.get('V', 1) / p.get('E', 1) < 1.8]
            for pattern in golden_patterns[:10]:
                self.pre_engine.cache.store_pattern(
                    symbol_hash=pattern['symbol_hash'],
                    F=pattern['F'],
                    V=pattern['V'],
                    E=pattern['E'],
                    trajectory=pattern['trajectory'],
                    performance=pattern['performance']
                )
        
        # Baseline estimation
        baseline_iterations = self._estimate_baseline_v3(initial_state, objective_function)
        
        # Initialize
        current_state = initial_state.copy()
        best_state = current_state.copy()
        best_score = objective_function(current_state)
        
        if not np.isfinite(best_score):
            best_score = -1e10
        
        print(f"Starting Enhanced META-OPT-QUANT V3")
        print(f"Problem: {problem_name}, Golden focus: {self.golden_focus_mode}")
        print(f"Initial score: {best_score:.6f}")
        
        # Tracking
        convergence_history = []
        no_improvement_count = 0
        best_golden_error = float('inf')
        golden_discovery_iteration = None
        
        for iteration in range(max_iterations):
            self.iteration_count += 1
            start_time = time.time()
            
            # V3: Dynamic strategy adjustment
            self._adjust_strategy(iteration, max_iterations, convergence_history)
            
            # Generate instructions with V3 enhancements
            pre_instructions = self._generate_v3_instructions(
                current_state, iteration, max_iterations, best_golden_error
            )
            
            # Execute
            results = self._execute_safely(current_state, pre_instructions, objective_function)
            
            if results:
                valid_results = [r for r in results if np.isfinite(r['score'])]
                
                if valid_results:
                    # V3: Smart selection based on problem type
                    best_result = self._select_best_result(valid_results, best_golden_error)
                    improvement = best_result['score'] - best_score
                    
                    # Accept improvements
                    if improvement > 0 and improvement < abs(best_score) * 10:
                        # Evolution tracking
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
                        
                        best_state = best_result['state']
                        best_score = best_result['score']
                        current_state = best_state.copy()
                        no_improvement_count = 0
                        
                        self._store_bounded_pattern(best_result)
                        
                        # V3: Enhanced golden ratio checking
                        golden_error = self._check_golden_v3(best_result)
                        if golden_error < best_golden_error:
                            best_golden_error = golden_error
                            if golden_error < 0.1 and golden_discovery_iteration is None:
                                golden_discovery_iteration = iteration
                        
                        print(f"Iteration {iteration}: score: {best_score:.6f} "
                              f"(+{improvement:.6f}) φ-error: {golden_error:.4f}")
                    else:
                        no_improvement_count += 1
                        
                        # V3: Intelligent recovery
                        if no_improvement_count > 2:
                            current_state = self._intelligent_recovery(
                                current_state, best_state, best_golden_error
                            )
                else:
                    no_improvement_count += 1
                
                # Update history
                convergence_history.append({
                    'iteration': iteration,
                    'score': best_score,
                    'improvement': improvement if 'improvement' in locals() else 0,
                    'time': time.time() - start_time,
                    'patterns_used': len(self.patterns_used),
                    'golden_ratio_error': best_golden_error
                })
                
                # V3: Multi-criteria convergence
                if self._check_convergence_v3(convergence_history, convergence_threshold, best_golden_error):
                    print(f"Converged after {iteration} iterations")
                    break
            
            # Progress analysis
            if iteration % 20 == 0 and iteration > 0:
                self._analyze_progress_v3(convergence_history)
        
        # Record results
        actual_iterations = self.iteration_count
        self.global_cache.record_convergence(
            session_id=self.session_id,
            problem_type=self.problem_type,
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
            'best_golden_ratio_error': best_golden_error,
            'golden_discoveries': len(self.golden_discoveries),
            'golden_discovery_iteration': golden_discovery_iteration,
            'problem_type': problem_name
        }
    
    def _configure_for_problem(self, problem_name: str, initial_state: Dict[str, Any]):
        """V3: Configure optimizer based on problem type"""
        dimensions = len([k for k in initial_state if isinstance(initial_state[k], (int, float))])
        self.dimension_factor = np.sqrt(dimensions) / 3.0
        
        # Golden-focused problems
        if any(term in problem_name.lower() for term in ['golden', 'fibonacci', 'cos_exp', 'harmonic']):
            self.golden_focus_mode = True
            self.exploration_rate = 0.1
            self.golden_bonus = 1.5
            self.pattern_trust = 0.9
            
            # Pre-compute golden strategies
            self._prepare_golden_strategies(initial_state)
            
        # Standard optimization problems
        elif any(term in problem_name.lower() for term in ['rosenbrock', 'rastrigin', 'sphere']):
            self.golden_focus_mode = False
            self.exploration_rate = 0.2
            self.golden_bonus = 1.1
            self.pattern_trust = 0.7
            
        # High-dimensional problems
        if dimensions > 20:
            self.exploration_rate *= 0.5
            self.gradient_clip *= 0.5
    
    def _prepare_initial_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """V3: Smart initial state preparation"""
        prepared = {}
        
        for key, value in state.items():
            if isinstance(value, (int, float)):
                # Bound values
                prepared[key] = np.clip(value, self.min_value, self.max_value)
                
                # V3: Bias toward golden ratio range for suitable parameters
                if self.golden_focus_mode and key in ['frequency', 'vibration', 'energy']:
                    if 0.5 < value < 3.0:
                        # Gently nudge toward golden ratio neighborhood
                        prepared[key] = value * (1 + np.random.normal(0, 0.05))
            else:
                prepared[key] = value
                
        return prepared
    
    def _estimate_baseline_v3(self, initial_state: Dict[str, Any],
                            objective_function: Callable) -> int:
        """V3: Improved baseline estimation"""
        dimensions = len([k for k in initial_state if isinstance(initial_state[k], (int, float))])
        
        # Problem-specific baselines
        if self.golden_focus_mode:
            # Golden problems converge faster with our methods
            base = max(10, dimensions * 3)
        else:
            # Standard problems need more iterations
            base = max(20, dimensions * 5)
        
        # Sample gradient for adjustment
        try:
            initial_score = objective_function(initial_state)
            if np.isfinite(initial_score):
                gradients = []
                for key in list(initial_state.keys())[:5]:  # Sample first 5
                    if isinstance(initial_state[key], (int, float)):
                        perturbed = initial_state.copy()
                        perturbed[key] *= 1.01 if initial_state[key] != 0 else 0.01
                        perturbed_score = objective_function(perturbed)
                        if np.isfinite(perturbed_score):
                            grad = abs(perturbed_score - initial_score) / (abs(initial_state[key]) + 1e-6)
                            gradients.append(min(grad, 10))
                
                if gradients:
                    avg_gradient = np.mean(gradients)
                    # High gradient = easier problem = fewer iterations
                    gradient_factor = 1.0 / (1.0 + avg_gradient)
                    base = int(base * gradient_factor)
        except:
            pass
        
        return min(max(base, 10), 150)
    
    def _prepare_golden_strategies(self, state: Dict[str, Any]):
        """V3: Pre-compute golden ratio strategies"""
        self.golden_strategies = []
        
        # Strategy 1: Direct F-V-E golden ratio
        if all(k in state for k in ['frequency', 'vibration', 'energy']):
            self.golden_strategies.append('fve_direct')
        
        # Strategy 2: Sequential ratios
        x_params = sorted([k for k in state if k.startswith('x')])
        if len(x_params) >= 2:
            self.golden_strategies.append('sequential_ratios')
        
        # Strategy 3: Fibonacci sequence
        if len(x_params) >= 3:
            self.golden_strategies.append('fibonacci_sequence')
        
        # Strategy 4: Golden spiral
        if len(x_params) >= 4:
            self.golden_strategies.append('golden_spiral')
    
    def _generate_v3_instructions(self, state: Dict[str, Any], iteration: int,
                                max_iterations: int, current_golden_error: float) -> List[Dict[str, Any]]:
        """V3: Advanced instruction generation"""
        instructions = []
        
        # Base instructions from cache
        base = self.pre_engine.generate_parallel(state, top_k=2)
        instructions.extend(base)
        
        # V3: Golden ratio focused instructions
        if self.golden_focus_mode or current_golden_error > 0.1:
            # Try multiple golden strategies
            for strategy in self.golden_strategies[:3]:
                golden_inst = self._generate_golden_instruction_v3(state, strategy, current_golden_error)
                if golden_inst:
                    instructions.append(golden_inst)
        
        # V3: Adaptive exploration
        if iteration < max_iterations * 0.8:  # Explore more early
            if np.random.random() < self.exploration_rate:
                explore_inst = self._generate_adaptive_exploration(state, iteration, max_iterations)
                instructions.append(explore_inst)
        
        # V3: Convergence acceleration
        if iteration > max_iterations * 0.5 and current_golden_error < 0.2:
            fine_tune = self._generate_fine_tuning(state, current_golden_error)
            if fine_tune:
                instructions.append(fine_tune)
        
        return instructions
    
    def _generate_golden_instruction_v3(self, state: Dict[str, Any], 
                                      strategy: str, current_error: float) -> Optional[Dict[str, Any]]:
        """V3: Strategy-specific golden ratio instruction"""
        trajectory = np.zeros(10)
        confidence = 0.8
        
        if strategy == 'fve_direct':
            # Direct F-V-E tuning with adaptive step size
            F = abs(state.get('frequency', 1.0))
            V = abs(state.get('vibration', 1.0))
            E = abs(state.get('energy', 1.0))
            
            if E > 0:
                current_ratio = F * V / E
                error = current_ratio - self.phi
                
                # Adaptive step size based on error magnitude
                step_size = min(0.2, abs(error) * 0.3)
                
                # Precise adjustments
                if abs(error) < 0.5:  # Close to target
                    trajectory[0] = -np.sign(error) * step_size * 0.6  # F
                    trajectory[1] = -np.sign(error) * step_size * 0.3  # V
                    trajectory[2] = np.sign(error) * step_size * 0.1   # E
                    confidence = 0.9
                else:  # Far from target
                    trajectory[0] = -np.sign(error) * step_size
                    trajectory[1] = -np.sign(error) * step_size * 0.5
                    trajectory[2] = np.sign(error) * step_size * 0.5
        
        elif strategy == 'sequential_ratios':
            # Adjust sequential parameters for golden ratios
            x_params = sorted([(k, v) for k, v in state.items() 
                             if k.startswith('x') and isinstance(v, (int, float))],
                             key=lambda x: x[0])
            
            if len(x_params) >= 2:
                best_pair = None
                best_error = float('inf')
                
                # Find best pair to adjust
                for i in range(len(x_params) - 1):
                    if x_params[i][1] > 0:
                        ratio = x_params[i+1][1] / x_params[i][1]
                        error = abs(ratio - self.phi)
                        if error < best_error and error < 2.0:
                            best_error = error
                            best_pair = i
                
                if best_pair is not None:
                    # Adjust the best pair
                    step = min(0.1, best_error * 0.2)
                    trajectory[best_pair] = -step if x_params[best_pair+1][1] / x_params[best_pair][1] > self.phi else step
                    trajectory[best_pair + 1] = step if x_params[best_pair+1][1] / x_params[best_pair][1] > self.phi else -step
                    confidence = 0.85
        
        elif strategy == 'fibonacci_sequence':
            # Create Fibonacci relationships
            x_params = sorted([(k, v) for k, v in state.items() 
                             if k.startswith('x') and isinstance(v, (int, float))],
                             key=lambda x: x[0])
            
            if len(x_params) >= 3:
                for i in range(len(x_params) - 2):
                    if x_params[i][1] > 0 and x_params[i+1][1] > 0:
                        target = x_params[i][1] + x_params[i+1][1]
                        error = x_params[i+2][1] - target
                        if abs(error) < 5:
                            trajectory[i+2] = -error * 0.1
                            confidence = 0.75
                            break
        
        elif strategy == 'golden_spiral':
            # Golden spiral pattern
            amplitude = 0.1 * (1 - current_error / 2)  # Decrease amplitude as we approach golden ratio
            for i in range(min(10, len(trajectory))):
                angle = i * self.phi
                trajectory[i] = amplitude * np.sin(angle) * np.exp(-i * 0.1)
            confidence = 0.7
        
        if np.any(trajectory != 0):
            return {
                'instruction_id': f"golden_v3_{strategy}_{np.random.randint(1000)}",
                'trajectory': np.clip(trajectory, -self.gradient_clip, self.gradient_clip),
                'expected_improvement': 0.1 * confidence,
                'source': f'golden_v3_{strategy}',
                'confidence': confidence,
                'mutation_type': 'golden_ratio'
            }
        
        return None
    
    def _generate_adaptive_exploration(self, state: Dict[str, Any], 
                                     iteration: int, max_iterations: int) -> Dict[str, Any]:
        """V3: Adaptive exploration based on progress"""
        progress = iteration / max_iterations
        
        # Decay exploration over time
        base_amplitude = self.exploration_rate * (1 - progress * 0.5)
        
        # Problem-aware exploration
        if self.golden_focus_mode:
            # Explore around golden ratio values
            trajectory = np.zeros(10)
            for i in range(min(10, len(state))):
                if np.random.random() < 0.5:
                    # Explore near golden ratio multiples
                    golden_mult = self.phi ** (np.random.randint(-2, 3))
                    trajectory[i] = np.random.normal(0, base_amplitude) * golden_mult * 0.1
                else:
                    trajectory[i] = np.random.normal(0, base_amplitude)
        else:
            # Standard exploration
            trajectory = np.random.normal(0, base_amplitude, 10)
        
        return {
            'instruction_id': f"adaptive_explore_{iteration}",
            'trajectory': np.clip(trajectory, -self.gradient_clip * 0.5, self.gradient_clip * 0.5),
            'expected_improvement': 0.05,
            'source': 'adaptive_exploration',
            'confidence': 0.5,
            'mutation_type': 'exploration'
        }
    
    def _generate_fine_tuning(self, state: Dict[str, Any], golden_error: float) -> Optional[Dict[str, Any]]:
        """V3: Fine-tuning when close to golden ratio"""
        if golden_error > 0.5:  # Not close enough
            return None
        
        # Very small adjustments
        trajectory = np.zeros(10)
        
        # Fine-tune F-V-E if available
        if all(k in state for k in ['frequency', 'vibration', 'energy']):
            F = abs(state.get('frequency', 1.0))
            V = abs(state.get('vibration', 1.0))
            E = abs(state.get('energy', 1.0))
            
            if E > 0:
                current_ratio = F * V / E
                error = current_ratio - self.phi
                
                # Micro adjustments
                micro_step = min(0.01, abs(error) * 0.1)
                trajectory[0] = -np.sign(error) * micro_step * 0.5
                trajectory[1] = -np.sign(error) * micro_step * 0.3
                trajectory[2] = np.sign(error) * micro_step * 0.2
        
        return {
            'instruction_id': f"fine_tune_{np.random.randint(1000)}",
            'trajectory': trajectory,
            'expected_improvement': 0.01,
            'source': 'fine_tuning',
            'confidence': 0.95,
            'mutation_type': 'fine_tune'
        }
    
    def _execute_safely(self, state: Dict[str, Any], instructions: List[Dict[str, Any]],
                       objective_function: Callable) -> List[Dict[str, Any]]:
        """V3: Safe execution with timeout and validation"""
        with ThreadPoolExecutor(max_workers=min(len(instructions), 5)) as executor:
            futures = []
            
            for instruction in instructions:
                future = executor.submit(
                    self._execute_single_safe,
                    state, instruction, objective_function
                )
                futures.append((future, instruction))
            
            results = []
            for future, instruction in futures:
                try:
                    result = future.result(timeout=1.0)
                    if result and np.isfinite(result['score']) and abs(result['score']) < 1e10:
                        results.append(result)
                except:
                    pass
            
            return results
    
    def _execute_single_safe(self, state: Dict[str, Any], instruction: Dict[str, Any],
                           objective_function: Callable) -> Dict[str, Any]:
        """V3: Execute with safety checks"""
        new_state = state.copy()
        trajectory = instruction.get('trajectory', np.zeros(10))
        
        # Apply changes
        param_keys = sorted([k for k in new_state if isinstance(new_state[k], (int, float))])
        for i, delta in enumerate(trajectory):
            if i < len(param_keys):
                key = param_keys[i]
                old_value = new_state[key]
                
                # Safe update
                if abs(old_value) > 0.01:
                    new_value = old_value * (1 + np.clip(delta, -0.5, 0.5))
                else:
                    new_value = old_value + delta * 0.1
                
                new_state[key] = np.clip(new_value, self.min_value, self.max_value)
        
        # Evaluate
        try:
            score = objective_function(new_state)
            if not np.isfinite(score):
                score = -1e10
            score = np.clip(score, -1e10, 1e10)
        except:
            score = -1e10
        
        # Quantize
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
    
    def _select_best_result(self, results: List[Dict[str, Any]], 
                          current_golden_error: float) -> Dict[str, Any]:
        """V3: Smart result selection based on multiple criteria"""
        # Calculate composite scores
        for result in results:
            base_score = result['score']
            
            # Golden ratio bonus
            if result['E'] > 0:
                fve_ratio = result['F'] * result['V'] / result['E']
                golden_error = abs(fve_ratio - self.phi)
                
                # Stronger bonus for golden ratio proximity
                if golden_error < 0.1:
                    golden_bonus = self.golden_bonus * (1 + (0.1 - golden_error))
                    result['composite_score'] = base_score * golden_bonus
                elif golden_error < current_golden_error:
                    # Improvement bonus
                    result['composite_score'] = base_score * (1 + 0.1)
                else:
                    result['composite_score'] = base_score
            else:
                result['composite_score'] = base_score
            
            # Source bonus
            if result['source'].startswith('golden_v3'):
                result['composite_score'] *= 1.05
        
        # Select best by composite score
        return max(results, key=lambda x: x['composite_score'])
    
    def _check_golden_v3(self, result: Dict[str, Any]) -> float:
        """V3: Comprehensive golden ratio checking"""
        errors = []
        
        # Check F*V/E
        if result['E'] > 0:
            fve_ratio = result['F'] * result['V'] / result['E']
            fve_error = abs(fve_ratio - self.phi)
            errors.append(fve_error)
            
            # Check reciprocal
            if result['F'] > 0:
                vf_ratio = result['V'] / result['F']
                errors.append(abs(vf_ratio - self.phi_inverse))
        
        # Check state parameters
        state = result['state']
        
        # Sequential ratios
        x_params = sorted([(k, v) for k, v in state.items() 
                         if isinstance(v, (int, float)) and abs(v) > 0.01],
                         key=lambda x: x[0])
        
        for i in range(len(x_params) - 1):
            if x_params[i][1] != 0:
                ratio = x_params[i+1][1] / x_params[i][1]
                if 0.3 < ratio < 3.0:
                    errors.append(abs(ratio - self.phi))
                    errors.append(abs(ratio - self.phi_inverse))
        
        # Fibonacci check
        if len(x_params) >= 3:
            for i in range(len(x_params) - 2):
                if x_params[i+2][1] != 0:
                    fib_ratio = (x_params[i][1] + x_params[i+1][1]) / x_params[i+2][1]
                    if 0.5 < fib_ratio < 1.5:
                        errors.append(abs(fib_ratio - 1.0))
        
        # Best error
        best_error = min(errors) if errors else float('inf')
        
        # Track discovery
        if best_error < 0.1:
            self.golden_discoveries.append({
                'iteration': self.iteration_count,
                'error': best_error,
                'type': 'fve' if best_error == errors[0] else 'other'
            })
            print(f"  🌟 Golden ratio discovered! Error: {best_error:.6f}")
        
        return best_error
    
    def _intelligent_recovery(self, current_state: Dict[str, Any],
                            best_state: Dict[str, Any], 
                            golden_error: float) -> Dict[str, Any]:
        """V3: Smart recovery strategy"""
        new_state = current_state.copy()
        
        if golden_error < 0.5 and self.golden_focus_mode:
            # If close to golden ratio, make small adjustments
            for key in new_state:
                if isinstance(new_state[key], (int, float)) and key in best_state:
                    # Weighted average favoring best state
                    new_state[key] = 0.8 * best_state[key] + 0.2 * new_state[key]
                    # Small perturbation
                    new_state[key] += np.random.normal(0, 0.01 * abs(new_state[key]))
        else:
            # Larger exploration
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    if key in ['frequency', 'vibration', 'energy'] and self.golden_focus_mode:
                        # Reset to golden-friendly range
                        new_state[key] = np.random.uniform(0.8, 2.0)
                    else:
                        # Mix with best state
                        if key in best_state:
                            new_state[key] = 0.5 * new_state[key] + 0.5 * best_state[key]
                        # Exploration
                        new_state[key] *= (1 + np.random.normal(0, self.exploration_rate))
                    
                    # Bounds
                    new_state[key] = np.clip(new_state[key], self.min_value, self.max_value)
        
        return new_state
    
    def _check_convergence_v3(self, history: List[Dict[str, Any]], 
                            threshold: float, golden_error: float) -> bool:
        """V3: Multi-criteria convergence"""
        if len(history) < 5:
            return False
        
        recent = history[-5:]
        improvements = [h['improvement'] for h in recent]
        
        # Standard convergence
        if all(abs(imp) < threshold for imp in improvements):
            return True
        
        # Golden ratio achievement
        if golden_error < 0.001:  # Very close
            return True
        
        # Good enough with stability
        if (golden_error < 0.01 and 
            all(abs(imp) < threshold * 10 for imp in improvements)):
            return True
        
        # Time-based with good result
        if (len(history) > 30 and golden_error < 0.1 and
            all(abs(imp) < threshold * 100 for imp in improvements)):
            return True
        
        return False
    
    def _adjust_strategy(self, iteration: int, max_iterations: int, history: List[Dict[str, Any]]):
        """V3: Dynamic strategy adjustment"""
        progress = iteration / max_iterations
        
        # Decay exploration
        self.exploration_rate *= 0.995
        
        # Adjust based on golden ratio progress
        if history and history[-1]['golden_ratio_error'] < 0.1:
            # Close to golden ratio - be more conservative
            self.exploration_rate *= 0.9
            self.gradient_clip *= 0.9
        
        # Late-stage fine-tuning
        if progress > 0.7:
            self.gradient_clip = min(self.gradient_clip, 1.0)
    
    def _analyze_progress_v3(self, history: List[Dict[str, Any]]):
        """V3: Enhanced progress analysis"""
        recent = history[-20:] if len(history) >= 20 else history
        
        recent_golden_errors = [h['golden_ratio_error'] for h in recent if h['golden_ratio_error'] < float('inf')]
        recent_improvements = [h['improvement'] for h in recent]
        
        print(f"\nV3 Progress Analysis:")
        print(f"  Golden discoveries: {len(self.golden_discoveries)}")
        if recent_golden_errors:
            print(f"  Recent best φ error: {min(recent_golden_errors):.6f}")
            print(f"  φ error trend: {'improving' if recent_golden_errors[-1] < recent_golden_errors[0] else 'stable'}")
        print(f"  Avg recent improvement: {np.mean(recent_improvements):.6f}")
        print(f"  Exploration rate: {self.exploration_rate:.4f}")
    
    def _store_bounded_pattern(self, result: Dict[str, Any]):
        """Store pattern with bounds"""
        bounded_score = np.clip(result['score'], -1e6, 1e6)
        
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
        
        self.patterns_used.add(result['symbol_hash'])


if __name__ == "__main__":
    # Test V3
    from meta_optimizer import example_objective_function
    
    print("Testing Enhanced Meta-Optimizer V3")
    print("=" * 50)
    
    optimizer = EnhancedMetaOptimizerV3()
    
    initial_state = {
        'frequency': 1.0,
        'vibration': 1.5,
        'energy': 0.9,
        'x0': 1.0,
        'x1': 1.6,
        'x2': 2.6,
        'x3': 4.2
    }
    
    problem_signature = {
        'type': 'golden_seeking',
        'dimensions': 7,
        'objective_type': 'fibonacci_optimizer'
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
    if result['golden_discovery_iteration'] is not None:
        print(f"First golden discovery at iteration: {result['golden_discovery_iteration']}")