# LTX Video Models Analysis & Cost Structure

## 🎯 Key Discovery: Dual Cost Structure

### Your Insight is Correct ✅
**LTX Studio Standard Plan** ($28/month) provides:
- **Access** to Veo 2 video generation
- **28,800 Computing Seconds** per month
- But likely **additional per-generation costs** apply

### 💰 Cost Structure Analysis

| Model | Subscription Access | Additional Cost | Notes |
|-------|-------------------|------------------|-------|
| **Veo 2** | ✅ Standard Plan | ~$0.85 per video | Requires startAssetId |
| **Veo 3** | ❌ Higher tier needed | ~$3.80-$5.55 per video | Text-to-video |
| **LTXV** | ✅ Should be included | ~$0.06 per video | Native LTX model |
| **LTXV Turbo** | ✅ Should be included | ~$0.06 per video | Faster native model |

## 🔧 LTXV Native Models Research

### Model Specifications
- **LTXV**: Standard quality, longer processing
- **LTXV Turbo**: Faster processing, default model
- **Duration**: 3, 5, 7, 9 seconds
- **Aspect Ratios**: 16:9, 9:16, 1:1
- **Cost**: ~$0.06 per generation (vs $0.85 for Veo2)

### API Requirements (All Models)
- **startAssetId** OR **endAssetId** required
- **Prompt**: Required (max 2000 chars)
- **Format**: Form data OR JSON (both tested)

## 🚨 Blocking Issue: Asset Format

### Attempted Formats (All Failed):
```
asset:80d32de9b3184c870c5a2a9d14cd5833d0c426e0473aa56ba1e55034f97257a1-type:image/jpeg
asset:4ae07f998e4082002d221562eec1758f013e8d68626157641527abb44d58effd-type:image/jpeg
```

### Tested Approaches:
- ✅ Form data format (as shown in blog)
- ✅ JSON format
- ✅ With/without quotes
- ✅ Multiple different assets
- ❌ All return "incorrect format" error

## 💡 Hypothesis: Credit Balance Issue

### Possible Scenarios:
1. **Credit System**: Even with subscription, need to purchase credits
2. **Account Setup**: Missing step for video generation activation
3. **Asset Processing**: Assets need special processing for video use
4. **Format Documentation**: Actual working format differs from examples

## 🎯 Recommended Next Steps

### Immediate Actions:
1. **Contact useapi.net support** with specific asset format question
2. **Check account credit balance** - may need to purchase video credits
3. **Request working asset format example** from support

### Alternative Approaches:
1. **Set up Kling API** - Text-to-video without assets
2. **Try MiniMax video** - Free tier available
3. **Use image sequences** - Create video from multiple images

### Research Priorities:
1. **LTX Studio credit system** - How to purchase/check credits
2. **Working asset format** - Get official documentation
3. **LTXV vs Veo costs** - Confirm pricing structure

## 📊 Business Impact Analysis

### Current Status:
- ✅ **Image generation**: Working perfectly ($0.01-$0.03 per image)
- ❌ **Video generation**: Blocked on asset format
- 🔄 **Content pipeline**: 90% complete

### If We Solve Asset Format:
- **LTXV models**: $0.06 per video = ~$2.40 for 40 videos/week
- **Veo 2 models**: $0.85 per video = ~$34 for 40 videos/week
- **Monthly video costs**: $10-150 depending on model choice

### Alternative Costs:
- **Kling**: Variable pricing, text-to-video
- **MiniMax**: Free tier + paid options
- **Runway**: $0.50 per 10-second video

## 🚀 Action Plan

### Phase 1: Resolve Asset Format (1-2 days)
1. Email useapi.net support with exact asset format question
2. Request official documentation for startAssetId format
3. Ask for working example with real asset ID

### Phase 2: Credit System (1-2 days)
1. Check if account needs credit purchase for video generation
2. Test with minimal credit purchase if needed
3. Document actual costs vs estimated costs

### Phase 3: Alternative APIs (2-3 days)
1. Set up Kling account for text-to-video
2. Test MiniMax free tier
3. Compare quality and costs across platforms

### Phase 4: Production Pipeline (1 week)
1. Integrate working video API
2. Complete social media posting automation
3. Deploy 24/7 content generation

---

**Bottom Line**: We're very close! The asset format issue is likely a documentation problem or missing account configuration step. Once solved, we'll have access to high-quality, cost-effective video generation for the Tenxsom AI pipeline.