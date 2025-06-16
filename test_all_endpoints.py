#!/usr/bin/env python3
"""
Verificación completa de endpoints del servidor
"""

import requests
import json

def test_all_endpoints():
    """Prueba todos los endpoints del servidor"""
    
    base_url = "http://localhost:5000"
    
    endpoints_to_test = [
        # Endpoints básicos
        ("/api/health", "GET"),
        ("/api/tools", "GET"),
        ("/api/system/status", "GET"),
        
        # Endpoints de memoria
        ("/api/memory/all", "GET"),
        ("/api/memory/conversations", "GET"),
        ("/api/memory/preferences", "GET"),
        ("/api/memory/patterns", "GET"),
        ("/api/memory/stats", "GET"),
        
        # Endpoints de outputs
        ("/api/outputs/recent", "GET"),
        
        # Endpoints de MCP
        ("/api/mcp/tools", "GET"),
        
        # Endpoints de LLM
        ("/api/llm/config", "GET"),
    ]
    
    print("🔍 VERIFICACIÓN COMPLETA DE ENDPOINTS")
    print("=" * 50)
    
    working_endpoints = []
    broken_endpoints = []
    
    for endpoint, method in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"🔗 Probando: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json={}, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ OK - {response.status_code}")
                working_endpoints.append((endpoint, method, response.status_code))
                
                # Mostrar muestra de datos
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        keys = list(data.keys())[:3]
                        print(f"   📊 Datos: {keys}")
                    elif isinstance(data, list):
                        print(f"   📊 Lista: {len(data)} elementos")
                except:
                    print(f"   📊 Respuesta: {len(response.text)} chars")
                    
            else:
                print(f"   ❌ ERROR - {response.status_code}")
                broken_endpoints.append((endpoint, method, response.status_code))
                
        except Exception as e:
            print(f"   💥 EXCEPCIÓN - {str(e)}")
            broken_endpoints.append((endpoint, method, f"Exception: {str(e)}"))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 50)
    
    print(f"✅ Endpoints funcionando: {len(working_endpoints)}")
    for endpoint, method, status in working_endpoints:
        print(f"   {method} {endpoint} - {status}")
    
    print(f"\n❌ Endpoints con problemas: {len(broken_endpoints)}")
    for endpoint, method, status in broken_endpoints:
        print(f"   {method} {endpoint} - {status}")
    
    return working_endpoints, broken_endpoints

def test_specific_outputs_endpoint():
    """Prueba específica del endpoint de outputs"""
    
    print("\n🔍 PRUEBA ESPECÍFICA: ENDPOINT DE OUTPUTS")
    print("=" * 50)
    
    try:
        # Probar endpoint de outputs recientes
        url = "http://localhost:5000/api/outputs/recent"
        print(f"🔗 Probando: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        print(f"📊 Content: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos recibidos correctamente")
            print(f"📊 Estructura: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def check_server_routes():
    """Verifica las rutas disponibles en el servidor"""
    
    print("\n🔍 VERIFICACIÓN: RUTAS DEL SERVIDOR")
    print("=" * 50)
    
    try:
        # Intentar obtener información de rutas
        response = requests.get("http://localhost:5000/", timeout=10)
        print(f"📊 Ruta raíz: {response.status_code}")
        
        # Probar algunas rutas comunes
        common_routes = [
            "/",
            "/api",
            "/api/",
            "/socket.io/",
        ]
        
        for route in common_routes:
            try:
                response = requests.get(f"http://localhost:5000{route}", timeout=5)
                print(f"   {route}: {response.status_code}")
            except:
                print(f"   {route}: ERROR")
                
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO COMPLETO DE ENDPOINTS")
    print("=" * 55)
    
    # Verificar que el servidor esté funcionando
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Servidor funcionando")
            print(f"📊 Versión: {health_response.json().get('version', 'N/A')}")
        else:
            print("❌ Servidor no responde correctamente")
            exit(1)
    except:
        print("❌ No se puede conectar al servidor")
        exit(1)
    
    # Ejecutar todas las pruebas
    working, broken = test_all_endpoints()
    test_specific_outputs_endpoint()
    check_server_routes()
    
    # Veredicto final
    print(f"\n🎯 VEREDICTO FINAL")
    print("=" * 30)
    
    if len(broken) == 0:
        print("🎉 Todos los endpoints funcionan correctamente")
    elif "/api/outputs/recent" in [ep[0] for ep in broken]:
        print("❌ PROBLEMA CRÍTICO: Endpoint de outputs no funciona")
        print("💡 Esto explica por qué el Panel de Outputs está vacío")
    else:
        print(f"⚠️ {len(broken)} endpoints con problemas, pero outputs podría funcionar")
    
    exit(0 if len(broken) == 0 else 1)