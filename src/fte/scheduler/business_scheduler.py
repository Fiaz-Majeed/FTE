"""
Business Schedule Manager - Handles LinkedIn post scheduling with optimization,
follow-up sequences, and recurring business activities.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from ..vault_manager import VaultManager


class BusinessScheduleManager:
    """Manages business-related scheduling with optimization features."""

    def __init__(self, vault_path: Optional[str] = None):
        """Initialize the business schedule manager.

        Args:
            vault_path: Path to vault for storing schedule history
        """
        self.scheduler = AsyncIOScheduler()
        self.vault_manager = VaultManager(vault_path)
        self.job_callbacks: Dict[str, Callable] = {}
        self.optimization_rules = self._load_optimization_rules()
        self.followup_sequences = self._load_followup_sequences()

    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load scheduling optimization rules."""
        return {
            "linkedin_optimal_times": [
                {"day": "Tuesday", "hour": 8, "minute": 0},
                {"day": "Tuesday", "hour": 12, "minute": 0},
                {"day": "Wednesday", "hour": 8, "minute": 0},
                {"day": "Wednesday", "hour": 12, "minute": 0},
                {"day": "Thursday", "hour": 8, "minute": 0},
                {"day": "Thursday", "hour": 12, "minute": 0}
            ],
            "engagement_analysis": {
                "peak_hours": [9, 10, 11, 12, 13, 14],
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "avoid_times": [0, 1, 2, 3, 4, 5, 6, 7, 22, 23]  # Night hours
            },
            "frequency_limits": {
                "linkedin_daily_max": 2,
                "email_daily_max": 5,
                "social_daily_max": 3
            }
        }

    def _load_followup_sequences(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load predefined follow-up sequences."""
        return {
            "linkedin_connection": [
                {"delay_days": 1, "action": "send_connection_message", "content": "Thanks for connecting!"},
                {"delay_days": 3, "action": "share_valuable_content", "content": "Here's an article I think you'd find interesting..."},
                {"delay_days": 7, "action": "ask_engaging_question", "content": "What's your take on recent industry developments?"}
            ],
            "business_inquiry": [
                {"delay_days": 0, "action": "acknowledge_inquiry", "content": "Thank you for your inquiry. We'll get back to you soon."},
                {"delay_days": 2, "action": "provide_initial_response", "content": "Here's our initial thoughts on your requirements..."},
                {"delay_days": 5, "action": "follow_up", "content": "Just checking if you had any questions about our proposal..."},
                {"delay_days": 10, "action": "final_follow_up", "content": "We'd love to move forward with your project..."}
            ],
            "content_engagement": [
                {"delay_days": 1, "action": "thank_for_engagement", "content": "Thanks for engaging with our content!"},
                {"delay_days": 4, "action": "share_related_content", "content": "Since you liked that post, you might enjoy this..."},
                {"delay_days": 8, "action": "ask_for_feedback", "content": "We'd love to hear your thoughts on this topic..."}
            ]
        }

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def schedule_linkedin_post(self, content: str, target_datetime: Optional[datetime] = None,
                             optimize: bool = True, tags: Optional[List[str]] = None) -> str:
        """Schedule a LinkedIn post with optional optimization.

        Args:
            content: Content of the post
            target_datetime: Target time for posting (optimized if None)
            optimize: Whether to optimize the posting time
            tags: Hashtags to include with the post

        Returns:
            Job ID of the scheduled post
        """
        if optimize and target_datetime is None:
            target_datetime = self._find_optimal_linkedin_time()

        job = self.scheduler.add_job(
            self._execute_linkedin_post,
            'date',
            run_date=target_datetime,
            id=f"linkedin_post_{int(target_datetime.timestamp())}",
            kwargs={
                'content': content,
                'tags': tags or []
            }
        )

        # Save to vault
        self._save_scheduled_item(job.id, "linkedin_post", content, target_datetime)

        return job.id

    def schedule_followup_sequence(self, sequence_type: str, recipient: str,
                                 start_date: Optional[datetime] = None) -> List[str]:
        """Schedule a follow-up sequence.

        Args:
            sequence_type: Type of follow-up sequence
            recipient: Target recipient for the sequence
            start_date: Start date for the sequence (now if None)

        Returns:
            List of job IDs for the scheduled sequence
        """
        if start_date is None:
            start_date = datetime.now()

        if sequence_type not in self.followup_sequences:
            raise ValueError(f"Unknown sequence type: {sequence_type}")

        sequence = self.followup_sequences[sequence_type]
        job_ids = []

        for step in sequence:
            delay = timedelta(days=step["delay_days"])
            run_date = start_date + delay

            job = self.scheduler.add_job(
                self._execute_followup_step,
                'date',
                run_date=run_date,
                id=f"followup_{sequence_type}_{step['delay_days']}d_{recipient}",
                kwargs={
                    'step': step,
                    'recipient': recipient
                }
            )

            job_ids.append(job.id)
            self._save_scheduled_item(job.id, f"followup_{sequence_type}", step["content"], run_date)

        return job_ids

    def schedule_recurring_business_activity(self, activity_type: str, interval: str,
                                          start_date: Optional[datetime] = None,
                                          end_date: Optional[datetime] = None) -> str:
        """Schedule a recurring business activity.

        Args:
            activity_type: Type of business activity
            interval: Interval for recurrence (e.g., 'daily', 'weekly', 'monthly')
            start_date: Start date for the activity
            end_date: End date for the activity (None for indefinite)

        Returns:
            Job ID of the scheduled activity
        """
        if start_date is None:
            start_date = datetime.now()

        # Map interval to cron trigger
        cron_args = self._interval_to_cron(interval)

        job = self.scheduler.add_job(
            self._execute_recurring_activity,
            CronTrigger(**cron_args),
            id=f"recurring_{activity_type}_{interval}",
            start_date=start_date,
            end_date=end_date,
            kwargs={
                'activity_type': activity_type
            }
        )

        # Save to vault
        self._save_scheduled_item(job.id, f"recurring_{activity_type}", f"Recurring {activity_type}", start_date)

        return job.id

    def get_scheduled_jobs(self, job_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of scheduled jobs.

        Args:
            job_type: Filter by job type (optional)

        Returns:
            List of scheduled jobs
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'func': job.func.__name__ if job.func else 'unknown',
                'args': job.args,
                'kwargs': job.kwargs
            }

            if job_type is None or job_type in job.id:
                jobs.append(job_info)

        return jobs

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job.

        Args:
            job_id: ID of the job to cancel

        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.remove_job(job_id)
            return True
        except KeyError:
            return False

    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job.

        Args:
            job_id: ID of the job to pause

        Returns:
            True if successful, False otherwise
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.pause()
                return True
            return False
        except Exception:
            return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job.

        Args:
            job_id: ID of the job to resume

        Returns:
            True if successful, False otherwise
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.resume()
                return True
            return False
        except Exception:
            return False

    def _find_optimal_linkedin_time(self) -> datetime:
        """Find the optimal time for LinkedIn posting based on rules."""
        now = datetime.now()

        # Get optimal times
        optimal_times = self.optimization_rules["linkedin_optimal_times"]

        # Find the next optimal time from now
        for opt_time in optimal_times:
            # Create a datetime for the optimal time on the current day
            opt_datetime = now.replace(hour=opt_time["hour"], minute=opt_time["minute"], second=0, microsecond=0)

            # If this time is in the future today, use it
            if opt_datetime > now:
                return opt_datetime

        # If no optimal time left today, use tomorrow's first optimal time
        tomorrow = now + timedelta(days=1)
        first_optimal = optimal_times[0]
        return tomorrow.replace(hour=first_optimal["hour"], minute=first_optimal["minute"], second=0, microsecond=0)

    def _interval_to_cron(self, interval: str) -> Dict[str, str]:
        """Convert interval string to cron arguments."""
        interval_map = {
            'hourly': {'minute': '0'},
            'daily': {'hour': '9', 'minute': '0'},  # 9 AM daily
            'weekly': {'day_of_week': 'mon', 'hour': '9', 'minute': '0'},  # Monday 9 AM
            'biweekly': {'day_of_week': 'mon', 'hour': '9', 'minute': '0'},  # Every Monday (adjust as needed)
            'monthly': {'day': '1', 'hour': '9', 'minute': '0'}  # 1st of month at 9 AM
        }

        return interval_map.get(interval, {'hour': '9', 'minute': '0'})

    async def _execute_linkedin_post(self, content: str, tags: List[str]):
        """Execute a scheduled LinkedIn post."""
        print(f"Executing LinkedIn post: {content[:50]}...")

        # In a real implementation, this would post to LinkedIn
        # For now, we'll just log it

        # Add tags to content if provided
        if tags:
            tag_str = " ".join([f"#{tag.replace(' ', '')}" for tag in tags])
            content += f"\n\n{tag_str}"

        result = {
            'status': 'posted',
            'content_preview': content[:100],
            'timestamp': datetime.now().isoformat(),
            'tags': tags
        }

        # Save result to vault
        self._save_execution_result('linkedin_post', result)

        print(f"LinkedIn post executed successfully at {result['timestamp']}")

    async def _execute_followup_step(self, step: Dict[str, Any], recipient: str):
        """Execute a follow-up sequence step."""
        print(f"Executing follow-up step for {recipient}: {step['action']}")

        result = {
            'status': 'executed',
            'step': step['action'],
            'recipient': recipient,
            'content': step['content'],
            'timestamp': datetime.now().isoformat()
        }

        # Save result to vault
        self._save_execution_result('followup_step', result)

        print(f"Follow-up step executed for {recipient}")

    async def _execute_recurring_activity(self, activity_type: str):
        """Execute a recurring business activity."""
        print(f"Executing recurring activity: {activity_type}")

        result = {
            'status': 'executed',
            'activity_type': activity_type,
            'timestamp': datetime.now().isoformat()
        }

        # Save result to vault
        self._save_execution_result('recurring_activity', result)

        print(f"Recurring activity {activity_type} executed successfully")

    def _save_scheduled_item(self, job_id: str, item_type: str, content: str, scheduled_time: datetime):
        """Save scheduled item to vault."""
        item_data = {
            'job_id': job_id,
            'type': item_type,
            'content': content,
            'scheduled_time': scheduled_time.isoformat(),
            'created_at': datetime.now().isoformat()
        }

        try:
            self.vault_manager.save_content(
                f"schedule_{job_id}",
                json.dumps(item_data, indent=2),
                category="scheduled_items"
            )
        except Exception as e:
            print(f"Error saving scheduled item: {e}")

    def _save_execution_result(self, action_type: str, result: Dict[str, Any]):
        """Save execution result to vault."""
        try:
            self.vault_manager.save_content(
                f"execution_{action_type}_{int(datetime.now().timestamp())}",
                json.dumps(result, indent=2),
                category="execution_results"
            )
        except Exception as e:
            print(f"Error saving execution result: {e}")

    def get_schedule_statistics(self) -> Dict[str, Any]:
        """Get statistics about scheduled activities.

        Returns:
            Dictionary with schedule statistics
        """
        jobs = self.scheduler.get_jobs()

        stats = {
            'total_scheduled': len(jobs),
            'linkedin_posts': 0,
            'followups': 0,
            'recurring_activities': 0,
            'by_type': {},
            'next_execution_times': []
        }

        for job in jobs:
            job_id = job.id

            if 'linkedin_post' in job_id:
                stats['linkedin_posts'] += 1
            elif 'followup' in job_id:
                stats['followups'] += 1
            elif 'recurring' in job_id:
                stats['recurring_activities'] += 1

            # Count by type
            job_type = job_id.split('_')[0]
            stats['by_type'][job_type] = stats['by_type'].get(job_type, 0) + 1

            # Add next execution time if available
            if job.next_run_time:
                stats['next_execution_times'].append(job.next_run_time.isoformat())

        # Sort next execution times
        stats['next_execution_times'].sort()

        return stats

    def optimize_schedule_for_engagement(self, content_type: str = "linkedin") -> Dict[str, Any]:
        """Suggest optimal scheduling based on engagement patterns.

        Args:
            content_type: Type of content to optimize for

        Returns:
            Dictionary with optimization suggestions
        """
        if content_type == "linkedin":
            optimal_times = self.optimization_rules["linkedin_optimal_times"]
            peak_hours = self.optimization_rules["engagement_analysis"]["peak_hours"]
            best_days = self.optimization_rules["engagement_analysis"]["best_days"]

            return {
                "recommended_times": optimal_times,
                "peak_hours": peak_hours,
                "best_days": best_days,
                "frequency_limit": self.optimization_rules["frequency_limits"]["linkedin_daily_max"],
                "avoid_times": self.optimization_rules["engagement_analysis"]["avoid_times"]
            }

        return {}


# Dynamic Scheduler - extends BusinessScheduleManager with dynamic adjustment capabilities
class DynamicScheduler(BusinessScheduleManager):
    """Extends BusinessScheduleManager with dynamic scheduling adjustments."""

    def __init__(self, vault_path: Optional[str] = None):
        """Initialize the dynamic scheduler."""
        super().__init__(vault_path)
        self.performance_data = self._load_performance_data()
        self.conflict_resolver = ConflictResolver()

    def _load_performance_data(self) -> Dict[str, Any]:
        """Load historical performance data for dynamic adjustments."""
        # In a real system, this would load from database or vault
        return {
            "engagement_rates": {
                "morning": 0.12,  # 12% engagement
                "afternoon": 0.08,  # 8% engagement
                "evening": 0.05,   # 5% engagement
                "weekend": 0.03    # 3% engagement
            },
            "response_rates": {
                "followups_day1": 0.15,
                "followups_day3": 0.10,
                "followups_day7": 0.05
            },
            "optimal_frequency": {
                "linkedin": 2,  # 2 posts per day
                "email": 1      # 1 email per day
            }
        }

    def adjust_schedule_based_on_performance(self, job_id: str, performance_metrics: Dict[str, float]):
        """Adjust a schedule based on performance metrics.

        Args:
            job_id: ID of the job to adjust
            performance_metrics: Performance metrics to consider
        """
        job = self.scheduler.get_job(job_id)
        if not job:
            return

        # Analyze performance and adjust timing if needed
        engagement_rate = performance_metrics.get('engagement_rate', 0)

        if engagement_rate < 0.05:  # Below threshold
            # Reschedule to better time
            current_time = job.next_run_time or datetime.now()
            new_time = self._find_better_time(current_time)

            # Reschedule the job
            self.scheduler.reschedule_job(job_id, trigger='date', run_date=new_time)

    def _find_better_time(self, current_time: datetime) -> datetime:
        """Find a better time for scheduling based on performance data."""
        # Get optimal times
        optimal_times = self.optimization_rules["linkedin_optimal_times"]

        # Find the next optimal time that's different from current
        for opt_time in optimal_times:
            opt_datetime = current_time.replace(
                hour=opt_time["hour"],
                minute=opt_time["minute"],
                second=0,
                microsecond=0
            )

            # Make sure it's not the same as current time
            if opt_datetime.time() != current_time.time() and opt_datetime > datetime.now():
                return opt_datetime

        # If no better time found, advance by 1 hour
        return current_time + timedelta(hours=1)

    def pause_resume_cycles(self, business_cycle: str, action: str = "pause"):
        """Pause or resume entire business cycles.

        Args:
            business_cycle: Name of the business cycle
            action: 'pause' or 'resume'
        """
        jobs = self.get_scheduled_jobs()

        for job in jobs:
            if business_cycle in job['id']:
                if action == "pause":
                    self.pause_job(job['id'])
                elif action == "resume":
                    self.resume_job(job['id'])

    def resolve_conflicts(self, job_ids: List[str]) -> List[Dict[str, Any]]:
        """Resolve scheduling conflicts between jobs.

        Args:
            job_ids: List of job IDs to check for conflicts

        Returns:
            List of conflict resolution results
        """
        return self.conflict_resolver.resolve_conflicts(job_ids, self.scheduler)


class ConflictResolver:
    """Handles resolution of scheduling conflicts."""

    def __init__(self):
        """Initialize the conflict resolver."""
        self.resolution_strategies = {
            "time_shift": self._resolve_by_time_shift,
            "priority_based": self._resolve_by_priority,
            "frequency_adjustment": self._resolve_by_frequency_adjustment
        }

    def resolve_conflicts(self, job_ids: List[str], scheduler) -> List[Dict[str, Any]]:
        """Resolve conflicts between scheduled jobs.

        Args:
            job_ids: List of job IDs to check
            scheduler: Scheduler instance

        Returns:
            List of resolution results
        """
        conflicts = self._detect_conflicts(job_ids, scheduler)
        results = []

        for conflict in conflicts:
            # Apply resolution strategy
            resolution = self._apply_resolution_strategy(conflict, scheduler)
            results.append(resolution)

        return results

    def _detect_conflicts(self, job_ids: List[str], scheduler) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts."""
        conflicts = []
        jobs = [scheduler.get_job(job_id) for job_id in job_ids if scheduler.get_job(job_id)]

        # Group jobs by execution time
        time_groups = {}
        for job in jobs:
            if job.next_run_time:
                time_key = job.next_run_time.strftime("%Y-%m-%d %H:%M")
                if time_key not in time_groups:
                    time_groups[time_key] = []
                time_groups[time_key].append(job)

        # Find groups with more than one job (conflicts)
        for time_key, job_group in time_groups.items():
            if len(job_group) > 1:
                conflicts.append({
                    'time': time_key,
                    'jobs': [job.id for job in job_group],
                    'count': len(job_group)
                })

        return conflicts

    def _apply_resolution_strategy(self, conflict: Dict[str, Any], scheduler) -> Dict[str, Any]:
        """Apply a resolution strategy to a conflict."""
        # For simplicity, use time shift strategy
        # In a real system, you might evaluate multiple strategies

        jobs = [scheduler.get_job(job_id) for job_id in conflict['jobs']]

        # Shift subsequent jobs by 15 minutes
        for i, job in enumerate(jobs[1:], 1):  # Skip first job
            new_time = job.next_run_time + timedelta(minutes=i*15)
            scheduler.reschedule_job(job.id, trigger='date', run_date=new_time)

        return {
            'conflict': conflict,
            'resolution': 'time_shift',
            'status': 'resolved',
            'adjusted_jobs': [job.id for job in jobs[1:]]
        }

    def _resolve_by_time_shift(self, conflict: Dict[str, Any], scheduler) -> Dict[str, Any]:
        """Resolve conflict by shifting times."""
        return self._apply_resolution_strategy(conflict, scheduler)

    def _resolve_by_priority(self, conflict: Dict[str, Any], scheduler) -> Dict[str, Any]:
        """Resolve conflict based on job priorities."""
        # Placeholder implementation
        return {
            'conflict': conflict,
            'resolution': 'priority_based',
            'status': 'not_implemented'
        }

    def _resolve_by_frequency_adjustment(self, conflict: Dict[str, Any], scheduler) -> Dict[str, Any]:
        """Resolve conflict by adjusting frequency."""
        # Placeholder implementation
        return {
            'conflict': conflict,
            'resolution': 'frequency_adjustment',
            'status': 'not_implemented'
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_scheduler():
        # Create the business scheduler
        scheduler = BusinessScheduleManager()
        scheduler.start()

        print("Testing Business Schedule Manager...")

        # Schedule a LinkedIn post
        post_job_id = scheduler.schedule_linkedin_post(
            content="Exciting business insights from our latest project!",
            optimize=True,
            tags=["business", "insights", "growth"]
        )
        print(f"Scheduled LinkedIn post: {post_job_id}")

        # Schedule a follow-up sequence
        followup_job_ids = scheduler.schedule_followup_sequence(
            sequence_type="business_inquiry",
            recipient="client@example.com"
        )
        print(f"Scheduled follow-up sequence: {followup_job_ids}")

        # Schedule a recurring activity
        recurring_job_id = scheduler.schedule_recurring_business_activity(
            activity_type="weekly_report",
            interval="weekly"
        )
        print(f"Scheduled recurring activity: {recurring_job_id}")

        # Get schedule statistics
        stats = scheduler.get_schedule_statistics()
        print(f"\nSchedule Statistics: {stats}")

        # Test dynamic scheduler
        print("\nTesting Dynamic Scheduler...")
        dynamic_scheduler = DynamicScheduler()
        dynamic_scheduler.start()

        # Get optimization suggestions
        optimization = dynamic_scheduler.optimize_schedule_for_engagement("linkedin")
        print(f"Optimization suggestions: {optimization}")

        # Stop schedulers
        scheduler.stop()
        dynamic_scheduler.stop()

    # Run the test
    asyncio.run(test_scheduler())