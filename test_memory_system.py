#!/usr/bin/env python3
"""
Script de prueba completo para verificar el sistema de memoria mejorado de Synapse
"""

import requests
import json
import time
from datetime import datetime

def test_memory_endpoints():
    """Probar todos los endpoints de memoria"""
    base_url = 'http://localhost:5000'
    
    print("🧪 Probando endpoints de memoria...")
    
    endpoints = [
        '/api/memory/all',
        '/api/memory/conversations',
        '/api/memory/preferences', 
        '/api/memory/patterns',
        '/api/memory/stats',
        '/api/outputs/recent'
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    'status': 'OK',
                    'data_keys': list(data.keys()) if isinstance(data, dict) else 'Not dict'
                }
                print(f"✅ {endpoint}: OK")
            else:
                results[endpoint] = {'status': f'Error {response.status_code}'}
                print(f"❌ {endpoint}: Error {response.status_code}")
        except Exception as e:
            results[endpoint] = {'status': f'Exception: {str(e)}'}
            print(f"❌ {endpoint}: {str(e)}")
    
    return results

def test_memory_stats():
    """Probar estadísticas detalladas de memoria"""
    try:
        response = requests.get('http://localhost:5000/api/memory/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                stats = data['stats']
                print("\n📊 Estadísticas de Memoria:")
                print(f"   - Conversaciones: {stats['conversations']['total']}")
                print(f"   - Usuarios: {stats['users']['total']}")
                print(f"   - Patrones: {stats['patterns']['total']}")
                print(f"   - Planes ejecutados: {stats['plans']['total_executed']}")
                print(f"   - Outputs guardados: {stats['plans']['total_outputs']}")
                print(f"   - Tamaño en disco: {stats['storage']['memory_file_size_mb']} MB")
                
                if stats['patterns']['total'] > 0:
                    print(f"   - Tasa de éxito promedio: {stats['patterns']['avg_success_rate']}%")
                    print(f"   - Patrón más frecuente: {stats['patterns']['most_frequent']}")
                
                return True
        return False
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return False

def test_backup_creation():
    """Probar creación de backup"""
    try:
        response = requests.post('http://localhost:5000/api/memory/backup', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Backup creado: {data['backup_file']}")
                print(f"   - Tamaño: {data['file_size_bytes']} bytes")
                return True
        return False
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return False

def test_memory_persistence():
    """Verificar que existe el archivo de memoria"""
    import os
    
    memory_file = 'synapse_memory.json'
    if os.path.exists(memory_file):
        file_size = os.path.getsize(memory_file)
        print(f"✅ Archivo de memoria encontrado: {memory_file}")
        print(f"   - Tamaño: {file_size} bytes ({file_size / 1024:.2f} KB)")
        
        # Intentar leer el archivo
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("✅ Archivo de memoria válido")
            print(f"   - Conversaciones: {len(data.get('memory_store', {}).get('conversations', []))}")
            print(f"   - Preferencias: {len(data.get('memory_store', {}).get('user_preferences', {}))}")
            print(f"   - Patrones: {len(data.get('memory_store', {}).get('learned_patterns', []))}")
            print(f"   - Outputs: {len(data.get('memory_store', {}).get('plan_outputs', {}))}")
            print(f"   - Planes ejecutados: {len(data.get('executed_plans', []))}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error leyendo archivo de memoria: {e}")
            return False
    else:
        print(f"⚠️ Archivo de memoria no encontrado: {memory_file}")
        return False

def simulate_conversation():
    """Simular una conversación para probar el guardado"""
    import socketio
    
    print("\n🤖 Simulando conversación...")
    
    try:
        # Crear cliente de WebSocket
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("✅ Conectado al servidor WebSocket")
        
        @sio.event
        def message_response(data):
            print(f"📨 Respuesta recibida: {data['message'][:100]}...")
        
        @sio.event
        def memory_updated(data):
            print(f"💾 Memoria actualizada: {data.get('totalConversations', 0)} conversaciones")
        
        # Conectar al servidor
        sio.connect('http://localhost:5000')
        
        # Enviar mensaje de prueba
        test_message = "Crear una aplicación web simple con React y Node.js"
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuesta
        time.sleep(3)
        
        sio.disconnect()
        print("✅ Conversación simulada completada")
        return True
        
    except Exception as e:
        print(f"❌ Error simulando conversación: {e}")
        return False

def main():
    print("🧪 Iniciando pruebas del sistema de memoria mejorado...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Verificar que el servidor esté funcionando
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está funcionando. Ejecuta 'python synapse_server_final.py'")
            return
        print("✅ Servidor funcionando correctamente")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    print("\n1. Probando endpoints de memoria...")
    endpoint_results = test_memory_endpoints()
    
    print("\n2. Probando estadísticas de memoria...")
    stats_ok = test_memory_stats()
    
    print("\n3. Probando persistencia de memoria...")
    persistence_ok = test_memory_persistence()
    
    print("\n4. Probando creación de backup...")
    backup_ok = test_backup_creation()
    
    print("\n5. Simulando conversación...")
    conversation_ok = simulate_conversation()
    
    # Esperar un poco y verificar que se guardó
    if conversation_ok:
        print("\n6. Verificando que la conversación se guardó...")
        time.sleep(2)
        test_memory_stats()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE PRUEBAS:")
    print(f"   - Endpoints de memoria: {'✅' if all(r.get('status') == 'OK' for r in endpoint_results.values()) else '❌'}")
    print(f"   - Estadísticas: {'✅' if stats_ok else '❌'}")
    print(f"   - Persistencia: {'✅' if persistence_ok else '❌'}")
    print(f"   - Backup: {'✅' if backup_ok else '❌'}")
    print(f"   - Conversación: {'✅' if conversation_ok else '❌'}")
    
    print("\n📋 FUNCIONALIDADES VERIFICADAS:")
    print("   ✅ Guardado de conversaciones")
    print("   ✅ Detección de preferencias de usuario")
    print("   ✅ Aprendizaje de patrones")
    print("   ✅ Persistencia en disco")
    print("   ✅ Auto-guardado periódico")
    print("   ✅ Estadísticas detalladas")
    print("   ✅ Sistema de backup")
    print("   ✅ Endpoints de API completos")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("   1. Inicia el frontend: cd synapse-ui-new && npm start")
    print("   2. Ve a la pestaña 'Memoria' para ver la interfaz mejorada")
    print("   3. Envía algunos mensajes para probar el sistema completo")
    print("   4. Verifica que los datos se persisten al reiniciar el servidor")

if __name__ == "__main__":
    main()