#!/usr/bin/env python3
"""
🎭 DÉMONSTRATIONS - ANALYSEUR DE TRAFIC RÉSEAU
============================================

Ce fichier contient toutes les démonstrations du système d'analyse de trafic réseau.
Séparé des scripts principaux pour maintenir un code de production propre.

Fonctionnalités démontrées :
- Génération de données simulées IPv4/IPv6
- Modes de démonstration pour tous les composants
- Tests interactifs des fonctionnalités
- Exemples d'utilisation avancée
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
import numpy as np
from colorama import init, Fore, Style

# Ajouter le répertoire parent au path pour imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from analyseur_trafic import AnalyseurTrafic
    from database_manager import DatabaseManager  
    from ml_detector import MLAnomalyDetector
    from notification_system import NotificationSystem
    from advanced_filters import AdvancedPacketFilters
    from integrated_analyzer import IntegratedTrafficAnalyzer
    print("✅ Modules principaux importés avec succès")
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur d'importation: {e}")
    print(f"{Fore.YELLOW}💡 Exécutez ce script depuis le dossier parent")
    sys.exit(1)

init(autoreset=True)

def generate_demo_data_ipv4_ipv6(analyseur):
    """Générer des données de démonstration pour les tests - Support IPv4/IPv6"""
    print(f"{Fore.YELLOW}🎭 Génération de données de démonstration avec IPv4/IPv6...")
    
    analyseur.start_time = datetime.now() - timedelta(minutes=5)
    
    # Simulation de différents types de paquets
    demo_packets = []
    protocols = ['TCP', 'UDP', 'ICMP', 'ARP', 'TCPv6', 'UDPv6', 'ICMPv6']
    ipv4_ips = ['192.168.1.1', '192.168.1.10', '192.168.1.20', '8.8.8.8', '1.1.1.1']
    ipv6_ips = [
        '2001:db8::1', '2001:db8::2', '2001:db8::10',
        'fe80::1', 'fe80::2', 'fc00::1',
        '2606:4700:4700::1111', '2001:4860:4860::8888'
    ]
    ports = [80, 443, 53, 22, 21, 25, 110, 143, 993, 995]
    
    for i in range(800):
        # 70% IPv4, 30% IPv6 pour simuler un trafic mixte réaliste
        is_ipv6 = np.random.random() < 0.3
        
        if is_ipv6:
            protocol_choices = ['TCPv6', 'UDPv6', 'ICMPv6']
            protocol_probs = [0.5, 0.35, 0.15]
            src_ip = np.random.choice(ipv6_ips)
            dst_ip = np.random.choice(ipv6_ips)
            ip_version = 6
        else:
            protocol_choices = ['TCP', 'UDP', 'ICMP', 'ARP']
            protocol_probs = [0.6, 0.25, 0.1, 0.05]
            src_ip = np.random.choice(ipv4_ips)
            dst_ip = np.random.choice(ipv4_ips)
            ip_version = 4
        
        selected_protocol = np.random.choice(protocol_choices, p=protocol_probs)
        
        packet_info = {
            'timestamp': analyseur.start_time + timedelta(seconds=i/10),
            'length': np.random.randint(64, 1500),
            'protocol': selected_protocol,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': np.random.randint(1024, 65535) if np.random.random() > 0.3 else None,
            'dst_port': np.random.choice(ports) if np.random.random() > 0.3 else None,
            'ip_version': ip_version,
            'packet_summary': f"Demo packet {i}"
        }
        
        # Ajouter des champs spécifiques IPv6
        if is_ipv6:
            packet_info['ipv6_next_header'] = np.random.choice([6, 17, 58])  # TCP, UDP, ICMPv6
            packet_info['ipv6_hop_limit'] = np.random.randint(32, 255)
            
            if selected_protocol == 'ICMPv6':
                packet_info['icmpv6_type'] = np.random.choice([1, 2, 135, 136])
                packet_info['icmpv6_code'] = 0
        
        demo_packets.append(packet_info)
        
        # Mise à jour des statistiques
        analyseur.protocol_stats[packet_info['protocol']] += 1
        if packet_info['src_ip']:
            analyseur.ip_stats[packet_info['src_ip']] += 1
        if packet_info['dst_port']:
            analyseur.port_stats[packet_info['dst_port']] += 1
        
        analyseur.statistics['total_packets'] += 1
        analyseur.statistics['total_bytes'] += packet_info['length']
        
        # Statistiques par version IP
        ip_version_key = f"IPv{packet_info['ip_version']}"
        analyseur.statistics[ip_version_key] = analyseur.statistics.get(ip_version_key, 0) + 1
    
    analyseur.packets = demo_packets
    
    # Simulation d'anomalies IPv4 et IPv6
    analyseur.anomalies = [
        {
            'type': 'Port Scan Detected',
            'timestamp': datetime.now(),
            'source_ip': '192.168.1.100',
            'details': 'Scan de 25 ports différents en 1 minute'
        },
        {
            'type': 'IPv6 Tunneling Anomaly',
            'timestamp': datetime.now(),
            'source_ip': '2001:db8::suspicious',
            'details': 'Trop de messages IPv6 Destination Unreachable: 75'
        },
        {
            'type': 'IPv6 Low Hop Limit',
            'timestamp': datetime.now(),
            'source_ip': 'fe80::attack',
            'details': 'Hop limit très bas: 3'
        }
    ]
    
    print(f"{Fore.GREEN}✓ {len(demo_packets)} paquets de démonstration générés")
    ipv4_count = analyseur.statistics.get('IPv4', 0)
    ipv6_count = analyseur.statistics.get('IPv6', 0)
    print(f"{Fore.CYAN}📊 Répartition: {ipv4_count} paquets IPv4, {ipv6_count} paquets IPv6")
    return analyseur

def demo_basic_analysis():
    """Démonstration de l'analyse de base"""
    print(f"\n{Fore.BLUE}🎯 DÉMONSTRATION - ANALYSE DE BASE")
    print("=" * 50)
    
    # Créer l'analyseur
    analyseur = AnalyseurTrafic("lo")  # Interface loopback pour demo
    
    # Générer des données de démonstration
    analyseur = generate_demo_data_ipv4_ipv6(analyseur)
    
    # Générer les statistiques
    print(f"\n{Fore.CYAN}📊 Génération des statistiques...")
    analyseur.generate_statistics()
    
    # Visualisation
    print(f"\n{Fore.CYAN}📈 Génération des graphiques...")
    analyseur.visualize_traffic("demos/demo_basic_analysis.png")
    
    # Export des données
    print(f"\n{Fore.CYAN}💾 Export des données...")
    analyseur.export_data("json", "demos/demo_basic_export.json")
    
    return analyseur

