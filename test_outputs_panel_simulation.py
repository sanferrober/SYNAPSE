#!/usr/bin/env python3
"""
Test específico para simular el problema del OutputsPanel
"""

import socketio
import time
import json

def test_outputs_panel_simulation():
    print("🔍 SIMULACIÓN ESPECÍFICA: OutputsPanel")
    print("=" * 50)
    
    # Crear cliente WebSocket
    sio = socketio.Client()
    
    # Variables para capturar datos exactos
    received_plan = None
    received_steps = []
    
    @sio.on('connect')
    def connect():
        print("🔌 Conectado - Simulando frontend")
    
    @sio.on('plan_generated')
    def plan_generated(data):
        nonlocal received_plan
        received_plan = data.get('plan', {})
        print(f"📋 Plan recibido: {received_plan.get('title', 'Sin título')}")
        print(f"📊 Pasos iniciales: {len(received_plan.get('steps', []))}")
        
        # Simular el estado inicial del contexto
        initial_steps = received_plan.get('steps', [])
        for step in initial_steps:
            print(f"   Paso inicial: {step.get('title')} - Status: {step.get('status', 'pending')} - Output: {bool(step.get('output'))}")
    
    @sio.on('plan_step_update')
    def plan_step_update(data):
        received_steps.append(data)
        step_id = data.get('step_id')
        status = data.get('status')
        output = data.get('output', '')
        
        print(f"\n🔄 Step Update #{len(received_steps)}:")
        print(f"   Step ID: {step_id}")
        print(f"   Status: {status}")
        print(f"   Output presente: {'SÍ' if output else 'NO'}")
        print(f"   Output length: {len(output)} chars")
        
        # Simular la lógica del contexto de React
        print(f"   🧠 Simulando contexto React:")
        print(f"      - step.id === {step_id}")
        print(f"      - step.status = '{status}'")
        print(f"      - step.output = {'presente' if output else 'ausente'}")
        
        # Simular la lógica de filtrado del OutputsPanel
        has_output_for_panel = output and output.strip() and len(output.strip()) > 0
        print(f"   📊 ¿Pasaría filtro OutputsPanel? {'SÍ' if has_output_for_panel else 'NO'}")
        
        if has_output_for_panel:
            print(f"   ✅ Este paso DEBERÍA aparecer en OutputsPanel")
        else:
            print(f"   ❌ Este paso NO aparecería en OutputsPanel")
    
    try:
        # Conectar
        sio.connect('http://localhost:5000')
        
        # Enviar mensaje
        test_message = "Analiza repositorios de Python"
        print(f"\n📤 Enviando: {test_message}")
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuestas
        time.sleep(12)
        
        # Análisis final
        print(f"\n" + "=" * 50)
        print("🔍 ANÁLISIS FINAL - SIMULACIÓN OUTPUTSPANEL")
        print("=" * 50)
        
        print(f"📋 Plan recibido: {'SÍ' if received_plan else 'NO'}")
        if received_plan:
            print(f"   Título: {received_plan.get('title')}")
            print(f"   Pasos iniciales: {len(received_plan.get('steps', []))}")
        
        print(f"🔄 Step updates recibidos: {len(received_steps)}")
        
        # Simular exactamente la lógica del OutputsPanel
        simulated_plan_steps = []
        
        # Empezar con los pasos iniciales del plan
        if received_plan:
            for step in received_plan.get('steps', []):
                simulated_plan_steps.append({
                    'id': step.get('id'),
                    'title': step.get('title'),
                    'status': step.get('status', 'pending'),
                    'output': step.get('output', '')
                })
        
        # Aplicar los updates
        for update in received_steps:
            step_id = update.get('step_id')
            for i, step in enumerate(simulated_plan_steps):
                if step['id'] == step_id:
                    simulated_plan_steps[i]['status'] = update.get('status', step['status'])
                    simulated_plan_steps[i]['message'] = update.get('message', '')
                    if update.get('output'):
                        simulated_plan_steps[i]['output'] = update.get('output')
                    break
        
        print(f"\n📊 Estado final simulado de planSteps:")
        for i, step in enumerate(simulated_plan_steps):
            has_output = step.get('output') and step.get('output').strip() and len(step.get('output').strip()) > 0
            print(f"   Paso {i+1}: {step.get('title')}")
            print(f"      Status: {step.get('status')}")
            print(f"      Output: {'SÍ' if has_output else 'NO'} ({len(step.get('output', ''))} chars)")
            if has_output:
                print(f"      Preview: {step.get('output', '')[:100]}...")
        
        # Aplicar filtro del OutputsPanel
        steps_with_output = [step for step in simulated_plan_steps 
                           if step.get('output') and step.get('output').strip() and len(step.get('output').strip()) > 0]
        
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"   Total pasos: {len(simulated_plan_steps)}")
        print(f"   Pasos con output (filtrados): {len(steps_with_output)}")
        
        if len(steps_with_output) > 0:
            print(f"   ✅ OutputsPanel DEBERÍA mostrar {len(steps_with_output)} outputs")
            for i, step in enumerate(steps_with_output):
                print(f"      Output {i+1}: {step.get('title')} ({len(step.get('output', ''))} chars)")
        else:
            print(f"   ❌ OutputsPanel mostraría 'Esperando outputs...'")
            print(f"   🔍 Razón: Ningún paso pasó el filtro de output")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_outputs_panel_simulation()