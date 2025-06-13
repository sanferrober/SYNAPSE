import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Settings,
  Eye,
  EyeOff,
  MoreVertical,
  Activity,
  Zap,
  Code,
  Globe,
  FileText,
  Database,
  Server,
  GitBranch,
  Terminal,
  Search,
  Cloud,
  Shield,
  Monitor,
  Cpu,
  HardDrive,
  MessageSquare,
  BarChart3,
  Container,
  Lock
} from 'lucide-react';

const MCPToolsPanel = ({ isVisible, onToggle }) => {
  const [mcpTools, setMcpTools] = useState([]);
  const [mcpServers, setMcpServers] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [mcpStatus, setMcpStatus] = useState(null);
  const [executingTool, setExecutingTool] = useState(null);
  const [toolResults, setToolResults] = useState({});

  // Categorías expandidas de herramientas MCP
  const categories = [
    { id: 'all', name: 'Todas', icon: Wrench, color: 'text-gray-600' },
    { id: 'Search', name: 'Búsqueda', icon: Search, color: 'text-blue-600' },
    { id: 'System', name: 'Sistema', icon: Cpu, color: 'text-green-600' },
    { id: 'Development', name: 'Desarrollo', icon: Code, color: 'text-purple-600' },
    { id: 'Database', name: 'Base de Datos', icon: Database, color: 'text-orange-600' },
    { id: 'Automation', name: 'Automatización', icon: Zap, color: 'text-yellow-600' },
    { id: 'DevOps', name: 'DevOps', icon: Container, color: 'text-indigo-600' },
    { id: 'Cloud', name: 'Nube', icon: Cloud, color: 'text-sky-600' },
    { id: 'Communication', name: 'Comunicación', icon: MessageSquare, color: 'text-pink-600' },
    { id: 'Analysis', name: 'Análisis', icon: BarChart3, color: 'text-emerald-600' },
    { id: 'Security', name: 'Seguridad', icon: Shield, color: 'text-red-600' },
    { id: 'Monitoring', name: 'Monitoreo', icon: Monitor, color: 'text-teal-600' }
  ];

  // Cargar herramientas MCP expandidas al montar el componente
  useEffect(() => {
    loadExpandedMCPTools();
  }, []);

  const loadExpandedMCPTools = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://5000-itcsuhehi0bk40bfz4mii-984c0f23.manus.computer/api/mcp/tools/expanded');
      const data = await response.json();
      
      if (data.mcp_tools) {
        setMcpTools(data.mcp_tools);
        setMcpStatus({
          total: data.total_mcp_tools,
          enabled: data.enabled_tools,
          categories: data.categories.length
        });
        console.log(`🛠️ Cargadas ${data.total_mcp_tools} herramientas MCP expandidas`);
      }
    } catch (error) {
      console.error('❌ Error cargando herramientas MCP:', error);
      setMcpStatus({ error: 'Error de conexión' });
    } finally {
      setLoading(false);
    }
  };

  const executeMCPTool = async (toolId, parameters = {}) => {
    setExecutingTool(toolId);
    try {
      const response = await fetch(`https://5000-itcsuhehi0bk40bfz4mii-984c0f23.manus.computer/api/mcp/tools/${toolId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ parameters })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setToolResults(prev => ({
          ...prev,
          [toolId]: {
            ...result,
            timestamp: new Date().toLocaleTimeString()
          }
        }));
        console.log(`✅ Herramienta ${toolId} ejecutada exitosamente`);
      } else {
        console.error(`❌ Error ejecutando ${toolId}:`, result.error);
      }
      
      return result;
    } catch (error) {
      console.error(`❌ Error ejecutando herramienta ${toolId}:`, error);
      return { success: false, error: error.message };
    } finally {
      setExecutingTool(null);
    }
  };

  // Filtrar herramientas por categoría y búsqueda
  const filteredTools = mcpTools.filter(tool => {
    const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
    const matchesSearch = tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tool.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Obtener icono para categoría
  const getCategoryIcon = (category) => {
    const categoryData = categories.find(cat => cat.id === category);
    return categoryData ? categoryData.icon : Wrench;
  };

  // Obtener color para categoría
  const getCategoryColor = (category) => {
    const categoryData = categories.find(cat => cat.id === category);
    return categoryData ? categoryData.color : 'text-gray-600';
  };

  // Obtener emoji para herramienta
  const getToolEmoji = (tool) => {
    return tool.icon || '🛠️';
  };

  if (!isVisible) return null;

  return (
    <div className="bg-white border-l border-gray-200 w-80 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Wrench className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">Herramientas MCP</h3>
          </div>
          <button
            onClick={onToggle}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <EyeOff className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* Estado MCP */}
        {mcpStatus && (
          <div className="bg-blue-50 rounded-lg p-3 mb-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-blue-700 font-medium">Estado MCP</span>
              <CheckCircle className="w-4 h-4 text-green-500" />
            </div>
            <div className="mt-1 text-xs text-blue-600">
              {mcpStatus.error ? (
                <span className="text-red-600">{mcpStatus.error}</span>
              ) : (
                <>
                  {mcpStatus.enabled}/{mcpStatus.total} herramientas activas
                  <br />
                  {mcpStatus.categories} categorías disponibles
                </>
              )}
            </div>
          </div>
        )}

        {/* Búsqueda */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar herramientas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Categorías */}
      <div className="p-4 border-b border-gray-200">
        <div className="grid grid-cols-2 gap-2">
          {categories.slice(0, 8).map((category) => {
            const Icon = category.icon;
            const isSelected = selectedCategory === category.id;
            const toolCount = category.id === 'all' 
              ? mcpTools.length 
              : mcpTools.filter(t => t.category === category.id).length;

            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center space-x-2 p-2 rounded-lg text-sm transition-colors ${
                  isSelected
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50 text-gray-600'
                }`}
              >
                <Icon className={`w-4 h-4 ${isSelected ? 'text-blue-600' : category.color}`} />
                <span className="font-medium">{category.name}</span>
                <span className="text-xs bg-gray-200 px-1.5 py-0.5 rounded-full">
                  {toolCount}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Lista de herramientas */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {filteredTools.map((tool) => {
              const Icon = getCategoryIcon(tool.category);
              const isExecuting = executingTool === tool.id;
              const hasResult = toolResults[tool.id];

              return (
                <div
                  key={tool.id}
                  className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className="flex-shrink-0">
                        <span className="text-lg">{getToolEmoji(tool)}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900 text-sm truncate">
                            {tool.name}
                          </h4>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            tool.enabled 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {tool.enabled ? 'Activa' : 'Inactiva'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {tool.description}
                        </p>
                        
                        {/* Capacidades */}
                        {tool.capabilities && tool.capabilities.length > 0 && (
                          <div className="mt-2">
                            <div className="flex flex-wrap gap-1">
                              {tool.capabilities.slice(0, 2).map((capability, index) => (
                                <span
                                  key={index}
                                  className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700"
                                >
                                  {capability}
                                </span>
                              ))}
                              {tool.capabilities.length > 2 && (
                                <span className="text-xs text-gray-500">
                                  +{tool.capabilities.length - 2} más
                                </span>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Resultado de ejecución */}
                        {hasResult && (
                          <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                            <div className="flex items-center space-x-1 text-xs text-green-700">
                              <CheckCircle className="w-3 h-3" />
                              <span>Ejecutado a las {hasResult.timestamp}</span>
                            </div>
                            <div className="text-xs text-green-600 mt-1">
                              Tiempo: {hasResult.execution_time}s
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Botón de ejecución */}
                    <div className="flex-shrink-0 ml-2">
                      <button
                        onClick={() => executeMCPTool(tool.id)}
                        disabled={!tool.enabled || isExecuting}
                        className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                          tool.enabled && !isExecuting
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {isExecuting ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                          <Zap className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}

            {filteredTools.length === 0 && !loading && (
              <div className="text-center py-8">
                <Wrench className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">
                  No se encontraron herramientas
                </p>
                <p className="text-gray-400 text-xs mt-1">
                  Intenta cambiar los filtros de búsqueda
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer con estadísticas */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>
            {filteredTools.length} de {mcpTools.length} herramientas
          </span>
          <button
            onClick={loadExpandedMCPTools}
            className="flex items-center space-x-1 hover:text-blue-600 transition-colors"
          >
            <Activity className="w-3 h-3" />
            <span>Actualizar</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MCPToolsPanel;

