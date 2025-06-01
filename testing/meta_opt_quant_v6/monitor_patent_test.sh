#!/bin/bash
echo "Patent Demonstration Test Monitor"
echo "=================================="
echo "Start time: $(date)"
echo ""

while true; do
    # Check if process is still running
    if ! ps aux | grep -q "[p]ython3 run_patent_test.py"; then
        echo "Test completed at: $(date)"
        break
    fi
    
    # Show latest log entries
    echo "Current status ($(date +%H:%M:%S)):"
    tail -n 10 patent_test_output.log | grep -E "(Progress|φ discoveries|innovation|claim)"
    
    # Check for report file
    if [ -f "patent_demonstration_test_report.json" ]; then
        echo ""
        echo "Report generated! Key metrics:"
        python3 -c "import json; data=json.load(open('patent_demonstration_test_report.json')); print(f'φ discovery rate: {data.get(\"phi_discovery_rate\", 0):.1f}%'); print(f'Innovation score: {data.get(\"innovation_score\", 0):.3f}')"
    fi
    
    echo "---"
    sleep 300  # Check every 5 minutes
done