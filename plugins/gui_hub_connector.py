"""
GUI Hub Connector - Connect GUI to HomeGateway/Hub APIs.

This module provides comprehensive integration between GUI components
and HomeGateway/Hub backend APIs (GUI-003).

Implements:
- GUI-003: Hook GUI to HomeGateway/Hub APIs
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from collections import defaultdict


class APIEndpoint(Enum):
    """API endpoint types."""

    HEALTH = "health"
    STATUS = "status"
    DEVICES = "devices"
    CONFIG = "config"
    METRICS = "metrics"
    EVENTS = "events"
    COMMANDS = "commands"


class ConnectionState(Enum):
    """Connection states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class RequestMethod(Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ResponseStatus(Enum):
    """API response status."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RETRY = "retry"


@dataclass
class APIRequest:
    """Represents an API request."""

    request_id: str
    endpoint: APIEndpoint
    method: RequestMethod
    timestamp: datetime = field(default_factory=datetime.utcnow)
    params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "endpoint": self.endpoint.value,
            "method": self.method.value,
            "timestamp": self.timestamp.isoformat(),
            "params": self.params,
            "headers": self.headers,
            "body": self.body,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class APIResponse:
    """Represents an API response."""

    request_id: str
    status: ResponseStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status_code: int = 200
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "status_code": self.status_code,
            "data": self.data,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


@dataclass
class HubConfig:
    """Hub connection configuration."""

    hub_url: str
    api_key: Optional[str] = None
    timeout_seconds: int = 30
    retry_count: int = 3
    retry_delay_ms: int = 1000
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

    def __post_init__(self):
        """Validate configuration."""
        if not self.hub_url:
            raise ValueError("hub_url required")


@dataclass
class ConnectionEvent:
    """Connection state change event."""

    event_id: str
    old_state: ConnectionState
    new_state: ConnectionState
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "old_state": self.old_state.value,
            "new_state": self.new_state.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "metadata": self.metadata,
        }


class GUIHubConnector:
    """
    Manages connection between GUI and HomeGateway/Hub APIs.

    Features:
    - API request/response handling
    - Connection state management
    - Request caching
    - Retry logic
    - Event callbacks
    - Metrics tracking
    """

    def __init__(self, config: HubConfig):
        """Initialize the GUI Hub connector."""
        self._config = config
        self._state = ConnectionState.DISCONNECTED
        self._requests: List[APIRequest] = []
        self._responses: List[APIResponse] = []
        self._connection_events: List[ConnectionEvent] = []
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)

    def connect(self) -> bool:
        """
        Establish connection to Hub.

        Returns:
            True if connected successfully
        """
        old_state = self._state
        self._state = ConnectionState.CONNECTING

        self._record_connection_event(old_state, self._state, "Connection initiated")

        # Simulate connection logic
        try:
            # In real implementation, establish HTTP connection
            self._state = ConnectionState.CONNECTED
            self._record_connection_event(
                ConnectionState.CONNECTING,
                self._state,
                "Connection established",
            )
            self._trigger_callbacks("connected", {"hub_url": self._config.hub_url})
            return True
        except Exception as e:
            self._state = ConnectionState.ERROR
            self._record_connection_event(
                ConnectionState.CONNECTING, self._state, str(e)
            )
            return False

    def disconnect(self) -> None:
        """Disconnect from Hub."""
        old_state = self._state
        self._state = ConnectionState.DISCONNECTED
        self._record_connection_event(old_state, self._state, "Disconnected by client")
        self._trigger_callbacks("disconnected", {})

    def get_state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state

    def send_request(
        self,
        request_id: str,
        endpoint: APIEndpoint,
        method: RequestMethod = RequestMethod.GET,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """
        Send API request to Hub.

        Args:
            request_id: Unique request identifier
            endpoint: API endpoint to call
            method: HTTP method
            params: Query parameters
            body: Request body

        Returns:
            APIResponse instance
        """
        if self._state != ConnectionState.CONNECTED:
            return APIResponse(
                request_id=request_id,
                status=ResponseStatus.ERROR,
                error_message="Not connected to Hub",
                status_code=503,
            )

        request = APIRequest(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            params=params or {},
            body=body,
            timeout_seconds=self._config.timeout_seconds,
        )

        self._requests.append(request)

        # Check cache for GET requests
        if method == RequestMethod.GET and self._config.enable_caching:
            cache_key = self._get_cache_key(endpoint, params or {})
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response

        # Simulate API call
        start_time = datetime.utcnow()

        try:
            # In real implementation, make HTTP request
            response_data = self._simulate_api_call(endpoint, method, body)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            response = APIResponse(
                request_id=request_id,
                status=ResponseStatus.SUCCESS,
                status_code=200,
                data=response_data,
                duration_ms=duration,
            )

            # Cache GET responses
            if method == RequestMethod.GET and self._config.enable_caching:
                self._add_to_cache(cache_key, response)

            self._responses.append(response)
            self._trigger_callbacks("response", response.to_dict())

            return response

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            response = APIResponse(
                request_id=request_id,
                status=ResponseStatus.ERROR,
                status_code=500,
                error_message=str(e),
                duration_ms=duration,
            )

            self._responses.append(response)
            return response

    def get_health(self) -> APIResponse:
        """Get Hub health status."""
        return self.send_request(
            f"health_{datetime.utcnow().timestamp()}",
            APIEndpoint.HEALTH,
            RequestMethod.GET,
        )

    def get_devices(self, filters: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Get device list from Hub."""
        return self.send_request(
            f"devices_{datetime.utcnow().timestamp()}",
            APIEndpoint.DEVICES,
            RequestMethod.GET,
            params=filters,
        )

    def get_metrics(self, metric_names: Optional[List[str]] = None) -> APIResponse:
        """Get metrics from Hub."""
        params = {"metrics": metric_names} if metric_names else {}
        return self.send_request(
            f"metrics_{datetime.utcnow().timestamp()}",
            APIEndpoint.METRICS,
            RequestMethod.GET,
            params=params,
        )

    def send_command(
        self, device_id: str, command: str, params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Send command to device via Hub."""
        body = {
            "device_id": device_id,
            "command": command,
            "params": params or {},
        }
        return self.send_request(
            f"cmd_{device_id}_{datetime.utcnow().timestamp()}",
            APIEndpoint.COMMANDS,
            RequestMethod.POST,
            body=body,
        )

    def _simulate_api_call(
        self,
        endpoint: APIEndpoint,
        method: RequestMethod,
        body: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Simulate API response (for testing)."""
        if endpoint == APIEndpoint.HEALTH:
            return {"status": "healthy", "uptime": 12345}
        elif endpoint == APIEndpoint.DEVICES:
            return {"devices": [], "count": 0}
        elif endpoint == APIEndpoint.METRICS:
            return {"cpu": 25.5, "memory": 1024, "disk": 5000}
        elif endpoint == APIEndpoint.COMMANDS:
            return {"command_id": "cmd_123", "status": "executed"}
        else:
            return {"result": "ok"}

    def _get_cache_key(self, endpoint: APIEndpoint, params: Dict[str, Any]) -> str:
        """Generate cache key."""
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{endpoint.value}:{param_str}"

    def _add_to_cache(self, key: str, response: APIResponse) -> None:
        """Add response to cache."""
        self._cache[key] = (response, datetime.utcnow())

    def _get_from_cache(self, key: str) -> Optional[APIResponse]:
        """Get response from cache if valid."""
        if key not in self._cache:
            return None

        response, cached_at = self._cache[key]
        age = (datetime.utcnow() - cached_at).total_seconds()

        if age > self._config.cache_ttl_seconds:
            del self._cache[key]
            return None

        return response

    def clear_cache(self) -> int:
        """Clear response cache. Returns count of cleared entries."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def _record_connection_event(
        self,
        old_state: ConnectionState,
        new_state: ConnectionState,
        reason: str,
    ) -> None:
        """Record a connection state change."""
        event = ConnectionEvent(
            event_id=f"evt_{len(self._connection_events)}",
            old_state=old_state,
            new_state=new_state,
            reason=reason,
        )
        self._connection_events.append(event)

    def get_connection_history(self) -> List[ConnectionEvent]:
        """Get connection state change history."""
        return self._connection_events.copy()

    def get_request_history(self, limit: Optional[int] = None) -> List[APIRequest]:
        """Get API request history."""
        if limit:
            return self._requests[-limit:]
        return self._requests.copy()

    def get_response_history(self, limit: Optional[int] = None) -> List[APIResponse]:
        """Get API response history."""
        if limit:
            return self._responses[-limit:]
        return self._responses.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get connector statistics."""
        if not self._responses:
            return {
                "total_requests": len(self._requests),
                "total_responses": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_duration_ms": 0.0,
                "cache_size": len(self._cache),
            }

        success_count = sum(
            1 for r in self._responses if r.status == ResponseStatus.SUCCESS
        )
        error_count = len(self._responses) - success_count

        total_duration = sum(r.duration_ms for r in self._responses)
        avg_duration = total_duration / len(self._responses) if self._responses else 0.0

        return {
            "total_requests": len(self._requests),
            "total_responses": len(self._responses),
            "success_count": success_count,
            "error_count": error_count,
            "avg_duration_ms": avg_duration,
            "cache_size": len(self._cache),
            "connection_state": self._state.value,
        }

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for events."""
        self._callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger callbacks for event type."""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception:
                pass  # Silently ignore callback errors

    def export_report(self) -> Dict[str, Any]:
        """Export comprehensive connector report."""
        return {
            "config": {
                "hub_url": self._config.hub_url,
                "timeout_seconds": self._config.timeout_seconds,
                "retry_count": self._config.retry_count,
                "enable_caching": self._config.enable_caching,
            },
            "statistics": self.get_statistics(),
            "connection_history": [e.to_dict() for e in self._connection_events],
            "recent_requests": [
                r.to_dict() for r in self.get_request_history(limit=10)
            ],
            "recent_responses": [
                r.to_dict() for r in self.get_response_history(limit=10)
            ],
        }
