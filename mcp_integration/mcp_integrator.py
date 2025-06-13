"""
Integrador Principal MCP para Synapse

Este módulo orquesta toda la integración MCP, conectando el gestor de clientes,
el adaptador de herramientas y el registro de servidores con el sistema principal de Synapse.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from mcp_integration.client.mcp_client_manager import MCPClientManager
from mcp_integration.tools.mcp_tool_adapter import MCPToolAdapter
from mcp_integration.servers.mcp_server_registry import MCPServerRegistry

logger = logging.getLogger(__name__)

@dataclass
class MCPIntegrationStatus:
    """Estado de la integración MCP"""
    initialized: bool = False
    running: bool = False
    connected_servers: int = 0
    total_tools: int = 0
    last_error: Optional[str] = None

class MCPIntegration:
    """Integrador principal MCP para Synapse"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir
        
        # Componentes principales
        self.server_registry = MCPServerRegistry(config_dir)
        self.client_manager = MCPClientManager()
        self.tool_adapter = MCPToolAdapter(self.client_manager)
        
        # Estado
        self.status = MCPIntegrationStatus()
        self.event_handlers: Dict[str, List[Callable]] = {
            'server_connected': [],
            'server_disconnected': [],
            'tools_updated': [],
            'error': []
        }
        
        # Configurar manejadores de eventos del cliente
        self.client_manager.add_event_handler('server_connected', self._on_server_connected)
        self.client_manager.add_event_handler('server_disconnected', self._on_server_disconnected)
        self.client_manager.add_event_handler('error', self._on_error)
        
        logger.info("MCP Integration inicializado")
    
    def add_event_handler(self, event: str, handler: Callable):
        """Añade un manejador de eventos"""
        if event in self.event_handlers:
            self.event_handlers[event].append(handler)
    
    def remove_event_handler(self, event: str, handler: Callable):
        """Remueve un manejador de eventos"""
        if event in self.event_handlers and handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
    
    async def _emit_event(self, event: str, *args, **kwargs):
        """Emite un evento a todos los manejadores registrados"""
        for handler in self.event_handlers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error en manejador de evento {event}: {e}")
    
    async def _on_server_connected(self, server_name: str, connection):
        """Manejador para cuando se conecta un servidor"""
        logger.info(f"Servidor MCP conectado: {server_name}")
        await self._refresh_tools()
        await self._emit_event('server_connected', server_name)
    
    async def _on_server_disconnected(self, server_name: str):
        """Manejador para cuando se desconecta un servidor"""
        logger.info(f"Servidor MCP desconectado: {server_name}")
        await self._refresh_tools()
        await self._emit_event('server_disconnected', server_name)
    
    async def _on_error(self, error_message: str):
        """Manejador para errores"""
        logger.error(f"Error MCP: {error_message}")
        self.status.last_error = error_message
        await self._emit_event('error', error_message)
    
    async def _refresh_tools(self):
        """Actualiza las herramientas adaptadas"""
        try:
            await self.tool_adapter.refresh_tools()
            self.status.total_tools = len(self.tool_adapter.adapted_tools)
            await self._emit_event('tools_updated', self.status.total_tools)
        except Exception as e:
            logger.error(f"Error actualizando herramientas: {e}")
    
    async def initialize(self) -> bool:
        """Inicializa la integración MCP"""
        try:
            # Iniciar el gestor de clientes
            await self.client_manager.start()
            
            # Conectar a todos los servidores configurados y habilitados
            server_configs = self.server_registry.get_all_server_configs()
            connection_tasks = []
            
            for config in server_configs.values():
                if config.enabled:
                    connection_tasks.append(self.client_manager.add_server(config))
            
            if connection_tasks:
                results = await asyncio.gather(*connection_tasks, return_exceptions=True)
                successful_connections = sum(1 for result in results if result is True)
                logger.info(f"Conectados {successful_connections} de {len(connection_tasks)} servidores MCP")
            
            # Actualizar herramientas
            await self._refresh_tools()
            
            # Actualizar estado
            self.status.initialized = True
            self.status.running = True
            self.status.connected_servers = len(self.client_manager.list_servers())
            
            logger.info("MCP Integration inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando MCP Integration: {e}")
            self.status.last_error = str(e)
            return False
    
    async def shutdown(self):
        """Cierra la integración MCP"""
        try:
            await self.client_manager.stop()
            
            self.status.running = False
            self.status.connected_servers = 0
            self.status.total_tools = 0
            
            logger.info("MCP Integration cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando MCP Integration: {e}")
    
    # Métodos de gestión de servidores
    
    async def add_server_from_template(self, template_name: str, server_name: str, 
                                     custom_config: Optional[Dict[str, Any]] = None) -> bool:
        """Añade un servidor desde una plantilla y lo conecta"""
        if not self.server_registry.add_server_from_template(template_name, server_name, custom_config):
            return False
        
        if self.status.running:
            config = self.server_registry.get_server_config(server_name)
            if config and config.enabled:
                success = await self.client_manager.add_server(config)
                if success:
                    self.status.connected_servers = len(self.client_manager.list_servers())
                return success
        
        return True
    
    async def add_custom_server(self, config) -> bool:
        """Añade un servidor personalizado y lo conecta"""
        if not self.server_registry.add_custom_server(config):
            return False
        
        if self.status.running and config.enabled:
            success = await self.client_manager.add_server(config)
            if success:
                self.status.connected_servers = len(self.client_manager.list_servers())
            return success
        
        return True
    
    async def remove_server(self, server_name: str) -> bool:
        """Remueve un servidor y lo desconecta"""
        # Desconectar si está conectado
        if self.status.running:
            await self.client_manager.remove_server(server_name)
            self.status.connected_servers = len(self.client_manager.list_servers())
        
        # Remover de la configuración
        return self.server_registry.remove_server(server_name)
    
    async def enable_server(self, server_name: str) -> bool:
        """Habilita y conecta un servidor"""
        if not self.server_registry.update_server(server_name, {'enabled': True}):
            return False
        
        if self.status.running:
            config = self.server_registry.get_server_config(server_name)
            if config:
                success = await self.client_manager.add_server(config)
                if success:
                    self.status.connected_servers = len(self.client_manager.list_servers())
                return success
        
        return True
    
    async def disable_server(self, server_name: str) -> bool:
        """Deshabilita y desconecta un servidor"""
        if not self.server_registry.update_server(server_name, {'enabled': False}):
            return False
        
        if self.status.running:
            await self.client_manager.remove_server(server_name)
            self.status.connected_servers = len(self.client_manager.list_servers())
        
        return True
    
    # Métodos de gestión de herramientas
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todas las herramientas disponibles"""
        tools = self.tool_adapter.list_tools(category)
        return [self.tool_adapter.get_tool_info(tool.id) for tool in tools]
    
    def get_tool_categories(self) -> List[str]:
        """Obtiene todas las categorías de herramientas"""
        return self.tool_adapter.get_categories()
    
    def get_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtiene herramientas agrupadas por categoría"""
        return self.tool_adapter.get_tools_by_category()
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Busca herramientas por nombre o descripción"""
        tools = self.tool_adapter.search_tools(query)
        return [self.tool_adapter.get_tool_info(tool.id) for tool in tools]
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información detallada de una herramienta"""
        return self.tool_adapter.get_tool_info(tool_id)
    
    async def execute_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta MCP"""
        return await self.tool_adapter.execute_tool(tool_id, arguments)
    
    # Métodos de información y estado
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo de la integración MCP"""
        client_status = self.client_manager.get_status()
        tool_stats = self.tool_adapter.get_statistics()
        registry_stats = self.server_registry.get_statistics()
        
        return {
            'integration_status': {
                'initialized': self.status.initialized,
                'running': self.status.running,
                'connected_servers': self.status.connected_servers,
                'total_tools': self.status.total_tools,
                'last_error': self.status.last_error
            },
            'client_manager': client_status,
            'tool_adapter': tool_stats,
            'server_registry': registry_stats
        }
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """Lista todas las plantillas de servidor disponibles"""
        templates = []
        for name in self.server_registry.list_available_templates():
            template = self.server_registry.get_template(name)
            if template:
                templates.append({
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'transport_type': template.transport_type.value,
                    'author': template.author,
                    'version': template.version,
                    'documentation_url': template.documentation_url,
                    'installation_instructions': template.installation_instructions
                })
        return templates
    
    def list_configured_servers(self) -> List[Dict[str, Any]]:
        """Lista todos los servidores configurados"""
        servers = []
        for name in self.server_registry.list_configured_servers():
            config = self.server_registry.get_server_config(name)
            connection = self.client_manager.get_server(name)
            
            if config:
                servers.append({
                    'name': config.name,
                    'transport_type': config.transport_type.value,
                    'enabled': config.enabled,
                    'connected': connection.connected if connection else False,
                    'tools_count': len(connection.tools) if connection and connection.connected else 0,
                    'last_error': connection.last_error if connection else None
                })
        
        return servers
    
    async def health_check(self) -> Dict[str, Any]:
        """Realiza un chequeo de salud completo"""
        client_health = await self.client_manager.health_check()
        
        return {
            'overall_status': 'healthy' if self.status.running and not self.status.last_error else 'unhealthy',
            'integration_initialized': self.status.initialized,
            'integration_running': self.status.running,
            'servers_health': client_health,
            'total_servers': len(self.server_registry.configured_servers),
            'connected_servers': self.status.connected_servers,
            'total_tools': self.status.total_tools,
            'last_error': self.status.last_error
        }
    
    # Métodos de configuración
    
    def export_configuration(self, file_path: str):
        """Exporta toda la configuración MCP"""
        self.server_registry.export_configuration(file_path)
    
    def import_configuration(self, file_path: str, merge: bool = True):
        """Importa configuración MCP"""
        self.server_registry.import_configuration(file_path, merge)
    
    async def reload_configuration(self):
        """Recarga la configuración y reconecta servidores"""
        if self.status.running:
            # Desconectar todos los servidores actuales
            for server_name in self.client_manager.list_servers():
                await self.client_manager.remove_server(server_name)
            
            # Recargar configuración
            self.server_registry._load_configurations()
            
            # Reconectar servidores habilitados
            server_configs = self.server_registry.get_all_server_configs()
            for config in server_configs.values():
                if config.enabled:
                    await self.client_manager.add_server(config)
            
            # Actualizar estado
            self.status.connected_servers = len(self.client_manager.list_servers())
            await self._refresh_tools()
            
            logger.info("Configuración MCP recargada")

# Instancia global de integración MCP
mcp_integration: Optional[MCPIntegration] = None

def get_mcp_integration() -> Optional[MCPIntegration]:
    """Obtiene la instancia global de integración MCP"""
    return mcp_integration

async def initialize_mcp_integration(config_dir: Optional[str] = None) -> MCPIntegration:
    """Inicializa la integración MCP global"""
    global mcp_integration
    
    if mcp_integration is None:
        mcp_integration = MCPIntegration(config_dir)
        await mcp_integration.initialize()
    
    return mcp_integration

async def shutdown_mcp_integration():
    """Cierra la integración MCP global"""
    global mcp_integration
    
    if mcp_integration is not None:
        await mcp_integration.shutdown()
        mcp_integration = None

