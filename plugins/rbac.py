#!/usr/bin/env python3
"""AAS-332: Role-Based Access Control (RBAC)"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Any, Optional
from enum import Enum


class Permission(Enum):
    """System permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class Role:
    """Role definition"""
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""


@dataclass
class User:
    """User definition"""
    user_id: str
    username: str
    roles: Set[str] = field(default_factory=set)


@dataclass
class Resource:
    """Protected resource"""
    resource_id: str
    name: str
    required_permission: Permission


class RBACManager:
    """Manages role-based access control"""

    def __init__(self):
        """Initialize RBAC manager"""
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.resources: Dict[str, Resource] = {}

    def create_role(self, name: str,
                    permissions: Optional[Set[Permission]] = None,
                    description: str = "") -> Role:
        """Create new role"""
        role = Role(
            name=name,
            permissions=permissions or set(),
            description=description
        )
        self.roles[name] = role
        return role

    def add_permission_to_role(self, role_name: str,
                               permission: Permission) -> bool:
        """Add permission to role"""
        if role_name in self.roles:
            self.roles[role_name].permissions.add(permission)
            return True
        return False

    def remove_permission_from_role(self, role_name: str,
                                    permission: Permission) -> bool:
        """Remove permission from role"""
        if role_name in self.roles:
            self.roles[role_name].permissions.discard(permission)
            return True
        return False

    def create_user(self, user_id: str,
                    username: str) -> User:
        """Create new user"""
        user = User(user_id=user_id, username=username)
        self.users[user_id] = user
        return user

    def assign_role_to_user(self, user_id: str,
                            role_name: str) -> bool:
        """Assign role to user"""
        if user_id in self.users and role_name in self.roles:
            self.users[user_id].roles.add(role_name)
            return True
        return False

    def revoke_role_from_user(self, user_id: str,
                              role_name: str) -> bool:
        """Revoke role from user"""
        if user_id in self.users:
            self.users[user_id].roles.discard(role_name)
            return True
        return False

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        if user_id not in self.users:
            return set()

        user = self.users[user_id]
        permissions = set()

        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                permissions.update(role.permissions)

        return permissions

    def can_access(self, user_id: str,
                   resource_id: str) -> bool:
        """Check if user can access resource"""
        if resource_id not in self.resources:
            return False

        resource = self.resources[resource_id]
        user_perms = self.get_user_permissions(user_id)

        return resource.required_permission in user_perms

    def register_resource(self, resource: Resource) -> None:
        """Register protected resource"""
        self.resources[resource.resource_id] = resource

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get user's roles"""
        if user_id in self.users:
            return list(self.users[user_id].roles)
        return []

    def list_roles(self) -> List[Dict[str, Any]]:
        """List all roles"""
        return [
            {
                'name': role.name,
                'permissions': [p.value for p in role.permissions],
                'description': role.description
            }
            for role in self.roles.values()
        ]

    def audit_access(self, user_id: str) -> Dict[str, Any]:
        """Audit user access"""
        if user_id not in self.users:
            return {'error': 'User not found'}

        user = self.users[user_id]
        permissions = self.get_user_permissions(user_id)
        accessible_resources = [
            rid for rid in self.resources
            if self.can_access(user_id, rid)
        ]

        return {
            'user_id': user_id,
            'username': user.username,
            'roles': list(user.roles),
            'permissions': [p.value for p in permissions],
            'accessible_resources': accessible_resources
        }

    def has_admin(self) -> bool:
        """Check if any admin role exists"""
        for role in self.roles.values():
            if Permission.ADMIN in role.permissions:
                return True
        return False
