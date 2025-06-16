#!/usr/bin/env python3
"""
Prueba corregida para verificar si las herramientas MCP están simuladas
"""

import requests
import json
import time

def test_mcp_tool_directly():
    """Prueba directa de herramientas MCP con endpoint correcto"""
    
    print("🔍 PRUEBA DIRECTA: HERRAMIENTAS MCP (ENDPOINT CORREGIDO)")
    print("=" * 55)
    
    base_url = "http://localhost:5000"
    
    # Primero obtener la lista de herramientas disponibles
    print("\n📋 Obteniendo lista de herramientas...")
    try:
        tools_response = requests.get(f"{base_url}/api/tools")
        if tools_response.status_code == 200:
            tools_data = tools_response.json()
            print(f"✅ {tools_data['enabled']} herramientas disponibles")
            
            # Mostrar algunas herramientas
            if 'tools' in tools_data:
                for i, tool in enumerate(tools_data['tools'][:5]):
                    print(f"   {i+1}. {tool.get('name', 'N/A')} - {tool.get('category', 'N/A')}")
        else:
            print(f"❌ Error obteniendo herramientas: {tools_response.status_code}")
    except Exception as e:
        print(f"💥 Error: {e}")
    
    # Test 1: Probar herramienta GitHub con endpoint correcto
    print("\n🧪 PRUEBA 1: GitHub Search - 'python machine learning'")
    try:
        response1 = requests.post(f"{base_url}/api/mcp/tools/github_search/execute", 
                                json={
                                    "query": "python machine learning",
                                    "language": "python"
                                }, timeout=15)
        
        print(f"📊 Status Code 1: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Respuesta 1 recibida: {len(str(result1))} chars")
            print(f"📊 Resultado 1: {str(result1)[:300]}...")
        else:
            print(f"❌ Error 1: {response1.status_code}")
            print(f"📝 Respuesta 1: {response1.text[:200]}")
            result1 = None
            
    except Exception as e:
        print(f"💥 Error en prueba 1: {e}")
        result1 = None
    
    time.sleep(3)
    
    # Test 2: Probar la misma herramienta con consulta diferente
    print("\n🧪 PRUEBA 2: GitHub Search - 'javascript react'")
    try:
        response2 = requests.post(f"{base_url}/api/mcp/tools/github_search/execute", 
                                json={
                                    "query": "javascript react",
                                    "language": "javascript"
                                }, timeout=15)
        
        print(f"📊 Status Code 2: {response2.status_code}")
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Respuesta 2 recibida: {len(str(result2))} chars")
            print(f"📊 Resultado 2: {str(result2)[:300]}...")
        else:
            print(f"❌ Error 2: {response2.status_code}")
            print(f"📝 Respuesta 2: {response2.text[:200]}")
            result2 = None
            
    except Exception as e:
        print(f"💥 Error en prueba 2: {e}")
        result2 = None
    
    # Comparar resultados
    print("\n" + "=" * 55)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("=" * 55)
    
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
        
        print(f"\n📋 MUESTRA DE RESULTADO SIMULADO:")
        print(f"   {str1[:400]}...")
        
        return False
    else:
        print("\n✅ VEREDICTO: HERRAMIENTAS POSIBLEMENTE REALES")
        print("💡 Los resultados son diferentes para consultas diferentes")
        print("🌐 Las herramientas MCP podrían estar usando APIs reales")
        
        # Buscar indicadores de datos reales
        real_indicators = ['repositorios', 'encontrados', 'API', 'GitHub', 'resultados', 'stars', 'forks']
        found_indicators = []
        
        for indicator in real_indicators:
            if indicator in str1 or indicator in str2:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"🔍 Indicadores reales encontrados: {', '.join(found_indicators)}")
        
        return True

def test_web_search_tool():
    """Prueba herramienta de búsqueda web con endpoint correcto"""
    
    print("\n🌐 PRUEBA: WEB SEARCH")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.post(f"{base_url}/api/mcp/tools/web_search/execute", 
                               json={
                                   "query": "artificial intelligence 2024"
                               }, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Web Search respuesta: {len(str(result))} chars")
            print(f"📊 Resultado: {str(result)[:400]}...")
            
            # Buscar indicadores de búsqueda real
            result_str = str(result).lower()
            if 'duckduckgo' in result_str or 'tiempo de respuesta' in result_str or 'resultados encontrados' in result_str:
                print("🌐 Indicadores de búsqueda real encontrados")
                return True
            else:
                print("🤖 Parece ser simulación")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_available_mcp_tools():
    """Prueba diferentes herramientas MCP disponibles"""
    
    print("\n🔧 PRUEBA: HERRAMIENTAS MCP DISPONIBLES")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Lista de herramientas a probar
    tools_to_test = [
        ("github_search", {"query": "python", "language": "python"}),
        ("web_search", {"query": "test search"}),
        ("duckduckgo_search", {"query": "artificial intelligence"}),
        ("brave_search", {"query": "machine learning"})
    ]
    
    working_tools = 0
    
    for tool_name, params in tools_to_test:
        print(f"\n🧪 Probando: {tool_name}")
        try:
            response = requests.post(f"{base_url}/api/mcp/tools/{tool_name}/execute", 
                                   json=params, timeout=10)
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Funciona: {len(str(result))} chars")
                working_tools += 1
                
                # Buscar indicadores de datos reales
                result_str = str(result).lower()
                if any(indicator in result_str for indicator in ['api', 'encontrados', 'resultados', 'tiempo']):
                    print(f"   🌐 Posiblemente real")
                else:
                    print(f"   🤖 Posiblemente simulado")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print(f"\n📊 Herramientas funcionando: {working_tools}/{len(tools_to_test)}")
    return working_tools > 0

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DIRECTAS DE HERRAMIENTAS MCP")
    print("=" * 55)
    
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
    tools_available = test_available_mcp_tools()
    github_real = test_mcp_tool_directly()
    web_real = test_web_search_tool()
    
    print("\n" + "=" * 55)
    print("🎯 RESUMEN FINAL")
    print("=" * 55)
    
    if tools_available:
        print("✅ Algunas herramientas MCP están respondiendo")
    else:
        print("❌ Ninguna herramienta MCP está respondiendo")
    
    if github_real or web_real:
        print("✅ Al menos algunas herramientas MCP parecen reales")
        print(f"🐙 GitHub Search: {'REAL' if github_real else 'SIMULADO'}")
        print(f"🌐 Web Search: {'REAL' if web_real else 'SIMULADO'}")
    else:
        print("❌ TODAS las herramientas MCP están simuladas o no funcionan")
        print("🔧 Necesita revisión de la implementación")
    
    exit(0 if (github_real or web_real or tools_available) else 1)