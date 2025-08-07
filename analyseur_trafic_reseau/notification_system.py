#!/usr/bin/env python3
"""
Système de Notifications - Analyseur de Trafic Réseau
Support Email, Slack, Webhooks et templates personnalisables

Fonctionnalités:
- Notifications Email (SMTP)
- Notifications Slack (Webhooks)
- Notifications génériques (Webhooks)
- Templates de messages personnalisables
- Seuils d'alerte configurables
- Rate limiting et cooldown
- Historique des notifications
"""

import smtplib
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from colorama import Fore, Style
import logging
import os
from pathlib import Path
import threading
from queue import Queue
import jinja2

# Import conditionnel pour email
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print(f"{Fore.YELLOW}⚠ Module email non disponible - notifications email désactivées")

class NotificationSystem:
    """Système de notifications avancé pour l'analyseur de trafic"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.notification_queue = Queue()
        self.notification_history = []
        self.rate_limits = {}
        self.logger = self._setup_logger()
        self.templates = self._load_templates()
        
        # Démarrer le worker de notifications en arrière-plan
        self.worker_thread = threading.Thread(target=self._notification_worker, daemon=True)
        self.worker_thread.start()
        
        print(f"{Fore.GREEN}✓ Système de Notifications initialisé")
    
    def _setup_logger(self):
        """Configuration du logger pour les notifications"""
        logger = logging.getLogger('NotificationSystem')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_config(self) -> Dict:
        """Charger la configuration des notifications"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": [],
                "use_tls": True
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#alerts",
                "username": "TrafficAnalyzer",
                "icon_emoji": ":warning:"
            },
            "webhooks": {
                "enabled": False,
                "endpoints": []
            },
            "rate_limiting": {
                "enabled": True,
                "max_notifications_per_hour": 60,
                "cooldown_seconds": 300
            },
            "alert_thresholds": {
                "anomaly_count": 5,
                "packet_rate": 1000,
                "suspicious_ips": 10,
                "port_scan_threshold": 20
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merger avec la config par défaut
                    default_config.update(loaded_config)
                    return default_config
            else:
                # Créer le fichier de config par défaut
                self._save_config(default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la config: {e}")
            return default_config
    
    def _save_config(self, config: Dict):
        """Sauvegarder la configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
    
    def _load_templates(self) -> Dict:
        """Charger les templates de messages"""
        return {
            "anomaly_detected": {
                "subject": "🚨 Anomalie détectée - Analyseur de Trafic",
                "email_template": """
                <h2>🚨 Anomalie de Trafic Réseau Détectée</h2>
                
                <p><strong>Type d'anomalie:</strong> {{ anomaly_type }}</p>
                <p><strong>Heure de détection:</strong> {{ timestamp }}</p>
                <p><strong>IP Source:</strong> {{ source_ip }}</p>
                <p><strong>Détails:</strong> {{ details }}</p>
                
                <h3>📊 Statistiques du moment:</h3>
                <ul>
                    <li>Total paquets: {{ total_packets }}</li>
                    <li>Paquets/seconde: {{ packets_per_second }}</li>
                    <li>Anomalies détectées: {{ anomaly_count }}</li>
                </ul>
                
                <p><em>Message automatique de l'Analyseur de Trafic Réseau</em></p>
                """,
                "slack_template": {
                    "text": "🚨 Anomalie de trafic réseau détectée",
                    "attachments": [
                        {
                            "color": "danger",
                            "fields": [
                                {"title": "Type", "value": "{{ anomaly_type }}", "short": True},
                                {"title": "IP Source", "value": "{{ source_ip }}", "short": True},
                                {"title": "Heure", "value": "{{ timestamp }}", "short": True},
                                {"title": "Détails", "value": "{{ details }}", "short": False}
                            ]
                        }
                    ]
                }
            },
            "high_traffic": {
                "subject": "⚡ Trafic élevé détecté - Analyseur de Trafic",
                "email_template": """
                <h2>⚡ Trafic Réseau Élevé</h2>
                
                <p><strong>Seuil dépassé:</strong> {{ threshold }} paquets/seconde</p>
                <p><strong>Trafic actuel:</strong> {{ current_rate }} paquets/seconde</p>
                <p><strong>Heure de détection:</strong> {{ timestamp }}</p>
                
                <h3>📈 Statistiques détaillées:</h3>
                <ul>
                    <li>Top protocoles: {{ top_protocols }}</li>
                    <li>Top IPs: {{ top_ips }}</li>
                    <li>Durée de l'événement: {{ event_duration }}</li>
                </ul>
                """,
                "slack_template": {
                    "text": "⚡ Trafic réseau élevé détecté",
                    "attachments": [
                        {
                            "color": "warning",
                            "fields": [
                                {"title": "Seuil", "value": "{{ threshold }} pps", "short": True},
                                {"title": "Actuel", "value": "{{ current_rate }} pps", "short": True},
                                {"title": "Heure", "value": "{{ timestamp }}", "short": False}
                            ]
                        }
                    ]
                }
            },
            "system_status": {
                "subject": "📊 Rapport de statut - Analyseur de Trafic",
                "email_template": """
                <h2>📊 Rapport de Statut Système</h2>
                
                <p><strong>Période:</strong> {{ period }}</p>
                <p><strong>Status:</strong> {{ system_status }}</p>
                
                <h3>📈 Statistiques de la période:</h3>
                <ul>
                    <li>Total paquets analysés: {{ total_packets }}</li>
                    <li>Anomalies détectées: {{ anomalies_count }}</li>
                    <li>Taux de détection: {{ detection_rate }}%</li>
                    <li>Performance moyenne: {{ avg_performance }} pps</li>
                </ul>
                
                <h3>🎯 Top événements:</h3>
                {{ top_events }}
                """,
                "slack_template": {
                    "text": "📊 Rapport de statut système",
                    "attachments": [
                        {
                            "color": "good",
                            "fields": [
                                {"title": "Période", "value": "{{ period }}", "short": True},
                                {"title": "Status", "value": "{{ system_status }}", "short": True},
                                {"title": "Paquets", "value": "{{ total_packets }}", "short": True},
                                {"title": "Anomalies", "value": "{{ anomalies_count }}", "short": True}
                            ]
                        }
                    ]
                }
            }
        }
    
    def _check_rate_limit(self, notification_type: str) -> bool:
        """Vérifier les limites de taux pour éviter le spam"""
        if not self.config["rate_limiting"]["enabled"]:
            return True
        
        current_time = datetime.now()
        max_per_hour = self.config["rate_limiting"]["max_notifications_per_hour"]
        cooldown = self.config["rate_limiting"]["cooldown_seconds"]
        
        # Vérifier le cooldown global
        if notification_type in self.rate_limits:
            last_sent = self.rate_limits[notification_type]["last_sent"]
            if (current_time - last_sent).total_seconds() < cooldown:
                return False
        
        # Vérifier le nombre d'envois par heure
        hour_ago = current_time - timedelta(hours=1)
        recent_notifications = [
            n for n in self.notification_history
            if n["timestamp"] > hour_ago and n["type"] == notification_type
        ]
        
        if len(recent_notifications) >= max_per_hour:
            return False
        
        return True
    
    def _update_rate_limit(self, notification_type: str):
        """Mettre à jour les informations de rate limiting"""
        current_time = datetime.now()
        self.rate_limits[notification_type] = {
            "last_sent": current_time,
            "count": self.rate_limits.get(notification_type, {}).get("count", 0) + 1
        }
    
    def _render_template(self, template_name: str, template_type: str, data: Dict) -> str:
        """Rendre un template avec les données fournies"""
        try:
            if template_name not in self.templates:
                return f"Template '{template_name}' non trouvé"
            
            template_content = self.templates[template_name].get(template_type, "")
            if not template_content:
                return f"Type de template '{template_type}' non trouvé"
            
            # Utiliser Jinja2 pour le rendu si c'est une string
            if isinstance(template_content, str):
                template = jinja2.Template(template_content)
                return template.render(**data)
            
            # Pour les templates complexes (Slack), traiter récursivement
            if isinstance(template_content, dict):
                rendered = {}
                for key, value in template_content.items():
                    if isinstance(value, str):
                        template = jinja2.Template(value)
                        rendered[key] = template.render(**data)
                    elif isinstance(value, list):
                        rendered[key] = []
                        for item in value:
                            if isinstance(item, dict):
                                rendered_item = {}
                                for k, v in item.items():
                                    if isinstance(v, str):
                                        template = jinja2.Template(v)
                                        rendered_item[k] = template.render(**data)
                                    elif isinstance(v, list):
                                        rendered_item[k] = []
                                        for sub_item in v:
                                            if isinstance(sub_item, dict):
                                                rendered_sub_item = {}
                                                for sk, sv in sub_item.items():
                                                    if isinstance(sv, str):
                                                        template = jinja2.Template(sv)
                                                        rendered_sub_item[sk] = template.render(**data)
                                                    else:
                                                        rendered_sub_item[sk] = sv
                                                rendered_item[k].append(rendered_sub_item)
                                            else:
                                                rendered_item[k].append(sub_item)
                                    else:
                                        rendered_item[k] = v
                                rendered[key].append(rendered_item)
                            else:
                                rendered[key].append(item)
                    else:
                        rendered[key] = value
                return rendered
            
            return str(template_content)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du rendu du template: {e}")
            return f"Erreur de template: {e}"
    
    def send_email_notification(self, subject: str, body: str, to_addresses: List[str] = None) -> bool:
        """Envoyer une notification par email"""
        try:
            if not EMAIL_AVAILABLE:
                self.logger.warning("Module email non disponible")
                return False
                
            if not self.config["email"]["enabled"]:
                return False
            
            config = self.config["email"]
            to_addresses = to_addresses or config["to_addresses"]
            
            if not to_addresses:
                self.logger.warning("Aucune adresse email de destination configurée")
                return False
            
            # Créer le message
            msg = MimeMultipart('alternative')
            msg['From'] = config["from_address"]
            msg['To'] = ", ".join(to_addresses)
            msg['Subject'] = subject
            
            # Ajouter le corps du message (HTML)
            html_part = MimeText(body, 'html')
            msg.attach(html_part)
            
            # Envoyer
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            if config["use_tls"]:
                server.starttls()
            
            server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email envoyé à {len(to_addresses)} destinataires")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi d'email: {e}")
            return False
    
    def send_slack_notification(self, message: Dict) -> bool:
        """Envoyer une notification Slack"""
        try:
            if not self.config["slack"]["enabled"]:
                return False
            
            webhook_url = self.config["slack"]["webhook_url"]
            if not webhook_url:
                self.logger.warning("URL webhook Slack non configurée")
                return False
            
            # Ajouter les paramètres par défaut
            payload = {
                "channel": self.config["slack"]["channel"],
                "username": self.config["slack"]["username"],
                "icon_emoji": self.config["slack"]["icon_emoji"]
            }
            
            # Merger avec le message fourni
            payload.update(message)
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Notification Slack envoyée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi Slack: {e}")
            return False
    
    def send_webhook_notification(self, endpoint: str, payload: Dict) -> bool:
        """Envoyer une notification via webhook générique"""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Webhook envoyé à {endpoint}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi webhook: {e}")
            return False
    
    def _notification_worker(self):
        """Worker en arrière-plan pour traiter les notifications"""
        while True:
            try:
                notification = self.notification_queue.get(timeout=1)
                self._process_notification(notification)
                self.notification_queue.task_done()
            except:
                time.sleep(1)
    
    def _process_notification(self, notification: Dict):
        """Traiter une notification individuelle"""
        try:
            notification_type = notification["type"]
            template_name = notification["template"]
            data = notification["data"]
            
            # Vérifier les limites de taux
            if not self._check_rate_limit(notification_type):
                self.logger.info(f"Notification {notification_type} bloquée par rate limiting")
                return
            
            success_count = 0
            
            # Email
            if self.config["email"]["enabled"]:
                subject = self._render_template(template_name, "subject", data)
                body = self._render_template(template_name, "email_template", data)
                if self.send_email_notification(subject, body):
                    success_count += 1
            
            # Slack
            if self.config["slack"]["enabled"]:
                slack_message = self._render_template(template_name, "slack_template", data)
                if isinstance(slack_message, dict):
                    if self.send_slack_notification(slack_message):
                        success_count += 1
            
            # Webhooks
            if self.config["webhooks"]["enabled"]:
                for endpoint in self.config["webhooks"]["endpoints"]:
                    webhook_payload = {
                        "type": notification_type,
                        "template": template_name,
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }
                    if self.send_webhook_notification(endpoint, webhook_payload):
                        success_count += 1
            
            # Enregistrer dans l'historique
            self.notification_history.append({
                "type": notification_type,
                "template": template_name,
                "timestamp": datetime.now(),
                "success": success_count > 0,
                "channels_sent": success_count
            })
            
            # Mettre à jour les limites de taux
            if success_count > 0:
                self._update_rate_limit(notification_type)
                self.logger.info(f"Notification {notification_type} envoyée via {success_count} canaux")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la notification: {e}")
    
    def queue_notification(self, notification_type: str, template_name: str, data: Dict):
        """Ajouter une notification à la queue"""
        notification = {
            "type": notification_type,
            "template": template_name,
            "data": data,
            "queued_at": datetime.now()
        }
        self.notification_queue.put(notification)
    
    def send_anomaly_alert(self, anomaly_data: Dict):
        """Envoyer une alerte d'anomalie"""
        self.queue_notification("anomaly_detected", "anomaly_detected", anomaly_data)
    
    def send_high_traffic_alert(self, traffic_data: Dict):
        """Envoyer une alerte de trafic élevé"""
        self.queue_notification("high_traffic", "high_traffic", traffic_data)
    
    def send_status_report(self, status_data: Dict):
        """Envoyer un rapport de statut"""
        self.queue_notification("system_status", "system_status", status_data)
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, 
                       password: str, from_address: str, to_addresses: List[str]):
        """Configurer les paramètres email"""
        self.config["email"].update({
            "enabled": True,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_address": from_address,
            "to_addresses": to_addresses
        })
        self._save_config(self.config)
        print(f"{Fore.GREEN}✓ Configuration email mise à jour")
    
    def configure_slack(self, webhook_url: str, channel: str = "#alerts"):
        """Configurer les paramètres Slack"""
        self.config["slack"].update({
            "enabled": True,
            "webhook_url": webhook_url,
            "channel": channel
        })
        self._save_config(self.config)
        print(f"{Fore.GREEN}✓ Configuration Slack mise à jour")
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """Récupérer l'historique des notifications"""
        return self.notification_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """Obtenir les statistiques des notifications"""
        total_notifications = len(self.notification_history)
        successful_notifications = len([n for n in self.notification_history if n["success"]])
        
        return {
            "total_notifications": total_notifications,
            "successful_notifications": successful_notifications,
            "success_rate": successful_notifications / total_notifications * 100 if total_notifications > 0 else 0,
            "rate_limits": self.rate_limits,
            "queue_size": self.notification_queue.qsize()
        }

def main():
    """Fonction de démonstration du système de notifications"""
    print(f"{Fore.BLUE}📧 SYSTÈME DE NOTIFICATIONS - DÉMONSTRATION")
    print("=" * 60)
    
    # Initialiser le système
    notification_system = NotificationSystem()
    
    # Configuration de démonstration
    print(f"\n{Fore.CYAN}⚙️ Configuration de démonstration:")
    
    # Simuler une configuration email (ne pas utiliser de vraies credentials)
    print(f"{Fore.YELLOW}📧 Configuration email (simulation)...")
    
    # Simuler une configuration Slack
    print(f"{Fore.YELLOW}💬 Configuration Slack (simulation)...")
    
    # Tester les templates
    print(f"\n{Fore.CYAN}🎨 Test des templates:")
    
    # Données de test pour anomalie
    anomaly_data = {
        "anomaly_type": "Port Scan Detected",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip": "192.168.1.100",
        "details": "Scan de 25 ports différents détecté",
        "total_packets": 15420,
        "packets_per_second": 342.5,
        "anomaly_count": 3
    }
    
    # Tester le rendu des templates
    email_subject = notification_system._render_template("anomaly_detected", "subject", anomaly_data)
    email_body = notification_system._render_template("anomaly_detected", "email_template", anomaly_data)
    
    print(f"{Fore.GREEN}✓ Subject: {email_subject}")
    print(f"{Fore.GREEN}✓ Email template rendu avec succès ({len(email_body)} caractères)")
    
    # Test de notification en queue
    print(f"\n{Fore.CYAN}📤 Test de notification en queue:")
    notification_system.send_anomaly_alert(anomaly_data)
    
    # Attendre un peu pour le traitement
    time.sleep(2)
    
    # Afficher les statistiques
    print(f"\n{Fore.CYAN}📊 Statistiques:")
    stats = notification_system.get_statistics()
    for key, value in stats.items():
        print(f"{Fore.YELLOW}{key}: {value}")
    
    # Afficher l'historique
    print(f"\n{Fore.CYAN}📜 Historique récent:")
    history = notification_system.get_notification_history(5)
    for i, notification in enumerate(history, 1):
        timestamp = notification["timestamp"].strftime("%H:%M:%S")
        print(f"{Fore.YELLOW}{i}. {timestamp} - {notification['type']} - {'✓' if notification['success'] else '✗'}")
    
    print(f"\n{Fore.GREEN}✅ Démonstration terminée avec succès!")

if __name__ == "__main__":
    main()