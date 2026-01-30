"""
Plan Generator Skill - Generates structured Plan.md files from business objectives
with timeline, resources, and success metrics.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..vault_manager import VaultManager


class PlanGenerator:
    """Generates structured Plan.md files from business objectives."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize the plan generator.

        Args:
            vault_path: Path to the vault directory for historical context
        """
        self.vault_manager = VaultManager(vault_path)
        self.plan_templates = self._load_plan_templates()
        self.resource_estimator = ResourceEstimator()

    def _load_plan_templates(self) -> Dict[str, Any]:
        """Load different plan templates for various business objectives."""
        return {
            "business_development": {
                "title": "Business Development Plan",
                "sections": [
                    "Executive Summary",
                    "Objectives & Goals",
                    "Market Analysis",
                    "Target Audience",
                    "Strategies & Tactics",
                    "Timeline",
                    "Resources Needed",
                    "Budget",
                    "Success Metrics",
                    "Risk Assessment",
                    "Action Items"
                ],
                "duration_options": ["30 days", "60 days", "90 days", "6 months", "1 year"]
            },
            "product_launch": {
                "title": "Product Launch Plan",
                "sections": [
                    "Product Overview",
                    "Market Opportunity",
                    "Launch Objectives",
                    "Target Market",
                    "Marketing Strategy",
                    "Sales Strategy",
                    "Timeline",
                    "Resource Allocation",
                    "Budget",
                    "Success Metrics",
                    "Risk Management",
                    "Post-Launch Activities"
                ],
                "duration_options": ["45 days", "60 days", "90 days", "120 days"]
            },
            "marketing_campaign": {
                "title": "Marketing Campaign Plan",
                "sections": [
                    "Campaign Overview",
                    "Target Audience",
                    "Key Messages",
                    "Channel Strategy",
                    "Content Calendar",
                    "Timeline",
                    "Budget",
                    "Success Metrics",
                    "Competitive Analysis",
                    "Adjustment Protocols"
                ],
                "duration_options": ["30 days", "45 days", "60 days", "90 days"]
            },
            "process_improvement": {
                "title": "Process Improvement Plan",
                "sections": [
                    "Current State Analysis",
                    "Improvement Objectives",
                    "Proposed Solutions",
                    "Implementation Steps",
                    "Timeline",
                    "Resources Required",
                    "Cost-Benefit Analysis",
                    "Success Metrics",
                    "Change Management",
                    "Monitoring Plan"
                ],
                "duration_options": ["30 days", "60 days", "90 days", "6 months"]
            }
        }

    def analyze_business_objective(self, objective: str) -> Dict[str, Any]:
        """Analyze a business objective to determine the best plan type.

        Args:
            objective: Description of the business objective

        Returns:
            Analysis including plan type recommendation
        """
        objective_lower = objective.lower()

        # Determine plan type based on keywords
        if any(keyword in objective_lower for keyword in [
            "launch", "product", "market entry", "new offering", "go-to-market"
        ]):
            plan_type = "product_launch"
        elif any(keyword in objective_lower for keyword in [
            "marketing", "campaign", "promote", "awareness", "brand", "social media"
        ]):
            plan_type = "marketing_campaign"
        elif any(keyword in objective_lower for keyword in [
            "process", "efficiency", "optimization", "workflow", "improvement", "streamline"
        ]):
            plan_type = "process_improvement"
        else:
            # Default to business development for general objectives
            plan_type = "business_development"

        # Extract key elements from objective
        elements = {
            "primary_goal": self._extract_primary_goal(objective),
            "timeline_requirement": self._extract_timeline_requirement(objective),
            "resource_constraints": self._extract_resource_constraints(objective),
            "success_metrics": self._extract_success_metrics(objective),
            "stakeholders": self._extract_stakeholders(objective)
        }

        return {
            "recommended_plan_type": plan_type,
            "confidence": 0.8,  # High confidence based on keyword matching
            "key_elements": elements,
            "historical_context": self._get_historical_context(objective)
        }

    def _extract_primary_goal(self, objective: str) -> str:
        """Extract the primary goal from the objective."""
        # Look for goal-indicating phrases
        goal_patterns = [
            "increase", "grow", "expand", "launch", "develop", "improve",
            "reduce", "optimize", "enhance", "establish", "build", "create"
        ]

        words = objective.lower().split()
        for i, word in enumerate(words):
            if word in goal_patterns and i + 1 < len(words):
                # Return the goal phrase (verb + object)
                return f"{word} {words[i+1]}"

        return objective[:50] + "..." if len(objective) > 50 else objective

    def _extract_timeline_requirement(self, objective: str) -> Optional[str]:
        """Extract timeline requirements from the objective."""
        timeline_patterns = [
            "by", "within", "in", "next", "over the next", "until", "before"
        ]

        words = objective.lower().split()
        for i, word in enumerate(words):
            if word in timeline_patterns and i + 1 < len(words):
                # Return the next 2-3 words as the timeline
                end_idx = min(i + 3, len(words))
                return " ".join(words[i:end_idx])

        return None

    def _extract_resource_constraints(self, objective: str) -> List[str]:
        """Extract resource constraints from the objective."""
        constraint_patterns = [
            "limited", "small", "tight", "constrained", "minimal",
            "budget", "low", "restricted", "few", "short"
        ]

        constraints = []
        words = objective.lower().split()
        for word in constraint_patterns:
            if word in words:
                constraints.append(word)

        return constraints

    def _extract_success_metrics(self, objective: str) -> List[str]:
        """Extract potential success metrics from the objective."""
        metric_patterns = [
            "revenue", "profit", "sales", "customers", "users",
            "engagement", "conversion", "growth", "roi", "efficiency"
        ]

        metrics = []
        objective_lower = objective.lower()
        for pattern in metric_patterns:
            if pattern in objective_lower:
                metrics.append(pattern)

        return metrics

    def _extract_stakeholders(self, objective: str) -> List[str]:
        """Extract stakeholders from the objective."""
        stakeholder_patterns = [
            "team", "department", "client", "customer", "partner",
            "vendor", "supplier", "manager", "employee"
        ]

        stakeholders = []
        objective_lower = objective.lower()
        for pattern in stakeholder_patterns:
            if pattern in objective_lower:
                stakeholders.append(pattern)

        return stakeholders

    def _get_historical_context(self, objective: str) -> Dict[str, Any]:
        """Get historical context from the vault for similar objectives."""
        # Search vault for similar objectives or related content
        related_content = self.vault_manager.search_content(objective, limit=5)

        return {
            "similar_past_projects": len(related_content),
            "relevant_lessons_learned": self._extract_lessons(related_content),
            "past_performance_data": self._extract_performance_data(related_content)
        }

    def _extract_lessons(self, content_list: List[Dict[str, Any]]) -> List[str]:
        """Extract lessons learned from historical content."""
        lessons = []
        for content in content_list:
            text = content.get('content', '')
            if 'lesson' in text.lower() or 'learned' in text.lower() or 'mistake' in text.lower():
                lessons.append(text[:100] + "..." if len(text) > 100 else text)

        return lessons[:3]  # Limit to top 3 lessons

    def _extract_performance_data(self, content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract performance data from historical content."""
        performance_data = {}

        for content in content_list:
            text = content.get('content', '').lower()
            # Look for performance indicators
            if 'performance' in text or 'result' in text or 'metric' in text:
                performance_data[content.get('title', 'Unknown')] = text

        return performance_data

    def generate_plan(self, objective: str, plan_type: Optional[str] = None,
                     duration: Optional[str] = None) -> Dict[str, Any]:
        """Generate a structured plan based on the business objective.

        Args:
            objective: Description of the business objective
            plan_type: Specific plan type (optional, auto-detected if not provided)
            duration: Duration for the plan (optional, auto-selected if not provided)

        Returns:
            Dictionary containing the complete plan structure
        """
        if not plan_type:
            analysis = self.analyze_business_objective(objective)
            plan_type = analysis["recommended_plan_type"]
        else:
            analysis = {"key_elements": {}, "historical_context": {}}

        if plan_type not in self.plan_templates:
            raise ValueError(f"Unknown plan type: {plan_type}")

        template = self.plan_templates[plan_type]

        # Estimate resources needed
        resource_estimate = self.resource_estimator.estimate_resources(objective)

        # Generate the plan
        plan = {
            "title": f"{template['title']} - {objective[:50]}{'...' if len(objective) > 50 else ''}",
            "generated_date": datetime.now().isoformat(),
            "objective": objective,
            "plan_type": plan_type,
            "duration": duration or self._select_duration(template["duration_options"]),
            "sections": self._generate_sections(template["sections"], objective, analysis),
            "resources_needed": resource_estimate,
            "estimated_budget": self._estimate_budget(resource_estimate),
            "success_metrics": self._generate_success_metrics(objective),
            "risks": self._identify_risks(objective),
            "timeline": self._generate_timeline(duration or self._select_duration(template["duration_options"])),
            "action_items": self._generate_action_items(objective),
            "analysis": analysis
        }

        return plan

    def _select_duration(self, duration_options: List[str]) -> str:
        """Select an appropriate duration from available options."""
        # Default to middle option if no specific requirement
        middle_index = len(duration_options) // 2
        return duration_options[middle_index]

    def _generate_sections(self, section_names: List[str], objective: str,
                          analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate content for each section of the plan."""
        sections = {}

        for section_name in section_names:
            sections[section_name] = self._generate_section_content(section_name, objective, analysis)

        return sections

    def _generate_section_content(self, section_name: str, objective: str,
                                 analysis: Dict[str, Any]) -> str:
        """Generate content for a specific section."""
        section_lower = section_name.lower()

        if "executive" in section_lower or "overview" in section_lower:
            return self._generate_executive_summary(objective, analysis)
        elif "objective" in section_lower or "goal" in section_lower:
            return self._generate_objectives(objective, analysis)
        elif "strategy" in section_lower or "tactic" in section_lower:
            return self._generate_strategies(objective, analysis)
        elif "timeline" in section_lower:
            return self._generate_timeline_overview(analysis.get("key_elements", {}))
        elif "resource" in section_lower or "budget" in section_lower:
            return self._generate_resource_section(analysis.get("key_elements", {}))
        elif "metric" in section_lower or "success" in section_lower:
            return self._generate_metrics_section(analysis.get("key_elements", {}))
        elif "risk" in section_lower:
            return self._generate_risk_section(objective)
        elif "action" in section_lower or "item" in section_lower:
            return self._generate_action_items_section(objective)
        else:
            # Generic content for other sections
            return f"This section addresses the {section_name.lower()} aspect of the plan."

    def _generate_executive_summary(self, objective: str, analysis: Dict[str, Any]) -> str:
        """Generate executive summary content."""
        summary = f"This plan outlines the strategy to achieve: {objective}\n\n"
        summary += "Key highlights:\n"

        # Safely get key elements with fallbacks
        key_elements = analysis.get('key_elements', {})
        primary_goal = key_elements.get('primary_goal', 'Not specified')
        summary += f"- Primary goal: {primary_goal}\n"

        timeline = key_elements.get('timeline_requirement')
        if timeline:
            summary += f"- Timeline: {timeline}\n"

        stakeholders = key_elements.get('stakeholders', [])
        if stakeholders:
            summary += f"- Key stakeholders: {', '.join(stakeholders)}\n"

        metrics = key_elements.get('success_metrics', [])
        if metrics:
            summary += f"- Success metrics: {', '.join(metrics)}\n"

        return summary

    def _generate_objectives(self, objective: str, analysis: Dict[str, Any]) -> str:
        """Generate objectives and goals content."""
        return f"Primary Objective: {objective}\n\n" \
               f"Supporting Goals:\n" \
               f"- Goal 1: Define specific, measurable outcome\n" \
               f"- Goal 2: Establish clear timeline\n" \
               f"- Goal 3: Identify success metrics\n" \
               f"- Goal 4: Allocate necessary resources"

    def _generate_strategies(self, objective: str, analysis: Dict[str, Any]) -> str:
        """Generate strategies and tactics content."""
        return f"To achieve {objective}, we will employ the following strategies:\n\n" \
               f"1. Strategy One: Description of the first approach\n" \
               f"   - Tactic 1a: Specific action\n" \
               f"   - Tactic 1b: Specific action\n\n" \
               f"2. Strategy Two: Description of the second approach\n" \
               f"   - Tactic 2a: Specific action\n" \
               f"   - Tactic 2b: Specific action\n\n" \
               f"3. Strategy Three: Description of the third approach\n" \
               f"   - Tactic 3a: Specific action\n" \
               f"   - Tactic 3b: Specific action"

    def _generate_timeline_overview(self, elements: Dict[str, Any]) -> str:
        """Generate timeline overview content."""
        return "Phase 1: Planning and Preparation (Weeks 1-2)\n" \
               "  - Define requirements\n" \
               "  - Assemble team\n" \
               "  - Set up infrastructure\n\n" \
               "Phase 2: Implementation (Weeks 3-6)\n" \
               "  - Execute primary activities\n" \
               "  - Monitor progress\n" \
               "  - Make adjustments\n\n" \
               "Phase 3: Evaluation and Optimization (Weeks 7-8)\n" \
               "  - Assess outcomes\n" \
               "  - Document learnings\n" \
               "  - Plan next steps"

    def _generate_resource_section(self, elements: Dict[str, Any]) -> str:
        """Generate resource requirements content."""
        return "Human Resources:\n" \
               "  - Project Manager: 1 FTE\n" \
               "  - Subject Matter Experts: 2-3 part-time\n" \
               "  - Support Staff: As needed\n\n" \
               "Material Resources:\n" \
               "  - Software licenses\n" \
               "  - Equipment\n" \
               "  - Infrastructure\n\n" \
               "Financial Resources:\n" \
               "  - Personnel costs\n" \
               "  - Operational expenses\n" \
               "  - Contingency fund"

    def _generate_metrics_section(self, elements: Dict[str, Any]) -> str:
        """Generate success metrics content."""
        metrics = elements.get("success_metrics", [])
        base_metrics = [
            "Overall achievement of primary objective",
            "Timeline adherence",
            "Budget compliance",
            "Stakeholder satisfaction"
        ]

        if metrics:
            base_metrics.extend([f"{metric.title()} growth/improvement" for metric in metrics])

        result = "Primary Metrics:\n"
        for i, metric in enumerate(base_metrics, 1):
            result += f"  {i}. {metric}\n"

        result += "\nSecondary Metrics:\n"
        result += "  1. Process efficiency improvements\n"
        result += "  2. Team productivity gains\n"
        result += "  3. Knowledge sharing effectiveness\n"

        return result

    def _generate_risk_section(self, objective: str) -> str:
        """Generate risk assessment content."""
        return "High Priority Risks:\n" \
               "  - Resource availability\n" \
               "  - Timeline constraints\n" \
               "  - External dependencies\n\n" \
               "Medium Priority Risks:\n" \
               "  - Scope creep\n" \
               "  - Stakeholder alignment\n" \
               "  - Technology limitations\n\n" \
               "Mitigation Strategies:\n" \
               "  - Regular monitoring and reporting\n" \
               "  - Clear communication protocols\n" \
               "  - Contingency planning"

    def _generate_action_items_section(self, objective: str) -> str:
        """Generate action items content."""
        return "Immediate Actions (Week 1):\n" \
               "  [ ] Define project scope and requirements\n" \
               "  [ ] Identify and assemble project team\n" \
               "  [ ] Establish communication channels\n" \
               "  [ ] Set up project tracking tools\n\n" \
               "Short-term Actions (Weeks 2-4):\n" \
               "  [ ] Begin implementation activities\n" \
               "  [ ] Conduct regular progress reviews\n" \
               "  [ ] Address initial challenges\n\n" \
               "Ongoing Actions:\n" \
               "  [ ] Monitor KPIs and metrics\n" \
               "  [ ] Communicate progress to stakeholders\n" \
               "  [ ] Adapt approach based on feedback"

    def _estimate_budget(self, resources: Dict[str, Any]) -> str:
        """Estimate budget based on resources."""
        total_cost = 0
        breakdown = []

        if 'personnel' in resources:
            personnel_cost = resources['personnel']['cost']
            total_cost += personnel_cost
            breakdown.append(f"Personnel: ${personnel_cost:,}")

        if 'materials' in resources:
            materials_cost = resources['materials']['cost']
            total_cost += materials_cost
            breakdown.append(f"Materials: ${materials_cost:,}")

        if 'tools' in resources:
            tools_cost = resources['tools']['cost']
            total_cost += tools_cost
            breakdown.append(f"Tools/Software: ${tools_cost:,}")

        breakdown.append(f"Total Estimated: ${total_cost:,}")
        breakdown.append("Note: Costs are estimates and may vary based on actual requirements")

        return "\n".join(breakdown)

    def _generate_success_metrics(self, objective: str) -> List[str]:
        """Generate success metrics for the objective."""
        metrics = [
            f"Achievement of primary goal: {objective}",
            "Adherence to timeline",
            "Budget compliance",
            "Stakeholder satisfaction rating",
            "Quality of deliverables"
        ]

        # Add specific metrics based on objective content
        obj_lower = objective.lower()
        if 'customer' in obj_lower:
            metrics.extend([
                "Customer satisfaction score",
                "Customer retention rate",
                "Net Promoter Score"
            ])
        elif 'revenue' in obj_lower or 'sales' in obj_lower:
            metrics.extend([
                "Revenue growth percentage",
                "Sales conversion rate",
                "Average deal size"
            ])
        elif 'process' in obj_lower or 'efficiency' in obj_lower:
            metrics.extend([
                "Process cycle time reduction",
                "Error rate improvement",
                "Cost per transaction decrease"
            ])

        return metrics

    def _identify_risks(self, objective: str) -> List[str]:
        """Identify potential risks for the objective."""
        risks = [
            "Resource availability constraints",
            "Timeline pressure",
            "Scope creep",
            "External dependencies",
            "Technology challenges"
        ]

        # Add specific risks based on objective content
        obj_lower = objective.lower()
        if 'new' in obj_lower or 'innovative' in obj_lower:
            risks.extend([
                "Technical feasibility challenges",
                "Market acceptance uncertainty",
                "Learning curve for new technologies"
            ])
        elif 'regulatory' in obj_lower or 'compliance' in obj_lower:
            risks.extend([
                "Regulatory changes",
                "Compliance audit findings",
                "Legal liability concerns"
            ])

        return risks

    def _generate_timeline(self, duration: str) -> Dict[str, Any]:
        """Generate a detailed timeline."""
        # Parse duration to get time units
        duration_parts = duration.split()
        num_units = int(duration_parts[0])
        unit = duration_parts[1]

        # Calculate end date
        start_date = datetime.now()
        if 'day' in unit:
            end_date = start_date + timedelta(days=num_units)
        elif 'week' in unit:
            end_date = start_date + timedelta(weeks=num_units)
        elif 'month' in unit:
            # Approximate: 30 days per month
            end_date = start_date + timedelta(days=num_units * 30)
        elif 'year' in unit:
            end_date = start_date + timedelta(days=num_units * 365)
        else:
            end_date = start_date + timedelta(days=30)  # Default to 30 days

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration": duration,
            "milestones": self._generate_milestones(start_date, end_date)
        }

    def _generate_milestones(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate project milestones."""
        duration = end_date - start_date
        milestones = []

        # Add key milestones
        milestones.append({
            "name": "Project Kickoff",
            "date": start_date.isoformat(),
            "description": "Official project start and team alignment"
        })

        # Mid-project milestone
        mid_point = start_date + (duration / 2)
        milestones.append({
            "name": "Mid-Project Review",
            "date": mid_point.isoformat(),
            "description": "Review progress and make necessary adjustments"
        })

        # Final milestone
        milestones.append({
            "name": "Project Completion",
            "date": end_date.isoformat(),
            "description": "Final delivery and evaluation"
        })

        return milestones

    def _generate_action_items(self, objective: str) -> List[Dict[str, Any]]:
        """Generate specific action items."""
        return [
            {
                "task": "Define detailed requirements",
                "responsible": "Project Manager",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "High",
                "status": "Not Started"
            },
            {
                "task": "Assemble project team",
                "responsible": "Department Head",
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "priority": "High",
                "status": "Not Started"
            },
            {
                "task": "Establish success metrics",
                "responsible": "Analytics Team",
                "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
                "priority": "Medium",
                "status": "Not Started"
            }
        ]

    def save_plan_as_markdown(self, plan: Dict[str, Any], output_path: Path) -> Path:
        """Save the plan as a markdown file.

        Args:
            plan: The complete plan dictionary
            output_path: Path where to save the markdown file

        Returns:
            Path to the saved file
        """
        md_content = f"# {plan['title']}\n\n"
        md_content += f"*Generated on: {plan['generated_date']}*\n\n"
        md_content += f"**Objective:** {plan['objective']}\n\n"

        # Add plan details
        md_content += "## Plan Details\n\n"
        md_content += f"- **Type:** {plan['plan_type'].replace('_', ' ').title()}\n"
        md_content += f"- **Duration:** {plan['duration']}\n"
        md_content += f"- **Estimated Budget:** {plan['estimated_budget'].split('\\n')[0]}\n\n"

        # Add each section
        for section_name, content in plan['sections'].items():
            md_content += f"## {section_name}\n\n{content}\n\n"

        # Add resources needed
        md_content += "## Resources Needed\n\n"
        for resource_type, details in plan['resources_needed'].items():
            md_content += f"### {resource_type.title()}\n"
            if isinstance(details, dict):
                for key, value in details.items():
                    md_content += f"- **{key.title()}:** {value}\n"
            else:
                md_content += f"- {details}\n"
            md_content += "\n"

        # Add timeline
        md_content += "## Timeline\n\n"
        md_content += f"**Start Date:** {plan['timeline']['start_date']}\n\n"
        md_content += f"**End Date:** {plan['timeline']['end_date']}\n\n"
        md_content += f"**Duration:** {plan['timeline']['duration']}\n\n"

        md_content += "### Milestones\n\n"
        for milestone in plan['timeline']['milestones']:
            md_content += f"- **{milestone['name']}** ({milestone['date']}): {milestone['description']}\n"

        # Add success metrics
        md_content += "\n## Success Metrics\n\n"
        for i, metric in enumerate(plan['success_metrics'], 1):
            md_content += f"{i}. {metric}\n"

        # Add risks
        md_content += "\n## Risk Assessment\n\n"
        for i, risk in enumerate(plan['risks'], 1):
            md_content += f"{i}. {risk}\n"

        # Add action items
        md_content += "\n## Action Items\n\n"
        md_content += "| Task | Responsible | Due Date | Priority | Status |\n"
        md_content += "|------|-------------|----------|----------|--------|\n"
        for item in plan['action_items']:
            md_content += f"| {item['task']} | {item['responsible']} | {item['due_date']} | {item['priority']} | {item['status']} |\n"

        # Add analysis if available
        if 'analysis' in plan:
            md_content += "\n## Analysis\n\n"
            md_content += f"**Confidence Level:** {plan['analysis'].get('confidence', 'N/A')}\n\n"
            md_content += "### Historical Context\n\n"
            hist_ctx = plan['analysis'].get('historical_context', {})
            md_content += f"- **Similar Past Projects:** {hist_ctx.get('similar_past_projects', 0)}\n"

        output_path.write_text(md_content, encoding='utf-8')
        return output_path


class ResourceEstimator:
    """Estimates resources needed for a business objective."""

    def estimate_resources(self, objective: str) -> Dict[str, Any]:
        """Estimate resources needed based on the objective."""
        obj_lower = objective.lower()

        resources = {
            "personnel": {
                "roles": [],
                "estimation_basis": "Based on objective requirements",
                "cost": self._estimate_personnel_cost(obj_lower)
            },
            "materials": {
                "items": [],
                "estimation_basis": "Standard requirements for this type of objective",
                "cost": self._estimate_materials_cost(obj_lower)
            },
            "tools": {
                "software": [],
                "estimation_basis": "Required for effective execution",
                "cost": self._estimate_tools_cost(obj_lower)
            }
        }

        # Determine specific needs based on objective
        if 'digital' in obj_lower or 'online' in obj_lower or 'web' in obj_lower:
            resources["tools"]["software"] = ["Project management software", "Design tools", "Analytics platform"]
            resources["materials"]["items"] = ["Digital infrastructure", "Online marketing materials"]

        if 'marketing' in obj_lower or 'promotion' in obj_lower:
            resources["personnel"]["roles"] = ["Marketing Specialist", "Content Creator", "Analyst"]
            resources["materials"]["items"] = ["Marketing materials", "Campaign assets", "Promotional items"]

        if 'development' in obj_lower or 'building' in obj_lower:
            resources["personnel"]["roles"] = ["Developer", "Designer", "QA Engineer"]
            resources["materials"]["items"] = ["Development tools", "Testing environments", "Documentation systems"]

        return resources

    def _estimate_personnel_cost(self, objective: str) -> int:
        """Estimate personnel costs."""
        # Base cost calculation
        base_cost = 5000  # $5k per person-month average

        # Adjust based on objective complexity
        if any(word in objective for word in ['complex', 'advanced', 'sophisticated']):
            base_cost *= 1.5
        elif any(word in objective for word in ['simple', 'basic', 'routine']):
            base_cost *= 0.7

        # Number of people estimation
        if 'team' in objective or 'collaboration' in objective:
            num_people = 3
        elif 'individual' in objective or 'personal' in objective:
            num_people = 1
        else:
            num_people = 2  # Default assumption

        return base_cost * num_people

    def _estimate_materials_cost(self, objective: str) -> int:
        """Estimate materials costs."""
        base_cost = 1000  # $1k base materials cost

        if 'physical' in objective or 'hardware' in objective:
            base_cost *= 3
        elif 'digital' in objective or 'online' in objective:
            base_cost *= 0.5  # Digital typically lower material cost

        return base_cost

    def _estimate_tools_cost(self, objective: str) -> int:
        """Estimate tools/software costs."""
        base_cost = 2000  # $2k base tools cost

        if 'ai' in objective or 'machine learning' in objective or 'data' in objective:
            base_cost *= 2  # AI/data tools often more expensive

        return base_cost


# Example usage
if __name__ == "__main__":
    generator = PlanGenerator()

    # Example objective
    sample_objective = "Increase customer engagement on social media platforms by 40% over the next 3 months through targeted content strategy and community management"

    # Analyze the objective
    analysis = generator.analyze_business_objective(sample_objective)
    print(f"Recommended plan type: {analysis['recommended_plan_type']}")
    print(f"Confidence: {analysis['confidence']}")
    print(f"Key elements: {analysis['key_elements']}")

    # Generate the plan
    plan = generator.generate_plan(sample_objective)

    # Print a summary
    print(f"\nPlan Title: {plan['title']}")
    print(f"Duration: {plan['duration']}")
    print(f"Resources needed: {list(plan['resources_needed'].keys())}")
    print(f"Success metrics: {len(plan['success_metrics'])} defined")
    print(f"Milestones: {len(plan['timeline']['milestones'])} identified")

    # Save as markdown
    output_file = Path("Plan.md")
    generator.save_plan_as_markdown(plan, output_file)
    print(f"\nPlan saved to: {output_file.absolute()}")