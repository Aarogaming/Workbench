"""
AAS-256: Dependency Injection Container
Implements a lightweight DI container with singleton and factory patterns
"""

from typing import Dict, Any, Callable, Type, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import inspect


class LifecycleType(Enum):
    """Service lifecycle patterns"""
    SINGLETON = "singleton"
    FACTORY = "factory"
    TRANSIENT = "transient"


@dataclass
class ServiceDefinition:
    """Service registration metadata"""
    service_type: Type
    factory_func: Callable
    lifecycle: LifecycleType
    dependencies: List[str] = field(default_factory=list)
    instance: Optional[Any] = None


class DIContainer:
    """Lightweight dependency injection container"""

    def __init__(self) -> None:
        """Initialize container"""
        self.services: Dict[str, ServiceDefinition] = {}
        self.singletons: Dict[str, Any] = {}

    def register_singleton(self, name: str, service_type: Type,
                           factory_func: Optional[Callable] = None
                           ) -> Dict[str, Any]:
        """Register singleton service"""
        if name in self.services:
            return {'error': f'Service {name} already registered'}

        factory = factory_func or (lambda: service_type())
        service_def = ServiceDefinition(
            service_type=service_type,
            factory_func=factory,
            lifecycle=LifecycleType.SINGLETON
        )
        self.services[name] = service_def
        return {'success': True, 'service': name, 'lifecycle': 'singleton'}

    def register_factory(self, name: str, service_type: Type,
                         factory_func: Callable) -> Dict[str, Any]:
        """Register factory service (new instance each time)"""
        if name in self.services:
            return {'error': f'Service {name} already registered'}

        service_def = ServiceDefinition(
            service_type=service_type,
            factory_func=factory_func,
            lifecycle=LifecycleType.FACTORY
        )
        self.services[name] = service_def
        return {'success': True, 'service': name, 'lifecycle': 'factory'}

    def register_transient(self, name: str, service_type: Type,
                           factory_func: Optional[Callable] = None
                           ) -> Dict[str, Any]:
        """Register transient service (temporary)"""
        if name in self.services:
            return {'error': f'Service {name} already registered'}

        factory = factory_func or (lambda: service_type())
        service_def = ServiceDefinition(
            service_type=service_type,
            factory_func=factory,
            lifecycle=LifecycleType.TRANSIENT
        )
        self.services[name] = service_def
        return {'success': True, 'service': name, 'lifecycle': 'transient'}

    def resolve(self, name: str) -> Any:
        """Resolve service instance"""
        if name not in self.services:
            raise ValueError(f'Service {name} not registered')

        service_def = self.services[name]

        if service_def.lifecycle == LifecycleType.SINGLETON:
            if name not in self.singletons:
                self.singletons[name] = self._create_instance(service_def)
            return self.singletons[name]

        elif service_def.lifecycle == LifecycleType.FACTORY:
            return self._create_instance(service_def)

        elif service_def.lifecycle == LifecycleType.TRANSIENT:
            instance = self._create_instance(service_def)
            return instance

        raise ValueError(f'Unknown lifecycle: {service_def.lifecycle}')

    def _create_instance(self, service_def: ServiceDefinition) -> Any:
        """Create service instance with dependency resolution"""
        try:
            sig = inspect.signature(service_def.factory_func)
            params = {}

            for param_name, param in sig.parameters.items():
                if param_name in self.services:
                    params[param_name] = self.resolve(param_name)

            return service_def.factory_func(**params)
        except Exception as e:
            raise ValueError(f'Failed to create instance: {str(e)}')

    def list_services(self) -> Dict[str, Any]:
        """List all registered services"""
        services_info = {}
        for name, service_def in self.services.items():
            services_info[name] = {
                'type': service_def.service_type.__name__,
                'lifecycle': service_def.lifecycle.value,
                'cached': name in self.singletons
            }
        return services_info

    def clear_singletons(self) -> Dict[str, Any]:
        """Clear singleton cache"""
        count = len(self.singletons)
        self.singletons.clear()
        return {'success': True, 'cleared': count}

    def get_status(self) -> Dict[str, Any]:
        """Get container status"""
        return {
            'total_services': len(self.services),
            'cached_singletons': len(self.singletons),
            'services': self.list_services()
        }


class DIContainerBuilder:
    """Builder for container configuration"""

    def __init__(self) -> None:
        """Initialize builder"""
        self.container = DIContainer()
        self.registrations: List[Dict[str, Any]] = []

    def add_singleton(self, name: str, service_type: Type,
                      factory_func: Optional[Callable] = None
                      ) -> 'DIContainerBuilder':
        """Add singleton to builder"""
        self.registrations.append({
            'name': name,
            'type': service_type,
            'factory': factory_func,
            'lifecycle': LifecycleType.SINGLETON
        })
        return self

    def add_factory(self, name: str, service_type: Type,
                    factory_func: Callable) -> 'DIContainerBuilder':
        """Add factory to builder"""
        self.registrations.append({
            'name': name,
            'type': service_type,
            'factory': factory_func,
            'lifecycle': LifecycleType.FACTORY
        })
        return self

    def build(self) -> DIContainer:
        """Build container"""
        for reg in self.registrations:
            if reg['lifecycle'] == LifecycleType.SINGLETON:
                self.container.register_singleton(
                    reg['name'], reg['type'], reg['factory']
                )
            elif reg['lifecycle'] == LifecycleType.FACTORY:
                self.container.register_factory(
                    reg['name'], reg['type'], reg['factory']
                )

        return self.container
