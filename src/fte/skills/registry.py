"""
Skill Registry - Centralized skill discovery, configuration management, and runtime activation/deactivation
"""
import asyncio
import importlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from .framework import BaseSkill, SkillRegistry as FrameworkSkillRegistry
from ..vault_manager import VaultManager


class SkillRegistry:
    """Centralized registry for discovering, configuring, and managing skills at runtime."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize the skill registry.

        Args:
            vault_path: Path to vault for storing skill configurations
        """
        self.framework_registry = FrameworkSkillRegistry(vault_path)
        self.vault_manager = VaultManager(vault_path)
        self.skill_configurations: Dict[str, Dict[str, Any]] = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.skill_instances: Dict[str, BaseSkill] = {}
        self.activation_states: Dict[str, bool] = {}

        # Load initial configurations
        self._load_skill_configurations()

    def _load_skill_configurations(self):
        """Load skill configurations from vault."""
        try:
            config_content = self.vault_manager.get_content("skill_registry_config.json")
            if config_content:
                self.skill_configurations = json.loads(config_content)
            else:
                # Set up default configurations
                self._setup_default_configurations()
        except Exception:
            # Set up default configurations if loading fails
            self._setup_default_configurations()

    def _setup_default_configurations(self):
        """Set up default skill configurations."""
        self.skill_configurations = {
            "business_intelligence": {
                "module_path": "src.fte.skills.business_intelligence",
                "class_name": "BusinessIntelligenceSkill",
                "enabled": True,
                "auto_load": True,
                "dependencies": [],
                "config": {}
            },
            "customer_outreach": {
                "module_path": "src.fte.skills.customer_outreach",
                "class_name": "CustomerOutreachSkill",
                "enabled": True,
                "auto_load": True,
                "dependencies": [],
                "config": {}
            },
            "sales_pipeline": {
                "module_path": "src.fte.skills.sales_pipeline",
                "class_name": "SalesPipelineSkill",
                "enabled": True,
                "auto_load": True,
                "dependencies": [],
                "config": {}
            },
            "content_strategy": {
                "module_path": "src.fte.skills.content_strategy",
                "class_name": "ContentStrategySkill",
                "enabled": True,
                "auto_load": True,
                "dependencies": [],
                "config": {}
            },
            "linkedin_post_generator": {
                "module_path": "src.fte.skills.linkedin_post_generator",
                "class_name": "LinkedInPostGenerator",
                "enabled": True,
                "auto_load": True,
                "dependencies": [],
                "config": {}
            },
            "plan_generator": {
                "module_path": "src.fte.skills.plan_generator",
                "class_name": "PlanGenerator",
                "enabled": True,
                "auto_load": True,
                "dependencies": [],
                "config": {}
            }
        }

    def register_skill_type(self, skill_name: str, module_path: str, class_name: str,
                           enabled: bool = True, auto_load: bool = True,
                           dependencies: Optional[List[str]] = None,
                           config: Optional[Dict[str, Any]] = None):
        """Register a new skill type in the registry.

        Args:
            skill_name: Name of the skill
            module_path: Python module path to the skill
            class_name: Class name of the skill
            enabled: Whether the skill is enabled
            auto_load: Whether to auto-load the skill
            dependencies: List of skill dependencies
            config: Additional configuration for the skill
        """
        self.skill_configurations[skill_name] = {
            "module_path": module_path,
            "class_name": class_name,
            "enabled": enabled,
            "auto_load": auto_load,
            "dependencies": dependencies or [],
            "config": config or {}
        }

        # Save configuration to vault
        self._save_configurations()

    def get_skill_configuration(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Configuration dictionary if found, None otherwise
        """
        return self.skill_configurations.get(skill_name)

    def list_registered_skills(self) -> List[str]:
        """Get list of all registered skill names.

        Returns:
            List of registered skill names
        """
        return list(self.skill_configurations.keys())

    def list_enabled_skills(self) -> List[str]:
        """Get list of enabled skill names.

        Returns:
            List of enabled skill names
        """
        return [name for name, config in self.skill_configurations.items() if config["enabled"]]

    def list_loaded_skills(self) -> List[str]:
        """Get list of currently loaded skill names.

        Returns:
            List of loaded skill names
        """
        return list(self.skill_instances.keys())

    async def load_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """Load and instantiate a skill.

        Args:
            skill_name: Name of the skill to load

        Returns:
            Loaded skill instance if successful, None otherwise
        """
        if skill_name in self.skill_instances:
            return self.skill_instances[skill_name]

        if skill_name not in self.skill_configurations:
            print(f"Skill {skill_name} not registered in registry")
            return None

        config = self.skill_configurations[skill_name]

        if not config["enabled"]:
            print(f"Skill {skill_name} is disabled")
            return None

        # Check dependencies
        dependencies = config["dependencies"]
        for dep_name in dependencies:
            if dep_name not in self.skill_instances:
                print(f"Dependency {dep_name} not loaded for skill {skill_name}")
                return None

        try:
            # Import the skill module
            if config["module_path"] not in self.loaded_modules:
                module = importlib.import_module(config["module_path"])
                self.loaded_modules[config["module_path"]] = module
            else:
                module = self.loaded_modules[config["module_path"]]

            # Get the skill class
            skill_class = getattr(module, config["class_name"])

            # Instantiate the skill
            skill_instance = skill_class(name=skill_name, vault_path=self.vault_manager.vault_path)

            # Apply configuration
            for key, value in config["config"].items():
                if hasattr(skill_instance, key):
                    setattr(skill_instance, key, value)

            # Store the instance
            self.skill_instances[skill_name] = skill_instance

            # Set activation state
            self.activation_states[skill_name] = False

            print(f"Successfully loaded skill: {skill_name}")
            return skill_instance

        except (ImportError, AttributeError) as e:
            print(f"Error loading skill {skill_name}: {e}")
            return None

    async def unload_skill(self, skill_name: str) -> bool:
        """Unload a skill.

        Args:
            skill_name: Name of the skill to unload

        Returns:
            True if successful, False otherwise
        """
        if skill_name not in self.skill_instances:
            return False

        # Deactivate if active
        if self.activation_states.get(skill_name, False):
            await self.deactivate_skill(skill_name)

        # Remove from instances
        del self.skill_instances[skill_name]
        if skill_name in self.activation_states:
            del self.activation_states[skill_name]

        print(f"Successfully unloaded skill: {skill_name}")
        return True

    async def activate_skill(self, skill_name: str) -> bool:
        """Activate a loaded skill.

        Args:
            skill_name: Name of the skill to activate

        Returns:
            True if successful, False otherwise
        """
        if skill_name not in self.skill_instances:
            print(f"Skill {skill_name} not loaded")
            return False

        skill = self.skill_instances[skill_name]

        try:
            await skill.activate()
            self.activation_states[skill_name] = True
            print(f"Successfully activated skill: {skill_name}")
            return True
        except Exception as e:
            print(f"Error activating skill {skill_name}: {e}")
            return False

    async def deactivate_skill(self, skill_name: str) -> bool:
        """Deactivate an active skill.

        Args:
            skill_name: Name of the skill to deactivate

        Returns:
            True if successful, False otherwise
        """
        if skill_name not in self.skill_instances:
            print(f"Skill {skill_name} not loaded")
            return False

        skill = self.skill_instances[skill_name]

        try:
            await skill.deactivate()
            self.activation_states[skill_name] = False
            print(f"Successfully deactivated skill: {skill_name}")
            return True
        except Exception as e:
            print(f"Error deactivating skill {skill_name}: {e}")
            return False

    def is_skill_loaded(self, skill_name: str) -> bool:
        """Check if a skill is loaded.

        Args:
            skill_name: Name of the skill

        Returns:
            True if loaded, False otherwise
        """
        return skill_name in self.skill_instances

    def is_skill_active(self, skill_name: str) -> bool:
        """Check if a skill is active.

        Args:
            skill_name: Name of the skill

        Returns:
            True if active, False otherwise
        """
        return self.activation_states.get(skill_name, False)

    async def execute_skill(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill with given parameters.

        Args:
            skill_name: Name of the skill to execute
            params: Parameters for skill execution

        Returns:
            Result of skill execution
        """
        if not self.is_skill_loaded(skill_name):
            await self.load_skill(skill_name)

        if not self.is_skill_active(skill_name):
            await self.activate_skill(skill_name)

        if skill_name not in self.skill_instances:
            return {
                "status": "error",
                "message": f"Skill {skill_name} could not be loaded or activated"
            }

        skill = self.skill_instances[skill_name]

        try:
            result = await skill.execute_with_tracking(params)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "skill": skill_name
            }

    def update_skill_configuration(self, skill_name: str, **kwargs) -> bool:
        """Update configuration for a skill.

        Args:
            skill_name: Name of the skill
            **kwargs: Configuration parameters to update

        Returns:
            True if successful, False otherwise
        """
        if skill_name not in self.skill_configurations:
            return False

        config = self.skill_configurations[skill_name]

        # Update configuration
        for key, value in kwargs.items():
            if key in config:
                config[key] = value

        # Save updated configuration
        self._save_configurations()

        print(f"Updated configuration for skill: {skill_name}")
        return True

    def _save_configurations(self):
        """Save skill configurations to vault."""
        try:
            self.vault_manager.save_content(
                "skill_registry_config",
                json.dumps(self.skill_configurations, indent=2, default=str),
                category="config"
            )
        except Exception as e:
            print(f"Error saving skill configurations: {e}")

    async def batch_load_skills(self, skill_names: List[str]) -> Dict[str, bool]:
        """Load multiple skills at once.

        Args:
            skill_names: List of skill names to load

        Returns:
            Dictionary mapping skill names to load success status
        """
        results = {}
        for skill_name in skill_names:
            success = await self.load_skill(skill_name) is not None
            results[skill_name] = success
        return results

    async def batch_activate_skills(self, skill_names: List[str]) -> Dict[str, bool]:
        """Activate multiple skills at once.

        Args:
            skill_names: List of skill names to activate

        Returns:
            Dictionary mapping skill names to activation success status
        """
        results = {}
        for skill_name in skill_names:
            results[skill_name] = await self.activate_skill(skill_name)
        return results

    async def batch_deactivate_skills(self, skill_names: List[str]) -> Dict[str, bool]:
        """Deactivate multiple skills at once.

        Args:
            skill_names: List of skill names to deactivate

        Returns:
            Dictionary mapping skill names to deactivation success status
        """
        results = {}
        for skill_name in skill_names:
            results[skill_name] = await self.deactivate_skill(skill_name)
        return results

    def get_skill_status_report(self) -> Dict[str, Any]:
        """Get a comprehensive status report of all skills.

        Returns:
            Dictionary with status information for all skills
        """
        report = {
            "registered_skills": len(self.skill_configurations),
            "loaded_skills": len(self.skill_instances),
            "active_skills": sum(1 for active in self.activation_states.values() if active),
            "skills": {}
        }

        for skill_name, config in self.skill_configurations.items():
            skill_info = {
                "configuration": config,
                "is_loaded": self.is_skill_loaded(skill_name),
                "is_active": self.is_skill_active(skill_name),
                "activation_state": self.activation_states.get(skill_name, False)
            }

            # Add execution stats if skill is loaded
            if skill_name in self.skill_instances:
                skill = self.skill_instances[skill_name]
                skill_info["execution_stats"] = skill.metadata.execution_stats
                skill_info["status"] = skill.status.value
                skill_info["last_updated"] = skill.metadata.last_updated.isoformat()

            report["skills"][skill_name] = skill_info

        return report

    async def refresh_registry(self):
        """Refresh the registry by reloading configurations."""
        self._load_skill_configurations()

        # Reload any skills that should be auto-loaded
        for skill_name, config in self.skill_configurations.items():
            if config["auto_load"] and config["enabled"]:
                if not self.is_skill_loaded(skill_name):
                    await self.load_skill(skill_name)
                if not self.is_skill_active(skill_name):
                    await self.activate_skill(skill_name)

    def get_skill_dependencies(self, skill_name: str) -> List[str]:
        """Get dependencies for a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            List of dependency skill names
        """
        config = self.skill_configurations.get(skill_name, {})
        return config.get("dependencies", [])

    def get_dependent_skills(self, skill_name: str) -> List[str]:
        """Get skills that depend on a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            List of dependent skill names
        """
        dependents = []
        for name, config in self.skill_configurations.items():
            if skill_name in config.get("dependencies", []):
                dependents.append(name)
        return dependents


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_skill_registry():
        # Create the skill registry
        registry = SkillRegistry()

        print("Testing Skill Registry...")

        # List registered skills
        registered = registry.list_registered_skills()
        print(f"Registered skills: {registered}")

        # Load a few skills
        print("\nLoading skills...")
        load_results = await registry.batch_load_skills(["business_intelligence", "customer_outreach"])
        print(f"Load results: {load_results}")

        # Activate loaded skills
        print("\nActivating skills...")
        activate_results = await registry.batch_activate_skills(list(load_results.keys()))
        print(f"Activation results: {activate_results}")

        # Execute a skill
        print("\nExecuting business intelligence skill...")
        result = await registry.execute_skill("business_intelligence", {
            "market_data": {"revenue": [100, 200, 300]},
            "business_context": {"focus_areas": ["revenue"]}
        })
        print(f"Execution result: {result}")

        # Get status report
        print("\nGetting status report...")
        status_report = registry.get_skill_status_report()
        print(f"Total registered: {status_report['registered_skills']}")
        print(f"Currently loaded: {status_report['loaded_skills']}")
        print(f"Currently active: {status_report['active_skills']}")

        # Show details for loaded skills
        for skill_name, info in status_report["skills"].items():
            if info["is_loaded"]:
                print(f"  {skill_name}: Active={info['is_active']}, Status={info.get('status', 'N/A')}")

        # Test configuration update
        print("\nUpdating skill configuration...")
        update_success = registry.update_skill_configuration(
            "business_intelligence",
            enabled=True,
            auto_load=False
        )
        print(f"Configuration update success: {update_success}")

    # Run the test
    asyncio.run(test_skill_registry())