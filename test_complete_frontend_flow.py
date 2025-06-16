#!/usr/bin/env python3
"""
Prueba completa del flujo frontend -> backend -> outputs
Simula exactamente lo que hace el frontend cuando envías un mensaje
"""

import socketio
import json
import time
from datetime import datetime

def test_complete_frontend_flow():
    """Prueba el flujo completo como lo hace el frontend"""
    
    print("🔍 PRUEBA COMPLETA: FLUJO FRONTEND -> BACKEND -> OUTPUTS")
    print("=" * 60)
    
    # Conectar como lo hace el frontend
    sio = socketio.Client()
    
    # Variables para capturar todo el flujo
    plan_data = None
    plan_steps = []
    outputs_received = []
    
    @sio.event
    def connect():
        print("✅ Conectado al servidor (simulando frontend)")
    
    @sio.event
    def disconnect():
        print("❌ Desconectado del servidor")
    
    @sio.event
    def plan_generated(data):
        nonlocal plan_data
        plan_data = data.get('plan', {})
        print(f"📋 Plan generado: {plan_data.get('title', 'Sin título')}")
        print(f"   📊 Pasos: {len(plan_data.get('steps', []))}")
    
    @sio.event
    def plan_step_update(data):
        nonlocal plan_steps
        step_id = data.get('step_id')
        status = data.get('status')
        output = data.get('output', '')
        message = data.get('message', '')
        
        print(f"🔧 Paso {step_id}: {status}")
        if message:
            print(f"   💬 Mensaje: {message[:100]}...")
        
        # Actualizar o agregar paso
        existing_step = None
        for step in plan_steps:
            if step.get('id') == step_id:
                existing_step = step
                break
        
        if existing_step:
            existing_step.update({
                'status': status,
                'output': output,
                'message': message
            })
        else:
            plan_steps.append({
                'id': step_id,
                'status': status,
                'output': output,
                'message': message
            })
        
        # Si hay output, guardarlo
        if output and status == 'completed':
            outputs_received.append({
                'step_id': step_id,
                'output': output,
                'length': len(output),
                'timestamp': datetime.now().isoformat()
            })
            print(f"   📊 Output recibido: {len(output)} chars")
            
            # Mostrar muestra del output
            if len(output) > 100:
                print(f"   📝 Muestra: {output[:200]}...")
            else:
                print(f"   📝 Output completo: {output}")
    
    @sio.event
    def plan_completed(data):
        print(f"✅ Plan completado: {data.get('message', 'Sin mensaje')}")
    
    try:
        # Conectar
        print("🔌 Conectando al servidor...")
        sio.connect('http://localhost:5000')
        time.sleep(2)
        
        # Enviar mensaje como lo hace el frontend
        test_message = "Busca repositorios de Python sobre machine learning en GitHub"
        print(f"📤 Enviando mensaje: {test_message}")
        
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuestas (como lo hace el frontend)
        print("⏳ Esperando respuestas del servidor...")
        time.sleep(25)  # Esperar más tiempo para asegurar que todo se complete
        
        # Analizar resultados
        print("\n" + "=" * 60)
        print("📊 ANÁLISIS DE RESULTADOS")
        print("=" * 60)
        
        print(f"📋 Plan recibido: {'✅ SÍ' if plan_data else '❌ NO'}")
        if plan_data:
            print(f"   🏷️ Título: {plan_data.get('title', 'N/A')}")
            print(f"   📊 Pasos planificados: {len(plan_data.get('steps', []))}")
        
        print(f"🔧 Pasos ejecutados: {len(plan_steps)}")
        for i, step in enumerate(plan_steps, 1):
            print(f"   {i}. Paso {step.get('id')}: {step.get('status')} - {len(step.get('output', ''))} chars")
        
        print(f"📊 Outputs recibidos: {len(outputs_received)}")
        
        # Verificar si hay outputs reales
        real_outputs = 0
        simulated_outputs = 0
        
        for output_data in outputs_received:
            output = output_data['output']
            
            # Buscar indicadores de datos reales
            real_indicators = [
                'github.com', 'tensorflow', 'scikit-learn', 'pytorch',
                'stars', 'forks', 'repositorios encontrados',
                'API GitHub', 'tiempo de respuesta'
            ]
            
            found_real = any(indicator.lower() in output.lower() for indicator in real_indicators)
            
            if found_real:
                real_outputs += 1
                print(f"   🌐 Paso {output_data['step_id']}: OUTPUT REAL ({output_data['length']} chars)")
                
                # Mostrar evidencia
                for indicator in real_indicators:
                    if indicator.lower() in output.lower():
                        print(f"      ✅ Contiene: {indicator}")
                        break
            else:
                simulated_outputs += 1
                print(f"   🤖 Paso {output_data['step_id']}: OUTPUT SIMULADO ({output_data['length']} chars)")
        
        # Veredicto final
        print("\n" + "=" * 60)
        print("🎯 VEREDICTO FINAL")
        print("=" * 60)
        
        if len(outputs_received) == 0:
            print("❌ PROBLEMA: NO se recibieron outputs en el frontend")
            print("🔧 El Panel de Outputs estará vacío")
            print("💡 Posible problema de comunicación WebSocket")
            return False
            
        elif real_outputs > 0:
            print("✅ ÉXITO: Outputs REALES recibidos en el frontend")
            print(f"🌐 {real_outputs} outputs reales de {len(outputs_received)} totales")
            print("🎉 El Panel de Outputs debería mostrar datos reales")
            
            # Mostrar muestra de output real
            for output_data in outputs_received:
                output = output_data['output']
                if any(indicator.lower() in output.lower() for indicator in ['github.com', 'tensorflow', 'repositorios']):
                    print(f"\n📊 MUESTRA DE OUTPUT REAL (Paso {output_data['step_id']}):")
                    print(f"   {output[:300]}...")
                    break
            
            return True
            
        else:
            print("⚠️ PROBLEMA: Solo outputs SIMULADOS recibidos")
            print(f"🤖 {simulated_outputs} outputs simulados")
            print("💡 Las herramientas MCP no están enviando datos reales al frontend")
            return False
    
    except Exception as e:
        print(f"💥 Error durante la prueba: {e}")
        return False
    
    finally:
        if sio.connected:
            sio.disconnect()

