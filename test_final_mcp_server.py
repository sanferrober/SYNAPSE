#!/usr/bin/env python3
"""
Script de prueba final para verificar herramientas MCP reales en el servidor
"""

import socketio
import json
import time

def test_real_mcp_tools_server():
    """Prueba las herramientas MCP reales a través del servidor"""
    
    print("🧪 PRUEBA FINAL: HERRAMIENTAS MCP REALES EN SERVIDOR")
    print("=" * 60)
    
    # Conectar al servidor
    sio = socketio.Client()
    
    # Variables para capturar respuestas
    responses = []
    plan_data = {}
    
    @sio.event
    def connect():
        print("✅ Conectado al servidor Synapse")
    
    @sio.event
    def disconnect():
        print("❌ Desconectado del servidor")
    
    @sio.event
    def plan_generated(data):
        print(f"📋 Plan generado: {data['plan']['title']}")
        plan_data['plan'] = data['plan']
        plan_data['steps'] = data['plan']['steps']
    
    @sio.event
    def plan_step_update(data):
        step_id = data.get('step_id')
        status = data.get('status')
        output = data.get('output', '')
        
        print(f"🔧 Paso {step_id}: {status}")
        if output and len(output) > 100:
            print(f"   📊 Output: {output[:100]}...")
        
        responses.append({
            'step_id': step_id,
            'status': status,
            'output': output,
            'has_real_data': 'API' in output or 'Resultados Reales' in output or 'encontrados:' in output
        })
    
    @sio.event
    def plan_completed(data):
        print(f"✅ Plan completado: {data.get('message', 'Sin mensaje')}")
    
    try:
        # Conectar al servidor
        sio.connect('http://localhost:5000')
        time.sleep(2)
        
        # Enviar mensaje que active herramientas MCP reales
        test_message = "Busca información sobre 'python machine learning' y repositorios de GitHub sobre 'react components'"
        
        print(f"📤 Enviando mensaje: {test_message}")
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuestas
        print("⏳ Esperando respuestas del servidor...")
        time.sleep(20)  # Esperar 20 segundos para que se ejecuten las herramientas
        
        # Analizar resultados
        print("\n" + "=" * 60)
        print("📊 ANÁLISIS DE RESULTADOS")
        print("=" * 60)
        
        if not responses:
            print("❌ No se recibieron respuestas del servidor")
            return False
        
        real_tools_used = 0
        total_steps = len(responses)
        
        print(f"📈 Total de pasos ejecutados: {total_steps}")
        
        for i, response in enumerate(responses, 1):
            step_id = response['step_id']
            status = response['status']
            has_real_data = response['has_real_data']
            output_length = len(response['output'])
            
            real_indicator = "🌐 REAL" if has_real_data else "🤖 SIM"
            
            print(f"{real_indicator} Paso {step_id}: {status} - {output_length} chars")
            
            if has_real_data:
                real_tools_used += 1
                # Mostrar evidencia de datos reales
                output = response['output']
                if 'encontrados:' in output:
                    # Extraer número de resultados
                    import re
                    match = re.search(r'encontrados: (\d+)', output)
                    if match:
                        count = match.group(1)
                        print(f"   📊 Datos reales: {count} resultados encontrados")
                
                if 'Tiempo de respuesta:' in output:
                    # Extraer tiempo de respuesta real
                    match = re.search(r'Tiempo de respuesta: ([\d.]+)s', output)
                    if match:
                        time_taken = match.group(1)
                        print(f"   ⏱️ Tiempo real de API: {time_taken}s")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("🎯 RESUMEN FINAL")
        print("=" * 60)
        
        real_percentage = (real_tools_used / total_steps) * 100 if total_steps > 0 else 0
        
        print(f"🌐 Herramientas REALES usadas: {real_tools_used}/{total_steps}")
        print(f"🤖 Herramientas SIMULADAS: {total_steps - real_tools_used}/{total_steps}")
        print(f"📈 Porcentaje de herramientas reales: {real_percentage:.1f}%")
        
        if real_tools_used > 0:
            print("✅ ÉXITO: Se están usando herramientas MCP REALES")
            print("🎉 Las APIs externas están funcionando correctamente")
        else:
            print("⚠️ ADVERTENCIA: Solo se están usando herramientas simuladas")
            print("💡 Verifica las claves de API o la conectividad de red")
        
        # Guardar resultados detallados
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_steps': total_steps,
            'real_tools_used': real_tools_used,
            'real_percentage': real_percentage,
            'plan_data': plan_data,
            'detailed_responses': responses
        }
        
        with open('test_final_mcp_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: test_final_mcp_results.json")
        
        return real_tools_used > 0
        
    except Exception as e:
        print(f"💥 Error durante la prueba: {str(e)}")
        return False
    
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == "__main__":
    success = test_real_mcp_tools_server()
    if success:
        print("\n🎉 PRUEBA EXITOSA: Herramientas MCP reales funcionando")
    else:
        print("\n❌ PRUEBA FALLIDA: Problemas con herramientas MCP reales")
    
    exit(0 if success else 1)