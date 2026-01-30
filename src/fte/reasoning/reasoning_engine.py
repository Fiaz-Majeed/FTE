"""Claude Reasoning Engine - Process Plan.md files with iterative reasoning."""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..vault_manager import VaultManager
from .plan_parser import PlanParser


class ReasoningEngine:
    """Iterative reasoning engine that processes Plan.md files."""

    def __init__(
        self,
        vault_path: str | Path | None = None,
        ai_provider: str = "qwen",
        ai_model: str = "qwen3-coder-plus",
    ):
        """Initialize the reasoning engine.

        Args:
            vault_path: Path to vault directory
            ai_provider: AI provider to use
            ai_model: AI model to use
        """
        self.base_path = Path(__file__).parent.parent.parent
        if vault_path is None:
            self.vault_path = self.base_path / "vault"
        else:
            self.vault_path = Path(vault_path)

        self.vault_manager = VaultManager(self.vault_path)
        self.plan_parser = PlanParser()
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        self.reasoning_history: List[Dict[str, Any]] = []

    def process_plan_file(self, plan_file_path: str | Path) -> Dict[str, Any]:
        """Process a Plan.md file with iterative reasoning.

        Args:
            plan_file_path: Path to the Plan.md file to process

        Returns:
            Dictionary with reasoning results and action plan
        """
        plan_path = Path(plan_file_path)

        # Parse the plan file
        plan_data = self.plan_parser.parse_plan_file(plan_path)

        # Perform initial analysis
        analysis = self._analyze_plan(plan_data)

        # Generate action plan
        action_plan = self._generate_action_plan(plan_data, analysis)

        # Create reasoning trace
        reasoning_trace = {
            "input_file": str(plan_path),
            "parsed_plan": plan_data,
            "analysis": analysis,
            "action_plan": action_plan,
            "processed_at": datetime.now().isoformat(),
            "engine_version": "1.0.0",
        }

        # Store in reasoning history
        self.reasoning_history.append(reasoning_trace)

        return reasoning_trace

    def _analyze_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the parsed plan data.

        Args:
            plan_data: Parsed plan data

        Returns:
            Analysis results
        """
        goals = plan_data.get("goals", [])
        tasks = plan_data.get("tasks", [])
        dependencies = plan_data.get("dependencies", {})
        timeline = plan_data.get("timeline", {})

        # Analyze goal completion status
        completed_goals = sum(1 for goal in goals if goal.get("completed", False))
        total_goals = len(goals)

        # Analyze task completion status
        completed_tasks = sum(1 for task in tasks if task.get("completed", False))
        total_tasks = len(tasks)

        # Analyze priorities
        priority_breakdown = {"high": 0, "medium": 0, "low": 0}
        for task in tasks:
            priority = task.get("priority", "medium")
            priority_breakdown[priority] += 1

        # Analyze dependencies
        dependency_analysis = {
            "total_dependencies": len(dependencies),
            "tasks_with_dependencies": len([t for t in tasks if t.get("dependencies")]),
            "potential_bottlenecks": self._identify_bottlenecks(dependencies, tasks),
        }

        # Analyze timeline
        timeline_analysis = {
            "has_start_date": "start_date" in timeline,
            "has_end_date": "end_date" in timeline,
            "has_milestones": len(timeline.get("milestones", [])) > 0,
        }

        return {
            "goals_analysis": {
                "total": total_goals,
                "completed": completed_goals,
                "completion_rate": completed_goals / total_goals if total_goals > 0 else 0,
            },
            "tasks_analysis": {
                "total": total_tasks,
                "completed": completed_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            },
            "priorities_analysis": priority_breakdown,
            "dependencies_analysis": dependency_analysis,
            "timeline_analysis": timeline_analysis,
            "recommendations": self._generate_recommendations(
                completed_goals, total_goals, completed_tasks, total_tasks, dependencies
            ),
        }

    def _generate_action_plan(self, plan_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an action plan based on the analysis.

        Args:
            plan_data: Parsed plan data
            analysis: Analysis results

        Returns:
            Action plan with prioritized tasks
        """
        tasks = plan_data.get("tasks", [])
        dependencies = plan_data.get("dependencies", {})

        # Sort tasks by priority and dependencies
        prioritized_tasks = self._prioritize_tasks(tasks, dependencies)

        # Generate next steps
        next_steps = self._generate_next_steps(tasks, dependencies, analysis)

        # Create timeline recommendations
        timeline_recommendations = self._generate_timeline_recommendations(
            tasks, dependencies, analysis
        )

        return {
            "prioritized_tasks": prioritized_tasks,
            "next_steps": next_steps,
            "timeline_recommendations": timeline_recommendations,
            "status_updates": self._generate_status_updates(tasks),
        }

    def _prioritize_tasks(
        self,
        tasks: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Prioritize tasks based on priority level and dependencies.

        Args:
            tasks: List of tasks
            dependencies: Task dependencies

        Returns:
            List of prioritized tasks
        """
        # Create a copy of tasks with additional metadata
        prioritized = []
        for i, task in enumerate(tasks):
            task_copy = task.copy()
            task_copy["index"] = i
            task_copy["ready_to_start"] = self._is_task_ready(i, dependencies, tasks)
            prioritized.append(task_copy)

        # Sort by priority (high first) and readiness
        priority_order = {"high": 3, "medium": 2, "low": 1}
        prioritized.sort(
            key=lambda t: (
                priority_order.get(t.get("priority", "medium"), 2),
                t["ready_to_start"],
                t["index"]
            ),
            reverse=True
        )

        return prioritized

    def _generate_next_steps(
        self,
        tasks: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate next steps based on current state.

        Args:
            tasks: List of tasks
            dependencies: Task dependencies
            analysis: Analysis results

        Returns:
            List of next steps
        """
        next_steps = []

        # Identify incomplete tasks that are ready to start
        incomplete_ready_tasks = [
            task for i, task in enumerate(tasks)
            if not task.get("completed", False) and self._is_task_ready(i, dependencies, tasks)
        ]

        if incomplete_ready_tasks:
            # Add highest priority ready task as immediate next step
            priority_order = {"high": 3, "medium": 2, "low": 1}
            highest_priority_task = max(
                incomplete_ready_tasks,
                key=lambda t: priority_order.get(t.get("priority", "medium"), 2)
            )

            next_steps.append({
                "action": "Start immediate task",
                "task": highest_priority_task["text"],
                "priority": highest_priority_task.get("priority", "medium"),
            })

        # Identify tasks that could be started soon (dependencies nearly met)
        for i, task in enumerate(tasks):
            if not task.get("completed", False) and not self._is_task_ready(i, dependencies, tasks):
                # Check if dependencies are mostly met
                deps = dependencies.get(str(i), [])
                completed_deps = sum(
                    1 for dep_idx_str in deps
                    if dep_idx_str.isdigit() and int(dep_idx_str) < len(tasks) and tasks[int(dep_idx_str)].get("completed", False)
                )

                if deps and completed_deps == len(deps) - 1:
                    next_steps.append({
                        "action": "Prepare for upcoming task",
                        "task": task["text"],
                        "dependencies_met": f"{completed_deps}/{len(deps)}",
                    })

        # Add general recommendations based on analysis
        if analysis["tasks_analysis"]["completion_rate"] < 0.5:
            next_steps.append({
                "action": "Focus on completing high-priority tasks",
                "task": "Review and prioritize remaining tasks",
            })

        return next_steps

    def _generate_timeline_recommendations(
        self,
        tasks: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate timeline recommendations.

        Args:
            tasks: List of tasks
            dependencies: Task dependencies
            analysis: Analysis results

        Returns:
            List of timeline recommendations
        """
        recommendations = []

        # Estimate completion time based on current pace
        incomplete_tasks = [t for t in tasks if not t.get("completed", False)]

        if incomplete_tasks:
            estimated_completion = self._estimate_completion_time(incomplete_tasks, analysis)
            recommendations.append({
                "type": "completion_estimate",
                "message": f"Estimated completion time: {estimated_completion}",
            })

        # Identify critical path
        critical_path = self._identify_critical_path(tasks, dependencies)
        if critical_path:
            recommendations.append({
                "type": "critical_path",
                "message": f"Critical path includes: {', '.join([tasks[i]['text'][:30] + '...' if len(tasks[i]['text']) > 30 else tasks[i]['text'] for i in critical_path[:3]])}",
            })

        return recommendations

    def _generate_status_updates(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate status updates for tasks.

        Args:
            tasks: List of tasks

        Returns:
            List of status updates
        """
        updates = []

        completed_tasks = [t for t in tasks if t.get("completed", False)]
        pending_tasks = [t for t in tasks if not t.get("completed", False)]

        if completed_tasks:
            updates.append({
                "type": "progress_update",
                "message": f"Completed {len(completed_tasks)} out of {len(tasks)} tasks ({len(completed_tasks)/len(tasks)*100:.1f}%)",
            })

        if pending_tasks:
            priority_order = {"high": 3, "medium": 2, "low": 1}

            # Count by priority
            high_prio_pending = sum(1 for t in pending_tasks if priority_order.get(t.get("priority", "medium"), 2) == 3)
            medium_prio_pending = sum(1 for t in pending_tasks if priority_order.get(t.get("priority", "medium"), 2) == 2)
            low_prio_pending = sum(1 for t in pending_tasks if priority_order.get(t.get("priority", "medium"), 2) == 1)

            updates.append({
                "type": "pending_tasks",
                "message": f"Pending: {high_prio_pending} high, {medium_prio_pending} medium, {low_prio_pending} low priority tasks",
            })

        return updates

    def _is_task_ready(self, task_index: int, dependencies: Dict[str, List[str]], tasks: List[Dict[str, Any]]) -> bool:
        """Check if a task is ready to start (dependencies met).

        Args:
            task_index: Index of the task to check
            dependencies: Task dependencies
            tasks: List of all tasks

        Returns:
            True if task is ready to start
        """
        deps = dependencies.get(str(task_index), [])

        for dep_idx_str in deps:
            dep_idx = int(dep_idx_str) if dep_idx_str.isdigit() else -1
            if dep_idx < len(tasks) and not tasks[dep_idx].get("completed", False):
                return False

        return True

    def _identify_bottlenecks(
        self,
        dependencies: Dict[str, List[str]],
        tasks: List[Dict[str, Any]]
    ) -> List[int]:
        """Identify potential bottleneck tasks.

        Args:
            dependencies: Task dependencies
            tasks: List of tasks

        Returns:
            List of task indices that are potential bottlenecks
        """
        bottlenecks = []

        # A bottleneck is a task that many other tasks depend on
        dependency_counts = {}

        for task_idx, deps in dependencies.items():
            for dep in deps:
                if dep not in dependency_counts:
                    dependency_counts[dep] = 0
                dependency_counts[dep] += 1

        # Identify tasks that are dependencies for many others
        threshold = len(tasks) * 0.1  # 10% of total tasks
        for task_idx_str, count in dependency_counts.items():
            if count >= threshold and task_idx_str.isdigit():
                bottlenecks.append(int(task_idx_str))

        return bottlenecks

    def _estimate_completion_time(self, incomplete_tasks: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Estimate completion time based on task characteristics.

        Args:
            incomplete_tasks: List of incomplete tasks
            analysis: Analysis results

        Returns:
            String with estimated completion time
        """
        # Simple estimation based on number of tasks and priority
        high_prio = sum(1 for t in incomplete_tasks if t.get("priority", "medium") == "high")
        medium_prio = sum(1 for t in incomplete_tasks if t.get("priority", "medium") == "medium")
        low_prio = sum(1 for t in incomplete_tasks if t.get("priority", "medium") == "low")

        # Rough estimate: high priority = 1 day, medium = 2 days, low = 3 days
        est_days = (high_prio * 1) + (medium_prio * 2) + (low_prio * 3)

        if est_days <= 7:
            return f"Within 1 week"
        elif est_days <= 30:
            return f"Within 1 month"
        else:
            return f"More than 1 month ({est_days} days estimated)"

    def _identify_critical_path(
        self,
        tasks: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]]
    ) -> List[int]:
        """Identify the critical path in the task dependencies.

        Args:
            tasks: List of tasks
            dependencies: Task dependencies

        Returns:
            List of task indices in the critical path
        """
        # For simplicity, return the longest sequence of dependent tasks
        # This is a simplified implementation - a full critical path algorithm would be more complex

        # Find tasks with no dependencies that are not completed
        start_candidates = [
            i for i, task in enumerate(tasks)
            if not task.get("completed", False) and str(i) not in dependencies
        ]

        if not start_candidates:
            return []

        # Return first uncompleted task as a starting point
        return [start_candidates[0]]

    def _generate_recommendations(
        self,
        completed_goals: int,
        total_goals: int,
        completed_tasks: int,
        total_tasks: int,
        dependencies: Dict[str, List[str]]
    ) -> List[str]:
        """Generate recommendations based on plan analysis.

        Args:
            completed_goals: Number of completed goals
            total_goals: Total number of goals
            completed_tasks: Number of completed tasks
            total_tasks: Total number of tasks
            dependencies: Task dependencies

        Returns:
            List of recommendations
        """
        recommendations = []

        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

        if completion_rate < 0.3:
            recommendations.append("Consider breaking down large tasks into smaller, manageable chunks")
        elif completion_rate > 0.7:
            recommendations.append("Maintain current momentum and focus on completing remaining tasks")

        if len(dependencies) > total_tasks * 0.5:
            recommendations.append("High dependency count detected - consider parallelizing where possible")

        if total_goals > 10:
            recommendations.append("Consider grouping related goals for better organization")

        return recommendations

    def create_plan_markdown(self, reasoning_result: Dict[str, Any]) -> str:
        """Create a Plan.md file from reasoning results.

        Args:
            reasoning_result: Reasoning results to convert to markdown

        Returns:
            Markdown content for Plan.md file
        """
        plan_data = reasoning_result.get("parsed_plan", {})
        analysis = reasoning_result.get("analysis", {})
        action_plan = reasoning_result.get("action_plan", {})

        content = [
            "---",
            "type: plan",
            f"generated_by: claude-reasoning-engine",
            f"generated_at: {datetime.now().isoformat()}",
            f"engine_version: 1.0.0",
            "---",
            "",
            "# Plan Analysis Report",
            "",
            "## Original Plan Summary",
            f"- Goals: {analysis['goals_analysis']['total']} (completed: {analysis['goals_analysis']['completed']})",
            f"- Tasks: {analysis['tasks_analysis']['total']} (completed: {analysis['tasks_analysis']['completed']})",
            "",
            "## Current Status",
        ]

        # Add status updates
        for update in action_plan.get("status_updates", []):
            content.append(f"- {update['message']}")

        content.extend([
            "",
            "## Next Steps",
        ])

        # Add next steps
        for step in action_plan.get("next_steps", []):
            content.append(f"- [ ] {step['action']}: {step['task']}")

        content.extend([
            "",
            "## Prioritized Tasks",
        ])

        # Add prioritized tasks
        for task in action_plan.get("prioritized_tasks", []):
            status = "x" if task.get("completed", False) else " "
            priority = task.get("priority", "medium").upper()
            content.append(f"- [{status}] **[{priority}]** {task['text']}")

        content.extend([
            "",
            "## Timeline Recommendations",
        ])

        # Add timeline recommendations
        for rec in action_plan.get("timeline_recommendations", []):
            content.append(f"- {rec['message']}")

        content.extend([
            "",
            "## Recommendations",
        ])

        # Add general recommendations
        for rec in analysis.get("recommendations", []):
            content.append(f"- {rec}")

        content.extend([
            "",
            "## Plan Details",
            "",
            "### Goals",
        ])

        # Add original goals
        for goal in plan_data.get("goals", []):
            status = "x" if goal.get("completed", False) else " "
            content.append(f"- [{status}] {goal['text']}")

        content.extend([
            "",
            "### Tasks",
        ])

        # Add original tasks
        for task in plan_data.get("tasks", []):
            status = "x" if task.get("completed", False) else " "
            priority = task.get("priority", "medium").upper()
            content.append(f"- [{status}] **[{priority}]** {task['text']}")

        return "\n".join(content)

    def process_all_plans_in_vault(self) -> Dict[str, Any]:
        """Process all Plan.md files in the vault.

        Returns:
            Dictionary with results from processing all plans
        """
        plan_files = []

        # Look for Plan.md files in all vault folders
        for folder in ["Inbox", "Needs_Action", "Done"]:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                for file_path in folder_path.glob("Plan*.md"):
                    plan_files.append(file_path)
                for file_path in folder_path.glob("*plan*.md"):
                    plan_files.append(file_path)

        results = {
            "total_plans_found": len(plan_files),
            "processed_plans": [],
            "errors": [],
        }

        for plan_file in plan_files:
            try:
                result = self.process_plan_file(plan_file)
                results["processed_plans"].append({
                    "file": str(plan_file),
                    "result": result
                })
            except Exception as e:
                results["errors"].append({
                    "file": str(plan_file),
                    "error": str(e)
                })

        return results


def process_plan_file(
    plan_file_path: str | Path,
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Convenience function to process a Plan.md file.

    Args:
        plan_file_path: Path to the Plan.md file to process
        vault_path: Path to vault directory

    Returns:
        Dictionary with reasoning results and action plan
    """
    engine = ReasoningEngine(vault_path=vault_path)
    return engine.process_plan_file(plan_file_path)