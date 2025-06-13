"""
Módulo de análisis dinámico para expansión de planes
Funciones independientes para análisis y generación de pasos dinámicos
"""

import re
import random
from datetime import datetime

def analyze_step_results(step, output, plan):
    """
    Analizar los resultados de un paso para determinar si necesita expansión dinámica
    
    Args:
        step: Diccionario con información del paso
        output: String con el output generado del paso
        plan: Diccionario con información del plan completo
    
    Returns:
        dict: Análisis con needs_expansion, confidence, expansion_reason, etc.
    """
    analysis = {
        'needs_expansion': False,
        'confidence': 0.0,
        'expansion_reason': '',
        'suggested_steps': [],
        'priority': 'low',
        'step_id': step.get('id', 'unknown'),
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Patrones que indican necesidad de expansión
    expansion_patterns = {
        'high_priority': [
            r'❌.*ERROR.*ENCONTRADO',
            r'⚠️.*PROBLEMAS DETECTADOS',
            r'❌.*FALLÓ',
            r'ERROR.*CRÍTICO',
            r'FALLO.*SISTEMA'
        ],
        'medium_priority': [
            r'⚠️.*CONFIGURACIÓN ADICIONAL REQUERIDA',
            r'🔍.*ANÁLISIS INCOMPLETO',
            r'⚠️.*COBERTURA INSUFICIENTE',
            r'🔧.*OPTIMIZACIÓN REQUERIDA',
            r'🔍.*TESTING ADICIONAL REQUERIDO'
        ],
        'low_priority': [
            r'💡.*MEJORAS SUGERIDAS',
            r'💡.*RECOMENDACIONES',
            r'🔍.*MONITOREO RECOMENDADO',
            r'💡.*PRÓXIMOS PASOS',
            r'💡.*CONSIDERAR IMPLEMENTAR'
        ]
    }
    
    # Analizar el output en busca de patrones
    for priority, patterns in expansion_patterns.items():
        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
                analysis['needs_expansion'] = True
                analysis['priority'] = priority
                
                # Asignar confianza basada en prioridad
                if priority == 'high_priority':
                    analysis['confidence'] = random.uniform(0.85, 0.95)
                    analysis['expansion_reason'] = 'Errores críticos detectados que requieren corrección inmediata'
                elif priority == 'medium_priority':
                    analysis['confidence'] = random.uniform(0.70, 0.85)
                    analysis['expansion_reason'] = 'Configuración adicional o optimizaciones necesarias'
                else:  # low_priority
                    analysis['confidence'] = random.uniform(0.60, 0.75)
                    analysis['expansion_reason'] = 'Mejoras opcionales identificadas'
                
                break
        
        if analysis['needs_expansion']:
            break
    
    # Análisis adicional basado en el contenido específico
    if analysis['needs_expansion']:
        # Extraer detalles específicos del output
        if 'API externa' in output:
            analysis['suggested_steps'].append('Configurar integración con API externa')
        if 'rendimiento' in output.lower():
            analysis['suggested_steps'].append('Optimizar rendimiento del sistema')
        if 'base de datos' in output.lower():
            analysis['suggested_steps'].append('Optimizar consultas de base de datos')
        if 'testing' in output.lower() or 'test' in output.lower():
            analysis['suggested_steps'].append('Implementar tests adicionales')
        if 'seguridad' in output.lower():
            analysis['suggested_steps'].append('Reforzar medidas de seguridad')
        if 'monitoreo' in output.lower() or 'logs' in output.lower():
            analysis['suggested_steps'].append('Configurar sistema de monitoreo')
        if 'backup' in output.lower():
            analysis['suggested_steps'].append('Implementar sistema de backup')
        if 'SSL' in output or 'certificado' in output.lower():
            analysis['suggested_steps'].append('Configurar certificados SSL')
    
    return analysis

def generate_dynamic_steps(analysis, plan, current_step_index):
    """
    Generar nuevos pasos basados en el análisis dinámico
    
    Args:
        analysis: Resultado del análisis de analyze_step_results
        plan: Plan actual
        current_step_index: Índice del paso actual
    
    Returns:
        list: Lista de nuevos pasos a añadir al plan
    """
    if not analysis.get('needs_expansion', False):
        return []
    
    new_steps = []
    base_id = f"dynamic_{current_step_index}_{random.randint(1000, 9999)}"
    
    # Generar pasos basados en las sugerencias del análisis
    suggested_steps = analysis.get('suggested_steps', [])
    
    if not suggested_steps:
        # Generar pasos genéricos basados en la razón de expansión
        if 'error' in analysis['expansion_reason'].lower():
            suggested_steps = ['Corregir errores identificados', 'Validar correcciones']
        elif 'configuración' in analysis['expansion_reason'].lower():
            suggested_steps = ['Completar configuración adicional', 'Verificar configuración']
        elif 'optimización' in analysis['expansion_reason'].lower():
            suggested_steps = ['Implementar optimizaciones', 'Medir mejoras de rendimiento']
        else:
            suggested_steps = ['Implementar mejoras sugeridas']
    
    # Crear pasos dinámicos
    for i, step_title in enumerate(suggested_steps[:3]):  # Máximo 3 pasos por expansión
        step_id = f"{base_id}_{i+1}"
        
        new_step = {
            'id': step_id,
            'title': step_title,
            'description': f'Paso generado dinámicamente: {step_title}',
            'status': 'pending',
            'dynamic': True,  # Marcar como paso dinámico
            'parent_step': analysis['step_id'],
            'priority': analysis['priority'],
            'generated_at': datetime.now().isoformat(),
            'expansion_reason': analysis['expansion_reason']
        }
        
        new_steps.append(new_step)
    
    return new_steps

def should_expand_plan(analysis, plan):
    """
    Determinar si el plan debe expandirse basado en criterios específicos
    
    Args:
        analysis: Resultado del análisis
        plan: Plan actual
    
    Returns:
        bool: True si debe expandirse, False en caso contrario
    """
    if not analysis.get('needs_expansion', False):
        return False
    
    # Criterios de filtrado
    
    # 1. Confianza mínima
    min_confidence = 0.6
    if analysis.get('confidence', 0) < min_confidence:
        return False
    
    # 2. Límite de pasos dinámicos por plan
    max_dynamic_steps = 5
    current_dynamic_steps = len([s for s in plan.get('steps', []) if s.get('dynamic', False)])
    if current_dynamic_steps >= max_dynamic_steps:
        return False
    
    # 3. Prioridad alta siempre se expande
    if analysis.get('priority') == 'high_priority':
        return True
    
    # 4. Para prioridades menores, aplicar probabilidad
    if analysis.get('priority') == 'medium_priority':
        return random.random() < 0.7  # 70% de probabilidad
    else:  # low_priority
        return random.random() < 0.4  # 40% de probabilidad

def notify_plan_expansion(plan, new_steps, analysis, sid=None):
    """
    Notificar sobre la expansión del plan (función placeholder)
    
    Args:
        plan: Plan expandido
        new_steps: Nuevos pasos añadidos
        analysis: Análisis que motivó la expansión
        sid: Session ID para WebSocket (opcional)
    """
    print(f"🔄 PLAN EXPANDIDO:")
    print(f"   Plan ID: {plan.get('id', 'unknown')}")
    print(f"   Nuevos pasos: {len(new_steps)}")
    print(f"   Razón: {analysis['expansion_reason']}")
    print(f"   Confianza: {analysis['confidence']:.0%}")
    
    for i, step in enumerate(new_steps, 1):
        print(f"   {i}. {step['title']}")

# Función de utilidad para testing
def test_dynamic_analysis():
    """Función de prueba para el análisis dinámico"""
    
    # Caso de prueba 1: Output con problemas
    test_step = {
        'id': 'step_1',
        'title': 'Crear sistema de autenticación',
        'description': 'Implementar login y registro de usuarios',
        'status': 'completed'
    }
    
    problem_output = """🛠️ CREACIÓN COMPLETADA - Paso 1/5

⚠️ PROBLEMAS DETECTADOS:
• Error en la integración con API externa
• Problema de rendimiento en consultas complejas

✅ Estado: Artefacto listo para uso"""
    
    test_plan = {
        'id': 'plan_123',
        'title': 'Desarrollo de aplicación web',
        'steps': [test_step]
    }
    
    # Ejecutar análisis
    analysis = analyze_step_results(test_step, problem_output, test_plan)
    print("📊 Análisis de paso con problemas:")
    print(f"   Necesita expansión: {analysis['needs_expansion']}")
    print(f"   Confianza: {analysis['confidence']:.0%}")
    print(f"   Razón: {analysis['expansion_reason']}")
    print(f"   Pasos sugeridos: {analysis['suggested_steps']}")
    
    # Generar pasos dinámicos
    if analysis['needs_expansion']:
        new_steps = generate_dynamic_steps(analysis, test_plan, 0)
        print(f"\n🔄 Pasos dinámicos generados: {len(new_steps)}")
        for step in new_steps:
            print(f"   - {step['title']}")
    
    return analysis

if __name__ == "__main__":
    test_dynamic_analysis()