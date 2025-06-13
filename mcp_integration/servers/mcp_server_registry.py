"""
Configuración y gestión de servidores MCP para Synapse

Este módulo maneja la configuración, registro y gestión del ciclo de vida
de los servidores MCP integrados con Synapse.
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from mcp_integration.client.mcp_client_manager import MCPServerConfig, MCPTransportType

logger = logging.getLogger(__name__)

@dataclass
class MCPServerTemplate:
    """Plantilla para configuración de servidor MCP"""
    name: str
    description: str
    transport_type: MCPTransportType
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    category: str = "General"
    version: str = "1.0.0"
    author: str = "Unknown"
    documentation_url: Optional[str] = None
    installation_instructions: Optional[str] = None

class MCPServerRegistry:
    """Registro de servidores MCP disponibles y configurados"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.join(os.getcwd(), "mcp_integration", "config"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.servers_config_file = self.config_dir / "servers.json"
        self.templates_config_file = self.config_dir / "templates.yaml"
        
        self.configured_servers: Dict[str, MCPServerConfig] = {}
        self.server_templates: Dict[str, MCPServerTemplate] = {}
        
        self._load_configurations()
        self._load_default_templates()
    
    def _load_configurations(self):
        """Carga las configuraciones de servidores desde archivo"""
        if self.servers_config_file.exists():
            try:
                with open(self.servers_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for server_data in data.get('servers', []):
                    config = MCPServerConfig(
                        name=server_data['name'],
                        transport_type=MCPTransportType(server_data['transport_type']),
                        command=server_data.get('command'),
                        args=server_data.get('args'),
                        url=server_data.get('url'),
                        env=server_data.get('env'),
                        enabled=server_data.get('enabled', True),
                        timeout=server_data.get('timeout', 30),
                        retry_attempts=server_data.get('retry_attempts', 3)
                    )
                    self.configured_servers[config.name] = config
                
                logger.info(f"Cargadas {len(self.configured_servers)} configuraciones de servidor")
                
            except Exception as e:
                logger.error(f"Error cargando configuraciones de servidor: {e}")
    
    def _save_configurations(self):
        """Guarda las configuraciones de servidores a archivo"""
        try:
            data = {
                'servers': [
                    {
                        'name': config.name,
                        'transport_type': config.transport_type.value,
                        'command': config.command,
                        'args': config.args,
                        'url': config.url,
                        'env': config.env,
                        'enabled': config.enabled,
                        'timeout': config.timeout,
                        'retry_attempts': config.retry_attempts
                    }
                    for config in self.configured_servers.values()
                ]
            }
            
            with open(self.servers_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("Configuraciones de servidor guardadas")
            
        except Exception as e:
            logger.error(f"Error guardando configuraciones de servidor: {e}")
    
    def _load_default_templates(self):
        """Carga plantillas predefinidas de servidores MCP"""
        default_templates = {
            'github': MCPServerTemplate(
                name='github',
                description='Servidor MCP oficial de GitHub para gestión de repositorios',
                transport_type=MCPTransportType.STDIO,
                command='npx',
                args=['-y', '@modelcontextprotocol/server-github'],
                category='Control de Versiones',
                author='Anthropic',
                documentation_url='https://github.com/modelcontextprotocol/servers/tree/main/src/github',
                installation_instructions='npm install -g @modelcontextprotocol/server-github'
            ),
            'filesystem': MCPServerTemplate(
                name='filesystem',
                description='Servidor MCP para operaciones seguras del sistema de archivos',
                transport_type=MCPTransportType.STDIO,
                command='npx',
                args=['-y', '@modelcontextprotocol/server-filesystem'],
                category='Sistema de Archivos',
                author='Anthropic',
                documentation_url='https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem',
                installation_instructions='npm install -g @modelcontextprotocol/server-filesystem'
            ),
            'git': MCPServerTemplate(
                name='git',
                description='Servidor MCP para operaciones con repositorios Git',
                transport_type=MCPTransportType.STDIO,
                command='npx',
                args=['-y', '@modelcontextprotocol/server-git'],
                category='Control de Versiones',
                author='Anthropic',
                documentation_url='https://github.com/modelcontextprotocol/servers/tree/main/src/git',
                installation_instructions='npm install -g @modelcontextprotocol/server-git'
            ),
            'postgres': MCPServerTemplate(
                name='postgres',
                description='Servidor MCP para acceso a bases de datos PostgreSQL',
                transport_type=MCPTransportType.STDIO,
                command='npx',
                args=['-y', '@modelcontextprotocol/server-postgres'],
                env={'POSTGRES_CONNECTION_STRING': 'postgresql://user:password@localhost:5432/database'},
                category='Base de Datos',
                author='Anthropic',
                documentation_url='https://github.com/modelcontextprotocol/servers/tree/main/src/postgres',
                installation_instructions='npm install -g @modelcontextprotocol/server-postgres'
            ),
            'puppeteer': MCPServerTemplate(
                name='puppeteer',
                description='Servidor MCP para automatización de navegador web',
                transport_type=MCPTransportType.STDIO,
                command='npx',
                args=['-y', '@modelcontextprotocol/server-puppeteer'],
                category='Web',
                author='Anthropic',
                documentation_url='https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer',
                installation_instructions='npm install -g @modelcontextprotocol/server-puppeteer'
            ),
            'docker': MCPServerTemplate(
                name='docker',
                description='Servidor MCP para gestión de contenedores Docker',
                transport_type=MCPTransportType.STDIO,
                command='python',
                args=['-m', 'mcp_docker_server'],
                category='DevOps',
                author='Community',
                documentation_url='https://github.com/docker/mcp-server',
                installation_instructions='pip install mcp-docker-server'
            ),
            'vscode': MCPServerTemplate(
                name='vscode',
                description='Servidor MCP para integración con Visual Studio Code',
                transport_type=MCPTransportType.SSE,
                url='http://localhost:3001/mcp',
                category='Desarrollo',
                author='Community',
                documentation_url='https://github.com/microsoft/vscode-mcp',
                installation_instructions='Instalar extensión MCP en VS Code'
            ),
            'mcpcontrol': MCPServerTemplate(
                name='mcpcontrol',
                description='Servidor MCP para control de sistema Windows',
                transport_type=MCPTransportType.SSE,
                url='http://localhost:3232/mcp',
                category='Sistema',
                author='claude-did-this',
                documentation_url='https://github.com/claude-did-this/MCPControl',
                installation_instructions='npm install -g mcp-control'
            )
        }
        
        self.server_templates.update(default_templates)
        
        # Cargar plantillas personalizadas si existen
        if self.templates_config_file.exists():
            try:
                with open(self.templates_config_file, 'r', encoding='utf-8') as f:
                    custom_templates = yaml.safe_load(f)
                
                for template_data in custom_templates.get('templates', []):
                    template = MCPServerTemplate(**template_data)
                    self.server_templates[template.name] = template
                
                logger.info(f"Cargadas {len(custom_templates.get('templates', []))} plantillas personalizadas")
                
            except Exception as e:
                logger.error(f"Error cargando plantillas personalizadas: {e}")
    
    def add_server_from_template(self, template_name: str, server_name: str, 
                                custom_config: Optional[Dict[str, Any]] = None) -> bool:
        """Añade un servidor basado en una plantilla"""
        template = self.server_templates.get(template_name)
        if not template:
            logger.error(f"Plantilla {template_name} no encontrada")
            return False
        
        if server_name in self.configured_servers:
            logger.error(f"Servidor {server_name} ya existe")
            return False
        
        # Crear configuración base desde plantilla
        config = MCPServerConfig(
            name=server_name,
            transport_type=template.transport_type,
            command=template.command,
            args=template.args.copy() if template.args else None,
            url=template.url,
            env=template.env.copy() if template.env else None
        )
        
        # Aplicar configuración personalizada
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        self.configured_servers[server_name] = config
        self._save_configurations()
        
        logger.info(f"Servidor {server_name} añadido desde plantilla {template_name}")
        return True
    
    def add_custom_server(self, config: MCPServerConfig) -> bool:
        """Añade un servidor con configuración personalizada"""
        if config.name in self.configured_servers:
            logger.error(f"Servidor {config.name} ya existe")
            return False
        
        self.configured_servers[config.name] = config
        self._save_configurations()
        
        logger.info(f"Servidor personalizado {config.name} añadido")
        return True
    
    def remove_server(self, server_name: str) -> bool:
        """Remueve un servidor configurado"""
        if server_name not in self.configured_servers:
            logger.error(f"Servidor {server_name} no encontrado")
            return False
        
        del self.configured_servers[server_name]
        self._save_configurations()
        
        logger.info(f"Servidor {server_name} removido")
        return True
    
    def update_server(self, server_name: str, updates: Dict[str, Any]) -> bool:
        """Actualiza la configuración de un servidor"""
        if server_name not in self.configured_servers:
            logger.error(f"Servidor {server_name} no encontrado")
            return False
        
        config = self.configured_servers[server_name]
        
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"Atributo {key} no válido para configuración de servidor")
        
        self._save_configurations()
        
        logger.info(f"Servidor {server_name} actualizado")
        return True
    
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """Obtiene la configuración de un servidor"""
        return self.configured_servers.get(server_name)
    
    def list_configured_servers(self) -> List[str]:
        """Lista todos los servidores configurados"""
        return list(self.configured_servers.keys())
    
    def list_available_templates(self) -> List[str]:
        """Lista todas las plantillas disponibles"""
        return list(self.server_templates.keys())
    
    def get_template(self, template_name: str) -> Optional[MCPServerTemplate]:
        """Obtiene una plantilla de servidor"""
        return self.server_templates.get(template_name)
    
    def get_all_server_configs(self) -> Dict[str, MCPServerConfig]:
        """Obtiene todas las configuraciones de servidor"""
        return self.configured_servers.copy()
    
    def get_servers_by_category(self) -> Dict[str, List[str]]:
        """Obtiene servidores agrupados por categoría"""
        servers_by_category = {}
        
        for server_name, config in self.configured_servers.items():
            # Buscar plantilla para obtener categoría
            template = None
            for tmpl in self.server_templates.values():
                if (tmpl.command == config.command and 
                    tmpl.transport_type == config.transport_type):
                    template = tmpl
                    break
            
            category = template.category if template else 'General'
            
            if category not in servers_by_category:
                servers_by_category[category] = []
            
            servers_by_category[category].append(server_name)
        
        return servers_by_category
    
    def validate_server_config(self, config: MCPServerConfig) -> List[str]:
        """Valida una configuración de servidor y retorna errores"""
        errors = []
        
        if not config.name:
            errors.append("Nombre de servidor requerido")
        
        if config.transport_type == MCPTransportType.STDIO:
            if not config.command:
                errors.append("Comando requerido para transporte STDIO")
        elif config.transport_type == MCPTransportType.SSE:
            if not config.url:
                errors.append("URL requerida para transporte SSE")
        
        if config.timeout <= 0:
            errors.append("Timeout debe ser mayor a 0")
        
        if config.retry_attempts < 0:
            errors.append("Intentos de reintento no pueden ser negativos")
        
        return errors
    
    def export_configuration(self, file_path: str):
        """Exporta la configuración completa a un archivo"""
        export_data = {
            'servers': [asdict(config) for config in self.configured_servers.values()],
            'templates': [asdict(template) for template in self.server_templates.values()]
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración exportada a {file_path}")
            
        except Exception as e:
            logger.error(f"Error exportando configuración: {e}")
            raise
    
    def import_configuration(self, file_path: str, merge: bool = True):
        """Importa configuración desde un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    import_data = yaml.safe_load(f)
                else:
                    import_data = json.load(f)
            
            if not merge:
                self.configured_servers.clear()
                self.server_templates.clear()
            
            # Importar servidores
            for server_data in import_data.get('servers', []):
                config = MCPServerConfig(**server_data)
                self.configured_servers[config.name] = config
            
            # Importar plantillas
            for template_data in import_data.get('templates', []):
                template = MCPServerTemplate(**template_data)
                self.server_templates[template.name] = template
            
            self._save_configurations()
            logger.info(f"Configuración importada desde {file_path}")
            
        except Exception as e:
            logger.error(f"Error importando configuración: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del registro"""
        enabled_servers = sum(1 for config in self.configured_servers.values() if config.enabled)
        
        transport_stats = {}
        for config in self.configured_servers.values():
            transport = config.transport_type.value
            transport_stats[transport] = transport_stats.get(transport, 0) + 1
        
        return {
            'total_servers': len(self.configured_servers),
            'enabled_servers': enabled_servers,
            'disabled_servers': len(self.configured_servers) - enabled_servers,
            'available_templates': len(self.server_templates),
            'transport_distribution': transport_stats,
            'categories': len(self.get_servers_by_category())
        }

