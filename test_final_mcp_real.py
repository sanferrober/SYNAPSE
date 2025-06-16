#!/usr/bin/env python3
"""
Prueba final con IDs correctos de herramientas MCP
"""

import requests
import json
import time

def test_real_mcp_tools():
    """Prueba herramientas MCP reales con IDs correctos"""
    
    print("🔍 PRUEBA FINAL: HERRAMIENTAS MCP REALES")
    print("=" * 45)
    
    base_url = "http://localhost:5000"
    
    # Herramientas a probar con sus IDs correctos
    tools_to_test = [
        ("web_search", {"query": "python programming 2024"}, "Búsqueda Web"),
        ("brave_search_advanced", {"query": "machine learning frameworks"}, "Brave Search Advanced"),
        ("github_mcp", {"query": "artificial intelligence", "language": "python"}, "GitHub MCP"),
        ("duckduckgo_mcp", {"query": "javascript frameworks"}, "DuckDuckGo MCP"),
        ("tavily_search", {"query": "deep learning tutorials"}, "Tavily Search")
    ]
    
    results = []
    
    for tool_id, params, tool_name in tools_to_test:
        print(f"\n🧪 PROBANDO: {tool_name} ({tool_id})")
        print("-" * 40)
        
        try:
            # Hacer dos consultas diferentes para comparar
            print(f"📤 Consulta 1: {params}")
            response1 = requests.post(f"{base_url}/api/mcp/tools/{tool_id}/execute", 
                                    json=params, timeout=20)
            
            print(f"📊 Status 1: {response1.status_code}")
            
            if response1.status_code == 200:
                result1 = response1.json()
                print(f"✅ Respuesta 1: {len(str(result1))} chars")
                
                # Modificar parámetros para segunda consulta
                params2 = params.copy()
                if "query" in params2:
                    params2["query"] = params2["query"].replace("python", "javascript").replace("machine", "deep").replace("artificial", "natural")
                
                time.sleep(2)  # Pausa entre consultas
                
                print(f"📤 Consulta 2: {params2}")
                response2 = requests.post(f"{base_url}/api/mcp/tools/{tool_id}/execute", 
                                        json=params2, timeout=20)
                
                print(f"📊 Status 2: {response2.status_code}")
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    print(f"✅ Respuesta 2: {len(str(result2))} chars")
                    
                    # Comparar resultados
                    str1 = str(result1)
                    str2 = str(result2)
                    
                    if str1 == str2:
                        print("🤖 SIMULADO: Respuestas idénticas")
                        status = "SIMULADO"
                    else:
                        print("🌐 REAL: Respuestas diferentes")
                        status = "REAL"
                        
                        # Buscar indicadores de datos reales
                        real_indicators = [
                            'encontrados', 'resultados', 'tiempo de respuesta', 
                            'api', 'github', 'repositorios', 'stars', 'forks',
                            'duckduckgo', 'brave', 'tavily'
                        ]
                        
                        found_indicators = []
                        for indicator in real_indicators:
                            if indicator.lower() in str1.lower() or indicator.lower() in str2.lower():
                                found_indicators.append(indicator)
                        
                        if found_indicators:
                            print(f"🔍 Indicadores reales: {', '.join(found_indicators)}")
                    
                    results.append({
                        'tool_id': tool_id,
                        'tool_name': tool_name,
                        'status': status,
                        'response1_length': len(str1),
                        'response2_length': len(str2),
                        'sample_response': str1[:200]
                    })
                    
                else:
                    print(f"❌ Error en consulta 2: {response2.status_code}")
                    print(f"📝 Respuesta 2: {response2.text[:200]}")
            else:
                print(f"❌ Error en consulta 1: {response1.status_code}")
                print(f"📝 Respuesta 1: {response1.text[:200]}")
                
        except Exception as e:
            print(f"💥 Error: {e}")
    
    # Análisis final
    print("\n" + "=" * 45)
    print("📊 ANÁLISIS FINAL")
    print("=" * 45)
    
    if not results:
        print("❌ No se pudieron probar herramientas")
        return False
    
    real_tools = [r for r in results if r['status'] == 'REAL']
    simulated_tools = [r for r in results if r['status'] == 'SIMULADO']
    
    print(f"📈 Total herramientas probadas: {len(results)}")
    print(f"🌐 Herramientas REALES: {len(real_tools)}")
    print(f"🤖 Herramientas SIMULADAS: {len(simulated_tools)}")
    
    if real_tools:
        print(f"📊 Porcentaje REAL: {(len(real_tools)/len(results))*100:.1f}%")
        print("\n✅ HERRAMIENTAS REALES ENCONTRADAS:")
        for tool in real_tools:
            print(f"   🌐 {tool['tool_name']} ({tool['tool_id']})")
            print(f"      📏 Respuestas: {tool['response1_length']} / {tool['response2_length']} chars")
            print(f"      📝 Muestra: {tool['sample_response'][:100]}...")
    
    if simulated_tools:
        print("\n🤖 HERRAMIENTAS SIMULADAS:")
        for tool in simulated_tools:
            print(f"   🤖 {tool['tool_name']} ({tool['tool_id']})")
            print(f"      📝 Muestra: {tool['sample_response'][:100]}...")
    
    # Veredicto final
    print("\n" + "=" * 45)
    print("🎯 VEREDICTO FINAL")
    print("=" * 45)
    
    if len(real_tools) > 0:
        print("✅ ÉXITO: Herramientas MCP REALES funcionando")
        print(f"🌐 {len(real_tools)} herramientas usando APIs externas")
        print("🎉 El sistema Synapse tiene capacidades reales")
        return True
    else:
        print("❌ FALLO: Todas las herramientas están simuladas")
        print("🔧 Las herramientas MCP NO usan APIs reales")
        print("💡 Solo generan respuestas ficticias")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA DEFINITIVA: HERRAMIENTAS MCP REALES VS SIMULADAS")
    print("=" * 60)
    
    # Verificar servidor
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Servidor Synapse funcionando")
        else:
            print("❌ Servidor no responde")
            exit(1)
    except:
        print("❌ No se puede conectar al servidor")
        exit(1)
    
    # Ejecutar prueba
    success = test_real_mcp_tools()
    
    print(f"\n{'🎉 RESULTADO: HERRAMIENTAS REALES DETECTADAS' if success else '❌ RESULTADO: SOLO HERRAMIENTAS SIMULADAS'}")
    
    exit(0 if success else 1)