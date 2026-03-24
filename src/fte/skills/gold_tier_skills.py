"""
Social Media Management Skill - Agent Skill for Gold Tier
Manages posting and monitoring across Twitter, Facebook, and Instagram
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..skills.framework import BaseSkill
from ..social.twitter_api import TwitterAPI, TwitterContentGenerator
from ..social.facebook_instagram_api import FacebookAPI, SocialMediaContentGenerator
from ..audit.audit_logger import get_audit_logger


class SocialMediaManagementSkill(BaseSkill):
    """Agent skill for managing social media across multiple platforms."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize social media management skill.

        Args:
            vault_path: Path to vault
        """
        super().__init__(
            name="social_media_management",
            description="Manage social media posting and monitoring across Twitter, Facebook, and Instagram",
            version="1.0.0"
        )
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"

        self.twitter_api = TwitterAPI()
        self.facebook_api = FacebookAPI()
        self.twitter_content = TwitterContentGenerator(vault_path)
        self.social_content = SocialMediaContentGenerator(vault_path)
        self.audit_logger = get_audit_logger()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute social media management task.

        Args:
            action: Action to perform (post, monitor, summary)
            platforms: List of platforms (twitter, facebook, instagram)
            content: Content to post (optional)
            topic: Topic for content generation (optional)

        Returns:
            Execution result
        """
        action = kwargs.get("action", "summary")
        platforms = kwargs.get("platforms", ["twitter", "facebook", "instagram"])
        content = kwargs.get("content")
        topic = kwargs.get("topic", "business update")

        results = {
            "action": action,
            "platforms": platforms,
            "results": {}
        }

        if action == "post":
            # Post to specified platforms
            for platform in platforms:
                try:
                    if platform == "twitter":
                        if not content:
                            content = self.twitter_content.generate_business_update(topic)
                        result = self.twitter_api.post_tweet(content)
                        results["results"][platform] = {
                            "status": "success",
                            "post_id": result["id"],
                            "url": result["url"]
                        }

                    elif platform == "facebook":
                        if not content:
                            post_data = self.social_content.generate_facebook_post(topic)
                            content = post_data["message"]
                        result = self.facebook_api.post_to_facebook(content)
                        results["results"][platform] = {
                            "status": "success",
                            "post_id": result["id"],
                            "url": result["url"]
                        }

                    elif platform == "instagram":
                        # Instagram requires image URL
                        image_url = kwargs.get("image_url")
                        if not image_url:
                            results["results"][platform] = {
                                "status": "skipped",
                                "reason": "Instagram requires image_url parameter"
                            }
                            continue

                        if not content:
                            content = self.social_content.generate_instagram_caption(topic)
                        result = self.facebook_api.post_to_instagram(image_url, content)
                        results["results"][platform] = {
                            "status": "success",
                            "post_id": result["id"]
                        }

                except Exception as e:
                    results["results"][platform] = {
                        "status": "error",
                        "error": str(e)
                    }

        elif action == "monitor":
            # Monitor platforms for engagement
            for platform in platforms:
                try:
                    if platform == "twitter":
                        mentions = self.twitter_api.get_mentions(since_hours=24)
                        results["results"][platform] = {
                            "status": "success",
                            "mentions": len(mentions),
                            "data": mentions[:5]  # First 5 mentions
                        }

                    elif platform == "facebook":
                        insights = self.facebook_api.get_facebook_insights(days=1)
                        results["results"][platform] = {
                            "status": "success",
                            "insights": insights
                        }

                    elif platform == "instagram":
                        insights = self.facebook_api.get_instagram_insights(days=1)
                        results["results"][platform] = {
                            "status": "success",
                            "insights": insights
                        }

                except Exception as e:
                    results["results"][platform] = {
                        "status": "error",
                        "error": str(e)
                    }

        elif action == "summary":
            # Generate engagement summaries
            for platform in platforms:
                try:
                    if platform == "twitter":
                        tweets = self.twitter_api.get_user_tweets("me", max_results=10)
                        summary = self.twitter_api.generate_engagement_summary(tweets)
                        results["results"][platform] = {
                            "status": "success",
                            "summary": summary
                        }

                    elif platform in ["facebook", "instagram"]:
                        summary = self.facebook_api.generate_summary(platform, days=7)
                        results["results"][platform] = {
                            "status": "success",
                            "summary": summary
                        }

                except Exception as e:
                    results["results"][platform] = {
                        "status": "error",
                        "error": str(e)
                    }

        self.audit_logger.log_action(
            action=f"social_media_{action}",
            actor="social_media_management_skill",
            resource=",".join(platforms),
            status="success"
        )

        return results


