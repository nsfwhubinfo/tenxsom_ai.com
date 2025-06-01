#!/bin/bash
# Launch script for 8-hour continuous test

echo "META-OPT-QUANT V6 8-Hour Test Launcher"
echo "======================================"
echo "Start time: $(date)"
echo

# Change to test directory
cd /home/golde/Tenxsom_AI/testing/meta_opt_quant_v6

# Create backup of any existing results
if [ -f "eight_hour_test_results.db" ]; then
    backup_name="eight_hour_test_results_backup_$(date +%Y%m%d_%H%M%S).db"
    echo "Backing up existing results to: $backup_name"
    cp eight_hour_test_results.db "$backup_name"
fi

# Set Python path
export PYTHONPATH=/home/golde/Tenxsom_AI:$PYTHONPATH

# Set process priority (nice value)
NICE_VALUE=10  # Lower priority to not interfere with system

# Launch with nohup to continue running if terminal closes
echo "Launching test suite with nice value $NICE_VALUE..."
echo "Output will be logged to: eight_hour_test_output.log"
echo

# Use exec to replace shell with python process
exec nice -n $NICE_VALUE python3 -u eight_hour_test_suite.py > eight_hour_test_output.log 2>&1