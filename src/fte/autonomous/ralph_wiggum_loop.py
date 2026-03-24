"""
Ralph Wiggum Loop - Autonomous Multi-Step Task Completion System
Implements goal decomposition, planning, execution, and self-correction
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

from ..audit.audit_logger import get_audit_logger, AuditEventType, AuditSeverity
from ..vault_manager import VaultManager


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AutonomousTask:
    """Represents a single autonomous task."""

    def __init__(
        self,
        task_id: str,
        goal: str,
        steps: List[Dict[str, Any]],
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize autonomous task.

        Args:
            task_id: Unique task identifier
            goal: High-level goal description
            steps: List of execution steps
            dependencies: List of task IDs this depends on
            metadata: Additional task metadata
        """
        self.task_id = task_id
        self.goal = goal
        self.steps = steps
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.status = TaskStatus.PENDING
        self.current_step = 0
        self.results: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "steps": self.steps,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "status": self.status.value,
            "current_step": self.current_step,
            "results": self.results,
            "errors": self.errors,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutonomousTask':
        """Create task from dictionary."""
        task = cls(
            task_id=data["task_id"],
            goal=data["goal"],
            steps=data["steps"],
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {})
        )
        task.status = TaskStatus(data["status"])
        task.current_step = data["current_step"]
        task.results = data.get("results", [])
        task.errors = data.get("errors", [])
        task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        return task


