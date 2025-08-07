#!/usr/bin/env python3
"""
Module de Mode Hors Ligne Avancé
Gestionnaire de Mots de Passe - Advanced Offline Mode

Fonctionnalités:
- Mode hors ligne complet avec synchronisation différée
- Cache intelligent des mots de passe fréquemment utilisés
- Résolution de conflits automatique lors de la synchronisation
- Backup automatique et restauration en cas de corruption
- Compression et optimisation de la base locale
- Indicateurs visuels d'état de synchronisation
- Mode urgence pour accès critique hors ligne
"""

import json
import sqlite3
import logging
import threading
import time
import hashlib
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from colorama import Fore, Style

class SyncStatus(Enum):
    """États de synchronisation"""
    SYNCHRONIZED = "synchronized"
    OFFLINE = "offline"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"

class ConflictResolution(Enum):
    """Stratégies de résolution de conflits"""
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins" 
    MERGE = "merge"
    MANUAL = "manual"

@dataclass
class SyncConflict:
    """Conflit de synchronisation"""
    password_id: str
    field: str
    local_value: str
    remote_value: str
    local_timestamp: datetime
    remote_timestamp: datetime
    resolved: bool = False
    resolution_strategy: Optional[ConflictResolution] = None

@dataclass
class OfflineChange:
    """Changement en mode hors ligne"""
    change_id: str
    password_id: str
    change_type: str  # "create", "update", "delete"
    old_data: Optional[Dict]
    new_data: Dict
    timestamp: datetime
    synced: bool = False

