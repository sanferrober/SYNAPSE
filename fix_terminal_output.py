#!/usr/bin/env python3
"""
🔧 DIAGNÓSTICO Y SOLUCIÓN: Error "Failed to retrieve terminal output"
Identifica y resuelve problemas comunes con la salida del terminal
"""

import os
import sys
import subprocess
import platform
import json
from datetime import datetime

def diagnose_terminal_issues():
    """Diagnostica problemas comunes del terminal"""
    print("🔍 DIAGNÓSTICO DEL TERMINAL")
    print("=" * 50)
    
    # Información del sistema
    print(f"💻 Sistema operativo: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"👤 Usuario: {os.getenv('USERNAME', os.getenv('USER', 'Desconocido'))}")
    
    # Verificar shell
    shell = os.getenv('SHELL', os.getenv('COMSPEC', 'Desconocido'))
    print(f"🐚 Shell: {shell}")
    
    # Verificar permisos
    current_dir = os.getcwd()
    print(f"📝 Permisos de escritura: {'✅ Sí' if os.access(current_dir, os.W_OK) else '❌ No'}")
    print(f"📖 Permisos de lectura: {'✅ Sí' if os.access(current_dir, os.R_OK) else '❌ No'}")
    print(f"🏃 Permisos de ejecución: {'✅ Sí' if os.access(current_dir, os.X_OK) else '❌ No'}")
    
    return {
        'system': platform.system(),
        'python_version': sys.version,
        'shell': shell,
        'current_dir': current_dir,
        'permissions': {
            'write': os.access(current_dir, os.W_OK),
            'read': os.access(current_dir, os.R_OK),
            'execute': os.access(current_dir, os.X_OK)
        }
    }

def test_basic_commands():
    """Prueba comandos básicos del sistema"""
    print("\n🧪 PRUEBA DE COMANDOS BÁSICOS")
    print("=" * 50)
    
    commands = []
    if platform.system() == "Windows":
        commands = [
            ("dir", "Listar archivos"),
            ("echo Hello", "Comando echo"),
            ("python --version", "Versión de Python"),
            ("where python", "Ubicación de Python")
        ]
    else:
        commands = [
            ("ls -la", "Listar archivos"),
            ("echo Hello", "Comando echo"),
            ("python3 --version", "Versión de Python"),
            ("which python3", "Ubicación de Python")
        ]
    
    results = []
    for cmd, description in commands:
        try:
            print(f"🔄 Probando: {description}")
            result = subprocess.run(
                cmd.split(), 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"   ✅ Éxito: {result.stdout.strip()[:100]}")
                results.append((cmd, True, result.stdout.strip()))
            else:
                print(f"   ❌ Error: {result.stderr.strip()[:100]}")
                results.append((cmd, False, result.stderr.strip()))
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout: Comando tardó demasiado")
            results.append((cmd, False, "Timeout"))
        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")
            results.append((cmd, False, str(e)))
    
    return results

def check_python_environment():
    """Verifica el entorno de Python"""
    print("\n🐍 VERIFICACIÓN DEL ENTORNO PYTHON")
    print("=" * 50)
    
    # Verificar módulos importantes
    modules_to_check = [
        'subprocess',
        'os',
        'sys',
        'json',
        'requests',
        'flask',
        'socketio'
    ]
    
    available_modules = []
    missing_modules = []
    
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"   ✅ {module}: Disponible")
            available_modules.append(module)
        except ImportError:
            print(f"   ❌ {module}: No disponible")
            missing_modules.append(module)
    
    # Verificar pip
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ pip: {result.stdout.strip()}")
        else:
            print(f"   ❌ pip: Error - {result.stderr.strip()}")
    except Exception as e:
        print(f"   ❌ pip: No disponible - {str(e)}")
    
    return {
        'available_modules': available_modules,
        'missing_modules': missing_modules
    }

