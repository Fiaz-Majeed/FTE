# FTE Gold Tier - Foundation Tier Enhanced

**Version**: 1.0.0 (Gold Tier - Autonomous Employee)
**Status**: ✅ Production Ready

FTE (Foundation Tier Enhanced) is a fully autonomous employee system that integrates personal and business workflows across multiple domains. It provides comprehensive automation with social media management, self-hosted accounting, intelligent task execution, and business intelligence.

## 🎯 Gold Tier Features

- **Full Cross-Domain Integration**: Personal + Business workflows unified
- **Self-Hosted Accounting**: Odoo Community Edition with JSON-RPC integration
- **Multi-Platform Social Media**: Twitter, Facebook, Instagram automation
- **Autonomous Task Execution**: Ralph Wiggum loop with self-correction and learning
- **Weekly Business Audits**: Automated CEO briefings with insights
- **Error Recovery**: Circuit breakers, retry logic, health checks, fallbacks
- **Comprehensive Audit Logging**: SQLite-based tracking of all activities
- **Multiple MCP Servers**: Specialized servers for different domains
- **20+ Agent Skills**: All AI functionality as modular skills

## Features

### 🤖 Autonomous Operations
- **Ralph Wiggum Loop**: Multi-step task completion with goal decomposition
- **Self-Correction**: Automatic retry and error recovery
- **Learning**: Pattern tracking and outcome-based improvement
- **Task Dependencies**: Intelligent dependency management

### 📱 Social Media Integration
- **Twitter/X**: Post tweets, monitor mentions, engagement summaries
- **Facebook**: Post updates, get insights, generate reports
- **Instagram**: Post images with captions, track engagement
- **LinkedIn**: Automated posting and monitoring (existing)
- **Content Generation**: AI-powered content from vault notes

### 💰 Accounting System
- **Odoo 19 Community**: Self-hosted accounting system
- **JSON-RPC Integration**: Full API access via MCP server
- **Invoice Management**: Create and track invoices
- **Payment Recording**: Record and reconcile payments
- **Financial Reports**: P&L, Balance Sheet, custom reports

### 📊 Business Intelligence
- **Weekly Audits**: Automated business and accounting audits
- **CEO Briefings**: Executive summaries with insights and recommendations
- **Trend Analysis**: Identify positive trends and areas of concern
- **Performance Metrics**: Track KPIs across all domains

### 🛡️ Resilience & Error Recovery
- **Circuit Breakers**: Prevent cascading failures
- **Retry Logic**: Exponential backoff with jitter
- **Health Checks**: Monitor service availability
- **Fallback Strategies**: Graceful degradation

### 📝 Comprehensive Audit Logging
- **SQLite Database**: Persistent event storage
- **10 Event Types**: ACTION, DECISION, API_CALL, APPROVAL, ERROR, SYSTEM, SOCIAL_POST, EMAIL, ACCOUNTING, AUTONOMOUS_TASK
- **Query Interface**: Filter and analyze events
- **Statistics**: Generate reports and insights

### 🔌 Multiple MCP Servers
- **Router** (8000): Central request routing
- **Accounting** (8001): Odoo integration
- **Social** (8002): Social media operations
- **Communication** (8003): Email and messaging
- **Analytics** (8004): Reporting and analytics

### 👁️ Watchers (6 Active)
- **Gmail**: Email monitoring with desktop notifications
- **WhatsApp**: Twilio API integration
- **LinkedIn**: Professional network monitoring
- **Twitter**: Mention and engagement tracking
- **Facebook**: Page monitoring and insights
- **Instagram**: Business account monitoring

#### Why APScheduler Instead of Cron/Task Scheduler?

The FTE system uses **APScheduler** (Advanced Python Scheduler) instead of native cron (Linux/macOS) or Task Scheduler (Windows) for several important reasons:

1. **Cross-Platform Consistency**: APScheduler works identically on Windows, macOS, and Linux, ensuring the same scheduling behavior across all platforms.

2. **Python Integration**: Being a native Python library, APScheduler can directly call Python functions with full access to the application state, environment variables, and class instances.

3. **In-Process Scheduling**: Unlike cron/Task Scheduler which spawn external processes, APScheduler runs within the Python application, allowing for:
   - Shared memory and state between scheduled tasks
   - Lower resource usage (no separate process overhead)
   - Better error handling and logging
   - Real-time task management (add/modify/cancel tasks programmatically)

4. **Flexible Trigger Types**: APScheduler supports multiple trigger types:
   - `IntervalTrigger` - Run every X seconds/minutes/hours
   - `CronTrigger` - Run at specific times (cron-like syntax)
   - `DateTrigger` - Run once at a specific datetime

5. **Persistent State**: The scheduler maintains state in JSON format that can be persisted and restored across application restarts, including task definitions and execution history.

6. **Dynamic Management**: Tasks can be added, modified, or cancelled at runtime through the MCP server API, something not easily possible with static cron jobs.

7. **Built-in Concurrency Control**: APScheduler provides built-in support for handling concurrent executions and preventing overlapping tasks using `max_instances` and `coalesce` options.

**Comparison Summary:**

