import React from 'react';
import { useSynapse } from '../contexts/SynapseContext';

const SimpleOutputsPanel = () => {
  const { currentPlan, planSteps, isConnected } = useSynapse();

  // Log detallado para debug
  console.log('🔍 SimpleOutputsPanel - Render');
  console.log('   isConnected:', isConnected);
  console.log('   currentPlan:', currentPlan);
  console.log('   planSteps:', planSteps);
  console.log('   planSteps type:', typeof planSteps);
  console.log('   planSteps length:', planSteps?.length);

  if (planSteps && Array.isArray(planSteps)) {
    console.log('   📊 Análisis detallado de planSteps:');
    planSteps.forEach((step, index) => {
      console.log(`      Paso ${index + 1}:`, {
        id: step.id,
        title: step.title,
        status: step.status,
        output: step.output,
        outputType: typeof step.output,
        outputLength: step.output?.length || 0,
        hasOutput: !!step.output,
        outputTrimmed: step.output?.trim?.(),
        outputTrimmedLength: step.output?.trim?.()?.length || 0
      });
    });
  }

  // Aplicar el mismo filtro que OutputsPanel
  const stepsWithOutput = (planSteps || []).filter(step => {
    const hasOutput = step.output && step.output.trim().length > 0;
    console.log(`   🔍 Filtro paso ${step.id}: ${step.title} - hasOutput: ${hasOutput}`);
    return hasOutput;
  });

  console.log('   📊 stepsWithOutput length:', stepsWithOutput.length);

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">🔍 Simple Outputs Panel</h3>
      
      <div className="space-y-4">
        <div className="bg-gray-100 p-3 rounded">
          <h4 className="font-semibold">Estado de Conexión</h4>
          <p>Conectado: {isConnected ? '✅ SÍ' : '❌ NO'}</p>
        </div>

        <div className="bg-gray-100 p-3 rounded">
          <h4 className="font-semibold">Plan Actual</h4>
          <p>Título: {currentPlan?.title || 'Sin plan'}</p>
          <p>ID: {currentPlan?.id || 'Sin ID'}</p>
        </div>

        <div className="bg-gray-100 p-3 rounded">
          <h4 className="font-semibold">Plan Steps</h4>
          <p>Total pasos: {planSteps?.length || 0}</p>
          <p>Tipo: {typeof planSteps}</p>
          <p>Es array: {Array.isArray(planSteps) ? 'SÍ' : 'NO'}</p>
        </div>

        <div className="bg-gray-100 p-3 rounded">
          <h4 className="font-semibold">Steps con Output (Filtrados)</h4>
          <p>Total filtrados: {stepsWithOutput.length}</p>
        </div>

        {planSteps && planSteps.length > 0 && (
          <div className="bg-blue-50 p-3 rounded">
            <h4 className="font-semibold">Todos los Pasos (Raw)</h4>
            {planSteps.map((step, index) => (
              <div key={step.id || index} className="border-b py-2">
                <div className="text-sm">
                  <strong>Paso {index + 1}:</strong> {step.title || 'Sin título'}
                </div>
                <div className="text-xs text-gray-600">
                  ID: {step.id} | Status: {step.status || 'sin status'}
                </div>
                <div className="text-xs text-gray-600">
                  Output presente: {step.output ? 'SÍ' : 'NO'} 
                  {step.output && ` (${step.output.length} chars)`}
                </div>
                <div className="text-xs text-gray-600">
                  Output trimmed: {step.output?.trim?.() ? 'SÍ' : 'NO'}
                  {step.output?.trim?.() && ` (${step.output.trim().length} chars)`}
                </div>
                {step.output && (
                  <div className="text-xs bg-gray-200 p-1 mt-1 rounded max-h-20 overflow-y-auto">
                    <strong>Output:</strong> {step.output.substring(0, 200)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {stepsWithOutput.length > 0 && (
          <div className="bg-green-50 p-3 rounded">
            <h4 className="font-semibold">✅ Steps que DEBERÍAN mostrarse</h4>
            {stepsWithOutput.map((step, index) => (
              <div key={step.id || index} className="border-b py-2">
                <div className="text-sm">
                  <strong>Output {index + 1}:</strong> {step.title}
                </div>
                <div className="text-xs text-gray-600">
                  {step.output.length} caracteres
                </div>
                <div className="text-xs bg-white p-1 mt-1 rounded max-h-16 overflow-y-auto">
                  {step.output.substring(0, 150)}...
                </div>
              </div>
            ))}
          </div>
        )}

        {stepsWithOutput.length === 0 && planSteps && planSteps.length > 0 && (
          <div className="bg-red-50 p-3 rounded">
            <h4 className="font-semibold">❌ No hay outputs para mostrar</h4>
            <p>Razón: Ningún paso pasó el filtro de output</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleOutputsPanel;