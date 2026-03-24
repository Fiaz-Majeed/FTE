# FTE Gold Tier - Quick Start Guide

**Version**: 1.0.0 (Gold Tier)
**Date**: 2026-03-24

---

## What is FTE Gold Tier?

FTE (Foundation Tier Enhanced) Gold Tier is a **fully autonomous employee system** that integrates personal and business workflows across multiple domains:

- 📧 **Email & Messaging**: Gmail, WhatsApp, LinkedIn
- 📱 **Social Media**: Twitter, Facebook, Instagram
- 💰 **Accounting**: Self-hosted Odoo Community Edition
- 🤖 **Autonomous Operations**: Multi-step task completion with learning
- 📊 **Business Intelligence**: Weekly audits with CEO briefings
- 🛡️ **Resilience**: Error recovery, circuit breakers, health checks
- 📝 **Audit Logging**: Comprehensive tracking of all activities

---

## Quick Start (5 Minutes)

### 1. Install FTE

```bash
cd "E:\PIAIC\Quarter 5\FTE"
pip install -e .
```

### 2. Set Up Odoo (Optional but Recommended)

```bash
python -m fte.setup.odoo_setup odoo-fte
cd odoo-fte
docker-compose up -d
```

Access Odoo at http://localhost:8069 and complete the initial setup.

### 3. Configure Credentials

Create a `.env` file in the project root:

```bash
# Twitter/X
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Facebook/Instagram
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_account_id

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin
```

### 4. Start the System

```bash
# Start MCP servers
python -m fte.mcp.mcp_router &
python -m fte.mcp.odoo_mcp_server &

# Start watchers
fte gmail &
fte whatsapp &
fte linkedin &
```

### 5. Verify Installation

```bash
# Check MCP servers
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check Odoo
curl http://localhost:8069

# Check audit logs
ls -la audit_logs.db
```

---

## Key Features

### 🤖 Autonomous Task Execution

```python
from fte.autonomous import RalphWiggumLoop

ralph = RalphWiggumLoop()
task_id = ralph.create_task("Post weekly business update to social media")
result = ralph.execute_task(task_id)
```

### 📱 Social Media Management

```python
from fte.skills.gold_tier_skills import SocialMediaManagementSkill

skill = SocialMediaManagementSkill()
result = await skill.execute(
    action="post",
    platforms=["twitter", "facebook"],
    topic="business update"
)
```

### 💰 Accounting Operations

```python
from fte.mcp.odoo_mcp_server import OdooClient

client = OdooClient()
client.authenticate()
invoice_id = client.create_invoice(
    partner_id=1,
    invoice_lines=[{"product_id": 1, "quantity": 1, "price_unit": 100}]
)
```

### 📊 Weekly Business Audit

```python
from fte.audit.weekly_audit import WeeklyAuditSystem

audit = WeeklyAuditSystem()
briefing_path = audit.run_weekly_audit()
```

### 📝 Audit Logging