class AccountingManagementSkill(BaseSkill):
    """Agent skill for managing accounting operations via Odoo."""

    def __init__(self):
        """Initialize accounting management skill."""
        super().__init__(
            name="accounting_management",
            description="Manage accounting operations through Odoo integration",
            version="1.0.0"
        )
        from ..mcp.odoo_mcp_server import OdooClient
        self.odoo_client = OdooClient()
        self.audit_logger = get_audit_logger()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute accounting management task.

        Args:
            action: Action to perform (invoice, payment, report, balance)
            **kwargs: Action-specific parameters

        Returns:
            Execution result
        """
        action = kwargs.get("action", "report")

        try:
            if action == "invoice":
                invoice_id = self.odoo_client.create_invoice(
                    partner_id=kwargs["partner_id"],
                    invoice_lines=kwargs["invoice_lines"],
                    invoice_type=kwargs.get("invoice_type", "out_invoice")
                )
                return {
                    "status": "success",
                    "action": "invoice",
                    "invoice_id": invoice_id
                }

            elif action == "payment":
                payment_id = self.odoo_client.create_payment(
                    amount=kwargs["amount"],
                    partner_id=kwargs["partner_id"],
                    payment_type=kwargs.get("payment_type", "inbound"),
                    journal_id=kwargs.get("journal_id")
                )
                return {
                    "status": "success",
                    "action": "payment",
                    "payment_id": payment_id
                }

            elif action == "report":
                report = self.odoo_client.get_financial_report(
                    report_type=kwargs.get("report_type", "profit_loss"),
                    date_from=kwargs.get("date_from"),
                    date_to=kwargs.get("date_to")
                )
                return {
                    "status": "success",
                    "action": "report",
                    "report": report
                }

            elif action == "balance":
                balance = self.odoo_client.get_account_balance(kwargs["account_id"])
                return {
                    "status": "success",
                    "action": "balance",
                    "account_id": kwargs["account_id"],
                    "balance": balance
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            self.audit_logger.log_error(
                f"Accounting operation failed: {e}",
                actor="accounting_management_skill",
                resource=action
            )
            return {
                "status": "error",
                "action": action,
                "error": str(e)
            }


class AutonomousTaskSkill(BaseSkill):
    """Agent skill for autonomous task execution."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize autonomous task skill.

        Args:
            vault_path: Path to vault
        """
        super().__init__(
            name="autonomous_task",
            description="Execute autonomous multi-step tasks using Ralph Wiggum Loop",
            version="1.0.0"
        )
        from ..autonomous.ralph_wiggum_loop import RalphWiggumLoop
        self.ralph = RalphWiggumLoop(vault_path)
        self.audit_logger = get_audit_logger()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute autonomous task.

        Args:
            action: Action to perform (create, execute, status, list)
            goal: Task goal (for create)
            task_id: Task ID (for execute/status)

        Returns:
            Execution result
        """
        action = kwargs.get("action", "list")

        try:
            if action == "create":
                task_id = self.ralph.create_task(
                    goal=kwargs["goal"],
                    dependencies=kwargs.get("dependencies"),
                    metadata=kwargs.get("metadata")
                )
                return {
                    "status": "success",
                    "action": "create",
                    "task_id": task_id
                }

            elif action == "execute":
                result = self.ralph.execute_task(kwargs["task_id"])
                return {
                    "status": "success",
                    "action": "execute",
                    "result": result
                }

            elif action == "status":
                status = self.ralph.get_task_status(kwargs["task_id"])
                return {
                    "status": "success",
                    "action": "status",
                    "task_status": status
                }

            elif action == "list":
                from ..autonomous.ralph_wiggum_loop import TaskStatus
                status_filter = kwargs.get("status_filter")
                if status_filter:
                    status_filter = TaskStatus(status_filter)
                tasks = self.ralph.list_tasks(status_filter)
                return {
                    "status": "success",
                    "action": "list",
                    "tasks": tasks
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            self.audit_logger.log_error(
                f"Autonomous task operation failed: {e}",
                actor="autonomous_task_skill",
                resource=action
            )
            return {
                "status": "error",
                "action": action,
                "error": str(e)
            }


class WeeklyAuditSkill(BaseSkill):
    """Agent skill for running weekly audits."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize weekly audit skill.

        Args:
            vault_path: Path to vault
        """
        super().__init__(
            name="weekly_audit",
            description="Run weekly business and accounting audit with CEO briefing",
            version="1.0.0"
        )
        from ..audit.weekly_audit import WeeklyAuditSystem
        from ..mcp.odoo_mcp_server import OdooClient

        try:
            odoo_client = OdooClient()
            odoo_client.authenticate()
        except:
            odoo_client = None

        self.audit_system = WeeklyAuditSystem(vault_path, odoo_client)
        self.audit_logger = get_audit_logger()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute weekly audit.

        Returns:
            Execution result with briefing path
        """
        try:
            briefing_path = self.audit_system.run_weekly_audit()
            return {
                "status": "success",
                "briefing_path": briefing_path,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Weekly audit failed: {e}",
                actor="weekly_audit_skill",
                resource="audit"
            )
            return {
                "status": "error",
                "error": str(e)
            }
