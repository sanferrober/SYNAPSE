import socketio
import time
import json

# Crear cliente SocketIO
sio = socketio.Client()

# Variables para almacenar datos recibidos
received_data = {
    'plan_generated': None,
    'plan_steps': [],
    'step_updates': []
}

@sio.event
def connect():
    print("✅ Conectado al servidor")

@sio.event
def disconnect():
    print("❌ Desconectado del servidor")

@sio.on('plan_generated')
def plan_generated(data):
    print(f"📋 Plan generado recibido: {data.get('plan', {}).get('title', 'Sin título')}")
    received_data['plan_generated'] = data
    if 'plan' in data and 'steps' in data['plan']:
        received_data['plan_steps'] = data['plan']['steps']
        print(f"📊 Pasos del plan: {len(data['plan']['steps'])}")
        for i, step in enumerate(data['plan']['steps']):
            print(f"  {i+1}. {step.get('title', 'Sin título')} - ID: {step.get('id', 'Sin ID')}")

@sio.on('plan_step_update')
def plan_step_update(data):
    print(f"\n🔄 Actualización de paso recibida:")
    print(f"   Step ID: {data.get('step_id', 'N/A')}")
    print(f"   Status: {data.get('status', 'N/A')}")
    print(f"   Message: {data.get('message', 'N/A')}")
    
    if 'output' in data and data['output']:
        print(f"   📄 Output: {len(data['output'])} caracteres")
        print(f"   📄 Primeros 200 chars: {data['output'][:200]}...")
        
        # Actualizar el paso en nuestra lista local
        for step in received_data['plan_steps']:
            if step.get('id') == data.get('step_id'):
                step['output'] = data['output']
                step['status'] = data.get('status')
                print(f"   ✅ Paso actualizado localmente")
                break
    else:
        print(f"   ⚠️ No hay output en esta actualización")
    
    received_data['step_updates'].append(data)

@sio.on('plan_completed')
def plan_completed(data):
    print(f"\n🎉 Plan completado!")
    if 'final_summary' in data:
        print(f"📊 Resumen final: {len(data['final_summary'])} caracteres")

@sio.on('message_response')
def message_response(data):
    print(f"💬 Respuesta del mensaje recibida: {data.get('response', 'Sin respuesta')[:100]}...")

def test_frontend_data_reception():
    """Prueba la recepción de datos del frontend"""
    try:
        # Conectar al servidor
        print("🔌 Conectando al servidor...")
        sio.connect('http://localhost:5000')
        
        # Enviar mensaje de prueba usando el evento correcto
        print("📤 Enviando mensaje de prueba...")
        sio.emit('user_message', {
            'message': 'Crear un plan de prueba para verificar outputs',
            'user_id': 'test_user'
        })
        
        # Esperar a que se complete el plan
        print("⏳ Esperando respuesta del servidor...")
        time.sleep(20)  # Esperar 20 segundos para que se complete
        
        # Mostrar resumen de datos recibidos
        print("\n" + "="*50)
        print("📊 RESUMEN DE DATOS RECIBIDOS")
        print("="*50)
        
        if received_data['plan_generated']:
            plan = received_data['plan_generated'].get('plan', {})
            print(f"✅ Plan generado: {plan.get('title', 'Sin título')}")
            print(f"📋 Número de pasos: {len(received_data['plan_steps'])}")
        else:
            print("❌ No se recibió plan generado")
        
        print(f"🔄 Actualizaciones de pasos recibidas: {len(received_data['step_updates'])}")
        
        # Verificar outputs en los pasos
        steps_with_output = 0
        for step in received_data['plan_steps']:
            if step.get('output'):
                steps_with_output += 1
                print(f"✅ Paso {step.get('id')}: {step.get('title')} - Output: {len(step['output'])} chars")
            else:
                print(f"❌ Paso {step.get('id')}: {step.get('title')} - Sin output")
        
        print(f"\n📊 Pasos con output: {steps_with_output}/{len(received_data['plan_steps'])}")
        
        # Guardar datos para análisis
        with open('frontend_test_data.json', 'w', encoding='utf-8') as f:
            json.dump(received_data, f, indent=2, ensure_ascii=False)
        print("💾 Datos guardados en 'frontend_test_data.json'")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_frontend_data_reception()