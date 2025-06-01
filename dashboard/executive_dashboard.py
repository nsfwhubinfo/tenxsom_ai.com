#!/usr/bin/env python3
"""
Tenxsom AI Executive Dashboard
==============================
Unified command center for project monitoring, financial tracking, and knowledge ingestion
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
from dataclasses import dataclass, asdict

@dataclass
class DashboardMetrics:
    """Core metrics for executive view"""
    timestamp: str
    launch_status: Dict[str, str]
    financial_metrics: Dict[str, float]
    next_actions: List[str]
    health_indicators: Dict[str, str]
    knowledge_ingestion: Dict[str, int]
    stripe_metrics: Dict[str, Any]

class TenxsomDashboard:
    """Executive dashboard for Tenxsom AI project management"""
    
    def __init__(self, project_root: str = "/home/golde/Tenxsom_AI"):
        self.project_root = Path(project_root)
        self.dashboard_dir = self.project_root / "dashboard"
        self.dashboard_dir.mkdir(exist_ok=True)
        
        # Component status tracking
        self.components = {
            "sdk": {
                "name": "FMO Optimizer SDK",
                "path": self.project_root / "sdk",
                "status_file": "SDK_MVP_READY_CHECKLIST.md"
            },
            "chm": {
                "name": "Cognitive Health Monitor",
                "path": self.project_root / "chm",
                "status_file": "CHM_STATUS.md"
            },
            "payment": {
                "name": "Stripe Integration",
                "path": self.project_root / "finance/stripe_integration",
                "status_file": ".env.stripe"
            }
        }
        
    def get_launch_status(self) -> Dict[str, str]:
        """Check product launch readiness"""
        status = {
            "landing_page": "UNKNOWN",
            "payment_gateway": "UNKNOWN",
            "sdk_download": "UNKNOWN",
            "documentation": "UNKNOWN",
            "stripe_mode": "UNKNOWN"
        }
        
        # Check Stripe configuration
        stripe_env = self.project_root / "finance/stripe_integration/.env.stripe"
        if stripe_env.exists():
            with open(stripe_env, 'r') as f:
                content = f.read()
                if "STRIPE_MODE=live" in content:
                    status["stripe_mode"] = "LIVE"
                    status["payment_gateway"] = "READY"
                else:
                    status["stripe_mode"] = "TEST"
                    status["payment_gateway"] = "TEST_MODE"
        
        # Check SDK readiness
        sdk_checklist = self.project_root / "sdk/SDK_MVP_READY_CHECKLIST.md"
        if sdk_checklist.exists():
            with open(sdk_checklist, 'r') as f:
                content = f.read()
                ready_items = content.count("[x]")
                total_items = content.count("[ ]") + ready_items
                if ready_items == total_items and total_items > 0:
                    status["sdk_download"] = "VERIFIED"
                else:
                    status["sdk_download"] = f"{ready_items}/{total_items} READY"
        
        return status
    
    def get_financial_metrics(self) -> Dict[str, float]:
        """Get financial tracking metrics"""
        # In production, this would connect to Stripe API
        # For now, reading from tracking file
        metrics = {
            "daily_sales": 0,
            "daily_revenue": 0.0,
            "mrr_total": 0.0,
            "living_expense_met": 0.0,
            "reinvest_available": 0.0
        }
        
        finance_log = self.dashboard_dir / "financial_tracking.json"
        if finance_log.exists():
            with open(finance_log, 'r') as f:
                saved_metrics = json.load(f)
                metrics.update(saved_metrics)
        
        # Calculate 80/15/5 split
        if metrics["daily_revenue"] > 0:
            metrics["reinvest_available"] = metrics["daily_revenue"] * 0.80
            metrics["living_expense_met"] += metrics["daily_revenue"] * 0.15
            
        return metrics
    
    def get_stripe_metrics(self) -> Dict[str, Any]:
        """Get live Stripe metrics if available"""
        try:
            # Check if we can import stripe
            import stripe
            stripe_metrics = {
                "mode": "unknown",
                "recent_payments": 0,
                "pending_webhooks": 0
            }
            
            # Try to get account info
            try:
                account = stripe.Account.retrieve()
                stripe_metrics["mode"] = "live" if account.charges_enabled else "test"
            except:
                pass
                
            return stripe_metrics
        except ImportError:
            return {"status": "Stripe SDK not available"}
    
    def get_next_actions(self) -> List[str]:
        """Determine highest priority next actions"""
        actions = []
        
        # Check launch status
        launch_status = self.get_launch_status()
        
        if launch_status["stripe_mode"] == "TEST":
            actions.append("Switch Stripe to LIVE mode: Update .env.stripe")
        
        if "READY" not in launch_status["sdk_download"]:
            actions.append("Complete SDK checklist items")
            
        if not (self.project_root / "marketing/landing_page_live.flag").exists():
            actions.append("Deploy landing page: Run deploy_landing.sh")
            
        # Check for pending milestones
        milestone_files = list(self.project_root.glob("**/Milestone*_Report.md"))
        for mf in sorted(milestone_files)[-2:]:  # Last 2 milestones
            if "COMPLETE" not in mf.read_text():
                actions.append(f"Complete: {mf.stem}")
                
        return actions[:3]  # Top 3 actions only
    
    def get_health_indicators(self) -> Dict[str, str]:
        """System health check"""
        health = {
            "test_suite": "UNKNOWN",
            "docker_services": "UNKNOWN",
            "backup_status": "UNKNOWN",
            "knowledge_base": "UNKNOWN"
        }
        
        # Check test results
        test_results = list(self.project_root.glob("**/test_results_*.log"))
        if test_results:
            latest = max(test_results, key=lambda x: x.stat().st_mtime)
            content = latest.read_text()
            if "FAILED" in content:
                health["test_suite"] = "FAILURES"
            elif "PASSED" in content:
                health["test_suite"] = "PASSED"
                
        # Check Docker
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if "tenxsom" in result.stdout.lower():
                health["docker_services"] = "RUNNING"
            else:
                health["docker_services"] = "NOT_RUNNING"
        except:
            health["docker_services"] = "DOCKER_ERROR"
            
        # Check backups
        backup_files = list(self.project_root.glob("*.enc"))
        if backup_files:
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            days_old = (datetime.datetime.now() - datetime.datetime.fromtimestamp(latest_backup.stat().st_mtime)).days
            if days_old < 1:
                health["backup_status"] = "CURRENT"
            elif days_old < 7:
                health["backup_status"] = f"{days_old}d OLD"
            else:
                health["backup_status"] = "OUTDATED"
                
        return health
    
    def get_knowledge_ingestion_stats(self) -> Dict[str, int]:
        """Track knowledge base ingestion progress"""
        stats = {
            "notes_pending": 0,
            "notes_processed": 0,
            "txt_files_pending": 0,
            "txt_files_processed": 0,
            "total_kb_entries": 0
        }
        
        # Check ingestion directories
        notes_inbox = self.dashboard_dir / "knowledge_inbox/notes"
        txt_inbox = self.dashboard_dir / "knowledge_inbox/texts"
        processed = self.dashboard_dir / "knowledge_processed"
        
        if notes_inbox.exists():
            stats["notes_pending"] = len(list(notes_inbox.glob("*")))
        if txt_inbox.exists():
            stats["txt_files_pending"] = len(list(txt_inbox.glob("*.txt")))
        if processed.exists():
            stats["notes_processed"] = len(list(processed.glob("note_*")))
            stats["txt_files_processed"] = len(list(processed.glob("text_*")))
            
        # Count FMO entries
        fmo_files = list(self.project_root.glob("**/fmo_*.json"))
        for fmo in fmo_files:
            try:
                with open(fmo, 'r') as f:
                    data = json.load(f)
                    if "nodes" in data:
                        stats["total_kb_entries"] += len(data["nodes"])
            except:
                pass
                
        return stats
    
    def generate_dashboard(self) -> DashboardMetrics:
        """Generate complete dashboard metrics"""
        return DashboardMetrics(
            timestamp=datetime.datetime.now().isoformat(),
            launch_status=self.get_launch_status(),
            financial_metrics=self.get_financial_metrics(),
            next_actions=self.get_next_actions(),
            health_indicators=self.get_health_indicators(),
            knowledge_ingestion=self.get_knowledge_ingestion_stats(),
            stripe_metrics=self.get_stripe_metrics()
        )
    
    def format_greentext_briefing(self, metrics: DashboardMetrics) -> str:
        """Format dashboard as concise greentext briefing"""
        briefing = f"""
