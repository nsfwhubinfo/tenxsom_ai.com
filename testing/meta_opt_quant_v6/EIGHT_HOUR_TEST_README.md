# 8-Hour Continuous Test Suite for META-OPT-QUANT V6

## Overview
This test suite is designed to run continuously for 8 hours, testing diverse quality datasets and following optimization paths to push the system toward and beyond efficiency targets.

## Pre-Launch Checklist ✓

### Environment Verified
- [x] Python 3.12 compatible
- [x] All V6 components accessible
- [x] 946.5 GB disk space available (10 GB required)
- [x] Write permissions verified
- [x] Output directories created
- [x] Fallback implementations in place
- [x] Configuration file generated

### Resource Requirements
- **CPU**: 60-80% utilization across multiple cores
- **Memory**: Up to 4 GB RAM
- **Disk**: 10 GB free space
- **Time**: 8 hours uninterrupted operation

## Launch Instructions

### Method 1: Using Launch Script (Recommended)
```bash
cd /home/golde/Tenxsom_AI/testing/meta_opt_quant_v6
./launch_eight_hour_test.sh
```

### Method 2: Direct Python Execution
```bash
cd /home/golde/Tenxsom_AI/testing/meta_opt_quant_v6
python3 eight_hour_test_suite.py
```

### Method 3: Background Execution with nohup
```bash
cd /home/golde/Tenxsom_AI/testing/meta_opt_quant_v6
nohup python3 eight_hour_test_suite.py > test_output.log 2>&1 &
```

## Test Configuration

The test is configured via `eight_hour_test_config.json`:
- **Duration**: 8 hours
- **Checkpoints**: Every 30 minutes
- **Dataset batches**: 100 problems per batch
- **Difficulty scaling**: Progressive increase
- **Parallel workers**: 4 (or CPU count)
- **Memory limit**: 500 MB for cache

## Monitoring Progress

### Real-time Logs
```bash
tail -f eight_hour_test.log
```

### Database Queries
```bash
sqlite3 eight_hour_test_results.db "SELECT COUNT(*) FROM test_results;"
```

### System Metrics
Check `system_metrics` table for efficiency tracking.

## Recovery from Interruption

The test suite automatically saves checkpoints every 30 minutes. If interrupted:

1. The test will automatically resume from the last checkpoint
2. No data will be lost
3. Progress continues from where it left off

## Expected Outcomes

### Dataset Coverage
- 50,000-100,000 optimization problems
- 6 problem types: sphere, rosenbrock, rastrigin, golden_ratio, symmetry, mixed
- Progressive difficulty from 0.0 to 1.0
- Dimension variations: 6, 12, 24, 36, 48, 60, 72, 96

### Target Metrics
- **Compression**: 15-20x (currently 6.7x average, 54.9x best)
- **Memory Efficiency**: 80%+ hit rate with 80% reduction
- **Speed**: 2.7x improvement
- **φ Discovery**: 100% maintained
- **Overall Efficiency**: 85%+ target

### Output Files
1. `eight_hour_test_results.db` - Main results database
2. `eight_hour_test.log` - Detailed execution log
3. `checkpoints/` - Recovery checkpoints
4. `test_results/` - Additional test artifacts
5. `cache_data/` - LRU managed cache
6. Final report JSON with comprehensive analysis

## Permissions Required

The test needs the following permissions to run uninterrupted:

1. **File System**
   - Read: `/home/golde/Tenxsom_AI/research/meta_opt_quant/`
   - Write: `/home/golde/Tenxsom_AI/testing/meta_opt_quant_v6/`
   - Create/modify: Database files, log files, checkpoints

2. **System Resources**
   - CPU: Up to 80% utilization
   - Memory: Up to 4 GB allocation
   - Process: Create threads and subprocesses

3. **Time**
   - 8 hours continuous execution
   - No sleep/hibernation during test

## Emergency Stop

To stop the test gracefully:
```bash
# Find process ID
ps aux | grep eight_hour_test_suite.py

# Send interrupt signal
kill -INT <process_id>
```

The test will complete current batch and save checkpoint before exiting.

## Post-Test Analysis

After completion, a comprehensive report will be generated:
- `eight_hour_test_report_YYYYMMDD_HHMMSS.json`

This includes:
- Total tests completed
- Success rates by problem type
- Average improvements
- φ discovery statistics
- Compression achievements
- System efficiency metrics

## Troubleshooting

### If test doesn't start
- Check `setup_test_environment.py` output
- Verify Python path is correct
- Ensure no permission issues

### If test stops early
- Check error count in logs (max 100 errors)
- Review `eight_hour_test.log` for issues
- Verify disk space available

### If performance is poor
- Check system load with `top` or `htop`
- Ensure no other intensive processes running
- Verify configuration parameters

## Ready to Launch?

All systems are GO for the 8-hour test. The environment has been validated and all dependencies are in place. The test will run autonomously without requiring any intervention.

**Launch Command**: `./launch_eight_hour_test.sh`

Good luck! The test will push META-OPT-QUANT V6 toward its full potential.