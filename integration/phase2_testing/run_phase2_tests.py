#!/usr/bin/env python3
"""
Phase 2 Test Runner
==================

Coordinates and runs all Phase 2 tests with appropriate configurations.
Provides options for quick validation or full extended testing.

For Tenxsom AI integration validation.
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class Phase2TestRunner:
    """Coordinate Phase 2 testing"""
    
    def __init__(self, mode='quick'):
        self.mode = mode
        self.results = {
            'test_id': f'phase2_{mode}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'mode': mode,
            'tests': {},
            'summary': {}
        }
        
        # Test configurations
        if mode == 'quick':
            self.tests = [
                {
                    'name': '4-hour validation',
                    'script': 'extended_validation_4hour.py',
                    'args': ['--quick'],  # 20 minutes
                    'expected_duration': 20
                },
                {
                    'name': '8-hour stability',
                    'script': 'stability_test_8hour.py',
                    'args': ['--quick'],  # 30 minutes
                    'expected_duration': 30
                },
                {
                    'name': 'performance optimization',
                    'script': 'performance_optimizer.py',
                    'args': [],
                    'expected_duration': 5
                }
            ]
        else:  # full mode
            self.tests = [
                {
                    'name': '4-hour validation',
                    'script': 'extended_validation_4hour.py',
                    'args': [],
                    'expected_duration': 240
                },
                {
                    'name': '8-hour stability',
                    'script': 'stability_test_8hour.py',
                    'args': [],
                    'expected_duration': 480
                },
                {
                    'name': 'performance optimization',
                    'script': 'performance_optimizer.py',
                    'args': [],
                    'expected_duration': 10
                }
            ]
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("=" * 80)
        print("PHASE 2 EXTENDED TESTING & OPTIMIZATION")
        print("=" * 80)
        print(f"Mode: {self.mode.upper()}")
        print(f"Start time: {datetime.now()}")
        print(f"Total expected duration: {sum(t['expected_duration'] for t in self.tests)} minutes")
        print()
        
        start_time = time.time()
        
        for i, test in enumerate(self.tests):
            print(f"\n{'='*60}")
            print(f"Test {i+1}/{len(self.tests)}: {test['name']}")
            print(f"{'='*60}")
            
            test_result = self._run_single_test(test)
            self.results['tests'][test['name']] = test_result
            
            if not test_result['success']:
                print(f"\n⚠️ Test failed: {test['name']}")
                if self.mode != 'quick':
                    print("Continuing with remaining tests...")
        
        # Summary
        self._generate_summary()
        
        # Save results
        self._save_results()
        
        total_time = time.time() - start_time
        print(f"\nTotal runtime: {total_time/60:.1f} minutes")
    
    def _run_single_test(self, test: dict) -> dict:
        """Run a single test"""
        script_path = os.path.join(os.path.dirname(__file__), test['script'])
        
        print(f"Running: {test['script']}")
        print(f"Expected duration: {test['expected_duration']} minutes")
        
        start_time = time.time()
        
        try:
            # Build command
            cmd = [sys.executable, script_path] + test['args']
            
            # Run test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=test['expected_duration'] * 60 * 1.5  # 50% buffer
            )
            
            runtime = time.time() - start_time
            
            # Parse output for key metrics
            metrics = self._parse_test_output(result.stdout)
            
            return {
                'success': result.returncode == 0,
                'runtime': runtime,
                'return_code': result.returncode,
                'metrics': metrics,
                'errors': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'runtime': time.time() - start_time,
                'error': 'Test timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'runtime': time.time() - start_time,
                'error': str(e)
            }
    
    def _parse_test_output(self, output: str) -> dict:
        """Parse test output for key metrics"""
        metrics = {}
        
        # Look for common patterns
        lines = output.split('\n')
        for line in lines:
            # Success rate
            if 'Success Rate:' in line and '%' in line:
                try:
                    rate = float(line.split('(')[1].split('%')[0])
                    metrics['success_rate'] = rate
                except:
                    pass
            
            # Performance metrics
            if 'Average Speedup:' in line:
                try:
                    speedup = float(line.split(':')[1].split('x')[0].strip())
                    metrics['speedup'] = speedup
                except:
                    pass
            
            # Stability metrics
            if 'Total Errors:' in line:
                try:
                    errors = int(line.split(':')[1].strip())
                    metrics['total_errors'] = errors
                except:
                    pass
            
            # Memory metrics
            if 'Memory growth:' in line and 'MB' in line:
                try:
                    growth = float(line.split(':')[1].split('MB')[0].strip())
                    metrics['memory_growth_mb'] = growth
                except:
                    pass
        
        return metrics
    
    def _generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("PHASE 2 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for r in self.results['tests'].values() if r['success'])
        
        print(f"\nTests Passed: {passed_tests}/{total_tests}")
        
        # Individual test results
        print("\nTest Results:")
        for test_name, result in self.results['tests'].items():
            status = "PASS" if result['success'] else "FAIL"
            runtime = result['runtime'] / 60
            print(f"  {test_name}: {status} ({runtime:.1f} minutes)")
            
            # Key metrics
            if 'metrics' in result and result['metrics']:
                for metric, value in result['metrics'].items():
                    print(f"    - {metric}: {value}")
        
        # Overall assessment
        validation_passed = self.results['tests'].get('4-hour validation', {}).get('success', False)
        stability_passed = self.results['tests'].get('8-hour stability', {}).get('success', False)
        perf_passed = self.results['tests'].get('performance optimization', {}).get('success', False)
        
        print("\nPhase 2 Criteria:")
        print(f"  Extended Validation: {'PASS' if validation_passed else 'FAIL'}")
        print(f"  System Stability: {'PASS' if stability_passed else 'FAIL'}")
        print(f"  Performance Optimization: {'PASS' if perf_passed else 'FAIL'}")
        
        all_passed = validation_passed and stability_passed and perf_passed
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'validation_passed': validation_passed,
            'stability_passed': stability_passed,
            'performance_passed': perf_passed,
            'phase2_complete': all_passed
        }
        
        if all_passed:
            print("\n✅ PHASE 2 COMPLETE!")
            print("The META-CHRONOSONIC integration has passed all extended tests.")
            print("Ready for Phase 3: FA-CMS Integration")
        else:
            print("\n⚠️ PHASE 2 INCOMPLETE")
            print("Review failed tests before proceeding.")
    
    def _save_results(self):
        """Save test results"""
        filename = f"phase2_results_{self.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {filename}")


def run_quick_validation():
    """Run a quick validation of Phase 2 components"""
    print("Quick Phase 2 Validation")
    print("=" * 60)
    
    # Just verify imports and basic functionality
    try:
        from extended_validation_4hour import ExtendedValidationTest
        print("✓ 4-hour validation module loaded")
        
        from stability_test_8hour import StabilityTest8Hour
        print("✓ 8-hour stability module loaded")
        
        from performance_optimizer import PerformanceOptimizer
        print("✓ Performance optimizer module loaded")
        
        # Quick integration test
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from meta_chronosonic_bridge import MetaChronosonicBridge, IntegrationConfig
        
        config = IntegrationConfig(v6_max_iterations=5)
        bridge = MetaChronosonicBridge(config)
        
        def simple_obj(params):
            return sum(v**2 for v in params.values())
        
        initial = {'x': 1.0, 'y': 2.0}
        best, scores = bridge.optimize_integrated(simple_obj, initial, max_iterations=5)
        
        print("✓ Integration bridge functional")
        print(f"  Optimization improvement: {(scores[0]-scores[-1])/scores[0]*100:.1f}%")
        
        print("\n✅ All Phase 2 components are functional!")
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Phase 2 Test Runner')
    parser.add_argument('--mode', choices=['quick', 'full', 'validate'], 
                       default='validate',
                       help='Test mode (default: validate)')
    
    args = parser.parse_args()
    
    if args.mode == 'validate':
        # Just validate components
        success = run_quick_validation()
        return 0 if success else 1
    else:
        # Run full test suite
        runner = Phase2TestRunner(mode=args.mode)
        runner.run_all_tests()
        
        return 0 if runner.results['summary'].get('phase2_complete', False) else 1


if __name__ == "__main__":
    sys.exit(main())