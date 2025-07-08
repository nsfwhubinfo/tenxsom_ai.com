"""
Template processor for MCP templates - converts JSON templates into executable production plans
"""

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessedScene:
    """Represents a processed scene from a template"""
    scene_id: str
    scene_type: str
    duration_seconds: int
    resolved_script_prompt: str
    resolved_video_prompts: List[Dict[str, Any]]
    audio_elements: Dict[str, Any]
    on_screen_elements: List[Dict[str, Any]]
    timing_offset: float = 0.0


@dataclass
class ProductionPlan:
    """Complete production plan generated from a template"""
    template_name: str
    execution_id: str
    total_duration: int
    global_style_profile: Dict[str, Any]
    scenes: List[ProcessedScene]
    context_variables: Dict[str, Any]
    created_at: datetime
    estimated_cost: float = 0.0
    recommended_generation_tier: str = "standard"


class TemplateProcessor:
    """Processes MCP templates into executable production plans"""
    
    def __init__(self):
        """Initialize template processor"""
        self.variable_pattern = re.compile(r'\{([^}]+)\}')
    
    def process_template(
        self, 
        template_data: Dict[str, Any], 
        context_variables: Dict[str, Any]
    ) -> ProductionPlan:
        """
        Convert a JSON template into an executable production plan
        
        Args:
            template_data: The MCP JSON template
            context_variables: Variables to substitute in the template
            
        Returns:
            ProductionPlan: Complete executable plan
        """
        execution_id = str(uuid.uuid4())
        logger.info(f"Processing template '{template_data.get('template_name')}' with execution ID {execution_id}")
        
        # Validate template structure
        self._validate_template(template_data)
        
        # Enhance context variables with template-specific data
        enhanced_context = self._enhance_context_variables(template_data, context_variables)
        
        # Process global style profile
        global_style = self._process_global_style(template_data.get('global_style_profile', {}), enhanced_context)
        
        # Process scenes
        processed_scenes = []
        current_timing_offset = 0.0
        
        for scene_data in template_data.get('scenes', []):
            processed_scene = self._process_scene(scene_data, enhanced_context, global_style)
            processed_scene.timing_offset = current_timing_offset
            current_timing_offset += processed_scene.duration_seconds
            processed_scenes.append(processed_scene)
        
        # Calculate total duration
        total_duration = sum(scene.duration_seconds for scene in processed_scenes)
        
        # Determine recommended generation tier
        recommended_tier = self._determine_generation_tier(template_data, total_duration, len(processed_scenes))
        
        # Estimate cost
        estimated_cost = self._estimate_cost(template_data, total_duration, recommended_tier)
        
        return ProductionPlan(
            template_name=template_data.get('template_name'),
            execution_id=execution_id,
            total_duration=total_duration,
            global_style_profile=global_style,
            scenes=processed_scenes,
            context_variables=enhanced_context,
            created_at=datetime.now(),
            estimated_cost=estimated_cost,
            recommended_generation_tier=recommended_tier
        )
    
    def _validate_template(self, template_data: Dict[str, Any]):
        """Validate template structure"""
        required_fields = ['template_name', 'scenes']
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Template missing required field: {field}")
        
        if not isinstance(template_data['scenes'], list) or len(template_data['scenes']) == 0:
            raise ValueError("Template must have at least one scene")
        
        # Validate each scene
        for i, scene in enumerate(template_data['scenes']):
            if 'scene_id' not in scene:
                raise ValueError(f"Scene {i} missing scene_id")
            if 'duration_estimate_seconds' not in scene:
                raise ValueError(f"Scene {scene.get('scene_id', i)} missing duration_estimate_seconds")
    
    def _enhance_context_variables(
        self, 
        template_data: Dict[str, Any], 
        context_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance context variables with template-specific data"""
        enhanced = context_variables.copy()
        
        # Add template metadata
        enhanced['template_name'] = template_data.get('template_name')
        enhanced['template_description'] = template_data.get('description', '')
        enhanced['archetype'] = template_data.get('archetype', 'generic')
        enhanced['target_platform'] = template_data.get('target_platform', 'youtube')
        enhanced['content_tier'] = template_data.get('content_tier', 'standard')
        
        # Add global style modifiers for easy access
        global_style = template_data.get('global_style_profile', {})
        if 'visual' in global_style:
            enhanced['global_visual_modifiers'] = global_style['visual'].get('prompt_modifiers', '')
        if 'audio' in global_style:
            enhanced['global_audio_style'] = global_style['audio'].get('music_palette', '')
        
        # Add timing context
        enhanced['current_date'] = datetime.now().strftime('%Y-%m-%d')
        enhanced['current_time'] = datetime.now().strftime('%H:%M')
        
        return enhanced
    
    def _process_global_style(
        self, 
        global_style_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process global style profile with variable substitution"""
        return self._substitute_variables(global_style_data, context)
    
    def _process_scene(
        self, 
        scene_data: Dict[str, Any], 
        context: Dict[str, Any],
        global_style: Dict[str, Any]
    ) -> ProcessedScene:
        """Process a single scene"""
        scene_id = scene_data['scene_id']
        scene_type = scene_data.get('scene_type', 'generic')
        duration = int(scene_data['duration_estimate_seconds'])
        
        # Add scene-specific context
        scene_context = context.copy()
        scene_context['scene_id'] = scene_id
        scene_context['scene_type'] = scene_type
        scene_context['duration_seconds'] = duration
        
        # Process script prompt
        script_prompt = scene_data.get('llm_prompt_for_script', '')
        resolved_script_prompt = self._substitute_variables(script_prompt, scene_context)
        
        # Process video prompts
        video_prompts = scene_data.get('generative_video_prompts', [])
        if isinstance(video_prompts, str):
            # Single prompt format
            video_prompts = [{"time": 0, "prompt": video_prompts}]
        elif isinstance(video_prompts, list) and video_prompts and isinstance(video_prompts[0], str):
            # List of strings format
            video_prompts = [{"time": 0, "prompt": prompt} for prompt in video_prompts]
        
        resolved_video_prompts = []
        for prompt_data in video_prompts:
            resolved_prompt = self._substitute_variables(prompt_data, scene_context)
            resolved_video_prompts.append(resolved_prompt)
        
        # Process audio elements
        audio_elements = self._substitute_variables(
            scene_data.get('audio_elements', {}), 
            scene_context
        )
        
        # Process on-screen elements
        on_screen_elements = self._substitute_variables(
            scene_data.get('on_screen_elements', []), 
            scene_context
        )
        
        return ProcessedScene(
            scene_id=scene_id,
            scene_type=scene_type,
            duration_seconds=duration,
            resolved_script_prompt=resolved_script_prompt,
            resolved_video_prompts=resolved_video_prompts,
            audio_elements=audio_elements,
            on_screen_elements=on_screen_elements
        )
    
    def _substitute_variables(self, data: Any, context: Dict[str, Any]) -> Any:
        """Recursively substitute variables in data structure"""
        if isinstance(data, str):
            # Replace variables in string
            def replace_var(match):
                var_name = match.group(1)
                # Handle nested variable access (e.g., {global_style.visual.prompt_modifiers})
                if '.' in var_name:
                    parts = var_name.split('.')
                    value = context
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            return match.group(0)  # Return original if not found
                    return str(value)
                else:
                    return str(context.get(var_name, match.group(0)))
            
            return self.variable_pattern.sub(replace_var, data)
        
        elif isinstance(data, dict):
            return {key: self._substitute_variables(value, context) for key, value in data.items()}
        
        elif isinstance(data, list):
            return [self._substitute_variables(item, context) for item in data]
        
        else:
            return data
    
    def _determine_generation_tier(
        self, 
        template_data: Dict[str, Any], 
        total_duration: int, 
        scene_count: int
    ) -> str:
        """Determine the recommended generation tier based on template characteristics"""
        content_tier = template_data.get('content_tier', 'standard')
        archetype = template_data.get('archetype', 'generic')
        
        # Premium tier for high-quality archetypes
        premium_archetypes = [
            'documentary_mystery', 'narrative_explainer', 'cinematic_tutorial',
            'aspirational_showcase', 'first_person_essay'
        ]
        
        # Volume tier for simple, fast-turnaround content
        volume_archetypes = [
            'sensory_morph_short', 'satisfying_slice', 'viral_shorts',
            'pixel_to_person', 'compressed_history'
        ]
        
        if content_tier == 'premium' or archetype in premium_archetypes:
            return 'premium'
        elif content_tier == 'volume' or archetype in volume_archetypes or total_duration <= 15:
            return 'volume'
        else:
            return 'standard'
    
    def _estimate_cost(
        self, 
        template_data: Dict[str, Any], 
        total_duration: int, 
        generation_tier: str
    ) -> float:
        """Estimate the cost of generating content from this template"""
        # Base costs per tier (in credits/dollars)
        tier_costs = {
            'premium': 100.0,  # Veo 3 Quality
            'standard': 20.0,  # Veo 3 Fast
            'volume': 0.0      # LTX Turbo (free)
        }
        
        base_cost = tier_costs.get(generation_tier, 20.0)
        
        # Additional costs for complex scenes
        scene_count = len(template_data.get('scenes', []))
        complexity_multiplier = 1.0 + (scene_count - 1) * 0.1  # 10% per additional scene
        
        # Duration multiplier for longer content
        duration_multiplier = 1.0 + (max(0, total_duration - 30) / 60) * 0.2  # 20% per minute over 30s
        
        return base_cost * complexity_multiplier * duration_multiplier
    
    def serialize_production_plan(self, plan: ProductionPlan) -> Dict[str, Any]:
        """Serialize production plan to JSON-compatible format"""
        return {
            'template_name': plan.template_name,
            'execution_id': plan.execution_id,
            'total_duration': plan.total_duration,
            'global_style_profile': plan.global_style_profile,
            'scenes': [
                {
                    'scene_id': scene.scene_id,
                    'scene_type': scene.scene_type,
                    'duration_seconds': scene.duration_seconds,
                    'timing_offset': scene.timing_offset,
                    'resolved_script_prompt': scene.resolved_script_prompt,
                    'resolved_video_prompts': scene.resolved_video_prompts,
                    'audio_elements': scene.audio_elements,
                    'on_screen_elements': scene.on_screen_elements
                }
                for scene in plan.scenes
            ],
            'context_variables': plan.context_variables,
            'created_at': plan.created_at.isoformat(),
            'estimated_cost': plan.estimated_cost,
            'recommended_generation_tier': plan.recommended_generation_tier
        }