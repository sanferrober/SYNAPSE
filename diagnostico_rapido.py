#!/usr/bin/env python3
"""
🔧 DIAGNÓSTICO RÁPIDO: Problemas de Terminal
"""

import sys
import os
import subprocess
from datetime import datetime

print("🔧 DIAGNÓSTICO RÁPIDO DEL TERMINAL")
print("=" * 50)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Información básica
print(f"\n💻 Sistema: {os.name}")
print(f"🐍 Python: {sys.version.split()[0]}")
print(f"📁 Directorio: {os.getcwd()}")

# 2. Probar comando simple
try:
    result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"✅ Python funciona: {result.stdout.strip()}")
    else:
        print(f"❌ Python error: {result.stderr.strip()}")
except Exception as e:
    print(f"❌ Error ejecutando Python: {str(e)}")

# 3. Verificar archivos clave
archivos_clave = ['synapse_server_final.py', 'requirements.txt', 'llm_config.json']
for archivo in archivos_clave:
    if os.path.exists(archivo):
        print(f"✅ {archivo}: Existe")
    else:
        print(f"❌ {archivo}: No encontrado")

# 4. Probar importaciones críticas
modulos = ['json', 'os', 'sys', 'subprocess']
for modulo in modulos:
    try:
        __import__(modulo)
        print(f"✅ {modulo}: OK")
    except ImportError:
        print(f"❌ {modulo}: Error")

print("\n📊 DIAGNÓSTICO COMPLETADO")
print("=" * 50)