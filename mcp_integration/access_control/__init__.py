"""
Módulo de inicialización para control de acceso
"""

from .access_manager import (
    AccessControlManager, 
    User, 
    UserRole, 
    Permission, 
    AuditLogEntry,
    access_control,
    require_permission,
    require_role
)

from .auth_middleware import (
    auth_required,
    admin_required,
    permission_required,
    get_current_user
)

__all__ = [
    'AccessControlManager',
    'User',
    'UserRole', 
    'Permission',
    'AuditLogEntry',
    'access_control',
    'require_permission',
    'require_role',
    'auth_required',
    'admin_required', 
    'permission_required',
    'get_current_user'
]

