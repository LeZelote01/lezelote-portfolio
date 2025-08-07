#!/usr/bin/env python3
"""
Gestionnaire de Base de Données pour l'Analyseur de Trafic Réseau
Stockage permanent des captures, statistiques et anomalies
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path

@dataclass
class CaptureSession:
    """Métadonnées d'une session de capture"""
    id: str
    timestamp: datetime
    interface: str
    duration: float
    packets_captured: int
    bytes_captured: int
    anomalies_detected: int
    protocol_distribution: Dict[str, int]
    top_ips: Dict[str, int]
    top_ports: Dict[str, int]
    description: str = ""
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['protocol_distribution'] = json.dumps(self.protocol_distribution)
        data['top_ips'] = json.dumps(self.top_ips)
        data['top_ports'] = json.dumps(self.top_ports)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['protocol_distribution'] = json.loads(data.get('protocol_distribution', '{}'))
        data['top_ips'] = json.loads(data.get('top_ips', '{}'))
        data['top_ports'] = json.loads(data.get('top_ports', '{}'))
        return cls(**data)

@dataclass
class PacketRecord:
    """Enregistrement d'un paquet capturé"""
    id: str
    session_id: str
    timestamp: datetime
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    length: int
    summary: str

@dataclass
class AnomalyRecord:
    """Enregistrement d'une anomalie détectée"""
    id: str
    session_id: str
    timestamp: datetime
    type: str
    severity: str
    source_ip: str
    details: str
    resolved: bool = False

