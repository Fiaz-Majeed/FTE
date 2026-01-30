# Plan Reasoning Skill

This skill helps analyze and process Plan.md files using Claude reasoning to create action plans and recommendations.

## Functions:

### analyze_plan
Analyze a Plan.md file using Claude reasoning.
- `plan_file_path`: Path to the Plan.md file to analyze
- `vault_path`: Path to vault directory (optional)

### generate_action_plan
Generate an action plan from a Plan.md file.
- `plan_file_path`: Path to the Plan.md file
- `vault_path`: Path to vault directory (optional)

### create_plan_summary
Create a summary of a Plan.md file.
- `plan_file_path`: Path to the Plan.md file
- `vault_path`: Path to vault directory (optional)

### process_all_plans
Process all Plan.md files in the vault.
- `vault_path`: Path to vault directory (optional)

### update_plan_with_reasoning
Update a Plan.md file with Claude reasoning insights.
- `plan_file_path`: Path to the Plan.md file to update
- `vault_path`: Path to vault directory (optional)

## Usage Examples:

```
/inbox-processor analyze_plan plan.md
/task-manager generate_action_plan plan.md
/dashboard-updater create_plan_summary plan.md
/note-creator process_all_plans
```