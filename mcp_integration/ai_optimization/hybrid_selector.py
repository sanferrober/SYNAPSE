"""
Integración de Algoritmos Inteligentes con el Selector Automático
================================================================

Este módulo integra los algoritmos avanzados de ML con el selector
automático existente, creando un sistema híbrido que combina
reglas heurísticas con aprendizaje automático.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .automatic_tool_selector import (
    automatic_selector, TaskAnalysis, ToolMetadata, TaskCategory, ToolCapability
)
from .intelligent_algorithms import intelligent_selector, TaskContext

logger = logging.getLogger(__name__)

class HybridIntelligentSelector:
    """
    Selector híbrido que combina reglas heurísticas con ML avanzado
    
    Implementa una estrategia de selección en dos fases:
    1. Filtrado inicial usando reglas heurísticas (rápido, confiable)
    2. Optimización final usando algoritmos de ML (preciso, adaptativo)
    """
    
    def __init__(self):
        self.use_ml_optimization = True
        self.ml_confidence_threshold = 0.6
        self.fallback_to_heuristics = True
        
    async def initialize(self):
        """Inicializa el sistema híbrido"""
        logger.info("Inicializando selector híbrido inteligente...")
        
        # Cargar modelos ML si están disponibles
        if intelligent_selector._load_models():
            logger.info("Modelos ML cargados exitosamente")
        else:
            # Entrenar modelos con datos sintéticos
            await intelligent_selector.train_models()
            logger.info("Modelos ML entrenados con datos sintéticos")
        
        # Registrar herramientas de ejemplo en el selector automático
        await self._register_example_tools()
        
        logger.info("Selector híbrido inicializado")
    
    async def _register_example_tools(self):
        """Registra herramientas de ejemplo para demostración"""
        example_tools = [
            ToolMetadata(
                name="github_mcp",
                capabilities=[ToolCapability.VERSION_CONTROL, ToolCapability.API_INTERACTION],
                task_categories=[TaskCategory.CODE_DEVELOPMENT, TaskCategory.CODE_REVIEW, TaskCategory.DEPLOYMENT],
                success_rate=0.85,
                average_execution_time=12.0,
                resource_usage={'cpu': 25, 'memory': 30, 'network': 15},
                reliability_score=0.90,
                last_updated=datetime.now(),
                configuration_complexity=6
            ),
            ToolMetadata(
                name="vscode_mcp",
                capabilities=[ToolCapability.CODE_EXECUTION, ToolCapability.FILE_MANAGEMENT, ToolCapability.TEXT_PROCESSING],
                task_categories=[TaskCategory.CODE_DEVELOPMENT, TaskCategory.CODE_REVIEW, TaskCategory.DOCUMENTATION],
                success_rate=0.92,
                average_execution_time=8.0,
                resource_usage={'cpu': 35, 'memory': 45, 'network': 5},
                reliability_score=0.95,
                last_updated=datetime.now(),
                configuration_complexity=4
            ),
            ToolMetadata(
                name="docker_mcp",
                capabilities=[ToolCapability.CONTAINER_MANAGEMENT, ToolCapability.SYSTEM_MONITORING],
                task_categories=[TaskCategory.DEPLOYMENT, TaskCategory.TESTING, TaskCategory.SYSTEM_ADMINISTRATION],
                success_rate=0.78,
                average_execution_time=18.0,
                resource_usage={'cpu': 45, 'memory': 60, 'network': 25},
                reliability_score=0.85,
                last_updated=datetime.now(),
                configuration_complexity=8
            ),
            ToolMetadata(
                name="database_mcp",
                capabilities=[ToolCapability.DATABASE_ACCESS, ToolCapability.DATA_ANALYSIS],
                task_categories=[TaskCategory.DATA_ANALYSIS, TaskCategory.SYSTEM_ADMINISTRATION],
                success_rate=0.88,
                average_execution_time=10.0,
                resource_usage={'cpu': 20, 'memory': 40, 'network': 30},
                reliability_score=0.92,
                last_updated=datetime.now(),
                configuration_complexity=5
            )
        ]
        
        for tool in example_tools:
            automatic_selector.register_tool(tool)
        
        logger.info(f"Registradas {len(example_tools)} herramientas de ejemplo")
    
    async def select_tools_intelligently(self, task_analysis: TaskAnalysis,
                                       user_context: Optional[Dict] = None) -> List[str]:
        """
        Selecciona herramientas usando el enfoque híbrido inteligente
        
        Args:
            task_analysis: Análisis de la tarea
            user_context: Contexto adicional del usuario
            
        Returns:
            List[str]: Lista de herramientas seleccionadas
        """
        logger.info(f"Iniciando selección híbrida para: {task_analysis.detected_category.value}")
        
        try:
            # Fase 1: Filtrado heurístico inicial
            candidate_tools = await self._heuristic_filtering(task_analysis, user_context)
            
            if not candidate_tools:
                logger.warning("No se encontraron herramientas candidatas")
                return []
            
            # Fase 2: Optimización con ML (si está habilitada y disponible)
            if self.use_ml_optimization and len(candidate_tools) > 1:
                optimized_tools = await self._ml_optimization(
                    task_analysis, candidate_tools, user_context
                )
                
                if optimized_tools:
                    logger.info(f"Selección optimizada con ML: {optimized_tools}")
                    return optimized_tools
            
            # Fallback a selección heurística
            if self.fallback_to_heuristics:
                heuristic_selection = await automatic_selector.select_tools_automatically(
                    task_analysis, user_context
                )
                logger.info(f"Selección heurística: {heuristic_selection}")
                return heuristic_selection
            
            return candidate_tools[:2]  # Máximo 2 herramientas por defecto
            
        except Exception as e:
            logger.error(f"Error en selección híbrida: {e}")
            # Fallback de emergencia
            return await automatic_selector.select_tools_automatically(task_analysis, user_context)
    
    async def _heuristic_filtering(self, task_analysis: TaskAnalysis,
                                 user_context: Optional[Dict]) -> List[str]:
        """Fase 1: Filtrado inicial usando reglas heurísticas"""
        # Usar el selector automático existente para filtrado inicial
        candidate_tools = await automatic_selector.select_tools_automatically(
            task_analysis, user_context
        )
        
        # Expandir candidatos basándose en capacidades requeridas
        all_tools = list(automatic_selector.tool_registry.keys())
        
        for tool_name in all_tools:
            if tool_name not in candidate_tools:
                metadata = automatic_selector.tool_registry[tool_name]
                
                # Verificar si la herramienta tiene capacidades relevantes
                if any(cap in metadata.capabilities for cap in task_analysis.required_capabilities):
                    candidate_tools.append(tool_name)
        
        # Limitar a máximo 6 candidatos para eficiencia
        return candidate_tools[:6]
    
    async def _ml_optimization(self, task_analysis: TaskAnalysis,
                             candidate_tools: List[str],
                             user_context: Optional[Dict]) -> Optional[List[str]]:
        """Fase 2: Optimización usando algoritmos de ML"""
        try:
            # Crear contexto enriquecido para ML
            task_context = self._create_task_context(task_analysis, user_context)
            
            # Usar algoritmos inteligentes para selección óptima
            optimal_tools = await intelligent_selector.select_optimal_tools(
                task_analysis, candidate_tools, task_context
            )
            
            return optimal_tools
            
        except Exception as e:
            logger.warning(f"Error en optimización ML: {e}")
            return None
    
    def _create_task_context(self, task_analysis: TaskAnalysis,
                           user_context: Optional[Dict]) -> TaskContext:
        """Crea contexto enriquecido para algoritmos ML"""
        return TaskContext(
            user_id=user_context.get('user_id', 'anonymous') if user_context else 'anonymous',
            project_type=user_context.get('project_type', 'general') if user_context else 'general',
            urgency_level=task_analysis.urgency_level,
            complexity_score=task_analysis.complexity_score,
            similar_tasks_history=user_context.get('recent_tasks', []) if user_context else [],
            available_resources={
                'cpu': 70.0,  # Asumir recursos disponibles
                'memory': 60.0,
                'network': 80.0
            },
            time_constraints=task_analysis.estimated_duration,
            quality_requirements=0.8  # Calidad alta por defecto
        )
    
    async def record_execution_feedback(self, task_analysis: TaskAnalysis,
                                      selected_tools: List[str],
                                      execution_result: Dict[str, Any]):
        """Registra feedback de ejecución para aprendizaje continuo"""
        success = execution_result.get('status') == 'completed'
        execution_time = execution_result.get('execution_time', 0)
        
        # Actualizar métricas en el selector automático
        for tool_name in selected_tools:
            automatic_selector.update_tool_performance(
                tool_name=tool_name,
                success=success,
                execution_time=execution_time / len(selected_tools),  # Dividir tiempo entre herramientas
                resource_usage=execution_result.get('resource_usage', {})
            )
        
        # Registrar en algoritmos inteligentes para ML
        if self.use_ml_optimization:
            await intelligent_selector.record_execution_result(
                task_analysis=task_analysis,
                selected_tools=selected_tools,
                success=success,
                execution_time=execution_time,
                user_feedback=execution_result.get('user_feedback')
            )
        
        logger.info(f"Feedback registrado - Éxito: {success}, Tiempo: {execution_time:.1f}min")
    
    async def get_selection_explanation(self, task_analysis: TaskAnalysis,
                                      selected_tools: List[str]) -> str:
        """Genera explicación de la selección para transparencia administrativa"""
        explanation = await automatic_selector.get_tool_recommendations_explanation(
            task_analysis, selected_tools
        )
        
        # Añadir información sobre optimización ML
        if self.use_ml_optimization:
            explanation += f"""

Optimización con Machine Learning:
- Algoritmos ML habilitados: Sí
- Modelos utilizados: Predictor de éxito, Predictor de tiempo, Recomendador de herramientas
- Enfoque híbrido: Filtrado heurístico + Optimización ML
- Confianza ML: {self.ml_confidence_threshold}
"""
        
        return explanation
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema híbrido"""
        return {
            'ml_optimization_enabled': self.use_ml_optimization,
            'ml_confidence_threshold': self.ml_confidence_threshold,
            'fallback_enabled': self.fallback_to_heuristics,
            'registered_tools': len(automatic_selector.tool_registry),
            'learning_enabled': intelligent_selector.learning_enabled,
            'performance_history_size': len(intelligent_selector.performance_history),
            'model_version': intelligent_selector.model_version
        }

# Instancia global del selector híbrido
hybrid_selector = HybridIntelligentSelector()

