import React, { useState, useEffect } from 'react';
import { 
  Send, 
  Loader, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Eye,
  EyeOff,
  Zap
} from 'lucide-react';

const EndUserInterface = () => {
  const [taskInput, setTaskInput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [taskHistory, setTaskHistory] = useState([]);
  const [showDetails, setShowDetails] = useState({});

  const executeTask = async () => {
    if (!taskInput.trim() || isExecuting) return;

    setIsExecuting(true);
    const taskId = `task_${Date.now()}`;
    
    // Añadir tarea en progreso al historial
    const newTask = {
      id: taskId,
      text: taskInput,
      status: 'executing',
      timestamp: new Date(),
      tools_used: [],
      execution_time: 0,
      category: 'unknown',
      confidence: 0
    };
    
    setTaskHistory(prev => [newTask, ...prev]);
    setTaskInput('');

    try {
      const response = await fetch('/api/tasks/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          task: taskInput,
          context: {
            recent_successful_tools: taskHistory
              .filter(t => t.status === 'completed')
              .slice(0, 3)
              .flatMap(t => t.tools_used || [])
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Actualizar la tarea en el historial
        setTaskHistory(prev => prev.map(task => 
          task.id === taskId 
            ? {
                ...task,
                status: result.status,
                tools_used: result.tools_used || [],
                execution_time: result.execution_time || 0,
                category: result.category || 'general',
                confidence: result.confidence || 0,
                message: result.message
              }
            : task
        ));
      } else {
        // Marcar como error
        setTaskHistory(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, status: 'error', message: 'Error ejecutando la tarea' }
            : task
        ));
      }
    } catch (error) {
      console.error('Error ejecutando tarea:', error);
      setTaskHistory(prev => prev.map(task => 
        task.id === taskId 
          ? { ...task, status: 'error', message: 'Error de conexión' }
          : task
      ));
    } finally {
      setIsExecuting(false);
    }
  };

  const toggleDetails = (taskId) => {
    setShowDetails(prev => ({
      ...prev,
      [taskId]: !prev[taskId]
    }));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'executing':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'executing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'code_development': 'bg-purple-100 text-purple-800',
      'code_review': 'bg-indigo-100 text-indigo-800',
      'testing': 'bg-yellow-100 text-yellow-800',
      'deployment': 'bg-red-100 text-red-800',
      'monitoring': 'bg-green-100 text-green-800',
      'documentation': 'bg-blue-100 text-blue-800',
      'data_analysis': 'bg-orange-100 text-orange-800',
      'system_administration': 'bg-gray-100 text-gray-800',
      'research': 'bg-pink-100 text-pink-800',
      'general': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || colors['general'];
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Synapse AI Assistant
        </h1>
        <p className="text-gray-600">
          Describe lo que necesitas hacer y Synapse seleccionará automáticamente las mejores herramientas para completar tu tarea.
        </p>
      </div>

      {/* Input de tarea */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <div className="flex flex-col space-y-4">
          <textarea
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            placeholder="Describe la tarea que quieres realizar... Por ejemplo: 'Crear una aplicación web simple con React' o 'Analizar los logs del servidor para encontrar errores'"
            className="w-full p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
            disabled={isExecuting}
          />
          
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {taskInput.length}/500 caracteres
            </div>
            
            <button
              onClick={executeTask}
              disabled={!taskInput.trim() || isExecuting}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isExecuting ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Ejecutando...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Ejecutar Tarea</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Historial de tareas */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Historial de Tareas</h2>
        
        {taskHistory.length === 0 ? (
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              No hay tareas ejecutadas aún. ¡Describe tu primera tarea arriba!
            </p>
          </div>
        ) : (
          taskHistory.map((task) => (
            <div key={task.id} className="bg-white rounded-lg shadow border">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(task.status)}
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(task.status)}`}>
                        {task.status === 'executing' ? 'Ejecutando' :
                         task.status === 'completed' ? 'Completada' :
                         task.status === 'error' ? 'Error' : 'Pendiente'}
                      </span>
                      
                      {task.category && task.category !== 'unknown' && (
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getCategoryColor(task.category)}`}>
                          {task.category.replace('_', ' ')}
                        </span>
                      )}
                      
                      <span className="text-xs text-gray-500">
                        {task.timestamp.toLocaleString()}
                      </span>
                    </div>
                    
                    <p className="text-gray-900 mb-2">{task.text}</p>
                    
                    {task.message && (
                      <p className="text-sm text-gray-600 mb-2">{task.message}</p>
                    )}
                    
                    {task.status === 'completed' && (
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>⚡ {task.tools_used?.length || 0} herramientas</span>
                        <span>⏱️ {task.execution_time?.toFixed(1)}min</span>
                        {task.confidence > 0 && (
                          <span>🎯 {(task.confidence * 100).toFixed(0)}% confianza</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {task.status === 'completed' && task.tools_used?.length > 0 && (
                    <button
                      onClick={() => toggleDetails(task.id)}
                      className="ml-4 p-2 text-gray-400 hover:text-gray-600"
                    >
                      {showDetails[task.id] ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  )}
                </div>
                
                {/* Detalles expandibles */}
                {showDetails[task.id] && task.tools_used?.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      Herramientas utilizadas automáticamente:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {task.tools_used.map((tool, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full"
                        >
                          {tool}
                        </span>
                      ))}
                    </div>
                    
                    <div className="mt-3 text-xs text-gray-500">
                      <p>
                        💡 Synapse seleccionó estas herramientas automáticamente basándose en el análisis de tu tarea.
                        No necesitaste configurar nada manualmente.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Información adicional */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          ¿Cómo funciona la selección automática?
        </h3>
        <div className="text-blue-800 space-y-2">
          <p>• Synapse analiza tu descripción de tarea usando IA avanzada</p>
          <p>• Identifica automáticamente qué herramientas son necesarias</p>
          <p>• Selecciona las mejores opciones basándose en rendimiento histórico</p>
          <p>• Ejecuta la tarea de forma transparente sin requerir configuración manual</p>
        </div>
      </div>
    </div>
  );
};

export default EndUserInterface;

