import random
from datetime import datetime
import threading
import time
import psutil
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Importar funciones de generación de outputs
from output_generators import generate_step_output, generate_plan_summary

# Importar herramientas MCP CONSOLIDADAS (todas las anteriores + nuevas)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_integration'))
from consolidated_mcp_tools import get_consolidated_mcp_tools, execute_mcp_tool
# Estado del sistema con memoria persistente
system_state = {
    'active_connections': 0,
    'total_messages': 0,
    'active_plans': [],  # Lista de planes activos
    'executed_plans': [],  # Historial de planes ejecutados
    'memory_store': {      # Almacén de memoria persistente
        'conversations': [],
        'plan_outputs': {},
        'user_preferences': {},
        'learned_patterns': []
    },
    'last_activity': None,
    'server_start_time': datetime.now().isoformat()
}

# Herramientas disponibles - Combinando core y MCP expandidas
core_tools = [
    {'id': 'web_search', 'name': 'Búsqueda Web', 'enabled': True, 'category': 'Research', 'type': 'core'},
    {'id': 'data_analyzer', 'name': 'Analizador de Datos', 'enabled': True, 'category': 'Analysis', 'type': 'core'},
    {'id': 'code_generator', 'name': 'Generador de Código', 'enabled': True, 'category': 'Development', 'type': 'core'},
    {'id': 'task_planner', 'name': 'Planificador de Tareas', 'enabled': True, 'category': 'Planning', 'type': 'core'}
]

# Combinar herramientas core con MCP consolidadas
available_tools = core_tools + get_consolidated_mcp_tools()

def analyze_intent(message):
    """Análisis NLU mejorado para detectar intenciones"""
    message_lower = message.lower()
    
    patterns = {
        'create_app': ['crear app', 'desarrollar aplicación', 'hacer una app', 'build app', 'crear aplicación'],
        'analyze_data': ['analizar datos', 'análisis de datos', 'procesar datos', 'data analysis'],
        'plan_project': ['planificar proyecto', 'crear plan', 'organizar proyecto', 'project plan'],
        'research': ['buscar información', 'investigar', 'información sobre'],
        'help_general': ['ayuda', 'ayúdame', 'help', 'asistencia']
    }
    
    detected_intents = []
    for intent, keywords in patterns.items():
        for keyword in keywords:
            if keyword in message_lower:
                detected_intents.append(intent)
                break
    
    return detected_intents if detected_intents else ['help_general']

