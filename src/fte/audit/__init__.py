"""Audit logging system for FTE Gold Tier."""

from .audit_logger import (
    AuditLogger,
    AuditEventType,
    AuditSeverity,
    get_audit_logger
)

__all__ = [
    'AuditLogger',
    'AuditEventType',
    'AuditSeverity',
    'get_audit_logger'
]
