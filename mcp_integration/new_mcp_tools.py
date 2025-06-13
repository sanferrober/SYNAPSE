"""
Nuevas herramientas MCP para Synapse
Integración de herramientas MCP adicionales gratuitas
"""

# Nuevas herramientas MCP identificadas
new_mcp_tools = [
    {
        'id': 'github_mcp',
        'name': 'GitHub Integration',
        'description': 'Gestión completa de repositorios GitHub',
        'enabled': True,
        'category': 'development',
        'capabilities': [
            'create_repository',
            'manage_issues',
            'pull_requests',
            'code_review',
            'repository_search'
        ],
        'server_type': 'github-mcp-server',
        'config': {
            'requires_auth': True,
            'auth_type': 'token'
        }
    },
    {
        'id': 'filesystem_mcp',
        'name': 'File System Access',
        'description': 'Acceso y gestión de archivos locales',
        'enabled': True,
        'category': 'system',
        'capabilities': [
            'read_files',
            'write_files',
            'list_directories',
            'file_search',
            'file_operations'
        ],
        'server_type': 'filesystem-mcp-server',
        'config': {
            'safe_mode': True,
            'allowed_paths': ['/tmp', '/home/user/projects']
        }
    },
    {
        'id': 'brave_search_mcp',
        'name': 'Brave Search',
        'description': 'Búsqueda web y local con Brave API',
        'enabled': True,
        'category': 'research',
        'capabilities': [
            'web_search',
            'local_search',
            'image_search',
            'news_search',
            'academic_search'
        ],
        'server_type': 'brave-search-mcp-server',
        'config': {
            'api_key_required': True,
            'rate_limit': '1000/day'
        }
    },
    {
        'id': 'playwright_mcp',
        'name': 'Web Automation',
        'description': 'Automatización de navegadores con Playwright',
        'enabled': True,
        'category': 'automation',
        'capabilities': [
            'browser_automation',
            'web_scraping',
            'form_filling',
            'screenshot_capture',
            'page_interaction'
        ],
        'server_type': 'playwright-mcp-server',
        'config': {
            'headless': True,
            'timeout': 30000
        }
    },
    {
        'id': 'database_mcp',
        'name': 'Database Tools',
        'description': 'Herramientas para múltiples bases de datos',
        'enabled': True,
        'category': 'data',
        'capabilities': [
            'sql_queries',
            'schema_analysis',
            'data_export',
            'database_backup',
            'performance_monitoring'
        ],
        'server_type': 'database-mcp-server',
        'config': {
            'supported_dbs': ['postgresql', 'mysql', 'sqlite', 'mongodb'],
            'connection_pooling': True
        }
    },
    {
        'id': 'jupyter_mcp',
        'name': 'Jupyter Notebooks',
        'description': 'Integración con notebooks Jupyter',
        'enabled': True,
        'category': 'analysis',
        'capabilities': [
            'notebook_execution',
            'cell_management',
            'data_visualization',
            'kernel_management',
            'export_formats'
        ],
        'server_type': 'jupyter-mcp-server',
        'config': {
            'kernel_timeout': 300,
            'max_output_size': '10MB'
        }
    },
    {
        'id': 'firecrawl_mcp',
        'name': 'Web Scraping',
        'description': 'Web scraping avanzado con Firecrawl',
        'enabled': True,
        'category': 'data_extraction',
        'capabilities': [
            'website_crawling',
            'content_extraction',
            'structured_data',
            'pdf_processing',
            'dynamic_content'
        ],
        'server_type': 'firecrawl-mcp-server',
        'config': {
            'respect_robots_txt': True,
            'rate_limit': '10/second'
        }
    },
    {
        'id': 'meilisearch_mcp',
        'name': 'Search Engine',
        'description': 'Motor de búsqueda con Meilisearch',
        'enabled': True,
        'category': 'search',
        'capabilities': [
            'full_text_search',
            'faceted_search',
            'typo_tolerance',
            'instant_search',
            'search_analytics'
        ],
        'server_type': 'meilisearch-mcp-server',
        'config': {
            'index_management': True,
            'search_timeout': 5000
        }
    }
]

def get_new_mcp_tools():
    """Retorna la lista de nuevas herramientas MCP"""
    return new_mcp_tools

def get_tool_by_id(tool_id):
    """Obtiene una herramienta específica por ID"""
    for tool in new_mcp_tools:
        if tool['id'] == tool_id:
            return tool
    return None

def get_tools_by_category(category):
    """Obtiene herramientas por categoría"""
    return [tool for tool in new_mcp_tools if tool['category'] == category]

def get_enabled_tools():
    """Obtiene solo las herramientas habilitadas"""
    return [tool for tool in new_mcp_tools if tool['enabled']]

