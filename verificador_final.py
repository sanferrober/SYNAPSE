#!/usr/bin/env python3
"""
Verificador final - Crea archivo de estado que podemos leer
"""
import os
import sys
import json
from datetime import datetime

# Crear reporte de estado
estado = {
    "timestamp": datetime.now().isoformat(),
    "python_version": sys.version.split()[0],
    "sistema": os.name,
    "directorio": os.getcwd(),
    "archivos_clave": {},
    "status": "verificando"
}

# Verificar archivos clave
archivos_importantes = [
    "synapse_server_final.py",
    "requirements.txt", 
    "llm_config.json",
    "script_maestro.py",
    "ejecutor_directo.py"
]

for archivo in archivos_importantes:
    if os.path.exists(archivo):
        estado["archivos_clave"][archivo] = {
            "existe": True,
            "tamaño": os.path.getsize(archivo)
        }
    else:
        estado["archivos_clave"][archivo] = {
            "existe": False,
            "tamaño": 0
        }

# Verificar módulos
try:
    import requests
    estado["requests"] = "disponible"
except ImportError:
    estado["requests"] = "no_disponible"

try:
    import flask
    estado["flask"] = "disponible"  
except ImportError:
    estado["flask"] = "no_disponible"

# Determinar estado final
archivos_ok = sum(1 for f in estado["archivos_clave"].values() if f["existe"])
total_archivos = len(archivos_importantes)

if archivos_ok == total_archivos:
    estado["status"] = "completo"
    estado["mensaje"] = "Todos los archivos están presentes"
else:
    estado["status"] = "parcial"
    estado["mensaje"] = f"Faltan {total_archivos - archivos_ok} archivos"

# Guardar estado
with open("estado_final.json", "w", encoding="utf-8") as f:
    json.dump(estado, f, indent=2, ensure_ascii=False)

# Crear archivo de texto simple
with open("estado_final.txt", "w", encoding="utf-8") as f:
    f.write("VERIFICACIÓN FINAL DEL SISTEMA\n")
    f.write("=" * 40 + "\n")
    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Python: {sys.version.split()[0]}\n")
    f.write(f"Sistema: {os.name}\n")
    f.write(f"Directorio: {os.getcwd()}\n")
    f.write(f"Estado: {estado['status'].upper()}\n")
    f.write(f"Mensaje: {estado['mensaje']}\n")
    f.write("\nArchivos verificados:\n")
    for archivo, info in estado["archivos_clave"].items():
        status = "✅" if info["existe"] else "❌"
        f.write(f"{status} {archivo}: {info['tamaño']:,} bytes\n")
    
    f.write(f"\nMódulos:\n")
    f.write(f"- requests: {estado.get('requests', 'no_verificado')}\n")
    f.write(f"- flask: {estado.get('flask', 'no_verificado')}\n")

print("Verificación completada - archivos creados:")
print("- estado_final.json")
print("- estado_final.txt")