# UseAPI.net MCP Server

A comprehensive Model Context Protocol (MCP) server that provides seamless integration with UseAPI.net's AI services including Midjourney, Runway, MiniMax, Kling, LTX Studio, and more.

## Features

### 🎨 **Image Generation & Editing**
- **Midjourney**: Professional image generation with variations, upscaling, and blending
- **LTX Studio**: FLUX-powered image creation and editing
- **Kling**: Advanced image manipulation and enhancement
- **MiniMax**: Text-to-image generation
- **InsightFaceSwap**: Face swapping and background changing

### 🎬 **Video Generation & Processing**
- **LTX Studio**: Real-time video generation with Veo models
- **Runway**: Gen-3/Gen-4 video creation and editing
- **Kling**: Text/image-to-video with high quality output
- **MiniMax**: Video creation and agent-based generation
- **PixVerse**: Video generation with advanced effects
- **Pika**: Simple video creation from text and images

### 🎵 **Audio & Music Generation**
- **Kling**: Text-to-speech generation
- **MiniMax**: Audio creation with voice cloning
- **Mureka**: AI music generation with SkyMusic 2.0
- **TemPolor**: Royalty-free music with voice cloning

### 💬 **Large Language Models**
- **MiniMax**: Chat LLM models (MiniMax-M1, MiniMax-Text-01)

## Quick Start

### Installation

```bash
pip install useapi-mcp-server
```

### Configuration

1. Get your UseAPI.net API key from [https://useapi.net](https://useapi.net)
2. Set up authentication:

```bash
export USEAPI_API_KEY="your-api-key-here"
```

### Basic Usage

#### As an MCP Server

```python
from useapi_mcp_server import UseAPIServer

# Start the server
server = UseAPIServer(api_key="your-api-key")
server.run()
```

#### With Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "useapi": {
      "command": "python",
      "args": ["-m", "useapi_mcp_server"],
      "env": {
        "USEAPI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### Image Tools
- `midjourney_imagine` - Generate images with Midjourney
- `midjourney_upscale` - Upscale Midjourney images
- `midjourney_variations` - Create image variations
- `midjourney_describe` - Describe images for prompts
- `midjourney_blend` - Blend multiple images
- `ltx_studio_image_create` - Create images with FLUX
- `ltx_studio_image_edit` - Edit images with FLUX
- `kling_image_enhance` - Enhance images with Kling
- `minimax_image_create` - Generate images with MiniMax
- `insight_face_swap` - Swap faces in images

### Video Tools
- `ltx_studio_video_create` - Generate videos with LTX/Veo models
- `runway_image_to_video` - Convert images to videos
- `runway_video_to_video` - Transform existing videos
- `runway_lipsync` - Add lip sync to videos
- `kling_text_to_video` - Generate videos from text
- `kling_image_to_video` - Generate videos from images
- `minimax_video_create` - Create videos with MiniMax
- `pixverse_video_create` - Generate videos with PixVerse
- `pika_create` - Simple video creation with Pika

### Audio Tools
- `kling_text_to_speech` - Generate speech with Kling
- `minimax_audio_create` - Create audio with MiniMax
- `minimax_voice_clone` - Clone voices with MiniMax
- `mureka_music_create` - Generate music with Mureka
- `tempolor_music_create` - Create royalty-free music

### Chat Tools
- `minimax_chat` - Chat with MiniMax LLM models

## Example Usage

### Generate a Midjourney Image

```python
# Through MCP client
result = await client.call_tool(
    "midjourney_imagine",
    {
        "prompt": "A futuristic cityscape at sunset, cyberpunk style",
        "aspect_ratio": "16:9",
        "model": "v6.1"
    }
)
```

### Create a Video with LTX Studio

```python
result = await client.call_tool(
    "ltx_studio_video_create",
    {
        "prompt": "A serene lake with mountains in the background",
        "duration": 5,
        "aspect_ratio": "16:9",
        "model": "veo2"
    }
)
```

### Generate Music with Mureka

```python
result = await client.call_tool(
    "mureka_music_create",
    {
        "prompt": "Upbeat electronic dance music for a party",
        "duration": 30,
        "style": "electronic"
    }
)
```

## Advanced Features

### Workflow Combinations

The server supports complex workflows combining multiple services:

```python
# Generate image, then create video from it
image_result = await client.call_tool("midjourney_imagine", {...})
video_result = await client.call_tool(
    "runway_image_to_video",
    {"image_url": image_result.image_url}
)
```

### Status Tracking

All long-running operations support status tracking:

```python
# Check job status
status = await client.get_resource("useapi://jobs/job-id-123")
print(f"Status: {status.status}, Progress: {status.progress}%")
```

### Error Handling

Comprehensive error handling with retry logic:

```python
try:
    result = await client.call_tool("midjourney_imagine", {...})
except UseAPIError as e:
    print(f"API Error: {e.message}")
except UseAPIRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
```

## Resources

The server provides several resources for tracking and management:

- `useapi://jobs/{job_id}` - Individual job status
- `useapi://jobs` - List all jobs
- `useapi://models` - Available models per service
- `useapi://account` - Account information and credits
- `useapi://history` - Generation history

## Configuration

### Environment Variables

- `USEAPI_API_KEY` - Your UseAPI.net API key (required)
- `USEAPI_BASE_URL` - Base URL for API (default: https://api.useapi.net/v1)
- `USEAPI_TIMEOUT` - Request timeout in seconds (default: 300)
- `USEAPI_MAX_RETRIES` - Maximum retry attempts (default: 3)
- `USEAPI_RATE_LIMIT` - Rate limit per minute (default: 60)

### Advanced Configuration

```python
from useapi_mcp_server import UseAPIServer, UseAPIConfig

config = UseAPIConfig(
    api_key="your-key",
    timeout=600,  # 10 minutes
    max_retries=5,
    rate_limit=100,  # 100 requests per minute
    enable_webhooks=True,
    webhook_url="https://your-app.com/webhooks/useapi"
)

server = UseAPIServer(config=config)
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/tenxsom-ai/useapi-mcp-server
cd useapi-mcp-server
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
ruff check src/
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Documentation: [GitHub README](https://github.com/tenxsom-ai/useapi-mcp-server#readme)
- Issues: [GitHub Issues](https://github.com/tenxsom-ai/useapi-mcp-server/issues)
- UseAPI.net Documentation: [https://useapi.net/docs](https://useapi.net/docs)

## Changelog

### v1.0.0
- Initial release
- Full support for all UseAPI.net services
- MCP server implementation with tools and resources
- Comprehensive error handling and status tracking
- Workflow combination support
- Development tools and testing framework