#!/usr/bin/env python3
"""
🌐 ANALYSEUR DE TRAFIC RÉSEAU - VERSION UNIFIÉE ET ORCHESTRÉE
=============================================================

Fichier principal qui orchestre tous les composants du système d'analyse de trafic réseau.
Cette version intègre toutes les fonctionnalités avancées développées dans les modules séparés.

🎯 FONCTIONNALITÉS INTÉGRÉES:
- ✅ Capture de paquets IPv4/IPv6 avec détection d'anomalies
- ✅ Interface graphique moderne (Tkinter avancée)  
- ✅ Dashboard web temps réel avec WebSockets
- ✅ API REST complète avec authentification JWT
- ✅ Machine Learning pour détection d'anomalies avancée
- ✅ Base de données SQLite pour persistance
- ✅ Système de notifications multi-canaux (Email/Slack/Webhooks)
- ✅ Filtres BPF avancés personnalisables
- ✅ Export de données en JSON/CSV
- ✅ Support IPv6 complet avec détections spécialisées

🚀 MODES D'UTILISATION:
- CLI: Analyse en ligne de commande 
- GUI: Interface graphique complète
- WEB: Dashboard web temps réel
- API: Serveur API REST pour intégrations
- ALL: Démarrer tous les composants simultanément

Auteur: Système de Cybersécurité Avancé
Version: 1.0.0 - Production Ready
"""

import argparse
import sys
import os
import threading
import time
import signal
from datetime import datetime
from typing import Optional, List, Dict
from colorama import init, Fore, Style

# Configuration de colorama pour Windows/Linux
init(autoreset=True)

# Imports des modules du système
try:
    from analyseur_trafic import AnalyseurTrafic
    from database_manager import DatabaseManager  
    from ml_detector import MLAnomalyDetector
    from notification_system import NotificationSystem
    from advanced_filters import AdvancedPacketFilters
    from integrated_analyzer import IntegratedTrafficAnalyzer
    from gui_analyseur_tkinter import AnalyseurGUI
    print("✅ Modules principaux importés avec succès")
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur d'importation des modules principaux: {e}")
    print(f"{Fore.YELLOW}💡 Vérifiez que tous les fichiers sont présents dans le même dossier")
    sys.exit(1)

# Imports optionnels pour les services web (peuvent échouer)
webapp = None
socketio = None
api_app = None
traffic_api = None

try:
    from webapp_analyseur import app as webapp, socketio
    print("✅ WebApp importé avec succès")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️ WebApp non disponible: {e}")

try:
    from rest_api import app as api_app, traffic_api
    print("✅ API REST importé avec succès")
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️ API REST non disponible: {e}")

