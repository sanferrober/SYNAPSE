import React from 'react';
import { useSynapse } from '../contexts/SynapseContext';

const SimpleDebugPanel = () => {
  const { currentPlan, planSteps, isConnected } = useSynapse();

  console.log('🔍 SimpleDebugPanel - Estado actual:');
  console.log('   isConnected:', isConnected);
  console.log('   currentPlan:', currentPlan);
  console.log('   planSteps:', planSteps);
  console.log('   planSteps length:', planSteps?.length || 0);
  
  if (planSteps && planSteps.length > 0) {
    planSteps.forEach((step, index) => {
      console.log(`   Step ${index + 1}:`, {
        id: step.id,
        title: step.title,
        status: step.status,
        hasOutput: !!step.output,
        outputLength: step.output?.length || 0
      });
    });
  }

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-bold mb-4">🔍 Debug Simple</h3>
      
      <div className="space-y-2">
        <div>
          <strong>Conexión:</strong> {isConnected ? '✅ Conectado' : '❌ Desconectado'}
        </div>
        
        <div>
          <strong>Plan actual:</strong> {currentPlan?.title || 'Sin plan'}
        </div>
        
        <div>
          <strong>Total pasos:</strong> {planSteps?.length || 0}
        </div>
        
        {planSteps && planSteps.length > 0 && (
          <div>
            <strong>Pasos:</strong>
            <ul className="ml-4 mt-2">
              {planSteps.map((step, index) => (
                <li key={step.id || index} className="mb-2">
                  <div className="text-sm">
                    <strong>Paso {index + 1}:</strong> {step.title}
                  </div>
                  <div className="text-xs text-gray-600">
                    Status: {step.status} | 
                    Output: {step.output ? `SÍ (${step.output.length} chars)` : 'NO'}
                  </div>
                  {step.output && (
                    <div className="text-xs bg-gray-200 p-2 mt-1 rounded">
                      {step.output.substring(0, 200)}...
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleDebugPanel;