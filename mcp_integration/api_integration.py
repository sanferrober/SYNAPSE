"""
Integración de MCP con el servidor API de Synapse

Este módulo integra el sistema MCP con el servidor Flask principal,
proporcionando endpoints REST y eventos WebSocket para gestionar
servidores MCP y herramientas.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify
from flask_socketio import emit

from mcp_integration import (
    get_mcp_integration,
    initialize_mcp_integration,
    shutdown_mcp_integration
)

logger = logging.getLogger(__name__)

# Blueprint para endpoints MCP
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

@mcp_bp.route('/status', methods=['GET'])
def get_mcp_status():
    """Obtiene el estado actual de la integración MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'not_initialized',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        status = mcp_integration.get_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        logger.error(f"Error obteniendo estado MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/health', methods=['GET'])
async def get_mcp_health():
    """Realiza un chequeo de salud de la integración MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        health = await mcp_integration.health_check()
        return jsonify({
            'status': 'success',
            'data': health
        })
    except Exception as e:
        logger.error(f"Error en chequeo de salud MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/servers', methods=['GET'])
def list_mcp_servers():
    """Lista todos los servidores MCP configurados"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        servers = mcp_integration.list_configured_servers()
        return jsonify({
            'status': 'success',
            'data': servers
        })
    except Exception as e:
        logger.error(f"Error listando servidores MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/servers/templates', methods=['GET'])
def list_mcp_templates():
    """Lista todas las plantillas de servidor MCP disponibles"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        templates = mcp_integration.list_available_templates()
        return jsonify({
            'status': 'success',
            'data': templates
        })
    except Exception as e:
        logger.error(f"Error listando plantillas MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/servers', methods=['POST'])
async def add_mcp_server():
    """Añade un nuevo servidor MCP"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos JSON requeridos'
            }), 400
        
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        # Determinar si es desde plantilla o personalizado
        if 'template_name' in data:
            success = await mcp_integration.add_server_from_template(
                data['template_name'],
                data['server_name'],
                data.get('custom_config')
            )
        else:
            # Servidor personalizado - necesita validación de configuración
            return jsonify({
                'status': 'error',
                'message': 'Configuración de servidor personalizado no implementada'
            }), 501
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f"Servidor {data['server_name']} añadido exitosamente"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error añadiendo servidor MCP'
            }), 500
            
    except Exception as e:
        logger.error(f"Error añadiendo servidor MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/servers/<server_name>', methods=['DELETE'])
async def remove_mcp_server(server_name: str):
    """Elimina un servidor MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        success = await mcp_integration.remove_server(server_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f"Servidor {server_name} eliminado exitosamente"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f"Error eliminando servidor {server_name}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error eliminando servidor MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/servers/<server_name>/enable', methods=['POST'])
async def enable_mcp_server(server_name: str):
    """Habilita un servidor MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        success = await mcp_integration.enable_server(server_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f"Servidor {server_name} habilitado exitosamente"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f"Error habilitando servidor {server_name}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error habilitando servidor MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/servers/<server_name>/disable', methods=['POST'])
async def disable_mcp_server(server_name: str):
    """Deshabilita un servidor MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        success = await mcp_integration.disable_server(server_name)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f"Servidor {server_name} deshabilitado exitosamente"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f"Error deshabilitando servidor {server_name}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error deshabilitando servidor MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/tools', methods=['GET'])
def list_mcp_tools():
    """Lista todas las herramientas MCP disponibles"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        category = request.args.get('category')
        tools = mcp_integration.list_tools(category)
        
        return jsonify({
            'status': 'success',
            'data': tools
        })
    except Exception as e:
        logger.error(f"Error listando herramientas MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/tools/categories', methods=['GET'])
def get_mcp_tool_categories():
    """Obtiene todas las categorías de herramientas MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        categories = mcp_integration.get_tool_categories()
        
        return jsonify({
            'status': 'success',
            'data': categories
        })
    except Exception as e:
        logger.error(f"Error obteniendo categorías MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/tools/by-category', methods=['GET'])
def get_mcp_tools_by_category():
    """Obtiene herramientas MCP agrupadas por categoría"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        tools_by_category = mcp_integration.get_tools_by_category()
        
        return jsonify({
            'status': 'success',
            'data': tools_by_category
        })
    except Exception as e:
        logger.error(f"Error obteniendo herramientas por categoría: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/tools/search', methods=['GET'])
def search_mcp_tools():
    """Busca herramientas MCP por nombre o descripción"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Parámetro de búsqueda "q" requerido'
            }), 400
        
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        tools = mcp_integration.search_tools(query)
        
        return jsonify({
            'status': 'success',
            'data': tools
        })
    except Exception as e:
        logger.error(f"Error buscando herramientas MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/tools/<tool_id>', methods=['GET'])
def get_mcp_tool_info(tool_id: str):
    """Obtiene información detallada de una herramienta MCP"""
    try:
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        tool_info = mcp_integration.get_tool_info(tool_id)
        
        if tool_info:
            return jsonify({
                'status': 'success',
                'data': tool_info
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f"Herramienta {tool_id} no encontrada"
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo información de herramienta MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mcp_bp.route('/tools/<tool_id>/execute', methods=['POST'])
async def execute_mcp_tool(tool_id: str):
    """Ejecuta una herramienta MCP"""
    try:
        data = request.get_json()
        arguments = data.get('arguments', {}) if data else {}
        
        mcp_integration = get_mcp_integration()
        if not mcp_integration:
            return jsonify({
                'status': 'error',
                'message': 'Integración MCP no inicializada'
            }), 503
        
        result = await mcp_integration.execute_tool(tool_id, arguments)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error ejecutando herramienta MCP: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Funciones para eventos WebSocket
def setup_mcp_websocket_events(socketio):
    """Configura eventos WebSocket para MCP"""
    
    @socketio.on('mcp_get_status')
    def handle_mcp_get_status():
        """Maneja solicitud de estado MCP via WebSocket"""
        try:
            mcp_integration = get_mcp_integration()
            if not mcp_integration:
                emit('mcp_status', {
                    'status': 'error',
                    'message': 'Integración MCP no inicializada'
                })
                return
            
            status = mcp_integration.get_status()
            emit('mcp_status', {
                'status': 'success',
                'data': status
            })
        except Exception as e:
            logger.error(f"Error en WebSocket MCP status: {e}")
            emit('mcp_status', {
                'status': 'error',
                'message': str(e)
            })
    
    @socketio.on('mcp_list_tools')
    def handle_mcp_list_tools(data):
        """Maneja solicitud de lista de herramientas MCP via WebSocket"""
        try:
            mcp_integration = get_mcp_integration()
            if not mcp_integration:
                emit('mcp_tools_list', {
                    'status': 'error',
                    'message': 'Integración MCP no inicializada'
                })
                return
            
            category = data.get('category') if data else None
            tools = mcp_integration.list_tools(category)
            
            emit('mcp_tools_list', {
                'status': 'success',
                'data': tools
            })
        except Exception as e:
            logger.error(f"Error en WebSocket MCP list tools: {e}")
            emit('mcp_tools_list', {
                'status': 'error',
                'message': str(e)
            })
    
    @socketio.on('mcp_execute_tool')
    async def handle_mcp_execute_tool(data):
        """Maneja ejecución de herramienta MCP via WebSocket"""
        try:
            if not data or 'tool_id' not in data:
                emit('mcp_tool_result', {
                    'status': 'error',
                    'message': 'tool_id requerido'
                })
                return
            
            mcp_integration = get_mcp_integration()
            if not mcp_integration:
                emit('mcp_tool_result', {
                    'status': 'error',
                    'message': 'Integración MCP no inicializada'
                })
                return
            
            tool_id = data['tool_id']
            arguments = data.get('arguments', {})
            
            # Emitir evento de inicio de ejecución
            emit('mcp_tool_execution_started', {
                'tool_id': tool_id,
                'arguments': arguments
            })
            
            result = await mcp_integration.execute_tool(tool_id, arguments)
            
            emit('mcp_tool_result', {
                'status': 'success',
                'tool_id': tool_id,
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error en WebSocket MCP execute tool: {e}")
            emit('mcp_tool_result', {
                'status': 'error',
                'tool_id': data.get('tool_id') if data else 'unknown',
                'message': str(e)
            })

# Función para configurar manejadores de eventos MCP
def setup_mcp_event_handlers(socketio):
    """Configura manejadores de eventos MCP para notificaciones en tiempo real"""
    
    def on_server_connected(server_name: str):
        """Maneja evento de servidor conectado"""
        socketio.emit('mcp_server_connected', {
            'server_name': server_name,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    def on_server_disconnected(server_name: str):
        """Maneja evento de servidor desconectado"""
        socketio.emit('mcp_server_disconnected', {
            'server_name': server_name,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    def on_tools_updated(total_tools: int):
        """Maneja evento de herramientas actualizadas"""
        socketio.emit('mcp_tools_updated', {
            'total_tools': total_tools,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    def on_error(error_message: str):
        """Maneja evento de error MCP"""
        socketio.emit('mcp_error', {
            'error': error_message,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    # Registrar manejadores de eventos
    mcp_integration = get_mcp_integration()
    if mcp_integration:
        mcp_integration.add_event_handler('server_connected', on_server_connected)
        mcp_integration.add_event_handler('server_disconnected', on_server_disconnected)
        mcp_integration.add_event_handler('tools_updated', on_tools_updated)
        mcp_integration.add_event_handler('error', on_error)

# Función de inicialización para el servidor principal
async def initialize_mcp_for_server(app, socketio, config_dir: Optional[str] = None):
    """Inicializa la integración MCP para el servidor principal"""
    try:
        # Inicializar integración MCP
        mcp_integration = await initialize_mcp_integration(config_dir)
        
        # Registrar blueprint
        app.register_blueprint(mcp_bp)
        
        # Configurar eventos WebSocket
        setup_mcp_websocket_events(socketio)
        setup_mcp_event_handlers(socketio)
        
        logger.info("Integración MCP inicializada exitosamente en el servidor")
        return True
        
    except Exception as e:
        logger.error(f"Error inicializando MCP en el servidor: {e}")
        return False

# Función de limpieza para el servidor principal
async def cleanup_mcp_for_server():
    """Limpia la integración MCP al cerrar el servidor"""
    try:
        await shutdown_mcp_integration()
        logger.info("Integración MCP cerrada exitosamente")
    except Exception as e:
        logger.error(f"Error cerrando integración MCP: {e}")

