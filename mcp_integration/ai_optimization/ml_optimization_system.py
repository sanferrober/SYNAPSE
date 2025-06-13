"""
Sistema de Aprendizaje Automático para Optimización MCP
Diseño de arquitectura y componentes principales para IA integrada en Synapse
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import pickle
import sqlite3
from pathlib import Path

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolUsageMetrics:
    """Métricas de uso de herramientas MCP"""
    tool_id: str
    user_id: str
    task_type: str
    execution_time: float
    success_rate: float
    resource_usage: Dict[str, float]
    user_satisfaction: Optional[float]
    context: Dict[str, Any]
    timestamp: datetime

@dataclass
class OptimizationRecommendation:
    """Recomendación de optimización generada por IA"""
    tool_id: str
    recommended_config: Dict[str, Any]
    confidence_score: float
    expected_improvement: float
    reasoning: str
    alternative_configs: List[Dict[str, Any]]

class MLOptimizationEngine(ABC):
    """Clase base para motores de optimización de ML"""
    
    @abstractmethod
    async def train(self, data: List[ToolUsageMetrics]) -> None:
        """Entrena el modelo con datos históricos"""
        pass
    
    @abstractmethod
    async def predict_optimal_config(self, tool_id: str, context: Dict[str, Any]) -> OptimizationRecommendation:
        """Predice la configuración óptima para una herramienta"""
        pass
    
    @abstractmethod
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza el modelo con nuevo feedback"""
        pass

class BayesianOptimizationEngine(MLOptimizationEngine):
    """Motor de optimización bayesiana para hiperparámetros de herramientas MCP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}  # Modelos por herramienta
        self.acquisition_function = config.get('acquisition_function', 'expected_improvement')
        self.n_initial_points = config.get('n_initial_points', 10)
        self.n_calls = config.get('n_calls', 50)
        
    async def train(self, data: List[ToolUsageMetrics]) -> None:
        """Entrena modelos de optimización bayesiana por herramienta"""
        try:
            # Agrupar datos por herramienta
            tool_data = {}
            for metric in data:
                if metric.tool_id not in tool_data:
                    tool_data[metric.tool_id] = []
                tool_data[metric.tool_id].append(metric)
            
            # Entrenar modelo para cada herramienta
            for tool_id, metrics in tool_data.items():
                if len(metrics) >= self.n_initial_points:
                    await self._train_tool_model(tool_id, metrics)
                    logger.info(f"Modelo entrenado para herramienta {tool_id} con {len(metrics)} muestras")
                    
        except Exception as e:
            logger.error(f"Error entrenando modelos de optimización bayesiana: {e}")
            raise
    
    async def _train_tool_model(self, tool_id: str, metrics: List[ToolUsageMetrics]) -> None:
        """Entrena modelo específico para una herramienta"""
        # Extraer características y objetivos
        X = []  # Configuraciones
        y = []  # Métricas de rendimiento
        
        for metric in metrics:
            # Convertir configuración a vector numérico
            config_vector = self._config_to_vector(metric.context.get('config', {}))
            X.append(config_vector)
            
            # Calcular métrica de rendimiento combinada
            performance = self._calculate_performance_score(metric)
            y.append(performance)
        
        # Simular entrenamiento de proceso gaussiano
        # En implementación real, usar bibliotecas como scikit-optimize o GPyOpt
        self.models[tool_id] = {
            'X': np.array(X),
            'y': np.array(y),
            'trained_at': datetime.now(),
            'n_samples': len(X)
        }
    
    def _config_to_vector(self, config: Dict[str, Any]) -> List[float]:
        """Convierte configuración de herramienta a vector numérico"""
        # Implementación simplificada - en la práctica, esto sería más sofisticado
        vector = []
        for key, value in config.items():
            if isinstance(value, (int, float)):
                vector.append(float(value))
            elif isinstance(value, bool):
                vector.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                # Hash simple para strings
                vector.append(float(hash(value) % 1000) / 1000.0)
        
        # Padding o truncamiento para vector de tamaño fijo
        target_size = 10
        if len(vector) < target_size:
            vector.extend([0.0] * (target_size - len(vector)))
        elif len(vector) > target_size:
            vector = vector[:target_size]
            
        return vector
    
    def _calculate_performance_score(self, metric: ToolUsageMetrics) -> float:
        """Calcula puntuación de rendimiento combinada"""
        # Combinar múltiples métricas en una sola puntuación
        time_score = 1.0 / (1.0 + metric.execution_time)  # Menor tiempo es mejor
        success_score = metric.success_rate
        satisfaction_score = metric.user_satisfaction or 0.5
        
        # Peso ponderado
        weights = {'time': 0.3, 'success': 0.4, 'satisfaction': 0.3}
        
        total_score = (
            weights['time'] * time_score +
            weights['success'] * success_score +
            weights['satisfaction'] * satisfaction_score
        )
        
        return total_score
    
    async def predict_optimal_config(self, tool_id: str, context: Dict[str, Any]) -> OptimizationRecommendation:
        """Predice configuración óptima usando optimización bayesiana"""
        try:
            if tool_id not in self.models:
                # Configuración por defecto si no hay modelo
                return OptimizationRecommendation(
                    tool_id=tool_id,
                    recommended_config={},
                    confidence_score=0.1,
                    expected_improvement=0.0,
                    reasoning="No hay datos históricos suficientes para optimización",
                    alternative_configs=[]
                )
            
            model = self.models[tool_id]
            
            # Simular optimización bayesiana
            # En implementación real, usar acquisition function para encontrar próximo punto óptimo
            best_config = await self._find_optimal_config(model, context)
            
            return OptimizationRecommendation(
                tool_id=tool_id,
                recommended_config=best_config['config'],
                confidence_score=best_config['confidence'],
                expected_improvement=best_config['expected_improvement'],
                reasoning=best_config['reasoning'],
                alternative_configs=best_config['alternatives']
            )
            
        except Exception as e:
            logger.error(f"Error prediciendo configuración óptima para {tool_id}: {e}")
            raise
    
    async def _find_optimal_config(self, model: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Encuentra configuración óptima usando acquisition function"""
        # Implementación simplificada
        X = model['X']
        y = model['y']
        
        # Encontrar mejor configuración histórica
        best_idx = np.argmax(y)
        best_config_vector = X[best_idx]
        
        # Convertir vector de vuelta a configuración
        best_config = self._vector_to_config(best_config_vector)
        
        # Generar configuraciones alternativas
        alternatives = []
        for i in range(min(3, len(X))):
            if i != best_idx:
                alt_config = self._vector_to_config(X[i])
                alternatives.append(alt_config)
        
        return {
            'config': best_config,
            'confidence': min(0.9, len(X) / 100.0),  # Confianza basada en cantidad de datos
            'expected_improvement': float(y[best_idx] - np.mean(y)),
            'reasoning': f"Configuración basada en {len(X)} muestras históricas",
            'alternatives': alternatives
        }
    
    def _vector_to_config(self, vector: np.ndarray) -> Dict[str, Any]:
        """Convierte vector numérico de vuelta a configuración"""
        # Implementación simplificada - mapeo inverso
        config = {}
        param_names = ['timeout', 'max_retries', 'batch_size', 'memory_limit', 'cpu_limit']
        
        for i, name in enumerate(param_names[:len(vector)]):
            if name in ['timeout', 'max_retries', 'batch_size']:
                config[name] = max(1, int(vector[i] * 100))
            elif name in ['memory_limit', 'cpu_limit']:
                config[name] = max(0.1, vector[i])
            else:
                config[name] = vector[i]
        
        return config
    
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza modelo con nuevo feedback"""
        try:
            tool_id = feedback.get('tool_id')
            if not tool_id or tool_id not in self.models:
                return
            
            # Crear nueva métrica de feedback
            new_metric = ToolUsageMetrics(
                tool_id=tool_id,
                user_id=feedback.get('user_id', 'unknown'),
                task_type=feedback.get('task_type', 'unknown'),
                execution_time=feedback.get('execution_time', 0.0),
                success_rate=feedback.get('success_rate', 0.0),
                resource_usage=feedback.get('resource_usage', {}),
                user_satisfaction=feedback.get('user_satisfaction'),
                context=feedback.get('context', {}),
                timestamp=datetime.now()
            )
            
            # Actualizar modelo incrementalmente
            await self._update_tool_model(tool_id, new_metric)
            logger.info(f"Modelo actualizado para herramienta {tool_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando modelo: {e}")
            raise
    
    async def _update_tool_model(self, tool_id: str, new_metric: ToolUsageMetrics) -> None:
        """Actualiza modelo específico de herramienta con nueva muestra"""
        model = self.models[tool_id]
        
        # Agregar nueva muestra
        new_x = np.array([self._config_to_vector(new_metric.context.get('config', {}))])
        new_y = np.array([self._calculate_performance_score(new_metric)])
        
        model['X'] = np.vstack([model['X'], new_x])
        model['y'] = np.append(model['y'], new_y)
        model['n_samples'] += 1
        model['updated_at'] = datetime.now()

class ReinforcementLearningEngine(MLOptimizationEngine):
    """Motor de aprendizaje por refuerzo para selección de herramientas"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.q_table = {}  # Tabla Q simplificada
        self.learning_rate = config.get('learning_rate', 0.1)
        self.discount_factor = config.get('discount_factor', 0.9)
        self.epsilon = config.get('epsilon', 0.1)  # Exploración
        self.state_space = config.get('state_space_size', 1000)
        
    async def train(self, data: List[ToolUsageMetrics]) -> None:
        """Entrena agente de RL con datos históricos"""
        try:
            # Convertir datos históricos en episodios de entrenamiento
            episodes = self._create_episodes_from_data(data)
            
            for episode in episodes:
                await self._train_episode(episode)
            
            logger.info(f"Entrenamiento RL completado con {len(episodes)} episodios")
            
        except Exception as e:
            logger.error(f"Error entrenando modelo RL: {e}")
            raise
    
    def _create_episodes_from_data(self, data: List[ToolUsageMetrics]) -> List[List[Dict[str, Any]]]:
        """Convierte métricas en episodios de entrenamiento"""
        # Agrupar por usuario y sesión
        episodes = []
        current_episode = []
        
        # Ordenar por timestamp
        sorted_data = sorted(data, key=lambda x: x.timestamp)
        
        for i, metric in enumerate(sorted_data):
            state = self._metric_to_state(metric)
            action = metric.tool_id
            reward = self._calculate_reward(metric)
            
            current_episode.append({
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': None
            })
            
            # Determinar fin de episodio
            if (i == len(sorted_data) - 1 or 
                sorted_data[i + 1].user_id != metric.user_id or
                sorted_data[i + 1].timestamp - metric.timestamp > timedelta(hours=1)):
                
                # Establecer next_state para transiciones
                for j in range(len(current_episode) - 1):
                    current_episode[j]['next_state'] = current_episode[j + 1]['state']
                
                episodes.append(current_episode)
                current_episode = []
        
        return episodes
    
    def _metric_to_state(self, metric: ToolUsageMetrics) -> str:
        """Convierte métrica a representación de estado"""
        # Simplificación: usar hash del contexto como estado
        context_str = json.dumps(metric.context, sort_keys=True)
        state_hash = hash(context_str) % self.state_space
        return f"state_{state_hash}"
    
    def _calculate_reward(self, metric: ToolUsageMetrics) -> float:
        """Calcula recompensa basada en métricas de rendimiento"""
        # Recompensa basada en éxito, tiempo y satisfacción
        success_reward = metric.success_rate * 10
        time_penalty = -metric.execution_time / 100.0  # Penalizar tiempo excesivo
        satisfaction_bonus = (metric.user_satisfaction or 0.5) * 5
        
        return success_reward + time_penalty + satisfaction_bonus
    
    async def _train_episode(self, episode: List[Dict[str, Any]]) -> None:
        """Entrena con un episodio usando Q-learning"""
        for transition in episode:
            state = transition['state']
            action = transition['action']
            reward = transition['reward']
            next_state = transition['next_state']
            
            # Inicializar Q-value si no existe
            if state not in self.q_table:
                self.q_table[state] = {}
            if action not in self.q_table[state]:
                self.q_table[state][action] = 0.0
            
            # Calcular Q-value objetivo
            if next_state and next_state in self.q_table:
                max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
            else:
                max_next_q = 0.0
            
            target_q = reward + self.discount_factor * max_next_q
            
            # Actualizar Q-value
            current_q = self.q_table[state][action]
            self.q_table[state][action] = current_q + self.learning_rate * (target_q - current_q)
    
    async def predict_optimal_config(self, tool_id: str, context: Dict[str, Any]) -> OptimizationRecommendation:
        """Predice herramienta óptima usando política RL"""
        try:
            # Convertir contexto a estado
            state = self._context_to_state(context)
            
            # Seleccionar acción usando política epsilon-greedy
            if state in self.q_table and np.random.random() > self.epsilon:
                # Explotar: seleccionar mejor acción conocida
                best_action = max(self.q_table[state], key=self.q_table[state].get)
                confidence = 0.8
                reasoning = "Selección basada en política aprendida"
            else:
                # Explorar: selección aleatoria
                available_tools = context.get('available_tools', [tool_id])
                best_action = np.random.choice(available_tools)
                confidence = 0.2
                reasoning = "Selección exploratoria"
            
            # Generar alternativas
            alternatives = []
            if state in self.q_table:
                sorted_actions = sorted(self.q_table[state].items(), key=lambda x: x[1], reverse=True)
                for action, q_value in sorted_actions[:3]:
                    if action != best_action:
                        alternatives.append({'tool_id': action, 'q_value': q_value})
            
            return OptimizationRecommendation(
                tool_id=best_action,
                recommended_config={'selected_by': 'rl_agent'},
                confidence_score=confidence,
                expected_improvement=self.q_table.get(state, {}).get(best_action, 0.0),
                reasoning=reasoning,
                alternative_configs=alternatives
            )
            
        except Exception as e:
            logger.error(f"Error en predicción RL: {e}")
            raise
    
    def _context_to_state(self, context: Dict[str, Any]) -> str:
        """Convierte contexto a representación de estado"""
        context_str = json.dumps(context, sort_keys=True)
        state_hash = hash(context_str) % self.state_space
        return f"state_{state_hash}"
    
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza modelo RL con nuevo feedback"""
        try:
            # Crear transición de aprendizaje online
            state = self._context_to_state(feedback.get('context', {}))
            action = feedback.get('tool_id')
            reward = self._calculate_reward_from_feedback(feedback)
            
            # Actualizar Q-table
            if state not in self.q_table:
                self.q_table[state] = {}
            if action not in self.q_table[state]:
                self.q_table[state][action] = 0.0
            
            # Actualización simple sin next_state (aprendizaje online)
            current_q = self.q_table[state][action]
            self.q_table[state][action] = current_q + self.learning_rate * (reward - current_q)
            
            logger.info(f"Modelo RL actualizado para estado {state}, acción {action}")
            
        except Exception as e:
            logger.error(f"Error actualizando modelo RL: {e}")
            raise
    
    def _calculate_reward_from_feedback(self, feedback: Dict[str, Any]) -> float:
        """Calcula recompensa desde feedback directo"""
        success_rate = feedback.get('success_rate', 0.0)
        execution_time = feedback.get('execution_time', 0.0)
        user_satisfaction = feedback.get('user_satisfaction', 0.5)
        
        success_reward = success_rate * 10
        time_penalty = -execution_time / 100.0
        satisfaction_bonus = user_satisfaction * 5
        
        return success_reward + time_penalty + satisfaction_bonus

class MLOptimizationManager:
    """Gestor principal de sistemas de optimización ML"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engines = {}
        self.data_store = MLDataStore(config.get('data_store', {}))
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Inicializa todos los motores de optimización"""
        try:
            # Inicializar motores de optimización
            self.engines['bayesian'] = BayesianOptimizationEngine(
                self.config.get('bayesian_optimization', {})
            )
            self.engines['reinforcement_learning'] = ReinforcementLearningEngine(
                self.config.get('reinforcement_learning', {})
            )
            
            # Inicializar almacén de datos
            await self.data_store.initialize()
            
            # Cargar datos históricos y entrenar modelos
            historical_data = await self.data_store.load_historical_data()
            if historical_data:
                await self._train_all_engines(historical_data)
            
            self.is_initialized = True
            logger.info("MLOptimizationManager inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando MLOptimizationManager: {e}")
            raise
    
    async def _train_all_engines(self, data: List[ToolUsageMetrics]) -> None:
        """Entrena todos los motores con datos históricos"""
        training_tasks = []
        for engine_name, engine in self.engines.items():
            training_tasks.append(self._train_engine_safe(engine_name, engine, data))
        
        await asyncio.gather(*training_tasks, return_exceptions=True)
    
    async def _train_engine_safe(self, engine_name: str, engine: MLOptimizationEngine, data: List[ToolUsageMetrics]) -> None:
        """Entrena un motor de forma segura con manejo de errores"""
        try:
            await engine.train(data)
            logger.info(f"Motor {engine_name} entrenado exitosamente")
        except Exception as e:
            logger.error(f"Error entrenando motor {engine_name}: {e}")
    
    async def get_optimization_recommendation(self, tool_id: str, context: Dict[str, Any], engine_type: str = 'bayesian') -> OptimizationRecommendation:
        """Obtiene recomendación de optimización"""
        if not self.is_initialized:
            await self.initialize()
        
        if engine_type not in self.engines:
            raise ValueError(f"Motor de optimización '{engine_type}' no disponible")
        
        engine = self.engines[engine_type]
        recommendation = await engine.predict_optimal_config(tool_id, context)
        
        # Guardar recomendación para análisis futuro
        await self.data_store.save_recommendation(recommendation, context)
        
        return recommendation
    
    async def update_with_feedback(self, feedback: Dict[str, Any]) -> None:
        """Actualiza modelos con feedback de usuario"""
        if not self.is_initialized:
            return
        
        # Crear métrica de uso desde feedback
        usage_metric = ToolUsageMetrics(
            tool_id=feedback.get('tool_id', ''),
            user_id=feedback.get('user_id', ''),
            task_type=feedback.get('task_type', ''),
            execution_time=feedback.get('execution_time', 0.0),
            success_rate=feedback.get('success_rate', 0.0),
            resource_usage=feedback.get('resource_usage', {}),
            user_satisfaction=feedback.get('user_satisfaction'),
            context=feedback.get('context', {}),
            timestamp=datetime.now()
        )
        
        # Guardar en almacén de datos
        await self.data_store.save_usage_metric(usage_metric)
        
        # Actualizar todos los motores
        update_tasks = []
        for engine in self.engines.values():
            update_tasks.append(engine.update_model(feedback))
        
        await asyncio.gather(*update_tasks, return_exceptions=True)
        
        logger.info(f"Modelos actualizados con feedback para herramienta {feedback.get('tool_id')}")
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas de rendimiento del sistema"""
        if not self.is_initialized:
            return {}
        
        analytics = await self.data_store.get_analytics()
        
        # Agregar métricas de modelos
        model_metrics = {}
        for engine_name, engine in self.engines.items():
            if hasattr(engine, 'models'):
                model_metrics[engine_name] = {
                    'trained_tools': len(engine.models),
                    'total_samples': sum(model.get('n_samples', 0) for model in engine.models.values())
                }
            elif hasattr(engine, 'q_table'):
                model_metrics[engine_name] = {
                    'states': len(engine.q_table),
                    'total_actions': sum(len(actions) for actions in engine.q_table.values())
                }
        
        analytics['model_metrics'] = model_metrics
        return analytics

