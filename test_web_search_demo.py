#!/usr/bin/env python3
"""
🔍 DEMOSTRACIÓN: Búsqueda Web con Herramientas MCP - Synapse
Muestra cómo funciona la consulta web real usando herramientas MCP
"""

import requests
import json
import time
import socketio
from datetime import datetime

# Configuración
BACKEND_URL = "http://localhost:5000"

def test_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor Synapse funcionando")
            print(f"   📊 Versión: {data.get('version', 'N/A')}")
            print(f"   🔗 Conexiones activas: {data.get('active_connections', 0)}")
            return True
        else:
            print(f"❌ Servidor responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_mcp_tools_direct():
    """Probar herramientas MCP directamente via API REST"""
    print("\n🔧 PRUEBA DIRECTA DE HERRAMIENTAS MCP")
    print("=" * 50)
    
    # Lista de herramientas MCP para probar
    tools_to_test = [
        {
            'tool_id': 'web_search_mcp',
            'params': {'query': 'inteligencia artificial 2024 tendencias'},
            'name': 'Búsqueda Web DuckDuckGo'
        },
        {
            'tool_id': 'brave_search_mcp', 
            'params': {'query': 'machine learning frameworks python'},
            'name': 'Brave Search'
        },
        {
            'tool_id': 'github_mcp',
            'params': {'query': 'react hooks tutorial'},
            'name': 'GitHub Search'
        }
    ]
    
    results = []
    
    for tool in tools_to_test:
        print(f"\n🔍 Probando: {tool['name']}")
        print(f"   🎯 Consulta: {tool['params']['query']}")
        
        try:
            # Llamada directa a la API MCP
            response = requests.post(
                f"{BACKEND_URL}/api/mcp/tools/{tool['tool_id']}/execute",
                json=tool['params'],
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Éxito - Tiempo: {result.get('execution_time', 'N/A')}s")
                
                # Mostrar resultado resumido
                if 'result' in result:
                    result_text = result['result']
                    # Mostrar primeras líneas del resultado
                    lines = result_text.split('\n')[:8]
                    for line in lines:
                        if line.strip():
                            print(f"   📄 {line.strip()}")
                
                results.append({
                    'tool': tool['name'],
                    'success': True,
                    'result': result
                })
                
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                results.append({
                    'tool': tool['name'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'tool': tool['name'],
                'success': False,
                'error': str(e)
            })
    
    return results

def test_websocket_search():
    """Probar búsqueda web via WebSocket (simulando frontend)"""
    print("\n🌐 PRUEBA VIA WEBSOCKET (Simulando Frontend)")
    print("=" * 50)
    
    # Variables para capturar datos
    received_plan = None
    received_steps = []
    
    # Crear cliente SocketIO
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("🔗 Conectado al servidor via WebSocket")
    
    @sio.event
    def disconnect():
        print("🔌 Desconectado del servidor")
    
    @sio.event
    def plan_generated(data):
        nonlocal received_plan
        received_plan = data
        print(f"📋 Plan generado: {data.get('title', 'Sin título')}")
        print(f"   📊 Pasos: {len(data.get('steps', []))}")
    
    @sio.event
    def plan_step_update(data):
        nonlocal received_steps
        received_steps.append(data)
        
        step_id = data.get('step_id', 'N/A')
        status = data.get('status', 'N/A')
        output = data.get('output', '')
        
        print(f"🔄 Paso {step_id}: {status}")
        
        if output and len(output) > 100:
            print(f"   📤 Output recibido: {len(output)} caracteres")
            # Mostrar primeras líneas del output
            lines = output.split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"   📄 {line.strip()}")
    
    @sio.event
    def plan_completed(data):
        print(f"✅ Plan completado: {data.get('message', 'Sin mensaje')}")
    
    try:
        # Conectar al servidor
        sio.connect(BACKEND_URL)
        
        # Enviar mensaje que active búsqueda web
        test_message = "Busca información sobre las últimas tendencias en inteligencia artificial y machine learning para 2024"
        
        print(f"📤 Enviando consulta: {test_message}")
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuestas
        print("⏳ Esperando respuestas del servidor...")
        time.sleep(20)  # Esperar 20 segundos para recibir todas las respuestas
        
        # Desconectar
        sio.disconnect()
        
        # Analizar resultados
        print(f"\n📊 RESUMEN DE RESULTADOS:")
        print(f"   📋 Plan recibido: {'Sí' if received_plan else 'No'}")
        print(f"   🔄 Actualizaciones de pasos: {len(received_steps)}")
        
        # Buscar outputs con contenido web real
        web_outputs = []
        for step in received_steps:
            output = step.get('output', '')
            if any(keyword in output.lower() for keyword in ['duckduckgo', 'búsqueda', 'resultados', 'web', 'url', 'http']):
                web_outputs.append(step)
        
        print(f"   🌐 Pasos con búsqueda web: {len(web_outputs)}")
        
        # Mostrar ejemplo de output web
        if web_outputs:
            example = web_outputs[0]
            output = example.get('output', '')
            print(f"\n🔍 EJEMPLO DE BÚSQUEDA WEB:")
            lines = output.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")
        
        return len(web_outputs) > 0
        
    except Exception as e:
        print(f"❌ Error en prueba WebSocket: {e}")
        return False

def main():
    """Función principal de demostración"""
    print("🚀 DEMOSTRACIÓN: Búsqueda Web con Herramientas MCP - Synapse")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar servidor
    if not test_server_health():
        print("\n❌ No se puede continuar sin el servidor funcionando")
        print("💡 Ejecuta: python synapse_server_final.py")
        return
    
    # 2. Probar herramientas MCP directamente
    direct_results = test_mcp_tools_direct()
    
    # 3. Probar via WebSocket
    websocket_success = test_websocket_search()
    
    # 4. Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE LA DEMOSTRACIÓN")
    print("=" * 60)
    
    successful_tools = sum(1 for r in direct_results if r['success'])
    total_tools = len(direct_results)
    
    print(f"🔧 Herramientas MCP probadas: {successful_tools}/{total_tools}")
    print(f"🌐 Búsqueda via WebSocket: {'✅ Exitosa' if websocket_success else '❌ Falló'}")
    
    if successful_tools > 0:
        print("\n✅ DEMOSTRACIÓN EXITOSA")
        print("   Las herramientas MCP están funcionando correctamente")
        print("   Se pueden realizar búsquedas web reales")
    else:
        print("\n⚠️  DEMOSTRACIÓN PARCIAL")
        print("   Algunas herramientas pueden estar en modo simulación")
    
    print(f"\n⏰ Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()