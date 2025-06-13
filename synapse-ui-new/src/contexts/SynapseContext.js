import React, { createContext, useContext, useReducer, useEffect } from 'react';
import io from 'socket.io-client';

// Estado inicial del contexto de Synapse
const initialState = {
  // Estado de conexión
  isConnected: false,
  connectionStatus: 'disconnected',
  
  // Estado de la conversación
  messages: [],
  currentInput: '',
  isProcessing: false,
  
  // Estado de planificación
  currentPlan: null,
  planSteps: [],
  currentStepIndex: 0,
  planStatus: 'idle', // idle, generating, executing, completed, error
  
  // Estado de herramientas
  availableTools: [],
  activeTools: [],
  toolExecutions: [],
  
  // Estado de memoria y outputs
  executedPlans: [],
  planOutputs: {},
  memoryStore: {
    conversations: [],
    planOutputs: {},
    userPreferences: {},
    learnedPatterns: []
  },
  
  // Estado del sistema
  systemStatus: {
    cpu: 0,
    memory: 0,
    activeTasks: 0,
  },
  
  // Configuración
  settings: {
    autoApprove: false,
    showDetailedLogs: true,
    theme: 'light',
  },
  
  // Errores y notificaciones
  errors: [],
  notifications: [],
};

// Tipos de acciones
const actionTypes = {
  // Conexión
  SET_CONNECTION_STATUS: 'SET_CONNECTION_STATUS',
  SET_CONNECTED: 'SET_CONNECTED',

  // Mensajes
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_CURRENT_INPUT: 'SET_CURRENT_INPUT',
  SET_PROCESSING: 'SET_PROCESSING',

  // Planificación
  SET_CURRENT_PLAN: 'SET_CURRENT_PLAN',
  UPDATE_CURRENT_PLAN: 'UPDATE_CURRENT_PLAN',
  UPDATE_PLAN_STEP: 'UPDATE_PLAN_STEP',
  UPDATE_PLAN_PROGRESS: 'UPDATE_PLAN_PROGRESS',
  UPDATE_STEP_OUTPUT: 'UPDATE_STEP_OUTPUT',
  UPDATE_PLAN_SUMMARY: 'UPDATE_PLAN_SUMMARY',
  SAVE_PLAN_TO_MEMORY: 'SAVE_PLAN_TO_MEMORY',
  LOAD_EXECUTED_PLANS: 'LOAD_EXECUTED_PLANS',
  UPDATE_MEMORY_STORE: 'UPDATE_MEMORY_STORE',
  COMPLETE_PLAN: 'COMPLETE_PLAN',
  SET_PLAN_ERROR: 'SET_PLAN_ERROR',
  SET_PLAN_STATUS: 'SET_PLAN_STATUS',

  // Herramientas
  SET_AVAILABLE_TOOLS: 'SET_AVAILABLE_TOOLS',
  ADD_TOOL_EXECUTION: 'ADD_TOOL_EXECUTION',

  // Sistema
  UPDATE_SYSTEM_STATUS: 'UPDATE_SYSTEM_STATUS',

  // Errores y notificaciones
  ADD_ERROR: 'ADD_ERROR',
  CLEAR_ERRORS: 'CLEAR_ERRORS',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
};

