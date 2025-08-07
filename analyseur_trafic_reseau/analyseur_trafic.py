#!/usr/bin/env python3
"""
Analyseur de Trafic Réseau
Outil pour capturer et analyser le trafic réseau local

Fonctionnalités:
- Capture de paquets réseau
- Analyse des protocoles
- Détection d'anomalies
- Visualisation du trafic
- Export des données
"""

import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, ARP
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import csv
import argparse
import threading
import time
import os
from collections import defaultdict, Counter
from colorama import init, Fore, Style
from tabulate import tabulate
from tqdm import tqdm
import numpy as np

# Initialize colorama for colored output
init(autoreset=True)

class AnalyseurTrafic:
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.packets = []
        self.is_capturing = False
        self.start_time = None
        self.statistics = defaultdict(int)
        self.protocol_stats = Counter()
        self.ip_stats = Counter()
        self.port_stats = Counter()
        self.anomalies = []
        
        # Configuration des seuils pour la détection d'anomalies
        self.anomaly_thresholds = {
            'packets_per_second': 1000,
            'unique_ips_per_minute': 100,
            'port_scan_threshold': 20,
            'suspicious_protocols': ['DNS', 'FTP', 'TELNET'],
            'ipv6_tunneling_threshold': 50,  # Seuil pour tunneling IPv6 suspect
            'ipv6_extension_headers_max': 10  # Nombre max d'en-têtes d'extension IPv6
        }
        
        print(f"{Fore.GREEN}✓ Analyseur de Trafic Réseau initialisé")
        print(f"{Fore.CYAN}Interface: {interface}")

    def packet_handler(self, packet):
        """Gestionnaire de paquets capturés - Support IPv4 et IPv6"""
        timestamp = datetime.now()
        
        # Informations de base du paquet
        packet_info = {
            'timestamp': timestamp,
            'length': len(packet),
            'protocol': 'Unknown',
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dst_port': None,
            'ip_version': None,
            'ipv6_next_header': None,
            'ipv6_hop_limit': None,
            'packet_summary': packet.summary()
        }
        
        # Analyse des couches IPv4 et IPv6
        if packet.haslayer(IP):
            # Traitement IPv4
            ip_layer = packet[IP]
            packet_info['src_ip'] = ip_layer.src
            packet_info['dst_ip'] = ip_layer.dst
            packet_info['ip_version'] = 4
            
            # Statistiques IP
            self.ip_stats[ip_layer.src] += 1
            self.ip_stats[ip_layer.dst] += 1
            
            # Analyse des protocoles de transport IPv4
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                packet_info['protocol'] = 'TCP'
                packet_info['src_port'] = tcp_layer.sport
                packet_info['dst_port'] = tcp_layer.dport
                self.port_stats[tcp_layer.dport] += 1
                
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                packet_info['protocol'] = 'UDP'
                packet_info['src_port'] = udp_layer.sport
                packet_info['dst_port'] = udp_layer.dport
                self.port_stats[udp_layer.dport] += 1
                
            elif packet.haslayer(ICMP):
                packet_info['protocol'] = 'ICMP'
                
        elif packet.haslayer(IPv6):
            # Traitement IPv6
            ipv6_layer = packet[IPv6]
            packet_info['src_ip'] = ipv6_layer.src
            packet_info['dst_ip'] = ipv6_layer.dst
            packet_info['ip_version'] = 6
            packet_info['ipv6_next_header'] = ipv6_layer.nh
            packet_info['ipv6_hop_limit'] = ipv6_layer.hlim
            
            # Statistiques IPv6
            self.ip_stats[ipv6_layer.src] += 1
            self.ip_stats[ipv6_layer.dst] += 1
            
            # Analyse des protocoles de transport IPv6
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                packet_info['protocol'] = 'TCPv6'
                packet_info['src_port'] = tcp_layer.sport
                packet_info['dst_port'] = tcp_layer.dport
                self.port_stats[tcp_layer.dport] += 1
                
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                packet_info['protocol'] = 'UDPv6'
                packet_info['src_port'] = udp_layer.sport
                packet_info['dst_port'] = udp_layer.dport
                self.port_stats[udp_layer.dport] += 1
                
            elif packet.haslayer(scapy.ICMPv6):
                icmpv6_layer = packet[scapy.ICMPv6]
                packet_info['protocol'] = 'ICMPv6'
                packet_info['icmpv6_type'] = icmpv6_layer.type
                packet_info['icmpv6_code'] = icmpv6_layer.code
                
                # Détection spécifique IPv6
                self._detect_ipv6_anomalies(packet_info, icmpv6_layer)
                
        elif packet.haslayer(ARP):
            packet_info['protocol'] = 'ARP'
            arp_layer = packet[ARP]
            packet_info['src_ip'] = arp_layer.psrc
            packet_info['dst_ip'] = arp_layer.pdst
            packet_info['ip_version'] = 4  # ARP est lié à IPv4
        
        # Mise à jour des statistiques
        self.protocol_stats[packet_info['protocol']] += 1
        self.statistics['total_packets'] += 1
        self.statistics['total_bytes'] += packet_info['length']
        
        # Statistiques par version IP
        if packet_info['ip_version']:
            ip_version_key = f"IPv{packet_info['ip_version']}"
            self.statistics[ip_version_key] = self.statistics.get(ip_version_key, 0) + 1
        
        # Stockage du paquet
        self.packets.append(packet_info)
        
        # Détection d'anomalies en temps réel
        self.detect_anomalies(packet_info)
    
    def _detect_ipv6_anomalies(self, packet_info, icmpv6_layer):
        """Détection d'anomalies spécifiques à IPv6"""
        current_time = datetime.now()
        
        # Détection de tunneling IPv6 suspect
        if icmpv6_layer.type == 1:  # Destination Unreachable
            recent_unreachable = len([p for p in self.packets[-50:] 
                                    if p.get('protocol') == 'ICMPv6' and 
                                       p.get('icmpv6_type') == 1 and
                                       (current_time - p['timestamp']).seconds < 60])
            
            if recent_unreachable > self.anomaly_thresholds['ipv6_tunneling_threshold']:
                anomaly = {
                    'type': 'IPv6 Tunneling Anomaly',
                    'timestamp': current_time,
                    'source_ip': packet_info['src_ip'],
                    'details': f'Trop de messages IPv6 Destination Unreachable: {recent_unreachable}'
                }
                self.anomalies.append(anomaly)
                print(f"{Fore.RED}🚨 ANOMALIE IPv6: {anomaly['type']} - {anomaly['source_ip']}")
        
        # Détection de hop limit anormalement bas (possible attaque)
        if packet_info.get('ipv6_hop_limit', 255) < 10:
            anomaly = {
                'type': 'IPv6 Low Hop Limit',
                'timestamp': current_time,
                'source_ip': packet_info['src_ip'],
                'details': f'Hop limit très bas: {packet_info.get("ipv6_hop_limit")}'
            }
            self.anomalies.append(anomaly)
            print(f"{Fore.RED}🚨 ANOMALIE IPv6: {anomaly['type']} - {anomaly['source_ip']}")

    def detect_anomalies(self, packet_info):
        """Détection d'anomalies en temps réel"""
        current_time = datetime.now()
        
        # Détection de scan de ports (nombreuses connexions vers différents ports)
        if packet_info['src_ip'] and packet_info['dst_port']:
            recent_packets = [p for p in self.packets[-100:] 
                            if p['src_ip'] == packet_info['src_ip'] 
                            and (current_time - p['timestamp']).seconds < 60]
            
            unique_ports = len(set(p['dst_port'] for p in recent_packets if p['dst_port']))
            
            if unique_ports > self.anomaly_thresholds['port_scan_threshold']:
                anomaly = {
                    'type': 'Port Scan Detected',
                    'timestamp': current_time,
                    'source_ip': packet_info['src_ip'],
                    'details': f'Scan de {unique_ports} ports différents en 1 minute'
                }
                self.anomalies.append(anomaly)
                print(f"{Fore.RED}🚨 ANOMALIE: {anomaly['type']} - {anomaly['source_ip']}")

    def start_capture(self, duration=60, packet_count=None):
        """Démarrer la capture de paquets"""
        print(f"{Fore.YELLOW}🎯 Démarrage de la capture...")
        print(f"Interface: {self.interface}")
        print(f"Durée: {duration}s" + (f", Max paquets: {packet_count}" if packet_count else ""))
        
        self.is_capturing = True
        self.start_time = datetime.now()
        
        try:
            if packet_count:
                scapy.sniff(iface=self.interface, prn=self.packet_handler, 
                          count=packet_count, timeout=duration)
            else:
                scapy.sniff(iface=self.interface, prn=self.packet_handler, 
                          timeout=duration)
        except PermissionError:
            print(f"{Fore.RED}❌ Erreur: Permissions insuffisantes pour capturer sur {self.interface}")
            print(f"{Fore.YELLOW}💡 Essayez d'exécuter avec sudo ou utilisez une interface virtuelle")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la capture: {e}")
            return False
        finally:
            self.is_capturing = False
            
        print(f"{Fore.GREEN}✓ Capture terminée - {len(self.packets)} paquets capturés")
        return True

    def generate_statistics(self):
        """Générer des statistiques détaillées - Support IPv4/IPv6"""
        if not self.packets:
            print(f"{Fore.RED}❌ Aucun paquet capturé")
            return
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n{Fore.CYAN}📊 STATISTIQUES DE CAPTURE")
        print("=" * 50)
        
        # Statistiques générales avec IPv4/IPv6
        ipv4_count = self.statistics.get('IPv4', 0)
        ipv6_count = self.statistics.get('IPv6', 0)
        
        general_stats = [
            ["Durée de capture", f"{duration:.2f}s"],
            ["Total paquets", self.statistics['total_packets']],
            ["Total bytes", f"{self.statistics['total_bytes']:,}"],
            ["Paquets IPv4", ipv4_count],
            ["Paquets IPv6", ipv6_count],
            ["Ratio IPv6/IPv4", f"{ipv6_count/ipv4_count:.2f}" if ipv4_count > 0 else "N/A"],
            ["Paquets/seconde", f"{self.statistics['total_packets']/duration:.2f}"],
            ["Débit moyen", f"{(self.statistics['total_bytes']*8/duration/1000000):.2f} Mbps"],
            ["Anomalies détectées", len(self.anomalies)]
        ]
        
        print(tabulate(general_stats, headers=["Métrique", "Valeur"], tablefmt="grid"))
        
        # Top protocoles avec distinction IPv4/IPv6
        print(f"\n{Fore.CYAN}🔗 TOP PROTOCOLES (IPv4/IPv6)")
        protocol_table = [[proto, count, f"{count/self.statistics['total_packets']*100:.1f}%"] 
                         for proto, count in self.protocol_stats.most_common(15)]
        print(tabulate(protocol_table, headers=["Protocole", "Paquets", "%"], tablefmt="grid"))
        
        # Top IPs sources (IPv4 et IPv6)
        print(f"\n{Fore.CYAN}🌐 TOP IPs SOURCES (IPv4/IPv6)")
        ip_table = []
        for ip, count in self.ip_stats.most_common(15):
            ip_version = "IPv6" if ":" in str(ip) else "IPv4"
            # Raccourcir les adresses IPv6 pour l'affichage
            display_ip = str(ip)[:30] + "..." if len(str(ip)) > 30 else str(ip)
            ip_table.append([display_ip, ip_version, count])
        print(tabulate(ip_table, headers=["IP", "Version", "Paquets"], tablefmt="grid"))
        
        # Top ports de destination
        print(f"\n{Fore.CYAN}🚪 TOP PORTS DE DESTINATION")
        port_table = [[port, count] for port, count in self.port_stats.most_common(10)]
        print(tabulate(port_table, headers=["Port", "Paquets"], tablefmt="grid"))
        
        # Anomalies détectées avec types IPv6
        if self.anomalies:
            print(f"\n{Fore.RED}🚨 ANOMALIES DÉTECTÉES")
            anomaly_table = []
            for a in self.anomalies:
                ip_display = str(a.get('source_ip', 'N/A'))[:25] + "..." if len(str(a.get('source_ip', 'N/A'))) > 25 else str(a.get('source_ip', 'N/A'))
                anomaly_table.append([
                    a['type'], 
                    a['timestamp'].strftime('%H:%M:%S'),
                    ip_display,
                    a['details'][:50] + "..." if len(a['details']) > 50 else a['details']
                ])
            print(tabulate(anomaly_table, headers=["Type", "Heure", "IP Source", "Détails"], 
                         tablefmt="grid"))

    def visualize_traffic(self, save_path="traffic_analysis.png"):
        """Générer des visualisations du trafic"""
        if not self.packets:
            print(f"{Fore.RED}❌ Aucun paquet à visualiser")
            return
        
        print(f"{Fore.YELLOW}📈 Génération des graphiques...")
        
        # Création de la figure avec subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Analyse du Trafic Réseau', fontsize=16, fontweight='bold')
        
        # 1. Trafic par protocole (camembert)
        protocols = list(self.protocol_stats.keys())
        counts = list(self.protocol_stats.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(protocols)))
        
        ax1.pie(counts, labels=protocols, autopct='%1.1f%%', colors=colors)
        ax1.set_title('Répartition par Protocole')
        
        # 2. Top 10 des IPs sources (barres horizontales)
        top_ips = self.ip_stats.most_common(10)
        if top_ips:
            ips, ip_counts = zip(*top_ips)
            ax2.barh(range(len(ips)), ip_counts, color='skyblue')
            ax2.set_yticks(range(len(ips)))
            ax2.set_yticklabels(ips)
            ax2.set_xlabel('Nombre de paquets')
            ax2.set_title('Top 10 IPs Sources')
        
        # 3. Évolution temporelle du trafic
        if len(self.packets) > 10:
            # Regrouper par intervalles de temps
            df = pd.DataFrame(self.packets)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df_grouped = df.resample('10S', on='timestamp').size()
            
            ax3.plot(df_grouped.index, df_grouped.values, marker='o', color='red')
            ax3.set_xlabel('Temps')
            ax3.set_ylabel('Paquets par 10s')
            ax3.set_title('Évolution Temporelle du Trafic')
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. Top ports de destination
        top_ports = self.port_stats.most_common(10)
        if top_ports:
            ports, port_counts = zip(*top_ports)
            ax4.bar(range(len(ports)), port_counts, color='green', alpha=0.7)
            ax4.set_xticks(range(len(ports)))
            ax4.set_xticklabels([str(p) for p in ports], rotation=45)
            ax4.set_xlabel('Port')
            ax4.set_ylabel('Nombre de paquets')
            ax4.set_title('Top 10 Ports de Destination')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"{Fore.GREEN}✓ Graphiques sauvegardés dans {save_path}")
        
        # Afficher si possible
        try:
            plt.show()
        except:
            pass

    def export_data(self, format_type="csv", filename=None):
        """Exporter les données capturées"""
        if not self.packets:
            print(f"{Fore.RED}❌ Aucune donnée à exporter")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == "csv":
            filename = filename or f"traffic_capture_{timestamp}.csv"
            df = pd.DataFrame(self.packets)
            df.to_csv(filename, index=False)
            print(f"{Fore.GREEN}✓ Données exportées en CSV: {filename}")
            
        elif format_type.lower() == "json":
            filename = filename or f"traffic_capture_{timestamp}.json"
            # Convertir les timestamps en strings pour JSON
            packets_json = []
            for packet in self.packets:
                packet_copy = packet.copy()
                packet_copy['timestamp'] = packet_copy['timestamp'].isoformat()
                # Convertir les types numpy en types Python natifs
                for key, value in packet_copy.items():
                    if hasattr(value, 'item'):  # Numpy scalar
                        packet_copy[key] = value.item()
                packets_json.append(packet_copy)
            
            # Fonction pour convertir les types numpy
            def convert_numpy(obj):
                if hasattr(obj, 'item'):
                    return obj.item()
                elif isinstance(obj, dict):
                    return {k: convert_numpy(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                return obj
            
            export_data = {
                'capture_info': {
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'interface': self.interface,
                    'total_packets': len(self.packets)
                },
                'statistics': convert_numpy(dict(self.statistics)),
                'protocol_stats': convert_numpy(dict(self.protocol_stats)),
                'anomalies': [
                    {**anomaly, 'timestamp': anomaly['timestamp'].isoformat()}
                    for anomaly in self.anomalies
                ],
                'packets': packets_json
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"{Fore.GREEN}✓ Données exportées en JSON: {filename}")
        
        return filename

def main():
    parser = argparse.ArgumentParser(description="Analyseur de Trafic Réseau")
    parser.add_argument("-i", "--interface", default="eth0", 
                       help="Interface réseau à surveiller (défaut: eth0)")
    parser.add_argument("-t", "--time", type=int, default=60,
                       help="Durée de capture en secondes (défaut: 60)")
    parser.add_argument("-c", "--count", type=int,
                       help="Nombre maximum de paquets à capturer")
    parser.add_argument("--export", choices=['csv', 'json'], 
                       help="Format d'export des données")
    parser.add_argument("--no-visual", action="store_true",
                       help="Désactiver la génération de graphiques")
    
    args = parser.parse_args()
    
    print(f"{Fore.BLUE}🌐 ANALYSEUR DE TRAFIC RÉSEAU")
    print("=" * 40)
    
    # Initialiser l'analyseur
    analyseur = AnalyseurTrafic(interface=args.interface)
    
    # Capture réelle
    success = analyseur.start_capture(duration=args.time, packet_count=args.count)
    if not success:
        return
    
    # Générer les statistiques
    analyseur.generate_statistics()
    
    # Visualisation
    if not args.no_visual:
        analyseur.visualize_traffic()
    
    # Export des données
    if args.export:
        analyseur.export_data(format_type=args.export)
    
    print(f"\n{Fore.GREEN}✅ Analyse terminée avec succès!")

if __name__ == "__main__":
    main()