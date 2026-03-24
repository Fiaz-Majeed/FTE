#!/usr/bin/env python3
"""
FTE Gold Tier - Verification Script
Verifies all Gold Tier components are properly installed and configured
"""
import sys
from pathlib import Path

def verify_gold_tier():
    """Verify Gold Tier implementation."""
    print("=" * 70)
    print("FTE GOLD TIER - VERIFICATION")
    print("=" * 70)
    print()

    errors = []
    warnings = []

    # Check modules
    print("Checking Gold Tier Modules...")
    modules = [
        ("Audit System", "src/fte/audit/__init__.py"),
        ("Resilience System", "src/fte/resilience/__init__.py"),
        ("Autonomous System", "src/fte/autonomous/__init__.py"),
        ("Setup Utilities", "src/fte/setup/__init__.py"),
    ]

    for name, path in modules:
        if Path(path).exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            errors.append(f"Missing: {path}")

    print()

    # Check integrations
    print("Checking Social Media Integrations...")
    integrations = [
        ("Twitter API", "src/fte/social/twitter_api.py"),
        ("Facebook/Instagram API", "src/fte/social/facebook_instagram_api.py"),
        ("Social Media Watchers", "src/fte/watchers/social_media_watchers.py"),
    ]

    for name, path in integrations:
        if Path(path).exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            errors.append(f"Missing: {path}")

    print()

    # Check MCP servers
    print("Checking MCP Servers...")
    servers = [
        ("Odoo MCP Server", "src/fte/mcp/odoo_mcp_server.py"),
        ("MCP Router", "src/fte/mcp/mcp_router.py"),
    ]

    for name, path in servers:
        if Path(path).exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            errors.append(f"Missing: {path}")

    print()

    # Check skills
    print("Checking Gold Tier Skills...")
    if Path("src/fte/skills/gold_tier_skills.py").exists():
        print(f"  ✅ Gold Tier Skills")
    else:
        print(f"  ❌ Gold Tier Skills")
        errors.append("Missing: src/fte/skills/gold_tier_skills.py")

    print()

    # Check documentation
    print("Checking Documentation...")
    docs = [
        ("Architecture", "GOLD_TIER_ARCHITECTURE.md"),
        ("Completion Report", "GOLD_TIER_COMPLETION_REPORT.md"),
        ("Lessons Learned", "LESSONS_LEARNED.md"),
        ("Quick Start", "QUICK_START.md"),
        ("Summary", "GOLD_TIER_SUMMARY.md"),
    ]

    for name, path in docs:
        if Path(path).exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            warnings.append(f"Missing documentation: {path}")

    print()

    # Check dependencies
    print("Checking Dependencies...")
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            if "tweepy" in content:
                print(f"  ✅ Twitter dependency (tweepy)")
            else:
                warnings.append("Missing tweepy in dependencies")

            if "httpx" in content:
                print(f"  ✅ HTTP client dependency (httpx)")
            else:
                warnings.append("Missing httpx in dependencies")

            if "1.0.0" in content:
                print(f"  ✅ Version updated to 1.0.0")
            else:
                warnings.append("Version not updated to 1.0.0")
    except Exception as e:
        errors.append(f"Error reading pyproject.toml: {e}")

    print()
    print("=" * 70)

    # Summary
    if errors:
        print("❌ VERIFICATION FAILED")
        print()
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    elif warnings:
        print("⚠️  VERIFICATION PASSED WITH WARNINGS")
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        return True
    else:
        print("✅ VERIFICATION PASSED")
        print()
        print("All Gold Tier components are properly installed!")
        print()
        print("Next Steps:")
        print("  1. Configure API credentials in .env file")
        print("  2. Set up Odoo: python -m fte.setup.odoo_setup odoo-fte")
        print("  3. Start MCP servers")
        print("  4. Start watchers")
        print("  5. Run weekly audit")
        print()
        print("See QUICK_START.md for detailed instructions.")
        return True

if __name__ == "__main__":
    success = verify_gold_tier()
    sys.exit(0 if success else 1)
