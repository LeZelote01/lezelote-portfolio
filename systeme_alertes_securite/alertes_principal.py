#!/usr/bin/env python3
"""
🚨 SYSTÈME D'ALERTES SÉCURITÉ - FICHIER PRINCIPAL UNIFIÉ
=========================================================

Orchestrateur centralisé pour toutes les fonctionnalités du système d'alertes :
- Interface CLI unifiée avec 6 modes d'utilisation
- Gestion centralisée des configurations et composants  
- Architecture modulaire intégrée
- Point d'entrée unique pour déploiement et maintenance

Modes disponibles :
- CLI      : Interface en ligne de commande
- Daemon   : Service de monitoring continu
- Web      : Dashboard web interactif  
- API      : Serveur API REST
- ML       : Machine Learning et analyse d'anomalies
- All      : Tous les services simultanément

Version : 3.0.0 - Architecture Harmonisée
Auteur  : Système d'Intelligence Artificielle
Date    : 2025
"""

import os
import sys
import json
import time
import signal
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse
from colorama import init, Fore, Style

# Initialisation colorama
init(autoreset=True)

# Imports des modules du système d'alertes
try:
    from alertes_securite import SystemeAlertes, Alerte
    from ml_anomaly_detector import MLAnomalyDetector
    MODULES_DISPONIBLES = True
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur import modules: {e}")
    MODULES_DISPONIBLES = False

class AlertesPrincipal:
    """
    Orchestrateur principal du système d'alertes sécurité
    
    Gère l'architecture intégrée avec :
    - Configuration centralisée
    - Services multiples (monitoring, web, API, ML)
    - Interface CLI unifiée
    - Gestion du cycle de vie des composants
    """
    
    def __init__(self, config_path="config.json", db_path="alertes.db"):
        self.config_path = config_path
        self.db_path = db_path
        self.config = self.charger_configuration()
        
        # Composants principaux
        self.systeme_alertes = None
        self.webapp = None
        self.api_app = None
        self.ml_detector = None
        
        # État des services
        self.services_actifs = {
            'monitoring': False,
            'webapp': False,
            'api': False,
            'ml': False
        }
        
        # Thread management
        self.threads = {}
        self.running = False
        
        print(f"{Fore.BLUE}🚨 SYSTÈME D'ALERTES SÉCURITÉ - PRINCIPAL")
        print(f"{Fore.CYAN}   Version 3.0.0 - Architecture Harmonisée")
        print("=" * 50)
    
    def charger_configuration(self) -> Dict[str, Any]:
        """Charger et valider la configuration centralisée"""
        config_defaut = {
            "version": "3.0.0",
            "services": {
                "monitoring": {"enabled": True, "auto_start": True},
                "webapp": {"enabled": True, "port": 5000, "host": "127.0.0.1"},
                "api": {"enabled": True, "port": 5001, "host": "127.0.0.1"}, 
                "ml": {"enabled": True, "auto_train": False}
            },
            "paths": {
                "logs": "./logs",
                "models": "./ml_models",
                "temp": "./temp"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_utilisateur = json.load(f)
                
                # Merger avec config par défaut
                config = {**config_defaut, **config_utilisateur}
                
                # Ajouter la configuration des services si manquante
                if 'services' not in config:
                    config['services'] = config_defaut['services']
                
                return config
            else:
                print(f"{Fore.YELLOW}⚠️  Configuration par défaut utilisée")
                return config_defaut
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur chargement config: {e}")
            return config_defaut
    
    def initialiser_systeme(self):
        """Initialiser le système d'alertes principal"""
        if not MODULES_DISPONIBLES:
            print(f"{Fore.RED}❌ Modules non disponibles")
            return False
        
        try:
            self.systeme_alertes = SystemeAlertes(
                db_path=self.db_path,
                config_path=self.config_path
            )
            print(f"{Fore.GREEN}✓ Système d'alertes initialisé")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur initialisation système: {e}")
            return False
    
    def initialiser_ml(self):
        """Initialiser le détecteur ML"""
        if self.config.get('services', {}).get('ml', {}).get('enabled', True):
            try:
                self.ml_detector = MLAnomalyDetector(db_path=self.db_path)
                
                # Tentative de chargement des modèles
                if self.ml_detector.load_models():
                    print(f"{Fore.GREEN}🤖 Modèles ML chargés")
                else:
                    print(f"{Fore.YELLOW}🤖 Pas de modèles pré-entraînés")
                
                # Auto-entraînement si configuré
                if self.config.get('services', {}).get('ml', {}).get('auto_train', False):
                    self.entrainer_ml_auto()
                
                self.services_actifs['ml'] = True
                return True
                
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur initialisation ML: {e}")
                return False
        return True
    
    def entrainer_ml_auto(self):
        """Entraînement automatique des modèles ML"""
        try:
            print(f"{Fore.CYAN}🤖 Auto-entraînement ML...")
            alerts_data = self.ml_detector.load_training_data(days_back=30)
            
            if len(alerts_data) >= 100:
                self.ml_detector.train_models(alerts_data)
                print(f"{Fore.GREEN}✅ Entraînement ML terminé")
            else:
                print(f"{Fore.YELLOW}⚠️  Pas assez de données pour l'entraînement ML")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur auto-entraînement ML: {e}")
    
    def demarrer_monitoring(self):
        """Démarrer le service de monitoring"""
        if self.systeme_alertes and not self.services_actifs['monitoring']:
            try:
                self.systeme_alertes.demarrer_monitoring()
                self.services_actifs['monitoring'] = True
                print(f"{Fore.GREEN}✓ Service monitoring démarré")
                return True
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur démarrage monitoring: {e}")
                return False
        return True
    
    def demarrer_webapp(self):
        """Démarrer l'interface web"""
        if not self.services_actifs['webapp']:
            try:
                webapp_config = self.config.get('services', {}).get('webapp', {})
                port = webapp_config.get('port', 5000)
                host = webapp_config.get('host', '127.0.0.1')
                
                def run_webapp():
                    # Initialiser le système d'alertes pour webapp
                    from webapp import init_systeme_alertes
                    init_systeme_alertes(db_path=self.db_path, config_path=self.config_path)
                    # Importer et lancer webapp
                    from webapp import socketio, app
                    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
                
                thread = threading.Thread(target=run_webapp, daemon=True)
                thread.start()
                self.threads['webapp'] = thread
                self.services_actifs['webapp'] = True
                
                print(f"{Fore.GREEN}🌐 Interface web démarrée sur http://{host}:{port}")
                return True
                
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur démarrage webapp: {e}")
                return False
        return True
    
    def demarrer_api(self):
        """Démarrer l'API REST"""
        if not self.services_actifs['api']:
            try:
                api_config = self.config.get('services', {}).get('api', {})
                port = api_config.get('port', 5001)
                host = api_config.get('host', '127.0.0.1')
                
                def run_api():
                    # Initialiser les clés API et le système
                    from api_rest import init_api_keys_db, app
                    init_api_keys_db()
                    app.run(host=host, port=port, debug=False, use_reloader=False)
                
                thread = threading.Thread(target=run_api, daemon=True)
                thread.start()
                self.threads['api'] = thread
                self.services_actifs['api'] = True
                
                print(f"{Fore.GREEN}🔌 API REST démarrée sur http://{host}:{port}")
                return True
                
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur démarrage API: {e}")
                return False
        return True
    
    def arreter_services(self):
        """Arrêter tous les services"""
        print(f"{Fore.YELLOW}🛑 Arrêt des services...")
        
        # Arrêter le monitoring
        if self.systeme_alertes and self.services_actifs['monitoring']:
            self.systeme_alertes.arreter_monitoring()
            self.services_actifs['monitoring'] = False
        
        # Marquer les autres services comme arrêtés
        for service in ['webapp', 'api', 'ml']:
            self.services_actifs[service] = False
        
        self.running = False
        print(f"{Fore.YELLOW}✓ Services arrêtés")
    
    def afficher_statut(self):
        """Afficher le statut de tous les services"""
        print(f"\n{Fore.CYAN}📊 STATUT DES SERVICES")
        print("=" * 30)
        
        for service, actif in self.services_actifs.items():
            status = f"{Fore.GREEN}✅ Actif" if actif else f"{Fore.RED}❌ Inactif"
            print(f"  {service.capitalize():<12} : {status}")
        
        # Informations supplémentaires
        if self.ml_detector:
            ml_status = self.ml_detector.get_model_status()
            print(f"\n{Fore.CYAN}🤖 MACHINE LEARNING")
            print(f"  Modèles entraînés : {'✅ Oui' if ml_status['models_trained'] else '❌ Non'}")
            print(f"  Taille données    : {ml_status['training_data_size']}")
        
        if self.systeme_alertes:
            stats = self.systeme_alertes.obtenir_statistiques()
            print(f"\n{Fore.CYAN}📈 STATISTIQUES ALERTES")
            print(f"  Total             : {stats['globales']['total']}")
            print(f"  Non résolues      : {stats['globales']['non_resolues']}")
    
    def mode_cli(self, args):
        """Mode interface en ligne de commande"""
        if not self.initialiser_systeme():
            return False
        
        if args.command == 'list':
            alertes = self.systeme_alertes.lister_alertes(
                limite=args.limite,
                niveau=args.niveau,
                resolu=False if args.non_resolues else None
            )
            
            if alertes:
                from tabulate import tabulate
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
            stats = self.systeme_alertes.obtenir_statistiques()
            
            from tabulate import tabulate
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
        
        elif args.command == 'resolve':
            if self.systeme_alertes.marquer_resolu(args.id):
                print(f"{Fore.GREEN}✓ Alerte {args.id} marquée comme résolue")
            else:
                print(f"{Fore.RED}❌ Alerte {args.id} introuvable")
        
        return True
    
    def mode_daemon(self):
        """Mode service daemon"""
        if not self.initialiser_systeme():
            return False
        
        self.initialiser_ml()
        
        # Démarrer le monitoring
        if not self.demarrer_monitoring():
            return False
        
        self.running = True
        print(f"{Fore.GREEN}🔄 Mode daemon actif - Ctrl+C pour arrêter")
        
        # Gestion des signaux
        def signal_handler(signum, frame):
            print(f"\n{Fore.YELLOW}⏹️  Signal reçu, arrêt en cours...")
            self.arreter_services()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.arreter_services()
        
        return True
    
    def mode_web(self, port=None):
        """Mode interface web uniquement"""
        if not self.initialiser_systeme():
            return False
        
        port = port or self.config.get('services', {}).get('webapp', {}).get('port', 5000)
        
        print(f"{Fore.GREEN}🌐 Démarrage interface web sur port {port}")
        
        try:
            # Initialiser le système d'alertes pour webapp
            from webapp import init_systeme_alertes, socketio, app
            init_systeme_alertes(db_path=self.db_path, config_path=self.config_path)
            socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur démarrage web: {e}")
            return False
        
        return True
    
    def mode_api(self, port=None):
        """Mode API REST uniquement"""
        if not self.initialiser_systeme():
            return False
        
        port = port or self.config.get('services', {}).get('api', {}).get('port', 5001)
        
        print(f"{Fore.GREEN}🔌 Démarrage API REST sur port {port}")
        
        try:
            # Initialiser les clés API et le système
            from api_rest import init_api_keys_db, app
            init_api_keys_db()
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur démarrage API: {e}")
            return False
        
        return True
    
    def mode_ml(self, args):
        """Mode Machine Learning"""
        if not self.initialiser_systeme():
            return False
        
        if not self.initialiser_ml():
            return False
        
        if args.ml_command == 'train':
            print(f"{Fore.CYAN}🤖 Entraînement des modèles ML...")
            try:
                alerts_data = self.ml_detector.load_training_data(days_back=args.days)
                if len(alerts_data) < 100:
                    print(f"{Fore.RED}❌ Pas assez de données (minimum 100, trouvé {len(alerts_data)})")
                    return False
                
                self.ml_detector.train_models(alerts_data)
                print(f"{Fore.GREEN}✅ Entraînement terminé avec succès")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur lors de l'entraînement: {e}")
                return False
        
        elif args.ml_command == 'status':
            status = self.ml_detector.get_model_status()
            print(f"\n{Fore.CYAN}📊 STATUT DES MODÈLES ML")
            print("=" * 35)
            print(f"Modèles entraînés: {'✅ Oui' if status['models_trained'] else '❌ Non'}")
            print(f"Taille données entraînement: {status['training_data_size']}")
            print(f"Dernier entraînement: {status['last_training'] or 'Jamais'}")
        
        elif args.ml_command == 'report':
            print(f"{Fore.CYAN}📊 Génération du rapport ML...")
            report = self.ml_detector.generate_analytics_report()
            
            if 'error' not in report:
                print(f"\n{Fore.GREEN}📈 RAPPORT D'ANALYSE ML")
                print("=" * 40)
                print(f"Période: {report['period']}")
                print(f"Alertes analysées: {report['total_alerts_analyzed']}")
                print(f"Anomalies détectées: {report['anomalies_detected']}")
                print(f"Taux d'anomalies: {report['anomaly_rate']:.1%}")
            else:
                print(f"{Fore.RED}❌ {report['error']}")
        
        return True
    
    def mode_all(self):
        """Mode tous services simultanément"""
        if not self.initialiser_systeme():
            return False
        
        self.initialiser_ml()
        
        print(f"{Fore.GREEN}🚀 Démarrage de tous les services...")
        
        # Démarrer tous les services
        services_ok = True
        services_ok &= self.demarrer_monitoring()
        services_ok &= self.demarrer_webapp() 
        services_ok &= self.demarrer_api()
        
        if not services_ok:
            print(f"{Fore.RED}❌ Erreur démarrage des services")
            return False
        
        self.running = True
        
        # Gestion des signaux pour arrêt propre
        def signal_handler(signum, frame):
            print(f"\n{Fore.YELLOW}⏹️  Arrêt de tous les services...")
            self.arreter_services()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print(f"{Fore.GREEN}✅ Tous les services démarrés")
        self.afficher_statut()
        print(f"\n{Fore.CYAN}Ctrl+C pour arrêter tous les services")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.arreter_services()
        
        return True

def main():
    """Point d'entrée principal unifié"""
    parser = argparse.ArgumentParser(
        description="🚨 Système d'Alertes Sécurité - Interface Unifiée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MODES D'UTILISATION:
  cli      Interface en ligne de commande pour gestion des alertes
  daemon   Service de monitoring continu en arrière-plan  
  web      Dashboard web interactif avec interface graphique
  api      Serveur API REST pour intégrations externes
  ml       Machine Learning et analyse d'anomalies
  all      Tous les services simultanément

EXEMPLES:
  %(prog)s cli list --niveau ERROR --non-resolues
  %(prog)s daemon
  %(prog)s web --port 8080
  %(prog)s api --port 8081  
  %(prog)s ml train --days 30
  %(prog)s all
        """
    )
    
    # Arguments globaux
    parser.add_argument("--config", default="config.json", help="Fichier de configuration")
    parser.add_argument("--db", default="alertes.db", help="Base de données SQLite")
    parser.add_argument("--version", action="version", version="Système d'Alertes Sécurité 3.0.0")
    
    # Sous-commandes principales (modes)
    subparsers = parser.add_subparsers(dest='mode', help='Mode d\'utilisation')
    
    # Mode CLI
    cli_parser = subparsers.add_parser('cli', help='Interface en ligne de commande')
    cli_subparsers = cli_parser.add_subparsers(dest='command')
    
    # CLI: list
    list_cmd = cli_subparsers.add_parser('list', help='Lister les alertes')
    list_cmd.add_argument('--niveau', choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    list_cmd.add_argument('--non-resolues', action='store_true')
    list_cmd.add_argument('--limite', type=int, default=20)
    
    # CLI: stats  
    cli_subparsers.add_parser('stats', help='Statistiques des alertes')
    
    # CLI: resolve
    resolve_cmd = cli_subparsers.add_parser('resolve', help='Marquer une alerte comme résolue')
    resolve_cmd.add_argument('id', help='ID de l\'alerte')
    
    # Mode Daemon
    subparsers.add_parser('daemon', help='Service de monitoring continu')
    
    # Mode Web
    web_parser = subparsers.add_parser('web', help='Interface web')
    web_parser.add_argument('--port', type=int, default=5000, help='Port web')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host web')
    
    # Mode API
    api_parser = subparsers.add_parser('api', help='Serveur API REST')
    api_parser.add_argument('--port', type=int, default=5001, help='Port API')
    api_parser.add_argument('--host', default='0.0.0.0', help='Host API')
    
    # Mode ML
    ml_parser = subparsers.add_parser('ml', help='Machine Learning')
    ml_subparsers = ml_parser.add_subparsers(dest='ml_command')
    
    train_cmd = ml_subparsers.add_parser('train', help='Entraîner les modèles')
    train_cmd.add_argument('--days', type=int, default=30, help='Jours de données')
    
    ml_subparsers.add_parser('status', help='Statut des modèles ML')
    ml_subparsers.add_parser('report', help='Rapport d\'analyse ML')
    
    # Mode All
    subparsers.add_parser('all', help='Tous les services simultanément')
    
    # Mode Status (pour diagnostic)
    subparsers.add_parser('status', help='Statut de tous les services')
    
    args = parser.parse_args()
    
    # Si aucun mode spécifié, afficher l'aide
    if not args.mode:
        parser.print_help()
        return 1
    
    # Initialiser le système principal
    principal = AlertesPrincipal(config_path=args.config, db_path=args.db)
    
    try:
        # Dispatcher selon le mode
        if args.mode == 'cli':
            return 0 if principal.mode_cli(args) else 1
        
        elif args.mode == 'daemon':
            return 0 if principal.mode_daemon() else 1
        
        elif args.mode == 'web':
            return 0 if principal.mode_web(args.port) else 1
        
        elif args.mode == 'api':
            return 0 if principal.mode_api(args.port) else 1
        
        elif args.mode == 'ml':
            return 0 if principal.mode_ml(args) else 1
        
        elif args.mode == 'all':
            return 0 if principal.mode_all() else 1
        
        elif args.mode == 'status':
            principal.initialiser_systeme()
            principal.initialiser_ml()
            principal.afficher_statut()
            return 0
        
        else:
            print(f"{Fore.RED}❌ Mode inconnu: {args.mode}")
            return 1
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Interruption utilisateur")
        return 0
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())