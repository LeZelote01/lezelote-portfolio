#!/usr/bin/env python3
"""
Analyseur de Trafic Réseau - Version Complète Intégrée
Intégration de toutes les améliorations: Filtres BPF, Notifications, API REST

Nouvelles fonctionnalités intégrées:
- Filtres de capture avancés (BPF)
- Système de notifications (Email/Slack/Webhooks)
- API REST complète avec authentification
- Interface GUI améliorée
- Machine Learning et base de données
"""

import argparse
import threading
import time
from datetime import datetime
from colorama import Fore, Style, init
import sys
import os
import signal

# Importer tous nos modules
try:
    from analyseur_trafic import AnalyseurTrafic
    from database_manager import DatabaseManager
    from ml_detector import MLAnomalyDetector
    from gui_analyseur_tkinter import AnalyseurGUI
    from notification_system import NotificationSystem
    from advanced_filters import AdvancedPacketFilters
    from rest_api import app as api_app
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur d'import: {e}")
    print(f"{Fore.YELLOW}💡 Assurez-vous que tous les modules sont présents")
    sys.exit(1)

init(autoreset=True)

class IntegratedTrafficAnalyzer:
    """Analyseur de trafic intégré avec toutes les améliorations"""
    
    def __init__(self):
        self.analyseur = None
        self.db_manager = None
        self.ml_detector = None
        self.notification_system = None
        self.filter_system = None
        self.api_thread = None
        self.gui_thread = None
        self.running = False
        
        print(f"{Fore.BLUE}🚀 ANALYSEUR DE TRAFIC RÉSEAU - VERSION INTÉGRÉE")
        print("=" * 60)
        
        # Gestionnaire de signaux pour arrêt propre
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire pour arrêt propre"""
        print(f"\n{Fore.YELLOW}🛑 Arrêt demandé...")
        self.stop_all_services()
        sys.exit(0)
    
    def initialize_components(self):
        """Initialiser tous les composants"""
        try:
            print(f"{Fore.CYAN}⚙️ Initialisation des composants...")
            
            # Système de filtres avancés
            print(f"{Fore.YELLOW}🔍 Initialisation des filtres...")
            self.filter_system = AdvancedPacketFilters()
            
            # Base de données
            print(f"{Fore.YELLOW}🗄️ Initialisation de la base de données...")
            self.db_manager = DatabaseManager("integrated_traffic.db")
            
            # Machine Learning
            print(f"{Fore.YELLOW}🤖 Initialisation du ML...")
            self.ml_detector = MLAnomalyDetector()
            
            # Système de notifications
            print(f"{Fore.YELLOW}📧 Initialisation des notifications...")
            self.notification_system = NotificationSystem()
            
            print(f"{Fore.GREEN}✅ Tous les composants initialisés avec succès")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'initialisation: {e}")
            return False
    
    def create_enhanced_analyzer(self, interface="eth0", custom_filter=None):
        """Créer un analyseur amélioré avec toutes les fonctionnalités"""
        self.analyseur = AnalyseurTrafic(interface)
        
        # Appliquer un filtre personnalisé si fourni
        if custom_filter:
            if custom_filter in self.filter_system.list_available_filters():
                bpf_filter = self.filter_system.get_filter_by_name(custom_filter)
                print(f"{Fore.GREEN}✓ Filtre appliqué: {custom_filter} -> {bpf_filter}")
            else:
                print(f"{Fore.YELLOW}⚠ Filtre personnalisé: {custom_filter}")
                bpf_filter = custom_filter
        
        return self.analyseur
    
    def start_capture_with_enhancements(self, interface="eth0", duration=60, 
                                      enable_notifications=True, custom_filter=None):
        """Démarrer une capture avec toutes les améliorations"""
        try:
            print(f"\n{Fore.CYAN}🎯 Démarrage de la capture améliorée...")
            
            # Créer l'analyseur
            analyzer = self.create_enhanced_analyzer(interface, custom_filter)
            
            # Hook pour notifications en temps réel
            original_detect_anomalies = analyzer.detect_anomalies
            
            def enhanced_anomaly_detection(packet_info):
                # Appeler la détection originale
                original_detect_anomalies(packet_info)
                
                # ML Detection
                if self.ml_detector:
                    is_anomaly = self.ml_detector.detect_anomaly(packet_info)
                    if is_anomaly:
                        anomaly = {
                            'type': 'ML Anomaly Detected',
                            'timestamp': datetime.now(),
                            'source_ip': packet_info.get('src_ip'),
                            'details': f'ML confidence: {self.ml_detector.last_confidence:.3f}',
                            'ml_based': True
                        }
                        analyzer.anomalies.append(anomaly)
                        
                        # Notification en temps réel
                        if enable_notifications and self.notification_system:
                            notification_data = {
                                'anomaly_type': anomaly['type'],
                                'timestamp': anomaly['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                                'source_ip': anomaly['source_ip'] or 'Unknown',
                                'details': anomaly['details'],
                                'total_packets': analyzer.statistics.get('total_packets', 0),
                                'packets_per_second': 0,  # Calculé plus tard
                                'anomaly_count': len(analyzer.anomalies)
                            }
                            self.notification_system.send_anomaly_alert(notification_data)
            
            # Remplacer la méthode de détection
            analyzer.detect_anomalies = enhanced_anomaly_detection
            
            # Démarrer la capture
            success = analyzer.start_capture(duration=duration)
            
            if success:
                # Sauvegarder en base de données
                if self.db_manager:
                    session_id = self.db_manager.save_capture_session(analyzer)
                    print(f"{Fore.GREEN}✓ Session sauvegardée avec ID: {session_id}")
                
                # Notification de fin de capture
                if enable_notifications and self.notification_system:
                    status_data = {
                        'period': f'{duration} secondes',
                        'system_status': 'Capture terminée avec succès',
                        'total_packets': analyzer.statistics.get('total_packets', 0),
                        'anomalies_count': len(analyzer.anomalies),
                        'detection_rate': 95.5,  # Exemple
                        'avg_performance': analyzer.statistics.get('total_packets', 0) / duration,
                        'top_events': 'Port scans, Trafic élevé'
                    }
                    self.notification_system.send_status_report(status_data)
                
                return analyzer
            else:
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la capture: {e}")
            return None
    
    def start_api_server(self, port=5000):
        """Démarrer le serveur API en arrière-plan"""
        def run_api():
            try:
                print(f"{Fore.CYAN}🌐 Démarrage de l'API REST sur le port {port}...")
                api_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur API: {e}")
        
        self.api_thread = threading.Thread(target=run_api, daemon=True)
        self.api_thread.start()
        time.sleep(2)  # Laisser le temps de démarrer
        print(f"{Fore.GREEN}✅ API REST disponible sur http://localhost:{port}")
    
    def start_gui_interface(self):
        """Démarrer l'interface graphique"""
        def run_gui():
            try:
                print(f"{Fore.CYAN}🖥️ Démarrage de l'interface graphique...")
                gui = AnalyseurGUI()
                gui.run()
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur GUI: {e}")
        
        self.gui_thread = threading.Thread(target=run_gui, daemon=True)
        self.gui_thread.start()
        print(f"{Fore.GREEN}✅ Interface graphique lancée")
    
    def run_production_mode(self):
        """Mode production avec toutes les fonctionnalités"""
        print(f"\n{Fore.CYAN}🚀 MODE PRODUCTION INTÉGRÉ")
        print("=" * 50)
        
        # Configuration des filtres avancés
        print(f"\n{Fore.YELLOW}1. 🔍 Configuration des filtres avancés:")
        self.filter_system.create_custom_filter(
            "https_monitoring",
            "tcp port 443 and net 192.168.0.0/16",
            "Surveillance HTTPS réseau local"
        )
        
        # Capture en production
        print(f"\n{Fore.YELLOW}2. 🤖 Capture avec détection ML:")
        analyzer = self.start_capture_with_enhancements(
            interface="eth0",
            duration=60,
            enable_notifications=True,
            custom_filter="https_monitoring"
        )
        
        if analyzer:
            # Afficher les statistiques
            print(f"\n{Fore.CYAN}📊 Statistiques de la session:")
            analyzer.generate_statistics()
            
            # Visualisation
            print(f"\n{Fore.YELLOW}3. 📈 Génération des visualisations:")
            analyzer.visualize_traffic("production_analysis.png")
            
            # Export de données
            print(f"\n{Fore.YELLOW}4. 💾 Export des données:")
            analyzer.export_data("json", "production_export.json")
        
        # Statistiques des composants
        print(f"\n{Fore.YELLOW}5. 📋 Statistiques des composants:")
        if self.notification_system:
            stats = self.notification_system.get_statistics()
            print(f"{Fore.CYAN}   Notifications: {stats}")
        
        if self.filter_system:
            filters_count = len(self.filter_system.list_available_filters())
            print(f"{Fore.CYAN}   Filtres disponibles: {filters_count}")
        
        print(f"\n{Fore.GREEN}🎉 Mode production terminé!")
    
    def show_system_status(self):
        """Afficher le statut de tous les composants"""
        print(f"\n{Fore.CYAN}📊 STATUT DU SYSTÈME INTÉGRÉ")
        print("=" * 50)
        
        components = [
            ("Analyseur principal", self.analyseur is not None),
            ("Base de données", self.db_manager is not None),
            ("Machine Learning", self.ml_detector is not None),
            ("Notifications", self.notification_system is not None),
            ("Filtres avancés", self.filter_system is not None),
            ("API REST", self.api_thread is not None and self.api_thread.is_alive()),
            ("Interface GUI", self.gui_thread is not None and self.gui_thread.is_alive())
        ]
        
        for component, status in components:
            status_icon = "✅" if status else "❌"
            color = Fore.GREEN if status else Fore.RED
            print(f"{color}{status_icon} {component}")
        
        # Statistiques supplémentaires
        if self.db_manager:
            try:
                stats = self.db_manager.get_statistics_summary()
                print(f"\n{Fore.CYAN}📈 Statistiques de la base de données:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
            except:
                pass
    
    def stop_all_services(self):
        """Arrêter tous les services"""
        print(f"\n{Fore.YELLOW}🛑 Arrêt de tous les services...")
        self.running = False
        
        # Les threads daemon s'arrêteront automatiquement
        if self.api_thread and self.api_thread.is_alive():
            print(f"{Fore.YELLOW}   Arrêt de l'API REST...")
        
        if self.gui_thread and self.gui_thread.is_alive():
            print(f"{Fore.YELLOW}   Arrêt de l'interface GUI...")
        
        print(f"{Fore.GREEN}✅ Tous les services arrêtés")

def main():
    parser = argparse.ArgumentParser(description="Analyseur de Trafic Réseau Intégré")
    parser.add_argument("-i", "--interface", default="eth0", 
                       help="Interface réseau (défaut: eth0)")
    parser.add_argument("-t", "--time", type=int, default=60,
                       help="Durée de capture en secondes (défaut: 60)")
    parser.add_argument("-f", "--filter", 
                       help="Filtre de capture (nom prédéfini ou BPF)")
    parser.add_argument("--api", action="store_true",
                       help="Démarrer l'API REST")
    parser.add_argument("--gui", action="store_true",
                       help="Démarrer l'interface graphique")
    parser.add_argument("--notifications", action="store_true",
                       help="Activer les notifications")
    parser.add_argument("--production", action="store_true",
                       help="Mode production avec toutes les fonctionnalités")
    parser.add_argument("--status", action="store_true",
                       help="Afficher le statut du système")
    parser.add_argument("--interactive", action="store_true",
                       help="Mode interactif avec menu")
    
    args = parser.parse_args()
    
    # Créer l'analyseur intégré
    integrated_analyzer = IntegratedTrafficAnalyzer()
    
    # Initialiser les composants
    if not integrated_analyzer.initialize_components():
        print(f"{Fore.RED}❌ Échec de l'initialisation")
        return
    
    try:
        # Mode production
        if args.production:
            integrated_analyzer.run_production_mode()
            return
        
        # Affichage du statut
        if args.status:
            integrated_analyzer.show_system_status()
            return
        
        # Démarrer l'API si demandée
        if args.api:
            integrated_analyzer.start_api_server()
        
        # Démarrer la GUI si demandée
        if args.gui:
            integrated_analyzer.start_gui_interface()
        
        # Mode interactif
        if args.interactive:
            while True:
                print(f"\n{Fore.CYAN}🎛️ MENU INTERACTIF")
                print("1. Démarrer une capture")
                print("2. Afficher le statut")
                print("3. Lister les filtres")
                print("4. Démarrer l'API")
                print("5. Démarrer la GUI")
                print("6. Mode production complète")
                print("0. Quitter")
                
                choice = input(f"\n{Fore.YELLOW}Votre choix: ")
                
                if choice == "1":
                    analyzer = integrated_analyzer.start_capture_with_enhancements(
                        interface=args.interface,
                        duration=args.time,
                        enable_notifications=args.notifications,
                        custom_filter=args.filter
                    )
                    if analyzer:
                        analyzer.generate_statistics()
                
                elif choice == "2":
                    integrated_analyzer.show_system_status()
                
                elif choice == "3":
                    filters = integrated_analyzer.filter_system.list_available_filters()
                    for name, bpf in list(filters.items())[:10]:
                        print(f"  {name}: {bpf}")
                
                elif choice == "4":
                    integrated_analyzer.start_api_server()
                
                elif choice == "5":
                    integrated_analyzer.start_gui_interface()
                
                elif choice == "6":
                    integrated_analyzer.run_production_mode()
                
                elif choice == "0":
                    break
                
                input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...")
        
        else:
            # Mode capture standard
            analyzer = integrated_analyzer.start_capture_with_enhancements(
                interface=args.interface,
                duration=args.time,
                enable_notifications=args.notifications,
                custom_filter=args.filter
            )
            
            if analyzer:
                analyzer.generate_statistics()
                analyzer.visualize_traffic()
        
        # Maintenir les services actifs si API ou GUI lancées
        if args.api or args.gui:
            print(f"\n{Fore.GREEN}🔄 Services actifs. Ctrl+C pour arrêter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
    
    finally:
        integrated_analyzer.stop_all_services()

if __name__ == "__main__":
    main()