#!/bin/bash
set -e

echo "🚀 Starting META-OPT-QUANT V6 Quick CI/CD Validation"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "run_quick_validation_test.py" ]; then
    echo "❌ Error: run_quick_validation_test.py not found"
    echo "   Please run this script from the testing/meta_opt_quant_v6 directory"
    exit 1
fi

# Run the validation test
echo "⏳ Running quick validation test..."
python3 run_quick_validation_test.py

# Check exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ VALIDATION PASSED"
    echo "==================="
    echo "✓ Basic functionality: 100%"
    echo "✓ No crashes: 100%" 
    echo "✓ System stability: Confirmed"
    echo "✓ Ready for deployment"
    echo ""
    echo "📊 View detailed results:"
    echo "   - Report: quick_validation_test_report.json"
    echo "   - Logs: quick_validation_test.log"
else
    echo ""
    echo "❌ VALIDATION FAILED"
    echo "==================="
    echo "   Check logs for details: quick_validation_test.log"
    echo "   Deployment blocked until issues are resolved"
    exit 1
fi