def test_outputs_panel_data():
    """Verifica qué datos están disponibles para el Panel de Outputs"""
    
    print("\n🔍 VERIFICACIÓN: DATOS PARA PANEL DE OUTPUTS")
    print("=" * 50)
    
    try:
        import requests
        
        # Verificar endpoints que usa el Panel de Outputs
        base_url = "http://localhost:5000"
        
        # 1. Verificar outputs recientes
        print("📊 Verificando /api/outputs/recent...")
        response = requests.get(f"{base_url}/api/outputs/recent")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Outputs recientes: {len(data.get('outputs', []))} encontrados")
            
            for i, output in enumerate(data.get('outputs', [])[:3]):
                print(f"   {i+1}. {output.get('step_title', 'Sin título')}: {len(output.get('output', ''))} chars")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # 2. Verificar memoria del sistema
        print("\n📊 Verificando /api/memory/all...")
        response = requests.get(f"{base_url}/api/memory/all")
        if response.status_code == 200:
            data = response.json()
            executed_plans = data.get('executed_plans', [])
            print(f"✅ Planes ejecutados: {len(executed_plans)} encontrados")
            
            for i, plan in enumerate(executed_plans[-3:]):
                steps_with_output = [s for s in plan.get('steps', []) if s.get('output')]
                print(f"   {i+1}. {plan.get('title', 'Sin título')}: {len(steps_with_output)} pasos con output")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 PRUEBA COMPLETA: FRONTEND -> BACKEND -> OUTPUTS")
    print("=" * 65)
    
    # Verificar servidor
    try:
        import requests
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print("❌ Servidor no responde")
            exit(1)
    except:
        print("❌ No se puede conectar al servidor")
        exit(1)
    
    # Ejecutar pruebas
    success = test_complete_frontend_flow()
    test_outputs_panel_data()
    
    print(f"\n{'🎉 RESULTADO: Frontend recibiendo datos reales' if success else '❌ RESULTADO: Problema en el flujo frontend'}")
    
    if not success:
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("1. Verificar que el frontend esté conectado al WebSocket")
        print("2. Revisar la consola del navegador para errores")
        print("3. Verificar que el Panel de Outputs esté recibiendo props correctos")
        print("4. Comprobar que los eventos WebSocket se estén emitiendo correctamente")
    
    exit(0 if success else 1)