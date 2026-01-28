"""
AAS-271: Plugin Sandboxing

Provides isolated execution environments for plugins with resource limits,
capability restrictions, and security boundaries.
"""

from dataclasses import dataclass, field
from typing import Set, Optional, Dict, Any
from enum import Enum


class Capability(Enum):
    """Plugin capabilities that can be restricted"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK = "network"
    SUBPROCESS = "subprocess"
    SYSTEM_INFO = "system_info"
    MEMORY_ACCESS = "memory_access"


@dataclass
class ResourceLimits:
    """Resource limits for sandboxed plugin"""
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_threads: int = 4
    timeout_seconds: int = 30
    max_file_handles: int = 10


@dataclass
class SandboxPolicy:
    """Sandbox policy for a plugin"""
    plugin_id: str
    allowed_capabilities: Set[Capability] = field(default_factory=set)
    allowed_paths: Set[str] = field(default_factory=set)
    allowed_hosts: Set[str] = field(default_factory=set)
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    restricted_modules: Set[str] = field(default_factory=set)


class PluginSandbox:
    """Manages plugin execution in isolated environment"""
    
    def __init__(self, policy: SandboxPolicy):
        self.policy = policy
        self.violations: list[str] = []
    
    def validate_capability(self, capability: Capability) -> bool:
        """Check if plugin is allowed to use capability"""
        if capability not in self.policy.allowed_capabilities:
            self.violations.append(f"Capability {capability.value} not allowed")
            return False
        return True
    
    def validate_file_access(self, path: str, access_type: str) -> bool:
        """Validate file system access"""
        capability = Capability.FILE_READ if access_type == "read" else Capability.FILE_WRITE
        
        if not self.validate_capability(capability):
            return False
        
        if self.policy.allowed_paths and path not in self.policy.allowed_paths:
            self.violations.append(f"Access to {path} not allowed")
            return False
        
        return True
    
    def validate_network_access(self, host: str) -> bool:
        """Validate network access"""
        if not self.validate_capability(Capability.NETWORK):
            return False
        
        if self.policy.allowed_hosts and host not in self.policy.allowed_hosts:
            self.violations.append(f"Access to {host} not allowed")
            return False
        
        return True
    
    def validate_import(self, module_name: str) -> bool:
        """Validate module imports"""
        if module_name in self.policy.restricted_modules:
            self.violations.append(f"Import of {module_name} blocked by sandbox")
            return False
        return True
    
    def get_enforced_limits(self) -> Dict[str, Any]:
        """Get active resource limits for this sandbox"""
        limits = self.policy.resource_limits
        return {
            "max_memory_mb": limits.max_memory_mb,
            "max_cpu_percent": limits.max_cpu_percent,
            "max_threads": limits.max_threads,
            "timeout_seconds": limits.timeout_seconds,
            "max_file_handles": limits.max_file_handles,
        }
    
    def has_violations(self) -> bool:
        """Check if any violations were recorded"""
        return len(self.violations) > 0


class SandboxManager:
    """Manages sandbox policies for all plugins"""
    
    def __init__(self):
        self.policies: Dict[str, SandboxPolicy] = {}
    
    def register_policy(self, policy: SandboxPolicy):
        """Register sandbox policy for plugin"""
        self.policies[policy.plugin_id] = policy
    
    def create_sandbox(self, plugin_id: str) -> Optional[PluginSandbox]:
        """Create isolated sandbox for plugin"""
        policy = self.policies.get(plugin_id)
        if policy is None:
            return None
        return PluginSandbox(policy)
    
    def enforce(self, plugin_id: str) -> PluginSandbox:
        """Get or create enforced sandbox for plugin"""
        sandbox = self.create_sandbox(plugin_id)
        if sandbox is None:
            # Default restrictive policy
            policy = SandboxPolicy(plugin_id=plugin_id)
            sandbox = PluginSandbox(policy)
        return sandbox


# Export public API
__all__ = ['Capability', 'ResourceLimits', 'SandboxPolicy', 'PluginSandbox', 'SandboxManager']