def generate_plan(message, intents):
    """Generador de planes inteligente basado en intenciones"""
    
    if 'create_app' in intents or 'plan_project' in intents:
        return {
            'id': f'plan_{int(time.time())}',
            'title': 'Plan de Desarrollo de Aplicación Web',
            'description': 'Plan completo para desarrollar una aplicación web moderna',
            'status': 'active',
            'progress': 0,
            'steps': [
                {
                    'id': 1,
                    'title': 'Análisis de Requisitos',
                    'description': 'Definir funcionalidades y especificaciones técnicas',
                    'status': 'pending',
                    'estimated_time': '2-3 horas',
                    'tools': ['web_search', 'data_analyzer']
                },
                {
                    'id': 2,
                    'title': 'Diseño de Arquitectura',
                    'description': 'Diseñar la estructura del sistema y base de datos',
                    'status': 'pending',
                    'estimated_time': '3-4 horas',
                    'tools': ['task_planner']
                },
                {
                    'id': 3,
                    'title': 'Desarrollo del Backend',
                    'description': 'Implementar API REST y lógica de negocio',
                    'status': 'pending',
                    'estimated_time': '8-12 horas',
                    'tools': ['code_generator']
                },
                {
                    'id': 4,
                    'title': 'Desarrollo del Frontend',
                    'description': 'Crear interfaz de usuario responsive',
                    'status': 'pending',
                    'estimated_time': '6-10 horas',
                    'tools': ['code_generator', 'web_search']
                },
                {
                    'id': 5,
                    'title': 'Testing y Deployment',
                    'description': 'Pruebas exhaustivas y despliegue en producción',
                    'status': 'pending',
                    'estimated_time': '4-6 horas',
                    'tools': ['task_planner', 'data_analyzer']
                }
            ],
            'total_estimated_time': '23-35 horas',
            'created_at': datetime.now().isoformat()
        }
    
    elif 'analyze_data' in intents:
        return {
            'id': f'plan_{int(time.time())}',
            'title': 'Plan de Análisis de Datos',
            'description': 'Análisis completo y visualización de datos',
            'status': 'active',
            'progress': 0,
            'steps': [
                {
                    'id': 1,
                    'title': 'Recolección de Datos',
                    'description': 'Obtener y validar fuentes de datos',
                    'status': 'pending',
                    'estimated_time': '1-2 horas',
                    'tools': ['web_search', 'data_analyzer']
                },
                {
                    'id': 2,
                    'title': 'Limpieza y Preparación',
                    'description': 'Procesar y limpiar los datos',
                    'status': 'pending',
                    'estimated_time': '2-3 horas',
                    'tools': ['data_analyzer', 'code_generator']
                },
                {
                    'id': 3,
                    'title': 'Análisis Exploratorio',
                    'description': 'Identificar patrones y tendencias',
                    'status': 'pending',
                    'estimated_time': '3-4 horas',
                    'tools': ['data_analyzer']
                },
                {
                    'id': 4,
                    'title': 'Visualización',
                    'description': 'Crear gráficos y dashboards',
                    'status': 'pending',
                    'estimated_time': '2-3 horas',
                    'tools': ['data_analyzer', 'code_generator']
                }
            ],
            'total_estimated_time': '8-12 horas',
            'created_at': datetime.now().isoformat()
        }
    
    else:
        return {
            'id': f'plan_{int(time.time())}',
            'title': 'Plan de Asistencia General',
            'description': 'Plan personalizado basado en tu solicitud',
            'status': 'active',
            'progress': 0,
            'steps': [
                {
                    'id': 1,
                    'title': 'Análisis de Solicitud',
                    'description': 'Entender los requisitos específicos',
                    'status': 'pending',
                    'estimated_time': '15-30 minutos',
                    'tools': ['task_planner']
                },
                {
                    'id': 2,
                    'title': 'Investigación',
                    'description': 'Buscar información relevante',
                    'status': 'pending',
                    'estimated_time': '30-60 minutos',
                    'tools': ['web_search']
                },
                {
                    'id': 3,
                    'title': 'Implementación',
                    'description': 'Ejecutar la solución propuesta',
                    'status': 'pending',
                    'estimated_time': '1-2 horas',
                    'tools': ['code_generator', 'data_analyzer']
                }
            ],
            'total_estimated_time': '2-3 horas',
            'created_at': datetime.now().isoformat()
        }

def generate_response(message, plan):
    """Generar respuesta contextual inteligente"""
    responses = [
        f"¡Perfecto! He analizado tu solicitud y he creado un plan detallado: '{plan['title']}'. Este plan incluye {len(plan['steps'])} pasos principales con un tiempo estimado de {plan['total_estimated_time']}.",
        f"Excelente idea. He generado un plan completo para '{plan['title']}' que te guiará paso a paso. El plan está optimizado para completarse en aproximadamente {plan['total_estimated_time']}.",
        f"¡Genial! He creado un plan estratégico llamado '{plan['title']}' con {len(plan['steps'])} fases bien definidas. Tiempo estimado total: {plan['total_estimated_time']}."
    ]
    
    return random.choice(responses)

