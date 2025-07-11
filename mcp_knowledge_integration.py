#!/usr/bin/env python3

"""
MCP Knowledge Integration System for TenxsomAI
Transforms static tutorials into dynamic production intelligence
"""

import asyncio
import logging
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """Types of knowledge artifacts"""
    BEST_PRACTICE = "best_practice"
    TIP = "tip"
    PITFALL = "pitfall"
    WORKFLOW_STEP = "workflow_step"
    PARAMETER = "parameter"
    PROMPT_ELEMENT = "prompt_element"


class ToolCategory(Enum):
    """Tool categories for knowledge"""
    VEO3 = "veo3"
    LTX_STUDIO = "ltx_studio"
    MIDJOURNEY = "midjourney"
    PROMPT_ENGINEERING = "prompt_engineering"


@dataclass
class KnowledgeArtifact:
    """Individual knowledge artifact from manifests"""
    knowledge_id: str
    tool_name: str
    feature_category: str
    knowledge_type: KnowledgeType
    content: str
    source: str
    engagement_metric: int
    tags: List[str]
    examples: List[str]
    created_at: datetime


@dataclass
class ProductionGenome:
    """Complete production DNA for a video"""
    genome_id: str
    base_archetype: str
    target_tools: List[str]
    youtube_api_analytics: Dict[str, Any]
    executed_steps: List[Dict[str, Any]]
    injected_knowledge: List[str]
    performance_score: float
    created_at: datetime
    video_id: Optional[str] = None


@dataclass
class PerformanceInsight:
    """Performance correlation insight"""
    insight_id: str
    knowledge_id: str
    correlation_metric: str
    positive_impact_score: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    recommendation: str


