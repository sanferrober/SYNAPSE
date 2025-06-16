#!/usr/bin/env python3
"""
Test final para simular exactamente el comportamiento del navegador
"""

import socketio
import time
import json

def test_browser_simulation():
    print("🌐 SIMULACIÓN COMPLETA DEL NAVEGADOR")
    print("=" * 50)
    
    sio = socketio.Client()
    
    # Simular el estado del contexto de React
    react_state = {
        'isConnected': False,
        'currentPlan': None,
        'planSteps': [],
        'messages': []
    }
    
    def update_react_state(action_type, payload):
        """Simular el reducer de React"""
        print(f"🔄 React Action: {action_type}")
        
        if action_type == 'SET_CONNECTED':
            react_state['isConnected'] = payload
            
        elif action_type == 'SET_CURRENT_PLAN':
            react_state['currentPlan'] = payload
            react_state['planSteps'] = payload.get('steps', [])
            print(f"   📋 Plan establecido: {payload.get('title')}")
            print(f"   📊 Pasos iniciales: {len(react_state['planSteps'])}")
            for i, step in enumerate(react_state['planSteps']):
                print(f"      Paso {i+1}: ID={step.get('id')} | '{step.get('title')}' | Output: {bool(step.get('output'))}")
                
        elif action_type == 'UPDATE_PLAN_STEP':
            step_id = payload.get('step_id')
            print(f"   🔄 Actualizando paso {step_id}")
            print(f"   📊 Estado antes: {len([s for s in react_state['planSteps'] if s.get('output')])}/{len(react_state['planSteps'])} con output")
            
            # Aplicar la misma lógica que el contexto de React
            updated_steps = []
            for step in react_state['planSteps']:
                if step.get('id') == step_id:
                    updated_step = {
                        **step,
                        'status': payload.get('status', step.get('status')),
                        'message': payload.get('message', step.get('message')),
                        'output': payload.get('output') or step.get('output', '')
                    }
                    updated_steps.append(updated_step)
                    print(f"      ✅ Paso {step_id} actualizado:")
                    print(f"         Status: {updated_step.get('status')}")
                    print(f"         Output: {'SÍ' if updated_step.get('output') else 'NO'} ({len(updated_step.get('output', ''))} chars)")
                else:
                    updated_steps.append(step)
            
            react_state['planSteps'] = updated_steps
            print(f"   📊 Estado después: {len([s for s in react_state['planSteps'] if s.get('output')])}/{len(react_state['planSteps'])} con output")
    
    def simulate_outputs_panel():
        """Simular la lógica del OutputsPanel"""
        print(f"\n🎯 SIMULANDO OUTPUTSPANEL:")
        
        current_plan = react_state.get('currentPlan')
        plan_steps = react_state.get('planSteps', [])
        
        print(f"   currentPlan: {'SÍ' if current_plan else 'NO'}")
        print(f"   planSteps: {len(plan_steps)} pasos")
        
        if not current_plan:
            print(f"   ❌ Mostraría: 'No hay plan activo'")
            return
        
        # Aplicar el filtro exacto del OutputsPanel
        steps_with_output = []
        for step in plan_steps:
            has_output = step.get('output') and step.get('output').strip() and len(step.get('output').strip()) > 0
            print(f"   🔍 Paso {step.get('id')}: '{step.get('title')}' - Output: {'SÍ' if has_output else 'NO'}")
            if has_output:
                steps_with_output.append(step)
        
        print(f"   📊 Steps filtrados: {len(steps_with_output)}")
        
        if len(steps_with_output) == 0:
            print(f"   ❌ Mostraría: 'Esperando outputs...'")
        else:
            print(f"   ✅ Mostraría: {len(steps_with_output)} outputs")
            for i, step in enumerate(steps_with_output):
                print(f"      Output {i+1}: {step.get('title')} ({len(step.get('output', ''))} chars)")
    
    @sio.on('connect')
    def connect():
        print("🔌 Conectado al servidor")
        update_react_state('SET_CONNECTED', True)
    
    @sio.on('disconnect')
    def disconnect():
        print("❌ Desconectado del servidor")
        update_react_state('SET_CONNECTED', False)
    
    @sio.on('plan_generated')
    def plan_generated(data):
        plan = data.get('plan', {})
        update_react_state('SET_CURRENT_PLAN', plan)
        simulate_outputs_panel()
    
    @sio.on('plan_step_update')
    def plan_step_update(data):
        update_react_state('UPDATE_PLAN_STEP', data)
        simulate_outputs_panel()
    
    try:
        # Conectar
        sio.connect('http://localhost:5000')
        
        # Enviar mensaje
        print(f"\n📤 Enviando mensaje de prueba...")
        sio.emit('user_message', {'message': 'Test completo del navegador'})
        
        # Esperar respuestas
        time.sleep(12)
        
        # Análisis final
        print(f"\n" + "=" * 50)
        print("🎯 ANÁLISIS FINAL - SIMULACIÓN NAVEGADOR")
        print("=" * 50)
        
        print(f"📊 Estado final del contexto React:")
        print(f"   isConnected: {react_state['isConnected']}")
        print(f"   currentPlan: {react_state['currentPlan'].get('title') if react_state['currentPlan'] else 'None'}")
        print(f"   planSteps: {len(react_state['planSteps'])} pasos")
        
        steps_with_output = [s for s in react_state['planSteps'] if s.get('output') and s.get('output').strip()]
        print(f"   Steps con output: {len(steps_with_output)}")
        
        print(f"\n🎯 VEREDICTO FINAL:")
        if len(steps_with_output) > 0:
            print(f"   ✅ El OutputsPanel DEBERÍA mostrar {len(steps_with_output)} outputs")
            print(f"   📋 Si no los muestra, el problema está en el componente React")
        else:
            print(f"   ❌ El OutputsPanel correctamente muestra 'Esperando outputs...'")
        
        # Última simulación
        print(f"\n🔍 SIMULACIÓN FINAL DEL OUTPUTSPANEL:")
        simulate_outputs_panel()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_browser_simulation()