def demo_ml_detection():
    """Démonstration de la détection ML"""
    print(f"\n{Fore.BLUE}🤖 DÉMONSTRATION - MACHINE LEARNING")
    print("=" * 50)
    
    # Initialiser le détecteur ML
    ml_detector = MLAnomalyDetector()
    
    # Créer quelques paquets de test
    test_packets = [
        {
            'length': 1024, 'protocol': 'TCP', 'src_ip': '192.168.1.10',
            'dst_ip': '8.8.8.8', 'src_port': 54321, 'dst_port': 443,
            'timestamp': datetime.now(), 'ip_version': 4
        },
        {
            'length': 64, 'protocol': 'ICMP', 'src_ip': '192.168.1.100',
            'dst_ip': '192.168.1.1', 'src_port': None, 'dst_port': None,
            'timestamp': datetime.now(), 'ip_version': 4
        },
        {
            'length': 1500, 'protocol': 'TCPv6', 'src_ip': '2001:db8::1',
            'dst_ip': '2001:db8::2', 'src_port': 12345, 'dst_port': 80,
            'timestamp': datetime.now(), 'ip_version': 6
        }
    ]
    
    print(f"\n{Fore.YELLOW}🔍 Test de détection sur paquets:")
    for i, packet in enumerate(test_packets, 1):
        is_anomaly = ml_detector.detect_anomaly(packet)
        confidence = ml_detector.last_confidence
        
        status = "🚨 ANOMALIE" if is_anomaly else "✅ NORMAL"
        print(f"   Paquet {i}: {status} (confiance: {confidence:.3f})")
        print(f"      {packet['protocol']} {packet['src_ip']} -> {packet['dst_ip']}")
    
    return ml_detector

