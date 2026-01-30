"""Plan Reasoning Skill - Process Plan.md files with Claude reasoning loop."""

from pathlib import Path
from typing import Dict, Any
from ..reasoning.reasoning_engine import ReasoningEngine, process_plan_file


def analyze_plan(
    plan_file_path: str,
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Analyze a Plan.md file using Claude reasoning.

    Args:
        plan_file_path: Path to the Plan.md file to analyze
        vault_path: Path to vault directory

    Returns:
        Dictionary with analysis results
    """
    try:
        result = process_plan_file(plan_file_path, vault_path)

        return {
            "success": True,
            "analysis": result,
            "message": f"Successfully analyzed plan: {plan_file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to analyze plan: {plan_file_path}"
        }


def generate_action_plan(
    plan_file_path: str,
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Generate an action plan from a Plan.md file.

    Args:
        plan_file_path: Path to the Plan.md file
        vault_path: Path to vault directory

    Returns:
        Dictionary with action plan
    """
    try:
        engine = ReasoningEngine(vault_path=vault_path)
        result = engine.process_plan_file(plan_file_path)

        action_plan = result.get("action_plan", {})

        return {
            "success": True,
            "action_plan": action_plan,
            "message": f"Generated action plan from: {plan_file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate action plan: {plan_file_path}"
        }


def create_plan_summary(
    plan_file_path: str,
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Create a summary of a Plan.md file.

    Args:
        plan_file_path: Path to the Plan.md file
        vault_path: Path to vault directory

    Returns:
        Dictionary with plan summary
    """
    try:
        engine = ReasoningEngine(vault_path=vault_path)
        result = engine.process_plan_file(plan_file_path)

        analysis = result.get("analysis", {})
        goals_analysis = analysis.get("goals_analysis", {})
        tasks_analysis = analysis.get("tasks_analysis", {})

        summary = {
            "original_file": plan_file_path,
            "goals_total": goals_analysis.get("total", 0),
            "goals_completed": goals_analysis.get("completed", 0),
            "goals_completion_rate": goals_analysis.get("completion_rate", 0),
            "tasks_total": tasks_analysis.get("total", 0),
            "tasks_completed": tasks_analysis.get("completed", 0),
            "tasks_completion_rate": tasks_analysis.get("completion_rate", 0),
            "next_steps": result.get("action_plan", {}).get("next_steps", []),
            "recommendations": analysis.get("recommendations", []),
        }

        return {
            "success": True,
            "summary": summary,
            "message": f"Created summary for plan: {plan_file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create plan summary: {plan_file_path}"
        }


def process_all_plans(
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Process all Plan.md files in the vault.

    Args:
        vault_path: Path to vault directory

    Returns:
        Dictionary with results from processing all plans
    """
    try:
        engine = ReasoningEngine(vault_path=vault_path)
        results = engine.process_all_plans_in_vault()

        return {
            "success": True,
            "results": results,
            "message": f"Processed {results['total_plans_found']} plan files"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process all plans in vault"
        }


def update_plan_with_reasoning(
    plan_file_path: str,
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Update a Plan.md file with Claude reasoning insights.

    Args:
        plan_file_path: Path to the Plan.md file to update
        vault_path: Path to vault directory

    Returns:
        Dictionary with update results
    """
    try:
        engine = ReasoningEngine(vault_path=vault_path)
        result = engine.process_plan_file(plan_file_path)

        # Create updated Plan.md content
        updated_content = engine.create_plan_markdown(result)

        # Write back to file
        with open(plan_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        return {
            "success": True,
            "updated_file": plan_file_path,
            "changes_made": len(result.get("action_plan", {}).get("next_steps", [])),
            "message": f"Updated plan with reasoning: {plan_file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update plan: {plan_file_path}"
        }