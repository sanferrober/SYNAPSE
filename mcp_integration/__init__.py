"""
Módulo de inicialización para la integración MCP
"""

from .mcp_integrator import (
    MCPIntegration,
    MCPIntegrationStatus,
    get_mcp_integration,
    initialize_mcp_integration,
    shutdown_mcp_integration
)

from .client.mcp_client_manager import (
    MCPClientManager,
    MCPServerConnection,
    MCPServerConfig,
    MCPTransportType
)

from .tools.mcp_tool_adapter import (
    MCPToolAdapter,
    SynapseTool,
    SynapseToolParameter
)

from .servers.mcp_server_registry import (
    MCPServerRegistry,
    MCPServerTemplate
)

__all__ = [
    # Integrador principal
    'MCPIntegration',
    'MCPIntegrationStatus',
    'get_mcp_integration',
    'initialize_mcp_integration',
    'shutdown_mcp_integration',
    
    # Cliente MCP
    'MCPClientManager',
    'MCPServerConnection',
    'MCPServerConfig',
    'MCPTransportType',
    
    # Adaptador de herramientas
    'MCPToolAdapter',
    'SynapseTool',
    'SynapseToolParameter',
    
    # Registro de servidores
    'MCPServerRegistry',
    'MCPServerTemplate'
]

