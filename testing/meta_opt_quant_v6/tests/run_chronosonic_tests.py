#!/usr/bin/env python3
"""
CHRONOSONIC Test Runner
Executes all CHRONOSONIC-related tests and generates comprehensive reports
"""

import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime
import unittest
import tempfile
import subprocess

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "research" / "chronosonic_qualia"))

# Import test modules
from test_chronosonic_extended import run_extended_test_suite
from test_chronosonic_pipeline_integration import run_pipeline_integration_tests


class ChronosonicTestReport:
    """Generate comprehensive test reports for CHRONOSONIC"""
    
    def __init__(self):
        self.report_data = {
            'test_run_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'started_at': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'test_results': {},
            'metrics': {},
            'recommendations': []
        }
        
    def _get_system_info(self):
        """Get system information"""
        import platform
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'test_directory': str(Path.cwd())
        }
        
    def add_test_suite_results(self, suite_name: str, result: unittest.TestResult, duration: float):
        """Add test suite results to report"""
        self.report_data['test_results'][suite_name] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0,
            'duration_seconds': duration,
            'status': 'PASSED' if result.wasSuccessful() else 'FAILED'
        }
        
        # Add failure details if any
        if result.failures:
            self.report_data['test_results'][suite_name]['failure_details'] = [
                {
                    'test': str(test),
                    'traceback': traceback
                }
                for test, traceback in result.failures
            ]
            
        if result.errors:
            self.report_data['test_results'][suite_name]['error_details'] = [
                {
                    'test': str(test),
                    'traceback': traceback
                }
                for test, traceback in result.errors
            ]
            
    def calculate_overall_metrics(self):
        """Calculate overall test metrics"""
        total_tests = sum(r['tests_run'] for r in self.report_data['test_results'].values())
        total_failures = sum(r['failures'] for r in self.report_data['test_results'].values())
        total_errors = sum(r['errors'] for r in self.report_data['test_results'].values())
        total_duration = sum(r['duration_seconds'] for r in self.report_data['test_results'].values())
        
        self.report_data['metrics'] = {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'overall_success_rate': (total_tests - total_failures - total_errors) / total_tests * 100 if total_tests > 0 else 0,
            'total_duration_seconds': total_duration,
            'average_test_duration': total_duration / total_tests if total_tests > 0 else 0
        }
        
        # Check against pipeline criteria
        pipeline_criteria_met = {
            'frequency_accuracy': self.report_data['metrics']['overall_success_rate'] >= 95,
            'state_coherence': self.report_data['metrics']['overall_success_rate'] >= 90,
            'temporal_stability': total_errors == 0
        }
        
        self.report_data['pipeline_criteria_met'] = pipeline_criteria_met
        self.report_data['pipeline_ready'] = all(pipeline_criteria_met.values())
        
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check overall success rate
        if self.report_data['metrics']['overall_success_rate'] < 95:
            recommendations.append("Improve test coverage and fix failing tests to meet 95% success criteria")
            
        # Check for errors
        if self.report_data['metrics']['total_errors'] > 0:
            recommendations.append("Address critical errors before pipeline deployment")
            
        # Check specific test suites
        for suite_name, results in self.report_data['test_results'].items():
            if results['status'] == 'FAILED':
                recommendations.append(f"Fix issues in {suite_name} test suite")
                
        # Pipeline-specific recommendations
        if not self.report_data['pipeline_ready']:
            recommendations.append("Complete all pipeline readiness criteria before deployment")
        else:
            recommendations.append("System meets pipeline criteria - proceed with deployment preparation")
            
        self.report_data['recommendations'] = recommendations
        
    def save_report(self, output_dir: str = None):
        """Save test report to file"""
        if output_dir is None:
            output_dir = Path.cwd() / "test_reports"
            
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Add completion timestamp
        self.report_data['completed_at'] = datetime.now().isoformat()
        
        # Save JSON report
        report_file = output_dir / f"chronosonic_test_report_{self.report_data['test_run_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(self.report_data, f, indent=2, default=str)
            
        # Save human-readable summary
        summary_file = output_dir / f"chronosonic_test_summary_{self.report_data['test_run_id']}.txt"
        with open(summary_file, 'w') as f:
            f.write(self._generate_summary())
            
        return report_file, summary_file
        
    def _generate_summary(self) -> str:
        """Generate human-readable test summary"""
        summary = []
        summary.append("=" * 80)
        summary.append("CHRONOSONIC Test Summary")
        summary.append("=" * 80)
        summary.append(f"Test Run ID: {self.report_data['test_run_id']}")
        summary.append(f"Started: {self.report_data['started_at']}")
        summary.append(f"Completed: {self.report_data['completed_at']}")
        summary.append("")
        
        summary.append("Test Results:")
        summary.append("-" * 40)
        for suite_name, results in self.report_data['test_results'].items():
            summary.append(f"\n{suite_name}:")
            summary.append(f"  Status: {results['status']}")
            summary.append(f"  Tests Run: {results['tests_run']}")
            summary.append(f"  Failures: {results['failures']}")
            summary.append(f"  Errors: {results['errors']}")
            summary.append(f"  Success Rate: {results['success_rate']:.1f}%")
            summary.append(f"  Duration: {results['duration_seconds']:.2f}s")
            
        summary.append("")
        summary.append("Overall Metrics:")
        summary.append("-" * 40)
        metrics = self.report_data['metrics']
        summary.append(f"Total Tests: {metrics['total_tests']}")
        summary.append(f"Total Failures: {metrics['total_failures']}")
        summary.append(f"Total Errors: {metrics['total_errors']}")
        summary.append(f"Overall Success Rate: {metrics['overall_success_rate']:.1f}%")
        summary.append(f"Total Duration: {metrics['total_duration_seconds']:.2f}s")
        
        summary.append("")
        summary.append("Pipeline Readiness:")
        summary.append("-" * 40)
        for criterion, met in self.report_data['pipeline_criteria_met'].items():
            status = "✓ MET" if met else "✗ NOT MET"
            summary.append(f"{criterion}: {status}")
        summary.append(f"\nOverall Pipeline Ready: {'YES' if self.report_data['pipeline_ready'] else 'NO'}")
        
        summary.append("")
        summary.append("Recommendations:")
        summary.append("-" * 40)
        for i, rec in enumerate(self.report_data['recommendations'], 1):
            summary.append(f"{i}. {rec}")
            
        summary.append("")
        summary.append("=" * 80)
        
        return "\n".join(summary)


