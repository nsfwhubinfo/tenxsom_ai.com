# Autonomous Test Framework Templates

## Overview

This directory contains reusable templates for creating autonomous, long-running test suites for proof-of-concept validation and performance measurement. The framework is designed to run unattended for hours or days while collecting comprehensive metrics.

## Core Components

### 1. `autonomous_test_framework_template.py`
The main framework template with:
- **TestConfiguration**: Configurable attributes for different testing goals
- **Abstract base classes**: For dataset generation, system testing, and metrics
- **AutonomousTestOrchestrator**: Main test execution engine
- **Factory functions**: For common test scenarios

### 2. `test_configuration_examples.py`
Pre-configured test scenarios:
- **Golden Ratio Optimization** (8h): Focus on φ discovery
- **Compression Efficiency** (12h): Maximum compression testing
- **Memory Optimization** (6h): Cache efficiency
- **Speed Performance** (4h): SIMD and parallelization
- **Reliability Stress** (24h): Error handling and recovery
- **Full Integration** (48h): Comprehensive system test
- **Quick Validation** (1h): CI/CD pipeline test
- **Patent Demonstration** (8h): Patent claim validation

## Key Features

### Autonomous Operation
- Runs unattended for specified duration
- Automatic checkpointing and recovery
- Self-contained with all dependencies
- Progress logging and monitoring

### Configurable Testing
- Dataset types and generation
- Performance targets (min/target/stretch)
- Resource limits (CPU, memory)
- Custom metrics and validators

### Comprehensive Metrics
- Real-time performance tracking
- Target progress monitoring
- System resource usage
- Custom domain-specific metrics

### Robust Error Handling
- Graceful error recovery
- Checkpoint-based resumption
- Error threshold management
- Detailed error logging

## Usage Example

```python
from test_configuration_examples import get_test_configuration
from autonomous_test_framework_template import (
    AutonomousTestOrchestrator,
    ExampleDatasetGenerator
)

# Get pre-configured test
config = get_test_configuration('golden_ratio')

# Or customize your own
config = TestConfiguration()
config.test_duration_hours = 12.0
config.targets['compression_ratio']['target'] = 20.0

# Create components
dataset_gen = YourDatasetGenerator()
system = YourSystemUnderTest()
metrics = YourMetricsCollector()

# Run test
orchestrator = AutonomousTestOrchestrator(
    config, dataset_gen, system, metrics
)
orchestrator.run()
```

## Creating Custom Tests

### 1. Define Configuration
```python
class MyCustomTest(TestConfiguration):
    def __init__(self):
        super().__init__()
        self.test_duration_hours = 6.0
        self.dataset_types = ["custom_type_1", "custom_type_2"]
        self.targets = {
            'my_metric': {'min': 80.0, 'target': 90.0, 'stretch': 95.0}
        }
```

### 2. Implement Dataset Generator
```python
class MyDatasetGenerator(DatasetGenerator):
    def generate_problem(self, problem_type, dimensions, difficulty):
        # Generate test problem
        return problem_dict
```

### 3. Implement System Interface
```python
class MySystem(SystemUnderTest):
    def optimize(self, problem):
        # Run optimization
        return result_dict
```

### 4. Launch Test
```python
config = MyCustomTest()
orchestrator = AutonomousTestOrchestrator(config, ...)
orchestrator.run()
```

## Output Files

Each test generates:
- `{test_name}.db` - SQLite database with all results
- `{test_name}.log` - Detailed execution log
- `{test_name}_report.json` - Final summary report
- `checkpoints/` - Recovery checkpoints

## Best Practices

### 1. Resource Planning
- Estimate disk space: ~1-2 GB per million tests
- Memory usage: Configure based on system capacity
- CPU usage: Leave headroom for system processes

### 2. Target Setting
- **Min**: Absolute minimum acceptable
- **Target**: Expected achievement
- **Stretch**: Best-case scenario

### 3. Dataset Design
- Start with easier problems
- Gradually increase difficulty
- Include edge cases
- Balance problem types

### 4. Monitoring
- Check logs periodically: `tail -f test.log`
- Query database for progress
- Monitor system resources
- Set up alerts for failures

## Database Schema

### test_results
- Core test results and metadata
- Custom fields based on configuration
- Success/failure tracking
- Error messages

### system_metrics
- Time-series performance data
- Resource utilization
- Efficiency metrics
- Custom measurements

### checkpoints
- Recovery state information
- Progress snapshots
- Configuration backup
- Resumption data

## Extending the Framework

The framework is designed for extension:

1. **Custom Metrics**: Add to `custom_metrics` dict
2. **New Problem Types**: Extend dataset generator
3. **Validators**: Add to `custom_validators` list
4. **Visualizations**: Set `generate_visualizations = True`
5. **Reports**: Override `_generate_final_report()`

## Performance Tips

1. **Batch Processing**: Adjust `batch_size` for efficiency
2. **Parallelization**: Set `parallel_workers` appropriately
3. **Checkpointing**: Balance frequency vs overhead
4. **Memory Management**: Use LRU caching for large datasets
5. **Database Optimization**: Index frequently queried fields

## Troubleshooting

### Test Won't Start
- Check Python version (3.8+)
- Verify all imports
- Check write permissions

### Poor Performance
- Reduce parallel workers
- Increase batch size
- Check system resources

### High Error Rate
- Review error logs
- Adjust error threshold
- Check dataset validity

### Recovery Issues
- Verify checkpoint integrity
- Check database corruption
- Review checkpoint interval

## Future Enhancements

Planned improvements:
- Distributed testing support
- Real-time dashboard
- Cloud integration
- A/B testing framework
- ML-based target adjustment

---

This framework provides a solid foundation for autonomous testing across different proof-of-concept scenarios. Customize it to meet your specific validation needs.