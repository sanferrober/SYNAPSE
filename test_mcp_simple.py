#!/usr/bin/env python3
"""
Script de prueba simplificado para el sistema refactorizado de herramientas MCP
"""

import sys
import os
import json

# Agregar el directorio al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mcp_config_manager():
    """Prueba el gestor de configuración MCP"""
    print("🧪 Probando Gestor de Configuración MCP")
    print("=" * 60)
    
    try:
        from mcp_integration.mcp_config_manager import MCPConfigManager
        config_manager = MCPConfigManager()
        
        print("\n✅ MCPConfigManager importado correctamente")
        
        # Mostrar estado de configuración
        print("\n📋 Estado de Configuración:")
        print(f"   Archivo de configuración: {config_manager.config_file}")
        print(f"   Archivo existe: {os.path.exists(config_manager.config_file)}")
        
        # Verificar API keys
        services = ['brave_search', 'tavily_search', 'github', 'openweather', 'newsapi']
        print("\n🔑 Estado de API Keys:")
        for service in services:
            has_key = config_manager.has_api_key(service)
            print(f"   {service}: {'✅ Configurada' if has_key else '❌ No configurada'}")
        
        # Mostrar herramientas gratuitas
        free_tools = config_manager.config.get('free_tools', [])
        print(f"\n🆓 Herramientas Gratuitas: {len(free_tools)}")
        for tool in free_tools[:5]:  # Mostrar solo las primeras 5
            print(f"   - {tool}")
        
        # Mostrar instrucciones
        print("\n📝 Instrucciones de Configuración:")
        print(config_manager.get_config_instructions())
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_real_mcp_tools():
    """Prueba las herramientas MCP reales"""
    print("\n\n🧪 Probando Herramientas MCP Reales")
    print("=" * 60)
    
    try:
        # Intentar importar sin todas las dependencias
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_integration'))
        
        # Importar solo lo necesario
        from real_mcp_tools import execute_real_mcp_tool
        
        print("\n✅ real_mcp_tools importado correctamente")
        
        # Probar herramientas gratuitas
        test_cases = [
            {
                'tool_id': 'web_search_mcp',
                'parameters': {'query': 'Python programming'},
                'description': 'Búsqueda web con DuckDuckGo'
            },
            {
                'tool_id': 'github_mcp',
                'parameters': {'query': 'machine learning', 'language': 'python'},
                'description': 'Búsqueda en GitHub'
            }
        ]
        
        print("\n🔧 Ejecutando Pruebas de Herramientas Gratuitas:")
        for test in test_cases:
            print(f"\n📌 {test['description']}")
            print(f"   Tool ID: {test['tool_id']}")
            
            result = execute_real_mcp_tool(test['tool_id'], test['parameters'])
            
            if result['success']:
                print(f"   ✅ Éxito en {result.get('execution_time', 0):.2f}s")
                print(f"   📊 Resultado (primeros 100 caracteres):")
                print(f"      {result['result'][:100]}...")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al probar herramientas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Sistema Refactorizado de Herramientas MCP - Prueba Simplificada")
    print("=" * 70)
    
    # Probar gestor de configuración
    config_success = test_mcp_config_manager()
    
    # Probar herramientas reales
    tools_success = test_real_mcp_tools()
    
    # Resumen
    print("\n\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 70)
    print(f"✅ Gestor de Configuración: {'Exitoso' if config_success else 'Fallido'}")
    print(f"✅ Herramientas MCP: {'Exitoso' if tools_success else 'Fallido'}")
    
    if config_success and tools_success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. Configura las API Keys en mcp_api_config.json")
        print("   2. Reinicia el servidor Synapse")
        print("   3. Accede al panel 'MCP Config' en el frontend")
        print("   4. Configura las API Keys desde la interfaz web")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return config_success and tools_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)