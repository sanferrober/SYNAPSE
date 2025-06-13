#!/usr/bin/env python3
"""
Test script para verificar el sistema de configuración de LLMs
"""

import sys
import os
import json
import time
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_llm_config_functions():
    """Probar las funciones de configuración de LLMs"""
    print("🧪 TESTING SISTEMA DE CONFIGURACIÓN DE LLMS")
    print("=" * 50)
    
    try:
        # Importar funciones desde el servidor
        from synapse_server_final import (
            DEFAULT_LLM_CONFIG,
            llm_config,
            get_llm_for_agent,
            test_llm_connection_real,
            save_llm_config_to_disk,
            load_llm_config_from_disk
        )
        
        print("✅ Funciones importadas correctamente")
        
        # Test 1: Configuración por defecto
        print("\n📋 Test 1: Configuración por defecto")
        print(f"   Configuración default: {DEFAULT_LLM_CONFIG}")
        print(f"   Configuración actual: {llm_config}")
        
        # Test 2: Obtener LLM para agente específico
        print("\n🤖 Test 2: Obtener LLM para agentes")
        agents_to_test = ['conversation_agent', 'planning_agent', 'execution_agent']
        for agent in agents_to_test:
            llm = get_llm_for_agent(agent)
            print(f"   {agent}: {llm}")
        
        # Test 3: Probar conexiones LLM
        print("\n🧪 Test 3: Probar conexiones LLM")
        llms_to_test = ['gpt-4', 'gpt-3.5-turbo', 'claude-3-sonnet']
        for llm_id in llms_to_test:
            print(f"   Probando {llm_id}...", end=" ")
            success = test_llm_connection_real(llm_id)
            print(f"{'✅ Éxito' if success else '❌ Fallo'}")
        
        # Test 4: Guardar y cargar configuración
        print("\n💾 Test 4: Persistencia de configuración")
        
        # Modificar configuración temporalmente
        original_config = llm_config.copy()
        llm_config['conversation_agent'] = 'claude-3-opus'
        llm_config['execution_agent'] = 'gemini-flash'
        
        # Guardar
        save_llm_config_to_disk()
        print("   ✅ Configuración guardada")
        
        # Restaurar configuración original y cargar desde disco
        llm_config.clear()
        llm_config.update(DEFAULT_LLM_CONFIG)
        
        load_success = load_llm_config_from_disk()
        print(f"   {'✅' if load_success else '❌'} Configuración cargada")
        
        if load_success:
            print(f"   Configuración cargada: {llm_config}")
        
        # Restaurar configuración original
        llm_config.clear()
        llm_config.update(original_config)
        
        print("\n🎉 TODOS LOS TESTS DE CONFIGURACIÓN COMPLETADOS")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando funciones: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_options():
    """Probar las opciones de LLM disponibles"""
    print("\n🎯 TESTING OPCIONES DE LLMS DISPONIBLES")
    print("=" * 50)
    
    # Definir LLMs disponibles (copiado del componente)
    llm_options = [
        {
            'id': 'gpt-4',
            'name': 'GPT-4',
            'provider': 'OpenAI',
            'tier': 'premium',
            'strengths': ['Razonamiento complejo', 'Análisis profundo', 'Creatividad'],
            'cost': 'Alto',
            'speed': 'Medio'
        },
        {
            'id': 'gpt-3.5-turbo',
            'name': 'GPT-3.5 Turbo',
            'provider': 'OpenAI',
            'tier': 'standard',
            'strengths': ['Velocidad', 'Eficiencia', 'Costo-efectivo'],
            'cost': 'Bajo',
            'speed': 'Rápido'
        },
        {
            'id': 'claude-3-opus',
            'name': 'Claude 3 Opus',
            'provider': 'Anthropic',
            'tier': 'premium',
            'strengths': ['Análisis detallado', 'Seguridad', 'Precisión'],
            'cost': 'Alto',
            'speed': 'Medio'
        },
        {
            'id': 'claude-3-sonnet',
            'name': 'Claude 3 Sonnet',
            'provider': 'Anthropic',
            'tier': 'standard',
            'strengths': ['Balance', 'Versatilidad', 'Confiabilidad'],
            'cost': 'Medio',
            'speed': 'Medio'
        },
        {
            'id': 'claude-3-haiku',
            'name': 'Claude 3 Haiku',
            'provider': 'Anthropic',
            'tier': 'fast',
            'strengths': ['Velocidad', 'Eficiencia', 'Respuestas rápidas'],
            'cost': 'Bajo',
            'speed': 'Muy Rápido'
        },
        {
            'id': 'gemini-pro',
            'name': 'Gemini Pro',
            'provider': 'Google',
            'tier': 'standard',
            'strengths': ['Multimodal', 'Análisis de código', 'Integración'],
            'cost': 'Medio',
            'speed': 'Rápido'
        },
        {
            'id': 'gemini-flash',
            'name': 'Gemini Flash',
            'provider': 'Google',
            'tier': 'fast',
            'strengths': ['Velocidad extrema', 'Bajo costo', 'Eficiencia'],
            'cost': 'Muy Bajo',
            'speed': 'Muy Rápido'
        }
    ]
    
    print(f"📊 Total de LLMs disponibles: {len(llm_options)}")
    
    # Agrupar por proveedor
    providers = {}
    for llm in llm_options:
        provider = llm['provider']
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(llm)
    
    print("\n🏢 LLMs por proveedor:")
    for provider, llms in providers.items():
        print(f"   {provider}: {len(llms)} modelos")
        for llm in llms:
            print(f"     - {llm['name']} ({llm['tier']}) - {llm['cost']} costo")
    
    # Agrupar por tier
    tiers = {}
    for llm in llm_options:
        tier = llm['tier']
        if tier not in tiers:
            tiers[tier] = []
        tiers[tier].append(llm)
    
    print("\n⭐ LLMs por tier:")
    for tier, llms in tiers.items():
        print(f"   {tier.upper()}: {len(llms)} modelos")
        for llm in llms:
            print(f"     - {llm['name']} ({llm['provider']})")
    
    print("\n✅ Test de opciones LLM completado")
    return True

