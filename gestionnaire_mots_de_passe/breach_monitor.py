#!/usr/bin/env python3
"""
Module de Surveillance des Violations de Données
Gestionnaire de Mots de Passe - Breach Monitor

Fonctionnalités:
- Surveillance proactive des violations de données
- Notifications automatiques par email/SMS/Webhook
- Vérification périodique des comptes compromis
- Intégration avec HaveIBeenPwned API
- Recommandations automatiques de changement
- Historique des violations détectées
"""

import json
import time
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore, Style

class NotificationChannel(Enum):
    """Canaux de notification disponibles"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DESKTOP = "desktop"

class BreachSeverity(Enum):
    """Niveaux de sévérité des violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BreachInfo:
    """Informations sur une violation de données"""
    breach_name: str
    domain: str
    date_discovered: datetime
    compromised_accounts: int
    compromised_data: List[str]
    description: str
    severity: BreachSeverity
    verified: bool

@dataclass
class AccountBreach:
    """Association compte-violation"""
    account_id: str
    account_title: str
    account_username: str
    account_email: str
    breach_info: BreachInfo
    detected_at: datetime
    notified: bool
    password_changed: bool

class BreachMonitor:
    """Moniteur de violations de données"""
    
    def __init__(self, gestionnaire_mdp, config_file: str = "breach_monitor_config.json"):
        self.gestionnaire = gestionnaire_mdp
        self.config_file = config_file
        self.config = self._load_config()
        self.breach_db_path = "breaches.db"
        self.hibp_api_url = "https://haveibeenpwned.com/api/v3"
        self.running = False
        self.monitor_thread = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('breach_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialiser la base des violations
        self._init_breach_database()
        
        print(f"{Fore.GREEN}🚨 Moniteur de Violations initialisé")
    
    def _load_config(self) -> Dict[str, Any]:
        """Charger la configuration"""
        default_config = {
            "hibp_api_key": None,
            "monitoring_enabled": True,
            "check_interval_hours": 24,
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "to_emails": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                },
                "desktop": {
                    "enabled": True
                }
            },
            "breach_sources": {
                "haveibeenpwned": True,
                "local_database": True
            }
        }
        
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                # Fusionner avec la config par défaut
                config = {**default_config, **user_config}
                return config
        except FileNotFoundError:
            self._save_config(default_config)
            return default_config
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur de configuration JSON: {e}")
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Sauvegarder la configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Impossible de sauvegarder la configuration: {e}")
    
    def _init_breach_database(self):
        """Initialiser la base de données des violations"""
        conn = sqlite3.connect(self.breach_db_path)
        cursor = conn.cursor()
        
        # Table des violations connues
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS breaches (
                id INTEGER PRIMARY KEY,
                breach_name TEXT UNIQUE NOT NULL,
                domain TEXT,
                date_discovered TEXT,
                compromised_accounts INTEGER,
                compromised_data TEXT,
                description TEXT,
                severity TEXT,
                verified BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des comptes compromis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_breaches (
                id INTEGER PRIMARY KEY,
                account_id TEXT NOT NULL,
                account_title TEXT,
                account_username TEXT,
                account_email TEXT,
                breach_name TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE,
                password_changed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (breach_name) REFERENCES breaches (breach_name)
            )
        ''')
        
        # Table des notifications envoyées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications_sent (
                id INTEGER PRIMARY KEY,
                account_id TEXT,
                breach_name TEXT,
                notification_channel TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_email_breached(self, email: str) -> List[BreachInfo]:
        """Vérifier si un email a été compromis"""
        if not self.config.get("hibp_api_key"):
            self.logger.warning("Clé API HaveIBeenPwned manquante")
            return []
        
        breaches = []
        
        try:
            # Requête vers HaveIBeenPwned
            headers = {
                'hibp-api-key': self.config["hibp_api_key"],
                'User-Agent': 'Password-Manager-Breach-Monitor'
            }
            
            response = requests.get(
                f"{self.hibp_api_url}/breachedaccount/{email}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                breach_data = response.json()
                
                for breach in breach_data:
                    breach_info = BreachInfo(
                        breach_name=breach['Name'],
                        domain=breach['Domain'],
                        date_discovered=datetime.fromisoformat(breach['BreachDate']),
                        compromised_accounts=breach['PwnCount'],
                        compromised_data=breach['DataClasses'],
                        description=breach['Description'],
                        severity=self._determine_severity(breach),
                        verified=breach['IsVerified']
                    )
                    breaches.append(breach_info)
            
            elif response.status_code == 404:
                # Aucune violation trouvée - c'est une bonne nouvelle
                self.logger.info(f"Aucune violation trouvée pour {email}")
            
            elif response.status_code == 429:
                # Rate limit atteint
                self.logger.warning("Rate limit HaveIBeenPwned atteint")
                time.sleep(2)
            
            else:
                self.logger.error(f"Erreur API HaveIBeenPwned: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur réseau HaveIBeenPwned: {e}")
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la vérification: {e}")
        
        return breaches
    
    def _determine_severity(self, breach_data: Dict) -> BreachSeverity:
        """Déterminer la sévérité d'une violation"""
        # Facteurs de sévérité
        sensitive_data = ['Passwords', 'Credit cards', 'Social security numbers', 
                         'Phone numbers', 'Physical addresses', 'Banking details']
        
        compromised_data = breach_data.get('DataClasses', [])
        pwn_count = breach_data.get('PwnCount', 0)
        verified = breach_data.get('IsVerified', False)
        
        # Calcul du score de sévérité
        severity_score = 0
        
        # Données sensibles compromises
        for data_type in compromised_data:
            if data_type in sensitive_data:
                severity_score += 2
            else:
                severity_score += 1
        
        # Nombre de comptes compromis
        if pwn_count > 1000000:  # Plus d'1M
            severity_score += 3
        elif pwn_count > 100000:  # Plus de 100K
            severity_score += 2
        elif pwn_count > 10000:   # Plus de 10K
            severity_score += 1
        
        # Vérification de la violation
        if verified:
            severity_score += 1
        
        # Déterminer le niveau
        if severity_score >= 8:
            return BreachSeverity.CRITICAL
        elif severity_score >= 5:
            return BreachSeverity.HIGH
        elif severity_score >= 3:
            return BreachSeverity.MEDIUM
        else:
            return BreachSeverity.LOW
    
    def monitor_all_accounts(self) -> List[AccountBreach]:
        """Surveiller tous les comptes pour des violations"""
        if not self.gestionnaire.check_session():
            raise Exception("Session expirée, authentification requise")
        
        self.logger.info("Début de la surveillance des comptes...")
        
        # Récupérer tous les comptes
        accounts = self.gestionnaire.list_passwords()
        account_breaches = []
        
        for account in accounts:
            try:
                # Récupérer les détails complets du compte
                full_account = self.gestionnaire.get_password(account['id'])
                if not full_account:
                    continue
                
                # Extraire l'email (username ou notes)
                email = None
                username = full_account.get('username', '')
                notes = full_account.get('notes', '')
                
                # Détecter l'email dans username
                if '@' in username:
                    email = username
                # Sinon chercher dans les notes
                elif '@' in notes:
                    import re
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', notes)
                    if email_match:
                        email = email_match.group()
                
                if email:
                    self.logger.info(f"Vérification de l'email: {email}")
                    breaches = self.check_email_breached(email)
                    
                    for breach in breaches:
                        # Vérifier si cette violation est déjà connue pour ce compte
                        if not self._is_breach_known(account['id'], breach.breach_name):
                            account_breach = AccountBreach(
                                account_id=account['id'],
                                account_title=full_account['title'],
                                account_username=username,
                                account_email=email,
                                breach_info=breach,
                                detected_at=datetime.now(),
                                notified=False,
                                password_changed=False
                            )
                            account_breaches.append(account_breach)
                            
                            # Enregistrer dans la base
                            self._save_account_breach(account_breach)
                
                # Délai pour éviter le rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la vérification du compte {account.get('title', 'Unknown')}: {e}")
        
        self.logger.info(f"Surveillance terminée. {len(account_breaches)} nouvelles violations détectées.")
        
        # Envoyer les notifications
        if account_breaches:
            self._send_breach_notifications(account_breaches)
        
        return account_breaches
    
    def _is_breach_known(self, account_id: str, breach_name: str) -> bool:
        """Vérifier si une violation est déjà connue pour un compte"""
        conn = sqlite3.connect(self.breach_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM account_breaches 
            WHERE account_id = ? AND breach_name = ?
        ''', (account_id, breach_name))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def _save_account_breach(self, account_breach: AccountBreach):
        """Enregistrer une violation de compte"""
        conn = sqlite3.connect(self.breach_db_path)
        cursor = conn.cursor()
        
        # Sauvegarder la violation générale
        cursor.execute('''
            INSERT OR IGNORE INTO breaches 
            (breach_name, domain, date_discovered, compromised_accounts, 
             compromised_data, description, severity, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            account_breach.breach_info.breach_name,
            account_breach.breach_info.domain,
            account_breach.breach_info.date_discovered.isoformat(),
            account_breach.breach_info.compromised_accounts,
            json.dumps(account_breach.breach_info.compromised_data),
            account_breach.breach_info.description,
            account_breach.breach_info.severity.value,
            account_breach.breach_info.verified
        ))
        
        # Sauvegarder l'association compte-violation
        cursor.execute('''
            INSERT INTO account_breaches 
            (account_id, account_title, account_username, account_email, 
             breach_name, detected_at, notified, password_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            account_breach.account_id,
            account_breach.account_title,
            account_breach.account_username,
            account_breach.account_email,
            account_breach.breach_info.breach_name,
            account_breach.detected_at.isoformat(),
            account_breach.notified,
            account_breach.password_changed
        ))
        
        conn.commit()
        conn.close()
    
    def _send_breach_notifications(self, account_breaches: List[AccountBreach]):
        """Envoyer les notifications de violation"""
        for account_breach in account_breaches:
            notifications_sent = []
            
            # Notification par email
            if self.config["notifications"]["email"]["enabled"]:
                success = self._send_email_notification(account_breach)
                notifications_sent.append(("email", success))
            
            # Notification par webhook
            if self.config["notifications"]["webhook"]["enabled"]:
                success = self._send_webhook_notification(account_breach)
                notifications_sent.append(("webhook", success))
            
            # Notification desktop (toujours activée)
            success = self._send_desktop_notification(account_breach)
            notifications_sent.append(("desktop", success))
            
            # Marquer comme notifié si au moins une notification a réussi
            if any(success for _, success in notifications_sent):
                self._mark_breach_notified(account_breach.account_id, account_breach.breach_info.breach_name)
            
            # Enregistrer les notifications envoyées
            for channel, success in notifications_sent:
                self._log_notification_sent(account_breach, channel, success)
    
    def _send_email_notification(self, account_breach: AccountBreach) -> bool:
        """Envoyer une notification par email"""
        try:
            email_config = self.config["notifications"]["email"]
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = f"🚨 ALERTE SÉCURITÉ - Violation de données détectée"
            
            # Corps du message
            body = self._generate_email_body(account_breach)
            msg.attach(MIMEText(body, 'html'))
            
            # Envoyer l'email
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["from_email"], email_config["to_emails"], text)
            server.quit()
            
            self.logger.info(f"Email de notification envoyé pour {account_breach.account_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def _send_webhook_notification(self, account_breach: AccountBreach) -> bool:
        """Envoyer une notification par webhook"""
        try:
            webhook_config = self.config["notifications"]["webhook"]
            
            payload = {
                "alert_type": "data_breach",
                "severity": account_breach.breach_info.severity.value,
                "account": {
                    "title": account_breach.account_title,
                    "username": account_breach.account_username,
                    "email": account_breach.account_email
                },
                "breach": {
                    "name": account_breach.breach_info.breach_name,
                    "domain": account_breach.breach_info.domain,
                    "date_discovered": account_breach.breach_info.date_discovered.isoformat(),
                    "compromised_accounts": account_breach.breach_info.compromised_accounts,
                    "compromised_data": account_breach.breach_info.compromised_data,
                    "verified": account_breach.breach_info.verified
                },
                "timestamp": account_breach.detected_at.isoformat()
            }
            
            headers = {
                'Content-Type': 'application/json',
                **webhook_config.get("headers", {})
            }
            
            response = requests.post(
                webhook_config["url"],
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Webhook envoyé pour {account_breach.account_title}")
                return True
            else:
                self.logger.error(f"Erreur webhook: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du webhook: {e}")
            return False
    
    def _send_desktop_notification(self, account_breach: AccountBreach) -> bool:
        """Envoyer une notification desktop"""
        try:
            severity_color = {
                BreachSeverity.LOW: Fore.YELLOW,
                BreachSeverity.MEDIUM: Fore.MAGENTA,
                BreachSeverity.HIGH: Fore.RED,
                BreachSeverity.CRITICAL: Fore.RED + Style.BRIGHT
            }
            
            color = severity_color.get(account_breach.breach_info.severity, Fore.WHITE)
            
            print(f"\n{color}🚨 ALERTE VIOLATION DE DONNÉES")
            print(f"══════════════════════════════════════")
            print(f"📧 Compte: {account_breach.account_title}")
            print(f"👤 Email: {account_breach.account_email}")
            print(f"🏢 Violation: {account_breach.breach_info.breach_name}")
            print(f"📅 Découverte: {account_breach.breach_info.date_discovered.strftime('%d/%m/%Y')}")
            print(f"📊 Comptes compromis: {account_breach.breach_info.compromised_accounts:,}")
            print(f"🔥 Sévérité: {account_breach.breach_info.severity.value.upper()}")
            print(f"🔍 Vérifiée: {'✓' if account_breach.breach_info.verified else '✗'}")
            print(f"💡 Données compromises: {', '.join(account_breach.breach_info.compromised_data)}")
            print(f"\n{Fore.GREEN}📝 ACTIONS RECOMMANDÉES:")
            print(f"  1. Changez IMMÉDIATEMENT le mot de passe de ce compte")
            print(f"  2. Activez l'authentification à deux facteurs (2FA)")
            print(f"  3. Surveillez vos comptes pour des activités suspectes")
            print(f"  4. Considérez changer les mots de passe similaires")
            print(f"{Style.RESET_ALL}══════════════════════════════════════\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur notification desktop: {e}")
            return False
    
    def _generate_email_body(self, account_breach: AccountBreach) -> str:
        """Générer le corps HTML de l'email de notification"""
        severity_colors = {
            BreachSeverity.LOW: "#FFA500",
            BreachSeverity.MEDIUM: "#FF4500", 
            BreachSeverity.HIGH: "#FF0000",
            BreachSeverity.CRITICAL: "#8B0000"
        }
        
        severity_color = severity_colors.get(account_breach.breach_info.severity, "#808080")
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                .alert {{ background: linear-gradient(135deg, #ff416c, #ff4b2b); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .severity {{ background: {severity_color}; color: white; padding: 5px 10px; border-radius: 4px; display: inline-block; }}
                .actions {{ background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h1>🚨 ALERTE VIOLATION DE DONNÉES</h1>
                <p>Une violation de données affectant l'un de vos comptes a été détectée</p>
            </div>
            
            <div class="content">
                <h2>📋 Détails du compte compromis</h2>
                <ul>
                    <li><strong>Compte:</strong> {account_breach.account_title}</li>
                    <li><strong>Email:</strong> {account_breach.account_email}</li>
                    <li><strong>Nom d'utilisateur:</strong> {account_breach.account_username}</li>
                </ul>
                
                <h2>🏢 Informations sur la violation</h2>
                <ul>
                    <li><strong>Nom de la violation:</strong> {account_breach.breach_info.breach_name}</li>
                    <li><strong>Domaine:</strong> {account_breach.breach_info.domain}</li>
                    <li><strong>Date de découverte:</strong> {account_breach.breach_info.date_discovered.strftime('%d/%m/%Y')}</li>
                    <li><strong>Comptes compromis:</strong> {account_breach.breach_info.compromised_accounts:,}</li>
                    <li><strong>Sévérité:</strong> <span class="severity">{account_breach.breach_info.severity.value.upper()}</span></li>
                    <li><strong>Violation vérifiée:</strong> {'✓ Oui' if account_breach.breach_info.verified else '✗ Non'}</li>
                </ul>
                
                <h2>💡 Données compromises</h2>
                <p>{', '.join(account_breach.breach_info.compromised_data)}</p>
                
                <h2>📄 Description</h2>
                <p>{account_breach.breach_info.description[:500]}...</p>
            </div>
            
            <div class="actions">
                <h2>🚀 Actions recommandées IMMÉDIATEMENT</h2>
                <ol>
                    <li><strong>Changez le mot de passe</strong> de ce compte immédiatement</li>
                    <li><strong>Activez l'authentification à deux facteurs</strong> (2FA) si ce n'est pas déjà fait</li>
                    <li><strong>Surveillez vos comptes</strong> pour des activités suspectes</li>
                    <li><strong>Changez les mots de passe similaires</strong> sur d'autres comptes</li>
                    <li><strong>Vérifiez vos relevés</strong> bancaires et autres comptes sensibles</li>
                </ol>
            </div>
            
            <div class="footer">
                <p>Cette alerte a été générée automatiquement par votre Gestionnaire de Mots de Passe</p>
                <p>Date de détection: {account_breach.detected_at.strftime('%d/%m/%Y à %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        return html_body
    
    def _mark_breach_notified(self, account_id: str, breach_name: str):
        """Marquer une violation comme notifiée"""
        conn = sqlite3.connect(self.breach_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE account_breaches 
            SET notified = TRUE 
            WHERE account_id = ? AND breach_name = ?
        ''', (account_id, breach_name))
        
        conn.commit()
        conn.close()
    
    def _log_notification_sent(self, account_breach: AccountBreach, channel: str, success: bool):
        """Enregistrer qu'une notification a été envoyée"""
        conn = sqlite3.connect(self.breach_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications_sent 
            (account_id, breach_name, notification_channel, success)
            VALUES (?, ?, ?, ?)
        ''', (
            account_breach.account_id,
            account_breach.breach_info.breach_name,
            channel,
            success
        ))
        
        conn.commit()
        conn.close()
    
    def start_monitoring(self):
        """Démarrer la surveillance continue"""
        if self.running:
            self.logger.warning("La surveillance est déjà en cours")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Surveillance automatique démarrée")
        print(f"{Fore.GREEN}🚨 Surveillance des violations démarrée")
    
    def stop_monitoring(self):
        """Arrêter la surveillance continue"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Surveillance automatique arrêtée")
        print(f"{Fore.YELLOW}⏹️ Surveillance des violations arrêtée")
    
    def _monitoring_loop(self):
        """Boucle principale de surveillance"""
        check_interval = self.config.get("check_interval_hours", 24) * 3600  # En secondes
        
        while self.running:
            try:
                self.logger.info("Début d'un cycle de surveillance...")
                breaches = self.monitor_all_accounts()
                
                if breaches:
                    self.logger.warning(f"{len(breaches)} nouvelles violations détectées!")
                else:
                    self.logger.info("Aucune nouvelle violation détectée")
                
                # Attendre jusqu'au prochain cycle
                for _ in range(check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle de surveillance: {e}")
                # Attendre 5 minutes avant de réessayer en cas d'erreur
                for _ in range(300):
                    if not self.running:
                        break
                    time.sleep(1)
    
    def get_breach_report(self) -> Dict[str, Any]:
        """Obtenir un rapport des violations détectées"""
        conn = sqlite3.connect(self.breach_db_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        cursor.execute('SELECT COUNT(*) FROM account_breaches')
        total_breaches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM account_breaches WHERE notified = FALSE')
        unnotified_breaches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM account_breaches WHERE password_changed = FALSE')
        unchanged_passwords = cursor.fetchone()[0]
        
        # Violations par sévérité
        cursor.execute('''
            SELECT b.severity, COUNT(*) 
            FROM account_breaches ab
            JOIN breaches b ON ab.breach_name = b.breach_name
            GROUP BY b.severity
        ''')
        severity_counts = dict(cursor.fetchall())
        
        # Violations récentes (7 derniers jours)
        cursor.execute('''
            SELECT ab.account_title, ab.breach_name, ab.detected_at, b.severity
            FROM account_breaches ab
            JOIN breaches b ON ab.breach_name = b.breach_name
            WHERE ab.detected_at > datetime('now', '-7 days')
            ORDER BY ab.detected_at DESC
        ''')
        recent_breaches = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_breaches": total_breaches,
            "unnotified_breaches": unnotified_breaches,
            "unchanged_passwords": unchanged_passwords,
            "severity_distribution": severity_counts,
            "recent_breaches": [
                {
                    "account_title": row[0],
                    "breach_name": row[1],
                    "detected_at": row[2],
                    "severity": row[3]
                }
                for row in recent_breaches
            ],
            "monitoring_status": "active" if self.running else "inactive"
        }

if __name__ == "__main__":
    print(f"{Fore.BLUE}🚨 SURVEILLANCE DES VIOLATIONS")
    print("=" * 50)
    print(f"{Fore.CYAN}Pour tester ce module, utilisez les modes production appropriés")