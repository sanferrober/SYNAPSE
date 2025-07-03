#!/usr/bin/env python3
"""
🔍 PRUEBA DIRECTA: Herramientas MCP de Búsqueda Web
Demuestra el funcionamiento directo de las herramientas MCP sin servidor
"""

import sys
import os
from datetime import datetime

# Agregar el directorio mcp_integration al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_integration'))

try:
    from real_mcp_tools import execute_real_mcp_tool
    print("✅ Módulo real_mcp_tools importado correctamente")
except ImportError as e:
    print(f"❌ Error importando real_mcp_tools: {e}")
    sys.exit(1)

def demo_web_search():
    """Demostración de búsqueda web con DuckDuckGo"""
    print("\n🔍 DEMOSTRACIÓN: Búsqueda Web con DuckDuckGo")
    print("=" * 50)
    
    # Consulta de ejemplo
    query = "inteligencia artificial tendencias 2024"
    print(f"📝 Consulta: {query}")
    
    # Ejecutar búsqueda
    print("⏳ Ejecutando búsqueda...")
    result = execute_real_mcp_tool('web_search_mcp', {'query': query})
    
    # Mostrar resultados
    if result.get('success'):
        print("✅ Búsqueda exitosa!")
        print(f"⏱️  Tiempo de ejecución: {result.get('execution_time', 'N/A')}s")
        print(f"🕐 Timestamp: {result.get('timestamp', 'N/A')}")
        
        # Mostrar el resultado
        result_text = result.get('result', '')
        if result_text:
            print("\n📄 RESULTADO DE LA BÚSQUEDA:")
            print("-" * 40)
            # Mostrar las primeras líneas del resultado
            lines = result_text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(line)
                if i > 20:  # Limitar a las primeras 20 líneas
                    print("... (resultado truncado)")
                    break
        
        # Mostrar datos raw si están disponibles
        if 'raw_data' in result:
            raw_data = result['raw_data']
            print(f"\n📊 DATOS TÉCNICOS:")
            print(f"   🔧 Herramienta: {result.get('tool_name', 'N/A')}")
            print(f"   🆔 ID: {result.get('tool_id', 'N/A')}")
            if isinstance(raw_data, dict):
                print(f"   📈 Campos en respuesta: {list(raw_data.keys())}")
    else:
        print("❌ Error en la búsqueda")
        print(f"   Error: {result.get('error', 'Error desconocido')}")
    
    return result

def demo_brave_search():
    """Demostración de búsqueda con Brave Search"""
    print("\n🦁 DEMOSTRACIÓN: Búsqueda con Brave Search")
    print("=" * 50)
    
    # Consulta de ejemplo
    query = "machine learning frameworks python 2024"
    print(f"📝 Consulta: {query}")
    
    # Ejecutar búsqueda
    print("⏳ Ejecutando búsqueda...")
    result = execute_real_mcp_tool('brave_search_mcp', {'query': query, 'count': 5})
    
    # Mostrar resultados
    if result.get('success'):
        print("✅ Búsqueda exitosa!")
        print(f"⏱️  Tiempo de ejecución: {result.get('execution_time', 'N/A')}s")
        
        # Mostrar el resultado
        result_text = result.get('result', '')
        if result_text:
            print("\n📄 RESULTADO DE LA BÚSQUEDA:")
            print("-" * 40)
            lines = result_text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(line)
                if i > 25:  # Limitar a las primeras 25 líneas
                    print("... (resultado truncado)")
                    break
    else:
        print("❌ Error en la búsqueda")
        print(f"   Error: {result.get('error', 'Error desconocido')}")
    
    return result

def demo_github_search():
    """Demostración de búsqueda en GitHub"""
    print("\n🐙 DEMOSTRACIÓN: Búsqueda en GitHub")
    print("=" * 50)
    
    # Consulta de ejemplo
    query = "react hooks tutorial"
    print(f"📝 Consulta: {query}")
    
    # Ejecutar búsqueda
    print("⏳ Ejecutando búsqueda...")
    result = execute_real_mcp_tool('github_mcp', {'query': query})
    
    # Mostrar resultados
    if result.get('success'):
        print("✅ Búsqueda exitosa!")
        print(f"⏱️  Tiempo de ejecución: {result.get('execution_time', 'N/A')}s")
        
        # Mostrar el resultado
        result_text = result.get('result', '')
        if result_text:
            print("\n📄 RESULTADO DE LA BÚSQUEDA:")
            print("-" * 40)
            lines = result_text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(line)
                if i > 20:  # Limitar a las primeras 20 líneas
                    print("... (resultado truncado)")
                    break
    else:
        print("❌ Error en la búsqueda")
        print(f"   Error: {result.get('error', 'Error desconocido')}")
    
    return result

def main():
    """Función principal"""
    print("🚀 DEMOSTRACIÓN DIRECTA: Herramientas MCP de Búsqueda Web")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1. Probar DuckDuckGo
    try:
        web_result = demo_web_search()
        results.append(('DuckDuckGo Web Search', web_result.get('success', False)))
    except Exception as e:
        print(f"❌ Error en DuckDuckGo: {e}")
        results.append(('DuckDuckGo Web Search', False))
    
    # 2. Probar Brave Search
    try:
        brave_result = demo_brave_search()
        results.append(('Brave Search', brave_result.get('success', False)))
    except Exception as e:
        print(f"❌ Error en Brave Search: {e}")
        results.append(('Brave Search', False))
    
    # 3. Probar GitHub Search
    try:
        github_result = demo_github_search()
        results.append(('GitHub Search', github_result.get('success', False)))
    except Exception as e:
        print(f"❌ Error en GitHub Search: {e}")
        results.append(('GitHub Search', False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for tool, success in results:
        status = "✅ Exitosa" if success else "❌ Falló"
        print(f"   {tool}: {status}")
    
    print(f"\n📈 Herramientas funcionando: {successful}/{total}")
    
    if successful > 0:
        print("\n🎉 ¡DEMOSTRACIÓN EXITOSA!")
        print("   Las herramientas MCP están recuperando información real de la web")
        print("   Synapse puede realizar búsquedas web efectivas")
    else:
        print("\n⚠️  Todas las herramientas están en modo simulación")
        print("   Esto es normal si no hay claves API configuradas")
    
    print(f"\n⏰ Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()