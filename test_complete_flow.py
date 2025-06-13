#!/usr/bin/env python3
"""
Script de prueba completo para verificar el flujo de outputs
"""

import requests
import json
import time
from datetime import datetime

def test_server_health():
    """Probar que el servidor esté funcionando"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor funcionando - Versión: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_memory_endpoints():
    """Probar los endpoints de memoria"""
    try:
        # Probar endpoint de memoria completa
        response = requests.get('http://localhost:5000/api/memory/all', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint de memoria funcionando")
            print(f"   - Planes ejecutados: {len(data.get('executed_plans', []))}")
            print(f"   - Outputs guardados: {len(data.get('memory_store', {}).get('plan_outputs', {}))}")
        else:
            print(f"❌ Endpoint de memoria falló: {response.status_code}")
        
        # Probar endpoint de outputs recientes
        response = requests.get('http://localhost:5000/api/outputs/recent', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint de outputs recientes funcionando")
            print(f"   - Outputs recientes: {len(data.get('recent_outputs', []))}")
        else:
            print(f"❌ Endpoint de outputs recientes falló: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando endpoints: {e}")

def main():
    print("🧪 Iniciando pruebas del sistema Synapse...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # Probar salud del servidor
    print("1. Probando salud del servidor...")
    if not test_server_health():
        print("❌ El servidor no está funcionando. Asegúrate de ejecutar 'python synapse_server_final.py'")
        return
    
    print("\n2. Probando endpoints de memoria...")
    test_memory_endpoints()
    
    print("\n3. Verificando generación de outputs...")
    try:
        from output_generators import generate_step_output
        test_step = {'title': 'Prueba de Output', 'description': 'Verificación del sistema'}
        output = generate_step_output(test_step, 1, 1)
        print(f"✅ Generación de outputs funcionando ({len(output)} caracteres)")
    except Exception as e:
        print(f"❌ Error en generación de outputs: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNÓSTICO COMPLETO:")
    print("1. Verifica que el servidor esté ejecutándose en puerto 5000")
    print("2. Verifica que el frontend esté ejecutándose en puerto 3000")
    print("3. Abre las herramientas de desarrollador del navegador")
    print("4. Ve a la pestaña 'Debug' en la aplicación")
    print("5. Envía un mensaje y observa los logs en consola")
    print("6. Verifica que los outputs aparezcan en el panel de Resultados")

if __name__ == "__main__":
    main()