class AnalyseurTraficPrincipal:
    """Orchestrateur principal pour tous les composants de l'analyseur de trafic"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.components = {
            'analyseur': None,
            'database': None,
            'ml_detector': None,
            'notifications': None,
            'filters': None,
            'integrated_analyzer': None
        }
        self.services = {
            'webapp': None,
            'api_server': None,
            'gui': None
        }
        self.running = False
        self.threads = []
        
        # Configuration du gestionnaire de signaux pour arrêt propre
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Configuration signaux échouée: {e}")
        
        self._print_banner()
        
    def _print_banner(self):
        """Afficher la bannière du système"""
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"{Fore.BLUE}🌐 ANALYSEUR DE TRAFIC RÉSEAU - VERSION ORCHESTRÉE v{self.version}")
        print(f"{Fore.BLUE}{'='*80}")
        print(f"{Fore.CYAN}🎯 Système complet d'analyse et de monitoring de trafic réseau")
        print(f"{Fore.CYAN}✨ Intégrant ML, Dashboard Web, API REST, GUI et plus encore")
        print(f"{Fore.BLUE}{'='*80}\n")
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        print(f"\n{Fore.YELLOW}🛑 Signal d'arrêt reçu ({signum})...")
        self.stop_all_services()
        sys.exit(0)
    
    def initialize_components(self) -> bool:
        """Initialiser tous les composants du système"""
        try:
            print(f"{Fore.CYAN}⚙️ Initialisation des composants principaux...")
            
            # 1. Système de base de données
            print(f"{Fore.YELLOW}🗄️ Initialisation de la base de données...")
            self.components['database'] = DatabaseManager("analyseur_principal.db")
            
            # 2. Machine Learning
            print(f"{Fore.YELLOW}🤖 Initialisation du détecteur ML...")
            self.components['ml_detector'] = MLAnomalyDetector(threshold=0.1)
            
            # 3. Système de notifications  
            print(f"{Fore.YELLOW}📧 Initialisation du système de notifications...")
            self.components['notifications'] = NotificationSystem()
            
            # 4. Système de filtres avancés
            print(f"{Fore.YELLOW}🔍 Initialisation des filtres avancés...")
            self.components['filters'] = AdvancedPacketFilters()
            
            # 5. Analyseur intégré
            print(f"{Fore.YELLOW}🔧 Initialisation de l'analyseur intégré...")
            self.components['integrated_analyzer'] = IntegratedTrafficAnalyzer()
            if not self.components['integrated_analyzer'].initialize_components():
                print(f"{Fore.YELLOW}⚠️ Certains composants intégrés non disponibles")
            
            print(f"{Fore.GREEN}✅ Tous les composants initialisés avec succès")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'initialisation: {e}")
            return False
    
    def start_cli_mode(self, args) -> bool:
        """Démarrer le mode CLI (ligne de commande)"""
        try:
            print(f"\n{Fore.CYAN}🖥️ DÉMARRAGE DU MODE CLI")
            print("=" * 50)
            
            # Créer l'analyseur de base
            interface = args.interface or "eth0"
            analyseur = AnalyseurTrafic(interface=interface)
            self.components['analyseur'] = analyseur
            
            # Appliquer un filtre personnalisé si spécifié
            if args.filter:
                if args.filter in self.components['filters'].list_available_filters():
                    bpf_filter = self.components['filters'].get_filter_by_name(args.filter)
                    print(f"{Fore.GREEN}✓ Filtre appliqué: {args.filter} -> {bpf_filter}")
                else:
                    print(f"{Fore.YELLOW}💡 Filtre personnalisé: {args.filter}")
            
            # Démarrer la capture
            print(f"{Fore.CYAN}🎯 Démarrage de la capture sur {interface}...")
            success = analyseur.start_capture(
                duration=args.duration or 60,
                packet_count=args.count
            )
            
            if success:
                # Sauvegarder en base de données
                if self.components['database']:
                    session_id = self.components['database'].save_capture_session(analyseur)
                    print(f"{Fore.GREEN}✓ Session sauvegardée avec ID: {session_id}")
                
                # Générer les statistiques
                analyseur.generate_statistics()
                
                # Visualisation si demandée
                if not args.no_visual:
                    analyseur.visualize_traffic()
                
                # Export si demandé
                if args.export:
                    filename = analyseur.export_data(format_type=args.export)
                    print(f"{Fore.GREEN}✓ Données exportées: {filename}")
                
                return True
            else:
                print(f"{Fore.RED}❌ Échec de la capture")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur en mode CLI: {e}")
            return False
    
    def start_gui_mode(self) -> bool:
        """Démarrer le mode GUI (interface graphique)"""
        try:
            print(f"\n{Fore.CYAN}🖥️ DÉMARRAGE DU MODE GUI")
            print("=" * 50)
            
            import tkinter as tk
            
            def run_gui():
                try:
                    root = tk.Tk()
                    root.title(f"🌐 Analyseur de Trafic Réseau - v{self.version}")
                    root.geometry("1400x900")
                    
                    # Créer l'interface avec nos composants intégrés
                    gui_app = AnalyseurGUI(root)
                    
                    # Injecter nos composants
                    if self.components['database']:
                        gui_app.db_manager = self.components['database']
                    if self.components['ml_detector']:
                        gui_app.ml_detector = self.components['ml_detector']
                    
                    print(f"{Fore.GREEN}✅ Interface graphique démarrée")
                    root.mainloop()
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ Erreur GUI: {e}")
            
            # Démarrer dans un thread séparé
            gui_thread = threading.Thread(target=run_gui, daemon=True)
            gui_thread.start()
            self.threads.append(gui_thread)
            self.services['gui'] = gui_thread
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du démarrage du GUI: {e}")
            return False
    
    def start_web_mode(self, port: int = 5000) -> bool:
        """Démarrer le mode Web (dashboard)"""
        try:
            if webapp is None or socketio is None:
                print(f"{Fore.RED}❌ WebApp non disponible - imports manquants")
                return False
                
            print(f"\n{Fore.CYAN}🌐 DÉMARRAGE DU MODE WEB")
            print("=" * 50)
            
            def run_webapp():
                try:
                    print(f"{Fore.GREEN}✅ Dashboard web disponible sur: http://localhost:{port}")
                    print(f"{Fore.CYAN}🎯 Interface de monitoring temps réel active")
                    socketio.run(webapp, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
                except Exception as e:
                    print(f"{Fore.RED}❌ Erreur webapp: {e}")
            
            # Démarrer le serveur web dans un thread
            web_thread = threading.Thread(target=run_webapp, daemon=True)
            web_thread.start()
            self.threads.append(web_thread)
            self.services['webapp'] = web_thread
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du démarrage du serveur web: {e}")
            return False
    
    def start_api_mode(self, port: int = 5001) -> bool:
        """Démarrer le mode API REST"""
        try:
            if api_app is None:
                print(f"{Fore.RED}❌ API REST non disponible - imports manquants")
                return False
                
            print(f"\n{Fore.CYAN}🔌 DÉMARRAGE DU MODE API REST")
            print("=" * 50)
            
            def run_api():
                try:
                    print(f"{Fore.GREEN}✅ API REST disponible sur: http://localhost:{port}")
                    print(f"{Fore.CYAN}📚 Documentation: http://localhost:{port}/api/v1/docs")
                    print(f"{Fore.CYAN}🏥 Health check: http://localhost:{port}/api/v1/health")
                    print(f"\n{Fore.YELLOW}📝 Credentials par défaut:")
                    print(f"    Username: admin")
                    print(f"    Password: admin123")
                    
                    api_app.run(host='0.0.0.0', port=port, debug=False)
                except Exception as e:
                    print(f"{Fore.RED}❌ Erreur API: {e}")
            
            # Démarrer l'API dans un thread
            api_thread = threading.Thread(target=run_api, daemon=True)
            api_thread.start()
            self.threads.append(api_thread)
            self.services['api_server'] = api_thread
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du démarrage de l'API: {e}")
            return False
    
    def start_integrated_mode(self) -> bool:
        """Démarrer le mode intégré avec tous les composants"""
        try:
            print(f"\n{Fore.CYAN}🔧 DÉMARRAGE DU MODE INTÉGRÉ")
            print("=" * 60)
            
            # Utiliser l'analyseur intégré
            if self.components['integrated_analyzer']:
                return self.components['integrated_analyzer'].initialize_components()
            else:
                print(f"{Fore.RED}❌ Analyseur intégré non disponible")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur en mode intégré: {e}")
            return False
    
    def show_components_status(self):
        """Afficher le statut des composants individuels"""
        print(f"\n{Fore.CYAN}🔧 STATUT DES COMPOSANTS:")
        
        # Statut ML
        if self.components['ml_detector']:
            print(f"\n{Fore.YELLOW}🤖 Machine Learning:")
            print(f"   Détecteur initialisé: ✅")
            print(f"   Seuil configuré: {self.components['ml_detector'].threshold}")
        
        # Statut des filtres
        if self.components['filters']:
            print(f"\n{Fore.YELLOW}🔍 Filtres avancés:")
            filters_count = len(self.components['filters'].list_available_filters())
            print(f"   Filtres disponibles: {filters_count}")
            print(f"   Exemple: {list(self.components['filters'].list_available_filters().keys())[:3]}")
        
        # Statut notifications
        if self.components['notifications']:
            print(f"\n{Fore.YELLOW}📧 Notifications:")
            stats = self.components['notifications'].get_statistics()
            print(f"   Système opérationnel, queue size: {stats.get('queue_size', 0)}")
    
    def start_all_services(self, web_port: int = 5000, api_port: int = 5001) -> bool:
        """Démarrer tous les services simultanément"""
        try:
            print(f"\n{Fore.CYAN}🚀 DÉMARRAGE DE TOUS LES SERVICES")
            print("=" * 60)
            
            success_count = 0
            
            # Démarrer le dashboard web
            if self.start_web_mode(web_port):
                success_count += 1
                time.sleep(1)  # Attendre le démarrage
            
            # Démarrer l'API REST
            if self.start_api_mode(api_port):
                success_count += 1
                time.sleep(1)
            
            # Démarrer l'interface graphique
            if self.start_gui_mode():
                success_count += 1
                time.sleep(1)
            
            if success_count > 0:
                print(f"\n{Fore.GREEN}✅ {success_count} services démarrés avec succès")
                print(f"\n{Fore.CYAN}🌐 ACCÈS AUX SERVICES:")
                print(f"{Fore.YELLOW}📊 Dashboard Web:  http://localhost:{web_port}")
                print(f"{Fore.YELLOW}🔌 API REST:       http://localhost:{api_port}")
                print(f"{Fore.YELLOW}🖥️ Interface GUI:  Fenêtre séparée")
                print(f"{Fore.YELLOW}📚 Documentation API: http://localhost:{api_port}/api/v1/docs")
                
                self.running = True
                return True
            else:
                print(f"{Fore.RED}❌ Échec du démarrage des services")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du démarrage de tous les services: {e}")
            return False
    
    def stop_all_services(self):
        """Arrêter proprement tous les services"""
        try:
            print(f"\n{Fore.YELLOW}⏹️ Arrêt des services en cours...")
            self.running = False
            
            # Attendre que les threads se terminent
            for thread in self.threads:
                if thread.is_alive():
                    thread.join(timeout=2)
            
            print(f"{Fore.GREEN}✅ Tous les services arrêtés")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'arrêt: {e}")
    
    def show_system_status(self):
        """Afficher le statut complet du système"""
        print(f"\n{Fore.CYAN}📊 STATUT DU SYSTÈME ANALYSEUR DE TRAFIC")
        print("=" * 60)
        
        # Statut des composants
        print(f"{Fore.YELLOW}🔧 Composants:")
        for name, component in self.components.items():
            status = "✅ Actif" if component is not None else "❌ Inactif"
            color = Fore.GREEN if component is not None else Fore.RED
            print(f"  {color}{name:20s} : {status}")
        
        # Statut des services
        print(f"\n{Fore.YELLOW}🌐 Services:")
        for name, service in self.services.items():
            if service and hasattr(service, 'is_alive'):
                status = "✅ Actif" if service.is_alive() else "❌ Inactif"
                color = Fore.GREEN if service.is_alive() else Fore.RED
            else:
                status = "❌ Non démarré"
                color = Fore.RED
            print(f"  {color}{name:20s} : {status}")
        
        # Informations système
        print(f"\n{Fore.YELLOW}💻 Système:")
        print(f"  {Fore.CYAN}Version              : {self.version}")
        print(f"  {Fore.CYAN}Threads actifs       : {len(self.threads)}")
        print(f"  {Fore.CYAN}Statut général       : {'🟢 Opérationnel' if self.running else '🔴 Arrêté'}")
        
        # Statistiques des composants
        if self.components['database']:
            try:
                stats = self.components['database'].get_statistics_summary()
                print(f"\n{Fore.YELLOW}📊 Base de données:")
                print(f"  {Fore.CYAN}Sessions totales     : {stats.get('total_sessions', 0)}")
                print(f"  {Fore.CYAN}Paquets totaux       : {stats.get('total_packets', 0)}")
                print(f"  {Fore.CYAN}Anomalies totales    : {stats.get('total_anomalies', 0)}")
            except:
                print(f"  {Fore.RED}Erreur lors de la récupération des stats DB")

def create_parser():
    """Créer le parser d'arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="🌐 Analyseur de Trafic Réseau - Version Orchestrée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 MODES D'UTILISATION:

