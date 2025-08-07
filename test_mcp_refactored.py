#!/usr/bin/env python3
"""
Script de prueba para el sistema refactorizado de herramientas MCP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_integration.real_mcp_tools import execute_real_mcp_tool
from mcp_integration.mcp_config_manager import MCPConfigManager
import json

def test_mcp_tools_refactored():
    """Prueba el sistema refactorizado de herramientas MCP"""
    
    print("🧪 Probando Sistema Refactorizado de Herramientas MCP")
    print("=" * 60)
    
    # Inicializar gestor de configuración
    config_manager = MCPConfigManager()
    
    # Mostrar estado de configuración
    print("\n📋 Estado de Configuración de API Keys:")
    print(config_manager.get_config_instructions())
    
    # Herramientas a probar
    test_cases = [
        {
            'tool_id': 'web_search_mcp',
            'parameters': {'query': 'artificial intelligence 2024'},
            'description': 'Búsqueda web gratuita (DuckDuckGo)'
        },
        {
            'tool_id': 'github_mcp',
            'parameters': {'query': 'machine learning', 'language': 'python'},
            'description': 'Búsqueda en GitHub (API pública)'
        },
        {
            'tool_id': 'wikipedia_mcp',
            'parameters': {'query': 'quantum computing'},
            'description': 'Búsqueda en Wikipedia (gratuita)'
        },
        {
            'tool_id': 'brave_search_mcp',
            'parameters': {'query': 'latest technology news'},
            'description': 'Búsqueda con Brave (requiere API key)'
        },
        {
            'tool_id': 'tavily_search',
            'parameters': {'query': 'climate change solutions'},
            'description': 'Búsqueda con Tavily (requiere API key)'
        },
        {
            'tool_id': 'weather_mcp',
            'parameters': {'city': 'Madrid'},
            'description': 'Clima con OpenWeather (requiere API key)'
        },
        {
            'tool_id': 'news_mcp',
            'parameters': {'query': 'artificial intelligence'},
            'description': 'Noticias con NewsAPI (requiere API key)'
        }
    ]
    
    print("\n🔧 Ejecutando Pruebas:")
    print("-" * 60)
    
    results = []
    
    for test in test_cases:
        print(f"\n📌 Probando: {test['tool_id']}")
        print(f"   Descripción: {test['description']}")
        print(f"   Parámetros: {test['parameters']}")
        
        result = execute_real_mcp_tool(test['tool_id'], test['parameters'])
        
        # Analizar resultado
        if result['success']:
            print(f"   ✅ Éxito: Ejecutado en {result['execution_time']}s")
            if 'tool_name' in result:
                print(f"   🔧 Herramienta usada: {result['tool_name']}")
            print(f"   📊 Resultado (primeros 200 caracteres):")
            print(f"      {result['result'][:200]}...")
        else:
            print(f"   ❌ Error: {result['error'][:200]}...")
            if 'missing_api_key' in result:
                print(f"   🔑 API Key faltante: {result['missing_api_key']}")
                print(f"   📁 Archivo de configuración: {result.get('config_file', 'N/A')}")
        
        results.append({
            'tool_id': test['tool_id'],
            'success': result['success'],
            'execution_time': result.get('execution_time', 0),
            'error': result.get('error', '') if not result['success'] else None,
            'missing_api_key': result.get('missing_api_key')
        })
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n✅ Exitosas: {successful}/{len(results)}")
    print(f"❌ Fallidas: {failed}/{len(results)}")
    
    # Agrupar por tipo
    free_tools = ['web_search_mcp', 'github_mcp', 'wikipedia_mcp']
    paid_tools = [r for r in results if r['tool_id'] not in free_tools]
    
    print("\n🆓 Herramientas Gratuitas:")
    for result in results:
        if result['tool_id'] in free_tools:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['tool_id']}")
    
    print("\n💰 Herramientas que Requieren API Key:")
    for result in paid_tools:
        status = "✅" if result['success'] else "❌"
        api_key = result.get('missing_api_key', '')
        if api_key:
            print(f"   {status} {result['tool_id']} - Falta: {api_key}")
        else:
            print(f"   {status} {result['tool_id']}")
    
    # Guardar resultados detallados
    output_file = 'test_mcp_refactored_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': result.get('timestamp', ''),
            'summary': {
                'total_tests': len(results),
                'successful': successful,
                'failed': failed
            },
            'results': results,
            'missing_keys': config_manager.get_missing_keys_info()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # Recomendaciones finales
    if failed > 0:
        print("\n💡 RECOMENDACIONES:")
        print("-" * 40)
        missing_keys = config_manager.get_missing_keys_info()
        if missing_keys:
            print("Para habilitar todas las herramientas, configura las siguientes API Keys:")
            for service, description in missing_keys.items():
                print(f"   • {service}: {description}")
            print(f"\n📁 Edita el archivo: {os.path.abspath(config_manager.config_file)}")
            print("   O configura las variables de entorno correspondientes.")
    
    return successful == len(results)

if __name__ == "__main__":
    success = test_mcp_tools_refactored()
    sys.exit(0 if success else 1)