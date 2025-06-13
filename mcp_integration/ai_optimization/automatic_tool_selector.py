"""
Motor de Decisión Automática para Selección de Herramientas MCP
================================================================

Este módulo implementa el motor de decisión automática que selecciona
transparentemente las herramientas MCP más apropiadas para cada tarea
solicitada por el usuario, sin requerir intervención manual del usuario.

Características principales:
- Selección automática basada en análisis de la tarea
- Transparencia total para el usuario final
- Aprendizaje continuo de patrones de éxito
- Fallback a herramientas por defecto cuando sea necesario
- Logging detallado para administradores
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskCategory(Enum):
    """Categorías de tareas para clasificación automática"""
    CODE_DEVELOPMENT = "code_development"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    DOCUMENTATION = "documentation"
    DATA_ANALYSIS = "data_analysis"
    SYSTEM_ADMINISTRATION = "system_administration"
    RESEARCH = "research"
    GENERAL = "general"

class ToolCapability(Enum):
    """Capacidades que pueden tener las herramientas MCP"""
    FILE_MANAGEMENT = "file_management"
    CODE_EXECUTION = "code_execution"
    VERSION_CONTROL = "version_control"
    CONTAINER_MANAGEMENT = "container_management"
    DATABASE_ACCESS = "database_access"
    API_INTERACTION = "api_interaction"
    TEXT_PROCESSING = "text_processing"
    IMAGE_PROCESSING = "image_processing"
    NETWORK_OPERATIONS = "network_operations"
    SYSTEM_MONITORING = "system_monitoring"

@dataclass
class ToolMetadata:
    """Metadatos de una herramienta MCP para decisión automática"""
    name: str
    capabilities: List[ToolCapability]
    task_categories: List[TaskCategory]
    success_rate: float
    average_execution_time: float
    resource_usage: Dict[str, float]  # CPU, memoria, etc.
    reliability_score: float
    last_updated: datetime
    configuration_complexity: int  # 1-10, donde 10 es más complejo
    admin_only: bool = False

@dataclass
class TaskAnalysis:
    """Resultado del análisis automático de una tarea"""
    task_text: str
    detected_category: TaskCategory
    required_capabilities: List[ToolCapability]
    complexity_score: float
    urgency_level: int  # 1-5
    estimated_duration: float
    context_keywords: List[str]
    confidence_score: float

class AutomaticToolSelector:
    """
    Motor principal de selección automática de herramientas MCP
    """
    
    def __init__(self):
        self.tool_registry: Dict[str, ToolMetadata] = {}
        self.task_patterns: Dict[str, TaskCategory] = {}
        self.capability_mappings: Dict[str, List[ToolCapability]] = {}
        self.success_history: Dict[str, List[Dict]] = {}
        self.learning_enabled = True
        
        # Inicializar patrones de tareas
        self._initialize_task_patterns()
        self._initialize_capability_mappings()
        
    def _initialize_task_patterns(self):
        """Inicializa patrones de reconocimiento de tareas"""
        self.task_patterns = {
            # Desarrollo de código
            r'(crear|desarrollar|programar|codificar|implementar).*(aplicación|app|código|función|clase|módulo)': TaskCategory.CODE_DEVELOPMENT,
            r'(escribir|generar).*(código|script|programa)': TaskCategory.CODE_DEVELOPMENT,
            r'(construir|build).*(proyecto|aplicación)': TaskCategory.CODE_DEVELOPMENT,
            
            # Revisión de código
            r'(revisar|analizar|verificar).*(código|script)': TaskCategory.CODE_REVIEW,
            r'(encontrar|detectar).*(errores|bugs|problemas)': TaskCategory.CODE_REVIEW,
            r'(optimizar|mejorar).*(código|rendimiento)': TaskCategory.CODE_REVIEW,
            
            # Testing
            r'(probar|testear|test).*(aplicación|código|función)': TaskCategory.TESTING,
            r'(ejecutar|correr).*(pruebas|tests)': TaskCategory.TESTING,
            r'(validar|verificar).*(funcionalidad|comportamiento)': TaskCategory.TESTING,
            
            # Despliegue
            r'(desplegar|deploy|publicar).*(aplicación|servicio)': TaskCategory.DEPLOYMENT,
            r'(configurar|setup).*(servidor|infraestructura)': TaskCategory.DEPLOYMENT,
            r'(docker|kubernetes|container)': TaskCategory.DEPLOYMENT,
            
            # Monitoreo
            r'(monitorear|supervisar|observar).*(sistema|aplicación|servicio)': TaskCategory.MONITORING,
            r'(verificar|comprobar).*(estado|salud|health)': TaskCategory.MONITORING,
            r'(métricas|logs|alertas)': TaskCategory.MONITORING,
            
            # Documentación
            r'(documentar|escribir documentación|crear docs)': TaskCategory.DOCUMENTATION,
            r'(generar|crear).*(readme|manual|guía)': TaskCategory.DOCUMENTATION,
            
            # Análisis de datos
            r'(analizar|procesar).*(datos|data|información)': TaskCategory.DATA_ANALYSIS,
            r'(visualizar|graficar).*(datos|estadísticas)': TaskCategory.DATA_ANALYSIS,
            
            # Administración de sistemas
            r'(administrar|gestionar).*(sistema|servidor|infraestructura)': TaskCategory.SYSTEM_ADMINISTRATION,
            r'(configurar|instalar).*(software|herramienta|servicio)': TaskCategory.SYSTEM_ADMINISTRATION,
            
            # Investigación
            r'(investigar|buscar información|research)': TaskCategory.RESEARCH,
            r'(comparar|evaluar).*(opciones|alternativas|herramientas)': TaskCategory.RESEARCH,
        }
    
    def _initialize_capability_mappings(self):
        """Inicializa mapeos de palabras clave a capacidades"""
        self.capability_mappings = {
            'archivo': [ToolCapability.FILE_MANAGEMENT],
            'file': [ToolCapability.FILE_MANAGEMENT],
            'código': [ToolCapability.CODE_EXECUTION, ToolCapability.FILE_MANAGEMENT],
            'code': [ToolCapability.CODE_EXECUTION, ToolCapability.FILE_MANAGEMENT],
            'git': [ToolCapability.VERSION_CONTROL],
            'github': [ToolCapability.VERSION_CONTROL, ToolCapability.API_INTERACTION],
            'docker': [ToolCapability.CONTAINER_MANAGEMENT],
            'kubernetes': [ToolCapability.CONTAINER_MANAGEMENT],
            'database': [ToolCapability.DATABASE_ACCESS],
            'db': [ToolCapability.DATABASE_ACCESS],
            'api': [ToolCapability.API_INTERACTION],
            'texto': [ToolCapability.TEXT_PROCESSING],
            'text': [ToolCapability.TEXT_PROCESSING],
            'imagen': [ToolCapability.IMAGE_PROCESSING],
            'image': [ToolCapability.IMAGE_PROCESSING],
            'red': [ToolCapability.NETWORK_OPERATIONS],
            'network': [ToolCapability.NETWORK_OPERATIONS],
            'monitor': [ToolCapability.SYSTEM_MONITORING],
            'sistema': [ToolCapability.SYSTEM_MONITORING, ToolCapability.FILE_MANAGEMENT],
            'system': [ToolCapability.SYSTEM_MONITORING, ToolCapability.FILE_MANAGEMENT],
        }
    
    async def analyze_task(self, task_text: str, context: Optional[Dict] = None) -> TaskAnalysis:
        """
        Analiza automáticamente una tarea para determinar qué herramientas necesita
        
        Args:
            task_text: Texto de la tarea solicitada por el usuario
            context: Contexto adicional (proyecto actual, herramientas recientes, etc.)
            
        Returns:
            TaskAnalysis: Análisis completo de la tarea
        """
        logger.info(f"Analizando tarea: {task_text[:100]}...")
        
        # Detectar categoría de tarea
        detected_category = self._detect_task_category(task_text)
        
        # Identificar capacidades requeridas
        required_capabilities = self._identify_required_capabilities(task_text)
        
        # Calcular puntuaciones
        complexity_score = self._calculate_complexity(task_text, required_capabilities)
        urgency_level = self._detect_urgency(task_text, context)
        estimated_duration = self._estimate_duration(complexity_score, required_capabilities)
        
        # Extraer palabras clave de contexto
        context_keywords = self._extract_context_keywords(task_text)
        
        # Calcular confianza del análisis
        confidence_score = self._calculate_confidence(
            detected_category, required_capabilities, context_keywords
        )
        
        analysis = TaskAnalysis(
            task_text=task_text,
            detected_category=detected_category,
            required_capabilities=required_capabilities,
            complexity_score=complexity_score,
            urgency_level=urgency_level,
            estimated_duration=estimated_duration,
            context_keywords=context_keywords,
            confidence_score=confidence_score
        )
        
        logger.info(f"Análisis completado - Categoría: {detected_category.value}, "
                   f"Capacidades: {[cap.value for cap in required_capabilities]}, "
                   f"Confianza: {confidence_score:.2f}")
        
        return analysis
    
    def _detect_task_category(self, task_text: str) -> TaskCategory:
        """Detecta la categoría de la tarea usando patrones regex"""
        task_lower = task_text.lower()
        
        for pattern, category in self.task_patterns.items():
            if re.search(pattern, task_lower):
                return category
        
        return TaskCategory.GENERAL
    
    def _identify_required_capabilities(self, task_text: str) -> List[ToolCapability]:
        """Identifica las capacidades requeridas basándose en palabras clave"""
        task_lower = task_text.lower()
        required_capabilities = set()
        
        for keyword, capabilities in self.capability_mappings.items():
            if keyword in task_lower:
                required_capabilities.update(capabilities)
        
        return list(required_capabilities)
    
    def _calculate_complexity(self, task_text: str, capabilities: List[ToolCapability]) -> float:
        """Calcula la complejidad de la tarea (0.0 - 1.0)"""
        base_complexity = len(capabilities) * 0.1
        
        # Palabras que indican complejidad
        complexity_indicators = {
            'complejo': 0.3, 'avanzado': 0.25, 'sofisticado': 0.25,
            'múltiple': 0.2, 'varios': 0.15, 'integrar': 0.2,
            'optimizar': 0.25, 'escalable': 0.3, 'distribuido': 0.35
        }
        
        task_lower = task_text.lower()
        for indicator, weight in complexity_indicators.items():
            if indicator in task_lower:
                base_complexity += weight
        
        return min(base_complexity, 1.0)
    
    def _detect_urgency(self, task_text: str, context: Optional[Dict]) -> int:
        """Detecta el nivel de urgencia (1-5)"""
        task_lower = task_text.lower()
        
        urgency_keywords = {
            'urgente': 5, 'inmediato': 5, 'ahora': 4, 'rápido': 4,
            'pronto': 3, 'cuando puedas': 2, 'sin prisa': 1
        }
        
        for keyword, level in urgency_keywords.items():
            if keyword in task_lower:
                return level
        
        return 3  # Urgencia media por defecto
    
    def _estimate_duration(self, complexity: float, capabilities: List[ToolCapability]) -> float:
        """Estima la duración en minutos"""
        base_duration = 5.0  # 5 minutos base
        complexity_factor = complexity * 30  # Hasta 30 minutos por complejidad
        capability_factor = len(capabilities) * 10  # 10 minutos por capacidad
        
        return base_duration + complexity_factor + capability_factor
    
    def _extract_context_keywords(self, task_text: str) -> List[str]:
        """Extrae palabras clave relevantes del contexto"""
        # Palabras técnicas importantes
        technical_keywords = [
            'python', 'javascript', 'react', 'node', 'docker', 'kubernetes',
            'git', 'github', 'api', 'database', 'sql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'linux', 'windows', 'macos'
        ]
        
        task_lower = task_text.lower()
        found_keywords = []
        
        for keyword in technical_keywords:
            if keyword in task_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_confidence(self, category: TaskCategory, 
                            capabilities: List[ToolCapability],
                            keywords: List[str]) -> float:
        """Calcula la confianza del análisis (0.0 - 1.0)"""
        base_confidence = 0.5
        
        # Mayor confianza si se detectó una categoría específica
        if category != TaskCategory.GENERAL:
            base_confidence += 0.2
        
        # Mayor confianza con más capacidades identificadas
        if capabilities:
            base_confidence += min(len(capabilities) * 0.1, 0.2)
        
        # Mayor confianza con palabras clave técnicas
        if keywords:
            base_confidence += min(len(keywords) * 0.05, 0.1)
        
        return min(base_confidence, 1.0)
    
    async def select_tools_automatically(self, task_analysis: TaskAnalysis, 
                                       context: Optional[Dict] = None) -> List[str]:
        """
        Selecciona automáticamente las herramientas más apropiadas para la tarea
        
        Args:
            task_analysis: Análisis de la tarea
            context: Contexto adicional
            
        Returns:
            List[str]: Lista de nombres de herramientas seleccionadas
        """
        logger.info(f"Seleccionando herramientas para categoría: {task_analysis.detected_category.value}")
        
        # Filtrar herramientas por capacidades requeridas
        candidate_tools = self._filter_tools_by_capabilities(task_analysis.required_capabilities)
        
        # Filtrar por categoría de tarea
        candidate_tools = self._filter_tools_by_category(candidate_tools, task_analysis.detected_category)
        
        # Puntuar herramientas basándose en múltiples factores
        scored_tools = self._score_tools(candidate_tools, task_analysis, context)
        
        # Seleccionar las mejores herramientas
        selected_tools = self._select_best_tools(scored_tools, task_analysis)
        
        # Registrar la selección para aprendizaje
        await self._record_tool_selection(task_analysis, selected_tools)
        
        logger.info(f"Herramientas seleccionadas: {selected_tools}")
        return selected_tools
    
    def _filter_tools_by_capabilities(self, required_capabilities: List[ToolCapability]) -> List[str]:
        """Filtra herramientas que tienen las capacidades requeridas"""
        if not required_capabilities:
            return list(self.tool_registry.keys())
        
        matching_tools = []
        for tool_name, metadata in self.tool_registry.items():
            # Verificar si la herramienta tiene al menos una capacidad requerida
            if any(cap in metadata.capabilities for cap in required_capabilities):
                matching_tools.append(tool_name)
        
        return matching_tools
    
    def _filter_tools_by_category(self, tools: List[str], category: TaskCategory) -> List[str]:
        """Filtra herramientas apropiadas para la categoría de tarea"""
        matching_tools = []
        for tool_name in tools:
            metadata = self.tool_registry.get(tool_name)
            if metadata and (category in metadata.task_categories or 
                           TaskCategory.GENERAL in metadata.task_categories):
                matching_tools.append(tool_name)
        
        return matching_tools
    
    def _score_tools(self, tools: List[str], task_analysis: TaskAnalysis, 
                    context: Optional[Dict]) -> List[Tuple[str, float]]:
        """Puntúa las herramientas basándose en múltiples factores"""
        scored_tools = []
        
        for tool_name in tools:
            metadata = self.tool_registry.get(tool_name)
            if not metadata:
                continue
            
            score = 0.0
            
            # Factor 1: Tasa de éxito histórica (peso: 30%)
            score += metadata.success_rate * 0.3
            
            # Factor 2: Confiabilidad (peso: 25%)
            score += metadata.reliability_score * 0.25
            
            # Factor 3: Velocidad de ejecución (peso: 20%)
            # Invertir el tiempo de ejecución (menos tiempo = mejor puntuación)
            max_time = 300  # 5 minutos máximo esperado
            time_score = max(0, (max_time - metadata.average_execution_time) / max_time)
            score += time_score * 0.2
            
            # Factor 4: Uso de recursos (peso: 15%)
            # Menos uso de recursos = mejor puntuación
            resource_score = 1.0 - min(1.0, sum(metadata.resource_usage.values()) / 100)
            score += resource_score * 0.15
            
            # Factor 5: Complejidad de configuración (peso: 10%)
            # Menos complejidad = mejor puntuación para selección automática
            complexity_score = 1.0 - (metadata.configuration_complexity / 10)
            score += complexity_score * 0.1
            
            # Bonificaciones por contexto
            if context:
                # Bonificar herramientas usadas recientemente con éxito
                recent_tools = context.get('recent_successful_tools', [])
                if tool_name in recent_tools:
                    score += 0.1
                
                # Bonificar herramientas del mismo proyecto
                project_tools = context.get('project_tools', [])
                if tool_name in project_tools:
                    score += 0.05
            
            scored_tools.append((tool_name, score))
        
        # Ordenar por puntuación descendente
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return scored_tools
    
    def _select_best_tools(self, scored_tools: List[Tuple[str, float]], 
                          task_analysis: TaskAnalysis) -> List[str]:
        """Selecciona las mejores herramientas basándose en las puntuaciones"""
        if not scored_tools:
            return []
        
        selected_tools = []
        
        # Determinar número de herramientas a seleccionar basándose en complejidad
        if task_analysis.complexity_score < 0.3:
            max_tools = 1  # Tareas simples: 1 herramienta
        elif task_analysis.complexity_score < 0.7:
            max_tools = 2  # Tareas medianas: 2 herramientas
        else:
            max_tools = 3  # Tareas complejas: hasta 3 herramientas
        
        # Seleccionar herramientas con puntuación mínima
        min_score = 0.5
        for tool_name, score in scored_tools[:max_tools]:
            if score >= min_score:
                selected_tools.append(tool_name)
        
        # Si no hay herramientas con puntuación suficiente, seleccionar la mejor
        if not selected_tools and scored_tools:
            selected_tools.append(scored_tools[0][0])
        
        return selected_tools
    
    async def _record_tool_selection(self, task_analysis: TaskAnalysis, 
                                   selected_tools: List[str]):
        """Registra la selección de herramientas para aprendizaje futuro"""
        if not self.learning_enabled:
            return
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'task_category': task_analysis.detected_category.value,
            'required_capabilities': [cap.value for cap in task_analysis.required_capabilities],
            'complexity_score': task_analysis.complexity_score,
            'selected_tools': selected_tools,
            'confidence_score': task_analysis.confidence_score
        }
        
        # Almacenar en historial para análisis futuro
        category_key = task_analysis.detected_category.value
        if category_key not in self.success_history:
            self.success_history[category_key] = []
        
        self.success_history[category_key].append(record)
        
        # Mantener solo los últimos 1000 registros por categoría
        if len(self.success_history[category_key]) > 1000:
            self.success_history[category_key] = self.success_history[category_key][-1000:]
    
    def register_tool(self, tool_metadata: ToolMetadata):
        """Registra una nueva herramienta en el sistema"""
        self.tool_registry[tool_metadata.name] = tool_metadata
        logger.info(f"Herramienta registrada: {tool_metadata.name}")
    
    def update_tool_performance(self, tool_name: str, success: bool, 
                              execution_time: float, resource_usage: Dict[str, float]):
        """Actualiza las métricas de rendimiento de una herramienta"""
        if tool_name not in self.tool_registry:
            return
        
        metadata = self.tool_registry[tool_name]
        
        # Actualizar tasa de éxito (promedio móvil)
        alpha = 0.1  # Factor de aprendizaje
        if success:
            metadata.success_rate = metadata.success_rate * (1 - alpha) + alpha
        else:
            metadata.success_rate = metadata.success_rate * (1 - alpha)
        
        # Actualizar tiempo promedio de ejecución
        metadata.average_execution_time = (
            metadata.average_execution_time * (1 - alpha) + 
            execution_time * alpha
        )
        
        # Actualizar uso de recursos
        for resource, usage in resource_usage.items():
            if resource in metadata.resource_usage:
                metadata.resource_usage[resource] = (
                    metadata.resource_usage[resource] * (1 - alpha) + 
                    usage * alpha
                )
        
        metadata.last_updated = datetime.now()
        
        logger.info(f"Métricas actualizadas para {tool_name}: "
                   f"éxito={metadata.success_rate:.2f}, "
                   f"tiempo={metadata.average_execution_time:.1f}s")
    
    async def get_tool_recommendations_explanation(self, task_analysis: TaskAnalysis, 
                                                 selected_tools: List[str]) -> str:
        """
        Genera una explicación de por qué se seleccionaron las herramientas
        (para transparencia administrativa)
        """
        explanation = f"""
Análisis de Selección Automática de Herramientas:

Tarea: {task_analysis.task_text[:200]}...
Categoría detectada: {task_analysis.detected_category.value}
Capacidades requeridas: {[cap.value for cap in task_analysis.required_capabilities]}
Complejidad: {task_analysis.complexity_score:.2f}/1.0
Confianza del análisis: {task_analysis.confidence_score:.2f}/1.0

Herramientas seleccionadas:
"""
        
        for tool_name in selected_tools:
            metadata = self.tool_registry.get(tool_name)
            if metadata:
                explanation += f"""
- {tool_name}:
  * Tasa de éxito: {metadata.success_rate:.2f}
  * Confiabilidad: {metadata.reliability_score:.2f}
  * Tiempo promedio: {metadata.average_execution_time:.1f}s
  * Capacidades: {[cap.value for cap in metadata.capabilities]}
"""
        
        return explanation

# Instancia global del selector automático
automatic_selector = AutomaticToolSelector()

