"""
Agent management system for Synapse
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, config):
        self.name = name
        self.config = config
        self.llm_model = config.get_llm_for_agent(name)
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        pass
    
    def get_llm_model(self) -> str:
        """Get the LLM model for this agent"""
        return self.llm_model


class ConversationAgent(BaseAgent):
    """Handles user conversations"""
    
    def __init__(self, config):
        super().__init__("conversation", config)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversation input"""
        message = input_data.get("message", "")
        context = input_data.get("context", {})
        
        # Simulate conversation processing
        response = self._generate_response(message, context)
        
        return {
            "response": response,
            "metadata": {
                "agent": self.name,
                "model": self.llm_model,
                "processed_at": input_data.get("timestamp")
            }
        }
    
    def _generate_response(self, message: str, context: Dict) -> str:
        """Generate response based on message and context"""
        # This would integrate with actual LLM
        return f"Procesando mensaje con {self.llm_model}: {message}"


class PlanningAgent(BaseAgent):
    """Handles plan generation"""
    
    def __init__(self, config):
        super().__init__("planning", config)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan"""
        intent = input_data.get("intent", {})
        context = input_data.get("context", {})
        
        plan = self._generate_plan(intent, context)
        
        return {
            "plan": plan,
            "metadata": {
                "agent": self.name,
                "model": self.llm_model,
                "total_steps": len(plan.get("steps", []))
            }
        }
    
    def _generate_plan(self, intent: Dict, context: Dict) -> Dict[str, Any]:
        """Generate execution plan based on intent"""
        # Simplified plan generation
        steps = []
        
        if intent.get("type") == "search":
            steps = [
                {
                    "id": "step_1",
                    "title": "Búsqueda Web",
                    "description": "Buscar información relevante",
                    "tool": "web_search_mcp",
                    "parameters": {"query": intent.get("query", "")}
                },
                {
                    "id": "step_2",
                    "title": "Análisis de Resultados",
                    "description": "Analizar y filtrar resultados",
                    "tool": "data_analyzer",
                    "parameters": {}
                }
            ]
        
        return {
            "id": f"plan_{hash(str(intent))}",
            "title": f"Plan para: {intent.get('query', 'Tarea')}",
            "steps": steps,
            "status": "pending"
        }


class ExecutionAgent(BaseAgent):
    """Handles plan execution"""
    
    def __init__(self, config):
        super().__init__("execution", config)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plan step"""
        step = input_data.get("step", {})
        plan_context = input_data.get("plan_context", {})
        
        result = self._execute_step(step, plan_context)
        
        return {
            "result": result,
            "metadata": {
                "agent": self.name,
                "model": self.llm_model,
                "step_id": step.get("id")
            }
        }
    
    def _execute_step(self, step: Dict, context: Dict) -> Dict[str, Any]:
        """Execute a single step"""
        tool = step.get("tool")
        parameters = step.get("parameters", {})
        
        # This would call actual tool execution
        return {
            "status": "completed",
            "output": f"Ejecutado {tool} con parámetros {parameters}",
            "execution_time": 1.5
        }


