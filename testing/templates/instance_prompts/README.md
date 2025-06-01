# Instance Prompts for Autonomous Testing

This directory contains ready-to-use prompts for launching separate Claude Code instances to run different test configurations in parallel.

## Available Test Prompts

### 1. Compression Efficiency Test (`PROMPT_1_COMPRESSION_TEST.md`)
- **Duration**: 12 hours
- **Focus**: Maximum compression ratios, symmetry detection
- **Target**: 30x compression (stretch: 48x)
- **Key Metrics**: Compression ratio, symmetry detection, encoding efficiency

### 2. Memory Optimization Test (`PROMPT_2_MEMORY_TEST.md`)
- **Duration**: 6 hours
- **Focus**: Cache efficiency, memory reduction
- **Target**: 85% cache hit rate with 200MB limit
- **Key Metrics**: Hit rate, memory usage, retrieval speed

### 3. Speed Performance Test (`PROMPT_3_SPEED_TEST.md`)
- **Duration**: 4 hours
- **Focus**: SIMD operations, parallel processing
- **Target**: 3x speedup (stretch: 5x)
- **Key Metrics**: SIMD speedup, throughput, latency

### 4. Patent Demonstration Test (`PROMPT_4_PATENT_TEST.md`)
- **Duration**: 8 hours
- **Focus**: Validating all patent claims
- **Target**: 100% φ discovery, claim validation
- **Key Metrics**: Patent claim scores, innovation validation

### 5. Quick CI/CD Validation (`PROMPT_5_QUICK_CICD_TEST.md`)
- **Duration**: 1 hour
- **Focus**: Basic functionality, stability
- **Target**: No crashes, baseline performance
- **Key Metrics**: Success rate, basic φ discovery

## How to Use

1. **Open a new Claude Code instance**

2. **Copy the entire content of the desired prompt file**

3. **Paste it into the new Claude Code instance**

4. **The instance will:**
   - Create the necessary test implementation
   - Set up the autonomous test orchestrator
   - Launch the test to run unattended
   - Generate results and reports

## Running Multiple Tests

To run all 5 tests simultaneously:

1. Open 5 separate Claude Code instances
2. Give each instance its respective prompt
3. All tests will run in parallel without interference
4. Each generates its own database and reports

## Expected Outputs

Each test produces:
- `{test_name}.db` - SQLite database with results
- `{test_name}.log` - Detailed execution log
- `{test_name}_report.json` - Final summary report
- `{test_name}_output.log` - Console output (if backgrounded)

## Monitoring Progress

From any terminal, you can monitor a test:

```bash
# View real-time log
tail -f compression_efficiency_test.log

# Check database
sqlite3 compression_efficiency_test.db "SELECT COUNT(*) FROM test_results;"

# View output (if using nohup)
tail -f compression_test_output.log
```

## Results Collection

After tests complete, collect all reports:

```bash
# Create results directory
mkdir test_results_collection

# Copy all reports
cp *_test_report.json test_results_collection/

# Copy all databases
cp *_test.db test_results_collection/
```

## Test Comparison

| Test | Duration | Focus | Key Target |
|------|----------|-------|------------|
| Compression | 12h | Symmetry & compression | 30x ratio |
| Memory | 6h | Cache efficiency | 85% hit rate |
| Speed | 4h | SIMD performance | 3x speedup |
| Patent | 8h | Claim validation | 100% validation |
| CI/CD | 1h | Quick validation | No crashes |

## Notes

- All tests use the same autonomous framework
- Each test is self-contained and independent
- Tests automatically checkpoint for recovery
- Results are saved continuously
- No manual intervention required

## Troubleshooting

If a test fails to start:
1. Check the error in the output log
2. Verify all imports are correct
3. Ensure sufficient disk space
4. Check system resources

For test-specific issues, refer to the individual prompt files which contain expected results and monitoring instructions.