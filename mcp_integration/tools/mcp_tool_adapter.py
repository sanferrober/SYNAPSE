"""
Adaptador de Herramientas MCP para Synapse

Este módulo adapta las herramientas MCP al sistema de herramientas nativo de Synapse,
proporcionando una interfaz unificada y transparente.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from mcp.types import Tool as MCPTool, CallToolResult
from mcp_integration.client.mcp_client_manager import MCPClientManager, MCPServerConfig, MCPTransportType

logger = logging.getLogger(__name__)

@dataclass
class SynapseToolParameter:
    """Parámetro de herramienta en formato Synapse"""
    name: str
    type: str
    description: str
    required: bool = False
    default: Any = None
    enum: Optional[List[str]] = None

@dataclass
class SynapseTool:
    """Herramienta en formato Synapse"""
    id: str
    name: str
    description: str
    category: str
    parameters: List[SynapseToolParameter]
    server_name: str
    mcp_tool_name: str
    enabled: bool = True
    version: str = "1.0.0"

class MCPToolAdapter:
    """Adaptador que convierte herramientas MCP al formato de Synapse"""
    
    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp_manager = mcp_manager
        self.adapted_tools: Dict[str, SynapseTool] = {}
        self.tool_categories = {
            'git': 'Control de Versiones',
            'github': 'Control de Versiones', 
            'gitlab': 'Control de Versiones',
            'file': 'Sistema de Archivos',
            'filesystem': 'Sistema de Archivos',
            'docker': 'DevOps',
            'kubernetes': 'DevOps',
            'database': 'Base de Datos',
            'postgres': 'Base de Datos',
            'mysql': 'Base de Datos',
            'redis': 'Base de Datos',
            'web': 'Web',
            'browser': 'Web',
            'http': 'Web',
            'ai': 'Inteligencia Artificial',
            'llm': 'Inteligencia Artificial',
            'code': 'Desarrollo',
            'ide': 'Desarrollo',
            'vscode': 'Desarrollo',
            'test': 'Testing',
            'ci': 'CI/CD',
            'cd': 'CI/CD',
            'deploy': 'CI/CD',
            'monitor': 'Monitoreo',
            'log': 'Monitoreo',
            'metric': 'Monitoreo'
        }
    
    def _categorize_tool(self, tool_name: str, server_name: str) -> str:
        """Categoriza una herramienta basándose en su nombre y servidor"""
        tool_lower = tool_name.lower()
        server_lower = server_name.lower()
        
        # Buscar categoría por nombre de herramienta
        for keyword, category in self.tool_categories.items():
            if keyword in tool_lower:
                return category
        
        # Buscar categoría por nombre de servidor
        for keyword, category in self.tool_categories.items():
            if keyword in server_lower:
                return category
        
        return 'General'
    
    def _convert_mcp_parameter_type(self, mcp_type: Any) -> str:
        """Convierte tipos de parámetros MCP a tipos de Synapse"""
        if isinstance(mcp_type, str):
            type_mapping = {
                'string': 'string',
                'number': 'number',
                'integer': 'integer',
                'boolean': 'boolean',
                'array': 'array',
                'object': 'object'
            }
            return type_mapping.get(mcp_type.lower(), 'string')
        
        if isinstance(mcp_type, dict):
            if mcp_type.get('type'):
                return self._convert_mcp_parameter_type(mcp_type['type'])
        
        return 'string'
    
    def _extract_parameters_from_schema(self, input_schema: Dict[str, Any]) -> List[SynapseToolParameter]:
        """Extrae parámetros de un esquema JSON Schema de MCP"""
        parameters = []
        
        if not isinstance(input_schema, dict):
            return parameters
        
        properties = input_schema.get('properties', {})
        required_fields = input_schema.get('required', [])
        
        for param_name, param_def in properties.items():
            if not isinstance(param_def, dict):
                continue
            
            param_type = self._convert_mcp_parameter_type(param_def.get('type', 'string'))
            description = param_def.get('description', f'Parámetro {param_name}')
            is_required = param_name in required_fields
            default_value = param_def.get('default')
            enum_values = param_def.get('enum')
            
            parameter = SynapseToolParameter(
                name=param_name,
                type=param_type,
                description=description,
                required=is_required,
                default=default_value,
                enum=enum_values
            )
            parameters.append(parameter)
        
        return parameters
    
    def adapt_mcp_tool(self, mcp_tool: MCPTool, server_name: str) -> SynapseTool:
        """Adapta una herramienta MCP al formato de Synapse"""
        # Generar ID único para la herramienta
        tool_id = f"mcp_{server_name}_{mcp_tool.name}".replace('-', '_').replace(' ', '_')
        
        # Categorizar la herramienta
        category = self._categorize_tool(mcp_tool.name, server_name)
        
        # Extraer parámetros del esquema de entrada
        parameters = []
        if hasattr(mcp_tool, 'inputSchema') and mcp_tool.inputSchema:
            parameters = self._extract_parameters_from_schema(mcp_tool.inputSchema)
        
        synapse_tool = SynapseTool(
            id=tool_id,
            name=mcp_tool.name,
            description=mcp_tool.description or f"Herramienta {mcp_tool.name} del servidor {server_name}",
            category=category,
            parameters=parameters,
            server_name=server_name,
            mcp_tool_name=mcp_tool.name
        )
        
        return synapse_tool
    
    async def refresh_tools(self):
        """Actualiza todas las herramientas adaptadas desde los servidores MCP"""
        self.adapted_tools.clear()
        
        all_tools = self.mcp_manager.get_all_tools()
        
        for server_name, mcp_tools in all_tools.items():
            for mcp_tool in mcp_tools:
                try:
                    synapse_tool = self.adapt_mcp_tool(mcp_tool, server_name)
                    self.adapted_tools[synapse_tool.id] = synapse_tool
                    logger.debug(f"Herramienta adaptada: {synapse_tool.id}")
                except Exception as e:
                    logger.error(f"Error adaptando herramienta {mcp_tool.name} de {server_name}: {e}")
        
        logger.info(f"Adaptadas {len(self.adapted_tools)} herramientas MCP")
    
    def get_tool(self, tool_id: str) -> Optional[SynapseTool]:
        """Obtiene una herramienta adaptada por ID"""
        return self.adapted_tools.get(tool_id)
    
    def list_tools(self, category: Optional[str] = None) -> List[SynapseTool]:
        """Lista todas las herramientas adaptadas, opcionalmente filtradas por categoría"""
        tools = list(self.adapted_tools.values())
        
        if category:
            tools = [tool for tool in tools if tool.category == category]
        
        return sorted(tools, key=lambda t: (t.category, t.name))
    
    def get_categories(self) -> List[str]:
        """Obtiene todas las categorías de herramientas disponibles"""
        categories = set(tool.category for tool in self.adapted_tools.values())
        return sorted(list(categories))
    
    async def execute_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta MCP adaptada"""
        tool = self.adapted_tools.get(tool_id)
        if not tool:
            raise ValueError(f"Herramienta {tool_id} no encontrada")
        
        if not tool.enabled:
            raise RuntimeError(f"Herramienta {tool_id} está deshabilitada")
        
        try:
            # Validar argumentos
            validated_args = self._validate_arguments(tool, arguments)
            
            # Ejecutar en el servidor MCP
            result = await self.mcp_manager.call_tool(
                tool.server_name, 
                tool.mcp_tool_name, 
                validated_args
            )
            
            # Convertir resultado a formato Synapse
            synapse_result = self._convert_mcp_result(result)
            
            logger.info(f"Herramienta {tool_id} ejecutada exitosamente")
            return synapse_result
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta {tool_id}: {e}")
            raise
    
    def _validate_arguments(self, tool: SynapseTool, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Valida los argumentos de una herramienta"""
        validated = {}
        
        # Verificar parámetros requeridos
        for param in tool.parameters:
            if param.required and param.name not in arguments:
                raise ValueError(f"Parámetro requerido '{param.name}' faltante para herramienta {tool.name}")
            
            if param.name in arguments:
                value = arguments[param.name]
                
                # Validación básica de tipos
                if param.type == 'integer' and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Parámetro '{param.name}' debe ser un entero")
                
                elif param.type == 'number' and not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Parámetro '{param.name}' debe ser un número")
                
                elif param.type == 'boolean' and not isinstance(value, bool):
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = bool(value)
                
                # Validar enum si existe
                if param.enum and value not in param.enum:
                    raise ValueError(f"Parámetro '{param.name}' debe ser uno de: {param.enum}")
                
                validated[param.name] = value
            
            elif param.default is not None:
                validated[param.name] = param.default
        
        return validated
    
    def _convert_mcp_result(self, mcp_result: CallToolResult) -> Dict[str, Any]:
        """Convierte un resultado MCP al formato de Synapse"""
        result = {
            'success': True,
            'data': None,
            'error': None,
            'metadata': {}
        }
        
        if hasattr(mcp_result, 'content') and mcp_result.content:
            # Procesar contenido del resultado
            if len(mcp_result.content) == 1:
                content_item = mcp_result.content[0]
                if hasattr(content_item, 'text'):
                    result['data'] = content_item.text
                elif hasattr(content_item, 'data'):
                    result['data'] = content_item.data
                else:
                    result['data'] = str(content_item)
            else:
                result['data'] = [
                    getattr(item, 'text', getattr(item, 'data', str(item)))
                    for item in mcp_result.content
                ]
        
        if hasattr(mcp_result, 'isError') and mcp_result.isError:
            result['success'] = False
            result['error'] = result['data']
            result['data'] = None
        
        return result
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información detallada de una herramienta"""
        tool = self.adapted_tools.get(tool_id)
        if not tool:
            return None
        
        return {
            'id': tool.id,
            'name': tool.name,
            'description': tool.description,
            'category': tool.category,
            'server_name': tool.server_name,
            'mcp_tool_name': tool.mcp_tool_name,
            'enabled': tool.enabled,
            'version': tool.version,
            'parameters': [asdict(param) for param in tool.parameters]
        }
    
    def get_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtiene herramientas agrupadas por categoría"""
        tools_by_category = {}
        
        for tool in self.adapted_tools.values():
            if tool.category not in tools_by_category:
                tools_by_category[tool.category] = []
            
            tools_by_category[tool.category].append(self.get_tool_info(tool.id))
        
        return tools_by_category
    
    def search_tools(self, query: str) -> List[SynapseTool]:
        """Busca herramientas por nombre o descripción"""
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self.adapted_tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower() or
                query_lower in tool.category.lower()):
                matching_tools.append(tool)
        
        return sorted(matching_tools, key=lambda t: t.name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de las herramientas adaptadas"""
        total_tools = len(self.adapted_tools)
        enabled_tools = sum(1 for tool in self.adapted_tools.values() if tool.enabled)
        categories = self.get_categories()
        
        tools_by_server = {}
        for tool in self.adapted_tools.values():
            server = tool.server_name
            if server not in tools_by_server:
                tools_by_server[server] = 0
            tools_by_server[server] += 1
        
        return {
            'total_tools': total_tools,
            'enabled_tools': enabled_tools,
            'disabled_tools': total_tools - enabled_tools,
            'categories': len(categories),
            'category_list': categories,
            'tools_by_server': tools_by_server
        }

