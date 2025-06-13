"""
Arquitectura de IA Integrada para Sistema MCP
Implementa la infraestructura principal para integrar sistemas de IA en Synapse
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import sqlite3
from pathlib import Path
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import pickle

# Importar sistemas de IA desarrollados
from .ml_optimization_system import (
    MLOptimizationManager, 
    ToolUsageMetrics, 
    OptimizationRecommendation,
    DEFAULT_ML_CONFIG
)
from .recommendation_system import (
    HybridRecommendationEngine,
    ToolProfile,
    TaskProfile,
    UserProfile,
    RecommendationResult,
    DEFAULT_RECOMMENDATION_CONFIG
)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AISystemConfig:
    """Configuración para sistemas de IA"""
    ml_optimization_config: Dict[str, Any]
    recommendation_config: Dict[str, Any]
    ai_coordinator_config: Dict[str, Any]
    performance_monitoring_config: Dict[str, Any]
    data_pipeline_config: Dict[str, Any]

@dataclass
class AIInsight:
    """Insight generado por sistemas de IA"""
    insight_id: str
    insight_type: str  # 'optimization', 'recommendation', 'pattern', 'anomaly'
    title: str
    description: str
    confidence_score: float
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    actionable_items: List[str]
    supporting_data: Dict[str, Any]
    generated_by: str
    timestamp: datetime
    expires_at: Optional[datetime]

@dataclass
class AIPerformanceMetrics:
    """Métricas de rendimiento de sistemas de IA"""
    system_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    response_time_ms: float
    throughput_per_second: float
    resource_usage: Dict[str, float]
    error_rate: float
    user_satisfaction: float
    timestamp: datetime

class AICoordinator:
    """Coordinador principal de sistemas de IA para MCP"""
    
    def __init__(self, config: AISystemConfig):
        self.config = config
        self.ml_optimization_manager = None
        self.recommendation_engine = None
        self.performance_monitor = None
        self.data_pipeline = None
        self.insight_generator = None
        self.is_initialized = False
        self.active_tasks = {}
        self.ai_insights = []
        self.performance_metrics = {}
        
        # Threading para operaciones asíncronas
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
    async def initialize(self) -> None:
        """Inicializa todos los componentes de IA"""
        try:
            logger.info("Inicializando coordinador de IA para sistema MCP...")
            
            # Inicializar gestor de optimización ML
            self.ml_optimization_manager = MLOptimizationManager(
                self.config.ml_optimization_config
            )
            await self.ml_optimization_manager.initialize()
            
            # Inicializar motor de recomendación
            self.recommendation_engine = HybridRecommendationEngine(
                self.config.recommendation_config
            )
            
            # Inicializar monitor de rendimiento
            self.performance_monitor = AIPerformanceMonitor(
                self.config.performance_monitoring_config
            )
            await self.performance_monitor.initialize()
            
            # Inicializar pipeline de datos
            self.data_pipeline = AIDataPipeline(
                self.config.data_pipeline_config
            )
            await self.data_pipeline.initialize()
            
            # Inicializar generador de insights
            self.insight_generator = AIInsightGenerator(
                self.config.ai_coordinator_config.get('insight_generation', {})
            )
            
            # Iniciar tareas de fondo
            await self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("Coordinador de IA inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando coordinador de IA: {e}")
            raise
    
    async def _start_background_tasks(self) -> None:
        """Inicia tareas de fondo para monitoreo y optimización"""
        # Tarea de monitoreo de rendimiento
        asyncio.create_task(self._performance_monitoring_loop())
        
        # Tarea de generación de insights
        asyncio.create_task(self._insight_generation_loop())
        
        # Tarea de limpieza de datos
        asyncio.create_task(self._data_cleanup_loop())
        
        logger.info("Tareas de fondo de IA iniciadas")
    
    async def get_tool_recommendation(self, task_description: str, user_context: Dict[str, Any],
                                    available_tools: List[str]) -> RecommendationResult:
        """Obtiene recomendación de herramientas para una tarea"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Crear perfil de tarea
            task_profile = await self._create_task_profile(task_description, user_context)
            
            # Crear perfil de usuario
            user_profile = await self._create_user_profile(user_context)
            
            # Obtener herramientas disponibles
            tool_profiles = await self._get_tool_profiles(available_tools)
            
            # Entrenar motor si es necesario
            if not self.recommendation_engine.is_trained:
                await self._train_recommendation_engine(tool_profiles, [task_profile], [user_profile])
            
            # Generar recomendación
            recommendation = await self.recommendation_engine.recommend(
                task_profile, user_profile, available_tools
            )
            
            # Registrar métricas
            await self._record_recommendation_metrics(recommendation)
            
            # Generar insight si es relevante
            await self._generate_recommendation_insight(recommendation, task_profile)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendación de herramientas: {e}")
            raise
    
    async def get_optimization_recommendation(self, tool_id: str, context: Dict[str, Any],
                                           optimization_type: str = 'bayesian') -> OptimizationRecommendation:
        """Obtiene recomendación de optimización para una herramienta"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Obtener recomendación de optimización
            recommendation = await self.ml_optimization_manager.get_optimization_recommendation(
                tool_id, context, optimization_type
            )
            
            # Registrar métricas
            await self._record_optimization_metrics(recommendation)
            
            # Generar insight si es relevante
            await self._generate_optimization_insight(recommendation, context)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendación de optimización: {e}")
            raise
    
    async def update_with_feedback(self, feedback: Dict[str, Any]) -> None:
        """Actualiza sistemas de IA con feedback del usuario"""
        try:
            if not self.is_initialized:
                return
            
            # Actualizar gestor de optimización ML
            await self.ml_optimization_manager.update_with_feedback(feedback)
            
            # Actualizar motor de recomendación
            await self.recommendation_engine.update_model(feedback)
            
            # Registrar feedback en pipeline de datos
            await self.data_pipeline.record_feedback(feedback)
            
            # Generar insight sobre feedback si es relevante
            await self._generate_feedback_insight(feedback)
            
            logger.info(f"Sistemas de IA actualizados con feedback para herramienta {feedback.get('tool_id')}")
            
        except Exception as e:
            logger.error(f"Error actualizando sistemas de IA con feedback: {e}")
    
    async def get_ai_insights(self, insight_types: Optional[List[str]] = None,
                            max_insights: int = 10) -> List[AIInsight]:
        """Obtiene insights generados por sistemas de IA"""
        try:
            # Filtrar insights por tipo si se especifica
            filtered_insights = self.ai_insights
            
            if insight_types:
                filtered_insights = [
                    insight for insight in self.ai_insights 
                    if insight.insight_type in insight_types
                ]
            
            # Filtrar insights expirados
            current_time = datetime.now()
            active_insights = [
                insight for insight in filtered_insights
                if insight.expires_at is None or insight.expires_at > current_time
            ]
            
            # Ordenar por relevancia (combinación de confianza e impacto)
            impact_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            
            def insight_score(insight):
                impact_weight = impact_weights.get(insight.impact_level, 1)
                return insight.confidence_score * impact_weight
            
            sorted_insights = sorted(active_insights, key=insight_score, reverse=True)
            
            return sorted_insights[:max_insights]
            
        except Exception as e:
            logger.error(f"Error obteniendo insights de IA: {e}")
            return []
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas de rendimiento de sistemas de IA"""
        try:
            analytics = {}
            
            # Analíticas de optimización ML
            if self.ml_optimization_manager:
                ml_analytics = await self.ml_optimization_manager.get_performance_analytics()
                analytics['ml_optimization'] = ml_analytics
            
            # Analíticas de recomendación
            if self.recommendation_engine:
                rec_analytics = await self._get_recommendation_analytics()
                analytics['recommendation_system'] = rec_analytics
            
            # Métricas de rendimiento general
            if self.performance_monitor:
                perf_metrics = await self.performance_monitor.get_current_metrics()
                analytics['performance_metrics'] = perf_metrics
            
            # Estadísticas de insights
            insight_stats = await self._get_insight_statistics()
            analytics['ai_insights'] = insight_stats
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas de rendimiento: {e}")
            return {}
    
    async def _create_task_profile(self, task_description: str, context: Dict[str, Any]) -> TaskProfile:
        """Crea perfil de tarea desde descripción y contexto"""
        # Análisis simple de la descripción para extraer características
        task_type = context.get('task_type', 'general')
        domain = context.get('domain', 'general')
        complexity = context.get('complexity_level', 'medium')
        
        # Extraer capacidades requeridas (simplificado)
        required_capabilities = []
        if 'git' in task_description.lower() or 'repository' in task_description.lower():
            required_capabilities.append('version_control')
        if 'docker' in task_description.lower() or 'container' in task_description.lower():
            required_capabilities.append('container_management')
        if 'code' in task_description.lower() or 'programming' in task_description.lower():
            required_capabilities.append('code_execution')
        
        return TaskProfile(
            task_id=f"task_{int(time.time())}",
            description=task_description,
            task_type=task_type,
            domain=domain,
            complexity_level=complexity,
            required_capabilities=required_capabilities,
            input_data_types=context.get('input_types', ['text']),
            expected_output_types=context.get('output_types', ['result']),
            performance_requirements=context.get('performance_requirements', {}),
            context=context,
            user_preferences=context.get('user_preferences', {}),
            timestamp=datetime.now()
        )
    
    async def _create_user_profile(self, context: Dict[str, Any]) -> UserProfile:
        """Crea perfil de usuario desde contexto"""
        user_id = context.get('user_id', 'anonymous')
        
        return UserProfile(
            user_id=user_id,
            skill_level=context.get('skill_level', 'intermediate'),
            preferred_tools=context.get('preferred_tools', []),
            domain_expertise=context.get('domain_expertise', []),
            usage_patterns=context.get('usage_patterns', {}),
            tool_ratings=context.get('tool_ratings', {}),
            collaboration_preferences=context.get('collaboration_preferences', {}),
            learning_style=context.get('learning_style', 'hands_on'),
            productivity_metrics=context.get('productivity_metrics', {}),
            last_active=datetime.now()
        )
    
    async def _get_tool_profiles(self, tool_ids: List[str]) -> List[ToolProfile]:
        """Obtiene perfiles de herramientas desde IDs"""
        # En implementación real, esto vendría de la base de datos
        tool_profiles = []
        
        for tool_id in tool_ids:
            # Crear perfil básico (en implementación real, cargar desde BD)
            profile = ToolProfile(
                tool_id=tool_id,
                name=tool_id.replace('_', ' ').title(),
                description=f"Herramienta MCP: {tool_id}",
                categories=['general'],
                capabilities=['general_purpose'],
                input_types=['text'],
                output_types=['result'],
                complexity_score=2.0,
                resource_requirements={'cpu': 0.5, 'memory': 1.0},
                compatibility_matrix={},
                performance_metrics={'success_rate': 0.8, 'avg_execution_time': 30.0},
                user_ratings=[4.0],
                usage_frequency=10,
                last_updated=datetime.now()
            )
            tool_profiles.append(profile)
        
        return tool_profiles
    
    async def _train_recommendation_engine(self, tools: List[ToolProfile], 
                                         tasks: List[TaskProfile], 
                                         users: List[UserProfile]) -> None:
        """Entrena motor de recomendación con datos disponibles"""
        try:
            await self.recommendation_engine.train(tools, tasks, users)
            logger.info("Motor de recomendación entrenado")
        except Exception as e:
            logger.warning(f"Error entrenando motor de recomendación: {e}")
    
    async def _record_recommendation_metrics(self, recommendation: RecommendationResult) -> None:
        """Registra métricas de recomendación"""
        try:
            metrics = AIPerformanceMetrics(
                system_name='recommendation_engine',
                accuracy=np.mean(recommendation.confidence_scores) if recommendation.confidence_scores else 0.0,
                precision=0.0,  # Se calculará con feedback
                recall=0.0,     # Se calculará con feedback
                f1_score=0.0,   # Se calculará con feedback
                response_time_ms=100.0,  # Placeholder
                throughput_per_second=10.0,  # Placeholder
                resource_usage={'cpu': 0.1, 'memory': 0.2},
                error_rate=0.0,
                user_satisfaction=0.0,  # Se actualizará con feedback
                timestamp=datetime.now()
            )
            
            await self.performance_monitor.record_metrics(metrics)
            
        except Exception as e:
            logger.warning(f"Error registrando métricas de recomendación: {e}")
    
    async def _record_optimization_metrics(self, recommendation: OptimizationRecommendation) -> None:
        """Registra métricas de optimización"""
        try:
            metrics = AIPerformanceMetrics(
                system_name='ml_optimization',
                accuracy=recommendation.confidence_score,
                precision=0.0,  # Se calculará con feedback
                recall=0.0,     # Se calculará con feedback
                f1_score=0.0,   # Se calculará con feedback
                response_time_ms=50.0,  # Placeholder
                throughput_per_second=20.0,  # Placeholder
                resource_usage={'cpu': 0.2, 'memory': 0.3},
                error_rate=0.0,
                user_satisfaction=0.0,  # Se actualizará con feedback
                timestamp=datetime.now()
            )
            
            await self.performance_monitor.record_metrics(metrics)
            
        except Exception as e:
            logger.warning(f"Error registrando métricas de optimización: {e}")
    
    async def _generate_recommendation_insight(self, recommendation: RecommendationResult, 
                                             task: TaskProfile) -> None:
        """Genera insight basado en recomendación"""
        try:
            if not recommendation.recommended_tools:
                return
            
            # Generar insight si la confianza es baja
            avg_confidence = np.mean(recommendation.confidence_scores)
            
            if avg_confidence < 0.5:
                insight = AIInsight(
                    insight_id=f"rec_insight_{int(time.time())}",
                    insight_type='recommendation',
                    title='Baja Confianza en Recomendaciones',
                    description=f"Las recomendaciones para la tarea '{task.task_type}' tienen baja confianza promedio ({avg_confidence:.2f})",
                    confidence_score=0.8,
                    impact_level='medium',
                    actionable_items=[
                        'Considerar entrenar el modelo con más datos',
                        'Revisar la descripción de la tarea para mayor claridad',
                        'Verificar disponibilidad de herramientas apropiadas'
                    ],
                    supporting_data={
                        'avg_confidence': avg_confidence,
                        'task_type': task.task_type,
                        'num_recommendations': len(recommendation.recommended_tools)
                    },
                    generated_by='recommendation_analyzer',
                    timestamp=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=24)
                )
                
                self.ai_insights.append(insight)
                
        except Exception as e:
            logger.warning(f"Error generando insight de recomendación: {e}")
    
    async def _generate_optimization_insight(self, recommendation: OptimizationRecommendation,
                                           context: Dict[str, Any]) -> None:
        """Genera insight basado en optimización"""
        try:
            if recommendation.expected_improvement > 0.2:
                insight = AIInsight(
                    insight_id=f"opt_insight_{int(time.time())}",
                    insight_type='optimization',
                    title='Oportunidad de Optimización Significativa',
                    description=f"Se detectó una oportunidad de mejora del {recommendation.expected_improvement:.1%} para la herramienta {recommendation.tool_id}",
                    confidence_score=recommendation.confidence_score,
                    impact_level='high' if recommendation.expected_improvement > 0.5 else 'medium',
                    actionable_items=[
                        f'Aplicar configuración recomendada: {recommendation.recommended_config}',
                        'Monitorear rendimiento después de aplicar cambios',
                        'Considerar aplicar optimización similar a herramientas relacionadas'
                    ],
                    supporting_data={
                        'tool_id': recommendation.tool_id,
                        'expected_improvement': recommendation.expected_improvement,
                        'recommended_config': recommendation.recommended_config
                    },
                    generated_by='optimization_analyzer',
                    timestamp=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=7)
                )
                
                self.ai_insights.append(insight)
                
        except Exception as e:
            logger.warning(f"Error generando insight de optimización: {e}")
    
    async def _generate_feedback_insight(self, feedback: Dict[str, Any]) -> None:
        """Genera insight basado en feedback del usuario"""
        try:
            user_satisfaction = feedback.get('user_satisfaction', 0.5)
            
            if user_satisfaction < 0.3:
                insight = AIInsight(
                    insight_id=f"feedback_insight_{int(time.time())}",
                    insight_type='pattern',
                    title='Baja Satisfacción del Usuario Detectada',
                    description=f"El usuario reportó baja satisfacción ({user_satisfaction:.1f}/1.0) con la herramienta {feedback.get('tool_id')}",
                    confidence_score=0.9,
                    impact_level='high',
                    actionable_items=[
                        'Revisar configuración de la herramienta',
                        'Considerar herramientas alternativas',
                        'Solicitar feedback adicional del usuario',
                        'Analizar patrones de uso para identificar problemas'
                    ],
                    supporting_data=feedback,
                    generated_by='feedback_analyzer',
                    timestamp=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=3)
                )
                
                self.ai_insights.append(insight)
                
        except Exception as e:
            logger.warning(f"Error generando insight de feedback: {e}")
    
    async def _get_recommendation_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas del sistema de recomendación"""
        # Placeholder - en implementación real, calcular desde datos históricos
        return {
            'total_recommendations': 100,
            'avg_confidence': 0.75,
            'user_acceptance_rate': 0.68,
            'top_recommended_tools': ['github_mcp_server', 'docker_mcp_server'],
            'recommendation_accuracy': 0.72
        }
    
    async def _get_insight_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de insights generados"""
        try:
            total_insights = len(self.ai_insights)
            
            if total_insights == 0:
                return {'total_insights': 0}
            
            # Contar por tipo
            type_counts = {}
            impact_counts = {}
            
            for insight in self.ai_insights:
                type_counts[insight.insight_type] = type_counts.get(insight.insight_type, 0) + 1
                impact_counts[insight.impact_level] = impact_counts.get(insight.impact_level, 0) + 1
            
            # Calcular confianza promedio
            avg_confidence = np.mean([insight.confidence_score for insight in self.ai_insights])
            
            return {
                'total_insights': total_insights,
                'insights_by_type': type_counts,
                'insights_by_impact': impact_counts,
                'avg_confidence': avg_confidence,
                'recent_insights': len([
                    insight for insight in self.ai_insights
                    if insight.timestamp > datetime.now() - timedelta(hours=24)
                ])
            }
            
        except Exception as e:
            logger.warning(f"Error calculando estadísticas de insights: {e}")
            return {'total_insights': 0}
    
    async def _performance_monitoring_loop(self) -> None:
        """Loop de monitoreo de rendimiento en segundo plano"""
        while True:
            try:
                await asyncio.sleep(300)  # Cada 5 minutos
                
                if self.performance_monitor:
                    await self.performance_monitor.collect_system_metrics()
                
            except Exception as e:
                logger.warning(f"Error en loop de monitoreo de rendimiento: {e}")
                await asyncio.sleep(60)  # Esperar antes de reintentar
    
    async def _insight_generation_loop(self) -> None:
        """Loop de generación de insights en segundo plano"""
        while True:
            try:
                await asyncio.sleep(600)  # Cada 10 minutos
                
                if self.insight_generator:
                    new_insights = await self.insight_generator.generate_periodic_insights()
                    self.ai_insights.extend(new_insights)
                
            except Exception as e:
                logger.warning(f"Error en loop de generación de insights: {e}")
                await asyncio.sleep(120)  # Esperar antes de reintentar
    
    async def _data_cleanup_loop(self) -> None:
        """Loop de limpieza de datos en segundo plano"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cada hora
                
                # Limpiar insights expirados
                current_time = datetime.now()
                self.ai_insights = [
                    insight for insight in self.ai_insights
                    if insight.expires_at is None or insight.expires_at > current_time
                ]
                
                # Limpiar métricas antiguas
                if self.performance_monitor:
                    await self.performance_monitor.cleanup_old_metrics()
                
            except Exception as e:
                logger.warning(f"Error en loop de limpieza de datos: {e}")
                await asyncio.sleep(300)  # Esperar antes de reintentar

class AIPerformanceMonitor:
    """Monitor de rendimiento para sistemas de IA"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history = []
        self.db_path = config.get('db_path', 'ai_performance.db')
        self.connection = None
        
    async def initialize(self) -> None:
        """Inicializa el monitor de rendimiento"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            await self._create_tables()
            logger.info("Monitor de rendimiento de IA inicializado")
        except Exception as e:
            logger.error(f"Error inicializando monitor de rendimiento: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Crea tablas para métricas de rendimiento"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_name TEXT NOT NULL,
                accuracy REAL,
                precision_score REAL,
                recall_score REAL,
                f1_score REAL,
                response_time_ms REAL,
                throughput_per_second REAL,
                resource_usage TEXT,
                error_rate REAL,
                user_satisfaction REAL,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_name ON ai_performance_metrics(system_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON ai_performance_metrics(timestamp)')
        
        self.connection.commit()
    
    async def record_metrics(self, metrics: AIPerformanceMetrics) -> None:
        """Registra métricas de rendimiento"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO ai_performance_metrics 
                (system_name, accuracy, precision_score, recall_score, f1_score,
                 response_time_ms, throughput_per_second, resource_usage, 
                 error_rate, user_satisfaction, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.system_name,
                metrics.accuracy,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
                metrics.response_time_ms,
                metrics.throughput_per_second,
                json.dumps(metrics.resource_usage),
                metrics.error_rate,
                metrics.user_satisfaction,
                metrics.timestamp.isoformat()
            ))
            self.connection.commit()
            
            # Mantener en memoria también
            self.metrics_history.append(metrics)
            
        except Exception as e:
            logger.error(f"Error registrando métricas: {e}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas actuales de rendimiento"""
        try:
            cursor = self.connection.cursor()
            
            # Métricas por sistema en las últimas 24 horas
            cursor.execute('''
                SELECT system_name, 
                       AVG(accuracy) as avg_accuracy,
                       AVG(response_time_ms) as avg_response_time,
                       AVG(error_rate) as avg_error_rate,
                       COUNT(*) as measurement_count
                FROM ai_performance_metrics
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY system_name
            ''')
            
            system_metrics = {}
            for row in cursor.fetchall():
                system_metrics[row[0]] = {
                    'avg_accuracy': row[1],
                    'avg_response_time_ms': row[2],
                    'avg_error_rate': row[3],
                    'measurement_count': row[4]
                }
            
            return {
                'system_metrics': system_metrics,
                'total_systems': len(system_metrics),
                'measurement_period': '24 hours'
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas actuales: {e}")
            return {}
    
    async def collect_system_metrics(self) -> None:
        """Recolecta métricas del sistema"""
        try:
            import psutil
            
            # Métricas del sistema
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            # Crear métricas sintéticas para el sistema general
            system_metrics = AIPerformanceMetrics(
                system_name='system_overall',
                accuracy=0.0,  # No aplicable
                precision=0.0,  # No aplicable
                recall=0.0,     # No aplicable
                f1_score=0.0,   # No aplicable
                response_time_ms=0.0,  # No aplicable
                throughput_per_second=0.0,  # No aplicable
                resource_usage={'cpu': cpu_usage, 'memory': memory_usage},
                error_rate=0.0,
                user_satisfaction=0.0,
                timestamp=datetime.now()
            )
            
            await self.record_metrics(system_metrics)
            
        except Exception as e:
            logger.warning(f"Error recolectando métricas del sistema: {e}")
    
    async def cleanup_old_metrics(self) -> None:
        """Limpia métricas antiguas"""
        try:
            cursor = self.connection.cursor()
            
            # Eliminar métricas más antiguas de 30 días
            cursor.execute('''
                DELETE FROM ai_performance_metrics
                WHERE timestamp < datetime('now', '-30 days')
            ''')
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            if deleted_count > 0:
                logger.info(f"Eliminadas {deleted_count} métricas antiguas")
                
        except Exception as e:
            logger.warning(f"Error limpiando métricas antiguas: {e}")

class AIDataPipeline:
    """Pipeline de datos para sistemas de IA"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get('db_path', 'ai_data_pipeline.db')
        self.connection = None
        
    async def initialize(self) -> None:
        """Inicializa el pipeline de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            await self._create_tables()
            logger.info("Pipeline de datos de IA inicializado")
        except Exception as e:
            logger.error(f"Error inicializando pipeline de datos: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Crea tablas para el pipeline de datos"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT,
                user_id TEXT,
                task_type TEXT,
                rating REAL,
                success BOOLEAN,
                execution_time REAL,
                user_satisfaction REAL,
                feedback_text TEXT,
                context TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_tool_id ON feedback_data(tool_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback_data(user_id)')
        
        self.connection.commit()
    
    async def record_feedback(self, feedback: Dict[str, Any]) -> None:
        """Registra feedback del usuario"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO feedback_data 
                (tool_id, user_id, task_type, rating, success, execution_time,
                 user_satisfaction, feedback_text, context, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.get('tool_id'),
                feedback.get('user_id'),
                feedback.get('task_type'),
                feedback.get('rating'),
                feedback.get('success'),
                feedback.get('execution_time'),
                feedback.get('user_satisfaction'),
                feedback.get('feedback_text'),
                json.dumps(feedback.get('context', {})),
                datetime.now().isoformat()
            ))
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error registrando feedback: {e}")

class AIInsightGenerator:
    """Generador de insights de IA"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def generate_periodic_insights(self) -> List[AIInsight]:
        """Genera insights periódicos"""
        insights = []
        
        try:
            # Insight de ejemplo - en implementación real, analizar datos reales
            current_time = datetime.now()
            
            if current_time.hour == 9:  # Insight matutino
                insight = AIInsight(
                    insight_id=f"periodic_insight_{int(time.time())}",
                    insight_type='pattern',
                    title='Análisis de Patrones de Uso Matutino',
                    description='Se detectaron patrones de uso específicos en las horas matutinas',
                    confidence_score=0.7,
                    impact_level='low',
                    actionable_items=[
                        'Considerar pre-cargar herramientas populares en la mañana',
                        'Optimizar recursos para picos de uso matutinos'
                    ],
                    supporting_data={'hour': current_time.hour},
                    generated_by='periodic_analyzer',
                    timestamp=current_time,
                    expires_at=current_time + timedelta(hours=12)
                )
                insights.append(insight)
            
        except Exception as e:
            logger.warning(f"Error generando insights periódicos: {e}")
        
        return insights

# Configuración por defecto
DEFAULT_AI_SYSTEM_CONFIG = AISystemConfig(
    ml_optimization_config=DEFAULT_ML_CONFIG,
    recommendation_config=DEFAULT_RECOMMENDATION_CONFIG,
    ai_coordinator_config={
        'insight_generation': {
            'enabled': True,
            'generation_interval_minutes': 10
        }
    },
    performance_monitoring_config={
        'db_path': 'ai_performance.db',
        'collection_interval_minutes': 5
    },
    data_pipeline_config={
        'db_path': 'ai_data_pipeline.db'
    }
)

# Función de utilidad para crear coordinador de IA
async def create_ai_coordinator(config: Optional[AISystemConfig] = None) -> AICoordinator:
    """Crea y configura coordinador de IA"""
    if config is None:
        config = DEFAULT_AI_SYSTEM_CONFIG
    
    coordinator = AICoordinator(config)
    await coordinator.initialize()
    return coordinator

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Crear coordinador de IA
        coordinator = await create_ai_coordinator()
        
        # Ejemplo de recomendación de herramientas
        recommendation = await coordinator.get_tool_recommendation(
            task_description="Revisar código y crear pull request en GitHub",
            user_context={
                'user_id': 'user123',
                'skill_level': 'intermediate',
                'domain_expertise': ['development'],
                'task_type': 'code_review'
            },
            available_tools=['github_mcp_server', 'docker_mcp_server']
        )
        
        print(f"Recomendación de herramientas: {recommendation}")
        
        # Ejemplo de optimización
        optimization = await coordinator.get_optimization_recommendation(
            tool_id='github_mcp_server',
            context={'repository_size': 'large', 'team_size': 5}
        )
        
        print(f"Recomendación de optimización: {optimization}")
        
        # Ejemplo de feedback
        await coordinator.update_with_feedback({
            'tool_id': 'github_mcp_server',
            'user_id': 'user123',
            'rating': 4.5,
            'success': True,
            'execution_time': 30.0,
            'user_satisfaction': 0.9
        })
        
        # Obtener insights
        insights = await coordinator.get_ai_insights()
        print(f"Insights de IA: {len(insights)} insights disponibles")
        
        # Obtener analíticas
        analytics = await coordinator.get_performance_analytics()
        print(f"Analíticas: {analytics}")
    
    # Ejecutar ejemplo
    asyncio.run(main())