class DatabaseManager:
    """Gestionnaire de base de données pour l'analyseur de trafic"""
    
    def __init__(self, db_path: str = "traffic_analysis.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données avec toutes les tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des sessions de capture
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capture_sessions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                interface TEXT NOT NULL,
                duration REAL NOT NULL,
                packets_captured INTEGER NOT NULL,
                bytes_captured INTEGER NOT NULL,
                anomalies_detected INTEGER NOT NULL,
                protocol_distribution TEXT,
                top_ips TEXT,
                top_ports TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des paquets capturés - Support IPv6
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                protocol TEXT NOT NULL,
                src_ip TEXT,
                dst_ip TEXT,
                src_port INTEGER,
                dst_port INTEGER,
                length INTEGER NOT NULL,
                summary TEXT,
                ip_version INTEGER,
                ipv6_next_header INTEGER,
                ipv6_hop_limit INTEGER,
                icmpv6_type INTEGER,
                icmpv6_code INTEGER,
                FOREIGN KEY (session_id) REFERENCES capture_sessions (id)
            )
        ''')
        
        # Table des anomalies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                details TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES capture_sessions (id)
            )
        ''')
        
        # Index pour améliorer les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_packets_session ON packets(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_packets_timestamp ON packets(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_session ON anomalies(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON capture_sessions(timestamp)')
        
        conn.commit()
        conn.close()
    
    def save_capture_session(self, analyseur) -> str:
        """Sauvegarder une session de capture complète"""
        session_id = str(uuid.uuid4())
        
        # Calculer les statistiques
        packets_count = len(analyseur.packets) if analyseur.packets else 0
        bytes_count = sum(p.get('length', 0) for p in analyseur.packets) if analyseur.packets else 0
        anomalies_count = len(analyseur.anomalies) if hasattr(analyseur, 'anomalies') and analyseur.anomalies else 0
        
        # Distribution des protocoles (top 10)
        protocol_dist = {}
        if hasattr(analyseur, 'protocol_stats') and analyseur.protocol_stats:
            for protocol, count in analyseur.protocol_stats.most_common(10):
                protocol_dist[str(protocol)] = int(count)
        
        # Top IPs (top 10) 
        top_ips = {}
        if hasattr(analyseur, 'ip_stats') and analyseur.ip_stats:
            for ip, count in analyseur.ip_stats.most_common(10):
                top_ips[str(ip)] = int(count)
        
        # Top ports (top 10)
        top_ports = {}
        if hasattr(analyseur, 'port_stats') and analyseur.port_stats:
            for port, count in analyseur.port_stats.most_common(10):
                top_ports[str(port)] = int(count)
        
        # Calculer la durée
        duration = 0
        if analyseur.start_time and analyseur.packets:
            end_time = max(p['timestamp'] for p in analyseur.packets if 'timestamp' in p)
            if isinstance(end_time, datetime):
                duration = (end_time - analyseur.start_time).total_seconds()
        
        # Créer la session
        session = CaptureSession(
            id=session_id,
            timestamp=analyseur.start_time or datetime.now(),
            interface=analyseur.interface,
            duration=duration,
            packets_captured=packets_count,
            bytes_captured=bytes_count,
            anomalies_detected=anomalies_count,
            protocol_distribution=protocol_dist,
            top_ips=top_ips,
            top_ports=top_ports,
            description=f"Capture sur {analyseur.interface} - {packets_count} paquets"
        )
        
        # Sauvegarder en base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Sauvegarder la session
            session_data = session.to_dict()
            cursor.execute('''
                INSERT INTO capture_sessions 
                (id, timestamp, interface, duration, packets_captured, bytes_captured, 
                 anomalies_detected, protocol_distribution, top_ips, top_ports, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_data['id'], session_data['timestamp'], session_data['interface'],
                session_data['duration'], session_data['packets_captured'], session_data['bytes_captured'],
                session_data['anomalies_detected'], session_data['protocol_distribution'],
                session_data['top_ips'], session_data['top_ports'], session_data['description']
            ))
            
            # Sauvegarder les paquets (limiter à 1000 pour les performances)
            if analyseur.packets:
                packets_to_save = analyseur.packets[-1000:] # Garder les 1000 derniers
                for packet in packets_to_save:
                    packet_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO packets 
                        (id, session_id, timestamp, protocol, src_ip, dst_ip, src_port, dst_port, 
                         length, summary, ip_version, ipv6_next_header, ipv6_hop_limit, icmpv6_type, icmpv6_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        packet_id, session_id,
                        packet['timestamp'].isoformat() if isinstance(packet.get('timestamp'), datetime) else str(packet.get('timestamp', '')),
                        packet.get('protocol', ''),
                        packet.get('src_ip', ''),
                        packet.get('dst_ip', ''),
                        packet.get('src_port'),
                        packet.get('dst_port'),
                        packet.get('length', 0),
                        packet.get('packet_summary', ''),
                        packet.get('ip_version'),
                        packet.get('ipv6_next_header'),
                        packet.get('ipv6_hop_limit'),
                        packet.get('icmpv6_type'),
                        packet.get('icmpv6_code')
                    ))
            
            # Sauvegarder les anomalies
            if hasattr(analyseur, 'anomalies') and analyseur.anomalies:
                for anomaly in analyseur.anomalies:
                    anomaly_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO anomalies 
                        (id, session_id, timestamp, type, severity, source_ip, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        anomaly_id, session_id,
                        anomaly['timestamp'].isoformat() if isinstance(anomaly.get('timestamp'), datetime) else str(anomaly.get('timestamp', '')),
                        anomaly.get('type', ''),
                        'HIGH',  # Toutes les anomalies sont considérées comme importantes pour l'instant
                        anomaly.get('source_ip', ''),
                        anomaly.get('details', '')
                    ))
            
            conn.commit()
            print(f"✓ Session de capture sauvegardée: {session_id}")
            return session_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return None
        finally:
            conn.close()
    
    def get_capture_sessions(self, limit: int = 50) -> List[CaptureSession]:
        """Récupérer la liste des sessions de capture"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, interface, duration, packets_captured, bytes_captured,
                   anomalies_detected, protocol_distribution, top_ips, top_ports, description
            FROM capture_sessions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            session_data = {
                'id': row[0],
                'timestamp': row[1],
                'interface': row[2],
                'duration': row[3],
                'packets_captured': row[4],
                'bytes_captured': row[5],
                'anomalies_detected': row[6],
                'protocol_distribution': row[7] or '{}',
                'top_ips': row[8] or '{}',
                'top_ports': row[9] or '{}',
                'description': row[10] or ''
            }
            sessions.append(CaptureSession.from_dict(session_data))
        
        conn.close()
        return sessions
    
    def get_session_packets(self, session_id: str, limit: int = 500) -> List[PacketRecord]:
        """Récupérer les paquets d'une session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, timestamp, protocol, src_ip, dst_ip, src_port, dst_port, 
                   length, summary, ip_version, ipv6_next_header, ipv6_hop_limit, icmpv6_type, icmpv6_code
            FROM packets 
            WHERE session_id = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (session_id, limit))
        
        packets = []
        for row in cursor.fetchall():
            packet = PacketRecord(
                id=row[0],
                session_id=row[1],
                timestamp=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                protocol=row[3],
                src_ip=row[4],
                dst_ip=row[5],
                src_port=row[6],
                dst_port=row[7],
                length=row[8],
                summary=row[9]
            )
            # Ajouter les champs IPv6 si disponibles
            if len(row) > 10:
                packet.ip_version = row[10]
                packet.ipv6_next_header = row[11]
                packet.ipv6_hop_limit = row[12]
                packet.icmpv6_type = row[13]
                packet.icmpv6_code = row[14]
            
            packets.append(packet)
        
        conn.close()
        return packets
    
    def get_session_anomalies(self, session_id: str) -> List[AnomalyRecord]:
        """Récupérer les anomalies d'une session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_id, timestamp, type, severity, source_ip, details, resolved
            FROM anomalies 
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', (session_id,))
        
        anomalies = []
        for row in cursor.fetchall():
            anomaly = AnomalyRecord(
                id=row[0],
                session_id=row[1],
                timestamp=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                type=row[3],
                severity=row[4],
                source_ip=row[5],
                details=row[6],
                resolved=bool(row[7])
            )
            anomalies.append(anomaly)
        
        conn.close()
        return anomalies
    
    def get_statistics_summary(self) -> Dict:
        """Obtenir un résumé des statistiques globales"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                SUM(packets_captured) as total_packets,
                SUM(bytes_captured) as total_bytes,
                SUM(anomalies_detected) as total_anomalies,
                AVG(duration) as avg_duration
            FROM capture_sessions
        ''')
        
        general_stats = cursor.fetchone()
        
        # Sessions récentes (7 derniers jours)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM capture_sessions 
            WHERE timestamp >= ?
        ''', (week_ago,))
        
        recent_sessions = cursor.fetchone()[0]
        
        # Protocoles les plus fréquents (agrégation sur toutes les sessions)
        cursor.execute('SELECT protocol_distribution FROM capture_sessions')
        all_protocols = {}
        for row in cursor.fetchall():
            if row[0]:
                try:
                    protocols = json.loads(row[0])
                    for protocol, count in protocols.items():
                        all_protocols[protocol] = all_protocols.get(protocol, 0) + count
                except:
                    continue
        
        top_protocols = dict(sorted(all_protocols.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Anomalies par type
        cursor.execute('''
            SELECT type, COUNT(*) as count
            FROM anomalies 
            GROUP BY type 
            ORDER BY count DESC
        ''')
        
        anomaly_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_sessions': general_stats[0] or 0,
            'total_packets': general_stats[1] or 0,
            'total_bytes': general_stats[2] or 0,
            'total_anomalies': general_stats[3] or 0,
            'avg_duration': general_stats[4] or 0,
            'recent_sessions': recent_sessions,
            'top_protocols': top_protocols,
            'anomaly_types': anomaly_types
        }
    
    def delete_session(self, session_id: str) -> bool:
        """Supprimer une session et toutes ses données associées"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Supprimer dans l'ordre à cause des contraintes de clé étrangère
            cursor.execute('DELETE FROM packets WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM anomalies WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM capture_sessions WHERE id = ?', (session_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
        finally:
            conn.close()
    
    def cleanup_old_sessions(self, days_to_keep: int = 30) -> int:
        """Nettoyer les anciennes sessions (garder seulement X jours)"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupérer les IDs des sessions à supprimer
            cursor.execute('SELECT id FROM capture_sessions WHERE timestamp < ?', (cutoff_date,))
            old_session_ids = [row[0] for row in cursor.fetchall()]
            
            # Supprimer les données associées
            for session_id in old_session_ids:
                cursor.execute('DELETE FROM packets WHERE session_id = ?', (session_id,))
                cursor.execute('DELETE FROM anomalies WHERE session_id = ?', (session_id,))
            
            # Supprimer les sessions
            cursor.execute('DELETE FROM capture_sessions WHERE timestamp < ?', (cutoff_date,))
            
            conn.commit()
            return len(old_session_ids)
        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur lors du nettoyage: {e}")
            return 0
        finally:
            conn.close()
    
    def export_session_to_csv(self, session_id: str, output_path: str) -> bool:
        """Exporter une session vers un fichier CSV"""
        try:
            packets = self.get_session_packets(session_id)
            
            if not packets:
                return False
            
            # Convertir en DataFrame pandas
            data = []
            for packet in packets:
                data.append({
                    'timestamp': packet.timestamp.isoformat(),
                    'protocol': packet.protocol,
                    'src_ip': packet.src_ip,
                    'dst_ip': packet.dst_ip,
                    'src_port': packet.src_port,
                    'dst_port': packet.dst_port,
                    'length': packet.length,
                    'summary': packet.summary
                })
            
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'export CSV: {e}")
            return False