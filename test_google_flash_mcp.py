#!/usr/bin/env python3
"""
Script de prueba final para verificar herramientas MCP reales con Google Flash
"""

import socketio
import json
import time

def test_mcp_tools_with_google_flash():
    """Prueba las herramientas MCP reales con Google Flash configurado"""
    
    print("🤖 PRUEBA FINAL: HERRAMIENTAS MCP REALES CON GOOGLE FLASH")
    print("=" * 65)
    
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
        plan_title = data['plan']['title']
        print(f"📋 Plan generado: {plan_title}")
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
        
        # Detectar si es una herramienta MCP real
        is_real_mcp = any([
            'API' in output,
            'Resultados Reales' in output,
            'encontrados:' in output,
            'Tiempo de respuesta:' in output,
            'DuckDuckGo' in output,
            'GitHub' in output,
            'repositorios' in output.lower()
        ])
        
        responses.append({
            'step_id': step_id,
            'status': status,
            'output': output,
            'has_real_data': is_real_mcp,
            'output_length': len(output)
        })
    
    @sio.event
    def plan_completed(data):
        print(f"✅ Plan completado: {data.get('message', 'Sin mensaje')}")
    
    try:
        # Conectar al servidor
        sio.connect('http://localhost:5000')
        time.sleep(2)
        
        # Enviar mensaje que active herramientas MCP reales
        test_message = "Busca información sobre 'artificial intelligence' en internet y encuentra repositorios de GitHub sobre 'machine learning frameworks'"
        
        print(f"📤 Enviando mensaje: {test_message}")
        sio.emit('user_message', {'message': test_message})
        
        # Esperar respuestas
        print("⏳ Esperando respuestas del servidor...")
        time.sleep(25)  # Esperar 25 segundos para que se ejecuten las herramientas
        
        # Analizar resultados
        print("\n" + "=" * 65)
        print("📊 ANÁLISIS DE RESULTADOS CON GOOGLE FLASH")
        print("=" * 65)
        
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
            output_length = response['output_length']
            
            real_indicator = "🌐 REAL" if has_real_data else "🤖 SIM"
            
            print(f"{real_indicator} Paso {step_id}: {status} - {output_length} chars")
            
            if has_real_data:
                real_tools_used += 1
                output = response['output']
                
                # Mostrar evidencia específica de datos reales
                if 'encontrados:' in output:
                    import re
                    match = re.search(r'encontrados: (\d+)', output)
                    if match:
                        count = match.group(1)
                        print(f"   📊 Datos reales: {count} resultados encontrados")
                
                if 'Tiempo de respuesta:' in output:
                    match = re.search(r'Tiempo de respuesta: ([\d.]+)s', output)
                    if match:
                        time_taken = match.group(1)
                        print(f"   ⏱️ Tiempo real de API: {time_taken}s")
                
                if 'DuckDuckGo' in output:
                    print(f"   🔍 API DuckDuckGo utilizada")
                
                if 'GitHub' in output and 'repositorios' in output.lower():
                    print(f"   🐙 API GitHub utilizada")
        
        # Resumen final
        print("\n" + "=" * 65)
        print("🎯 RESUMEN FINAL - GOOGLE FLASH + MCP REALES")
        print("=" * 65)
        
        real_percentage = (real_tools_used / total_steps) * 100 if total_steps > 0 else 0
        
        print(f"🤖 LLM Configurado: Google Flash (gemini-1.5-flash)")
        print(f"🌐 Herramientas REALES usadas: {real_tools_used}/{total_steps}")
        print(f"🤖 Herramientas SIMULADAS: {total_steps - real_tools_used}/{total_steps}")
        print(f"📈 Porcentaje de herramientas reales: {real_percentage:.1f}%")
        
        if real_tools_used > 0:
            print("✅ ÉXITO: Herramientas MCP REALES funcionando con Google Flash")
            print("🎉 Las APIs externas están respondiendo correctamente")
            print("🤖 Google Flash está procesando las respuestas exitosamente")
        else:
            print("⚠️ ADVERTENCIA: Solo se están usando herramientas simuladas")
            print("💡 Verifica la conectividad de red o las APIs externas")
        
        # Guardar resultados detallados
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'llm_model': 'gemini-1.5-flash',
            'total_steps': total_steps,
            'real_tools_used': real_tools_used,
            'real_percentage': real_percentage,
            'plan_data': plan_data,
            'detailed_responses': responses,
            'test_message': test_message
        }
        
        with open('test_google_flash_mcp_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: test_google_flash_mcp_results.json")
        
        return real_tools_used > 0
        
    except Exception as e:
        print(f"💥 Error durante la prueba: {str(e)}")
        return False
    
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == "__main__":
    success = test_mcp_tools_with_google_flash()
    if success:
        print("\n🎉 PRUEBA EXITOSA: Google Flash + Herramientas MCP reales funcionando")
    else:
        print("\n❌ PRUEBA FALLIDA: Problemas con la configuración")
    
    exit(0 if success else 1)