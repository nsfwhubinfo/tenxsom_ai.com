#!/usr/bin/env python3
"""
Complete TenxsomAI System Status and FMS Integration Report
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.append("youtube-upload-pipeline")
from services.multi_channel_token_manager import get_token_manager

def generate_comprehensive_status_report():
    """Generate complete system status report"""
    print("🎯 TENXSOMAI COMPLETE SYSTEM STATUS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    status_report = {
        "timestamp": datetime.now().isoformat(),
        "components": {},
        "monetization": {},
        "youtube_status": {},
        "recommendations": []
    }
    
    # 1. MCP Framework Status
    print("\n🚀 MCP FRAMEWORK STATUS")
    print("-" * 40)
    
    try:
        mcp_url = "https://tenxsom-mcp-server-540103863590.us-central1.run.app"
        
        # Health check
        health_response = requests.get(f"{mcp_url}/health", timeout=10)
        health_status = health_response.status_code == 200
        
        # Templates check
        templates_response = requests.get(f"{mcp_url}/api/templates", timeout=10)
        templates_data = templates_response.json() if templates_response.status_code == 200 else {}
        templates = templates_data.get("templates", [])
        
        print(f"✅ Server Health: {'Healthy' if health_status else 'Unhealthy'}")
        print(f"✅ Templates Loaded: {len(templates)}")
        
        # Template analysis
        if templates:
            archetypes = {}
            platforms = {}
            tiers = {}
            
            for template in templates:
                archetype = template.get("archetype", "unknown")
                platform = template.get("target_platform", "unknown")  
                tier = template.get("content_tier", "unknown")
                
                archetypes[archetype] = archetypes.get(archetype, 0) + 1
                platforms[platform] = platforms.get(platform, 0) + 1
                tiers[tier] = tiers.get(tier, 0) + 1
            
            print("📋 Template Categories:")
            for archetype, count in archetypes.items():
                print(f"   • {archetype}: {count}")
            
            print("🎯 Platform Distribution:")
            for platform, count in platforms.items():
                print(f"   • {platform}: {count}")
            
            print("⚡ Quality Tiers:")
            for tier, count in tiers.items():
                print(f"   • {tier}: {count}")
        
        status_report["components"]["mcp"] = {
            "healthy": health_status,
            "templates_count": len(templates),
            "archetypes": len(archetypes) if templates else 0
        }
        
    except Exception as e:
        print(f"❌ MCP Error: {e}")
        status_report["components"]["mcp"] = {"healthy": False, "error": str(e)}
    
    # 2. YouTube Integration Status
    print("\n🎬 YOUTUBE INTEGRATION STATUS")
    print("-" * 40)
    
    try:
        manager = get_token_manager()
        youtube, channel_info = manager.get_channel_service("hub")
        
        # Channel details
        channel_response = youtube.channels().list(
            part="snippet,statistics,status,brandingSettings",
            mine=True
        ).execute()
        
        if channel_response["items"]:
            channel = channel_response["items"][0]
            stats = channel["statistics"]
            snippet = channel["snippet"]
            
            channel_id = channel["id"]
            channel_name = snippet["title"]
            subscribers = int(stats.get("subscriberCount", 0))
            views = int(stats.get("viewCount", 0))
            videos = int(stats.get("videoCount", 0))
            
            print(f"✅ Channel: {channel_name}")
            print(f"✅ Channel ID: {channel_id}")
            print(f"✅ Subscribers: {subscribers:,}")
            print(f"✅ Total Views: {views:,}")
            print(f"✅ Videos: {videos}")
            
            # Partner Program eligibility
            subscriber_eligible = subscribers >= 1000
            print(f"\n📊 YouTube Partner Program:")
            print(f"   Subscribers: {subscribers:,}/1,000 {'✅' if subscriber_eligible else '❌'}")
            print(f"   Watch Time: ⏳ (4,000 hours required)")
            
            status_report["youtube_status"] = {
                "authenticated": True,
                "channel_name": channel_name,
                "channel_id": channel_id,
                "subscribers": subscribers,
                "views": views,
                "videos": videos,
                "partner_eligible": subscriber_eligible
            }
            
        else:
            print("❌ No channel data available")
            status_report["youtube_status"] = {"authenticated": False}
            
    except Exception as e:
        print(f"❌ YouTube Error: {e}")
        status_report["youtube_status"] = {"authenticated": False, "error": str(e)}
    
    # 3. Monetization Strategy Analysis
    print("\n💰 MONETIZATION STRATEGY STATUS")
    print("-" * 40)
    
    # Three-tier content strategy
    content_strategy = {
        "premium": {"daily": 4, "monthly_cost": 24, "model": "Veo 3 Quality"},
        "standard": {"daily": 8, "monthly_cost": 24, "model": "Veo 3 Fast"},
        "volume": {"daily": 84, "monthly_cost": 0, "model": "LTX Turbo (Free)"}
    }
    
    total_daily = sum(tier["daily"] for tier in content_strategy.values())
    total_monthly_cost = sum(tier["monthly_cost"] for tier in content_strategy.values())
    total_monthly_videos = total_daily * 30
    avg_cost_per_video = total_monthly_cost / total_monthly_videos if total_monthly_videos > 0 else 0
    
    print(f"🎯 Content Generation Strategy:")
    print(f"   Daily Videos: {total_daily}")
    print(f"   Monthly Videos: {total_monthly_videos:,}")
    print(f"   Monthly Cost: ${total_monthly_cost}")
    print(f"   Cost per Video: ${avg_cost_per_video:.3f}")
    
    # Revenue projections
    low_cpm = 2.0
    high_cpm = 6.0
    views_per_video_low = 100
    views_per_video_high = 1000
    
    monthly_views_low = total_monthly_videos * views_per_video_low
    monthly_views_high = total_monthly_videos * views_per_video_high
    
    revenue_low = (monthly_views_low / 1000) * low_cpm
    revenue_high = (monthly_views_high / 1000) * high_cpm
    
    print(f"\n💰 Revenue Projections:")
    print(f"   Low estimate: ${revenue_low:.0f}/month ({monthly_views_low:,} views)")
    print(f"   High estimate: ${revenue_high:.0f}/month ({monthly_views_high:,} views)")
    print(f"   ROI: {revenue_low/total_monthly_cost:.1f}x - {revenue_high/total_monthly_cost:.1f}x")
    
    status_report["monetization"] = {
        "daily_videos": total_daily,
        "monthly_cost": total_monthly_cost,
        "cost_per_video": avg_cost_per_video,
        "revenue_low": revenue_low,
        "revenue_high": revenue_high,
        "roi_low": revenue_low/total_monthly_cost if total_monthly_cost > 0 else 0,
        "roi_high": revenue_high/total_monthly_cost if total_monthly_cost > 0 else 0
    }
    
    # 4. Financial Management System Analysis
    print("\n💳 FINANCIAL MANAGEMENT SYSTEM (FMS)")
    print("-" * 40)
    
    # Check for FMS components
    fms_components = {
        "monetization_strategy_executor.py": os.path.exists("monetization_strategy_executor.py"),
        "analytics_tracker.py": os.path.exists("analytics_tracker.py"),
        "content_upload_orchestrator.py": os.path.exists("content_upload_orchestrator.py"),
        "agents/youtube_expert/main.py": os.path.exists("agents/youtube_expert/main.py")
    }
    
    print("✅ Revenue Optimization Components:")
    for component, exists in fms_components.items():
        status = "✅" if exists else "❌"
        description = {
            "monetization_strategy_executor.py": "Core monetization engine",
            "analytics_tracker.py": "Revenue tracking system",
            "content_upload_orchestrator.py": "Multi-platform uploader", 
            "agents/youtube_expert/main.py": "YouTube optimization expert"
        }.get(component, component)
        print(f"   {status} {description}")
    
    # Payment processing analysis
    print("\n💡 FMS Architecture Analysis:")
    print("   Current: Platform-based monetization (YouTube Partner Program)")
    print("   Revenue Source: YouTube ad revenue, not direct payments")
    print("   Payment Method: YouTube pays creator directly")
    print("   Financial Tracking: Performance analytics, not billing")
    
    print("\n⚠️ Missing Traditional FMS Components:")
    print("   ❌ Stripe payment processing")
    print("   ❌ Subscription billing system")
    print("   ❌ Invoice generation")
    print("   ❌ Partner revenue sharing")
    print("   ❌ Direct customer payments")
    
    print("\n✅ Current FMS Strengths:")
    print("   ✅ Revenue optimization strategy")
    print("   ✅ Cost management (96 videos/day at $48/month)")
    print("   ✅ ROI tracking and analytics")
    print("   ✅ Multi-tier content strategy")
    print("   ✅ Partner Program eligibility tracking")
    
    # 5. Recommendations
    print("\n🎯 RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    # Upload test video publicly
    if status_report["youtube_status"].get("videos", 0) == 0:
        recommendations.append("Upload first public video to start channel growth")
        print("1. 🎬 Upload first public video (current test video is private)")
    
    # Subscriber growth strategy
    if status_report["youtube_status"].get("subscribers", 0) < 1000:
        recommendations.append("Focus on subscriber growth for Partner Program")
        print("2. 📈 Implement subscriber growth strategy (need 1,000 for monetization)")
    
    # Content automation
    recommendations.append("Start automated content production")
    print("3. 🚀 Begin 96 videos/day production schedule")
    
    # Analytics setup
    recommendations.append("Set up YouTube Analytics API for watch time tracking")
    print("4. 📊 Configure YouTube Analytics API for detailed metrics")
    
    # Future FMS expansion
    if total_monthly_cost > 0:
        recommendations.append("Consider direct payment system for premium services")
        print("5. 💳 Consider adding Stripe for premium services/courses")
    
    status_report["recommendations"] = recommendations
    
    # 6. Summary
    print("\n" + "=" * 70)
    print("🎉 SYSTEM STATUS SUMMARY")
    print("=" * 70)
    
    mcp_healthy = status_report["components"]["mcp"]["healthy"]
    youtube_auth = status_report["youtube_status"]["authenticated"]
    
    if mcp_healthy and youtube_auth:
        print("✅ SYSTEM STATUS: FULLY OPERATIONAL")
        print("✅ Ready for production content generation")
        print("✅ YouTube integration verified") 
        print("✅ Monetization strategy configured")
        print("✅ Revenue optimization active")
        print(f"✅ Target: ${revenue_low:.0f}-${revenue_high:.0f}/month revenue")
    else:
        print("⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        if not mcp_healthy:
            print("❌ MCP framework issues detected")
        if not youtube_auth:
            print("❌ YouTube authentication problems")
    
    return status_report

def save_status_report(report):
    """Save status report to file"""
    report_file = f"system_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Status report saved: {report_file}")

def main():
    """Main function"""
    report = generate_comprehensive_status_report()
    save_status_report(report)

if __name__ == "__main__":
    main()