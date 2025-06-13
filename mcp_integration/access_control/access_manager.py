"""
Sistema de Control de Acceso y Roles para MCP Synapse
====================================================

Este módulo implementa un sistema robusto de control de acceso basado en roles
que separa claramente las capacidades de usuarios finales y administradores.

Características principales:
- Usuarios finales: Solo pueden ejecutar tareas, selección automática de herramientas
- Administradores: Pueden configurar herramientas, ver métricas, gestionar sistema
- Autenticación y autorización robusta
- Auditoría completa de acciones administrativas
- Gestión de sesiones segura
"""

import asyncio
import logging
import json
import hashlib
import secrets
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Roles de usuario en el sistema"""
    END_USER = "end_user"           # Usuario final - solo ejecución de tareas
    ADMIN = "admin"                 # Administrador - configuración completa
    SUPER_ADMIN = "super_admin"     # Super administrador - gestión de usuarios

class Permission(Enum):
    """Permisos específicos en el sistema"""
    # Permisos de usuario final
    EXECUTE_TASK = "execute_task"
    VIEW_TASK_HISTORY = "view_task_history"
    VIEW_BASIC_STATUS = "view_basic_status"
    
    # Permisos de administrador
    CONFIGURE_TOOLS = "configure_tools"
    VIEW_TOOL_METRICS = "view_tool_metrics"
    MANAGE_TOOL_REGISTRY = "manage_tool_registry"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    VIEW_ADMIN_DASHBOARD = "view_admin_dashboard"
    MODIFY_AI_SETTINGS = "modify_ai_settings"
    
    # Permisos de super administrador
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    SYSTEM_ADMINISTRATION = "system_administration"

@dataclass
class User:
    """Representación de un usuario del sistema"""
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: Set[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    password_hash: Optional[str] = None
    session_token: Optional[str] = None
    session_expires: Optional[datetime] = None

@dataclass
class AuditLogEntry:
    """Entrada del log de auditoría"""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True

class AccessControlManager:
    """
    Gestor principal del sistema de control de acceso
    """
    
    def __init__(self, secret_key: str = None):
        self.users: Dict[str, User] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.session_timeout = timedelta(hours=8)  # 8 horas de sesión
        
        # Definir permisos por rol
        self.role_permissions = {
            UserRole.END_USER: {
                Permission.EXECUTE_TASK,
                Permission.VIEW_TASK_HISTORY,
                Permission.VIEW_BASIC_STATUS
            },
            UserRole.ADMIN: {
                Permission.EXECUTE_TASK,
                Permission.VIEW_TASK_HISTORY,
                Permission.VIEW_BASIC_STATUS,
                Permission.CONFIGURE_TOOLS,
                Permission.VIEW_TOOL_METRICS,
                Permission.MANAGE_TOOL_REGISTRY,
                Permission.VIEW_SYSTEM_LOGS,
                Permission.VIEW_ADMIN_DASHBOARD,
                Permission.MODIFY_AI_SETTINGS
            },
            UserRole.SUPER_ADMIN: {
                # Super admin tiene todos los permisos
                Permission.EXECUTE_TASK,
                Permission.VIEW_TASK_HISTORY,
                Permission.VIEW_BASIC_STATUS,
                Permission.CONFIGURE_TOOLS,
                Permission.VIEW_TOOL_METRICS,
                Permission.MANAGE_TOOL_REGISTRY,
                Permission.VIEW_SYSTEM_LOGS,
                Permission.VIEW_ADMIN_DASHBOARD,
                Permission.MODIFY_AI_SETTINGS,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.VIEW_AUDIT_LOGS,
                Permission.SYSTEM_ADMINISTRATION
            }
        }
        
        # Crear usuario administrador por defecto
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Crea un usuario administrador por defecto"""
        admin_id = "admin_default"
        if admin_id not in self.users:
            admin_user = User(
                user_id=admin_id,
                username="admin",
                email="admin@synapse.local",
                role=UserRole.SUPER_ADMIN,
                permissions=self.role_permissions[UserRole.SUPER_ADMIN],
                created_at=datetime.now(),
                password_hash=self._hash_password("admin123")  # Cambiar en producción
            )
            self.users[admin_id] = admin_user
            logger.info("Usuario administrador por defecto creado")
    
    def _hash_password(self, password: str) -> str:
        """Hash seguro de contraseña"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256',
                                                    password.encode('utf-8'),
                                                    salt.encode('utf-8'),
                                                    100000)
            return stored_hash == password_hash_check.hex()
        except Exception:
            return False
    
    def _generate_session_token(self, user_id: str) -> str:
        """Genera un token de sesión JWT"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.session_timeout,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _verify_session_token(self, token: str) -> Optional[str]:
        """Verifica un token de sesión y retorna el user_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            logger.warning("Token de sesión expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token de sesión inválido")
            return None
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = None) -> Optional[str]:
        """
        Autentica un usuario y retorna un token de sesión
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            ip_address: Dirección IP del cliente
            
        Returns:
            str: Token de sesión si la autenticación es exitosa
        """
        # Buscar usuario por nombre de usuario
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break
        
        if not user or not user.password_hash:
            await self._log_audit_event(
                user_id=username,
                action="LOGIN_FAILED",
                resource="authentication",
                details={"reason": "user_not_found"},
                ip_address=ip_address,
                success=False
            )
            return None
        
        if not self._verify_password(password, user.password_hash):
            await self._log_audit_event(
                user_id=user.user_id,
                action="LOGIN_FAILED",
                resource="authentication",
                details={"reason": "invalid_password"},
                ip_address=ip_address,
                success=False
            )
            return None
        
        # Generar token de sesión
        session_token = self._generate_session_token(user.user_id)
        user.session_token = session_token
        user.session_expires = datetime.now() + self.session_timeout
        user.last_login = datetime.now()
        
        await self._log_audit_event(
            user_id=user.user_id,
            action="LOGIN_SUCCESS",
            resource="authentication",
            details={"username": username},
            ip_address=ip_address
        )
        
        logger.info(f"Usuario autenticado exitosamente: {username}")
        return session_token
    
    async def validate_session(self, session_token: str) -> Optional[User]:
        """
        Valida un token de sesión y retorna el usuario
        
        Args:
            session_token: Token de sesión
            
        Returns:
            User: Usuario si la sesión es válida
        """
        user_id = self._verify_session_token(session_token)
        if not user_id:
            return None
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return None
        
        # Verificar que el token coincida con el almacenado
        if user.session_token != session_token:
            return None
        
        # Verificar que la sesión no haya expirado
        if user.session_expires and datetime.now() > user.session_expires:
            user.session_token = None
            user.session_expires = None
            return None
        
        return user
    
    async def logout_user(self, session_token: str, ip_address: str = None):
        """Cierra la sesión de un usuario"""
        user = await self.validate_session(session_token)
        if user:
            user.session_token = None
            user.session_expires = None
            
            await self._log_audit_event(
                user_id=user.user_id,
                action="LOGOUT",
                resource="authentication",
                details={"username": user.username},
                ip_address=ip_address
            )
            
            logger.info(f"Usuario desconectado: {user.username}")
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        return permission in user.permissions
    
    async def create_user(self, username: str, email: str, password: str, 
                         role: UserRole, created_by: str) -> str:
        """
        Crea un nuevo usuario (solo para administradores)
        
        Args:
            username: Nombre de usuario
            email: Email del usuario
            password: Contraseña
            role: Rol del usuario
            created_by: ID del usuario que crea este usuario
            
        Returns:
            str: ID del usuario creado
        """
        # Verificar que el usuario que crea tiene permisos
        creator = self.users.get(created_by)
        if not creator or not self.check_permission(creator, Permission.MANAGE_USERS):
            raise PermissionError("No tiene permisos para crear usuarios")
        
        # Verificar que el username no existe
        for user in self.users.values():
            if user.username == username:
                raise ValueError("El nombre de usuario ya existe")
        
        # Crear nuevo usuario
        user_id = f"user_{secrets.token_hex(8)}"
        new_user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=self.role_permissions[role],
            created_at=datetime.now(),
            password_hash=self._hash_password(password)
        )
        
        self.users[user_id] = new_user
        
        await self._log_audit_event(
            user_id=created_by,
            action="USER_CREATED",
            resource="user_management",
            details={
                "new_user_id": user_id,
                "username": username,
                "role": role.value
            }
        )
        
        logger.info(f"Usuario creado: {username} con rol {role.value}")
        return user_id
    
    async def update_user_role(self, user_id: str, new_role: UserRole, 
                              updated_by: str):
        """Actualiza el rol de un usuario"""
        updater = self.users.get(updated_by)
        if not updater or not self.check_permission(updater, Permission.MANAGE_ROLES):
            raise PermissionError("No tiene permisos para modificar roles")
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        old_role = user.role
        user.role = new_role
        user.permissions = self.role_permissions[new_role]
        
        await self._log_audit_event(
            user_id=updated_by,
            action="ROLE_UPDATED",
            resource="user_management",
            details={
                "target_user_id": user_id,
                "old_role": old_role.value,
                "new_role": new_role.value
            }
        )
        
        logger.info(f"Rol actualizado para {user.username}: {old_role.value} -> {new_role.value}")
    
    async def deactivate_user(self, user_id: str, deactivated_by: str):
        """Desactiva un usuario"""
        deactivator = self.users.get(deactivated_by)
        if not deactivator or not self.check_permission(deactivator, Permission.MANAGE_USERS):
            raise PermissionError("No tiene permisos para desactivar usuarios")
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        user.is_active = False
        user.session_token = None
        user.session_expires = None
        
        await self._log_audit_event(
            user_id=deactivated_by,
            action="USER_DEACTIVATED",
            resource="user_management",
            details={
                "target_user_id": user_id,
                "username": user.username
            }
        )
        
        logger.info(f"Usuario desactivado: {user.username}")
    
    async def _log_audit_event(self, user_id: str, action: str, resource: str,
                              details: Dict[str, Any], ip_address: str = None,
                              user_agent: str = None, success: bool = True):
        """Registra un evento en el log de auditoría"""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        
        self.audit_log.append(entry)
        
        # Mantener solo los últimos 10000 eventos
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
    
    async def get_audit_logs(self, user_id: str, start_date: datetime = None,
                           end_date: datetime = None, limit: int = 100) -> List[Dict]:
        """Obtiene logs de auditoría (solo para super admins)"""
        user = self.users.get(user_id)
        if not user or not self.check_permission(user, Permission.VIEW_AUDIT_LOGS):
            raise PermissionError("No tiene permisos para ver logs de auditoría")
        
        filtered_logs = self.audit_log
        
        if start_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]
        
        # Limitar resultados
        filtered_logs = filtered_logs[-limit:]
        
        return [asdict(log) for log in filtered_logs]
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Obtiene información básica de un usuario"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        return {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    def list_users(self, requesting_user_id: str) -> List[Dict]:
        """Lista todos los usuarios (solo para admins)"""
        user = self.users.get(requesting_user_id)
        if not user or not self.check_permission(user, Permission.MANAGE_USERS):
            raise PermissionError("No tiene permisos para listar usuarios")
        
        return [self.get_user_info(uid) for uid in self.users.keys()]

def require_permission(permission: Permission):
    """Decorador para requerir un permiso específico"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el parámetro user en los argumentos
            user = kwargs.get('user') or (args[0] if args and isinstance(args[0], User) else None)
            
            if not user or not isinstance(user, User):
                raise PermissionError("Usuario no autenticado")
            
            if not access_control.check_permission(user, permission):
                raise PermissionError(f"Permiso requerido: {permission.value}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: UserRole):
    """Decorador para requerir un rol específico"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('user') or (args[0] if args and isinstance(args[0], User) else None)
            
            if not user or not isinstance(user, User):
                raise PermissionError("Usuario no autenticado")
            
            if user.role != role:
                raise PermissionError(f"Rol requerido: {role.value}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Instancia global del gestor de control de acceso
access_control = AccessControlManager()

