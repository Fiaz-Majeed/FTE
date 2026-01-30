"""Setup and Demo for LinkedIn Auto Posting"""

import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Add the src directory to the path so we can import fte modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_linkedin_demo():
    """Setup and demonstrate LinkedIn auto posting."""

    print("LinkedIn Auto Posting Setup & Demo")
    print("=" * 50)

    # Show current config
    print("\nCurrent Configuration:")
    config_path = Path("config.json")
    if config_path.exists():
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)

        mcp_enabled = config.get("MCP", {}).get("enabled", False)
        linkedin_enabled = config.get("Watchers", {}).get("linkedin", {}).get("enabled", False)

        print(f"  - MCP Server Enabled: {mcp_enabled}")
        print(f"  - LinkedIn Watcher Enabled: {linkedin_enabled}")
        print(f"  - LinkedIn Poll Interval: {config.get('Watchers', {}).get('linkedin', {}).get('poll_interval', 300)}s")
    else:
        print("  - config.json not found")

    print("\nLinkedIn Credentials Setup:")
    print("To use LinkedIn posting, you need to set credentials.")
    print("\nOption 1: Environment Variables (recommended)")
    print("  set LINKEDIN_USERNAME=your_email@example.com")
    print("  set LINKEDIN_PASSWORD=your_password")
    print("  (On Unix/Mac: export instead of set)")

    print("\nOption 2: Update config.json")
    print("  Add your credentials to the config.json file")

    print("\nAvailable LinkedIn Commands:")
    print("  fte linkedin          - Start LinkedIn watcher")
    print("  fte help             - Show all available commands")

    print("\nLinkedIn Auto Posting Features:")
    print("  - Monitor vault for business content")
    print("  - Auto-convert notes to LinkedIn posts")
    print("  - Optimal posting time selection")
    print("  - Engagement tracking")
    print("  - Content scheduling")

    print("\nCreating sample business content...")

    # Create sample content in the vault
    from src.fte.vault_manager import VaultManager
    vault_manager = VaultManager()

    sample_posts = [
        {
            "title": "Weekly Business Update",
            "content": """# Weekly Business Update

Exciting developments this week! Our team has been making significant progress on several key initiatives.

## This Week's Wins:
- Completed Q1 planning phase
- Launched new customer portal
- Expanded team with 2 new developers
- Reached 10,000 customers milestone

## Coming Up:
- Product roadmap announcement
- Partnership opportunities
- Community events

#Business #Growth #Innovation #Team"""
        },
        {
            "title": "Product Launch Announcement",
            "content": """# New Product Launch!

We're thrilled to announce the launch of our latest innovation. This represents months of hard work and dedication from our team.

## Key Features:
- Enhanced user experience
- Improved performance
- Advanced security measures
- Seamless integration

## Impact:
This launch will help our customers achieve their goals more efficiently and effectively.

#ProductLaunch #Innovation #Technology #Business"""
        },
        {
            "title": "Industry Insights",
            "content": """# Industry Trends & Insights

Based on our research and market observations, here are key trends shaping our industry:

## Current Trends:
- Digital transformation acceleration
- Sustainability focus increasing
- Remote work becoming standard
- AI adoption growing rapidly

## Our Response:
We're adapting our strategies to leverage these trends for our customers' benefit.

#Insights #Trends #BusinessStrategy #Innovation"""
        }
    ]

    for i, post in enumerate(sample_posts, 1):
        filename = f"linkedin_demo_content_{i:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = vault_manager.vault_path / "Inbox" / filename
        content = f"""---
type: business_update
tags: [business, update, {post['title'].lower().replace(' ', '_')}]
created: {datetime.now().isoformat()}
---

{post['content']}
"""
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created: {filename}")

    print(f"\nSample content created in vault Inbox folder")
    print(f"   These can be automatically converted to LinkedIn posts")

    print("\nTo Run LinkedIn Auto Posting:")
    print("  1. Set your LinkedIn credentials (environment variables or config)")
    print("  2. Run: fte linkedin")
    print("  3. The system will monitor your vault for business content")
    print("  4. Auto-convert suitable notes to LinkedIn posts")
    print("  5. Schedule posts at optimal times")

    print(f"\nLinkedIn Auto Posting Setup Complete!")
    print(f"   Next step: Configure your LinkedIn credentials and start the watcher")


def show_linkedin_skills():
    """Show available LinkedIn posting skills."""
    print("\nLinkedIn Posting Skills Available:")

    skills_examples = [
        ("Create LinkedIn Post", "create_linkedin_post", "content='Check out our new feature!'"),
        ("Schedule LinkedIn Post", "schedule_linkedin_post", "content='New blog post!' scheduled_time='2024-01-15T10:00:00'"),
        ("Create Post from Vault", "create_post_from_vault_content", "content_type='business_update'"),
        ("Get Suggested Times", "get_suggested_posting_times", "count=3"),
        ("Get Profile Info", "get_linkedin_profile_info", ""),
        ("Get Network Info", "get_linkedin_network_info", ""),
    ]

    for name, skill, params in skills_examples:
        print(f"  - {name}: /linkedin-posting {skill} {params if params else ''}")


if __name__ == "__main__":
    setup_linkedin_demo()
    show_linkedin_skills()
    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")