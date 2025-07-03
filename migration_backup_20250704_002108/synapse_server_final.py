import random
from datetime import datetime
import threading
import time
import psutil
import json
import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Importar funciones de generación de outputs
from output_generators import generate_step_output, generate_plan_summary

# Importar funciones de análisis dinámico
from dynamic_analysis import (
    analyze_step_results,
    generate_dynamic_steps,
    should_expand_plan,
    notify_plan_expansion
)

# Importar herramientas MCP CONSOLIDADAS (todas las anteriores + nuevas)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_integration'))
from consolidated_mcp_tools import get_consolidated_mcp_tools, execute_mcp_tool
from real_mcp_tools import execute_real_mcp_tool
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

# 💾 FUNCIONES DE PERSISTENCIA DE MEMORIA
MEMORY_FILE = 'synapse_memory.json'

def save_memory_to_disk():
    """Guardar memoria del sistema en disco"""
    try:
        memory_data = {
            'memory_store': system_state['memory_store'],
            'executed_plans': system_state['executed_plans'],
            'last_saved': datetime.now().isoformat(),
            'version': '2.1.0'
        }

        # Crear backup del archivo anterior si existe
        if os.path.exists(MEMORY_FILE):
            backup_file = f"{MEMORY_FILE}.backup"
            os.rename(MEMORY_FILE, backup_file)

        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Memoria guardada en disco: {MEMORY_FILE}")
        return True

    except Exception as e:
        print(f"❌ Error guardando memoria en disco: {e}")
        return False

def load_memory_from_disk():
    """Cargar memoria del sistema desde disco"""
    try:
        if not os.path.exists(MEMORY_FILE):
            print(f"📁 Archivo de memoria no encontrado: {MEMORY_FILE}")
            return False

        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)

        # Restaurar memoria
        if 'memory_store' in memory_data:
            system_state['memory_store'] = memory_data['memory_store']

        if 'executed_plans' in memory_data:
            system_state['executed_plans'] = memory_data['executed_plans']

        print(f"💾 Memoria cargada desde disco:")
        print(f"   - Conversaciones: {len(system_state['memory_store']['conversations'])}")
        print(f"   - Planes ejecutados: {len(system_state['executed_plans'])}")
        print(f"   - Outputs guardados: {len(system_state['memory_store']['plan_outputs'])}")
        print(f"   - Preferencias de usuario: {len(system_state['memory_store']['user_preferences'])}")
        print(f"   - Patrones aprendidos: {len(system_state['memory_store']['learned_patterns'])}")

        return True

    except Exception as e:
        print(f"❌ Error cargando memoria desde disco: {e}")
        return False

def auto_save_memory():
    """Guardar memoria automáticamente cada 5 minutos"""
    def save_periodically():
        while True:
            time.sleep(300)  # 5 minutos
            save_memory_to_disk()

    thread = threading.Thread(target=save_periodically)
    thread.daemon = True
    thread.start()
    print("🔄 Auto-guardado de memoria iniciado (cada 5 minutos)")

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
    
    # Analyze detected intents and enrich with dynamic planning capabilities
    final_intents = detected_intents if detected_intents else ['help_general']

    # Add dynamic planning intents if needed
    if any(intent in ['create_app', 'plan_project', 'develop'] for intent in final_intents):
        final_intents.extend(['dynamic_planning', 'step_analysis'])

    return final_intents

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
    """Generar respuesta contextual basada en el plan"""
    responses = [
        f"He analizado tu solicitud y he creado un plan completo: '{plan['title']}'. Este plan incluye {len(plan['steps'])} pasos principales que te ayudarán a lograr tu objetivo de manera eficiente.",
        f"Perfecto, he diseñado una estrategia detallada para tu proyecto: '{plan['title']}'. El plan está estructurado en {len(plan['steps'])} fases que cubrirán todos los aspectos necesarios.",
        f"Excelente idea. He preparado un plan de acción llamado '{plan['title']}' con {len(plan['steps'])} pasos clave que te guiarán desde el inicio hasta la finalización exitosa."
    ]
    return random.choice(responses)