def process_message_with_context(message, sid):
    """Procesar mensaje con contexto de aplicación Flask"""
    try:
        with app.app_context():
            print(f"📨 Procesando mensaje: {message}")
            
            # Análisis NLU
            intents = analyze_intent(message)
            print(f"🧠 Intenciones detectadas: {intents}")
            
            # Generar plan
            plan = generate_plan(message, intents)
            if 'active_plans' not in system_state:
                system_state['active_plans'] = []
            system_state['active_plans'].append(plan)
            print(f"📋 Plan generado: {plan['title']}")
            
            # Generar respuesta
            response = generate_response(message, plan)
            print(f"💬 Respuesta generada: {response[:100]}...")
            
            # Emitir eventos con contexto correcto
            print(f"📤 Emitiendo message_response...")
            socketio.emit('message_response', {
                'message': response,
                'timestamp': datetime.now().isoformat(),
                'type': 'assistant'
            }, room=sid)
            
            print(f"📤 Emitiendo plan_generated...")
            socketio.emit('plan_generated', {
                'plan': plan,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
            
            # Iniciar ejecución automática del plan
            print(f"🚀 Iniciando ejecución automática del plan...")
            execute_plan_automatically(plan, sid)
            
            # Actualizar estado del sistema
            system_state['total_messages'] += 1
            system_state['last_activity'] = datetime.now().isoformat()
            
            print(f"✅ Mensaje procesado exitosamente")
            
            # Marcar como no procesando después de generar plan
            print(f"📤 Emitiendo processing_complete...")
            socketio.emit('processing_complete', {
                'timestamp': datetime.now().isoformat()
            }, room=sid)
            
    except Exception as e:
        print(f"❌ Error procesando mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        
        try:
            with app.app_context():
                socketio.emit('error', {
                    'message': f'Error procesando tu solicitud: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }, room=sid)
                
                # También emitir processing_complete en caso de error
                socketio.emit('processing_complete', {
                    'timestamp': datetime.now().isoformat(),
                    'error': True
                }, room=sid)
        except Exception as emit_error:
            print(f"❌ Error emitiendo error: {emit_error}")

def execute_plan_automatically(plan, sid):
    """Ejecutar plan automáticamente paso a paso con manejo robusto de errores"""
    
    def execute_steps():
        try:
            with app.app_context():
                plan_id = plan['id']
                steps = plan['steps']
                
                print(f"🔄 Iniciando ejecución de {len(steps)} pasos para plan: {plan['title']}")
                
                # Marcar inicio de ejecución
                plan['start_time'] = time.time()
                
                for i, step in enumerate(steps):
                    try:
                        print(f"📋 Ejecutando paso {i+1}/{len(steps)}: {step['title']}")
                        
                        # Marcar paso actual como en progreso
                        step['status'] = 'in_progress'
                        
                        socketio.emit('plan_step_update', {
                            'plan_id': plan_id,
                            'step_id': step['id'],
                            'status': 'in_progress',
                            'timestamp': datetime.now().isoformat(),
                            'message': f"Ejecutando: {step['title']}"
                        }, room=sid)
                        
                        # Simular tiempo de ejecución (2-5 segundos por paso)
                        execution_time = random.uniform(2, 5)
                        print(f"⏱️ Tiempo de ejecución simulado: {execution_time:.1f}s")
                        time.sleep(execution_time)
                        
                        # Generar output realista para el paso
                        try:
                            step_output = generate_step_output(step, i + 1, len(steps))
                            step['output'] = step_output
                            print(f"📄 Output generado: {len(step_output)} caracteres")
                        except Exception as output_error:
                            print(f"❌ Error generando output: {output_error}")
                            step['output'] = f"Error generando output: {str(output_error)}"
                        
                        # Marcar paso como completado
                        step['status'] = 'completed'
                        
                        socketio.emit('plan_step_update', {
                            'plan_id': plan_id,
                            'step_id': step['id'],
                            'status': 'completed',
                            'timestamp': datetime.now().isoformat(),
                            'message': f"Completado: {step['title']}",
                            'output': step.get('output', 'Sin output generado')
                        }, room=sid)
                        
                        # Actualizar progreso del plan
                        progress = ((i + 1) / len(steps)) * 100
                        
                        socketio.emit('plan_progress_update', {
                            'plan_id': plan_id,
                            'progress': progress,
                            'current_step': i + 1,
                            'total_steps': len(steps),
                            'timestamp': datetime.now().isoformat()
                        }, room=sid)
                        
                        print(f"✅ Paso {i+1}/{len(steps)} completado exitosamente")
                        
                    except Exception as step_error:
                        print(f"❌ Error en paso {i+1}: {step_error}")
                        step['status'] = 'error'
                        step['error'] = str(step_error)
                        
                        socketio.emit('plan_step_update', {
                            'plan_id': plan_id,
                            'step_id': step['id'],
                            'status': 'error',
                            'timestamp': datetime.now().isoformat(),
                            'message': f"Error en: {step['title']}",
                            'error': str(step_error)
                        }, room=sid)
                
                # Generar resumen final del plan
                try:
                    final_summary = generate_plan_summary(plan, steps)
                    print(f"📊 Resumen final generado: {len(final_summary)} caracteres")
                except Exception as summary_error:
                    print(f"❌ Error generando resumen: {summary_error}")
                    final_summary = f"Plan completado con {len(steps)} pasos. Error generando resumen: {str(summary_error)}"
                
                # Marcar plan como completado y GUARDAR EN MEMORIA
                plan['status'] = 'completed'
                plan['progress'] = 100
                plan['final_summary'] = final_summary
                plan['completion_time'] = datetime.now().isoformat()
                
                # GUARDAR PLAN EJECUTADO EN MEMORIA PERSISTENTE
                executed_plan = {
                    'id': plan_id,
                    'title': plan['title'],
                    'steps': steps,
                    'final_summary': final_summary,
                    'completion_time': plan['completion_time'],
                    'total_outputs': len([s for s in steps if s.get('output')]),
                    'execution_duration': time.time() - plan.get('start_time', time.time())
                }
                
                # Añadir a historial de planes ejecutados
                system_state['executed_plans'].append(executed_plan)
                
                # Guardar outputs en memoria por plan_id
                system_state['memory_store']['plan_outputs'][plan_id] = {
                    'plan_title': plan['title'],
                    'steps_outputs': {step['id']: step.get('output', '') for step in steps if step.get('output')},
                    'final_summary': final_summary,
                    'timestamp': plan['completion_time']
                }
                
                print(f"💾 Plan guardado en memoria: {plan['title']}")
                print(f"📊 Total planes en memoria: {len(system_state['executed_plans'])}")
                print(f"📄 Outputs guardados: {len([s for s in steps if s.get('output')])}")
                
                socketio.emit('plan_completed', {
                    'plan_id': plan_id,
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Plan '{plan['title']}' completado exitosamente",
                    'final_summary': final_summary,
                    'total_outputs': len([s for s in steps if s.get('output')]),
                    'saved_to_memory': True  # Indicar que se guardó en memoria
                }, room=sid)
                
                print(f"🎉 Plan completado exitosamente: {plan['title']}")
                
        except Exception as e:
            print(f"❌ Error crítico ejecutando plan: {str(e)}")
            import traceback
            traceback.print_exc()
            
            try:
                with app.app_context():
                    socketio.emit('plan_error', {
                        'plan_id': plan['id'],
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'message': 'Error crítico durante la ejecución del plan'
                    }, room=sid)
            except Exception as emit_error:
                print(f"❌ Error emitiendo error crítico: {emit_error}")
    
    # Ejecutar en hilo separado para no bloquear
    thread = threading.Thread(target=execute_steps)
    thread.daemon = True
    thread.start()
    print(f"🧵 Hilo de ejecución iniciado para plan: {plan['title']}")

# Eventos WebSocket
@socketio.on('connect')
def handle_connect():
    system_state['active_connections'] += 1
    print(f"🔌 Cliente conectado: {request.sid}")
    
    # Enviar estado de conexión y métricas iniciales
    emit('connection_status', {'status': 'connected', 'message': 'Conectado a Synapse'})
    
    # Enviar métricas del sistema inmediatamente
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        emit('system_metrics', {
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1),
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'active_connections': system_state['active_connections'],
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"📊 Métricas enviadas: CPU {cpu_percent}%, RAM {memory.percent}%")
    except Exception as e:
        print(f"❌ Error enviando métricas: {e}")
        emit('system_metrics', {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_used_gb': 0,
            'memory_total_gb': 0,
            'active_connections': system_state['active_connections'],
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('disconnect')
def handle_disconnect():
    system_state['active_connections'] -= 1
    print(f"🔌 Cliente desconectado: {request.sid}")

@socketio.on('user_message')
def handle_message(data):
    message = data.get('text', '') or data.get('message', '')
    print(f"📨 Mensaje recibido del cliente {request.sid}: {message}")
    
    if not message.strip():
        print("⚠️ Mensaje vacío recibido")
        emit('error', {
            'message': 'Mensaje vacío recibido',
            'timestamp': datetime.now().isoformat()
        })
        return
    
    # Emitir confirmación inmediata de recepción
    emit('message_received', {
        'message': 'Mensaje recibido, procesando...',
        'timestamp': datetime.now().isoformat()
    })
    
    # Procesar en hilo separado con contexto
    thread = threading.Thread(
        target=process_message_with_context,
        args=(message, request.sid)
    )
    thread.daemon = True
    thread.start()
    print(f"🧵 Hilo de procesamiento iniciado para mensaje: {message[:50]}...")

# API REST Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1.0',
        'active_connections': system_state['active_connections'],
        'total_messages': system_state['total_messages'],
        'active_plans': len(system_state['active_plans'])
    })

@app.route('/api/tools', methods=['GET'])
def get_tools():
    return jsonify({
        'tools': available_tools,
        'total': len(available_tools),
        'enabled': len([t for t in available_tools if t['enabled']])
    })

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return jsonify({
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1),
            'active_connections': system_state['active_connections'],
            'total_messages': system_state['total_messages'],
            'active_plans': len(system_state['active_plans']),
            'server_uptime': system_state['server_start_time'],
            'last_activity': system_state['last_activity'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mcp/tools/expanded', methods=['GET'])
def get_expanded_mcp_tools_endpoint():
    """Endpoint para obtener todas las herramientas MCP expandidas"""
    mcp_tools = [t for t in available_tools if t.get('type') == 'mcp']
    categories = list(set([t['category'] for t in mcp_tools]))
    
    return jsonify({
        'mcp_tools': mcp_tools,
        'total_mcp_tools': len(mcp_tools),
        'total_tools': len(available_tools),
        'categories': sorted(categories),
        'enabled_tools': len([t for t in mcp_tools if t['enabled']]),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/mcp/tools/<tool_id>/execute', methods=['POST'])
def execute_mcp_tool_endpoint(tool_id):
    """Endpoint para ejecutar una herramienta MCP específica"""
    try:
        data = request.get_json() or {}
        parameters = data.get('parameters', {})
        
        # Verificar que la herramienta existe y está habilitada
        tool = next((t for t in available_tools if t['id'] == tool_id), None)
        if not tool:
            return jsonify({'error': f'Herramienta {tool_id} no encontrada'}), 404
        
        if not tool.get('enabled', False):
            return jsonify({'error': f'Herramienta {tool_id} está deshabilitada'}), 403
        
        # Ejecutar la herramienta
        result = execute_mcp_tool(tool_id, parameters)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/mcp/categories', methods=['GET'])
def get_mcp_categories():
    """Endpoint para obtener categorías de herramientas MCP"""
    mcp_tools = [t for t in available_tools if t.get('type') == 'mcp']
    categories = {}
    
    for tool in mcp_tools:
        category = tool['category']
        if category not in categories:
            categories[category] = {
                'name': category,
                'tools': [],
                'enabled_count': 0,
                'total_count': 0
            }
        
        categories[category]['tools'].append({
            'id': tool['id'],
            'name': tool['name'],
            'enabled': tool['enabled']
        })
        categories[category]['total_count'] += 1
        if tool['enabled']:
            categories[category]['enabled_count'] += 1
    
    return jsonify({
        'categories': list(categories.values()),
        'total_categories': len(categories),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Synapse Server v2.2.0...")
    print("🔧 Configuración:")
    print(f"   - Puerto: 5000")
    print(f"   - CORS: Habilitado para todos los orígenes")
    print(f"   - WebSocket: Habilitado")
    print(f"   - Herramientas disponibles: {len(available_tools)}")
    print(f"   - Herramientas MCP: {len([t for t in available_tools if t.get('type') == 'mcp'])}")
    print(f"   - Herramientas Core: {len([t for t in available_tools if t.get('type') == 'core'])}")
    print("✅ Servidor listo para recibir conexiones")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)



# Nuevos endpoints para memoria y outputs
@app.route('/api/memory/plans', methods=['GET'])
def get_executed_plans():
    """Obtener historial de planes ejecutados"""
    try:
        plans = system_state.get('executed_plans', [])
        return jsonify({
            'success': True,
            'plans': plans,
            'total_plans': len(plans),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/plan/<plan_id>/outputs', methods=['GET'])
def get_plan_outputs(plan_id):
    """Obtener outputs de un plan específico"""
    try:
        plan_outputs = system_state['memory_store']['plan_outputs'].get(plan_id)
        if not plan_outputs:
            return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'outputs': plan_outputs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/all', methods=['GET'])
def get_all_memory():
    """Obtener toda la memoria del sistema"""
    try:
        return jsonify({
            'success': True,
            'memory_store': system_state['memory_store'],
            'executed_plans': system_state['executed_plans'],
            'total_plans': len(system_state['executed_plans']),
            'total_outputs': len(system_state['memory_store']['plan_outputs']),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/clear', methods=['POST'])
def clear_memory():
    """Limpiar memoria del sistema"""
    try:
        system_state['executed_plans'] = []
        system_state['memory_store'] = {
            'conversations': [],
            'plan_outputs': {},
            'user_preferences': {},
            'learned_patterns': []
        }
        
        return jsonify({
            'success': True,
            'message': 'Memoria limpiada exitosamente',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/outputs/recent', methods=['GET'])
def get_recent_outputs():
    """Obtener outputs recientes de todos los planes"""
    try:
        recent_outputs = []
        
        # Obtener los últimos 10 planes ejecutados
        recent_plans = system_state['executed_plans'][-10:] if system_state['executed_plans'] else []
        
        for plan in recent_plans:
            plan_id = plan['id']
            plan_outputs = system_state['memory_store']['plan_outputs'].get(plan_id, {})
            
            if plan_outputs.get('steps_outputs'):
                recent_outputs.append({
                    'plan_id': plan_id,
                    'plan_title': plan['title'],
                    'completion_time': plan['completion_time'],
                    'outputs_count': len(plan_outputs['steps_outputs']),
                    'final_summary': plan_outputs.get('final_summary', ''),
                    'sample_outputs': list(plan_outputs['steps_outputs'].values())[:3]  # Primeros 3 outputs
                })
        
        return jsonify({
            'success': True,
            'recent_outputs': recent_outputs,
            'total_plans_with_outputs': len(recent_outputs),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Iniciando Synapse Server v2.3.0...")
    print("🔧 Configuración:")
    print(f"   - Puerto: 5000")
    print(f"   - CORS: Habilitado para todos los orígenes")
    print(f"   - WebSocket: Habilitado")
    print(f"   - Herramientas disponibles: {len(available_tools)}")
    print(f"   - Herramientas MCP: {len(get_consolidated_mcp_tools())}")
    print(f"   - Herramientas Core: {len(core_tools)}")
    print(f"   - Memoria persistente: Habilitada")
    print("✅ Servidor listo para recibir conexiones")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

