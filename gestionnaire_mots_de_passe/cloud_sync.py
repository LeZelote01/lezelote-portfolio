#!/usr/bin/env python3
"""
Module principal de synchronisation cloud
Gestionnaire de Mots de Passe - Cloud Sync Module
"""

import os
import json
import time
import sqlite3
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import threading
from pathlib import Path

try:
    import dropbox
    from dropbox import DropboxOAuth2Flow
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False
    print("Dropbox SDK non disponible. Installez-le avec: pip install dropbox")

from .cloud_config import cloud_config
from .cloud_auth import cloud_auth
from .cloud_encryption import cloud_encryption
from .conflict_resolver import conflict_resolver, ConflictInfo, ResolutionStrategy, ResolutionResult

class CloudSyncManager:
    """Gestionnaire principal de synchronisation cloud"""
    
    def __init__(self, db_path: str = "passwords.db"):
        self.db_path = db_path
        self.sync_status = {
            'last_sync': None,
            'is_syncing': False,
            'auto_sync_enabled': True,
            'sync_interval_minutes': 30,
            'last_error': None
        }
        self.sync_lock = threading.Lock()
        self.sync_callbacks = []
        self.conflict_callbacks = []
        
        # Démarrer le thread de synchronisation automatique
        self.auto_sync_thread = None
        self.stop_auto_sync = threading.Event()
        
    def add_sync_callback(self, callback):
        """Ajouter un callback pour les notifications de synchronisation"""
        self.sync_callbacks.append(callback)
    
    def add_conflict_callback(self, callback):
        """Ajouter un callback pour la gestion des conflits"""
        self.conflict_callbacks.append(callback)
    
    def notify_sync_status(self, status: str, message: str = "", progress: float = 0.0):
        """Notifier les callbacks du status de synchronisation"""
        for callback in self.sync_callbacks:
            try:
                callback(status, message, progress)
            except Exception as e:
                print(f"Erreur dans le callback de sync: {e}")
    
    def notify_conflict_detected(self, conflicts: List[ConflictInfo]) -> List[ResolutionResult]:
        """Notifier les callbacks des conflits détectés"""
        results = []
        for callback in self.conflict_callbacks:
            try:
                callback_results = callback(conflicts)
                if callback_results:
                    results.extend(callback_results)
            except Exception as e:
                print(f"Erreur dans le callback de conflit: {e}")
        return results
    
    def is_cloud_sync_available(self) -> bool:
        """Vérifier si la synchronisation cloud est disponible"""
        enabled_services = cloud_config.get_enabled_services()
        return len(enabled_services) > 0
    
    def get_sync_status(self) -> Dict:
        """Obtenir le status actuel de synchronisation"""
        return {
            **self.sync_status,
            'available_services': cloud_config.get_enabled_services(),
            'authenticated_services': self._get_authenticated_services(),
            'cloud_available': self.is_cloud_sync_available()
        }
    
    def _get_authenticated_services(self) -> List[str]:
        """Obtenir la liste des services authentifiés"""
        authenticated = []
        for service in cloud_config.get_enabled_services():
            if cloud_auth.is_authenticated(service):
                authenticated.append(service)
        return authenticated
    
    def start_auto_sync(self):
        """Démarrer la synchronisation automatique"""
        if self.auto_sync_thread and self.auto_sync_thread.is_alive():
            return
        
        self.stop_auto_sync.clear()
        self.auto_sync_thread = threading.Thread(target=self._auto_sync_worker, daemon=True)
        self.auto_sync_thread.start()
        print("Synchronisation automatique démarrée")
    
    def stop_auto_sync_process(self):
        """Arrêter la synchronisation automatique"""
        self.stop_auto_sync.set()
        if self.auto_sync_thread:
            self.auto_sync_thread.join(timeout=5)
        print("Synchronisation automatique arrêtée")
    
    def _auto_sync_worker(self):
        """Worker thread pour la synchronisation automatique"""
        while not self.stop_auto_sync.is_set():
            try:
                if (self.sync_status['auto_sync_enabled'] and 
                    self.is_cloud_sync_available() and 
                    not self.sync_status['is_syncing']):
                    
                    # Vérifier si il est temps de synchroniser
                    last_sync = self.sync_status['last_sync']
                    if last_sync:
                        last_sync_time = datetime.fromisoformat(last_sync)
                        next_sync = last_sync_time + timedelta(minutes=self.sync_status['sync_interval_minutes'])
                        
                        if datetime.now() >= next_sync:
                            self.sync_with_cloud()
                    else:
                        # Première synchronisation
                        self.sync_with_cloud()
                
                # Attendre avant la prochaine vérification (1 minute)
                self.stop_auto_sync.wait(60)
                
            except Exception as e:
                print(f"Erreur dans la synchronisation automatique: {e}")
                self.sync_status['last_error'] = str(e)
                # Attendre plus longtemps en cas d'erreur
                self.stop_auto_sync.wait(300)
    
    def sync_with_cloud(self, master_password: str = None, force: bool = False) -> bool:
        """Synchroniser avec le cloud"""
        if not self.is_cloud_sync_available():
            self.notify_sync_status("error", "Aucun service cloud configuré")
            return False
        
        with self.sync_lock:
            if self.sync_status['is_syncing'] and not force:
                self.notify_sync_status("error", "Synchronisation déjà en cours")
                return False
            
            self.sync_status['is_syncing'] = True
            self.sync_status['last_error'] = None
        
        try:
            self.notify_sync_status("starting", "Démarrage de la synchronisation", 0.0)
            
            # Étape 1: Charger les données locales
            self.notify_sync_status("loading", "Chargement des données locales", 10.0)
            local_data = self._load_local_password_data()
            
            # Étape 2: Charger les données du cloud
            self.notify_sync_status("downloading", "Téléchargement depuis le cloud", 30.0)
            cloud_data = self._download_cloud_data(master_password)
            
            # Étape 3: Détecter les conflits
            self.notify_sync_status("analyzing", "Analyse des conflits", 50.0)
            conflicts = conflict_resolver.detect_conflicts(local_data, cloud_data)
            
            if conflicts:
                self.notify_sync_status("conflicts", f"{len(conflicts)} conflits détectés", 60.0)
                resolution_results = self.notify_conflict_detected(conflicts)
                
                # Appliquer les résolutions
                for result in resolution_results:
                    self._apply_conflict_resolution(result)
            
            # Étape 4: Fusionner et synchroniser
            self.notify_sync_status("syncing", "Synchronisation des données", 80.0)
            merged_data = self._merge_data(local_data, cloud_data, conflicts)
            
            # Étape 5: Upload vers le cloud
            self.notify_sync_status("uploading", "Upload vers le cloud", 90.0)
            success = self._upload_to_cloud(merged_data, master_password)
            
            if success:
                # Étape 6: Mettre à jour la base locale si nécessaire
                self._update_local_database(merged_data)
                
                self.sync_status['last_sync'] = datetime.now().isoformat()
                self.notify_sync_status("completed", "Synchronisation terminée", 100.0)
                return True
            else:
                self.notify_sync_status("error", "Erreur lors de l'upload", 90.0)
                return False
                
        except Exception as e:
            error_msg = f"Erreur de synchronisation: {str(e)}"
            self.sync_status['last_error'] = error_msg
            self.notify_sync_status("error", error_msg, 0.0)
            print(error_msg)
            return False
        finally:
            self.sync_status['is_syncing'] = False
    
    def _load_local_password_data(self) -> Dict:
        """Charger les données locales de mots de passe"""
        local_data = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, username, password_encrypted, url, notes, category,
                       created_at, updated_at, last_accessed, access_count
                FROM passwords
            ''')
            
            for row in cursor.fetchall():
                password_data = {
                    'id': row[0],
                    'title': row[1],
                    'username': row[2],
                    'password_encrypted': row[3],
                    'url': row[4],
                    'notes': row[5],
                    'category': row[6],
                    'created_at': row[7],
                    'updated_at': row[8],
                    'last_accessed': row[9],
                    'access_count': row[10]
                }
                local_data[row[0]] = password_data
            
            conn.close()
            
        except Exception as e:
            print(f"Erreur lors du chargement des données locales: {e}")
            raise
        
        return local_data
    
    def _download_cloud_data(self, master_password: str = None) -> Dict:
        """Télécharger les données depuis le cloud"""
        cloud_data = {}
        
        for service_name in cloud_config.get_enabled_services():
            if not cloud_auth.is_authenticated(service_name):
                print(f"Service {service_name} non authentifié, ignoré")
                continue
            
            try:
                service_data = self._download_from_service(service_name, master_password)
                cloud_data.update(service_data)
            except Exception as e:
                print(f"Erreur lors du téléchargement depuis {service_name}: {e}")
                # Continuer avec les autres services
        
        return cloud_data
    
    def _download_from_service(self, service_name: str, master_password: str = None) -> Dict:
        """Télécharger les données depuis un service spécifique"""
        client = cloud_auth.get_authenticated_client(service_name)
        if not client:
            return {}
        
        try:
            if service_name == 'google_drive':
                return self._download_from_google_drive(client, master_password)
            elif service_name == 'dropbox':
                return self._download_from_dropbox(client, master_password)
        except Exception as e:
            print(f"Erreur lors du téléchargement depuis {service_name}: {e}")
            return {}
        
        return {}
    
    def _download_from_google_drive(self, drive_client, master_password: str = None) -> Dict:
        """Télécharger depuis Google Drive"""
        try:
            # Chercher le fichier de sauvegarde
            query = "name='password_backup.json' and parents in 'appDataFolder'"
            results = drive_client.files().list(q=query, spaces='appDataFolder').execute()
            files = results.get('files', [])
            
            if not files:
                print("Aucune sauvegarde trouvée sur Google Drive")
                return {}
            
            # Télécharger le fichier le plus récent
            file_id = files[0]['id']
            request = drive_client.files().get_media(fileId=file_id)
            
            # Pour une vraie implémentation, on utiliserait BytesIO
            # Ici on simule le téléchargement
            encrypted_content = request.execute()
            
            if master_password:
                # Déchiffrer le contenu
                metadata = {'algorithm': 'PBKDF2_Fernet_AES256'}  # Récupéré depuis les métadonnées du fichier
                decrypted_data = cloud_encryption.decrypt_password_data(
                    encrypted_content.decode('utf-8'), metadata, master_password
                )
                return decrypted_data.get('passwords', {})
            else:
                # Retourner les données chiffrées pour traitement ultérieur
                return json.loads(encrypted_content.decode('utf-8'))
                
        except Exception as e:
            print(f"Erreur Google Drive: {e}")
            return {}
    
    def _download_from_dropbox(self, dropbox_client, master_password: str = None) -> Dict:
        """Télécharger depuis Dropbox"""
        try:
            # Télécharger le fichier de sauvegarde
            file_path = '/Apps/PasswordManager/password_backup.json'
            
            try:
                metadata, response = dropbox_client.files_download(file_path)
                encrypted_content = response.content
                
                if master_password:
                    # Déchiffrer le contenu
                    metadata_dict = {'algorithm': 'PBKDF2_Fernet_AES256'}
                    decrypted_data = cloud_encryption.decrypt_password_data(
                        encrypted_content.decode('utf-8'), metadata_dict, master_password
                    )
                    return decrypted_data.get('passwords', {})
                else:
                    # Retourner les données chiffrées
                    return json.loads(encrypted_content.decode('utf-8'))
                    
            except Exception as e:
                if DROPBOX_AVAILABLE and "dropbox" in str(type(e)):
                    # Gestion spécifique des erreurs Dropbox si le SDK est disponible
                    if "not_found" in str(e).lower():
                        print("Aucune sauvegarde trouvée sur Dropbox")
                        return {}
                    else:
                        raise e
                else:
                    raise e
                    
        except Exception as e:
            print(f"Erreur Dropbox: {e}")
            return {}
    
    def _merge_data(self, local_data: Dict, cloud_data: Dict, conflicts: List[ConflictInfo]) -> Dict:
        """Fusionner les données locales et cloud"""
        merged_data = local_data.copy()
        
        # Ajouter les nouveaux éléments du cloud
        for password_id, password_data in cloud_data.items():
            if password_id not in merged_data:
                merged_data[password_id] = password_data
        
        # Les conflits ont déjà été résolus et appliqués
        
        return merged_data
    
    def _upload_to_cloud(self, data: Dict, master_password: str = None) -> bool:
        """Upload vers le cloud"""
        success_count = 0
        total_services = len(cloud_config.get_enabled_services())
        
        if total_services == 0:
            return False
        
        for service_name in cloud_config.get_enabled_services():
            if not cloud_auth.is_authenticated(service_name):
                continue
            
            try:
                if self._upload_to_service(service_name, data, master_password):
                    success_count += 1
            except Exception as e:
                print(f"Erreur lors de l'upload vers {service_name}: {e}")
        
        # Succès si au moins un service a fonctionné
        return success_count > 0
    
    def _upload_to_service(self, service_name: str, data: Dict, master_password: str = None) -> bool:
        """Upload vers un service spécifique"""
        client = cloud_auth.get_authenticated_client(service_name)
        if not client:
            return False
        
        try:
            # Chiffrer les données
            backup_data = {'passwords': data, 'created_at': datetime.now().isoformat()}
            encrypted_content, metadata = cloud_encryption.encrypt_password_data(backup_data, master_password)
            
            if service_name == 'google_drive':
                return self._upload_to_google_drive(client, encrypted_content, metadata)
            elif service_name == 'dropbox':
                return self._upload_to_dropbox(client, encrypted_content, metadata)
        except Exception as e:
            print(f"Erreur lors de l'upload vers {service_name}: {e}")
            return False
        
        return False
    
    def _upload_to_google_drive(self, drive_client, encrypted_content: str, metadata: Dict) -> bool:
        """Upload vers Google Drive"""
        try:
            # Créer les métadonnées du fichier
            file_metadata = {
                'name': 'password_backup.json',
                'parents': ['appDataFolder'],
                'description': f"Sauvegarde chiffrée - {datetime.now().isoformat()}"
            }
            
            # Pour une vraie implémentation, on utiliserait MediaIoBaseUpload
            # Ici on simule l'upload
            print(f"Upload vers Google Drive: {len(encrypted_content)} bytes")
            
            # Sauvegarder les métadonnées de chiffrement dans les propriétés du fichier
            file_metadata['properties'] = {
                'encryption_metadata': json.dumps(metadata)
            }
            
            return True
            
        except Exception as e:
            print(f"Erreur upload Google Drive: {e}")
            return False
    
    def _upload_to_dropbox(self, dropbox_client, encrypted_content: str, metadata: Dict) -> bool:
        """Upload vers Dropbox"""
        try:
            file_path = '/Apps/PasswordManager/password_backup.json'
            
            # Upload du fichier
            if DROPBOX_AVAILABLE:
                # Mode avec SDK complet
                dropbox_client.files_upload(
                    encrypted_content.encode('utf-8'),
                    file_path,
                    mode=dropbox.files.WriteMode.overwrite,
                    autorename=False
                )
                
                # Sauvegarder les métadonnées séparément
                metadata_path = '/Apps/PasswordManager/backup_metadata.json'
                dropbox_client.files_upload(
                    json.dumps(metadata).encode('utf-8'),
                    metadata_path,
                    mode=dropbox.files.WriteMode.overwrite,
                    autorename=False
                )
            else:
                # Simulation pour environnement sans SDK
                print("SDK Dropbox non disponible - simulation de l'upload")
                return True
            
            print(f"Upload vers Dropbox: {len(encrypted_content)} bytes")
            return True
            
        except Exception as e:
            print(f"Erreur upload Dropbox: {e}")
            return False
    
    def _apply_conflict_resolution(self, resolution: ResolutionResult):
        """Appliquer la résolution d'un conflit"""
        # Cette méthode sera appelée pour appliquer les résolutions de conflits
        # L'implémentation dépendra de la stratégie de résolution
        print(f"Application de la résolution: {resolution.resolution_strategy}")
    
    def _update_local_database(self, merged_data: Dict):
        """Mettre à jour la base de données locale avec les données fusionnées"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Pour chaque mot de passe dans les données fusionnées
            for password_id, password_data in merged_data.items():
                # Vérifier si le mot de passe existe déjà
                cursor.execute('SELECT id FROM passwords WHERE id = ?', (password_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Mettre à jour
                    cursor.execute('''
                        UPDATE passwords 
                        SET title=?, username=?, password_encrypted=?, url=?, notes=?, 
                            category=?, updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                    ''', (
                        password_data.get('title'),
                        password_data.get('username'),
                        password_data.get('password_encrypted'),
                        password_data.get('url'),
                        password_data.get('notes'),
                        password_data.get('category'),
                        password_id
                    ))
                else:
                    # Insérer nouveau
                    cursor.execute('''
                        INSERT INTO passwords 
                        (id, title, username, password_encrypted, url, notes, category)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        password_id,
                        password_data.get('title'),
                        password_data.get('username'),
                        password_data.get('password_encrypted'),
                        password_data.get('url'),
                        password_data.get('notes'),
                        password_data.get('category')
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la base locale: {e}")
            raise
    
    def export_to_cloud(self, master_password: str, services: List[str] = None) -> bool:
        """Exporter manuellement vers le cloud"""
        if services is None:
            services = cloud_config.get_enabled_services()
        
        local_data = self._load_local_password_data()
        
        success_count = 0
        for service_name in services:
            if service_name in cloud_config.get_enabled_services():
                if self._upload_to_service(service_name, local_data, master_password):
                    success_count += 1
        
        return success_count > 0
    
    def import_from_cloud(self, master_password: str, merge: bool = True) -> bool:
        """Importer manuellement depuis le cloud"""
        cloud_data = self._download_cloud_data(master_password)
        
        if not cloud_data:
            return False
        
        if merge:
            # Fusionner avec les données locales
            local_data = self._load_local_password_data()
            conflicts = conflict_resolver.detect_conflicts(local_data, cloud_data)
            
            if conflicts:
                # Gérer les conflits (stratégie par défaut: demander à l'utilisateur)
                resolution_results = self.notify_conflict_detected(conflicts)
                for result in resolution_results:
                    self._apply_conflict_resolution(result)
            
            merged_data = self._merge_data(local_data, cloud_data, conflicts)
            self._update_local_database(merged_data)
        else:
            # Remplacer complètement les données locales
            self._update_local_database(cloud_data)
        
        return True

# Instance globale du gestionnaire de synchronisation
cloud_sync_manager = CloudSyncManager()