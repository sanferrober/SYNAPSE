#!/usr/bin/env python3
"""
Script de prueba para herramientas MCP reales
Verifica que las implementaciones reales funcionan correctamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_integration'))

from real_mcp_tools import execute_real_mcp_tool
import json

def test_real_mcp_tools():
    """Prueba las herramientas MCP reales"""
    
    print("🧪 PRUEBAS DE HERRAMIENTAS MCP REALES")
    print("=" * 50)
    
    # Lista de herramientas a probar
    test_cases = [
        {
            'tool_id': 'web_search_mcp',
            'parameters': {'query': 'python machine learning'},
            'description': 'Búsqueda web con DuckDuckGo'
        },
        {
            'tool_id': 'github_mcp',
            'parameters': {'query': 'react components', 'sort': 'stars'},
            'description': 'Búsqueda en GitHub'
        },
        {
            'tool_id': 'brave_search_mcp',
            'parameters': {'query': 'artificial intelligence 2024', 'count': 5},
            'description': 'Búsqueda con Brave (simulada)'
        },
        {
            'tool_id': 'tavily_search',
            'parameters': {'query': 'docker containers best practices'},
            'description': 'Búsqueda con Tavily (simulada)'
        },
        {
            'tool_id': 'filesystem_mcp',
            'parameters': {'action': 'list', 'path': '/tmp'},
            'description': 'Operaciones de sistema de archivos (simulada)'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔧 PRUEBA {i}: {test_case['description']}")
        print(f"   Herramienta: {test_case['tool_id']}")
        print(f"   Parámetros: {test_case['parameters']}")
        print("-" * 40)
        
        try:
            result = execute_real_mcp_tool(test_case['tool_id'], test_case['parameters'])
            
            if result['success']:
                print(f"✅ ÉXITO - Tiempo: {result['execution_time']}s")
                print(f"📊 Resultado (primeros 200 chars):")
                print(f"   {result['result'][:200]}...")
                
                results.append({
                    'test': i,
                    'tool_id': test_case['tool_id'],
                    'success': True,
                    'execution_time': result['execution_time'],
                    'result_length': len(result['result'])
                })
            else:
                print(f"❌ ERROR: {result.get('error', 'Error desconocido')}")
                results.append({
                    'test': i,
                    'tool_id': test_case['tool_id'],
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                })
                
        except Exception as e:
            print(f"💥 EXCEPCIÓN: {str(e)}")
            results.append({
                'test': i,
                'tool_id': test_case['tool_id'],
                'success': False,
                'error': f'Excepción: {str(e)}'
            })
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Exitosas: {successful}/{total}")
    print(f"❌ Fallidas: {total - successful}/{total}")
    print(f"📈 Tasa de éxito: {(successful/total)*100:.1f}%")
    
    print("\n🔍 DETALLES POR HERRAMIENTA:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        tool_name = result['tool_id'].replace('_mcp', '').replace('_', ' ').title()
        
        if result['success']:
            print(f"{status} {tool_name}: {result['execution_time']}s - {result['result_length']} chars")
        else:
            print(f"{status} {tool_name}: {result['error']}")
    
    # Guardar resultados detallados
    with open('test_real_mcp_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': '2024-01-15T10:30:00',
            'total_tests': total,
            'successful_tests': successful,
            'success_rate': (successful/total)*100,
            'detailed_results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: test_real_mcp_results.json")
    
    return successful == total

def test_specific_tool(tool_id, parameters=None):
    """Prueba una herramienta específica"""
    
    print(f"🔧 PRUEBA ESPECÍFICA: {tool_id}")
    print("=" * 40)
    
    if parameters is None:
        parameters = {'query': 'test query'}
    
    try:
        result = execute_real_mcp_tool(tool_id, parameters)
        
        print(f"📊 Resultado completo:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result['success']
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Prueba específica
        tool_id = sys.argv[1]
        parameters = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
        test_specific_tool(tool_id, parameters)
    else:
        # Prueba completa
        success = test_real_mcp_tools()
        sys.exit(0 if success else 1)