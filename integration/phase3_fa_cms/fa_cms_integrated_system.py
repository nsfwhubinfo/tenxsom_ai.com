#!/usr/bin/env python3
"""
FA-CMS Integrated System
========================

Complete integration of:
- META-OPT-QUANT V6.1 (optimization)
- CHRONOSONIC V2 (consciousness dynamics)
- Fractal Consciousness Engine (fractal analysis)

Provides a unified consciousness modeling and optimization framework
with plugin architecture for extensibility.

For Tenxsom AI's production deployment.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import time
import json
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fa_plugin_interface import (
    PluginManager,
    PluginConfig,
    UnifiedState,
    ChakraState,
    FAMessage,
    MessageType
)

from meta_chronosonic_plugin import (
    MetaChronosonicPlugin,
    SevenChakraExtension
)

from fractal_consciousness_engine import (
    FractalConsciousnessPlugin
)


class FACMSIntegratedSystem:
    """Complete FA-CMS integrated system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.plugin_manager = PluginManager()
        self.plugins_initialized = False
        self.processing_history = []
        self.start_time = time.time()
        
        # Performance monitoring
        self.performance_metrics = {
            'total_states_processed': 0,
            'total_processing_time': 0.0,
            'plugin_execution_times': {},
            'error_count': 0
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """Default system configuration"""
        return {
            'enable_meta_chronosonic': True,
            'enable_fractal_engine': True,
            'enable_7_chakra': True,
            'optimization_interval': 1.0,
            'target_fractal_dimension': 1.618,  # φ
            'plugin_priorities': {
                'meta_chronosonic': 8,
                'fractal_consciousness': 7
            }
        }
    
    def initialize(self) -> bool:
        """Initialize the FA-CMS system"""
        print("=" * 70)
        print("FA-CMS INTEGRATED SYSTEM INITIALIZATION")
        print("=" * 70)
        print(f"Timestamp: {datetime.now()}")
        print()
        
        try:
            # Start plugin manager
            self.plugin_manager.start()
            
            # Initialize META-CHRONOSONIC plugin
            if self.config['enable_meta_chronosonic']:
                mc_config = PluginConfig(
                    name="META-CHRONOSONIC",
                    version="1.0.0",
                    priority=self.config['plugin_priorities']['meta_chronosonic'],
                    custom_params={
                        'enable_7_chakra': self.config['enable_7_chakra']
                    }
                )
                
                mc_plugin = MetaChronosonicPlugin(mc_config)
                if self.plugin_manager.register_plugin(mc_plugin):
                    print("✓ META-CHRONOSONIC plugin registered")
                else:
                    print("✗ Failed to register META-CHRONOSONIC plugin")
                    return False
            
            # Initialize Fractal Consciousness plugin
            if self.config['enable_fractal_engine']:
                fc_config = PluginConfig(
                    name="FractalConsciousness",
                    version="1.0.0",
                    priority=self.config['plugin_priorities']['fractal_consciousness'],
                    custom_params={
                        'target_dimension': self.config['target_fractal_dimension'],
                        'enhance_fractality': True,
                        'multiscale_analysis': True
                    }
                )
                
                fc_plugin = FractalConsciousnessPlugin(fc_config)
                if self.plugin_manager.register_plugin(fc_plugin):
                    print("✓ Fractal Consciousness plugin registered")
                else:
                    print("✗ Failed to register Fractal Consciousness plugin")
                    return False
            
            self.plugins_initialized = True
            print("\n✅ FA-CMS system initialized successfully!")
            print(f"Active plugins: {len(self.plugin_manager.plugins)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            return False
    
    def create_initial_state(self, n_params: int = 12) -> UnifiedState:
        """Create initial unified state"""
        # Create optimization parameters
        optimization_params = {
            f'param_{i}': 1.0 + i * 0.1 
            for i in range(n_params)
        }
        
        # Create chakra states
        if self.config['enable_7_chakra']:
            chakra_states = SevenChakraExtension.create_full_chakra_states()
        else:
            # Simplified 3-chakra system
            chakra_states = [
                ChakraState(type="root", frequency=256.0, amplitude=0.5, 
                           phase=0.0, coherence=0.7),
                ChakraState(type="heart", frequency=341.3, amplitude=0.6, 
                           phase=np.pi/3, coherence=0.8),
                ChakraState(type="crown", frequency=512.0, amplitude=0.5, 
                           phase=2*np.pi/3, coherence=0.75)
            ]
        
        # Create unified state
        state = UnifiedState(
            optimization_params=optimization_params,
            chakra_states=chakra_states,
            fractal_dimension=1.5,  # Initial estimate
            metadata={
                'created_at': time.time(),
                'system': 'FA-CMS',
                'version': '1.0.0'
            }
        )
        
        return state
    
    def process_state(self, state: UnifiedState, 
                     iterations: int = 1) -> Tuple[UnifiedState, Dict[str, Any]]:
        """Process state through the FA-CMS system"""
        if not self.plugins_initialized:
            raise RuntimeError("System not initialized")
        
        print(f"\nProcessing state through FA-CMS...")
        print(f"  State ID: {state.id}")
        print(f"  Parameters: {len(state.optimization_params)}")
        print(f"  Chakras: {len(state.chakra_states)}")
        
        results = {
            'initial_state_id': state.id,
            'iterations': [],
            'final_state_id': None,
            'total_time': 0.0,
            'improvements': {}
        }
        
        start_time = time.time()
        
        for iteration in range(iterations):
            iter_start = time.time()
            
            print(f"\n  Iteration {iteration + 1}/{iterations}")
            
            # Process through plugin chain
            try:
                processed_state = self.plugin_manager.process_state(state)
                
                # Calculate improvements
                improvements = self._calculate_improvements(state, processed_state)
                
                # Record iteration results
                iter_results = {
                    'iteration': iteration + 1,
                    'processing_time': time.time() - iter_start,
                    'improvements': improvements,
                    'plugin_metrics': self._get_plugin_metrics()
                }
                
                results['iterations'].append(iter_results)
                
                # Update state for next iteration
                state = processed_state
                
                # Update performance metrics
                self.performance_metrics['total_states_processed'] += 1
                self.performance_metrics['total_processing_time'] += iter_results['processing_time']
                
                # Display progress
                print(f"    Processing time: {iter_results['processing_time']:.2f}s")
                
                if 'meta_chronosonic' in processed_state.metadata:
                    mc_data = processed_state.metadata['meta_chronosonic']
                    print(f"    Optimization improvement: {mc_data.get('optimization_improvement', 0):.1f}%")
                    print(f"    φ discovery: {mc_data.get('phi_discovery', 0):.1f}%")
                
                if 'fractal_metrics' in processed_state.metadata:
                    fm_data = processed_state.metadata['fractal_metrics']
                    print(f"    Fractal dimension: {fm_data.get('dimension', 0):.3f}")
                
            except Exception as e:
                print(f"    ❌ Error in iteration {iteration + 1}: {e}")
                self.performance_metrics['error_count'] += 1
                results['iterations'].append({
                    'iteration': iteration + 1,
                    'error': str(e)
                })
        
        # Final results
        results['final_state_id'] = state.id
        results['total_time'] = time.time() - start_time
        
        # Calculate overall improvements
        results['improvements'] = self._calculate_overall_improvements(results)
        
        # Add to processing history
        self.processing_history.append(results)
        
        return state, results
    
    def run_optimization_cycle(self, 
                              initial_state: Optional[UnifiedState] = None,
                              cycles: int = 5,
                              iterations_per_cycle: int = 10) -> Dict[str, Any]:
        """Run complete optimization cycle"""
        print("\n" + "=" * 70)
        print("FA-CMS OPTIMIZATION CYCLE")
        print("=" * 70)
        print(f"Cycles: {cycles}")
        print(f"Iterations per cycle: {iterations_per_cycle}")
        
        # Create initial state if not provided
        if initial_state is None:
            initial_state = self.create_initial_state()
        
        cycle_results = {
            'start_time': datetime.now().isoformat(),
            'cycles': [],
            'overall_metrics': {}
        }
        
        current_state = initial_state
        
        for cycle in range(cycles):
            print(f"\n{'='*50}")
            print(f"CYCLE {cycle + 1}/{cycles}")
            print(f"{'='*50}")
            
            cycle_start = time.time()
            
            # Process state
            final_state, results = self.process_state(
                current_state, 
                iterations=iterations_per_cycle
            )
            
            # Save cycle results
            cycle_data = {
                'cycle': cycle + 1,
                'duration': time.time() - cycle_start,
                'initial_state_id': current_state.id,
                'final_state_id': final_state.id,
                'iterations': results['iterations'],
                'improvements': results['improvements']
            }
            
            cycle_results['cycles'].append(cycle_data)
            
            # Display cycle summary
            self._display_cycle_summary(cycle_data)
            
            # Prepare for next cycle
            current_state = final_state
            
            # Brief pause between cycles
            time.sleep(0.5)
        
        # Calculate overall metrics
        cycle_results['overall_metrics'] = self._calculate_overall_metrics(cycle_results)
        cycle_results['end_time'] = datetime.now().isoformat()
        
        # Display final summary
        self._display_final_summary(cycle_results)
        
        return cycle_results
    
    def _calculate_improvements(self, 
                               initial: UnifiedState, 
                               final: UnifiedState) -> Dict[str, float]:
        """Calculate improvements between states"""
        improvements = {}
        
        # Fractal dimension improvement (closer to target)
        target_dim = self.config['target_fractal_dimension']
        initial_error = abs(initial.fractal_dimension - target_dim)
        final_error = abs(final.fractal_dimension - target_dim)
        improvements['fractal_dimension'] = (initial_error - final_error) / (initial_error + 1e-10) * 100
        
        # Average chakra coherence
        if initial.chakra_states and final.chakra_states:
            initial_coherence = np.mean([c.coherence for c in initial.chakra_states])
            final_coherence = np.mean([c.coherence for c in final.chakra_states])
            improvements['chakra_coherence'] = (final_coherence - initial_coherence) / (initial_coherence + 1e-10) * 100
        
        return improvements
    
    def _calculate_overall_improvements(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall improvements from iteration results"""
        overall = {}
        
        # Aggregate from all iterations
        all_improvements = []
        for iter_data in results['iterations']:
            if 'improvements' in iter_data and iter_data['improvements']:
                all_improvements.append(iter_data['improvements'])
        
        if all_improvements:
            # Average improvements
            keys = all_improvements[0].keys()
            for key in keys:
                values = [imp.get(key, 0) for imp in all_improvements]
                overall[key] = np.mean(values)
        
        return overall
    
    def _get_plugin_metrics(self) -> Dict[str, Any]:
        """Get current plugin metrics"""
        metrics = {}
        
        for plugin_id, plugin in self.plugin_manager.plugins.items():
            plugin_info = plugin.get_info()
            metrics[plugin_info['name']] = {
                'status': plugin_info['status'],
                'processed_count': plugin_info['metrics']['processed_count'],
                'error_count': plugin_info['metrics']['error_count']
            }
        
        return metrics
    
    def _calculate_overall_metrics(self, cycle_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics across all cycles"""
        metrics = {
            'total_duration': sum(c['duration'] for c in cycle_results['cycles']),
            'avg_cycle_duration': np.mean([c['duration'] for c in cycle_results['cycles']]),
            'total_iterations': sum(len(c['iterations']) for c in cycle_results['cycles']),
            'convergence_profile': []
        }
        
        # Extract convergence profile
        for cycle in cycle_results['cycles']:
            for iteration in cycle['iterations']:
                if 'improvements' in iteration:
                    metrics['convergence_profile'].append(iteration['improvements'])
        
        return metrics
    
    def _display_cycle_summary(self, cycle_data: Dict[str, Any]):
        """Display cycle summary"""
        print(f"\nCycle {cycle_data['cycle']} Summary:")
        print(f"  Duration: {cycle_data['duration']:.1f}s")
        
        if cycle_data['improvements']:
            print("  Improvements:")
            for metric, value in cycle_data['improvements'].items():
                print(f"    {metric}: {value:+.1f}%")
    
    def _display_final_summary(self, results: Dict[str, Any]):
        """Display final optimization summary"""
        print("\n" + "=" * 70)
        print("OPTIMIZATION SUMMARY")
        print("=" * 70)
        
        metrics = results['overall_metrics']
        print(f"\nTotal duration: {metrics['total_duration']:.1f}s")
        print(f"Total iterations: {metrics['total_iterations']}")
        print(f"Average cycle time: {metrics['avg_cycle_duration']:.1f}s")
        
        # System status
        system_status = self.plugin_manager.get_system_status()
        print(f"\nSystem Status:")
        print(f"  Active plugins: {system_status['plugin_count']}")
        print(f"  Total states processed: {self.performance_metrics['total_states_processed']}")
        print(f"  Total errors: {self.performance_metrics['error_count']}")
        
        # Plugin performance
        print(f"\nPlugin Performance:")
        for plugin_id, plugin_info in system_status['plugins'].items():
            name = plugin_info['name']
            metrics = plugin_info['metrics']
            print(f"  {name}:")
            print(f"    Processed: {metrics['processed_count']}")
            print(f"    Errors: {metrics['error_count']}")
            print(f"    Avg time: {metrics['last_processing_time']:.3f}s")
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"fa_cms_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert numpy arrays and other non-serializable types
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(v) for v in obj]
            return obj
        
        results_json = convert_for_json(results)
        
        with open(filename, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    def shutdown(self):
        """Shutdown the FA-CMS system"""
        print("\nShutting down FA-CMS system...")
        self.plugin_manager.stop()
        print("✓ FA-CMS shutdown complete")


def demo_fa_cms_system():
    """Demonstrate the complete FA-CMS integrated system"""
    print("FA-CMS INTEGRATED SYSTEM DEMO")
    print("=" * 70)
    
    # Create system
    system = FACMSIntegratedSystem()
    
    # Initialize
    if not system.initialize():
        print("Failed to initialize system!")
        return
    
    # Run optimization cycle
    results = system.run_optimization_cycle(
        cycles=3,
        iterations_per_cycle=5
    )
    
    # Save results
    system.save_results(results)
    
    # Shutdown
    system.shutdown()
    
    print("\n✅ FA-CMS demo complete!")


if __name__ == "__main__":
    demo_fa_cms_system()