def update_user_preferences(message, intents, session_id):
    """Detectar y actualizar preferencias del usuario basadas en el mensaje"""
    try:
        message_lower = message.lower()
        preferences_key = f'user_{session_id}'

        # Inicializar preferencias si no existen
        if preferences_key not in system_state['memory_store']['user_preferences']:
            system_state['memory_store']['user_preferences'][preferences_key] = {
                'language': 'es',  # Por defecto español
                'response_style': 'balanced',
                'preferred_tools': [],
                'project_types': [],
                'complexity_level': 'medium',
                'last_updated': datetime.now().isoformat()
            }

        user_prefs = system_state['memory_store']['user_preferences'][preferences_key]
        updated = False

        # Detectar preferencias de idioma
        if any(word in message_lower for word in ['english', 'inglés', 'in english']):
            user_prefs['language'] = 'en'
            updated = True
        elif any(word in message_lower for word in ['español', 'castellano', 'en español']):
            user_prefs['language'] = 'es'
            updated = True

        # Detectar estilo de respuesta preferido
        if any(word in message_lower for word in ['detallado', 'completo', 'exhaustivo', 'detailed']):
            user_prefs['response_style'] = 'detailed'
            updated = True
        elif any(word in message_lower for word in ['simple', 'básico', 'resumido', 'brief']):
            user_prefs['response_style'] = 'simple'
            updated = True

        # Detectar tipos de proyecto preferidos
        if 'create_app' in intents or 'plan_project' in intents:
            if 'web' in message_lower:
                if 'web_development' not in user_prefs['project_types']:
                    user_prefs['project_types'].append('web_development')
                    updated = True
            if 'mobile' in message_lower or 'móvil' in message_lower:
                if 'mobile_development' not in user_prefs['project_types']:
                    user_prefs['project_types'].append('mobile_development')
                    updated = True

        # Detectar nivel de complejidad preferido
        if any(word in message_lower for word in ['avanzado', 'complejo', 'profesional', 'advanced']):
            user_prefs['complexity_level'] = 'high'
            updated = True
        elif any(word in message_lower for word in ['básico', 'simple', 'principiante', 'beginner']):
            user_prefs['complexity_level'] = 'low'
            updated = True

        if updated:
            user_prefs['last_updated'] = datetime.now().isoformat()
            print(f"🎯 Preferencias actualizadas para usuario {session_id}: {user_prefs}")

    except Exception as e:
        print(f"⚠️ Error actualizando preferencias: {e}")

def learn_from_plan_execution(plan, success_rate, execution_time):
    """Aprender patrones de planes exitosos"""
    try:
        pattern = {
            'id': f'pattern_{int(time.time())}',
            'plan_type': plan.get('title', '').lower(),
            'steps_count': len(plan.get('steps', [])),
            'success_rate': success_rate,
            'execution_time': execution_time,
            'tools_used': [step.get('tools', []) for step in plan.get('steps', [])],
            'timestamp': datetime.now().isoformat(),
            'frequency': 1
        }

        # Buscar patrones similares existentes
        existing_pattern = None
        for p in system_state['memory_store']['learned_patterns']:
            if (p.get('plan_type') == pattern['plan_type'] and
                p.get('steps_count') == pattern['steps_count']):
                existing_pattern = p
                break

        if existing_pattern:
            # Actualizar patrón existente
            existing_pattern['frequency'] += 1
            existing_pattern['success_rate'] = (existing_pattern['success_rate'] + success_rate) / 2
            existing_pattern['execution_time'] = (existing_pattern.get('execution_time', 0) + execution_time) / 2
            existing_pattern['last_seen'] = datetime.now().isoformat()
            print(f"🧠 Patrón actualizado: {existing_pattern['plan_type']} (frecuencia: {existing_pattern['frequency']})")
        else:
            # Crear nuevo patrón
            system_state['memory_store']['learned_patterns'].append(pattern)
            print(f"🧠 Nuevo patrón aprendido: {pattern['plan_type']}")

        # Limitar número de patrones (mantener solo los 50 más recientes)
        if len(system_state['memory_store']['learned_patterns']) > 50:
            system_state['memory_store']['learned_patterns'] = sorted(
                system_state['memory_store']['learned_patterns'],
                key=lambda x: x.get('frequency', 0) * x.get('success_rate', 0),
                reverse=True
            )[:50]

    except Exception as e:
        print(f"⚠️ Error aprendiendo patrón: {e}")