// Reducer para manejar el estado
const synapseReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_CONNECTION_STATUS:
      return {
        ...state,
        connectionStatus: action.payload,
        isConnected: action.payload === 'connected',
      };
      
    case actionTypes.SET_CONNECTED:
      return {
        ...state,
        isConnected: action.payload,
        connectionStatus: action.payload ? 'connected' : 'disconnected',
      };
      
    case actionTypes.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };
      
    case actionTypes.SET_CURRENT_INPUT:
      return {
        ...state,
        currentInput: action.payload,
      };
      
    case actionTypes.SET_PROCESSING:
      return {
        ...state,
        isProcessing: action.payload,
      };
      
    case actionTypes.SET_CURRENT_PLAN:
      return {
        ...state,
        currentPlan: action.payload,
        planSteps: action.payload?.steps || [],
        currentStepIndex: 0,
        planStatus: 'idle',
      };

    case actionTypes.UPDATE_CURRENT_PLAN:
      return {
        ...state,
        currentPlan: action.payload,
        planSteps: action.payload?.steps || [],
      };
      
    case actionTypes.UPDATE_PLAN_STEP:
      console.log('🔄 UPDATE_PLAN_STEP - Payload:', action.payload);
      console.log('🔄 Estado actual planSteps:', state.planSteps.map(s => ({ id: s.id, title: s.title, status: s.status, hasOutput: !!s.output })));

      const updatedSteps = state.planSteps.map(step =>
        step.id === action.payload.step_id
          ? {
              ...step,
              status: action.payload.status,
              message: action.payload.message,
              output: action.payload.output || step.output  // Preservar output existente o añadir nuevo
            }
          : step
      );

      console.log('🔄 Pasos actualizados:', updatedSteps.map(s => ({ id: s.id, title: s.title, status: s.status, hasOutput: !!s.output, outputLength: s.output?.length || 0 })));

      return {
        ...state,
        planSteps: updatedSteps,
      };
      
    case actionTypes.UPDATE_PLAN_PROGRESS:
      return {
        ...state,
        currentPlan: {
          ...state.currentPlan,
          progress: action.payload.progress,
        },
        currentStepIndex: action.payload.current_step - 1,
      };
      
    case actionTypes.UPDATE_STEP_OUTPUT:
      return {
        ...state,
        planSteps: state.planSteps.map(step =>
          step.id === action.payload.stepId
            ? { ...step, output: action.payload.output }
            : step
        ),
      };
      
    case actionTypes.UPDATE_PLAN_SUMMARY:
      return {
        ...state,
        currentPlan: {
          ...state.currentPlan,
          final_summary: action.payload,
        },
      };
      
    case actionTypes.SAVE_PLAN_TO_MEMORY:
      const planToSave = action.payload;
      return {
        ...state,
        executedPlans: [...state.executedPlans, planToSave],
        planOutputs: {
          ...state.planOutputs,
          [planToSave.id]: planToSave.outputs
        }
      };
      
    case actionTypes.LOAD_EXECUTED_PLANS:
      return {
        ...state,
        executedPlans: action.payload.plans || [],
        memoryStore: {
          ...state.memoryStore,
          ...action.payload.memoryStore
        }
      };
      
    case actionTypes.UPDATE_MEMORY_STORE:
      return {
        ...state,
        memoryStore: {
          ...state.memoryStore,
          ...action.payload
        }
      };
      
    case actionTypes.COMPLETE_PLAN:
      return {
        ...state,
        currentPlan: {
          ...state.currentPlan,
          status: 'completed',
          progress: 100,
        },
        planStatus: 'completed',
      };
      
    case actionTypes.SET_PLAN_ERROR:
      return {
        ...state,
        planStatus: 'error',
        currentPlan: {
          ...state.currentPlan,
          error: action.payload,
        },
      };
      
    case actionTypes.SET_PLAN_STATUS:
      return {
        ...state,
        planStatus: action.payload,
      };
      
    case actionTypes.SET_AVAILABLE_TOOLS:
      return {
        ...state,
        availableTools: action.payload,
      };
      
    case actionTypes.ADD_TOOL_EXECUTION:
      return {
        ...state,
        toolExecutions: [...state.toolExecutions, action.payload],
      };
      
    case actionTypes.UPDATE_SYSTEM_STATUS:
      return {
        ...state,
        systemStatus: {
          ...state.systemStatus,
          cpu: action.payload.cpu_percent || action.payload.cpu || 0,
          memory: action.payload.memory_percent || action.payload.memory || 0,
          activeTasks: action.payload.active_connections || action.payload.activeTasks || 0,
        },
      };
      
    case actionTypes.ADD_ERROR:
      return {
        ...state,
        errors: [...state.errors, action.payload],
      };
      
    case actionTypes.CLEAR_ERRORS:
      return {
        ...state,
        errors: [],
      };
      
    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, action.payload],
      };
      
    case actionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload),
      };
      
    default:
      return state;
  }
};

// Crear el contexto
const SynapseContext = createContext();

// URL del backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

