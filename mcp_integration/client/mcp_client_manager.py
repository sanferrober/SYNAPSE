"""
MCP Client Manager para Synapse

Este módulo gestiona las conexiones y comunicación con servidores MCP,
proporcionando una interfaz unificada para el sistema de herramientas de Synapse.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.types import (
    Tool, 
    Resource, 
    Prompt,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListResourcesRequest,
    ListPromptsRequest,
    GetResourceRequest,
    GetPromptRequest
)

logger = logging.getLogger(__name__)

class MCPTransportType(Enum):
    """Tipos de transporte soportados para MCP"""
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"

@dataclass
class MCPServerConfig:
    """Configuración para un servidor MCP"""
    name: str
    transport_type: MCPTransportType
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    enabled: bool = True
    timeout: int = 30
    retry_attempts: int = 3

class MCPServerConnection:
    """Representa una conexión activa a un servidor MCP"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.client = None
        self.connected = False
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
        self.prompts: List[Prompt] = []
        self.last_error: Optional[str] = None
        
    async def connect(self) -> bool:
        """Establece conexión con el servidor MCP"""
        try:
            if self.config.transport_type == MCPTransportType.STDIO:
                await self._connect_stdio()
            elif self.config.transport_type == MCPTransportType.SSE:
                await self._connect_sse()
            else:
                raise ValueError(f"Transporte no soportado: {self.config.transport_type}")
                
            # Obtener capacidades del servidor
            await self._fetch_capabilities()
            self.connected = True
            self.last_error = None
            logger.info(f"Conectado exitosamente a servidor MCP: {self.config.name}")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error conectando a servidor MCP {self.config.name}: {e}")
            return False
    
    async def _connect_stdio(self):
        """Conecta usando transporte STDIO"""
        if not self.config.command:
            raise ValueError("Comando requerido para transporte STDIO")
            
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args or [],
            env=self.config.env
        )
        
        self.session, self.client = await stdio_client(server_params)
        
    async def _connect_sse(self):
        """Conecta usando transporte SSE"""
        if not self.config.url:
            raise ValueError("URL requerida para transporte SSE")
            
        self.session, self.client = await sse_client(self.config.url)
    
    async def _fetch_capabilities(self):
        """Obtiene las capacidades del servidor (tools, resources, prompts)"""
        try:
            # Obtener herramientas
            tools_response = await self.session.list_tools(ListToolsRequest())
            self.tools = tools_response.tools
            
            # Obtener recursos
            try:
                resources_response = await self.session.list_resources(ListResourcesRequest())
                self.resources = resources_response.resources
            except Exception as e:
                logger.warning(f"Servidor {self.config.name} no soporta recursos: {e}")
                self.resources = []
            
            # Obtener prompts
            try:
                prompts_response = await self.session.list_prompts(ListPromptsRequest())
                self.prompts = prompts_response.prompts
            except Exception as e:
                logger.warning(f"Servidor {self.config.name} no soporta prompts: {e}")
                self.prompts = []
                
            logger.info(f"Servidor {self.config.name}: {len(self.tools)} tools, "
                       f"{len(self.resources)} resources, {len(self.prompts)} prompts")
                       
        except Exception as e:
            logger.error(f"Error obteniendo capacidades de {self.config.name}: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Ejecuta una herramienta en el servidor MCP"""
        if not self.connected or not self.session:
            raise RuntimeError(f"No conectado a servidor {self.config.name}")
            
        request = CallToolRequest(
            name=tool_name,
            arguments=arguments
        )
        
        try:
            result = await self.session.call_tool(request)
            logger.debug(f"Tool {tool_name} ejecutada en {self.config.name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error ejecutando tool {tool_name} en {self.config.name}: {e}")
            raise
    
    async def get_resource(self, resource_uri: str) -> Any:
        """Obtiene un recurso del servidor MCP"""
        if not self.connected or not self.session:
            raise RuntimeError(f"No conectado a servidor {self.config.name}")
            
        request = GetResourceRequest(uri=resource_uri)
        
        try:
            result = await self.session.get_resource(request)
            logger.debug(f"Recurso {resource_uri} obtenido de {self.config.name}")
            return result
        except Exception as e:
            logger.error(f"Error obteniendo recurso {resource_uri} de {self.config.name}: {e}")
            raise
    
    async def get_prompt(self, prompt_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Obtiene un prompt del servidor MCP"""
        if not self.connected or not self.session:
            raise RuntimeError(f"No conectado a servidor {self.config.name}")
            
        request = GetPromptRequest(
            name=prompt_name,
            arguments=arguments or {}
        )
        
        try:
            result = await self.session.get_prompt(request)
            logger.debug(f"Prompt {prompt_name} obtenido de {self.config.name}")
            return result
        except Exception as e:
            logger.error(f"Error obteniendo prompt {prompt_name} de {self.config.name}: {e}")
            raise
    
    async def disconnect(self):
        """Desconecta del servidor MCP"""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.warning(f"Error cerrando sesión MCP {self.config.name}: {e}")
        
        self.session = None
        self.client = None
        self.connected = False
        logger.info(f"Desconectado de servidor MCP: {self.config.name}")

class MCPClientManager:
    """Gestor principal de clientes MCP para Synapse"""
    
    def __init__(self):
        self.connections: Dict[str, MCPServerConnection] = {}
        self.event_handlers: Dict[str, List[Callable]] = {
            'server_connected': [],
            'server_disconnected': [],
            'tool_executed': [],
            'error': []
        }
        self._running = False
        
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
    
    async def add_server(self, config: MCPServerConfig) -> bool:
        """Añade y conecta a un servidor MCP"""
        if config.name in self.connections:
            logger.warning(f"Servidor MCP {config.name} ya existe")
            return False
        
        if not config.enabled:
            logger.info(f"Servidor MCP {config.name} está deshabilitado")
            return False
        
        connection = MCPServerConnection(config)
        
        # Intentar conectar con reintentos
        for attempt in range(config.retry_attempts):
            if await connection.connect():
                self.connections[config.name] = connection
                await self._emit_event('server_connected', config.name, connection)
                return True
            
            if attempt < config.retry_attempts - 1:
                logger.info(f"Reintentando conexión a {config.name} en 2 segundos...")
                await asyncio.sleep(2)
        
        await self._emit_event('error', f"No se pudo conectar a servidor {config.name}")
        return False
    
    async def remove_server(self, server_name: str) -> bool:
        """Remueve y desconecta un servidor MCP"""
        if server_name not in self.connections:
            return False
        
        connection = self.connections[server_name]
        await connection.disconnect()
        del self.connections[server_name]
        
        await self._emit_event('server_disconnected', server_name)
        return True
    
    def get_server(self, server_name: str) -> Optional[MCPServerConnection]:
        """Obtiene una conexión de servidor por nombre"""
        return self.connections.get(server_name)
    
    def list_servers(self) -> List[str]:
        """Lista todos los servidores conectados"""
        return list(self.connections.keys())
    
    def get_all_tools(self) -> Dict[str, List[Tool]]:
        """Obtiene todas las herramientas de todos los servidores"""
        all_tools = {}
        for name, connection in self.connections.items():
            if connection.connected:
                all_tools[name] = connection.tools
        return all_tools
    
    def get_all_resources(self) -> Dict[str, List[Resource]]:
        """Obtiene todos los recursos de todos los servidores"""
        all_resources = {}
        for name, connection in self.connections.items():
            if connection.connected:
                all_resources[name] = connection.resources
        return all_resources
    
    def get_all_prompts(self) -> Dict[str, List[Prompt]]:
        """Obtiene todos los prompts de todos los servidores"""
        all_prompts = {}
        for name, connection in self.connections.items():
            if connection.connected:
                all_prompts[name] = connection.prompts
        return all_prompts
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Ejecuta una herramienta en un servidor específico"""
        connection = self.connections.get(server_name)
        if not connection:
            raise ValueError(f"Servidor {server_name} no encontrado")
        
        if not connection.connected:
            raise RuntimeError(f"Servidor {server_name} no está conectado")
        
        try:
            result = await connection.call_tool(tool_name, arguments)
            await self._emit_event('tool_executed', server_name, tool_name, arguments, result)
            return result
        except Exception as e:
            await self._emit_event('error', f"Error ejecutando {tool_name} en {server_name}: {e}")
            raise
    
    async def find_and_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Busca y ejecuta una herramienta en cualquier servidor que la tenga"""
        for server_name, connection in self.connections.items():
            if not connection.connected:
                continue
                
            # Buscar la herramienta en este servidor
            for tool in connection.tools:
                if tool.name == tool_name:
                    return await self.call_tool(server_name, tool_name, arguments)
        
        raise ValueError(f"Herramienta {tool_name} no encontrada en ningún servidor")
    
    async def get_resource(self, server_name: str, resource_uri: str) -> Any:
        """Obtiene un recurso de un servidor específico"""
        connection = self.connections.get(server_name)
        if not connection:
            raise ValueError(f"Servidor {server_name} no encontrado")
        
        return await connection.get_resource(resource_uri)
    
    async def get_prompt(self, server_name: str, prompt_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Obtiene un prompt de un servidor específico"""
        connection = self.connections.get(server_name)
        if not connection:
            raise ValueError(f"Servidor {server_name} no encontrado")
        
        return await connection.get_prompt(prompt_name, arguments)
    
    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        """Verifica el estado de salud de todos los servidores"""
        health_status = {}
        
        for name, connection in self.connections.items():
            status = {
                'connected': connection.connected,
                'tools_count': len(connection.tools),
                'resources_count': len(connection.resources),
                'prompts_count': len(connection.prompts),
                'last_error': connection.last_error,
                'transport_type': connection.config.transport_type.value
            }
            health_status[name] = status
        
        return health_status
    
    async def start(self):
        """Inicia el gestor MCP"""
        self._running = True
        logger.info("MCP Client Manager iniciado")
    
    async def stop(self):
        """Detiene el gestor MCP y desconecta todos los servidores"""
        self._running = False
        
        # Desconectar todos los servidores
        disconnect_tasks = []
        for connection in self.connections.values():
            disconnect_tasks.append(connection.disconnect())
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        self.connections.clear()
        logger.info("MCP Client Manager detenido")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado general del gestor MCP"""
        connected_servers = sum(1 for conn in self.connections.values() if conn.connected)
        total_tools = sum(len(conn.tools) for conn in self.connections.values() if conn.connected)
        total_resources = sum(len(conn.resources) for conn in self.connections.values() if conn.connected)
        total_prompts = sum(len(conn.prompts) for conn in self.connections.values() if conn.connected)
        
        return {
            'running': self._running,
            'total_servers': len(self.connections),
            'connected_servers': connected_servers,
            'total_tools': total_tools,
            'total_resources': total_resources,
            'total_prompts': total_prompts
        }

