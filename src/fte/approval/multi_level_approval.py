"""
Multi-Level Approval System - Implements escalation procedures and time-based auto-approvals
for business-sensitive actions with notification system.
"""
import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from ..vault_manager import VaultManager


class ApprovalLevel(Enum):
    """Different levels of approval required for actions."""
    BASIC = "basic"          # Low-risk actions
    STANDARD = "standard"    # Medium-risk actions
    BUSINESS_CRITICAL = "business_critical"  # High-risk business actions
    EXECUTIVE = "executive"  # Strategic decisions requiring executive approval


class ApprovalStatus(Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ESCALATED = "escalated"


@dataclass
class ApprovalRequest:
    """Represents a single approval request."""
    id: str
    action_type: str
    action_details: Dict[str, Any]
    requester: str
    required_level: ApprovalLevel
    created_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    approvers: List[str] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    rejected_by: List[str] = field(default_factory=list)
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    escalation_level: int = 0
    notes: str = ""


class BusinessActionClassifier:
    """Classifies actions requiring business approval based on sensitivity and impact."""

    def __init__(self):
        """Initialize the classifier with business rules."""
        self.classification_rules = self._load_classification_rules()

    def _load_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load classification rules for different action types."""
        return {
            "financial": {
                "level": ApprovalLevel.BUSINESS_CRITICAL,
                "amount_thresholds": {
                    "standard": 1000,      # $1,000
                    "business_critical": 10000,  # $10,000
                    "executive": 100000    # $100,000
                }
            },
            "marketing": {
                "level": ApprovalLevel.STANDARD,
                "sensitivity_keywords": ["press release", "public statement", "brand", "crisis"]
            },
            "linkedin_post": {
                "level": ApprovalLevel.STANDARD,
                "business_impact_keywords": ["business", "revenue", "partnership", "investment"]
            },
            "data_access": {
                "level": ApprovalLevel.BUSINESS_CRITICAL,
                "sensitive_data_types": ["personal", "financial", "confidential"]
            },
            "system_change": {
                "level": ApprovalLevel.EXECUTIVE,
                "change_types": ["production", "database", "security"]
            }
        }

    def classify_action(self, action_type: str, action_details: Dict[str, Any]) -> ApprovalLevel:
        """Classify an action based on type and details.

        Args:
            action_type: Type of action being requested
            action_details: Details about the action

        Returns:
            Required approval level for the action
        """
        # Check if action type has specific rules
        if action_type in self.classification_rules:
            rule = self.classification_rules[action_type]
            level = rule["level"]

            # Apply additional checks based on action details
            if action_type == "financial":
                amount = action_details.get("amount", 0)
                thresholds = rule["amount_thresholds"]

                if amount >= thresholds["executive"]:
                    return ApprovalLevel.EXECUTIVE
                elif amount >= thresholds["business_critical"]:
                    return ApprovalLevel.BUSINESS_CRITICAL
                elif amount >= thresholds["standard"]:
                    return ApprovalLevel.STANDARD
                else:
                    return ApprovalLevel.BASIC

            elif action_type == "marketing" or action_type == "linkedin_post":
                # Check for high-sensitivity keywords
                content = action_details.get("content", "").lower()
                sensitive_keywords = rule.get("sensitivity_keywords", [])

                if any(keyword in content for keyword in sensitive_keywords):
                    return ApprovalLevel.BUSINESS_CRITICAL

            elif action_type == "data_access":
                data_type = action_details.get("data_type", "")
                sensitive_types = rule.get("sensitive_data_types", [])

                if data_type in sensitive_types:
                    return ApprovalLevel.BUSINESS_CRITICAL

        # Default classification based on action type
        high_risk_types = ["financial", "data_access", "system_change"]
        medium_risk_types = ["marketing", "linkedin_post", "hr_decision"]

        if action_type in high_risk_types:
            return ApprovalLevel.BUSINESS_CRITICAL
        elif action_type in medium_risk_types:
            return ApprovalLevel.STANDARD
        else:
            return ApprovalLevel.BASIC


class MultiLevelApprovalSystem:
    """Implements multi-level approval system with escalation and auto-approval features."""

    def __init__(self, vault_path: Optional[str] = None):
        """Initialize the approval system.

        Args:
            vault_path: Path to vault for storing approval history
        """
        self.requests: Dict[str, ApprovalRequest] = {}
        self.business_classifier = BusinessActionClassifier()
        self.vault_manager = VaultManager(vault_path)
        self.notification_callbacks: List[Callable] = []
        self.auto_approval_rules = self._load_auto_approval_rules()

        # Default approvers for each level
        self.default_approvers = {
            ApprovalLevel.BASIC: ["manager"],
            ApprovalLevel.STANDARD: ["senior_manager"],
            ApprovalLevel.BUSINESS_CRITICAL: ["director", "vp"],
            ApprovalLevel.EXECUTIVE: ["ceo", "executive_board"]
        }

    def _load_auto_approval_rules(self) -> Dict[str, Any]:
        """Load rules for time-based auto-approvals."""
        return {
            "basic": {
                "enabled": True,
                "hours": 24,  # Auto-approve basic actions after 24 hours if no response
                "conditions": ["low_risk", "routine", "automated"]
            },
            "standard": {
                "enabled": True,
                "hours": 72,  # Auto-approve standard actions after 72 hours
                "conditions": ["non_financial", "informational"]
            },
            "business_critical": {
                "enabled": False,  # Never auto-approve critical actions
                "hours": 0,
                "conditions": []
            },
            "executive": {
                "enabled": False,  # Never auto-approve executive actions
                "hours": 0,
                "conditions": []
            }
        }

    def register_notification_callback(self, callback: Callable):
        """Register a callback function for approval notifications.

        Args:
            callback: Function to call when notifications occur
        """
        self.notification_callbacks.append(callback)

    def _notify(self, message: str, request_id: Optional[str] = None):
        """Send notification to registered callbacks.

        Args:
            message: Notification message
            request_id: Associated request ID (optional)
        """
        for callback in self.notification_callbacks:
            try:
                callback(message, request_id)
            except Exception as e:
                print(f"Error in notification callback: {e}")

    def create_request(self, action_type: str, action_details: Dict[str, Any],
                      requester: str, required_level: Optional[ApprovalLevel] = None,
                      approvers: Optional[List[str]] = None) -> str:
        """Create a new approval request.

        Args:
            action_type: Type of action requiring approval
            action_details: Details about the action
            requester: Person requesting the approval
            required_level: Required approval level (auto-determined if None)
            approvers: Specific approvers (auto-assigned if None)

        Returns:
            ID of the created request
        """
        # Classify the action if no level specified
        if required_level is None:
            required_level = self.business_classifier.classify_action(action_type, action_details)

        # Generate unique request ID
        request_id = f"req_{int(datetime.now().timestamp() * 1000)}_{hash(action_type) % 10000}"

        # Determine approvers if not specified
        if approvers is None:
            approvers = self.default_approvers.get(required_level, ["default_approver"])

        # Set expiration time based on auto-approval rules
        auto_rule = self.auto_approval_rules.get(required_level.value, {})
        if auto_rule.get("enabled", False):
            hours = auto_rule.get("hours", 24)
            expires_at = datetime.now() + timedelta(hours=hours)
        else:
            expires_at = None

        # Create the request
        request = ApprovalRequest(
            id=request_id,
            action_type=action_type,
            action_details=action_details,
            requester=requester,
            required_level=required_level,
            created_at=datetime.now(),
            approvers=approvers,
            expires_at=expires_at
        )

        # Store the request
        self.requests[request_id] = request

        # Send notification
        self._notify(
            f"New approval request #{request_id} from {requester} for {action_type} "
            f"(Level: {required_level.value})",
            request_id
        )

        return request_id

    def approve_request(self, request_id: str, approver: str, reason: str = "") -> bool:
        """Approve a pending request.

        Args:
            request_id: ID of the request to approve
            approver: Person approving the request
            reason: Reason for approval (optional)

        Returns:
            True if successful, False otherwise
        """
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]

        # Check if request is still pending
        if request.status != ApprovalStatus.PENDING:
            return False

        # Check if approver is authorized
        if approver not in request.approvers and request.required_level != ApprovalLevel.BASIC:
            # For non-basic requests, check if approver has appropriate authority
            approver_level = self._get_approver_level(approver)
            if not self._approver_can_approve_level(approver_level, request.required_level):
                return False

        # Update request status
        request.approved_by.append(approver)
        request.reason = reason
        request.status = self._determine_final_status(request)

        # Notify about approval
        self._notify(
            f"Request #{request_id} approved by {approver}",
            request_id
        )

        # Save to vault for audit trail
        self._save_approval_history(request)

        return True

    def reject_request(self, request_id: str, approver: str, reason: str = "") -> bool:
        """Reject a pending request.

        Args:
            request_id: ID of the request to reject
            approver: Person rejecting the request
            reason: Reason for rejection

        Returns:
            True if successful, False otherwise
        """
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]

        # Check if request is still pending
        if request.status != ApprovalStatus.PENDING:
            return False

        # Check if approver is authorized
        if approver not in request.approvers and request.required_level != ApprovalLevel.BASIC:
            # For non-basic requests, check if approver has appropriate authority
            approver_level = self._get_approver_level(approver)
            if not self._approver_can_approve_level(approver_level, request.required_level):
                return False

        # Update request status
        request.rejected_by.append(approver)
        request.reason = reason
        request.status = ApprovalStatus.REJECTED

        # Notify about rejection
        self._notify(
            f"Request #{request_id} rejected by {approver}: {reason}",
            request_id
        )

        # Save to vault for audit trail
        self._save_approval_history(request)

        return True

    def escalate_request(self, request_id: str, reason: str = "") -> bool:
        """Escalate a request to a higher approval level.

        Args:
            request_id: ID of the request to escalate
            reason: Reason for escalation

        Returns:
            True if successful, False otherwise
        """
        if request_id not in self.requests:
            return False

        request = self.requests[request_id]

        # Check if request is still pending
        if request.status != ApprovalStatus.PENDING:
            return False

        # Increase escalation level
        request.escalation_level += 1

        # Determine new approval level (escalate to next level)
        escalation_map = {
            ApprovalLevel.BASIC: ApprovalLevel.STANDARD,
            ApprovalLevel.STANDARD: ApprovalLevel.BUSINESS_CRITICAL,
            ApprovalLevel.BUSINESS_CRITICAL: ApprovalLevel.EXECUTIVE,
            ApprovalLevel.EXECUTIVE: ApprovalLevel.EXECUTIVE  # Executive stays executive
        }

        new_level = escalation_map.get(request.required_level, request.required_level)
        if new_level != request.required_level:
            request.required_level = new_level
            request.approvers = self.default_approvers.get(new_level, request.approvers)

        request.notes += f"\nEscalated: {reason}" if request.notes else f"Escalated: {reason}"
        request.status = ApprovalStatus.ESCALATED

        # Notify about escalation
        self._notify(
            f"Request #{request_id} escalated to {request.required_level.value}: {reason}",
            request_id
        )

        return True

    def get_pending_requests(self, approver: Optional[str] = None,
                           level: Optional[ApprovalLevel] = None) -> List[ApprovalRequest]:
        """Get pending approval requests.

        Args:
            approver: Filter by specific approver (optional)
            level: Filter by approval level (optional)

        Returns:
            List of pending requests
        """
        pending = [
            req for req in self.requests.values()
            if req.status == ApprovalStatus.PENDING
        ]

        if approver:
            pending = [req for req in pending if approver in req.approvers]

        if level:
            pending = [req for req in pending if req.required_level == level]

        # Check for expired requests and update their status
        self._check_expired_requests()

        return pending

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific request by ID.

        Args:
            request_id: ID of the request

        Returns:
            Request object or None if not found
        """
        return self.requests.get(request_id)

    def _determine_final_status(self, request: ApprovalRequest) -> ApprovalStatus:
        """Determine the final status based on approvals and rejections."""
        # If any rejection, the request is rejected
        if request.rejected_by:
            return ApprovalStatus.REJECTED

        # For basic level, one approval is sufficient
        if request.required_level == ApprovalLevel.BASIC:
            if request.approved_by:
                return ApprovalStatus.APPROVED
        # For other levels, check if all required approvers have approved
        else:
            # This is a simplified model - in practice, you might need
            # more sophisticated approval rules
            if request.approved_by:
                return ApprovalStatus.APPROVED

        return request.status  # Return current status if not fully approved

    def _get_approver_level(self, approver: str) -> ApprovalLevel:
        """Determine the approval level of an approver."""
        # This would normally come from a user management system
        # For now, use a simple mapping
        approver_level_map = {
            "junior_staff": ApprovalLevel.BASIC,
            "manager": ApprovalLevel.STANDARD,
            "senior_manager": ApprovalLevel.STANDARD,
            "director": ApprovalLevel.BUSINESS_CRITICAL,
            "vp": ApprovalLevel.BUSINESS_CRITICAL,
            "ceo": ApprovalLevel.EXECUTIVE,
            "executive_board": ApprovalLevel.EXECUTIVE
        }

        return approver_level_map.get(approver, ApprovalLevel.BASIC)

    def _approver_can_approve_level(self, approver_level: ApprovalLevel,
                                  required_level: ApprovalLevel) -> bool:
        """Check if an approver can approve a request at the required level."""
        level_hierarchy = {
            ApprovalLevel.BASIC: 1,
            ApprovalLevel.STANDARD: 2,
            ApprovalLevel.BUSINESS_CRITICAL: 3,
            ApprovalLevel.EXECUTIVE: 4
        }

        return level_hierarchy.get(approver_level, 0) >= level_hierarchy.get(required_level, 0)

    def _check_expired_requests(self):
        """Check for and handle expired requests."""
        now = datetime.now()

        for request_id, request in self.requests.items():
            if (request.expires_at and
                request.status == ApprovalStatus.PENDING and
                now > request.expires_at):

                # Apply auto-approval if enabled for this level
                auto_rule = self.auto_approval_rules.get(request.required_level.value, {})
                if auto_rule.get("enabled", False):
                    # Auto-approve the request
                    request.status = ApprovalStatus.APPROVED
                    request.approved_by = ["system_auto_approve"]
                    request.reason = f"Auto-approved after {auto_rule.get('hours', 24)} hours"

                    self._notify(
                        f"Request #{request_id} auto-approved by system",
                        request_id
                    )

                    # Save to vault
                    self._save_approval_history(request)

    def _save_approval_history(self, request: ApprovalRequest):
        """Save approval request to vault for audit trail."""
        try:
            history_entry = {
                "request_id": request.id,
                "action_type": request.action_type,
                "requester": request.requester,
                "required_level": request.required_level.value,
                "status": request.status.value,
                "created_at": request.created_at.isoformat(),
                "approved_by": request.approved_by,
                "rejected_by": request.rejected_by,
                "reason": request.reason,
                "approvers": request.approvers,
                "action_details": request.action_details
            }

            # Save to vault
            self.vault_manager.save_content(
                f"approval_{request.id}",
                json.dumps(history_entry, indent=2),
                category="approvals"
            )
        except Exception as e:
            print(f"Error saving approval history: {e}")

    def get_approval_statistics(self) -> Dict[str, Any]:
        """Get statistics about approval requests.

        Returns:
            Dictionary with approval statistics
        """
        stats = {
            "total_requests": len(self.requests),
            "pending_requests": 0,
            "approved_requests": 0,
            "rejected_requests": 0,
            "escalated_requests": 0,
            "expired_requests": 0,
            "requests_by_level": {
                "basic": 0,
                "standard": 0,
                "business_critical": 0,
                "executive": 0
            },
            "average_processing_time": 0
        }

        processing_times = []

        for request in self.requests.values():
            # Count by status
            if request.status == ApprovalStatus.PENDING:
                stats["pending_requests"] += 1
            elif request.status == ApprovalStatus.APPROVED:
                stats["approved_requests"] += 1
            elif request.status == ApprovalStatus.REJECTED:
                stats["rejected_requests"] += 1
            elif request.status == ApprovalStatus.ESCALATED:
                stats["escalated_requests"] += 1
            elif request.status == ApprovalStatus.EXPIRED:
                stats["expired_requests"] += 1

            # Count by level
            level_key = request.required_level.value.replace("_", "")
            if level_key in stats["requests_by_level"]:
                stats["requests_by_level"][level_key] += 1

            # Calculate processing time if completed
            if request.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
                processing_time = (datetime.now() - request.created_at).total_seconds()
                processing_times.append(processing_time)

        # Calculate average processing time
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            stats["average_processing_time"] = avg_time

        return stats


# Example usage and testing
if __name__ == "__main__":
    # Create the multi-level approval system
    approval_system = MultiLevelApprovalSystem()

    # Register a simple notification callback
    def simple_notification(message, request_id):
        print(f"NOTIFICATION: {message}")

    approval_system.register_notification_callback(simple_notification)

    # Test creating different types of requests
    print("Creating approval requests...")

    # Basic request (low-risk)
    req1 = approval_system.create_request(
        action_type="time_off",
        action_details={"days": 2, "reason": "Personal"},
        requester="john.doe",
        required_level=ApprovalLevel.BASIC
    )
    print(f"Created basic request: {req1}")

    # Standard request
    req2 = approval_system.create_request(
        action_type="linkedin_post",
        action_details={
            "content": "Exciting news about our new product launch!",
            "audience": "business professionals"
        },
        requester="marketing.team",
        required_level=ApprovalLevel.STANDARD
    )
    print(f"Created standard request: {req2}")

    # Business critical request
    req3 = approval_system.create_request(
        action_type="financial",
        action_details={
            "amount": 15000,
            "description": "Q1 marketing campaign budget",
            "vendor": "Marketing Agency Inc."
        },
        requester="finance.manager",
        required_level=ApprovalLevel.BUSINESS_CRITICAL
    )
    print(f"Created business critical request: {req3}")

    # Get pending requests
    pending = approval_system.get_pending_requests()
    print(f"\nPending requests: {len(pending)}")

    for req in pending:
        print(f"  - {req.id}: {req.action_type} (Level: {req.required_level.value})")

    # Approve one request
    success = approval_system.approve_request(req1, "supervisor", "Routine request approved")
    print(f"\nApproval result for {req1}: {success}")

    # Get statistics
    stats = approval_system.get_approval_statistics()
    print(f"\nApproval Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")