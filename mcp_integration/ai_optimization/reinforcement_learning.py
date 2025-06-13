"""
Algoritmos de Aprendizaje por Refuerzo para Optimización de Herramientas MCP
Implementa agentes RL para aprendizaje automático de configuraciones óptimas
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pickle
import sqlite3
from pathlib import Path
import time
import random
from collections import deque, defaultdict
from abc import ABC, abstractmethod

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RLState:
    """Estado del entorno para aprendizaje por refuerzo"""
    tool_id: str
    current_config: Dict[str, Any]
    performance_metrics: Dict[str, float]
    resource_usage: Dict[str, float]
    context_features: Dict[str, Any]
    timestamp: datetime

@dataclass
class RLAction:
    """Acción en el entorno de RL"""
    action_id: str
    config_changes: Dict[str, Any]
    action_type: str  # 'increase', 'decrease', 'toggle', 'set'
    parameter_name: str
    parameter_value: Any

@dataclass
class RLReward:
    """Recompensa del entorno de RL"""
    reward_value: float
    reward_components: Dict[str, float]
    performance_improvement: float
    resource_efficiency: float
    user_satisfaction: float
    timestamp: datetime

@dataclass
class RLExperience:
    """Experiencia para replay buffer"""
    state: RLState
    action: RLAction
    reward: RLReward
    next_state: RLState
    done: bool
    timestamp: datetime

class RLEnvironment(ABC):
    """Entorno base para aprendizaje por refuerzo"""
    
    @abstractmethod
    async def reset(self) -> RLState:
        """Reinicia el entorno y retorna estado inicial"""
        pass
    
    @abstractmethod
    async def step(self, action: RLAction) -> Tuple[RLState, RLReward, bool]:
        """Ejecuta acción y retorna (nuevo_estado, recompensa, terminado)"""
        pass
    
    @abstractmethod
    async def get_valid_actions(self, state: RLState) -> List[RLAction]:
        """Obtiene acciones válidas para el estado actual"""
        pass

class MCPToolEnvironment(RLEnvironment):
    """Entorno de RL para optimización de herramientas MCP"""
    
    def __init__(self, tool_id: str, config: Dict[str, Any]):
        self.tool_id = tool_id
        self.config = config
        self.current_state = None
        self.episode_length = config.get('episode_length', 50)
        self.current_step = 0
        self.baseline_performance = None
        
        # Parámetros configurables de la herramienta
        self.configurable_params = config.get('configurable_params', {
            'timeout': {'min': 10, 'max': 300, 'type': 'int'},
            'batch_size': {'min': 1, 'max': 100, 'type': 'int'},
            'retry_count': {'min': 0, 'max': 10, 'type': 'int'},
            'cache_enabled': {'type': 'bool'},
            'parallel_execution': {'type': 'bool'},
            'memory_limit': {'min': 0.1, 'max': 4.0, 'type': 'float'}
        })
        
    async def reset(self) -> RLState:
        """Reinicia el entorno con configuración por defecto"""
        self.current_step = 0
        
        # Configuración inicial (valores por defecto)
        initial_config = {}
        for param, spec in self.configurable_params.items():
            if spec['type'] == 'int':
                initial_config[param] = (spec['min'] + spec['max']) // 2
            elif spec['type'] == 'float':
                initial_config[param] = (spec['min'] + spec['max']) / 2
            elif spec['type'] == 'bool':
                initial_config[param] = True
        
        # Simular métricas de rendimiento iniciales
        performance_metrics = await self._simulate_performance(initial_config)
        resource_usage = await self._simulate_resource_usage(initial_config)
        
        self.current_state = RLState(
            tool_id=self.tool_id,
            current_config=initial_config,
            performance_metrics=performance_metrics,
            resource_usage=resource_usage,
            context_features={'episode_step': self.current_step},
            timestamp=datetime.now()
        )
        
        # Establecer baseline si no existe
        if self.baseline_performance is None:
            self.baseline_performance = performance_metrics.copy()
        
        return self.current_state
    
    async def step(self, action: RLAction) -> Tuple[RLState, RLReward, bool]:
        """Ejecuta acción y retorna nuevo estado"""
        self.current_step += 1
        
        # Aplicar cambios de configuración
        new_config = self.current_state.current_config.copy()
        
        if action.action_type == 'set':
            new_config[action.parameter_name] = action.parameter_value
        elif action.action_type == 'increase':
            current_val = new_config.get(action.parameter_name, 0)
            param_spec = self.configurable_params[action.parameter_name]
            if param_spec['type'] == 'int':
                new_config[action.parameter_name] = min(param_spec['max'], current_val + 1)
            elif param_spec['type'] == 'float':
                new_config[action.parameter_name] = min(param_spec['max'], current_val + 0.1)
        elif action.action_type == 'decrease':
            current_val = new_config.get(action.parameter_name, 0)
            param_spec = self.configurable_params[action.parameter_name]
            if param_spec['type'] == 'int':
                new_config[action.parameter_name] = max(param_spec['min'], current_val - 1)
            elif param_spec['type'] == 'float':
                new_config[action.parameter_name] = max(param_spec['min'], current_val - 0.1)
        elif action.action_type == 'toggle':
            new_config[action.parameter_name] = not new_config.get(action.parameter_name, False)
        
        # Simular nuevas métricas
        new_performance = await self._simulate_performance(new_config)
        new_resource_usage = await self._simulate_resource_usage(new_config)
        
        # Crear nuevo estado
        new_state = RLState(
            tool_id=self.tool_id,
            current_config=new_config,
            performance_metrics=new_performance,
            resource_usage=new_resource_usage,
            context_features={'episode_step': self.current_step},
            timestamp=datetime.now()
        )
        
        # Calcular recompensa
        reward = await self._calculate_reward(
            self.current_state, new_state, action
        )
        
        # Determinar si el episodio terminó
        done = self.current_step >= self.episode_length
        
        # Actualizar estado actual
        self.current_state = new_state
        
        return new_state, reward, done
    
    async def get_valid_actions(self, state: RLState) -> List[RLAction]:
        """Genera acciones válidas para el estado actual"""
        actions = []
        
        for param_name, param_spec in self.configurable_params.items():
            current_value = state.current_config.get(param_name)
            
            if param_spec['type'] == 'bool':
                # Acción de toggle para booleanos
                actions.append(RLAction(
                    action_id=f"toggle_{param_name}",
                    config_changes={param_name: not current_value},
                    action_type='toggle',
                    parameter_name=param_name,
                    parameter_value=not current_value
                ))
            
            elif param_spec['type'] in ['int', 'float']:
                # Acciones de incremento y decremento
                if current_value < param_spec['max']:
                    actions.append(RLAction(
                        action_id=f"increase_{param_name}",
                        config_changes={param_name: current_value + (1 if param_spec['type'] == 'int' else 0.1)},
                        action_type='increase',
                        parameter_name=param_name,
                        parameter_value=current_value + (1 if param_spec['type'] == 'int' else 0.1)
                    ))
                
                if current_value > param_spec['min']:
                    actions.append(RLAction(
                        action_id=f"decrease_{param_name}",
                        config_changes={param_name: current_value - (1 if param_spec['type'] == 'int' else 0.1)},
                        action_type='decrease',
                        parameter_name=param_name,
                        parameter_value=current_value - (1 if param_spec['type'] == 'int' else 0.1)
                    ))
        
        return actions
    
    async def _simulate_performance(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Simula métricas de rendimiento basadas en configuración"""
        # Simulación realista basada en parámetros de configuración
        base_performance = 0.7
        
        # Timeout afecta tiempo de respuesta
        timeout_factor = 1.0 - (config.get('timeout', 60) - 60) / 240  # Normalizado
        
        # Batch size afecta throughput
        batch_size = config.get('batch_size', 10)
        batch_factor = min(1.0, batch_size / 50)  # Óptimo alrededor de 50
        
        # Cache mejora rendimiento
        cache_factor = 1.2 if config.get('cache_enabled', True) else 1.0
        
        # Parallel execution mejora throughput
        parallel_factor = 1.3 if config.get('parallel_execution', True) else 1.0
        
        # Calcular métricas finales con algo de ruido
        noise = np.random.normal(0, 0.05)
        
        performance_score = base_performance * timeout_factor * batch_factor * cache_factor * parallel_factor + noise
        performance_score = max(0.1, min(1.0, performance_score))
        
        response_time = 100 / performance_score + np.random.normal(0, 10)
        response_time = max(10, response_time)
        
        throughput = performance_score * 100 + np.random.normal(0, 5)
        throughput = max(1, throughput)
        
        success_rate = performance_score * 0.95 + np.random.normal(0, 0.02)
        success_rate = max(0.5, min(1.0, success_rate))
        
        return {
            'performance_score': performance_score,
            'response_time_ms': response_time,
            'throughput_per_second': throughput,
            'success_rate': success_rate,
            'error_rate': 1.0 - success_rate
        }
    
    async def _simulate_resource_usage(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Simula uso de recursos basado en configuración"""
        base_cpu = 0.3
        base_memory = 0.4
        
        # Batch size afecta uso de memoria
        batch_size = config.get('batch_size', 10)
        memory_factor = 1.0 + (batch_size - 10) / 100
        
        # Parallel execution aumenta uso de CPU
        cpu_factor = 1.5 if config.get('parallel_execution', True) else 1.0
        
        # Cache usa más memoria
        cache_memory = 0.1 if config.get('cache_enabled', True) else 0.0
        
        # Memory limit
        memory_limit = config.get('memory_limit', 2.0)
        
        cpu_usage = base_cpu * cpu_factor + np.random.normal(0, 0.05)
        cpu_usage = max(0.1, min(1.0, cpu_usage))
        
        memory_usage = (base_memory * memory_factor + cache_memory) + np.random.normal(0, 0.05)
        memory_usage = max(0.1, min(memory_limit, memory_usage))
        
        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_io': np.random.uniform(0.1, 0.5),
            'network_io': np.random.uniform(0.1, 0.3)
        }
    
    async def _calculate_reward(self, old_state: RLState, new_state: RLState, 
                              action: RLAction) -> RLReward:
        """Calcula recompensa basada en cambio de estado"""
        # Componentes de recompensa
        performance_improvement = (
            new_state.performance_metrics['performance_score'] - 
            old_state.performance_metrics['performance_score']
        )
        
        # Penalizar uso excesivo de recursos
        resource_penalty = 0.0
        if new_state.resource_usage['cpu_usage'] > 0.8:
            resource_penalty += 0.1
        if new_state.resource_usage['memory_usage'] > 0.8:
            resource_penalty += 0.1
        
        # Bonificar mejora en tiempo de respuesta
        response_time_improvement = (
            old_state.performance_metrics['response_time_ms'] - 
            new_state.performance_metrics['response_time_ms']
        ) / 100  # Normalizar
        
        # Bonificar mejora en throughput
        throughput_improvement = (
            new_state.performance_metrics['throughput_per_second'] - 
            old_state.performance_metrics['throughput_per_second']
        ) / 100  # Normalizar
        
        # Calcular recompensa total
        reward_components = {
            'performance_improvement': performance_improvement * 10,
            'response_time_improvement': response_time_improvement * 2,
            'throughput_improvement': throughput_improvement * 2,
            'resource_penalty': -resource_penalty * 5
        }
        
        total_reward = sum(reward_components.values())
        
        # Simular satisfacción del usuario (basada en rendimiento general)
        user_satisfaction = new_state.performance_metrics['performance_score']
        
        return RLReward(
            reward_value=total_reward,
            reward_components=reward_components,
            performance_improvement=performance_improvement,
            resource_efficiency=1.0 - resource_penalty,
            user_satisfaction=user_satisfaction,
            timestamp=datetime.now()
        )

class DQNAgent:
    """Agente Deep Q-Network para optimización de herramientas"""
    
    def __init__(self, state_size: int, action_size: int, config: Dict[str, Any]):
        self.state_size = state_size
        self.action_size = action_size
        self.config = config
        
        # Hiperparámetros
        self.learning_rate = config.get('learning_rate', 0.001)
        self.epsilon = config.get('epsilon', 1.0)
        self.epsilon_min = config.get('epsilon_min', 0.01)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.gamma = config.get('gamma', 0.95)
        self.batch_size = config.get('batch_size', 32)
        
        # Replay buffer
        self.memory = deque(maxlen=config.get('memory_size', 10000))
        
        # Q-tables (simplificado para este ejemplo)
        self.q_table = defaultdict(lambda: np.zeros(action_size))
        
        # Estadísticas
        self.training_stats = {
            'episodes': 0,
            'total_reward': 0,
            'avg_reward': 0,
            'epsilon_history': [],
            'loss_history': []
        }
    
    def state_to_key(self, state: RLState) -> str:
        """Convierte estado a clave para Q-table"""
        # Simplificación: usar configuración como clave
        config_str = json.dumps(state.current_config, sort_keys=True)
        return config_str
    
    def choose_action(self, state: RLState, valid_actions: List[RLAction]) -> RLAction:
        """Selecciona acción usando epsilon-greedy"""
        if np.random.random() <= self.epsilon:
            # Exploración: acción aleatoria
            return random.choice(valid_actions)
        else:
            # Explotación: mejor acción conocida
            state_key = self.state_to_key(state)
            q_values = self.q_table[state_key]
            
            # Seleccionar acción con mayor Q-value entre las válidas
            best_action_idx = 0
            best_q_value = float('-inf')
            
            for i, action in enumerate(valid_actions):
                if i < len(q_values) and q_values[i] > best_q_value:
                    best_q_value = q_values[i]
                    best_action_idx = i
            
            return valid_actions[best_action_idx]
    
    def remember(self, experience: RLExperience) -> None:
        """Almacena experiencia en replay buffer"""
        self.memory.append(experience)
    
    def replay(self) -> float:
        """Entrena el agente usando experiencias del replay buffer"""
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # Muestrear batch de experiencias
        batch = random.sample(self.memory, self.batch_size)
        
        total_loss = 0.0
        
        for experience in batch:
            state_key = self.state_to_key(experience.state)
            next_state_key = self.state_to_key(experience.next_state)
            
            # Q-learning update
            target = experience.reward.reward_value
            if not experience.done:
                target += self.gamma * np.max(self.q_table[next_state_key])
            
            # Encontrar índice de la acción
            action_idx = hash(experience.action.action_id) % self.action_size
            
            # Actualizar Q-value
            current_q = self.q_table[state_key][action_idx]
            self.q_table[state_key][action_idx] = current_q + self.learning_rate * (target - current_q)
            
            # Calcular loss para estadísticas
            loss = (target - current_q) ** 2
            total_loss += loss
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        avg_loss = total_loss / self.batch_size
        self.training_stats['loss_history'].append(avg_loss)
        self.training_stats['epsilon_history'].append(self.epsilon)
        
        return avg_loss
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de entrenamiento"""
        return self.training_stats.copy()

class RLOptimizationManager:
    """Gestor principal de optimización por aprendizaje por refuerzo"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.environments = {}
        self.agents = {}
        self.training_history = {}
        self.db_path = config.get('db_path', 'rl_optimization.db')
        self.connection = None
        
    async def initialize(self) -> None:
        """Inicializa el gestor de RL"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            await self._create_tables()
            logger.info("Gestor de optimización RL inicializado")
        except Exception as e:
            logger.error(f"Error inicializando gestor RL: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Crea tablas para datos de RL"""
        cursor = self.connection.cursor()
        
        # Tabla de episodios de entrenamiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rl_episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                episode_number INTEGER,
                total_reward REAL,
                steps INTEGER,
                final_performance REAL,
                final_config TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de experiencias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rl_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                episode_number INTEGER,
                step_number INTEGER,
                state_data TEXT,
                action_data TEXT,
                reward_value REAL,
                next_state_data TEXT,
                done BOOLEAN,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rl_episodes_tool_id ON rl_episodes(tool_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rl_experiences_tool_id ON rl_experiences(tool_id)')
        
        self.connection.commit()
    
    async def create_environment(self, tool_id: str, env_config: Dict[str, Any]) -> None:
        """Crea entorno de RL para una herramienta"""
        try:
            environment = MCPToolEnvironment(tool_id, env_config)
            self.environments[tool_id] = environment
            
            # Crear agente correspondiente
            state_size = len(env_config.get('configurable_params', {})) * 3  # Aproximación
            action_size = len(env_config.get('configurable_params', {})) * 2  # Aproximación
            
            agent_config = self.config.get('agent_config', {})
            agent = DQNAgent(state_size, action_size, agent_config)
            self.agents[tool_id] = agent
            
            logger.info(f"Entorno y agente RL creados para herramienta {tool_id}")
            
        except Exception as e:
            logger.error(f"Error creando entorno RL para {tool_id}: {e}")
            raise
    
    async def train_agent(self, tool_id: str, num_episodes: int = 100) -> Dict[str, Any]:
        """Entrena agente RL para optimizar herramienta"""
        try:
            if tool_id not in self.environments or tool_id not in self.agents:
                raise ValueError(f"Entorno o agente no encontrado para {tool_id}")
            
            environment = self.environments[tool_id]
            agent = self.agents[tool_id]
            
            training_results = {
                'tool_id': tool_id,
                'episodes_completed': 0,
                'total_reward': 0,
                'best_episode_reward': float('-inf'),
                'best_configuration': None,
                'avg_reward_last_10': 0,
                'training_time_seconds': 0
            }
            
            start_time = time.time()
            recent_rewards = deque(maxlen=10)
            
            for episode in range(num_episodes):
                # Reiniciar entorno
                state = await environment.reset()
                episode_reward = 0
                episode_steps = 0
                
                while True:
                    # Obtener acciones válidas
                    valid_actions = await environment.get_valid_actions(state)
                    
                    if not valid_actions:
                        break
                    
                    # Seleccionar acción
                    action = agent.choose_action(state, valid_actions)
                    
                    # Ejecutar acción
                    next_state, reward, done = await environment.step(action)
                    
                    # Almacenar experiencia
                    experience = RLExperience(
                        state=state,
                        action=action,
                        reward=reward,
                        next_state=next_state,
                        done=done,
                        timestamp=datetime.now()
                    )
                    
                    agent.remember(experience)
                    
                    # Entrenar agente
                    if len(agent.memory) > agent.batch_size:
                        loss = agent.replay()
                    
                    # Actualizar estado y métricas
                    state = next_state
                    episode_reward += reward.reward_value
                    episode_steps += 1
                    
                    # Registrar experiencia en BD
                    await self._record_experience(tool_id, episode, episode_steps, experience)
                    
                    if done:
                        break
                
                # Actualizar estadísticas
                recent_rewards.append(episode_reward)
                training_results['episodes_completed'] = episode + 1
                training_results['total_reward'] += episode_reward
                
                if episode_reward > training_results['best_episode_reward']:
                    training_results['best_episode_reward'] = episode_reward
                    training_results['best_configuration'] = state.current_config.copy()
                
                # Registrar episodio en BD
                await self._record_episode(
                    tool_id, episode, episode_reward, episode_steps,
                    state.performance_metrics['performance_score'],
                    state.current_config
                )
                
                # Log progreso cada 10 episodios
                if (episode + 1) % 10 == 0:
                    avg_reward = np.mean(recent_rewards)
                    training_results['avg_reward_last_10'] = avg_reward
                    logger.info(f"Episodio {episode + 1}/{num_episodes}, "
                              f"Recompensa promedio (últimos 10): {avg_reward:.3f}, "
                              f"Epsilon: {agent.epsilon:.3f}")
            
            training_results['training_time_seconds'] = time.time() - start_time
            
            # Actualizar estadísticas del agente
            agent.training_stats['episodes'] = num_episodes
            agent.training_stats['total_reward'] = training_results['total_reward']
            agent.training_stats['avg_reward'] = training_results['total_reward'] / num_episodes
            
            # Almacenar historial de entrenamiento
            self.training_history[tool_id] = training_results
            
            logger.info(f"Entrenamiento completado para {tool_id}. "
                       f"Mejor recompensa: {training_results['best_episode_reward']:.3f}")
            
            return training_results
            
        except Exception as e:
            logger.error(f"Error entrenando agente RL para {tool_id}: {e}")
            raise
    
    async def get_optimal_configuration(self, tool_id: str, 
                                      current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene configuración óptima usando agente entrenado"""
        try:
            if tool_id not in self.agents:
                raise ValueError(f"Agente no encontrado para {tool_id}")
            
            agent = self.agents[tool_id]
            environment = self.environments[tool_id]
            
            # Crear estado basado en contexto actual
            state = await environment.reset()
            
            # Usar agente en modo de explotación (epsilon = 0)
            original_epsilon = agent.epsilon
            agent.epsilon = 0.0
            
            try:
                # Ejecutar varios pasos para encontrar configuración óptima
                best_config = state.current_config.copy()
                best_performance = state.performance_metrics['performance_score']
                
                for _ in range(20):  # Máximo 20 pasos de optimización
                    valid_actions = await environment.get_valid_actions(state)
                    
                    if not valid_actions:
                        break
                    
                    action = agent.choose_action(state, valid_actions)
                    next_state, reward, done = await environment.step(action)
                    
                    # Actualizar mejor configuración si mejora
                    if next_state.performance_metrics['performance_score'] > best_performance:
                        best_config = next_state.current_config.copy()
                        best_performance = next_state.performance_metrics['performance_score']
                    
                    state = next_state
                    
                    if done:
                        break
                
                return best_config
                
            finally:
                # Restaurar epsilon original
                agent.epsilon = original_epsilon
            
        except Exception as e:
            logger.error(f"Error obteniendo configuración óptima para {tool_id}: {e}")
            return {}
    
    async def get_training_analytics(self, tool_id: str) -> Dict[str, Any]:
        """Obtiene analíticas de entrenamiento para una herramienta"""
        try:
            analytics = {}
            
            # Estadísticas del agente
            if tool_id in self.agents:
                agent_stats = self.agents[tool_id].get_training_stats()
                analytics['agent_stats'] = agent_stats
            
            # Historial de entrenamiento
            if tool_id in self.training_history:
                analytics['training_history'] = self.training_history[tool_id]
            
            # Estadísticas de episodios desde BD
            episode_stats = await self._get_episode_statistics(tool_id)
            analytics['episode_statistics'] = episode_stats
            
            # Análisis de convergencia
            convergence_analysis = await self._analyze_convergence(tool_id)
            analytics['convergence_analysis'] = convergence_analysis
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas para {tool_id}: {e}")
            return {}
    
    async def _record_episode(self, tool_id: str, episode_number: int, 
                            total_reward: float, steps: int, 
                            final_performance: float, final_config: Dict[str, Any]) -> None:
        """Registra episodio en base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO rl_episodes 
                (tool_id, episode_number, total_reward, steps, final_performance, 
                 final_config, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                tool_id,
                episode_number,
                total_reward,
                steps,
                final_performance,
                json.dumps(final_config),
                datetime.now().isoformat()
            ))
            self.connection.commit()
            
        except Exception as e:
            logger.warning(f"Error registrando episodio: {e}")
    
    async def _record_experience(self, tool_id: str, episode_number: int, 
                               step_number: int, experience: RLExperience) -> None:
        """Registra experiencia en base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO rl_experiences 
                (tool_id, episode_number, step_number, state_data, action_data,
                 reward_value, next_state_data, done, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tool_id,
                episode_number,
                step_number,
                json.dumps(asdict(experience.state)),
                json.dumps(asdict(experience.action)),
                experience.reward.reward_value,
                json.dumps(asdict(experience.next_state)),
                experience.done,
                experience.timestamp.isoformat()
            ))
            self.connection.commit()
            
        except Exception as e:
            logger.warning(f"Error registrando experiencia: {e}")
    
    async def _get_episode_statistics(self, tool_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas de episodios desde BD"""
        try:
            cursor = self.connection.cursor()
            
            # Estadísticas básicas
            cursor.execute('''
                SELECT COUNT(*) as total_episodes,
                       AVG(total_reward) as avg_reward,
                       MAX(total_reward) as max_reward,
                       MIN(total_reward) as min_reward,
                       AVG(final_performance) as avg_performance
                FROM rl_episodes
                WHERE tool_id = ?
            ''', (tool_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_episodes': row[0],
                    'avg_reward': row[1] or 0,
                    'max_reward': row[2] or 0,
                    'min_reward': row[3] or 0,
                    'avg_performance': row[4] or 0
                }
            
        except Exception as e:
            logger.warning(f"Error obteniendo estadísticas de episodios: {e}")
        
        return {}
    
    async def _analyze_convergence(self, tool_id: str) -> Dict[str, Any]:
        """Analiza convergencia del entrenamiento"""
        try:
            cursor = self.connection.cursor()
            
            # Obtener últimos 50 episodios
            cursor.execute('''
                SELECT episode_number, total_reward, final_performance
                FROM rl_episodes
                WHERE tool_id = ?
                ORDER BY episode_number DESC
                LIMIT 50
            ''', (tool_id,))
            
            rows = cursor.fetchall()
            
            if len(rows) < 10:
                return {'converged': False, 'reason': 'Insufficient data'}
            
            # Analizar tendencia de recompensas
            rewards = [row[1] for row in reversed(rows)]
            performances = [row[2] for row in reversed(rows)]
            
            # Calcular varianza de los últimos 10 episodios
            recent_rewards = rewards[-10:]
            reward_variance = np.var(recent_rewards)
            
            # Calcular tendencia
            episodes = list(range(len(rewards)))
            reward_trend = np.polyfit(episodes, rewards, 1)[0]  # Pendiente
            
            # Determinar convergencia
            converged = (
                reward_variance < 0.1 and  # Baja varianza
                abs(reward_trend) < 0.01   # Tendencia estable
            )
            
            return {
                'converged': converged,
                'reward_variance': reward_variance,
                'reward_trend': reward_trend,
                'avg_recent_reward': np.mean(recent_rewards),
                'avg_recent_performance': np.mean(performances[-10:])
            }
            
        except Exception as e:
            logger.warning(f"Error analizando convergencia: {e}")
            return {'converged': False, 'reason': 'Analysis error'}

# Configuración por defecto
DEFAULT_RL_CONFIG = {
    'agent_config': {
        'learning_rate': 0.001,
        'epsilon': 1.0,
        'epsilon_min': 0.01,
        'epsilon_decay': 0.995,
        'gamma': 0.95,
        'batch_size': 32,
        'memory_size': 10000
    },
    'environment_config': {
        'episode_length': 50,
        'configurable_params': {
            'timeout': {'min': 10, 'max': 300, 'type': 'int'},
            'batch_size': {'min': 1, 'max': 100, 'type': 'int'},
            'retry_count': {'min': 0, 'max': 10, 'type': 'int'},
            'cache_enabled': {'type': 'bool'},
            'parallel_execution': {'type': 'bool'},
            'memory_limit': {'min': 0.1, 'max': 4.0, 'type': 'float'}
        }
    },
    'db_path': 'rl_optimization.db'
}

# Función de utilidad para crear gestor RL
async def create_rl_optimization_manager(config: Optional[Dict[str, Any]] = None) -> RLOptimizationManager:
    """Crea y configura gestor de optimización RL"""
    if config is None:
        config = DEFAULT_RL_CONFIG
    
    manager = RLOptimizationManager(config)
    await manager.initialize()
    return manager

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Crear gestor RL
        manager = await create_rl_optimization_manager()
        
        # Crear entorno para herramienta
        await manager.create_environment(
            'github_mcp_server',
            DEFAULT_RL_CONFIG['environment_config']
        )
        
        # Entrenar agente
        training_results = await manager.train_agent('github_mcp_server', num_episodes=50)
        print(f"Entrenamiento completado: {training_results}")
        
        # Obtener configuración óptima
        optimal_config = await manager.get_optimal_configuration(
            'github_mcp_server',
            {'current_load': 'high', 'user_priority': 'performance'}
        )
        print(f"Configuración óptima: {optimal_config}")
        
        # Obtener analíticas
        analytics = await manager.get_training_analytics('github_mcp_server')
        print(f"Analíticas de entrenamiento: {analytics}")
    
    # Ejecutar ejemplo
    asyncio.run(main())

