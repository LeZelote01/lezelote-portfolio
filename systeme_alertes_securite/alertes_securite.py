#!/usr/bin/env python3
"""
Système d'Alertes Sécurité
Système de monitoring avec alertes en temps réel

Fonctionnalités:
- Monitoring des logs système
- Alertes multi-canaux (Email, Telegram)  
- Dashboard web Flask
- Configuration flexible
- Historique des incidents
- API REST
"""

import os
import sys
import sqlite3
import json
import re
import time
import threading
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Imports pour monitoring
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Imports pour notifications
try:
    import telegram
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  Telegram bot non disponible (pip install python-telegram-bot)")

# Imports pour interface web
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Import du détecteur ML d'anomalies
try:
    from ml_anomaly_detector import MLAnomalyDetector, AnomalyResult
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  Détecteur ML non disponible")

from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)

@dataclass
class Alerte:
    id: str
    timestamp: datetime
    niveau: str  # INFO, WARNING, ERROR, CRITICAL
    source: str
    message: str
    details: Dict[str, Any]
    resolu: bool = False
    canal_notification: List[str] = None

    def to_dict(self):
        """Convertir en dictionnaire pour JSON"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class RegleAlerte:
    id: str
    nom: str
    actif: bool
    source: str  # log_file, system, network, custom
    pattern: str  # regex ou condition
    niveau: str
    description: str
    canaux: List[str]  # email, telegram, webhook
    cooldown: int = 300  # secondes entre alertes similaires

class NotificationManager:
    """Gestionnaire des notifications multi-canaux"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.telegram_bot = None
        
        # Configuration Telegram
        if TELEGRAM_AVAILABLE and config.get('telegram', {}).get('token'):
            try:
                self.telegram_bot = Bot(token=config['telegram']['token'])
                print(f"{Fore.GREEN}✓ Bot Telegram configuré")
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur configuration Telegram: {e}")
    
    def envoyer_email(self, alerte: Alerte) -> bool:
        """Envoyer une alerte par email"""
        try:
            email_config = self.config.get('email', {})
            if not email_config.get('enabled', False):
                return False
            
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username')
            password = email_config.get('password')
            destinataires = email_config.get('destinataires', [])
            
            if not all([username, password, destinataires]):
                print(f"{Fore.YELLOW}⚠️  Configuration email incomplète")
                return False
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(destinataires)
            msg['Subject'] = f"🚨 Alerte Sécurité [{alerte.niveau}] - {alerte.source}"
            
            # Corps du message
            corps = f"""
Alerte Sécurité - {alerte.niveau}

Timestamp: {alerte.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Source: {alerte.source}
Message: {alerte.message}

Détails:
{json.dumps(alerte.details, indent=2, ensure_ascii=False)}

---
Système d'Alertes Sécurité
            """
            
            msg.attach(MIMEText(corps, 'plain', 'utf-8'))
            
            # Envoyer
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            print(f"{Fore.GREEN}✓ Email envoyé pour alerte {alerte.id}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur envoi email: {e}")
            return False
    
    def envoyer_telegram(self, alerte: Alerte) -> bool:
        """Envoyer une alerte via Telegram"""
        try:
            if not self.telegram_bot:
                return False
            
            telegram_config = self.config.get('telegram', {})
            chat_ids = telegram_config.get('chat_ids', [])
            
            if not chat_ids:
                print(f"{Fore.YELLOW}⚠️  Aucun chat_id Telegram configuré")
                return False
            
            # Formater le message
            emoji_map = {
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '🚨'
            }
            
            emoji = emoji_map.get(alerte.niveau, '📢')
            
            message = f"""
{emoji} **Alerte Sécurité [{alerte.niveau}]**

🕐 **Timestamp:** {alerte.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
📡 **Source:** {alerte.source}
💬 **Message:** {alerte.message}

📋 **Détails:**
```json
{json.dumps(alerte.details, indent=2, ensure_ascii=False)}
```
            """
            
            # Envoyer à tous les chats configurés
            for chat_id in chat_ids:
                self.telegram_bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
            
            print(f"{Fore.GREEN}✓ Message Telegram envoyé pour alerte {alerte.id}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur envoi Telegram: {e}")
            return False
    
    def envoyer_webhook(self, alerte: Alerte) -> bool:
        """Envoyer une alerte via webhook"""
        try:
            webhook_config = self.config.get('webhook', {})
            if not webhook_config.get('enabled', False):
                return False
            
            import requests
            
            url = webhook_config.get('url')
            headers = webhook_config.get('headers', {'Content-Type': 'application/json'})
            
            payload = {
                'alerte': alerte.to_dict(),
                'timestamp': datetime.now().isoformat(),
                'source_system': 'alertes_securite'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            print(f"{Fore.GREEN}✓ Webhook envoyé pour alerte {alerte.id}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur envoi webhook: {e}")
            return False

class LogMonitor(FileSystemEventHandler):
    """Moniteur de fichiers de logs"""
    
    def __init__(self, systeme_alertes):
        self.systeme_alertes = systeme_alertes
        super().__init__()
    
    def on_modified(self, event):
        """Appelé quand un fichier est modifié"""
        if not event.is_directory:
            self.analyser_fichier_log(event.src_path)
    
    def analyser_fichier_log(self, chemin_fichier):
        """Analyser un fichier de log pour des patterns d'alerte"""
        try:
            # Lire seulement les nouvelles lignes
            with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
                # Aller à la fin du fichier
                f.seek(0, 2)
                taille_fichier = f.tell()
                
                # Lire les dernières lignes (max 1KB)
                debut = max(0, taille_fichier - 1024)
                f.seek(debut)
                lignes = f.readlines()
                
                # Analyser chaque ligne récente
                for ligne in lignes[-10:]:  # 10 dernières lignes
                    self.analyser_ligne_log(ligne.strip(), chemin_fichier)
                    
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lecture log {chemin_fichier}: {e}")
    
    def analyser_ligne_log(self, ligne: str, source: str):
        """Analyser une ligne de log contre les règles"""
        for regle in self.systeme_alertes.regles_actives():
            if regle.source == 'log_file':
                try:
                    if re.search(regle.pattern, ligne, re.IGNORECASE):
                        # Pattern trouvé, créer une alerte
                        alerte = Alerte(
                            id=f"log_{int(time.time())}_{hash(ligne) % 10000}",
                            timestamp=datetime.now(),
                            niveau=regle.niveau,
                            source=f"log:{Path(source).name}",
                            message=f"Pattern détecté: {regle.nom}",
                            details={
                                'ligne_log': ligne,
                                'fichier': source,
                                'pattern': regle.pattern,
                                'regle_id': regle.id
                            }
                        )
                        
                        self.systeme_alertes.traiter_alerte(alerte, regle)
                        
                except re.error as e:
                    print(f"{Fore.RED}❌ Erreur regex dans règle {regle.id}: {e}")

class SystemMonitor:
    """Moniteur des ressources système"""
    
    def __init__(self, systeme_alertes):
        self.systeme_alertes = systeme_alertes
        self.running = False
        self.thread = None
    
    def start(self):
        """Démarrer le monitoring système"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"{Fore.GREEN}✓ Monitoring système démarré")
    
    def stop(self):
        """Arrêter le monitoring système"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _monitor_loop(self):
        """Boucle principale de monitoring"""
        while self.running:
            try:
                self.verifier_ressources()
                time.sleep(30)  # Vérification toutes les 30 secondes
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur monitoring système: {e}")
                time.sleep(60)
    
    def verifier_ressources(self):
        """Vérifier les ressources système"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            self._creer_alerte_systeme(
                "CPU_HIGH",
                "WARNING",
                f"Utilisation CPU élevée: {cpu_percent:.1f}%",
                {'cpu_percent': cpu_percent}
            )
        
        # Mémoire
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            self._creer_alerte_systeme(
                "MEMORY_HIGH",
                "WARNING", 
                f"Utilisation mémoire élevée: {memory.percent:.1f}%",
                {
                    'memory_percent': memory.percent,
                    'memory_available': memory.available,
                    'memory_total': memory.total
                }
            )
        
        # Disque
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:
                    self._creer_alerte_systeme(
                        "DISK_HIGH",
                        "ERROR",
                        f"Espace disque faible: {partition.mountpoint} ({usage.percent:.1f}%)",
                        {
                            'partition': partition.mountpoint,
                            'disk_percent': usage.percent,
                            'disk_free': usage.free,
                            'disk_total': usage.total
                        }
                    )
            except PermissionError:
                continue
    
    def _creer_alerte_systeme(self, type_alerte: str, niveau: str, message: str, details: dict):
        """Créer une alerte système"""
        alerte = Alerte(
            id=f"sys_{type_alerte}_{int(time.time())}",
            timestamp=datetime.now(),
            niveau=niveau,
            source="system",
            message=message,
            details=details
        )
        
        # Chercher une règle correspondante
        for regle in self.systeme_alertes.regles_actives():
            if regle.source == 'system' and type_alerte in regle.pattern:
                self.systeme_alertes.traiter_alerte(alerte, regle)
                break

class SystemeAlertes:
    """Système principal d'alertes sécurité"""
    
    def __init__(self, db_path="alertes.db", config_path="config.json"):
        self.db_path = db_path
        self.config_path = config_path
        self.config = self.charger_configuration()
        
        # Initialiser les composants
        self.notification_manager = NotificationManager(self.config)
        self.log_monitor = LogMonitor(self)
        self.system_monitor = SystemMonitor(self)
        
        # Détecteur ML d'anomalies
        self.ml_detector = None
        if ML_AVAILABLE and self.config.get('machine_learning', {}).get('enabled', True):
            self.ml_detector = MLAnomalyDetector(db_path=db_path)
            # Tenter de charger les modèles existants
            if self.ml_detector.load_models():
                print(f"{Fore.GREEN}🤖 Modèles ML chargés avec succès")
            else:
                print(f"{Fore.YELLOW}🤖 Aucun modèle ML pré-entraîné trouvé")
            print(f"{Fore.CYAN}🤖 Détecteur ML d'anomalies initialisé")
        
        # Cache des alertes récentes (pour cooldown)
        self.alertes_recentes = {}
        
        # Observer pour les fichiers de logs
        self.observer = Observer()
        
        # Initialiser la base de données
        self.init_database()
        
        print(f"{Fore.GREEN}🚨 Système d'Alertes Sécurité initialisé")
    
    def charger_configuration(self) -> Dict[str, Any]:
        """Charger la configuration depuis le fichier JSON"""
        config_par_defaut = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "destinataires": []
            },
            "telegram": {
                "enabled": False,
                "token": "",
                "chat_ids": []
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "headers": {}
            },
            "monitoring": {
                "log_directories": ["/var/log", "./logs"],
                "system_monitoring": True,
                "check_interval": 30
            },
            "regles": [
                {
                    "id": "failed_login",
                    "nom": "Tentative de connexion échouée",
                    "actif": True,
                    "source": "log_file",
                    "pattern": r"(failed|failure|authentication failed|login failed)",
                    "niveau": "WARNING",
                    "description": "Détecte les tentatives de connexion échouées",
                    "canaux": ["email"],
                    "cooldown": 300
                },
                {
                    "id": "cpu_high",
                    "nom": "CPU élevé",
                    "actif": True,
                    "source": "system",
                    "pattern": "CPU_HIGH",
                    "niveau": "WARNING",
                    "description": "CPU utilisation > 90%",
                    "canaux": ["telegram"],
                    "cooldown": 600
                },
                {
                    "id": "disk_full",
                    "nom": "Disque plein",
                    "actif": True,
                    "source": "system", 
                    "pattern": "DISK_HIGH",
                    "niveau": "ERROR",
                    "description": "Espace disque < 10%",
                    "canaux": ["email", "telegram"],
                    "cooldown": 1800
                }
            ]
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merger avec la config par défaut
                    return {**config_par_defaut, **config}
            else:
                # Créer le fichier de config par défaut
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_par_defaut, f, indent=2, ensure_ascii=False)
                print(f"{Fore.YELLOW}⚠️  Configuration par défaut créée: {self.config_path}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur chargement configuration: {e}")
        
        return config_par_defaut
    
    def init_database(self):
        """Initialiser la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertes (
                id TEXT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                niveau TEXT NOT NULL,
                source TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                resolu BOOLEAN DEFAULT FALSE,
                canal_notification TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des règles d'alerte
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regles (
                id TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                actif BOOLEAN DEFAULT TRUE,
                source TEXT NOT NULL,
                pattern TEXT NOT NULL,
                niveau TEXT NOT NULL,
                description TEXT,
                canaux TEXT,
                cooldown INTEGER DEFAULT 300,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des statistiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                date DATE PRIMARY KEY,
                total_alertes INTEGER DEFAULT 0,
                alertes_critiques INTEGER DEFAULT 0,
                alertes_erreurs INTEGER DEFAULT 0,
                alertes_warnings INTEGER DEFAULT 0,
                alertes_info INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Synchroniser les règles depuis la configuration
        self.synchroniser_regles()
    
    def synchroniser_regles(self):
        """Synchroniser les règles depuis la configuration vers la base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for regle_config in self.config.get('regles', []):
            cursor.execute('''
                INSERT OR REPLACE INTO regles 
                (id, nom, actif, source, pattern, niveau, description, canaux, cooldown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                regle_config['id'],
                regle_config['nom'],
                regle_config['actif'],
                regle_config['source'],
                regle_config['pattern'],
                regle_config['niveau'],
                regle_config['description'],
                json.dumps(regle_config['canaux']),
                regle_config['cooldown']
            ))
        
        conn.commit()
        conn.close()
    
    def regles_actives(self) -> List[RegleAlerte]:
        """Récupérer toutes les règles actives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM regles WHERE actif = TRUE')
        rows = cursor.fetchall()
        conn.close()
        
        regles = []
        for row in rows:
            regles.append(RegleAlerte(
                id=row[0],
                nom=row[1],
                actif=bool(row[2]),
                source=row[3],
                pattern=row[4],
                niveau=row[5],
                description=row[6] or "",
                canaux=json.loads(row[7]) if row[7] else [],
                cooldown=row[8] or 300
            ))
        
        return regles
    
    def traiter_alerte(self, alerte: Alerte, regle: RegleAlerte):
        """Traiter une nouvelle alerte"""
        # Vérifier le cooldown
        cooldown_key = f"{regle.id}_{alerte.source}"
        maintenant = time.time()
        
        if cooldown_key in self.alertes_recentes:
            derniere_alerte = self.alertes_recentes[cooldown_key]
            if maintenant - derniere_alerte < regle.cooldown:
                return  # Cooldown actif, ignorer
        
        # Analyse ML pour détection d'anomalies
        ml_result = None
        if self.ml_detector and self.ml_detector.models_trained:
            try:
                alert_data = {
                    'id': alerte.id,
                    'timestamp': alerte.timestamp.isoformat(),
                    'niveau': alerte.niveau,
                    'source': alerte.source,
                    'message': alerte.message,
                    'details': alerte.details
                }
                ml_result = self.ml_detector.detect_anomaly(alert_data)
                
                # Si c'est une anomalie, augmenter la priorité
                if ml_result.is_anomaly:
                    print(f"{Fore.MAGENTA}🤖 ML: Anomalie détectée (confiance: {ml_result.confidence_score:.3f})")
                    # Ajouter les informations ML aux détails
                    alerte.details['ml_anomaly'] = {
                        'is_anomaly': True,
                        'confidence': ml_result.confidence_score,
                        'type': ml_result.anomaly_type,
                        'explanation': ml_result.explanation
                    }
                else:
                    alerte.details['ml_anomaly'] = {
                        'is_anomaly': False,
                        'confidence': ml_result.confidence_score
                    }
                    
                    # Si ML dit que ce n'est pas une anomalie ET confiance élevée, 
                    # on peut réduire les notifications (réduction faux positifs)
                    if ml_result.confidence_score > 0.8 and alerte.niveau in ['WARNING', 'INFO']:
                        print(f"{Fore.GREEN}🤖 ML: Probable faux positif ignoré")
                        return  # Ignorer cette alerte
                    
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur analyse ML: {e}")
        
        # Enregistrer l'alerte
        self.enregistrer_alerte(alerte)
        
        # Marquer le cooldown
        self.alertes_recentes[cooldown_key] = maintenant
        
        # Envoyer les notifications
        for canal in regle.canaux:
            if canal == 'email':
                self.notification_manager.envoyer_email(alerte)
            elif canal == 'telegram':
                self.notification_manager.envoyer_telegram(alerte)
            elif canal == 'webhook':
                self.notification_manager.envoyer_webhook(alerte)
        
        print(f"{Fore.CYAN}🚨 Alerte traitée: {alerte.niveau} - {alerte.message}")
    
    def enregistrer_alerte(self, alerte: Alerte):
        """Enregistrer une alerte dans la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alertes 
            (id, timestamp, niveau, source, message, details, canal_notification)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alerte.id,
            alerte.timestamp,
            alerte.niveau,
            alerte.source,
            alerte.message,
            json.dumps(alerte.details),
            json.dumps(alerte.canal_notification) if alerte.canal_notification else None
        ))
        
        # Mettre à jour les statistiques
        date_aujourd_hui = datetime.now().date()
        cursor.execute('''
            INSERT OR IGNORE INTO stats (date, total_alertes) VALUES (?, 0)
        ''', (date_aujourd_hui,))
        
        # Mapping correct des niveaux vers les colonnes
        niveau_mapping = {
            'CRITICAL': 'alertes_critiques',
            'ERROR': 'alertes_erreurs', 
            'WARNING': 'alertes_warnings',
            'INFO': 'alertes_info'
        }
        
        niveau_col = niveau_mapping.get(alerte.niveau, 'alertes_info')
        cursor.execute(f'''
            UPDATE stats 
            SET total_alertes = total_alertes + 1,
                {niveau_col} = {niveau_col} + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE date = ?
        ''', (date_aujourd_hui,))
        
        conn.commit()
        conn.close()
    
    def lister_alertes(self, limite=50, niveau=None, resolu=None) -> List[Alerte]:
        """Lister les alertes avec filtres"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM alertes WHERE 1=1"
        params = []
        
        if niveau:
            query += " AND niveau = ?"
            params.append(niveau)
        
        if resolu is not None:
            query += " AND resolu = ?"
            params.append(resolu)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        alertes = []
        for row in rows:
            alertes.append(Alerte(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                niveau=row[2],
                source=row[3],
                message=row[4],
                details=json.loads(row[5]) if row[5] else {},
                resolu=bool(row[6]),
                canal_notification=json.loads(row[7]) if row[7] else None
            ))
        
        return alertes
    
    def marquer_resolu(self, alerte_id: str) -> bool:
        """Marquer une alerte comme résolue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE alertes SET resolu = TRUE WHERE id = ?', (alerte_id,))
        conn.commit()
        
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def obtenir_statistiques(self) -> Dict[str, Any]:
        """Obtenir les statistiques des alertes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Stats globales
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN niveau = 'CRITICAL' THEN 1 ELSE 0 END) as critiques,
                SUM(CASE WHEN niveau = 'ERROR' THEN 1 ELSE 0 END) as erreurs,
                SUM(CASE WHEN niveau = 'WARNING' THEN 1 ELSE 0 END) as warnings,
                SUM(CASE WHEN niveau = 'INFO' THEN 1 ELSE 0 END) as info,
                SUM(CASE WHEN resolu = FALSE THEN 1 ELSE 0 END) as non_resolues
            FROM alertes
        ''')
        
        stats_globales = cursor.fetchone()
        
        # Stats par jour (7 derniers jours)
        cursor.execute('''
            SELECT date, total_alertes, alertes_critiques, alertes_erreurs, alertes_warnings, alertes_info
            FROM stats 
            WHERE date >= date('now', '-7 days')
            ORDER BY date DESC
        ''')
        
        stats_journalieres = cursor.fetchall()
        
        # Top sources
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM alertes
            GROUP BY source
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        top_sources = cursor.fetchall()
        
        conn.close()
        
        return {
            'globales': {
                'total': stats_globales[0] or 0,
                'critiques': stats_globales[1] or 0,
                'erreurs': stats_globales[2] or 0,
                'warnings': stats_globales[3] or 0,
                'info': stats_globales[4] or 0,
                'non_resolues': stats_globales[5] or 0
            },
            'journalieres': [
                {
                    'date': row[0],
                    'total': row[1] or 0,
                    'critiques': row[2] or 0,
                    'erreurs': row[3] or 0,
                    'warnings': row[4] or 0,
                    'info': row[5] or 0
                }
                for row in stats_journalieres
            ],
            'top_sources': [
                {'source': row[0], 'count': row[1]}
                for row in top_sources
            ]
        }
    
    def demarrer_monitoring(self):
        """Démarrer tous les services de monitoring"""
        print(f"{Fore.CYAN}🚀 Démarrage du monitoring...")
        
        # Monitoring système
        if self.config.get('monitoring', {}).get('system_monitoring', True):
            self.system_monitor.start()
        
        # Monitoring des logs
        log_directories = self.config.get('monitoring', {}).get('log_directories', [])
        for log_dir in log_directories:
            if os.path.exists(log_dir):
                self.observer.schedule(self.log_monitor, log_dir, recursive=True)
                print(f"{Fore.GREEN}✓ Monitoring ajouté: {log_dir}")
        
        if log_directories:
            self.observer.start()
            print(f"{Fore.GREEN}✓ Observer de logs démarré")
        
        print(f"{Fore.GREEN}🚨 Monitoring actif")
    
    def arreter_monitoring(self):
        """Arrêter tous les services de monitoring"""
        print(f"{Fore.YELLOW}🛑 Arrêt du monitoring...")
        
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        self.system_monitor.stop()
        
        print(f"{Fore.YELLOW}🛑 Monitoring arrêté")

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Système d'Alertes Sécurité")
    parser.add_argument("--config", default="config.json", help="Fichier de configuration")
    parser.add_argument("--db", default="alertes.db", help="Base de données SQLite")
    parser.add_argument("--daemon", action="store_true", help="Mode daemon")
    parser.add_argument("--web", action="store_true", help="Lancer l'interface web")
    parser.add_argument("--port", type=int, default=5000, help="Port pour l'interface web")
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Lister les alertes')
    list_parser.add_argument('--niveau', choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    list_parser.add_argument('--non-resolues', action='store_true')
    list_parser.add_argument('--limite', type=int, default=20)
    
    # Commande stats
    subparsers.add_parser('stats', help='Afficher les statistiques')
    
    # Commande resolve
    resolve_parser = subparsers.add_parser('resolve', help='Marquer une alerte comme résolue')
    resolve_parser.add_argument('id', help='ID de l\'alerte')
    
    # Commande test
    test_parser = subparsers.add_parser('test', help='Tester les notifications')
    test_parser.add_argument('--canal', choices=['email', 'telegram', 'webhook'])
    
    # Commandes ML
    ml_parser = subparsers.add_parser('ml', help='Commandes Machine Learning')
    ml_subparsers = ml_parser.add_subparsers(dest='ml_command')
    
    # ML train
    ml_train_parser = ml_subparsers.add_parser('train', help='Entraîner les modèles ML')
    ml_train_parser.add_argument('--days', type=int, default=30, help='Jours de données pour l\'entraînement')
    
    # ML analyze
    ml_analyze_parser = ml_subparsers.add_parser('analyze', help='Analyser les alertes avec ML')
    ml_analyze_parser.add_argument('--days', type=int, default=7, help='Jours d\'alertes à analyser')
    
    # ML report
    ml_subparsers.add_parser('report', help='Rapport d\'analyse ML')
    
    # ML status
    ml_subparsers.add_parser('status', help='Statut des modèles ML')
    
    args = parser.parse_args()
    
    print(f"{Fore.BLUE}🚨 SYSTÈME D'ALERTES SÉCURITÉ")
    print("=" * 40)
    
    # Initialiser le système
    systeme = SystemeAlertes(db_path=args.db, config_path=args.config)
    
    if args.command == 'list':
        # Lister les alertes
        alertes = systeme.lister_alertes(
            limite=args.limite,
            niveau=args.niveau,
            resolu=False if args.non_resolues else None
        )
        
        if alertes:
            table_data = []
            for alerte in alertes:
                table_data.append([
                    alerte.id[:12] + "...",
                    alerte.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    alerte.niveau,
                    alerte.source,
                    alerte.message[:50] + "..." if len(alerte.message) > 50 else alerte.message,
                    "✓" if alerte.resolu else "❌"
                ])
            
            print(f"\n{Fore.CYAN}📋 ALERTES ({len(alertes)} trouvées)")
            print(tabulate(table_data, 
                         headers=["ID", "Timestamp", "Niveau", "Source", "Message", "Résolu"],
                         tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}⚠️  Aucune alerte trouvée")
    
    elif args.command == 'stats':
        # Afficher les statistiques
        stats = systeme.obtenir_statistiques()
        
        print(f"\n{Fore.CYAN}📊 STATISTIQUES GLOBALES")
        stats_table = [
            ["Total", stats['globales']['total']],
            ["Critiques", stats['globales']['critiques']],
            ["Erreurs", stats['globales']['erreurs']],
            ["Warnings", stats['globales']['warnings']],
            ["Info", stats['globales']['info']],
            ["Non résolues", stats['globales']['non_resolues']]
        ]
        print(tabulate(stats_table, headers=["Type", "Nombre"], tablefmt="grid"))
        
        if stats['top_sources']:
            print(f"\n{Fore.CYAN}📡 TOP SOURCES")
            print(tabulate(stats['top_sources'], headers=["Source", "Alertes"], tablefmt="grid"))
    
    elif args.command == 'resolve':
        # Marquer comme résolu
        if systeme.marquer_resolu(args.id):
            print(f"{Fore.GREEN}✓ Alerte {args.id} marquée comme résolue")
        else:
            print(f"{Fore.RED}❌ Alerte {args.id} introuvable")
    
    elif args.command == 'test':
        # Tester les notifications
        alerte_test = Alerte(
            id=f"test_{int(time.time())}",
            timestamp=datetime.now(),
            niveau="INFO",
            source="test",
            message="Test de notification du système d'alertes",
            details={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        if args.canal == 'email' or not args.canal:
            systeme.notification_manager.envoyer_email(alerte_test)
        
        if args.canal == 'telegram' or not args.canal:
            systeme.notification_manager.envoyer_telegram(alerte_test)
        
        if args.canal == 'webhook' or not args.canal:
            systeme.notification_manager.envoyer_webhook(alerte_test)
    
    elif args.command == 'ml':
        # Commandes ML
        if not systeme.ml_detector:
            print(f"{Fore.RED}❌ Détecteur ML non disponible")
            return
        
        if args.ml_command == 'train':
            print(f"{Fore.CYAN}🤖 Entraînement des modèles ML...")
            try:
                alerts_data = systeme.ml_detector.load_training_data(days_back=args.days)
                if len(alerts_data) < 100:
                    print(f"{Fore.RED}❌ Pas assez de données (minimum 100, trouvé {len(alerts_data)})")
                    return
                
                metrics = systeme.ml_detector.train_models(alerts_data)
                print(f"{Fore.GREEN}✅ Entraînement terminé avec succès")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur lors de l'entraînement: {e}")
        
        elif args.ml_command == 'analyze':
            print(f"{Fore.CYAN}🔍 Analyse ML des alertes récentes...")
            alerts_data = systeme.ml_detector.load_training_data(days_back=args.days)
            
            if not systeme.ml_detector.models_trained:
                print(f"{Fore.RED}❌ Modèles non entraînés. Utilisez 'ml train' d'abord")
                return
            
            results = systeme.ml_detector.analyze_batch(alerts_data)
            
            # Afficher les anomalies
            anomalies = [r for r in results if r.is_anomaly]
            if anomalies:
                print(f"\n{Fore.RED}🚨 ANOMALIES DÉTECTÉES ({len(anomalies)}):")
                table_data = []
                for anomaly in anomalies[:10]:  # Limiter à 10
                    table_data.append([
                        anomaly.anomaly_type,
                        f"{anomaly.confidence_score:.3f}",
                        anomaly.explanation[:60] + "..." if len(anomaly.explanation) > 60 else anomaly.explanation
                    ])
                
                print(tabulate(table_data, 
                             headers=["Type", "Confiance", "Explication"],
                             tablefmt="grid"))
            else:
                print(f"{Fore.GREEN}✅ Aucune anomalie détectée")
        
        elif args.ml_command == 'report':
            print(f"{Fore.CYAN}📊 Génération du rapport ML...")
            report = systeme.ml_detector.generate_analytics_report()
            
            if 'error' not in report:
                print(f"\n{Fore.GREEN}📈 RAPPORT D'ANALYSE ML")
                print("=" * 40)
                print(f"Période: {report['period']}")
                print(f"Alertes analysées: {report['total_alerts_analyzed']}")
                print(f"Anomalies détectées: {report['anomalies_detected']}")
                print(f"Taux d'anomalies: {report['anomaly_rate']:.1%}")
                print(f"Confiance moyenne: {report['avg_confidence']:.3f}")
                
                if report['anomaly_types']:
                    print(f"\n{Fore.CYAN}Types d'anomalies:")
                    for anomaly_type, count in report['anomaly_types'].items():
                        print(f"  • {anomaly_type}: {count}")
                
                print(f"\n{Fore.YELLOW}Recommandations:")
                for rec in report['recommendations']:
                    print(f"  {rec}")
            else:
                print(f"{Fore.RED}❌ {report['error']}")
        
        elif args.ml_command == 'status':
            status = systeme.ml_detector.get_model_status()
            print(f"\n{Fore.CYAN}📊 STATUT DES MODÈLES ML")
            print("=" * 35)
            print(f"Modèles entraînés: {'✅ Oui' if status['models_trained'] else '❌ Non'}")
            print(f"Taille données entraînement: {status['training_data_size']}")
            print(f"Dernier entraînement: {status['last_training'] or 'Jamais'}")
            print(f"Dossier modèles: {status['models_dir']}")
            
            if status['metrics']:
                print(f"\n{Fore.GREEN}Métriques:")
                for model_name, metrics in status['metrics'].items():
                    if hasattr(metrics, 'samples_count'):
                        print(f"  • {model_name}: {metrics.samples_count} échantillons")
                    else:
                        print(f"  • {model_name}: Métrique disponible")
    
    elif args.web:
        # Lancer l'interface web (voir webapp.py)
        print(f"{Fore.GREEN}🌐 Interface web disponible sur: webapp.py")
    
    elif args.daemon:
        # Mode daemon
        print(f"{Fore.GREEN}🔄 Mode daemon activé")
        systeme.demarrer_monitoring()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Arrêt demandé...")
            systeme.arreter_monitoring()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()