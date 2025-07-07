"""
YouTube Production Flow
Main workflow for automated video generation and upload using Veo 3 via AI Ultra subscription
"""

import sys
import os
import logging
sys.path.append('..')
from flow_framework import func as flow_func

# Configure production logging
logger = logging.getLogger(__name__)
from tools.veo_tool_functions import (
    check_veo3_connection, 
    generate_veo3_video_complete,
    fallback_to_imagen
)

# Add parent directory for Tenxsom AI imports
sys.path.append('/home/golde/tenxsom-ai-vertex')
from agents.youtube_expert.main import YouTubePlatformExpert, ContentCategory


@flow_func
def generate_video_prompt(topic: str, duration: int = 5) -> str:
    """
    Generate an optimized prompt for Veo 3 video generation using YouTube expert agent
    
    Args:
        topic: The main topic/theme for the video
        duration: Target duration in seconds
        
    Returns:
        Optimized prompt for video generation
    """
    
    try:
        # Initialize YouTube expert agent for strategic prompt optimization
        youtube_expert = YouTubePlatformExpert()
        
        # Get trend-aware content optimization for the topic
        content_strategy = youtube_expert.optimize_content_for_platform(
            content_idea=topic,
            target_platform="youtube",
            target_audience="general",
            performance_goals=["engagement", "monetization"]
        )
        
        # Extract strategic elements from agent recommendations
        optimization_tips = content_strategy.get("optimization_strategy", {})
        visual_elements = optimization_tips.get("visual_elements", [])
        engagement_hooks = optimization_tips.get("engagement_hooks", [])
        
        # Enhanced style elements based on expert recommendations
        style_elements = [
            "cinematic quality",
            "4K ultra HD", 
            "professional lighting",
            "smooth camera movement"
        ]
        
        # Add agent-recommended visual elements
        if visual_elements:
            style_elements.extend(visual_elements[:2])  # Take top 2 recommendations
        
        # Build strategic prompt with agent intelligence
        enhanced_prompt = f"""
A {duration}-second cinematic video about {topic}. 
Features: {', '.join(style_elements)}.
Scene: Dynamic and engaging visuals with natural movement{', focusing on ' + engagement_hooks[0] if engagement_hooks else ''}.
Style: Modern, high-quality production optimized for YouTube monetization.
Audio: Environmental sounds and atmosphere.
Movement: Smooth transitions and compelling visual storytelling.
""".strip()
        
        logger.info(f"Generated strategic prompt for topic: {topic}")
        return enhanced_prompt
        
    except Exception as e:
        logger.warning(f"YouTube expert agent failed for prompt generation: {e}")
        
        # Fallback to basic prompt optimization
        style_elements = [
            "cinematic quality",
            "4K ultra HD",
            "professional lighting", 
            "smooth camera movement"
        ]
        
        enhanced_prompt = f"""
A {duration}-second cinematic video about {topic}. 
Features: {', '.join(style_elements)}.
Scene: Dynamic and engaging visuals with natural movement.
Style: Modern, high-quality production suitable for YouTube.
Audio: Environmental sounds and atmosphere.
Movement: Smooth transitions and compelling visual storytelling.
""".strip()
        
        return enhanced_prompt


@flow_func 
async def check_service_availability() -> dict:
    """Check availability of video generation services"""
    
    logger.info("Checking Veo 3 service availability...")
    
    # Check Veo 3 connection
    veo_status = await check_veo3_connection()
    
    return {
        "veo3_available": veo_status.get("veo3_available", False),
        "veo3_status": veo_status.get("status", "unknown"),
        "fallback_needed": not veo_status.get("veo3_available", False),
        "service_details": veo_status
    }


