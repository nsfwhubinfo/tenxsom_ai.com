#!/usr/bin/env python3
"""
Quick Note Processor for Tenxsom AI
===================================
Streamlined workflow for processing notes without OCR dependencies
"""

import os
import sys
import json
import datetime
from pathlib import Path
import shutil

class QuickNoteProcessor:
    """Simple note processing without external dependencies"""
    
    def __init__(self):
        self.dashboard_dir = Path("/home/golde/Tenxsom_AI/dashboard")
        self.inbox_dir = self.dashboard_dir / "knowledge_inbox"
        self.manual_dir = self.dashboard_dir / "manual_transcription"
        self.manual_dir.mkdir(exist_ok=True)
        
    def create_transcription_template(self, image_path: Path) -> Path:
        """Create a template for manual transcription"""
        template_path = self.manual_dir / f"{image_path.stem}_transcribe.txt"
        
        template = f"""# Transcription Template for: {image_path.name}
# Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
# Instructions: Replace the text below with your handwritten notes

## Original Image: {image_path}

## Categories (mark relevant ones with X):
[ ] Mathematical formulas/concepts
[ ] Technical implementation notes  
[ ] Business/revenue ideas
[ ] Research/paper references
[ ] Urgent/deadline items

## Transcribed Content:
[Start typing your notes here]




## Key Concepts Mentioned:
- 
- 
- 

## Action Items:
- 
- 

## Related to Tenxsom Components:
[ ] FMO (Fractal Meta-Ontology)
[ ] ZFR-IOP (Zeta Function Regularization)
[ ] QHFM (Quantum-Hexagonal-Fractal Memory)
[ ] SDK (FMO Optimizer)
[ ] CHM (Cognitive Health Monitor)
[ ] Other: 

---
Save this file and run: txingest process
"""
        
        with open(template_path, 'w') as f:
            f.write(template)
            
        # Copy image to manual directory for reference
        shutil.copy2(image_path, self.manual_dir / image_path.name)
        
        return template_path
        
    def process_quick_note(self, note_text: str, category: str = "general"):
        """Process a quick text note"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quick_note_{category}_{timestamp}.txt"
        
        note_path = self.inbox_dir / "texts" / filename
        
        with open(note_path, 'w') as f:
            f.write(f"# Quick Note - {category}\n")
            f.write(f"# Timestamp: {datetime.datetime.now().isoformat()}\n\n")
            f.write(note_text)
            
        print(f"✓ Note saved: {filename}")
        print("Run 'txingest process' to add to knowledge base")
        
    def list_pending_transcriptions(self):
        """List images waiting for transcription"""
        images = list((self.inbox_dir / "notes").glob("*"))
        templates = list(self.manual_dir.glob("*_transcribe.txt"))
        
        print(f"Images pending transcription: {len(images)}")
        print(f"Transcription templates created: {len(templates)}")
        
        if images:
            print("\nPending images:")
            for img in images[:5]:
                print(f"  - {img.name}")
                
        if templates:
            print("\nOpen templates:")
            for tmp in templates[:5]:
                print(f"  - {tmp.name}")
                
    def quick_entry(self):
        """Interactive quick note entry"""
        print("Tenxsom AI Quick Note Entry")
        print("-" * 40)
        print("Categories: math, tech, business, research, urgent")
        print("Type 'done' to finish, 'image' to process an image file")
        print("-" * 40)
        
        while True:
            entry = input("\n> ").strip()
            
            if entry.lower() == 'done':
                break
            elif entry.lower() == 'image':
                img_name = input("Image filename: ").strip()
                img_path = self.inbox_dir / "notes" / img_name
                if img_path.exists():
                    template = self.create_transcription_template(img_path)
                    print(f"✓ Created template: {template}")
                    print(f"Edit the file and run 'txingest process' when done")
                else:
                    print(f"Image not found: {img_path}")
            else:
                # Parse category if provided
                if entry.startswith('[') and ']' in entry:
                    category = entry[1:entry.index(']')]
                    note_text = entry[entry.index(']')+1:].strip()
                else:
                    category = "general"
                    note_text = entry
                    
                if note_text:
                    self.process_quick_note(note_text, category)


def main():
    processor = QuickNoteProcessor()
    
    if len(sys.argv) < 2:
        processor.quick_entry()
    else:
        command = sys.argv[1]
        
        if command == "list":
            processor.list_pending_transcriptions()
        elif command == "template" and len(sys.argv) > 2:
            img_path = Path(sys.argv[2])
            if img_path.exists():
                template = processor.create_transcription_template(img_path)
                print(f"Created: {template}")
                os.system(f"nano {template}")  # Open in editor
            else:
                print(f"Image not found: {img_path}")
        else:
            # Treat as quick note
            note_text = " ".join(sys.argv[1:])
            processor.process_quick_note(note_text)


if __name__ == "__main__":
    main()