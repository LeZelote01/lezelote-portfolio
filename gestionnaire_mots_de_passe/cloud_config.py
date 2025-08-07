#!/usr/bin/env python3
"""
Configuration pour la synchronisation cloud chiffrée
Gestionnaire de Mots de Passe - Cloud Sync Module
"""

import os
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CloudService:
    """Configuration d'un service cloud"""
    name: str
    enabled: bool
    client_id: str
    client_secret: str
    scopes: List[str]
    auth_url: str
    token_url: str
    api_base_url: str

class CloudConfig:
    """Gestionnaire de configuration cloud"""
    
    def __init__(self, config_file: str = "cloud_config.json"):
        self.config_file = config_file
        self.config_path = Path(__file__).parent / config_file
        self.services = {}
        self.load_config()
    
    def load_config(self):
        """Charger la configuration depuis le fichier"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._parse_config(config_data)
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration cloud: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _parse_config(self, config_data: Dict):
        """Parser la configuration chargée"""
        for service_name, service_config in config_data.get('services', {}).items():
            self.services[service_name] = CloudService(
                name=service_name,
                enabled=service_config.get('enabled', False),
                client_id=service_config.get('client_id', ''),
                client_secret=service_config.get('client_secret', ''),
                scopes=service_config.get('scopes', []),
                auth_url=service_config.get('auth_url', ''),
                token_url=service_config.get('token_url', ''),
                api_base_url=service_config.get('api_base_url', '')
            )
    
    def _create_default_config(self):
        """Créer la configuration par défaut"""
        self.services = {
            'google_drive': CloudService(
                name='google_drive',
                enabled=False,  # Désactivé par défaut jusqu'à configuration des clés
                client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
                scopes=[
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive.appdata'
                ],
                auth_url='https://accounts.google.com/o/oauth2/auth',
                token_url='https://accounts.google.com/o/oauth2/token',
                api_base_url='https://www.googleapis.com/drive/v3'
            ),
            'dropbox': CloudService(
                name='dropbox',
                enabled=False,  # Désactivé par défaut jusqu'à configuration des clés
                client_id=os.getenv('DROPBOX_APP_KEY', ''),
                client_secret=os.getenv('DROPBOX_APP_SECRET', ''),
                scopes=[
                    'files.metadata.write',
                    'files.content.write',
                    'files.content.read'
                ],
                auth_url='https://www.dropbox.com/oauth2/authorize',
                token_url='https://api.dropboxapi.com/oauth2/token',
                api_base_url='https://api.dropboxapi.com/2'
            )
        }
        self.save_config()
    
    def save_config(self):
        """Sauvegarder la configuration dans le fichier"""
        config_data = {
            'services': {}
        }
        
        for service_name, service in self.services.items():
            config_data['services'][service_name] = {
                'enabled': service.enabled,
                'client_id': service.client_id,
                'client_secret': service.client_secret,
                'scopes': service.scopes,
                'auth_url': service.auth_url,
                'token_url': service.token_url,
                'api_base_url': service.api_base_url
            }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration cloud: {e}")
    
    def get_service(self, service_name: str) -> Optional[CloudService]:
        """Obtenir la configuration d'un service"""
        return self.services.get(service_name)
    
    def is_service_configured(self, service_name: str) -> bool:
        """Vérifier si un service est configuré"""
        service = self.get_service(service_name)
        if not service:
            return False
        return bool(service.client_id and service.client_secret)
    
    def is_service_enabled(self, service_name: str) -> bool:
        """Vérifier si un service est activé"""
        service = self.get_service(service_name)
        if not service:
            return False
        return service.enabled and self.is_service_configured(service_name)
    
    def configure_service(self, service_name: str, client_id: str, client_secret: str, enabled: bool = True):
        """Configurer un service cloud"""
        if service_name in self.services:
            self.services[service_name].client_id = client_id
            self.services[service_name].client_secret = client_secret
            self.services[service_name].enabled = enabled
            self.save_config()
            return True
        return False
    
    def get_enabled_services(self) -> List[str]:
        """Obtenir la liste des services activés"""
        return [name for name, service in self.services.items() if service.enabled and self.is_service_configured(name)]
    
    def get_sync_settings(self) -> Dict:
        """Obtenir les paramètres de synchronisation"""
        return {
            'auto_sync': True,
            'sync_interval_minutes': 30,
            'conflict_resolution': 'ask_user',  # 'ask_user', 'local_wins', 'remote_wins', 'keep_both'
            'encryption_enabled': True,
            'compression_enabled': True
        }

# Instance globale de configuration
cloud_config = CloudConfig()