@flow_func
async def generate_video_content(prompt: str, duration: int = 5, 
                               aspect_ratio: str = "16:9") -> str:
    """
    Generate video content using available services
    
    Args:
        prompt: Video generation prompt
        duration: Video duration in seconds
        aspect_ratio: Video aspect ratio for YouTube
        
    Returns:
        Video URL or base64 image data (fallback)
    """
    
    try:
        # Attempt Veo 3 generation
        logger.info(f"Generating {duration}s video with Veo 3...")
        video_url = await generate_veo3_video_complete(
            prompt=prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            include_audio=True,
            max_wait_minutes=10
        )
        
        return {
            "type": "video",
            "url": video_url,
            "duration": duration,
            "format": "mp4",
            "audio_included": True
        }
        
    except Exception as veo_error:
        logger.warning(f"Veo 3 failed: {veo_error}")
        logger.info("Falling back to Imagen for image generation...")
        
        try:
            # Fallback to image generation
            image_data = await fallback_to_imagen(prompt)
            
            return {
                "type": "image",
                "data": image_data,
                "format": "base64",
                "fallback": True,
                "original_error": str(veo_error)
            }
            
        except Exception as imagen_error:
            raise Exception(f"Both Veo 3 and Imagen failed. Veo: {veo_error}, Imagen: {imagen_error}")


@flow_func
def create_youtube_metadata(topic: str, video_duration: int) -> dict:
    """
    Generate optimized YouTube metadata using YouTube expert agent strategy
    
    Args:
        topic: Video topic
        video_duration: Duration in seconds
        
    Returns:
        YouTube metadata dictionary optimized for monetization
    """
    
    try:
        # Initialize YouTube expert agent for metadata optimization
        youtube_expert = YouTubePlatformExpert()
        
        # Get strategic content optimization for metadata
        content_strategy = youtube_expert.optimize_content_for_platform(
            content_idea=topic,
            target_platform="youtube",
            target_audience="general",
            performance_goals=["engagement", "monetization", "discovery"]
        )
        
        # Extract strategic elements
        optimization = content_strategy.get("optimization_strategy", {})
        seo_keywords = optimization.get("seo_keywords", [])
        engagement_hooks = optimization.get("engagement_hooks", [])
        content_structure = optimization.get("content_structure", {})
        
        # Generate strategic title with SEO optimization
        title_hook = engagement_hooks[0] if engagement_hooks else "Amazing"
        seo_keyword = seo_keywords[0] if seo_keywords else topic
        title = f"{title_hook} {seo_keyword} | {video_duration}s AI Video"
        
        # Generate strategic description with engagement and SEO
        description_hook = content_structure.get("hook", f"Watch this incredible {video_duration}-second video about {topic}!")
        
        description = f"""
🎬 {description_hook}

{content_structure.get('main_points', [f'Generated using cutting-edge AI technology for stunning visual quality.'])[0] if content_structure.get('main_points') else 'Generated using cutting-edge AI technology for stunning visual quality.'}

🔔 Subscribe for more AI-generated content!
👍 Like if you enjoyed this video
💬 Comment your video requests below

#{' #'.join(seo_keywords[:5])} #AI #VideoGeneration #YouTube

Created with Tenxsom AI - Pushing the boundaries of AI content creation.
""".strip()
        
        # Generate strategic tags with SEO keywords
        tags = ["AI generated", "video generation", "artificial intelligence"]
        tags.extend(seo_keywords[:5])  # Add top 5 SEO keywords
        tags.extend([topic, f"{topic} video"])
        
        # Determine optimal category
        category_mapping = {
            "business": "Education",
            "tech": "Science & Technology", 
            "entertainment": "Entertainment",
            "education": "Education",
            "gaming": "Gaming"
        }
        
        category = "Science & Technology"  # Default
        for key, cat in category_mapping.items():
            if key.lower() in topic.lower():
                category = cat
                break
        
        logger.info(f"Generated strategic metadata for topic: {topic}")
        
        return {
            "title": title,
            "description": description,
            "tags": tags,
            "category": category,
            "privacy": "public",
            "duration": video_duration,
            "optimization_strategy": optimization
        }
        
    except Exception as e:
        logger.warning(f"YouTube expert agent failed for metadata generation: {e}")
        
        # Fallback to basic metadata
        title = f"Amazing {topic.title()} | {video_duration}s AI Generated Video"
        
        description = f"""
🎬 Watch this incredible {video_duration}-second video about {topic}!

Generated using cutting-edge AI technology for stunning visual quality.

🔔 Subscribe for more AI-generated content!
👍 Like if you enjoyed this video
💬 Comment your video requests below

#AI #VideoGeneration #YouTube #Technology #{topic.replace(' ', '')}

Created with Tenxsom AI - Pushing the boundaries of AI content creation.
""".strip()
        
        tags = [
            "AI generated",
            "video generation", 
            "artificial intelligence",
            "technology",
            "YouTube content",
            topic,
            f"{topic} video",
            "AI technology"
        ]
        
        return {
            "title": title,
            "description": description,
            "tags": tags,
            "category": "Science & Technology",
            "privacy": "public",
            "duration": video_duration
        }


