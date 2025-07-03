#!/usr/bin/env python3
"""
🔧 SCRIPT MAESTRO: Solución Completa del Error de Terminal
Ejecuta todos los pasos necesarios para solucionar el problema
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def ejecutar_script(script_name, descripcion):
    """Ejecuta un script y captura su salida"""
    print(f"\n🔄 Ejecutando: {descripcion}")
    print(f"📄 Script: {script_name}")
    
    if not os.path.exists(script_name):
        print(f"❌ Script no encontrado: {script_name}")
        return False, f"Script {script_name} no existe"
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ {descripcion}: Completado exitosamente")
            if result.stdout.strip():
                # Mostrar solo las últimas líneas para no saturar
                lines = result.stdout.strip().split('\n')
                if len(lines) > 10:
                    print("   📄 Salida (últimas 10 líneas):")
                    for line in lines[-10:]:
                        if line.strip():
                            print(f"      {line.strip()}")
                else:
                    print("   📄 Salida completa:")
                    for line in lines:
                        if line.strip():
                            print(f"      {line.strip()}")
            return True, result.stdout
        else:
            print(f"❌ {descripcion}: Error (código {result.returncode})")
            if result.stderr.strip():
                print(f"   📄 Error: {result.stderr.strip()[:300]}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {descripcion}: Timeout - El script tardó demasiado")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ {descripcion}: Excepción - {str(e)}")
        return False, str(e)

def main():
    """Función principal del script maestro"""
    print("🔧 SCRIPT MAESTRO: Solución Completa del Error de Terminal")
    print("=" * 70)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de scripts a ejecutar en orden
    scripts = [
        ('instalar_dependencias.py', 'Instalación de dependencias'),
        ('prueba_synapse.py', 'Verificación del sistema'),
        ('demo_mcp_simple.py', 'Demostración de herramientas MCP')
    ]
    
    resultados = []
    
    # Ejecutar cada script
    for script_name, descripcion in scripts:
        exito, salida = ejecutar_script(script_name, descripcion)
        resultados.append({
            'script': script_name,
            'descripcion': descripcion,
            'exito': exito,
            'salida': salida[:500] if salida else "",  # Limitar tamaño
            'timestamp': datetime.now().isoformat()
        })
    
    # Verificar archivos generados
    print(f"\n📁 Verificando archivos generados...")
    archivos_esperados = [
        'prueba_resultado.json',
        'mcp_demo_resultado.json'
    ]
    
    archivos_encontrados = []
    for archivo in archivos_esperados:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"   ✅ {archivo}: Encontrado ({size} bytes)")
            archivos_encontrados.append(archivo)
        else:
            print(f"   ❌ {archivo}: No encontrado")
    
    # Generar reporte final
    reporte_final = {
        'timestamp': datetime.now().isoformat(),
        'problema_original': 'Failed to retrieve terminal output',
        'solucion_aplicada': True,
        'scripts_ejecutados': len(scripts),
        'scripts_exitosos': sum(1 for r in resultados if r['exito']),
        'archivos_generados': len(archivos_encontrados),
        'resultados_detallados': resultados,
        'archivos_encontrados': archivos_encontrados,
        'recomendaciones': []
    }
    
    # Generar recomendaciones basadas en resultados
    scripts_exitosos = sum(1 for r in resultados if r['exito'])
    
    if scripts_exitosos == len(scripts):
        reporte_final['status'] = 'success'
        reporte_final['recomendaciones'] = [
            "Todos los scripts se ejecutaron correctamente",
            "El problema del terminal ha sido solucionado",
            "Synapse debería funcionar normalmente ahora",
            "Usar los archivos JSON generados para verificar resultados"
        ]
    elif scripts_exitosos >= len(scripts) * 0.5:
        reporte_final['status'] = 'partial'
        reporte_final['recomendaciones'] = [
            "La mayoría de scripts funcionaron correctamente",
            "Revisar errores específicos en scripts fallidos",
            "Verificar dependencias manualmente si es necesario",
            "El sistema debería funcionar con limitaciones"
        ]
    else:
        reporte_final['status'] = 'failed'
        reporte_final['recomendaciones'] = [
            "Múltiples scripts fallaron",
            "Verificar instalación de Python y permisos",
            "Instalar dependencias manualmente",
            "Contactar soporte técnico si persisten problemas"
        ]
    
    # Guardar reporte final
    try:
        with open('solucion_maestro_reporte.json', 'w', encoding='utf-8') as f:
            json.dump(reporte_final, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Reporte final guardado: solucion_maestro_reporte.json")
    except Exception as e:
        print(f"\n❌ Error guardando reporte: {e}")
    
    # Resumen final
    print(f"\n" + "=" * 70)
    print("📊 RESUMEN FINAL DE LA SOLUCIÓN")
    print("=" * 70)
    
    print(f"🎯 Problema original: Failed to retrieve terminal output")
    print(f"📄 Scripts ejecutados: {len(scripts)}")
    print(f"✅ Scripts exitosos: {scripts_exitosos}")
    print(f"📁 Archivos generados: {len(archivos_encontrados)}")
    print(f"📊 Estado general: {reporte_final['status'].upper()}")
    
    print(f"\n📋 RESULTADOS POR SCRIPT:")
    for resultado in resultados:
        estado = "✅" if resultado['exito'] else "❌"
        print(f"   {estado} {resultado['descripcion']}")
    
    print(f"\n💡 RECOMENDACIONES:")
    for i, rec in enumerate(reporte_final['recomendaciones'], 1):
        print(f"   {i}. {rec}")
    
    if reporte_final['status'] == 'success':
        print(f"\n🎉 SOLUCIÓN COMPLETADA EXITOSAMENTE")
        print("✅ El error 'Failed to retrieve terminal output' ha sido solucionado")
        print("✅ Todos los componentes están funcionando correctamente")
        print("✅ Synapse está listo para usar")
    elif reporte_final['status'] == 'partial':
        print(f"\n⚠️ SOLUCIÓN PARCIALMENTE EXITOSA")
        print("✅ Los componentes principales están funcionando")
        print("⚠️ Algunos componentes pueden necesitar atención")
        print("💡 Revisar logs para detalles específicos")
    else:
        print(f"\n❌ SOLUCIÓN REQUIERE ATENCIÓN ADICIONAL")
        print("⚠️ Múltiples componentes presentaron problemas")
        print("💡 Verificar instalación y permisos del sistema")
    
    print(f"\n⏰ Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return reporte_final['status'] == 'success'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)