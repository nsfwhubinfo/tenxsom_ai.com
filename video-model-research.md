# Video Model Research & Testing Results

## 🎯 Issue Discovery
**Root Cause Found**: LTX Studio Standard Plan ($28/month) specifically includes **Veo 2**, not Veo 3.

## 📋 Plan Features
- 28,800 Computing Seconds / month
- **Veo 2 video generation model** ✅
- Image & video generation
- Advanced camera controls
- Character casting & animation

## 🔧 Model Requirements Analysis

### Veo 2 (Included in Standard Plan)
- **Requires**: startAssetId (reference image)
- **Duration**: 5-8 seconds
- **Aspect Ratios**: 16:9, 9:16, 1:1
- **Audio**: No
- **Cost**: ~$0.85 per generation

### Veo 3 (NOT included - returns 402)
- **Requires**: Text prompt only
- **Duration**: 8 seconds (fixed)
- **Aspect Ratios**: 16:9 only
- **Audio**: Yes
- **Cost**: Higher tier required

### LTX/LTX Turbo (Need to test)
- **Requires**: startAssetId or endAssetId
- **Duration**: 3, 5, 7, 9 seconds
- **Cost**: ~$0.06 per generation

## 🚨 Current Blocking Issue
**Asset Format Error**: `"Parameter startAssetId has incorrect format"`

### Attempted Asset IDs:
```
asset:80d32de9b3184c870c5a2a9d14cd5833d0c426e0473aa56ba1e55034f97257a1-type:image/jpeg
```

### Generated From:
- AI workspace image (16:9)
- Successfully created via FLUX
- Viewable and downloadable

## 📊 Alternative Video Models to Test

### 1. Kling API (useapi.net)
- **Status**: Requires account setup
- **Error**: "Please configure at least one account"
- **Next**: Set up Kling account configuration

### 2. Runway API (useapi.net)
- **Status**: Not tested yet
- **Features**: Gen-3 Alpha models
- **Cost**: Pay-per-use model

### 3. MiniMax API (useapi.net)
- **Status**: Not tested yet  
- **Features**: Free tier available
- **Model**: Hailuo AI integration

### 4. Pika API (useapi.net)
- **Status**: Not tested yet
- **Features**: Video generation and editing

## 🎯 Next Action Plan

### Immediate (Asset Format Fix)
1. Research exact asset format in useapi.net docs
2. Try uploading asset specifically for video use
3. Test with different image formats (PNG vs JPEG)
4. Check if asset needs processing time

### Alternative Models
1. Set up Kling account configuration
2. Test MiniMax free tier for video
3. Explore Runway Gen-3 options
4. Compare costs and quality

### Workarounds
1. Use image-to-video with correct format
2. Create video sequences from multiple images
3. Post-process with video editing APIs

## 💡 Key Insights
- ✅ Subscription is correctly configured for Veo 2
- ❌ Asset format preventing all video generation
- 🔄 Multiple alternative video APIs available
- 💰 Cost structure is clear and reasonable

## 📝 Testing Log

| Model | Status | Error | Next Action |
|-------|--------|-------|-------------|
| Veo 3 | ❌ | 402 Payment Required | Not included in plan |
| Veo 2 | ❌ | Asset format error | Fix startAssetId format |
| LTX Turbo | ❌ | Asset format error | Fix startAssetId format |
| Kling | ❌ | Account not configured | Set up account |
| Runway | 🔄 | Not tested | Test next |
| MiniMax | 🔄 | Not tested | Test next |

---

**Bottom Line**: We have the right subscription, but need to solve the asset format issue or set up alternative video APIs.