@flow_func
async def main_youtube_production_flow(topic: str, duration: int = 5, 
                                     aspect_ratio: str = "16:9") -> dict:
    """
    Main production flow for generating YouTube videos
    
    Args:
        topic: Video topic/theme
        duration: Target video duration in seconds
        aspect_ratio: Video aspect ratio (16:9 for YouTube)
        
    Returns:
        Complete production result with video and metadata
    """
    
    logger.info(f"Starting YouTube production for topic: '{topic}'")
    
    # Step 1: Check service availability
    service_status = await check_service_availability()
    logger.info(f"Service status: {service_status}")
    
    # Step 2: Generate optimized prompt
    enhanced_prompt = generate_video_prompt(topic, duration)
    logger.info(f"Generated prompt: {enhanced_prompt[:100]}...")
    
    # Step 3: Generate video content
    video_result = await generate_video_content(
        prompt=enhanced_prompt,
        duration=duration,
        aspect_ratio=aspect_ratio
    )
    logger.info(f"Generated content type: {video_result.get('type', 'unknown')}")
    
    # Step 4: Create YouTube metadata
    metadata = create_youtube_metadata(topic, duration)
    logger.info(f"Created metadata: {metadata['title']}")
    
    # Step 5: Compile final result
    production_result = {
        "status": "completed",
        "topic": topic,
        "content": video_result,
        "metadata": metadata,
        "service_status": service_status,
        "ready_for_upload": video_result.get("type") == "video",
        "requires_manual_processing": video_result.get("type") == "image"
    }
    
    if production_result["ready_for_upload"]:
        logger.info("Video ready for YouTube upload!")
    else:
        logger.warning("Generated image content - requires manual video creation")
    
    return production_result


@flow_func
async def batch_production_flow(topics: list, duration: int = 5) -> list:
    """
    Batch production flow for multiple videos
    
    Args:
        topics: List of video topics
        duration: Duration for each video
        
    Returns:
        List of production results
    """
    
    logger.info(f"Starting batch production for {len(topics)} videos")
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        logger.info(f"Processing {i}/{len(topics)}: {topic}")
        
        try:
            result = await main_youtube_production_flow(
                topic=topic,
                duration=duration,
                aspect_ratio="16:9"
            )
            
            result["batch_index"] = i
            result["batch_total"] = len(topics)
            results.append(result)
            
        except Exception as e:
            logger.error(f"Failed to process '{topic}': {e}")
            results.append({
                "status": "failed",
                "topic": topic,
                "error": str(e),
                "batch_index": i,
                "batch_total": len(topics)
            })
    
    # Summary
    successful = len([r for r in results if r.get("status") == "completed"])
    logger.info(f"Batch production completed: {successful}/{len(topics)} successful")
    
    return results


# Export main functions
__all__ = [
    'main_youtube_production_flow',
    'batch_production_flow',
    'generate_video_prompt',
    'check_service_availability'
]