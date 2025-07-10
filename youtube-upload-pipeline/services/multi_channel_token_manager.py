#!/usr/bin/env python3
"""
Multi-Channel Token Manager for YouTube OAuth
Manages refresh tokens for multiple YouTube channels
"""

import os
import json
import logging
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class MultiChannelTokenManager:
    """Manages OAuth tokens for multiple YouTube channels"""
    
    def __init__(self):
        self.token_store_path = Path("youtube-upload-pipeline/auth/channel_tokens")
        self.token_store_path.mkdir(parents=True, exist_ok=True)
        
        # Channel mapping
        self.channel_mapping = {
            "hub": {
                "channel_name": "TenxsomAI",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_HUB"),
                "token_file": "token_hub.json",
                "role": "hub"
            },
            "tech": {
                "channel_name": "Tenxsom Tech News",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_TECH"),
                "token_file": "token_tech.json",
                "role": "spoke"
            },
            "morphs": {
                "channel_name": "Tenxsom Morphs",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_MORPHS"),
                "token_file": "token_morphs.json",
                "role": "spoke"
            },
            "histories": {
                "channel_name": "Tenxsom Histories", 
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_HISTORIES"),
                "token_file": "token_histories.json",
                "role": "spoke"
            },
            "future": {
                "channel_name": "Tenxsom Future",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_FUTURE"),
                "token_file": "token_future.json",
                "role": "spoke"
            }
        }
        
        # OAuth scopes
        self.scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.readonly"
        ]
    
    def get_channel_service(self, channel_key: str):
        """Get YouTube service for specific channel"""
        if channel_key not in self.channel_mapping:
            raise ValueError(f"Unknown channel key: {channel_key}")
        
        channel_info = self.channel_mapping[channel_key]
        token_path = self.token_store_path / channel_info["token_file"]
        
        # Load credentials
        if not token_path.exists():
            # Try legacy token location
            legacy_token = Path("youtube-upload-pipeline/auth/token.json")
            if legacy_token.exists() and channel_key == "hub":
                logger.info("Using legacy token for hub channel")
                token_path = legacy_token
            else:
                raise FileNotFoundError(
                    f"No token found for channel: {channel_info['channel_name']}. "
                    f"Please run OAuth flow for this channel."
                )
        
        # Load and refresh credentials
        credentials = Credentials.from_authorized_user_file(
            str(token_path), self.scopes
        )
        
        if credentials.expired and credentials.refresh_token:
            logger.info(f"Refreshing token for {channel_info['channel_name']}")
            credentials.refresh(Request())
            
            # Save refreshed token
            with open(token_path, 'w') as f:
                f.write(credentials.to_json())
        
        # Build service
        youtube = build('youtube', 'v3', credentials=credentials)
        
        logger.info(f"YouTube service created for: {channel_info['channel_name']}")
        return youtube, channel_info
    
    def list_available_channels(self) -> Dict[str, Dict]:
        """List all configured channels and their token status"""
        channel_status = {}
        
        for key, info in self.channel_mapping.items():
            token_path = self.token_store_path / info["token_file"]
            
            # Check legacy location for hub
            if not token_path.exists() and key == "hub":
                legacy_token = Path("youtube-upload-pipeline/auth/token.json")
                if legacy_token.exists():
                    token_path = legacy_token
            
            channel_status[key] = {
                "name": info["channel_name"],
                "role": info["role"],
                "token_exists": token_path.exists(),
                "token_path": str(token_path),
                "ready": token_path.exists()
            }
        
        return channel_status
    
    def route_content_to_channel(self, archetype: str) -> str:
        """Route content to appropriate channel based on archetype"""
        archetype_to_channel = {
            "tech_news_analysis": "tech",
            "sensory_asmr_content": "morphs",
            "educational_documentary": "histories",
            "future_tech_ai": "future",
            "hub_incubator": "hub"
        }
        
        channel_key = archetype_to_channel.get(archetype, "hub")
        
        # Check if spoke channel is ready, fallback to hub
        channel_status = self.list_available_channels()
        if not channel_status[channel_key]["ready"]:
            logger.info(f"Spoke channel {channel_key} not ready, routing to hub")
            return "hub"
        
        return channel_key
    
    def get_network_analytics(self) -> Dict:
        """Get analytics across all channels"""
        network_stats = {
            "timestamp": datetime.now().isoformat(),
            "channels": {},
            "total_ready": 0,
            "total_configured": len(self.channel_mapping)
        }
        
        for key, status in self.list_available_channels().items():
            if status["ready"]:
                network_stats["total_ready"] += 1
                
                try:
                    youtube, channel_info = self.get_channel_service(key)
                    
                    # Get channel statistics
                    response = youtube.channels().list(
                        part="statistics,snippet",
                        id=channel_info["channel_id"] or "mine"
                    ).execute()
                    
                    if response["items"]:
                        stats = response["items"][0]["statistics"]
                        network_stats["channels"][key] = {
                            "name": channel_info["channel_name"],
                            "subscribers": int(stats.get("subscriberCount", 0)),
                            "views": int(stats.get("viewCount", 0)),
                            "videos": int(stats.get("videoCount", 0))
                        }
                except Exception as e:
                    logger.error(f"Failed to get stats for {key}: {e}")
        
        return network_stats


# Singleton instance
_token_manager = None

def get_token_manager() -> MultiChannelTokenManager:
    """Get singleton token manager instance"""
    global _token_manager
    if _token_manager is None:
        _token_manager = MultiChannelTokenManager()
    return _token_manager