# TENXSOM AI EXECUTIVE BRIEFING
> Generated: {metrics.timestamp[:16]}

## LAUNCH STATUS
> Landing Page: {metrics.launch_status.get('landing_page', 'UNKNOWN')}
> Payment Gateway: {metrics.launch_status.get('payment_gateway', 'UNKNOWN')} [{metrics.launch_status.get('stripe_mode', 'UNKNOWN')}]
> SDK Download: {metrics.launch_status.get('sdk_download', 'UNKNOWN')}

## FINANCIAL CHECKPOINT
> Daily Sales: {metrics.financial_metrics['daily_sales']} units (${metrics.financial_metrics['daily_revenue']:.2f})
> MRR Progress: ${metrics.financial_metrics['mrr_total']:.2f}
> Living Expense: ${metrics.financial_metrics['living_expense_met']:.2f}/$2500 ({(metrics.financial_metrics['living_expense_met']/2500*100):.1f}%)
> Reinvest Ready: ${metrics.financial_metrics['reinvest_available']:.2f}

## PRIORITY ACTIONS
"""
        for i, action in enumerate(metrics.next_actions, 1):
            briefing += f"> {i}. {action}\n"
            
        briefing += f"""
## SYSTEM HEALTH
> Test Suite: {metrics.health_indicators['test_suite']}
> Docker: {metrics.health_indicators['docker_services']}
> Backups: {metrics.health_indicators['backup_status']}