def run_all_chronosonic_tests():
    """Run all CHRONOSONIC test suites"""
    print("=" * 80)
    print("CHRONOSONIC Comprehensive Test Suite")
    print("=" * 80)
    print(f"Starting test run at: {datetime.now()}")
    print()
    
    # Create test report
    report = ChronosonicTestReport()
    
    # Test Suite 1: Extended Tests
    print("\n" + "-" * 80)
    print("Running Extended Test Suite...")
    print("-" * 80)
    
    start_time = time.time()
    extended_result = run_extended_test_suite()
    extended_duration = time.time() - start_time
    
    report.add_test_suite_results("Extended Tests", extended_result, extended_duration)
    
    # Test Suite 2: Pipeline Integration Tests
    print("\n" + "-" * 80)
    print("Running Pipeline Integration Tests...")
    print("-" * 80)
    
    start_time = time.time()
    pipeline_result = run_pipeline_integration_tests()
    pipeline_duration = time.time() - start_time
    
    report.add_test_suite_results("Pipeline Integration", pipeline_result, pipeline_duration)
    
    # Calculate overall metrics
    report.calculate_overall_metrics()
    report.generate_recommendations()
    
    # Save reports
    print("\n" + "-" * 80)
    print("Generating Test Reports...")
    print("-" * 80)
    
    json_report, summary_report = report.save_report()
    
    print(f"\nTest reports saved:")
    print(f"  JSON Report: {json_report}")
    print(f"  Summary Report: {summary_report}")
    
    # Display summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Overall Success Rate: {report.report_data['metrics']['overall_success_rate']:.1f}%")
    print(f"Pipeline Ready: {'YES' if report.report_data['pipeline_ready'] else 'NO'}")
    
    if report.report_data['recommendations']:
        print("\nKey Recommendations:")
        for rec in report.report_data['recommendations'][:3]:  # Show top 3
            print(f"  • {rec}")
            
    return report.report_data['pipeline_ready']


def run_specific_test_module(module_name: str):
    """Run a specific test module"""
    if module_name == "extended":
        return run_extended_test_suite()
    elif module_name == "pipeline":
        return run_pipeline_integration_tests()
    else:
        print(f"Unknown test module: {module_name}")
        print("Available modules: extended, pipeline")
        return None


def main():
    """Main entry point for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CHRONOSONIC Test Runner")
    parser.add_argument('--module', type=str, help='Run specific test module (extended, pipeline)')
    parser.add_argument('--quick', action='store_true', help='Run quick validation tests only')
    parser.add_argument('--report-only', action='store_true', help='Generate report from existing results')
    
    args = parser.parse_args()
    
    if args.module:
        # Run specific module
        result = run_specific_test_module(args.module)
        if result is not None:
            sys.exit(0 if result.wasSuccessful() else 1)
        else:
            sys.exit(1)
    elif args.quick:
        # Run quick validation
        print("Running quick validation tests...")
        # Import and run minimal tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add a subset of critical tests
        from test_chronosonic_extended import (
            TestChakraSystem, TestFrequencyModulatedIAMState,
            TestCognitivePerformanceMetrics
        )
        
        for test_class in [TestChakraSystem, TestFrequencyModulatedIAMState, TestCognitivePerformanceMetrics]:
            suite.addTests(loader.loadTestsFromTestCase(test_class))
            
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print(f"\nQuick validation: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # Run all tests
        pipeline_ready = run_all_chronosonic_tests()
        sys.exit(0 if pipeline_ready else 1)


if __name__ == "__main__":
    main()