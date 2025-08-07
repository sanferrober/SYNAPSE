#!/usr/bin/env python3
"""
Demostración del sistema refactorizado de herramientas MCP
"""

import json
import os
import time
from datetime import datetime

def demo_mcp_config():
    """Demuestra la configuración de API Keys MCP"""
    print("🔧 Demostración del Sistema de Configuración MCP")
    print("=" * 60)
    
    # Verificar si existe el archivo de configuración
    config_file = "mcp_api_config.json"
    
    if os.path.exists(config_file):
        print(f"✅ Archivo de configuración encontrado: {config_file}")
        
        # Leer y mostrar configuración
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("\n📋 Contenido de la configuración:")
        print(f"   - API Keys definidas: {len(config.get('api_keys', {}))}")
        print(f"   - Herramientas gratuitas: {len(config.get('free_tools', []))}")
        print(f"   - Herramientas con fallback: {len(config.get('fallback_tools', {}))}")
        
        print("\n🔑 Estado de API Keys:")
        for service, info in config.get('api_keys', {}).items():
            has_key = bool(info.get('key'))
            status = "✅ Configurada" if has_key else "❌ No configurada"
            print(f"   {service}: {status}")
            if not has_key:
                print(f"      Descripción: {info.get('description', 'N/A')}")
        
        print("\n🆓 Herramientas Gratuitas (primeras 5):")
        for tool in config.get('free_tools', [])[:5]:
            print(f"   - {tool}")
    else:
        print(f"❌ Archivo de configuración no encontrado: {config_file}")
        print("   Creando archivo de configuración de ejemplo...")
        
        # Crear configuración de ejemplo
        example_config = {
            "api_keys": {
                "brave_search": {
                    "key": "",
                    "description": "API Key para Brave Search",
                    "required": False
                },
                "tavily_search": {
                    "key": "",
                    "description": "API Key para Tavily Search",
                    "required": False
                }
            },
            "free_tools": [
                "web_search_mcp",
                "github_mcp",
                "wikipedia_mcp"
            ],
            "fallback_tools": {
                "brave_search_mcp": "web_search_mcp",
                "tavily_search": "web_search_mcp"
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Archivo creado: {config_file}")

def demo_tool_execution():
    """Demuestra la ejecución de herramientas MCP"""
    print("\n\n🚀 Demostración de Ejecución de Herramientas MCP")
    print("=" * 60)
    
    # Simular ejecución de herramientas
    tools_demo = [
        {
            'tool_id': 'web_search_mcp',
            'name': 'Búsqueda Web (DuckDuckGo)',
            'type': 'Gratuita',
            'parameters': {'query': 'artificial intelligence 2024'},
            'result': 'Resultados de búsqueda sobre IA en 2024...'
        },
        {
            'tool_id': 'github_mcp',
            'name': 'Búsqueda en GitHub',
            'type': 'Gratuita',
            'parameters': {'query': 'machine learning', 'language': 'python'},
            'result': 'Repositorios de ML en Python encontrados...'
        },
        {
            'tool_id': 'brave_search_mcp',
            'name': 'Búsqueda con Brave',
            'type': 'Requiere API Key',
            'parameters': {'query': 'latest tech news'},
            'result': 'Error: API Key no configurada. Usando fallback a DuckDuckGo...'
        }
    ]
    
    for tool in tools_demo:
        print(f"\n📌 {tool['name']} ({tool['type']})")
        print(f"   Tool ID: {tool['tool_id']}")
        print(f"   Parámetros: {tool['parameters']}")
        print(f"   Ejecutando...")
        time.sleep(0.5)  # Simular tiempo de ejecución
        print(f"   Resultado: {tool['result']}")

def show_integration_flow():
    """Muestra el flujo de integración"""
    print("\n\n📊 Flujo de Integración del Sistema Refactorizado")
    print("=" * 60)
    
    flow = """
    1. Usuario solicita ejecutar herramienta MCP
       ↓
    2. Sistema verifica en MCPConfigManager:
       - ¿La herramienta es gratuita?
       - ¿Tiene API Key configurada?
       - ¿Existe herramienta de fallback?
       ↓
    3. Decisión de ejecución:
       a) Herramienta gratuita → Ejecutar directamente
       b) API Key configurada → Ejecutar con API Key
       c) Sin API Key pero con fallback → Usar fallback
       d) Sin API Key y sin fallback → Retornar error informativo
       ↓
    4. Ejecutar herramienta y retornar resultado
    """
    
    print(flow)
    
    print("\n🎯 Beneficios del Sistema Refactorizado:")
    print("   ✅ No más simulaciones cuando faltan API Keys")
    print("   ✅ Mensajes de error claros e informativos")
    print("   ✅ Gestión centralizada de configuración")
    print("   ✅ Interfaz web para configurar API Keys")
    print("   ✅ Fallback automático a herramientas gratuitas")

def main():
    """Función principal"""
    print("🌟 SISTEMA REFACTORIZADO DE HERRAMIENTAS MCP")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar demostraciones
    demo_mcp_config()
    demo_tool_execution()
    show_integration_flow()
    
    # Resumen final
    print("\n\n" + "=" * 70)
    print("✅ RESUMEN DEL SISTEMA REFACTORIZADO")
    print("=" * 70)
    
    print("\n📁 Archivos Creados/Modificados:")
    files = [
        ("mcp_api_config.json", "Configuración de API Keys"),
        ("mcp_integration/mcp_config_manager.py", "Gestor de configuración"),
        ("mcp_integration/real_mcp_tools.py", "Herramientas MCP refactorizadas"),
        ("synapse-ui-new/src/components/MCPConfigPanel.js", "Panel de configuración UI"),
        ("synapse_server_final.py", "Endpoints de configuración agregados")
    ]
    
    for file, desc in files:
        exists = "✅" if os.path.exists(file) else "❓"
        print(f"   {exists} {file}")
        print(f"      → {desc}")
    
    print("\n💡 Próximos Pasos:")
    print("   1. Instalar dependencias: pip install -r requirements.txt")
    print("   2. Configurar API Keys en mcp_api_config.json")
    print("   3. Reiniciar el servidor Synapse")
    print("   4. Acceder al panel 'MCP Config' en el frontend")
    print("   5. Probar las herramientas MCP")
    
    print("\n🎉 ¡Sistema refactorizado listo para usar!")

if __name__ == "__main__":
    main()