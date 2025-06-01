#!/bin/bash
# Fix permissions and run continuous testing

echo "Fixing permissions and starting META-OPT-QUANT testing..."

# Remove the problematic directory
sudo rm -rf /home/golde/Tenxsom_AI/testing/continuous_test_results

# Create it fresh with correct ownership
mkdir -p /home/golde/Tenxsom_AI/testing/continuous_test_results

# Verify ownership
echo "Directory created with permissions:"
ls -la /home/golde/Tenxsom_AI/testing/continuous_test_results/

# Set Python path
export PYTHONPATH="/home/golde/Tenxsom_AI/research/meta_opt_quant:$PYTHONPATH"

# Run directly
echo -e "\nStarting continuous testing..."
cd /home/golde/Tenxsom_AI/testing
python3 continuous_meta_opt_testing.py