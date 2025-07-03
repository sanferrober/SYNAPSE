#!/usr/bin/env python3
"""
📦 INSTALADOR DE DEPENDENCIAS: Synapse
Instala todas las dependencias necesarias para que Synapse funcione correctamente
"""

import sys
import subprocess
import os
from datetime import datetime

def log_message(message):
    """Imprime mensaje con timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

def install_package(package_name, pip_name=None):
    """Instala un paquete usando pip"""
    if pip_name is None:
        pip_name = package_name
    
    log_message(f"Instalando {package_name}...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', pip_name
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            log_message(f"✅ {package_name}: Instalado correctamente")
            return True
        else:
            log_message(f"❌ {package_name}: Error - {result.stderr.strip()[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message(f"⏰ {package_name}: Timeout durante instalación")
        return False
    except Exception as e:
        log_message(f"❌ {package_name}: Excepción - {str(e)}")
        return False

def check_package(package_name):
    """Verifica si un paquete está instalado"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """Función principal del instalador"""
    log_message("🚀 INSTALADOR DE DEPENDENCIAS SYNAPSE")
    log_message("=" * 50)
    
    # Lista de dependencias críticas
    dependencias = [
        ('requests', 'requests'),
        ('flask', 'flask'),
        ('flask-cors', 'flask-cors'),
        ('flask-socketio', 'flask-socketio'),
        ('socketio', 'python-socketio[client]'),
        ('psutil', 'psutil'),
        ('aiofiles', 'aiofiles'),
        ('pydantic', 'pydantic>=2.8.0')
    ]
    
    # Verificar estado actual
    log_message("🔍 Verificando estado actual de dependencias...")
    
    instaladas = []
    faltantes = []
    
    for package_name, pip_name in dependencias:
        if check_package(package_name.replace('-', '_')):
            log_message(f"   ✅ {package_name}: Ya instalado")
            instaladas.append(package_name)
        else:
            log_message(f"   ❌ {package_name}: Faltante")
            faltantes.append((package_name, pip_name))
    
    log_message(f"\n📊 Estado: {len(instaladas)} instaladas, {len(faltantes)} faltantes")
    
    if not faltantes:
        log_message("🎉 Todas las dependencias ya están instaladas!")
        return True
    
    # Actualizar pip primero
    log_message("\n🔄 Actualizando pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      capture_output=True, timeout=60)
        log_message("✅ pip actualizado")
    except:
        log_message("⚠️ No se pudo actualizar pip, continuando...")
    
    # Instalar dependencias faltantes
    log_message(f"\n📦 Instalando {len(faltantes)} dependencias faltantes...")
    
    exitosos = 0
    fallidos = 0
    
    for package_name, pip_name in faltantes:
        if install_package(package_name, pip_name):
            exitosos += 1
        else:
            fallidos += 1
    
    # Verificación final
    log_message(f"\n🔍 Verificación final...")
    
    verificacion_final = []
    for package_name, _ in dependencias:
        if check_package(package_name.replace('-', '_')):
            log_message(f"   ✅ {package_name}: Funcionando")
            verificacion_final.append(True)
        else:
            log_message(f"   ❌ {package_name}: Aún no disponible")
            verificacion_final.append(False)
    
    # Resumen final
    log_message(f"\n" + "=" * 50)
    log_message("📋 RESUMEN DE INSTALACIÓN")
    log_message("=" * 50)
    
    log_message(f"📦 Total dependencias: {len(dependencias)}")
    log_message(f"✅ Instalaciones exitosas: {exitosos}")
    log_message(f"❌ Instalaciones fallidas: {fallidos}")
    log_message(f"🔍 Verificación final: {sum(verificacion_final)}/{len(verificacion_final)} funcionando")
    
    if sum(verificacion_final) >= len(verificacion_final) * 0.8:
        log_message(f"\n🎉 INSTALACIÓN EXITOSA")
        log_message("✅ Synapse debería funcionar correctamente ahora")
        log_message("💡 Ejecuta 'python prueba_synapse.py' para verificar")
        return True
    else:
        log_message(f"\n⚠️ INSTALACIÓN PARCIAL")
        log_message("💡 Algunas dependencias pueden necesitar instalación manual")
        log_message("💡 Verifica tu conexión a Internet y permisos")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)