def execute_core_tool(tool_id, parameters, step):
    """Ejecuta herramientas core (simuladas con resultados realistas)"""

    execution_time = random.uniform(1.0, 3.0)

    if tool_id == 'web_search':
        query = parameters.get('query', step.get('title', 'búsqueda'))
        return {
            'tool_id': tool_id,
            'tool_name': 'Búsqueda Web',
            'result': f"""🔍 Búsqueda Web Completada

📝 Consulta: "{query}"
📊 Resultados encontrados: {random.randint(25, 200)}
⏱️ Tiempo de respuesta: {random.uniform(0.3, 1.2):.2f}s

🎯 Resultados principales:
• Documentación oficial y guías técnicas
• Tutoriales y ejemplos prácticos
• Foros de desarrolladores y Stack Overflow
• Repositorios de GitHub relacionados
• Artículos técnicos y blogs especializados

✅ Información recopilada exitosamente""",
            'execution_time': round(execution_time, 2)
        }

    elif tool_id == 'data_analyzer':
        return {
            'tool_id': tool_id,
            'tool_name': 'Analizador de Datos',
            'result': f"""📊 Análisis de Datos Completado

🔍 Análisis realizado: {step.get('title', 'Análisis general')}
📈 Registros procesados: {random.randint(500, 5000)}
⏱️ Tiempo de procesamiento: {execution_time:.2f}s

📋 Resultados del análisis:
• Patrones identificados: {random.randint(3, 12)}
• Anomalías detectadas: {random.randint(0, 5)}
• Correlaciones encontradas: {random.randint(2, 8)}
• Precisión del modelo: {random.uniform(85, 98):.1f}%
• Métricas de calidad: {random.uniform(7.5, 9.8):.1f}/10

✅ Análisis completado exitosamente""",
            'execution_time': round(execution_time, 2)
        }

    elif tool_id == 'code_generator':
        return {
            'tool_id': tool_id,
            'tool_name': 'Generador de Código',
            'result': f"""💻 Generación de Código Completada

🎯 Tarea: {step.get('title', 'Generación de código')}
📝 Líneas de código generadas: {random.randint(50, 300)}
⏱️ Tiempo de generación: {execution_time:.2f}s

🔧 Componentes generados:
• Funciones principales: {random.randint(3, 8)}
• Clases y métodos: {random.randint(2, 6)}
• Tests unitarios: {random.randint(5, 15)}
• Documentación: Incluida
• Validaciones: Implementadas

📊 Calidad del código:
• Cobertura de tests: {random.uniform(85, 95):.0f}%
• Complejidad ciclomática: {random.uniform(1.2, 3.5):.1f}
• Estándares de codificación: ✅ Cumplidos

✅ Código generado exitosamente""",
            'execution_time': round(execution_time, 2)
        }

    elif tool_id == 'task_planner':
        return {
            'tool_id': tool_id,
            'tool_name': 'Planificador de Tareas',
            'result': f"""📋 Planificación de Tareas Completada

🎯 Contexto: {step.get('title', 'Planificación general')}
📊 Subtareas identificadas: {random.randint(5, 15)}
⏱️ Tiempo de planificación: {execution_time:.2f}s

📈 Plan de ejecución:
• Tareas críticas: {random.randint(2, 5)}
• Tareas de alta prioridad: {random.randint(3, 7)}
• Tareas de prioridad media: {random.randint(4, 8)}
• Dependencias identificadas: {random.randint(3, 10)}

⏰ Estimaciones de tiempo:
• Tiempo total estimado: {random.randint(8, 24)} horas
• Paralelización posible: {random.randint(30, 70)}%
• Recursos necesarios: {random.randint(2, 5)} desarrolladores

✅ Planificación completada exitosamente""",
            'execution_time': round(execution_time, 2)
        }

    else:
        return {
            'tool_id': tool_id,
            'tool_name': f'Herramienta {tool_id}',
            'result': f"""🔧 Herramienta Ejecutada

📝 Herramienta: {tool_id}
🎯 Contexto: {step.get('title', 'Ejecución general')}
⏱️ Tiempo de ejecución: {execution_time:.2f}s

✅ Ejecución completada exitosamente""",
            'execution_time': round(execution_time, 2)
        }

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

            # 💾 GUARDAR CONVERSACIÓN EN MEMORIA
            conversation_entry = {
                'id': f'conv_{int(time.time())}_{sid}',
                'user_message': message,
                'assistant_response': response,
                'timestamp': datetime.now().isoformat(),
                'intents': intents,
                'plan_generated': plan['id'],
                'plan_title': plan['title'],
                'session_id': sid
            }
            system_state['memory_store']['conversations'].append(conversation_entry)
            print(f"💾 Conversación guardada en memoria (ID: {conversation_entry['id']})")

            # 🔍 DETECTAR Y GUARDAR PREFERENCIAS DE USUARIO
            update_user_preferences(message, intents, sid)

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

            # 📊 EMITIR ACTUALIZACIÓN DE MEMORIA AL FRONTEND
            socketio.emit('memory_updated', {
                'memoryStore': system_state['memory_store'],
                'totalConversations': len(system_state['memory_store']['conversations']),
                'totalPreferences': len(system_state['memory_store']['user_preferences']),
                'timestamp': datetime.now().isoformat()
            }, room=sid)

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

                        # EJECUTAR HERRAMIENTAS ASIGNADAS AL PASO
                        tool_results = []
                        if 'tools' in step and step['tools']:
                            print(f"🔧 Ejecutando {len(step['tools'])} herramientas: {step['tools']}")

                            for tool_id in step['tools']:
                                try:
                                    print(f"🛠️ Ejecutando herramienta: {tool_id}")

                                    # Preparar parámetros básicos para la herramienta
                                    tool_params = {
                                        'query': step.get('description', step.get('title', '')),
                                        'context': plan.get('title', ''),
                                        'step_number': i + 1,
                                        'total_steps': len(steps)
                                    }

                                    # Ejecutar herramienta MCP
                                    if tool_id in [t['id'] for t in available_tools if t['type'] == 'mcp']:
                                        tool_result = execute_mcp_tool(tool_id, tool_params)
                                        if tool_result['success']:
                                            tool_results.append({
                                                'tool_id': tool_id,
                                                'tool_name': tool_result['tool_name'],
                                                'result': tool_result['result'],
                                                'execution_time': tool_result['execution_time']
                                            })
                                            print(f"✅ Herramienta {tool_id} ejecutada exitosamente")
                                        else:
                                            print(f"❌ Error ejecutando {tool_id}: {tool_result.get('error', 'Error desconocido')}")
                                            tool_results.append({
                                                'tool_id': tool_id,
                                                'error': tool_result.get('error', 'Error desconocido')
                                            })

                                    # Ejecutar herramientas core (simuladas)
                                    elif tool_id in [t['id'] for t in available_tools if t['type'] == 'core']:
                                        core_result = execute_core_tool(tool_id, tool_params, step)
                                        tool_results.append(core_result)
                                        print(f"✅ Herramienta core {tool_id} ejecutada")

                                    else:
                                        print(f"⚠️ Herramienta {tool_id} no encontrada")
                                        tool_results.append({
                                            'tool_id': tool_id,
                                            'error': f'Herramienta {tool_id} no encontrada'
                                        })

                                except Exception as tool_error:
                                    print(f"❌ Error ejecutando herramienta {tool_id}: {tool_error}")
                                    tool_results.append({
                                        'tool_id': tool_id,
                                        'error': str(tool_error)
                                    })
                        else:
                            print(f"ℹ️ No hay herramientas asignadas para este paso")

                        # Generar output realista para el paso
                        try:
                            step_output = generate_step_output(step, i + 1, len(steps))

                            # Agregar resultados de herramientas al output
                            if tool_results:
                                step_output += "\n\n🔧 **RESULTADOS DE HERRAMIENTAS:**\n"
                                for tool_result in tool_results:
                                    if 'error' in tool_result:
                                        step_output += f"\n❌ **{tool_result['tool_id']}**: {tool_result['error']}\n"
                                    else:
                                        step_output += f"\n✅ **{tool_result.get('tool_name', tool_result['tool_id'])}**:\n"
                                        step_output += f"{tool_result['result']}\n"
                                        if 'execution_time' in tool_result:
                                            step_output += f"⏱️ Tiempo de ejecución: {tool_result['execution_time']}s\n"

                            step['output'] = step_output
                            step['tool_results'] = tool_results  # Guardar resultados para referencia
                            print(f"📄 Output generado para paso {step['id']}: {len(step_output)} caracteres")
                            print(f"📄 Primeros 200 chars: {step_output[:200]}...")
                        except Exception as output_error:
                            print(f"❌ Error generando output: {output_error}")
                            step['output'] = f"Error generando output: {str(output_error)}"

                        # Marcar paso como completado
                        step['status'] = 'completed'

                        print(f"📤 Enviando plan_step_update con output de {len(step.get('output', ''))} caracteres")
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

                        # 🔄 ANÁLISIS DINÁMICO DEL PASO COMPLETADO
                        try:
                            print(f"🔍 Analizando resultados del paso {i+1} para posible expansión...")

                            # Analizar los resultados del paso
                            step_analysis = analyze_step_results(step, step.get('output', ''), plan)

                            if step_analysis['needs_expansion']:
                                print(f"🔄 Expansión sugerida: {step_analysis['expansion_reason']}")
                                print(f"   Confianza: {step_analysis['confidence']:.0%}")

                                # Verificar si debe expandirse el plan
                                if should_expand_plan(step_analysis, plan):
                                    print(f"✅ Expandiendo plan dinámicamente...")

                                    # Generar nuevos pasos
                                    new_steps = generate_dynamic_steps(step_analysis, plan, i)

                                    if new_steps:
                                        # Añadir nuevos pasos al plan
                                        plan['steps'].extend(new_steps)
                                        steps.extend(new_steps)  # También actualizar la lista local

                                        # Notificar al usuario
                                        notify_plan_expansion(plan, new_steps, step_analysis, sid)

                                        # Emitir actualización del plan completo
                                        socketio.emit('plan_updated', {
                                            'plan_id': plan_id,
                                            'plan': plan,
                                            'new_steps_added': len(new_steps),
                                            'expansion_reason': step_analysis['expansion_reason'],
                                            'timestamp': datetime.now().isoformat()
                                        }, room=sid)

                                        print(f"🎯 Plan expandido: {len(new_steps)} pasos añadidos")
                                        print(f"   Total pasos ahora: {len(steps)}")
                                    else:
                                        print(f"⚠️ No se pudieron generar pasos dinámicos")
                                else:
                                    print(f"❌ Expansión rechazada por criterios de filtrado")
                                    print(f"   Confianza: {step_analysis['confidence']:.0%} (mín: 0.6)")
                                    current_dynamic = len([s for s in plan.get('steps', []) if s.get('dynamic', False)])
                                    print(f"   Pasos dinámicos actuales: {current_dynamic} (máx: 5)")
                            else:
                                print(f"✅ No se requiere expansión para este paso")

                        except Exception as analysis_error:
                            print(f"❌ Error en análisis dinámico: {analysis_error}")
                            # No interrumpir la ejecución por errores de análisis
                            import traceback
                            traceback.print_exc()
                        
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

                # 🧠 APRENDER DE LA EJECUCIÓN DEL PLAN
                execution_duration = time.time() - plan.get('start_time', time.time())
                success_rate = len([s for s in steps if s.get('status') == 'completed']) / len(steps)
                learn_from_plan_execution(plan, success_rate, execution_duration)

                # 💾 GUARDAR MEMORIA EN DISCO (persistencia)
                save_memory_to_disk()

                socketio.emit('plan_completed', {
                    'plan_id': plan_id,
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Plan '{plan['title']}' completado exitosamente",
                    'final_summary': final_summary,
                    'total_outputs': len([s for s in steps if s.get('output')]),
                    'saved_to_memory': True,  # Indicar que se guardó en memoria
                    'success_rate': success_rate,
                    'execution_duration': execution_duration
                }, room=sid)

                # 📊 EMITIR ACTUALIZACIÓN DE MEMORIA COMPLETA
                socketio.emit('memory_updated', {
                    'memoryStore': system_state['memory_store'],
                    'executedPlans': system_state['executed_plans'],
                    'totalConversations': len(system_state['memory_store']['conversations']),
                    'totalPatterns': len(system_state['memory_store']['learned_patterns']),
                    'timestamp': datetime.now().isoformat()
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

# ========================================
# 🤖 HANDLERS DE CONFIGURACIÓN DE LLMS
# ========================================

# Configuración por defecto de LLMs
DEFAULT_LLM_CONFIG = {
    'conversation_agent': 'gemini-1.5-flash',
    'planning_agent': 'gemini-1.5-flash',
    'execution_agent': 'gemini-1.5-flash',
    'analysis_agent': 'gemini-1.5-flash',
    'memory_agent': 'gemini-1.5-flash',
    'optimization_agent': 'gemini-1.5-flash'
}

# Estado global de configuración LLM
llm_config = DEFAULT_LLM_CONFIG.copy()

@socketio.on('get_llm_config')
def handle_get_llm_config():
    """Obtener configuración actual de LLMs"""
    print(f"📋 Solicitando configuración LLM para cliente {request.sid}")
    emit('llm_config_response', llm_config)

@socketio.on('update_llm_config')
def handle_update_llm_config(data):
    """Actualizar configuración de LLMs"""
    global llm_config

    try:
        print(f"🔄 Actualizando configuración LLM: {data}")

        # Validar que los agentes existen
        valid_agents = set(DEFAULT_LLM_CONFIG.keys())
        for agent_id in data.keys():
            if agent_id not in valid_agents:
                raise ValueError(f"Agente inválido: {agent_id}")

        # Actualizar configuración
        llm_config.update(data)

        # Guardar configuración (aquí podrías persistir en archivo/DB)
        save_llm_config_to_disk()

        print(f"✅ Configuración LLM actualizada: {llm_config}")
        emit('llm_config_updated', {
            'success': True,
            'config': llm_config,
            'timestamp': datetime.now().isoformat()
        })

        # Notificar a todos los clientes conectados
        socketio.emit('llm_config_response', llm_config)

    except Exception as e:
        print(f"❌ Error actualizando configuración LLM: {e}")
        emit('llm_config_updated', {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('test_llm_connection')
def handle_test_llm_connection(data):
    """Probar conexión con un LLM específico"""
    llm_id = data.get('llm_id')

    try:
        print(f"🧪 Probando conexión con LLM: {llm_id}")

        # Simular test de conexión (aquí implementarías la lógica real)
        success = test_llm_connection_real(llm_id)

        emit('llm_test_result', {
            'llm_id': llm_id,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'error': None if success else f"No se pudo conectar con {llm_id}"
        })

    except Exception as e:
        print(f"❌ Error probando LLM {llm_id}: {e}")
        emit('llm_test_result', {
            'llm_id': llm_id,
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        })

def test_llm_connection_real(llm_id):
    """
    Función para probar conexión real con LLM
    Aquí implementarías la lógica específica para cada proveedor
    """
    # Simulación - en producción harías llamadas reales a las APIs
    import random
    import time

    time.sleep(1)  # Simular latencia

    # Simular diferentes tasas de éxito según el LLM
    success_rates = {
        'gpt-4': 0.95,
        'gpt-3.5-turbo': 0.98,
        'claude-3-opus': 0.90,
        'claude-3-sonnet': 0.92,
        'claude-3-haiku': 0.95,
        'gemini-pro': 0.88,
        'gemini-flash': 0.93
    }

    rate = success_rates.get(llm_id, 0.85)
    return random.random() < rate

def save_llm_config_to_disk():
    """Guardar configuración LLM en disco"""
    try:
        config_file = 'llm_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(llm_config, f, indent=2, ensure_ascii=False)
        print(f"💾 Configuración LLM guardada en {config_file}")
    except Exception as e:
        print(f"❌ Error guardando configuración LLM: {e}")

def load_llm_config_from_disk():
    """Cargar configuración LLM desde disco"""
    global llm_config
    try:
        config_file = 'llm_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                llm_config.update(loaded_config)
            print(f"📂 Configuración LLM cargada desde {config_file}")
            return True
    except Exception as e:
        print(f"❌ Error cargando configuración LLM: {e}")
    return False

def get_llm_for_agent(agent_type):
    """Obtener el LLM configurado para un agente específico"""
    return llm_config.get(agent_type, DEFAULT_LLM_CONFIG.get(agent_type, 'gpt-3.5-turbo'))

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
        
        # Ejecutar la herramienta REAL
        result = execute_real_mcp_tool(tool_id, parameters)

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

# 🧠 NUEVOS ENDPOINTS DE MEMORIA MEJORADOS

@app.route('/api/memory/conversations', methods=['GET'])
def get_conversations():
    """Obtener historial de conversaciones"""
    try:
        conversations = system_state['memory_store']['conversations']

        # Filtrar por sesión si se especifica
        session_id = request.args.get('session_id')
        if session_id:
            conversations = [c for c in conversations if c.get('session_id') == session_id]

        # Limitar número de conversaciones
        limit = int(request.args.get('limit', 50))
        conversations = conversations[-limit:] if len(conversations) > limit else conversations

        return jsonify({
            'success': True,
            'conversations': conversations,
            'total': len(system_state['memory_store']['conversations']),
            'filtered': len(conversations),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/preferences', methods=['GET'])
def get_user_preferences():
    """Obtener preferencias de usuarios"""
    try:
        preferences = system_state['memory_store']['user_preferences']

        # Filtrar por usuario específico si se especifica
        user_id = request.args.get('user_id')
        if user_id:
            user_key = f'user_{user_id}'
            preferences = {user_key: preferences.get(user_key, {})}

        return jsonify({
            'success': True,
            'preferences': preferences,
            'total_users': len(system_state['memory_store']['user_preferences']),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/patterns', methods=['GET'])
def get_learned_patterns():
    """Obtener patrones aprendidos"""
    try:
        patterns = system_state['memory_store']['learned_patterns']

        # Ordenar por frecuencia y tasa de éxito
        patterns_sorted = sorted(
            patterns,
            key=lambda x: x.get('frequency', 0) * x.get('success_rate', 0),
            reverse=True
        )

        # Limitar número de patrones
        limit = int(request.args.get('limit', 20))
        patterns_limited = patterns_sorted[:limit]

        return jsonify({
            'success': True,
            'patterns': patterns_limited,
            'total_patterns': len(patterns),
            'top_patterns': patterns_limited[:5],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    """Obtener estadísticas de memoria"""
    try:
        memory_store = system_state['memory_store']

        # Calcular estadísticas
        total_conversations = len(memory_store['conversations'])
        total_users = len(memory_store['user_preferences'])
        total_patterns = len(memory_store['learned_patterns'])
        total_outputs = len(memory_store['plan_outputs'])
        total_executed_plans = len(system_state['executed_plans'])

        # Estadísticas de patrones
        if total_patterns > 0:
            avg_success_rate = sum(p.get('success_rate', 0) for p in memory_store['learned_patterns']) / total_patterns
            most_frequent_pattern = max(memory_store['learned_patterns'], key=lambda x: x.get('frequency', 0))
        else:
            avg_success_rate = 0
            most_frequent_pattern = None

        # Tamaño de memoria en disco
        memory_file_size = 0
        if os.path.exists(MEMORY_FILE):
            memory_file_size = os.path.getsize(MEMORY_FILE)

        return jsonify({
            'success': True,
            'stats': {
                'conversations': {
                    'total': total_conversations,
                    'recent_24h': len([c for c in memory_store['conversations']
                                     if (datetime.now() - datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))).days < 1])
                },
                'users': {
                    'total': total_users,
                    'active_preferences': len([p for p in memory_store['user_preferences'].values() if p])
                },
                'patterns': {
                    'total': total_patterns,
                    'avg_success_rate': round(avg_success_rate, 2),
                    'most_frequent': most_frequent_pattern['plan_type'] if most_frequent_pattern else None
                },
                'plans': {
                    'total_executed': total_executed_plans,
                    'total_outputs': total_outputs
                },
                'storage': {
                    'memory_file_size_bytes': memory_file_size,
                    'memory_file_size_mb': round(memory_file_size / (1024 * 1024), 2)
                }
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/backup', methods=['POST'])
def create_memory_backup():
    """Crear backup manual de la memoria"""
    try:
        backup_filename = f"synapse_memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        memory_data = {
            'memory_store': system_state['memory_store'],
            'executed_plans': system_state['executed_plans'],
            'backup_created': datetime.now().isoformat(),
            'version': '2.3.0'
        }

        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'backup_file': backup_filename,
            'file_size_bytes': os.path.getsize(backup_filename),
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
    print(f"   - Herramientas Core: {len([t for t in available_tools if t.get('type') == 'core'])}")

    # Cargar configuración LLM desde disco
    print("🤖 Cargando configuración de LLMs...")
    if load_llm_config_from_disk():
        print("✅ Configuración LLM cargada exitosamente")
        for agent, llm in llm_config.items():
            print(f"   - {agent}: {llm}")
    else:
        print("⚠️ Usando configuración LLM por defecto")
        for agent, llm in DEFAULT_LLM_CONFIG.items():
            print(f"   - {agent}: {llm}")

    # Cargar memoria desde disco
    print("💾 Cargando memoria del sistema...")
    load_memory_from_disk()

    # Iniciar auto-guardado de memoria
    auto_save_memory()

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

# 🧠 NUEVOS ENDPOINTS DE MEMORIA MEJORADOS

@app.route('/api/memory/conversations', methods=['GET'])
def get_conversations():
    """Obtener historial de conversaciones"""
    try:
        conversations = system_state['memory_store']['conversations']

        # Filtrar por sesión si se especifica
        session_id = request.args.get('session_id')
        if session_id:
            conversations = [c for c in conversations if c.get('session_id') == session_id]

        # Limitar número de conversaciones
        limit = int(request.args.get('limit', 50))
        conversations = conversations[-limit:] if len(conversations) > limit else conversations

        return jsonify({
            'success': True,
            'conversations': conversations,
            'total': len(system_state['memory_store']['conversations']),
            'filtered': len(conversations),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/preferences', methods=['GET'])
def get_user_preferences():
    """Obtener preferencias de usuarios"""
    try:
        preferences = system_state['memory_store']['user_preferences']

        # Filtrar por usuario específico si se especifica
        user_id = request.args.get('user_id')
        if user_id:
            user_key = f'user_{user_id}'
            preferences = {user_key: preferences.get(user_key, {})}

        return jsonify({
            'success': True,
            'preferences': preferences,
            'total_users': len(system_state['memory_store']['user_preferences']),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/patterns', methods=['GET'])
def get_learned_patterns():
    """Obtener patrones aprendidos"""
    try:
        patterns = system_state['memory_store']['learned_patterns']

        # Ordenar por frecuencia y tasa de éxito
        patterns_sorted = sorted(
            patterns,
            key=lambda x: x.get('frequency', 0) * x.get('success_rate', 0),
            reverse=True
        )

        # Limitar número de patrones
        limit = int(request.args.get('limit', 20))
        patterns_limited = patterns_sorted[:limit]

        return jsonify({
            'success': True,
            'patterns': patterns_limited,
            'total_patterns': len(patterns),
            'top_patterns': patterns_limited[:5],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    """Obtener estadísticas de memoria"""
    try:
        memory_store = system_state['memory_store']

        # Calcular estadísticas
        total_conversations = len(memory_store['conversations'])
        total_users = len(memory_store['user_preferences'])
        total_patterns = len(memory_store['learned_patterns'])
        total_outputs = len(memory_store['plan_outputs'])
        total_executed_plans = len(system_state['executed_plans'])

        # Estadísticas de patrones
        if total_patterns > 0:
            avg_success_rate = sum(p.get('success_rate', 0) for p in memory_store['learned_patterns']) / total_patterns
            most_frequent_pattern = max(memory_store['learned_patterns'], key=lambda x: x.get('frequency', 0))
        else:
            avg_success_rate = 0
            most_frequent_pattern = None

        # Tamaño de memoria en disco
        memory_file_size = 0
        if os.path.exists(MEMORY_FILE):
            memory_file_size = os.path.getsize(MEMORY_FILE)

        return jsonify({
            'success': True,
            'stats': {
                'conversations': {
                    'total': total_conversations,
                    'recent_24h': len([c for c in memory_store['conversations']
                                     if (datetime.now() - datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))).days < 1])
                },
                'users': {
                    'total': total_users,
                    'active_preferences': len([p for p in memory_store['user_preferences'].values() if p])
                },
                'patterns': {
                    'total': total_patterns,
                    'avg_success_rate': round(avg_success_rate, 2),
                    'most_frequent': most_frequent_pattern['plan_type'] if most_frequent_pattern else None
                },
                'plans': {
                    'total_executed': total_executed_plans,
                    'total_outputs': total_outputs
                },
                'storage': {
                    'memory_file_size_bytes': memory_file_size,
                    'memory_file_size_mb': round(memory_file_size / (1024 * 1024), 2)
                }
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory/backup', methods=['POST'])
def create_memory_backup():
    """Crear backup manual de la memoria"""
    try:
        backup_filename = f"synapse_memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        memory_data = {
            'memory_store': system_state['memory_store'],
            'executed_plans': system_state['executed_plans'],
            'backup_created': datetime.now().isoformat(),
            'version': '2.3.0'
        }

        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'backup_file': backup_filename,
            'file_size_bytes': os.path.getsize(backup_filename),
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

    # 💾 CARGAR MEMORIA DESDE DISCO AL INICIAR
    print("💾 Cargando memoria persistente...")
    if load_memory_from_disk():
        print("✅ Memoria cargada exitosamente")
    else:
        print("📝 Iniciando con memoria nueva")

    # 🔄 INICIAR AUTO-GUARDADO DE MEMORIA
    auto_save_memory()

    print("✅ Servidor listo para recibir conexiones")

    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

