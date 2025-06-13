import React, { useState, useEffect } from 'react';
import { useSynapse } from '../contexts/SynapseContext';
import {
  Brain,
  MessageSquare,
  User,
  TrendingUp,
  Database,
  Download,
  Trash2,
  RefreshCw,
  BarChart3,
  CheckCircle
} from 'lucide-react';

const MemoryPanel = () => {
  const { memoryStore, isConnected } = useSynapse();
  const [memoryStats, setMemoryStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);

  // Cargar estadísticas de memoria
  const loadMemoryStats = async () => {
    if (!isConnected) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/memory/stats');
      const data = await response.json();
      if (data.success) {
        setMemoryStats(data.stats);
      }
    } catch (error) {
      console.error('Error cargando estadísticas de memoria:', error);
    } finally {
      setLoading(false);
    }
  };

  // Crear backup de memoria
  const createBackup = async () => {
    if (!isConnected) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/memory/backup', {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert(`Backup creado: ${data.backup_file}`);
      }
    } catch (error) {
      console.error('Error creando backup:', error);
      alert('Error creando backup');
    } finally {
      setLoading(false);
    }
  };

  // Limpiar memoria
  const clearMemory = async () => {
    if (!isConnected) return;
    if (!confirm('¿Estás seguro de que quieres limpiar toda la memoria?')) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/memory/clear', {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert('Memoria limpiada exitosamente');
        loadMemoryStats();
      }
    } catch (error) {
      console.error('Error limpiando memoria:', error);
      alert('Error limpiando memoria');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemoryStats();
  }, [isConnected]);

  const tabs = [
    { id: 'overview', name: 'Resumen', icon: BarChart3 },
    { id: 'conversations', name: 'Conversaciones', icon: MessageSquare },
    { id: 'preferences', name: 'Preferencias', icon: User },
    { id: 'patterns', name: 'Patrones', icon: TrendingUp },
    { id: 'storage', name: 'Almacenamiento', icon: Database }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Estadísticas principales */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600">Conversaciones</p>
              <p className="text-2xl font-bold text-blue-800">
                {memoryStats?.conversations?.total || 0}
              </p>
            </div>
            <MessageSquare className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600">Usuarios</p>
              <p className="text-2xl font-bold text-green-800">
                {memoryStats?.users?.total || 0}
              </p>
            </div>
            <User className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600">Patrones</p>
              <p className="text-2xl font-bold text-purple-800">
                {memoryStats?.patterns?.total || 0}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-orange-600">Planes</p>
              <p className="text-2xl font-bold text-orange-800">
                {memoryStats?.plans?.total_executed || 0}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Información adicional */}
      {memoryStats && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Detalles de Memoria</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p><strong>Conversaciones recientes (24h):</strong> {memoryStats.conversations?.recent_24h || 0}</p>
              <p><strong>Usuarios con preferencias:</strong> {memoryStats.users?.active_preferences || 0}</p>
              <p><strong>Tasa de éxito promedio:</strong> {memoryStats.patterns?.avg_success_rate || 0}%</p>
            </div>
            <div>
              <p><strong>Patrón más frecuente:</strong> {memoryStats.patterns?.most_frequent || 'N/A'}</p>
              <p><strong>Total de outputs:</strong> {memoryStats.plans?.total_outputs || 0}</p>
              <p><strong>Tamaño en disco:</strong> {memoryStats.storage?.memory_file_size_mb || 0} MB</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderConversations = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Historial de Conversaciones</h3>
        <span className="text-sm text-gray-500">
          {memoryStore?.conversations?.length || 0} conversaciones
        </span>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {memoryStore?.conversations?.slice(-10).reverse().map((conv, index) => (
          <div key={conv.id || index} className="bg-white p-3 rounded-lg border">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-500">
                {new Date(conv.timestamp).toLocaleString()}
              </span>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {conv.intents?.join(', ') || 'N/A'}
              </span>
            </div>
            <div className="space-y-2">
              <div>
                <p className="text-sm font-medium text-gray-700">Usuario:</p>
                <p className="text-sm text-gray-600">{conv.user_message}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Asistente:</p>
                <p className="text-sm text-gray-600">{conv.assistant_response}</p>
              </div>
              {conv.plan_title && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Plan generado:</p>
                  <p className="text-sm text-blue-600">{conv.plan_title}</p>
                </div>
              )}
            </div>
          </div>
        )) || (
          <p className="text-gray-500 text-center py-8">No hay conversaciones guardadas</p>
        )}
      </div>
    </div>
  );

  const renderPreferences = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Preferencias de Usuario</h3>
      
      <div className="space-y-3">
        {Object.entries(memoryStore?.userPreferences || {}).map(([userId, prefs]) => (
          <div key={userId} className="bg-white p-4 rounded-lg border">
            <h4 className="font-medium text-gray-800 mb-2">{userId}</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><strong>Idioma:</strong> {prefs.language || 'N/A'}</div>
              <div><strong>Estilo:</strong> {prefs.response_style || 'N/A'}</div>
              <div><strong>Complejidad:</strong> {prefs.complexity_level || 'N/A'}</div>
              <div><strong>Actualizado:</strong> {prefs.last_updated ? new Date(prefs.last_updated).toLocaleDateString() : 'N/A'}</div>
            </div>
            {prefs.project_types && prefs.project_types.length > 0 && (
              <div className="mt-2">
                <strong className="text-sm">Tipos de proyecto:</strong>
                <div className="flex flex-wrap gap-1 mt-1">
                  {prefs.project_types.map((type, idx) => (
                    <span key={idx} className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )) || (
          <p className="text-gray-500 text-center py-8">No hay preferencias guardadas</p>
        )}
      </div>
    </div>
  );

  const renderPatterns = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Patrones Aprendidos</h3>
      
      <div className="space-y-3">
        {memoryStore?.learnedPatterns?.slice(0, 10).map((pattern, index) => (
          <div key={pattern.id || index} className="bg-white p-4 rounded-lg border">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-medium text-gray-800">{pattern.plan_type}</h4>
              <div className="flex gap-2">
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                  {pattern.success_rate}% éxito
                </span>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {pattern.frequency}x usado
                </span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
              <div><strong>Pasos:</strong> {pattern.steps_count}</div>
              <div><strong>Tiempo promedio:</strong> {pattern.execution_time?.toFixed(1)}s</div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Último uso: {new Date(pattern.timestamp).toLocaleDateString()}
            </p>
          </div>
        )) || (
          <p className="text-gray-500 text-center py-8">No hay patrones aprendidos</p>
        )}
      </div>
    </div>
  );

  const renderStorage = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Gestión de Almacenamiento</h3>
        <div className="flex gap-2">
          <button
            onClick={createBackup}
            disabled={loading || !isConnected}
            className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            Backup
          </button>
          <button
            onClick={clearMemory}
            disabled={loading || !isConnected}
            className="flex items-center gap-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4" />
            Limpiar
          </button>
        </div>
      </div>

      {memoryStats && (
        <div className="bg-white p-4 rounded-lg border">
          <h4 className="font-medium mb-3">Información de Almacenamiento</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Tamaño del archivo de memoria:</span>
              <span className="font-mono">{memoryStats.storage?.memory_file_size_mb || 0} MB</span>
            </div>
            <div className="flex justify-between">
              <span>Tamaño en bytes:</span>
              <span className="font-mono">{memoryStats.storage?.memory_file_size_bytes || 0} bytes</span>
            </div>
            <div className="flex justify-between">
              <span>Última actualización:</span>
              <span>{new Date().toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}

      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <h4 className="font-medium text-yellow-800 mb-2">⚠️ Información Importante</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• La memoria se guarda automáticamente cada 5 minutos</li>
          <li>• Los backups se crean con timestamp único</li>
          <li>• Limpiar memoria eliminará todos los datos permanentemente</li>
          <li>• La memoria se carga automáticamente al iniciar el servidor</li>
        </ul>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="flex-shrink-0 p-4 bg-white border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-500" />
            <h2 className="text-lg font-semibold">Memoria del Sistema</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadMemoryStats}
              disabled={loading || !isConnected}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
              title="Actualizar estadísticas"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mt-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-4 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-500">Cargando...</span>
          </div>
        )}

        {!loading && (
          <>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'conversations' && renderConversations()}
            {activeTab === 'preferences' && renderPreferences()}
            {activeTab === 'patterns' && renderPatterns()}
            {activeTab === 'storage' && renderStorage()}
          </>
        )}
      </div>
    </div>
  );
};

export default MemoryPanel;