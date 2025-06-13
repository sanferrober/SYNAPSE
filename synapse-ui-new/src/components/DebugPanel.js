import React from 'react';
import { useSynapse } from '../contexts/SynapseContext';

const DebugPanel = () => {
  const { currentPlan, planSteps, isConnected } = useSynapse();

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-bold mb-4">🐛 Panel de Debug</h3>
      
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold">Estado de Conexión:</h4>
          <p className={isConnected ? 'text-green-600' : 'text-red-600'}>
            {isConnected ? '✅ Conectado' : '❌ Desconectado'}
          </p>
        </div>

        <div>
          <h4 className="font-semibold">Plan Actual:</h4>
          <p>{currentPlan ? currentPlan.title : 'Sin plan activo'}</p>
          {currentPlan && (
            <pre className="text-xs bg-white p-2 rounded mt-2">
              {JSON.stringify(currentPlan, null, 2)}
            </pre>
          )}
        </div>

        <div>
          <h4 className="font-semibold">Pasos del Plan ({planSteps?.length || 0}):</h4>
          {planSteps && planSteps.length > 0 ? (
            <div className="space-y-2">
              {planSteps.map((step, index) => (
                <div key={step.id} className="bg-white p-2 rounded text-xs">
                  <div><strong>ID:</strong> {step.id}</div>
                  <div><strong>Título:</strong> {step.title}</div>
                  <div><strong>Estado:</strong> {step.status}</div>
                  <div><strong>Output:</strong> {step.output ? `${step.output.length} chars` : 'Sin output'}</div>
                  {step.output && (
                    <div className="mt-1">
                      <strong>Preview:</strong>
                      <div className="bg-gray-100 p-1 rounded text-xs max-h-20 overflow-y-auto">
                        {step.output.substring(0, 200)}...
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No hay pasos disponibles</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default DebugPanel;