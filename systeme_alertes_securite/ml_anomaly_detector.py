#!/usr/bin/env python3
"""
Module de Détection d'Anomalies par Machine Learning
Amélioration prioritaire pour le Système d'Alertes Sécurité

Fonctionnalités:
- Apprentissage non supervisé pour détecter des patterns normaux
- Détection automatique d'anomalies comportementales  
- Réduction drastique des faux positifs
- Analyse prédictive des tendances
- Clustering des types d'alertes similaires
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import sqlite3
import pickle
import logging
from dataclasses import dataclass
from pathlib import Path

# Machine Learning imports
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('seaborn-v0_8')

from colorama import init, Fore, Style
init(autoreset=True)

@dataclass
class AnomalyResult:
    """Résultat d'analyse d'anomalie"""
    is_anomaly: bool
    confidence_score: float
    anomaly_type: str
    cluster_id: int
    explanation: str
    features_importance: Dict[str, float]
    timestamp: datetime

@dataclass
class MLModelMetrics:
    """Métriques d'un modèle ML"""
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    training_time: float
    last_retrain: datetime
    samples_count: int

class FeatureExtractor:
    """Extracteur de caractéristiques pour les alertes"""
    
    def __init__(self):
        self.label_encoders = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.fitted = False
    
    def extract_temporal_features(self, timestamp: datetime) -> Dict[str, float]:
        """Extraire les caractéristiques temporelles"""
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day,
            'month': timestamp.month,
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
            'is_night': 1 if timestamp.hour < 6 or timestamp.hour > 22 else 0,
            'is_business_hours': 1 if 9 <= timestamp.hour <= 17 else 0
        }
    
    def extract_alert_features(self, alert_data: Dict[str, Any]) -> Dict[str, float]:
        """Extraire les caractéristiques d'une alerte"""
        features = {}
        
        # Caractéristiques temporelles
        timestamp = datetime.fromisoformat(alert_data['timestamp'])
        features.update(self.extract_temporal_features(timestamp))
        
        # Niveau d'alerte (encodé)
        niveau_mapping = {'INFO': 0, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 3}
        features['niveau_encoded'] = niveau_mapping.get(alert_data.get('niveau', 'INFO'), 0)
        
        # Longueur du message
        message = alert_data.get('message', '')
        features['message_length'] = len(message)
        features['message_word_count'] = len(message.split())
        
        # Source (encodée)
        source = alert_data.get('source', 'unknown')
        if not self.fitted:
            # Mode training
            features['source_encoded'] = hash(source) % 1000
        else:
            # Mode inference
            features['source_encoded'] = self.label_encoders.get('source', {}).get(source, 0)
        
        # Caractéristiques des détails
        details = alert_data.get('details', {})
        features['details_count'] = len(details)
        features['has_ip'] = 1 if any('ip' in str(k).lower() or 'ip' in str(v).lower() 
                                     for k, v in details.items()) else 0
        features['has_user'] = 1 if any('user' in str(k).lower() or 'user' in str(v).lower() 
                                       for k, v in details.items()) else 0
        features['has_file'] = 1 if any('file' in str(k).lower() or 'path' in str(k).lower() 
                                       for k, v in details.items()) else 0
        
        return features
    
    def extract_sequence_features(self, alerts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extraire les caractéristiques de séquence d'alertes"""
        if len(alerts) < 2:
            return {
                'sequence_length': len(alerts),
                'avg_time_between': 0,
                'niveau_variance': 0,
                'source_diversity': 1 if alerts else 0
            }
        
        # Trier par timestamp
        alerts_sorted = sorted(alerts, key=lambda x: datetime.fromisoformat(x['timestamp']))
        
        # Calculer les intervals de temps
        intervals = []
        for i in range(1, len(alerts_sorted)):
            t1 = datetime.fromisoformat(alerts_sorted[i-1]['timestamp'])
            t2 = datetime.fromisoformat(alerts_sorted[i]['timestamp'])
            intervals.append((t2 - t1).total_seconds())
        
        # Variance des niveaux
        niveau_mapping = {'INFO': 0, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 3}
        niveaux = [niveau_mapping.get(a.get('niveau', 'INFO'), 0) for a in alerts_sorted]
        
        # Diversité des sources
        sources = set(a.get('source', 'unknown') for a in alerts_sorted)
        
        return {
            'sequence_length': len(alerts),
            'avg_time_between': np.mean(intervals) if intervals else 0,
            'max_time_between': max(intervals) if intervals else 0,
            'min_time_between': min(intervals) if intervals else 0,
            'time_variance': np.var(intervals) if intervals else 0,
            'niveau_variance': np.var(niveaux),
            'niveau_trend': niveaux[-1] - niveaux[0] if len(niveaux) > 1 else 0,
            'source_diversity': len(sources) / len(alerts),
            'repetition_rate': 1 - (len(sources) / len(alerts))  # Plus de répétition = plus suspect
        }
    
    def fit_transform(self, alerts_data: List[Dict[str, Any]]) -> np.ndarray:
        """Ajuster l'extracteur et transformer les données"""
        features_list = []
        
        # Collecter les caractéristiques individuelles
        for alert in alerts_data:
            features = self.extract_alert_features(alert)
            features_list.append(features)
        
        # Créer un DataFrame pour faciliter le traitement
        df = pd.DataFrame(features_list)
        
        # Ajuster les encodeurs
        if not self.fitted:
            # Encoder les sources
            sources = [a.get('source', 'unknown') for a in alerts_data]
            unique_sources = list(set(sources))
            self.label_encoders['source'] = {source: idx for idx, source in enumerate(unique_sources)}
            
            # Re-encoder avec les vrais indices
            for i, alert in enumerate(alerts_data):
                source = alert.get('source', 'unknown')
                features_list[i]['source_encoded'] = self.label_encoders['source'].get(source, 0)
            
            df = pd.DataFrame(features_list)
            self.fitted = True
        
        return df.values
    
    def transform(self, alerts_data: List[Dict[str, Any]]) -> np.ndarray:
        """Transformer les données (mode inference)"""
        if not self.fitted:
            raise ValueError("L'extracteur doit être ajusté avant la transformation")
        
        features_list = []
        for alert in alerts_data:
            features = self.extract_alert_features(alert)
            features_list.append(features)
        
        df = pd.DataFrame(features_list)
        return df.values

class MLAnomalyDetector:
    """Détecteur d'anomalies par Machine Learning"""
    
    def __init__(self, db_path: str, model_dir: str = "./ml_models"):
        self.db_path = db_path
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Modèles ML
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.feature_extractor = FeatureExtractor()
        
        # Métriques et état
        self.models_trained = False
        self.training_data_size = 0
        self.last_training = None
        self.metrics = {}
        
        # Configuration
        self.min_training_samples = 100
        self.retrain_threshold = 1000  # Nouveaux échantillons avant re-entraînement
        self.anomaly_threshold = 0.1
        
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger('MLAnomalyDetector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.model_dir / 'ml_anomaly.log')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_training_data(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Charger les données d'entraînement depuis la base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        cursor.execute('''
            SELECT id, timestamp, niveau, source, message, details, resolu
            FROM alertes 
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (cutoff_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        alerts_data = []
        for row in rows:
            alert = {
                'id': row[0],
                'timestamp': row[1],
                'niveau': row[2],
                'source': row[3],
                'message': row[4],
                'details': json.loads(row[5]) if row[5] else {},
                'resolu': bool(row[6])
            }
            alerts_data.append(alert)
        
        self.logger.info(f"Chargé {len(alerts_data)} alertes pour l'entraînement")
        return alerts_data
    
    def create_labels(self, alerts_data: List[Dict[str, Any]]) -> np.ndarray:
        """Créer des labels pour l'entraînement supervisé (optionnel)"""
        # Utiliser des heuristiques pour étiqueter les anomalies
        labels = []
        
        for alert in alerts_data:
            is_anomaly = False
            
            # Règles heuristiques pour identifier les anomalies
            timestamp = datetime.fromisoformat(alert['timestamp'])
            
            # Alertes en dehors des heures normales
            if timestamp.hour < 6 or timestamp.hour > 22:
                is_anomaly = True
            
            # Alertes critiques répétitives
            if alert.get('niveau') == 'CRITICAL':
                is_anomaly = True
            
            # Messages très courts ou très longs (suspects)
            message_len = len(alert.get('message', ''))
            if message_len < 10 or message_len > 500:
                is_anomaly = True
            
            # Sources inhabituelles (basé sur fréquence)
            # TODO: Améliorer avec l'analyse de fréquence
            
            labels.append(1 if is_anomaly else 0)
        
        return np.array(labels)
    
    def train_models(self, alerts_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, MLModelMetrics]:
        """Entraîner tous les modèles ML"""
        if alerts_data is None:
            alerts_data = self.load_training_data()
        
        if len(alerts_data) < self.min_training_samples:
            raise ValueError(f"Pas assez de données pour l'entraînement (minimum {self.min_training_samples})")
        
        start_time = datetime.now()
        self.logger.info(f"Début de l'entraînement avec {len(alerts_data)} échantillons")
        
        # Extraire les caractéristiques
        X = self.feature_extractor.fit_transform(alerts_data)
        
        # Normaliser
        X_scaled = self.scaler.fit_transform(X)
        
        metrics = {}
        
        # 1. Entraîner Isolation Forest (détection d'anomalies non supervisée)
        print(f"{Fore.CYAN}🤖 Entraînement Isolation Forest...")
        if_start = datetime.now()
        self.isolation_forest.fit(X_scaled)
        if_time = (datetime.now() - if_start).total_seconds()
        
        # Évaluer Isolation Forest
        anomaly_scores = self.isolation_forest.decision_function(X_scaled)
        predictions = self.isolation_forest.predict(X_scaled)
        anomaly_rate = np.sum(predictions == -1) / len(predictions)
        
        metrics['isolation_forest'] = MLModelMetrics(
            model_type="Isolation Forest",
            accuracy=0.0,  # Non applicable pour non supervisé
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            false_positive_rate=anomaly_rate,
            training_time=if_time,
            last_retrain=datetime.now(),
            samples_count=len(alerts_data)
        )
        
        # 2. Entraîner DBSCAN (clustering)
        print(f"{Fore.CYAN}🤖 Entraînement DBSCAN...")
        dbscan_start = datetime.now()
        cluster_labels = self.dbscan.fit_predict(X_scaled)
        dbscan_time = (datetime.now() - dbscan_start).total_seconds()
        
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        noise_ratio = np.sum(cluster_labels == -1) / len(cluster_labels)
        
        metrics['dbscan'] = MLModelMetrics(
            model_type="DBSCAN",
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            false_positive_rate=noise_ratio,
            training_time=dbscan_time,
            last_retrain=datetime.now(),
            samples_count=len(alerts_data)
        )
        
        # Mettre à jour l'état
        self.models_trained = True
        self.training_data_size = len(alerts_data)
        self.last_training = datetime.now()
        self.metrics = metrics
        
        # Sauvegarder les modèles (après mise à jour de l'état)
        self.save_models()
        
        total_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Entraînement terminé en {total_time:.2f}s")
        
        # Afficher les résultats
        self.print_training_summary(metrics, n_clusters, anomaly_rate, noise_ratio)
        
        return metrics
    
    def print_training_summary(self, metrics: Dict[str, MLModelMetrics], 
                             n_clusters: int, anomaly_rate: float, noise_ratio: float):
        """Afficher un résumé de l'entraînement"""
        print(f"\n{Fore.GREEN}🎯 RÉSUMÉ DE L'ENTRAÎNEMENT ML")
        print("=" * 50)
        
        print(f"{Fore.CYAN}📊 Isolation Forest:")
        print(f"   • Taux d'anomalies détectées: {anomaly_rate:.1%}")
        print(f"   • Temps d'entraînement: {metrics['isolation_forest'].training_time:.2f}s")
        
        print(f"\n{Fore.CYAN}🔍 DBSCAN Clustering:")
        print(f"   • Nombre de clusters: {n_clusters}")
        print(f"   • Taux de bruit: {noise_ratio:.1%}")
        print(f"   • Temps d'entraînement: {metrics['dbscan'].training_time:.2f}s")
        
        print(f"\n{Fore.GREEN}✅ Modèles sauvegardés dans: {self.model_dir}")
    
    def detect_anomaly(self, alert_data: Dict[str, Any]) -> AnomalyResult:
        """Détecter si une alerte est une anomalie"""
        if not self.models_trained:
            return AnomalyResult(
                is_anomaly=False,
                confidence_score=0.5,
                anomaly_type="model_not_trained",
                cluster_id=-1,
                explanation="Les modèles ML ne sont pas encore entraînés",
                features_importance={},
                timestamp=datetime.now()
            )
        
        # Extraire les caractéristiques
        X = self.feature_extractor.transform([alert_data])
        X_scaled = self.scaler.transform(X)
        
        # Prédiction Isolation Forest
        if_score = self.isolation_forest.decision_function(X_scaled)[0]
        if_prediction = self.isolation_forest.predict(X_scaled)[0]
        
        # Prédiction DBSCAN (cluster)
        cluster_id = self.dbscan.fit_predict(X_scaled)[0]
        
        # Déterminer si c'est une anomalie
        is_anomaly = if_prediction == -1
        confidence_score = abs(if_score)  # Score de confiance
        
        # Type d'anomalie
        anomaly_type = "normal"
        if is_anomaly:
            if cluster_id == -1:
                anomaly_type = "outlier"
            else:
                anomaly_type = f"cluster_{cluster_id}"
        
        # Explication
        explanation = self.generate_explanation(alert_data, if_score, cluster_id)
        
        # Importance des caractéristiques (approximation)
        features_importance = self.calculate_feature_importance(X_scaled[0])
        
        result = AnomalyResult(
            is_anomaly=is_anomaly,
            confidence_score=confidence_score,
            anomaly_type=anomaly_type,
            cluster_id=cluster_id,
            explanation=explanation,
            features_importance=features_importance,
            timestamp=datetime.now()
        )
        
        self.logger.info(f"Anomalie détectée: {is_anomaly}, Score: {confidence_score:.3f}, Type: {anomaly_type}")
        return result
    
    def generate_explanation(self, alert_data: Dict[str, Any], if_score: float, cluster_id: int) -> str:
        """Générer une explication pour le résultat"""
        explanations = []
        
        # Analyse temporelle
        timestamp = datetime.fromisoformat(alert_data['timestamp'])
        if timestamp.hour < 6 or timestamp.hour > 22:
            explanations.append("Alerte en dehors des heures normales")
        
        if timestamp.weekday() >= 5:
            explanations.append("Alerte en weekend")
        
        # Analyse du niveau
        niveau = alert_data.get('niveau', 'INFO')
        if niveau in ['CRITICAL', 'ERROR']:
            explanations.append(f"Niveau {niveau} inhabituel")
        
        # Score d'isolation
        if if_score < -0.5:
            explanations.append("Pattern très inhabituel détecté")
        elif if_score < 0:
            explanations.append("Pattern légèrement inhabituel")
        
        # Cluster
        if cluster_id == -1:
            explanations.append("Ne correspond à aucun pattern connu")
        else:
            explanations.append(f"Similaire au groupe de patterns #{cluster_id}")
        
        return " • ".join(explanations) if explanations else "Pattern normal"
    
    def calculate_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """Calculer l'importance approximative des caractéristiques"""
        feature_names = [
            'hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 
            'is_night', 'is_business_hours', 'niveau_encoded', 'message_length',
            'message_word_count', 'source_encoded', 'details_count', 
            'has_ip', 'has_user', 'has_file'
        ]
        
        # Approximation simple basée sur la déviation par rapport à la moyenne
        importance = {}
        for i, name in enumerate(feature_names[:len(features)]):
            # Plus la valeur est éloignée de 0 (après normalisation), plus elle est importante
            importance[name] = abs(float(features[i]))
        
        return importance
    
    def analyze_batch(self, alerts_data: List[Dict[str, Any]]) -> List[AnomalyResult]:
        """Analyser un lot d'alertes"""
        results = []
        
        print(f"{Fore.CYAN}🔍 Analyse ML de {len(alerts_data)} alertes...")
        
        for alert in alerts_data:
            result = self.detect_anomaly(alert)
            results.append(result)
        
        # Statistiques
        anomalies = [r for r in results if r.is_anomaly]
        print(f"{Fore.GREEN}📊 Résultats: {len(anomalies)} anomalies détectées sur {len(results)} alertes")
        
        return results
    
    def save_models(self):
        """Sauvegarder les modèles entraînés"""
        models_to_save = {
            'isolation_forest': self.isolation_forest,
            'dbscan': self.dbscan,
            'scaler': self.scaler,
            'feature_extractor': self.feature_extractor
        }
        
        for name, model in models_to_save.items():
            filepath = self.model_dir / f"{name}.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
        
        # Sauvegarder les métadonnées
        metadata = {
            'training_data_size': self.training_data_size,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'models_trained': self.models_trained,  # Cette variable doit être True après l'entraînement
            'metrics': {k: {
                'model_type': v.model_type,
                'training_time': v.training_time,
                'samples_count': v.samples_count,
                'last_retrain': v.last_retrain.isoformat()
            } for k, v in self.metrics.items()}
        }
        
        with open(self.model_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Modèles sauvegardés dans {self.model_dir}")
    
    def load_models(self) -> bool:
        """Charger les modèles sauvegardés"""
        try:
            models_to_load = ['isolation_forest', 'dbscan', 'scaler', 'feature_extractor']
            
            for name in models_to_load:
                filepath = self.model_dir / f"{name}.pkl"
                if filepath.exists():
                    with open(filepath, 'rb') as f:
                        setattr(self, name, pickle.load(f))
                else:
                    return False
            
            # Charger les métadonnées
            metadata_path = self.model_dir / 'metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                self.training_data_size = metadata.get('training_data_size', 0)
                self.last_training = datetime.fromisoformat(metadata['last_training']) if metadata.get('last_training') else None
                self.models_trained = metadata.get('models_trained', False)
                
                # Reconstruire les métriques
                self.metrics = {}
                for k, v in metadata.get('metrics', {}).items():
                    self.metrics[k] = MLModelMetrics(
                        model_type=v['model_type'],
                        accuracy=0.0,
                        precision=0.0,
                        recall=0.0,
                        f1_score=0.0,
                        false_positive_rate=0.0,
                        training_time=v['training_time'],
                        last_retrain=datetime.fromisoformat(v['last_retrain']),
                        samples_count=v['samples_count']
                    )
            
            self.logger.info("Modèles chargés avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des modèles: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """Obtenir le statut des modèles ML"""
        return {
            'models_trained': self.models_trained,
            'training_data_size': self.training_data_size,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'models_dir': str(self.model_dir),
            'metrics': self.metrics
        }
    
    def should_retrain(self) -> bool:
        """Déterminer s'il faut re-entraîner les modèles"""
        if not self.models_trained:
            return True
        
        # Vérifier si assez de nouvelles données
        current_data_size = len(self.load_training_data(days_back=7))
        
        if current_data_size >= self.retrain_threshold:
            return True
        
        # Vérifier l'ancienneté du dernier entraînement
        if self.last_training:
            days_since_training = (datetime.now() - self.last_training).days
            if days_since_training > 7:  # Re-entraîner chaque semaine
                return True
        
        return False
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Générer un rapport d'analyse ML"""
        if not self.models_trained:
            return {'error': 'Modèles non entraînés'}
        
        # Analyser les données récentes
        recent_data = self.load_training_data(days_back=7)
        results = self.analyze_batch(recent_data)
        
        # Statistiques
        total_alerts = len(results)
        anomalies = [r for r in results if r.is_anomaly]
        anomaly_rate = len(anomalies) / total_alerts if total_alerts > 0 else 0
        
        # Analyse des types d'anomalies
        anomaly_types = {}
        for result in anomalies:
            anomaly_types[result.anomaly_type] = anomaly_types.get(result.anomaly_type, 0) + 1
        
        # Scores de confiance
        confidence_scores = [r.confidence_score for r in results]
        
        return {
            'period': '7 derniers jours',
            'total_alerts_analyzed': total_alerts,
            'anomalies_detected': len(anomalies),
            'anomaly_rate': anomaly_rate,
            'anomaly_types': anomaly_types,
            'avg_confidence': np.mean(confidence_scores),
            'confidence_std': np.std(confidence_scores),
            'model_status': self.get_model_status(),
            'recommendations': self._generate_recommendations(anomaly_rate, anomaly_types)
        }
    
    def _generate_recommendations(self, anomaly_rate: float, anomaly_types: Dict[str, int]) -> List[str]:
        """Générer des recommandations basées sur l'analyse"""
        recommendations = []
        
        if anomaly_rate > 0.3:
            recommendations.append("⚠️ Taux d'anomalies très élevé - Vérifier les règles d'alerte")
        elif anomaly_rate > 0.15:
            recommendations.append("📊 Taux d'anomalies modéré - Surveillance recommandée")
        else:
            recommendations.append("✅ Taux d'anomalies normal")
        
        if 'outlier' in anomaly_types and anomaly_types['outlier'] > 5:
            recommendations.append("🔍 Beaucoup de patterns inconnus - Enrichir les données d'entraînement")
        
        if self.should_retrain():
            recommendations.append("🔄 Re-entraînement des modèles recommandé")
        
        return recommendations


def main():
    """Fonction principale pour tester le détecteur ML"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Détecteur d'Anomalies ML pour Alertes Sécurité")
    parser.add_argument("--db", default="../systeme_alertes_securite/alertes.db", help="Base de données des alertes")
    parser.add_argument("--train", action="store_true", help="Entraîner les modèles")
    parser.add_argument("--analyze", action="store_true", help="Analyser les alertes récentes")
    parser.add_argument("--report", action="store_true", help="Générer un rapport d'analyse")
    parser.add_argument("--days", type=int, default=30, help="Nombre de jours pour les données")
    
    args = parser.parse_args()
    
    print(f"{Fore.BLUE}🤖 DÉTECTEUR D'ANOMALIES ML - ALERTES SÉCURITÉ")
    print("=" * 55)
    
    # Initialiser le détecteur
    detector = MLAnomalyDetector(db_path=args.db)
    
    # Tenter de charger les modèles existants
    if detector.load_models():
        print(f"{Fore.GREEN}✅ Modèles existants chargés")
    else:
        print(f"{Fore.YELLOW}⚠️ Aucun modèle existant trouvé")
    
    if args.train or not detector.models_trained:
        print(f"{Fore.CYAN}🚀 Entraînement des modèles ML...")
        try:
            metrics = detector.train_models()
            print(f"{Fore.GREEN}✅ Entraînement terminé avec succès")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'entraînement: {e}")
            return
    
    if args.analyze:
        print(f"\n{Fore.CYAN}🔍 Analyse des alertes récentes...")
        recent_alerts = detector.load_training_data(days_back=7)
        results = detector.analyze_batch(recent_alerts)
        
        # Afficher les anomalies détectées
        anomalies = [r for r in results if r.is_anomaly]
        if anomalies:
            print(f"\n{Fore.RED}🚨 ANOMALIES DÉTECTÉES:")
            for i, anomaly in enumerate(anomalies[:5], 1):
                print(f"{i}. Type: {anomaly.anomaly_type}")
                print(f"   Confiance: {anomaly.confidence_score:.3f}")
                print(f"   Explication: {anomaly.explanation}")
                print()
    
    if args.report:
        print(f"\n{Fore.CYAN}📊 Génération du rapport d'analyse...")
        report = detector.generate_analytics_report()
        
        if 'error' not in report:
            print(f"\n{Fore.GREEN}📈 RAPPORT D'ANALYSE ML")
            print("-" * 30)
            print(f"Période analysée: {report['period']}")
            print(f"Alertes analysées: {report['total_alerts_analyzed']}")
            print(f"Anomalies détectées: {report['anomalies_detected']}")
            print(f"Taux d'anomalies: {report['anomaly_rate']:.1%}")
            print(f"Confiance moyenne: {report['avg_confidence']:.3f}")
            
            print(f"\n{Fore.CYAN}🔍 Types d'anomalies:")
            for anomaly_type, count in report['anomaly_types'].items():
                print(f"  • {anomaly_type}: {count}")
            
            print(f"\n{Fore.YELLOW}💡 Recommandations:")
            for rec in report['recommendations']:
                print(f"  {rec}")
        else:
            print(f"{Fore.RED}❌ {report['error']}")


if __name__ == "__main__":
    main()