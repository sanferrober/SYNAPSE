import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, FileText, Clock, CheckCircle, AlertCircle, Download, Copy } from 'lucide-react';

const OutputsPanelFixed = ({ currentPlan, planSteps }) => {
  const [expandedOutputs, setExpandedOutputs] = useState({});
  const [showFinalSummary, setShowFinalSummary] = useState(false);
  const [renderCount, setRenderCount] = useState(0);

  // Force re-render counter para debugging
  useEffect(() => {
    setRenderCount(prev => prev + 1);
  }, [currentPlan, planSteps]);

  // Log detallado para debug - SIEMPRE
  console.log(`🔍 OutputsPanelFixed - Render #${renderCount}`);
  console.log('   currentPlan:', currentPlan);
  console.log('   planSteps:', planSteps);
  console.log('   planSteps type:', typeof planSteps);
  console.log('   planSteps length:', planSteps?.length);
  console.log('   planSteps is array:', Array.isArray(planSteps));

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

  // Filtrar pasos que tienen output - MEJORADO
  const stepsWithOutput = React.useMemo(() => {
    console.log('🔍 Calculando stepsWithOutput...');
    
    if (!planSteps || !Array.isArray(planSteps)) {
      console.log('   ❌ planSteps no es un array válido');
      return [];
    }

    const filtered = planSteps.filter((step, index) => {
      const hasOutput = step && step.output && typeof step.output === 'string' && step.output.trim().length > 0;
      console.log(`   📊 Paso ${index + 1} (ID: ${step?.id}): ${step?.title} - Output: ${hasOutput ? 'SÍ' : 'NO'} (${step?.output?.length || 0} chars)`);
      
      if (hasOutput) {
        console.log(`   📝 Preview: ${step.output.substring(0, 100)}...`);
      }
      
      return hasOutput;
    });

    console.log(`   🎯 Resultado: ${filtered.length}/${planSteps.length} pasos con output`);
    return filtered;
  }, [planSteps]);

  console.log(`📊 stepsWithOutput final: ${stepsWithOutput.length} pasos`);

  // Verificación de currentPlan
  if (!currentPlan) {
    console.log('❌ No hay currentPlan - mostrando mensaje de no plan activo');
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No hay plan activo</p>
          <p className="text-sm">Los outputs aparecerán aquí cuando se ejecute un plan</p>
          <div className="mt-4 text-xs text-gray-400">
            <p>Render #{renderCount}</p>
          </div>
        </div>
      </div>
    );
  }

  // Verificación de outputs
  if (stepsWithOutput.length === 0) {
    console.log('❌ No hay outputs - mostrando mensaje de esperando');
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Esperando outputs...</p>
          <p className="text-sm">Los resultados aparecerán conforme se ejecuten los pasos</p>
          <div className="mt-4 text-xs text-gray-400 space-y-1">
            <p>Render #{renderCount}</p>
            <p>Debug: {planSteps?.length || 0} pasos totales</p>
            <p>Pasos completados: {(planSteps || []).filter(s => s.status === 'completed').length}</p>
            <p>Pasos con output: {(planSteps || []).filter(s => s.output && s.output.trim().length > 0).length}</p>
            <div className="mt-2 text-left">
              <p>Estados de pasos:</p>
              {(planSteps || []).map((step, index) => (
                <div key={step.id || index} className="text-xs">
                  {step.id}: {step.status} - {step.output ? `${step.output.length} chars` : 'sin output'}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  console.log('✅ Mostrando outputs - renderizando lista');

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Resultados y Outputs</h2>
            <p className="text-sm text-gray-600">
              {stepsWithOutput.length} de {planSteps?.length || 0} pasos con resultados (Render #{renderCount})
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500">
              Plan: {currentPlan?.title || 'Sin título'}
            </span>
          </div>
        </div>
      </div>

      {/* Lista de outputs */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {stepsWithOutput.map((step, index) => (
          <div key={step.id || index} className="bg-white rounded-lg border border-gray-200 shadow-sm">
            {/* Header del paso */}
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {step.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : step.status === 'error' ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <Clock className="w-5 h-5 text-yellow-500" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      Paso {index + 1}: {step.title}
                    </h3>
                    <p className="text-xs text-gray-500">
                      Estado: {step.status} • {step.output?.length || 0} caracteres
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => copyOutput(step.output)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Copiar output"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => downloadOutput(step.output, step.title)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Descargar output"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => toggleOutput(step.id)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {expandedOutputs[step.id] ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Contenido del output */}
            <div className={`transition-all duration-200 ${expandedOutputs[step.id] ? 'block' : 'hidden'}`}>
              <div className="p-4">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded border max-h-96 overflow-y-auto">
                  {step.output}
                </pre>
              </div>
            </div>

            {/* Preview cuando está colapsado */}
            {!expandedOutputs[step.id] && (
              <div className="p-4 pt-0">
                <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded border">
                  <strong>Preview:</strong> {step.output?.substring(0, 200)}...
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Final summary si existe */}
      {currentPlan?.final_summary && (
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-900">Resumen Final del Plan</h3>
            <button
              onClick={() => setShowFinalSummary(!showFinalSummary)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              {showFinalSummary ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>
          {showFinalSummary && (
            <div className="text-xs text-gray-700 bg-blue-50 p-3 rounded border">
              <pre className="whitespace-pre-wrap">{currentPlan.final_summary}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OutputsPanelFixed;