def demo_notifications():
    """Démonstration du système de notifications"""
    print(f"\n{Fore.BLUE}📧 DÉMONSTRATION - NOTIFICATIONS")
    print("=" * 50)
    
    # Initialiser le système de notifications
    notification_system = NotificationSystem()
    
    # Simuler une anomalie
    anomaly_data = {
        'anomaly_type': 'Port Scan Detected (DEMO)',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source_ip': '192.168.1.100',
        'details': 'Scan de 25 ports différents en démonstration',
        'total_packets': 1500,
        'packets_per_second': 25.5,
        'anomaly_count': 3
    }
    
    print(f"\n{Fore.YELLOW}📤 Envoi de notification d'anomalie...")
    notification_system.send_anomaly_alert(anomaly_data)
    
    # Simuler un rapport de statut
    status_data = {
        'period': '60 secondes (démonstration)',
        'system_status': 'Démonstration en cours',
        'total_packets': 800,
        'anomalies_count': 3,
        'detection_rate': 97.8,
        'avg_performance': 13.3,
        'top_events': 'Port scans, Trafic IPv6'
    }
    
    print(f"\n{Fore.YELLOW}📊 Envoi de rapport de statut...")
    notification_system.send_status_report(status_data)
    
    # Afficher les statistiques
    stats = notification_system.get_statistics()
    print(f"\n{Fore.CYAN}📈 Statistiques du système de notifications:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return notification_system

def demo_filters():
    """Démonstration des filtres avancés"""
    print(f"\n{Fore.BLUE}🔍 DÉMONSTRATION - FILTRES AVANCÉS")
    print("=" * 50)
    
    # Initialiser le système de filtres
    filter_system = AdvancedPacketFilters()
    
    print(f"\n{Fore.YELLOW}📋 Filtres prédéfinis disponibles:")
    filters = filter_system.list_available_filters()
    for i, (name, bpf) in enumerate(list(filters.items())[:10], 1):
        print(f"   {i:2d}. {name:<20} : {bpf}")
    
    print(f"\n{Fore.CYAN}Total: {len(filters)} filtres disponibles")
    
    # Créer un filtre personnalisé pour la démo
    custom_name = "demo_https_analysis"
    custom_bpf = "tcp port 443 and host 8.8.8.8"
    custom_desc = "Analyse HTTPS vers DNS Google (démonstration)"
    
    print(f"\n{Fore.YELLOW}➕ Création d'un filtre personnalisé:")
    print(f"   Nom: {custom_name}")
    print(f"   BPF: {custom_bpf}")
    print(f"   Description: {custom_desc}")
    
    filter_system.create_custom_filter(custom_name, custom_bpf, custom_desc)
    
    # Valider le filtre
    is_valid = filter_system.validate_bpf_filter(custom_bpf)
    print(f"   Validation: {'✅ VALIDE' if is_valid else '❌ INVALIDE'}")
    
    return filter_system

def demo_integrated_analysis():
    """Démonstration de l'analyseur intégré"""
    print(f"\n{Fore.BLUE}🚀 DÉMONSTRATION - ANALYSEUR INTÉGRÉ")
    print("=" * 60)
    
    # Créer l'analyseur intégré
    integrated = IntegratedTrafficAnalyzer()
    
    # Initialiser les composants
    if not integrated.initialize_components():
        print(f"{Fore.RED}❌ Échec de l'initialisation")
        return None
    
    print(f"\n{Fore.CYAN}🎯 Exécution du mode démonstration intégré...")
    integrated.run_demo_mode()
    
    print(f"\n{Fore.CYAN}📊 Affichage du statut du système...")
    integrated.show_system_status()
    
    return integrated

def demo_complete_workflow():
    """Démonstration du workflow complet"""
    print(f"\n{Fore.BLUE}🎯 DÉMONSTRATION - WORKFLOW COMPLET")
    print("=" * 60)
    
    print(f"{Fore.CYAN}Phase 1: Analyse de base...")
    basic_analyzer = demo_basic_analysis()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 2: Machine Learning...")
    ml_detector = demo_ml_detection()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 3: Notifications...")
    notifications = demo_notifications()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 4: Filtres avancés...")
    filters = demo_filters()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 5: Analyseur intégré...")
    integrated = demo_integrated_analysis()
    
    print(f"\n{Fore.GREEN}🎉 DÉMONSTRATION COMPLÈTE TERMINÉE!")
    print("=" * 60)
    print(f"{Fore.YELLOW}📁 Fichiers générés dans le dossier demos/:")
    print(f"   - demo_basic_analysis.png")
    print(f"   - demo_basic_export.json")
    print(f"   - demo_integrated_analysis.png") 
    print(f"   - demo_integrated_export.json")
    
    return {
        'basic_analyzer': basic_analyzer,
        'ml_detector': ml_detector,
        'notifications': notifications,
        'filters': filters,
        'integrated': integrated
    }

def interactive_demo_menu():
    """Menu interactif pour les démonstrations"""
    while True:
        print(f"\n{Fore.CYAN}🎭 MENU DES DÉMONSTRATIONS - ANALYSEUR DE TRAFIC")
        print("=" * 60)
        print(f"{Fore.YELLOW}1. Analyse de base (génération données + stats)")
        print(f"{Fore.YELLOW}2. Machine Learning (détection anomalies)")
        print(f"{Fore.YELLOW}3. Système de notifications")
        print(f"{Fore.YELLOW}4. Filtres avancés")
        print(f"{Fore.YELLOW}5. Analyseur intégré")
        print(f"{Fore.YELLOW}6. Workflow complet (toutes les démos)")
        print(f"{Fore.YELLOW}0. Quitter")
        
        try:
            choice = input(f"\n{Fore.WHITE}Votre choix: ").strip()
            
            if choice == "1":
                demo_basic_analysis()
            elif choice == "2":
                demo_ml_detection()
            elif choice == "3":
                demo_notifications()
            elif choice == "4":
                demo_filters()
            elif choice == "5":
                demo_integrated_analysis()
            elif choice == "6":
                demo_complete_workflow()
            elif choice == "0":
                print(f"\n{Fore.GREEN}👋 Au revoir!")
                break
            else:
                print(f"\n{Fore.RED}❌ Choix invalide. Veuillez recommencer.")
            
            if choice != "0":
                input(f"\n{Fore.CYAN}📝 Appuyez sur Entrée pour continuer...")
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}🛑 Arrêt demandé par l'utilisateur")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Erreur: {e}")
            input(f"\n{Fore.CYAN}📝 Appuyez sur Entrée pour continuer...")

