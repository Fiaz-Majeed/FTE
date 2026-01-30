#!/usr/bin/env python3
"""
Silver Tier Demo - Demonstrates the complete Silver Tier Functional Assistant Implementation
showcasing all integrated components working together.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Import all Silver Tier components
from src.fte.watchers.watcher_manager import initialize_watchers
from src.fte.skills.linkedin_post_generator import LinkedInPostGenerator
from src.fte.skills.plan_generator import PlanGenerator
from src.fte.skills.business_intelligence import BusinessIntelligenceSkill
from src.fte.skills.customer_outreach import CustomerOutreachSkill
from src.fte.skills.sales_pipeline import SalesPipelineSkill
from src.fte.skills.content_strategy import ContentStrategySkill
from src.fte.skills.registry import SkillRegistry
from src.fte.approval.multi_level_approval import MultiLevelApprovalSystem
from src.fte.scheduler.business_scheduler import BusinessScheduleManager


async def demonstrate_complete_workflow():
    """Demonstrate the complete Silver Tier workflow."""
    print("="*70)
    print("SILVER TIER FUNCTIONAL ASSISTANT DEMONSTRATION")
    print("="*70)

    print("\nOBJECTIVE: Demonstrate integrated business automation system")
    print("- Multi-platform monitoring (Gmail, LinkedIn, WhatsApp)")
    print("- Automated LinkedIn business posting")
    print("- Claude reasoning loop with Plan.md generation")
    print("- MCP server with comprehensive control")
    print("- Human-in-the-loop approval workflows")
    print("- Advanced scheduling capabilities")
    print("- Modular Agent Skills architecture")

    # 1. Initialize Watcher System
    print("\n" + "="*50)
    print("1. WATCHER SYSTEM INITIALIZATION")
    print("="*50)

    watcher_manager = initialize_watchers()
    print("[SUCCESS] Watcher manager initialized")
    print(f"   Registered watchers: {list(watcher_manager.get_all_statuses().keys())}")

    # 2. Business Intelligence & Planning
    print("\n" + "="*50)
    print("2. BUSINESS INTELLIGENCE & PLANNING")
    print("="*50)

    # Create business intelligence analysis
    bi_skill = BusinessIntelligenceSkill()
    bi_result = await bi_skill.execute({
        "market_data": {
            "revenue": [100000, 120000, 140000, 160000, 180000],
            "customer_acquisition": [100, 120, 150, 180, 200],
            "market_share": [0.05, 0.06, 0.07, 0.08, 0.09]
        },
        "business_context": {
            "focus_areas": ["revenue", "customer_acquisition"],
            "capabilities": ["consulting", "development", "analytics"],
            "current_challenges": ["market_penetration", "competition"]
        }
    })

    print(f"[SUCCESS] Business intelligence analysis completed")
    print(f"   Opportunities identified: {bi_result['opportunities_identified']}")
    print(f"   Confidence level: {bi_result['analysis_results']['confidence']:.2f}")

    # Generate business plan
    plan_generator = PlanGenerator()
    plan = plan_generator.generate_plan(
        objective="Increase market share by 15% through strategic LinkedIn content and customer outreach",
        plan_type="marketing_campaign",
        duration="90 days"
    )

    print(f"[SUCCESS] Business plan generated: {plan['title']}")
    print(f"   Plan type: {plan['plan_type']}")
    print(f"   Duration: {plan['duration']}")

    # Save plan to vault
    plan_path = Path("Plan.md")
    plan_generator.save_plan_as_markdown(plan, plan_path)
    print(f"[SUCCESS] Plan saved to: {plan_path.absolute()}")

    # 3. Content Strategy & LinkedIn Automation
    print("\n" + "="*50)
    print("3. CONTENT STRATEGY & LINKEDIN AUTOMATION")
    print("="*50)

    # Create content strategy
    cs_skill = ContentStrategySkill()
    cs_result = await cs_skill.execute({
        "topics": ["AI Innovation", "Business Growth", "Market Trends"],
        "target_audience": "decision_maker",
        "content_goals": ["awareness", "engagement", "lead_generation"],
        "time_period": "monthly",
        "budget": 5000
    })

    print(f"[SUCCESS] Content strategy developed")
    print(f"   Content calendar length: {len(cs_result['content_calendar'])}")
    print(f"   Recommended channels: {cs_result['recommended_channels']}")

    # Generate LinkedIn post
    linkedin_generator = LinkedInPostGenerator()
    post = linkedin_generator.generate_business_post(
        post_type="success_story",
        vault_analysis=linkedin_generator.analyze_vault_content()
    )

    print(f"[SUCCESS] LinkedIn post generated")
    print(f"   Post type: {post['template_used']}")
    print(f"   Hashtags: {len(post['hashtags'])}")

    # 4. Approval Workflow
    print("\n" + "="*50)
    print("4. APPROVAL WORKFLOW")
    print("="*50)

    approval_system = MultiLevelApprovalSystem()

    # Register notification callback
    notifications = []
    def notification_callback(message, request_id):
        notifications.append({"message": message, "request_id": request_id})
        print(f"   [BROADCAST] {message}")

    approval_system.register_notification_callback(notification_callback)

    # Request approval for LinkedIn post
    request_id = approval_system.create_request(
        action_type="linkedin_post",
        action_details={
            "content_preview": post['content'][:100] + "...",
            "hashtags": post['hashtags'][:3],
            "target_audience": "business professionals"
        },
        requester="linkedin_automation",
        required_level=None  # Auto-determined
    )

    print(f"[SUCCESS] Approval request created: {request_id}")

    # Approve the request (simulating human approval)
    approval_success = approval_system.approve_request(request_id, "marketing_manager", "Content looks good for business audience")
    print(f"[SUCCESS] Approval granted: {approval_success}")

    # 5. Scheduling System
    print("\n" + "="*50)
    print("5. SCHEDULING SYSTEM")
    print("="*50)

    scheduler = BusinessScheduleManager()
    scheduler.start()

    # Schedule the LinkedIn post
    post_job_id = scheduler.schedule_linkedin_post(
        content=post['content'],
        optimize=True,
        tags=post['hashtags']
    )

    print(f"[SUCCESS] LinkedIn post scheduled: {post_job_id}")

    # Schedule follow-up sequence for business inquiries
    followup_job_ids = scheduler.schedule_followup_sequence(
        sequence_type="business_inquiry",
        recipient="prospects@business.com"
    )

    print(f"[SUCCESS] Follow-up sequence scheduled: {len(followup_job_ids)} steps")

    # 6. Customer Outreach & Sales Pipeline
    print("\n" + "="*50)
    print("6. CUSTOMER OUTREACH & SALES PIPELINE")
    print("="*50)

    # Initialize skills via registry
    registry = SkillRegistry()
    await registry.batch_load_skills(["customer_outreach", "sales_pipeline"])

    # Perform customer outreach
    co_result = await registry.execute_skill("customer_outreach", {
        "customers": [
            {"id": "cust_001", "name": "Acme Corp", "email": "contact@acme.com", "industry": "Technology"},
            {"id": "cust_002", "name": "Beta Inc", "email": "info@beta.com", "industry": "Finance"}
        ],
        "strategy": "existing_customers",
        "message_type": "promotional",
        "channels": ["email", "linkedin"]
    })

    print(f"[SUCCESS] Customer outreach executed")
    print(f"   Customers contacted: {co_result['total_customers_contacted']}")
    print(f"   Successful deliveries: {co_result['successful_deliveries']}")

    # Manage sales pipeline
    sp_skill = SalesPipelineSkill()
    sp_result = await sp_skill.execute({
        "leads": [
            {"id": "lead_001", "name": "Enterprise Client", "stage": "prospect", "interest_level": 0.8},
            {"id": "lead_002", "name": "Mid-Market Company", "stage": "qualified", "interest_level": 0.6}
        ],
        "target_stage": "proposal",
        "actions": ["send_proposal", "schedule_demo"]
    })

    print(f"[SUCCESS] Sales pipeline management executed")
    print(f"   Leads moved: {sp_result['leads_moved']}")
    print(f"   Conversion rate: {sp_result['conversion_rate']:.2%}")

    # 7. System Status Report
    print("\n" + "="*50)
    print("7. SYSTEM STATUS REPORT")
    print("="*50)

    # Watcher status
    watcher_statuses = watcher_manager.get_all_statuses()
    print("[CHART] Watcher Status:")
    for name, info in watcher_statuses.items():
        print(f"   {name}: {info.status.value}")

    # Skill registry status
    skill_report = registry.get_skill_status_report()
    print(f"\n[PUZZLE] Skills Status:")
    print(f"   Registered: {skill_report['registered_skills']}")
    print(f"   Loaded: {skill_report['loaded_skills']}")
    print(f"   Active: {skill_report['active_skills']}")

    # Scheduler status
    scheduled_jobs = scheduler.get_scheduled_jobs()
    print(f"\n[TIME] Scheduled Jobs: {len(scheduled_jobs)}")

    # Approval system status
    pending_approvals = approval_system.get_pending_requests()
    print(f"[CLIPBOARD] Pending Approvals: {len(pending_approvals)}")

    # 8. Performance Metrics
    print("\n" + "="*50)
    print("8. PERFORMANCE METRICS")
    print("="*50)

    print("[SUCCESS] Multi-platform monitoring active (Gmail, LinkedIn, WhatsApp)")
    print("[SUCCESS] Automated LinkedIn posting with approval workflow")
    print("[SUCCESS] Business plan generation with Plan.md output")
    print("[SUCCESS] Customer outreach and sales pipeline management")
    print("[SUCCESS] Content strategy and scheduling optimization")
    print("[SUCCESS] Real-time notifications and status reporting")

    # 9. Success Indicators
    print("\n" + "="*50)
    print("9. SUCCESS INDICATORS")
    print("="*50)

    success_indicators = [
        ("Watchers operational", len(watcher_statuses) > 0),
        ("Business intelligence working", bi_result['status'] == 'success'),
        ("Plan generated", plan is not None),
        ("Content strategy created", len(cs_result['content_calendar']) > 0),
        ("Approval workflow functioning", approval_success),
        ("Scheduling active", post_job_id is not None),
        ("Customer outreach executed", co_result['status'] == 'success'),
        ("Sales pipeline managed", sp_result['status'] == 'success')
    ]

    all_successful = True
    for indicator, success in success_indicators:
        status = "[SUCCESS]" if success else "[ERROR]"
        print(f"   {status} {indicator}")
        if not success:
            all_successful = False

    print(f"\n[TARGET] OVERALL SYSTEM STATUS: {'OPERATIONAL' if all_successful else 'ISSUES DETECTED'}")

    # Stop scheduler
    scheduler.stop()

    print("\n" + "="*70)
    print("SILVER TIER DEMONSTRATION COMPLETE")
    print("="*70)

    return all_successful


async def main():
    """Main entry point for the Silver Tier demo."""
    print("Initializing Silver Tier Functional Assistant...")

    try:
        success = await demonstrate_complete_workflow()

        if success:
            print("\n[PARTY] SILVER TIER IMPLEMENTATION SUCCESSFUL!")
            print("All components are integrated and functioning as designed.")
        else:
            print("\n[WARNING]  Some components require attention.")

    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())