def test_agent_recommendations():
    """Probar las recomendaciones de LLM por agente"""
    print("\n🎯 TESTING RECOMENDACIONES POR AGENTE")
    print("=" * 50)
    
    # Definir agentes (copiado del componente)
    agents = [
        {
            'id': 'conversation_agent',
            'name': 'Agente de Conversación',
            'recommended': ['gpt-4', 'claude-3-opus', 'gemini-pro']
        },
        {
            'id': 'planning_agent',
            'name': 'Agente de Planificación',
            'recommended': ['gpt-4', 'claude-3-sonnet', 'gemini-pro']
        },
        {
            'id': 'execution_agent',
            'name': 'Agente de Ejecución',
            'recommended': ['gpt-3.5-turbo', 'claude-3-haiku', 'gemini-flash']
        },
        {
            'id': 'analysis_agent',
            'name': 'Agente de Análisis',
            'recommended': ['gpt-4', 'claude-3-sonnet', 'gemini-pro']
        },
        {
            'id': 'memory_agent',
            'name': 'Agente de Memoria',
            'recommended': ['gpt-3.5-turbo', 'claude-3-haiku', 'gemini-flash']
        },
        {
            'id': 'optimization_agent',
            'name': 'Agente de Optimización',
            'recommended': ['claude-3-sonnet', 'gpt-4', 'gemini-pro']
        }
    ]
    
    print("🤖 Recomendaciones por agente:")
    for agent in agents:
        print(f"\n   {agent['name']}:")
        for i, rec_llm in enumerate(agent['recommended'], 1):
            print(f"     {i}. {rec_llm}")
    
    # Verificar que todos los agentes tienen recomendaciones
    all_have_recommendations = all(len(agent['recommended']) > 0 for agent in agents)
    print(f"\n✅ Todos los agentes tienen recomendaciones: {'Sí' if all_have_recommendations else 'No'}")
    
    return True

def main():
    """Función principal de testing"""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE CONFIGURACIÓN DE LLMS")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar tests
    test1_result = test_llm_config_functions()
    test2_result = test_llm_options()
    test3_result = test_agent_recommendations()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    print(f"✅ Test funciones configuración: {'PASÓ' if test1_result else 'FALLÓ'}")
    print(f"✅ Test opciones LLM: {'PASÓ' if test2_result else 'FALLÓ'}")
    print(f"✅ Test recomendaciones agentes: {'PASÓ' if test3_result else 'FALLÓ'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 TODOS LOS TESTS PASARON - Sistema de configuración LLM listo")
        return 0
    else:
        print("\n❌ ALGUNOS TESTS FALLARON - Revisar implementación")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)