"""Approval Workflow Skill - Handle human-in-the-loop approval for sensitive actions."""

from pathlib import Path
from typing import Dict, Any, List
from ..approval.workflow import ApprovalWorkflow, ApprovalHelper, create_approval_workflow


def request_action_approval(
    action_type: str,
    action_details: Dict[str, Any],
    requester: str = "system",
    reason: str = "",
    urgency: str = "normal",
    vault_path: str | Path | None = None,
    admin_email: str | None = None,
) -> Dict[str, Any]:
    """Request approval for an action.

    Args:
        action_type: Type of action requesting approval
        action_details: Details about the action
        requester: Who is requesting approval
        reason: Reason for the request
        urgency: Urgency level
        vault_path: Path to vault directory
        admin_email: Admin email for notifications

    Returns:
        Dictionary with approval request result
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path, admin_email=admin_email)

        request_id = workflow.request_approval(
            action_type=action_type,
            action_details=action_details,
            requester=requester,
            reason=reason,
            urgency=urgency
        )

        return {
            "success": True,
            "request_id": request_id,
            "message": f"Approval requested: {request_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error requesting action approval"
        }


def get_pending_approvals(
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Get all pending approval requests.

    Args:
        vault_path: Path to vault directory

    Returns:
        Dictionary with pending approvals
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path)

        pending = workflow.get_pending_approvals()

        return {
            "success": True,
            "pending_approvals": pending,
            "count": len(pending),
            "message": f"Found {len(pending)} pending approvals"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error getting pending approvals"
        }


def approve_action(
    request_id: str,
    approver: str,
    notes: str = "",
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Approve an approval request.

    Args:
        request_id: ID of the request to approve
        approver: Who approved the request
        notes: Optional approval notes
        vault_path: Path to vault directory

    Returns:
        Dictionary with approval result
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path)

        result = workflow.approve_request(
            request_id=request_id,
            approver=approver,
            notes=notes
        )

        return {
            "success": result["success"],
            "result": result,
            "message": f"Action {request_id} {'approved' if result['success'] else 'failed to approve'}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error approving action: {request_id}"
        }


def reject_action(
    request_id: str,
    approver: str,
    rejection_reason: str = "",
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Reject an approval request.

    Args:
        request_id: ID of the request to reject
        approver: Who rejected the request
        rejection_reason: Reason for rejection
        vault_path: Path to vault directory

    Returns:
        Dictionary with rejection result
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path)

        result = workflow.reject_request(
            request_id=request_id,
            approver=approver,
            rejection_reason=rejection_reason
        )

        return {
            "success": result["success"],
            "result": result,
            "message": f"Action {request_id} {'rejected' if result['success'] else 'failed to reject'}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error rejecting action: {request_id}"
        }


def get_approval_status(
    request_id: str,
    vault_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Get the status of an approval request.

    Args:
        request_id: ID of the request
        vault_path: Path to vault directory

    Returns:
        Dictionary with approval status
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path)

        status = workflow.get_approval_status(request_id)

        if status is None:
            return {
                "success": False,
                "error": "Request not found",
                "message": f"Approval request {request_id} not found"
            }

        return {
            "success": True,
            "status": status,
            "message": f"Status for request {request_id}: {status['status']}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error getting approval status: {request_id}"
        }


def request_gmail_approval(
    to: str,
    subject: str,
    body: str,
    urgency: str = "normal",
    vault_path: str | Path | None = None,
    admin_email: str | None = None,
) -> Dict[str, Any]:
    """Request approval for sending an email.

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        urgency: Urgency level
        vault_path: Path to vault directory
        admin_email: Admin email for notifications

    Returns:
        Dictionary with approval request result
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path, admin_email=admin_email)
        helper = ApprovalHelper(workflow)

        request_id = helper.request_gmail_approval(
            to=to,
            subject=subject,
            body=body,
            urgency=urgency
        )

        return {
            "success": True,
            "request_id": request_id,
            "message": f"Gmail approval requested: {request_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error requesting Gmail approval"
        }


def request_linkedin_post_approval(
    content: str,
    visibility: str = "PUBLIC",
    urgency: str = "normal",
    vault_path: str | Path | None = None,
    admin_email: str | None = None,
) -> Dict[str, Any]:
    """Request approval for posting on LinkedIn.

    Args:
        content: Post content
        visibility: Post visibility
        urgency: Urgency level
        vault_path: Path to vault directory
        admin_email: Admin email for notifications

    Returns:
        Dictionary with approval request result
    """
    try:
        workflow = create_approval_workflow(vault_path=vault_path, admin_email=admin_email)
        helper = ApprovalHelper(workflow)

        request_id = helper.request_linkedin_post_approval(
            content=content,
            visibility=visibility,
            urgency=urgency
        )

        return {
            "success": True,
            "request_id": request_id,
            "message": f"LinkedIn post approval requested: {request_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error requesting LinkedIn post approval"
        }