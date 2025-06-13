import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, Clock, CheckCircle, AlertCircle, Download, Copy } from 'lucide-react';

const OutputsPanel = ({ currentPlan, planSteps }) => {
  const [expandedOutputs, setExpandedOutputs] = useState({});
  const [showFinalSummary, setShowFinalSummary] = useState(false);

  // Expandir/contraer output de un paso específico
  const toggleOutput = (stepId) => {
    setExpandedOutputs(prev => ({
      ...prev,
      [stepId]: !prev[stepId]
    }));
  };

  // Copiar output al portapapeles
  const copyOutput = async (output) => {
    try {
      await navigator.clipboard.writeText(output);
      // Aquí podrías añadir una notificación de éxito
    } catch (err) {
      console.error('Error copiando al portapapeles:', err);
    }
  };

  // Descargar output como archivo
  const downloadOutput = (output, stepTitle) => {
    const blob = new Blob([output], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${stepTitle.replace(/[^a-zA-Z0-9]/g, '_')}_output.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Filtrar pasos que tienen output - CORREGIDO para detectar outputs
  const stepsWithOutput = (planSteps || []).filter(step => {
    const hasOutput = step.output && step.output.trim().length > 0;
    console.log(`📊 Paso ${step.id}: ${step.title} - Status: ${step.status} - Output: ${hasOutput ? 'SÍ' : 'NO'} (${step.output?.length || 0} chars)`);
    if (step.output) {
      console.log(`📊 Output preview: ${step.output.substring(0, 100)}...`);
    }
    return hasOutput;
  });

  console.log(`📊 Total pasos: ${planSteps?.length || 0}, Con output: ${stepsWithOutput.length}`);
  console.log(`📊 Plan actual:`, currentPlan?.title || 'Sin plan');
  console.log(`📊 Todos los pasos:`, planSteps?.map(s => ({ id: s.id, title: s.title, status: s.status, hasOutput: !!s.output })) || []);

  if (!currentPlan) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No hay plan activo</p>
          <p className="text-sm">Los outputs aparecerán aquí cuando se ejecute un plan</p>
        </div>
      </div>
    );
  }

  if (stepsWithOutput.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Esperando outputs...</p>
          <p className="text-sm">Los resultados aparecerán conforme se ejecuten los pasos</p>
          <div className="mt-4 text-xs text-gray-400 space-y-1">
            <p>Debug: {planSteps?.length || 0} pasos totales</p>
            <p>Pasos completados: {(planSteps || []).filter(s => s.status === 'completed').length}</p>
            <p>Pasos con output: {(planSteps || []).filter(s => s.output && s.output.trim().length > 0).length}</p>
            <div className="mt-2 text-left">
              <p>Estados de pasos:</p>
              {(planSteps || []).map(step => (
                <div key={step.id} className="text-xs">
                  {step.id}: {step.status} - {step.output ? `${step.output.length} chars` : 'sin output'}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Resultados y Outputs</h2>
            <p className="text-sm text-gray-600">
              {stepsWithOutput.length} de {planSteps?.length || 0} pasos con resultados
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <CheckCircle className="w-3 h-3 mr-1" />
              {stepsWithOutput.length} Completados
            </span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Outputs de pasos individuales */}
        {stepsWithOutput.map((step, index) => (
          <div key={step.id} className="bg-white rounded-lg border border-gray-200 shadow-sm">
            {/* Header del paso */}
            <div 
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleOutput(step.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      Paso {index + 1}: {step.title}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {step.description || 'Sin descripción'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-400">
                    {step.output ? `${(step.output.length / 1024).toFixed(1)} KB` : '0 KB'}
                  </span>
                  {expandedOutputs[step.id] ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </div>
            </div>

            {/* Output expandible */}
            {expandedOutputs[step.id] && step.output && (
              <div className="border-t border-gray-200">
                <div className="p-4">
                  {/* Controles del output */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-medium text-gray-700">Output generado:</span>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => copyOutput(step.output)}
                        className="inline-flex items-center px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                      >
                        <Copy className="w-3 h-3 mr-1" />
                        Copiar
                      </button>
                      <button
                        onClick={() => downloadOutput(step.output, step.title)}
                        className="inline-flex items-center px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Descargar
                      </button>
                    </div>
                  </div>

                  {/* Contenido del output */}
                  <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-sm text-gray-100 whitespace-pre-wrap font-mono">
                      {step.output}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Resumen final del plan */}
        {currentPlan?.final_summary && (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
            <div 
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => setShowFinalSummary(!showFinalSummary)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <CheckCircle className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      Resumen Final del Plan
                    </h3>
                    <p className="text-xs text-gray-500">
                      Síntesis completa de todos los resultados
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-400">
                    {currentPlan.final_summary ? `${(currentPlan.final_summary.length / 1024).toFixed(1)} KB` : '0 KB'}
                  </span>
                  {showFinalSummary ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </div>
            </div>

            {showFinalSummary && currentPlan.final_summary && (
              <div className="border-t border-gray-200">
                <div className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-medium text-gray-700">Resumen final:</span>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => copyOutput(currentPlan.final_summary)}
                        className="inline-flex items-center px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                      >
                        <Copy className="w-3 h-3 mr-1" />
                        Copiar
                      </button>
                      <button
                        onClick={() => downloadOutput(currentPlan.final_summary, 'Resumen_Final')}
                        className="inline-flex items-center px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Descargar
                      </button>
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-sm text-blue-900 whitespace-pre-wrap font-mono">
                      {currentPlan.final_summary}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default OutputsPanel;

