"""
Sales Pipeline Skill - Lead management and nurturing
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .framework import BaseSkill, SkillMetadata, SkillStatus
from ..vault_manager import VaultManager


class SalesPipelineSkill(BaseSkill):
    """Manages lead management and nurturing in the sales pipeline."""

    def __init__(self, name: str = "sales_pipeline", vault_path: Optional[str] = None):
        """Initialize the sales pipeline skill.

        Args:
            name: Name of the skill
            vault_path: Path to vault for storage
        """
        super().__init__(name, vault_path)
        self.metadata.description = "Manages lead management and nurturing in the sales pipeline"
        self.metadata.category = "sales"

        # Define pipeline stages and progression rules
        self.pipeline_stages = self._define_pipeline_stages()
        self.nurturing_sequences = self._define_nurturing_sequences()

    def _define_pipeline_stages(self) -> Dict[str, Any]:
        """Define the sales pipeline stages."""
        return {
            "prospect": {
                "name": "Prospect",
                "description": "Initial contact with potential customer",
                "qualification_criteria": ["contact_info_valid", "initial_interest"],
                "next_stage": "qualified",
                "typical_duration_days": 7
            },
            "qualified": {
                "name": "Qualified",
                "description": "Lead meets basic qualification criteria",
                "qualification_criteria": ["budget_confirmed", "authority_identified", "need_established", "timeline_defined"],
                "next_stage": "proposal",
                "typical_duration_days": 14
            },
            "proposal": {
                "name": "Proposal",
                "description": "Solution proposal sent to qualified lead",
                "qualification_criteria": ["proposal_accepted"],
                "next_stage": "negotiation",
                "typical_duration_days": 21
            },
            "negotiation": {
                "name": "Negotiation",
                "description": "Contract terms and pricing negotiations",
                "qualification_criteria": ["terms_agreed"],
                "next_stage": "closed_won",
                "typical_duration_days": 14
            },
            "closed_won": {
                "name": "Closed Won",
                "description": "Deal successfully closed",
                "qualification_criteria": ["contract_signed", "payment_received"],
                "next_stage": None,
                "typical_duration_days": 0
            },
            "closed_lost": {
                "name": "Closed Lost",
                "description": "Deal lost to competitor or abandoned",
                "qualification_criteria": ["deal_lost", "alternative_chosen"],
                "next_stage": None,
                "typical_duration_days": 0
            }
        }

    def _define_nurturing_sequences(self) -> Dict[str, List[Dict[str, Any]]]:
        """Define nurturing sequences for different lead types."""
        return {
            "cold_to_warm": [
                {"day": 1, "action": "send_introduction_email", "content": "Nice to meet you, here's what we do..."},
                {"day": 3, "action": "share_valuable_content", "content": "Here's an article you might find interesting..."},
                {"day": 7, "action": "ask_open_question", "content": "What challenges are you facing in your business?"},
                {"day": 14, "action": "offer_consultation", "content": "Would you be interested in a free consultation?"},
                {"day": 21, "action": "present_solution", "content": "Based on our conversation, here's how we can help..."}
            ],
            "warm_to_hot": [
                {"day": 1, "action": "confirm_interest", "content": "Great talking with you yesterday, let's move forward..."},
                {"day": 2, "action": "send_case_study", "content": "Here's how we helped a similar company..."},
                {"day": 5, "action": "schedule_demo", "content": "Shall we schedule a product demonstration?"},
                {"day": 7, "action": "address_concerns", "content": "Do you have any concerns about our solution?"},
                {"day": 10, "action": "send_proposal", "content": "Here's the proposal we discussed..."}
            ],
            "hot_to_closed": [
                {"day": 1, "action": "follow_up_proposal", "content": "Following up on the proposal I sent..."},
                {"day": 3, "action": "address_objections", "content": "I heard your concerns, here's how we can address them..."},
                {"day": 5, "action": "negotiate_terms", "content": "Let me know if these terms work for you..."},
                {"day": 7, "action": "final_push", "content": "Last chance to secure this offer..."},
                {"day": 10, "action": "contract_prep", "content": "Preparing the contract for signature..."}
            ]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sales pipeline operation.

        Args:
            params: Parameters for pipeline management including leads, stage, actions

        Returns:
            Pipeline management results with lead movement and nurturing status
        """
        leads = params.get("leads", [])
        target_stage = params.get("target_stage", "qualified")
        actions = params.get("actions", [])
        time_period = params.get("time_period", "30_days")

        # Manage the sales pipeline
        pipeline_results = await self._manage_sales_pipeline(
            leads, target_stage, actions, time_period
        )

        return {
            "status": "success",
            "pipeline_results": pipeline_results,
            "leads_moved": len(pipeline_results.get("moved_leads", [])),
            "leads_nurtured": len(pipeline_results.get("nurtured_leads", [])),
            "deals_progressed": len(pipeline_results.get("progressed_deals", [])),
            "conversion_rate": pipeline_results.get("conversion_metrics", {}).get("overall_conversion_rate", 0.0),
            "timestamp": datetime.now().isoformat()
        }

    async def _manage_sales_pipeline(
        self,
        leads: List[Dict[str, Any]],
        target_stage: str,
        actions: List[str],
        time_period: str
    ) -> Dict[str, Any]:
        """Manage the sales pipeline for given leads."""
        moved_leads = []
        nurtured_leads = []
        progressed_deals = []
        conversion_metrics = {
            "total_leads": len(leads),
            "converted_leads": 0,
            "lost_leads": 0,
            "overall_conversion_rate": 0.0,
            "stage_conversion_rates": {},
            "avg_sales_cycle_days": 0
        }

        # Process each lead
        for lead in leads:
            processed_lead = await self._process_lead(
                lead, target_stage, actions
            )

            # Determine what happened to the lead
            if processed_lead["previous_stage"] != processed_lead["current_stage"]:
                moved_leads.append(processed_lead)

                # Check if lead was converted
                if processed_lead["current_stage"] == "closed_won":
                    progressed_deals.append(processed_lead)
                    conversion_metrics["converted_leads"] += 1
                elif processed_lead["current_stage"] == "closed_lost":
                    conversion_metrics["lost_leads"] += 1
            else:
                # Even if stage didn't change, lead may have been nurtured
                nurtured_leads.append(processed_lead)

        # Calculate conversion metrics
        if conversion_metrics["total_leads"] > 0:
            conversion_metrics["overall_conversion_rate"] = conversion_metrics["converted_leads"] / conversion_metrics["total_leads"]

        # Calculate stage conversion rates
        stage_counts = {}
        for lead in leads:
            stage = lead.get("stage", "prospect")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

        for stage, count in stage_counts.items():
            if count > 0:
                # Calculate conversion from this stage to closed_won
                converted_from_stage = len([lead for lead in leads if
                                           lead.get("stage_history", []).count(stage) > 0 and
                                           lead.get("current_stage") == "closed_won"])
                conversion_metrics["stage_conversion_rates"][stage] = converted_from_stage / count

        return {
            "moved_leads": moved_leads,
            "nurtured_leads": nurtured_leads,
            "progressed_deals": progressed_deals,
            "conversion_metrics": conversion_metrics,
            "actions_performed": actions,
            "time_period": time_period
        }

    async def _process_lead(
        self,
        lead: Dict[str, Any],
        target_stage: str,
        actions: List[str]
    ) -> Dict[str, Any]:
        """Process a single lead through the pipeline."""
        original_stage = lead.get("stage", "prospect")

        # Determine if lead can advance to target stage
        updated_lead = await self._advance_lead_if_qualified(lead, target_stage)

        # Apply nurturing sequence if needed
        if updated_lead["stage"] != target_stage:
            updated_lead = await self._apply_nurturing_sequence(updated_lead, actions)

        # Update lead history
        if "stage_history" not in updated_lead:
            updated_lead["stage_history"] = []

        if updated_lead["stage"] != original_stage:
            updated_lead["stage_history"].append({
                "stage": updated_lead["stage"],
                "timestamp": datetime.now().isoformat(),
                "reason": f"Advanced toward {target_stage}"
            })

        # Update last contact date
        updated_lead["last_contacted"] = datetime.now().isoformat()

        return {
            **updated_lead,
            "previous_stage": original_stage,
            "current_stage": updated_lead["stage"],
            "stage_advanced": updated_lead["stage"] != original_stage,
            "nurturing_applied": updated_lead.get("nurturing_sequence_applied", False)
        }

    async def _advance_lead_if_qualified(
        self,
        lead: Dict[str, Any],
        target_stage: str
    ) -> Dict[str, Any]:
        """Advance lead to next stage if qualified."""
        current_stage = lead.get("stage", "prospect")

        # Check if we can advance to target stage
        while current_stage != target_stage:
            next_stage = self.pipeline_stages[current_stage]["next_stage"]

            if not next_stage:
                break  # End of pipeline

            # Check qualification criteria for next stage
            qualified = self._check_qualification_criteria(lead, next_stage)

            if qualified:
                lead["stage"] = next_stage
                current_stage = next_stage
            else:
                break  # Can't advance further

        return lead

    async def _apply_nurturing_sequence(
        self,
        lead: Dict[str, Any],
        actions: List[str]
    ) -> Dict[str, Any]:
        """Apply nurturing sequence to the lead."""
        current_stage = lead.get("stage", "prospect")

        # Determine appropriate nurturing sequence based on current stage
        sequence_type = self._determine_nurturing_sequence_type(current_stage)
        sequence = self.nurturing_sequences.get(sequence_type, self.nurturing_sequences["cold_to_warm"])

        # Apply nurturing actions
        applied_actions = []
        for nurture_step in sequence:
            action_taken = await self._execute_nurturing_action(
                lead, nurture_step, actions
            )

            if action_taken:
                applied_actions.append(nurture_step["action"])

        lead["nurturing_sequence_applied"] = True
        lead["last_nurturing_action"] = applied_actions[-1] if applied_actions else None
        lead["nurturing_actions_applied"] = applied_actions

        return lead

    async def _execute_nurturing_action(
        self,
        lead: Dict[str, Any],
        nurture_step: Dict[str, Any],
        requested_actions: List[str]
    ) -> bool:
        """Execute a single nurturing action."""
        # Check if this action is requested or if no specific actions requested
        if requested_actions and nurture_step["action"] not in requested_actions:
            return False

        # In a real implementation, this would execute the actual nurturing action
        # For simulation, we'll just log the action

        action_log = {
            "lead_id": lead.get("id", "unknown"),
            "action": nurture_step["action"],
            "content": nurture_step["content"],
            "timestamp": datetime.now().isoformat()
        }

        # Save action log to vault
        self.vault_manager.save_content(
            f"nurturing_log_{action_log['lead_id']}_{int(datetime.now().timestamp())}",
            str(action_log),
            category="sales_pipeline"
        )

        # Update lead with nurturing activity
        if "nurturing_activities" not in lead:
            lead["nurturing_activities"] = []

        lead["nurturing_activities"].append(action_log)

        # Simulate potential stage advancement based on nurturing
        if nurture_step["action"] == "send_proposal" and lead.get("stage") == "qualified":
            # Proposal often advances leads to proposal stage
            lead["stage"] = "proposal"

        return True

    def _check_qualification_criteria(
        self,
        lead: Dict[str, Any],
        stage: str
    ) -> bool:
        """Check if lead meets qualification criteria for stage."""
        criteria = self.pipeline_stages[stage]["qualification_criteria"]

        # For simulation, we'll say qualification happens based on some lead properties
        # In a real system, this would involve more complex logic

        if stage == "qualified":
            # Check for basic qualification criteria
            has_contact_info = lead.get("email") or lead.get("phone")
            has_company = lead.get("company")
            has_interest = lead.get("interest_level", 0) > 0.5

            return has_contact_info and has_company and has_interest

        elif stage == "proposal":
            # Check if lead is qualified and has budget timeline
            is_qualified = lead.get("stage") == "qualified"
            has_budget = lead.get("budget_range") is not None
            has_timeline = lead.get("decision_timeline") is not None

            return is_qualified and has_budget and has_timeline

        elif stage == "closed_won":
            # Check if terms agreed and contract signed
            terms_agreed = lead.get("terms_agreed", False)
            contract_signed = lead.get("contract_signed", False)

            return terms_agreed and contract_signed

        # For other stages, return True (they can advance if they reach this point)
        return True

    def _determine_nurturing_sequence_type(self, current_stage: str) -> str:
        """Determine the appropriate nurturing sequence type for current stage."""
        if current_stage in ["prospect", "lead"]:
            return "cold_to_warm"
        elif current_stage == "qualified":
            return "warm_to_hot"
        elif current_stage == "proposal":
            return "hot_to_closed"
        else:
            return "cold_to_warm"  # Default

    def get_pipeline_analytics(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get analytics about the sales pipeline."""
        analytics = {
            "total_leads": len(leads),
            "by_stage": {},
            "conversion_funnels": {},
            "avg_time_in_stage": {},
            "lead_quality_metrics": {},
            "forecasted_revenue": 0.0
        }

        # Count leads by stage
        for lead in leads:
            stage = lead.get("stage", "prospect")
            analytics["by_stage"][stage] = analytics["by_stage"].get(stage, 0) + 1

        # Calculate conversion funnels
        stages = list(self.pipeline_stages.keys())
        for i, stage in enumerate(stages[:-1]):  # Exclude last stage
            next_stage = stages[i + 1]
            current_count = analytics["by_stage"].get(stage, 0)
            next_count = analytics["by_stage"].get(next_stage, 0)

            if current_count > 0:
                analytics["conversion_funnels"][f"{stage}_to_{next_stage}"] = next_count / current_count
            else:
                analytics["conversion_funnels"][f"{stage}_to_{next_stage}"] = 0.0

        # Calculate average time in stage (simplified)
        for stage in stages:
            # This would require more detailed timestamp data in real implementation
            avg_days = self.pipeline_stages[stage]["typical_duration_days"]
            analytics["avg_time_in_stage"][stage] = avg_days

        # Calculate lead quality metrics
        qualified_count = analytics["by_stage"].get("qualified", 0)
        total_count = analytics["total_leads"]

        if total_count > 0:
            analytics["lead_quality_metrics"]["qualification_rate"] = qualified_count / total_count

        # Calculate forecasted revenue (simplified)
        closed_won_count = analytics["by_stage"].get("closed_won", 0)
        avg_deal_value = 50000  # Placeholder average deal value
        analytics["forecasted_revenue"] = closed_won_count * avg_deal_value

        return analytics

    def predict_lead_outcome(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the likely outcome for a lead."""
        current_stage = lead.get("stage", "prospect")
        engagement_score = lead.get("engagement_score", 0.5)
        interaction_count = len(lead.get("nurturing_activities", []))

        # Calculate probability of advancing to next stage
        stage_info = self.pipeline_stages.get(current_stage, {})
        typical_duration = stage_info.get("typical_duration_days", 7)

        # Base probability influenced by engagement and interactions
        base_probability = 0.3
        engagement_factor = engagement_score
        interaction_factor = min(interaction_count / 10, 1.0)  # Cap at 1.0

        probability = base_probability + (engagement_factor * 0.4) + (interaction_factor * 0.3)
        probability = min(probability, 1.0)  # Cap at 1.0

        # Predict time to advance
        time_factor = 1.0 / max(engagement_score, 0.1)  # Lower engagement = longer time
        predicted_days = int(typical_duration * time_factor)

        return {
            "current_stage": current_stage,
            "probability_to_next_stage": probability,
            "predicted_days_to_advance": predicted_days,
            "confidence_level": 0.8,  # Model confidence
            "recommended_actions": self._get_recommend_actions(lead)
        }

    def _get_recommend_actions(self, lead: Dict[str, Any]) -> List[str]:
        """Get recommended actions for a lead."""
        current_stage = lead.get("stage", "prospect")
        engagement_score = lead.get("engagement_score", 0.5)

        if current_stage == "prospect":
            if engagement_score > 0.7:
                return ["qualify_lead", "schedule_call"]
            else:
                return ["nurture_email", "share_content"]
        elif current_stage == "qualified":
            if engagement_score > 0.6:
                return ["send_proposal", "schedule_demo"]
            else:
                return ["continue_nurturing", "address_concerns"]
        elif current_stage == "proposal":
            return ["follow_up", "address_objections"]
        elif current_stage == "negotiation":
            return ["finalize_terms", "prepare_contract"]
        else:
            return []


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_sales_pipeline():
        skill = SalesPipelineSkill()

        # Sample leads data
        leads = [
            {
                "id": "lead_001",
                "name": "Company A",
                "email": "contact@companya.com",
                "company": "Company A Inc.",
                "stage": "prospect",
                "interest_level": 0.8,
                "budget_range": "$50K-$100K",
                "decision_timeline": "2-3 months",
                "engagement_score": 0.7
            },
            {
                "id": "lead_002",
                "name": "Company B",
                "email": "info@companyb.com",
                "company": "Company B LLC",
                "stage": "qualified",
                "interest_level": 0.9,
                "budget_range": "$100K-$200K",
                "decision_timeline": "1-2 months",
                "engagement_score": 0.9
            }
        ]

        # Execute pipeline management
        result = await skill.execute({
            "leads": leads,
            "target_stage": "proposal",
            "actions": ["send_proposal", "schedule_demo"]
        })

        print("Sales Pipeline Result:")
        print(f"Status: {result['status']}")
        print(f"Leads Moved: {result['leads_moved']}")
        print(f"Conversion Rate: {result['conversion_rate']:.2%}")

        # Get pipeline analytics
        analytics = skill.get_pipeline_analytics(leads)
        print(f"\nPipeline Analytics: {analytics}")

        # Predict outcome for first lead
        prediction = skill.predict_lead_outcome(leads[0])
        print(f"\nLead Prediction: {prediction}")

    # Run the test
    asyncio.run(test_sales_pipeline())