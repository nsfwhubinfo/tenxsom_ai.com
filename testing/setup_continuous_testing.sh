#!/bin/bash
# Setup script for META-OPT-QUANT continuous testing

echo "Setting up META-OPT-QUANT Continuous Testing..."

# Create directories
mkdir -p continuous_test_results

# Make the testing script executable
chmod +x continuous_meta_opt_testing.py

# Install as systemd service (requires sudo)
if command -v systemctl &> /dev/null; then
    echo "Installing systemd service..."
    sudo cp meta_opt_testing.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "Service installed. To start:"
    echo "  sudo systemctl start meta_opt_testing"
    echo "  sudo systemctl enable meta_opt_testing  # for autostart"
    echo "  sudo systemctl status meta_opt_testing  # check status"
else
    echo "systemd not available. Run manually with:"
    echo "  python3 continuous_meta_opt_testing.py"
fi

echo "Setup complete!"