class MLDataStore:
    """Almacén de datos para sistemas de ML"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get('db_path', 'ml_optimization.db')
        self.connection = None
        
    async def initialize(self) -> None:
        """Inicializa el almacén de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            await self._create_tables()
            logger.info(f"Almacén de datos ML inicializado en {self.db_path}")
        except Exception as e:
            logger.error(f"Error inicializando almacén de datos: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Crea tablas necesarias en la base de datos"""
        cursor = self.connection.cursor()
        
        # Tabla de métricas de uso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                task_type TEXT,
                execution_time REAL,
                success_rate REAL,
                resource_usage TEXT,
                user_satisfaction REAL,
                context TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de recomendaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                recommended_config TEXT,
                confidence_score REAL,
                expected_improvement REAL,
                reasoning TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices para consultas eficientes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_id ON usage_metrics(tool_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON usage_metrics(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_metrics(timestamp)')
        
        self.connection.commit()
    
    async def save_usage_metric(self, metric: ToolUsageMetrics) -> None:
        """Guarda métrica de uso en la base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO usage_metrics 
                (tool_id, user_id, task_type, execution_time, success_rate, 
                 resource_usage, user_satisfaction, context, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.tool_id,
                metric.user_id,
                metric.task_type,
                metric.execution_time,
                metric.success_rate,
                json.dumps(metric.resource_usage),
                metric.user_satisfaction,
                json.dumps(metric.context),
                metric.timestamp.isoformat()
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error guardando métrica de uso: {e}")
            raise
    
    async def save_recommendation(self, recommendation: OptimizationRecommendation, context: Dict[str, Any]) -> None:
        """Guarda recomendación en la base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO recommendations 
                (tool_id, recommended_config, confidence_score, expected_improvement, reasoning, context)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                recommendation.tool_id,
                json.dumps(recommendation.recommended_config),
                recommendation.confidence_score,
                recommendation.expected_improvement,
                recommendation.reasoning,
                json.dumps(context)
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error guardando recomendación: {e}")
            raise
    
    async def load_historical_data(self, limit: int = 10000) -> List[ToolUsageMetrics]:
        """Carga datos históricos para entrenamiento"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT tool_id, user_id, task_type, execution_time, success_rate,
                       resource_usage, user_satisfaction, context, timestamp
                FROM usage_metrics
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            metrics = []
            
            for row in rows:
                metric = ToolUsageMetrics(
                    tool_id=row[0],
                    user_id=row[1],
                    task_type=row[2],
                    execution_time=row[3],
                    success_rate=row[4],
                    resource_usage=json.loads(row[5]) if row[5] else {},
                    user_satisfaction=row[6],
                    context=json.loads(row[7]) if row[7] else {},
                    timestamp=datetime.fromisoformat(row[8])
                )
                metrics.append(metric)
            
            logger.info(f"Cargados {len(metrics)} registros históricos")
            return metrics
            
        except Exception as e:
            logger.error(f"Error cargando datos históricos: {e}")
            return []
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas del almacén de datos"""
        try:
            cursor = self.connection.cursor()
            
            # Estadísticas básicas
            cursor.execute('SELECT COUNT(*) FROM usage_metrics')
            total_metrics = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT tool_id) FROM usage_metrics')
            unique_tools = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM usage_metrics')
            unique_users = cursor.fetchone()[0]
            
            # Herramientas más utilizadas
            cursor.execute('''
                SELECT tool_id, COUNT(*) as usage_count
                FROM usage_metrics
                GROUP BY tool_id
                ORDER BY usage_count DESC
                LIMIT 10
            ''')
            top_tools = cursor.fetchall()
            
            # Tendencias temporales (últimos 30 días)
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as daily_usage
                FROM usage_metrics
                WHERE timestamp >= datetime('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''')
            daily_trends = cursor.fetchall()
            
            return {
                'total_metrics': total_metrics,
                'unique_tools': unique_tools,
                'unique_users': unique_users,
                'top_tools': [{'tool_id': tool[0], 'usage_count': tool[1]} for tool in top_tools],
                'daily_trends': [{'date': trend[0], 'usage': trend[1]} for trend in daily_trends]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas: {e}")
            return {}

# Configuración por defecto
DEFAULT_ML_CONFIG = {
    'bayesian_optimization': {
        'acquisition_function': 'expected_improvement',
        'n_initial_points': 10,
        'n_calls': 50
    },
    'reinforcement_learning': {
        'learning_rate': 0.1,
        'discount_factor': 0.9,
        'epsilon': 0.1,
        'state_space_size': 1000
    },
    'data_store': {
        'db_path': 'ml_optimization.db'
    }
}

# Función de utilidad para crear manager
async def create_ml_optimization_manager(config: Optional[Dict[str, Any]] = None) -> MLOptimizationManager:
    """Crea y configura un manager de optimización ML"""
    if config is None:
        config = DEFAULT_ML_CONFIG
    
    manager = MLOptimizationManager(config)
    await manager.initialize()
    return manager

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Crear manager
        manager = await create_ml_optimization_manager()
        
        # Ejemplo de recomendación
        recommendation = await manager.get_optimization_recommendation(
            tool_id="github_mcp_server",
            context={
                "task_type": "code_review",
                "repository_size": "large",
                "team_size": 5,
                "available_tools": ["github_mcp_server", "docker_mcp_server"]
            },
            engine_type="bayesian"
        )
        
        print(f"Recomendación: {recommendation}")
        
        # Ejemplo de feedback
        await manager.update_with_feedback({
            "tool_id": "github_mcp_server",
            "user_id": "user123",
            "task_type": "code_review",
            "execution_time": 45.2,
            "success_rate": 0.95,
            "user_satisfaction": 0.8,
            "context": {"repository_size": "large"}
        })
        
        # Obtener analíticas
        analytics = await manager.get_performance_analytics()
        print(f"Analíticas: {analytics}")
    
    # Ejecutar ejemplo
    asyncio.run(main())