class RalphWiggumLoop:
    """
    Autonomous multi-step task completion system.

    Named after Ralph Wiggum's famous quote: "I'm helping!"
    This system autonomously breaks down goals, plans execution, and learns from outcomes.
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize Ralph Wiggum Loop.

        Args:
            vault_path: Path to vault for task storage
        """
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"
        self.vault_manager = VaultManager(vault_path)
        self.audit_logger = get_audit_logger()

        self.tasks: Dict[str, AutonomousTask] = {}
        self.action_registry: Dict[str, Callable] = {}

        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from vault."""
        tasks_file = self.vault_path / "autonomous_tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r') as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = AutonomousTask.from_dict(task_data)
                        self.tasks[task.task_id] = task
            except Exception as e:
                self.audit_logger.log_error(
                    f"Failed to load autonomous tasks: {e}",
                    actor="ralph_wiggum_loop",
                    resource="autonomous_tasks.json"
                )

    def _save_tasks(self):
        """Save tasks to vault."""
        tasks_file = self.vault_path / "autonomous_tasks.json"
        try:
            data = {
                "tasks": [task.to_dict() for task in self.tasks.values()],
                "updated_at": datetime.now().isoformat()
            }
            with open(tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to save autonomous tasks: {e}",
                actor="ralph_wiggum_loop",
                resource="autonomous_tasks.json"
            )

    def register_action(self, action_name: str, action_func: Callable):
        """Register an action that can be executed.

        Args:
            action_name: Name of the action
            action_func: Function to execute
        """
        self.action_registry[action_name] = action_func
        self.audit_logger.log_action(
            action="register_action",
            actor="ralph_wiggum_loop",
            resource=action_name,
            status="success"
        )

    def decompose_goal(self, goal: str) -> List[Dict[str, Any]]:
        """Decompose a high-level goal into executable steps.

        Args:
            goal: High-level goal description

        Returns:
            List of execution steps
        """
        # Simple rule-based decomposition (can be enhanced with AI)
        steps = []

        # Analyze goal keywords
        goal_lower = goal.lower()

        if "post" in goal_lower and "social" in goal_lower:
            steps.extend([
                {"action": "generate_content", "params": {"topic": goal}},
                {"action": "review_content", "params": {}},
                {"action": "post_to_social", "params": {"platforms": ["linkedin", "twitter"]}}
            ])

        elif "email" in goal_lower:
            steps.extend([
                {"action": "draft_email", "params": {"subject": goal}},
                {"action": "review_email", "params": {}},
                {"action": "send_email", "params": {}}
            ])

        elif "report" in goal_lower or "analysis" in goal_lower:
            steps.extend([
                {"action": "gather_data", "params": {"topic": goal}},
                {"action": "analyze_data", "params": {}},
                {"action": "generate_report", "params": {}},
                {"action": "save_report", "params": {"folder": "Done"}}
            ])

        else:
            # Generic steps
            steps.extend([
                {"action": "plan_task", "params": {"goal": goal}},
                {"action": "execute_task", "params": {}},
                {"action": "verify_completion", "params": {}}
            ])

        self.audit_logger.log(
            AuditEventType.AUTONOMOUS_TASK,
            "decompose_goal",
            actor="ralph_wiggum_loop",
            resource=goal,
            metadata={"steps_count": len(steps)}
        )

        return steps

    def create_task(
        self,
        goal: str,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new autonomous task.

        Args:
            goal: High-level goal
            dependencies: Task dependencies
            metadata: Additional metadata

        Returns:
            Task ID
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        steps = self.decompose_goal(goal)

        task = AutonomousTask(
            task_id=task_id,
            goal=goal,
            steps=steps,
            dependencies=dependencies,
            metadata=metadata
        )

        self.tasks[task_id] = task
        self._save_tasks()

        self.audit_logger.log(
            AuditEventType.AUTONOMOUS_TASK,
            "create_task",
            actor="ralph_wiggum_loop",
            resource=task_id,
            metadata={"goal": goal, "steps_count": len(steps)}
        )

        return task_id

    def execute_step(self, task: AutonomousTask, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task step.

        Args:
            task: The task being executed
            step: Step to execute

        Returns:
            Step result
        """
        action_name = step.get("action")
        params = step.get("params", {})

        if action_name not in self.action_registry:
            return {
                "status": "error",
                "error": f"Action '{action_name}' not registered",
                "action": action_name
            }

        try:
            action_func = self.action_registry[action_name]
            result = action_func(**params)

            self.audit_logger.log(
                AuditEventType.AUTONOMOUS_TASK,
                f"execute_step_{action_name}",
                actor="ralph_wiggum_loop",
                resource=task.task_id,
                status="success",
                metadata={"step": step}
            )

            return {
                "status": "success",
                "action": action_name,
                "result": result
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Step execution failed: {e}",
                actor="ralph_wiggum_loop",
                resource=task.task_id,
                action=action_name
            )

            return {
                "status": "error",
                "action": action_name,
                "error": str(e)
            }

    def execute_task(self, task_id: str, max_retries: int = 3) -> Dict[str, Any]:
        """Execute an autonomous task.

        Args:
            task_id: Task ID to execute
            max_retries: Maximum retries per step

        Returns:
            Execution result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        # Check dependencies
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    task.status = TaskStatus.BLOCKED
                    self._save_tasks()
                    return {
                        "status": "blocked",
                        "message": f"Waiting for dependency {dep_id}",
                        "task_id": task_id
                    }

        task.status = TaskStatus.IN_PROGRESS
        self._save_tasks()

        # Execute steps
        while task.current_step < len(task.steps):
            step = task.steps[task.current_step]

            retry_count = 0
            step_result = None

            while retry_count < max_retries:
                step_result = self.execute_step(task, step)

                if step_result["status"] == "success":
                    task.results.append(step_result)
                    task.current_step += 1
                    self._save_tasks()
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        self.audit_logger.log(
                            AuditEventType.AUTONOMOUS_TASK,
                            "retry_step",
                            actor="ralph_wiggum_loop",
                            resource=task_id,
                            severity=AuditSeverity.WARNING,
                            metadata={"retry": retry_count, "step": step}
                        )
                    else:
                        task.errors.append(f"Step {task.current_step} failed: {step_result.get('error')}")
                        task.status = TaskStatus.FAILED
                        self._save_tasks()
                        return {
                            "status": "failed",
                            "task_id": task_id,
                            "error": step_result.get("error"),
                            "completed_steps": task.current_step,
                            "total_steps": len(task.steps)
                        }

        # All steps completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        self._save_tasks()

        self.audit_logger.log(
            AuditEventType.AUTONOMOUS_TASK,
            "task_completed",
            actor="ralph_wiggum_loop",
            resource=task_id,
            severity=AuditSeverity.INFO,
            metadata={
                "goal": task.goal,
                "steps_completed": len(task.steps),
                "duration_seconds": (task.completed_at - task.created_at).total_seconds()
            }
        )

        return {
            "status": "completed",
            "task_id": task_id,
            "goal": task.goal,
            "results": task.results,
            "duration_seconds": (task.completed_at - task.created_at).total_seconds()
        }

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status.

        Args:
            task_id: Task ID

        Returns:
            Task status information
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "goal": task.goal,
            "status": task.status.value,
            "progress": f"{task.current_step}/{len(task.steps)}",
            "errors": task.errors,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }

    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """List all tasks.

        Args:
            status_filter: Optional status filter

        Returns:
            List of task summaries
        """
        tasks = self.tasks.values()

        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]

        return [
            {
                "task_id": t.task_id,
                "goal": t.goal,
                "status": t.status.value,
                "progress": f"{t.current_step}/{len(t.steps)}",
                "created_at": t.created_at.isoformat()
            }
            for t in sorted(tasks, key=lambda x: x.created_at, reverse=True)
        ]

    def learn_from_outcome(self, task_id: str):
        """Learn from task outcome to improve future planning.

        Args:
            task_id: Task ID to learn from
        """
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]

        # Simple learning: track success/failure patterns
        learning_file = self.vault_path / "autonomous_learning.json"

        try:
            if learning_file.exists():
                with open(learning_file, 'r') as f:
                    learning_data = json.load(f)
            else:
                learning_data = {"patterns": {}, "success_rate": {}}

            # Update patterns
            goal_type = task.goal.split()[0].lower()  # First word as type
            if goal_type not in learning_data["patterns"]:
                learning_data["patterns"][goal_type] = {
                    "successful_steps": [],
                    "failed_steps": [],
                    "total_attempts": 0,
                    "successful_attempts": 0
                }

            pattern = learning_data["patterns"][goal_type]
            pattern["total_attempts"] += 1

            if task.status == TaskStatus.COMPLETED:
                pattern["successful_attempts"] += 1
                pattern["successful_steps"].extend([s["action"] for s in task.steps])
            else:
                pattern["failed_steps"].extend([s["action"] for s in task.steps])

            # Calculate success rate
            pattern["success_rate"] = pattern["successful_attempts"] / pattern["total_attempts"]

            with open(learning_file, 'w') as f:
                json.dump(learning_data, f, indent=2)

            self.audit_logger.log(
                AuditEventType.AUTONOMOUS_TASK,
                "learn_from_outcome",
                actor="ralph_wiggum_loop",
                resource=task_id,
                metadata={"goal_type": goal_type, "success": task.status == TaskStatus.COMPLETED}
            )

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to learn from outcome: {e}",
                actor="ralph_wiggum_loop",
                resource=task_id
            )
