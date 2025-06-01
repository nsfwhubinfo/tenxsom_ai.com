"""
CHRONOSONIC Extended Test Suite
Comprehensive testing for the CHRONOSONIC Qualia prototype implementation
"""

from .test_chronosonic_extended import (
    TestChakraSystem,
    TestFrequencyModulatedIAMState,
    TestChronosonicDynamics,
    TestCognitivePerformanceMetrics,
    TestFrequencyPatterns,
    TestEmpiricalValidation,
    TestIntegrationScenarios,
    TestPerformanceOptimization,
    TestErrorHandling,
    TestDataPersistence,
    run_extended_test_suite
)

from .test_chronosonic_pipeline_integration import (
    TestChronosonicPipelineIntegration,
    TestChronosonicMetricsIntegration,
    TestChronosonicDeploymentReadiness,
    TestChronosonicScalingPaths,
    TestChronosonicValidationProtocols,
    run_pipeline_integration_tests
)

from .test_chronosonic_empirical_validation import (
    TestEmpiricalSuccessCriteria,
    TestValidationProtocolExecution,
    TestLongDurationValidation,
    TestValidationReporting,
    TestValidationVisualization,
    run_empirical_validation_suite
)

__all__ = [
    # Extended tests
    'TestChakraSystem',
    'TestFrequencyModulatedIAMState',
    'TestChronosonicDynamics',
    'TestCognitivePerformanceMetrics',
    'TestFrequencyPatterns',
    'TestEmpiricalValidation',
    'TestIntegrationScenarios',
    'TestPerformanceOptimization',
    'TestErrorHandling',
    'TestDataPersistence',
    'run_extended_test_suite',
    
    # Pipeline integration tests
    'TestChronosonicPipelineIntegration',
    'TestChronosonicMetricsIntegration',
    'TestChronosonicDeploymentReadiness',
    'TestChronosonicScalingPaths',
    'TestChronosonicValidationProtocols',
    'run_pipeline_integration_tests',
    
    # Empirical validation tests
    'TestEmpiricalSuccessCriteria',
    'TestValidationProtocolExecution',
    'TestLongDurationValidation',
    'TestValidationReporting',
    'TestValidationVisualization',
    'run_empirical_validation_suite',
]

# Version info
__version__ = '1.0.0'
__author__ = 'CHRONOSONIC Development Team'
__description__ = 'Extended test suite for CHRONOSONIC Qualia prototype'