def demo_ml_detector():
    """Démonstration du détecteur ML - DÉPLACÉ DU SCRIPT PRINCIPAL"""
    print("🤖 DÉMONSTRATION DU DÉTECTEUR ML")
    print("=" * 50)
    
    # Créer le détecteur
    detector = MLAnomalyDetector(threshold=0.1)
    
    # Générer des paquets d'exemple pour l'entraînement
    normal_packets = []
    anomalous_packets = []
    
    # Paquets normaux (IPv4 et IPv6)
    for i in range(100):
        is_ipv6 = i < 30  # 30% IPv6
        if is_ipv6:
            normal_packet = {
                'length': np.random.randint(64, 1500),
                'protocol': np.random.choice(['TCPv6', 'UDPv6', 'ICMPv6']),
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([80, 443, 53, 22, 25]),
                'src_ip': f"2001:db8::{np.random.randint(1, 254)}",
                'dst_ip': f"2001:db8::{np.random.randint(1, 254)}",
                'ip_version': 6,
                'ipv6_hop_limit': np.random.randint(32, 255),
                'timestamp': datetime.now()
            }
        else:
            normal_packet = {
                'length': np.random.randint(64, 1500),
                'protocol': np.random.choice(['TCP', 'UDP', 'HTTP', 'HTTPS']),
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([80, 443, 53, 22, 25]),
                'src_ip': f"192.168.1.{np.random.randint(1, 254)}",
                'dst_ip': f"8.8.8.{np.random.randint(1, 254)}",
                'ip_version': 4,
                'timestamp': datetime.now()
            }
        normal_packets.append(normal_packet)
    
    # Paquets anormaux (IPv4 et IPv6)
    for i in range(20):
        is_ipv6 = i < 8  # 40% IPv6 pour les anomalies
        if is_ipv6:
            anomalous_packet = {
                'length': np.random.choice([10, 9500]),  # Très petit ou très grand
                'protocol': 'ICMPv6',
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([1337, 31337, 4444]),  # Ports suspects
                'src_ip': f"2001:db8::suspicious{np.random.randint(1, 10)}",
                'dst_ip': f"fe80::target{np.random.randint(1, 10)}",
                'ip_version': 6,
                'ipv6_hop_limit': np.random.randint(1, 10),  # Hop limit très bas
                'icmpv6_type': 1,  # Destination Unreachable
                'timestamp': datetime.now()
            }
        else:
            anomalous_packet = {
                'length': np.random.choice([10, 9500]),  # Très petit ou très grand
                'protocol': 'ICMP',
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([1337, 31337, 4444]),  # Ports suspects
                'src_ip': f"192.168.1.{np.random.randint(1, 254)}",
                'dst_ip': f"10.0.0.{np.random.randint(1, 254)}",
                'ip_version': 4,
                'timestamp': datetime.now()
            }
        anomalous_packets.append(anomalous_packet)
    
    # Combiner et mélanger
    all_packets = normal_packets + anomalous_packets
    np.random.shuffle(all_packets)
    
    print(f"📊 Génération de {len(normal_packets)} paquets normaux et {len(anomalous_packets)} paquets anormaux")
    
    # Entraîner le modèle avec les paquets normaux
    training_data = detector.generate_training_data_from_packets(normal_packets)
    detector.train(training_data)
    
    # Tester sur tous les paquets
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    
    print("\n🔍 Test de détection:")
    for i, packet in enumerate(all_packets[:20]):  # Tester les 20 premiers
        is_anomaly_detected = detector.detect_anomaly(packet)
        is_actually_anomaly = packet in anomalous_packets
        
        print(f"Paquet {i+1}: {'🚨 ANOMALIE' if is_anomaly_detected else '✅ Normal'} "
              f"(Conf: {detector.last_confidence:.3f}) - "
              f"Réel: {'Anomalie' if is_actually_anomaly else 'Normal'}")
        
        if is_anomaly_detected and is_actually_anomaly:
            true_positives += 1
        elif is_anomaly_detected and not is_actually_anomaly:
            false_positives += 1
        elif not is_anomaly_detected and not is_actually_anomaly:
            true_negatives += 1
        elif not is_anomaly_detected and is_actually_anomaly:
            false_negatives += 1
    
    # Métriques de performance
    print(f"\n📈 MÉTRIQUES DE PERFORMANCE:")
    print(f"True Positives: {true_positives}")
    print(f"False Positives: {false_positives}")
    print(f"True Negatives: {true_negatives}")
    print(f"False Negatives: {false_negatives}")
    
    if (true_positives + false_positives) > 0:
        precision = true_positives / (true_positives + false_positives)
        print(f"Précision: {precision:.3f}")
    
    if (true_positives + false_negatives) > 0:
        recall = true_positives / (true_positives + false_negatives)
        print(f"Rappel: {recall:.3f}")
    
    # Importance des features
    print(f"\n🎯 IMPORTANCE DES FEATURES:")
    importances = detector.get_feature_importance()
    for feature, importance in sorted(importances.items(), key=lambda x: x[1], reverse=True):
        print(f"{feature}: {importance:.3f}")
    
    print(f"\n✅ Démonstration terminée!")

