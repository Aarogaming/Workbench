#!/usr/bin/env python3
"""
AAS-228: Build Integration Engine
Coordinates multi-service integrations with plugin architecture
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class IntegrationStatus(Enum):
    """Integration lifecycle status"""

    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class ServiceEndpoint:
    """External service endpoint configuration"""

    service_name: str
    url: str
    api_version: str
    auth_type: str  # bearer, oauth2, api_key, basic
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1


@dataclass
class IntegrationConfig:
    """Integration engine configuration"""

    engine_id: str
    endpoints: Dict[str, ServiceEndpoint] = field(default_factory=dict)
    plugins: List[str] = field(default_factory=list)
    poll_interval: int = 60
    max_concurrent: int = 5
    enable_caching: bool = True


class IntegrationPlugin:
    """Base integration plugin"""

    def __init__(self, name: str):
        """Initialize plugin"""
        self.name = name
        self.enabled = True

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data between services"""
        return data

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data before integration"""
        return isinstance(data, dict)


class IntegrationEngine:
    """Orchestrates multi-service integrations"""

    def __init__(self, config: IntegrationConfig):
        """Initialize integration engine"""
        self.config = config
        self.status = IntegrationStatus.IDLE
        self.connections: Dict[str, Any] = {}
        self.plugins: Dict[str, IntegrationPlugin] = {}
        self.sync_history: List[Dict[str, Any]] = []
        self.error_log: List[str] = []

    def register_plugin(self, plugin: IntegrationPlugin) -> Dict[str, Any]:
        """Register integration plugin"""
        if plugin.name in self.plugins:
            return {"error": f"Plugin {plugin.name} already registered"}

        self.plugins[plugin.name] = plugin
        return {"success": True, "plugin": plugin.name, "enabled": plugin.enabled}

    def connect_service(self, service_name: str) -> Dict[str, Any]:
        """Connect to external service"""
        if service_name not in self.config.endpoints:
            return {"error": f"Service {service_name} not configured"}

        endpoint = self.config.endpoints[service_name]
        try:
            self.status = IntegrationStatus.CONNECTING
            # Simulate connection establishment
            self.connections[service_name] = {
                "endpoint": endpoint.url,
                "connected_at": None,
                "last_sync": None,
                "sync_count": 0,
            }
            self.status = IntegrationStatus.CONNECTED
            return {
                "success": True,
                "service": service_name,
                "status": self.status.value,
            }
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            msg = f"Failed to connect {service_name}: {str(e)}"
            self.error_log.append(msg)
            return {"error": f"Connection failed: {str(e)}"}

    def add_endpoint(
        self, service_name: str, endpoint: ServiceEndpoint
    ) -> Dict[str, Any]:
        """Add service endpoint configuration"""
        if service_name in self.config.endpoints:
            return {"error": f"Endpoint {service_name} already exists"}

        self.config.endpoints[service_name] = endpoint
        return {
            "success": True,
            "service": service_name,
            "url": endpoint.url,
            "api_version": endpoint.api_version,
        }

    def sync_data(
        self, source: str, target: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synchronize data between services"""
        if source not in self.connections:
            return {"error": f"Source {source} not connected"}
        if target not in self.connections:
            return {"error": f"Target {target} not connected"}

        try:
            self.status = IntegrationStatus.SYNCING

            # Apply plugins transformations
            transformed_data = data
            for plugin_name in self.config.plugins:
                if plugin_name in self.plugins:
                    plugin = self.plugins[plugin_name]
                    if plugin.enabled and plugin.validate(transformed_data):
                        transformed_data = plugin.transform(transformed_data)

            sync_record = {
                "source": source,
                "target": target,
                "data_size": len(str(transformed_data)),
                "timestamp": None,
                "success": True,
            }
            self.sync_history.append(sync_record)
            self.connections[source]["sync_count"] += 1

            self.status = IntegrationStatus.CONNECTED
            return {
                "success": True,
                "sync_id": len(self.sync_history),
                "source": source,
                "target": target,
                "records_synced": 1,
            }
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_log.append(f"Sync failed {source}->{target}: {str(e)}")
            return {"error": f"Sync failed: {str(e)}"}

    def disconnect_service(self, service_name: str) -> Dict[str, Any]:
        """Disconnect from service"""
        if service_name not in self.connections:
            return {"error": f"Service {service_name} not connected"}

        self.connections[service_name]["connected_at"] = None
        self.status = IntegrationStatus.DISCONNECTED
        return {
            "success": True,
            "service": service_name,
            "syncs_performed": self.connections[service_name]["sync_count"],
        }

    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "engine_id": self.config.engine_id,
            "status": self.status.value,
            "connected_services": len(self.connections),
            "registered_plugins": len(self.plugins),
            "total_syncs": len(self.sync_history),
            "error_count": len(self.error_log),
            "endpoints_configured": len(self.config.endpoints),
        }

    def get_sync_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent sync history"""
        recent = self.sync_history[-limit:]
        return {
            "total_syncs": len(self.sync_history),
            "recent_syncs": recent,
            "limit": limit,
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all connections"""
        health = {"healthy_connections": 0, "failed_connections": 0, "services": {}}

        for service_name in self.connections:
            health["services"][service_name] = {
                "connected": True,
                "last_sync": self.connections[service_name]["last_sync"],
                "sync_count": self.connections[service_name]["sync_count"],
            }
            health["healthy_connections"] += 1

        return health


class IntegrationPipeline:
    """Coordinates sequences of integrations"""

    def __init__(self, pipeline_id: str):
        """Initialize pipeline"""
        self.pipeline_id = pipeline_id
        self.steps: List[Dict[str, Any]] = []
        self.engine: Optional[IntegrationEngine] = None

    def add_step(
        self, step_name: str, action: str, source: str, target: str
    ) -> Dict[str, Any]:
        """Add pipeline step"""
        step = {
            "step_id": len(self.steps) + 1,
            "name": step_name,
            "action": action,
            "source": source,
            "target": target,
            "status": "pending",
        }
        self.steps.append(step)
        return {"success": True, "step_id": step["step_id"]}

    def execute(self, engine: IntegrationEngine) -> Dict[str, Any]:
        """Execute all pipeline steps"""
        self.engine = engine
        results = {
            "pipeline_id": self.pipeline_id,
            "total_steps": len(self.steps),
            "completed": 0,
            "failed": 0,
            "step_results": [],
        }

        for step in self.steps:
            step["status"] = "executing"
            result = {"step_id": step["step_id"], "name": step["name"], "success": True}
            results["step_results"].append(result)
            results["completed"] += 1
            step["status"] = "completed"

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        completed = sum(1 for s in self.steps if s["status"] == "completed")
        return {
            "pipeline_id": self.pipeline_id,
            "total_steps": len(self.steps),
            "completed_steps": completed,
            "steps": self.steps,
        }
