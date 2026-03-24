# FTE (Foundation Tier Enhanced) - Project Context

## Project Overview

FTE is a workflow automation system that provides email, social media, and task management capabilities with AI-powered features. It consists of Bronze, Silver, and Gold tiers, with Silver Tier being the current production-ready implementation.

**Project Location**: `/mnt/e/PIAIC/Quarter 5/FTE`
**Current Tier**: Silver (Complete)
**Python Version**: 3.13+

## Architecture

### Core Components

```
src/fte/
├── watchers/           # Email and social media monitoring
│   ├── watcher_manager.py       # Central watcher management
│   ├── whatsapp_watcher.py      # Twilio WhatsApp integration
│   └── linkedin_watcher.py      # LinkedIn notifications & messages
├── social/             # Social media integrations
│   ├── linkedin_api.py          # LinkedIn API client
│   ├── linkedin_browser_automation.py  # Browser-based posting (fallback)
│   └── gmail_sender.py          # Gmail API for sending emails
├── reasoning/           # Claude reasoning engine
│   ├── plan_parser.py           # Parse Plan.md files
│   └── reasoning_engine.py       # Iterative reasoning loop
├── mcp/                # Model Context Protocol server
│   ├── server.py                # Basic MCP server
│   ├── enhanced_server.py        # Enhanced MCP with business actions
│   └── action_registry.py       # Action registration system
├── approval/           # Human-in-the-loop workflows
│   ├── workflow.py              # Basic approval workflow
│   └── multi_level_approval.py # Multi-level approval system
├── scheduler/           # Task scheduling
│   ├── task_scheduler.py        # APScheduler-based scheduling
│   └── business_scheduler.py    # Business-specific scheduling
├── skills/             # AI/Agent skills
│   ├── framework.py             # BaseSkill class
│   ├── registry.py              # Skill discovery & management
│   ├── email_response_generator.py
│   ├── plan_generator.py
│   ├── linkedin_post_generator.py
│   ├── inbox_processor.py
│   ├── task_manager.py
│   └── [business intelligence, customer outreach, etc.]
├── gmail_watcher.py    # Gmail inbox monitoring
└── vault_manager.py    # Obsidian-style vault management
```

### Vault Structure (Obsidian-style)

```
vault/
├── Inbox/                    # New items arrive here
├── Needs_Action/             # Items requiring user attention
├── Done/                     # Completed items
├── Pending_Approvals/        # Actions awaiting approval
├── Approved_Actions/          # Approved actions
└── Rejected_Actions/          # Rejected actions
```

## Key Technologies

- **Scheduling**: APScheduler (Python native, cross-platform)
- **Email**: Google API (OAuth2 with refresh tokens)
- **WhatsApp**: Twilio API
- **LinkedIn**: linkedin-api + Selenium browser automation (fallback)
- **Web Server**: FastAPI with Uvicorn
- **File Monitoring**: watchdog

## Important Implementation Details

### LinkedIn Authentication
LinkedIn has deprecated username/password API authentication. The system provides two approaches:
1. **Primary**: Browser automation via `linkedin_browser_automation.py` (Selenium)
2. **Fallback**: linkedin-api library (may not work due to API changes)

### Gmail Scopes
- **Reading**: `https://www.googleapis.com/auth/gmail.readonly` (token.pickle)
- **Sending**: `https://www.googleapis.com/auth/gmail.send` (token_send.pickle)

### APScheduler vs Cron
APScheduler is used instead of native cron/Task Scheduler for:
- Cross-platform consistency
- Native Python integration
- Dynamic task management
- Shared application state
- Built-in concurrency control

## Configuration Files

### config.json
Located at project root. Contains:
- API providers (Qwen, OpenAI, etc.)
- MCP server settings
- Watcher configurations
- Scheduling settings
- Approval workflow settings

### Environment Variables
- `LINKEDIN_USERNAME` - LinkedIn login
- `LINKEDIN_PASSWORD` - LinkedIn password
- `TWILIO_ACCOUNT_SID` - Twilio for WhatsApp
- `TWILIO_AUTH_TOKEN` - Twilio for WhatsApp
- `WHATSAPP_NUMBER` - Twilio WhatsApp number

