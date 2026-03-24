"""
Error Recovery and Graceful Degradation System
Implements retry mechanisms, circuit breakers, and fallback strategies
"""
import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type
import logging

from ..audit.audit_logger import get_audit_logger, AuditEventType, AuditSeverity


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """Initialize circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to catch
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self.audit_logger = get_audit_logger()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit breaker {self.name} recovered to CLOSED state")
            self.audit_logger.log(
                AuditEventType.SYSTEM,
                f"circuit_breaker_recovered",
                actor="system",
                resource=self.name,
                severity=AuditSeverity.INFO
            )

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker {self.name} opened after {self.failure_count} failures")
            self.audit_logger.log(
                AuditEventType.SYSTEM,
                f"circuit_breaker_opened",
                actor="system",
                resource=self.name,
                severity=AuditSeverity.ERROR,
                metadata={"failure_count": self.failure_count}
            )


class RetryStrategy:
    """Retry strategy with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """Initialize retry strategy.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())

        return delay


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for automatic retry with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            strategy = RetryStrategy(max_attempts=max_attempts, initial_delay=initial_delay)
            audit_logger = get_audit_logger()

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        audit_logger.log_error(
                            f"Function {func.__name__} failed after {max_attempts} attempts",
                            actor="system",
                            resource=func.__name__,
                            exception=str(e)
                        )
                        raise

                    delay = strategy.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}. "
                        f"Retrying in {delay:.2f}s. Error: {e}"
                    )
                    time.sleep(delay)

        return wrapper
    return decorator


def with_retry_async(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Async decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            strategy = RetryStrategy(max_attempts=max_attempts, initial_delay=initial_delay)
            audit_logger = get_audit_logger()

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        audit_logger.log_error(
                            f"Async function {func.__name__} failed after {max_attempts} attempts",
                            actor="system",
                            resource=func.__name__,
                            exception=str(e)
                        )
                        raise

                    delay = strategy.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}. "
                        f"Retrying in {delay:.2f}s. Error: {e}"
                    )
                    await asyncio.sleep(delay)

        return wrapper
    return decorator


class HealthCheck:
    """Health check system for monitoring service availability."""

    def __init__(self):
        """Initialize health check system."""
        self.services: Dict[str, Dict[str, Any]] = {}
        self.audit_logger = get_audit_logger()

    def register_service(
        self,
        name: str,
        check_func: Callable,
        interval: int = 60,
        timeout: int = 10
    ):
        """Register a service for health checking.

        Args:
            name: Service name
            check_func: Function that returns True if healthy
            interval: Check interval in seconds
            timeout: Check timeout in seconds
        """
        self.services[name] = {
            "check_func": check_func,
            "interval": interval,
            "timeout": timeout,
            "last_check": None,
            "status": "unknown",
            "consecutive_failures": 0
        }

    def check_service(self, name: str) -> bool:
        """Check health of a specific service.

        Args:
            name: Service name

        Returns:
            True if healthy, False otherwise
        """
        if name not in self.services:
            return False

        service = self.services[name]

        try:
            is_healthy = service["check_func"]()
            service["status"] = "healthy" if is_healthy else "unhealthy"
            service["last_check"] = datetime.now()

            if is_healthy:
                service["consecutive_failures"] = 0
            else:
                service["consecutive_failures"] += 1

            if service["consecutive_failures"] >= 3:
                self.audit_logger.log(
                    AuditEventType.SYSTEM,
                    f"service_unhealthy",
                    actor="health_check",
                    resource=name,
                    severity=AuditSeverity.ERROR,
                    metadata={"consecutive_failures": service["consecutive_failures"]}
                )

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            service["status"] = "error"
            service["consecutive_failures"] += 1
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get overall health status.

        Returns:
            Dictionary with health status of all services
        """
        return {
            name: {
                "status": service["status"],
                "last_check": service["last_check"].isoformat() if service["last_check"] else None,
                "consecutive_failures": service["consecutive_failures"]
            }
            for name, service in self.services.items()
        }


class FallbackStrategy:
    """Fallback strategy for graceful degradation."""

    def __init__(self, name: str):
        """Initialize fallback strategy.

        Args:
            name: Strategy name
        """
        self.name = name
        self.fallbacks: List[Callable] = []
        self.audit_logger = get_audit_logger()

    def add_fallback(self, func: Callable):
        """Add a fallback function.

        Args:
            func: Fallback function to try
        """
        self.fallbacks.append(func)

    def execute(self, *args, **kwargs) -> Any:
        """Execute with fallback chain.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from first successful fallback

        Raises:
            Exception if all fallbacks fail
        """
        errors = []

        for i, fallback in enumerate(self.fallbacks):
            try:
                result = fallback(*args, **kwargs)

                if i > 0:
                    self.audit_logger.log(
                        AuditEventType.SYSTEM,
                        f"fallback_used",
                        actor="system",
                        resource=self.name,
                        severity=AuditSeverity.WARNING,
                        metadata={"fallback_index": i}
                    )

                return result

            except Exception as e:
                logger.warning(f"Fallback {i} failed for {self.name}: {e}")
                errors.append(str(e))

        # All fallbacks failed
        self.audit_logger.log_error(
            f"All fallbacks failed for {self.name}",
            actor="system",
            resource=self.name,
            errors=errors
        )
        raise Exception(f"All fallbacks failed for {self.name}: {errors}")


# Global instances
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_health_check = HealthCheck()


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker.

    Args:
        name: Circuit breaker name
        **kwargs: CircuitBreaker initialization arguments

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, **kwargs)
    return _circuit_breakers[name]


def get_health_check() -> HealthCheck:
    """Get the global health check instance."""
    return _health_check