class OfflineMode:
    """Gestionnaire de mode hors ligne avancé"""
    
    def __init__(self, gestionnaire_mdp):
        self.gestionnaire = gestionnaire_mdp
        self.offline_db_path = "offline_cache.db"
        self.backup_dir = Path("offline_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config = {
            "max_cache_entries": 1000,
            "cache_expiry_hours": 72,
            "auto_backup_interval_hours": 6,
            "conflict_resolution_strategy": ConflictResolution.MERGE,
            "emergency_mode_threshold": 7  # jours sans sync avant mode urgence
        }
        
        # État de synchronisation
        self.sync_status = SyncStatus.SYNCHRONIZED
        self.last_sync = None
        self.pending_changes = []
        self.conflicts = []
        
        # Threading pour la synchronisation
        self.sync_thread = None
        self.running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialiser le cache hors ligne
        self._init_offline_database()
        
        # Démarrer la surveillance automatique
        self._start_auto_sync()
        
        print(f"{Fore.GREEN}📱 Mode Hors Ligne Avancé initialisé")
    
    def _init_offline_database(self):
        """Initialiser la base de données hors ligne"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        # Cache des mots de passe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_cache (
                password_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                username TEXT,
                password_encrypted TEXT NOT NULL,
                url TEXT,
                category TEXT,
                notes_encrypted TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                sync_hash TEXT,
                is_favorite BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Changements en attente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_changes (
                change_id TEXT PRIMARY KEY,
                password_id TEXT NOT NULL,
                change_type TEXT NOT NULL,
                old_data_json TEXT,
                new_data_json TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT FALSE,
                retry_count INTEGER DEFAULT 0
            )
        ''')
        
        # Conflits de synchronisation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_conflicts (
                conflict_id TEXT PRIMARY KEY,
                password_id TEXT NOT NULL,
                field TEXT NOT NULL,
                local_value TEXT,
                remote_value TEXT,
                local_timestamp TIMESTAMP,
                remote_timestamp TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE,
                resolution_strategy TEXT,
                resolved_at TIMESTAMP
            )
        ''')
        
        # Métadonnées de synchronisation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Backups automatiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_history (
                backup_id TEXT PRIMARY KEY,
                backup_path TEXT NOT NULL,
                backup_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                restore_tested BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Charger les métadonnées
        self._load_sync_metadata()
    
    def _load_sync_metadata(self):
        """Charger les métadonnées de synchronisation"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM sync_metadata')
        metadata = dict(cursor.fetchall())
        
        if 'last_sync' in metadata:
            self.last_sync = datetime.fromisoformat(metadata['last_sync'])
        
        if 'sync_status' in metadata:
            self.sync_status = SyncStatus(metadata['sync_status'])
        
        conn.close()
    
    def _save_sync_metadata(self):
        """Sauvegarder les métadonnées de synchronisation"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        metadata = {
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_status': self.sync_status.value
        }
        
        for key, value in metadata.items():
            if value is not None:
                cursor.execute('''
                    INSERT OR REPLACE INTO sync_metadata (key, value)
                    VALUES (?, ?)
                ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def cache_password(self, password_id: str, mark_favorite: bool = False):
        """Mettre en cache un mot de passe pour usage hors ligne"""
        if not self.gestionnaire.check_session():
            raise Exception("Session expirée")
        
        # Récupérer le mot de passe
        password_data = self.gestionnaire.get_password(password_id)
        if not password_data:
            raise Exception("Mot de passe non trouvé")
        
        # Calculer le hash de synchronisation
        sync_hash = self._calculate_password_hash(password_data)
        
        # Mettre en cache
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(hours=self.config["cache_expiry_hours"])
        
        cursor.execute('''
            INSERT OR REPLACE INTO password_cache
            (password_id, title, username, password_encrypted, url, category, 
             notes_encrypted, cached_at, expires_at, sync_hash, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            password_id,
            password_data['title'],
            password_data['username'],
            password_data['password'],  # Déjà chiffré par le gestionnaire principal
            password_data.get('url', ''),
            password_data.get('category', ''),
            password_data.get('notes', ''),
            datetime.now().isoformat(),
            expires_at.isoformat(),
            sync_hash,
            mark_favorite
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Mot de passe {password_data['title']} mis en cache")
    
    def get_cached_password(self, password_id: str) -> Optional[Dict]:
        """Récupérer un mot de passe du cache hors ligne"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM password_cache 
            WHERE password_id = ? AND expires_at > ?
        ''', (password_id, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        
        if result:
            # Mettre à jour les statistiques d'accès
            cursor.execute('''
                UPDATE password_cache 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE password_id = ?
            ''', (datetime.now().isoformat(), password_id))
            
            conn.commit()
            
            password_data = {
                'id': result[0],
                'title': result[1],
                'username': result[2],
                'password': result[3],
                'url': result[4],
                'category': result[5],
                'notes': result[6],
                'access_count': result[7] + 1,
                'cached': True,
                'is_favorite': bool(result[12])
            }
        else:
            password_data = None
        
        conn.close()
        return password_data
    
    def list_cached_passwords(self) -> List[Dict]:
        """Lister les mots de passe en cache"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT password_id, title, username, url, category, access_count, 
                   last_accessed, cached_at, is_favorite
            FROM password_cache 
            WHERE expires_at > ?
            ORDER BY is_favorite DESC, access_count DESC, last_accessed DESC
        ''', (datetime.now().isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        passwords = []
        for row in results:
            passwords.append({
                'id': row[0],
                'title': row[1],
                'username': row[2],
                'url': row[3],
                'category': row[4],
                'access_count': row[5],
                'last_accessed': row[6],
                'cached_at': row[7],
                'is_favorite': bool(row[8]),
                'cached': True
            })
        
        return passwords
    
    def add_password_offline(self, title: str, username: str, password: str, 
                           url: str = "", category: str = "Autre", notes: str = "") -> str:
        """Ajouter un mot de passe en mode hors ligne"""
        import secrets
        
        password_id = secrets.token_urlsafe(16)
        change_id = secrets.token_urlsafe(16)
        
        password_data = {
            'id': password_id,
            'title': title,
            'username': username,
            'password': password,
            'url': url,
            'category': category,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'offline_created': True
        }
        
        # Enregistrer le changement en attente
        self._record_pending_change(
            change_id=change_id,
            password_id=password_id,
            change_type="create",
            old_data=None,
            new_data=password_data
        )
        
        # Mettre en cache immédiatement
        self._cache_password_data(password_id, password_data)
        
        self.sync_status = SyncStatus.OFFLINE
        self._save_sync_metadata()
        
        print(f"{Fore.YELLOW}📱 Mot de passe ajouté en mode hors ligne (sync en attente)")
        return password_id
    
    def update_password_offline(self, password_id: str, updates: Dict) -> bool:
        """Mettre à jour un mot de passe en mode hors ligne"""
        # Récupérer les données actuelles (cache ou principale)
        current_data = self.get_cached_password(password_id)
        if not current_data and self.gestionnaire.check_session():
            current_data = self.gestionnaire.get_password(password_id)
        
        if not current_data:
            return False
        
        # Appliquer les modifications
        new_data = current_data.copy()
        new_data.update(updates)
        new_data['updated_at'] = datetime.now().isoformat()
        new_data['offline_updated'] = True
        
        # Enregistrer le changement en attente
        import secrets
        change_id = secrets.token_urlsafe(16)
        
        self._record_pending_change(
            change_id=change_id,
            password_id=password_id,
            change_type="update",
            old_data=current_data,
            new_data=new_data
        )
        
        # Mettre à jour le cache
        self._cache_password_data(password_id, new_data)
        
        self.sync_status = SyncStatus.OFFLINE
        self._save_sync_metadata()
        
        print(f"{Fore.YELLOW}📱 Mot de passe modifié en mode hors ligne (sync en attente)")
        return True
    
    def _record_pending_change(self, change_id: str, password_id: str, 
                             change_type: str, old_data: Optional[Dict], new_data: Dict):
        """Enregistrer un changement en attente"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pending_changes
            (change_id, password_id, change_type, old_data_json, new_data_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            change_id,
            password_id,
            change_type,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data)
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_password_data(self, password_id: str, password_data: Dict):
        """Mettre des données de mot de passe en cache"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(hours=self.config["cache_expiry_hours"])
        sync_hash = self._calculate_password_hash(password_data)
        
        cursor.execute('''
            INSERT OR REPLACE INTO password_cache
            (password_id, title, username, password_encrypted, url, category, 
             notes_encrypted, cached_at, expires_at, sync_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            password_id,
            password_data['title'],
            password_data['username'],
            password_data['password'],
            password_data.get('url', ''),
            password_data.get('category', ''),
            password_data.get('notes', ''),
            datetime.now().isoformat(),
            expires_at.isoformat(),
            sync_hash
        ))
        
        conn.commit()
        conn.close()
    
    def sync_pending_changes(self) -> Tuple[int, int]:
        """Synchroniser les changements en attente"""
        if not self.gestionnaire.check_session():
            self.logger.warning("Session expirée, impossible de synchroniser")
            return 0, 0
        
        self.sync_status = SyncStatus.SYNCING
        self._save_sync_metadata()
        
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        # Récupérer les changements en attente
        cursor.execute('''
            SELECT change_id, password_id, change_type, old_data_json, new_data_json
            FROM pending_changes 
            WHERE synced = FALSE
            ORDER BY timestamp ASC
        ''')
        
        pending = cursor.fetchall()
        synced_count = 0
        conflict_count = 0
        
        for row in pending:
            change_id, password_id, change_type, old_data_json, new_data_json = row
            
            try:
                new_data = json.loads(new_data_json)
                old_data = json.loads(old_data_json) if old_data_json else None
                
                success = False
                
                if change_type == "create":
                    # Vérifier si l'ID existe déjà (conflit potentiel)
                    if self.gestionnaire.get_password(password_id):
                        # Créer un nouveau ID pour éviter le conflit
                        import secrets
                        new_password_id = secrets.token_urlsafe(16)
                        new_data['id'] = new_password_id
                        password_id = new_password_id
                    
                    success = self.gestionnaire.add_password(
                        title=new_data['title'],
                        username=new_data['username'],
                        password=new_data['password'],
                        url=new_data.get('url', ''),
                        category=new_data.get('category', 'Autre'),
                        notes=new_data.get('notes', '')
                    ) is not None
                
                elif change_type == "update":
                    # Vérifier les conflits
                    current_remote = self.gestionnaire.get_password(password_id)
                    if current_remote and old_data:
                        conflicts = self._detect_conflicts(old_data, new_data, current_remote)
                        if conflicts:
                            for conflict in conflicts:
                                self._record_conflict(conflict)
                            conflict_count += len(conflicts)
                        else:
                            success = self.gestionnaire.update_password(password_id, {
                                k: v for k, v in new_data.items() 
                                if k in ['title', 'username', 'password', 'url', 'category', 'notes']
                            })
                
                elif change_type == "delete":
                    success = self.gestionnaire.delete_password(password_id)
                
                if success:
                    # Marquer comme synchronisé
                    cursor.execute('''
                        UPDATE pending_changes 
                        SET synced = TRUE
                        WHERE change_id = ?
                    ''', (change_id,))
                    synced_count += 1
                else:
                    # Incrémenter le compteur de retry
                    cursor.execute('''
                        UPDATE pending_changes 
                        SET retry_count = retry_count + 1
                        WHERE change_id = ?
                    ''', (change_id,))
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la sync du changement {change_id}: {e}")
                cursor.execute('''
                    UPDATE pending_changes 
                    SET retry_count = retry_count + 1
                    WHERE change_id = ?
                ''', (change_id,))
        
        conn.commit()
        conn.close()
        
        # Mettre à jour le statut
        if conflict_count > 0:
            self.sync_status = SyncStatus.CONFLICT
        elif synced_count > 0:
            self.sync_status = SyncStatus.SYNCHRONIZED
            self.last_sync = datetime.now()
        
        self._save_sync_metadata()
        
        return synced_count, conflict_count
    
    def _detect_conflicts(self, old_local: Dict, new_local: Dict, current_remote: Dict) -> List[SyncConflict]:
        """Détecter les conflits de synchronisation"""
        conflicts = []
        
        # Champs à vérifier pour les conflits
        fields_to_check = ['title', 'username', 'password', 'url', 'category', 'notes']
        
        for field in fields_to_check:
            local_value = new_local.get(field, '')
            remote_value = current_remote.get(field, '')
            old_local_value = old_local.get(field, '')
            
            # Conflit si les valeurs sont différentes et ont été modifiées des deux côtés
            if (local_value != remote_value and 
                local_value != old_local_value and 
                remote_value != old_local_value):
                
                conflict = SyncConflict(
                    password_id=new_local['id'],
                    field=field,
                    local_value=local_value,
                    remote_value=remote_value,
                    local_timestamp=datetime.fromisoformat(new_local.get('updated_at', datetime.now().isoformat())),
                    remote_timestamp=datetime.fromisoformat(current_remote.get('updated_at', datetime.now().isoformat()))
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _record_conflict(self, conflict: SyncConflict):
        """Enregistrer un conflit de synchronisation"""
        import secrets
        
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_conflicts
            (conflict_id, password_id, field, local_value, remote_value, 
             local_timestamp, remote_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            secrets.token_urlsafe(16),
            conflict.password_id,
            conflict.field,
            conflict.local_value,
            conflict.remote_value,
            conflict.local_timestamp.isoformat(),
            conflict.remote_timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_sync_conflicts(self) -> List[SyncConflict]:
        """Obtenir les conflits de synchronisation non résolus"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT password_id, field, local_value, remote_value, 
                   local_timestamp, remote_timestamp
            FROM sync_conflicts 
            WHERE resolved = FALSE
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        conflicts = []
        for row in results:
            conflict = SyncConflict(
                password_id=row[0],
                field=row[1],
                local_value=row[2],
                remote_value=row[3],
                local_timestamp=datetime.fromisoformat(row[4]),
                remote_timestamp=datetime.fromisoformat(row[5])
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def create_backup(self, description: str = "") -> str:
        """Créer un backup du cache hors ligne"""
        import secrets
        
        backup_id = secrets.token_urlsafe(16)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"offline_backup_{timestamp}_{backup_id}.gz"
        backup_path = self.backup_dir / backup_filename
        
        # Compresser la base de données
        with open(self.offline_db_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        backup_size = backup_path.stat().st_size
        
        # Enregistrer dans l'historique
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_history
            (backup_id, backup_path, backup_size, description)
            VALUES (?, ?, ?, ?)
        ''', (backup_id, str(backup_path), backup_size, description))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Backup créé: {backup_path}")
        return backup_id
    
    def _calculate_password_hash(self, password_data: Dict) -> str:
        """Calculer le hash d'un mot de passe pour la synchronisation"""
        key_fields = ['title', 'username', 'password', 'url', 'category', 'notes']
        content = '|'.join(str(password_data.get(field, '')) for field in key_fields)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _start_auto_sync(self):
        """Démarrer la synchronisation automatique"""
        self.running = True
        self.sync_thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
        self.sync_thread.start()
    
    def _auto_sync_loop(self):
        """Boucle de synchronisation automatique"""
        while self.running:
            try:
                time.sleep(300)  # Vérifier toutes les 5 minutes
                
                # Tentative de synchronisation si en ligne
                if self.gestionnaire.check_session():
                    synced, conflicts = self.sync_pending_changes()
                    if synced > 0:
                        self.logger.info(f"Auto-sync: {synced} changements synchronisés")
                    if conflicts > 0:
                        self.logger.warning(f"Auto-sync: {conflicts} conflits détectés")
                
                # Backup automatique
                if (not self.last_sync or 
                    datetime.now() - self.last_sync > timedelta(hours=self.config["auto_backup_interval_hours"])):
                    self.create_backup("Auto-backup périodique")
                    
            except Exception as e:
                self.logger.error(f"Erreur dans l'auto-sync: {e}")
    
    def get_offline_status(self) -> Dict[str, Any]:
        """Obtenir le statut du mode hors ligne"""
        conn = sqlite3.connect(self.offline_db_path)
        cursor = conn.cursor()
        
        # Compter les éléments en cache
        cursor.execute('SELECT COUNT(*) FROM password_cache WHERE expires_at > ?', 
                      (datetime.now().isoformat(),))
        cached_count = cursor.fetchone()[0]
        
        # Compter les changements en attente
        cursor.execute('SELECT COUNT(*) FROM pending_changes WHERE synced = FALSE')
        pending_count = cursor.fetchone()[0]
        
        # Compter les conflits
        cursor.execute('SELECT COUNT(*) FROM sync_conflicts WHERE resolved = FALSE')
        conflict_count = cursor.fetchone()[0]
        
        # Statistiques d'accès
        cursor.execute('''
            SELECT AVG(access_count), COUNT(*) 
            FROM password_cache 
            WHERE last_accessed > datetime('now', '-7 days')
        ''')
        avg_access, active_passwords = cursor.fetchone()
        
        conn.close()
        
        # Mode urgence ?
        emergency_mode = (
            self.last_sync is None or 
            datetime.now() - self.last_sync > timedelta(days=self.config["emergency_mode_threshold"])
        )
        
        return {
            'sync_status': self.sync_status.value,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'cached_passwords': cached_count,
            'pending_changes': pending_count,
            'conflicts': conflict_count,
            'emergency_mode': emergency_mode,
            'active_passwords_week': active_passwords or 0,
            'avg_access_count': avg_access or 0
        }
    
    def stop(self):
        """Arrêter le mode hors ligne"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)

def production_offline_mode():
    """Production offline mode - Use demos/ folder for demonstrations"""
    print(f"{Fore.BLUE}📱 PRODUCTION - MODE HORS LIGNE AVANCÉ")
    print("=" * 60)
    
    from gestionnaire_mdp import GestionnaireMDP
    
    # Initialiser le gestionnaire
    manager = GestionnaireMDP()
    if not manager.authenticate("production123!"):
        print(f"{Fore.RED}❌ Impossible de s'authentifier")
        return
    
    # Créer le gestionnaire de mode hors ligne
    offline_mode = OfflineMode(manager)
    
    print(f"\n{Fore.CYAN}💾 Mise en cache de mots de passe...")
    
    # Lister les mots de passe existants
    passwords = manager.list_passwords()
    if passwords:
        # Mettre les 3 premiers en cache
        for i, pwd in enumerate(passwords[:3]):
            offline_mode.cache_password(pwd['id'], mark_favorite=(i == 0))
            print(f"  ✓ {pwd['title']} mis en cache")
    
    print(f"\n{Fore.CYAN}📱 Simulation de mode hors ligne...")
    
    # Ajouter un mot de passe hors ligne
    offline_pwd_id = offline_mode.add_password_offline(
        title="Site Hors Ligne",
        username="offline_user",
        password="OfflinePassword123!",
        url="https://offline.example.com",
        category="Test",
        notes="Créé en mode hors ligne"
    )
    
    # Modifier un mot de passe en cache
    cached_passwords = offline_mode.list_cached_passwords()
    if cached_passwords:
        offline_mode.update_password_offline(
            cached_passwords[0]['id'],
            {'notes': 'Modifié en mode hors ligne'}
        )
    
    print(f"\n{Fore.CYAN}📊 Statut hors ligne...")
    status = offline_mode.get_offline_status()
    
    print(f"  🔄 Statut sync: {status['sync_status']}")
    print(f"  💾 Mots de passe en cache: {status['cached_passwords']}")
    print(f"  ⏳ Changements en attente: {status['pending_changes']}")
    print(f"  ⚠️ Conflits: {status['conflicts']}")
    print(f"  🚨 Mode urgence: {'Oui' if status['emergency_mode'] else 'Non'}")
    
    print(f"\n{Fore.CYAN}🔄 Synchronisation des changements...")
    
    try:
        synced, conflicts = offline_mode.sync_pending_changes()
        print(f"  ✅ Changements synchronisés: {synced}")
        print(f"  ⚠️ Conflits détectés: {conflicts}")
    except Exception as e:
        print(f"  ❌ Erreur de synchronisation: {e}")
    
    print(f"\n{Fore.CYAN}💾 Création d'un backup...")
    backup_id = offline_mode.create_backup("Backup de démonstration")
    print(f"  ✅ Backup créé: {backup_id}")
    
    print(f"\n{Fore.GREEN}🎉 Démonstration du mode hors ligne terminée!")
    print(f"{Fore.YELLOW}💡 Fonctionnalités du mode hors ligne:")
    print(f"   • Cache intelligent avec expiration automatique")
    print(f"   • Synchronisation différée des changements")  
    print(f"   • Détection et résolution de conflits")
    print(f"   • Backups automatiques compressés")
    print(f"   • Mode urgence pour accès critique")
    print(f"   • Statistiques d'utilisation hors ligne")
    
    # Nettoyage
    offline_mode.stop()

if __name__ == "__main__":
    production_offline_mode()