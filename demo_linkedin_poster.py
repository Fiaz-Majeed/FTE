"""LinkedIn Auto Poster - Demonstrate automated LinkedIn posting functionality."""

import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the src directory to the path so we can import fte modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.fte.social.post_scheduler import create_business_content_from_vault
from src.fte.skills.linkedin_posting import (
    create_post_from_vault_content,
    create_linkedin_post,
    get_suggested_posting_times
)
from src.fte.skills.scheduler_skills import schedule_cron_task
from src.fte.vault_manager import VaultManager


def demo_linkedin_auto_poster():
    """Demonstrate LinkedIn auto-posting functionality."""

    print("LinkedIn Auto Poster Demo")
    print("=" * 50)

    # Step 1: Look for business content in the vault
    print("\nSearching for business content in vault...")

    try:
        content_result = create_post_from_vault_content(
            content_type="business_update",
            hashtags=["Business", "Growth", "Innovation"]
        )

        if content_result["success"]:
            print(f"Found content suitable for LinkedIn posting")
            print(f"Content preview: {content_result['content'][:100]}...")
            print(f"Source note: {content_result['source_note']}")
        else:
            print("No suitable content found in vault")

            # Create sample content for demo
            print("\nCreating sample business content for demo...")
            vault_manager = VaultManager()

            sample_content = """# Business Growth Update

We're excited to announce significant progress in our Q1 objectives! Our team has been working diligently to improve our products and services.

## Key Achievements:
- Completed market expansion research
- Launched new customer onboarding process
- Improved operational efficiency by 20%

## Looking Forward:
- Planning new product features
- Expanding our partnership network
- Enhancing customer experience

#Business #Growth #Innovation #TeamWork"""

            sample_file = vault_manager.vault_path / "Inbox" / f"sample_business_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            sample_file.write_text(sample_content, encoding="utf-8")
            print(f"Sample content created: {sample_file.name}")

            # Try again with sample content
            content_result = create_post_from_vault_content(
                content_type="business_update",
                hashtags=["Business", "Growth", "Innovation"]
            )
    except Exception as e:
        print(f"Content generation error: {e}")
        print("Creating sample content for demo...")

        # Create sample content directly
        vault_manager = VaultManager()
        sample_content = """# Business Growth Update

We're excited to announce significant progress in our Q1 objectives! Our team has been working diligently to improve our products and services.

## Key Achievements:
- Completed market expansion research
- Launched new customer onboarding process
- Improved operational efficiency by 20%

## Looking Forward:
- Planning new product features
- Expanding our partnership network
- Enhancing customer experience

#Business #Growth #Innovation #TeamWork"""

        sample_file = vault_manager.vault_path / "Inbox" / f"demo_business_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        sample_file.write_text(sample_content, encoding="utf-8")
        print(f"Sample content created: {sample_file.name}")

        # For demo purposes, we'll use the content directly
        content_result = {
            "success": True,
            "content": "Check out our latest business update! We're making great progress on our Q1 objectives and improving our products. #Business #Growth #Innovation",
            "source_note": "demo_business_update",
            "hashtags": ["Business", "Growth", "Innovation"],
            "message": "Generated demo content"
        }

    # Step 2: Show suggested posting times
    print("\nGetting suggested optimal posting times...")
    try:
        times_result = get_suggested_posting_times(count=3)
        if times_result["success"]:
            print("Suggested posting times:")
            for i, time_str in enumerate(times_result["suggested_times"], 1):
                print(f"  {i}. {time_str}")
        else:
            print("Could not get suggested times")
    except Exception as e:
        print(f"Time suggestion error: {e}")

    # Step 3: Demonstrate scheduling a post (without actual posting to LinkedIn)
    print("\nDemonstrating post scheduling...")
    try:
        # For demo, we'll show what would happen if we had credentials
        print("In a real implementation with LinkedIn credentials, we would:")
        print(f"   - Post this content: '{content_result.get('content', 'Sample post')[:60]}...'")
        print(f"   - Use hashtags: {content_result.get('hashtags', ['Business', 'Growth'])}")
        print("   - Post according to optimal timing")
        print("   - Track engagement metrics")

        # Show how scheduling would work
        print("\nScheduling functionality available:")
        print("   - Schedule recurring business updates")
        print("   - Plan content calendar")
        print("   - Auto-post based on vault content")

    except Exception as e:
        print(f"Scheduling demo error: {e}")

    # Step 4: Show how the LinkedIn watcher would work
    print("\nLinkedIn Watcher functionality:")
    print("   - Monitor LinkedIn notifications")
    print("   - Track post engagement")
    print("   - Respond to comments/messages")
    print("   - Analyze content performance")

    print("\nPro Tip: To use real LinkedIn posting:")
    print("   1. Set LINKEDIN_USERNAME and LINKEDIN_PASSWORD environment variables")
    print("   2. Or update config.json with credentials")
    print("   3. Run: fte linkedin (to start watcher)")
    print("   4. Add business content to your vault Inbox folder")

    print(f"\nLinkedIn Auto Poster demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def start_linkedin_watcher():
    """Start the LinkedIn watcher to monitor for content."""
    print("Starting LinkedIn Watcher...")
    print("Note: This would normally connect to LinkedIn API to monitor for new content")
    print("For demo purposes, we'll simulate the monitoring process...\n")

    try:
        # This would normally start the actual LinkedIn watcher
        # from src.fte.watchers.linkedin_watcher import LinkedInWatcher
        # watcher = LinkedInWatcher()
        # watcher.run()

        print("Monitoring vault for business content...")
        print("Checking for new notes to convert to LinkedIn posts...")
        print("Tracking engagement on published posts...")

        # Simulate some monitoring activity
        for i in range(3):
            print(f"   Monitoring cycle {i+1} completed")
            time.sleep(1)

        print("\nLinkedIn Watcher simulation completed")
        print("   In a real implementation, this would run continuously")
        print("   and automatically post business updates from your vault")

    except ImportError as e:
        print(f"LinkedIn watcher not available: {e}")
        print("Install required dependency: pip install linkedin-api")


if __name__ == "__main__":
    demo_linkedin_auto_poster()
    print("\n" + "="*50)
    start_linkedin_watcher()