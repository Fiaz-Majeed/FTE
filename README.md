# FTE Silver Tier - Foundation Tier Enhanced

FTE (Foundation Tier Enhanced) is a workflow automation system that extends the Bronze Tier with additional watcher scripts, automated LinkedIn posting, Claude reasoning loop for Plan.md files, MCP server for external actions, human-in-the-loop approval workflow, basic scheduling, and all AI functionality as Agent Skills.

## Features

### 1. Additional Watcher Scripts
- **Gmail Watcher**: Monitors Gmail inbox for new emails with desktop notifications
- **WhatsApp Watcher**: Monitors WhatsApp messages using Twilio API
- **LinkedIn Watcher**: Monitors LinkedIn notifications and messages
- **Enhanced File Watcher**: Advanced file system monitoring with pattern matching

### 2. Automated LinkedIn Posting
- LinkedIn API integration for posting business updates
- Content generation from vault notes
- Scheduling mechanism for posts
- Post analytics tracking

### 3. Claude Reasoning Loop
- Parses Plan.md files to extract goals, tasks, and dependencies
- Implements iterative reasoning engine with progress tracking
- Generates adaptive plan adjustments

### 4. MCP Server
- FastAPI-based server for external actions
- Secure endpoint authentication with API keys
- Action registration system with permission management

### 5. Human-in-the-Lock Approval Workflow
- Decision points in workflows with user notification system
- Approval tracking and logging
- Integration with sensitive actions (emails, LinkedIn posts, etc.)

### 6. Basic Scheduling
- APScheduler integration for task scheduling
- Persistent scheduling and task queue management
- Scheduled actions for vault maintenance and reporting

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

## API Keys Required

- **Gmail**: Google API credentials (credentials.json, token.pickle)
- **WhatsApp**: Twilio Account SID and Auth Token
- **LinkedIn**: LinkedIn username/password (via environment variables)
- **MCP Server**: Auto-generated API key or custom key

## Development

This project follows a modular architecture with clear separation of concerns:

- `src/fte/watchers/` - All watcher implementations
- `src/fte/social/` - Social media integrations
- `src/fte/reasoning/` - Claude reasoning engine
- `src/fte/mcp/` - MCP server and action registry
- `src/fte/approval/` - Approval workflow system
- `src/fte/scheduler/` - Task scheduling
- `src/fte/skills/` - Agent skills
- `.claude/skills/` - Claude skill definitions

## License

MIT License