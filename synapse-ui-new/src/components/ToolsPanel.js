import React, { useState } from 'react';
import { useSynapse } from '../contexts/SynapseContext';
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
  Database
} from 'lucide-react';

const ToolsPanel = () => {
  const {
    availableTools,
    activeTools,
    toolExecutions,
    toggleTool,
  } = useSynapse();

  const [filter, setFilter] = useState('all'); // all, active, available, disabled
  const [expandedTool, setExpandedTool] = useState(null);

  const getToolIcon = (toolType) => {
    switch (toolType) {
      case 'code_execution':
        return <Code className="w-5 h-5" />;
      case 'web_browser':
        return <Globe className="w-5 h-5" />;
      case 'file_management':
        return <FileText className="w-5 h-5" />;
      case 'database':
        return <Database className="w-5 h-5" />;
      default:
        return <Wrench className="w-5 h-5" />;
    }
  };

  const getToolStatus = (toolName) => {
    const execution = toolExecutions.find(exec => 
      exec.toolName === toolName && exec.status === 'running'
    );
    
    if (execution) {
      return 'running';
    }
    
    const recentExecution = toolExecutions
      .filter(exec => exec.toolName === toolName)
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
    
    if (recentExecution) {
      return recentExecution.status;
    }
    
    return 'idle';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <Activity className="w-4 h-4 text-warning-600 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-error-600" />;
      default:
        return <Clock className="w-4 h-4 text-secondary-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'border-warning-200 bg-warning-50';
      case 'completed':
        return 'border-success-200 bg-success-50';
      case 'error':
        return 'border-error-200 bg-error-50';
      default:
        return 'border-secondary-200 bg-white';
    }
  };

  const filteredTools = availableTools.filter(tool => {
    switch (filter) {
      case 'active':
        return activeTools.includes(tool.name);
      case 'available':
        return tool.enabled && !activeTools.includes(tool.name);
      case 'disabled':
        return !tool.enabled;
      default:
        return true;
    }
  });

  const getFilterCount = (filterType) => {
    switch (filterType) {
      case 'active':
        return activeTools.length;
      case 'available':
        return availableTools.filter(tool => tool.enabled && !activeTools.includes(tool.name)).length;
      case 'disabled':
        return availableTools.filter(tool => !tool.enabled).length;
      default:
        return availableTools.length;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getToolExecutionHistory = (toolName) => {
    return toolExecutions
      .filter(exec => exec.toolName === toolName)
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 5); // Últimas 5 ejecuciones
  };

  return (
    <div className="h-full bg-white rounded-xl shadow-sm border border-secondary-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <Wrench className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-secondary-900">Herramientas</h2>
              <p className="text-sm text-secondary-600">
                {availableTools.length} herramientas disponibles
              </p>
            </div>
          </div>
          
          <button className="p-2 text-secondary-400 hover:text-secondary-600 rounded-lg hover:bg-secondary-100">
            <Settings className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-1 bg-secondary-100 rounded-lg p-1">
          {[
            { key: 'all', label: 'Todas' },
            { key: 'active', label: 'Activas' },
            { key: 'available', label: 'Disponibles' },
            { key: 'disabled', label: 'Deshabilitadas' },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                filter === key
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              {label}
              <span className="ml-2 px-2 py-0.5 bg-secondary-200 text-secondary-600 text-xs rounded-full">
                {getFilterCount(key)}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Tools List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
        {filteredTools.length === 0 ? (
          <div className="text-center py-8">
            <Wrench className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              No hay herramientas
            </h3>
            <p className="text-secondary-600">
              No se encontraron herramientas para el filtro seleccionado.
            </p>
          </div>
        ) : (
          filteredTools.map((tool) => {
            const status = getToolStatus(tool.name);
            const isExpanded = expandedTool === tool.name;
            const executionHistory = getToolExecutionHistory(tool.name);

            return (
              <div
                key={tool.name}
                className={`border rounded-lg transition-all duration-200 ${getStatusColor(status)}`}
              >
                {/* Tool Header */}
                <div className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        tool.enabled 
                          ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white'
                          : 'bg-secondary-200 text-secondary-500'
                      }`}>
                        {getToolIcon(tool.type)}
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-secondary-900 truncate">
                          {tool.displayName || tool.name}
                        </h4>
                        {getStatusIcon(status)}
                      </div>
                      <p className="text-sm text-secondary-600 mt-1 truncate">
                        {tool.description}
                      </p>
                      
                      {/* Tool Tags */}
                      {tool.tags && tool.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {tool.tags.slice(0, 3).map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 bg-primary-100 text-primary-800 text-xs rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                          {tool.tags.length > 3 && (
                            <span className="text-xs text-secondary-500">
                              +{tool.tags.length - 3} más
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      {/* Enable/Disable Toggle */}
                      <button
                        onClick={() => toggleTool(tool.name, !tool.enabled)}
                        className={`p-2 rounded-lg transition-colors duration-200 ${
                          tool.enabled
                            ? 'text-success-600 hover:bg-success-100'
                            : 'text-secondary-400 hover:bg-secondary-100'
                        }`}
                        title={tool.enabled ? 'Deshabilitar herramienta' : 'Habilitar herramienta'}
                      >
                        {tool.enabled ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                      </button>

                      {/* Expand Button */}
                      <button
                        onClick={() => setExpandedTool(isExpanded ? null : tool.name)}
                        className="p-2 text-secondary-400 hover:text-secondary-600 rounded-lg hover:bg-secondary-100"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Current Execution Info */}
                  {status === 'running' && (
                    <div className="mt-3 p-3 bg-warning-50 border border-warning-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-warning-600" />
                        <span className="text-sm font-medium text-warning-800">
                          Ejecutándose
                        </span>
                      </div>
                      {toolExecutions.find(exec => exec.toolName === tool.name && exec.status === 'running')?.progress && (
                        <div className="mt-2">
                          <div className="w-full bg-warning-200 rounded-full h-2">
                            <div
                              className="bg-warning-600 h-2 rounded-full transition-all duration-300"
                              style={{
                                width: `${toolExecutions.find(exec => exec.toolName === tool.name && exec.status === 'running')?.progress || 0}%`,
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="border-t border-secondary-200 p-4 bg-secondary-50">
                    {/* Tool Details */}
                    <div className="space-y-4">
                      {/* Capabilities */}
                      {tool.capabilities && tool.capabilities.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-secondary-800 mb-2">
                            Capacidades:
                          </h5>
                          <div className="grid grid-cols-2 gap-2">
                            {tool.capabilities.map((capability, index) => (
                              <div
                                key={index}
                                className="text-sm text-secondary-600 bg-white p-2 rounded border"
                              >
                                {capability}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Execution History */}
                      {executionHistory.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-secondary-800 mb-2">
                            Historial de Ejecución:
                          </h5>
                          <div className="space-y-2">
                            {executionHistory.map((execution, index) => (
                              <div
                                key={execution.id}
                                className="flex items-center justify-between p-2 bg-white rounded border text-sm"
                              >
                                <div className="flex items-center space-x-2">
                                  {getStatusIcon(execution.status)}
                                  <span className="text-secondary-700">
                                    {execution.operation || 'Operación'}
                                  </span>
                                </div>
                                <div className="text-secondary-500">
                                  {formatTimestamp(execution.timestamp)}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Tool Configuration */}
                      {tool.configuration && (
                        <div>
                          <h5 className="text-sm font-medium text-secondary-800 mb-2">
                            Configuración:
                          </h5>
                          <div className="bg-white p-3 rounded border">
                            <pre className="text-xs text-secondary-600 whitespace-pre-wrap">
                              {JSON.stringify(tool.configuration, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-secondary-200 bg-secondary-50">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-success-600">
              {availableTools.filter(tool => tool.enabled).length}
            </div>
            <div className="text-xs text-secondary-600">Habilitadas</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-warning-600">
              {activeTools.length}
            </div>
            <div className="text-xs text-secondary-600">Activas</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-primary-600">
              {toolExecutions.filter(exec => exec.status === 'completed').length}
            </div>
            <div className="text-xs text-secondary-600">Completadas</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ToolsPanel;

