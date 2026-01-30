# Approval Workflow Skill

This skill handles human-in-the-loop approval for sensitive actions.

## Functions:

### request_action_approval
Request approval for an action.
- `action_type`: Type of action requesting approval
- `action_details`: Details about the action
- `requester`: Who is requesting approval (default: 'system')
- `reason`: Reason for the request (optional)
- `urgency`: Urgency level ('normal', 'high', 'urgent', default: 'normal')
- `vault_path`: Path to vault directory (optional)
- `admin_email`: Admin email for notifications (optional)

### get_pending_approvals
Get all pending approval requests.
- `vault_path`: Path to vault directory (optional)

### approve_action
Approve an approval request.
- `request_id`: ID of the request to approve
- `approver`: Who approved the request
- `notes`: Optional approval notes (optional)
- `vault_path`: Path to vault directory (optional)

### reject_action
Reject an approval request.
- `request_id`: ID of the request to reject
- `approver`: Who rejected the request
- `rejection_reason`: Reason for rejection (optional)
- `vault_path`: Path to vault directory (optional)

### get_approval_status
Get the status of an approval request.
- `request_id`: ID of the request
- `vault_path`: Path to vault directory (optional)

### request_gmail_approval
Request approval for sending an email.
- `to`: Recipient email
- `subject`: Email subject
- `body`: Email body
- `urgency`: Urgency level (default: 'normal')
- `vault_path`: Path to vault directory (optional)
- `admin_email`: Admin email for notifications (optional)

### request_linkedin_post_approval
Request approval for posting on LinkedIn.
- `content`: Post content
- `visibility`: Post visibility (default: 'PUBLIC')
- `urgency`: Urgency level (default: 'normal')
- `vault_path`: Path to vault directory (optional)
- `admin_email`: Admin email for notifications (optional)

## Usage Examples:

```
/inbox-processor request_action_approval "send_email" {"to": "user@example.com", "subject": "Important Update"}
/task-manager get_pending_approvals
/dashboard-updater approve_action "approval_12345" "admin_user"
/note-creator request_gmail_approval "user@example.com" "Meeting Reminder" "Just a reminder about our meeting."
```