class AnalysisAgent(BaseAgent):
    """Handles result analysis"""
    
    def __init__(self, config):
        super().__init__("analysis", config)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze execution results"""
        results = input_data.get("results", [])
        context = input_data.get("context", {})
        
        analysis = self._analyze_results(results, context)
        
        return {
            "analysis": analysis,
            "metadata": {
                "agent": self.name,
                "model": self.llm_model,
                "results_analyzed": len(results)
            }
        }
    
    def _analyze_results(self, results: List[Dict], context: Dict) -> Dict[str, Any]:
        """Analyze results and provide insights"""
        return {
            "summary": "Análisis completado",
            "insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Recomendación 1"],
            "confidence": 0.85
        }


class MemoryAgent(BaseAgent):
    """Handles memory operations"""
    
    def __init__(self, config, memory_manager):
        super().__init__("memory", config)
        self.memory_manager = memory_manager
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process memory operations"""
        operation = input_data.get("operation", "retrieve")
        data = input_data.get("data", {})
        
        if operation == "store":
            return self._store_memory(data)
        elif operation == "retrieve":
            return self._retrieve_memory(data)
        elif operation == "analyze":
            return self._analyze_memory(data)
        
        return {"error": "Unknown operation"}
    
    def _store_memory(self, data: Dict) -> Dict[str, Any]:
        """Store data in memory"""
        memory_type = data.get("type", "conversation")
        
        if memory_type == "conversation":
            self.memory_manager.add_conversation(
                data.get("user_id", "default"),
                data.get("message", ""),
                data.get("response", "")
            )
        elif memory_type == "pattern":
            self.memory_manager.add_learned_pattern(data.get("pattern", {}))
        
        return {"status": "stored", "type": memory_type}
    
    def _retrieve_memory(self, data: Dict) -> Dict[str, Any]:
        """Retrieve data from memory"""
        memory_type = data.get("type", "conversation")
        
        if memory_type == "conversation":
            return {
                "data": self.memory_manager.get_recent_conversations(
                    data.get("user_id"),
                    data.get("limit", 10)
                )
            }
        elif memory_type == "preferences":
            return {
                "data": self.memory_manager.get_user_preferences(
                    data.get("user_id", "default")
                )
            }
        
        return {"data": []}
    
    def _analyze_memory(self, data: Dict) -> Dict[str, Any]:
        """Analyze memory patterns"""
        stats = self.memory_manager.get_memory_stats()
        patterns = self.memory_manager.get_learned_patterns()
        
        return {
            "stats": stats,
            "patterns_summary": {
                "total": len(patterns),
                "by_type": self._group_patterns_by_type(patterns)
            }
        }
    
    def _group_patterns_by_type(self, patterns: List[Dict]) -> Dict[str, int]:
        """Group patterns by type"""
        grouped = {}
        for pattern in patterns:
            pattern_type = pattern.get("type", "unknown")
            grouped[pattern_type] = grouped.get(pattern_type, 0) + 1
        return grouped


class OptimizationAgent(BaseAgent):
    """Handles system optimization"""
    
    def __init__(self, config):
        super().__init__("optimization", config)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system performance"""
        metrics = input_data.get("metrics", {})
        target = input_data.get("target", "efficiency")
        
        optimizations = self._generate_optimizations(metrics, target)
        
        return {
            "optimizations": optimizations,
            "metadata": {
                "agent": self.name,
                "model": self.llm_model,
                "target": target
            }
        }
    
    def _generate_optimizations(self, metrics: Dict, target: str) -> List[Dict]:
        """Generate optimization recommendations"""
        optimizations = []
        
        if target == "efficiency":
            if metrics.get("avg_response_time", 0) > 2.0:
                optimizations.append({
                    "type": "performance",
                    "recommendation": "Implementar caché para respuestas frecuentes",
                    "impact": "high"
                })
        
        return optimizations


class AgentManager:
    """Manages all agents in the system"""
    
    def __init__(self, config, memory_manager):
        self.config = config
        self.memory_manager = memory_manager
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all agents"""
        return {
            "conversation": ConversationAgent(self.config),
            "planning": PlanningAgent(self.config),
            "execution": ExecutionAgent(self.config),
            "analysis": AnalysisAgent(self.config),
            "memory": MemoryAgent(self.config, self.memory_manager),
            "optimization": OptimizationAgent(self.config)
        }
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get agent by type"""
        return self.agents.get(agent_type)
    
    def process_with_agent(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input with specific agent"""
        agent = self.get_agent(agent_type)
        if not agent:
            return {"error": f"Agent {agent_type} not found"}
        
        try:
            return agent.process(input_data)
        except Exception as e:
            return {"error": str(e), "agent": agent_type}
    
    def get_all_agents_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all agents"""
        return {
            name: {
                "type": agent.name,
                "model": agent.llm_model,
                "class": agent.__class__.__name__
            }
            for name, agent in self.agents.items()
        }