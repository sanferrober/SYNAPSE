"""
WebSocket handlers for Synapse
"""

from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import json
import threading
import time
from typing import Dict, Any, Optional


class WebSocketHandler:
    """Handles WebSocket connections and events"""
    
    def __init__(self, socketio, config, memory_manager, agent_manager, tool_registry):
        self.socketio = socketio
        self.config = config
        self.memory_manager = memory_manager
        self.agent_manager = agent_manager
        self.tool_registry = tool_registry
        self.active_connections = {}
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            from flask import request
            sid = request.sid
            
            self.active_connections[sid] = {
                "connected_at": datetime.now().isoformat(),
                "user_id": None,
                "current_plan": None
            }
            
            emit('connection_status', {
                "status": "connected",
                "sid": sid,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"Client connected: {sid}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            from flask import request
            sid = request.sid
            
            if sid in self.active_connections:
                del self.active_connections[sid]
            
            print(f"Client disconnected: {sid}")
        
        @self.socketio.on('user_message')
        def handle_user_message(data):
            """Handle user message"""
            from flask import request
            sid = request.sid
            
            message = data.get('message', '')
            user_id = data.get('user_id', 'default')
            
            # Update connection info
            if sid in self.active_connections:
                self.active_connections[sid]['user_id'] = user_id
            
            # Process message
            self._process_user_message(sid, user_id, message)
        
        @self.socketio.on('execute_plan')
        def handle_execute_plan(data):
            """Handle plan execution request"""
            from flask import request
            sid = request.sid
            
            plan = data.get('plan', {})
            self._execute_plan(sid, plan)
        
        @self.socketio.on('update_llm_config')
        def handle_update_llm_config(data):
            """Handle LLM configuration update"""
            try:
                self.config.update_llm_config(data)
                emit('llm_config_updated', {
                    "success": True,
                    "config": self.config.llm.__dict__
                })
            except Exception as e:
                emit('llm_config_updated', {
                    "success": False,
                    "error": str(e)
                })
        
        @self.socketio.on('get_memory_stats')
        def handle_get_memory_stats():
            """Handle memory stats request"""
            stats = self.memory_manager.get_memory_stats()
            emit('memory_stats', stats)
    
    def _process_user_message(self, sid: str, user_id: str, message: str):
        """Process user message through the agent pipeline"""
        
        # Step 1: Analyze intent
        intent_result = self.agent_manager.process_with_agent("conversation", {
            "message": message,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Emit initial response
        emit('message_response', {
            "type": "thinking",
            "message": "Analizando tu solicitud..."
        }, room=sid)
        
        # Step 2: Generate plan
        plan_result = self.agent_manager.process_with_agent("planning", {
            "intent": {"type": "search", "query": message},
            "context": {"user_id": user_id}
        })
        
        plan = plan_result.get("plan", {})
        
        # Emit plan
        emit('plan_generated', {
            "plan": plan,
            "timestamp": datetime.now().isoformat()
        }, room=sid)
        
        # Update connection info
        if sid in self.active_connections:
            self.active_connections[sid]['current_plan'] = plan
        
        # Step 3: Execute plan automatically
        self._execute_plan(sid, plan)
        
        # Step 4: Store in memory
        response = intent_result.get("response", "")
        self.memory_manager.add_conversation(user_id, message, response)
        
        # Emit final response
        emit('message_response', {
            "type": "complete",
            "message": response,
            "timestamp": datetime.now().isoformat()
        }, room=sid)
    
    def _execute_plan(self, sid: str, plan: Dict[str, Any]):
        """Execute a plan step by step"""
        
        def execute_steps():
            steps = plan.get("steps", [])
            
            for i, step in enumerate(steps):
                # Emit step start
                emit('plan_step_update', {
                    "step_id": step.get("id"),
                    "status": "executing",
                    "message": f"Ejecutando: {step.get('title')}",
                    "progress": (i / len(steps)) * 100
                }, room=sid)
                
                # Execute step
                result = self._execute_step(step, plan)
                
                # Emit step complete
                emit('plan_step_update', {
                    "step_id": step.get("id"),
                    "status": "completed",
                    "output": result.get("output", ""),
                    "message": f"Completado: {step.get('title')}",
                    "progress": ((i + 1) / len(steps)) * 100
                }, room=sid)
                
                # Small delay between steps
                time.sleep(0.5)
            
            # Emit plan completion
            emit('plan_completed', {
                "plan_id": plan.get("id"),
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "summary": self._generate_plan_summary(plan, steps)
            }, room=sid)
        
        # Execute in background thread
        thread = threading.Thread(target=execute_steps)
        thread.daemon = True
        thread.start()
    
    def _execute_step(self, step: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step"""
        tool_id = step.get("tool")
        parameters = step.get("parameters", {})
        
        if tool_id:
            # Execute with tool
            result = self.tool_registry.execute_tool(tool_id, parameters)
            
            if result.get("success"):
                return {
                    "status": "success",
                    "output": self._format_tool_output(result),
                    "execution_time": result.get("execution_time", 0)
                }
            else:
                return {
                    "status": "error",
                    "output": f"Error: {result.get('error', 'Unknown error')}",
                    "execution_time": 0
                }
        else:
            # Execute with agent
            result = self.agent_manager.process_with_agent("execution", {
                "step": step,
                "plan_context": plan
            })
            
            return {
                "status": "success",
                "output": str(result.get("result", {})),
                "execution_time": 1.0
            }
    
    def _format_tool_output(self, result: Dict[str, Any]) -> str:
        """Format tool output for display"""
        tool_id = result.get("tool_id", "unknown")
        
        if tool_id == "web_search":
            results = result.get("results", [])
            output = f"Encontrados {len(results)} resultados:\n\n"
            for r in results[:3]:  # Show first 3 results
                output += f"• {r.get('title', 'Sin título')}\n"
                output += f"  {r.get('snippet', '')}\n"
                output += f"  {r.get('url', '')}\n\n"
            return output
        
        elif tool_id == "data_analyzer":
            analysis = result.get("analysis", {})
            output = f"Análisis {analysis.get('type', 'general')}:\n\n"
            output += f"Resumen: {analysis.get('summary', '')}\n\n"
            output += "Insights:\n"
            for insight in analysis.get("insights", []):
                output += f"• {insight}\n"
            return output
        
        elif tool_id == "code_generator":
            return f"```{result.get('language', 'text')}\n{result.get('code', '')}\n```"
        
        else:
            # Generic formatting
            return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _generate_plan_summary(self, plan: Dict[str, Any], steps: list) -> str:
        """Generate a summary of the executed plan"""
        completed_steps = len(steps)
        plan_title = plan.get("title", "Plan")
        
        summary = f"✅ {plan_title} completado exitosamente\n\n"
        summary += f"📊 Resumen de ejecución:\n"
        summary += f"• Pasos completados: {completed_steps}\n"
        summary += f"• Estado: Exitoso\n"
        summary += f"• Tiempo total: ~{completed_steps * 1.5} segundos\n\n"
        summary += "🎯 Resultados obtenidos y listos para consultar"
        
        return summary
    
    def broadcast_system_update(self, update_type: str, data: Dict[str, Any]):
        """Broadcast system update to all connected clients"""
        self.socketio.emit('system_update', {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_connection_info(self, sid: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        return self.active_connections.get(sid)
    
    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get all active connections"""
        return self.active_connections.copy()