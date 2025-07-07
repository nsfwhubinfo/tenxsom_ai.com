"""
Tenxsom AI Account Pool Manager
Manages multiple UseAPI.net accounts for load balancing and fault tolerance
"""

import asyncio
import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import aiohttp
from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types"""
    VEO2 = "veo2"
    VEO3 = "veo3"
    LTX_TURBO = "ltx-turbo"
    LTX_VIDEO = "ltx-video"
    FLUX = "flux"


class AccountStatus(Enum):
    """Account health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    LOW_CREDITS = "low_credits"


@dataclass
class Account:
    """Represents a UseAPI.net account"""
    id: str
    email: str
    bearer_token: str
    models: List[ModelType]
    priority: int = 0
    credit_limit: int = 1000
    
    # Runtime state
    credits: int = 0
    status: AccountStatus = AccountStatus.HEALTHY
    last_used: Optional[datetime] = None
    error_count: int = 0
    requests_today: int = 0
    last_error: Optional[str] = None
    
    def can_use_model(self, model: ModelType) -> bool:
        """Check if account can use specific model"""
        if self.status != AccountStatus.HEALTHY:
            return False
            
        if model not in self.models:
            return False
            
        # LTX Turbo doesn't require credits
        if model == ModelType.LTX_TURBO:
            return True
            
        return self.credits > self.credit_limit
        
    def update_after_use(self, success: bool, credits_used: int = 0):
        """Update account state after API call"""
        self.last_used = datetime.now()
        self.requests_today += 1
        
        if success:
            self.credits -= credits_used
            self.error_count = 0
            if self.credits < self.credit_limit and ModelType.LTX_TURBO not in self.models:
                self.status = AccountStatus.LOW_CREDITS
        else:
            self.error_count += 1
            if self.error_count >= 3:
                self.status = AccountStatus.DEGRADED
            if self.error_count >= 5:
                self.status = AccountStatus.UNAVAILABLE


class LoadBalanceStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_USED = "least_used"
    PRIORITY = "priority"
    RANDOM = "random"
    COST_OPTIMIZED = "cost_optimized"


