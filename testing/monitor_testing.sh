#!/bin/bash
# Monitor META-OPT-QUANT continuous testing

echo "META-OPT-QUANT Testing Monitor"
echo "=============================="

# Check service status
echo -e "\nService Status:"
systemctl status meta_opt_testing --no-pager | head -10

# Check for results
RESULTS_DIR="/home/golde/Tenxsom_AI/testing/continuous_test_results"
echo -e "\nLatest Results:"
if [ -d "$RESULTS_DIR" ]; then
    # Show latest log entries
    if [ -f "$RESULTS_DIR/continuous_test_$(date +%Y%m%d).log" ]; then
        echo "Recent log entries:"
        tail -20 "$RESULTS_DIR/continuous_test_$(date +%Y%m%d).log"
    fi
    
    # Show test count
    if [ -f "$RESULTS_DIR/results_$(date +%Y%m%d).json" ]; then
        echo -e "\nTests completed today:"
        grep -c "test_id" "$RESULTS_DIR/results_$(date +%Y%m%d).json" || echo "0"
    fi
    
    # Show latest report if exists
    LATEST_REPORT=$(ls -t "$RESULTS_DIR"/report_*.txt 2>/dev/null | head -1)
    if [ -f "$LATEST_REPORT" ]; then
        echo -e "\nLatest Report Summary:"
        head -20 "$LATEST_REPORT"
    fi
else
    echo "Results directory not found. Service may not have started yet."
fi

echo -e "\nUseful commands:"
echo "  sudo systemctl status meta_opt_testing    # Check service status"
echo "  sudo systemctl stop meta_opt_testing      # Stop testing"
echo "  sudo systemctl restart meta_opt_testing   # Restart testing"
echo "  sudo journalctl -u meta_opt_testing -f    # Follow service logs"
echo "  tail -f $RESULTS_DIR/service.log          # Follow output log"