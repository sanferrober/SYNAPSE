"""
Herramientas MCP de Upstash para Synapse
Integración de Context7 y Upstash Redis MCP Servers
"""

# Nuevas herramientas MCP de Upstash
upstash_mcp_tools = [
    {
        'id': 'context7_mcp',
        'name': 'Context7 Documentation',
        'description': 'Documentación actualizada y específica por versión en tiempo real',
        'enabled': True,
        'category': 'documentation',
        'server_name': 'context7-mcp-server',
        'type': 'mcp',
        'capabilities': [
            'c7_query',
            'search_projects', 
            'get_project_metadata',
            'get_documentation',
            'version_specific_docs',
            'real_time_updates'
        ],
        'parameters': [
            { 'name': 'project', 'required': True, 'description': 'Nombre del proyecto o framework' },
            { 'name': 'query', 'required': True, 'description': 'Consulta específica sobre documentación' },
            { 'name': 'version', 'required': False, 'description': 'Versión específica del proyecto' }
        ],
        'config': {
            'installation': 'npx -y @upstash/context7-mcp',
            'real_time': True,
            'version_aware': True,
            'source_official': True
        }
    },
    {
        'id': 'upstash_redis_mcp',
        'name': 'Upstash Redis Manager',
        'description': 'Gestión completa de bases de datos Redis de Upstash',
        'enabled': True,
        'category': 'database',
        'server_name': 'upstash-mcp-server',
        'type': 'mcp',
        'capabilities': [
            'redis_database_create',
            'redis_database_list',
            'redis_database_delete',
            'redis_database_update_regions',
            'redis_set',
            'redis_get',
            'redis_del',
            'redis_keys',
            'redis_exists',
            'redis_expire'
        ],
        'parameters': [
            { 'name': 'database_name', 'required': False, 'description': 'Nombre de la base de datos Redis' },
            { 'name': 'region', 'required': False, 'description': 'Región para la base de datos' },
            { 'name': 'key', 'required': False, 'description': 'Clave de Redis' },
            { 'name': 'value', 'required': False, 'description': 'Valor a almacenar' },
            { 'name': 'ttl', 'required': False, 'description': 'Tiempo de vida en segundos' }
        ],
        'config': {
            'installation': 'npx @upstash/mcp-server',
            'requires_auth': True,
            'auth_type': 'api_key',
            'regions': ['us-east-1', 'us-west-1', 'eu-west-1', 'ap-southeast-1']
        }
    },
    {
        'id': 'context7_search_mcp',
        'name': 'Context7 Project Search',
        'description': 'Búsqueda avanzada en proyectos y documentación',
        'enabled': True,
        'category': 'search',
        'server_name': 'context7-mcp-server',
        'type': 'mcp',
        'capabilities': [
            'search_projects',
            'filter_by_language',
            'filter_by_framework',
            'get_trending_projects',
            'get_project_stats',
            'compare_versions'
        ],
        'parameters': [
            { 'name': 'search_term', 'required': True, 'description': 'Término de búsqueda' },
            { 'name': 'language', 'required': False, 'description': 'Lenguaje de programación' },
            { 'name': 'framework', 'required': False, 'description': 'Framework específico' },
            { 'name': 'limit', 'required': False, 'description': 'Número máximo de resultados' }
        ],
        'config': {
            'search_scope': 'global',
            'include_examples': True,
            'include_changelogs': True
        }
    },
    {
        'id': 'upstash_analytics_mcp',
        'name': 'Upstash Analytics',
        'description': 'Análisis y métricas de bases de datos Upstash',
        'enabled': True,
        'category': 'analytics',
        'server_name': 'upstash-mcp-server',
        'type': 'mcp',
        'capabilities': [
            'get_database_metrics',
            'get_usage_stats',
            'get_performance_data',
            'get_billing_info',
            'monitor_connections',
            'analyze_queries'
        ],
        'parameters': [
            { 'name': 'database_id', 'required': True, 'description': 'ID de la base de datos' },
            { 'name': 'metric_type', 'required': True, 'description': 'Tipo de métrica a obtener' },
            { 'name': 'time_range', 'required': False, 'description': 'Rango de tiempo para análisis' }
        ],
        'config': {
            'real_time_metrics': True,
            'historical_data': True,
            'export_formats': ['json', 'csv', 'xlsx']
        }
    }
]

def get_upstash_mcp_tools():
    """Retorna la lista de herramientas MCP de Upstash"""
    return upstash_mcp_tools

def get_upstash_tool_by_id(tool_id):
    """Obtiene una herramienta específica de Upstash por ID"""
    for tool in upstash_mcp_tools:
        if tool['id'] == tool_id:
            return tool
    return None

def get_upstash_tools_by_category(category):
    """Obtiene herramientas de Upstash por categoría"""
    return [tool for tool in upstash_mcp_tools if tool['category'] == category]

def get_context7_tools():
    """Obtiene solo las herramientas relacionadas con Context7"""
    return [tool for tool in upstash_mcp_tools if 'context7' in tool['id']]

def get_redis_tools():
    """Obtiene solo las herramientas relacionadas con Redis"""
    return [tool for tool in upstash_mcp_tools if 'redis' in tool['id']]

