#!/usr/bin/env python3
"""
Launch Tenxsom AI Production System
First production run with content generation
"""

import asyncio
import sys
sys.path.append('/home/golde/tenxsom-ai-vertex')
from monetization_strategy_executor import MonetizationStrategyExecutor
from production_config_manager import ProductionConfigManager
from datetime import datetime

async def launch_production():
    print('🚀 TENXSOM AI PRODUCTION LAUNCH')
    print('=' * 60)
    print(f'Launch Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Target: 96 videos/day (2,880 in 30 days)')
    print(f'Strategy: YouTube Monetization (1K subs, 4K watch hours)')
    print('=' * 60)
    
    config = ProductionConfigManager()
    executor = MonetizationStrategyExecutor(config)
    
    # Generate today's content plan
    print('\n📋 Generating today\'s content plan...')
    content_plan = executor.generate_daily_content_plan()
    print(f'✅ Content plan ready: {len(content_plan)} videos scheduled')
    
    # Show breakdown
    premium = len([r for r in content_plan if r.quality_tier == 'premium'])
    standard = len([r for r in content_plan if r.quality_tier == 'standard'])
    volume = len([r for r in content_plan if r.quality_tier == 'volume'])
    
    print(f'\n📊 Today\'s Distribution:')
    print(f'   Premium (Pixverse): {premium} videos')
    print(f'   Standard (Pixverse): {standard} videos')
    print(f'   Volume (LTX Turbo): {volume} videos')
    
    # Execute first batch
    print(f'\n🎬 Executing first production batch...')
    first_batch = content_plan[:5]  # Start with 5 videos
    
    try:
        results = await executor._execute_content_generation(first_batch)
        successful = [r for r in results if r.success]
        
        print(f'\n✅ First batch complete:')
        print(f'   Generated: {len(successful)}/{len(first_batch)} videos')
        print(f'   Total credits used: {sum(r.credits_used for r in successful)}')
        print(f'   Total cost: ${sum(r.cost_usd for r in successful):.2f}')
        
        if successful:
            print(f'\n🎯 Sample generated videos:')
            for result in successful[:3]:
                print(f'   - {result.video_id} ({result.model_used})')
        
        print(f'\n🚀 PRODUCTION SYSTEM LAUNCHED SUCCESSFULLY!')
        print(f'\n📈 Daily content generation will run automatically at:')
        print(f'   06:00, 10:00, 14:00, 18:00, 22:00')
        print(f'\n💡 Monitor progress:')
        print(f'   - Telegram Bot: @TenxsomAI_bot')
        print(f'   - Analytics: python3 analytics_tracker.py --test')
        print(f'   - Logs: tail -f production/logs/*.log')
        
    except Exception as e:
        print(f'\n❌ Launch error: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        if executor.model_router:
            await executor.model_router.stop()

if __name__ == "__main__":
    asyncio.run(launch_production())