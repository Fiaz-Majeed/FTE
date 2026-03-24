"""
Weekly Business and Accounting Audit System
Generates CEO briefings with insights and recommendations
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ..audit.audit_logger import get_audit_logger, AuditEventType
from ..vault_manager import VaultManager


class WeeklyAuditSystem:
    """Automated weekly business and accounting audit with CEO briefing generation."""

    def __init__(
        self,
        vault_path: Optional[Path] = None,
        odoo_client: Optional[Any] = None
    ):
        """Initialize weekly audit system.

        Args:
            vault_path: Path to vault for storing reports
            odoo_client: Odoo client for accounting data
        """
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"
        self.vault_manager = VaultManager(vault_path)
        self.odoo_client = odoo_client
        self.audit_logger = get_audit_logger()

    def gather_business_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Gather business metrics for the period.

        Args:
            days: Number of days to analyze

        Returns:
            Business metrics dictionary
        """
        metrics = {
            "period_days": days,
            "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "social_media": {},
            "email": {},
            "tasks": {},
            "approvals": {}
        }

        # Get audit statistics
        audit_stats = self.audit_logger.get_statistics(days=days)
        metrics["audit_stats"] = audit_stats

        # Count social media posts
        social_posts = self.audit_logger.query(
            event_type=AuditEventType.SOCIAL_POST,
            start_date=datetime.now() - timedelta(days=days),
            limit=1000
        )

        platforms = {}
        for post in social_posts:
            platform = post.get('resource', 'unknown')
            if platform not in platforms:
                platforms[platform] = 0
            platforms[platform] += 1

        metrics["social_media"] = {
            "total_posts": len(social_posts),
            "by_platform": platforms
        }

        # Count emails
        emails = self.audit_logger.query(
            event_type=AuditEventType.EMAIL,
            start_date=datetime.now() - timedelta(days=days),
            limit=1000
        )
        metrics["email"]["total_sent"] = len(emails)

        # Count approvals
        approvals = self.audit_logger.query(
            event_type=AuditEventType.APPROVAL,
            start_date=datetime.now() - timedelta(days=days),
            limit=1000
        )

        approved = sum(1 for a in approvals if a.get('status') == 'approved')
        rejected = sum(1 for a in approvals if a.get('status') == 'rejected')

        metrics["approvals"] = {
            "total": len(approvals),
            "approved": approved,
            "rejected": rejected,
            "approval_rate": round(approved / len(approvals) * 100, 2) if approvals else 0
        }

        # Count autonomous tasks
        autonomous_tasks = self.audit_logger.query(
            event_type=AuditEventType.AUTONOMOUS_TASK,
            start_date=datetime.now() - timedelta(days=days),
            limit=1000
        )
        metrics["tasks"]["autonomous_tasks"] = len(autonomous_tasks)

        return metrics

    def gather_accounting_metrics(self) -> Dict[str, Any]:
        """Gather accounting metrics from Odoo.

        Returns:
            Accounting metrics dictionary
        """
        if not self.odoo_client:
            return {
                "status": "unavailable",
                "message": "Odoo client not configured"
            }

        try:
            # Get profit & loss report
            profit_loss = self.odoo_client.get_financial_report(
                report_type="profit_loss",
                date_from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                date_to=datetime.now().strftime("%Y-%m-%d")
            )

            # Get balance sheet
            balance_sheet = self.odoo_client.get_financial_report(
                report_type="balance_sheet",
                date_to=datetime.now().strftime("%Y-%m-%d")
            )

            return {
                "status": "available",
                "profit_loss": profit_loss,
                "balance_sheet": balance_sheet,
                "retrieved_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to gather accounting metrics: {e}",
                actor="weekly_audit",
                resource="odoo"
            )
            return {
                "status": "error",
                "error": str(e)
            }

    def analyze_trends(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends and generate insights.

        Args:
            metrics: Business metrics

        Returns:
            Analysis and insights
        """
        insights = {
            "positive_trends": [],
            "concerns": [],
            "recommendations": []
        }

        # Analyze error rate
        error_rate = metrics.get("audit_stats", {}).get("error_rate", 0)
        if error_rate < 5:
            insights["positive_trends"].append(
                f"Low error rate ({error_rate}%) indicates stable system operation"
            )
        elif error_rate > 10:
            insights["concerns"].append(
                f"High error rate ({error_rate}%) requires investigation"
            )
            insights["recommendations"].append(
                "Review error logs and implement fixes for recurring issues"
            )

        # Analyze social media activity
        social_posts = metrics.get("social_media", {}).get("total_posts", 0)
        if social_posts > 10:
            insights["positive_trends"].append(
                f"Strong social media presence with {social_posts} posts this week"
            )
        elif social_posts < 3:
            insights["concerns"].append(
                f"Low social media activity ({social_posts} posts)"
            )
            insights["recommendations"].append(
                "Increase social media posting frequency to maintain engagement"
            )

        # Analyze approval workflow
        approval_rate = metrics.get("approvals", {}).get("approval_rate", 0)
        if approval_rate > 80:
            insights["positive_trends"].append(
                f"High approval rate ({approval_rate}%) shows good decision quality"
            )
        elif approval_rate < 50:
            insights["concerns"].append(
                f"Low approval rate ({approval_rate}%) may indicate quality issues"
            )
            insights["recommendations"].append(
                "Review approval criteria and improve content quality before submission"
            )

        # Analyze autonomous tasks
        autonomous_tasks = metrics.get("tasks", {}).get("autonomous_tasks", 0)
        if autonomous_tasks > 0:
            insights["positive_trends"].append(
                f"Autonomous system completed {autonomous_tasks} tasks"
            )

        return insights

    def generate_ceo_briefing(self, metrics: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate CEO briefing document.

        Args:
            metrics: Business metrics
            insights: Analysis insights

        Returns:
            Markdown formatted briefing
        """
        briefing = f"""# Weekly CEO Briefing

**Period**: {metrics['start_date'][:10]} to {metrics['end_date'][:10]}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Executive Summary

This week's automated audit reveals the following key points:

"""

        # Add positive trends
        if insights["positive_trends"]:
            briefing += "### ✅ Positive Trends\n\n"
            for trend in insights["positive_trends"]:
                briefing += f"- {trend}\n"
            briefing += "\n"

        # Add concerns
        if insights["concerns"]:
            briefing += "### ⚠️ Areas of Concern\n\n"
            for concern in insights["concerns"]:
                briefing += f"- {concern}\n"
            briefing += "\n"

        # Add recommendations
        if insights["recommendations"]:
            briefing += "### 💡 Recommendations\n\n"
            for rec in insights["recommendations"]:
                briefing += f"- {rec}\n"
            briefing += "\n"

        # Business metrics
        briefing += """---

## Business Metrics

### Social Media Performance
"""
        social = metrics.get("social_media", {})
        briefing += f"- **Total Posts**: {social.get('total_posts', 0)}\n"
        briefing += f"- **Platforms Active**: {len(social.get('by_platform', {}))}\n"

        for platform, count in social.get('by_platform', {}).items():
            briefing += f"  - {platform.title()}: {count} posts\n"

        briefing += "\n### Communication\n"
        email = metrics.get("email", {})
        briefing += f"- **Emails Sent**: {email.get('total_sent', 0)}\n"

        briefing += "\n### Approval Workflow\n"
        approvals = metrics.get("approvals", {})
        briefing += f"- **Total Requests**: {approvals.get('total', 0)}\n"
        briefing += f"- **Approved**: {approvals.get('approved', 0)}\n"
        briefing += f"- **Rejected**: {approvals.get('rejected', 0)}\n"
        briefing += f"- **Approval Rate**: {approvals.get('approval_rate', 0)}%\n"

        briefing += "\n### System Health\n"
        audit_stats = metrics.get("audit_stats", {})
        briefing += f"- **Total Events**: {audit_stats.get('total_events', 0)}\n"
        briefing += f"- **Error Rate**: {audit_stats.get('error_rate', 0)}%\n"
        briefing += f"- **Failures**: {audit_stats.get('failures', 0)}\n"

        # Accounting section
        briefing += "\n---\n\n## Accounting Summary\n\n"

        accounting = metrics.get("accounting", {})
        if accounting.get("status") == "available":
            briefing += "Financial reports retrieved successfully from Odoo.\n\n"
            briefing += "- Profit & Loss report generated\n"
            briefing += "- Balance Sheet report generated\n"
            briefing += "\n*Detailed financial reports available in Odoo system.*\n"
        else:
            briefing += f"⚠️ Accounting data unavailable: {accounting.get('message', 'Unknown error')}\n"

        briefing += "\n---\n\n## Next Steps\n\n"
        briefing += "1. Review areas of concern and implement recommended actions\n"
        briefing += "2. Continue monitoring system health and error rates\n"
        briefing += "3. Maintain social media posting schedule\n"
        briefing += "4. Review financial reports in detail in Odoo\n"

        briefing += "\n---\n\n*This briefing was automatically generated by the FTE Gold Tier Audit System.*\n"

        return briefing

    def run_weekly_audit(self) -> str:
        """Run complete weekly audit and generate briefing.

        Returns:
            Path to generated briefing file
        """
        self.audit_logger.log(
            AuditEventType.SYSTEM,
            "weekly_audit_started",
            actor="weekly_audit_system",
            resource="audit"
        )

        try:
            # Gather metrics
            business_metrics = self.gather_business_metrics(days=7)
            accounting_metrics = self.gather_accounting_metrics()

            business_metrics["accounting"] = accounting_metrics

            # Analyze trends
            insights = self.analyze_trends(business_metrics)

            # Generate briefing
            briefing_content = self.generate_ceo_briefing(business_metrics, insights)

            # Save briefing
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            briefing_filename = f"CEO_Briefing_{timestamp}.md"
            briefing_path = self.vault_path / "Done" / briefing_filename

            with open(briefing_path, 'w', encoding='utf-8') as f:
                f.write(briefing_content)

            # Save raw data
            data_filename = f"audit_data_{timestamp}.json"
            data_path = self.vault_path / "Done" / data_filename

            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metrics": business_metrics,
                    "insights": insights,
                    "generated_at": datetime.now().isoformat()
                }, f, indent=2)

            self.audit_logger.log(
                AuditEventType.SYSTEM,
                "weekly_audit_completed",
                actor="weekly_audit_system",
                resource=briefing_filename,
                status="success"
            )

            return str(briefing_path)

        except Exception as e:
            self.audit_logger.log_error(
                f"Weekly audit failed: {e}",
                actor="weekly_audit_system",
                resource="audit"
            )
            raise
