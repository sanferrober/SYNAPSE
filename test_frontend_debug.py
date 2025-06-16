#!/usr/bin/env python3
"""
Test específico para debuggear el frontend - verificar datos recibidos
"""

import socketio
import time
import json
import requests

def test_frontend_debug():
    print("🔍 DEBUG FRONTEND: Verificando datos recibidos")
    print("=" * 50)
    
    # Verificar que el servidor esté funcionando
    try:
        response = requests.get('http://localhost:5000/api/health')
        print(f"✅ Servidor funcionando: {response.json()}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # Crear cliente WebSocket
    sio = socketio.Client()
    
    # Variables para capturar datos
    plan_data = None
    step_updates = []
    
    @sio.on('connect')
    def connect():
        print("🔌 Conectado al servidor")
    
    @sio.on('disconnect')
    def disconnect():
        print("❌ Desconectado del servidor")
    
    @sio.on('plan_generated')
    def plan_generated(data):
        nonlocal plan_data
        plan_data = data
        print(f"📋 Plan generado: {data.get('plan', {}).get('title', 'Sin título')}")
        print(f"📊 Pasos en el plan: {len(data.get('plan', {}).get('steps', []))}")
        
        # Mostrar estructura del plan
        plan = data.get('plan', {})
        steps = plan.get('steps', [])
        for i, step in enumerate(steps):
            print(f"   Paso {i+1}: {step.get('title', 'Sin título')} - ID: {step.get('id', 'Sin ID')}")
    
    @sio.on('plan_step_update')
    def plan_step_update(data):
        step_updates.append(data)
        step_id = data.get('step_id', 'Sin ID')
        status = data.get('status', 'Sin status')
        message = data.get('message', 'Sin mensaje')
        output = data.get('output', '')
        
        print(f"\n🔧 Step Update #{len(step_updates)}:")
        print(f"   📍 Step ID: {step_id}")
        print(f"   📊 Status: {status}")
        print(f"   💬 Message: {message}")
        print(f"   📄 Output: {'SÍ' if output else 'NO'} ({len(output)} chars)")
        
        if output:
            print(f"   📝 Output preview: {output[:100]}...")
            
            # Verificar si es output real o simulado
            if any(keyword in output.lower() for keyword in ['tiempo de respuesta', 'github', 'api', 'real']):
                print(f"   🌐 OUTPUT REAL detectado")
            else:
                print(f"   🤖 Output simulado detectado")
        
        # Mostrar estructura completa del update
        print(f"   🔍 Campos disponibles: {list(data.keys())}")
    
    @sio.on('plan_completed')
    def plan_completed(data):
        print(f"\n✅ Plan completado: {data}")
    
    try:
        # Conectar al servidor
        sio.connect('http://localhost:5000')
        
        # Enviar mensaje de prueba
        test_message = "Busca información sobre Python en GitHub"
        print(f"\n📤 Enviando mensaje: {test_message}")
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuestas
        print("\n⏳ Esperando respuestas del servidor...")
        time.sleep(15)  # Esperar más tiempo para recibir todos los updates
        
        # Análisis de resultados
        print("\n" + "=" * 50)
        print("📊 ANÁLISIS DE RESULTADOS")
        print("=" * 50)
        
        print(f"📋 Plan recibido: {'SÍ' if plan_data else 'NO'}")
        if plan_data:
            plan = plan_data.get('plan', {})
            print(f"   🏷️ Título: {plan.get('title', 'Sin título')}")
            print(f"   📊 Pasos planificados: {len(plan.get('steps', []))}")
        
        print(f"🔧 Step updates recibidos: {len(step_updates)}")
        
        # Analizar cada step update
        steps_with_output = 0
        real_outputs = 0
        
        for i, update in enumerate(step_updates):
            output = update.get('output', '')
            has_output = bool(output and output.strip())
            
            if has_output:
                steps_with_output += 1
                
                # Verificar si es output real
                if any(keyword in output.lower() for keyword in ['tiempo de respuesta', 'github', 'api', 'real']):
                    real_outputs += 1
            
            print(f"   Update {i+1}: Step {update.get('step_id')} - Status: {update.get('status')} - Output: {'SÍ' if has_output else 'NO'}")
        
        print(f"📊 Steps con output: {steps_with_output}")
        print(f"🌐 Outputs reales: {real_outputs}")
        
        # Verificar datos disponibles en endpoints
        print(f"\n🔍 VERIFICACIÓN DE ENDPOINTS:")
        try:
            outputs_response = requests.get('http://localhost:5000/api/outputs/recent')
            if outputs_response.status_code == 200:
                outputs_data = outputs_response.json()
                recent_outputs = outputs_data.get('recent_outputs', [])
                print(f"📊 /api/outputs/recent: {len(recent_outputs)} outputs disponibles")
            else:
                print(f"❌ /api/outputs/recent: Error {outputs_response.status_code}")
        except Exception as e:
            print(f"❌ Error verificando outputs: {e}")
        
        try:
            memory_response = requests.get('http://localhost:5000/api/memory/all')
            if memory_response.status_code == 200:
                memory_data = memory_response.json()
                executed_plans = memory_data.get('executed_plans', [])
                print(f"📊 /api/memory/all: {len(executed_plans)} planes ejecutados")
                
                # Contar outputs en planes ejecutados
                total_outputs = 0
                for plan in executed_plans:
                    steps = plan.get('steps', [])
                    for step in steps:
                        if step.get('output'):
                            total_outputs += 1
                print(f"📊 Total outputs en memoria: {total_outputs}")
            else:
                print(f"❌ /api/memory/all: Error {memory_response.status_code}")
        except Exception as e:
            print(f"❌ Error verificando memoria: {e}")
        
        # Conclusión
        print(f"\n🎯 CONCLUSIÓN:")
        if steps_with_output > 0:
            print(f"✅ Frontend está recibiendo outputs ({steps_with_output} de {len(step_updates)})")
            if real_outputs > 0:
                print(f"🌐 Hay outputs reales disponibles ({real_outputs})")
            else:
                print(f"🤖 Solo outputs simulados detectados")
        else:
            print(f"❌ Frontend NO está recibiendo outputs")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_frontend_debug()