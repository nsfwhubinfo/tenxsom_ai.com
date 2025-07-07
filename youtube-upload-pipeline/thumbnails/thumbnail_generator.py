#!/usr/bin/env python3

"""
Thumbnail Generation Service
Creates YouTube thumbnails using Midjourney/UseAPI.net and applies A/B testing
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import httpx
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """Generates YouTube thumbnails with A/B testing capabilities"""
    
    def __init__(self, useapi_token: str = None):
        """Initialize thumbnail generator"""
        self.useapi_token = useapi_token or os.getenv("USEAPI_BEARER_TOKEN")
        self.base_url = "https://api.useapi.net/v1"
        
        # YouTube thumbnail specifications
        self.thumbnail_specs = {
            'width': int(os.getenv('THUMBNAIL_WIDTH', '1280')),
            'height': int(os.getenv('THUMBNAIL_HEIGHT', '720')),
            'quality': int(os.getenv('THUMBNAIL_QUALITY', '90')),
            'format': 'JPEG',
            'max_size_mb': 2.0
        }
        
        # Style templates based on your YouTube strategy
        self.style_templates = {
            'educational': {
                'style': 'clean, professional, educational, high contrast text',
                'colors': ['#0066CC', '#FFFFFF', '#333333'],
                'text_style': 'bold, clear, readable',
                'composition': 'focused subject, minimal background'
            },
            'entertainment': {
                'style': 'vibrant, energetic, eye-catching, dynamic',
                'colors': ['#FF6B35', '#F7931E', '#FFD700'],
                'text_style': 'bold, exciting, impactful',
                'composition': 'action-oriented, engaging expressions'
            },
            'tech': {
                'style': 'modern, sleek, futuristic, high-tech',
                'colors': ['#00D4FF', '#0099CC', '#333333'],
                'text_style': 'modern, tech-inspired font',
                'composition': 'technology focus, clean lines'
            },
            'business': {
                'style': 'professional, authoritative, trustworthy',
                'colors': ['#1E3A8A', '#059669', '#F59E0B'],
                'text_style': 'professional, confident',
                'composition': 'business-focused, authority positioning'
            }
        }
        
        # A/B testing configurations
        self.ab_test_variations = {
            'text_position': ['top', 'bottom', 'center', 'left', 'right'],
            'color_schemes': ['high_contrast', 'brand_colors', 'vibrant', 'minimal'],
            'composition': ['close_up', 'wide_shot', 'split_screen', 'action'],
            'facial_expression': ['serious', 'excited', 'surprised', 'confident']
        }
    
    async def generate_thumbnail_set(self, 
                                   video_title: str,
                                   content_category: str,
                                   subject_description: str,
                                   custom_prompt: str = None,
                                   ab_test_count: int = 3) -> Dict[str, Any]:
        """
        Generate a set of thumbnails for A/B testing
        
        Args:
            video_title: Title of the video
            content_category: Category (educational, entertainment, tech, business)
            subject_description: Description of main subject/content
            custom_prompt: Custom Midjourney prompt
            ab_test_count: Number of variations to generate
            
        Returns:
            Dict with generated thumbnails and metadata
        """
        logger.info(f"Generating thumbnail set for: {video_title}")
        
        # Get style template
        style_template = self.style_templates.get(content_category, self.style_templates['educational'])
        
        # Generate variations
        thumbnails = []
        
        for i in range(ab_test_count):
            variation_id = f"v{i+1}"
            
            # Create unique prompt for each variation
            prompt = self._create_thumbnail_prompt(
                video_title, 
                subject_description, 
                style_template, 
                variation_id,
                custom_prompt
            )
            
            # Generate thumbnail with Midjourney
            thumbnail_result = await self._generate_with_midjourney(prompt, variation_id)
            
            if thumbnail_result['status'] == 'success':
                # Process and optimize the generated image
                processed_thumbnail = await self._process_thumbnail(
                    thumbnail_result['image_url'],
                    video_title,
                    style_template,
                    variation_id
                )
                
                thumbnails.append({
                    'variation_id': variation_id,
                    'prompt': prompt,
                    'raw_image_url': thumbnail_result['image_url'],
                    'processed_image_path': processed_thumbnail['file_path'],
                    'metadata': {
                        'style': style_template,
                        'generation_time': thumbnail_result['generation_time'],
                        'processing_time': processed_thumbnail['processing_time'],
                        'file_size_mb': processed_thumbnail['file_size_mb']
                    }
                })
                
                logger.info(f"✅ Generated thumbnail variation {variation_id}")
            else:
                logger.error(f"❌ Failed to generate variation {variation_id}: {thumbnail_result['error']}")
        
        # Create result summary
        result = {
            'status': 'success' if thumbnails else 'failed',
            'video_title': video_title,
            'content_category': content_category,
            'thumbnails_generated': len(thumbnails),
            'thumbnails': thumbnails,
            'generation_timestamp': datetime.now().isoformat(),
            'recommended_tests': self._generate_ab_test_plan(thumbnails)
        }
        
        # Save thumbnail set metadata
        await self._save_thumbnail_metadata(result)
        
        return result
    
    def _create_thumbnail_prompt(self, 
                               title: str, 
                               subject: str, 
                               style: Dict[str, Any],
                               variation_id: str,
                               custom_prompt: str = None) -> str:
        """Create Midjourney prompt for thumbnail"""
        
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = f"YouTube thumbnail: {subject}, {title}"
        
        # Add style elements
        style_elements = [
            style['style'],
            f"colors: {', '.join(style['colors'])}",
            style['composition'],
            "YouTube thumbnail format",
            "1280x720 aspect ratio",
            "high quality",
            "professional"
        ]
        
        # Add variation-specific elements
        variation_elements = self._get_variation_elements(variation_id)
        
        full_prompt = f"{base_prompt}, {', '.join(style_elements)}, {variation_elements} --ar 16:9 --v 6"
        
        return full_prompt
    
    def _get_variation_elements(self, variation_id: str) -> str:
        """Get variation-specific prompt elements"""
        variations = {
            'v1': 'bold text overlay, high contrast, dramatic lighting',
            'v2': 'minimal text, focus on subject, bright colors',
            'v3': 'split composition, dynamic angles, action-oriented'
        }
        
        return variations.get(variation_id, 'standard composition')
    
    async def _generate_with_midjourney(self, prompt: str, variation_id: str) -> Dict[str, Any]:
        """Generate image using Midjourney via UseAPI.net"""
        logger.info(f"Generating image with Midjourney: {variation_id}")
        
        headers = {
            "Authorization": f"Bearer {self.useapi_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "model": "midjourney",
            "quality": "high"
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                start_time = datetime.now()
                
                response = await client.post(
                    f"{self.base_url}/midjourney/imagine",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generation_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        'status': 'success',
                        'image_url': result.get('image_url'),
                        'job_id': result.get('job_id'),
                        'generation_time': generation_time,
                        'prompt': prompt
                    }
                else:
                    return {
                        'status': 'error',
                        'error': f"API error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Generation failed: {e}"
            }
    
    async def _process_thumbnail(self, 
                               image_url: str, 
                               title: str, 
                               style: Dict[str, Any],
                               variation_id: str) -> Dict[str, Any]:
        """Process and optimize generated thumbnail"""
        logger.info(f"Processing thumbnail: {variation_id}")
        
        start_time = datetime.now()
        
        try:
            # Download image
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                # Save raw image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path(__file__).parent / "generated" / timestamp
                output_dir.mkdir(parents=True, exist_ok=True)
                
                raw_path = output_dir / f"raw_{variation_id}.jpg"
                with open(raw_path, 'wb') as f:
                    f.write(response.content)
            
            # Process image
            processed_path = await self._optimize_thumbnail(
                raw_path, 
                title, 
                style, 
                variation_id,
                output_dir
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            file_size_mb = processed_path.stat().st_size / (1024 * 1024)
            
            return {
                'status': 'success',
                'file_path': str(processed_path),
                'processing_time': processing_time,
                'file_size_mb': round(file_size_mb, 2)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Processing failed: {e}"
            }
    
    async def _optimize_thumbnail(self, 
                                image_path: Path, 
                                title: str, 
                                style: Dict[str, Any],
                                variation_id: str,
                                output_dir: Path) -> Path:
        """Optimize thumbnail for YouTube requirements"""
        
        # Load image
        image = Image.open(image_path)
        
        # Resize to YouTube specifications
        target_size = (self.thumbnail_specs['width'], self.thumbnail_specs['height'])
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Enhance image quality
        image = self._enhance_image(image)
        
        # Add text overlay if needed (optional)
        if len(title) < 50:  # Only add text for shorter titles
            image = self._add_text_overlay(image, title, style)
        
        # Save optimized image
        output_path = output_dir / f"optimized_{variation_id}.jpg"
        
        image.save(
            output_path,
            'JPEG',
            quality=self.thumbnail_specs['quality'],
            optimize=True
        )
        
        # Verify file size
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.thumbnail_specs['max_size_mb']:
            # Reduce quality if too large
            image.save(
                output_path,
                'JPEG',
                quality=80,
                optimize=True
            )
        
        return output_path
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Enhance image quality and contrast"""
        # Increase contrast slightly
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(1.1)
        
        # Increase sharpness slightly
        sharpness_enhancer = ImageEnhance.Sharpness(image)
        image = sharpness_enhancer.enhance(1.1)
        
        # Adjust brightness if needed
        brightness_enhancer = ImageEnhance.Brightness(image)
        image = brightness_enhancer.enhance(1.05)
        
        return image
    
    def _add_text_overlay(self, image: Image.Image, title: str, style: Dict[str, Any]) -> Image.Image:
        """Add text overlay to thumbnail (optional enhancement)"""
        # This is a basic implementation - you might want to use more sophisticated text rendering
        draw = ImageDraw.Draw(image)
        
        # Try to load a font (fallback to default if not available)
        try:
            font_size = 60
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), title, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (image.width - text_width) // 2
        y = image.height - text_height - 20  # Bottom position with margin
        
        # Add text with outline for better visibility
        outline_color = "black"
        text_color = "white"
        
        # Draw outline
        for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            draw.text((x+dx, y+dy), title, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), title, font=font, fill=text_color)
        
        return image
    
    def _generate_ab_test_plan(self, thumbnails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate A/B testing recommendations"""
        if len(thumbnails) < 2:
            return {'status': 'insufficient_variants'}
        
        return {
            'recommended_duration': '7 days',
            'success_metrics': [
                'Click-through rate (CTR)',
                'View duration',
                'Engagement rate'
            ],
            'test_strategy': {
                'phase_1': 'Equal traffic split between variants',
                'phase_2': 'Optimize towards best performer',
                'phase_3': 'Winner takes all traffic'
            },
            'monitoring_frequency': 'Daily for first 3 days, then every 2 days',
            'significance_threshold': '95% confidence level'
        }
    
    async def _save_thumbnail_metadata(self, result: Dict[str, Any]):
        """Save thumbnail generation metadata for tracking"""
        metadata_dir = Path(__file__).parent / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_file = metadata_dir / f"thumbnail_set_{timestamp}.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"Metadata saved: {metadata_file}")

def main():
    """Test thumbnail generation"""
    async def test_generation():
        print("🎨 Thumbnail Generation Test")
        print("=" * 50)
        
        generator = ThumbnailGenerator()
        
        # Test parameters
        test_video = {
            'title': 'How AI is Revolutionizing Content Creation',
            'category': 'tech',
            'subject': 'AI content creation, futuristic technology, automation'
        }
        
        print(f"📹 Test Video: {test_video['title']}")
        print(f"📂 Category: {test_video['category']}")
        print(f"🎯 Subject: {test_video['subject']}")
        
        # Check if UseAPI token is available
        if not generator.useapi_token:
            print("❌ UseAPI.net token not found")
            print("Please set USEAPI_BEARER_TOKEN environment variable")
            return
        
        print("\n🚀 Starting thumbnail generation...")
        
        # Generate thumbnail set
        result = await generator.generate_thumbnail_set(
            video_title=test_video['title'],
            content_category=test_video['category'],
            subject_description=test_video['subject'],
            ab_test_count=2  # Generate 2 variations for testing
        )
        
        if result['status'] == 'success':
            print(f"✅ Generated {result['thumbnails_generated']} thumbnails")
            
            for thumbnail in result['thumbnails']:
                print(f"\n📸 Variation {thumbnail['variation_id']}:")
                print(f"   File: {Path(thumbnail['processed_image_path']).name}")
                print(f"   Size: {thumbnail['metadata']['file_size_mb']} MB")
                print(f"   Generation: {thumbnail['metadata']['generation_time']:.1f}s")
                print(f"   Processing: {thumbnail['metadata']['processing_time']:.1f}s")
            
            print(f"\n📊 A/B Testing Plan:")
            ab_plan = result['recommended_tests']
            print(f"   Duration: {ab_plan['recommended_duration']}")
            print(f"   Metrics: {', '.join(ab_plan['success_metrics'])}")
            
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
    
    # Run test
    asyncio.run(test_generation())

if __name__ == "__main__":
    main()