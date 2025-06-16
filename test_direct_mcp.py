#!/usr/bin/env python3
"""
Prueba simple para verificar si las herramientas MCP están simuladas
"""

import requests
import json
import time

def test_mcp_tool_directly():
    """Prueba directa de herramientas MCP"""
    
    print("🔍 PRUEBA DIRECTA: HERRAMIENTAS MCP")
    print("=" * 40)
    
    # Probar endpoint directo de herramientas MCP
    base_url = "http://localhost:5000"
    
    # Test 1: Probar herramienta GitHub con consulta específica
    print("\n🧪 PRUEBA 1: GitHub Search - 'python machine learning'")
    try:
        response1 = requests.post(f"{base_url}/api/tools/execute", 
                                json={
                                    "tool_id": "github_mcp",
                                    "parameters": {
                                        "query": "python machine learning",
                                        "language": "python"
                                    }
                                }, timeout=10)
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Respuesta 1 recibida: {len(str(result1))} chars")
            print(f"📊 Resultado 1: {str(result1)[:200]}...")
        else:
            print(f"❌ Error 1: {response1.status_code}")
            result1 = None
            
    except Exception as e:
        print(f"💥 Error en prueba 1: {e}")
        result1 = None
    
    time.sleep(2)
    
    # Test 2: Probar la misma herramienta con consulta diferente
    print("\n🧪 PRUEBA 2: GitHub Search - 'javascript react'")
    try:
        response2 = requests.post(f"{base_url}/api/tools/execute", 
                                json={
                                    "tool_id": "github_mcp",
                                    "parameters": {
                                        "query": "javascript react",
                                        "language": "javascript"
                                    }
                                }, timeout=10)
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Respuesta 2 recibida: {len(str(result2))} chars")
            print(f"📊 Resultado 2: {str(result2)[:200]}...")
        else:
            print(f"❌ Error 2: {response2.status_code}")
            result2 = None
            
    except Exception as e:
        print(f"💥 Error en prueba 2: {e}")
        result2 = None
    
    # Comparar resultados
    print("\n" + "=" * 40)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("=" * 40)
    
    if result1 is None or result2 is None:
        print("❌ No se pudieron obtener ambos resultados")
        return False
    
    # Convertir a strings para comparar
    str1 = str(result1)
    str2 = str(result2)
    
    print(f"📏 Longitud resultado 1: {len(str1)} chars")
    print(f"📏 Longitud resultado 2: {len(str2)} chars")
    
    if str1 == str2:
        print("\n❌ VEREDICTO: HERRAMIENTAS COMPLETAMENTE SIMULADAS")
        print("💡 Los resultados son idénticos para consultas diferentes")
        print("🔧 Las herramientas MCP NO están usando APIs reales")
        
        # Mostrar evidencia de simulación
        if "simulación" in str1.lower() or "ficticio" in str1.lower():
            print("📝 Evidencia: Contiene texto de simulación explícita")
        
        return False
    else:
        print("\n✅ VEREDICTO: HERRAMIENTAS POSIBLEMENTE REALES")
        print("💡 Los resultados son diferentes para consultas diferentes")
        print("🌐 Las herramientas MCP podrían estar usando APIs reales")
        
        # Buscar indicadores de datos reales
        real_indicators = ['repositorios', 'encontrados', 'API', 'GitHub', 'resultados']
        found_indicators = []
        
        for indicator in real_indicators:
            if indicator in str1 or indicator in str2:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"🔍 Indicadores reales encontrados: {', '.join(found_indicators)}")
        
        return True

def test_web_search_tool():
    """Prueba herramienta de búsqueda web"""
    
    print("\n🌐 PRUEBA: WEB SEARCH")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.post(f"{base_url}/api/tools/execute", 
                               json={
                                   "tool_id": "web_search_mcp",
                                   "parameters": {
                                       "query": "artificial intelligence 2024"
                                   }
                               }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Web Search respuesta: {len(str(result))} chars")
            print(f"📊 Resultado: {str(result)[:300]}...")
            
            # Buscar indicadores de búsqueda real
            result_str = str(result).lower()
            if 'duckduckgo' in result_str or 'tiempo de respuesta' in result_str:
                print("🌐 Indicadores de búsqueda real encontrados")
                return True
            else:
                print("🤖 Parece ser simulación")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DIRECTAS DE HERRAMIENTAS MCP")
    print("=" * 50)
    
    # Verificar que el servidor esté funcionando
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print("❌ Servidor no responde correctamente")
            exit(1)
    except:
        print("❌ No se puede conectar al servidor")
        exit(1)
    
    # Ejecutar pruebas
    github_real = test_mcp_tool_directly()
    web_real = test_web_search_tool()
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN FINAL")
    print("=" * 50)
    
    if github_real or web_real:
        print("✅ Al menos algunas herramientas MCP están funcionando")
        print(f"🐙 GitHub Search: {'REAL' if github_real else 'SIMULADO'}")
        print(f"🌐 Web Search: {'REAL' if web_real else 'SIMULADO'}")
    else:
        print("❌ TODAS las herramientas MCP están simuladas")
        print("🔧 Necesita revisión de la implementación")
    
    exit(0 if (github_real or web_real) else 1)