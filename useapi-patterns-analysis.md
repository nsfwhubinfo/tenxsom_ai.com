# UseAPI.net Patterns Analysis from n8n-nodes-useapi

## 🔍 Key Insights from Working Implementation

Based on the n8n-nodes-useapi repository, here are the working patterns for useapi.net APIs:

## 📊 API Endpoints & Patterns

### 1. Base URLs
```typescript
const BASE_URL_V1 = 'https://api.useapi.net/v1'; // For API operations (RunwayML assets, etc.)
const BASE_URL_V2 = 'https://api.useapi.net/v2'; // For credential management and verification
```

### 2. RunwayML Gen-3 Turbo (WORKING PATTERN)
```typescript
// Line 423-432 from UseApi.node.ts
responseData = await this.helpers.request({
    method: 'POST',
    url: `${BASE_URL_V1}/runwayml/gen3turbo/create`,
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
    body: requestBody,
    json: true,
});
```

**Request Body Pattern:**
```typescript
const requestBody = {
    firstImage_assetId: firstImageAssetId,
    text_prompt: textPrompt || undefined,
    aspect_ratio: aspectRatio,
    seconds: seconds,
    // Optional parameters
    lastImage_assetId: lastImageAssetId,  // if using multiple images
    seed: seed,
    static: true,  // or camera motion parameters
    exploreMode: true,
    replyUrl: callbackUrl
};
```

### 3. Asset Upload Pattern (CRITICAL)
```typescript
// Line 340-349 from UseApi.node.ts
responseData = await this.helpers.request({
    method: 'POST',
    url: queryUrl,  // Includes name and optional params as query string
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': contentType,  // Actual MIME type of file
    },
    body: binaryData,  // Raw binary data, not FormData
    json: true,
});
```

### 4. MiniMax Video Creation
```typescript
// Line 750-759 from UseApi.node.ts
responseData = await this.helpers.request({
    method: 'POST',
    url: `${BASE_URL_V1}/minimax/videos/create`,
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
    body: requestBody,
    json: true,
});
```

## 🚀 Immediate Solutions Based on Working Patterns

### Solution 1: Use RunwayML Gen-3 Turbo (Most Promising)
This appears to be the most mature and working video API:

```bash
# First, upload an asset the correct way
curl -X POST "https://api.useapi.net/v1/runwayml/assets/?name=test_image" \
     -H "Authorization: Bearer user:1831-r8vA1WGayarXKuYwpT1PW" \
     -H "Content-Type: image/jpeg" \
     --data-binary @ai-workspace.jpg

# Then use that asset ID for video generation
curl -X POST "https://api.useapi.net/v1/runwayml/gen3turbo/create" \
     -H "Authorization: Bearer user:1831-r8vA1WGayarXKuYwpT1PW" \
     -H "Content-Type: application/json" \
     -d '{
       "firstImage_assetId": "ASSET_ID_FROM_UPLOAD",
       "text_prompt": "Sunrise over mountains, cinematic camera pan",
       "aspect_ratio": "landscape",
       "seconds": 5
     }'
```

### Solution 2: MiniMax Text-to-Video (No Asset Required)
```bash
# Create account first (if needed)
curl -X POST "https://api.useapi.net/v1/minimax/accounts/goldensonproperties@gmail.com" \
     -H "Authorization: Bearer user:1831-r8vA1WGayarXKuYwpT1PW" \
     -H "Content-Type: application/json" \
     -d '{
       "account": "goldensonproperties@gmail.com",
       "token": "YOUR_MINIMAX_TOKEN",
       "maxJobs": 1
     }'

# Create video
curl -X POST "https://api.useapi.net/v1/minimax/videos/create" \
     -H "Authorization: Bearer user:1831-r8vA1WGayarXKuYwpT1PW" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Sunrise over mountains, cinematic quality",
       "model": "video-01"
     }'
```

## 🔧 Key Differences from Our Previous Attempts

### 1. Asset Upload Method
- **Wrong**: Using FormData with multipart/form-data
- **Right**: Raw binary data with proper Content-Type header
- **Wrong**: Complex asset ID construction
- **Right**: Use exact asset ID returned from upload

### 2. Endpoint URLs
- **Wrong**: `/ltx-video/` endpoints
- **Right**: `/runwayml/` endpoints for RunwayML
- **Wrong**: Custom asset format construction
- **Right**: Use RunwayML asset system

### 3. Authentication Pattern
- **Confirmed**: `Bearer user:1831-r8vA1WGayarXKuYwpT1PW` format is correct
- **Working**: All endpoints use same auth pattern

## 📋 Action Plan Based on Working Patterns

### Phase 1: Test RunwayML Upload & Generation
1. Upload image using RunwayML asset endpoint
2. Capture returned asset ID
3. Use asset ID for Gen-3 Turbo video generation
4. Check task status until completion

### Phase 2: Set up MiniMax Account
1. Configure MiniMax account via API
2. Test text-to-video generation (no assets needed)
3. Compare quality and costs

### Phase 3: Integrate Working Solution
1. Update Tenxsom AI to use working video API
2. Test full pipeline: trend → image → video → social posting
3. Deploy production system

## 💡 Why This Should Work

1. **Proven Implementation**: n8n-nodes-useapi has 1000+ users successfully using these patterns
2. **Correct Endpoints**: Using v1 API instead of deprecated endpoints
3. **Proper Asset Handling**: Raw binary upload instead of FormData
4. **Multiple Fallbacks**: RunwayML and MiniMax both available

## 🎯 Expected Outcome

This should resolve the video generation blocking issue within 1-2 API calls, allowing us to complete the Tenxsom AI content pipeline and begin 24/7 automated content production.