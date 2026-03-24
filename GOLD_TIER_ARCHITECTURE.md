# FTE Gold Tier - Architecture Documentation

**Version**: 1.0.0
**Date**: 2026-03-24
**Status**: Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [System Components](#system-components)
4. [Integration Patterns](#integration-patterns)
5. [Data Flow](#data-flow)
6. [Security Architecture](#security-architecture)
7. [Deployment Guide](#deployment-guide)
8. [Lessons Learned](#lessons-learned)
9. [Future Enhancements](#future-enhancements)

---

## Executive Summary

FTE Gold Tier represents a fully autonomous employee system that integrates personal and business workflows across multiple domains:

- **Social Media**: Twitter, Facebook, Instagram
- **Accounting**: Odoo Community Edition (self-hosted)
- **Communication**: Email, WhatsApp, LinkedIn
- **Autonomous Operations**: Multi-step task completion with self-correction
- **Business Intelligence**: Weekly audits with CEO briefings

### Key Achievements

✅ Full cross-domain integration (Personal + Business)
✅ Self-hosted Odoo accounting system with JSON-RPC integration
✅ Multi-platform social media management
✅ Multiple specialized MCP servers
✅ Weekly business and accounting audits
✅ Error recovery and graceful degradation
✅ Comprehensive audit logging
✅ Ralph Wiggum autonomous loop
✅ All AI functionality as Agent Skills

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FTE Gold Tier System                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Watchers   │  │  MCP Servers │  │ Agent Skills │      │
│  │              │  │              │  │              │      │
│  │ • Gmail      │  │ • Social     │  │ • Social Mgmt│      │
│  │ • WhatsApp   │  │ • Accounting │  │ • Accounting │      │
│  │ • LinkedIn   │  │ • Comms      │  │ • Autonomous │      │
│  │ • Twitter    │  │ • Analytics  │  │ • Weekly Audit│     │
│  │ • Facebook   │  │ • Router     │  │ • Business Intel│   │
│  │ • Instagram  │  └──────────────┘  └──────────────┘      │
│  └──────────────┘                                            │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Ralph Wiggum Autonomous Loop                  │   │
│  │  • Goal Decomposition                                 │   │
│  │  • Task Planning                                      │   │
│  │  • Execution Monitoring                               │   │
│  │  • Self-Correction                                    │   │
│  │  • Learning from Outcomes                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Resilience & Error Recovery                   │   │
│  │  • Circuit Breakers                                   │   │
│  │  • Retry Mechanisms                                   │   │
│  │  • Health Checks                                      │   │
│  │  • Fallback Strategies                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Audit & Logging System                        │   │
│  │  • SQLite Database                                    │   │
│  │  • Event Tracking                                     │   │
│  │  • Weekly Audits                                      │   │
│  │  • CEO Briefings                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │  Vault   │        │   Odoo   │        │ External │
   │ (Obsidian)│       │ (Docker) │        │   APIs   │
   └──────────┘        └──────────┘        └──────────┘
```

### Technology Stack

**Core**
- Python 3.13+
- FastAPI (MCP servers)
- SQLite (audit logs)
- APScheduler (task scheduling)

**Integrations**
- Odoo 19 Community (accounting)
- Twitter API v2
- Facebook Graph API
- LinkedIn API
- Gmail API
- Twilio (WhatsApp)

**Infrastructure**
- Docker & Docker Compose (Odoo)
- PostgreSQL 15 (Odoo database)
- Uvicorn (ASGI server)

---

## System Components

### 1. Audit Logging System

**Location**: `src/fte/audit/`

**Purpose**: Comprehensive tracking of all system actions, decisions, and events.

**Features**:
- SQLite-based persistent storage
- Event types: ACTION, DECISION, API_CALL, APPROVAL, ERROR, SYSTEM, SOCIAL_POST, EMAIL, ACCOUNTING, AUTONOMOUS_TASK
- Severity levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Query interface with filtering
- Statistics generation
- Automatic log retention

**Key Classes**:
- `AuditLogger`: Main logging interface
- `AuditEventType`: Event type enumeration
- `AuditSeverity`: Severity level enumeration

**Usage**:
```python
from fte.audit import get_audit_logger, AuditEventType

logger = get_audit_logger()
logger.log_action("post_to_twitter", actor="system", resource="tweet_123")
logger.log_api_call("twitter", "/tweets", "POST", 200, actor="system")
```

### 2. Error Recovery & Resilience

**Location**: `src/fte/resilience/`

**Purpose**: Ensure system stability through retry mechanisms, circuit breakers, and graceful degradation.

**Features**:
- Circuit breaker pattern (CLOSED, OPEN, HALF_OPEN states)
- Exponential backoff retry strategy
- Health check system
- Fallback strategies
- Decorators for easy integration

**Key Classes**:
- `CircuitBreaker`: Prevents cascading failures
- `RetryStrategy`: Configurable retry logic
- `HealthCheck`: Service health monitoring
- `FallbackStrategy`: Graceful degradation

**Usage**:
```python
from fte.resilience import with_retry, get_circuit_breaker

@with_retry(max_attempts=3, initial_delay=2.0)
def api_call():
    # Your API call here
    pass

circuit_breaker = get_circuit_breaker("twitter_api")
result = circuit_breaker.call(api_function, *args)
```

### 3. Social Media Integration

**Location**: `src/fte/social/`

**Components**:
- `twitter_api.py`: Twitter/X API v2 integration
- `facebook_instagram_api.py`: Facebook Graph API for both platforms
- `linkedin_api.py`: LinkedIn API (existing)
- `linkedin_browser_automation.py`: Selenium fallback (existing)

**Features**:
- Post to Twitter, Facebook, Instagram
- Monitor mentions and engagement
- Generate engagement summaries
- Content generation from vault notes

**Usage**:
```python
from fte.social.twitter_api import TwitterAPI

twitter = TwitterAPI()
result = twitter.post_tweet("Hello from FTE Gold Tier!")
mentions = twitter.get_mentions(since_hours=24)
summary = twitter.generate_engagement_summary(mentions)
```

### 4. Odoo Accounting Integration

**Location**: `src/fte/mcp/odoo_mcp_server.py`

**Purpose**: Full accounting system integration via JSON-RPC.

**Features**:
- Invoice creation
- Payment recording
- Financial reports (P&L, Balance Sheet)
- Account balance queries
- Journal entries
- MCP server endpoints

**Setup**:
```bash
# Run Odoo setup
python -m fte.setup.odoo_setup odoo-fte
cd odoo-fte
docker-compose up -d
```

**Usage**:
```python
from fte.mcp.odoo_mcp_server import OdooClient

client = OdooClient(url="http://localhost:8069", db="odoo")
client.authenticate()

invoice_id = client.create_invoice(
    partner_id=1,
    invoice_lines=[{"product_id": 1, "quantity": 1, "price_unit": 100}]
)
```

### 5. Ralph Wiggum Autonomous Loop

**Location**: `src/fte/autonomous/ralph_wiggum_loop.py`

**Purpose**: Autonomous multi-step task completion with self-correction and learning.

**Features**:
- Goal decomposition into executable steps
- Task dependency management
- Step-by-step execution with retry
- Self-correction on failures
- Learning from outcomes
- Task status tracking

**Key Classes**:
- `RalphWiggumLoop`: Main autonomous system
- `AutonomousTask`: Task representation
- `TaskStatus`: Task state enumeration

**Usage**:
```python
from fte.autonomous import RalphWiggumLoop

ralph = RalphWiggumLoop()

# Register actions
ralph.register_action("send_email", send_email_func)
ralph.register_action("post_social", post_social_func)

# Create and execute task
task_id = ralph.create_task("Post weekly business update to social media")
result = ralph.execute_task(task_id)
```

### 6. Weekly Audit System

**Location**: `src/fte/audit/weekly_audit.py`

**Purpose**: Automated weekly business and accounting audits with CEO briefings.

**Features**:
- Business metrics gathering
- Accounting data from Odoo
- Trend analysis
- Insight generation
- CEO briefing document generation
- Automatic scheduling

**Usage**:
```python
from fte.audit.weekly_audit import WeeklyAuditSystem

audit = WeeklyAuditSystem()
briefing_path = audit.run_weekly_audit()
```

### 7. MCP Server Architecture

**Location**: `src/fte/mcp/`

**Components**:
- `mcp_router.py`: Central router for multiple MCP servers
- `odoo_mcp_server.py`: Accounting operations (port 8001)
- `enhanced_server.py`: General operations (port 8000)

**Specialized Servers**:
- **Social MCP** (port 8002): Social media operations
- **Accounting MCP** (port 8001): Odoo integration
- **Communication MCP** (port 8003): Email/messaging
- **Analytics MCP** (port 8004): Reporting and analytics
- **Router** (port 8000): Request routing

**Usage**:
```python
from fte.mcp.mcp_router import MCPRouter, MCPServerRegistry

registry = MCPServerRegistry()
router = MCPRouter(registry)

result = await router.route_request(
    "accounting-mcp",
    "/accounting/invoice",
    method="POST",
    data={"partner_id": 1, "invoice_lines": [...]}
)
```

### 8. Agent Skills (Gold Tier)

**Location**: `src/fte/skills/gold_tier_skills.py`

**New Skills**:
- `SocialMediaManagementSkill`: Multi-platform social media
- `AccountingManagementSkill`: Odoo operations
- `AutonomousTaskSkill`: Ralph Wiggum loop interface
- `WeeklyAuditSkill`: Automated audits

**Usage**:
```python
from fte.skills.gold_tier_skills import SocialMediaManagementSkill

skill = SocialMediaManagementSkill()
result = await skill.execute(
    action="post",
    platforms=["twitter", "facebook"],
    topic="business update"
)
```

### 9. Social Media Watchers

**Location**: `src/fte/watchers/social_media_watchers.py`

**Components**:
- `TwitterWatcher`: Monitor Twitter mentions
- `FacebookInstagramWatcher`: Monitor FB/IG engagement

**Features**:
- Automatic mention capture
- Daily engagement summaries
- Vault integration
- Configurable polling intervals

---

## Integration Patterns

### 1. API Integration Pattern

All external API integrations follow this pattern:

```python
class ExternalAPI:
    def __init__(self):
        self.audit_logger = get_audit_logger()
        self.circuit_breaker = get_circuit_breaker("service_name")

    @with_retry(max_attempts=3, initial_delay=2.0)
    def api_method(self, params):
        try:
            result = self.circuit_breaker.call(self._make_request, params)
            self.audit_logger.log_api_call(...)
            return result
        except Exception as e:
            self.audit_logger.log_error(...)
            raise
```

### 2. MCP Server Pattern

All MCP servers follow FastAPI structure:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Service MCP", version="1.0.0")

class RequestModel(BaseModel):
    param1: str
    param2: int

@app.post("/endpoint")
async def endpoint(request: RequestModel):
    try:
        # Process request
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Agent Skill Pattern

All agent skills inherit from `BaseSkill`:

```python
from fte.skills.framework import BaseSkill

class MySkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="my_skill",
            description="Description",
            version="1.0.0"
        )

    async def execute(self, **kwargs):
        # Skill logic
        return {"status": "success", "result": result}
```

---

## Data Flow

### 1. Social Media Posting Flow

```
User/Scheduler → Agent Skill → Social API → Platform
                      ↓
                 Audit Logger
                      ↓
                 Vault (record)
```

### 2. Accounting Operation Flow

```
User/Autonomous Task → MCP Router → Odoo MCP → Odoo Server
                            ↓
                       Audit Logger
                            ↓
                       Weekly Audit
```

### 3. Autonomous Task Flow

```
Goal → Ralph Wiggum → Decompose → Execute Steps → Learn
         ↓                ↓            ↓            ↓
    Task Storage    Action Registry  Retry Logic  Patterns
```

### 4. Weekly Audit Flow

```
Scheduler → Audit System → Gather Metrics → Analyze → Generate Briefing
                ↓              ↓              ↓           ↓
           Audit DB      Odoo + APIs    Insights    Vault/Done
```

---

## Security Architecture

### 1. Authentication

- **API Keys**: Environment variables for all external services
- **OAuth2**: Gmail, LinkedIn (token-based)
- **Odoo**: Username/password with session management
- **MCP Servers**: Optional API key authentication

### 2. Data Protection

- **Audit Logs**: SQLite with file permissions
- **Credentials**: Environment variables, never hardcoded
- **Tokens**: Pickle files with restricted permissions
- **Vault**: File system permissions

### 3. Network Security

- **MCP Servers**: Localhost by default
- **Odoo**: Docker network isolation
- **APIs**: HTTPS for external calls
- **Rate Limiting**: Circuit breakers prevent abuse

### 4. Error Handling

- **No Sensitive Data in Logs**: Sanitized error messages
- **Graceful Degradation**: Fallback strategies
- **Audit Trail**: All security events logged

---

## Deployment Guide

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- 8GB RAM minimum
- Ports: 8000-8004, 8069 available

### Installation Steps

#### 1. Install FTE Gold Tier

```bash
cd "E:\PIAIC\Quarter 5\FTE"
pip install -e .
```

#### 2. Install Additional Dependencies

```bash
pip install tweepy httpx
```

#### 3. Set Up Odoo

```bash
python -m fte.setup.odoo_setup odoo-fte
cd odoo-fte
docker-compose up -d
```

Access Odoo at http://localhost:8069 and complete initial setup.

#### 4. Configure Environment Variables

Create `.env` file:

```bash
# Twitter
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Facebook/Instagram
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_account_id

# LinkedIn (existing)
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password

# Gmail (existing)
# Use credentials.json and token.pickle

# WhatsApp (existing)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
WHATSAPP_NUMBER=your_number

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin
```

#### 5. Start MCP Servers

```bash
# Terminal 1: Main MCP Router
python -m fte.mcp.mcp_router

# Terminal 2: Odoo MCP Server
python -m fte.mcp.odoo_mcp_server

# Terminal 3: Enhanced MCP Server (existing)
fte-mcp --port 8000
```

#### 6. Start Watchers

```bash
# Gmail
fte gmail

# WhatsApp
fte whatsapp

# LinkedIn
fte linkedin

# Twitter (new)
python -m fte.watchers.social_media_watchers twitter

# Facebook/Instagram (new)
python -m fte.watchers.social_media_watchers facebook
```

#### 7. Schedule Weekly Audit

```python
from apscheduler.schedulers.background import BackgroundScheduler
from fte.skills.gold_tier_skills import WeeklyAuditSkill

scheduler = BackgroundScheduler()
audit_skill = WeeklyAuditSkill()

scheduler.add_job(
    lambda: audit_skill.execute(),
    'cron',
    day_of_week='mon',
    hour=9,
    minute=0
)

scheduler.start()
```

---

## Lessons Learned

### 1. Architecture Decisions

**✅ What Worked Well**:
- **Modular Design**: Separation of concerns made development and testing easier
- **Circuit Breakers**: Prevented cascading failures across services
- **Audit Logging**: Comprehensive tracking enabled debugging and compliance
- **Agent Skills**: Unified interface for all AI functionality
- **Docker for Odoo**: Simplified deployment and isolation

**⚠️ Challenges**:
- **API Rate Limits**: Required careful throttling and retry logic
- **LinkedIn API Deprecation**: Forced browser automation fallback
- **Multiple MCP Servers**: Increased complexity but improved modularity
- **Async/Sync Mix**: Required careful handling of async operations

### 2. Integration Insights

**Social Media**:
- Twitter API v2 is well-documented but requires elevated access
- Facebook Graph API is powerful but complex
- Instagram requires business account and Facebook page
- Rate limits vary significantly across platforms

**Accounting**:
- Odoo JSON-RPC is stable and well-supported
- Docker deployment is straightforward
- Initial setup requires manual configuration
- Financial reports need careful parsing

**Autonomous Operations**:
- Goal decomposition is challenging without AI
- Simple rule-based approach works for common patterns
- Learning from outcomes improves over time
- Task dependencies require careful management

### 3. Performance Considerations

**Bottlenecks**:
- API calls are the slowest operations
- SQLite is sufficient for audit logs
- Vault file operations are fast
- MCP routing adds minimal overhead

**Optimizations**:
- Parallel API calls where possible
- Caching for frequently accessed data
- Batch operations for bulk updates
- Connection pooling for databases

### 4. Operational Insights

**Monitoring**:
- Health checks are essential
- Audit statistics provide good overview
- Weekly briefings surface issues early
- Error rates indicate system health

**Maintenance**:
- Log retention prevents database bloat
- Regular Odoo backups are critical
- Token refresh needs monitoring
- Circuit breaker states need attention

---

## Future Enhancements

### Short Term (1-3 months)

1. **Enhanced AI Integration**
   - Use LLM for better goal decomposition
   - Improve content generation quality
   - Add sentiment analysis for social media

2. **Advanced Analytics**
   - Real-time dashboards
   - Predictive analytics
   - Trend forecasting

3. **Mobile App**
   - Approval workflow on mobile
   - Push notifications
   - Quick actions

### Medium Term (3-6 months)

1. **Multi-User Support**
   - Role-based access control
   - Team collaboration features
   - Shared vault spaces

2. **Advanced Automation**
   - More sophisticated autonomous tasks
   - Cross-platform workflows
   - Conditional logic

3. **Integration Expansion**
   - Slack integration
   - Microsoft Teams
   - Salesforce CRM

### Long Term (6-12 months)

1. **Enterprise Features**
   - Multi-tenant architecture
   - Advanced security (SSO, 2FA)
   - Compliance reporting

2. **AI Enhancements**
   - Custom model training
   - Personalized recommendations
   - Automated decision making

3. **Platform Expansion**
   - Cloud deployment options
   - Kubernetes orchestration
   - Global CDN

---

## Conclusion

FTE Gold Tier successfully implements a fully autonomous employee system with comprehensive integration across personal and business domains. The modular architecture, robust error handling, and extensive audit logging provide a solid foundation for future enhancements.

**Key Success Factors**:
- Modular, maintainable architecture
- Comprehensive error handling
- Extensive audit logging
- Agent Skills pattern for AI
- Docker-based deployment

**Next Steps**:
1. Deploy to production environment
2. Monitor system performance
3. Gather user feedback
4. Implement priority enhancements
5. Scale as needed

---

**Document Version**: 1.0.0
**Last Updated**: 2026-03-24
**Author**: FTE Development Team
**Status**: Complete
