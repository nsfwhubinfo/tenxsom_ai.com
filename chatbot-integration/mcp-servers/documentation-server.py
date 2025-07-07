#!/usr/bin/env python3

"""
Documentation MCP Server for Tenxsom AI
Provides access to technical reports, user guides, and troubleshooting documentation
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentSection:
    """Represents a section of documentation"""
    document_path: str
    section_title: str
    content: str
    line_start: int
    line_end: int
    relevance_score: float = 0.0

class DocumentationIndex:
    """Index of all technical documentation for fast search"""
    
    def __init__(self, docs_root: str = "/home/golde/tenxsom-ai-vertex"):
        self.docs_root = Path(docs_root)
        self.documents = {}
        self.sections = []
        self._build_index()
    
    def _build_index(self):
        """Build searchable index of all documentation"""
        logger.info("Building documentation index...")
        
        # Key documentation files to index
        doc_files = [
            "USEAPI-MCP-INTEGRATION-COMPLETE.md",
            "PRODUCTION-INTEGRATION-SUMMARY.md", 
            "SECURITY-AND-MONITORING-GUIDE.md",
            "useapi-patterns-analysis.md",
            "video-generation-solution.md",
            "MULTI-ACCOUNT-SCALING-STRATEGY.md",
            "cost-analysis-results.md",
            "video-generation-success.md",
            "phase1-consolidation/README.md",
            "useapi-mcp-server/README.md",
            "heygen-integration/test-heygen-api.py",
            "heygen-integration/voice-discovery-tool.py",
            "heygen-integration/youtube-narration-workflow.py",
            "chatbot-integration/CHATBOT-IMPLEMENTATION-PLAN.md"
        ]
        
        for doc_file in doc_files:
            doc_path = self.docs_root / doc_file
            if doc_path.exists():
                self._index_document(doc_path)
            else:
                logger.warning(f"Document not found: {doc_path}")
        
        logger.info(f"Indexed {len(self.documents)} documents with {len(self.sections)} sections")
    
    def _index_document(self, doc_path: Path):
        """Index a single document"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.documents[str(doc_path)] = {
                "path": str(doc_path),
                "name": doc_path.name,
                "content": content,
                "size": len(content),
                "indexed_at": datetime.now().isoformat()
            }
            
            # Split into sections for better search
            self._extract_sections(doc_path, content)
            
        except Exception as e:
            logger.error(f"Error indexing {doc_path}: {e}")
    
    def _extract_sections(self, doc_path: Path, content: str):
        """Extract sections from markdown content"""
        lines = content.split('\n')
        current_section = None
        section_content = []
        line_start = 0
        
        for i, line in enumerate(lines):
            # Detect section headers (markdown)
            if line.startswith('#'):
                # Save previous section
                if current_section and section_content:
                    self.sections.append(DocumentSection(
                        document_path=str(doc_path),
                        section_title=current_section,
                        content='\n'.join(section_content),
                        line_start=line_start,
                        line_end=i-1
                    ))
                
                # Start new section
                current_section = line.strip('#').strip()
                section_content = []
                line_start = i
            else:
                section_content.append(line)
        
        # Save final section
        if current_section and section_content:
            self.sections.append(DocumentSection(
                document_path=str(doc_path),
                section_title=current_section,
                content='\n'.join(section_content),
                line_start=line_start,
                line_end=len(lines)-1
            ))
    
    def search(self, query: str, max_results: int = 5) -> List[DocumentSection]:
        """Search documentation for relevant sections"""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Score each section
        for section in self.sections:
            section.relevance_score = self._calculate_relevance(
                section, query_lower, query_words
            )
        
        # Sort by relevance and return top results
        relevant_sections = [s for s in self.sections if s.relevance_score > 0]
        relevant_sections.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant_sections[:max_results]
    
    def _calculate_relevance(self, section: DocumentSection, 
                           query_lower: str, query_words: List[str]) -> float:
        """Calculate relevance score for a section"""
        content_lower = section.content.lower()
        title_lower = section.section_title.lower()
        
        score = 0.0
        
        # Exact phrase match (highest score)
        if query_lower in content_lower:
            score += 10.0
        if query_lower in title_lower:
            score += 15.0
        
        # Individual word matches
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                content_matches = content_lower.count(word)
                title_matches = title_lower.count(word)
                
                score += content_matches * 1.0
                score += title_matches * 3.0
        
        # Boost score for certain document types
        doc_name = Path(section.document_path).name.lower()
        if "error" in query_lower or "troubleshoot" in query_lower:
            if "solution" in doc_name or "troubleshoot" in doc_name:
                score *= 2.0
        
        if "setup" in query_lower or "install" in query_lower:
            if "readme" in doc_name or "guide" in doc_name:
                score *= 2.0
        
        return score