class AccountPoolManager:
    """Manages pool of UseAPI.net accounts with load balancing"""
    
    def __init__(self, 
                 accounts_config: List[Dict],
                 strategy: LoadBalanceStrategy = LoadBalanceStrategy.COST_OPTIMIZED,
                 health_check_interval: int = 300):
        """
        Initialize account pool
        
        Args:
            accounts_config: List of account configurations
            strategy: Load balancing strategy
            health_check_interval: Seconds between health checks
        """
        self.accounts: Dict[str, Account] = {}
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.round_robin_index = 0
        self.session: Optional[ClientSession] = None
        
        # Load accounts
        for config in accounts_config:
            account = Account(
                id=config['id'],
                email=config['email'],
                bearer_token=config['bearer_token'],
                models=[ModelType(m) for m in config['models']],
                priority=config.get('priority', 0),
                credit_limit=config.get('credit_limit', 1000)
            )
            self.accounts[account.id] = account
            
        # Start health check loop
        self._health_check_task = None
        
    async def start(self):
        """Start the account pool manager"""
        self.session = aiohttp.ClientSession()
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info(f"Started account pool with {len(self.accounts)} accounts")
        
    async def stop(self):
        """Stop the account pool manager"""
        if self._health_check_task:
            self._health_check_task.cancel()
        if self.session:
            await self.session.close()
            
    async def get_account_for_model(self, 
                                   model: ModelType,
                                   prefer_free: bool = True) -> Optional[Account]:
        """
        Get best account for specific model
        
        Args:
            model: Model type needed
            prefer_free: Prefer zero-credit models when possible
            
        Returns:
            Selected account or None if unavailable
        """
        # Filter available accounts
        available = [
            acc for acc in self.accounts.values()
            if acc.can_use_model(model)
        ]
        
        if not available:
            logger.warning(f"No accounts available for model {model}")
            return None
            
        # Apply strategy
        if self.strategy == LoadBalanceStrategy.COST_OPTIMIZED:
            # Prefer LTX Turbo accounts if prefer_free is True
            if prefer_free and model != ModelType.VEO2:
                ltx_accounts = [a for a in available if ModelType.LTX_TURBO in a.models]
                if ltx_accounts:
                    available = ltx_accounts
                    
        return self._select_account(available)
        
    def _select_account(self, accounts: List[Account]) -> Account:
        """Select account based on strategy"""
        if not accounts:
            return None
            
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            selected = accounts[self.round_robin_index % len(accounts)]
            self.round_robin_index += 1
            return selected
            
        elif self.strategy == LoadBalanceStrategy.LEAST_USED:
            return min(accounts, key=lambda a: a.requests_today)
            
        elif self.strategy == LoadBalanceStrategy.PRIORITY:
            return max(accounts, key=lambda a: a.priority)
            
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(accounts)
            
        elif self.strategy == LoadBalanceStrategy.COST_OPTIMIZED:
            # Sort by: LTX Turbo first, then by credits
            def sort_key(acc):
                has_ltx = ModelType.LTX_TURBO in acc.models
                return (not has_ltx, -acc.credits)
            return sorted(accounts, key=sort_key)[0]
            
        return accounts[0]
        
    async def check_credits(self, account: Account) -> int:
        """Check account credits via API"""
        url = "https://api.useapi.net/v1/accounts/credits"
        headers = {"Authorization": f"Bearer {account.bearer_token}"}
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('credits', 0)
                else:
                    logger.error(f"Failed to check credits for {account.email}: {response.status}")
                    return account.credits
        except Exception as e:
            logger.error(f"Error checking credits for {account.email}: {e}")
            return account.credits
            
    async def _health_check_loop(self):
        """Periodic health check for all accounts"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_accounts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                
    async def _check_all_accounts(self):
        """Check health of all accounts"""
        tasks = []
        for account in self.accounts.values():
            tasks.append(self._check_account_health(account))
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _check_account_health(self, account: Account):
        """Check individual account health"""
        try:
            # Check credits
            credits = await self.check_credits(account)
            account.credits = credits
            
            # Update status based on credits
            if credits < account.credit_limit and ModelType.LTX_TURBO not in account.models:
                account.status = AccountStatus.LOW_CREDITS
            elif account.error_count >= 5:
                account.status = AccountStatus.UNAVAILABLE
            elif account.error_count >= 3:
                account.status = AccountStatus.DEGRADED
            else:
                account.status = AccountStatus.HEALTHY
                
            # Reset daily counters at midnight
            if datetime.now().hour == 0 and datetime.now().minute < 5:
                account.requests_today = 0
                
        except Exception as e:
            logger.error(f"Health check failed for {account.email}: {e}")
            account.status = AccountStatus.UNAVAILABLE
            
    def get_stats(self) -> Dict:
        """Get pool statistics"""
        total_credits = sum(acc.credits for acc in self.accounts.values())
        healthy_accounts = sum(1 for acc in self.accounts.values() if acc.status == AccountStatus.HEALTHY)
        
        return {
            "total_accounts": len(self.accounts),
            "healthy_accounts": healthy_accounts,
            "total_credits": total_credits,
            "total_requests_today": sum(acc.requests_today for acc in self.accounts.values()),
            "accounts": [
                {
                    "id": acc.id,
                    "email": acc.email,
                    "status": acc.status.value,
                    "credits": acc.credits,
                    "requests_today": acc.requests_today,
                    "models": [m.value for m in acc.models],
                    "last_used": acc.last_used.isoformat() if acc.last_used else None
                }
                for acc in self.accounts.values()
            ]
        }
        
    def emergency_ltx_mode(self):
        """Switch all accounts to LTX Turbo only mode"""
        logger.warning("EMERGENCY: Switching all accounts to LTX Turbo mode")
        for account in self.accounts.values():
            if ModelType.LTX_TURBO in account.models:
                # Temporarily restrict to LTX Turbo only
                account.models = [ModelType.LTX_TURBO]
                account.status = AccountStatus.HEALTHY
                

# Example usage
if __name__ == "__main__":
    # Example configuration
    accounts_config = [
        {
            "id": "primary",
            "email": "goldensonproperties@gmail.com",
            "bearer_token": "user:1831-r8vA1WGayarXKuYwpT1PW",
            "models": ["veo2", "ltx-turbo", "flux"],
            "priority": 1,
            "credit_limit": 5000
        },
        {
            "id": "volume-1",
            "email": "tenxsom.ai.1@gmail.com",
            "bearer_token": "user:XXXX-XXXXXXXXXXXXXXXXXX",
            "models": ["ltx-turbo"],
            "priority": 2,
            "credit_limit": 0
        },
        {
            "id": "volume-2",
            "email": "tenxsom.ai.2@gmail.com",
            "bearer_token": "user:YYYY-YYYYYYYYYYYYYYYYYY",
            "models": ["ltx-turbo"],
            "priority": 2,
            "credit_limit": 0
        }
    ]
    
    async def test_pool():
        pool = AccountPoolManager(accounts_config)
        await pool.start()
        
        # Get account for YouTube (premium)
        youtube_account = await pool.get_account_for_model(ModelType.VEO2, prefer_free=False)
        print(f"YouTube account: {youtube_account.email if youtube_account else 'None'}")
        
        # Get account for TikTok (volume)
        tiktok_account = await pool.get_account_for_model(ModelType.LTX_TURBO, prefer_free=True)
        print(f"TikTok account: {tiktok_account.email if tiktok_account else 'None'}")
        
        # Get stats
        stats = pool.get_stats()
        print(f"Pool stats: {json.dumps(stats, indent=2)}")
        
        await pool.stop()
        
    asyncio.run(test_pool())