class MCPKnowledgeIntegration:
    """
    Dynamic knowledge integration system for MCP
    
    Features:
    - XML manifest parsing and ingestion
    - Dynamic knowledge injection into prompts
    - Production genome generation
    - YouTube analytics correlation
    - Performance-based optimization
    """
    
    def __init__(self, db_connection=None):
        """Initialize knowledge integration system"""
        self.db_connection = db_connection
        
        # Knowledge storage
        self.knowledge_base = {}
        self.production_genomes = {}
        self.performance_insights = {}
        
        # Configuration
        self.integration_config = {
            "max_knowledge_per_step": 3,
            "min_engagement_threshold": 100,
            "performance_correlation_threshold": 0.7,
            "genome_retention_days": 90,
            "analytics_update_interval": 3600  # 1 hour
        }
        
        # Tool-specific knowledge categories
        self.tool_categories = {
            "veo3": ["prompting", "parameters", "safety", "optimization"],
            "ltx_studio": ["storyboarding", "character_creation", "lora_controls", "workflow"],
            "midjourney": ["camera_angles", "lighting", "styles", "motion"],
            "prompt_engineering": ["structure", "accuracy", "visual_language", "best_practices"]
        }
        
    async def ingest_manifests(self, manifest_files: List[str]):
        """Parse and ingest XML manifests into knowledge base"""
        
        logger.info(f"📚 Ingesting {len(manifest_files)} knowledge manifests")
        
        for manifest_file in manifest_files:
            try:
                await self._parse_manifest(manifest_file)
            except Exception as e:
                logger.error(f"Failed to parse manifest {manifest_file}: {e}")
        
        # Save to database
        await self._save_knowledge_to_db()
        
        logger.info(f"✅ Ingested {len(self.knowledge_base)} knowledge artifacts")
        
    async def _parse_manifest(self, manifest_file: str):
        """Parse individual XML manifest"""
        
        tree = ET.parse(manifest_file)
        root = tree.getroot()
        
        # Determine tool from root tag
        tool_name = self._determine_tool_from_manifest(root.tag)
        
        # Extract knowledge artifacts
        await self._extract_best_practices(root, tool_name)
        await self._extract_tips(root, tool_name)
        await self._extract_workflow_steps(root, tool_name)
        await self._extract_parameters(root, tool_name)
        
    def _determine_tool_from_manifest(self, root_tag: str) -> str:
        """Determine tool name from manifest root tag"""
        
        tag_mappings = {
            "Veo3VertexAITutorialManifest": "veo3",
            "LTXStudioTutorialManifest": "ltx_studio",
            "PromptManifestForHighQualityVideoAndImages": "midjourney"
        }
        
        return tag_mappings.get(root_tag, "unknown")
    
    async def _extract_best_practices(self, root: ET.Element, tool_name: str):
        """Extract best practices from manifest"""
        
        # Find all BestPractices elements
        for bp_element in root.findall(".//BestPractices"):
            content = bp_element.text.strip() if bp_element.text else ""
            
            if content:
                knowledge_id = self._generate_knowledge_id(tool_name, "best_practice", content)
                
                artifact = KnowledgeArtifact(
                    knowledge_id=knowledge_id,
                    tool_name=tool_name,
                    feature_category=self._extract_parent_category(bp_element),
                    knowledge_type=KnowledgeType.BEST_PRACTICE,
                    content=content,
                    source=self._extract_source(bp_element),
                    engagement_metric=self._extract_engagement_metric(content),
                    tags=self._extract_tags(content),
                    examples=self._extract_examples(bp_element),
                    created_at=datetime.now()
                )
                
                self.knowledge_base[knowledge_id] = artifact
    
    async def _extract_tips(self, root: ET.Element, tool_name: str):
        """Extract tips from manifest"""
        
        for tip_element in root.findall(".//Tip"):
            content = tip_element.text.strip() if tip_element.text else ""
            
            if content:
                knowledge_id = self._generate_knowledge_id(tool_name, "tip", content)
                
                # Determine tip category
                parent = tip_element.find("..")
                category = parent.get("name", "general") if parent is not None else "general"
                
                artifact = KnowledgeArtifact(
                    knowledge_id=knowledge_id,
                    tool_name=tool_name,
                    feature_category=category.lower(),
                    knowledge_type=KnowledgeType.TIP,
                    content=content,
                    source=self._extract_source(tip_element),
                    engagement_metric=self._calculate_tip_value(content),
                    tags=self._extract_tags(content),
                    examples=[],
                    created_at=datetime.now()
                )
                
                self.knowledge_base[knowledge_id] = artifact
    
    async def _extract_workflow_steps(self, root: ET.Element, tool_name: str):
        """Extract workflow steps from manifest"""
        
        for workflow in root.findall(".//Workflow"):
            workflow_name = workflow.get("name", "unknown")
            
            for step in workflow.findall(".//Step"):
                content = step.text.strip() if step.text else ""
                
                if content:
                    knowledge_id = self._generate_knowledge_id(tool_name, "workflow", content)
                    
                    artifact = KnowledgeArtifact(
                        knowledge_id=knowledge_id,
                        tool_name=tool_name,
                        feature_category=workflow_name.lower().replace(" ", "_"),
                        knowledge_type=KnowledgeType.WORKFLOW_STEP,
                        content=content,
                        source="official_workflow",
                        engagement_metric=150,  # Default for workflows
                        tags=[workflow_name.lower()],
                        examples=[],
                        created_at=datetime.now()
                    )
                    
                    self.knowledge_base[knowledge_id] = artifact
    
    async def _extract_parameters(self, root: ET.Element, tool_name: str):
        """Extract parameters and technical details"""
        
        # For prompt engineering manifest
        for term in root.findall(".//Term"):
            content = term.text.strip() if term.text else ""
            
            if content and ":" in content:
                term_name, description = content.split(":", 1)
                
                knowledge_id = self._generate_knowledge_id(tool_name, "parameter", term_name)
                
                artifact = KnowledgeArtifact(
                    knowledge_id=knowledge_id,
                    tool_name=tool_name,
                    feature_category="parameters",
                    knowledge_type=KnowledgeType.PARAMETER,
                    content=f"{term_name.strip()}: {description.strip()}",
                    source="technical_reference",
                    engagement_metric=200,  # High value for technical accuracy
                    tags=[term_name.lower().strip()],
                    examples=self._extract_related_examples(root, term_name),
                    created_at=datetime.now()
                )
                
                self.knowledge_base[knowledge_id] = artifact
    
    def _generate_knowledge_id(self, tool_name: str, knowledge_type: str, content: str) -> str:
        """Generate unique knowledge ID"""
        
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{tool_name}_{knowledge_type}_{content_hash}"
    
    def _extract_parent_category(self, element: ET.Element) -> str:
        """Extract category from parent elements"""
        
        parent = element.find("..")
        if parent is not None:
            if parent.tag == "Workflow":
                return parent.get("name", "general").lower().replace(" ", "_")
            elif parent.tag == "Feature":
                return parent.get("name", "general").lower().replace(" ", "_")
        
        return "general"
    
    def _extract_source(self, element: ET.Element) -> str:
        """Extract source information"""
        
        # Look for source citations
        text = ET.tostring(element, encoding='unicode')
        
        if "reddit" in text.lower():
            if "upvoted" in text:
                return "reddit_high_engagement"
            return "reddit_community"
        elif "official" in text.lower():
            return "official_documentation"
        elif "youtube" in text.lower():
            return "youtube_tutorial"
        elif "x.com" in text.lower() or "@" in text:
            return "x_expert"
        
        return "community_knowledge"
    
    def _extract_engagement_metric(self, content: str) -> int:
        """Extract or estimate engagement metric"""
        
        # Look for engagement numbers in content
        import re
        
        # Pattern for likes/upvotes
        patterns = [
            r'(\d+)\+?\s*(?:likes|upvotes)',
            r'(?:upvoted|liked)\s*(\d+)',
            r'(\d+)k\+?\s*(?:views|likes)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1)
                if 'k' in match.group(0).lower():
                    return int(float(value) * 1000)
                return int(value)
        
        # Default based on content quality indicators
        quality_indicators = ['official', 'expert', 'pro tip', 'best practice', 'essential']
        score = 100
        
        for indicator in quality_indicators:
            if indicator in content.lower():
                score += 50
        
        return score
    
    def _calculate_tip_value(self, content: str) -> int:
        """Calculate value score for tips"""
        
        # High-value keywords
        high_value_keywords = [
            'avoid', 'essential', 'critical', 'must', 'never', 'always',
            'best practice', 'pro tip', 'expert', 'optimization',
            'performance', 'quality', 'accuracy'
        ]
        
        base_score = 100
        
        for keyword in high_value_keywords:
            if keyword in content.lower():
                base_score += 25
        
        return min(base_score, 500)  # Cap at 500
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        
        import re
        
        # Extract technical terms
        technical_patterns = [
            r'--\w+',  # Parameters
            r'\b(?:camera|angle|shot|lighting|motion|style)\b',
            r'\b(?:prompt|parameter|workflow|best practice)\b'
        ]
        
        tags = []
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, content.lower())
            tags.extend(matches)
        
        # Clean and deduplicate
        tags = list(set(tag.strip() for tag in tags))
        
        return tags[:10]  # Limit to 10 tags
    
    def _extract_examples(self, element: ET.Element) -> List[str]:
        """Extract related examples"""
        
        examples = []
        
        # Look for Example elements in same parent
        parent = element.find("..")
        if parent is not None:
            for example in parent.findall(".//Example"):
                if example.text:
                    examples.append(example.text.strip())
        
        return examples[:3]  # Limit to 3 examples
    
    def _extract_related_examples(self, root: ET.Element, term_name: str) -> List[str]:
        """Extract examples related to specific term"""
        
        examples = []
        
        for example in root.findall(".//Example"):
            if example.text and term_name.lower() in example.text.lower():
                examples.append(example.text.strip())
        
        return examples[:2]
    
    async def _save_knowledge_to_db(self):
        """Save knowledge artifacts to database"""
        
        if not self.db_connection:
            logger.warning("No database connection - knowledge stored in memory only")
            return
        
        # SQL for creating table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS mcp_tool_knowledge (
            knowledge_id VARCHAR(255) PRIMARY KEY,
            tool_name VARCHAR(100) NOT NULL,
            feature_category VARCHAR(100),
            knowledge_type VARCHAR(50),
            content TEXT NOT NULL,
            source VARCHAR(100),
            engagement_metric INTEGER DEFAULT 0,
            tags TEXT,
            examples TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            success_correlation FLOAT DEFAULT 0.0
        );
        """
        
        # Create indexes for performance
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_tool_category ON mcp_tool_knowledge(tool_name, feature_category);
        CREATE INDEX IF NOT EXISTS idx_engagement ON mcp_tool_knowledge(engagement_metric DESC);
        CREATE INDEX IF NOT EXISTS idx_success ON mcp_tool_knowledge(success_correlation DESC);
        """
        
        try:
            # Execute table creation
            await self.db_connection.execute(create_table_sql)
            await self.db_connection.execute(create_index_sql)
            
            # Insert knowledge artifacts
            for artifact in self.knowledge_base.values():
                insert_sql = """
                INSERT INTO mcp_tool_knowledge 
                (knowledge_id, tool_name, feature_category, knowledge_type, content, 
                 source, engagement_metric, tags, examples)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (knowledge_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    engagement_metric = EXCLUDED.engagement_metric,
                    tags = EXCLUDED.tags
                """
                
                await self.db_connection.execute(
                    insert_sql,
                    artifact.knowledge_id,
                    artifact.tool_name,
                    artifact.feature_category,
                    artifact.knowledge_type.value,
                    artifact.content,
                    artifact.source,
                    artifact.engagement_metric,
                    json.dumps(artifact.tags),
                    json.dumps(artifact.examples)
                )
            
            logger.info(f"💾 Saved {len(self.knowledge_base)} knowledge artifacts to database")
            
        except Exception as e:
            logger.error(f"Database save failed: {e}")
    
    async def generate_production_genome(self,
                                       archetype: str,
                                       target_tools: List[str],
                                       optimization_goal: str = "engagement") -> ProductionGenome:
        """Generate dynamic production genome with injected knowledge"""
        
        genome_id = f"genome_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(archetype.encode()).hexdigest()[:6]}"
        
        logger.info(f"🧬 Generating production genome: {genome_id}")
        
        # Query relevant knowledge for each tool
        injected_knowledge = []
        executed_steps = []
        
        for tool in target_tools:
            # Get top knowledge artifacts for this tool
            tool_knowledge = await self._query_relevant_knowledge(
                tool=tool,
                goal=optimization_goal,
                limit=self.integration_config["max_knowledge_per_step"]
            )
            
            # Create execution step with injected knowledge
            step = {
                "step_id": f"{len(executed_steps)+1:02d}_{tool}",
                "tool": tool,
                "injected_knowledge": [
                    f"knowledge_id: {k.knowledge_id} - {k.content}"
                    for k in tool_knowledge
                ],
                "knowledge_artifacts": [k.knowledge_id for k in tool_knowledge],
                "output_artifact": f"{tool}_output_{genome_id}"
            }
            
            executed_steps.append(step)
            injected_knowledge.extend([k.knowledge_id for k in tool_knowledge])
        
        # Create production genome
        genome = ProductionGenome(
            genome_id=genome_id,
            base_archetype=archetype,
            target_tools=target_tools,
            youtube_api_analytics={
                "retention_graph_points": [],
                "avg_view_duration_seconds": 0,
                "ctr": 0,
                "impressions": 0,
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            },
            executed_steps=executed_steps,
            injected_knowledge=injected_knowledge,
            performance_score=0.0,
            created_at=datetime.now()
        )
        
        # Store genome
        self.production_genomes[genome_id] = genome
        
        # Save to database
        await self._save_genome_to_db(genome)
        
        logger.info(f"✅ Generated genome with {len(injected_knowledge)} knowledge injections")
        
        return genome
    
    async def _query_relevant_knowledge(self,
                                      tool: str,
                                      goal: str,
                                      limit: int = 3) -> List[KnowledgeArtifact]:
        """Query most relevant knowledge for tool and goal"""
        
        # In-memory query (would be SQL in production)
        tool_knowledge = [
            artifact for artifact in self.knowledge_base.values()
            if artifact.tool_name == tool
        ]
        
        # Score and rank by relevance
        scored_knowledge = []
        
        for artifact in tool_knowledge:
            score = self._calculate_relevance_score(artifact, goal)
            scored_knowledge.append((artifact, score))
        
        # Sort by score and return top results
        scored_knowledge.sort(key=lambda x: x[1], reverse=True)
        
        return [artifact for artifact, _ in scored_knowledge[:limit]]
    
    def _calculate_relevance_score(self, artifact: KnowledgeArtifact, goal: str) -> float:
        """Calculate relevance score for knowledge artifact"""
        
        base_score = artifact.engagement_metric / 1000.0  # Normalize
        
        # Goal-based weighting
        goal_weights = {
            "engagement": {
                "tip": 1.2,
                "best_practice": 1.5,
                "workflow_step": 1.0,
                "parameter": 0.8
            },
            "quality": {
                "parameter": 1.5,
                "best_practice": 1.3,
                "workflow_step": 1.1,
                "tip": 0.9
            },
            "speed": {
                "workflow_step": 1.5,
                "tip": 1.2,
                "parameter": 1.0,
                "best_practice": 0.9
            }
        }
        
        type_weight = goal_weights.get(goal, {}).get(artifact.knowledge_type.value, 1.0)
        
        # Source credibility multiplier
        source_multipliers = {
            "official_documentation": 1.5,
            "reddit_high_engagement": 1.3,
            "youtube_tutorial": 1.2,
            "x_expert": 1.4,
            "community_knowledge": 1.0
        }
        
        source_multiplier = source_multipliers.get(artifact.source, 1.0)
        
        # Feature category bonus
        high_value_categories = ["prompting", "optimization", "best_practices", "camera_angles"]
        category_bonus = 1.2 if artifact.feature_category in high_value_categories else 1.0
        
        final_score = base_score * type_weight * source_multiplier * category_bonus
        
        return round(final_score, 3)
    
    async def _save_genome_to_db(self, genome: ProductionGenome):
        """Save production genome to database"""
        
        if not self.db_connection:
            return
        
        # Create genome table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS production_genomes (
            genome_id VARCHAR(255) PRIMARY KEY,
            base_archetype VARCHAR(100),
            target_tools TEXT,
            youtube_analytics TEXT,
            executed_steps TEXT,
            injected_knowledge TEXT,
            performance_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            video_id VARCHAR(255),
            channel_id VARCHAR(255),
            upload_date TIMESTAMP,
            last_analytics_update TIMESTAMP
        );
        """
        
        try:
            await self.db_connection.execute(create_table_sql)
            
            insert_sql = """
            INSERT INTO production_genomes 
            (genome_id, base_archetype, target_tools, youtube_analytics, 
             executed_steps, injected_knowledge, performance_score, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            
            await self.db_connection.execute(
                insert_sql,
                genome.genome_id,
                genome.base_archetype,
                json.dumps(genome.target_tools),
                json.dumps(genome.youtube_api_analytics),
                json.dumps(genome.executed_steps),
                json.dumps(genome.injected_knowledge),
                genome.performance_score,
                genome.created_at
            )
            
        except Exception as e:
            logger.error(f"Failed to save genome: {e}")
    
    async def enhance_prompt_with_knowledge(self,
                                          base_prompt: str,
                                          tool: str,
                                          context: Dict[str, Any]) -> str:
        """Dynamically enhance prompt with relevant knowledge"""
        
        # Get relevant knowledge
        knowledge_artifacts = await self._query_relevant_knowledge(
            tool=tool,
            goal=context.get("optimization_goal", "engagement"),
            limit=3
        )
        
        if not knowledge_artifacts:
            return base_prompt
        
        # Build enhanced prompt
        enhanced_prompt = f"{base_prompt}\n\n"
        enhanced_prompt += "Apply these expert techniques for optimal results:\n"
        
        for i, artifact in enumerate(knowledge_artifacts, 1):
            enhanced_prompt += f"{i}. {artifact.content}\n"
            
            # Add examples if available
            if artifact.examples:
                enhanced_prompt += f"   Example: {artifact.examples[0]}\n"
        
        # Add tool-specific optimizations
        if tool == "veo3":
            enhanced_prompt += "\nVeo 3 Optimization: Use cinematic vocabulary and specific parameters for best results."
        elif tool == "ltx_studio":
            enhanced_prompt += "\nLTX Studio: Break into 5-10 second scenes for optimal rendering."
        elif tool == "midjourney":
            enhanced_prompt += "\nMidjourney: Use modular prompt structure with precise visual language."
        
        return enhanced_prompt
    
    async def update_genome_analytics(self,
                                    genome_id: str,
                                    youtube_analytics: Dict[str, Any]):
        """Update production genome with YouTube performance data"""
        
        if genome_id not in self.production_genomes:
            logger.warning(f"Genome {genome_id} not found")
            return
        
        genome = self.production_genomes[genome_id]
        
        # Update analytics
        genome.youtube_api_analytics.update(youtube_analytics)
        
        # Calculate performance score
        views = youtube_analytics.get("views", 0)
        avg_view_duration = youtube_analytics.get("avg_view_duration_seconds", 0)
        ctr = youtube_analytics.get("ctr", 0)
        engagement_rate = (
            youtube_analytics.get("likes", 0) + 
            youtube_analytics.get("comments", 0) + 
            youtube_analytics.get("shares", 0)
        ) / max(views, 1)
        
        # Weighted performance score
        genome.performance_score = (
            (views / 1000) * 0.3 +  # Normalize views
            (avg_view_duration / 60) * 0.3 +  # Minutes watched
            (ctr * 100) * 0.2 +  # CTR percentage
            (engagement_rate * 100) * 0.2  # Engagement percentage
        )
        
        # Update knowledge success correlations
        await self._update_knowledge_correlations(genome)
        
        # Save updates to database
        await self._update_genome_in_db(genome)
        
        logger.info(f"📊 Updated genome {genome_id} with performance score: {genome.performance_score:.2f}")
    
    async def _update_knowledge_correlations(self, genome: ProductionGenome):
        """Update success correlations for used knowledge artifacts"""
        
        if not self.db_connection:
            return
        
        # Calculate relative performance (above/below average)
        avg_performance = 50.0  # Baseline
        relative_performance = genome.performance_score / avg_performance
        
        # Update each used knowledge artifact
        for knowledge_id in genome.injected_knowledge:
            update_sql = """
            UPDATE mcp_tool_knowledge 
            SET usage_count = usage_count + 1,
                success_correlation = 
                    (success_correlation * usage_count + $1) / (usage_count + 1),
                last_used = CURRENT_TIMESTAMP
            WHERE knowledge_id = $2
            """
            
            try:
                await self.db_connection.execute(update_sql, relative_performance, knowledge_id)
            except Exception as e:
                logger.error(f"Failed to update knowledge correlation: {e}")
    
    async def _update_genome_in_db(self, genome: ProductionGenome):
        """Update genome in database with new analytics"""
        
        if not self.db_connection:
            return
        
        update_sql = """
        UPDATE production_genomes 
        SET youtube_analytics = $1,
            performance_score = $2,
            last_analytics_update = CURRENT_TIMESTAMP
        WHERE genome_id = $3
        """
        
        try:
            await self.db_connection.execute(
                update_sql,
                json.dumps(genome.youtube_api_analytics),
                genome.performance_score,
                genome.genome_id
            )
        except Exception as e:
            logger.error(f"Failed to update genome in DB: {e}")
    
    async def generate_performance_insights(self) -> List[PerformanceInsight]:
        """Generate insights from genome performance data"""
        
        insights = []
        
        # Analyze high-performing genomes
        high_performers = [
            genome for genome in self.production_genomes.values()
            if genome.performance_score > 70.0  # Top performers
        ]
        
        # Count knowledge usage in high performers
        knowledge_usage = {}
        
        for genome in high_performers:
            for knowledge_id in genome.injected_knowledge:
                if knowledge_id not in knowledge_usage:
                    knowledge_usage[knowledge_id] = {"count": 0, "total_score": 0}
                
                knowledge_usage[knowledge_id]["count"] += 1
                knowledge_usage[knowledge_id]["total_score"] += genome.performance_score
        
        # Generate insights
        for knowledge_id, usage_data in knowledge_usage.items():
            if usage_data["count"] >= 3:  # Minimum sample size
                
                avg_score = usage_data["total_score"] / usage_data["count"]
                
                # Get knowledge artifact
                artifact = self.knowledge_base.get(knowledge_id)
                if not artifact:
                    continue
                
                # Calculate confidence interval (simplified)
                confidence_lower = avg_score * 0.9
                confidence_upper = avg_score * 1.1
                
                insight = PerformanceInsight(
                    insight_id=f"insight_{knowledge_id}_{int(datetime.now().timestamp())}",
                    knowledge_id=knowledge_id,
                    correlation_metric="performance_score",
                    positive_impact_score=avg_score / 100.0,  # Normalize to 0-1
                    sample_size=usage_data["count"],
                    confidence_interval=(confidence_lower / 100.0, confidence_upper / 100.0),
                    recommendation=self._generate_insight_recommendation(artifact, avg_score)
                )
                
                insights.append(insight)
                self.performance_insights[insight.insight_id] = insight
        
        # Sort by impact score
        insights.sort(key=lambda x: x.positive_impact_score, reverse=True)
        
        logger.info(f"🧠 Generated {len(insights)} performance insights")
        
        return insights
    
    def _generate_insight_recommendation(self, artifact: KnowledgeArtifact, avg_score: float) -> str:
        """Generate recommendation based on knowledge performance"""
        
        if avg_score > 80:
            return f"High impact: Prioritize '{artifact.content[:50]}...' for {artifact.tool_name} workflows"
        elif avg_score > 60:
            return f"Moderate impact: Consider '{artifact.content[:50]}...' for targeted improvements"
        else:
            return f"Low impact: Test alternatives to '{artifact.content[:50]}...' for better results"
    
    async def recommend_champion_genome(self,
                                      archetype: str,
                                      target_platform: str = "youtube") -> Dict[str, Any]:
        """Recommend optimal production genome based on performance data"""
        
        # Get top performing insights
        top_insights = sorted(
            self.performance_insights.values(),
            key=lambda x: x.positive_impact_score,
            reverse=True
        )[:5]
        
        # Build recommendation
        recommendation = {
            "archetype": archetype,
            "platform": target_platform,
            "recommended_tools": [],
            "champion_knowledge": [],
            "expected_performance_score": 0.0,
            "confidence": 0.0,
            "reasoning": []
        }
        
        # Determine optimal tools based on archetype
        if "short" in archetype.lower():
            recommendation["recommended_tools"] = ["veo3", "ltx_studio"]
        else:
            recommendation["recommended_tools"] = ["midjourney", "veo3"]
        
        # Add champion knowledge artifacts
        for insight in top_insights:
            artifact = self.knowledge_base.get(insight.knowledge_id)
            if artifact and artifact.tool_name in recommendation["recommended_tools"]:
                recommendation["champion_knowledge"].append({
                    "knowledge_id": insight.knowledge_id,
                    "content": artifact.content,
                    "impact_score": insight.positive_impact_score
                })
        
        # Calculate expected performance
        if recommendation["champion_knowledge"]:
            avg_impact = sum(
                k["impact_score"] for k in recommendation["champion_knowledge"]
            ) / len(recommendation["champion_knowledge"])
            
            recommendation["expected_performance_score"] = avg_impact * 100
            recommendation["confidence"] = min(avg_impact + 0.2, 0.95)
        
        # Generate reasoning
        recommendation["reasoning"] = [
            f"Based on {len(self.production_genomes)} analyzed productions",
            f"Top performing knowledge artifacts identified with {recommendation['confidence']:.0%} confidence",
            f"Expected performance score: {recommendation['expected_performance_score']:.1f}/100"
        ]
        
        logger.info(f"🏆 Recommended champion genome for {archetype}: {recommendation['expected_performance_score']:.1f} expected score")
        
        return recommendation


async def main():
    """Test knowledge integration system"""
    
    # Initialize system
    knowledge_system = MCPKnowledgeIntegration()
    
    # Simulate manifest ingestion
    manifest_files = [
        "veo3_tutorial_manifest.xml",
        "ltx_studio_tutorial_manifest.xml",
        "prompt_engineering_manifest.xml"
    ]
    
    # Note: In production, these would be actual XML files
    logger.info("📚 Knowledge Integration System Demo")
    
    # Generate sample genome
    genome = await knowledge_system.generate_production_genome(
        archetype="Sensory_Morph_Short_v1",
        target_tools=["veo3", "ltx_studio"],
        optimization_goal="engagement"
    )
    
    print(f"\n🧬 Generated Production Genome:")
    print(f"ID: {genome.genome_id}")
    print(f"Archetype: {genome.base_archetype}")
    print(f"Tools: {', '.join(genome.target_tools)}")
    print(f"Knowledge Injections: {len(genome.injected_knowledge)}")
    
    # Simulate analytics update
    sample_analytics = {
        "views": 15000,
        "avg_view_duration_seconds": 45,
        "ctr": 0.082,
        "likes": 850,
        "comments": 125,
        "shares": 95
    }
    
    await knowledge_system.update_genome_analytics(genome.genome_id, sample_analytics)
    
    print(f"\n📊 Updated Performance Score: {genome.performance_score:.2f}")
    
    # Generate insights
    insights = await knowledge_system.generate_performance_insights()
    
    if insights:
        print(f"\n🧠 Top Performance Insights:")
        for insight in insights[:3]:
            print(f"  • Knowledge {insight.knowledge_id}: {insight.positive_impact_score:.2f} impact")
    
    # Get champion recommendation
    recommendation = await knowledge_system.recommend_champion_genome("Pixel_to_Person_Short_v1")
    
    print(f"\n🏆 Champion Genome Recommendation:")
    print(f"Expected Performance: {recommendation['expected_performance_score']:.1f}")
    print(f"Confidence: {recommendation['confidence']:.0%}")
    print(f"Tools: {', '.join(recommendation['recommended_tools'])}")


if __name__ == "__main__":
    asyncio.run(main())