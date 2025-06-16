#!/usr/bin/env python3
"""
Script para probar si las herramientas MCP están realmente usando APIs o solo simulando
Hace dos solicitudes diferentes y compara si los resultados son idénticos (simulados) o diferentes (reales)
"""

import socketio
import json
import time
import hashlib

def test_real_vs_simulated():
    """Prueba si las herramientas MCP están simuladas o son reales"""
    
    print("🔍 PRUEBA: DETECCIÓN DE SIMULACIÓN VS REAL")
    print("=" * 50)
    
    # Dos mensajes diferentes para probar
    test_messages = [
        "Busca información sobre 'python programming' en GitHub",
        "Busca información sobre 'javascript frameworks' en GitHub"
    ]
    
    results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🧪 PRUEBA {i}/2: {message}")
        print("-" * 50)
        
        # Conectar al servidor
        sio = socketio.Client()
        
        # Variables para capturar respuestas
        responses = []
        
        @sio.event
        def connect():
            print(f"✅ Conectado para prueba {i}")
        
        @sio.event
        def disconnect():
            print(f"❌ Desconectado de prueba {i}")
        
        @sio.event
        def plan_generated(data):
            print(f"📋 Plan generado: {data['plan']['title']}")
        
        @sio.event
        def plan_step_update(data):
            step_id = data.get('step_id')
            status = data.get('status')
            output = data.get('output', '')
            
            if status == 'completed' and output:
                print(f"🔧 Paso {step_id} completado - {len(output)} chars")
                responses.append({
                    'step_id': step_id,
                    'output': output,
                    'output_hash': hashlib.md5(output.encode()).hexdigest()[:8]
                })
        
        @sio.event
        def plan_completed(data):
            print(f"✅ Plan {i} completado")
        
        try:
            # Conectar y enviar mensaje
            sio.connect('http://localhost:5000')
            time.sleep(2)
            
            print(f"📤 Enviando: {message}")
            sio.emit('user_message', {'message': message})
            
            # Esperar respuestas
            time.sleep(15)  # Esperar 15 segundos
            
            results.append({
                'test_number': i,
                'message': message,
                'responses': responses
            })
            
        except Exception as e:
            print(f"💥 Error en prueba {i}: {str(e)}")
        
        finally:
            if sio.connected:
                sio.disconnect()
        
        time.sleep(3)  # Pausa entre pruebas
    
    # Analizar resultados
    print("\n" + "=" * 50)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("=" * 50)
    
    if len(results) < 2:
        print("❌ No se pudieron completar ambas pruebas")
        return False
    
    # Comparar respuestas
    test1_responses = results[0]['responses']
    test2_responses = results[1]['responses']
    
    print(f"🧪 Prueba 1: {len(test1_responses)} respuestas")
    print(f"🧪 Prueba 2: {len(test2_responses)} respuestas")
    
    if not test1_responses or not test2_responses:
        print("❌ Una o ambas pruebas no generaron respuestas")
        return False
    
    # Comparar outputs paso a paso
    identical_outputs = 0
    different_outputs = 0
    
    print("\n📋 COMPARACIÓN DETALLADA:")
    print("-" * 30)
    
    max_steps = max(len(test1_responses), len(test2_responses))
    
    for i in range(max_steps):
        if i < len(test1_responses) and i < len(test2_responses):
            output1 = test1_responses[i]['output']
            output2 = test2_responses[i]['output']
            hash1 = test1_responses[i]['output_hash']
            hash2 = test2_responses[i]['output_hash']
            
            step_id = test1_responses[i]['step_id']
            
            if output1 == output2:
                print(f"🤖 Paso {step_id}: IDÉNTICO (Hash: {hash1}) - SIMULADO")
                identical_outputs += 1
                
                # Mostrar evidencia de simulación
                if "Simulación de" in output1 or "datos ficticios" in output1.lower():
                    print(f"   📝 Evidencia: Contiene texto de simulación")
                elif len(output1) < 200:
                    print(f"   📝 Evidencia: Output muy corto ({len(output1)} chars)")
                
            else:
                print(f"🌐 Paso {step_id}: DIFERENTE - POSIBLEMENTE REAL")
                print(f"   📊 Hash 1: {hash1} ({len(output1)} chars)")
                print(f"   📊 Hash 2: {hash2} ({len(output2)} chars)")
                different_outputs += 1
                
                # Buscar evidencia de datos reales
                real_indicators = [
                    'encontrados:', 'Tiempo de respuesta:', 'API', 
                    'repositorios', 'resultados', 'GitHub', 'DuckDuckGo'
                ]
                
                found_indicators = []
                for indicator in real_indicators:
                    if indicator in output1 or indicator in output2:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"   🔍 Indicadores reales: {', '.join(found_indicators)}")
    
    # Resumen final
    print("\n" + "=" * 50)
    print("🎯 VEREDICTO FINAL")
    print("=" * 50)
    
    total_comparisons = identical_outputs + different_outputs
    simulation_percentage = (identical_outputs / total_comparisons) * 100 if total_comparisons > 0 else 0
    
    print(f"📊 Total comparaciones: {total_comparisons}")
    print(f"🤖 Outputs idénticos: {identical_outputs}")
    print(f"🌐 Outputs diferentes: {different_outputs}")
    print(f"📈 Porcentaje simulado: {simulation_percentage:.1f}%")
    
    if simulation_percentage >= 80:
        print("\n❌ VEREDICTO: HERRAMIENTAS COMPLETAMENTE SIMULADAS")
        print("💡 Las respuestas son idénticas independientemente de la consulta")
        print("🔧 Las herramientas MCP NO están usando APIs reales")
        
        # Mostrar evidencia
        if test1_responses:
            sample_output = test1_responses[0]['output'][:200]
            print(f"\n📝 Muestra de output simulado:")
            print(f"   {sample_output}...")
        
        return False
        
    elif simulation_percentage >= 50:
        print("\n⚠️ VEREDICTO: PARCIALMENTE SIMULADO")
        print("💡 Algunas herramientas usan APIs reales, otras están simuladas")
        print(f"🌐 {different_outputs} herramientas parecen usar APIs reales")
        return True
        
    else:
        print("\n✅ VEREDICTO: HERRAMIENTAS MAYORMENTE REALES")
        print("💡 Las respuestas son diferentes, indicando uso de APIs reales")
        print("🌐 Las herramientas MCP están funcionando correctamente")
        return True
    
    # Guardar resultados detallados
    detailed_results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_messages': test_messages,
        'results': results,
        'analysis': {
            'total_comparisons': total_comparisons,
            'identical_outputs': identical_outputs,
            'different_outputs': different_outputs,
            'simulation_percentage': simulation_percentage
        }
    }
    
    with open('test_simulation_detection.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados detallados guardados en: test_simulation_detection.json")

if __name__ == "__main__":
    success = test_real_vs_simulated()
    if success:
        print("\n🎉 RESULTADO: Herramientas MCP funcionando (al menos parcialmente)")
    else:
        print("\n❌ RESULTADO: Herramientas MCP completamente simuladas")
    
    exit(0 if success else 1)