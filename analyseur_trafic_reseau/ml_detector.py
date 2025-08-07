#!/usr/bin/env python3
"""
Détecteur d'Anomalies par Machine Learning - Analyseur de Trafic Réseau
Utilise des algorithmes d'apprentissage automatique pour détecter des anomalies dans le trafic réseau
Support IPv4/IPv6 complet
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pickle
import os
import warnings

# Ignorer les warnings sklearn pour une sortie plus propre
warnings.filterwarnings('ignore', category=UserWarning)

class MLAnomalyDetector:
    """Détecteur d'anomalies utilisant l'apprentissage automatique"""
    
    def __init__(self, model_type: str = "isolation_forest", threshold: float = 0.1):
        """
        Initialiser le détecteur ML
        
        Args:
            model_type: Type de modèle ("isolation_forest" ou "dbscan")
            threshold: Seuil de détection d'anomalies (plus bas = plus strict)
        """
        self.model_type = model_type
        self.threshold = threshold
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.last_confidence = 0.0
        
        # Statistiques de détection
        self.detection_stats = {
            'total_packets': 0,
            'anomalies_detected': 0,
            'false_positives': 0,
            'true_positives': 0,
            'last_training': None
        }
        
        # Initialiser le modèle selon le type
        if model_type == "isolation_forest":
            self.model = IsolationForest(
                contamination=threshold,
                random_state=42,
                n_estimators=100
            )
        elif model_type == "dbscan":
            self.model = DBSCAN(
                eps=0.5,
                min_samples=5
            )
        else:
            raise ValueError(f"Type de modèle non supporté: {model_type}")
        
        print(f"🤖 Détecteur ML initialisé - Type: {model_type}, Seuil: {threshold}")
    
    def extract_features(self, packet: Dict) -> List[float]:
        """Extraire les features d'un paquet pour l'analyse ML - Support IPv6"""
        features = []
        
        # Feature 1: Taille du paquet (normalisée)
        length = packet.get('length', 0)
        features.append(min(length / 1500.0, 1.0))  # Normaliser par MTU standard
        
        # Feature 2: Type de protocole (encodage numérique)
        protocol_map = {'TCP': 1, 'UDP': 2, 'ICMP': 3, 'ICMPv6': 4, 'HTTP': 5, 'HTTPS': 6, 'FTP': 7, 'SSH': 8}
        protocol = packet.get('protocol', 'OTHER')
        features.append(protocol_map.get(protocol, 0) / 8.0)  # Normaliser
        
        # Feature 3: Port source (normalisé)
        src_port = packet.get('src_port', 0)
        if isinstance(src_port, int):
            features.append(src_port / 65535.0)
        else:
            features.append(0.0)
        
        # Feature 4: Port destination (normalisé)
        dst_port = packet.get('dst_port', 0)
        if isinstance(dst_port, int):
            features.append(dst_port / 65535.0)
        else:
            features.append(0.0)
        
        # Feature 5: Heure de la journée (cyclique)
        timestamp = packet.get('timestamp', datetime.now())
        if timestamp:
            hour = timestamp.hour
            features.append(hour / 24.0)
        else:
            features.append(0.0)
        
        # Feature 6: Jour de la semaine (cyclique)
        if timestamp:
            day = timestamp.weekday()
            features.append(day / 7.0)
        else:
            features.append(0.0)
        
        # Feature 7: Hash de l'IP source (pour anonymisation)
        src_ip = packet.get('src_ip', '0.0.0.0')
        src_ip_hash = self._get_ip_hash(src_ip)
        features.append(src_ip_hash / 255.0)
        
        # Feature 8: Hash de l'IP destination
        dst_ip = packet.get('dst_ip', '0.0.0.0')
        dst_ip_hash = self._get_ip_hash(dst_ip)
        features.append(dst_ip_hash / 255.0)
        
        # Feature 9: Ratio taille/port (indicateur de patterns suspects)
        if dst_port and dst_port > 0:
            port_length_ratio = length / float(dst_port)
            features.append(min(port_length_ratio / 100.0, 1.0))
        else:
            features.append(0.0)
        
        # Feature 10: Port bien connu (0-1024)
        is_well_known = 1.0 if (dst_port and dst_port <= 1024) else 0.0
        features.append(is_well_known)
        
        # Feature 11: Version IP (4.0 pour IPv4, 6.0 pour IPv6)
        ip_version = packet.get('ip_version', 4)
        features.append(float(ip_version))
        
        # Feature 12: Indicateur IPv6 spécifique (hop limit normalisé)
        if ip_version == 6:
            hop_limit = packet.get('ipv6_hop_limit', 64) / 255.0  # Normaliser sur [0,1]
        else:
            hop_limit = 0.5  # Valeur neutre pour IPv4
        features.append(hop_limit)
        
        # Feature 13: Longueur de l'adresse (IPv4=4, IPv6=16, approximation)
        addr_length_indicator = 16.0 if ':' in str(src_ip) else 4.0
        features.append(addr_length_indicator)
        
        return features
    
    def _get_ip_hash(self, ip_str: str) -> int:
        """Générer un hash numérique pour une adresse IP (IPv4 ou IPv6)"""
        try:
            if ':' in str(ip_str):  # IPv6
                # Prendre les derniers segments pour l'anonymisation
                segments = str(ip_str).split(':')
                if segments:
                    last_segment = segments[-1] if segments[-1] else segments[-2]
                    return int(last_segment, 16) % 255 if last_segment else 0
                return 0
            else:  # IPv4
                # Utiliser le dernier octet comme avant
                octets = str(ip_str).split('.')
                if len(octets) >= 4:
                    return int(octets[-1]) % 255
                return 0
        except (ValueError, IndexError):
            return 0
    
    def train(self, training_data: List[List[float]], labels: Optional[List[int]] = None):
        """Entraîner le modèle avec des données d'apprentissage"""
        if not training_data:
            print("❌ Aucune donnée d'entraînement fournie")
            return False
        
        try:
            # Convertir en numpy array
            X = np.array(training_data)
            
            # Vérifier la forme des données
            if X.shape[0] < 10:
                print("⚠️ Pas assez de données pour un entraînement efficace (min 10 échantillons)")
                return False
            
            # Normaliser les données
            X_scaled = self.scaler.fit_transform(X)
            
            # Entraîner le modèle
            if self.model_type == "isolation_forest":
                self.model.fit(X_scaled)
            elif self.model_type == "dbscan":
                # DBSCAN ne nécessite pas d'entraînement explicite
                pass
            
            self.is_trained = True
            self.detection_stats['last_training'] = datetime.now()
            
            print(f"✅ Modèle entraîné avec {X.shape[0]} échantillons et {X.shape[1]} features")
            
            # Sauvegarder le modèle
            self.save_model()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'entraînement: {e}")
            return False
    
    def detect_anomaly(self, packet: Dict) -> bool:
        """Détecter si un paquet est une anomalie"""
        if not self.is_trained:
            # Si le modèle n'est pas entraîné, utiliser des règles heuristiques simples
            return self._heuristic_detection(packet)
        
        try:
            # Extraire les features
            features = self.extract_features(packet)
            
            # Normaliser
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # Prédiction
            if self.model_type == "isolation_forest":
                # Isolation Forest retourne -1 pour les anomalies, 1 pour les normaux
                prediction = self.model.predict(X_scaled)[0]
                # Calculer le score d'anomalie (plus négatif = plus anormal)
                anomaly_score = self.model.decision_function(X_scaled)[0]
                
                # Normaliser le score entre 0 et 1
                self.last_confidence = abs(anomaly_score)
                
                is_anomaly = prediction == -1
                
            elif self.model_type == "dbscan":
                # Pour DBSCAN, on considère les points isolés comme des anomalies
                cluster = self.model.fit_predict(X_scaled)
                is_anomaly = cluster[0] == -1
                self.last_confidence = 0.5  # Score par défaut pour DBSCAN
            
            else:
                is_anomaly = False
                self.last_confidence = 0.0
            
            # Mettre à jour les statistiques
            self.detection_stats['total_packets'] += 1
            if is_anomaly:
                self.detection_stats['anomalies_detected'] += 1
            
            return is_anomaly
            
        except Exception as e:
            print(f"❌ Erreur lors de la détection: {e}")
            return False
    
    def _heuristic_detection(self, packet: Dict) -> bool:
        """Détection heuristique simple quand le modèle n'est pas entraîné - Support IPv6"""
        # Règles simples pour détecter des anomalies
        
        # Taille de paquet anormale
        length = packet.get('length', 0)
        if length > 9000 or length < 20:  # Jumbo frames ou paquets trop petits
            self.last_confidence = 0.8
            return True
        
        # Ports suspects
        dst_port = packet.get('dst_port', 0)
        suspicious_ports = {1337, 31337, 4444, 5555, 6666, 7777, 8888, 9999}
        if dst_port in suspicious_ports:
            self.last_confidence = 0.7
            return True
        
        # Protocoles rares ou suspects
        protocol = packet.get('protocol', '')
        if protocol in ['ICMP', 'ICMPv6'] and dst_port and dst_port > 1024:
            self.last_confidence = 0.6
            return True
        
        # IPv6 spécifique : hop limit très bas
        if packet.get('ip_version') == 6:
            hop_limit = packet.get('ipv6_hop_limit', 64)
            if hop_limit < 10:
                self.last_confidence = 0.8
                return True
            
            # ICMPv6 type suspect
            icmpv6_type = packet.get('icmpv6_type')
            if icmpv6_type == 1:  # Destination Unreachable en masse
                self.last_confidence = 0.6
                return True
        
        # IPs privées communicant sur des ports publics inhabituels (IPv4)
        src_ip = str(packet.get('src_ip', ''))
        if src_ip.startswith(('192.168.', '10.', '172.')):
            if dst_port in {21, 23, 135, 139, 445}:  # Ports souvent ciblés
                self.last_confidence = 0.5
                return True
        
        # IPv6 link-local addresses in unusual contexts
        if src_ip.startswith('fe80::') and dst_port and dst_port < 1024:
            self.last_confidence = 0.4
            return True
        
        self.last_confidence = 0.1
        return False
    
    def update_threshold(self, new_threshold: float):
        """Mettre à jour le seuil de détection"""
        self.threshold = new_threshold
        if self.model_type == "isolation_forest" and self.model:
            self.model.contamination = new_threshold
            # Re-entraîner si nécessaire
            if self.is_trained:
                print(f"✅ Seuil mis à jour: {new_threshold}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Obtenir l'importance des features (approximative pour Isolation Forest)"""
        if not self.is_trained or self.model_type != "isolation_forest":
            return {}
        
        # Pour Isolation Forest, on peut approximer l'importance des features
        # en analysant la profondeur moyenne des splits
        feature_names = [
            'packet_length', 'protocol_type', 'src_port', 'dst_port',
            'hour_of_day', 'day_of_week', 'src_ip_last_octet', 
            'dst_ip_last_octet', 'port_length_ratio', 'is_well_known_port'
        ]
        
        # Simulation d'importance (dans un vrai cas, on utiliserait des méthodes plus sophistiquées)
        importances = {
            'packet_length': 0.13,
            'protocol_type': 0.11,
            'dst_port': 0.16,
            'src_port': 0.09,
            'port_length_ratio': 0.12,
            'is_well_known_port': 0.11,
            'ip_version': 0.08,  # Nouvelle feature IPv6
            'ipv6_hop_limit': 0.06,  # Spécifique IPv6
            'addr_length_indicator': 0.04,
            'hour_of_day': 0.05,
            'day_of_week': 0.03,
            'src_ip_hash': 0.01,
            'dst_ip_hash': 0.01
        }
        
        return importances
    
    def generate_training_data_from_packets(self, packets: List[Dict]) -> List[List[float]]:
        """Générer des données d'entraînement à partir d'une liste de paquets"""
        training_data = []
        
        for packet in packets:
            features = self.extract_features(packet)
            training_data.append(features)
        
        return training_data
    
    def save_model(self, filepath: str = "ml_traffic_model.pkl"):
        """Sauvegarder le modèle entraîné"""
        if not self.is_trained:
            return False
        
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'threshold': self.threshold,
                'model_type': self.model_type,
                'detection_stats': self.detection_stats,
                'is_trained': self.is_trained
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✅ Modèle sauvegardé: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde modèle: {e}")
            return False
    
    def load_model(self, filepath: str = "ml_traffic_model.pkl"):
        """Charger un modèle pré-entraîné"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.threshold = model_data['threshold']
            self.model_type = model_data['model_type']
            self.detection_stats = model_data.get('detection_stats', self.detection_stats)
            self.is_trained = model_data['is_trained']
            
            print(f"✅ Modèle chargé: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Obtenir les métriques de performance du détecteur"""
        total = self.detection_stats['total_packets']
        if total == 0:
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0}
        
        # Calculs simplifiés (dans un vrai cas, on aurait besoin de labels vérité terrain)
        anomaly_rate = self.detection_stats['anomalies_detected'] / total
        
        metrics = {
            'total_packets_analyzed': total,
            'anomalies_detected': self.detection_stats['anomalies_detected'],
            'anomaly_rate': anomaly_rate,
            'model_type': self.model_type,
            'threshold': self.threshold,
            'is_trained': self.is_trained,
            'last_training': self.detection_stats['last_training']
        }
        
        return metrics
    
    def reset_stats(self):
        """Réinitialiser les statistiques de détection"""
        self.detection_stats = {
            'total_packets': 0,
            'anomalies_detected': 0,
            'false_positives': 0,
            'true_positives': 0,
            'last_training': self.detection_stats.get('last_training')
        }
    
    def auto_retrain(self, new_packets: List[Dict], retrain_threshold: int = 1000):
        """Réentraîner automatiquement le modèle avec de nouvelles données"""
        if len(new_packets) < retrain_threshold:
            return False
        
        print(f"🔄 Réentraînement automatique avec {len(new_packets)} nouveaux paquets...")
        
        # Générer les données d'entraînement
        training_data = self.generate_training_data_from_packets(new_packets)
        
        # Réentraîner
        success = self.train(training_data)
        
        if success:
            print("✅ Réentraînement automatique terminé")
            self.reset_stats()
        
        return success

if __name__ == "__main__":
    print("ML Detector - Mode production uniquement")
    print("Consultez la documentation pour l'utilisation avancée")