"""
Sistema de Recomendación de Herramientas MCP
Implementa algoritmos avanzados de recomendación para selección automática de herramientas
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import pickle
import sqlite3
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import networkx as nx

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolProfile:
    """Perfil de herramienta MCP con características y capacidades"""
    tool_id: str
    name: str
    description: str
    categories: List[str]
    capabilities: List[str]
    input_types: List[str]
    output_types: List[str]
    complexity_score: float
    resource_requirements: Dict[str, float]
    compatibility_matrix: Dict[str, float]
    performance_metrics: Dict[str, float]
    user_ratings: List[float]
    usage_frequency: int
    last_updated: datetime

@dataclass
class TaskProfile:
    """Perfil de tarea con características y requisitos"""
    task_id: str
    description: str
    task_type: str
    domain: str
    complexity_level: str
    required_capabilities: List[str]
    input_data_types: List[str]
    expected_output_types: List[str]
    performance_requirements: Dict[str, float]
    context: Dict[str, Any]
    user_preferences: Dict[str, Any]
    timestamp: datetime

@dataclass
class UserProfile:
    """Perfil de usuario con preferencias y patrones de uso"""
    user_id: str
    skill_level: str
    preferred_tools: List[str]
    domain_expertise: List[str]
    usage_patterns: Dict[str, Any]
    tool_ratings: Dict[str, float]
    collaboration_preferences: Dict[str, Any]
    learning_style: str
    productivity_metrics: Dict[str, float]
    last_active: datetime

@dataclass
class RecommendationResult:
    """Resultado de recomendación con herramientas sugeridas"""
    task_id: str
    recommended_tools: List[Dict[str, Any]]
    confidence_scores: List[float]
    reasoning: List[str]
    alternative_workflows: List[List[str]]
    estimated_performance: Dict[str, float]
    personalization_factors: Dict[str, float]
    explanation: str
    timestamp: datetime

class RecommendationEngine(ABC):
    """Clase base para motores de recomendación"""
    
    @abstractmethod
    async def train(self, tools: List[ToolProfile], tasks: List[TaskProfile], users: List[UserProfile]) -> None:
        """Entrena el motor de recomendación"""
        pass
    
    @abstractmethod
    async def recommend(self, task: TaskProfile, user: UserProfile, available_tools: List[str]) -> RecommendationResult:
        """Genera recomendaciones para una tarea específica"""
        pass
    
    @abstractmethod
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza el modelo con feedback del usuario"""
        pass

