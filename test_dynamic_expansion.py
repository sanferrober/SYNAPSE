#!/usr/bin/env python3
"""
Test script para verificar el sistema de expansión dinámica de planes
"""

import sys
import os
import json
import time
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dynamic_functions():
    """Probar las funciones de análisis dinámico"""
    print("🧪 TESTING SISTEMA DE EXPANSIÓN DINÁMICA")
    print("=" * 50)
    
    try:
        # Importar las funciones desde dynamic_analysis
        from dynamic_analysis import (
            analyze_step_results,
            generate_dynamic_steps,
            should_expand_plan,
            notify_plan_expansion
        )
        
        print("✅ Funciones importadas correctamente")
        
        # Test 1: Análisis de paso con problemas
        print("\n📊 Test 1: Análisis de paso con problemas")
        test_step = {
            'id': 'step_1',
            'title': 'Crear sistema de autenticación',
            'description': 'Implementar login y registro de usuarios',
            'status': 'completed'
        }
        
        test_output = """🛠️ CREACIÓN COMPLETADA - Paso 1/5

🎯 Elemento creado: Crear sistema de autenticación
📝 Especificación: Implementar login y registro de usuarios

⚠️ PROBLEMAS DETECTADOS:
• Error en la integración con API externa
• Problema de rendimiento en consultas complejas

✅ Estado: Artefacto listo para uso"""
        
        test_plan = {
            'id': 'plan_123',
            'title': 'Desarrollo de aplicación web',
            'steps': [test_step]
        }
        
        analysis = analyze_step_results(test_step, test_output, test_plan)
        print(f"   Análisis: {analysis}")
        print(f"   Necesita expansión: {analysis['needs_expansion']}")
        print(f"   Confianza: {analysis['confidence']:.0%}")
        
        # Test 2: Generación de pasos dinámicos
        if analysis['needs_expansion']:
            print("\n🔄 Test 2: Generación de pasos dinámicos")
            new_steps = generate_dynamic_steps(analysis, test_plan, 0)
            print(f"   Pasos generados: {len(new_steps)}")
            for i, step in enumerate(new_steps, 1):
                print(f"   {i}. {step['title']}")
        
        # Test 3: Verificar criterios de expansión
        print("\n✅ Test 3: Verificar criterios de expansión")
        should_expand = should_expand_plan(analysis, test_plan)
        print(f"   Debe expandirse: {should_expand}")
        
        # Test 4: Análisis de paso sin problemas
        print("\n📊 Test 4: Análisis de paso sin problemas")
        clean_output = """🛠️ CREACIÓN COMPLETADA - Paso 1/5

🎯 Elemento creado: Crear sistema de autenticación
📝 Especificación: Implementar login y registro de usuarios

✅ Estado: Artefacto listo para uso
⏱️ Tiempo de ejecución: 3.5 segundos
📊 Calidad: 92% de cobertura de tests"""
        
        clean_analysis = analyze_step_results(test_step, clean_output, test_plan)
        print(f"   Análisis: {clean_analysis}")
        print(f"   Necesita expansión: {clean_analysis['needs_expansion']}")
        
        # Test 5: Notificación de expansión
        if analysis['needs_expansion'] and should_expand:
            print("\n📢 Test 5: Notificación de expansión")
            new_steps = generate_dynamic_steps(analysis, test_plan, 0)
            notify_plan_expansion(test_plan, new_steps, analysis)
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando funciones: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_output_generation():
    """Probar la generación de outputs que activen análisis dinámico"""
    print("\n🎯 TESTING GENERACIÓN DE OUTPUTS DINÁMICOS")
    print("=" * 50)
    
    try:
        from output_generators import generate_step_output
        
        test_steps = [
            {
                'title': 'Crear API REST',
                'description': 'Desarrollar endpoints para la aplicación'
            },
            {
                'title': 'Configurar base de datos',
                'description': 'Instalar y configurar PostgreSQL'
            },
            {
                'title': 'Probar sistema completo',
                'description': 'Ejecutar tests de integración'
            }
        ]
        
        print("Generando outputs de prueba...")
        for i, step in enumerate(test_steps, 1):
            print(f"\n📋 Paso {i}: {step['title']}")
            output = generate_step_output(step, i, len(test_steps))
            
            # Verificar si el output contiene triggers dinámicos
            dynamic_triggers = [
                "PROBLEMAS DETECTADOS",
                "OPTIMIZACIÓN REQUERIDA",
                "MEJORAS SUGERIDAS",
                "CONFIGURACIÓN ADICIONAL REQUERIDA",
                "MONITOREO RECOMENDADO",
                "PRÓXIMOS PASOS",
                "ERRORES ENCONTRADOS",
                "COBERTURA INSUFICIENTE",
                "TESTING ADICIONAL REQUERIDO"
            ]
            
            has_trigger = any(trigger in output for trigger in dynamic_triggers)
            print(f"   Contiene trigger dinámico: {'✅ SÍ' if has_trigger else '❌ NO'}")
            
            if has_trigger:
                print("   Primeros 200 caracteres del output:")
                print(f"   {output[:200]}...")
        
        print("\n✅ Test de generación de outputs completado")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de outputs: {e}")
        return False

def main():
    """Función principal de testing"""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE EXPANSIÓN DINÁMICA")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar tests
    test1_result = test_dynamic_functions()
    test2_result = test_output_generation()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    print(f"✅ Test funciones dinámicas: {'PASÓ' if test1_result else 'FALLÓ'}")
    print(f"✅ Test generación outputs: {'PASÓ' if test2_result else 'FALLÓ'}")
    
    if test1_result and test2_result:
        print("\n🎉 TODOS LOS TESTS PASARON - Sistema listo para uso")
        return 0
    else:
        print("\n❌ ALGUNOS TESTS FALLARON - Revisar implementación")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)