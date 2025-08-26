from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
from loguru import logger

class EntrenadorModelos:
    """Sistema de entrenamiento de modelos de ML para clasificación éxito/fracaso"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.modelos = {}
        self.scalers = {}
        
    async def entrenar_modelo(self, X: pd.DataFrame, y: pd.Series, 
                            nombre_modelo: str = 'random_forest') -> Dict[str, Any]:
        """
        Entrena un modelo de clasificación para predecir éxito/fracaso.
        
        Args:
            X: Características de entrada
            y: Variable objetivo
            nombre_modelo: Tipo de modelo a entrenar
        
        Returns:
            Dict: Métricas y información del modelo entrenado
        """
        try:
            # Preprocesamiento
            X_processed, y_processed = self._preprocesar_datos(X, y)
            
            # Seleccionar modelo
            modelo = self._seleccionar_modelo(nombre_modelo)
            
            # Entrenamiento con validación cruzada
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scores = cross_val_score(modelo, X_processed, y_processed, 
                                   cv=cv, scoring='accuracy')
            
            # Entrenamiento final
            modelo.fit(X_processed, y_processed)
            
            # Evaluación
            y_pred = modelo.predict(X_processed)
            reporte = classification_report(y_processed, y_pred, output_dict=True)
            matriz_confusion = confusion_matrix(y_processed, y_pred)
            
            # Guardar modelo
            self.modelos[nombre_modelo] = modelo
            metricas = {
                'accuracy_cv_mean': np.mean(scores),
                'accuracy_cv_std': np.std(scores),
                'accuracy_train': accuracy_score(y_processed, y_pred),
                'classification_report': reporte,
                'confusion_matrix': matriz_confusion.tolist(),
                'n_muestras_entrenamiento': len(X_processed),
                'caracteristicas': X.columns.tolist()
            }
            
            logger.info(f"Modelo {nombre_modelo} entrenado. Accuracy CV: {np.mean(scores):.3f}")
            return metricas
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {e}")
            raise
    
    def _preprocesar_datos(self, X: pd.DataFrame, y: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocesa los datos para entrenamiento"""
        # Escalar características numéricas
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X.select_dtypes(include=[np.number]))
        self.scalers['standard'] = scaler
        
        # Balancear clases si es necesario
        if y.value_counts().min() / len(y) < 0.3:  # Si la clase minoritaria es <30%
            smote = SMOTE(random_state=42)
            X_balanced, y_balanced = smote.fit_resample(X_scaled, y)
            return X_balanced, y_balanced
        
        return X_scaled, y
    
    def _seleccionar_modelo(self, nombre_modelo: str):
        """Selecciona y configura el modelo especificado"""
        config_modelos = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            ),
            'svm': SVC(
                kernel='rbf',
                random_state=42,
                class_weight='balanced',
                probability=True
            )
        }
        
        return config_modelos.get(nombre_modelo, config_modelos['random_forest'])
    
    async def predecir_riesgo(self, caracteristicas: Dict[str, Any], 
                            nombre_modelo: str = 'random_forest') -> Dict[str, Any]:
        """
        Predice el riesgo de fracaso para un nuevo episodio.
        
        Args:
            caracteristicas: Características del nuevo episodio
            nombre_modelo: Modelo a utilizar para predicción
        
        Returns:
            Dict: Predicción de probabilidades y riesgo
        """
        if nombre_modelo not in self.modelos:
            raise ValueError(f"Modelo {nombre_modelo} no entrenado")
        
        try:
            # Preparar características para predicción
            X_pred = self._preparar_prediccion(caracteristicas)
            
            # Realizar predicción
            modelo = self.modelos[nombre_modelo]
            probabilidades = modelo.predict_proba(X_pred)[0]
            prediccion = modelo.predict(X_pred)[0]
            
            return {
                'prediccion': 'exito' if prediccion == 1 else 'fracaso',
                'probabilidad_exito': float(probabilidades[1]),
                'probabilidad_fracaso': float(probabilidades[0]),
                'riesgo_relativo': float(probabilidades[0] / probabilidades[1] if probabilidades[1] > 0 else float('inf')),
                'modelo_utilizado': nombre_modelo,
                'confianza': float(max(probabilidades))
            }
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise