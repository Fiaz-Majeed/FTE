"""
Comprehensive Audit Logging System for Gold Tier
Tracks all actions, decisions, API calls, approvals, and system events
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum
import threading


class AuditEventType(Enum):
    """Types of audit events."""
    ACTION = "action"
    DECISION = "decision"
    API_CALL = "api_call"
    APPROVAL = "approval"
    ERROR = "error"
    SYSTEM = "system"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    ACCOUNTING = "accounting"
    AUTONOMOUS_TASK = "autonomous_task"


class AuditSeverity(Enum):
    """Severity levels for audit events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogger:
    """Centralized audit logging system with SQLite backend."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[Path] = None):
        """Singleton pattern for audit logger."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize audit logger.

        Args:
            db_path: Path to SQLite database file
        """
        if hasattr(self, '_initialized'):
            return

        if db_path is None:
            db_path = Path(__file__).parent.parent.parent.parent / "audit_logs.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._initialized = True

    def _init_database(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                actor TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                status TEXT,
                details TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_actor ON audit_events(actor)
        """)

        conn.commit()
        conn.close()

    def log(
        self,
        event_type: AuditEventType,
        action: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        actor: Optional[str] = None,
        resource: Optional[str] = None,
        status: str = "success",
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log an audit event.

        Args:
            event_type: Type of event
            action: Action performed
            severity: Severity level
            actor: Who performed the action
            resource: Resource affected
            status: Status of action (success, failure, pending)
            details: Additional details
            metadata: Additional structured data

        Returns:
            Event ID
        """
        timestamp = datetime.utcnow().isoformat()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_events
            (timestamp, event_type, severity, actor, action, resource, status, details, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            event_type.value,
            severity.value,
            actor,
            action,
            resource,
            status,
            details,
            json.dumps(metadata) if metadata else None
        ))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id

    def log_action(self, action: str, actor: str, resource: Optional[str] = None,
                   status: str = "success", **kwargs):
        """Log a general action."""
        return self.log(
            AuditEventType.ACTION,
            action,
            actor=actor,
            resource=resource,
            status=status,
            metadata=kwargs
        )

    def log_api_call(self, service: str, endpoint: str, method: str,
                     status_code: int, actor: str, **kwargs):
        """Log an API call."""
        return self.log(
            AuditEventType.API_CALL,
            f"{method} {endpoint}",
            actor=actor,
            resource=service,
            status="success" if 200 <= status_code < 300 else "failure",
            severity=AuditSeverity.WARNING if status_code >= 400 else AuditSeverity.INFO,
            metadata={"status_code": status_code, **kwargs}
        )

    def log_approval(self, approval_id: str, action: str, approver: str,
                     decision: str, **kwargs):
        """Log an approval decision."""
        return self.log(
            AuditEventType.APPROVAL,
            action,
            actor=approver,
            resource=approval_id,
            status=decision,
            metadata=kwargs
        )

    def log_error(self, error: str, actor: Optional[str] = None,
                  resource: Optional[str] = None, **kwargs):
        """Log an error event."""
        return self.log(
            AuditEventType.ERROR,
            "error_occurred",
            severity=AuditSeverity.ERROR,
            actor=actor,
            resource=resource,
            status="failure",
            details=error,
            metadata=kwargs
        )

    def log_social_post(self, platform: str, post_id: str, actor: str,
                        content_preview: str, **kwargs):
        """Log a social media post."""
        return self.log(
            AuditEventType.SOCIAL_POST,
            f"post_to_{platform}",
            actor=actor,
            resource=post_id,
            details=content_preview[:200],
            metadata=kwargs
        )

    def log_accounting(self, operation: str, actor: str, amount: Optional[float] = None,
                       account: Optional[str] = None, **kwargs):
        """Log an accounting operation."""
        metadata = kwargs.copy()
        if amount is not None:
            metadata['amount'] = amount
        if account is not None:
            metadata['account'] = account

        return self.log(
            AuditEventType.ACCOUNTING,
            operation,
            actor=actor,
            resource=account,
            metadata=metadata
        )

    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        actor: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit events.

        Args:
            event_type: Filter by event type
            actor: Filter by actor
            start_date: Filter by start date
            end_date: Filter by end date
            severity: Filter by severity
            limit: Maximum number of results

        Returns:
            List of audit events
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)

        if actor:
            query += " AND actor = ?"
            params.append(actor)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        if severity:
            query += " AND severity = ?"
            params.append(severity.value)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        events = []
        for row in rows:
            event = dict(row)
            if event['metadata']:
                event['metadata'] = json.loads(event['metadata'])
            events.append(event)

        conn.close()
        return events

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get audit statistics for the last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)

        # Total events
        cursor.execute("""
            SELECT COUNT(*) FROM audit_events
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        total_events = cursor.fetchone()[0]

        # Events by type
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM audit_events
            WHERE timestamp >= ?
            GROUP BY event_type
        """, (start_date.isoformat(),))
        events_by_type = dict(cursor.fetchall())

        # Events by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM audit_events
            WHERE timestamp >= ?
            GROUP BY severity
        """, (start_date.isoformat(),))
        events_by_severity = dict(cursor.fetchall())

        # Top actors
        cursor.execute("""
            SELECT actor, COUNT(*) as count
            FROM audit_events
            WHERE timestamp >= ? AND actor IS NOT NULL
            GROUP BY actor
            ORDER BY count DESC
            LIMIT 10
        """, (start_date.isoformat(),))
        top_actors = dict(cursor.fetchall())

        # Error rate
        cursor.execute("""
            SELECT
                SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failures,
                COUNT(*) as total
            FROM audit_events
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        failures, total = cursor.fetchone()
        error_rate = (failures / total * 100) if total > 0 else 0

        conn.close()

        return {
            "period_days": days,
            "total_events": total_events,
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "top_actors": top_actors,
            "error_rate": round(error_rate, 2),
            "failures": failures
        }

    def cleanup_old_logs(self, retention_days: int = 90):
        """Remove audit logs older than retention period.

        Args:
            retention_days: Number of days to retain logs
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - retention_days)

        cursor.execute("""
            DELETE FROM audit_events
            WHERE timestamp < ?
        """, (cutoff_date.isoformat(),))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