class ContentBasedRecommendationEngine(RecommendationEngine):
    """Motor de recomendación basado en contenido"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tool_profiles = {}
        self.task_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.tool_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.tool_feature_matrix = None
        self.capability_matrix = None
        self.is_trained = False
        
    async def train(self, tools: List[ToolProfile], tasks: List[TaskProfile], users: List[UserProfile]) -> None:
        """Entrena el motor basado en contenido"""
        try:
            # Almacenar perfiles de herramientas
            self.tool_profiles = {tool.tool_id: tool for tool in tools}
            
            # Crear matriz de características de herramientas
            await self._build_tool_feature_matrix(tools)
            
            # Crear matriz de capacidades
            await self._build_capability_matrix(tools)
            
            # Entrenar vectorizadores de texto
            tool_descriptions = [f"{tool.description} {' '.join(tool.capabilities)}" for tool in tools]
            self.tool_vectorizer.fit(tool_descriptions)
            
            if tasks:
                task_descriptions = [task.description for task in tasks]
                self.task_vectorizer.fit(task_descriptions)
            
            self.is_trained = True
            logger.info(f"Motor de recomendación basado en contenido entrenado con {len(tools)} herramientas")
            
        except Exception as e:
            logger.error(f"Error entrenando motor basado en contenido: {e}")
            raise
    
    async def _build_tool_feature_matrix(self, tools: List[ToolProfile]) -> None:
        """Construye matriz de características de herramientas"""
        features = []
        
        for tool in tools:
            feature_vector = []
            
            # Características numéricas
            feature_vector.append(tool.complexity_score)
            feature_vector.extend(tool.resource_requirements.values())
            feature_vector.extend(tool.performance_metrics.values())
            feature_vector.append(np.mean(tool.user_ratings) if tool.user_ratings else 0.0)
            feature_vector.append(tool.usage_frequency)
            
            # Características categóricas (one-hot encoding simplificado)
            all_categories = ['development', 'testing', 'deployment', 'monitoring', 'analysis']
            category_vector = [1.0 if cat in tool.categories else 0.0 for cat in all_categories]
            feature_vector.extend(category_vector)
            
            all_capabilities = ['file_management', 'version_control', 'container_management', 
                              'code_execution', 'data_analysis', 'visualization']
            capability_vector = [1.0 if cap in tool.capabilities else 0.0 for cap in all_capabilities]
            feature_vector.extend(capability_vector)
            
            features.append(feature_vector)
        
        self.tool_feature_matrix = np.array(features)
        
        # Normalizar características
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        self.tool_feature_matrix = scaler.fit_transform(self.tool_feature_matrix)
    
    async def _build_capability_matrix(self, tools: List[ToolProfile]) -> None:
        """Construye matriz de capacidades herramienta-capacidad"""
        all_capabilities = set()
        for tool in tools:
            all_capabilities.update(tool.capabilities)
        
        all_capabilities = sorted(list(all_capabilities))
        capability_matrix = []
        
        for tool in tools:
            capability_vector = [1.0 if cap in tool.capabilities else 0.0 for cap in all_capabilities]
            capability_matrix.append(capability_vector)
        
        self.capability_matrix = np.array(capability_matrix)
        self.capability_names = all_capabilities
    
    async def recommend(self, task: TaskProfile, user: UserProfile, available_tools: List[str]) -> RecommendationResult:
        """Genera recomendaciones basadas en similitud de contenido"""
        try:
            if not self.is_trained:
                raise ValueError("Motor no entrenado")
            
            # Filtrar herramientas disponibles
            available_tool_profiles = [self.tool_profiles[tool_id] for tool_id in available_tools 
                                     if tool_id in self.tool_profiles]
            
            if not available_tool_profiles:
                return self._empty_recommendation(task.task_id)
            
            # Calcular similitud basada en capacidades requeridas
            capability_scores = await self._calculate_capability_similarity(task, available_tool_profiles)
            
            # Calcular similitud textual
            text_scores = await self._calculate_text_similarity(task, available_tool_profiles)
            
            # Calcular similitud de contexto
            context_scores = await self._calculate_context_similarity(task, available_tool_profiles)
            
            # Aplicar preferencias del usuario
            user_preference_scores = await self._apply_user_preferences(user, available_tool_profiles)
            
            # Combinar puntuaciones
            combined_scores = await self._combine_scores(
                capability_scores, text_scores, context_scores, user_preference_scores
            )
            
            # Generar recomendaciones finales
            recommendations = await self._generate_final_recommendations(
                task, available_tool_profiles, combined_scores
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones basadas en contenido: {e}")
            return self._empty_recommendation(task.task_id)
    
    async def _calculate_capability_similarity(self, task: TaskProfile, tools: List[ToolProfile]) -> np.ndarray:
        """Calcula similitud basada en capacidades requeridas"""
        required_capabilities = set(task.required_capabilities)
        scores = []
        
        for tool in tools:
            tool_capabilities = set(tool.capabilities)
            
            # Jaccard similarity
            intersection = len(required_capabilities.intersection(tool_capabilities))
            union = len(required_capabilities.union(tool_capabilities))
            
            if union == 0:
                similarity = 0.0
            else:
                similarity = intersection / union
            
            # Bonus por capacidades críticas
            critical_match_bonus = 0.0
            for req_cap in required_capabilities:
                if req_cap in tool_capabilities:
                    critical_match_bonus += 0.1
            
            final_score = min(1.0, similarity + critical_match_bonus)
            scores.append(final_score)
        
        return np.array(scores)
    
    async def _calculate_text_similarity(self, task: TaskProfile, tools: List[ToolProfile]) -> np.ndarray:
        """Calcula similitud textual entre descripción de tarea y herramientas"""
        try:
            # Vectorizar descripción de tarea
            task_vector = self.task_vectorizer.transform([task.description])
            
            # Vectorizar descripciones de herramientas
            tool_descriptions = [f"{tool.description} {' '.join(tool.capabilities)}" for tool in tools]
            tool_vectors = self.tool_vectorizer.transform(tool_descriptions)
            
            # Calcular similitud coseno
            similarities = cosine_similarity(task_vector, tool_vectors).flatten()
            
            return similarities
            
        except Exception as e:
            logger.warning(f"Error calculando similitud textual: {e}")
            return np.zeros(len(tools))
    
    async def _calculate_context_similarity(self, task: TaskProfile, tools: List[ToolProfile]) -> np.ndarray:
        """Calcula similitud basada en contexto de la tarea"""
        scores = []
        
        for tool in tools:
            score = 0.0
            
            # Similitud de dominio
            if task.domain in tool.categories:
                score += 0.3
            
            # Similitud de complejidad
            complexity_mapping = {'low': 1, 'medium': 2, 'high': 3}
            task_complexity = complexity_mapping.get(task.complexity_level, 2)
            tool_complexity = tool.complexity_score
            
            complexity_diff = abs(task_complexity - tool_complexity)
            complexity_score = max(0, 1.0 - complexity_diff / 3.0)
            score += 0.2 * complexity_score
            
            # Similitud de tipos de datos
            input_match = len(set(task.input_data_types).intersection(set(tool.input_types)))
            output_match = len(set(task.expected_output_types).intersection(set(tool.output_types)))
            
            if len(task.input_data_types) > 0:
                score += 0.25 * (input_match / len(task.input_data_types))
            if len(task.expected_output_types) > 0:
                score += 0.25 * (output_match / len(task.expected_output_types))
            
            scores.append(min(1.0, score))
        
        return np.array(scores)
    
    async def _apply_user_preferences(self, user: UserProfile, tools: List[ToolProfile]) -> np.ndarray:
        """Aplica preferencias del usuario a las puntuaciones"""
        scores = []
        
        for tool in tools:
            score = 0.0
            
            # Preferencia por herramientas específicas
            if tool.tool_id in user.preferred_tools:
                score += 0.4
            
            # Rating del usuario para la herramienta
            if tool.tool_id in user.tool_ratings:
                score += 0.3 * (user.tool_ratings[tool.tool_id] / 5.0)
            
            # Compatibilidad con nivel de habilidad
            skill_mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            user_skill = skill_mapping.get(user.skill_level, 2)
            
            if tool.complexity_score <= user_skill:
                score += 0.2
            elif tool.complexity_score > user_skill + 1:
                score -= 0.1  # Penalizar herramientas demasiado complejas
            
            # Experiencia en dominio
            tool_domains = set(tool.categories)
            user_domains = set(user.domain_expertise)
            domain_overlap = len(tool_domains.intersection(user_domains))
            
            if domain_overlap > 0:
                score += 0.1 * (domain_overlap / len(tool_domains))
            
            scores.append(max(0.0, min(1.0, score)))
        
        return np.array(scores)
    
    async def _combine_scores(self, capability_scores: np.ndarray, text_scores: np.ndarray, 
                            context_scores: np.ndarray, user_scores: np.ndarray) -> np.ndarray:
        """Combina diferentes puntuaciones con pesos"""
        weights = self.config.get('score_weights', {
            'capability': 0.4,
            'text': 0.2,
            'context': 0.25,
            'user': 0.15
        })
        
        combined = (
            weights['capability'] * capability_scores +
            weights['text'] * text_scores +
            weights['context'] * context_scores +
            weights['user'] * user_scores
        )
        
        return combined
    
    async def _generate_final_recommendations(self, task: TaskProfile, tools: List[ToolProfile], 
                                            scores: np.ndarray) -> RecommendationResult:
        """Genera recomendaciones finales ordenadas por puntuación"""
        # Ordenar herramientas por puntuación
        sorted_indices = np.argsort(scores)[::-1]
        
        max_recommendations = self.config.get('max_recommendations', 5)
        top_indices = sorted_indices[:max_recommendations]
        
        recommended_tools = []
        confidence_scores = []
        reasoning = []
        
        for idx in top_indices:
            tool = tools[idx]
            score = scores[idx]
            
            recommended_tools.append({
                'tool_id': tool.tool_id,
                'name': tool.name,
                'description': tool.description,
                'categories': tool.categories,
                'score': float(score)
            })
            
            confidence_scores.append(float(score))
            
            # Generar explicación
            explanation_parts = []
            if score > 0.8:
                explanation_parts.append("Excelente coincidencia de capacidades")
            elif score > 0.6:
                explanation_parts.append("Buena coincidencia de capacidades")
            else:
                explanation_parts.append("Coincidencia parcial de capacidades")
            
            reasoning.append("; ".join(explanation_parts))
        
        # Generar flujos de trabajo alternativos
        alternative_workflows = await self._generate_alternative_workflows(task, tools, scores)
        
        # Estimar rendimiento
        estimated_performance = await self._estimate_performance(task, recommended_tools)
        
        return RecommendationResult(
            task_id=task.task_id,
            recommended_tools=recommended_tools,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            alternative_workflows=alternative_workflows,
            estimated_performance=estimated_performance,
            personalization_factors={'content_based': 1.0},
            explanation=f"Recomendaciones basadas en análisis de contenido y capacidades para tarea de tipo '{task.task_type}'",
            timestamp=datetime.now()
        )
    
    async def _generate_alternative_workflows(self, task: TaskProfile, tools: List[ToolProfile], 
                                            scores: np.ndarray) -> List[List[str]]:
        """Genera flujos de trabajo alternativos"""
        workflows = []
        
        # Workflow secuencial simple
        sorted_indices = np.argsort(scores)[::-1]
        if len(sorted_indices) >= 2:
            workflow1 = [tools[sorted_indices[0]].tool_id, tools[sorted_indices[1]].tool_id]
            workflows.append(workflow1)
        
        # Workflow paralelo
        if len(sorted_indices) >= 3:
            workflow2 = [tools[sorted_indices[0]].tool_id, tools[sorted_indices[2]].tool_id]
            workflows.append(workflow2)
        
        return workflows
    
    async def _estimate_performance(self, task: TaskProfile, recommended_tools: List[Dict[str, Any]]) -> Dict[str, float]:
        """Estima rendimiento esperado"""
        if not recommended_tools:
            return {'estimated_success_rate': 0.0, 'estimated_execution_time': 0.0}
        
        # Estimación simple basada en puntuaciones
        avg_score = np.mean([tool['score'] for tool in recommended_tools])
        
        return {
            'estimated_success_rate': min(0.95, avg_score * 0.9 + 0.1),
            'estimated_execution_time': max(1.0, 100.0 * (1.0 - avg_score)),
            'confidence_level': avg_score
        }
    
    def _empty_recommendation(self, task_id: str) -> RecommendationResult:
        """Genera recomendación vacía cuando no hay herramientas disponibles"""
        return RecommendationResult(
            task_id=task_id,
            recommended_tools=[],
            confidence_scores=[],
            reasoning=["No hay herramientas disponibles"],
            alternative_workflows=[],
            estimated_performance={'estimated_success_rate': 0.0},
            personalization_factors={},
            explanation="No se encontraron herramientas compatibles",
            timestamp=datetime.now()
        )
    
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza modelo con feedback del usuario"""
        try:
            tool_id = feedback.get('tool_id')
            rating = feedback.get('rating', 0.0)
            success = feedback.get('success', False)
            
            if tool_id in self.tool_profiles:
                tool = self.tool_profiles[tool_id]
                
                # Actualizar ratings
                tool.user_ratings.append(rating)
                
                # Actualizar métricas de rendimiento
                if 'execution_time' in feedback:
                    current_time = tool.performance_metrics.get('avg_execution_time', 0.0)
                    new_time = feedback['execution_time']
                    # Media móvil simple
                    tool.performance_metrics['avg_execution_time'] = (current_time + new_time) / 2
                
                if success:
                    tool.performance_metrics['success_rate'] = tool.performance_metrics.get('success_rate', 0.5) * 0.9 + 0.1
                else:
                    tool.performance_metrics['success_rate'] = tool.performance_metrics.get('success_rate', 0.5) * 0.9
                
                tool.usage_frequency += 1
                tool.last_updated = datetime.now()
                
                logger.info(f"Modelo actualizado para herramienta {tool_id}")
                
        except Exception as e:
            logger.error(f"Error actualizando modelo con feedback: {e}")

