#!/usr/bin/env python3
"""
Test final para verificar el componente OutputsPanelFixed
"""

import socketio
import time
import json

def test_outputs_panel_fixed():
    print("🔧 TESTING OUTPUTSPANEL FIXED")
    print("=" * 50)
    
    sio = socketio.Client()
    
    @sio.on('connect')
    def connect():
        print("🔌 Conectado al servidor")
    
    @sio.on('disconnect')
    def disconnect():
        print("❌ Desconectado del servidor")
    
    @sio.on('plan_generated')
    def plan_generated(data):
        plan = data.get('plan', {})
        print(f"📋 Plan generado: {plan.get('title')}")
        print(f"   Pasos: {len(plan.get('steps', []))}")
    
    @sio.on('plan_step_update')
    def plan_step_update(data):
        step_id = data.get('step_id')
        status = data.get('status')
        output = data.get('output', '')
        print(f"🔄 Paso {step_id} actualizado: {status}")
        if output:
            print(f"   ✅ Output generado: {len(output)} caracteres")
            print(f"   📝 Preview: {output[:100]}...")
        else:
            print(f"   ❌ Sin output")
    
    try:
        # Conectar
        sio.connect('http://localhost:5000')
        
        print(f"\n📤 Enviando mensaje de prueba...")
        sio.emit('user_message', {'message': 'Test del OutputsPanelFixed'})
        
        # Esperar respuestas
        time.sleep(15)
        
        print(f"\n" + "=" * 50)
        print("🎯 INSTRUCCIONES PARA PROBAR EN EL NAVEGADOR:")
        print("=" * 50)
        print("1. Abre http://localhost:3000 en tu navegador")
        print("2. Ve a la pestaña 'Outputs Fixed'")
        print("3. Verifica que se muestren los outputs")
        print("4. Revisa la consola del navegador para ver los logs detallados")
        print("5. Si no se muestran, revisa los logs de debugging")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_outputs_panel_fixed()