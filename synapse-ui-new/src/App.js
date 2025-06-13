import React, { useState } from 'react';
import { SynapseProvider, useSynapse } from './contexts/SynapseContext';
import ConversationPanel from './components/ConversationPanel';
import PlanningPanel from './components/PlanningPanel';
import ToolsPanel from './components/ToolsPanel';
import MCPToolsPanel from './components/MCPToolsPanel';
import MemoryPanel from './components/MemoryPanel';
import OutputsPanel from './components/OutputsPanel';
import DebugPanel from './components/DebugPanel';
import LLMSelector from './components/LLMSelector';
import StatusBar from './components/StatusBar';
import {
  MessageSquare,
  Target,
  Wrench,
  Brain,
  Settings,
  FileText,
  Menu,
  X,
  Maximize2,
  Minimize2,
  Bug,
  Cpu
} from 'lucide-react';

// Componente interno que usa el contexto
function AppContent() {
  const [activePanel, setActivePanel] = useState('conversation');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Obtener datos del contexto de Synapse
  const { currentPlan, planSteps } = useSynapse();

  const panels = [
    {
      id: 'conversation',
      name: 'Conversación',
      icon: MessageSquare,
      component: ConversationPanel,
    },
    {
      id: 'planning',
      name: 'Planificación',
      icon: Target,
      component: PlanningPanel,
    },
    {
      id: 'tools',
      name: 'Herramientas',
      icon: Wrench,
      component: ToolsPanel,
    },
    {
      id: 'mcp',
      name: 'MCP Tools',
      icon: Settings,
      component: MCPToolsPanel,
    },
    {
      id: 'outputs',
      name: 'Resultados',
      icon: FileText,
      component: OutputsPanel,
    },
    {
      id: 'memory',
      name: 'Memoria',
      icon: Brain,
      component: MemoryPanel,
    },
    {
      id: 'llm-config',
      name: 'LLM Config',
      icon: Cpu,
      component: LLMSelector,
    },
    {
      id: 'debug',
      name: 'Debug',
      icon: Bug,
      component: DebugPanel,
    },
  ];

  // Función para renderizar el componente activo con las props correctas
  const renderActiveComponent = () => {
    const activeComponentData = panels.find(panel => panel.id === activePanel);
    if (!activeComponentData) return <ConversationPanel />;
    
    const Component = activeComponentData.component;
    
    // Pasar props específicas según el componente
    if (activePanel === 'outputs') {
      return <Component currentPlan={currentPlan} planSteps={planSteps} />;
    }
    
    return <Component />;
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <div className="h-screen bg-secondary-50 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-white border-b border-secondary-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <div className="w-4 h-4 bg-white rounded-sm"></div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">Synapse</h1>
              <p className="text-xs text-secondary-600">Agente de IA Autónomo</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1 bg-secondary-100 rounded-lg p-1">
            {panels.map(({ id, name, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActivePanel(id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                  activePanel === id
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Header Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleFullscreen}
            className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg"
          >
            {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>
          
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="md:hidden p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Mobile Sidebar Overlay */}
        {!sidebarCollapsed && (
          <div className="md:hidden fixed inset-0 z-50 bg-black bg-opacity-50">
            <div className="w-64 h-full bg-white">
              <div className="p-4 border-b border-secondary-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-secondary-900">Navegación</h2>
                  <button
                    onClick={() => setSidebarCollapsed(true)}
                    className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <nav className="p-4 space-y-2">
                {panels.map(({ id, name, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => {
                      setActivePanel(id);
                      setSidebarCollapsed(true);
                    }}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors duration-200 ${
                      activePanel === id
                        ? 'bg-primary-50 text-primary-600 border border-primary-200'
                        : 'text-secondary-700 hover:bg-secondary-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{name}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>
        )}

        {/* Desktop Layout */}
        <div className="flex-1 flex">
          {/* Main Panel */}
          <main className="flex-1 p-4 overflow-hidden">
            <div className="h-full">
              {renderActiveComponent()}
            </div>
          </main>

          {/* Secondary Panel (Desktop only) */}
          <aside className="hidden xl:block w-80 p-4 border-l border-secondary-200 bg-secondary-50">
            <div className="h-full">
              {activePanel === 'conversation' && <PlanningPanel />}
              {activePanel === 'planning' && <ToolsPanel />}
              {activePanel === 'tools' && <MemoryPanel />}
              {activePanel === 'memory' && <ConversationPanel />}
            </div>
          </aside>
        </div>
      </div>

      {/* Status Bar */}
      <StatusBar />
    </div>
  );
}

function App() {
  return (
    <SynapseProvider>
      <AppContent />
    </SynapseProvider>
  );
}

export default App;