class CollaborativeFilteringEngine(RecommendationEngine):
    """Motor de recomendación basado en filtrado colaborativo"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.user_tool_matrix = None
        self.user_similarity_matrix = None
        self.tool_similarity_matrix = None
        self.user_profiles = {}
        self.tool_profiles = {}
        self.svd_model = None
        self.is_trained = False
        
    async def train(self, tools: List[ToolProfile], tasks: List[TaskProfile], users: List[UserProfile]) -> None:
        """Entrena el motor de filtrado colaborativo"""
        try:
            self.user_profiles = {user.user_id: user for user in users}
            self.tool_profiles = {tool.tool_id: tool for tool in tools}
            
            # Construir matriz usuario-herramienta
            await self._build_user_tool_matrix(users, tools)
            
            # Calcular matrices de similitud
            await self._calculate_similarity_matrices()
            
            # Entrenar modelo SVD para factorización de matrices
            await self._train_svd_model()
            
            self.is_trained = True
            logger.info(f"Motor de filtrado colaborativo entrenado con {len(users)} usuarios y {len(tools)} herramientas")
            
        except Exception as e:
            logger.error(f"Error entrenando motor de filtrado colaborativo: {e}")
            raise
    
    async def _build_user_tool_matrix(self, users: List[UserProfile], tools: List[ToolProfile]) -> None:
        """Construye matriz de interacciones usuario-herramienta"""
        user_ids = [user.user_id for user in users]
        tool_ids = [tool.tool_id for tool in tools]
        
        matrix = np.zeros((len(user_ids), len(tool_ids)))
        
        for i, user in enumerate(users):
            for j, tool in enumerate(tools):
                # Usar ratings del usuario si están disponibles
                if tool.tool_id in user.tool_ratings:
                    matrix[i, j] = user.tool_ratings[tool.tool_id]
                # Usar preferencias implícitas
                elif tool.tool_id in user.preferred_tools:
                    matrix[i, j] = 4.0  # Rating implícito alto
                # Usar patrones de uso
                elif tool.tool_id in user.usage_patterns.get('frequently_used', []):
                    matrix[i, j] = 3.0
                elif tool.tool_id in user.usage_patterns.get('occasionally_used', []):
                    matrix[i, j] = 2.0
        
        self.user_tool_matrix = matrix
        self.user_ids = user_ids
        self.tool_ids = tool_ids
    
    async def _calculate_similarity_matrices(self) -> None:
        """Calcula matrices de similitud usuario-usuario y herramienta-herramienta"""
        # Similitud entre usuarios (basada en coseno)
        self.user_similarity_matrix = cosine_similarity(self.user_tool_matrix)
        
        # Similitud entre herramientas (basada en coseno)
        self.tool_similarity_matrix = cosine_similarity(self.user_tool_matrix.T)
    
    async def _train_svd_model(self) -> None:
        """Entrena modelo SVD para factorización de matrices"""
        n_components = min(50, min(self.user_tool_matrix.shape) - 1)
        if n_components > 0:
            self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
            self.svd_model.fit(self.user_tool_matrix)
    
    async def recommend(self, task: TaskProfile, user: UserProfile, available_tools: List[str]) -> RecommendationResult:
        """Genera recomendaciones usando filtrado colaborativo"""
        try:
            if not self.is_trained:
                raise ValueError("Motor no entrenado")
            
            user_idx = self.user_ids.index(user.user_id) if user.user_id in self.user_ids else None
            
            if user_idx is None:
                # Usuario nuevo - usar recomendaciones populares
                return await self._recommend_for_new_user(task, available_tools)
            
            # Filtrar herramientas disponibles
            available_tool_indices = [self.tool_ids.index(tool_id) for tool_id in available_tools 
                                    if tool_id in self.tool_ids]
            
            if not available_tool_indices:
                return self._empty_recommendation(task.task_id)
            
            # Generar recomendaciones basadas en usuarios similares
            user_based_scores = await self._user_based_recommendations(user_idx, available_tool_indices)
            
            # Generar recomendaciones basadas en herramientas similares
            item_based_scores = await self._item_based_recommendations(user_idx, available_tool_indices)
            
            # Generar recomendaciones usando SVD
            svd_scores = await self._svd_based_recommendations(user_idx, available_tool_indices)
            
            # Combinar puntuaciones
            combined_scores = await self._combine_collaborative_scores(
                user_based_scores, item_based_scores, svd_scores
            )
            
            # Generar recomendaciones finales
            recommendations = await self._generate_collaborative_recommendations(
                task, user, available_tools, available_tool_indices, combined_scores
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones colaborativas: {e}")
            return self._empty_recommendation(task.task_id)
    
    async def _user_based_recommendations(self, user_idx: int, available_tool_indices: List[int]) -> np.ndarray:
        """Genera recomendaciones basadas en usuarios similares"""
        user_similarities = self.user_similarity_matrix[user_idx]
        user_ratings = self.user_tool_matrix[user_idx]
        
        scores = np.zeros(len(available_tool_indices))
        
        for i, tool_idx in enumerate(available_tool_indices):
            if user_ratings[tool_idx] > 0:
                # Usuario ya ha interactuado con esta herramienta
                scores[i] = user_ratings[tool_idx]
                continue
            
            # Calcular puntuación basada en usuarios similares
            numerator = 0.0
            denominator = 0.0
            
            for other_user_idx in range(len(user_similarities)):
                if other_user_idx == user_idx:
                    continue
                
                similarity = user_similarities[other_user_idx]
                other_rating = self.user_tool_matrix[other_user_idx, tool_idx]
                
                if similarity > 0.1 and other_rating > 0:
                    numerator += similarity * other_rating
                    denominator += abs(similarity)
            
            if denominator > 0:
                scores[i] = numerator / denominator
            else:
                scores[i] = 0.0
        
        return scores
    
    async def _item_based_recommendations(self, user_idx: int, available_tool_indices: List[int]) -> np.ndarray:
        """Genera recomendaciones basadas en herramientas similares"""
        user_ratings = self.user_tool_matrix[user_idx]
        scores = np.zeros(len(available_tool_indices))
        
        for i, tool_idx in enumerate(available_tool_indices):
            if user_ratings[tool_idx] > 0:
                # Usuario ya ha interactuado con esta herramienta
                scores[i] = user_ratings[tool_idx]
                continue
            
            # Calcular puntuación basada en herramientas similares
            numerator = 0.0
            denominator = 0.0
            
            tool_similarities = self.tool_similarity_matrix[tool_idx]
            
            for other_tool_idx in range(len(tool_similarities)):
                if other_tool_idx == tool_idx:
                    continue
                
                similarity = tool_similarities[other_tool_idx]
                user_rating = user_ratings[other_tool_idx]
                
                if similarity > 0.1 and user_rating > 0:
                    numerator += similarity * user_rating
                    denominator += abs(similarity)
            
            if denominator > 0:
                scores[i] = numerator / denominator
            else:
                scores[i] = 0.0
        
        return scores
    
    async def _svd_based_recommendations(self, user_idx: int, available_tool_indices: List[int]) -> np.ndarray:
        """Genera recomendaciones usando factorización SVD"""
        if self.svd_model is None:
            return np.zeros(len(available_tool_indices))
        
        # Reconstruir matriz usando SVD
        reconstructed_matrix = self.svd_model.inverse_transform(
            self.svd_model.transform(self.user_tool_matrix)
        )
        
        user_predictions = reconstructed_matrix[user_idx]
        scores = np.array([user_predictions[tool_idx] for tool_idx in available_tool_indices])
        
        return scores
    
    async def _combine_collaborative_scores(self, user_based: np.ndarray, item_based: np.ndarray, 
                                          svd_based: np.ndarray) -> np.ndarray:
        """Combina puntuaciones de diferentes métodos colaborativos"""
        weights = self.config.get('collaborative_weights', {
            'user_based': 0.4,
            'item_based': 0.4,
            'svd_based': 0.2
        })
        
        combined = (
            weights['user_based'] * user_based +
            weights['item_based'] * item_based +
            weights['svd_based'] * svd_based
        )
        
        return combined
    
    async def _recommend_for_new_user(self, task: TaskProfile, available_tools: List[str]) -> RecommendationResult:
        """Genera recomendaciones para usuario nuevo basadas en popularidad"""
        # Calcular popularidad de herramientas
        tool_popularity = {}
        
        for tool_id in available_tools:
            if tool_id in self.tool_profiles:
                tool = self.tool_profiles[tool_id]
                popularity = (
                    tool.usage_frequency * 0.4 +
                    np.mean(tool.user_ratings) * 0.3 +
                    len(tool.user_ratings) * 0.3
                ) if tool.user_ratings else tool.usage_frequency
                
                tool_popularity[tool_id] = popularity
        
        # Ordenar por popularidad
        sorted_tools = sorted(tool_popularity.items(), key=lambda x: x[1], reverse=True)
        
        max_recommendations = self.config.get('max_recommendations', 5)
        top_tools = sorted_tools[:max_recommendations]
        
        recommended_tools = []
        confidence_scores = []
        reasoning = []
        
        for tool_id, popularity in top_tools:
            tool = self.tool_profiles[tool_id]
            
            recommended_tools.append({
                'tool_id': tool_id,
                'name': tool.name,
                'description': tool.description,
                'categories': tool.categories,
                'score': min(1.0, popularity / 100.0)
            })
            
            confidence_scores.append(min(1.0, popularity / 100.0))
            reasoning.append("Recomendación basada en popularidad para usuario nuevo")
        
        return RecommendationResult(
            task_id=task.task_id,
            recommended_tools=recommended_tools,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            alternative_workflows=[],
            estimated_performance={'estimated_success_rate': 0.7},
            personalization_factors={'new_user_popularity': 1.0},
            explanation="Recomendaciones basadas en popularidad para usuario nuevo",
            timestamp=datetime.now()
        )
    
    async def _generate_collaborative_recommendations(self, task: TaskProfile, user: UserProfile,
                                                    available_tools: List[str], available_tool_indices: List[int],
                                                    scores: np.ndarray) -> RecommendationResult:
        """Genera recomendaciones finales colaborativas"""
        # Ordenar por puntuación
        sorted_indices = np.argsort(scores)[::-1]
        
        max_recommendations = self.config.get('max_recommendations', 5)
        top_indices = sorted_indices[:max_recommendations]
        
        recommended_tools = []
        confidence_scores = []
        reasoning = []
        
        for idx in top_indices:
            tool_idx = available_tool_indices[idx]
            tool_id = self.tool_ids[tool_idx]
            tool = self.tool_profiles[tool_id]
            score = scores[idx]
            
            recommended_tools.append({
                'tool_id': tool_id,
                'name': tool.name,
                'description': tool.description,
                'categories': tool.categories,
                'score': float(score)
            })
            
            confidence_scores.append(float(score))
            reasoning.append("Recomendación basada en patrones de usuarios similares")
        
        return RecommendationResult(
            task_id=task.task_id,
            recommended_tools=recommended_tools,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            alternative_workflows=[],
            estimated_performance={'estimated_success_rate': min(0.9, np.mean(scores) * 0.8 + 0.1)},
            personalization_factors={'collaborative_filtering': 1.0},
            explanation="Recomendaciones basadas en filtrado colaborativo y usuarios similares",
            timestamp=datetime.now()
        )
    
    def _empty_recommendation(self, task_id: str) -> RecommendationResult:
        """Genera recomendación vacía"""
        return RecommendationResult(
            task_id=task_id,
            recommended_tools=[],
            confidence_scores=[],
            reasoning=["No hay datos suficientes para recomendaciones colaborativas"],
            alternative_workflows=[],
            estimated_performance={'estimated_success_rate': 0.0},
            personalization_factors={},
            explanation="Datos insuficientes para filtrado colaborativo",
            timestamp=datetime.now()
        )
    
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza modelo colaborativo con feedback"""
        try:
            user_id = feedback.get('user_id')
            tool_id = feedback.get('tool_id')
            rating = feedback.get('rating', 0.0)
            
            if user_id in self.user_ids and tool_id in self.tool_ids:
                user_idx = self.user_ids.index(user_id)
                tool_idx = self.tool_ids.index(tool_id)
                
                # Actualizar matriz usuario-herramienta
                self.user_tool_matrix[user_idx, tool_idx] = rating
                
                # Recalcular matrices de similitud (simplificado)
                await self._calculate_similarity_matrices()
                
                logger.info(f"Modelo colaborativo actualizado para usuario {user_id}, herramienta {tool_id}")
                
        except Exception as e:
            logger.error(f"Error actualizando modelo colaborativo: {e}")

