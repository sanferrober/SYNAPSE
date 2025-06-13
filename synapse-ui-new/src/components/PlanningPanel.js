import React, { useState } from 'react';
import { useSynapse } from '../contexts/SynapseContext';
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Edit3, 
  ChevronRight,
  ChevronDown,
  Target,
  Zap,
  Play,
  FileText
} from 'lucide-react';

const PlanningPanel = () => {
  const {
    currentPlan,
    planSteps,
    currentStepIndex,
    planStatus,
    approvePlan,
    modifyPlan,
    isProcessing,
  } = useSynapse();

  const [expandedSteps, setExpandedSteps] = useState(new Set());
  const [editingStep, setEditingStep] = useState(null);
  const [editText, setEditText] = useState('');

  const toggleStepExpansion = (stepIndex) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepIndex)) {
      newExpanded.delete(stepIndex);
    } else {
      newExpanded.add(stepIndex);
    }
    setExpandedSteps(newExpanded);
  };

  const startEditingStep = (stepIndex, currentText) => {
    setEditingStep(stepIndex);
    setEditText(currentText);
  };

  const saveStepEdit = () => {
    if (editingStep !== null) {
      modifyPlan({
        stepIndex: editingStep,
        newDescription: editText,
      });
      setEditingStep(null);
      setEditText('');
    }
  };

  const cancelStepEdit = () => {
    setEditingStep(null);
    setEditText('');
  };

  const getStepIcon = (step, index) => {
    if (index < (currentStepIndex || 0)) {
      return <CheckCircle className="w-5 h-5 text-success-600" />;
    } else if (index === (currentStepIndex || 0) && planStatus === 'executing') {
      return <Clock className="w-5 h-5 text-warning-600 animate-pulse" />;
    } else if (step?.status === 'error') {
      return <AlertCircle className="w-5 h-5 text-error-600" />;
    } else {
      return <div className="w-5 h-5 rounded-full border-2 border-secondary-300" />;
    }
  };

  const getStepStatus = (step, index) => {
    if (index < (currentStepIndex || 0)) {
      return 'completed';
    } else if (index === (currentStepIndex || 0) && planStatus === 'executing') {
      return 'current';
    } else if (step?.status === 'error') {
      return 'error';
    } else {
      return 'pending';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-50 border-success-200';
      case 'current':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'error':
        return 'text-error-600 bg-error-50 border-error-200';
      default:
        return 'text-secondary-600 bg-secondary-50 border-secondary-200';
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) {
      return `${seconds}s`;
    } else if (seconds < 3600) {
      return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    } else {
      return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    }
  };

  if (!currentPlan) {
    return (
      <div className="h-full bg-white rounded-xl shadow-sm border border-secondary-200 flex items-center justify-center">
        <div className="text-center">
          <Target className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-secondary-900 mb-2">
            Sin Plan Activo
          </h3>
          <p className="text-secondary-600 max-w-sm">
            Envía un mensaje para que Synapse genere un plan de ejecución
            para tu tarea.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white rounded-xl shadow-sm border border-secondary-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-secondary-900">Plan de Ejecución</h2>
              <p className="text-sm text-secondary-600">{currentPlan.title || 'Plan Actual'}</p>
            </div>
          </div>
          
          {/* Status Badge */}
          <div className={`px-3 py-1 rounded-full text-sm font-medium border ${
            planStatus === 'completed' ? 'text-success-600 bg-success-50 border-success-200' :
            planStatus === 'executing' ? 'text-warning-600 bg-warning-50 border-warning-200' :
            planStatus === 'error' ? 'text-error-600 bg-error-50 border-error-200' :
            'text-secondary-600 bg-secondary-50 border-secondary-200'
          }`}>
            {planStatus === 'generating' && 'Generando'}
            {planStatus === 'executing' && 'Ejecutando'}
            {planStatus === 'completed' && 'Completado'}
            {planStatus === 'error' && 'Error'}
            {planStatus === 'idle' && 'En Espera'}
          </div>
        </div>

        {/* Plan Description */}
        {currentPlan.description && (
          <p className="text-sm text-secondary-700 mb-3">
            {currentPlan.description}
          </p>
        )}

        {/* Progress Bar */}
        <div className="w-full bg-secondary-200 rounded-full h-2 mb-3">
          <div
            className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${(planSteps?.length || 0) > 0 ? ((currentStepIndex || 0) / (planSteps?.length || 1)) * 100 : 0}%`,
            }}
          />
        </div>

        {/* Plan Stats */}
        <div className="flex items-center justify-between text-sm text-secondary-600">
          <span>
            Paso {(currentStepIndex || 0) + 1} de {planSteps?.length || 0}
          </span>
          {currentPlan?.estimatedDuration && (
            <span>
              Duración estimada: {formatDuration(currentPlan.estimatedDuration)}
            </span>
          )}
        </div>

        {/* Action Buttons */}
        {planStatus === 'idle' && (
          <div className="flex space-x-2 mt-3">
            <button
              onClick={approvePlan}
              disabled={isProcessing}
              className="btn-primary flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>Aprobar y Ejecutar</span>
            </button>
            <button
              onClick={() => {/* Implementar modificación de plan */}}
              disabled={isProcessing}
              className="btn-secondary flex items-center space-x-2"
            >
              <Edit3 className="w-4 h-4" />
              <span>Modificar</span>
            </button>
          </div>
        )}
      </div>

      {/* Steps List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
        {(planSteps || []).map((step, index) => {
          const status = getStepStatus(step, index);
          const isExpanded = expandedSteps.has(index);
          const isEditing = editingStep === index;

          return (
            <div
              key={index}
              className={`border rounded-lg transition-all duration-200 ${getStatusColor(status)}`}
            >
              {/* Step Header */}
              <div className="p-3">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {getStepIcon(step, index)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    {isEditing ? (
                      <div className="space-y-2">
                        <textarea
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="w-full p-2 border border-secondary-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
                          rows="2"
                        />
                        <div className="flex space-x-2">
                          <button
                            onClick={saveStepEdit}
                            className="px-3 py-1 bg-primary-600 text-white text-sm rounded hover:bg-primary-700"
                          >
                            Guardar
                          </button>
                          <button
                            onClick={cancelStepEdit}
                            className="px-3 py-1 bg-secondary-300 text-secondary-700 text-sm rounded hover:bg-secondary-400"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <h4 className="font-medium text-secondary-900 truncate">
                          {step.title || `Paso ${index + 1}`}
                        </h4>
                        <p className="text-sm text-secondary-700 mt-1">
                          {step.description}
                        </p>
                      </>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {/* Duration */}
                    {step.duration && (
                      <span className="text-xs text-secondary-500">
                        {formatDuration(step.duration)}
                      </span>
                    )}

                    {/* Edit Button */}
                    {!isEditing && planStatus === 'idle' && (
                      <button
                        onClick={() => startEditingStep(index, step.description)}
                        className="p-1 text-secondary-400 hover:text-secondary-600 rounded"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                    )}

                    {/* Expand Button */}
                    {(step.details || step.tools || step.outputs) && (
                      <button
                        onClick={() => toggleStepExpansion(index)}
                        className="p-1 text-secondary-400 hover:text-secondary-600 rounded"
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="mt-3 pl-8 space-y-3">
                    {/* Step Details */}
                    {step.details && (
                      <div>
                        <h5 className="text-sm font-medium text-secondary-800 mb-1">
                          Detalles:
                        </h5>
                        <p className="text-sm text-secondary-600">
                          {step.details}
                        </p>
                      </div>
                    )}

                    {/* Tools Used */}
                    {step.tools && step.tools.length > 0 && (
                      <div>
                        <h5 className="text-sm font-medium text-secondary-800 mb-2">
                          Herramientas:
                        </h5>
                        <div className="flex flex-wrap gap-2">
                          {step.tools.map((tool, toolIndex) => (
                            <span
                              key={toolIndex}
                              className="inline-flex items-center px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                            >
                              <Zap className="w-3 h-3 mr-1" />
                              {tool}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Step Outputs */}
                    {step.output && (
                      <div>
                        <h5 className="text-sm font-medium text-secondary-800 mb-2 flex items-center">
                          <FileText className="w-4 h-4 mr-1" />
                          Output Generado:
                        </h5>
                        <div className="bg-gray-900 rounded-lg p-3 max-h-32 overflow-y-auto">
                          <pre className="text-xs text-gray-100 whitespace-pre-wrap font-mono">
                            {step.output.length > 200 ? 
                              `${step.output.substring(0, 200)}...\n\n[Ver output completo en panel de Resultados]` : 
                              step.output
                            }
                          </pre>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">
                          Tamaño: {(step.output.length / 1024).toFixed(1)} KB
                        </div>
                      </div>
                    )}

                    {/* Legacy Step Outputs */}
                    {step.outputs && step.outputs.length > 0 && (
                      <div>
                        <h5 className="text-sm font-medium text-secondary-800 mb-2">
                          Resultados:
                        </h5>
                        <div className="space-y-1">
                          {step.outputs.map((output, outputIndex) => (
                            <div
                              key={outputIndex}
                              className="text-sm text-secondary-600 bg-secondary-50 p-2 rounded"
                            >
                              {output}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PlanningPanel;

