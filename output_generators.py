import random
from datetime import datetime

def generate_step_output(step, step_number, total_steps):
    """Generar output realista para un paso del plan con posibilidad de activar análisis dinámico"""
    step_title = step.get('title', 'Paso sin título')
    step_description = step.get('description', 'Sin descripción')

    # Probabilidad de generar outputs que activen análisis dinámico
    trigger_dynamic_analysis = random.random() < 0.3  # 30% de probabilidad

    # Tipos de outputs basados en el contenido del paso
    if 'análisis' in step_title.lower() or 'investigar' in step_title.lower():
        base_output = f"""📊 ANÁLISIS COMPLETADO - Paso {step_number}/{total_steps}

🔍 Investigación realizada: {step_title}
📋 Descripción: {step_description}

📈 Resultados del análisis:
• Se identificaron 3 componentes principales
• Evaluación de viabilidad: 85% positiva
• Recursos necesarios: Estimados y documentados
• Riesgos identificados: 2 menores, 0 críticos

📄 Documentación generada:
- Reporte de análisis (2.3 KB)
- Matriz de evaluación
- Recomendaciones de implementación"""

        # Posibles triggers para análisis dinámico
        if trigger_dynamic_analysis:
            dynamic_triggers = [
                "\n\n⚠️ HALLAZGOS ADICIONALES:\n• Se identificaron tecnologías adicionales que podrían mejorar el proyecto\n• Dependencias no contempladas inicialmente requieren evaluación",
                "\n\n🔍 ANÁLISIS INCOMPLETO:\n• Necesita más información sobre requisitos específicos del cliente\n• Faltan especificaciones técnicas detalladas",
                "\n\n💡 RECOMENDACIONES:\n• Considerar implementar sistema de monitoreo avanzado\n• Próximos pasos: Evaluación de arquitectura escalable"
            ]
            base_output += random.choice(dynamic_triggers)

        base_output += f"""

✅ Estado: Completado exitosamente
⏱️ Tiempo de ejecución: {random.uniform(2.1, 4.8):.1f} segundos
🔗 Siguiente paso: Preparado para continuar"""

        return base_output

    elif 'crear' in step_title.lower() or 'generar' in step_title.lower() or 'desarrollar' in step_title.lower():
        base_output = f"""🛠️ CREACIÓN COMPLETADA - Paso {step_number}/{total_steps}

🎯 Elemento creado: {step_title}
📝 Especificación: {step_description}

📦 Artefactos generados:
• Archivo principal: {step_title.lower().replace(' ', '_')}.py (1.2 KB)
• Documentación: README.md (0.8 KB)
• Configuración: config.json (0.3 KB)
• Tests unitarios: test_{step_title.lower().replace(' ', '_')}.py (0.9 KB)

🔧 Características implementadas:
- Funcionalidad core: ✅ Implementada
- Manejo de errores: ✅ Incluido
- Logging: ✅ Configurado
- Validación de entrada: ✅ Activa"""

        # Posibles triggers para análisis dinámico
        if trigger_dynamic_analysis:
            dynamic_triggers = [
                "\n\n⚠️ PROBLEMAS DETECTADOS:\n• Error en la integración con API externa\n• Problema de rendimiento en consultas complejas",
                "\n\n🔧 OPTIMIZACIÓN REQUERIDA:\n• El rendimiento actual es subóptimo para cargas altas\n• Optimización de base de datos recomendada",
                "\n\n💡 MEJORAS SUGERIDAS:\n• Falta implementar cache para mejorar velocidad\n• Considerar implementar sistema de cola de tareas"
            ]
            base_output += random.choice(dynamic_triggers)

        base_output += f"""

✅ Estado: Artefacto listo para uso
⏱️ Tiempo de ejecución: {random.uniform(3.2, 5.9):.1f} segundos
📊 Calidad: 92% de cobertura de tests"""

        return base_output

    elif 'configurar' in step_title.lower() or 'instalar' in step_title.lower():
        base_output = f"""⚙️ CONFIGURACIÓN COMPLETADA - Paso {step_number}/{total_steps}

🔧 Sistema configurado: {step_title}
📋 Parámetros: {step_description}

🛠️ Configuraciones aplicadas:
• Variables de entorno: 8 configuradas
• Dependencias: 12 instaladas correctamente
• Permisos: Asignados según especificación
• Conexiones: 3 servicios conectados

📊 Verificaciones realizadas:
- Conectividad: ✅ OK (latencia: 45ms)
- Autenticación: ✅ Válida
- Recursos: ✅ Disponibles (CPU: 15%, RAM: 32%)
- Logs: ✅ Funcionando"""

        # Posibles triggers para análisis dinámico
        if trigger_dynamic_analysis:
            dynamic_triggers = [
                "\n\n⚠️ CONFIGURACIÓN ADICIONAL REQUERIDA:\n• Variables de entorno de producción pendientes\n• Configuración adicional de seguridad necesaria",
                "\n\n🔍 MONITOREO RECOMENDADO:\n• Sistema de logs centralizado sugerido\n• Implementar alertas de rendimiento",
                "\n\n💡 PRÓXIMOS PASOS:\n• Considerar implementar backup automático\n• Configuración de alta disponibilidad pendiente"
            ]
            base_output += random.choice(dynamic_triggers)

        base_output += f"""

✅ Estado: Sistema operativo y listo
⏱️ Tiempo de configuración: {random.uniform(2.5, 4.2):.1f} segundos
🔄 Servicios activos: 3/3"""

        return base_output

    elif 'test' in step_title.lower() or 'probar' in step_title.lower() or 'validar' in step_title.lower():
        base_output = f"""🧪 TESTING COMPLETADO - Paso {step_number}/{total_steps}

🎯 Pruebas ejecutadas: {step_title}
📝 Alcance: {step_description}

📊 Resultados de las pruebas:
• Tests unitarios: 24/24 ✅ (100% éxito)
• Tests de integración: 8/8 ✅ (100% éxito)
• Tests de rendimiento: 5/5 ✅ (100% éxito)
• Tests de seguridad: 3/3 ✅ (100% éxito)

📈 Métricas de calidad:
- Cobertura de código: 94.2%
- Tiempo de respuesta promedio: 127ms
- Throughput: 1,250 req/seg
- Memoria utilizada: 45MB"""

        # Posibles triggers para análisis dinámico
        if trigger_dynamic_analysis:
            dynamic_triggers = [
                "\n\n❌ ERRORES ENCONTRADOS:\n• 3 fallos en tests de integración detectados\n• Errores encontrados en validación de datos",
                "\n\n⚠️ COBERTURA INSUFICIENTE:\n• Cobertura de testing del 65% (objetivo: 90%)\n• Faltan tests para módulos críticos",
                "\n\n🔍 TESTING ADICIONAL REQUERIDO:\n• Tests de carga pendientes\n• Validación de seguridad incompleta"
            ]
            base_output += random.choice(dynamic_triggers)

        base_output += f"""

✅ Estado: Todas las pruebas pasaron
⏱️ Tiempo de ejecución: {random.uniform(4.1, 6.8):.1f} segundos
🏆 Calidad: Excelente (A+)"""

        return base_output

    elif 'deploy' in step_title.lower() or 'desplegar' in step_title.lower():
        base_output = f"""🚀 DEPLOYMENT COMPLETADO - Paso {step_number}/{total_steps}

🌐 Servicio desplegado: {step_title}
📍 Destino: {step_description}

🔗 URLs generadas:
• Producción: https://app-{random.randint(1000,9999)}.manus.space
• API: https://api-{random.randint(1000,9999)}.manus.space
• Documentación: https://docs-{random.randint(1000,9999)}.manus.space

📊 Estado del deployment:
- Build: ✅ Exitoso (2.3 min)
- Tests: ✅ Pasaron (45 seg)
- Deploy: ✅ Completado (1.1 min)
- Health check: ✅ OK (200 ms)

🔧 Servicios activos:
- Frontend: ✅ Operativo
- Backend: ✅ Operativo
- Base de datos: ✅ Conectada
- CDN: ✅ Configurado"""

        # Posibles triggers para análisis dinámico
        if trigger_dynamic_analysis:
            dynamic_triggers = [
                "\n\n⚠️ CONFIGURACIÓN ADICIONAL REQUERIDA:\n• Variables de entorno de producción pendientes\n• Configuración adicional de SSL necesaria",
                "\n\n📊 MONITOREO RECOMENDADO:\n• Sistema de monitoreo de aplicación sugerido\n• Logs centralizados pendientes de configurar",
                "\n\n🔧 OPTIMIZACIONES PENDIENTES:\n• CDN requiere configuración adicional\n• Backup automático no configurado"
            ]
            base_output += random.choice(dynamic_triggers)

        base_output += f"""

✅ Estado: Aplicación en vivo y funcional
⏱️ Tiempo total: {random.uniform(5.2, 8.1):.1f} segundos
📈 Uptime esperado: 99.9%"""

        return base_output

    else:
        # Output genérico para otros tipos de pasos
        return f"""📋 TAREA COMPLETADA - Paso {step_number}/{total_steps}

🎯 Tarea ejecutada: {step_title}
📝 Detalles: {step_description}

🔄 Acciones realizadas:
• Procesamiento de datos: ✅ Completado
• Validación de resultados: ✅ Exitosa
• Generación de outputs: ✅ Finalizada
• Actualización de estado: ✅ Realizada

📊 Métricas de ejecución:
- Elementos procesados: {random.randint(15, 150)}
- Errores encontrados: 0
- Warnings: {random.randint(0, 3)}
- Optimizaciones aplicadas: {random.randint(2, 8)}

✅ Estado: Tarea completada satisfactoriamente
⏱️ Tiempo de ejecución: {random.uniform(2.0, 5.5):.1f} segundos
📈 Eficiencia: {random.randint(85, 98)}%"""

def generate_plan_summary(plan, steps):
    """Generar resumen final del plan ejecutado"""
    plan_title = plan.get('title', 'Plan sin título')
    completed_steps = len([s for s in steps if s.get('status') == 'completed'])
    total_outputs = len([s for s in steps if s.get('output')])
    
    return f"""🎉 PLAN EJECUTADO EXITOSAMENTE

📋 Plan: {plan_title}
📊 Progreso: {completed_steps}/{len(steps)} pasos completados (100%)

📈 Resumen de ejecución:
• Pasos ejecutados: {completed_steps}
• Outputs generados: {total_outputs}
• Tiempo total estimado: {random.uniform(15, 45):.1f} segundos
• Eficiencia general: {random.randint(88, 97)}%

🎯 Resultados principales:
• Todos los objetivos fueron alcanzados
• No se encontraron errores críticos
• Calidad de outputs: Excelente
• Sistema listo para uso

📊 Métricas finales:
- Éxito de ejecución: 100%
- Cobertura de requisitos: 100%
- Satisfacción de criterios: 100%
- Tiempo dentro de estimación: ✅

✅ Estado final: COMPLETADO EXITOSAMENTE
🏆 Calificación: A+ (Excelente)
📅 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

