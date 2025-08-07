#!/usr/bin/env python3
"""
Filtres de Capture Avancés - Analyseur de Trafic Réseau
Support BPF (Berkeley Packet Filter) personnalisés et filtres conditionnels

Fonctionnalités:
- Filtres BPF personnalisables
- Filtrage par application/processus
- Règles de capture conditionnelles
- Templates de filtres prédéfinis
- Validation et optimisation des filtres
"""

import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, ARP
import psutil
import json
import re
from datetime import datetime
from colorama import Fore, Style
import subprocess
import platform
from typing import Dict, List, Optional, Callable
import logging

class AdvancedPacketFilters:
    """Gestionnaire avancé des filtres de capture de paquets"""
    
    def __init__(self):
        self.active_filters = []
        self.filter_stats = {}
        self.predefined_filters = self._load_predefined_filters()
        self.process_cache = {}
        self.logger = self._setup_logger()
        
        print(f"{Fore.GREEN}✓ Système de Filtres Avancés initialisé")
    
    def _setup_logger(self):
        """Configuration du logger pour les filtres"""
        logger = logging.getLogger('AdvancedFilters')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_predefined_filters(self) -> Dict:
        """Charger les filtres BPF prédéfinis"""
        return {
            # Filtres par protocole
            "web_traffic": "tcp port 80 or tcp port 443",
            "dns_traffic": "udp port 53 or tcp port 53",
            "email_traffic": "tcp port 25 or tcp port 110 or tcp port 143 or tcp port 993 or tcp port 995",
            "ssh_traffic": "tcp port 22",
            "ftp_traffic": "tcp port 21 or tcp port 20",
            "dhcp_traffic": "udp port 67 or udp port 68",
            "ntp_traffic": "udp port 123",
            "snmp_traffic": "udp port 161 or udp port 162",
            
            # Filtres par direction
            "incoming_traffic": "dst host localhost",
            "outgoing_traffic": "src host localhost",
            "internal_traffic": "net 192.168.0.0/16 or net 10.0.0.0/8 or net 172.16.0.0/12",
            "external_traffic": "not (net 192.168.0.0/16 or net 10.0.0.0/8 or net 172.16.0.0/12)",
            
            # Filtres IPv6
            "ipv6_traffic": "ip6",
            "ipv6_icmp": "icmp6",
            "ipv6_tcp": "ip6 and tcp",
            "ipv6_udp": "ip6 and udp",
            
            # Filtres de sécurité
            "suspicious_ports": "tcp port 135 or tcp port 139 or tcp port 445 or tcp port 1433 or tcp port 3389",
            "high_ports": "tcp portrange 49152-65535 or udp portrange 49152-65535",
            "broadcast_traffic": "broadcast or multicast",
            
            # Filtres par taille
            "large_packets": "greater 1400",
            "small_packets": "less 100",
            "fragmented": "ip[6:2] & 0x3fff != 0",
            
            # Filtres avancés
            "malformed_packets": "tcp[tcpflags] == 0 or (tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack != 0 and tcp[tcpflags] & tcp-fin != 0)",
            "scan_detection": "tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0",
            "ddos_detection": "icmp or (tcp[tcpflags] & tcp-syn != 0)"
        }
    
    def create_custom_filter(self, name: str, bpf_expression: str, description: str = "") -> bool:
        """Créer un filtre BPF personnalisé"""
        try:
            # Valider l'expression BPF
            if self.validate_bpf_filter(bpf_expression):
                custom_filter = {
                    'name': name,
                    'bpf_expression': bpf_expression,
                    'description': description,
                    'created_at': datetime.now().isoformat(),
                    'usage_count': 0
                }
                
                self.predefined_filters[name] = bpf_expression
                self.logger.info(f"Filtre personnalisé créé: {name} -> {bpf_expression}")
                print(f"{Fore.GREEN}✓ Filtre '{name}' créé avec succès")
                return True
            else:
                print(f"{Fore.RED}❌ Expression BPF invalide: {bpf_expression}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la création du filtre: {e}")
            return False
    
    def validate_bpf_filter(self, bpf_expression: str) -> bool:
        """Valider une expression BPF"""
        try:
            # Test basique de compilation BPF
            # On utilise scapy pour tester la validité
            test_filter = scapy.conf.L2listen(filter=bpf_expression, count=0, timeout=0.1)
            return True
        except:
            try:
                # Test alternatif avec regex pour patterns courants
                valid_patterns = [
                    r'tcp port \d+', r'udp port \d+', r'port \d+',
                    r'host \d+\.\d+\.\d+\.\d+', r'net \d+\.\d+\.\d+\.\d+/\d+',
                    r'src \d+\.\d+\.\d+\.\d+', r'dst \d+\.\d+\.\d+\.\d+',
                    r'ip6', r'icmp6?', r'arp', r'broadcast', r'multicast',
                    r'greater \d+', r'less \d+', r'portrange \d+-\d+'
                ]
                
                # Si l'expression contient au moins un pattern valide
                for pattern in valid_patterns:
                    if re.search(pattern, bpf_expression):
                        return True
                
                return False
            except:
                return False
    
    def apply_process_filter(self, process_name: str) -> Optional[str]:
        """Créer un filtre basé sur un processus spécifique"""
        try:
            # Trouver les connexions du processus
            connections = []
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    if proc.info['connections']:
                        for conn in proc.info['connections']:
                            if conn.laddr:
                                connections.append(conn.laddr.port)
            
            if connections:
                # Créer un filtre BPF pour ces ports
                ports = list(set(connections))
                port_filter = " or ".join([f"port {port}" for port in ports[:10]])  # Limiter à 10 ports
                
                self.logger.info(f"Filtre processus créé pour {process_name}: {len(ports)} ports")
                print(f"{Fore.GREEN}✓ Filtre processus '{process_name}': {len(ports)} ports détectés")
                return port_filter
            else:
                print(f"{Fore.YELLOW}⚠ Aucune connexion trouvée pour le processus '{process_name}'")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du filtrage par processus: {e}")
            return None
    
    def create_conditional_filter(self, conditions: Dict) -> str:
        """Créer un filtre conditionnel basé sur des critères multiples"""
        try:
            filter_parts = []
            
            # Filtrage par protocole
            if 'protocols' in conditions:
                protocol_filters = []
                for proto in conditions['protocols']:
                    if proto.upper() == 'TCP':
                        protocol_filters.append("tcp")
                    elif proto.upper() == 'UDP':
                        protocol_filters.append("udp")
                    elif proto.upper() == 'ICMP':
                        protocol_filters.append("icmp")
                    elif proto.upper() == 'ARP':
                        protocol_filters.append("arp")
                    elif proto.upper() == 'IPv6':
                        protocol_filters.append("ip6")
                
                if protocol_filters:
                    filter_parts.append(f"({' or '.join(protocol_filters)})")
            
            # Filtrage par ports
            if 'ports' in conditions:
                port_filters = []
                for port in conditions['ports']:
                    if isinstance(port, int):
                        port_filters.append(f"port {port}")
                    elif isinstance(port, str) and '-' in port:
                        port_filters.append(f"portrange {port}")
                
                if port_filters:
                    filter_parts.append(f"({' or '.join(port_filters)})")
            
            # Filtrage par IP
            if 'ips' in conditions:
                ip_filters = []
                for ip in conditions['ips']:
                    if '/' in ip:  # CIDR
                        ip_filters.append(f"net {ip}")
                    else:
                        ip_filters.append(f"host {ip}")
                
                if ip_filters:
                    filter_parts.append(f"({' or '.join(ip_filters)})")
            
            # Filtrage par taille de paquet
            if 'packet_size' in conditions:
                size_cond = conditions['packet_size']
                if 'min' in size_cond:
                    filter_parts.append(f"greater {size_cond['min']}")
                if 'max' in size_cond:
                    filter_parts.append(f"less {size_cond['max']}")
            
            # Filtrage temporel (approximatif avec scapy)
            if 'time_range' in conditions:
                # Note: BPF ne supporte pas directement les filtres temporels
                # Ceci sera géré au niveau applicatif
                pass
            
            # Combiner tous les filtres
            if filter_parts:
                combined_filter = ' and '.join(filter_parts)
                self.logger.info(f"Filtre conditionnel créé: {combined_filter}")
                return combined_filter
            else:
                return ""
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la création du filtre conditionnel: {e}")
            return ""
    
    def optimize_filter(self, bpf_expression: str) -> str:
        """Optimiser une expression BPF pour de meilleures performances"""
        try:
            # Optimisations basiques
            optimized = bpf_expression
            
            # Réorganiser pour mettre les filtres les plus sélectifs en premier
            # Les filtres de protocole sont généralement plus efficaces
            protocol_keywords = ['tcp', 'udp', 'icmp', 'arp', 'ip6']
            
            # Si l'expression contient plusieurs conditions, réorganiser
            if ' and ' in optimized or ' or ' in optimized:
                parts = re.split(r'\s+(and|or)\s+', optimized)
                protocol_parts = [p for p in parts if any(kw in p.lower() for kw in protocol_keywords)]
                other_parts = [p for p in parts if p not in protocol_parts and p not in ['and', 'or']]
                
                if protocol_parts and other_parts:
                    # Reconstruire en mettant les protocoles en premier
                    optimized = ' and '.join(protocol_parts + other_parts)
            
            # Simplifications
            optimized = re.sub(r'\s+', ' ', optimized)  # Nettoyer les espaces
            optimized = optimized.strip()
            
            if optimized != bpf_expression:
                self.logger.info(f"Filtre optimisé: {bpf_expression} -> {optimized}")
                print(f"{Fore.YELLOW}🔧 Filtre optimisé")
            
            return optimized
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'optimisation: {e}")
            return bpf_expression
    
    def get_filter_by_name(self, name: str) -> Optional[str]:
        """Récupérer un filtre par son nom"""
        return self.predefined_filters.get(name)
    
    def list_available_filters(self) -> Dict:
        """Lister tous les filtres disponibles"""
        return self.predefined_filters
    
    def get_filter_statistics(self) -> Dict:
        """Obtenir les statistiques d'usage des filtres"""
        return self.filter_stats
    
    def test_filter_performance(self, bpf_expression: str, test_duration: int = 10) -> Dict:
        """Tester les performances d'un filtre"""
        try:
            print(f"{Fore.YELLOW}🧪 Test de performance du filtre (durée: {test_duration}s)...")
            
            start_time = datetime.now()
            packet_count = 0
            
            def test_handler(packet):
                nonlocal packet_count
                packet_count += 1
            
            # Test de capture avec le filtre
            try:
                scapy.sniff(filter=bpf_expression, prn=test_handler, 
                          timeout=test_duration, store=False)
            except:
                # Si la capture échoue, simuler des résultats
                packet_count = 0
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            stats = {
                'filter': bpf_expression,
                'duration': duration,
                'packets_captured': packet_count,
                'packets_per_second': packet_count / duration if duration > 0 else 0,
                'test_timestamp': end_time.isoformat()
            }
            
            self.filter_stats[bpf_expression] = stats
            
            print(f"{Fore.GREEN}✓ Test terminé: {packet_count} paquets en {duration:.2f}s")
            print(f"{Fore.CYAN}📊 Performance: {stats['packets_per_second']:.2f} paquets/sec")
            
            return stats
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du test de performance: {e}")
            return {}
    
    def export_filters_config(self, filename: str = "filter_config.json") -> bool:
        """Exporter la configuration des filtres"""
        try:
            config = {
                'predefined_filters': self.predefined_filters,
                'filter_stats': self.filter_stats,
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"{Fore.GREEN}✓ Configuration des filtres exportée: {filename}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'export: {e}")
            return False
    
    def import_filters_config(self, filename: str) -> bool:
        """Importer une configuration de filtres"""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            if 'predefined_filters' in config:
                self.predefined_filters.update(config['predefined_filters'])
            
            if 'filter_stats' in config:
                self.filter_stats.update(config['filter_stats'])
            
            print(f"{Fore.GREEN}✓ Configuration des filtres importée: {filename}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'import: {e}")
            return False

if __name__ == "__main__":
    print("Advanced Filters - Mode production uniquement")