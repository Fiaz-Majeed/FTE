"""Plan Parser - Parse Plan.md files and extract goals, tasks, and dependencies."""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml


class PlanParser:
    """Parse Plan.md files and extract structured information."""

    def __init__(self):
        """Initialize the plan parser."""
        pass

    def parse_plan_file(self, file_path: str | Path) -> Dict[str, Any]:
        """Parse a Plan.md file and extract structured information.

        Args:
            file_path: Path to the Plan.md file

        Returns:
            Dictionary containing parsed plan information
        """
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")

        return self.parse_plan_content(content)

    def parse_plan_content(self, content: str) -> Dict[str, Any]:
        """Parse plan content and extract structured information.

        Args:
            content: Content of the Plan.md file

        Returns:
            Dictionary containing parsed plan information
        """
        # Extract frontmatter if present
        frontmatter = self._extract_frontmatter(content)

        # Extract sections
        sections = self._extract_sections(content)

        # Extract goals
        goals = self._extract_goals(content)

        # Extract tasks
        tasks = self._extract_tasks(content)

        # Extract dependencies
        dependencies = self._extract_dependencies(content, tasks)

        # Extract timeline
        timeline = self._extract_timeline(content)

        # Extract resources
        resources = self._extract_resources(content)

        return {
            "frontmatter": frontmatter,
            "sections": sections,
            "goals": goals,
            "tasks": tasks,
            "dependencies": dependencies,
            "timeline": timeline,
            "resources": resources,
            "parsed_at": datetime.now().isoformat(),
        }

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from content.

        Args:
            content: Content to extract frontmatter from

        Returns:
            Dictionary with frontmatter data
        """
        if content.startswith("---"):
            end_pos = content.find("---", 3)
            if end_pos != -1:
                frontmatter_content = content[3:end_pos].strip()
                try:
                    return yaml.safe_load(frontmatter_content)
                except yaml.YAMLError:
                    return {}

        return {}

    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from content.

        Args:
            content: Content to extract sections from

        Returns:
            List of sections with title and content
        """
        sections = []

        # Match markdown headers (##, ###, etc.)
        header_pattern = r'^(#{2,6})\s+(.+)$'
        lines = content.split('\n')

        current_section = None
        section_content = []

        for line in lines:
            match = re.match(header_pattern, line.strip())

            if match:
                # Save previous section
                if current_section:
                    sections.append({
                        "level": len(current_section["header"]),
                        "title": current_section["title"],
                        "content": "\n".join(section_content).strip()
                    })

                # Start new section
                current_section = {
                    "header": match.group(1),
                    "title": match.group(2)
                }
                section_content = []
            else:
                if current_section:
                    section_content.append(line)

        # Add last section
        if current_section:
            sections.append({
                "level": len(current_section["header"]),
                "title": current_section["title"],
                "content": "\n".join(section_content).strip()
            })

        return sections

    def _extract_goals(self, content: str) -> List[Dict[str, Any]]:
        """Extract goals from content.

        Args:
            content: Content to extract goals from

        Returns:
            List of goals with details
        """
        goals = []

        # Look for goal-related sections
        goal_patterns = [
            r'# Goals?\s*\n((?:.|\n)*?)(?=\n# |\Z)',
            r'## Goals?\s*\n((?:.|\n)*?)(?=\n## |\Z)',
            r'### Goals?\s*\n((?:.|\n)*?)(?=\n### |\Z)',
        ]

        for pattern in goal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Extract individual goals from the section
                goal_items = re.findall(r'- \[(?P<status>[ xX])\] (?P<goal>.+?)(?=\n- \[|$)', match)

                for status, goal_text in goal_items:
                    goals.append({
                        "text": goal_text.strip(),
                        "completed": status.lower() == 'x',
                        "priority": self._estimate_priority(goal_text),
                        "estimated_duration": self._estimate_duration(goal_text),
                    })

        # Also look for goals in lists not under specific headings
        # Look for goal-like statements
        standalone_goals = re.findall(r'- \[(?P<status>[ xX])\] (?P<goal>.+?)(?=\n- \[|$)', content)
        for status, goal_text in standalone_goals:
            if not any(g["text"] == goal_text.strip() for g in goals):  # Avoid duplicates
                goals.append({
                    "text": goal_text.strip(),
                    "completed": status.lower() == 'x',
                    "priority": self._estimate_priority(goal_text),
                    "estimated_duration": self._estimate_duration(goal_text),
                })

        return goals

    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract tasks from content.

        Args:
            content: Content to extract tasks from

        Returns:
            List of tasks with details
        """
        tasks = []

        # Look for task-related sections
        task_patterns = [
            r'# Tasks?\s*\n((?:.|\n)*?)(?=\n# |\Z)',
            r'## Tasks?\s*\n((?:.|\n)*?)(?=\n## |\Z)',
            r'### Tasks?\s*\n((?:.|\n)*?)(?=\n### |\Z)',
        ]

        for pattern in task_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Extract individual tasks from the section
                task_items = re.findall(r'- \[(?P<status>[ xX])\] (?P<task>.+?)(?=\n- \[|$)', match)

                for status, task_text in task_items:
                    tasks.append({
                        "text": task_text.strip(),
                        "completed": status.lower() == 'x',
                        "priority": self._estimate_priority(task_text),
                        "estimated_duration": self._estimate_duration(task_text),
                        "dependencies": [],
                    })

        # Also look for tasks in lists not under specific headings
        standalone_tasks = re.findall(r'- \[(?P<status>[ xX])\] (?P<task>.+?)(?=\n- \[|$)', content)
        for status, task_text in standalone_tasks:
            if not any(t["text"] == task_text.strip() for t in tasks):  # Avoid duplicates
                tasks.append({
                    "text": task_text.strip(),
                    "completed": status.lower() == 'x',
                    "priority": self._estimate_priority(task_text),
                    "estimated_duration": self._estimate_duration(task_text),
                    "dependencies": [],
                })

        return tasks

    def _extract_dependencies(self, content: str, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract task dependencies from content.

        Args:
            content: Content to extract dependencies from
            tasks: List of tasks to check dependencies for

        Returns:
            Dictionary mapping task indices to dependency indices
        """
        dependencies = {}

        # Look for dependency-related sections
        dep_patterns = [
            r'# Dependencies?\s*\n((?:.|\n)*?)(?=\n# |\Z)',
            r'## Dependencies?\s*\n((?:.|\n)*?)(?=\n## |\Z)',
            r'Dependency relationships?:\s*\n((?:.|\n)*?)(?=\n# |\n## |\Z)',
        ]

        for pattern in dep_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Look for dependency statements like "Task A depends on Task B"
                dep_statements = re.findall(r'(\w+)\s+depends\s+on\s+(\w+)', match, re.IGNORECASE)

                for dependent_task, prerequisite_task in dep_statements:
                    # Find the actual task indices
                    dependent_idx = self._find_task_index(dependent_task, tasks)
                    prerequisite_idx = self._find_task_index(prerequisite_task, tasks)

                    if dependent_idx != -1 and prerequisite_idx != -1:
                        if dependent_idx not in dependencies:
                            dependencies[dependent_idx] = []
                        if prerequisite_idx not in dependencies[dependent_idx]:
                            dependencies[dependent_idx].append(prerequisite_idx)

        return dependencies

    def _extract_timeline(self, content: str) -> Dict[str, Any]:
        """Extract timeline information from content.

        Args:
            content: Content to extract timeline from

        Returns:
            Dictionary with timeline information
        """
        timeline = {}

        # Look for start/end dates
        start_dates = re.findall(r'(?:start(?:ed)?|begin(?:ning)?|commencement):\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
        end_dates = re.findall(r'(?:end(?:ed)?|finish(?:ed)?|completion|deadline):\s*(.+?)(?=\n|$)', content, re.IGNORECASE)

        if start_dates:
            timeline["start_date"] = start_dates[0].strip()
        if end_dates:
            timeline["end_date"] = end_dates[0].strip()

        # Look for milestone dates
        milestones = re.findall(r'(?P<milestone>.+?)\s*:\s*(?P<date>.+?)(?=\n|$)', content)
        timeline["milestones"] = []

        for milestone, date in milestones:
            if any(keyword in milestone.lower() for keyword in ['milestone', 'phase', 'stage']):
                timeline["milestones"].append({
                    "name": milestone.strip(),
                    "date": date.strip()
                })

        return timeline

    def _extract_resources(self, content: str) -> List[Dict[str, str]]:
        """Extract resource information from content.

        Args:
            content: Content to extract resources from

        Returns:
            List of resources
        """
        resources = []

        # Look for resource sections
        resource_patterns = [
            r'# Resources?\s*\n((?:.|\n)*?)(?=\n# |\Z)',
            r'## Resources?\s*\n((?:.|\n)*?)(?=\n## |\Z)',
            r'Required resources?:\s*\n((?:.|\n)*?)(?=\n# |\n## |\Z)',
        ]

        for pattern in resource_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Extract resource items
                resource_items = re.findall(r'- (.+?)(?=\n- |$)', match)
                for resource in resource_items:
                    resources.append({"name": resource.strip()})

        return resources

    def _estimate_priority(self, text: str) -> str:
        """Estimate priority based on keywords in text.

        Args:
            text: Text to analyze for priority

        Returns:
            Priority level ('high', 'medium', 'low')
        """
        high_priority_keywords = [
            'urgent', 'critical', 'important', 'priority', 'crucial', 'essential',
            'must', 'need', 'required', 'vital', 'immediate'
        ]

        medium_priority_keywords = [
            'should', 'would', 'nice', 'good', 'beneficial', 'helpful'
        ]

        text_lower = text.lower()

        for keyword in high_priority_keywords:
            if keyword in text_lower:
                return 'high'

        for keyword in medium_priority_keywords:
            if keyword in text_lower:
                return 'medium'

        return 'low'

    def _estimate_duration(self, text: str) -> str:
        """Estimate duration based on keywords in text.

        Args:
            text: Text to analyze for duration

        Returns:
            Estimated duration ('short', 'medium', 'long')
        """
        short_duration_keywords = [
            'quick', 'fast', 'short', 'simple', 'easy', 'brief', 'immediate'
        ]

        long_duration_keywords = [
            'complex', 'long', 'extended', 'lengthy', 'extensive', 'major', 'significant'
        ]

        text_lower = text.lower()

        for keyword in short_duration_keywords:
            if keyword in text_lower:
                return 'short'

        for keyword in long_duration_keywords:
            if keyword in text_lower:
                return 'long'

        return 'medium'

    def _find_task_index(self, task_identifier: str, tasks: List[Dict[str, Any]]) -> int:
        """Find the index of a task by its identifier.

        Args:
            task_identifier: Identifier to search for
            tasks: List of tasks to search in

        Returns:
            Index of task or -1 if not found
        """
        for i, task in enumerate(tasks):
            # Check if identifier matches task text (partial match)
            if task_identifier.lower() in task["text"].lower():
                return i

        # If not found by partial match, try to match by position (e.g., "first task", "second task")
        if task_identifier.lower().startswith("first"):
            return 0
        elif task_identifier.lower().startswith("second"):
            return 1
        elif task_identifier.lower().startswith("third"):
            return 2

        return -1


def parse_plan_file(file_path: str | Path) -> Dict[str, Any]:
    """Convenience function to parse a Plan.md file.

    Args:
        file_path: Path to the Plan.md file

    Returns:
        Dictionary containing parsed plan information
    """
    parser = PlanParser()
    return parser.parse_plan_file(file_path)