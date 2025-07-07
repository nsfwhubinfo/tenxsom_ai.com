"""
Example workflows using the UseAPI MCP Server
"""

import asyncio
import json
from typing import Dict, Any

# Example workflows that would be executed through MCP clients


async def generate_social_media_content():
    """
    Example: Generate a complete social media post with image and video
    """
    workflow = {
        "name": "Social Media Content Generation",
        "steps": [
            {
                "tool": "midjourney_imagine",
                "arguments": {
                    "prompt": "A vibrant sunset over a mountain lake, cinematic style",
                    "aspect_ratio": "16:9",
                    "model": "v6.1"
                },
                "description": "Generate base image"
            },
            {
                "tool": "ltx_studio_video_create", 
                "arguments": {
                    "prompt": "Gentle camera movement over the lake, birds flying",
                    "duration": 10,
                    "aspect_ratio": "16:9",
                    "model": "veo2"
                },
                "description": "Create video from the generated image"
            },
            {
                "tool": "mureka_music_create",
                "arguments": {
                    "prompt": "Peaceful ambient music for nature video",
                    "duration": 10,
                    "instrumental": True
                },
                "description": "Generate background music"
            }
        ],
        "output": "Complete social media package with image, video, and audio"
    }
    return workflow


async def create_product_showcase():
    """
    Example: Create a product showcase video from a product image
    """
    workflow = {
        "name": "Product Showcase Video",
        "steps": [
            {
                "tool": "midjourney_upscale",
                "arguments": {
                    "image_id": "product_image_id",
                    "upscale_index": 1
                },
                "description": "Upscale product image for better quality"
            },
            {
                "tool": "runway_image_to_video",
                "arguments": {
                    "image_url": "upscaled_product_image_url",
                    "prompt": "Smooth 360-degree rotation showcasing the product",
                    "duration": 8,
                    "model": "gen3alpha"
                },
                "description": "Create rotating product video"
            },
            {
                "tool": "minimax_audio_create",
                "arguments": {
                    "text": "Introducing our latest innovation - experience the future today",
                    "voice": "professional"
                },
                "description": "Generate professional voiceover"
            }
        ],
        "output": "Product showcase video with professional narration"
    }
    return workflow


async def generate_educational_content():
    """
    Example: Create educational content with explanatory visuals
    """
    workflow = {
        "name": "Educational Content Creation",
        "steps": [
            {
                "tool": "ltx_studio_image_create",
                "arguments": {
                    "prompt": "Clear diagram explaining renewable energy sources",
                    "width": 1920,
                    "height": 1080
                },
                "description": "Create educational diagram"
            },
            {
                "tool": "minimax_chat",
                "arguments": {
                    "message": "Explain renewable energy in simple terms for students",
                    "model": "text-01",
                    "system_prompt": "You are an expert educator explaining complex topics simply"
                },
                "description": "Generate educational script"
            },
            {
                "tool": "minimax_audio_create",
                "arguments": {
                    "text": "[Generated script from previous step]",
                    "voice": "educator"
                },
                "description": "Create educational narration"
            }
        ],
        "output": "Educational content with visual and audio explanation"
    }
    return workflow


async def create_music_video():
    """
    Example: Create a music video with generated visuals
    """
    workflow = {
        "name": "AI Music Video Creation",
        "steps": [
            {
                "tool": "mureka_music_create",
                "arguments": {
                    "prompt": "Upbeat electronic pop song about dreams and aspirations",
                    "duration": 60,
                    "style": "electronic pop"
                },
                "description": "Generate original music"
            },
            {
                "tool": "midjourney_imagine",
                "arguments": {
                    "prompt": "Abstract colorful shapes flowing with music rhythm",
                    "aspect_ratio": "16:9",
                    "stylize": 500
                },
                "description": "Create visual concept art"
            },
            {
                "tool": "runway_image_to_video",
                "arguments": {
                    "image_url": "concept_art_url",
                    "prompt": "Shapes morphing and flowing rhythmically with beat",
                    "duration": 10,
                    "model": "gen3alpha"
                },
                "description": "Animate the visual concept"
            }
        ],
        "output": "Complete AI-generated music video"
    }
    return workflow


def print_workflow(workflow: Dict[str, Any]):
    """Print a formatted workflow example"""
    print(f"\n🎬 {workflow['name']}")
    print("=" * (len(workflow['name']) + 4))
    
    for i, step in enumerate(workflow['steps'], 1):
        print(f"\n{i}. {step['description']}")
        print(f"   Tool: {step['tool']}")
        print(f"   Arguments:")
        for key, value in step['arguments'].items():
            print(f"     {key}: {value}")
    
    print(f"\n📊 Output: {workflow['output']}")
    print("\n" + "-" * 50)


async def main():
    """Display all workflow examples"""
    print("🚀 UseAPI MCP Server - Workflow Examples")
    print("=" * 50)
    
    workflows = [
        await generate_social_media_content(),
        await create_product_showcase(),
        await generate_educational_content(),
        await create_music_video(),
    ]
    
    for workflow in workflows:
        print_workflow(workflow)
    
    print("\n💡 These workflows can be executed by calling the MCP tools in sequence")
    print("💡 Each step uses the output from previous steps as input")
    print("💡 The MCP server handles job status tracking and error handling")


if __name__ == "__main__":
    asyncio.run(main())