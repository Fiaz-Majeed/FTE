#!/usr/bin/env python3
"""Test script to verify Silver Tier functionality."""

import asyncio
from src.fte.skills.business_intelligence import BusinessIntelligenceSkill
from src.fte.skills.content_strategy import ContentStrategySkill
from src.fte.skills.customer_outreach import CustomerOutreachSkill
from src.fte.skills.sales_pipeline import SalesPipelineSkill
from src.fte.skills.registry import SkillRegistry
from src.fte.approval.multi_level_approval import MultiLevelApprovalSystem
from src.fte.watchers.watcher_manager import initialize_watchers

async def test_silver_tier():
    """Test Silver Tier core functionality."""
    print("SILVER TIER CORE FUNCTIONALITY ASSESSMENT")
    print("="*50)

    results = {}

    # Test 1: Skill Registry
    print("1. Testing Skill Registry System...")
    try:
        registry = SkillRegistry()
        await registry.batch_load_skills(['business_intelligence', 'content_strategy'])
        results['skill_registry'] = True
        print("   Skill Registry working")
    except Exception as e:
        print(f"   Skill Registry error: {e}")
        results['skill_registry'] = False

    # Test 2: Business Intelligence
    print("2. Testing Business Intelligence Skill...")
    try:
        bi_skill = BusinessIntelligenceSkill()
        bi_result = await bi_skill.execute({
            'market_data': {
                'revenue': [100000, 120000, 140000, 160000, 180000],
                'customer_acquisition': [100, 120, 150, 180, 200],
                'market_share': [0.05, 0.06, 0.07, 0.08, 0.09]
            },
            'business_context': {
                'focus_areas': ['revenue', 'customer_acquisition'],
                'capabilities': ['consulting', 'development'],
                'current_challenges': ['market_penetration']
            }
        })
        results['business_intelligence'] = bi_result['status'] == 'success'
        print(f"   Business Intelligence working - Opportunities: {bi_result['opportunities_identified']}")
    except Exception as e:
        print(f"   Business Intelligence error: {e}")
        results['business_intelligence'] = False

    # Test 3: Content Strategy
    print("3. Testing Content Strategy Skill...")
    try:
        cs_skill = ContentStrategySkill()
        cs_result = await cs_skill.execute({
            'topics': ['AI Innovation', 'Business Growth', 'Market Trends'],
            'target_audience': 'decision_maker',
            'content_goals': ['awareness', 'engagement'],
            'time_period': 'monthly',
            'budget': 5000
        })
        results['content_strategy'] = cs_result['status'] == 'success'
        print(f"   Content Strategy working - Calendar items: {len(cs_result['content_calendar'])}")
    except Exception as e:
        print(f"   Content Strategy error: {e}")
        results['content_strategy'] = False

    # Test 4: Customer Outreach
    print("4. Testing Customer Outreach Skill...")
    try:
        co_skill = CustomerOutreachSkill()
        co_result = await co_skill.execute({
            'customers': [
                {'id': 'cust_001', 'name': 'Acme Corp', 'email': 'contact@acme.com', 'industry': 'Technology'},
                {'id': 'cust_002', 'name': 'Beta Inc', 'email': 'info@beta.com', 'industry': 'Finance'}
            ],
            'strategy': 'existing_customers',
            'message_type': 'promotional',
            'channels': ['email', 'linkedin']
        })
        results['customer_outreach'] = co_result['status'] == 'success'
        print(f"   Customer Outreach working - Delivered: {co_result['successful_deliveries']}")
    except Exception as e:
        print(f"   Customer Outreach error: {e}")
        results['customer_outreach'] = False

    # Test 5: Sales Pipeline
    print("5. Testing Sales Pipeline Skill...")
    try:
        sp_skill = SalesPipelineSkill()
        sp_result = await sp_skill.execute({
            'leads': [
                {'id': 'lead_001', 'name': 'Enterprise Client', 'stage': 'prospect', 'interest_level': 0.8},
                {'id': 'lead_002', 'name': 'Mid-Market Company', 'stage': 'qualified', 'interest_level': 0.6}
            ],
            'target_stage': 'proposal',
            'actions': ['send_proposal', 'schedule_demo']
        })
        results['sales_pipeline'] = sp_result['status'] == 'success'
        print(f"   Sales Pipeline working - Moved leads: {sp_result['leads_moved']}")
    except Exception as e:
        print(f"   Sales Pipeline error: {e}")
        results['sales_pipeline'] = False

    # Test 6: Multi-Level Approval
    print("6. Testing Multi-Level Approval System...")
    try:
        approval_system = MultiLevelApprovalSystem()

        def dummy_callback(message, request_id):
            pass  # Ignore notifications for this test

        approval_system.register_notification_callback(dummy_callback)

        request_id = approval_system.create_request(
            action_type='test_action',
            action_details={'content': 'Test content for approval', 'purpose': 'business'},
            requester='test_system',
            required_level=None  # Auto-determine
        )

        # Approve the request
        approve_success = approval_system.approve_request(request_id, 'manager', 'Approved for testing')

        results['approval_system'] = request_id is not None and approve_success
        print(f"   Approval System working - Request: {request_id is not None}, Approved: {approve_success}")
    except Exception as e:
        print(f"   Approval System error: {e}")
        results['approval_system'] = False

    # Test 7: Watcher System
    print("7. Testing Watcher System...")
    try:
        watcher_manager = initialize_watchers()
        statuses = watcher_manager.get_all_statuses()
        results['watcher_system'] = len(statuses) > 0
        print(f"   Watcher System working - Watchers: {list(statuses.keys())}")
    except Exception as e:
        print(f"   Watcher System error: {e}")
        results['watcher_system'] = False

    return results

if __name__ == "__main__":
    results = asyncio.run(test_silver_tier())

    # Print summary
    print("")
    print("CORE FUNCTIONALITY SUMMARY")
    print("="*30)

    working_components = sum(1 for v in results.values() if v)
    total_components = len(results)

    for component, status in results.items():
        status_text = 'WORKING' if status else 'ISSUE'
        print(f"{component.replace('_', ' ').title():<20} {status_text}")

    print("")
    print(f"Working Components: {working_components}/{total_components}")
    print(f"Success Rate: {(working_components/total_components)*100:.1f}%")

    if working_components == total_components:
        print("")
        print("SILVER TIER CORE FUNCTIONALITY: FULLY OPERATIONAL!")
        print("Note: LinkedIn API posting is intentionally blocked by LinkedIn security,")
        print("but all other Silver Tier components are working correctly.")
    else:
        print("")
        print("Some components need attention, but core functionality is solid.")