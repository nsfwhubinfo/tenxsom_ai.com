"""
Chronosonic Qualia Research Module
CSQ.1.2 Implementation - Simplified 2-3 chakra model with frequency-modulated <I_AM> state dynamics
"""

from .chronosonic_prototype import (
    ChakraType,
    ChakraState,
    SimplifiedChakraSystem,
    FrequencyModulatedIAMState,
    ChronosonicDynamics,
    ComplexIAMFractalAnalyzer,
    CognitivePerformanceMetrics
)

from .chronosonic_visualizer import (
    ChronosonicVisualizer,
    SpectrumAnalyzer
)

from .chronosonic_experiments import (
    FrequencyPattern,
    ChronosonicExperiment,
    FrequencyPatternExperiment,
    CognitivePerformanceComparison,
    FractalSignatureAnalysis,
    EmpiricalValidationProtocol,
    run_example_experiments
)

__version__ = "0.1.0"
__author__ = "Tenxsom AI Research"

__all__ = [
    # Core components
    "ChakraType",
    "ChakraState",
    "SimplifiedChakraSystem",
    "FrequencyModulatedIAMState",
    "ChronosonicDynamics",
    "ComplexIAMFractalAnalyzer",
    "CognitivePerformanceMetrics",
    
    # Visualization
    "ChronosonicVisualizer",
    "SpectrumAnalyzer",
    
    # Experiments
    "FrequencyPattern",
    "ChronosonicExperiment",
    "FrequencyPatternExperiment",
    "CognitivePerformanceComparison",
    "FractalSignatureAnalysis",
    "EmpiricalValidationProtocol",
    "run_example_experiments"
]