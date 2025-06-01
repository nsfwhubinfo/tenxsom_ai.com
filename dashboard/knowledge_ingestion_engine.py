#!/usr/bin/env python3
"""
Tenxsom AI Knowledge Ingestion Engine
=====================================
Processes handwritten notes (images), text files, and conversation logs
into structured knowledge base entries
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
from dataclasses import dataclass, asdict
import shutil

@dataclass
class KnowledgeItem:
    """Structured knowledge entry"""
    id: str
    source_type: str  # "note_image", "text_file", "conversation", "research_paper"
    source_path: str
    processed_date: str
    content: str
    metadata: Dict[str, Any]
    tags: List[str]
    relevance_scores: Dict[str, float]
    linked_concepts: List[str]

class KnowledgeIngestionEngine:
    """Processes unstructured data into Tenxsom AI knowledge base"""
    
    def __init__(self, project_root: str = "/home/golde/Tenxsom_AI"):
        self.project_root = Path(project_root)
        self.dashboard_dir = self.project_root / "dashboard"
        self.inbox_dir = self.dashboard_dir / "knowledge_inbox"
        self.processed_dir = self.dashboard_dir / "knowledge_processed"
        self.kb_dir = self.dashboard_dir / "knowledge_base"
        
        # Create directory structure
        for dir_path in [self.inbox_dir / "notes", 
                        self.inbox_dir / "texts",
                        self.inbox_dir / "conversations",
                        self.processed_dir,
                        self.kb_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Pattern matching for different content types
        self.patterns = {
            "mathematical": [
                r"(?:fractal|dimension|topology|manifold|zeta|prime|quantum)",
                r"(?:FMO|ZFR|IOP|QHFM|PEDSOR|IE-HEV)",
                r"(?:optimization|convergence|eigenvalue|resonance)"
            ],
            "technical": [
                r"(?:API|SDK|microservice|Docker|Kubernetes)",
                r"(?:implementation|architecture|integration|deployment)",
                r"(?:Python|JavaScript|React|FastAPI)"
            ],
            "business": [
                r"(?:revenue|MRR|pricing|customer|market)",
                r"(?:Stripe|payment|subscription|launch)",
                r"(?:legal|patent|licensing|trademark)"
            ],
            "research": [
                r"(?:paper|study|theory|hypothesis|experiment)",
                r"(?:citation|reference|methodology|results)",
                r"(?:Grok|Claude|GPT|LLM|AGI)"
            ]
        }
        
    def generate_id(self, content: str, source: str) -> str:
        """Generate unique ID for knowledge item"""
        hash_input = f"{content[:100]}{source}{datetime.datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
    def extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = set()
        
        # Check against pattern categories
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    tags.add(category)
                    # Also add specific matches as tags
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches[:3]:  # Limit to 3 per pattern
                        tags.add(match.lower())
                        
        return list(tags)
        
    def calculate_relevance(self, content: str) -> Dict[str, float]:
        """Calculate relevance scores for different aspects"""
        scores = {
            "mathematical": 0.0,
            "technical": 0.0,
            "business": 0.0,
            "research": 0.0,
            "urgency": 0.0
        }
        
        content_lower = content.lower()
        
        # Count pattern matches
        for category, patterns in self.patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, content_lower))
            scores[category] = min(1.0, matches / 10.0)  # Normalize to 0-1
            
        # Check for urgency indicators
        urgency_keywords = ["urgent", "asap", "critical", "immediate", "deadline", "today", "tomorrow"]
        urgency_matches = sum(1 for keyword in urgency_keywords if keyword in content_lower)
        scores["urgency"] = min(1.0, urgency_matches / 3.0)
        
        return scores
        
    def extract_linked_concepts(self, content: str) -> List[str]:
        """Extract concepts that link to existing Tenxsom AI components"""
        concepts = []
        
        # Core component references
        components = {
            "FMO": "Fractal Meta-Ontology",
            "ZFR-IOP": "Zeta Function Regularization",
            "QHFM": "Quantum-Hexagonal-Fractal Memory",
            "PEDSOR": "Poiesis-Eimi Decision Support",
            "IE-HEV": "Intelligence Enhancement HEV",
            "CHM": "Cognitive Health Monitor",
            "SDK": "FMO Optimizer SDK"
        }
        
        for abbrev, full_name in components.items():
            if abbrev in content or full_name.lower() in content.lower():
                concepts.append(abbrev)
                
        # Extract cross-references (e.g., "see also X", "related to Y")
        cross_refs = re.findall(r"(?:see also|related to|connects to|similar to)\s+(\w+)", content, re.IGNORECASE)
        concepts.extend(cross_refs[:5])  # Limit to 5
        
        return list(set(concepts))
        
    def process_note_image(self, image_path: Path) -> Optional[KnowledgeItem]:
        """Process handwritten note image"""
        print(f"Processing note image: {image_path.name}")
        
        # OCR placeholder - in production, use pytesseract or cloud OCR
        # For now, create a placeholder entry
        ocr_text = f"""