```python
from fte.audit import get_audit_logger, AuditEventType

logger = get_audit_logger()
logger.log_action("custom_action", actor="system", resource="resource_id")
stats = logger.get_statistics(days=7)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  FTE Gold Tier System                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Watchers          MCP Servers        Agent Skills       │
│  • Gmail           • Social           • Social Mgmt      │
│  • WhatsApp        • Accounting       • Accounting       │
│  • LinkedIn        • Communication    • Autonomous       │
│  • Twitter         • Analytics        • Weekly Audit     │
│  • Facebook        • Router           • + 16 more        │
│  • Instagram                                             │
│                                                           │
│  Ralph Wiggum      Resilience         Audit System       │
│  • Autonomous      • Circuit Breakers • SQLite DB        │
│  • Multi-step      • Retry Logic      • 10 Event Types   │
│  • Self-correct    • Health Checks    • CEO Briefings    │
│  • Learning        • Fallbacks        • Statistics       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Available Commands

### Watchers
```bash
fte gmail          # Start Gmail watcher
fte whatsapp       # Start WhatsApp watcher
fte linkedin       # Start LinkedIn watcher
fte watch          # Start file system watcher
```

### MCP Servers
```bash
python -m fte.mcp.mcp_router           # Start MCP router (port 8000)
python -m fte.mcp.odoo_mcp_server      # Start Odoo MCP (port 8001)
fte-mcp --port 8000                    # Start enhanced MCP
```

### Utilities
```bash
fte status         # Show vault status
fte process        # Process inbox items
```

### Setup
```bash
python -m fte.setup.odoo_setup [dir]  # Generate Odoo setup files
```

---

## Agent Skills Available

### Gold Tier Skills (New)
1. **social_media_management** - Multi-platform social media
2. **accounting_management** - Odoo accounting operations
3. **autonomous_task** - Ralph Wiggum loop interface
4. **weekly_audit** - Automated business audits

### Silver Tier Skills
5. **business_intelligence** - Market analysis & opportunities
6. **customer_outreach** - Automated communication
7. **sales_pipeline** - Lead management
8. **content_strategy** - Content planning
9. **linkedin_post_generator** - LinkedIn content
10. **plan_generator** - Business plan generation
11. **email_response_generator** - Smart email replies

### Bronze Tier Skills
12. **inbox_processor** - Email categorization
13. **task_manager** - Task workflow management
14. **dashboard_updater** - Dashboard statistics
15. **note_creator** - Structured note creation

---

## MCP Servers

### Router (Port 8000)
Central router for all MCP servers

**Endpoints**:
- `GET /servers` - List all registered servers
- `POST /route/{server_name}` - Route request to server
- `GET /health` - Health check

### Accounting MCP (Port 8001)
Odoo integration for accounting operations

**Endpoints**:
- `POST /accounting/invoice` - Create invoice
- `POST /accounting/payment` - Record payment
- `POST /accounting/report` - Get financial report
- `GET /accounting/balance/{account_id}` - Get account balance
- `GET /health` - Health check

### Social MCP (Port 8002)
Social media operations (planned)

### Communication MCP (Port 8003)
Email and messaging operations (planned)

### Analytics MCP (Port 8004)
Reporting and analytics (planned)

---

## Configuration Files

### config.json
Main configuration file for providers, watchers, scheduling, etc.

### .env
Environment variables for API credentials

### credentials.json
Google OAuth credentials for Gmail

### token.pickle / token_send.pickle
Gmail OAuth tokens (auto-generated)

### docker-compose.yml
Odoo Docker configuration (in odoo-fte/)

---

## Vault Structure

```
vault/
├── Inbox/                 # New items
├── Needs_Action/          # Requires attention
├── Done/                  # Completed items
├── Pending_Approvals/     # Awaiting approval
├── Approved_Actions/      # Approved
├── Rejected_Actions/      # Rejected
├── Dashboard.md           # Central hub
└── Company_Handbook.md    # Documentation
```

---

## Troubleshooting

### MCP Server Won't Start
```bash
# Check if port is in use
netstat -ano | findstr :8000

# Check logs
python -m fte.mcp.mcp_router
```

### Odoo Connection Failed
```bash
# Check Odoo is running
docker ps | grep odoo

# Check logs
docker logs odoo19

# Restart Odoo
cd odoo-fte
docker-compose restart
```

### API Authentication Failed
- Check environment variables are set
- Verify API credentials are correct
- Check token expiration (Gmail)
- Review audit logs for details

### Watcher Not Capturing Items
- Check watcher is running
- Verify API credentials
- Check vault permissions
- Review audit logs

---

## Documentation

- **GOLD_TIER_ARCHITECTURE.md** - Complete architecture documentation
- **LESSONS_LEARNED.md** - Comprehensive lessons learned
- **GOLD_TIER_COMPLETION_REPORT.md** - Implementation report
- **README.md** - General project information
- **SILVER_TIER_COMPLETION_REPORT.md** - Silver Tier details
- **claude.md** - Project context for Claude Code

---

## Support

### Getting Help
- Check documentation in project root
- Review audit logs: `audit_logs.db`
- Check MCP server health endpoints
- Review vault for captured items

### Reporting Issues
- GitHub: https://github.com/anthropics/claude-code/issues
- Include: error message, logs, configuration
- Describe: expected vs actual behavior

---

## Next Steps

1. **Configure All Credentials**: Set up API keys for all services
2. **Test Each Integration**: Verify each service works independently
3. **Run Weekly Audit**: Test the audit system
4. **Create Autonomous Task**: Test Ralph Wiggum loop
5. **Monitor System**: Check audit logs and health endpoints
6. **Schedule Automation**: Set up recurring tasks
7. **Review CEO Briefing**: Check weekly audit output

---

## Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/19.0/
- **Twitter API**: https://developer.twitter.com/en/docs
- **Facebook Graph API**: https://developers.facebook.com/docs/graph-api
- **FastAPI**: https://fastapi.tiangolo.com/
- **APScheduler**: https://apscheduler.readthedocs.io/

---

## Version History

- **v1.0.0 (Gold Tier)** - 2026-03-24
  - Full autonomous employee system
  - Odoo accounting integration
  - Multi-platform social media
  - Ralph Wiggum autonomous loop
  - Weekly business audits
  - Comprehensive error recovery

- **v0.2.0 (Silver Tier)** - 2026-02-21
  - Multiple watchers
  - LinkedIn automation
  - MCP server
  - Approval workflows
  - Advanced scheduling

- **v0.1.0 (Bronze Tier)** - 2026-01-26
  - Obsidian vault
  - File system watcher
  - Gmail watcher
  - Basic agent skills

---

**🎉 Welcome to FTE Gold Tier - Your Fully Autonomous Employee! 🎉**

For detailed documentation, see `GOLD_TIER_ARCHITECTURE.md`
