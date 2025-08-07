import requests
import json
import os
from datetime import datetime
import time
from typing import Dict, Any, Optional
from .mcp_config_manager import MCPConfigManager

# Inicializar el gestor de configuración
config_manager = MCPConfigManager()

def execute_real_mcp_tool(tool_id: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Ejecuta herramientas MCP reales con gestión inteligente de API keys
    
    Args:
        tool_id: ID de la herramienta a ejecutar
        parameters: Parámetros para la herramienta
    
    Returns:
        Dict con el resultado de la ejecución
    """
    if parameters is None:
        parameters = {}
    
    start_time = time.time()
    
    try:
        # Verificar si es una herramienta gratuita
        if config_manager.is_free_tool(tool_id):
            return _execute_free_tool(tool_id, parameters, start_time)
        
        # Mapeo de herramientas a servicios de API
        tool_to_service = {
            'brave_search_mcp': 'brave_search',
            'tavily_search': 'tavily_search',
            'firecrawl_mcp': 'firecrawl',
            'weather_mcp': 'openweather',
            'news_mcp': 'newsapi'
        }
        
        # Verificar si la herramienta requiere API key
        service = tool_to_service.get(tool_id)
        if service and not config_manager.has_api_key(service):
            # Buscar herramientas alternativas
            fallback_tools = config_manager.get_fallback_tools(tool_id)
            
            for fallback_id in fallback_tools:
                # Intentar con herramienta alternativa
                if config_manager.is_free_tool(fallback_id) or _has_required_key(fallback_id):
                    print(f"🔄 Usando herramienta alternativa: {fallback_id} en lugar de {tool_id}")
                    return execute_real_mcp_tool(fallback_id, parameters)
            
            # Si no hay alternativas disponibles, retornar error informativo
            return _create_api_key_error(tool_id, service, start_time)
        
        # Ejecutar la herramienta con la API key disponible
        return _execute_tool_with_key(tool_id, parameters, start_time)
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'success': False,
            'tool_id': tool_id,
            'error': f'Error ejecutando {tool_id}: {str(e)}',
            'execution_time': round(execution_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def _has_required_key(tool_id: str) -> bool:
    """Verifica si una herramienta tiene la API key requerida"""
    tool_to_service = {
        'brave_search_mcp': 'brave_search',
        'tavily_search': 'tavily_search',
        'firecrawl_mcp': 'firecrawl',
        'weather_mcp': 'openweather',
        'news_mcp': 'newsapi'
    }
    
    service = tool_to_service.get(tool_id)
    return service is None or config_manager.has_api_key(service)

def _execute_free_tool(tool_id: str, parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta herramientas que no requieren API key"""
    if tool_id == 'web_search_mcp' or tool_id == 'duckduckgo_mcp':
        return execute_web_search(parameters, start_time)
    elif tool_id == 'github_mcp':
        return execute_github_search(parameters, start_time)
    elif tool_id == 'wikipedia_mcp':
        return execute_wikipedia_search(parameters, start_time)
    else:
        return {
            'success': False,
            'tool_id': tool_id,
            'error': f'Herramienta gratuita {tool_id} no implementada',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def _execute_tool_with_key(tool_id: str, parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta herramientas que requieren API key"""
    if tool_id == 'brave_search_mcp':
        return execute_brave_search(parameters, start_time)
    elif tool_id == 'tavily_search':
        return execute_tavily_search(parameters, start_time)
    elif tool_id == 'firecrawl_mcp':
        return execute_firecrawl(parameters, start_time)
    elif tool_id == 'weather_mcp':
        return execute_weather_search(parameters, start_time)
    elif tool_id == 'news_mcp':
        return execute_news_search(parameters, start_time)
    else:
        # Para herramientas no implementadas
        return {
            'success': False,
            'tool_id': tool_id,
            'error': f'Herramienta {tool_id} no implementada',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def _create_api_key_error(tool_id: str, service: str, start_time: float) -> Dict[str, Any]:
    """Crea un mensaje de error informativo sobre API keys faltantes"""
    execution_time = time.time() - start_time
    
    error_message = f"❌ No se puede ejecutar {tool_id}: API Key no configurada\n\n"
    error_message += config_manager.get_config_instructions()
    
    return {
        'success': False,
        'tool_id': tool_id,
        'error': error_message,
        'missing_api_key': service,
        'config_file': os.path.abspath(config_manager.config_file),
        'execution_time': round(execution_time, 2),
        'timestamp': datetime.now().isoformat()
    }

def execute_web_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda web usando DuckDuckGo API (gratuita)"""
    query = parameters.get('query', parameters.get('q', 'synapse ai assistant'))
    
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Formatear resultado
        result_text = f"🔍 Resultados de búsqueda para: '{query}'\n\n"
        
        if data.get('Abstract'):
            result_text += f"📝 Resumen: {data['Abstract']}\n"
            if data.get('AbstractURL'):
                result_text += f"🔗 Fuente: {data['AbstractURL']}\n\n"
        
        if data.get('Definition'):
            result_text += f"📖 Definición: {data['Definition']}\n\n"
        
        if data.get('RelatedTopics'):
            result_text += "📌 Temas relacionados:\n"
            for i, topic in enumerate(data['RelatedTopics'][:5], 1):
                if isinstance(topic, dict) and 'Text' in topic:
                    result_text += f"  {i}. {topic['Text']}\n"
                    if 'FirstURL' in topic:
                        result_text += f"     🔗 {topic['FirstURL']}\n"
        
        return {
            'success': True,
            'tool_id': 'web_search_mcp',
            'tool_name': 'DuckDuckGo Web Search',
            'result': result_text,
            'metadata': {
                'query': query,
                'source': 'DuckDuckGo API',
                'results_count': len(data.get('RelatedTopics', [])),
                'has_abstract': bool(data.get('Abstract')),
                'has_definition': bool(data.get('Definition'))
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'web_search_mcp',
            'error': f'Error en búsqueda web: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_github_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda en GitHub (API pública, límite de 60 requests/hora sin token)"""
    query = parameters.get('query', 'synapse')
    language = parameters.get('language', '')
    
    try:
        # Construir query para GitHub
        github_query = query
        if language:
            github_query += f" language:{language}"
        
        url = "https://api.github.com/search/repositories"
        params = {
            'q': github_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 10
        }
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Synapse-MCP-Tool'
        }
        
        # Agregar token si está disponible
        github_token = config_manager.get_api_key('github')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 403:
            return {
                'success': False,
                'tool_id': 'github_mcp',
                'error': 'Límite de rate de GitHub alcanzado. Configura un token para más requests.',
                'execution_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        
        data = response.json()
        
        # Formatear resultado
        result_text = f"🔍 Resultados de GitHub para: '{query}'\n"
        if language:
            result_text += f"📝 Lenguaje: {language}\n"
        result_text += f"📊 Total de resultados: {data.get('total_count', 0)}\n\n"
        
        if data.get('items'):
            result_text += "📦 Repositorios encontrados:\n\n"
            for i, repo in enumerate(data['items'][:10], 1):
                result_text += f"{i}. {repo['full_name']}\n"
                result_text += f"   ⭐ Stars: {repo['stargazers_count']}\n"
                result_text += f"   📝 {repo.get('description', 'Sin descripción')}\n"
                result_text += f"   🔗 {repo['html_url']}\n"
                result_text += f"   📅 Actualizado: {repo['updated_at'][:10]}\n\n"
        else:
            result_text += "No se encontraron repositorios.\n"
        
        return {
            'success': True,
            'tool_id': 'github_mcp',
            'tool_name': 'GitHub Search',
            'result': result_text,
            'metadata': {
                'query': query,
                'language': language,
                'total_results': data.get('total_count', 0),
                'results_shown': len(data.get('items', [])),
                'rate_limit_remaining': response.headers.get('X-RateLimit-Remaining', 'N/A')
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'github_mcp',
            'error': f'Error en búsqueda de GitHub: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_wikipedia_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda en Wikipedia (API gratuita)"""
    query = parameters.get('query', 'artificial intelligence')
    
    try:
        # Búsqueda en Wikipedia
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            'action': 'opensearch',
            'search': query,
            'limit': 5,
            'format': 'json'
        }
        
        response = requests.get(search_url, params=search_params, timeout=10)
        search_data = response.json()
        
        result_text = f"📚 Resultados de Wikipedia para: '{query}'\n\n"
        
        if len(search_data) > 1 and search_data[1]:
            titles = search_data[1]
            descriptions = search_data[2] if len(search_data) > 2 else []
            urls = search_data[3] if len(search_data) > 3 else []
            
            for i, title in enumerate(titles):
                result_text += f"{i+1}. {title}\n"
                if i < len(descriptions) and descriptions[i]:
                    result_text += f"   📝 {descriptions[i]}\n"
                if i < len(urls) and urls[i]:
                    result_text += f"   🔗 {urls[i]}\n"
                result_text += "\n"
        else:
            result_text += "No se encontraron resultados.\n"
        
        return {
            'success': True,
            'tool_id': 'wikipedia_mcp',
            'tool_name': 'Wikipedia Search',
            'result': result_text,
            'metadata': {
                'query': query,
                'results_count': len(search_data[1]) if len(search_data) > 1 else 0
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'wikipedia_mcp',
            'error': f'Error en búsqueda de Wikipedia: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_brave_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda usando Brave Search API"""
    api_key = config_manager.get_api_key('brave_search')
    if not api_key:
        return _create_api_key_error('brave_search_mcp', 'brave_search', start_time)
    
    query = parameters.get('query', parameters.get('q', ''))
    
    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': api_key
        }
        params = {
            'q': query,
            'count': 10
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 401:
            return {
                'success': False,
                'tool_id': 'brave_search_mcp',
                'error': 'API Key de Brave Search inválida',
                'execution_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        
        data = response.json()
        
        # Formatear resultado
        result_text = f"🔍 Resultados de Brave Search para: '{query}'\n\n"
        
        if 'web' in data and 'results' in data['web']:
            for i, result in enumerate(data['web']['results'][:10], 1):
                result_text += f"{i}. {result.get('title', 'Sin título')}\n"
                result_text += f"   📝 {result.get('description', 'Sin descripción')}\n"
                result_text += f"   🔗 {result.get('url', '')}\n\n"
        else:
            result_text += "No se encontraron resultados.\n"
        
        return {
            'success': True,
            'tool_id': 'brave_search_mcp',
            'tool_name': 'Brave Search',
            'result': result_text,
            'metadata': {
                'query': query,
                'results_count': len(data.get('web', {}).get('results', []))
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'brave_search_mcp',
            'error': f'Error en Brave Search: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_tavily_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda usando Tavily API"""
    api_key = config_manager.get_api_key('tavily_search')
    if not api_key:
        return _create_api_key_error('tavily_search', 'tavily_search', start_time)
    
    query = parameters.get('query', '')
    
    try:
        url = "https://api.tavily.com/search"
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            'api_key': api_key,
            'query': query,
            'search_depth': 'basic',
            'max_results': 10
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 401:
            return {
                'success': False,
                'tool_id': 'tavily_search',
                'error': 'API Key de Tavily inválida',
                'execution_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        
        data = response.json()
        
        # Formatear resultado
        result_text = f"🔍 Resultados de Tavily para: '{query}'\n\n"
        
        if 'results' in data:
            for i, result in enumerate(data['results'][:10], 1):
                result_text += f"{i}. {result.get('title', 'Sin título')}\n"
                result_text += f"   📝 {result.get('content', 'Sin contenido')[:200]}...\n"
                result_text += f"   🔗 {result.get('url', '')}\n"
                result_text += f"   📊 Relevancia: {result.get('score', 0):.2f}\n\n"
        else:
            result_text += "No se encontraron resultados.\n"
        
        return {
            'success': True,
            'tool_id': 'tavily_search',
            'tool_name': 'Tavily Search',
            'result': result_text,
            'metadata': {
                'query': query,
                'results_count': len(data.get('results', []))
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'tavily_search',
            'error': f'Error en Tavily Search: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_firecrawl(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta web scraping usando Firecrawl API"""
    api_key = config_manager.get_api_key('firecrawl')
    if not api_key:
        return _create_api_key_error('firecrawl_mcp', 'firecrawl', start_time)
    
    url = parameters.get('url', '')
    
    if not url:
        return {
            'success': False,
            'tool_id': 'firecrawl_mcp',
            'error': 'URL requerida para Firecrawl',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    try:
        api_url = "https://api.firecrawl.dev/v0/scrape"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'url': url,
            'pageOptions': {
                'onlyMainContent': True
            }
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 401:
            return {
                'success': False,
                'tool_id': 'firecrawl_mcp',
                'error': 'API Key de Firecrawl inválida',
                'execution_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        
        data = response.json()
        
        # Formatear resultado
        result_text = f"🌐 Contenido extraído de: {url}\n\n"
        
        if data.get('success') and data.get('data'):
            content = data['data'].get('content', '')
            result_text += content[:1000] + "..." if len(content) > 1000 else content
        else:
            result_text += "No se pudo extraer contenido de la página.\n"
        
        return {
            'success': True,
            'tool_id': 'firecrawl_mcp',
            'tool_name': 'Firecrawl Web Scraper',
            'result': result_text,
            'metadata': {
                'url': url,
                'content_length': len(data.get('data', {}).get('content', ''))
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'firecrawl_mcp',
            'error': f'Error en Firecrawl: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_weather_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda de clima usando OpenWeather API"""
    api_key = config_manager.get_api_key('openweather')
    if not api_key:
        return _create_api_key_error('weather_mcp', 'openweather', start_time)
    
    city = parameters.get('city', 'London')
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',
            'lang': 'es'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 401:
            return {
                'success': False,
                'tool_id': 'weather_mcp',
                'error': 'API Key de OpenWeather inválida',
                'execution_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        
        data = response.json()
        
        # Formatear resultado
        result_text = f"🌤️ Clima en {data.get('name', city)}, {data.get('sys', {}).get('country', '')}\n\n"
        result_text += f"🌡️ Temperatura: {data.get('main', {}).get('temp', 'N/A')}°C\n"
        result_text += f"🤔 Sensación térmica: {data.get('main', {}).get('feels_like', 'N/A')}°C\n"
        result_text += f"☁️ Condición: {data.get('weather', [{}])[0].get('description', 'N/A')}\n"
        result_text += f"💧 Humedad: {data.get('main', {}).get('humidity', 'N/A')}%\n"
        result_text += f"💨 Viento: {data.get('wind', {}).get('speed', 'N/A')} m/s\n"
        
        return {
            'success': True,
            'tool_id': 'weather_mcp',
            'tool_name': 'OpenWeather',
            'result': result_text,
            'metadata': {
                'city': city,
                'temperature': data.get('main', {}).get('temp'),
                'condition': data.get('weather', [{}])[0].get('main')
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'weather_mcp',
            'error': f'Error en búsqueda de clima: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

def execute_news_search(parameters: Dict, start_time: float) -> Dict[str, Any]:
    """Ejecuta búsqueda de noticias usando NewsAPI"""
    api_key = config_manager.get_api_key('newsapi')
    if not api_key:
        return _create_api_key_error('news_mcp', 'newsapi', start_time)
    
    query = parameters.get('query', 'technology')
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': api_key,
            'sortBy': 'relevancy',
            'pageSize': 10,
            'language': 'es'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 401:
            return {
                'success': False,
                'tool_id': 'news_mcp',
                'error': 'API Key de NewsAPI inválida',
                'execution_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        
        data = response.json()
        
        # Formatear resultado
        result_text = f"📰 Noticias sobre: '{query}'\n\n"
        
        if data.get('articles'):
            for i, article in enumerate(data['articles'][:10], 1):
                result_text += f"{i}. {article.get('title', 'Sin título')}\n"
                result_text += f"   📅 {article.get('publishedAt', '')[:10]}\n"
                result_text += f"   📝 {article.get('description', 'Sin descripción')[:150]}...\n"
                result_text += f"   🔗 {article.get('url', '')}\n"
                result_text += f"   📰 Fuente: {article.get('source', {}).get('name', 'Desconocida')}\n\n"
        else:
            result_text += "No se encontraron noticias.\n"
        
        return {
            'success': True,
            'tool_id': 'news_mcp',
            'tool_name': 'NewsAPI',
            'result': result_text,
            'metadata': {
                'query': query,
                'total_results': data.get('totalResults', 0),
                'results_shown': len(data.get('articles', []))
            },
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'tool_id': 'news_mcp',
            'error': f'Error en búsqueda de noticias: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }