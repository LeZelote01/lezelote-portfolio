#!/usr/bin/env python3
"""
Script de démonstration pour le Système d'Alertes Sécurité
Permet de tester toutes les fonctionnalités avec des scénarios réalistes
"""

import os
import sys
import json
import time
import threading
import tempfile
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialiser colorama
init(autoreset=True)

# Ajouter le chemin du module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alertes_securite import SystemeAlertes, Alerte
from webapp import init_systeme_alertes

def demo_complete():
    """Démonstration complète de toutes les fonctionnalités"""
    print(f"{Fore.BLUE}🚨 DÉMONSTRATION COMPLÈTE - SYSTÈME D'ALERTES SÉCURITÉ")
    print("=" * 70)
    
    # Créer une configuration et base de données temporaires
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='_demo.db')
    temp_db.close()
    
    temp_config = tempfile.NamedTemporaryFile(delete=False, suffix='_demo.json', mode='w')
    config_demo = {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "demo@exemple.com",
            "password": "demo_password",
            "destinataires": ["admin@exemple.com", "security@exemple.com"]
        },
        "telegram": {
            "enabled": True,
            "token": "DEMO_BOT_TOKEN",
            "chat_ids": [123456789, -987654321]
        },
        "webhook": {
            "enabled": True,
            "url": "https://hooks.slack.com/services/DEMO/WEBHOOK/URL",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer DEMO_TOKEN"
            }
        },
        "monitoring": {
            "log_directories": ["./demo_logs", "/tmp/demo_logs"],
            "system_monitoring": True,
            "check_interval": 10
        },
        "regles": [
            {
                "id": "failed_login_demo",
                "nom": "Tentatives de connexion échouées (Démo)",
                "actif": True,
                "source": "log_file",
                "pattern": "(failed password|authentication failure|login failed)",
                "niveau": "WARNING",
                "description": "Détecte les tentatives de connexion échouées dans les logs système",
                "canaux": ["email", "telegram"],
                "cooldown": 120
            },
            {
                "id": "brute_force_demo",
                "nom": "Attaque par force brute (Démo)",
                "actif": True,
                "source": "log_file",
                "pattern": "repeated failed.*from.*[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+",
                "niveau": "ERROR",
                "description": "Détecte les attaques par force brute SSH/FTP",
                "canaux": ["email", "telegram", "webhook"],
                "cooldown": 300
            },
            {
                "id": "sql_injection_demo",
                "nom": "Tentative d'injection SQL (Démo)",
                "actif": True,
                "source": "log_file",
                "pattern": "(union select|drop table|insert into|update.*set|delete from)",
                "niveau": "CRITICAL",
                "description": "Détecte les tentatives d'injection SQL dans les logs web",
                "canaux": ["email", "telegram", "webhook"],
                "cooldown": 60
            },
            {
                "id": "cpu_high_demo",
                "nom": "CPU Élevé (Démo)",
                "actif": True,
                "source": "system",
                "pattern": "CPU_HIGH",
                "niveau": "WARNING",
                "description": "CPU utilisation > 90% pendant plus d'une minute",
                "canaux": ["telegram"],
                "cooldown": 300
            },
            {
                "id": "disk_full_demo",
                "nom": "Disque Plein (Démo)",
                "actif": True,
                "source": "system",
                "pattern": "DISK_HIGH",
                "niveau": "ERROR",
                "description": "Espace disque < 10% disponible",
                "canaux": ["email", "telegram"],
                "cooldown": 600
            },
            {
                "id": "memory_leak_demo",
                "nom": "Fuite Mémoire (Démo)",
                "actif": True,
                "source": "system",
                "pattern": "MEMORY_HIGH",
                "niveau": "ERROR",
                "description": "Utilisation mémoire > 95%",
                "canaux": ["email", "telegram"],
                "cooldown": 180
            }
        ]
    }
    json.dump(config_demo, temp_config, indent=2)
    temp_config.close()
    
    try:
        # 1. Initialisation du système
        print(f"\n{Fore.CYAN}📋 ÉTAPE 1: Initialisation du système d'alertes")
        systeme = SystemeAlertes(db_path=temp_db.name, config_path=temp_config.name)
        print(f"{Fore.GREEN}✓ Système initialisé avec {len(systeme.regles_actives())} règles actives")
        
        # 2. Test des règles d'alerte
        print(f"\n{Fore.CYAN}📋 ÉTAPE 2: Test des règles d'alerte configurées")
        regles = systeme.regles_actives()
        
        print(f"{Fore.YELLOW}Règles actives:")
        for regle in regles:
            print(f"  • {regle.nom} ({regle.niveau}) - Canaux: {', '.join(regle.canaux)}")
        
        # 3. Génération d'alertes de démonstration
        print(f"\n{Fore.CYAN}📋 ÉTAPE 3: Génération d'alertes de démonstration")
        
        scenarios_alertes = [
            {
                'id': 'demo_ssh_attack',
                'niveau': 'WARNING',
                'source': 'log:auth.log',
                'message': 'Tentatives de connexion SSH échouées détectées',
                'details': {
                    'pattern_matched': 'failed password',
                    'source_ip': '192.168.1.100',
                    'username': 'admin',
                    'attempts': 5,
                    'time_window': '2 minutes',
                    'log_entries': [
                        'Mar  8 10:15:23 server sshd[1234]: Failed password for admin from 192.168.1.100 port 22 ssh2',
                        'Mar  8 10:15:35 server sshd[1235]: Failed password for admin from 192.168.1.100 port 22 ssh2'
                    ]
                }
            },
            {
                'id': 'demo_web_attack',
                'niveau': 'CRITICAL',
                'source': 'log:apache2/access.log',
                'message': 'Tentative d\'injection SQL détectée',
                'details': {
                    'pattern_matched': 'union select',
                    'request_uri': '/login.php',
                    'source_ip': '192.168.1.200',
                    'user_agent': 'sqlmap/1.4.12',
                    'payload': "' UNION SELECT user,password FROM users--",
                    'response_code': 500,
                    'risk_level': 'HIGH'
                }
            },
            {
                'id': 'demo_brute_force',
                'niveau': 'ERROR',
                'source': 'log:fail2ban.log',
                'message': 'Attaque par force brute détectée et bloquée',
                'details': {
                    'pattern_matched': 'repeated failed',
                    'source_ip': '10.0.0.50',
                    'service': 'ssh',
                    'attempts': 25,
                    'time_window': '5 minutes',
                    'action': 'IP banned for 1 hour',
                    'jail': 'sshd'
                }
            },
            {
                'id': 'demo_system_cpu',
                'niveau': 'WARNING',
                'source': 'system',
                'message': 'Utilisation CPU critique détectée',
                'details': {
                    'cpu_percent': 95.2,
                    'load_average': [3.45, 2.89, 2.12],
                    'top_processes': [
                        {'name': 'python3', 'cpu': 45.2, 'pid': 1234},
                        {'name': 'mysql', 'cpu': 23.8, 'pid': 5678},
                        {'name': 'apache2', 'cpu': 15.4, 'pid': 9012}
                    ],
                    'duration': '2 minutes',
                    'alert_threshold': '90%'
                }
            },
            {
                'id': 'demo_disk_space',
                'niveau': 'ERROR',
                'source': 'system',
                'message': 'Espace disque critique sur partition système',
                'details': {
                    'partition': '/dev/sda1',
                    'mount_point': '/',
                    'usage_percent': 94.7,
                    'free_space': '2.1 GB',
                    'total_space': '40 GB',
                    'largest_files': [
                        '/var/log/apache2/access.log (1.2 GB)',
                        '/tmp/backup.tar.gz (800 MB)',
                        '/var/lib/mysql/database.sql (650 MB)'
                    ]
                }
            },
            {
                'id': 'demo_memory_leak',
                'niveau': 'ERROR',
                'source': 'system',
                'message': 'Possible fuite mémoire détectée',
                'details': {
                    'memory_usage': 97.3,
                    'available_memory': '1.2 GB',
                    'total_memory': '32 GB',
                    'swap_usage': 45.6,
                    'suspect_process': {
                        'name': 'java',
                        'pid': 3456,
                        'memory_mb': 8192,
                        'uptime': '2 days 14:32:15'
                    },
                    'trend': 'increasing over 6 hours'
                }
            }
        ]
        
        alertes_creees = []
        for i, scenario in enumerate(scenarios_alertes):
            alerte = Alerte(
                id=f"{scenario['id']}_{int(time.time())}_{i}",
                timestamp=datetime.now() - timedelta(minutes=i*2),  # Étaler dans le temps
                niveau=scenario['niveau'],
                source=scenario['source'],
                message=scenario['message'],
                details=scenario['details']
            )
            
            systeme.enregistrer_alerte(alerte)
            alertes_creees.append(alerte)
            print(f"{Fore.GREEN}✓ Alerte créée: {scenario['niveau']} - {scenario['message']}")
            time.sleep(0.5)  # Petite pause pour l'effet visuel
        
        print(f"{Fore.GREEN}✓ {len(alertes_creees)} alertes de démonstration créées")
        
        # 4. Test des fonctionnalités de recherche et filtrage
        print(f"\n{Fore.CYAN}📋 ÉTAPE 4: Test des fonctionnalités de recherche et filtrage")
        
        # Toutes les alertes
        toutes_alertes = systeme.lister_alertes()
        print(f"{Fore.GREEN}✓ Total des alertes: {len(toutes_alertes)}")
        
        # Filtrage par niveau
        alertes_critiques = systeme.lister_alertes(niveau='CRITICAL')
        alertes_erreurs = systeme.lister_alertes(niveau='ERROR')
        alertes_warnings = systeme.lister_alertes(niveau='WARNING')
        
        print(f"{Fore.YELLOW}Répartition par niveau:")
        print(f"  • CRITICAL: {len(alertes_critiques)} alerte(s)")
        print(f"  • ERROR: {len(alertes_erreurs)} alerte(s)")
        print(f"  • WARNING: {len(alertes_warnings)} alerte(s)")
        
        # Alertes non résolues
        alertes_non_resolues = systeme.lister_alertes(resolu=False)
        print(f"  • Non résolues: {len(alertes_non_resolues)} alerte(s)")
        
        # 5. Test de résolution d'alertes
        print(f"\n{Fore.CYAN}📋 ÉTAPE 5: Test de résolution d'alertes")
        
        if alertes_creees:
            # Résoudre quelques alertes
            alertes_a_resoudre = alertes_creees[:3]
            for alerte in alertes_a_resoudre:
                success = systeme.marquer_resolu(alerte.id)
                if success:
                    print(f"{Fore.GREEN}✓ Alerte résolue: {alerte.message[:40]}...")
        
        # 6. Génération des statistiques complètes
        print(f"\n{Fore.CYAN}📋 ÉTAPE 6: Génération des statistiques complètes")
        
        stats = systeme.obtenir_statistiques()
        if stats:
            globales = stats['globales']
            print(f"{Fore.YELLOW}Statistiques globales:")
            print(f"  • Total: {globales['total']} alerte(s)")
            print(f"  • Critiques: {globales['critiques']}")
            print(f"  • Erreurs: {globales['erreurs']}")
            print(f"  • Warnings: {globales['warnings']}")
            print(f"  • Info: {globales['info']}")
            print(f"  • Non résolues: {globales['non_resolues']}")
            
            if stats['top_sources']:
                print(f"\n{Fore.YELLOW}Top sources d'alertes:")
                for source_info in stats['top_sources'][:5]:
                    print(f"  • {source_info['source']}: {source_info['count']} alerte(s)")
        
        # 7. Test des notifications (simulation)
        print(f"\n{Fore.CYAN}📋 ÉTAPE 7: Test des notifications (simulation)")
        
        # Créer une alerte de test pour les notifications
        alerte_notification = Alerte(
            id=f"notification_test_{int(time.time())}",
            timestamp=datetime.now(),
            niveau="WARNING",
            source="demo:notification_test",
            message="Test de notification depuis la démonstration",
            details={
                'demo_mode': True,
                'notification_channels': ['email', 'telegram', 'webhook'],
                'test_timestamp': datetime.now().isoformat(),
                'priority': 'medium'
            }
        )
        
        # Enregistrer l'alerte
        systeme.enregistrer_alerte(alerte_notification)
        
        # Simuler l'envoi de notifications
        print(f"{Fore.YELLOW}📧 Simulation notifications:")
        print(f"  • Email → admin@exemple.com, security@exemple.com")
        print(f"  • Telegram → Chat IDs: 123456789, -987654321")
        print(f"  • Webhook → https://hooks.slack.com/services/DEMO/WEBHOOK/URL")
        print(f"{Fore.GREEN}✓ Notifications simulées avec succès")
        
        # 8. Test de monitoring système (simulation)
        print(f"\n{Fore.CYAN}📋 ÉTAPE 8: Test de monitoring système")
        
        # Simuler des métriques système
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"{Fore.YELLOW}Métriques système actuelles:")
        print(f"  • CPU: {cpu_percent:.1f}%")
        print(f"  • Mémoire: {memory.percent:.1f}% ({memory.available // (1024**3):.1f} GB libre)")
        print(f"  • Disque: {disk.percent:.1f}% ({disk.free // (1024**3):.1f} GB libre)")
        
        # Simuler des alertes système si nécessaire
        if cpu_percent > 50:
            print(f"{Fore.YELLOW}⚠️  CPU relativement élevé - une alerte serait générée à >90%")
        if memory.percent > 70:
            print(f"{Fore.YELLOW}⚠️  Mémoire relativement élevée - une alerte serait générée à >90%")
        if disk.percent > 80:
            print(f"{Fore.YELLOW}⚠️  Disque relativement plein - une alerte serait générée à >90%")
        
        # 9. Génération de rapport de démonstration
        print(f"\n{Fore.CYAN}📋 ÉTAPE 9: Génération du rapport de démonstration")
        
        rapport_file = "demo_rapport_alertes.json"
        rapport_data = {
            'demo_info': {
                'timestamp': datetime.now().isoformat(),
                'duration': 'demo_complete',
                'version': '1.0',
                'generated_by': 'demo_alertes.py'
            },
            'alertes_generees': len(alertes_creees),
            'regles_actives': len(regles),
            'statistiques': stats,
            'scenarios_testes': [
                'Tentatives SSH échouées',
                'Injection SQL',
                'Attaque par force brute', 
                'CPU élevé',
                'Disque plein',
                'Fuite mémoire'
            ],
            'fonctionnalites_testees': [
                'Création d\'alertes',
                'Filtrage par niveau',
                'Résolution d\'alertes',
                'Génération de statistiques',
                'Simulation de notifications',
                'Monitoring système'
            ]
        }
        
        with open(rapport_file, 'w', encoding='utf-8') as f:
            json.dump(rapport_data, f, indent=2, ensure_ascii=False)
        
        print(f"{Fore.GREEN}✓ Rapport de démonstration sauvegardé: {rapport_file}")
        
        # 10. Résumé final
        print(f"\n{Fore.CYAN}📋 ÉTAPE 10: Résumé de la démonstration")
        
        print(f"{Fore.GREEN}✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        
        print(f"\n{Fore.BLUE}📊 Résumé final:")
        print(f"  🚨 {len(alertes_creees)} alertes de démonstration créées")
        print(f"  📋 {len(regles)} règles d'alerte configurées")
        print(f"  📈 {stats['globales']['total']} alertes totales en base")
        print(f"  🔧 {len(alertes_a_resoudre)} alertes résolues")
        print(f"  📊 Statistiques complètes générées")
        print(f"  📱 Notifications simulées sur 3 canaux")
        print(f"  📋 Rapport de démonstration créé")
        
        # Lister les fichiers créés
        print(f"\n{Fore.YELLOW}📁 FICHIERS CRÉÉS:")
        fichiers_demo = [
            temp_db.name,
            temp_config.name,
            rapport_file
        ]
        
        for fichier in fichiers_demo:
            if os.path.exists(fichier):
                taille = os.path.getsize(fichier)
                print(f"  ✓ {os.path.basename(fichier)} ({taille:,} bytes)")
        
        print(f"\n{Fore.CYAN}🌐 Pour tester l'interface web:")
        print(f"  python3 webapp.py --db {temp_db.name} --config {temp_config.name}")
        
        print(f"\n{Fore.CYAN}💻 Pour tester en ligne de commande:")
        print(f"  python3 alertes_securite.py --db {temp_db.name} list")
        print(f"  python3 alertes_securite.py --db {temp_db.name} stats")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Note: On ne supprime pas les fichiers temporaires pour permettre les tests
        print(f"\n{Fore.YELLOW}💡 Les fichiers de démonstration sont conservés pour exploration")

def demo_notifications():
    """Démonstration spécifique des notifications"""
    print(f"\n{Fore.BLUE}📱 DÉMONSTRATION NOTIFICATIONS - SYSTÈME D'ALERTES")
    print("=" * 50)
    
    # Configuration de test pour notifications
    temp_config = tempfile.NamedTemporaryFile(delete=False, suffix='_notif_demo.json', mode='w')
    config_notif = {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "demo@test.com",
            "password": "demo_app_password",
            "destinataires": ["admin@entreprise.com", "security@entreprise.com"]
        },
        "telegram": {
            "enabled": True,
            "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            "chat_ids": [123456789, -987654321]
        },
        "webhook": {
            "enabled": True,
            "url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
            "headers": {
                "Content-Type": "application/json"
            }
        }
    }
    json.dump(config_notif, temp_config, indent=2)
    temp_config.close()
    
    try:
        from alertes_securite import NotificationManager
        
        # Initialiser le gestionnaire de notifications
        notif_manager = NotificationManager(config_notif)
        
        # Créer des alertes de test pour chaque niveau
        alertes_test = [
            {
                'niveau': 'INFO',
                'message': 'Service démarré avec succès',
                'details': {'service': 'web_server', 'port': 80, 'status': 'running'}
            },
            {
                'niveau': 'WARNING',
                'message': 'Utilisation mémoire élevée détectée',
                'details': {'memory_usage': 85.2, 'threshold': 80, 'process': 'database'}
            },
            {
                'niveau': 'ERROR',
                'message': 'Échec de connexion à la base de données',
                'details': {'database': 'production', 'error': 'timeout', 'retry_count': 3}
            },
            {
                'niveau': 'CRITICAL',
                'message': 'Intrusion système détectée - Action immédiate requise',
                'details': {'source_ip': '192.168.1.200', 'attack_type': 'privilege_escalation', 'affected_users': ['admin', 'root']}
            }
        ]
        
        print(f"\n{Fore.CYAN}🧪 Test des formats de notification par niveau:")
        
        for i, alerte_data in enumerate(alertes_test):
            print(f"\n{Fore.YELLOW}📤 Test notification {alerte_data['niveau']}:")
            
            alerte = Alerte(
                id=f"notif_test_{i}_{int(time.time())}",
                timestamp=datetime.now(),
                niveau=alerte_data['niveau'],
                source="demo:notification",
                message=alerte_data['message'],
                details=alerte_data['details']
            )
            
            # Simuler l'envoi (les méthodes seront mockées en réalité)
            print(f"  📧 Email: {alerte_data['message']}")
            print(f"      └─ Destinataires: {', '.join(config_notif['email']['destinataires'])}")
            
            print(f"  📱 Telegram: {get_telegram_emoji(alerte_data['niveau'])} {alerte_data['message']}")
            print(f"      └─ Chat IDs: {', '.join(map(str, config_notif['telegram']['chat_ids']))}")
            
            print(f"  🌐 Webhook: JSON payload vers Slack")
            print(f"      └─ URL: {config_notif['webhook']['url'][:50]}...")
            
            time.sleep(0.5)
        
        print(f"\n{Fore.GREEN}✅ Tests de notification terminés")
        
        # Exemples de templates de notification
        print(f"\n{Fore.CYAN}📝 EXEMPLES DE TEMPLATES:")
        
        print(f"\n{Fore.YELLOW}📧 Template Email:")
        email_template = """
Subject: 🚨 Alerte Sécurité [CRITICAL] - Intrusion système détectée

Alerte Sécurité - CRITICAL

Timestamp: 2025-03-08 10:30:45
Source: demo:notification  
Message: Intrusion système détectée - Action immédiate requise

Détails:
{
  "source_ip": "192.168.1.200",
  "attack_type": "privilege_escalation", 
  "affected_users": ["admin", "root"]
}

Actions recommandées:
1. Isoler les comptes affectés
2. Analyser les logs de connexion
3. Vérifier l'intégrité du système
4. Contacter l'équipe sécurité

---
Système d'Alertes Sécurité
        """
        print(email_template)
        
        print(f"\n{Fore.YELLOW}📱 Template Telegram:")
        telegram_template = """
🚨 **Alerte Sécurité [CRITICAL]**

🕐 **Timestamp:** 2025-03-08 10:30:45
📡 **Source:** demo:notification
💬 **Message:** Intrusion système détectée - Action immédiate requise

📋 **Détails:**
```json
{
  "source_ip": "192.168.1.200",
  "attack_type": "privilege_escalation",
  "affected_users": ["admin", "root"]
}
```

⚡ **Action immédiate requise!**
        """
        print(telegram_template)
        
        print(f"\n{Fore.YELLOW}🌐 Template Webhook (Slack):")
        webhook_template = {
            "text": "🚨 Alerte Sécurité Critique",
            "attachments": [
                {
                    "color": "danger",
                    "fields": [
                        {"title": "Niveau", "value": "CRITICAL", "short": True},
                        {"title": "Source", "value": "demo:notification", "short": True},
                        {"title": "Message", "value": "Intrusion système détectée - Action immédiate requise"},
                        {"title": "IP Source", "value": "192.168.1.200", "short": True},
                        {"title": "Type d'attaque", "value": "privilege_escalation", "short": True}
                    ],
                    "footer": "Système d'Alertes Sécurité",
                    "ts": int(time.time())
                }
            ]
        }
        print(json.dumps(webhook_template, indent=2))
        
    finally:
        try:
            os.unlink(temp_config.name)
        except:
            pass

def get_telegram_emoji(niveau):
    """Retourner l'emoji approprié pour le niveau d'alerte"""
    emoji_map = {
        'INFO': 'ℹ️',
        'WARNING': '⚠️', 
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    return emoji_map.get(niveau, '📢')

def demo_monitoring():
    """Démonstration du monitoring système en temps réel"""
    print(f"\n{Fore.BLUE}🔍 DÉMONSTRATION MONITORING - SYSTÈME D'ALERTES")
    print("=" * 50)
    
    import psutil
    import tempfile
    
    # Créer un dossier de logs temporaire pour la démo
    temp_log_dir = tempfile.mkdtemp(prefix='demo_logs_')
    
    try:
        print(f"\n{Fore.CYAN}🖥️  Monitoring des ressources système:")
        
        # Monitoring CPU
        print(f"\n{Fore.YELLOW}📊 CPU:")
        for i in range(5):
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            print(f"  • Utilisation: {cpu_percent:5.1f}% ({cpu_count} cores)")
            print(f"  • Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            
            if cpu_percent > 80:
                print(f"    {Fore.RED}⚠️  Alerte CPU élevé serait déclenchée!")
            
            time.sleep(1)
        
        # Monitoring Mémoire
        print(f"\n{Fore.YELLOW}💾 Mémoire:")
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        print(f"  • RAM: {memory.percent:5.1f}% ({memory.used // (1024**3):.1f}/{memory.total // (1024**3):.1f} GB)")
        print(f"  • Disponible: {memory.available // (1024**3):.1f} GB")
        print(f"  • Swap: {swap.percent:5.1f}% ({swap.used // (1024**3):.1f}/{swap.total // (1024**3):.1f} GB)")
        
        if memory.percent > 80:
            print(f"    {Fore.RED}⚠️  Alerte mémoire élevée serait déclenchée!")
        
        # Monitoring Disque
        print(f"\n{Fore.YELLOW}💽 Stockage:")
        partitions = psutil.disk_partitions()
        
        for partition in partitions[:3]:  # Limiter à 3 partitions
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                print(f"  • {partition.device} ({partition.mountpoint}):")
                print(f"    └─ {partition_usage.percent:5.1f}% ({partition_usage.used // (1024**3):.1f}/{partition_usage.total // (1024**3):.1f} GB)")
                
                if partition_usage.percent > 85:
                    print(f"      {Fore.RED}⚠️  Alerte disque plein serait déclenchée!")
                    
            except PermissionError:
                print(f"  • {partition.device}: Permission refusée")
        
        # Monitoring Processus
        print(f"\n{Fore.YELLOW}🔄 Top Processus:")
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Trier par CPU et prendre les 5 premiers
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        for proc in processes[:5]:
            cpu = proc['cpu_percent'] or 0
            memory = proc['memory_percent'] or 0
            print(f"  • {proc['name']:15} (PID {proc['pid']:5}): CPU {cpu:5.1f}%, RAM {memory:5.1f}%")
        
        # Simulation de monitoring de logs
        print(f"\n{Fore.YELLOW}📄 Simulation monitoring de logs:")
        
        # Créer des logs de test
        log_files = ['auth.log', 'syslog', 'apache2/access.log', 'fail2ban.log']
        
        for log_file in log_files:
            log_path = os.path.join(temp_log_dir, log_file)
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            # Écrire des logs de démonstration
            with open(log_path, 'w') as f:
                if 'auth.log' in log_file:
                    f.write("Mar  8 10:15:23 server sshd[1234]: Failed password for admin from 192.168.1.100 port 22 ssh2\n")
                    f.write("Mar  8 10:15:35 server sshd[1235]: Failed password for root from 192.168.1.100 port 22 ssh2\n")
                elif 'access.log' in log_file:
                    f.write('192.168.1.200 - - [08/Mar/2025:10:30:45 +0000] "GET /login.php?id=1\' UNION SELECT user,password FROM users-- HTTP/1.1" 500 1234\n')
                elif 'fail2ban.log' in log_file:
                    f.write("2025-03-08 10:32:15,123 fail2ban.actions[1234]: NOTICE [sshd] Ban 192.168.1.100\n")
                else:
                    f.write("Mar  8 10:30:00 server kernel: [12345.678901] Out of memory: Kill process 1234 (mysql) score 123 or sacrifice child\n")
            
            print(f"  • {log_file}: {os.path.getsize(log_path)} bytes")
        
        print(f"\n{Fore.CYAN}📁 Dossier de logs de démonstration: {temp_log_dir}")
        print(f"{Fore.GREEN}✓ Monitoring système de démonstration terminé")
        
    finally:
        # Nettoyer le dossier temporaire
        import shutil
        try:
            shutil.rmtree(temp_log_dir)
        except:
            pass

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "complete":
            demo_complete()
        elif mode == "notifications":
            demo_notifications()
        elif mode == "monitoring":
            demo_monitoring()
        else:
            print(f"{Fore.RED}Mode inconnu: {mode}")
            print(f"{Fore.CYAN}Modes disponibles: complete, notifications, monitoring")
    else:
        # Menu interactif
        print(f"{Fore.BLUE}🚨 DÉMONSTRATIONS SYSTÈME D'ALERTES SÉCURITÉ")
        print("=" * 50)
        
        options = {
            "1": ("Démonstration complète", demo_complete),
            "2": ("Test des notifications", demo_notifications),
            "3": ("Monitoring système", demo_monitoring),
            "4": ("Quitter", None)
        }
        
        while True:
            print(f"\n{Fore.CYAN}Choisissez une démonstration:")
            for key, (description, _) in options.items():
                print(f"{Fore.YELLOW}{key}. {description}")
            
            choice = input(f"\n{Fore.WHITE}Votre choix (1-4): ").strip()
            
            if choice in options:
                description, func = options[choice]
                if func is None:
                    print(f"{Fore.GREEN}Au revoir!")
                    break
                else:
                    print(f"\n{Fore.BLUE}>>> {description}")
                    func()
                    input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")
            else:
                print(f"{Fore.RED}Choix invalide. Veuillez choisir entre 1 et 4.")

if __name__ == "__main__":
    main()