[OCR PLACEHOLDER for {image_path.name}]
To implement:
1. Install: pip install pytesseract pillow
2. Or use: AWS Textract / Google Cloud Vision
3. Extract handwritten text
4. Apply error correction for mathematical notation

Manual transcription instructions saved to: {self.processed_dir / f'ocr_needed_{image_path.stem}.txt'}
"""
        
        # Save OCR instruction file
        ocr_instruction = self.processed_dir / f"ocr_needed_{image_path.stem}.txt"
        with open(ocr_instruction, 'w') as f:
            f.write(f"Image file: {image_path}\n")
            f.write("Transcribe handwritten notes, paying attention to:\n")
            f.write("- Mathematical formulas\n")
            f.write("- Diagram descriptions\n")
            f.write("- Key concepts and connections\n")
            f.write("- Any urgency markers or deadlines\n")
            
        # Create knowledge item
        item = KnowledgeItem(
            id=self.generate_id(ocr_text, str(image_path)),
            source_type="note_image",
            source_path=str(image_path),
            processed_date=datetime.datetime.now().isoformat(),
            content=ocr_text,
            metadata={
                "file_size": image_path.stat().st_size,
                "ocr_status": "pending_manual",
                "original_filename": image_path.name
            },
            tags=["pending_ocr", "handwritten"],
            relevance_scores={"urgency": 0.5},  # Default medium urgency for handwritten
            linked_concepts=[]
        )
        
        return item
        
    def process_text_file(self, text_path: Path) -> Optional[KnowledgeItem]:
        """Process text file (conversation, notes, research)"""
        print(f"Processing text file: {text_path.name}")
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Detect content type
            content_type = "general"
            if "Human:" in content and "Assistant:" in content:
                content_type = "conversation"
            elif any(keyword in content.lower() for keyword in ["abstract", "methodology", "conclusion", "references"]):
                content_type = "research_paper"
            elif "```" in content:
                content_type = "code_snippet"
                
            # Extract metadata
            metadata = {
                "file_size": text_path.stat().st_size,
                "line_count": content.count('\n'),
                "word_count": len(content.split()),
                "content_type": content_type,
                "original_filename": text_path.name
            }
            
            # For conversations, extract key insights
            if content_type == "conversation":
                insights = self.extract_conversation_insights(content)
                metadata["key_insights"] = insights
                
            # Create knowledge item
            item = KnowledgeItem(
                id=self.generate_id(content[:500], str(text_path)),
                source_type=f"text_file_{content_type}",
                source_path=str(text_path),
                processed_date=datetime.datetime.now().isoformat(),
                content=content,
                metadata=metadata,
                tags=self.extract_tags(content),
                relevance_scores=self.calculate_relevance(content),
                linked_concepts=self.extract_linked_concepts(content)
            )
            
            return item
            
        except Exception as e:
            print(f"Error processing {text_path}: {e}")
            return None
            
    def extract_conversation_insights(self, conversation: str) -> List[str]:
        """Extract key insights from conversation text"""
        insights = []
        
        # Look for conclusion markers
        conclusion_patterns = [
            r"(?:in conclusion|to summarize|key takeaway|important note|remember that)[:\s]+([^.!?]+[.!?])",
            r"(?:the main point is|this means that|therefore)[:\s]+([^.!?]+[.!?])",
            r"(?:IMPORTANT|CRITICAL|KEY):[:\s]+([^.!?]+[.!?])"
        ]
        
        for pattern in conclusion_patterns:
            matches = re.findall(pattern, conversation, re.IGNORECASE | re.MULTILINE)
            insights.extend(matches[:3])  # Limit to 3 per pattern
            
        # Look for action items
        action_patterns = [
            r"(?:TODO|Action item|Next step)[:\s]+([^.!?\n]+)",
            r"(?:You should|I recommend|Consider)[:\s]+([^.!?\n]+)"
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, conversation, re.IGNORECASE)
            insights.extend([f"ACTION: {match}" for match in matches[:2]])
            
        return insights[:10]  # Limit total insights
        
    def create_fmo_entry(self, item: KnowledgeItem) -> Dict[str, Any]:
        """Create FMO-compatible entry from knowledge item"""
        return {
            "node_id": f"kb_{item.id}",
            "type": "knowledge",
            "subtype": item.source_type,
            "properties": {
                "content_hash": item.id,
                "processed_date": item.processed_date,
                "tags": item.tags,
                "relevance": item.relevance_scores,
                "source": item.source_path
            },
            "connections": [
                {
                    "target": f"concept_{concept}",
                    "relationship": "references",
                    "weight": 0.8
                }
                for concept in item.linked_concepts
            ],
            "metadata": item.metadata
        }
        
    def process_inbox(self, limit: Optional[int] = None) -> Dict[str, int]:
        """Process all pending items in inbox"""
        stats = {
            "notes_processed": 0,
            "texts_processed": 0,
            "errors": 0
        }
        
        # Process note images
        note_files = list((self.inbox_dir / "notes").glob("*"))
        for note_file in note_files[:limit]:
            try:
                item = self.process_note_image(note_file)
                if item:
                    self.save_knowledge_item(item)
                    # Move to processed
                    shutil.move(str(note_file), str(self.processed_dir / f"note_{note_file.name}"))
                    stats["notes_processed"] += 1
            except Exception as e:
                print(f"Error processing note {note_file}: {e}")
                stats["errors"] += 1
                
        # Process text files
        text_files = list((self.inbox_dir / "texts").glob("*.txt"))
        for text_file in text_files[:limit]:
            try:
                item = self.process_text_file(text_file)
                if item:
                    self.save_knowledge_item(item)
                    # Move to processed
                    shutil.move(str(text_file), str(self.processed_dir / f"text_{text_file.name}"))
                    stats["texts_processed"] += 1
            except Exception as e:
                print(f"Error processing text {text_file}: {e}")
                stats["errors"] += 1
                
        return stats
        
    def save_knowledge_item(self, item: KnowledgeItem):
        """Save knowledge item to knowledge base"""
        # Save as individual file
        item_file = self.kb_dir / f"kb_{item.id}.json"
        with open(item_file, 'w') as f:
            json.dump(asdict(item), f, indent=2)
            
        # Update master index
        index_file = self.kb_dir / "kb_index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {"items": [], "last_updated": None}
            
        index["items"].append({
            "id": item.id,
            "source_type": item.source_type,
            "processed_date": item.processed_date,
            "tags": item.tags,
            "relevance": item.relevance_scores
        })
        index["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
            
        # Create FMO entry
        fmo_entry = self.create_fmo_entry(item)
        fmo_file = self.project_root / "services/FMO/knowledge_fmo.json"
        
        if fmo_file.exists():
            with open(fmo_file, 'r') as f:
                fmo_data = json.load(f)
        else:
            fmo_data = {"nodes": [], "edges": []}
            
        fmo_data["nodes"].append(fmo_entry)
        
        with open(fmo_file, 'w') as f:
            json.dump(fmo_data, f, indent=2)
            
    def query_knowledge_base(self, query: str, limit: int = 10) -> List[KnowledgeItem]:
        """Query knowledge base for relevant items"""
        results = []
        
        # Calculate query relevance
        query_tags = self.extract_tags(query)
        query_relevance = self.calculate_relevance(query)
        
        # Search through knowledge items
        for kb_file in self.kb_dir.glob("kb_*.json"):
            if kb_file.name == "kb_index.json":
                continue
                
            with open(kb_file, 'r') as f:
                item_data = json.load(f)
                item = KnowledgeItem(**item_data)
                
            # Calculate match score
            score = 0.0
            
            # Tag overlap
            tag_overlap = len(set(item.tags) & set(query_tags))
            score += tag_overlap * 0.3
            
            # Relevance similarity
            for category in query_relevance:
                if category in item.relevance_scores:
                    score += (1 - abs(query_relevance[category] - item.relevance_scores[category])) * 0.2
                    
            # Content match
            if query.lower() in item.content.lower():
                score += 0.5
                
            results.append((score, item))
            
        # Sort by score and return top items
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in results[:limit]]


def main():
    """CLI for knowledge ingestion"""
    import sys
    
    engine = KnowledgeIngestionEngine()
    
    if len(sys.argv) < 2:
        print("Usage: python knowledge_ingestion_engine.py [process|query|status]")
        return
        
    command = sys.argv[1]
    
    if command == "process":
        print("Processing knowledge inbox...")
        stats = engine.process_inbox()
        print(f"Processed: {stats['notes_processed']} notes, {stats['texts_processed']} texts")
        print(f"Errors: {stats['errors']}")
        
    elif command == "query" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        print(f"Querying for: {query}")
        results = engine.query_knowledge_base(query, limit=5)
        
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item.source_type} - {item.processed_date[:10]}")
            print(f"   Tags: {', '.join(item.tags[:5])}")
            print(f"   Preview: {item.content[:200]}...")
            
    elif command == "status":
        notes_pending = len(list((engine.inbox_dir / "notes").glob("*")))
        texts_pending = len(list((engine.inbox_dir / "texts").glob("*.txt")))
        kb_items = len(list(engine.kb_dir.glob("kb_*.json"))) - 1  # Exclude index
        
        print(f"Knowledge Base Status:")
        print(f"  Notes pending: {notes_pending}")
        print(f"  Texts pending: {texts_pending}")
        print(f"  Total KB items: {kb_items}")
        

if __name__ == "__main__":
    main()