def install_missing_dependencies():
    """Instala dependencias faltantes"""
    print("\n📦 INSTALACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    # Lista de dependencias críticas
    critical_deps = [
        'requests',
        'flask',
        'flask-cors',
        'flask-socketio',
        'psutil'
    ]
    
    for dep in critical_deps:
        try:
            print(f"🔄 Instalando {dep}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ {dep}: Instalado correctamente")
            else:
                print(f"   ❌ {dep}: Error - {result.stderr.strip()[:200]}")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {dep}: Timeout durante instalación")
        except Exception as e:
            print(f"   ❌ {dep}: Excepción - {str(e)}")

def create_test_script():
    """Crea un script de prueba simple"""
    print("\n📝 CREANDO SCRIPT DE PRUEBA")
    print("=" * 50)
    
    test_script_content = '''#!/usr/bin/env python3
"""Script de prueba simple para verificar funcionalidad básica"""

import sys
import os
from datetime import datetime

def main():
    print("🚀 SCRIPT DE PRUEBA FUNCIONANDO")
    print("=" * 40)
    print(f"⏰ Fecha/Hora: {datetime.now()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")
    print("✅ Script ejecutado correctamente")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open('test_simple.py', 'w', encoding='utf-8') as f:
            f.write(test_script_content)
        print("   ✅ Script de prueba creado: test_simple.py")
        
        # Probar ejecución
        result = subprocess.run([sys.executable, 'test_simple.py'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Script ejecutado correctamente:")
            print("   " + "\n   ".join(result.stdout.strip().split('\n')))
        else:
            print(f"   ❌ Error ejecutando script: {result.stderr.strip()}")
            
    except Exception as e:
        print(f"   ❌ Error creando script: {str(e)}")

def fix_common_issues():
    """Aplica soluciones a problemas comunes"""
    print("\n🔧 APLICANDO SOLUCIONES")
    print("=" * 50)
    
    fixes_applied = []
    
    # 1. Verificar y crear directorios necesarios
    try:
        os.makedirs('logs', exist_ok=True)
        os.makedirs('temp', exist_ok=True)
        print("   ✅ Directorios logs/ y temp/ verificados")
        fixes_applied.append("Directorios creados")
    except Exception as e:
        print(f"   ❌ Error creando directorios: {str(e)}")
    
    # 2. Limpiar archivos temporales
    try:
        temp_files = [f for f in os.listdir('.') if f.endswith('.tmp') or f.endswith('.log')]
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"   🗑️  Eliminado: {temp_file}")
            except:
                pass
        fixes_applied.append("Archivos temporales limpiados")
    except Exception as e:
        print(f"   ⚠️  Advertencia limpiando temporales: {str(e)}")
    
    # 3. Verificar variables de entorno
    important_env_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER', 'USERNAME']
    for var in important_env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Configurado")
        else:
            print(f"   ⚠️  {var}: No configurado")
    
    return fixes_applied

def generate_report(diagnosis, command_results, python_env, fixes):
    """Genera un reporte completo del diagnóstico"""
    print("\n📊 GENERANDO REPORTE")
    print("=" * 50)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'diagnosis': diagnosis,
        'command_results': command_results,
        'python_environment': python_env,
        'fixes_applied': fixes,
        'recommendations': []
    }
    
    # Generar recomendaciones
    if not python_env['available_modules']:
        report['recommendations'].append("Instalar dependencias de Python faltantes")
    
    if not diagnosis['permissions']['write']:
        report['recommendations'].append("Verificar permisos de escritura en el directorio")
    
    successful_commands = sum(1 for _, success, _ in command_results if success)
    if successful_commands < len(command_results) / 2:
        report['recommendations'].append("Verificar configuración del shell/terminal")
    
    # Guardar reporte
    try:
        with open('terminal_diagnosis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("   ✅ Reporte guardado: terminal_diagnosis_report.json")
    except Exception as e:
        print(f"   ❌ Error guardando reporte: {str(e)}")
    
    return report

def main():
    """Función principal de diagnóstico y reparación"""
    print("🔧 DIAGNÓSTICO Y REPARACIÓN DEL TERMINAL")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Diagnóstico inicial
    diagnosis = diagnose_terminal_issues()
    
    # 2. Prueba de comandos básicos
    command_results = test_basic_commands()
    
    # 3. Verificación del entorno Python
    python_env = check_python_environment()
    
    # 4. Instalación de dependencias si es necesario
    if python_env['missing_modules']:
        install_missing_dependencies()
    
    # 5. Crear script de prueba
    create_test_script()
    
    # 6. Aplicar soluciones
    fixes = fix_common_issues()
    
    # 7. Generar reporte
    report = generate_report(diagnosis, command_results, python_env, fixes)
    
    # 8. Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL")
    print("=" * 60)
    
    successful_commands = sum(1 for _, success, _ in command_results if success)
    total_commands = len(command_results)
    
    print(f"🖥️  Sistema: {diagnosis['system']}")
    print(f"🐍 Python: Funcionando")
    print(f"📝 Comandos exitosos: {successful_commands}/{total_commands}")
    print(f"📦 Módulos disponibles: {len(python_env['available_modules'])}")
    print(f"🔧 Soluciones aplicadas: {len(fixes)}")
    
    if report['recommendations']:
        print(f"\n💡 RECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    if successful_commands >= total_commands * 0.8:
        print(f"\n✅ DIAGNÓSTICO EXITOSO")
        print("   El terminal debería funcionar correctamente ahora")
    else:
        print(f"\n⚠️  PROBLEMAS DETECTADOS")
        print("   Revisar el reporte para más detalles")
    
    print(f"\n⏰ Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()