#!/usr/bin/env python3
"""
Script de prueba para verificar la ejecución de herramientas en Synapse
"""

import requests
import socketio
import time
import json

# Configuración
BACKEND_URL = 'http://localhost:5000'

def test_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor funcionando - Versión: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ Error en servidor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_tools_endpoint():
    """Verificar endpoint de herramientas"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/tools')
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"✅ Herramientas disponibles: {len(tools)}")

            # Mostrar herramientas por tipo
            core_tools = [t for t in tools if t.get('type') == 'core']
            mcp_tools = [t for t in tools if t.get('type') == 'mcp']

            print(f"   - Herramientas Core: {len(core_tools)}")
            print(f"   - Herramientas MCP: {len(mcp_tools)}")

            # Mostrar algunas herramientas core
            print("\n🔧 Herramientas Core:")
            for tool in core_tools[:4]:
                print(f"   • {tool['id']}: {tool['name']}")

            # Mostrar algunas herramientas MCP
            print("\n🛠️ Herramientas MCP (primeras 5):")
            for tool in mcp_tools[:5]:
                print(f"   • {tool['id']}: {tool['name']}")

            return True
        else:
            print(f"❌ Error obteniendo herramientas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_plan_execution():
    """Probar la ejecución de un plan con herramientas"""
    print("\n🚀 Probando ejecución de plan con herramientas...")
    
    # Crear cliente SocketIO
    sio = socketio.Client()
    
    # Variables para capturar eventos
    plan_generated = False
    steps_completed = []
    plan_data = None
    
    @sio.event
    def connect():
        print("🔌 Conectado al servidor")
    
    @sio.event
    def disconnect():
        print("🔌 Desconectado del servidor")
    
    @sio.event
    def plan_generated(data):
        nonlocal plan_generated, plan_data
        plan_generated = True
        plan_data = data
        print(f"📋 Plan generado: {data.get('plan', {}).get('title', 'Sin título')}")
        print(f"   Pasos: {len(data.get('plan', {}).get('steps', []))}")
        
        # Mostrar herramientas asignadas
        steps = data.get('plan', {}).get('steps', [])
        for i, step in enumerate(steps, 1):
            tools = step.get('tools', [])
            if tools:
                print(f"   Paso {i}: {step.get('title', 'Sin título')} -> Herramientas: {tools}")
    
    @sio.event
    def plan_step_update(data):
        step_id = data.get('step_id')
        status = data.get('status')
        message = data.get('message', '')
        output = data.get('output', '')
        
        if status == 'completed':
            steps_completed.append(step_id)
            print(f"✅ Paso completado: {message}")
            if output and len(output) > 100:
                print(f"   Output: {output[:200]}...")
                
                # Verificar si hay resultados de herramientas
                if "RESULTADOS DE HERRAMIENTAS" in output:
                    print("   🔧 ¡Herramientas ejecutadas correctamente!")
            else:
                print(f"   Output: {output}")
        elif status == 'in_progress':
            print(f"⏳ Ejecutando: {message}")
    
    try:
        # Conectar
        sio.connect(BACKEND_URL)
        time.sleep(1)
        
        # Enviar mensaje de prueba
        test_message = "Crear un plan para desarrollar una aplicación web simple con análisis de datos"
        print(f"📤 Enviando mensaje: {test_message}")
        sio.emit('send_message', {'message': test_message})
        
        # Esperar a que se genere el plan
        timeout = 30
        start_time = time.time()
        
        while not plan_generated and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        if not plan_generated:
            print("❌ Timeout esperando generación del plan")
            return False
        
        # Esperar a que se completen los pasos
        expected_steps = len(plan_data.get('plan', {}).get('steps', []))
        print(f"⏳ Esperando completar {expected_steps} pasos...")
        
        timeout = 60  # 1 minuto para completar todos los pasos
        start_time = time.time()
        
        while len(steps_completed) < expected_steps and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        if len(steps_completed) >= expected_steps:
            print(f"✅ Plan completado exitosamente! ({len(steps_completed)}/{expected_steps} pasos)")
            return True
        else:
            print(f"⚠️ Plan parcialmente completado ({len(steps_completed)}/{expected_steps} pasos)")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False
    finally:
        try:
            sio.disconnect()
        except:
            pass

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de ejecución de herramientas en Synapse\n")
    
    # Prueba 1: Salud del servidor
    print("1️⃣ Verificando salud del servidor...")
    if not test_server_health():
        print("❌ El servidor no está funcionando. Abortando pruebas.")
        return
    
    # Prueba 2: Endpoint de herramientas
    print("\n2️⃣ Verificando herramientas disponibles...")
    if not test_tools_endpoint():
        print("❌ Error verificando herramientas. Abortando pruebas.")
        return
    
    # Prueba 3: Ejecución de plan
    print("\n3️⃣ Probando ejecución de plan...")
    success = test_plan_execution()
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    print("✅ Servidor funcionando: SÍ")
    print("✅ Herramientas disponibles: SÍ")
    print(f"{'✅' if success else '❌'} Ejecución de herramientas: {'SÍ' if success else 'NO'}")
    
    if success:
        print("\n🎉 ¡Todas las pruebas pasaron! Las herramientas se están ejecutando correctamente.")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar los logs para más detalles.")

if __name__ == "__main__":
    main()