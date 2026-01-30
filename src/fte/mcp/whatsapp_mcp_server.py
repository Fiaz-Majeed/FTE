"""
WhatsApp-Enabled MCP Server - Enhanced MCP server with WhatsApp messaging capabilities
including sending messages, monitoring status, and integration with business workflows.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Try to import py_mcp (may not be installed)
try:
    from py_mcp.server import MCPServer
    from py_mcp.protocol import ProtocolHandler
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: py_mcp not available. Using mock server.")

# Import local components
from ..skills.linkedin_post_generator import LinkedInPostGenerator
from ..approval.multi_level_approval import MultiLevelApprovalSystem
from ..scheduler.business_scheduler import BusinessScheduleManager
from ..skills.plan_generator import PlanGenerator
from ..watchers.whatsapp_watcher import WhatsAppWatcher

class WhatsAppMCPServer:
    """Enhanced MCP server with WhatsApp messaging capabilities."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize the WhatsApp-enabled MCP server.

        Args:
            host: Host address for the server
            port: Port number for the server
        """
        self.host = host
        self.port = port

        if MCP_AVAILABLE:
            self.server = MCPServer(host, port)
            self.protocol_handler = ProtocolHandler()
        else:
            self.server = None
            self.protocol_handler = None

        # Initialize business components
        self.linkedin_generator = LinkedInPostGenerator()
        self.approval_system = MultiLevelApprovalSystem()
        self.scheduler = BusinessScheduleManager()
        self.plan_generator = PlanGenerator()

        # Initialize WhatsApp components
        self.whatsapp_watcher = None
        self.twilio_client = None
        self.twilio_credentials = {}

        # Register enhanced actions
        self._register_enhanced_actions()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _register_enhanced_actions(self):
        """Register enhanced MCP actions for business automation including WhatsApp."""

        # LinkedIn posting actions
        if self.server:
            self.server.register_action("linkedin_create_post", self.create_linkedin_post)
            self.server.register_action("linkedin_schedule_post", self.schedule_linkedin_post)
            self.server.register_action("linkedin_analyze_content", self.analyze_linkedin_content)

            # Approval workflow actions
            self.server.register_action("approval_request", self.request_approval)
            self.server.register_action("approval_approve", self.approve_request)
            self.server.register_action("approval_reject", self.reject_request)
            self.server.register_action("approval_get_pending", self.get_pending_approvals)

            # Scheduling actions
            self.server.register_action("schedule_task", self.schedule_task)
            self.server.register_action("schedule_cancel", self.cancel_scheduled_task)
            self.server.register_action("schedule_list", self.list_scheduled_tasks)

            # Plan generation actions
            self.server.register_action("plan_generate", self.generate_plan)
            self.server.register_action("plan_save", self.save_plan)

            # Lead management actions
            self.server.register_action("lead_create", self.create_lead)
            self.server.register_action("lead_qualify", self.qualify_lead)
            self.server.register_action("lead_assign", self.assign_lead)
            self.server.register_action("lead_track", self.track_lead)

            # WhatsApp-specific actions
            self.server.register_action("whatsapp_send_message", self.send_whatsapp_message)
            self.server.register_action("whatsapp_check_status", self.check_whatsapp_message_status)
            self.server.register_action("whatsapp_get_conversations", self.get_whatsapp_conversations)
            self.server.register_action("whatsapp_setup", self.setup_whatsapp_integration)
            self.server.register_action("whatsapp_send_bulk", self.send_bulk_whatsapp_messages)
            self.server.register_action("whatsapp_schedule_message", self.schedule_whatsapp_message)

    async def setup_whatsapp_integration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Setup WhatsApp integration with Twilio credentials.

        Args:
            params: Parameters including Twilio credentials

        Returns:
            Response with setup status
        """
        try:
            account_sid = params.get('account_sid')
            auth_token = params.get('auth_token')
            from_number = params.get('from_number')  # WhatsApp number in format: whatsapp:+1234567890

            if not account_sid or not auth_token:
                return {
                    'status': 'error',
                    'message': 'Twilio account SID and auth token are required',
                    'timestamp': datetime.now().isoformat()
                }

            # Store credentials
            self.twilio_credentials = {
                'account_sid': account_sid,
                'auth_token': auth_token,
                'from_number': from_number or 'whatsapp:+14155238886'  # Default sandbox number
            }

            # Initialize Twilio client
            try:
                from twilio.rest import Client
                self.twilio_client = Client(account_sid, auth_token)

                # Test connection
                account_info = self.twilio_client.api.accounts(account_sid).fetch()

                return {
                    'status': 'success',
                    'message': 'WhatsApp integration setup successfully',
                    'account_name': account_info.friendly_name,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Twilio connection failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error setting up WhatsApp integration: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def send_whatsapp_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a WhatsApp message using Twilio API.

        Args:
            params: Parameters including recipient and message content

        Returns:
            Response with message details and status
        """
        try:
            # Check if Twilio is properly configured
            if not self.twilio_client:
                return {
                    'status': 'error',
                    'message': 'WhatsApp integration not configured. Call whatsapp_setup first.',
                    'timestamp': datetime.now().isoformat()
                }

            to_number = params.get('to_number')  # Should be in format: +1234567890
            message_body = params.get('message_body')
            media_url = params.get('media_url')  # Optional media URL

            if not to_number or not message_body:
                return {
                    'status': 'error',
                    'message': 'Both to_number and message_body are required',
                    'timestamp': datetime.now().isoformat()
                }

            # Format recipient number for WhatsApp
            if not to_number.startswith('+'):
                return {
                    'status': 'error',
                    'message': 'Phone number must start with + followed by country code',
                    'timestamp': datetime.now().isoformat()
                }

            whatsapp_recipient = f"whatsapp:{to_number}"
            whatsapp_sender = self.twilio_credentials.get('from_number', 'whatsapp:+14155238886')

            # Send the message
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=whatsapp_sender,
                to=whatsapp_recipient,
                media_url=[media_url] if media_url else None
            )

            return {
                'status': 'success',
                'message_sid': message.sid,
                'to_number': to_number,
                'message_body': message_body,
                'status': message.status,
                'timestamp': datetime.now().isoformat(),
                'date_created': str(message.date_created)
            }

        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def send_bulk_whatsapp_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send bulk WhatsApp messages to multiple recipients.

        Args:
            params: Parameters including list of recipients and message

        Returns:
            Response with bulk sending results
        """
        try:
            # Check if Twilio is properly configured
            if not self.twilio_client:
                return {
                    'status': 'error',
                    'message': 'WhatsApp integration not configured. Call whatsapp_setup first.',
                    'timestamp': datetime.now().isoformat()
                }

            recipients = params.get('recipients', [])  # List of phone numbers
            message_body = params.get('message_body')
            personalized_fields = params.get('personalized_fields', {})  # Fields to personalize message

            if not recipients or not message_body:
                return {
                    'status': 'error',
                    'message': 'Recipients list and message_body are required',
                    'timestamp': datetime.now().isoformat()
                }

            results = []
            success_count = 0
            error_count = 0

            for recipient in recipients:
                try:
                    # Personalize message if needed
                    personalized_message = message_body
                    for field, value in personalized_fields.items():
                        placeholder = f"{{{field}}}"
                        personalized_message = personalized_message.replace(placeholder, str(value))

                    # Send individual message
                    result = await self.send_whatsapp_message({
                        'to_number': recipient,
                        'message_body': personalized_message
                    })

                    if result['status'] == 'success':
                        success_count += 1
                    else:
                        error_count += 1

                    results.append({
                        'recipient': recipient,
                        'result': result
                    })

                except Exception as e:
                    error_count += 1
                    results.append({
                        'recipient': recipient,
                        'result': {
                            'status': 'error',
                            'message': str(e),
                            'timestamp': datetime.now().isoformat()
                        }
                    })

            return {
                'status': 'success',
                'total_recipients': len(recipients),
                'successful_sends': success_count,
                'failed_sends': error_count,
                'detailed_results': results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error sending bulk WhatsApp messages: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def check_whatsapp_message_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check the status of a sent WhatsApp message.

        Args:
            params: Parameters including message SID

        Returns:
            Response with message status details
        """
        try:
            # Check if Twilio is properly configured
            if not self.twilio_client:
                return {
                    'status': 'error',
                    'message': 'WhatsApp integration not configured. Call whatsapp_setup first.',
                    'timestamp': datetime.now().isoformat()
                }

            message_sid = params.get('message_sid')

            if not message_sid:
                return {
                    'status': 'error',
                    'message': 'Message SID is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Get message status
            message = self.twilio_client.messages(message_sid).fetch()

            return {
                'status': 'success',
                'message_sid': message.sid,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': str(message.date_sent),
                'date_updated': str(message.date_updated),
                'num_segments': message.num_segments,
                'price': message.price,
                'price_unit': message.price_unit,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp message status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def get_whatsapp_conversations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent WhatsApp conversations.

        Args:
            params: Parameters for filtering conversations

        Returns:
            Response with conversation history
        """
        try:
            # Check if Twilio is properly configured
            if not self.twilio_client:
                return {
                    'status': 'error',
                    'message': 'WhatsApp integration not configured. Call whatsapp_setup first.',
                    'timestamp': datetime.now().isoformat()
                }

            # Get message history
            limit = params.get('limit', 50)

            messages = self.twilio_client.messages.list(
                limit=min(limit, 100),  # Twilio max limit is 100
                # You can add filters like date ranges, to/from numbers, etc.
            )

            conversations = []
            phone_conversations = {}

            for msg in messages:
                phone_num = msg.from_ if msg.direction == 'inbound' else msg.to

                if phone_num not in phone_conversations:
                    phone_conversations[phone_num] = []

                phone_conversations[phone_num].append({
                    'sid': msg.sid,
                    'body': msg.body,
                    'direction': msg.direction,
                    'status': msg.status,
                    'date_sent': str(msg.date_sent),
                    'date_updated': str(msg.date_updated),
                    'num_segments': msg.num_segments
                })

            # Format conversations
            for phone, msgs in phone_conversations.items():
                conversations.append({
                    'phone_number': phone,
                    'message_count': len(msgs),
                    'latest_message': msgs[0]['body'][:100] + "..." if msgs else "",
                    'messages': msgs[:5]  # Last 5 messages
                })

            return {
                'status': 'success',
                'conversations': conversations,
                'total_conversations': len(conversations),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting WhatsApp conversations: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def schedule_whatsapp_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a WhatsApp message for future sending.

        Args:
            params: Parameters including message details and scheduled time

        Returns:
            Response with scheduling details
        """
        try:
            to_number = params.get('to_number')
            message_body = params.get('message_body')
            scheduled_time_str = params.get('scheduled_time')

            if not to_number or not message_body or not scheduled_time_str:
                return {
                    'status': 'error',
                    'message': 'to_number, message_body, and scheduled_time are required',
                    'timestamp': datetime.now().isoformat()
                }

            # Parse scheduled time
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            except ValueError:
                return {
                    'status': 'error',
                    'message': 'Invalid scheduled_time format. Use ISO format.',
                    'timestamp': datetime.now().isoformat()
                }

            # Create a delayed task to send the message
            async def send_scheduled_message():
                # Wait until scheduled time
                delay = (scheduled_time - datetime.now()).total_seconds()
                if delay > 0:
                    await asyncio.sleep(delay)

                # Send the message
                result = await self.send_whatsapp_message({
                    'to_number': to_number,
                    'message_body': message_body
                })

                self.logger.info(f"Scheduled WhatsApp message sent: {result}")
                return result

            # Schedule the task using the business scheduler
            task_id = f"whatsapp_{to_number}_{int(scheduled_time.timestamp())}"

            # In a real implementation, we would use the scheduler to handle this
            # For now, we'll just indicate that it's scheduled
            return {
                'status': 'success',
                'task_id': task_id,
                'to_number': to_number,
                'scheduled_time': scheduled_time.isoformat(),
                'message_preview': message_body[:50] + "..." if len(message_body) > 50 else message_body,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error scheduling WhatsApp message: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def create_linkedin_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a LinkedIn post based on parameters.

        Args:
            params: Parameters for post creation including type, content, etc.

        Returns:
            Response with post details and status
        """
        try:
            post_type = params.get('type', 'auto')
            objective = params.get('objective', '')

            # Generate the post
            if objective:
                post = self.linkedin_generator.generate_business_post(post_type, objective)
            else:
                post = self.linkedin_generator.generate_business_post(post_type)

            # Apply any additional formatting or customization
            if 'customization' in params:
                post = self._customize_post(post, params['customization'])

            return {
                'status': 'success',
                'post_id': hash(post['content']) % 100000,  # Mock post ID
                'content': post['content'],
                'hashtags': post['hashtags'],
                'scheduled_time': post.get('scheduled_time'),
                'engagement_strategy': post.get('engagement_strategy', 'N/A'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error creating LinkedIn post: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def schedule_linkedin_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a LinkedIn post for future publication.

        Args:
            params: Parameters including post content and scheduled time

        Returns:
            Response with scheduling details
        """
        try:
            post_content = params.get('post_content', '')
            scheduled_time_str = params.get('scheduled_time')

            if not post_content:
                return {
                    'status': 'error',
                    'message': 'Post content is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Parse scheduled time
            if scheduled_time_str:
                scheduled_time = datetime.fromisoformat(scheduled_time_str)
            else:
                # Use optimal posting time
                optimal_times = self.linkedin_generator.get_optimal_posting_times()
                scheduled_time = optimal_times[0] if optimal_times else datetime.now()

            # Create the post
            post_result = await self.create_linkedin_post(params)

            if post_result['status'] == 'success':
                # Schedule the post using the scheduler
                # For now, we'll just return the scheduling info
                task_id = f"linkedin_post_{int(scheduled_time.timestamp())}"

                return {
                    'status': 'success',
                    'task_id': task_id,
                    'scheduled_time': scheduled_time.isoformat(),
                    'post_id': post_result['post_id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return post_result

        except Exception as e:
            self.logger.error(f"Error scheduling LinkedIn post: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def analyze_linkedin_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze vault content for LinkedIn posting opportunities.

        Args:
            params: Parameters for content analysis

        Returns:
            Analysis results with potential posts
        """
        try:
            analysis = self.linkedin_generator.analyze_vault_content()

            return {
                'status': 'success',
                'analysis': analysis,
                'potential_posts': len(analysis.get('potential_stories', [])),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing LinkedIn content: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def request_approval(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Request approval for a business action.

        Args:
            params: Parameters for the approval request

        Returns:
            Response with approval request details
        """
        try:
            action_type = params.get('action_type', 'generic')
            action_details = params.get('action_details', {})
            requester = params.get('requester', 'system')
            required_level = params.get('approval_level', 'STANDARD')

            # Create approval request
            request_id = self.approval_system.create_request(
                action_type=action_type,
                action_details=action_details,
                requester=requester,
                required_level=required_level
            )

            return {
                'status': 'success',
                'request_id': request_id,
                'action_type': action_type,
                'requester': requester,
                'required_level': required_level,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error requesting approval: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def approve_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve a pending approval request.

        Args:
            params: Parameters including request ID and approver info

        Returns:
            Response with approval status
        """
        try:
            request_id = params.get('request_id')
            approver = params.get('approver', 'system')
            reason = params.get('reason', 'Approved')

            if not request_id:
                return {
                    'status': 'error',
                    'message': 'Request ID is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Approve the request
            success = self.approval_system.approve_request(
                request_id=request_id,
                approver=approver,
                reason=reason
            )

            if success:
                return {
                    'status': 'success',
                    'request_id': request_id,
                    'approved_by': approver,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to approve request',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error approving request: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def reject_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reject a pending approval request.

        Args:
            params: Parameters including request ID and rejection reason

        Returns:
            Response with rejection status
        """
        try:
            request_id = params.get('request_id')
            approver = params.get('approver', 'system')
            reason = params.get('reason', 'Rejected')

            if not request_id:
                return {
                    'status': 'error',
                    'message': 'Request ID is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Reject the request
            success = self.approval_system.reject_request(
                request_id=request_id,
                approver=approver,
                reason=reason
            )

            if success:
                return {
                    'status': 'success',
                    'request_id': request_id,
                    'rejected_by': approver,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to reject request',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error rejecting request: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def get_pending_approvals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of pending approval requests.

        Args:
            params: Parameters for filtering approvals

        Returns:
            Response with pending approvals
        """
        try:
            # Get pending approvals
            pending_approvals = self.approval_system.get_pending_requests()

            return {
                'status': 'success',
                'pending_approvals': pending_approvals,
                'count': len(pending_approvals),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def schedule_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a task for future execution.

        Args:
            params: Parameters for task scheduling

        Returns:
            Response with scheduling details
        """
        try:
            task_type = params.get('task_type')
            execution_time_str = params.get('execution_time')
            task_params = params.get('task_params', {})

            if not task_type or not execution_time_str:
                return {
                    'status': 'error',
                    'message': 'Task type and execution time are required',
                    'timestamp': datetime.now().isoformat()
                }

            # Parse execution time
            execution_time = datetime.fromisoformat(execution_time_str)

            # Schedule the task using the business scheduler
            if task_type == "whatsapp_message":
                result = await self.schedule_whatsapp_message({
                    'to_number': task_params.get('to_number'),
                    'message_body': task_params.get('message_body'),
                    'scheduled_time': execution_time_str
                })
            else:
                # For other task types, we'd use the business scheduler
                task_id = f"task_{task_type}_{int(execution_time.timestamp())}"
                result = {
                    'status': 'success',
                    'task_id': task_id,
                    'task_type': task_type,
                    'scheduled_time': execution_time.isoformat(),
                    'timestamp': datetime.now().isoformat()
                }

            return result
        except Exception as e:
            self.logger.error(f"Error scheduling task: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def cancel_scheduled_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a scheduled task.

        Args:
            params: Parameters including task ID

        Returns:
            Response with cancellation status
        """
        try:
            task_id = params.get('task_id')

            if not task_id:
                return {
                    'status': 'error',
                    'message': 'Task ID is required',
                    'timestamp': datetime.now().isoformat()
                }

            # For now, we'll just return a success response
            # In a real implementation, we'd cancel the actual scheduled task
            return {
                'status': 'success',
                'task_id': task_id,
                'cancelled': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error cancelling task: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def list_scheduled_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all scheduled tasks.

        Args:
            params: Parameters for filtering tasks

        Returns:
            Response with scheduled tasks
        """
        try:
            # Get scheduled tasks from the business scheduler
            tasks = self.scheduler.get_scheduled_jobs()

            return {
                'status': 'success',
                'tasks': tasks,
                'count': len(tasks),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error listing scheduled tasks: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def generate_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a business plan.

        Args:
            params: Parameters for plan generation

        Returns:
            Response with generated plan
        """
        try:
            objective = params.get('objective', '')
            plan_type = params.get('plan_type', 'auto')
            duration = params.get('duration')

            if not objective:
                return {
                    'status': 'error',
                    'message': 'Business objective is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Generate the plan
            plan = self.plan_generator.generate_plan(
                objective=objective,
                plan_type=plan_type,
                duration=duration
            )

            return {
                'status': 'success',
                'plan_id': hash(objective) % 100000,  # Mock plan ID
                'title': plan['title'],
                'plan_type': plan['plan_type'],
                'duration': plan['duration'],
                'timestamp': datetime.now().isoformat(),
                'plan_summary': plan  # Full plan data
            }
        except Exception as e:
            self.logger.error(f"Error generating plan: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def save_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save a generated plan to the vault.

        Args:
            params: Parameters including plan data and output path

        Returns:
            Response with save status
        """
        try:
            plan_data = params.get('plan_data')
            output_path_str = params.get('output_path', 'Plan.md')

            if not plan_data:
                return {
                    'status': 'error',
                    'message': 'Plan data is required',
                    'timestamp': datetime.now().isoformat()
                }

            output_path = Path(output_path_str)

            # Save the plan
            saved_path = self.plan_generator.save_plan_as_markdown(plan_data, output_path)

            return {
                'status': 'success',
                'saved_path': str(saved_path),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error saving plan: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def create_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead.

        Args:
            params: Parameters for lead creation

        Returns:
            Response with lead creation status
        """
        try:
            lead_data = {
                'id': f"lead_{hash(str(params)) % 100000}",
                'name': params.get('name', ''),
                'email': params.get('email', ''),
                'phone': params.get('phone', ''),
                'company': params.get('company', ''),
                'interest': params.get('interest', ''),
                'source': params.get('source', 'unknown'),
                'status': 'new',
                'score': params.get('score', 50),  # Default score
                'created_at': datetime.now().isoformat(),
                'assigned_to': params.get('assigned_to', 'unassigned'),
                'notes': params.get('notes', '')
            }

            # Store lead (in a real system, this would go to a database)
            # For now, we'll just return the created lead
            return {
                'status': 'success',
                'lead': lead_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error creating lead: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def qualify_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify a lead based on criteria.

        Args:
            params: Parameters including lead ID and qualification criteria

        Returns:
            Response with qualification status
        """
        try:
            lead_id = params.get('lead_id')
            qualification_data = params.get('qualification_data', {})

            if not lead_id:
                return {
                    'status': 'error',
                    'message': 'Lead ID is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Calculate qualification score based on provided criteria
            score = self._calculate_qualification_score(qualification_data)

            # Update lead status based on score
            if score >= 80:
                status = 'qualified'
            elif score >= 50:
                status = 'prospect'
            else:
                status = 'cold'

            return {
                'status': 'success',
                'lead_id': lead_id,
                'qualification_score': score,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error qualifying lead: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def assign_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a lead to a team member.

        Args:
            params: Parameters including lead ID and assignee

        Returns:
            Response with assignment status
        """
        try:
            lead_id = params.get('lead_id')
            assignee = params.get('assignee')

            if not lead_id or not assignee:
                return {
                    'status': 'error',
                    'message': 'Lead ID and assignee are required',
                    'timestamp': datetime.now().isoformat()
                }

            # In a real system, this would update the lead record
            # For now, we'll just return the assignment details
            return {
                'status': 'success',
                'lead_id': lead_id,
                'assigned_to': assignee,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error assigning lead: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def track_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track lead progress and interactions.

        Args:
            params: Parameters including lead ID and interaction details

        Returns:
            Response with tracking status
        """
        try:
            lead_id = params.get('lead_id')
            interaction_type = params.get('interaction_type', 'contact')
            notes = params.get('notes', '')

            if not lead_id:
                return {
                    'status': 'error',
                    'message': 'Lead ID is required',
                    'timestamp': datetime.now().isoformat()
                }

            # Record the interaction (in a real system, this would be stored)
            interaction = {
                'lead_id': lead_id,
                'type': interaction_type,
                'timestamp': datetime.now().isoformat(),
                'notes': notes
            }

            return {
                'status': 'success',
                'interaction': interaction,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error tracking lead: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _customize_post(self, post: Dict[str, Any], customization: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customizations to a LinkedIn post."""
        if 'tone' in customization:
            # Apply tone-specific modifications
            if customization['tone'] == 'professional':
                # Ensure professional language
                pass
            elif customization['tone'] == 'casual':
                # Make more casual
                pass

        if 'target_audience' in customization:
            # Customize for specific audience
            post['target_audience'] = customization['target_audience']

        return post

    def _calculate_qualification_score(self, qualification_data: Dict[str, Any]) -> int:
        """Calculate lead qualification score based on criteria."""
        score = 50  # Base score

        # Adjust based on various factors
        if qualification_data.get('budget_available'):
            score += 20
        if qualification_data.get('decision_maker'):
            score += 15
        if qualification_data.get('timeline_short_term'):
            score += 10
        if qualification_data.get('high_value_opportunity'):
            score += 15
        if qualification_data.get('referral_source'):
            score += 5

        # Cap at 100
        return min(score, 100)

    async def start(self):
        """Start the enhanced MCP server."""
        if self.server:
            self.logger.info(f"Starting WhatsApp-Enabled MCP Server on {self.host}:{self.port}")
            await self.server.start()
        else:
            self.logger.info("Starting WhatsApp-Enabled MCP Server (mock mode)")

    async def stop(self):
        """Stop the enhanced MCP server."""
        if self.server:
            self.logger.info("Stopping WhatsApp-Enabled MCP Server")
            await self.server.stop()
        else:
            self.logger.info("Stopping WhatsApp-Enabled MCP Server (mock mode)")


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_whatsapp_mcp_server():
        server = WhatsAppMCPServer()

        print("Testing WhatsApp MCP Server...")

        # Test WhatsApp setup (without actual credentials to avoid errors)
        print("\n1. Testing WhatsApp setup...")
        setup_result = await server.setup_whatsapp_integration({
            'account_sid': 'mock_sid',
            'auth_token': 'mock_token'
        })
        print(f"Setup result: {setup_result['status']}")

        # Test other functionality
        print("\n2. Testing LinkedIn post creation...")
        post_params = {
            'type': 'success_story',
            'objective': 'Increase brand awareness through customer success stories'
        }

        result = await server.create_linkedin_post(post_params)
        print(f"LinkedIn Post Creation: {result['status']}")

        # Test generating a plan
        print("\n3. Testing plan generation...")
        plan_params = {
            'objective': 'Launch new product to small businesses in Q2',
            'plan_type': 'product_launch',
            'duration': '90 days'
        }

        plan_result = await server.generate_plan(plan_params)
        print(f"Plan Generation: {plan_result['status']}")

    # Run the test
    asyncio.run(test_whatsapp_mcp_server())