import React, { useState, useEffect } from 'react';
import { Key, Check, X, AlertCircle, ExternalLink, Save, RefreshCw } from 'lucide-react';

const MCPConfigPanel = () => {
  const [configStatus, setConfigStatus] = useState({});
  const [missingKeys, setMissingKeys] = useState({});
  const [freeTools, setFreeTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [apiKeys, setApiKeys] = useState({});
  const [showKeys, setShowKeys] = useState({});
  const [testResults, setTestResults] = useState({});

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/mcp/config');
      const data = await response.json();
      
      if (data.success) {
        setConfigStatus(data.config_status);
        setMissingKeys(data.missing_keys);
        setFreeTools(data.free_tools);
        
        // Inicializar campos de API keys vacíos
        const keys = {};
        Object.keys(data.config_status).forEach(service => {
          keys[service] = '';
        });
        setApiKeys(keys);
      }
    } catch (error) {
      console.error('Error loading MCP config:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveApiKey = async (service) => {
    try {
      setSaving({ ...saving, [service]: true });
      
      const response = await fetch('/api/mcp/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service: service,
          api_key: apiKeys[service]
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Recargar configuración
        await loadConfig();
        // Limpiar el campo
        setApiKeys({ ...apiKeys, [service]: '' });
        alert(`API Key para ${service} guardada exitosamente`);
      } else {
        alert(`Error al guardar API Key: ${data.error}`);
      }
    } catch (error) {
      console.error('Error saving API key:', error);
      alert('Error al guardar API Key');
    } finally {
      setSaving({ ...saving, [service]: false });
    }
  };

  const testTool = async (toolId) => {
    try {
      setTestResults({ ...testResults, [toolId]: { loading: true } });
      
      const testParams = {
        'brave_search_mcp': { query: 'test search' },
        'tavily_search': { query: 'test search' },
        'weather_mcp': { city: 'Madrid' },
        'news_mcp': { query: 'technology' },
        'firecrawl_mcp': { url: 'https://example.com' },
        'github_mcp': { query: 'react' }
      };
      
      const response = await fetch(`/api/mcp/test/${toolId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testParams[toolId] || {})
      });
      
      const data = await response.json();
      
      setTestResults({
        ...testResults,
        [toolId]: {
          loading: false,
          success: data.success,
          message: data.success ? 'Herramienta funcionando correctamente' : data.error
        }
      });
    } catch (error) {
      setTestResults({
        ...testResults,
        [toolId]: {
          loading: false,
          success: false,
          message: 'Error al probar la herramienta'
        }
      });
    }
  };

  const getServiceInfo = (service) => {
    const serviceMap = {
      'brave_search': {
        name: 'Brave Search',
        tool: 'brave_search_mcp',
        url: 'https://brave.com/search/api/'
      },
      'tavily_search': {
        name: 'Tavily Search',
        tool: 'tavily_search',
        url: 'https://tavily.com/'
      },
      'firecrawl': {
        name: 'Firecrawl',
        tool: 'firecrawl_mcp',
        url: 'https://firecrawl.dev/'
      },
      'github': {
        name: 'GitHub',
        tool: 'github_mcp',
        url: 'https://github.com/settings/tokens'
      },
      'openweather': {
        name: 'OpenWeather',
        tool: 'weather_mcp',
        url: 'https://openweathermap.org/api'
      },
      'newsapi': {
        name: 'NewsAPI',
        tool: 'news_mcp',
        url: 'https://newsapi.org/'
      }
    };
    
    return serviceMap[service] || { name: service, tool: service, url: '#' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2 flex items-center">
          <Key className="w-6 h-6 mr-2" />
          Configuración de API Keys para Herramientas MCP
        </h2>
        <p className="text-gray-600">
          Configura las API Keys necesarias para habilitar todas las herramientas MCP.
        </p>
      </div>

      {/* Herramientas Gratuitas */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-3 text-green-700">
          🆓 Herramientas Gratuitas (No requieren API Key)
        </h3>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex flex-wrap gap-2">
            {freeTools.map(tool => (
              <span key={tool} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                {tool}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Herramientas que requieren API Key */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-blue-700">
          🔑 Herramientas que Requieren API Key
        </h3>
        
        <div className="space-y-4">
          {Object.entries(configStatus).map(([service, status]) => {
            const info = getServiceInfo(service);
            const testResult = testResults[info.tool];
            
            return (
              <div key={service} className="border rounded-lg p-4 bg-white shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-lg flex items-center">
                      {status.configured ? (
                        <Check className="w-5 h-5 text-green-500 mr-2" />
                      ) : (
                        <X className="w-5 h-5 text-red-500 mr-2" />
                      )}
                      {info.name}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">{status.description}</p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {status.configured && (
                      <button
                        onClick={() => testTool(info.tool)}
                        disabled={testResult?.loading}
                        className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                      >
                        {testResult?.loading ? 'Probando...' : 'Probar'}
                      </button>
                    )}
                    
                    <a
                      href={info.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:text-blue-700"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>

                {testResult && !testResult.loading && (
                  <div className={`mb-3 p-2 rounded text-sm ${
                    testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {testResult.message}
                  </div>
                )}

                {!status.configured && (
                  <div className="mt-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type={showKeys[service] ? 'text' : 'password'}
                        value={apiKeys[service] || ''}
                        onChange={(e) => setApiKeys({ ...apiKeys, [service]: e.target.value })}
                        placeholder="Ingresa tu API Key"
                        className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      
                      <button
                        onClick={() => setShowKeys({ ...showKeys, [service]: !showKeys[service] })}
                        className="px-3 py-2 text-gray-600 hover:text-gray-800"
                      >
                        {showKeys[service] ? '👁️' : '👁️‍🗨️'}
                      </button>
                      
                      <button
                        onClick={() => saveApiKey(service)}
                        disabled={!apiKeys[service] || saving[service]}
                        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 flex items-center"
                      >
                        <Save className="w-4 h-4 mr-1" />
                        {saving[service] ? 'Guardando...' : 'Guardar'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Información adicional */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">Información Importante:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Las API Keys se guardan de forma segura en el servidor</li>
              <li>También puedes configurar las API Keys usando variables de entorno</li>
              <li>Las herramientas gratuitas tienen límites de uso (ej: GitHub 60 req/hora sin token)</li>
              <li>Si una herramienta con API Key no está disponible, se usará una alternativa gratuita si existe</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MCPConfigPanel;