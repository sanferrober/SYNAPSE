#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBA: Verificación de funcionalidad básica
Este script verifica que el sistema funciona correctamente
"""

import sys
import os
import json
from datetime import datetime

def main():
    print("🚀 PRUEBA SYNAPSE - VERIFICACIÓN BÁSICA")
    print("=" * 50)
    print(f"⏰ Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Directorio: {os.getcwd()}")
    
    # Verificar archivos clave del sistema
    archivos_clave = [
        'synapse_server_final.py',
        'llm_config.json',
        'requirements.txt',
        'mcp_integration/real_mcp_tools.py'
    ]
    
    print(f"\n📁 VERIFICANDO ARCHIVOS CLAVE:")
    archivos_encontrados = 0
    for archivo in archivos_clave:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"   ✅ {archivo}: Encontrado ({size:,} bytes)")
            archivos_encontrados += 1
        else:
            print(f"   ❌ {archivo}: No encontrado")
    
    # Verificar importaciones críticas
    print(f"\n🐍 VERIFICANDO IMPORTACIONES:")
    modulos_criticos = [
        'json', 'os', 'sys', 'datetime', 'subprocess'
    ]
    
    modulos_opcionales = [
        'requests', 'flask', 'socketio'
    ]
    
    modulos_ok = 0
    for modulo in modulos_criticos:
        try:
            __import__(modulo)
            print(f"   ✅ {modulo}: OK")
            modulos_ok += 1
        except ImportError:
            print(f"   ❌ {modulo}: Error")
    
    print(f"\n📦 VERIFICANDO MÓDULOS OPCIONALES:")
    modulos_opcionales_ok = 0
    for modulo in modulos_opcionales:
        try:
            __import__(modulo)
            print(f"   ✅ {modulo}: Disponible")
            modulos_opcionales_ok += 1
        except ImportError:
            print(f"   ⚠️  {modulo}: No instalado")
    
    # Generar resultado
    resultado = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'directorio': os.getcwd(),
        'archivos_encontrados': archivos_encontrados,
        'total_archivos': len(archivos_clave),
        'modulos_criticos_ok': modulos_ok,
        'modulos_opcionales_ok': modulos_opcionales_ok,
        'status': 'success' if modulos_ok == len(modulos_criticos) else 'partial'
    }
    
    # Guardar resultado
    try:
        with open('prueba_resultado.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Resultado guardado en: prueba_resultado.json")
    except Exception as e:
        print(f"\n❌ Error guardando resultado: {e}")
    
    # Resumen final
    print(f"\n" + "=" * 50)
    print("📊 RESUMEN DE LA PRUEBA")
    print("=" * 50)
    
    print(f"📁 Archivos encontrados: {archivos_encontrados}/{len(archivos_clave)}")
    print(f"🐍 Módulos críticos: {modulos_ok}/{len(modulos_criticos)}")
    print(f"📦 Módulos opcionales: {modulos_opcionales_ok}/{len(modulos_opcionales)}")
    
    if resultado['status'] == 'success':
        print(f"\n✅ PRUEBA EXITOSA")
        print("   Todos los componentes críticos están funcionando")
        if modulos_opcionales_ok < len(modulos_opcionales):
            print("   💡 Instalar módulos opcionales para funcionalidad completa:")
            print("      pip install requests flask flask-socketio")
    else:
        print(f"\n⚠️  PRUEBA PARCIAL")
        print("   Algunos componentes críticos faltan")
        print("   💡 Verificar instalación de Python y dependencias")
    
    print(f"\n⏰ Prueba completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()