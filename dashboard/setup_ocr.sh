#!/bin/bash
# Setup OCR for Tenxsom AI Knowledge Ingestion

echo "Setting up OCR for handwritten note processing..."

# Option 1: Install with --break-system-packages (quick fix)
echo "Installing EasyOCR..."
pip3 install easyocr --break-system-packages

# Also install pytesseract as backup
echo "Installing Tesseract OCR..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr
pip3 install pytesseract --break-system-packages

echo "✓ OCR setup complete!"
echo ""
echo "Testing OCR availability..."
python3 dashboard/ocr_integration.py

echo ""
echo "You can now process handwritten notes!"
echo "Place images in: dashboard/knowledge_inbox/notes/"
echo "Then run: txingest process"