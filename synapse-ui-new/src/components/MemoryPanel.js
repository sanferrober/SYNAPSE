import React, { useState } from 'react';
import { useSynapse } from '../contexts/SynapseContext';
import { 
  Brain, 
  Clock, 
  Star, 
  MessageSquare, 
  TrendingUp, 
  User, 
  Search,
  Filter,
  ChevronRight,
  ChevronDown,
  Calendar,
  Tag,
  Lightbulb,
  Archive,
  Heart
} from 'lucide-react';

const MemoryPanel = () => {
  const {
    shortTermMemory,
    relevantMemories,
    userPreferences,
    provideFeedback,
  } = useSynapse();

  const [activeTab, setActiveTab] = useState('context'); // context, memories, preferences
  const [searchQuery, setSearchQuery] = useState('');
  const [memoryFilter, setMemoryFilter] = useState('all'); // all, episodic, semantic, procedural
  const [expandedMemory, setExpandedMemory] = useState(null);

  const getMemoryIcon = (type) => {
    switch (type) {
      case 'episodic':
        return <MessageSquare className="w-4 h-4" />;
      case 'semantic':
        return <Lightbulb className="w-4 h-4" />;
      case 'procedural':
        return <TrendingUp className="w-4 h-4" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  };

  const getMemoryTypeColor = (type) => {
    switch (type) {
      case 'episodic':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'semantic':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'procedural':
        return 'text-purple-600 bg-purple-50 border-purple-200';
      default:
        return 'text-secondary-600 bg-secondary-50 border-secondary-200';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Hace unos minutos';
    } else if (diffInHours < 24) {
      return `Hace ${Math.floor(diffInHours)} horas`;
    } else if (diffInHours < 168) {
      return `Hace ${Math.floor(diffInHours / 24)} días`;
    } else {
      return date.toLocaleDateString('es-ES');
    }
  };

  const filteredMemories = relevantMemories.filter(memory => {
    const matchesSearch = !searchQuery || 
      memory.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memory.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesFilter = memoryFilter === 'all' || memory.type === memoryFilter;
    
    return matchesSearch && matchesFilter;
  });

  const handleFeedback = (memoryId, rating, comment) => {
    provideFeedback({
      type: 'memory_relevance',
      memoryId,
      rating,
      comment,
      timestamp: new Date().toISOString(),
    });
  };

  return (
    <div className="h-full bg-white rounded-xl shadow-sm border border-secondary-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-secondary-900">Memoria y Contexto</h2>
              <p className="text-sm text-secondary-600">
                Información relevante y preferencias
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-secondary-100 rounded-lg p-1">
          {[
            { key: 'context', label: 'Contexto Actual', icon: Clock },
            { key: 'memories', label: 'Memorias', icon: Archive },
            { key: 'preferences', label: 'Preferencias', icon: User },
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                activeTab === key
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {/* Context Tab */}
        {activeTab === 'context' && (
          <div className="h-full overflow-y-auto p-4 space-y-4 scrollbar-thin">
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-secondary-800 flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>Contexto de la Sesión Actual</span>
              </h3>
              
              {shortTermMemory.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                  <p className="text-secondary-600">
                    No hay información contextual disponible
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {shortTermMemory.map((item, index) => (
                    <div
                      key={index}
                      className="p-3 bg-secondary-50 border border-secondary-200 rounded-lg"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-1">
                          {getMemoryIcon(item.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-secondary-900">
                            {item.title || 'Información Contextual'}
                          </h4>
                          <p className="text-sm text-secondary-700 mt-1">
                            {item.content}
                          </p>
                          {item.timestamp && (
                            <p className="text-xs text-secondary-500 mt-2">
                              {formatTimestamp(item.timestamp)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Memories Tab */}
        {activeTab === 'memories' && (
          <div className="h-full flex flex-col">
            {/* Search and Filter */}
            <div className="p-4 border-b border-secondary-200 space-y-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
                <input
                  type="text"
                  placeholder="Buscar en memorias..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-secondary-400" />
                <select
                  value={memoryFilter}
                  onChange={(e) => setMemoryFilter(e.target.value)}
                  className="text-sm border border-secondary-300 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="all">Todas las memorias</option>
                  <option value="episodic">Episódicas</option>
                  <option value="semantic">Semánticas</option>
                  <option value="procedural">Procedimentales</option>
                </select>
              </div>
            </div>

            {/* Memories List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
              {filteredMemories.length === 0 ? (
                <div className="text-center py-8">
                  <Archive className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                    No hay memorias
                  </h3>
                  <p className="text-secondary-600">
                    {searchQuery || memoryFilter !== 'all' 
                      ? 'No se encontraron memorias que coincidan con los filtros.'
                      : 'Aún no hay memorias almacenadas.'}
                  </p>
                </div>
              ) : (
                filteredMemories.map((memory) => {
                  const isExpanded = expandedMemory === memory.id;
                  
                  return (
                    <div
                      key={memory.id}
                      className={`border rounded-lg transition-all duration-200 ${getMemoryTypeColor(memory.type)}`}
                    >
                      <div className="p-3">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0 mt-1">
                            {getMemoryIcon(memory.type)}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              <h4 className="text-sm font-medium text-secondary-900 truncate">
                                {memory.title || 'Memoria sin título'}
                              </h4>
                              <span className={`px-2 py-0.5 text-xs rounded-full ${getMemoryTypeColor(memory.type)}`}>
                                {memory.type}
                              </span>
                            </div>
                            
                            <p className="text-sm text-secondary-700 line-clamp-2">
                              {memory.content}
                            </p>
                            
                            {/* Tags */}
                            {memory.tags && memory.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {memory.tags.slice(0, 3).map((tag, index) => (
                                  <span
                                    key={index}
                                    className="inline-flex items-center px-2 py-0.5 bg-secondary-100 text-secondary-700 text-xs rounded-full"
                                  >
                                    <Tag className="w-3 h-3 mr-1" />
                                    {tag}
                                  </span>
                                ))}
                                {memory.tags.length > 3 && (
                                  <span className="text-xs text-secondary-500">
                                    +{memory.tags.length - 3} más
                                  </span>
                                )}
                              </div>
                            )}
                            
                            <div className="flex items-center justify-between mt-2">
                              <div className="flex items-center space-x-2 text-xs text-secondary-500">
                                <Calendar className="w-3 h-3" />
                                <span>{formatTimestamp(memory.timestamp)}</span>
                                {memory.relevanceScore && (
                                  <>
                                    <Star className="w-3 h-3" />
                                    <span>{(memory.relevanceScore * 100).toFixed(0)}% relevante</span>
                                  </>
                                )}
                              </div>
                              
                              <button
                                onClick={() => setExpandedMemory(isExpanded ? null : memory.id)}
                                className="p-1 text-secondary-400 hover:text-secondary-600 rounded"
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                              </button>
                            </div>
                          </div>
                        </div>

                        {/* Expanded Content */}
                        {isExpanded && (
                          <div className="mt-3 pt-3 border-t border-secondary-200">
                            <div className="space-y-3">
                              {/* Full Content */}
                              <div>
                                <h5 className="text-sm font-medium text-secondary-800 mb-1">
                                  Contenido completo:
                                </h5>
                                <p className="text-sm text-secondary-700 whitespace-pre-wrap">
                                  {memory.content}
                                </p>
                              </div>

                              {/* Context */}
                              {memory.context && (
                                <div>
                                  <h5 className="text-sm font-medium text-secondary-800 mb-1">
                                    Contexto:
                                  </h5>
                                  <p className="text-sm text-secondary-600">
                                    {memory.context}
                                  </p>
                                </div>
                              )}

                              {/* Feedback */}
                              <div>
                                <h5 className="text-sm font-medium text-secondary-800 mb-2">
                                  ¿Fue útil esta memoria?
                                </h5>
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={() => handleFeedback(memory.id, 1, 'Útil')}
                                    className="flex items-center space-x-1 px-3 py-1 bg-success-100 text-success-700 rounded-full hover:bg-success-200 transition-colors"
                                  >
                                    <Heart className="w-3 h-3" />
                                    <span className="text-xs">Útil</span>
                                  </button>
                                  <button
                                    onClick={() => handleFeedback(memory.id, 0, 'No útil')}
                                    className="flex items-center space-x-1 px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full hover:bg-secondary-200 transition-colors"
                                  >
                                    <span className="text-xs">No útil</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <div className="h-full overflow-y-auto p-4 space-y-4 scrollbar-thin">
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-secondary-800 flex items-center space-x-2">
                <User className="w-4 h-4" />
                <span>Preferencias del Usuario</span>
              </h3>
              
              {Object.keys(userPreferences).length === 0 ? (
                <div className="text-center py-8">
                  <User className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                    Sin preferencias configuradas
                  </h3>
                  <p className="text-secondary-600">
                    Las preferencias se aprenderán automáticamente a medida que interactúes con Synapse.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {Object.entries(userPreferences).map(([key, value]) => (
                    <div
                      key={key}
                      className="p-3 bg-secondary-50 border border-secondary-200 rounded-lg"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-secondary-900 capitalize">
                            {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                          </h4>
                          <p className="text-sm text-secondary-700 mt-1">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </p>
                        </div>
                        <div className="flex items-center space-x-1">
                          {Array.from({ length: 5 }, (_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < (value.confidence || 3) 
                                  ? 'text-warning-400 fill-current' 
                                  : 'text-secondary-300'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryPanel;

