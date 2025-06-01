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
