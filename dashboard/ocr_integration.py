#!/usr/bin/env python3
"""
OCR Integration for Handwritten Notes
=====================================
Supports multiple OCR backends for processing handwritten notes
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np

class OCRProcessor:
    """Multi-backend OCR processor for handwritten notes"""
    
    def __init__(self, backend: str = "auto"):
        self.backend = backend
        self.available_backends = self.check_available_backends()
        
        if backend == "auto":
            self.backend = self.select_best_backend()
            
    def check_available_backends(self) -> Dict[str, bool]:
        """Check which OCR backends are available"""
        backends = {}
        
        # Check Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            backends["tesseract"] = True
        except:
            backends["tesseract"] = False
            
        # Check for cloud credentials
        backends["aws_textract"] = os.getenv("AWS_ACCESS_KEY_ID") is not None
        backends["google_vision"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is not None
        
        # Check EasyOCR
        try:
            import easyocr
            backends["easyocr"] = True
        except:
            backends["easyocr"] = False
            
        return backends
        
    def select_best_backend(self) -> str:
        """Select the best available backend"""
        if self.available_backends.get("easyocr"):
            return "easyocr"  # Best for handwriting
        elif self.available_backends.get("aws_textract"):
            return "aws_textract"  # Good for handwriting
        elif self.available_backends.get("google_vision"):
            return "google_vision"  # Good general OCR
        elif self.available_backends.get("tesseract"):
            return "tesseract"  # Fallback
        else:
            return "manual"  # No OCR available
            
    def preprocess_image(self, image_path: Path) -> Image.Image:
        """Preprocess image for better OCR results"""
        img = Image.open(image_path)
        
        # Convert to grayscale
        if img.mode != 'L':
            img = img.convert('L')
            
        # Enhance contrast
        img_array = np.array(img)
        
        # Simple threshold to make text clearer
        threshold = 128
        img_array = ((img_array > threshold) * 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
        
    def ocr_with_tesseract(self, image_path: Path) -> str:
        """OCR using Tesseract"""
        try:
            import pytesseract
            
            img = self.preprocess_image(image_path)
            
            # Configure for handwriting
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img, config=custom_config)
            
            return text
        except Exception as e:
            return f"Tesseract OCR failed: {str(e)}"
            
    def ocr_with_easyocr(self, image_path: Path) -> str:
        """OCR using EasyOCR (better for handwriting)"""
        try:
            import easyocr
            
            reader = easyocr.Reader(['en'])
            result = reader.readtext(str(image_path))
            
            # Combine all detected text
            text_parts = []
            for (bbox, text, prob) in result:
                if prob > 0.5:  # Confidence threshold
                    text_parts.append(text)
                    
            return " ".join(text_parts)
        except Exception as e:
            return f"EasyOCR failed: {str(e)}"
            
    def ocr_with_aws_textract(self, image_path: Path) -> str:
        """OCR using AWS Textract"""
        try:
            import boto3
            
            client = boto3.client('textract', region_name='us-east-1')
            
            with open(image_path, 'rb') as img_file:
                img_bytes = img_file.read()
                
            response = client.detect_document_text(
                Document={'Bytes': img_bytes}
            )
            
            # Extract text
            text_parts = []
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    text_parts.append(item['Text'])
                    
            return "\n".join(text_parts)
        except Exception as e:
            return f"AWS Textract failed: {str(e)}"
            
    def process_image(self, image_path: Path) -> Dict[str, Any]:
        """Process image with selected backend"""
        result = {
            "backend": self.backend,
            "success": False,
            "text": "",
            "confidence": 0.0,
            "metadata": {}
        }
        
        if self.backend == "manual":
            result["text"] = f"No OCR backend available. Manual transcription needed for: {image_path.name}"
            result["metadata"]["instruction"] = "Install pytesseract or easyocr: pip install pytesseract easyocr"
            
        elif self.backend == "tesseract":
            result["text"] = self.ocr_with_tesseract(image_path)
            result["success"] = not result["text"].startswith("Tesseract OCR failed")
            
        elif self.backend == "easyocr":
            result["text"] = self.ocr_with_easyocr(image_path)
            result["success"] = not result["text"].startswith("EasyOCR failed")
            
        elif self.backend == "aws_textract":
            result["text"] = self.ocr_with_aws_textract(image_path)
            result["success"] = not result["text"].startswith("AWS Textract failed")
            
        # Post-process for mathematical notation
        if result["success"]:
            result["text"] = self.fix_math_notation(result["text"])
            
        return result
        
    def fix_math_notation(self, text: str) -> str:
        """Fix common OCR errors in mathematical notation"""
        replacements = {
            "×": "*",
            "÷": "/",
            "−": "-",
            "∑": "sum",
            "∫": "integral",
            "∞": "infinity",
            "α": "alpha",
            "β": "beta",
            "γ": "gamma",
            "δ": "delta",
            "θ": "theta",
            "λ": "lambda",
            "μ": "mu",
            "π": "pi",
            "σ": "sigma",
            "φ": "phi",
            "ω": "omega",
            "≈": "~=",
            "≤": "<=",
            "≥": ">=",
            "≠": "!=",
            "∈": "in",
            "∉": "not in",
            "∀": "for all",
            "∃": "exists",
            "∴": "therefore",
            "∵": "because"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text


# Quick setup guide for OCR
def create_ocr_setup_guide():
    """Create setup guide for OCR"""
    guide = """
# OCR Setup Guide for Tenxsom AI Knowledge Ingestion

## Option 1: Tesseract (Free, Local)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
pip install pytesseract pillow

# macOS
brew install tesseract
pip install pytesseract pillow

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
pip install pytesseract pillow
```

## Option 2: EasyOCR (Free, Better for Handwriting)
```bash
pip install easyocr
# Note: First run will download models (~64MB)
```

## Option 3: AWS Textract (Pay-per-use, Best Quality)
```bash
pip install boto3
# Set AWS credentials:
export AWS_ACCESS_KEY_ID='your_key'
export AWS_SECRET_ACCESS_KEY='your_secret'
```

## Option 4: Manual Transcription Workflow
1. Place images in: dashboard/knowledge_inbox/notes/
2. Run: python knowledge_ingestion_engine.py process
3. Check: dashboard/knowledge_processed/ocr_needed_*.txt
4. Manually transcribe and save as .txt in knowledge_inbox/texts/
5. Run process again to ingest transcribed text

## Testing OCR
```python
from ocr_integration import OCRProcessor

ocr = OCRProcessor()
print(f"Selected backend: {ocr.backend}")
print(f"Available backends: {ocr.available_backends}")

# Process an image
result = ocr.process_image(Path("your_note.jpg"))
print(result["text"])
```
"""
    
    with open("/home/golde/Tenxsom_AI/dashboard/OCR_SETUP_GUIDE.md", "w") as f:
        f.write(guide)
        
    print("OCR setup guide created at: dashboard/OCR_SETUP_GUIDE.md")


if __name__ == "__main__":
    create_ocr_setup_guide()
    
    # Test available backends
    ocr = OCRProcessor()
    print(f"Available OCR backends: {ocr.available_backends}")
    print(f"Selected backend: {ocr.backend}")