#!/bin/bash
# Run continuous testing directly

cd /home/golde/Tenxsom_AI/testing

# Create results directory if needed
mkdir -p continuous_test_results

# Set Python path
export PYTHONPATH="/home/golde/Tenxsom_AI/research/meta_opt_quant:$PYTHONPATH"

# Run with nohup for background execution
echo "Starting META-OPT-QUANT continuous testing..."
nohup python3 continuous_meta_opt_testing.py > continuous_test_results/output.log 2>&1 &

PID=$!
echo "Started with PID: $PID"
echo "Logs: continuous_test_results/output.log"
echo ""
echo "To stop: kill $PID"
echo "To monitor: tail -f continuous_test_results/output.log"