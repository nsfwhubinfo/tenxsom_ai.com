#!/bin/bash
# Setup script for Tenxsom AI Executive Dashboard

echo "Setting up Tenxsom AI Executive Dashboard..."

# Create directory structure
mkdir -p dashboard/knowledge_inbox/{notes,texts,conversations}
mkdir -p dashboard/knowledge_processed
mkdir -p dashboard/knowledge_base

# Create initial financial tracking file
cat > dashboard/financial_tracking.json << 'EOF'
{
  "daily_sales": 0,
  "daily_revenue": 0.0,
  "mrr_total": 0.0,
  "living_expense_met": 0.0,
  "reinvest_available": 0.0,
  "last_updated": "2025-01-29"
}
EOF

# Create cron job for daily dashboard generation
CRON_CMD="0 6 * * * cd /home/golde/Tenxsom_AI && python3 dashboard/executive_dashboard.py > dashboard/daily_briefing.log 2>&1"

# Add to crontab if not already present
(crontab -l 2>/dev/null | grep -v "executive_dashboard.py"; echo "$CRON_CMD") | crontab -

# Create quick access aliases
cat >> ~/.bashrc << 'EOF'

# Tenxsom AI Dashboard Aliases
alias txdash='cd /home/golde/Tenxsom_AI && python3 dashboard/executive_dashboard.py'
alias txingest='cd /home/golde/Tenxsom_AI && python3 dashboard/knowledge_ingestion_engine.py'
alias txstatus='cd /home/golde/Tenxsom_AI && python3 dashboard/knowledge_ingestion_engine.py status'
alias txquery='cd /home/golde/Tenxsom_AI && python3 dashboard/knowledge_ingestion_engine.py query'
EOF

# Create usage instructions
cat > dashboard/README.md << 'EOF'
# Tenxsom AI Executive Dashboard

## Quick Start

### View Dashboard
```bash
txdash
# or
python3 dashboard/executive_dashboard.py
```

### Process Knowledge Inbox
```bash
# Add files to process:
# - Images: dashboard/knowledge_inbox/notes/
# - Text files: dashboard/knowledge_inbox/texts/
# - Conversations: dashboard/knowledge_inbox/texts/*.txt

# Process all pending files
txingest process

# Check status
txingest status

# Query knowledge base
txquery "fractal optimization"
```

### Update Financial Metrics
Edit `dashboard/financial_tracking.json` with daily sales data.

### Dashboard Components

1. **Launch Status**: SDK readiness, payment gateway status
2. **Financial Metrics**: Sales, MRR, 80/15/5 split tracking  
3. **Priority Actions**: Top 3 next steps
4. **System Health**: Tests, Docker, backups
5. **Knowledge Base**: Ingestion progress and stats

### Automated Features

- Daily briefing at 6 AM (via cron)
- Automatic knowledge categorization
- OCR support for handwritten notes (when configured)
- FMO integration for knowledge graph

### Adding Custom Metrics

Edit `executive_dashboard.py` to add new metrics in the appropriate getter method.
EOF

echo "✓ Dashboard setup complete!"
echo ""
echo "Next steps:"
echo "1. Source bashrc for aliases: source ~/.bashrc"
echo "2. Run dashboard: txdash"
echo "3. Add notes/texts to: dashboard/knowledge_inbox/"
echo "4. Process inbox: txingest process"
echo ""
echo "For OCR setup, see: dashboard/OCR_SETUP_GUIDE.md"