class HybridRecommendationEngine(RecommendationEngine):
    """Motor de recomendación híbrido que combina múltiples enfoques"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.content_engine = ContentBasedRecommendationEngine(config.get('content_based', {}))
        self.collaborative_engine = CollaborativeFilteringEngine(config.get('collaborative', {}))
        self.is_trained = False
        
    async def train(self, tools: List[ToolProfile], tasks: List[TaskProfile], users: List[UserProfile]) -> None:
        """Entrena ambos motores de recomendación"""
        try:
            # Entrenar motores en paralelo
            await asyncio.gather(
                self.content_engine.train(tools, tasks, users),
                self.collaborative_engine.train(tools, tasks, users)
            )
            
            self.is_trained = True
            logger.info("Motor de recomendación híbrido entrenado exitosamente")
            
        except Exception as e:
            logger.error(f"Error entrenando motor híbrido: {e}")
            raise
    
    async def recommend(self, task: TaskProfile, user: UserProfile, available_tools: List[str]) -> RecommendationResult:
        """Genera recomendaciones híbridas combinando múltiples enfoques"""
        try:
            if not self.is_trained:
                raise ValueError("Motor híbrido no entrenado")
            
            # Obtener recomendaciones de ambos motores
            content_recommendations, collaborative_recommendations = await asyncio.gather(
                self.content_engine.recommend(task, user, available_tools),
                self.collaborative_engine.recommend(task, user, available_tools),
                return_exceptions=True
            )
            
            # Manejar errores en motores individuales
            if isinstance(content_recommendations, Exception):
                logger.warning(f"Error en motor basado en contenido: {content_recommendations}")
                content_recommendations = self._empty_recommendation(task.task_id)
            
            if isinstance(collaborative_recommendations, Exception):
                logger.warning(f"Error en motor colaborativo: {collaborative_recommendations}")
                collaborative_recommendations = self._empty_recommendation(task.task_id)
            
            # Combinar recomendaciones
            hybrid_recommendations = await self._combine_recommendations(
                task, content_recommendations, collaborative_recommendations
            )
            
            return hybrid_recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones híbridas: {e}")
            return self._empty_recommendation(task.task_id)
    
    async def _combine_recommendations(self, task: TaskProfile, 
                                     content_rec: RecommendationResult,
                                     collaborative_rec: RecommendationResult) -> RecommendationResult:
        """Combina recomendaciones de múltiples motores"""
        # Pesos para combinación
        weights = self.config.get('hybrid_weights', {
            'content_based': 0.6,
            'collaborative': 0.4
        })
        
        # Crear diccionario de herramientas con puntuaciones combinadas
        tool_scores = {}
        
        # Agregar puntuaciones del motor basado en contenido
        for i, tool in enumerate(content_rec.recommended_tools):
            tool_id = tool['tool_id']
            score = content_rec.confidence_scores[i] if i < len(content_rec.confidence_scores) else 0.0
            tool_scores[tool_id] = {
                'tool_info': tool,
                'content_score': score,
                'collaborative_score': 0.0,
                'content_reasoning': content_rec.reasoning[i] if i < len(content_rec.reasoning) else ""
            }
        
        # Agregar puntuaciones del motor colaborativo
        for i, tool in enumerate(collaborative_rec.recommended_tools):
            tool_id = tool['tool_id']
            score = collaborative_rec.confidence_scores[i] if i < len(collaborative_rec.confidence_scores) else 0.0
            
            if tool_id in tool_scores:
                tool_scores[tool_id]['collaborative_score'] = score
            else:
                tool_scores[tool_id] = {
                    'tool_info': tool,
                    'content_score': 0.0,
                    'collaborative_score': score,
                    'content_reasoning': ""
                }
        
        # Calcular puntuaciones híbridas
        for tool_id, scores in tool_scores.items():
            hybrid_score = (
                weights['content_based'] * scores['content_score'] +
                weights['collaborative'] * scores['collaborative_score']
            )
            scores['hybrid_score'] = hybrid_score
        
        # Ordenar por puntuación híbrida
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1]['hybrid_score'], reverse=True)
        
        # Generar recomendaciones finales
        max_recommendations = self.config.get('max_recommendations', 5)
        top_tools = sorted_tools[:max_recommendations]
        
        recommended_tools = []
        confidence_scores = []
        reasoning = []
        
        for tool_id, scores in top_tools:
            recommended_tools.append(scores['tool_info'])
            confidence_scores.append(scores['hybrid_score'])
            
            # Combinar explicaciones
            explanations = []
            if scores['content_score'] > 0:
                explanations.append(f"Contenido: {scores['content_reasoning']}")
            if scores['collaborative_score'] > 0:
                explanations.append("Colaborativo: Basado en usuarios similares")
            
            reasoning.append("; ".join(explanations) if explanations else "Recomendación híbrida")
        
        # Combinar flujos de trabajo alternativos
        alternative_workflows = []
        alternative_workflows.extend(content_rec.alternative_workflows)
        alternative_workflows.extend(collaborative_rec.alternative_workflows)
        
        # Combinar estimaciones de rendimiento
        content_perf = content_rec.estimated_performance
        collab_perf = collaborative_rec.estimated_performance
        
        estimated_performance = {
            'estimated_success_rate': (
                weights['content_based'] * content_perf.get('estimated_success_rate', 0.0) +
                weights['collaborative'] * collab_perf.get('estimated_success_rate', 0.0)
            ),
            'confidence_level': np.mean(confidence_scores) if confidence_scores else 0.0
        }
        
        return RecommendationResult(
            task_id=task.task_id,
            recommended_tools=recommended_tools,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            alternative_workflows=alternative_workflows,
            estimated_performance=estimated_performance,
            personalization_factors={
                'hybrid_content_weight': weights['content_based'],
                'hybrid_collaborative_weight': weights['collaborative']
            },
            explanation=f"Recomendaciones híbridas combinando análisis de contenido ({weights['content_based']:.0%}) y filtrado colaborativo ({weights['collaborative']:.0%})",
            timestamp=datetime.now()
        )
    
    def _empty_recommendation(self, task_id: str) -> RecommendationResult:
        """Genera recomendación vacía"""
        return RecommendationResult(
            task_id=task_id,
            recommended_tools=[],
            confidence_scores=[],
            reasoning=["No hay recomendaciones disponibles"],
            alternative_workflows=[],
            estimated_performance={'estimated_success_rate': 0.0},
            personalization_factors={},
            explanation="No se pudieron generar recomendaciones",
            timestamp=datetime.now()
        )
    
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Actualiza ambos motores con feedback"""
        try:
            await asyncio.gather(
                self.content_engine.update_model(feedback),
                self.collaborative_engine.update_model(feedback),
                return_exceptions=True
            )
            
            logger.info("Motores híbridos actualizados con feedback")
            
        except Exception as e:
            logger.error(f"Error actualizando motores híbridos: {e}")

