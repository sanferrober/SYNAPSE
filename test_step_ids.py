#!/usr/bin/env python3
"""
Test específico para verificar IDs de pasos
"""

import socketio
import time
import json

def test_step_ids():
    print("🔍 VERIFICACIÓN DE IDs DE PASOS")
    print("=" * 50)
    
    sio = socketio.Client()
    
    plan_steps_initial = []
    step_updates_received = []
    
    @sio.on('connect')
    def connect():
        print("🔌 Conectado")
    
    @sio.on('plan_generated')
    def plan_generated(data):
        nonlocal plan_steps_initial
        plan = data.get('plan', {})
        plan_steps_initial = plan.get('steps', [])
        
        print(f"📋 Plan generado: {plan.get('title')}")
        print(f"📊 Pasos iniciales del plan:")
        for i, step in enumerate(plan_steps_initial):
            print(f"   Paso {i+1}: ID={step.get('id')} | Título='{step.get('title')}' | Status='{step.get('status', 'pending')}'")
    
    @sio.on('plan_step_update')
    def plan_step_update(data):
        step_updates_received.append(data)
        step_id = data.get('step_id')
        status = data.get('status')
        has_output = bool(data.get('output'))
        
        print(f"\n🔄 Step Update #{len(step_updates_received)}:")
        print(f"   step_id: {step_id} (tipo: {type(step_id)})")
        print(f"   status: {status}")
        print(f"   tiene output: {has_output}")
        
        # Verificar si el ID coincide con algún paso inicial
        matching_step = None
        for step in plan_steps_initial:
            if step.get('id') == step_id:
                matching_step = step
                break
        
        if matching_step:
            print(f"   ✅ ID coincide con paso: '{matching_step.get('title')}'")
        else:
            print(f"   ❌ ID NO coincide con ningún paso inicial")
            print(f"   🔍 IDs disponibles en plan inicial: {[s.get('id') for s in plan_steps_initial]}")
    
    try:
        sio.connect('http://localhost:5000')
        
        print(f"\n📤 Enviando mensaje de prueba...")
        sio.emit('user_message', {'message': 'Prueba de IDs de pasos'})
        
        time.sleep(10)
        
        print(f"\n" + "=" * 50)
        print("📊 ANÁLISIS DE IDs")
        print("=" * 50)
        
        print(f"📋 Pasos iniciales del plan: {len(plan_steps_initial)}")
        for i, step in enumerate(plan_steps_initial):
            print(f"   {i+1}. ID: {step.get('id')} ({type(step.get('id'))}) - '{step.get('title')}'")
        
        print(f"\n🔄 Step updates recibidos: {len(step_updates_received)}")
        for i, update in enumerate(step_updates_received):
            step_id = update.get('step_id')
            print(f"   {i+1}. step_id: {step_id} ({type(step_id)}) - Status: {update.get('status')}")
        
        # Verificar coincidencias
        print(f"\n🎯 VERIFICACIÓN DE COINCIDENCIAS:")
        initial_ids = [step.get('id') for step in plan_steps_initial]
        update_ids = [update.get('step_id') for update in step_updates_received]
        
        print(f"   IDs iniciales: {initial_ids}")
        print(f"   IDs de updates: {list(set(update_ids))}")
        
        matches = 0
        for update_id in set(update_ids):
            if update_id in initial_ids:
                matches += 1
                print(f"   ✅ ID {update_id} coincide")
            else:
                print(f"   ❌ ID {update_id} NO coincide")
        
        print(f"\n🎯 RESULTADO:")
        if matches == len(set(update_ids)):
            print(f"   ✅ Todos los IDs coinciden - El problema NO son los IDs")
        else:
            print(f"   ❌ {matches}/{len(set(update_ids))} IDs coinciden - PROBLEMA DE IDs DETECTADO")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_step_ids()