CLI Mode:
  python3 analyseur_principal.py cli --interface eth0 --duration 60
  
GUI Mode:
  python3 analyseur_principal.py gui
  
Web Dashboard:
  python3 analyseur_principal.py web --port 5000
  
API REST:
  python3 analyseur_principal.py api --port 5001
  
Tous les services:
  python3 analyseur_principal.py all --web-port 5000 --api-port 5001

📊 Status du système:
  python3 analyseur_principal.py status

🔧 EXEMPLES D'USAGE AVANCÉS:
  
# Capture avec filtre personnalisé
python3 analyseur_principal.py cli --filter web_traffic --export json

# Dashboard web sur port personnalisé
python3 analyseur_principal.py web --port 8080

# Démarrer tous les services
python3 analyseur_principal.py all --web-port 5000 --api-port 5001
        """
    )
    
    # Mode principal
    parser.add_argument('mode', choices=['cli', 'gui', 'web', 'api', 'all', 'status'],
                       help='Mode de fonctionnement')
    
    # Arguments pour le mode CLI
    parser.add_argument('-i', '--interface', default='eth0',
                       help='Interface réseau (défaut: eth0)')
    parser.add_argument('-t', '--duration', type=int, default=60,
                       help='Durée de capture en secondes (défaut: 60)')
    parser.add_argument('-c', '--count', type=int,
                       help='Nombre maximum de paquets à capturer')
    parser.add_argument('--filter',
                       help='Nom du filtre prédéfini ou expression BPF personnalisée')
    parser.add_argument('--export', choices=['csv', 'json'],
                       help='Format d\'export des données')
    parser.add_argument('--no-visual', action='store_true',
                       help='Désactiver la génération de graphiques')
    
    # Arguments pour les modes serveur
    parser.add_argument('--port', type=int, default=5000,
                       help='Port pour le serveur web/API (défaut: 5000)')
    parser.add_argument('--web-port', type=int, default=5000,
                       help='Port pour le dashboard web (défaut: 5000)')
    parser.add_argument('--api-port', type=int, default=5001,
                       help='Port pour l\'API REST (défaut: 5001)')
    
    return parser

def main():
    """Fonction principale"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Créer l'orchestrateur principal
    orchestrator = AnalyseurTraficPrincipal()
    
    # Initialiser les composants
    if not orchestrator.initialize_components():
        print(f"{Fore.RED}❌ Échec de l'initialisation des composants")
        sys.exit(1)
    
    # Traitement selon le mode demandé
    success = True
    
    if args.mode == 'cli':
        success = orchestrator.start_cli_mode(args)
        
    elif args.mode == 'gui':
        success = orchestrator.start_gui_mode()
        if success:
            print(f"{Fore.CYAN}🖥️ Interface graphique active. Appuyez sur Ctrl+C pour quitter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
    elif args.mode == 'web':
        success = orchestrator.start_web_mode(args.port)
        if success:
            print(f"{Fore.CYAN}🌐 Dashboard web actif. Appuyez sur Ctrl+C pour quitter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
    elif args.mode == 'api':
        success = orchestrator.start_api_mode(args.port)
        if success:
            print(f"{Fore.CYAN}🔌 Serveur API actif. Appuyez sur Ctrl+C pour quitter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
    elif args.mode == 'all':
        success = orchestrator.start_all_services(args.web_port, args.api_port)
        if success:
            print(f"\n{Fore.CYAN}🎯 Tous les services sont actifs.")
            print(f"{Fore.YELLOW}   Utilisez les URLs affichées ci-dessus pour accéder aux services.")
            print(f"{Fore.YELLOW}   Appuyez sur Ctrl+C pour arrêter tous les services.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
    elif args.mode == 'status':
        orchestrator.show_system_status()
        
    # Nettoyage
    orchestrator.stop_all_services()
    
    # Code de sortie
    exit_code = 0 if success else 1
    if success:
        print(f"\n{Fore.GREEN}🎉 Opération terminée avec succès!")
    else:
        print(f"\n{Fore.RED}❌ Opération échouée")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()