# Configuración por defecto
DEFAULT_RECOMMENDATION_CONFIG = {
    'content_based': {
        'max_recommendations': 5,
        'score_weights': {
            'capability': 0.4,
            'text': 0.2,
            'context': 0.25,
            'user': 0.15
        }
    },
    'collaborative': {
        'max_recommendations': 5,
        'collaborative_weights': {
            'user_based': 0.4,
            'item_based': 0.4,
            'svd_based': 0.2
        }
    },
    'hybrid_weights': {
        'content_based': 0.6,
        'collaborative': 0.4
    },
    'max_recommendations': 5
}

# Función de utilidad para crear motor de recomendación
async def create_recommendation_engine(engine_type: str = 'hybrid', 
                                     config: Optional[Dict[str, Any]] = None) -> RecommendationEngine:
    """Crea motor de recomendación del tipo especificado"""
    if config is None:
        config = DEFAULT_RECOMMENDATION_CONFIG
    
    if engine_type == 'content_based':
        return ContentBasedRecommendationEngine(config.get('content_based', {}))
    elif engine_type == 'collaborative':
        return CollaborativeFilteringEngine(config.get('collaborative', {}))
    elif engine_type == 'hybrid':
        return HybridRecommendationEngine(config)
    else:
        raise ValueError(f"Tipo de motor no soportado: {engine_type}")

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Crear motor híbrido
        engine = await create_recommendation_engine('hybrid')
        
        # Datos de ejemplo
        tools = [
            ToolProfile(
                tool_id="github_mcp_server",
                name="GitHub MCP Server",
                description="Gestión de repositorios Git y GitHub",
                categories=["development", "version_control"],
                capabilities=["version_control", "code_review", "issue_management"],
                input_types=["code", "text"],
                output_types=["repository", "pull_request"],
                complexity_score=2.0,
                resource_requirements={"cpu": 0.5, "memory": 1.0},
                compatibility_matrix={"docker_mcp_server": 0.8},
                performance_metrics={"avg_execution_time": 30.0, "success_rate": 0.95},
                user_ratings=[4.5, 4.0, 5.0],
                usage_frequency=150,
                last_updated=datetime.now()
            )
        ]
        
        users = [
            UserProfile(
                user_id="user123",
                skill_level="intermediate",
                preferred_tools=["github_mcp_server"],
                domain_expertise=["development", "testing"],
                usage_patterns={"frequently_used": ["github_mcp_server"]},
                tool_ratings={"github_mcp_server": 4.5},
                collaboration_preferences={"team_size": "medium"},
                learning_style="hands_on",
                productivity_metrics={"tasks_per_day": 8.5},
                last_active=datetime.now()
            )
        ]
        
        tasks = [
            TaskProfile(
                task_id="task123",
                description="Revisar código y crear pull request",
                task_type="code_review",
                domain="development",
                complexity_level="medium",
                required_capabilities=["version_control", "code_review"],
                input_data_types=["code"],
                expected_output_types=["pull_request"],
                performance_requirements={"max_time": 60.0},
                context={"repository_size": "large"},
                user_preferences={"automated": True},
                timestamp=datetime.now()
            )
        ]
        
        # Entrenar motor
        await engine.train(tools, tasks, users)
        
        # Generar recomendación
        recommendation = await engine.recommend(
            tasks[0], users[0], ["github_mcp_server"]
        )
        
        print(f"Recomendación: {recommendation}")
    
    # Ejecutar ejemplo
    asyncio.run(main())

