#!/usr/bin/env python3

"""
MCP Integration for Content Upload Orchestrator
Enhances content generation with template-based workflows
"""

import asyncio
import json
import logging
import httpx
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import existing components
from monetization_strategy_executor import GenerationResult
from agents.youtube_expert.main import YouTubePlatformExpert, ContentCategory

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MCPTemplateRequest:
    """Request for MCP template processing"""
    template_name: str
    context_variables: Dict[str, Any]
    generation_tier: str = "standard"
    target_platform: str = "youtube"


@dataclass
class MCPProductionPlan:
    """MCP template production plan"""
    template_name: str
    execution_id: str
    total_duration: int
    scenes: List[Dict[str, Any]]
    context_variables: Dict[str, Any]
    estimated_cost: float
    recommended_generation_tier: str
    global_style_profile: Dict[str, Any]


class MCPOrchestratorIntegration:
    """
    Integrates MCP template framework with the Content Upload Orchestrator
    
    Features:
    - Template-based content planning
    - Multi-modal workflow coordination (video + audio + thumbnails)
    - YouTube Expert Agent integration for template selection
    - Cost-optimized generation tier recommendation
    """
    
    def __init__(self, mcp_server_url: str = "https://tenxsom-mcp-server-540103863590.us-central1.run.app", youtube_expert: YouTubePlatformExpert = None):
        """Initialize MCP integration"""
        self.mcp_server_url = mcp_server_url
        self.youtube_expert = youtube_expert or YouTubePlatformExpert()
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Template selection strategies
        self.tier_template_mapping = {
            "premium": [
                "Documentary_Mystery_LEMMiNO_Style_v1",
                "Cinematic_Tutorial_MKBHD_v1", 
                "Aspirational_Showcase_AD_v1"
            ],
            "standard": [
                "Explainer_VoxStyle_v1",
                "Tech_News_MattWolfe_Style_v1",
                "High_Energy_Listicle_WatchMojo_v1"
            ],
            "volume": [
                "Sensory_Morph_Short_v1",
                "Satisfying_Sensory_Slice_v1",
                "Impossible_Fortnite_Play_v1",
                "Compressed_History_Timeline_v1",
                "Calm_Productivity_LoFi_v1"
            ]
        }
        
        # Platform-specific template preferences
        self.platform_template_mapping = {
            "youtube": {
                "long_form": ["Documentary_Mystery_LEMMiNO_Style_v1", "Explainer_VoxStyle_v1", "Tech_News_MattWolfe_Style_v1"],
                "shorts": ["Sensory_Morph_Short_v1", "Satisfying_Sensory_Slice_v1", "Impossible_Fortnite_Play_v1"]
            },
            "youtube_shorts": {
                "viral": ["Sensory_Morph_Short_v1", "Compressed_History_Timeline_v1"],
                "gaming": ["Impossible_Fortnite_Play_v1"],
                "asmr": ["Satisfying_Sensory_Slice_v1"],
                "productivity": ["Calm_Productivity_LoFi_v1"]
            },
            "tiktok": ["Sensory_Morph_Short_v1", "Compressed_History_Timeline_v1", "Impossible_Fortnite_Play_v1"],
            "instagram": ["Aspirational_Showcase_AD_v1", "Sensory_Morph_Short_v1", "Cinematic_Tutorial_MKBHD_v1"]
        }
    
    async def select_optimal_template(
        self, 
        topic: str, 
        content_tier: str, 
        target_platform: str,
        duration_preference: int = 30,
        content_category: str = "education"
    ) -> str:
        """
        Select optimal MCP template based on multiple factors
        
        Args:
            topic: Content topic/subject
            content_tier: premium/standard/volume
            target_platform: youtube/tiktok/instagram/x
            duration_preference: Preferred video duration in seconds
            content_category: Content category for strategic optimization
            
        Returns:
            Template name for the optimal template
        """
        logger.info(f"🎯 Selecting optimal template for topic: {topic}, tier: {content_tier}, platform: {target_platform}")
        
        # Get YouTube expert recommendation
        try:
            expert_strategy = self.youtube_expert.optimize_content_for_platform(
                content_idea=topic,
                target_platform=target_platform,
                target_audience="general",
                performance_goals=["engagement", "monetization", "discovery"]
            )
            
            optimization = expert_strategy.get("optimization_strategy", {})
            recommended_style = optimization.get("content_style", "educational")
            
            logger.info(f"📊 YouTube Expert recommends style: {recommended_style}")
            
        except Exception as e:
            logger.warning(f"⚠️ YouTube Expert unavailable: {e}")
            recommended_style = "educational"
        
        # Determine format based on duration
        if duration_preference <= 15:
            format_preference = "shorts"
        elif duration_preference <= 60:
            format_preference = "standard"
        else:
            format_preference = "long_form"
        
        # Select template based on multiple criteria
        candidate_templates = []
        
        # 1. Filter by content tier
        tier_templates = self.tier_template_mapping.get(content_tier, self.tier_template_mapping["standard"])
        
        # 2. Filter by platform and format
        platform_templates = self.platform_template_mapping.get(target_platform, {})
        if isinstance(platform_templates, dict):
            platform_filtered = platform_templates.get(format_preference, list(platform_templates.values())[0])
        else:
            platform_filtered = platform_templates
        
        # 3. Find intersection of tier and platform preferences
        candidate_templates = [t for t in tier_templates if t in platform_filtered]
        
        # 4. If no intersection, fall back to tier-based selection
        if not candidate_templates:
            candidate_templates = tier_templates
        
        # 5. Apply content-based selection logic
        if recommended_style in ["mystery", "documentary"]:
            preferred = [t for t in candidate_templates if "Mystery" in t or "Documentary" in t]
            if preferred:
                candidate_templates = preferred
        elif recommended_style in ["tech", "news", "update"]:
            preferred = [t for t in candidate_templates if "Tech" in t or "News" in t]
            if preferred:
                candidate_templates = preferred
        elif recommended_style in ["tutorial", "educational"]:
            preferred = [t for t in candidate_templates if "Tutorial" in t or "Explainer" in t]
            if preferred:
                candidate_templates = preferred
        elif recommended_style in ["entertainment", "viral"]:
            preferred = [t for t in candidate_templates if "Listicle" in t or "Morph" in t or "Fortnite" in t]
            if preferred:
                candidate_templates = preferred
        
        # Select the first candidate (could add more sophisticated selection logic)
        selected_template = candidate_templates[0] if candidate_templates else "Explainer_VoxStyle_v1"
        
        logger.info(f"✅ Selected template: {selected_template}")
        return selected_template
    
    async def generate_production_plan(
        self,
        topic: str,
        content_tier: str = "standard",
        target_platform: str = "youtube",
        duration_preference: int = 30,
        additional_context: Dict[str, Any] = None
    ) -> MCPProductionPlan:
        """
        Generate a complete production plan using MCP templates
        
        Args:
            topic: Main content topic
            content_tier: Generation quality tier
            target_platform: Target platform for optimization
            duration_preference: Preferred duration in seconds
            additional_context: Additional context variables
            
        Returns:
            Complete production plan with scene-by-scene breakdown
        """
        logger.info(f"🎬 Generating production plan for topic: {topic}")
        
        # Select optimal template
        template_name = await self.select_optimal_template(
            topic=topic,
            content_tier=content_tier,
            target_platform=target_platform,
            duration_preference=duration_preference
        )
        
        # Prepare context variables
        context_variables = {
            "topic": topic,
            "target_platform": target_platform,
            "content_tier": content_tier,
            "duration_preference": duration_preference,
            "current_date": datetime.now().strftime('%Y-%m-%d'),
            "current_time": datetime.now().strftime('%H:%M')
        }
        
        # Add additional context if provided
        if additional_context:
            context_variables.update(additional_context)
        
        # Get strategic context from YouTube Expert
        try:
            expert_strategy = self.youtube_expert.optimize_content_for_platform(
                content_idea=topic,
                target_platform=target_platform,
                target_audience="general",
                performance_goals=["engagement", "monetization", "discovery"]
            )
            
            optimization = expert_strategy.get("optimization_strategy", {})
            
            # Add expert recommendations to context
            context_variables.update({
                "seo_keywords": optimization.get("seo_keywords", []),
                "engagement_hooks": optimization.get("engagement_hooks", []),
                "main_points": optimization.get("content_structure", {}).get("main_points", []),
                "target_audience": optimization.get("target_audience", "general"),
                "monetization_strategy": optimization.get("monetization_approach", "standard")
            })
            
            logger.info(f"🧠 Enhanced context with YouTube Expert insights")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not get YouTube Expert insights: {e}")
        
        # Process template through MCP server
        try:
            response = await self.client.post(
                f"{self.mcp_server_url}/api/mcp_template_process",
                json={
                    "template_name": template_name,
                    "context_variables": context_variables
                }
            )
            response.raise_for_status()
            production_plan_data = response.json()
            
        except Exception as e:
            logger.error(f"❌ Failed to process template via MCP server: {e}")
            # Fallback to basic plan
            return self._create_fallback_production_plan(topic, context_variables)
        
        # Convert to MCPProductionPlan object
        production_plan = MCPProductionPlan(
            template_name=production_plan_data["template_name"],
            execution_id=production_plan_data["execution_id"],
            total_duration=production_plan_data["total_duration"],
            scenes=production_plan_data["scenes"],
            context_variables=production_plan_data["context_variables"],
            estimated_cost=production_plan_data["estimated_cost"],
            recommended_generation_tier=production_plan_data["recommended_generation_tier"],
            global_style_profile=production_plan_data["global_style_profile"]
        )
        
        logger.info(f"✅ Generated production plan: {production_plan.execution_id} ({production_plan.total_duration}s, {len(production_plan.scenes)} scenes)")
        
        return production_plan
    
    async def execute_multi_modal_workflow(self, production_plan: MCPProductionPlan) -> Dict[str, Any]:
        """
        Execute multi-modal content generation workflow
        
        Args:
            production_plan: Complete production plan from MCP template
            
        Returns:
            Generated content assets (video, audio, thumbnails)
        """
        logger.info(f"🎨 Executing multi-modal workflow for plan: {production_plan.execution_id}")
        
        # Initialize results
        workflow_results = {
            "execution_id": production_plan.execution_id,
            "template_name": production_plan.template_name,
            "video_clips": [],
            "audio_elements": [],
            "thumbnail_variants": [],
            "success": True,
            "errors": []
        }
        
        try:
            # 1. Generate video clips for each scene
            for i, scene in enumerate(production_plan.scenes):
                logger.info(f"🎥 Generating video for scene {i+1}/{len(production_plan.scenes)}: {scene['scene_id']}")
                
                # Process video prompts
                for video_prompt in scene.get("resolved_video_prompts", []):
                    try:
                        # Call video generation via MCP server
                        video_result = await self._generate_video_clip(video_prompt, production_plan.recommended_generation_tier)
                        workflow_results["video_clips"].append({
                            "scene_id": scene["scene_id"],
                            "clip_data": video_result,
                            "timing_offset": scene.get("timing_offset", 0),
                            "duration": scene["duration_seconds"]
                        })
                        
                    except Exception as e:
                        error_msg = f"Video generation failed for scene {scene['scene_id']}: {e}"
                        logger.error(f"❌ {error_msg}")
                        workflow_results["errors"].append(error_msg)
            
            # 2. Generate thumbnails using Midjourney via MCP
            thumbnail_prompt = self._create_thumbnail_prompt(production_plan)
            try:
                thumbnail_result = await self._generate_thumbnails(thumbnail_prompt)
                workflow_results["thumbnail_variants"] = thumbnail_result
                logger.info(f"🖼️ Generated {len(thumbnail_result)} thumbnail variants")
                
            except Exception as e:
                error_msg = f"Thumbnail generation failed: {e}"
                logger.error(f"❌ {error_msg}")
                workflow_results["errors"].append(error_msg)
            
            # 3. Generate audio elements and music
            audio_elements = self._extract_audio_requirements(production_plan)
            for audio_req in audio_elements:
                try:
                    audio_result = await self._generate_audio_element(audio_req)
                    workflow_results["audio_elements"].append(audio_result)
                    
                except Exception as e:
                    error_msg = f"Audio generation failed for {audio_req['type']}: {e}"
                    logger.error(f"❌ {error_msg}")
                    workflow_results["errors"].append(error_msg)
            
            # 4. Assess overall success
            if len(workflow_results["errors"]) > 0:
                logger.warning(f"⚠️ Workflow completed with {len(workflow_results['errors'])} errors")
                workflow_results["success"] = len(workflow_results["video_clips"]) > 0  # Success if at least some video generated
            
            logger.info(f"✅ Multi-modal workflow complete: {len(workflow_results['video_clips'])} video clips, {len(workflow_results['thumbnail_variants'])} thumbnails")
            
        except Exception as e:
            logger.error(f"❌ Multi-modal workflow failed: {e}")
            workflow_results["success"] = False
            workflow_results["errors"].append(str(e))
        
        return workflow_results
    
    async def _generate_video_clip(self, video_prompt: Dict[str, Any], generation_tier: str) -> Dict[str, Any]:
        """Generate video clip using MCP video generation tools"""
        # Determine the best video generation tool based on tier
        if generation_tier == "premium":
            tool_name = "ltx_studio_video_create"
            model = "veo3"
        elif generation_tier == "standard":
            tool_name = "ltx_studio_video_create"
            model = "ltx-video"
        else:  # volume
            tool_name = "minimax_video_create"
            model = "video-01"
        
        # Call MCP server to generate video
        response = await self.client.post(
            f"{self.mcp_server_url}/api/{tool_name}",
            json={
                "prompt": video_prompt["prompt"],
                "model": model,
                "duration": min(video_prompt.get("duration", 5), 10),
                "aspect_ratio": "16:9"  # Will be adjusted based on platform
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def _generate_thumbnails(self, thumbnail_prompt: str) -> List[Dict[str, Any]]:
        """Generate thumbnail variants using Midjourney via MCP"""
        response = await self.client.post(
            f"{self.mcp_server_url}/api/midjourney_imagine",
            json={
                "prompt": thumbnail_prompt,
                "model": "v6.1",
                "aspect_ratio": "16:9",
                "quality": "2",
                "stylize": 150
            }
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Generate variations for A/B testing
        variations = []
        if result.get("success"):
            image_id = result.get("image_id")
            for i in range(1, 5):  # Generate 4 variations
                var_response = await self.client.post(
                    f"{self.mcp_server_url}/api/midjourney_variations",
                    json={
                        "image_id": image_id,
                        "variation_index": i
                    }
                )
                if var_response.status_code == 200:
                    variations.append(var_response.json())
        
        return variations
    
    async def _generate_audio_element(self, audio_req: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio element using MCP audio tools"""
        if audio_req["type"] == "music":
            response = await self.client.post(
                f"{self.mcp_server_url}/api/mureka_music_create",
                json={
                    "prompt": audio_req["prompt"],
                    "style": audio_req.get("style", "ambient"),
                    "duration": audio_req.get("duration", 30),
                    "instrumental": True
                }
            )
        else:
            # For other audio types, could integrate additional audio generation tools
            return {"type": audio_req["type"], "status": "not_implemented"}
        
        response.raise_for_status()
        return response.json()
    
    def _create_thumbnail_prompt(self, production_plan: MCPProductionPlan) -> str:
        """Create optimized thumbnail prompt based on production plan"""
        topic = production_plan.context_variables.get("topic", "Content")
        style_profile = production_plan.global_style_profile.get("visual", {})
        style_modifiers = style_profile.get("prompt_modifiers", "high quality, engaging")
        
        return f"YouTube thumbnail for '{topic}'. {style_modifiers}, eye-catching, professional, click-worthy design, bold text overlay, dramatic lighting"
    
    def _extract_audio_requirements(self, production_plan: MCPProductionPlan) -> List[Dict[str, Any]]:
        """Extract audio generation requirements from production plan"""
        audio_reqs = []
        
        # Extract global music style
        global_audio = production_plan.global_style_profile.get("audio", {})
        if global_audio.get("music_palette"):
            audio_reqs.append({
                "type": "music",
                "prompt": global_audio["music_palette"],
                "duration": production_plan.total_duration,
                "style": "ambient"
            })
        
        # Extract scene-specific audio if needed
        for scene in production_plan.scenes:
            audio_elements = scene.get("audio_elements", {})
            if audio_elements and audio_elements.get("music_cue"):
                music_cue = audio_elements["music_cue"]
                audio_reqs.append({
                    "type": "scene_music",
                    "prompt": music_cue.get("track_style", "ambient"),
                    "duration": scene["duration_seconds"],
                    "scene_id": scene["scene_id"]
                })
        
        return audio_reqs
    
    def _create_fallback_production_plan(self, topic: str, context_variables: Dict[str, Any]) -> MCPProductionPlan:
        """Create a basic fallback production plan when MCP server is unavailable"""
        return MCPProductionPlan(
            template_name="Fallback_Basic_v1",
            execution_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            total_duration=30,
            scenes=[
                {
                    "scene_id": "01_intro",
                    "duration_seconds": 10,
                    "resolved_script_prompt": f"Introduction to {topic}",
                    "resolved_video_prompts": [{"time": 0, "prompt": f"Professional presentation about {topic}"}],
                    "audio_elements": {},
                    "on_screen_elements": []
                },
                {
                    "scene_id": "02_main",
                    "duration_seconds": 15,
                    "resolved_script_prompt": f"Main content about {topic}",
                    "resolved_video_prompts": [{"time": 0, "prompt": f"Detailed explanation of {topic}"}],
                    "audio_elements": {},
                    "on_screen_elements": []
                },
                {
                    "scene_id": "03_conclusion",
                    "duration_seconds": 5,
                    "resolved_script_prompt": f"Conclusion about {topic}",
                    "resolved_video_prompts": [{"time": 0, "prompt": f"Summary and call to action for {topic}"}],
                    "audio_elements": {},
                    "on_screen_elements": []
                }
            ],
            context_variables=context_variables,
            estimated_cost=0.0,
            recommended_generation_tier="volume",
            global_style_profile={"visual": {"prompt_modifiers": "professional, clear"}}
        )
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()