def demo_advanced_filters():
    """Démonstration des filtres avancés - DÉPLACÉ DU SCRIPT PRINCIPAL"""
    print(f"{Fore.BLUE}🔍 SYSTÈME DE FILTRES AVANCÉS - DÉMONSTRATION")
    print("=" * 60)
    
    # Initialiser le système de filtres
    filter_system = AdvancedPacketFilters()
    
    # Afficher les filtres prédéfinis
    print(f"\n{Fore.CYAN}📋 Filtres prédéfinis disponibles:")
    for i, (name, bpf) in enumerate(filter_system.list_available_filters().items(), 1):
        if i <= 10:  # Afficher seulement les 10 premiers
            print(f"{Fore.YELLOW}{i:2d}. {name:20s} -> {bpf}")
    
    print(f"{Fore.CYAN}... et {len(filter_system.list_available_filters())-10} autres filtres")
    
    # Démonstration de création de filtre personnalisé
    print(f"\n{Fore.CYAN}🛠️ Création d'un filtre personnalisé:")
    filter_system.create_custom_filter(
        name="custom_web_secure",
        bpf_expression="tcp port 443 and host 192.168.1.0/24",
        description="Trafic HTTPS vers le réseau local"
    )
    
    # Démonstration de filtre conditionnel
    print(f"\n{Fore.CYAN}⚙️ Création d'un filtre conditionnel:")
    conditions = {
        'protocols': ['TCP', 'UDP'],
        'ports': [80, 443, 53],
        'packet_size': {'min': 100, 'max': 1400}
    }
    conditional_filter = filter_system.create_conditional_filter(conditions)
    print(f"{Fore.GREEN}✓ Filtre conditionnel: {conditional_filter}")
    
    # Démonstration d'optimisation
    print(f"\n{Fore.CYAN}🚀 Optimisation d'un filtre:")
    test_filter = "host 8.8.8.8 and tcp and port 53"
    optimized = filter_system.optimize_filter(test_filter)
    print(f"{Fore.YELLOW}Original: {test_filter}")
    print(f"{Fore.GREEN}Optimisé: {optimized}")
    
    # Test de validation
    print(f"\n{Fore.CYAN}✅ Test de validation:")
    valid_filter = "tcp port 80" 
    invalid_filter = "invalid_syntax port xyz"
    
    print(f"'{valid_filter}' -> {filter_system.validate_bpf_filter(valid_filter)}")
    print(f"'{invalid_filter}' -> {filter_system.validate_bpf_filter(invalid_filter)}")
    
    # Export de configuration
    print(f"\n{Fore.CYAN}💾 Export de configuration:")
    filter_system.export_filters_config("demo_filters.json")
    
    print(f"\n{Fore.GREEN}✅ Démonstration terminée avec succès!")

if __name__ == "__main__":
    print(f"{Fore.BLUE}🌐 DÉMONSTRATIONS - ANALYSEUR DE TRAFIC RÉSEAU")
    print("=" * 60)
    print(f"{Fore.CYAN}📁 Fichier de démonstration séparé des scripts principaux")
    print(f"{Fore.CYAN}🎯 Contient toutes les fonctions de test et de démonstration")
    
    # Lancer le menu interactif par défaut
    interactive_demo_menu()