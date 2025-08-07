#!/usr/bin/env python3
"""
Générateur de données de test pour le système d'alertes
Crée des alertes variées pour entraîner les modèles ML
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
import uuid

def generate_test_alerts(db_path="alertes.db", num_alerts=500):
    """Générer des alertes de test variées"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Patterns d'alertes normales
    normal_patterns = [
        {
            'niveau': 'INFO',
            'source': 'system',
            'messages': [
                'Service démarré avec succès',
                'Connexion utilisateur établie',
                'Sauvegarde programmée terminée',
                'Mise à jour système appliquée',
                'Configuration rechargée'
            ],
            'weight': 0.4
        },
        {
            'niveau': 'WARNING',
            'source': 'log:auth.log',
            'messages': [
                'Tentative de connexion avec mot de passe incorrect',
                'Session utilisateur expirée',
                'Accès refusé pour utilisateur inconnu',
                'Limite de tentatives atteinte'
            ],
            'weight': 0.3
        },
        {
            'niveau': 'ERROR',
            'source': 'application',
            'messages': [
                'Erreur de connexion à la base de données',
                'Service temporairement indisponible',
                'Timeout de requête réseau',
                'Erreur de parsing de fichier configuration'
            ],
            'weight': 0.2
        }
    ]
    
    # Patterns d'alertes anormales/suspectes
    anomaly_patterns = [
        {
            'niveau': 'CRITICAL',
            'source': 'security',
            'messages': [
                'Tentative d\'intrusion détectée',
                'Accès root non autorisé',
                'Modification non autorisée de fichier système',
                'Trafic réseau suspect détecté'
            ],
            'weight': 0.05
        },
        {
            'niveau': 'ERROR',
            'source': 'log:system.log',
            'messages': [
                'Corruption de fichier système détectée',
                'Processus système anormal',
                'Utilisation excessive de ressources',
                'Erreur de segmentation critique'
            ],
            'weight': 0.05
        }
    ]
    
    all_patterns = normal_patterns + anomaly_patterns
    
    print(f"Génération de {num_alerts} alertes de test...")
    
    # Générer les alertes
    for i in range(num_alerts):
        # Choisir un pattern selon les poids
        weights = [p['weight'] for p in all_patterns]
        pattern = random.choices(all_patterns, weights=weights)[0]
        
        # Générer timestamp (30 derniers jours)
        base_time = datetime.now() - timedelta(days=30)
        random_offset = timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        timestamp = base_time + random_offset
        
        # Ajouter biais temporel pour les anomalies (plus la nuit et weekend)
        if pattern in anomaly_patterns:
            if random.random() < 0.3:  # 30% des anomalies la nuit
                night_hours = [22, 23, 0, 1, 2, 3, 4, 5]
                timestamp = timestamp.replace(hour=random.choice(night_hours))
            if random.random() < 0.2:  # 20% des anomalies le weekend
                # Ajuster au weekend
                days_to_weekend = (5 - timestamp.weekday()) % 7
                if days_to_weekend < 2:
                    timestamp += timedelta(days=days_to_weekend)
        
        # Générer l'alerte
        alert = {
            'id': f"test_{uuid.uuid4().hex[:12]}",
            'timestamp': timestamp,
            'niveau': pattern['niveau'],
            'source': pattern['source'],
            'message': random.choice(pattern['messages']),
            'details': generate_alert_details(pattern, timestamp),
            'resolu': random.random() < 0.7,  # 70% résolues
        }
        
        # Insérer dans la base
        cursor.execute('''
            INSERT INTO alertes 
            (id, timestamp, niveau, source, message, details, resolu)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert['id'],
            alert['timestamp'],
            alert['niveau'],
            alert['source'],
            alert['message'],
            json.dumps(alert['details']),
            alert['resolu']
        ))
        
        if (i + 1) % 100 == 0:
            print(f"  Généré {i + 1}/{num_alerts} alertes...")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {num_alerts} alertes de test générées dans {db_path}")

def generate_alert_details(pattern, timestamp):
    """Générer des détails réalistes pour une alerte"""
    details = {}
    
    # Ajouter des IPs
    if random.random() < 0.3:
        details['source_ip'] = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
    
    if random.random() < 0.2:
        details['target_ip'] = f"10.0.{random.randint(1,254)}.{random.randint(1,254)}"
    
    # Ajouter des utilisateurs
    if random.random() < 0.4:
        users = ['admin', 'john.doe', 'service_account', 'guest', 'root', 'www-data']
        details['user'] = random.choice(users)
    
    # Ajouter des fichiers
    if random.random() < 0.3:
        files = ['/var/log/auth.log', '/etc/passwd', '/home/user/data.txt', 
                '/tmp/suspicious_file', '/var/www/html/index.php']
        details['file_path'] = random.choice(files)
    
    # Détails spécifiques selon le pattern
    if pattern['source'] == 'system':
        details['pid'] = random.randint(1000, 9999)
        details['memory_usage'] = random.randint(10, 95)
        details['cpu_usage'] = random.randint(5, 98)
    
    elif 'log:' in pattern['source']:
        details['log_line'] = random.randint(1, 10000)
        details['process'] = random.choice(['sshd', 'httpd', 'mysqld', 'systemd'])
    
    elif pattern['source'] == 'security':
        details['attack_type'] = random.choice(['brute_force', 'sql_injection', 'xss', 'port_scan'])
        details['severity_score'] = random.randint(1, 10)
    
    # Ajouter timestamp de détection
    details['detection_timestamp'] = timestamp.isoformat()
    
    return details

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Générer des données de test pour les alertes")
    parser.add_argument("--db", default="alertes.db", help="Base de données SQLite")
    parser.add_argument("--count", type=int, default=500, help="Nombre d'alertes à générer")
    
    args = parser.parse_args()
    
    generate_test_alerts(db_path=args.db, num_alerts=args.count)