| Feature | APScheduler | Cron | Windows Task Scheduler |
|---------|--------------|------|----------------------|
| Cross-Platform | ✅ Yes | ❌ Linux/macOS only | ❌ Windows only |
| Python Integration | ✅ Native | ❌ External process | ❌ External process |
| Dynamic Task Management | ✅ Yes | ❌ Requires crontab edit | ❌ Requires GUI |
| State Persistence | ✅ JSON files | ❌ None | ❌ XML/Custom |
| Shared Application State | ✅ Yes | ❌ No | ❌ No |
| Cron Syntax Support | ✅ Yes | ✅ Native | ❌ Complex UI |

For these reasons, APScheduler provides a more robust and flexible solution for the FTE system's scheduling needs while maintaining the requirement for basic scheduling functionality.

### 7. Agent Skills
- All AI functionality implemented as standardized skills
- Claude Code integration for advanced automation
- Modular skill architecture

## Installation

```bash
pip install -e .
```

## Usage

### Basic Commands
```bash
fte help                    # Show help
fte status                 # Show vault status
fte process               # List and process Inbox items
fte watch                 # Start file system watcher
fte gmail                 # Start Gmail watcher
fte whatsapp              # Start WhatsApp watcher
fte linkedin              # Start LinkedIn watcher
fte enhanced-watch        # Start enhanced file watcher
```

### MCP Server
```bash
fte-mcp --port 8000       # Start MCP server
```

### Agent Skills (via Claude Code)
- `/inbox-processor` - Analyze and categorize inbox items
- `/task-manager` - Manage task status and movement
- `/dashboard-updater` - Refresh Dashboard.md statistics
- `/note-creator` - Create structured notes
- `/plan-reasoning` - Process Plan.md files with Claude reasoning
- `/linkedin-posting` - Automate LinkedIn posts about business
- `/approval-workflow` - Handle human-in-the-loop approval for actions
- `/scheduler-skills` - Schedule and manage recurring tasks

## Configuration

The `config.json` file contains all configuration settings:

```json
{
  "LOG": true,
  "LOG_LEVEL": "info",
  "HOST": "127.0.0.1",
  "PORT": 3456,
  "API_TIMEOUT_MS": 600000,
  "Providers": [...],
  "Router": {...},
  "MCP": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8000,
    "api_key": null,
    "ssl": false
  },
  "Watchers": {...},
  "Scheduling": {...},
  "Approval": {...}
}
```

## Vault Structure

The system uses an Obsidian-style vault structure:
```
vault/
├── Inbox/           # New items arrive here
├── Needs_Action/    # Items requiring attention
├── Done/           # Completed items
├── Pending_Approvals/ # Items awaiting approval
├── Approved_Actions/  # Approved actions
└── Rejected_Actions/  # Rejected actions
```

## Quick Start

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

```bash
# 1. Install FTE
pip install -e .

# 2. Set up Odoo (optional)
python -m fte.setup.odoo_setup odoo-fte
cd odoo-fte && docker-compose up -d

# 3. Configure credentials in .env file

# 4. Start MCP servers
python -m fte.mcp.mcp_router &
python -m fte.mcp.odoo_mcp_server &

# 5. Start watchers
fte gmail &
fte whatsapp &
fte linkedin &
```

## API Keys Required

- **Twitter/X**: API key, secret, access token, bearer token
- **Facebook/Instagram**: Access token, page ID, account ID
- **Gmail**: Google API credentials (credentials.json, token.pickle)
- **WhatsApp**: Twilio Account SID and Auth Token
- **LinkedIn**: LinkedIn username/password (via environment variables)
- **Odoo**: URL, database, username, password
- **MCP Server**: Auto-generated API key or custom key

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[GOLD_TIER_ARCHITECTURE.md](GOLD_TIER_ARCHITECTURE.md)** - Complete architecture documentation
- **[GOLD_TIER_COMPLETION_REPORT.md](GOLD_TIER_COMPLETION_REPORT.md)** - Implementation report
- **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** - Comprehensive lessons learned
- **[SILVER_TIER_COMPLETION_REPORT.md](SILVER_TIER_COMPLETION_REPORT.md)** - Silver Tier details
- **[claude.md](claude.md)** - Project context for Claude Code

## Development

This project follows a modular architecture with clear separation of concerns:

- `src/fte/audit/` - Audit logging and weekly audits
- `src/fte/resilience/` - Error recovery and circuit breakers
- `src/fte/autonomous/` - Ralph Wiggum autonomous loop
- `src/fte/watchers/` - All watcher implementations
- `src/fte/social/` - Social media integrations
- `src/fte/reasoning/` - Claude reasoning engine
- `src/fte/mcp/` - MCP servers and routing
- `src/fte/approval/` - Approval workflow system
- `src/fte/scheduler/` - Task scheduling
- `src/fte/skills/` - Agent skills
- `src/fte/setup/` - Setup utilities
- `.claude/skills/` - Claude skill definitions

## Project Timeline

- **Bronze Tier** (v0.1.0) - January 26, 2026
  - Obsidian vault, file watcher, Gmail watcher, basic skills

- **Silver Tier** (v0.2.0) - February 21, 2026
  - Multiple watchers, LinkedIn automation, MCP server, approval workflows

- **Gold Tier** (v1.0.0) - March 24, 2026
  - Full autonomous employee, Odoo accounting, multi-platform social media, Ralph Wiggum loop

## License

MIT License