"""
MiniMax/Hailuo AI tools for video, image, and chat generation
"""

import logging
from typing import Any, Dict

from .base import BaseTool
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class MiniMaxTools(BaseTool):
    """Tools for MiniMax/Hailuo AI"""
    
    def __init__(self, client):
        super().__init__(client, "minimax")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MiniMax tool"""
        try:
            self.validate_arguments(arguments)
            
            if tool_name == "minimax_video_create":
                return await self.create_video(arguments)
            elif tool_name == "minimax_image_create":
                return await self.create_image(arguments)
            elif tool_name == "minimax_chat":
                return await self.chat(arguments)
            elif tool_name == "minimax_audio_create":
                return await self.create_audio(arguments)
            elif tool_name == "minimax_voice_clone":
                return await self.clone_voice(arguments)
            else:
                raise UseAPIValidationError(f"Unknown MiniMax tool: {tool_name}")
                
        except Exception as e:
            logger.exception(f"Error executing {tool_name}")
            return self.format_error(e, tool_name)
    
    async def create_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video using MiniMax"""
        prompt = arguments["prompt"]
        model = arguments.get("model", "video-01")
        duration = arguments.get("duration", 6)
        
        data = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/videos/create",
            data,
            "create_video",
            wait_for_completion=True
        )
        
        return self.format_response(response, "create_video")
    
    async def create_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate image using MiniMax"""
        prompt = arguments["prompt"]
        model = arguments.get("model", "image-01")
        width = arguments.get("width", 1024)
        height = arguments.get("height", 1024)
        
        data = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/images/create",
            data,
            "create_image",
            wait_for_completion=True
        )
        
        return self.format_response(response, "create_image")
    
    async def chat(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with MiniMax LLM"""
        message = arguments["message"]
        model = arguments.get("model", "text-01")
        system_prompt = arguments.get("system_prompt")
        temperature = arguments.get("temperature", 0.7)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/llm",
            data,
            "chat",
            wait_for_completion=False  # Chat is typically synchronous
        )
        
        return self.format_response(response, "chat")
    
    async def create_audio(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio using MiniMax TTS"""
        text = arguments["text"]
        voice = arguments.get("voice", "default")
        model = arguments.get("model", "speech-01")
        
        data = {
            "text": text,
            "voice": voice,
            "model": model,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/audio/create-mp3",
            data,
            "create_audio",
            wait_for_completion=True
        )
        
        return self.format_response(response, "create_audio")
    
    async def clone_voice(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Clone voice using MiniMax"""
        audio_url = arguments["audio_url"]
        name = arguments["name"]
        
        data = {
            "audio_url": audio_url,
            "name": name,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/audio/clone-voice",
            data,
            "clone_voice",
            wait_for_completion=True
        )
        
        return self.format_response(response, "clone_voice")