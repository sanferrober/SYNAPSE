#!/usr/bin/env python3
"""
Servidor de prueba simplificado para diagnosticar el problema de outputs
"""

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print(f"🔌 Cliente conectado: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('send_message')
def handle_message(data):
    print(f"📨 Mensaje recibido: {data}")
    
    # Crear un plan de prueba simple
    test_plan = {
        'id': 'test_plan_123',
        'title': 'Plan de Prueba',
        'steps': [
            {'id': 1, 'title': 'Paso 1', 'description': 'Primer paso', 'status': 'pending'},
            {'id': 2, 'title': 'Paso 2', 'description': 'Segundo paso', 'status': 'pending'}
        ]
    }
    
    # Enviar plan
    emit('plan_generated', {'plan': test_plan})
    
    # Ejecutar pasos con outputs
    def execute_test_plan():
        time.sleep(1)
        
        # Paso 1
        print("📋 Ejecutando paso 1...")
        emit('plan_step_update', {
            'plan_id': 'test_plan_123',
            'step_id': 1,
            'status': 'completed',
            'message': 'Paso 1 completado',
            'output': '🎯 OUTPUT DE PRUEBA PASO 1\n\nEste es un output de prueba para verificar que los outputs se muestran correctamente en el panel.\n\n✅ Funcionalidad: OK\n📊 Datos: Procesados\n🔧 Estado: Completado'
        })
        
        time.sleep(2)
        
        # Paso 2
        print("📋 Ejecutando paso 2...")
        emit('plan_step_update', {
            'plan_id': 'test_plan_123',
            'step_id': 2,
            'status': 'completed',
            'message': 'Paso 2 completado',
            'output': '🚀 OUTPUT DE PRUEBA PASO 2\n\nSegundo output de prueba con más contenido para verificar el funcionamiento.\n\n📈 Métricas:\n- Tiempo: 2.3s\n- Memoria: 45MB\n- CPU: 12%\n\n✅ Todo funcionando correctamente'
        })
        
        print("✅ Plan de prueba completado")
    
    # Ejecutar en hilo separado
    thread = threading.Thread(target=execute_test_plan)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    print("🧪 Servidor de prueba iniciado en puerto 5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)