#!/usr/bin/env python3
"""
Script de prueba para verificar la generación y envío de outputs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_integration'))

from output_generators import generate_step_output

def test_output_generation():
    """Probar la generación de outputs"""
    print("🧪 Probando generación de outputs...")
    
    test_steps = [
        {'title': 'Análisis de Requisitos', 'description': 'Definir funcionalidades'},
        {'title': 'Crear Backend', 'description': 'Desarrollar API REST'},
        {'title': 'Configurar Base de Datos', 'description': 'Instalar y configurar PostgreSQL'},
        {'title': 'Testing de la Aplicación', 'description': 'Ejecutar pruebas unitarias'},
        {'title': 'Deploy a Producción', 'description': 'Desplegar en servidor'}
    ]
    
    for i, step in enumerate(test_steps):
        print(f"\n📋 Paso {i+1}: {step['title']}")
        try:
            output = generate_step_output(step, i+1, len(test_steps))
            print(f"✅ Output generado: {len(output)} caracteres")
            print(f"📄 Preview: {output[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Prueba completada")

if __name__ == "__main__":
    test_output_generation()