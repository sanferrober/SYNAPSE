#!/usr/bin/env python3
"""
Verificación detallada de la respuesta de GitHub MCP
"""

import requests
import json

def verify_github_mcp_response():
    """Verifica si GitHub MCP está devolviendo datos reales o simulados"""
    
    print("🔍 VERIFICACIÓN DETALLADA: GITHUB MCP")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Hacer consulta específica a GitHub MCP
        response = requests.post(f"{base_url}/api/mcp/tools/github_mcp/execute", 
                               json={
                                   "query": "python machine learning",
                                   "language": "python"
                               }, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Respuesta recibida: {len(str(result))} chars")
            print(f"📊 Tipo de respuesta: {type(result)}")
            
            # Mostrar estructura de la respuesta
            print("\n📋 ESTRUCTURA DE LA RESPUESTA:")
            print("-" * 30)
            
            if isinstance(result, dict):
                for key in result.keys():
                    value = result[key]
                    print(f"🔑 {key}: {type(value)} - {len(str(value))} chars")
                    
                    # Mostrar muestra del contenido
                    if isinstance(value, (str, int, float)):
                        print(f"   📝 Valor: {str(value)[:100]}...")
                    elif isinstance(value, list) and len(value) > 0:
                        print(f"   📝 Lista con {len(value)} elementos")
                        if len(value) > 0:
                            print(f"   📝 Primer elemento: {str(value[0])[:100]}...")
                    elif isinstance(value, dict):
                        print(f"   📝 Dict con {len(value)} claves: {list(value.keys())[:5]}")
            
            # Buscar indicadores específicos de datos reales de GitHub
            result_str = str(result).lower()
            
            print("\n🔍 ANÁLISIS DE CONTENIDO:")
            print("-" * 25)
            
            # Indicadores de datos reales de GitHub
            real_github_indicators = [
                ('github.com', 'URLs de GitHub'),
                ('stars', 'Estrellas de repositorios'),
                ('forks', 'Forks de repositorios'),
                ('created_at', 'Fechas de creación'),
                ('updated_at', 'Fechas de actualización'),
                ('owner', 'Propietarios de repos'),
                ('html_url', 'URLs HTML'),
                ('clone_url', 'URLs de clonado'),
                ('language', 'Lenguajes de programación'),
                ('description', 'Descripciones de repos')
            ]
            
            found_real_indicators = []
            for indicator, description in real_github_indicators:
                if indicator in result_str:
                    found_real_indicators.append((indicator, description))
            
            # Indicadores de simulación
            simulation_indicators = [
                ('simulación', 'Texto de simulación'),
                ('ficticio', 'Datos ficticios'),
                ('ejemplo', 'Datos de ejemplo'),
                ('demo', 'Datos de demostración'),
                ('placeholder', 'Datos placeholder')
            ]
            
            found_simulation_indicators = []
            for indicator, description in simulation_indicators:
                if indicator in result_str:
                    found_simulation_indicators.append((indicator, description))
            
            print(f"🌐 Indicadores REALES encontrados: {len(found_real_indicators)}")
            for indicator, desc in found_real_indicators[:5]:
                print(f"   ✅ {indicator} - {desc}")
            
            print(f"🤖 Indicadores SIMULADOS encontrados: {len(found_simulation_indicators)}")
            for indicator, desc in found_simulation_indicators:
                print(f"   ❌ {indicator} - {desc}")
            
            # Veredicto
            print("\n" + "=" * 40)
            print("🎯 VEREDICTO GITHUB MCP")
            print("=" * 40)
            
            if len(found_real_indicators) >= 5 and len(found_simulation_indicators) == 0:
                print("✅ REAL: GitHub MCP está usando la API real de GitHub")
                print(f"🌐 {len(found_real_indicators)} indicadores reales encontrados")
                print("🎉 Los datos provienen de repositorios reales")
                
                # Mostrar muestra de datos reales
                if 'raw_data' in result and isinstance(result['raw_data'], dict):
                    if 'items' in result['raw_data'] and len(result['raw_data']['items']) > 0:
                        first_repo = result['raw_data']['items'][0]
                        print(f"\n📊 MUESTRA DE REPOSITORIO REAL:")
                        print(f"   🏷️ Nombre: {first_repo.get('name', 'N/A')}")
                        print(f"   👤 Owner: {first_repo.get('owner', {}).get('login', 'N/A')}")
                        print(f"   ⭐ Stars: {first_repo.get('stargazers_count', 'N/A')}")
                        print(f"   🍴 Forks: {first_repo.get('forks_count', 'N/A')}")
                        print(f"   🔗 URL: {first_repo.get('html_url', 'N/A')}")
                
                return True
                
            elif len(found_simulation_indicators) > 0:
                print("❌ SIMULADO: GitHub MCP está generando datos ficticios")
                print(f"🤖 {len(found_simulation_indicators)} indicadores de simulación")
                print("💡 Los datos NO provienen de la API real de GitHub")
                return False
                
            else:
                print("⚠️ INCIERTO: No se puede determinar con certeza")
                print("🔍 Se necesita más análisis")
                return False
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DETALLADA DE GITHUB MCP")
    print("=" * 45)
    
    success = verify_github_mcp_response()
    
    if success:
        print("\n🎉 CONFIRMADO: GitHub MCP usa API REAL")
    else:
        print("\n❌ CONFIRMADO: GitHub MCP está SIMULADO")
    
    exit(0 if success else 1)