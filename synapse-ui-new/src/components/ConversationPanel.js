import React, { useState, useRef, useEffect } from 'react';
import { useSynapse } from '../contexts/SynapseContext';
import { Send, Loader2, User, Bot, AlertCircle, CheckCircle, Clock } from 'lucide-react';

const ConversationPanel = () => {
  const {
    messages,
    isProcessing,
    sendMessage,
    planStatus,
  } = useSynapse();

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll al final de los mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Enfocar input cuando no esté procesando
  useEffect(() => {
    if (!isProcessing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isProcessing]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isProcessing) {
      sendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const getMessageIcon = (sender, status) => {
    if (sender === 'user') {
      return <User className="w-5 h-5 text-primary-600" />;
    }
    
    switch (status) {
      case 'processing':
        return <Loader2 className="w-5 h-5 text-warning-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-error-600" />;
      default:
        return <Bot className="w-5 h-5 text-primary-600" />;
    }
  };

  const getStatusIndicator = () => {
    switch (planStatus) {
      case 'generating':
        return (
          <div className="flex items-center space-x-2 text-warning-600">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Generando plan...</span>
          </div>
        );
      case 'executing':
        return (
          <div className="flex items-center space-x-2 text-primary-600">
            <Clock className="w-4 h-4" />
            <span className="text-sm">Ejecutando plan...</span>
          </div>
        );
      case 'completed':
        return (
          <div className="flex items-center space-x-2 text-success-600">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">Plan completado</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex items-center space-x-2 text-error-600">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Error en ejecución</span>
          </div>
        );
      default:
        return null;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-secondary-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-secondary-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-secondary-900">Synapse</h2>
            <p className="text-sm text-secondary-600">Agente de IA Autónomo</p>
          </div>
        </div>
        {getStatusIndicator()}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              ¡Hola! Soy Synapse
            </h3>
            <p className="text-secondary-600 max-w-md">
              Soy tu agente de IA autónomo. Puedo ayudarte con tareas complejas,
              análisis de datos, desarrollo de aplicaciones y mucho más.
              ¿En qué puedo ayudarte hoy?
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className="flex-shrink-0">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user'
                    ? 'bg-secondary-100'
                    : 'bg-gradient-to-r from-primary-500 to-primary-600'
                }`}>
                  {getMessageIcon(message.sender, message.status)}
                </div>
              </div>
              <div className={`flex-1 max-w-3xl ${
                message.sender === 'user' ? 'text-right' : ''
              }`}>
                <div className={`inline-block p-3 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-secondary-100 text-secondary-900'
                }`}>
                  <p className="whitespace-pre-wrap">{message.content || message.text}</p>
                </div>
                <div className={`mt-1 text-xs text-secondary-500 ${
                  message.sender === 'user' ? 'text-right' : ''
                }`}>
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))
        )}
        
        {/* Indicador de procesamiento */}
        {isProcessing && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                <Loader2 className="w-5 h-5 text-white animate-spin" />
              </div>
            </div>
            <div className="flex-1">
              <div className="inline-block p-3 rounded-lg bg-secondary-100">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-secondary-600">Synapse está pensando...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-secondary-200">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje aquí..."
              className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-colors duration-200"
              rows="1"
              disabled={isProcessing}
              style={{
                minHeight: '48px',
                maxHeight: '120px',
                resize: 'none',
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isProcessing}
            className="flex-shrink-0 w-12 h-12 bg-primary-600 hover:bg-primary-700 disabled:bg-secondary-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors duration-200 flex items-center justify-center"
          >
            {isProcessing ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        
        <div className="mt-2 text-xs text-secondary-500 text-center">
          Presiona Enter para enviar, Shift+Enter para nueva línea
        </div>
      </div>
    </div>
  );
};

export default ConversationPanel;

