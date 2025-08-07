"""
Módulo de gestión de configuración de API Keys para herramientas MCP
"""

import json
import os
from typing import Dict, List, Optional

class MCPConfigManager:
    """Gestor de configuración de API Keys para herramientas MCP"""
    
    def __init__(self, config_file: str = "mcp_api_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self._load_env_vars()
    
    def _load_config(self) -> Dict:
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Archivo de configuración {self.config_file} no encontrado")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear {self.config_file}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Retorna configuración por defecto"""
        return {
            "api_keys": {},
            "fallback_tools": {},
            "free_tools": ["web_search_mcp", "duckduckgo_mcp", "github_mcp"]
        }
    
    def _load_env_vars(self):
        """Carga API keys desde variables de entorno si están disponibles"""
        env_mapping = {
            "BRAVE_API_KEY": "brave_search",
            "TAVILY_API_KEY": "tavily_search",
            "FIRECRAWL_API_KEY": "firecrawl",
            "GITHUB_TOKEN": "github",
            "OPENWEATHER_API_KEY": "openweather",
            "NEWSAPI_KEY": "newsapi"
        }
        
        for env_var, config_key in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value and config_key in self.config.get("api_keys", {}):
                self.config["api_keys"][config_key]["key"] = env_value
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Obtiene la API key para un servicio específico"""
        if service in self.config.get("api_keys", {}):
            key = self.config["api_keys"][service].get("key", "")
            if key and key != "":
                return key
        return None
    
    def has_api_key(self, service: str) -> bool:
        """Verifica si existe una API key configurada para el servicio"""
        key = self.get_api_key(service)
        return key is not None and key != ""
    
    def get_fallback_tools(self, tool_id: str) -> List[str]:
        """Obtiene herramientas alternativas para una herramienta específica"""
        return self.config.get("fallback_tools", {}).get(tool_id, [])
    
    def is_free_tool(self, tool_id: str) -> bool:
        """Verifica si una herramienta es gratuita (no requiere API key)"""
        return tool_id in self.config.get("free_tools", [])
    
    def get_missing_keys_info(self) -> Dict[str, str]:
        """Obtiene información sobre las API keys faltantes"""
        missing = {}
        for service, info in self.config.get("api_keys", {}).items():
            if not self.has_api_key(service) and info.get("required", True):
                missing[service] = info.get("description", "API Key required")
        return missing
    
    def save_config(self):
        """Guarda la configuración actual en el archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error al guardar configuración: {e}")
            return False
    
    def update_api_key(self, service: str, key: str) -> bool:
        """Actualiza una API key específica"""
        if service in self.config.get("api_keys", {}):
            self.config["api_keys"][service]["key"] = key
            return self.save_config()
        return False

    def update_api_key(self, service: str, api_key: str) -> bool:
        """
        Actualiza una API key en la configuración

        Args:
            service: Nombre del servicio
            api_key: Nueva API key

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Cargar configuración actual
            self.load_config()

            # Actualizar la API key
            if 'api_keys' not in self.config:
                self.config['api_keys'] = {}

            if service not in self.config['api_keys']:
                self.config['api_keys'][service] = {}

            self.config['api_keys'][service]['key'] = api_key

            # Guardar configuración
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            # Recargar configuración
            self.load_config()

            return True

        except Exception as e:
            print(f"Error actualizando API key para {service}: {str(e)}")
            return False

    def get_config_instructions(self) -> str:
        """Genera instrucciones para configurar las API keys"""
        instructions = "📋 Configuración de API Keys para Herramientas MCP\n"
        instructions += "=" * 50 + "\n\n"
        
        instructions += "Para usar todas las herramientas MCP, necesitas configurar las siguientes API Keys:\n\n"
        
        for service, info in self.config.get("api_keys", {}).items():
            status = "✅" if self.has_api_key(service) else "❌"
            required = "Requerida" if info.get("required", True) else "Opcional"
            instructions += f"{status} {service.upper()}: {required}\n"
            if not self.has_api_key(service):
                instructions += f"   → {info.get('description', 'API Key needed')}\n"
        
        instructions += f"\n📁 Archivo de configuración: {os.path.abspath(self.config_file)}\n"
        instructions += "\n💡 También puedes configurar las API Keys usando variables de entorno:\n"
        instructions += "   - BRAVE_API_KEY\n"
        instructions += "   - TAVILY_API_KEY\n"
        instructions += "   - FIRECRAWL_API_KEY\n"
        instructions += "   - GITHUB_TOKEN\n"
        instructions += "   - OPENWEATHER_API_KEY\n"
        instructions += "   - NEWSAPI_KEY\n"
        
        return instructions