### OAuth Credentials
- `credentials.json` - Google Cloud OAuth client credentials
- `token.pickle` - Gmail read access (auto-generated)
- `token_send.pickle` - Gmail send access (auto-generated)

## Command Line Interface

```bash
fte help                    # Show help
fte status                 # Show vault status
fte process               # List and process Inbox items
fte watch                 # Start file system watcher
fte gmail                 # Start Gmail watcher
fte whatsapp              # Start WhatsApp watcher
fte linkedin              # Start LinkedIn watcher

fte-mcp --port 8000       # Start MCP server
```

## Claude Code Skills

The following skills are available via Claude Code (`.claude/skills/`):
- `/inbox-processor` - Analyze and categorize inbox items
- `/task-manager` - Manage task status and movement
- `/dashboard-updater` - Refresh Dashboard.md statistics
- `/note-creator` - Create structured notes
- `/plan-reasoning` - Process Plan.md files with Claude reasoning
- `/linkedin-posting` - Automate LinkedIn posts about business
- `/approval-workflow` - Handle human-in-the-loop approval
- `/scheduler-skills` - Schedule and manage recurring tasks

## MCP Server Actions

The MCP server exposes the following actions:
- `send_email(to, subject, body)` - Send emails via Gmail API
- `create_note(title, content, folder)` - Create notes in vault
- `move_task(file_name, destination)` - Move tasks between vault folders

## Development Guidelines

### Adding a New Watcher
1. Create class in `src/fte/watchers/`
2. Inherit appropriate event handling patterns
3. Register in `watcher_manager.py`
4. Add CLI command in main entry point

### Adding a New Skill
1. Create class in `src/fte/skills/`
2. For AI/business skills: inherit from `BaseSkill`
3. Register in `src/fte/skills/registry.py`
4. Add Claude Code skill definition in `.claude/skills/`

### Adding a New MCP Action
1. Create async function with appropriate parameters
2. Register in `src/fte/mcp/action_registry.py`
3. Add parameter schema for validation
4. Update `create_default_action_registry()` if needed

## Common Issues & Solutions

### LinkedIn Authentication Fails
- Use browser automation: `from fte.social.linkedin_browser_automation import LinkedInBrowserAutomation`
- Set `headless=False` for first login to handle security checkpoint

### Gmail Token Expired
- Delete `token.pickle` and/or `token_send.pickle`
- Re-run the watcher - will trigger OAuth flow

### Module Import Errors
- Ensure `pip install -e .` has been run
- Virtual environment: `.venv/` in project root
- Python path: `src/` added to path automatically

## Testing

### Run Verification
```bash
cd /mnt/e/PIAIC/Quarter 5/FTE
python3 verify_silver_tier.py
```

### Run Integration Tests
```bash
python3 -m src.fte.integration_test
```

### Run Demo
```bash
python3 silver_tier_demo.py
```

## Project Status

### Silver Tier Requirements
- ✅ All Bronze requirements complete
- ✅ Two or more Watcher scripts (Gmail, WhatsApp, LinkedIn)
- ✅ Auto-post LinkedIn for sales (with browser automation fallback)
- ✅ Claude reasoning loop for Plan.md
- ✅ Working MCP server with email sending
- ✅ Human-in-the-loop approval workflow
- ✅ Basic scheduling (APScheduler documented)
- ✅ All AI as Agent Skills

### Completion Report
See `SILVER_TIER_COMPLETION_REPORT.md` for detailed implementation notes.

## Next Steps (Gold Tier)

For future enhancements:
1. Official LinkedIn Marketing Developer Program API integration
2. Multi-platform social media (Twitter, Facebook, Instagram)
3. Advanced AI models integration
4. Real-time analytics dashboard
5. Advanced approval workflows with multi-person routing
6. Advanced scheduling with resource allocation

## Contact & Support

- **Author**: Fiaz Majeed
- **Email**: fiazcomsats@gmail.com
- **License**: MIT