class TechnicalReportsMCP:
    """MCP server for technical documentation access"""
    
    def __init__(self):
        self.documentation_index = DocumentationIndex()
        self.tools = {
            "query_technical_docs": self._query_technical_docs,
            "search_troubleshooting": self._search_troubleshooting,
            "get_config_examples": self._get_config_examples,
            "find_error_solutions": self._find_error_solutions,
            "get_setup_instructions": self._get_setup_instructions,
            "search_api_patterns": self._search_api_patterns,
            "get_cost_analysis": self._get_cost_analysis,
            "find_scaling_strategies": self._find_scaling_strategies
        }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a documentation tool"""
        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            return await self.tools[tool_name](arguments)
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def _query_technical_docs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """General query across all technical documentation"""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 5)
        
        if not query:
            return {"error": "Query parameter is required"}
        
        results = self.documentation_index.search(query, max_results)
        
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "document": Path(r.document_path).name,
                    "section": r.section_title,
                    "content": r.content[:500] + "..." if len(r.content) > 500 else r.content,
                    "full_content": r.content,
                    "relevance": round(r.relevance_score, 2),
                    "location": f"Lines {r.line_start}-{r.line_end}"
                }
                for r in results
            ],
            "total_results": len(results)
        }
    
    async def _search_troubleshooting(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for troubleshooting and error solutions"""
        error_description = arguments.get("error", "")
        
        # Add troubleshooting keywords to the search
        enhanced_query = f"error troubleshoot solution fix {error_description}"
        
        results = self.documentation_index.search(enhanced_query, 3)
        
        # Filter for error-related content
        error_results = []
        for result in results:
            content_lower = result.content.lower()
            if any(keyword in content_lower for keyword in 
                   ["error", "fix", "solution", "troubleshoot", "problem", "issue"]):
                error_results.append(result)
        
        return {
            "status": "success",
            "error_query": error_description,
            "solutions": [
                {
                    "document": Path(r.document_path).name,
                    "solution_type": r.section_title,
                    "description": r.content[:300] + "..." if len(r.content) > 300 else r.content,
                    "full_solution": r.content,
                    "confidence": round(r.relevance_score, 2)
                }
                for r in error_results[:3]
            ]
        }
    
    async def _get_config_examples(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration examples and templates"""
        config_type = arguments.get("type", "")
        
        query = f"config configuration setup {config_type}"
        results = self.documentation_index.search(query, 5)
        
        # Extract code blocks and configuration examples
        config_examples = []
        for result in results:
            content = result.content
            
            # Find JSON/YAML configuration blocks
            json_blocks = re.findall(r'```(?:json|yaml)?\n(.*?)```', content, re.DOTALL)
            
            for block in json_blocks:
                if any(keyword in block.lower() for keyword in 
                       ["config", "token", "api", "url", "port"]):
                    config_examples.append({
                        "source": Path(result.document_path).name,
                        "section": result.section_title,
                        "config": block.strip(),
                        "type": "json/yaml"
                    })
        
        return {
            "status": "success",
            "config_type": config_type,
            "examples": config_examples[:3]
        }
    
    async def _find_error_solutions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Find solutions for specific error codes or messages"""
        error_code = arguments.get("error_code", "")
        error_message = arguments.get("error_message", "")
        
        query = f"error {error_code} {error_message}"
        results = self.documentation_index.search(query, 5)
        
        solutions = []
        for result in results:
            # Look for solution patterns
            content = result.content
            
            # Find solution steps (numbered lists)
            solution_steps = re.findall(r'(\d+\.\s+.*?)(?=\n\d+\.|\n[A-Z]|\n$)', 
                                       content, re.DOTALL)
            
            if solution_steps:
                solutions.append({
                    "error": f"{error_code} {error_message}".strip(),
                    "document": Path(result.document_path).name,
                    "solution_steps": [step.strip() for step in solution_steps],
                    "context": result.section_title
                })
        
        return {
            "status": "success", 
            "error_query": f"{error_code} {error_message}".strip(),
            "solutions": solutions[:2]
        }
    
    async def _get_setup_instructions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get setup and installation instructions"""
        service = arguments.get("service", "")
        
        query = f"setup install configure {service}"
        results = self.documentation_index.search(query, 3)
        
        instructions = []
        for result in results:
            content = result.content
            
            # Look for step-by-step instructions
            steps = re.findall(r'(?:Step \d+|^\d+\.)\s+(.*?)(?=\n(?:Step|\d+\.)|$)', 
                              content, re.MULTILINE | re.DOTALL)
            
            if steps:
                instructions.append({
                    "service": service,
                    "document": Path(result.document_path).name,
                    "setup_steps": [step.strip() for step in steps],
                    "section": result.section_title
                })
        
        return {
            "status": "success",
            "service": service,
            "instructions": instructions
        }
    
    async def _search_api_patterns(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for API usage patterns and examples"""
        api_name = arguments.get("api", "")
        operation = arguments.get("operation", "")
        
        query = f"api {api_name} {operation} curl endpoint"
        results = self.documentation_index.search(query, 5)
        
        patterns = []
        for result in results:
            content = result.content
            
            # Find curl commands and API examples
            curl_commands = re.findall(r'curl .*?(?=\n[^\s]|\n$)', content, re.DOTALL)
            
            for cmd in curl_commands:
                patterns.append({
                    "api": api_name,
                    "operation": operation,
                    "example": cmd.strip(),
                    "source": Path(result.document_path).name,
                    "context": result.section_title
                })
        
        return {
            "status": "success",
            "api": api_name,
            "patterns": patterns[:3]
        }
    
    async def _get_cost_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get cost analysis and pricing information"""
        service = arguments.get("service", "")
        
        query = f"cost price pricing {service} analysis"
        results = self.documentation_index.search(query, 3)
        
        cost_info = []
        for result in results:
            content = result.content
            
            # Look for cost/pricing information
            if any(keyword in content.lower() for keyword in 
                   ["$", "cost", "price", "free", "unlimited", "subscription"]):
                cost_info.append({
                    "service": service,
                    "document": Path(result.document_path).name,
                    "cost_details": result.content[:400] + "..." if len(result.content) > 400 else result.content,
                    "section": result.section_title
                })
        
        return {
            "status": "success",
            "service": service,
            "cost_analysis": cost_info
        }
    
    async def _find_scaling_strategies(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Find scaling and optimization strategies"""
        context = arguments.get("context", "")
        
        query = f"scaling scale multi-account optimization {context}"
        results = self.documentation_index.search(query, 3)
        
        strategies = []
        for result in results:
            if any(keyword in result.content.lower() for keyword in 
                   ["scale", "multi", "account", "optimization", "performance"]):
                strategies.append({
                    "strategy_type": result.section_title,
                    "document": Path(result.document_path).name,
                    "strategy": result.content[:500] + "..." if len(result.content) > 500 else result.content,
                    "full_strategy": result.content
                })
        
        return {
            "status": "success",
            "context": context,
            "strategies": strategies
        }

# MCP Server Implementation
async def main():
    """Main MCP server entry point"""
    print("📚 Starting Documentation MCP Server")
    print("="*50)
    
    # Initialize server
    server = TechnicalReportsMCP()
    
    print(f"✅ Indexed {len(server.documentation_index.documents)} documents")
    print(f"✅ Available tools: {len(server.tools)}")
    
    # Test the server
    test_queries = [
        "HeyGen TTS setup",
        "522 timeout error",
        "video generation workflow",
        "cost analysis useapi"
    ]
    
    print("\n🧪 Testing documentation search...")
    for query in test_queries:
        result = await server.execute_tool("query_technical_docs", {"query": query})
        if result.get("status") == "success":
            print(f"✅ '{query}': {len(result.get('results', []))} results found")
        else:
            print(f"❌ '{query}': {result.get('error', 'Unknown error')}")
    
    print("\n🚀 Documentation MCP Server ready for integration!")
    
    # Keep server running for testing
    while True:
        try:
            user_query = input("\n📚 Enter documentation query (or 'quit'): ")
            if user_query.lower() in ['quit', 'exit']:
                break
                
            result = await server.execute_tool("query_technical_docs", {"query": user_query})
            
            if result.get("status") == "success":
                results = result.get("results", [])
                print(f"\n📋 Found {len(results)} results:")
                
                for i, r in enumerate(results[:2]):
                    print(f"\n{i+1}. **{r['document']}** - {r['section']}")
                    print(f"   Relevance: {r['relevance']}")
                    print(f"   Content: {r['content'][:200]}...")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except KeyboardInterrupt:
            break
    
    print("👋 Documentation server shutting down")

if __name__ == "__main__":
    asyncio.run(main())