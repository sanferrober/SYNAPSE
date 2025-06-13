"""
Middleware de Autenticación para API Flask
=========================================

Este módulo proporciona middleware de autenticación y autorización
para las APIs de Synapse, integrándose con el sistema de control de acceso.
"""

from functools import wraps
from flask import request, jsonify, g
import asyncio
from typing import Optional

from .access_manager import access_control, User, Permission, UserRole

def auth_required(f):
    """Decorador que requiere autenticación válida"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autenticación requerido'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Validar sesión de forma síncrona (Flask no soporta async directamente)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(access_control.validate_session(token))
        finally:
            loop.close()
        
        if not user:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Almacenar usuario en el contexto de Flask
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorador que requiere rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'error': 'Autenticación requerida'}), 401
        
        if g.current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Permisos de administrador requeridos'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def permission_required(permission: Permission):
    """Decorador que requiere un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({'error': 'Autenticación requerida'}), 401
            
            if not access_control.check_permission(g.current_user, permission):
                return jsonify({'error': f'Permiso requerido: {permission.value}'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_current_user() -> Optional[User]:
    """Obtiene el usuario actual del contexto de Flask"""
    return getattr(g, 'current_user', None)

