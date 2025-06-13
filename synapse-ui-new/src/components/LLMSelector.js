import React, { useState, useEffect } from 'react';
import { useSynapse } from '../contexts/SynapseContext';
import { 
  Settings, 
  Brain, 
  Cpu, 
  Zap, 
  Target, 
  MessageSquare,
  Search,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';

const LLMSelector = () => {
  const { socket } = useSynapse();
  const [llmConfig, setLlmConfig] = useState({
    conversation_agent: 'gpt-4',
    planning_agent: 'gpt-4',
    execution_agent: 'gpt-3.5-turbo',
    analysis_agent: 'gpt-4',
    memory_agent: 'gpt-3.5-turbo',
    optimization_agent: 'claude-3-sonnet'
  });
  
  const [availableLLMs, setAvailableLLMs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});

  // Definición de agentes internos de Synapse
  const agents = [
    {
      id: 'conversation_agent',
      name: 'Agente de Conversación',
      description: 'Maneja la interacción con el usuario y comprensión de tareas',
      icon: MessageSquare,
      color: 'text-blue-500',
      recommended: ['gpt-4', 'claude-3-opus', 'gemini-pro']
    },
    {
      id: 'planning_agent',
      name: 'Agente de Planificación',
      description: 'Genera y estructura planes de ejecución detallados',
      icon: Target,
      color: 'text-green-500',
      recommended: ['gpt-4', 'claude-3-sonnet', 'gemini-pro']
    },
    {
      id: 'execution_agent',
      name: 'Agente de Ejecución',
      description: 'Ejecuta pasos del plan y coordina herramientas',
      icon: Zap,
      color: 'text-yellow-500',
      recommended: ['gpt-3.5-turbo', 'claude-3-haiku', 'gemini-flash']
    },
    {
      id: 'analysis_agent',
      name: 'Agente de Análisis',
      description: 'Analiza resultados y determina expansiones dinámicas',
      icon: Search,
      color: 'text-purple-500',
      recommended: ['gpt-4', 'claude-3-sonnet', 'gemini-pro']
    },
    {
      id: 'memory_agent',
      name: 'Agente de Memoria',
      description: 'Gestiona contexto persistente y recuperación de información',
      icon: Brain,
      color: 'text-indigo-500',
      recommended: ['gpt-3.5-turbo', 'claude-3-haiku', 'gemini-flash']
    },
    {
      id: 'optimization_agent',
      name: 'Agente de Optimización',
      description: 'Optimiza rendimiento y sugiere mejoras del sistema',
      icon: Cpu,
      color: 'text-red-500',
      recommended: ['claude-3-sonnet', 'gpt-4', 'gemini-pro']
    }
  ];

  // LLMs disponibles con sus características
  const llmOptions = [
    {
      id: 'gpt-4',
      name: 'GPT-4',
      provider: 'OpenAI',
      tier: 'premium',
      strengths: ['Razonamiento complejo', 'Análisis profundo', 'Creatividad'],
      cost: 'Alto',
      speed: 'Medio'
    },
    {
      id: 'gpt-3.5-turbo',
      name: 'GPT-3.5 Turbo',
      provider: 'OpenAI',
      tier: 'standard',
      strengths: ['Velocidad', 'Eficiencia', 'Costo-efectivo'],
      cost: 'Bajo',
      speed: 'Rápido'
    },
    {
      id: 'claude-3-opus',
      name: 'Claude 3 Opus',
      provider: 'Anthropic',
      tier: 'premium',
      strengths: ['Análisis detallado', 'Seguridad', 'Precisión'],
      cost: 'Alto',
      speed: 'Medio'
    },
    {
      id: 'claude-3-sonnet',
      name: 'Claude 3 Sonnet',
      provider: 'Anthropic',
      tier: 'standard',
      strengths: ['Balance', 'Versatilidad', 'Confiabilidad'],
      cost: 'Medio',
      speed: 'Medio'
    },
    {
      id: 'claude-3-haiku',
      name: 'Claude 3 Haiku',
      provider: 'Anthropic',
      tier: 'fast',
      strengths: ['Velocidad', 'Eficiencia', 'Respuestas rápidas'],
      cost: 'Bajo',
      speed: 'Muy Rápido'
    },
    {
      id: 'gemini-pro',
      name: 'Gemini Pro',
      provider: 'Google',
      tier: 'standard',
      strengths: ['Multimodal', 'Análisis de código', 'Integración'],
      cost: 'Medio',
      speed: 'Rápido'
    },
    {
      id: 'gemini-flash',
      name: 'Gemini Flash',
      provider: 'Google',
      tier: 'fast',
      strengths: ['Velocidad extrema', 'Bajo costo', 'Eficiencia'],
      cost: 'Muy Bajo',
      speed: 'Muy Rápido'
    }
  ];

  useEffect(() => {
    // Cargar configuración actual desde el servidor
    loadCurrentConfig();
    setAvailableLLMs(llmOptions);
  }, []);

  const loadCurrentConfig = async () => {
    if (socket) {
      socket.emit('get_llm_config');
      socket.on('llm_config_response', (config) => {
        setLlmConfig(config);
      });
    }
  };

  const handleLLMChange = (agentId, llmId) => {
    setLlmConfig(prev => ({
      ...prev,
      [agentId]: llmId
    }));
  };

  const saveConfiguration = async () => {
    setLoading(true);
    try {
      if (socket) {
        socket.emit('update_llm_config', llmConfig);
        socket.on('llm_config_updated', (response) => {
          if (response.success) {
            alert('✅ Configuración de LLMs actualizada correctamente');
          } else {
            alert('❌ Error al actualizar configuración: ' + response.error);
          }
          setLoading(false);
        });
      }
    } catch (error) {
      console.error('Error saving LLM configuration:', error);
      alert('❌ Error al guardar configuración');
      setLoading(false);
    }
  };

  const testLLMConnection = async (llmId) => {
    setTestResults(prev => ({ ...prev, [llmId]: 'testing' }));
    
    try {
      if (socket) {
        socket.emit('test_llm_connection', { llm_id: llmId });
        socket.on('llm_test_result', (result) => {
          setTestResults(prev => ({
            ...prev,
            [result.llm_id]: result.success ? 'success' : 'error'
          }));
        });
      }
    } catch (error) {
      setTestResults(prev => ({ ...prev, [llmId]: 'error' }));
    }
  };

  const resetToDefaults = () => {
    const defaultConfig = {
      conversation_agent: 'gpt-4',
      planning_agent: 'gpt-4',
      execution_agent: 'gpt-3.5-turbo',
      analysis_agent: 'gpt-4',
      memory_agent: 'gpt-3.5-turbo',
      optimization_agent: 'claude-3-sonnet'
    };
    setLlmConfig(defaultConfig);
  };

  const getLLMInfo = (llmId) => {
    return llmOptions.find(llm => llm.id === llmId) || {};
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'premium': return 'text-yellow-500 bg-yellow-50';
      case 'standard': return 'text-blue-500 bg-blue-50';
      case 'fast': return 'text-green-500 bg-green-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  const getTestIcon = (status) => {
    switch (status) {
      case 'testing': return <Loader className="w-4 h-4 animate-spin text-blue-500" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return null;
    }
  };

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Settings className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Configuración de LLMs
              </h2>
              <p className="text-sm text-gray-600">
                Selecciona los modelos para cada agente interno
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={resetToDefaults}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              Restaurar Defaults
            </button>
            <button
              onClick={saveConfiguration}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
            >
              {loading && <Loader className="w-4 h-4 animate-spin" />}
              <span>Guardar Configuración</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-6">
          {agents.map((agent) => {
            const IconComponent = agent.icon;
            const currentLLM = getLLMInfo(llmConfig[agent.id]);
            
            return (
              <div key={agent.id} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <IconComponent className={`w-6 h-6 ${agent.color}`} />
                    <div>
                      <h3 className="font-medium text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-600">{agent.description}</p>
                    </div>
                  </div>
                  {currentLLM.tier && (
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTierColor(currentLLM.tier)}`}>
                      {currentLLM.tier.toUpperCase()}
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Selector de LLM */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Modelo Seleccionado
                    </label>
                    <select
                      value={llmConfig[agent.id]}
                      onChange={(e) => handleLLMChange(agent.id, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {llmOptions.map((llm) => (
                        <option key={llm.id} value={llm.id}>
                          {llm.name} ({llm.provider}) - {llm.cost} costo, {llm.speed} velocidad
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Información del LLM actual */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Características
                    </label>
                    <div className="bg-white rounded-md p-3 border">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900">{currentLLM.name}</span>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => testLLMConnection(llmConfig[agent.id])}
                            className="text-xs text-blue-600 hover:text-blue-800"
                          >
                            Probar
                          </button>
                          {getTestIcon(testResults[llmConfig[agent.id]])}
                        </div>
                      </div>
                      <div className="text-sm text-gray-600">
                        <div className="flex justify-between">
                          <span>Proveedor:</span>
                          <span>{currentLLM.provider}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Costo:</span>
                          <span>{currentLLM.cost}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Velocidad:</span>
                          <span>{currentLLM.speed}</span>
                        </div>
                      </div>
                      {currentLLM.strengths && (
                        <div className="mt-2">
                          <div className="text-xs text-gray-500 mb-1">Fortalezas:</div>
                          <div className="flex flex-wrap gap-1">
                            {currentLLM.strengths.map((strength, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full"
                              >
                                {strength}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Recomendaciones */}
                <div className="mt-3">
                  <div className="text-xs text-gray-500 mb-1">Modelos recomendados para este agente:</div>
                  <div className="flex flex-wrap gap-2">
                    {agent.recommended.map((recLLM) => {
                      const isSelected = llmConfig[agent.id] === recLLM;
                      return (
                        <button
                          key={recLLM}
                          onClick={() => handleLLMChange(agent.id, recLLM)}
                          className={`px-2 py-1 text-xs rounded-md transition-colors ${
                            isSelected
                              ? 'bg-green-100 text-green-700 border border-green-300'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                        >
                          {getLLMInfo(recLLM).name || recLLM}
                          {isSelected && ' ✓'}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Resumen de configuración */}
        <div className="mt-8 bg-blue-50 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-3">Resumen de Configuración</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
            {agents.map((agent) => {
              const currentLLM = getLLMInfo(llmConfig[agent.id]);
              return (
                <div key={agent.id} className="flex justify-between">
                  <span className="text-blue-700">{agent.name}:</span>
                  <span className="font-medium text-blue-900">{currentLLM.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMSelector;