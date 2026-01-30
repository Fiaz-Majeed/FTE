"""Approval Workflow - Handle human-in-the-loop approval for sensitive actions."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..vault_manager import VaultManager


class ApprovalWorkflow:
    """Handle approval workflow for sensitive actions."""

    def __init__(self, vault_path: str | Path | None = None, admin_email: str | None = None):
        """Initialize the approval workflow.

        Args:
            vault_path: Path to vault directory
            admin_email: Admin email for approval notifications
        """
        self.base_path = Path(__file__).parent.parent.parent
        if vault_path is None:
            self.vault_path = self.base_path / "vault"
        else:
            self.vault_path = Path(vault_path)

        self.vault_manager = VaultManager(self.vault_path)
        self.admin_email = admin_email
        self.pending_approvals_dir = self.vault_path / "Pending_Approvals"
        self.approved_actions_dir = self.vault_path / "Approved_Actions"
        self.rejected_actions_dir = self.vault_path / "Rejected_Actions"

        # Create necessary directories
        self.pending_approvals_dir.mkdir(parents=True, exist_ok=True)
        self.approved_actions_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_actions_dir.mkdir(parents=True, exist_ok=True)

    def request_approval(
        self,
        action_type: str,
        action_details: Dict[str, Any],
        requester: str = "system",
        reason: str = "",
        urgency: str = "normal",  # normal, high, urgent
        notify_admin: bool = True,
    ) -> str:
        """Request approval for an action.

        Args:
            action_type: Type of action requesting approval
            action_details: Details about the action
            requester: Who is requesting approval
            reason: Reason for the request
            urgency: Urgency level
            notify_admin: Whether to notify admin via email

        Returns:
            Approval request ID
        """
        request_id = f"approval_{int(datetime.now().timestamp())}_{hash(json.dumps(action_details, sort_keys=True)) % 10000}"

        approval_request = {
            "request_id": request_id,
            "action_type": action_type,
            "action_details": action_details,
            "requester": requester,
            "reason": reason,
            "urgency": urgency,
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "approver": None,
            "approved_at": None,
            "rejected_at": None,
            "rejection_reason": None,
        }

        # Save to pending approvals
        file_path = self.pending_approvals_dir / f"{request_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(approval_request, f, indent=2, default=str)

        # Notify admin if requested
        if notify_admin and self.admin_email:
            self._notify_admin(approval_request)

        return request_id

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval requests.

        Returns:
            List of pending approval requests
        """
        pending = []
        for file_path in self.pending_approvals_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                approval = json.load(f)
                pending.append(approval)

        # Sort by urgency and request time
        urgency_order = {"urgent": 3, "high": 2, "normal": 1}
        pending.sort(key=lambda x: (
            urgency_order.get(x["urgency"], 1),
            datetime.fromisoformat(x["requested_at"])
        ), reverse=True)

        return pending

    def approve_request(
        self,
        request_id: str,
        approver: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Approve an approval request.

        Args:
            request_id: ID of the request to approve
            approver: Who approved the request
            notes: Optional approval notes

        Returns:
            Approval result
        """
        file_path = self.pending_approvals_dir / f"{request_id}.json"

        if not file_path.exists():
            return {
                "success": False,
                "error": f"Request {request_id} not found",
            }

        # Load the request
        with open(file_path, 'r', encoding='utf-8') as f:
            approval_request = json.load(f)

        # Update approval status
        approval_request["status"] = "approved"
        approval_request["approver"] = approver
        approval_request["approved_at"] = datetime.now().isoformat()
        approval_request["notes"] = notes

        # Move to approved actions
        approved_file_path = self.approved_actions_dir / f"{request_id}.json"
        with open(approved_file_path, 'w', encoding='utf-8') as f:
            json.dump(approval_request, f, indent=2, default=str)

        # Remove from pending
        file_path.unlink()

        return {
            "success": True,
            "request_id": request_id,
            "action_type": approval_request["action_type"],
            "result": "approved",
        }

    def reject_request(
        self,
        request_id: str,
        approver: str,
        rejection_reason: str = ""
    ) -> Dict[str, Any]:
        """Reject an approval request.

        Args:
            request_id: ID of the request to reject
            approver: Who rejected the request
            rejection_reason: Reason for rejection

        Returns:
            Rejection result
        """
        file_path = self.pending_approvals_dir / f"{request_id}.json"

        if not file_path.exists():
            return {
                "success": False,
                "error": f"Request {request_id} not found",
            }

        # Load the request
        with open(file_path, 'r', encoding='utf-8') as f:
            approval_request = json.load(f)

        # Update rejection status
        approval_request["status"] = "rejected"
        approval_request["approver"] = approver
        approval_request["rejected_at"] = datetime.now().isoformat()
        approval_request["rejection_reason"] = rejection_reason

        # Move to rejected actions
        rejected_file_path = self.rejected_actions_dir / f"{request_id}.json"
        with open(rejected_file_path, 'w', encoding='utf-8') as f:
            json.dump(approval_request, f, indent=2, default=str)

        # Remove from pending
        file_path.unlink()

        return {
            "success": True,
            "request_id": request_id,
            "action_type": approval_request["action_type"],
            "result": "rejected",
            "rejection_reason": rejection_reason,
        }

    def _notify_admin(self, approval_request: Dict[str, Any]):
        """Notify admin about pending approval.

        Args:
            approval_request: The approval request to notify about
        """
        if not self.admin_email:
            return

        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f"Action Approval Required: {approval_request['action_type']}"
            msg['From'] = "fte-approval@noreply.com"
            msg['To'] = self.admin_email

            # Create message body
            body = f"""
An action requires your approval:

Request ID: {approval_request['request_id']}
Action Type: {approval_request['action_type']}
Requester: {approval_request['requester']}
Urgency: {approval_request['urgency']}
Requested At: {approval_request['requested_at']}
Reason: {approval_request['reason']}

Action Details:
{json.dumps(approval_request['action_details'], indent=2)}

Please review and approve or reject this action.
            """

            msg.attach(MIMEText(body, 'plain'))

            # In a real implementation, you would send the email
            # For now, just print the notification
            print(f"Approval notification sent to {self.admin_email}")
            print(f"Subject: {msg['Subject']}")

        except Exception as e:
            print(f"Failed to send approval notification: {e}")

    def get_approval_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an approval request.

        Args:
            request_id: ID of the request

        Returns:
            Approval status or None if not found
        """
        # Check pending
        pending_file = self.pending_approvals_dir / f"{request_id}.json"
        if pending_file.exists():
            with open(pending_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Check approved
        approved_file = self.approved_actions_dir / f"{request_id}.json"
        if approved_file.exists():
            with open(approved_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Check rejected
        rejected_file = self.rejected_actions_dir / f"{request_id}.json"
        if rejected_file.exists():
            with open(rejected_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None

    def create_approval_decorator(self, action_type: str, urgency: str = "normal"):
        """Create a decorator to wrap functions that require approval.

        Args:
            action_type: Type of action
            urgency: Urgency level

        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Create approval request
                action_details = {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                    "module": func.__module__,
                }

                workflow = self
                request_id = workflow.request_approval(
                    action_type=action_type,
                    action_details=action_details,
                    reason=f"Execution of {func.__name__}",
                    urgency=urgency
                )

                # Wait for approval (in real implementation, this would be asynchronous)
                print(f"Waiting for approval of {request_id}...")

                # In a real implementation, you would wait for approval
                # Here we'll simulate checking for approval
                approval_status = workflow.get_approval_status(request_id)

                if approval_status and approval_status["status"] == "approved":
                    print(f"Action {request_id} approved. Executing...")
                    return func(*args, **kwargs)
                elif approval_status and approval_status["status"] == "rejected":
                    rejection_reason = approval_status.get("rejection_reason", "No reason provided")
                    raise PermissionError(f"Action {request_id} rejected: {rejection_reason}")
                else:
                    raise PermissionError(f"Action {request_id} not yet approved")

            return wrapper
        return decorator


class ApprovalHelper:
    """Helper class for common approval scenarios."""

    def __init__(self, workflow: ApprovalWorkflow):
        """Initialize the approval helper.

        Args:
            workflow: Approval workflow instance
        """
        self.workflow = workflow

    def request_gmail_approval(
        self,
        to: str,
        subject: str,
        body: str,
        urgency: str = "normal"
    ) -> str:
        """Request approval for sending an email.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            urgency: Urgency level

        Returns:
            Approval request ID
        """
        action_details = {
            "to": to,
            "subject": subject,
            "body_preview": body[:200] + "..." if len(body) > 200 else body,
            "body_length": len(body)
        }

        return self.workflow.request_approval(
            action_type="send_email",
            action_details=action_details,
            reason=f"Sending email to {to}: {subject}",
            urgency=urgency
        )

    def request_linkedin_post_approval(
        self,
        content: str,
        visibility: str = "PUBLIC",
        urgency: str = "normal"
    ) -> str:
        """Request approval for posting on LinkedIn.

        Args:
            content: Post content
            visibility: Post visibility
            urgency: Urgency level

        Returns:
            Approval request ID
        """
        action_details = {
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "content_length": len(content),
            "visibility": visibility
        }

        return self.workflow.request_approval(
            action_type="linkedin_post",
            action_details=action_details,
            reason="Creating LinkedIn post",
            urgency=urgency
        )

    def request_file_modification_approval(
        self,
        file_path: str,
        action: str,  # "create", "modify", "delete"
        urgency: str = "normal"
    ) -> str:
        """Request approval for file modification.

        Args:
            file_path: Path of file to modify
            action: Type of action
            urgency: Urgency level

        Returns:
            Approval request ID
        """
        action_details = {
            "file_path": file_path,
            "action": action
        }

        return self.workflow.request_approval(
            action_type=f"file_{action}",
            action_details=action_details,
            reason=f"{action.title()} file: {file_path}",
            urgency=urgency
        )


def create_approval_workflow(
    vault_path: str | Path | None = None,
    admin_email: str | None = None
) -> ApprovalWorkflow:
    """Create an approval workflow instance.

    Args:
        vault_path: Path to vault directory
        admin_email: Admin email for notifications

    Returns:
        ApprovalWorkflow instance
    """
    return ApprovalWorkflow(vault_path=vault_path, admin_email=admin_email)