## KNOWLEDGE BASE
> Notes: {metrics.knowledge_ingestion['notes_pending']} pending / {metrics.knowledge_ingestion['notes_processed']} processed
> Texts: {metrics.knowledge_ingestion['txt_files_pending']} pending / {metrics.knowledge_ingestion['txt_files_processed']} processed
> Total KB Entries: {metrics.knowledge_ingestion['total_kb_entries']:,}

---
> Next auto-refresh: 24h
"""
        return briefing
    
    def save_metrics(self, metrics: DashboardMetrics):
        """Save metrics for historical tracking"""
        history_file = self.dashboard_dir / "dashboard_history.jsonl"
        with open(history_file, 'a') as f:
            f.write(json.dumps(asdict(metrics)) + '\n')
            
        # Save latest as separate file
        latest_file = self.dashboard_dir / "latest_dashboard.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(metrics), f, indent=2)
    
    def run(self, output_format: str = "greentext"):
        """Run dashboard generation"""
        print("Generating Tenxsom AI Executive Dashboard...")
        
        metrics = self.generate_dashboard()
        self.save_metrics(metrics)
        
        if output_format == "greentext":
            briefing = self.format_greentext_briefing(metrics)
            print(briefing)
            
            # Save to file
            briefing_file = self.dashboard_dir / "latest_briefing.md"
            with open(briefing_file, 'w') as f:
                f.write(briefing)
                
        elif output_format == "json":
            print(json.dumps(asdict(metrics), indent=2))
            
        return metrics


def main():
    """Run dashboard from command line"""
    import sys
    
    dashboard = TenxsomDashboard()
    
    # Check for arguments
    output_format = "greentext"
    if len(sys.argv) > 1:
        output_format = sys.argv[1]
        
    dashboard.run(output_format)


if __name__ == "__main__":
    main()