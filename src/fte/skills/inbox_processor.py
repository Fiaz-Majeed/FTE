"""Inbox Processor Skill - Analyze and categorize inbox items."""

from pathlib import Path
import sys

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from fte.vault_manager import VaultManager
from fte.skills.email_response_generator import process_inbox_for_responses


def process_inbox(vault_path: str | Path | None = None) -> dict:
    """Process all items in the Inbox folder.

    Analyzes each item and provides categorization suggestions.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Dictionary with processing results
    """
    manager = VaultManager(vault_path)
    items = manager.get_inbox_items()

    results = {
        "total_items": len(items),
        "items": [],
        "suggestions": [],
    }

    if not items:
        results["message"] = "Inbox is empty"
        return results

    for item in items:
        item_info = {
            "name": item["name"],
            "path": str(item["path"]),
            "preview": item["preview"],
            "modified": item["modified"].isoformat(),
        }

        # Basic categorization based on content/name patterns
        suggestion = categorize_item(item["name"], item["preview"])
        item_info["suggested_action"] = suggestion

        results["items"].append(item_info)
        results["suggestions"].append(
            f"{item['name']}: {suggestion}"
        )

    results["message"] = f"Processed {len(items)} items"
    return results


def process_inbox_with_ai_responses(vault_path: str | Path | None = None) -> dict:
    """Process all items in the Inbox folder and generate AI responses for them.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Dictionary with processing results including AI response generation
    """
    # First, process the inbox normally
    normal_results = process_inbox(vault_path)

    # Then generate AI responses for all emails
    ai_results = process_inbox_for_responses(vault_path)

    # Combine results
    combined_results = {
        "normal_processing": normal_results,
        "ai_response_generation": ai_results,
        "summary": {
            "total_inbox_items": normal_results["total_items"],
            "ai_responses_generated": ai_results["successful"],
            "ai_responses_failed": ai_results["failed"]
        }
    }

    return combined_results


def categorize_item(name: str, content: str) -> str:
    """Suggest categorization for an item based on content analysis.

    Args:
        name: File name
        content: File content preview

    Returns:
        Suggested action
    """
    name_lower = name.lower()
    content_lower = content.lower()

    # Check for urgency indicators
    urgent_keywords = ["urgent", "asap", "important", "deadline", "critical"]
    if any(kw in name_lower or kw in content_lower for kw in urgent_keywords):
        return "URGENT: Move to Needs_Action immediately"

    # Check for reference material
    reference_keywords = ["reference", "documentation", "guide", "manual", "howto"]
    if any(kw in name_lower or kw in content_lower for kw in reference_keywords):
        return "Reference material: Consider archiving to Done"

    # Check for task indicators
    task_keywords = ["task", "todo", "action", "follow-up", "review"]
    if any(kw in name_lower or kw in content_lower for kw in task_keywords):
        return "Task item: Move to Needs_Action"

    # Check for meeting notes
    meeting_keywords = ["meeting", "notes", "minutes", "agenda"]
    if any(kw in name_lower or kw in content_lower for kw in meeting_keywords):
        return "Meeting notes: Review and extract action items"

    # Default suggestion
    return "Review and categorize manually"


def get_inbox_summary(vault_path: str | Path | None = None) -> str:
    """Get a text summary of inbox contents.

    Args:
        vault_path: Optional path to vault directory

    Returns:
        Formatted summary string
    """
    results = process_inbox(vault_path)

    lines = [
        "Inbox Summary",
        "=" * 40,
        f"Total items: {results['total_items']}",
        "",
    ]

    if results["items"]:
        lines.append("Items:")
        for item in results["items"]:
            lines.append(f"  - {item['name']}")
            lines.append(f"    Suggestion: {item['suggested_action']}")
            lines.append("")

    return "\n".join(lines)
