import React from 'react';
import { useSynapse } from '../contexts/SynapseContext';
import { 
  Wifi, 
  WifiOff, 
  Cpu, 
  HardDrive, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Zap
} from 'lucide-react';

const StatusBar = () => {
  const {
    isConnected,
    connectionStatus,
    systemStatus,
    activeTools,
    planStatus,
    isProcessing,
    errors,
    notifications,
  } = useSynapse();

  const getConnectionIcon = () => {
    if (isConnected) {
      return <Wifi className="w-4 h-4 text-success-600" />;
    } else {
      return <WifiOff className="w-4 h-4 text-error-600" />;
    }
  };

  const getConnectionStatus = () => {
    switch (connectionStatus) {
      case 'connected':
        return { text: 'Conectado', color: 'text-success-600' };
      case 'connecting':
        return { text: 'Conectando...', color: 'text-warning-600' };
      case 'disconnected':
        return { text: 'Desconectado', color: 'text-error-600' };
      case 'reconnecting':
        return { text: 'Reconectando...', color: 'text-warning-600' };
      default:
        return { text: 'Desconocido', color: 'text-secondary-600' };
    }
  };

  const getPlanStatusInfo = () => {
    switch (planStatus) {
      case 'generating':
        return { text: 'Generando plan', color: 'text-warning-600', icon: Clock };
      case 'executing':
        return { text: 'Ejecutando', color: 'text-primary-600', icon: Activity };
      case 'completed':
        return { text: 'Completado', color: 'text-success-600', icon: CheckCircle };
      case 'error':
        return { text: 'Error', color: 'text-error-600', icon: AlertTriangle };
      default:
        return { text: 'Inactivo', color: 'text-secondary-600', icon: Clock };
    }
  };

  const formatPercentage = (value) => {
    return `${Math.round(value)}%`;
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 80) return 'text-error-600';
    if (percentage >= 60) return 'text-warning-600';
    return 'text-success-600';
  };

  const connectionInfo = getConnectionStatus();
  const planInfo = getPlanStatusInfo();
  const PlanIcon = planInfo.icon;

  return (
    <div className="bg-white border-t border-secondary-200 px-4 py-2">
      <div className="flex items-center justify-between">
        {/* Left Section - Connection and System Status */}
        <div className="flex items-center space-x-6">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {getConnectionIcon()}
            <span className={`text-sm font-medium ${connectionInfo.color}`}>
              {connectionInfo.text}
            </span>
          </div>

          {/* System Resources */}
          <div className="flex items-center space-x-4">
            {/* CPU Usage */}
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-secondary-500" />
              <span className={`text-sm ${getUsageColor(systemStatus.cpu)}`}>
                CPU: {formatPercentage(systemStatus.cpu)}
              </span>
            </div>

            {/* Memory Usage */}
            <div className="flex items-center space-x-2">
              <HardDrive className="w-4 h-4 text-secondary-500" />
              <span className={`text-sm ${getUsageColor(systemStatus.memory)}`}>
                RAM: {formatPercentage(systemStatus.memory)}
              </span>
            </div>

            {/* Active Tasks */}
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-secondary-500" />
              <span className="text-sm text-secondary-700">
                Tareas: {systemStatus.activeTasks || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Center Section - Plan Status */}
        <div className="flex items-center space-x-6">
          {/* Plan Status */}
          <div className="flex items-center space-x-2">
            <PlanIcon className={`w-4 h-4 ${planInfo.color}`} />
            <span className={`text-sm font-medium ${planInfo.color}`}>
              {planInfo.text}
            </span>
          </div>

          {/* Active Tools */}
          {activeTools.length > 0 && (
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-warning-600" />
              <span className="text-sm text-secondary-700">
                {activeTools.length} herramienta{activeTools.length !== 1 ? 's' : ''} activa{activeTools.length !== 1 ? 's' : ''}
              </span>
            </div>
          )}

          {/* Processing Indicator */}
          {isProcessing && (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm text-primary-600 font-medium">
                Procesando...
              </span>
            </div>
          )}
        </div>

        {/* Right Section - Notifications and Errors */}
        <div className="flex items-center space-x-4">
          {/* Error Count */}
          {errors.length > 0 && (
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-error-600" />
              <span className="text-sm text-error-600 font-medium">
                {errors.length} error{errors.length !== 1 ? 'es' : ''}
              </span>
            </div>
          )}

          {/* Notification Count */}
          {notifications.length > 0 && (
            <div className="flex items-center space-x-2">
              <div className="relative">
                <CheckCircle className="w-4 h-4 text-primary-600" />
                {notifications.length > 0 && (
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary-600 rounded-full"></div>
                )}
              </div>
              <span className="text-sm text-primary-600 font-medium">
                {notifications.length}
              </span>
            </div>
          )}

          {/* Current Time */}
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-secondary-500" />
            <span className="text-sm text-secondary-700">
              {new Date().toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>

          {/* Version/Build Info */}
          <div className="text-xs text-secondary-500 border-l border-secondary-200 pl-4">
            Synapse v1.0.0
          </div>
        </div>
      </div>

      {/* Expanded Status Information (when there are errors or important notifications) */}
      {(errors.length > 0 || notifications.some(n => n.priority === 'high')) && (
        <div className="mt-2 pt-2 border-t border-secondary-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Latest Error */}
              {errors.length > 0 && (
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-error-600" />
                  <span className="text-sm text-error-700">
                    Último error: {errors[errors.length - 1]?.message || 'Error desconocido'}
                  </span>
                </div>
              )}

              {/* High Priority Notifications */}
              {notifications.filter(n => n.priority === 'high').map((notification, index) => (
                <div key={notification.id} className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-primary-600" />
                  <span className="text-sm text-primary-700">
                    {notification.message}
                  </span>
                </div>
              ))}
            </div>

            {/* Quick Actions */}
            <div className="flex items-center space-x-2">
              {errors.length > 0 && (
                <button className="text-xs text-error-600 hover:text-error-700 underline">
                  Ver detalles
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusBar;

