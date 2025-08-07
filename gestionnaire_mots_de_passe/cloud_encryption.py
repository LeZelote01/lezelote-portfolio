#!/usr/bin/env python3
"""
Module de chiffrement pour la synchronisation cloud
Gestionnaire de Mots de Passe - Cloud Encryption Module
"""

import os
import json
import base64
import hashlib
from typing import Dict, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring

class CloudEncryption:
    """Gestionnaire de chiffrement pour les données cloud"""
    
    def __init__(self, service_name: str = "GestionnairePasswords_CloudSync"):
        self.service_name = service_name
        self.encryption_keys = {}
        self.load_encryption_keys()
    
    def load_encryption_keys(self):
        """Charger les clés de chiffrement depuis le keyring"""
        try:
            keys_json = keyring.get_password(self.service_name, "encryption_keys")
            if keys_json:
                self.encryption_keys = json.loads(keys_json)
        except Exception as e:
            print(f"Erreur lors du chargement des clés de chiffrement: {e}")
            self.encryption_keys = {}
    
    def save_encryption_keys(self):
        """Sauvegarder les clés de chiffrement dans le keyring"""
        try:
            keys_json = json.dumps(self.encryption_keys)
            keyring.set_password(self.service_name, "encryption_keys", keys_json)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des clés de chiffrement: {e}")
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """Dériver une clé de chiffrement depuis un mot de passe"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def generate_encryption_key(self, key_id: str) -> str:
        """Générer une nouvelle clé de chiffrement"""
        key = Fernet.generate_key()
        key_str = key.decode('utf-8')
        
        # Sauvegarder la clé
        self.encryption_keys[key_id] = {
            'key': key_str,
            'created_at': str(int(os.times().elapsed)),
            'algorithm': 'Fernet_AES256'
        }
        self.save_encryption_keys()
        
        return key_str
    
    def get_encryption_key(self, key_id: str) -> Optional[str]:
        """Obtenir une clé de chiffrement"""
        key_data = self.encryption_keys.get(key_id)
        return key_data['key'] if key_data else None
    
    def encrypt_data(self, data: str, key_id: str = "default") -> Tuple[str, Dict]:
        """Chiffrer des données avec une clé spécifique"""
        # Obtenir ou générer la clé
        key_str = self.get_encryption_key(key_id)
        if not key_str:
            key_str = self.generate_encryption_key(key_id)
        
        try:
            fernet = Fernet(key_str.encode())
            encrypted_data = fernet.encrypt(data.encode('utf-8'))
            
            # Métadonnées de chiffrement
            metadata = {
                'key_id': key_id,
                'algorithm': 'Fernet_AES256',
                'version': '1.0',
                'checksum': hashlib.sha256(data.encode('utf-8')).hexdigest()
            }
            
            return base64.b64encode(encrypted_data).decode('utf-8'), metadata
            
        except Exception as e:
            print(f"Erreur lors du chiffrement: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str, metadata: Dict) -> str:
        """Déchiffrer des données"""
        key_id = metadata.get('key_id', 'default')
        key_str = self.get_encryption_key(key_id)
        
        if not key_str:
            raise ValueError(f"Clé de déchiffrement non trouvée pour {key_id}")
        
        try:
            fernet = Fernet(key_str.encode())
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(encrypted_bytes).decode('utf-8')
            
            # Vérifier l'intégrité si checksum disponible
            if 'checksum' in metadata:
                calculated_checksum = hashlib.sha256(decrypted_data.encode('utf-8')).hexdigest()
                if calculated_checksum != metadata['checksum']:
                    raise ValueError("Checksum de vérification échoué - données corrompues")
            
            return decrypted_data
            
        except Exception as e:
            print(f"Erreur lors du déchiffrement: {e}")
            raise
    
    def encrypt_password_data(self, password_data: Dict, master_password: str) -> Tuple[str, Dict]:
        """Chiffrer les données d'un mot de passe pour le cloud"""
        # Convertir les données en JSON
        json_data = json.dumps(password_data, ensure_ascii=False, indent=None)
        
        # Dériver une clé à partir du mot de passe maître
        key, salt = self.derive_key_from_password(master_password)
        
        try:
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(json_data.encode('utf-8'))
            
            # Métadonnées incluant le salt
            metadata = {
                'algorithm': 'PBKDF2_Fernet_AES256',
                'version': '1.0',
                'salt': base64.b64encode(salt).decode('utf-8'),
                'checksum': hashlib.sha256(json_data.encode('utf-8')).hexdigest(),
                'encrypted_at': str(int(os.times().elapsed))
            }
            
            return base64.b64encode(encrypted_data).decode('utf-8'), metadata
            
        except Exception as e:
            print(f"Erreur lors du chiffrement des données de mot de passe: {e}")
            raise
    
    def decrypt_password_data(self, encrypted_data: str, metadata: Dict, master_password: str) -> Dict:
        """Déchiffrer les données d'un mot de passe depuis le cloud"""
        if 'salt' not in metadata:
            raise ValueError("Salt manquant dans les métadonnées")
        
        try:
            salt = base64.b64decode(metadata['salt'].encode('utf-8'))
            key, _ = self.derive_key_from_password(master_password, salt)
            
            fernet = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_json = fernet.decrypt(encrypted_bytes).decode('utf-8')
            
            # Vérifier l'intégrité
            if 'checksum' in metadata:
                calculated_checksum = hashlib.sha256(decrypted_json.encode('utf-8')).hexdigest()
                if calculated_checksum != metadata['checksum']:
                    raise ValueError("Checksum de vérification échoué - données corrompues")
            
            return json.loads(decrypted_json)
            
        except Exception as e:
            print(f"Erreur lors du déchiffrement des données de mot de passe: {e}")
            raise
    
    def create_encrypted_backup(self, database_data: Dict, master_password: str) -> Tuple[str, Dict]:
        """Créer une sauvegarde chiffrée complète de la base de données"""
        try:
            # Ajouter des métadonnées à la sauvegarde
            backup_data = {
                'version': '1.0',
                'created_at': str(int(os.times().elapsed)),
                'database_data': database_data,
                'backup_type': 'full'
            }
            
            return self.encrypt_password_data(backup_data, master_password)
            
        except Exception as e:
            print(f"Erreur lors de la création de la sauvegarde chiffrée: {e}")
            raise
    
    def restore_encrypted_backup(self, encrypted_backup: str, metadata: Dict, master_password: str) -> Dict:
        """Restaurer une sauvegarde chiffrée"""
        try:
            backup_data = self.decrypt_password_data(encrypted_backup, metadata, master_password)
            
            # Vérifier que c'est bien une sauvegarde valide
            if 'database_data' not in backup_data:
                raise ValueError("Format de sauvegarde invalide")
            
            return backup_data['database_data']
            
        except Exception as e:
            print(f"Erreur lors de la restauration de la sauvegarde: {e}")
            raise
    
    def rotate_encryption_key(self, old_key_id: str, new_key_id: str) -> bool:
        """Effectuer une rotation des clés de chiffrement"""
        try:
            # Générer une nouvelle clé
            new_key = self.generate_encryption_key(new_key_id)
            
            # Marquer l'ancienne clé comme dépréciée
            if old_key_id in self.encryption_keys:
                self.encryption_keys[old_key_id]['deprecated'] = True
                self.encryption_keys[old_key_id]['deprecated_at'] = str(int(os.times().elapsed))
            
            self.save_encryption_keys()
            
            print(f"Rotation des clés effectuée: {old_key_id} -> {new_key_id}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la rotation des clés: {e}")
            return False
    
    def get_key_info(self, key_id: str) -> Optional[Dict]:
        """Obtenir les informations sur une clé de chiffrement"""
        key_data = self.encryption_keys.get(key_id)
        if key_data:
            # Retourner les infos sans la clé elle-même
            return {
                'key_id': key_id,
                'created_at': key_data.get('created_at'),
                'algorithm': key_data.get('algorithm'),
                'deprecated': key_data.get('deprecated', False)
            }
        return None
    
    def cleanup_deprecated_keys(self, max_age_days: int = 90):
        """Nettoyer les clés dépréciées anciennes"""
        current_time = int(os.times().elapsed)
        max_age_seconds = max_age_days * 24 * 3600
        
        keys_to_remove = []
        
        for key_id, key_data in self.encryption_keys.items():
            if key_data.get('deprecated', False):
                deprecated_at = int(key_data.get('deprecated_at', 0))
                if current_time - deprecated_at > max_age_seconds:
                    keys_to_remove.append(key_id)
        
        for key_id in keys_to_remove:
            del self.encryption_keys[key_id]
            print(f"Clé dépréciée supprimée: {key_id}")
        
        if keys_to_remove:
            self.save_encryption_keys()
        
        return len(keys_to_remove)

# Instance globale de chiffrement
cloud_encryption = CloudEncryption()