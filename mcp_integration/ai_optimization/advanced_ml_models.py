"""
Modelos de Machine Learning Específicos para Sistema MCP
Implementa algoritmos avanzados de ML para optimización y recomendación de herramientas
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

# Importaciones de ML
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_selection import SelectKBest, f_regression
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MLModelConfig:
    """Configuración para modelos de ML"""
    model_type: str
    hyperparameters: Dict[str, Any]
    feature_selection: Dict[str, Any]
    validation_strategy: Dict[str, Any]
    performance_threshold: float
    retrain_interval_hours: int

@dataclass
class FeatureImportance:
    """Importancia de características en modelos"""
    feature_name: str
    importance_score: float
    feature_type: str
    description: str

@dataclass
class ModelPerformance:
    """Métricas de rendimiento de modelo"""
    model_id: str
    model_type: str
    mse: float
    mae: float
    r2_score: float
    cross_val_score: float
    feature_count: int
    training_time_seconds: float
    prediction_time_ms: float
    timestamp: datetime

@dataclass
class PredictionResult:
    """Resultado de predicción de modelo"""
    prediction_id: str
    model_id: str
    input_features: Dict[str, Any]
    predicted_value: float
    confidence_interval: Tuple[float, float]
    feature_contributions: Dict[str, float]
    explanation: str
    timestamp: datetime

class AdvancedMLModelManager:
    """Gestor avanzado de modelos de machine learning"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_selectors = {}
        self.model_performance = {}
        self.training_data = {}
        self.db_path = config.get('db_path', 'ml_models.db')
        self.connection = None
        
    async def initialize(self) -> None:
        """Inicializa el gestor de modelos ML"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            await self._create_tables()
            await self._load_existing_models()
            logger.info("Gestor de modelos ML inicializado")
        except Exception as e:
            logger.error(f"Error inicializando gestor de modelos ML: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Crea tablas para almacenar datos de ML"""
        cursor = self.connection.cursor()
        
        # Tabla de datos de entrenamiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                features TEXT NOT NULL,
                target_value REAL NOT NULL,
                context TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de rendimiento de modelos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                model_type TEXT NOT NULL,
                mse REAL,
                mae REAL,
                r2_score REAL,
                cross_val_score REAL,
                feature_count INTEGER,
                training_time_seconds REAL,
                prediction_time_ms REAL,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de predicciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id TEXT NOT NULL,
                model_id TEXT NOT NULL,
                input_features TEXT,
                predicted_value REAL,
                confidence_lower REAL,
                confidence_upper REAL,
                feature_contributions TEXT,
                explanation TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_training_tool_id ON training_data(tool_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_performance_id ON model_performance(model_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_id ON predictions(prediction_id)')
        
        self.connection.commit()
    
    async def _load_existing_models(self) -> None:
        """Carga modelos existentes desde disco"""
        try:
            models_dir = Path(self.config.get('models_directory', 'ml_models'))
            models_dir.mkdir(exist_ok=True)
            
            for model_file in models_dir.glob('*.pkl'):
                try:
                    with open(model_file, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    model_id = model_file.stem
                    self.models[model_id] = model_data['model']
                    self.scalers[model_id] = model_data.get('scaler')
                    self.encoders[model_id] = model_data.get('encoder')
                    self.feature_selectors[model_id] = model_data.get('feature_selector')
                    
                    logger.info(f"Modelo {model_id} cargado exitosamente")
                    
                except Exception as e:
                    logger.warning(f"Error cargando modelo {model_file}: {e}")
            
        except Exception as e:
            logger.warning(f"Error cargando modelos existentes: {e}")
    
    async def train_performance_prediction_model(self, tool_id: str, 
                                                training_data: List[Dict[str, Any]]) -> str:
        """Entrena modelo para predecir rendimiento de herramientas"""
        try:
            if len(training_data) < 10:
                raise ValueError("Datos de entrenamiento insuficientes (mínimo 10 muestras)")
            
            # Preparar datos
            df = pd.DataFrame(training_data)
            
            # Extraer características y objetivo
            feature_columns = [col for col in df.columns if col not in ['performance_score', 'timestamp']]
            X = df[feature_columns]
            y = df['performance_score']
            
            # Preprocesamiento
            X_processed, scaler, encoder, feature_selector = await self._preprocess_features(X)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=0.2, random_state=42
            )
            
            # Entrenar múltiples modelos y seleccionar el mejor
            models_to_try = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42),
                'svr': SVR(kernel='rbf'),
                'ridge': Ridge(alpha=1.0)
            }
            
            best_model = None
            best_score = float('-inf')
            best_model_type = None
            
            start_time = time.time()
            
            for model_name, model in models_to_try.items():
                try:
                    # Validación cruzada
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                    avg_cv_score = np.mean(cv_scores)
                    
                    if avg_cv_score > best_score:
                        best_score = avg_cv_score
                        best_model = model
                        best_model_type = model_name
                        
                except Exception as e:
                    logger.warning(f"Error entrenando modelo {model_name}: {e}")
                    continue
            
            if best_model is None:
                raise ValueError("No se pudo entrenar ningún modelo exitosamente")
            
            # Entrenar el mejor modelo con todos los datos de entrenamiento
            best_model.fit(X_train, y_train)
            
            training_time = time.time() - start_time
            
            # Evaluar rendimiento
            y_pred = best_model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Generar ID del modelo
            model_id = f"{tool_id}_performance_{int(time.time())}"
            
            # Almacenar modelo
            self.models[model_id] = best_model
            self.scalers[model_id] = scaler
            self.encoders[model_id] = encoder
            self.feature_selectors[model_id] = feature_selector
            
            # Guardar modelo en disco
            await self._save_model_to_disk(model_id, best_model, scaler, encoder, feature_selector)
            
            # Registrar rendimiento
            performance = ModelPerformance(
                model_id=model_id,
                model_type=best_model_type,
                mse=mse,
                mae=mae,
                r2_score=r2,
                cross_val_score=best_score,
                feature_count=X_processed.shape[1],
                training_time_seconds=training_time,
                prediction_time_ms=0.0,  # Se medirá en predicciones
                timestamp=datetime.now()
            )
            
            await self._record_model_performance(performance)
            
            logger.info(f"Modelo {model_id} entrenado exitosamente. R² = {r2:.3f}")
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error entrenando modelo de rendimiento: {e}")
            raise
    
    async def train_resource_optimization_model(self, tool_id: str,
                                              optimization_data: List[Dict[str, Any]]) -> str:
        """Entrena modelo para optimización de recursos"""
        try:
            if len(optimization_data) < 15:
                raise ValueError("Datos de optimización insuficientes (mínimo 15 muestras)")
            
            # Preparar datos
            df = pd.DataFrame(optimization_data)
            
            # Características de configuración y métricas de recursos
            config_features = [col for col in df.columns if col.startswith('config_')]
            resource_features = [col for col in df.columns if col.startswith('resource_')]
            
            X = df[config_features + resource_features]
            y = df['efficiency_score']  # Métrica objetivo de eficiencia
            
            # Preprocesamiento específico para optimización
            X_processed, scaler, encoder, feature_selector = await self._preprocess_optimization_features(X)
            
            # Usar Gradient Boosting para optimización (mejor para relaciones no lineales)
            model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Optimización de hiperparámetros
            param_grid = {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [4, 6, 8]
            }
            
            grid_search = GridSearchCV(
                model, param_grid, cv=5, scoring='r2', n_jobs=-1
            )
            
            start_time = time.time()
            grid_search.fit(X_processed, y)
            training_time = time.time() - start_time
            
            best_model = grid_search.best_estimator_
            
            # Evaluar con validación cruzada
            cv_scores = cross_val_score(best_model, X_processed, y, cv=5, scoring='r2')
            
            # Generar ID del modelo
            model_id = f"{tool_id}_optimization_{int(time.time())}"
            
            # Almacenar modelo
            self.models[model_id] = best_model
            self.scalers[model_id] = scaler
            self.encoders[model_id] = encoder
            self.feature_selectors[model_id] = feature_selector
            
            # Guardar modelo
            await self._save_model_to_disk(model_id, best_model, scaler, encoder, feature_selector)
            
            # Registrar rendimiento
            performance = ModelPerformance(
                model_id=model_id,
                model_type='gradient_boosting_optimization',
                mse=0.0,  # Se calculará en evaluación completa
                mae=0.0,
                r2_score=np.mean(cv_scores),
                cross_val_score=np.mean(cv_scores),
                feature_count=X_processed.shape[1],
                training_time_seconds=training_time,
                prediction_time_ms=0.0,
                timestamp=datetime.now()
            )
            
            await self._record_model_performance(performance)
            
            logger.info(f"Modelo de optimización {model_id} entrenado. R² = {np.mean(cv_scores):.3f}")
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error entrenando modelo de optimización: {e}")
            raise
    
    async def train_usage_pattern_model(self, usage_data: List[Dict[str, Any]]) -> str:
        """Entrena modelo para detectar patrones de uso"""
        try:
            if len(usage_data) < 20:
                raise ValueError("Datos de patrones insuficientes (mínimo 20 muestras)")
            
            # Preparar datos para clustering
            df = pd.DataFrame(usage_data)
            
            # Características temporales y de uso
            temporal_features = ['hour_of_day', 'day_of_week', 'month']
            usage_features = [col for col in df.columns if col.startswith('usage_')]
            context_features = [col for col in df.columns if col.startswith('context_')]
            
            X = df[temporal_features + usage_features + context_features]
            
            # Preprocesamiento
            X_processed, scaler, encoder, _ = await self._preprocess_features(X, use_feature_selection=False)
            
            # Determinar número óptimo de clusters
            optimal_clusters = await self._find_optimal_clusters(X_processed)
            
            # Entrenar modelo de clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            
            start_time = time.time()
            cluster_labels = kmeans.fit_predict(X_processed)
            training_time = time.time() - start_time
            
            # Generar ID del modelo
            model_id = f"usage_patterns_{int(time.time())}"
            
            # Almacenar modelo
            self.models[model_id] = kmeans
            self.scalers[model_id] = scaler
            self.encoders[model_id] = encoder
            
            # Guardar modelo
            await self._save_model_to_disk(model_id, kmeans, scaler, encoder, None)
            
            # Analizar clusters
            cluster_analysis = await self._analyze_usage_clusters(X_processed, cluster_labels, optimal_clusters)
            
            # Registrar rendimiento
            performance = ModelPerformance(
                model_id=model_id,
                model_type='kmeans_clustering',
                mse=0.0,  # No aplicable para clustering
                mae=0.0,
                r2_score=0.0,
                cross_val_score=kmeans.inertia_,  # Usar inercia como métrica
                feature_count=X_processed.shape[1],
                training_time_seconds=training_time,
                prediction_time_ms=0.0,
                timestamp=datetime.now()
            )
            
            await self._record_model_performance(performance)
            
            logger.info(f"Modelo de patrones {model_id} entrenado con {optimal_clusters} clusters")
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error entrenando modelo de patrones: {e}")
            raise
    
    async def predict_tool_performance(self, model_id: str, 
                                     input_features: Dict[str, Any]) -> PredictionResult:
        """Predice rendimiento de herramienta usando modelo entrenado"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Modelo {model_id} no encontrado")
            
            model = self.models[model_id]
            scaler = self.scalers.get(model_id)
            encoder = self.encoders.get(model_id)
            feature_selector = self.feature_selectors.get(model_id)
            
            # Preparar características de entrada
            input_df = pd.DataFrame([input_features])
            
            # Aplicar preprocesamiento
            X_processed = await self._apply_preprocessing(
                input_df, scaler, encoder, feature_selector
            )
            
            # Realizar predicción
            start_time = time.time()
            prediction = model.predict(X_processed)[0]
            prediction_time = (time.time() - start_time) * 1000  # en ms
            
            # Calcular intervalo de confianza (aproximado)
            confidence_interval = await self._calculate_confidence_interval(
                model, X_processed, prediction
            )
            
            # Calcular contribuciones de características
            feature_contributions = await self._calculate_feature_contributions(
                model, X_processed, input_features
            )
            
            # Generar explicación
            explanation = await self._generate_prediction_explanation(
                prediction, feature_contributions, input_features
            )
            
            # Crear resultado
            result = PredictionResult(
                prediction_id=f"pred_{int(time.time())}_{np.random.randint(1000)}",
                model_id=model_id,
                input_features=input_features,
                predicted_value=float(prediction),
                confidence_interval=confidence_interval,
                feature_contributions=feature_contributions,
                explanation=explanation,
                timestamp=datetime.now()
            )
            
            # Registrar predicción
            await self._record_prediction(result)
            
            # Actualizar tiempo de predicción en métricas
            await self._update_prediction_time(model_id, prediction_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error realizando predicción: {e}")
            raise
    
    async def get_feature_importance(self, model_id: str) -> List[FeatureImportance]:
        """Obtiene importancia de características del modelo"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Modelo {model_id} no encontrado")
            
            model = self.models[model_id]
            
            # Obtener importancia según tipo de modelo
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importances = np.abs(model.coef_)
            else:
                logger.warning(f"Modelo {model_id} no soporta importancia de características")
                return []
            
            # Obtener nombres de características (simplificado)
            feature_names = [f"feature_{i}" for i in range(len(importances))]
            
            # Crear lista de importancia
            feature_importance_list = []
            for i, (name, importance) in enumerate(zip(feature_names, importances)):
                feature_importance_list.append(FeatureImportance(
                    feature_name=name,
                    importance_score=float(importance),
                    feature_type='numeric',  # Simplificado
                    description=f"Característica {i+1} del modelo"
                ))
            
            # Ordenar por importancia
            feature_importance_list.sort(key=lambda x: x.importance_score, reverse=True)
            
            return feature_importance_list
            
        except Exception as e:
            logger.error(f"Error obteniendo importancia de características: {e}")
            return []
    
    async def generate_model_insights(self, model_id: str) -> Dict[str, Any]:
        """Genera insights sobre el modelo"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Modelo {model_id} no encontrado")
            
            model = self.models[model_id]
            
            # Obtener métricas de rendimiento
            performance = await self._get_model_performance(model_id)
            
            # Obtener importancia de características
            feature_importance = await self.get_feature_importance(model_id)
            
            # Generar insights
            insights = {
                'model_id': model_id,
                'model_type': type(model).__name__,
                'performance_metrics': asdict(performance) if performance else {},
                'top_features': [
                    {'name': fi.feature_name, 'importance': fi.importance_score}
                    for fi in feature_importance[:5]
                ],
                'model_complexity': await self._assess_model_complexity(model),
                'recommendations': await self._generate_model_recommendations(model, performance),
                'data_requirements': await self._assess_data_requirements(model_id),
                'prediction_reliability': await self._assess_prediction_reliability(model_id)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights del modelo: {e}")
            return {}
    
    async def create_performance_visualization(self, model_id: str) -> str:
        """Crea visualización de rendimiento del modelo"""
        try:
            # Obtener datos de rendimiento histórico
            performance_data = await self._get_performance_history(model_id)
            
            if not performance_data:
                return ""
            
            # Crear visualización con Plotly
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('R² Score Over Time', 'Prediction Time', 
                              'Feature Importance', 'Error Distribution'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Gráfico de R² a lo largo del tiempo
            timestamps = [p['timestamp'] for p in performance_data]
            r2_scores = [p['r2_score'] for p in performance_data]
            
            fig.add_trace(
                go.Scatter(x=timestamps, y=r2_scores, mode='lines+markers', name='R² Score'),
                row=1, col=1
            )
            
            # Gráfico de tiempo de predicción
            pred_times = [p['prediction_time_ms'] for p in performance_data]
            fig.add_trace(
                go.Scatter(x=timestamps, y=pred_times, mode='lines+markers', 
                          name='Prediction Time (ms)', line=dict(color='orange')),
                row=1, col=2
            )
            
            # Gráfico de importancia de características
            feature_importance = await self.get_feature_importance(model_id)
            if feature_importance:
                top_features = feature_importance[:10]
                fig.add_trace(
                    go.Bar(x=[f.importance_score for f in top_features],
                           y=[f.feature_name for f in top_features],
                           orientation='h', name='Feature Importance'),
                    row=2, col=1
                )
            
            # Distribución de errores (simulada)
            errors = np.random.normal(0, 0.1, 100)  # Placeholder
            fig.add_trace(
                go.Histogram(x=errors, name='Error Distribution', nbinsx=20),
                row=2, col=2
            )
            
            # Actualizar layout
            fig.update_layout(
                title=f'Model Performance Dashboard - {model_id}',
                height=800,
                showlegend=True
            )
            
            # Guardar visualización
            viz_path = f"model_performance_{model_id}_{int(time.time())}.html"
            fig.write_html(viz_path)
            
            return viz_path
            
        except Exception as e:
            logger.error(f"Error creando visualización: {e}")
            return ""
    
    # Métodos auxiliares privados
    
    async def _preprocess_features(self, X: pd.DataFrame, 
                                 use_feature_selection: bool = True) -> Tuple[np.ndarray, Any, Any, Any]:
        """Preprocesa características para entrenamiento"""
        # Manejar valores faltantes
        X_filled = X.fillna(X.mean() if X.select_dtypes(include=[np.number]).shape[1] > 0 else 0)
        
        # Codificar variables categóricas
        encoder = None
        categorical_columns = X_filled.select_dtypes(include=['object']).columns
        
        if len(categorical_columns) > 0:
            encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            categorical_encoded = encoder.fit_transform(X_filled[categorical_columns])
            
            # Combinar con características numéricas
            numeric_columns = X_filled.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                X_processed = np.hstack([
                    X_filled[numeric_columns].values,
                    categorical_encoded
                ])
            else:
                X_processed = categorical_encoded
        else:
            X_processed = X_filled.values
        
        # Escalar características
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_processed)
        
        # Selección de características
        feature_selector = None
        if use_feature_selection and X_scaled.shape[1] > 10:
            k = min(10, X_scaled.shape[1])
            feature_selector = SelectKBest(score_func=f_regression, k=k)
            # Nota: necesitaríamos y para fit_transform, por ahora solo preparamos
            X_final = X_scaled
        else:
            X_final = X_scaled
        
        return X_final, scaler, encoder, feature_selector
    
    async def _preprocess_optimization_features(self, X: pd.DataFrame) -> Tuple[np.ndarray, Any, Any, Any]:
        """Preprocesamiento específico para optimización"""
        # Similar al preprocesamiento general pero con técnicas específicas para optimización
        return await self._preprocess_features(X, use_feature_selection=True)
    
    async def _apply_preprocessing(self, X: pd.DataFrame, scaler, encoder, feature_selector) -> np.ndarray:
        """Aplica preprocesamiento a nuevos datos"""
        # Manejar valores faltantes
        X_filled = X.fillna(X.mean() if X.select_dtypes(include=[np.number]).shape[1] > 0 else 0)
        
        # Aplicar codificación
        if encoder is not None:
            categorical_columns = X_filled.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                categorical_encoded = encoder.transform(X_filled[categorical_columns])
                numeric_columns = X_filled.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    X_processed = np.hstack([
                        X_filled[numeric_columns].values,
                        categorical_encoded
                    ])
                else:
                    X_processed = categorical_encoded
            else:
                X_processed = X_filled.values
        else:
            X_processed = X_filled.values
        
        # Aplicar escalado
        if scaler is not None:
            X_scaled = scaler.transform(X_processed)
        else:
            X_scaled = X_processed
        
        # Aplicar selección de características
        if feature_selector is not None:
            X_final = feature_selector.transform(X_scaled)
        else:
            X_final = X_scaled
        
        return X_final
    
    async def _find_optimal_clusters(self, X: np.ndarray) -> int:
        """Encuentra número óptimo de clusters usando método del codo"""
        max_clusters = min(10, X.shape[0] // 2)
        inertias = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
        
        # Método del codo simplificado
        if len(inertias) >= 3:
            # Encontrar el punto donde la mejora se reduce significativamente
            improvements = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
            improvement_ratios = [improvements[i] / improvements[i+1] if improvements[i+1] > 0 else 1 
                                for i in range(len(improvements)-1)]
            
            if improvement_ratios:
                optimal_k = improvement_ratios.index(max(improvement_ratios)) + 3
                return min(optimal_k, max_clusters)
        
        return 3  # Valor por defecto
    
    async def _analyze_usage_clusters(self, X: np.ndarray, labels: np.ndarray, 
                                    n_clusters: int) -> Dict[str, Any]:
        """Analiza clusters de patrones de uso"""
        cluster_analysis = {}
        
        for cluster_id in range(n_clusters):
            cluster_mask = labels == cluster_id
            cluster_data = X[cluster_mask]
            
            if len(cluster_data) > 0:
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    'size': len(cluster_data),
                    'percentage': len(cluster_data) / len(X) * 100,
                    'centroid': np.mean(cluster_data, axis=0).tolist(),
                    'std': np.std(cluster_data, axis=0).tolist()
                }
        
        return cluster_analysis
    
    async def _calculate_confidence_interval(self, model, X: np.ndarray, 
                                           prediction: float) -> Tuple[float, float]:
        """Calcula intervalo de confianza para predicción"""
        # Implementación simplificada - en producción usar métodos más sofisticados
        try:
            if hasattr(model, 'predict') and len(X) > 0:
                # Usar desviación estándar de predicciones como proxy
                std_error = 0.1 * abs(prediction)  # Aproximación simple
                lower = prediction - 1.96 * std_error
                upper = prediction + 1.96 * std_error
                return (float(lower), float(upper))
        except:
            pass
        
        # Fallback
        margin = 0.1 * abs(prediction)
        return (float(prediction - margin), float(prediction + margin))
    
    async def _calculate_feature_contributions(self, model, X: np.ndarray, 
                                             input_features: Dict[str, Any]) -> Dict[str, float]:
        """Calcula contribuciones de características a la predicción"""
        contributions = {}
        
        try:
            if hasattr(model, 'feature_importances_') and len(X) > 0:
                importances = model.feature_importances_
                feature_values = X[0]  # Primera (y única) muestra
                
                for i, (importance, value) in enumerate(zip(importances, feature_values)):
                    feature_name = f"feature_{i}"
                    contribution = importance * value
                    contributions[feature_name] = float(contribution)
            
        except Exception as e:
            logger.warning(f"Error calculando contribuciones: {e}")
        
        return contributions
    
    async def _generate_prediction_explanation(self, prediction: float,
                                             feature_contributions: Dict[str, float],
                                             input_features: Dict[str, Any]) -> str:
        """Genera explicación de la predicción"""
        try:
            # Encontrar características más influyentes
            sorted_contributions = sorted(
                feature_contributions.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
            
            top_features = sorted_contributions[:3]
            
            explanation_parts = [
                f"Predicción: {prediction:.3f}",
                "Factores principales:"
            ]
            
            for feature, contribution in top_features:
                direction = "aumenta" if contribution > 0 else "disminuye"
                explanation_parts.append(
                    f"- {feature}: {direction} la predicción en {abs(contribution):.3f}"
                )
            
            return " | ".join(explanation_parts)
            
        except Exception as e:
            logger.warning(f"Error generando explicación: {e}")
            return f"Predicción: {prediction:.3f}"
    
    async def _save_model_to_disk(self, model_id: str, model, scaler, encoder, feature_selector) -> None:
        """Guarda modelo en disco"""
        try:
            models_dir = Path(self.config.get('models_directory', 'ml_models'))
            models_dir.mkdir(exist_ok=True)
            
            model_data = {
                'model': model,
                'scaler': scaler,
                'encoder': encoder,
                'feature_selector': feature_selector,
                'timestamp': datetime.now().isoformat()
            }
            
            model_path = models_dir / f"{model_id}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
                
        except Exception as e:
            logger.warning(f"Error guardando modelo en disco: {e}")
    
    async def _record_model_performance(self, performance: ModelPerformance) -> None:
        """Registra rendimiento del modelo en base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO model_performance 
                (model_id, model_type, mse, mae, r2_score, cross_val_score,
                 feature_count, training_time_seconds, prediction_time_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                performance.model_id,
                performance.model_type,
                performance.mse,
                performance.mae,
                performance.r2_score,
                performance.cross_val_score,
                performance.feature_count,
                performance.training_time_seconds,
                performance.prediction_time_ms,
                performance.timestamp.isoformat()
            ))
            self.connection.commit()
            
        except Exception as e:
            logger.warning(f"Error registrando rendimiento del modelo: {e}")
    
    async def _record_prediction(self, result: PredictionResult) -> None:
        """Registra predicción en base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (prediction_id, model_id, input_features, predicted_value,
                 confidence_lower, confidence_upper, feature_contributions, 
                 explanation, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.prediction_id,
                result.model_id,
                json.dumps(result.input_features),
                result.predicted_value,
                result.confidence_interval[0],
                result.confidence_interval[1],
                json.dumps(result.feature_contributions),
                result.explanation,
                result.timestamp.isoformat()
            ))
            self.connection.commit()
            
        except Exception as e:
            logger.warning(f"Error registrando predicción: {e}")
    
    async def _get_model_performance(self, model_id: str) -> Optional[ModelPerformance]:
        """Obtiene rendimiento más reciente del modelo"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM model_performance 
                WHERE model_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (model_id,))
            
            row = cursor.fetchone()
            if row:
                return ModelPerformance(
                    model_id=row[1],
                    model_type=row[2],
                    mse=row[3],
                    mae=row[4],
                    r2_score=row[5],
                    cross_val_score=row[6],
                    feature_count=row[7],
                    training_time_seconds=row[8],
                    prediction_time_ms=row[9],
                    timestamp=datetime.fromisoformat(row[10])
                )
            
        except Exception as e:
            logger.warning(f"Error obteniendo rendimiento del modelo: {e}")
        
        return None
    
    async def _get_performance_history(self, model_id: str) -> List[Dict[str, Any]]:
        """Obtiene historial de rendimiento del modelo"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT timestamp, r2_score, prediction_time_ms, mse, mae
                FROM model_performance 
                WHERE model_id = ? 
                ORDER BY created_at ASC
            ''', (model_id,))
            
            rows = cursor.fetchall()
            return [
                {
                    'timestamp': row[0],
                    'r2_score': row[1],
                    'prediction_time_ms': row[2],
                    'mse': row[3],
                    'mae': row[4]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.warning(f"Error obteniendo historial de rendimiento: {e}")
            return []
    
    async def _update_prediction_time(self, model_id: str, prediction_time_ms: float) -> None:
        """Actualiza tiempo de predicción del modelo"""
        try:
            # Obtener rendimiento actual
            performance = await self._get_model_performance(model_id)
            if performance:
                # Actualizar con nueva medición
                performance.prediction_time_ms = prediction_time_ms
                await self._record_model_performance(performance)
                
        except Exception as e:
            logger.warning(f"Error actualizando tiempo de predicción: {e}")
    
    async def _assess_model_complexity(self, model) -> str:
        """Evalúa complejidad del modelo"""
        model_type = type(model).__name__
        
        if 'Linear' in model_type:
            return 'Low'
        elif 'RandomForest' in model_type or 'GradientBoosting' in model_type:
            return 'Medium'
        elif 'MLP' in model_type or 'SVM' in model_type:
            return 'High'
        else:
            return 'Unknown'
    
    async def _generate_model_recommendations(self, model, performance: Optional[ModelPerformance]) -> List[str]:
        """Genera recomendaciones para el modelo"""
        recommendations = []
        
        if performance:
            if performance.r2_score < 0.7:
                recommendations.append("Considerar recopilar más datos de entrenamiento")
                recommendations.append("Evaluar ingeniería de características adicional")
            
            if performance.prediction_time_ms > 100:
                recommendations.append("Optimizar modelo para reducir tiempo de predicción")
            
            if performance.feature_count > 50:
                recommendations.append("Considerar reducción de dimensionalidad")
        
        return recommendations
    
    async def _assess_data_requirements(self, model_id: str) -> Dict[str, Any]:
        """Evalúa requisitos de datos del modelo"""
        return {
            'minimum_samples': 50,
            'recommended_samples': 200,
            'feature_quality': 'medium',
            'update_frequency': 'weekly'
        }
    
    async def _assess_prediction_reliability(self, model_id: str) -> Dict[str, Any]:
        """Evalúa confiabilidad de predicciones"""
        performance = await self._get_model_performance(model_id)
        
        if performance:
            reliability_score = performance.r2_score
            if reliability_score > 0.8:
                reliability = 'High'
            elif reliability_score > 0.6:
                reliability = 'Medium'
            else:
                reliability = 'Low'
        else:
            reliability = 'Unknown'
            reliability_score = 0.0
        
        return {
            'reliability_level': reliability,
            'reliability_score': reliability_score,
            'confidence_threshold': 0.7
        }

# Configuración por defecto
DEFAULT_ML_MODEL_CONFIG = {
    'db_path': 'ml_models.db',
    'models_directory': 'ml_models',
    'performance_threshold': 0.7,
    'retrain_interval_hours': 168,  # Una semana
    'max_features': 50,
    'cross_validation_folds': 5
}

# Función de utilidad para crear gestor de modelos
async def create_ml_model_manager(config: Optional[Dict[str, Any]] = None) -> AdvancedMLModelManager:
    """Crea y configura gestor de modelos ML"""
    if config is None:
        config = DEFAULT_ML_MODEL_CONFIG
    
    manager = AdvancedMLModelManager(config)
    await manager.initialize()
    return manager

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Crear gestor de modelos
        manager = await create_ml_model_manager()
        
        # Datos de ejemplo para entrenamiento
        training_data = [
            {
                'config_param1': 0.5, 'config_param2': 1.0,
                'resource_cpu': 0.3, 'resource_memory': 0.4,
                'performance_score': 0.8
            },
            {
                'config_param1': 0.7, 'config_param2': 0.8,
                'resource_cpu': 0.5, 'resource_memory': 0.6,
                'performance_score': 0.9
            },
            # ... más datos
        ]
        
        # Entrenar modelo de rendimiento
        model_id = await manager.train_performance_prediction_model(
            'github_mcp_server', training_data * 10  # Simular más datos
        )
        
        print(f"Modelo entrenado: {model_id}")
        
        # Realizar predicción
        prediction = await manager.predict_tool_performance(
            model_id, 
            {'config_param1': 0.6, 'config_param2': 0.9, 
             'resource_cpu': 0.4, 'resource_memory': 0.5}
        )
        
        print(f"Predicción: {prediction.predicted_value:.3f}")
        print(f"Explicación: {prediction.explanation}")
        
        # Obtener importancia de características
        importance = await manager.get_feature_importance(model_id)
        print(f"Top 3 características importantes:")
        for fi in importance[:3]:
            print(f"- {fi.feature_name}: {fi.importance_score:.3f}")
        
        # Generar insights
        insights = await manager.generate_model_insights(model_id)
        print(f"Insights del modelo: {insights}")
    
    # Ejecutar ejemplo
    asyncio.run(main())