// Proveedor del contexto
export const SynapseProvider = ({ children }) => {
  const [state, dispatch] = useReducer(synapseReducer, initialState);
  const socketRef = React.useRef(null);

  // Extraer valores del estado
  const {
    isConnected,
    connectionStatus,
    messages,
    currentInput,
    isProcessing,
    currentPlan,
    planSteps,
    currentStepIndex,
    planStatus,
    executedPlans,
    planOutputs,
    memoryStore,
    availableTools,
    activeTools,
    toolExecutions,
    systemStatus,
    settings,
    errors,
    notifications,
  } = state;

  // Función para enviar mensajes
  const sendMessage = (message) => {
    if (socketRef.current && isConnected) {
      console.log('📤 Enviando mensaje:', message);
      socketRef.current.emit('user_message', { message });
      dispatch({
        type: actionTypes.ADD_MESSAGE,
        payload: {
          id: Date.now(),
          type: 'user',
          sender: 'user',
          content: message,
          timestamp: new Date().toISOString(),
        },
      });
      
      // Marcar como procesando
      dispatch({
        type: actionTypes.SET_PROCESSING,
        payload: true,
      });
    } else {
      console.error('❌ No conectado al servidor');
    }
  };

  // Función para aprobar plan
  const approvePlan = () => {
    if (socketRef.current && currentPlan) {
      socketRef.current.emit('approve_plan', { plan_id: currentPlan.id });
    }
  };

  // Función para modificar plan
  const modifyPlan = (modifications) => {
    if (socketRef.current && currentPlan) {
      socketRef.current.emit('modify_plan', {
        plan_id: currentPlan.id,
        modifications,
      });
    }
  };

  // Función para cargar planes ejecutados desde el backend
  const loadExecutedPlans = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/memory/all`);
      const data = await response.json();
      
      if (data.success) {
        dispatch({
          type: actionTypes.LOAD_EXECUTED_PLANS,
          payload: {
            plans: data.executed_plans,
            memoryStore: data.memory_store
          }
        });
      }
    } catch (error) {
      console.error('Error cargando planes ejecutados:', error);
    }
  };

  // Función para obtener outputs de un plan específico
  const getPlanOutputs = async (planId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/memory/plan/${planId}/outputs`);
      const data = await response.json();
      
      if (data.success) {
        return data.outputs;
      }
      return null;
    } catch (error) {
      console.error('Error obteniendo outputs del plan:', error);
      return null;
    }
  };

  // Función para obtener outputs recientes
  const getRecentOutputs = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/outputs/recent`);
      const data = await response.json();
      
      if (data.success) {
        return data.recent_outputs;
      }
      return [];
    } catch (error) {
      console.error('Error obteniendo outputs recientes:', error);
      return [];
    }
  };

  // Conectar a WebSocket al montar el componente
  useEffect(() => {
    const socket = io(BACKEND_URL, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    socketRef.current = socket;

    // Eventos de conexión
    socket.on('connect', () => {
      console.log('🔌 Conectado al servidor Synapse');
      dispatch({
        type: actionTypes.SET_CONNECTED,
        payload: true,
      });
      
      // Solicitar métricas del sistema al conectar
      socket.emit('get_system_metrics');
    });

    socket.on('disconnect', () => {
      console.log('🔌 Desconectado del servidor Synapse');
      dispatch({
        type: actionTypes.SET_CONNECTED,
        payload: false,
      });
      
      // Reset métricas al desconectar
      dispatch({
        type: actionTypes.UPDATE_SYSTEM_STATUS,
        payload: { cpu: 0, memory: 0, activeTasks: 0 }
      });
    });

    // Eventos de mensajes
    socket.on('message_response', (data) => {
      console.log('📨 Respuesta recibida:', data);
      dispatch({
        type: actionTypes.ADD_MESSAGE,
        payload: {
          id: Date.now(),
          type: 'synapse',
          sender: 'synapse',
          content: data.message,
          timestamp: new Date().toISOString(),
        },
      });
      
      // Dejar de procesar
      dispatch({
        type: actionTypes.SET_PROCESSING,
        payload: false,
      });
    });

    socket.on('synapse_response', (data) => {
      console.log('📨 Respuesta Synapse recibida:', data);
      dispatch({
        type: actionTypes.ADD_MESSAGE,
        payload: {
          id: Date.now(),
          type: 'synapse',
          sender: 'synapse',
          content: data.message,
          timestamp: new Date().toISOString(),
        },
      });
      
      // Dejar de procesar
      dispatch({
        type: actionTypes.SET_PROCESSING,
        payload: false,
      });
    });

    socket.on('message_received', (data) => {
      console.log('📨 Mensaje recibido por servidor:', data);
    });

    socket.on('processing_complete', (data) => {
      console.log('✅ Procesamiento completado');
      dispatch({
        type: actionTypes.SET_PROCESSING,
        payload: false,
      });
    });

    // Eventos de planificación
    socket.on('plan_generated', (data) => {
      dispatch({
        type: actionTypes.SET_CURRENT_PLAN,
        payload: data.plan,
      });
      
      dispatch({
        type: actionTypes.SET_PLAN_STATUS,
        payload: 'generated',
      });
    });

    socket.on('plan_step_update', (data) => {
      console.log('📊 Step update recibido:', data);
      console.log('📊 Datos completos del step update:', JSON.stringify(data, null, 2));

      dispatch({
        type: actionTypes.UPDATE_PLAN_STEP,
        payload: data,
      });

      // Log detallado para debugging
      if (data.output) {
        console.log('📄 Output detectado en step update:', data.output.length, 'caracteres');
        console.log('📄 Primeros 200 chars del output:', data.output.substring(0, 200));
      } else {
        console.log('⚠️ No hay output en step update');
        console.log('⚠️ Campos disponibles:', Object.keys(data));
      }
    });

    socket.on('plan_progress_update', (data) => {
      dispatch({
        type: actionTypes.UPDATE_PLAN_PROGRESS,
        payload: data,
      });
    });

    socket.on('plan_completed', (data) => {
      dispatch({
        type: actionTypes.SET_PLAN_STATUS,
        payload: 'completed',
      });
      
      // Actualizar el plan con el resumen final
      if (data.final_summary) {
        dispatch({
          type: actionTypes.UPDATE_PLAN_SUMMARY,
          payload: data.final_summary
        });
      }
      
      // Si el plan se guardó en memoria, cargar datos de memoria
      if (data.saved_to_memory) {
        loadExecutedPlans();
      }
      
      dispatch({
        type: actionTypes.ADD_NOTIFICATION,
        payload: {
          type: 'success',
          message: data.message || 'Plan completado exitosamente',
        },
      });
    });

    // Eventos del sistema
    // 🔄 Evento para expansión dinámica de planes
    socket.on('plan_expansion_notification', (data) => {
      console.log('🔄 Plan expandido dinámicamente:', data);

      // Actualizar notificaciones
      dispatch({
        type: actionTypes.ADD_NOTIFICATION,
        payload: {
          type: 'info',
          message: `Plan expandido: ${data.expansion_reason}`,
          details: `Se añadieron ${data.new_steps_count} pasos adicionales`,
        },
      });

      // Actualizar el plan actual si coincide
      if (data.plan_id && currentPlan && currentPlan.id === data.plan_id) {
        dispatch({
          type: actionTypes.UPDATE_CURRENT_PLAN,
          payload: data.updated_plan
        });
      }
    });

    // 🔄 Evento para actualización completa del plan
    socket.on('plan_updated', (data) => {
      console.log('📋 Plan actualizado:', data);

      // Actualizar el plan actual
      if (data.plan) {
        dispatch({
          type: actionTypes.UPDATE_CURRENT_PLAN,
          payload: data.plan
        });
      }

      // Notificar sobre la expansión
      if (data.new_steps_added > 0) {
        dispatch({
          type: actionTypes.ADD_NOTIFICATION,
          payload: {
            type: 'success',
            message: `Plan expandido automáticamente`,
            details: `${data.new_steps_added} pasos añadidos: ${data.expansion_reason}`,
          },
        });
      }
    });

    // Eventos del sistema
    socket.on('system_metrics', (data) => {
      console.log('📊 Métricas recibidas:', data);
      dispatch({
        type: actionTypes.UPDATE_SYSTEM_STATUS,
        payload: data,
      });
    });

    socket.on('connection_status', (data) => {
      dispatch({
        type: actionTypes.SET_CONNECTION_STATUS,
        payload: data.status,
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Cargar planes ejecutados al conectar
  useEffect(() => {
    if (isConnected) {
      loadExecutedPlans();
    }
  }, [isConnected]);

  return (
    <SynapseContext.Provider
      value={{
        // Estado
        isConnected,
        connectionStatus,
        messages,
        currentInput,
        isProcessing,
        currentPlan,
        planSteps,
        currentStepIndex,
        planStatus,
        executedPlans,
        planOutputs,
        memoryStore,
        availableTools,
        activeTools,
        toolExecutions,
        systemStatus,
        settings,
        errors,
        notifications,
        
        // Funciones
        sendMessage,
        approvePlan,
        modifyPlan,
        loadExecutedPlans,
        getPlanOutputs,
        getRecentOutputs,
      }}
    >
      {children}
    </SynapseContext.Provider>
  );
};

export const useSynapse = () => {
  const context = useContext(SynapseContext);
  if (!context) {
    throw new Error('useSynapse must be used within a SynapseProvider');
  }
  return context;
};

