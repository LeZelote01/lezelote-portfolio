#!/usr/bin/env python3
"""
Gestionnaire d'authentification OAuth2 pour les services cloud
Gestionnaire de Mots de Passe - Cloud Authentication Module
"""

import os
import json
import time
import urllib.parse
from typing import Dict, Optional, Tuple
import keyring
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import dropbox
from dropbox import DropboxOAuth2Flow

from .cloud_config import cloud_config

class CloudAuthenticator:
    """Gestionnaire d'authentification OAuth2 pour les services cloud"""
    
    def __init__(self):
        self.service_name = "GestionnairePasswords_CloudSync"
        self.credentials = {}
        self.load_saved_credentials()
    
    def load_saved_credentials(self):
        """Charger les credentials sauvegardées depuis le keyring"""
        for service_name in ['google_drive', 'dropbox']:
            try:
                creds_json = keyring.get_password(self.service_name, f"{service_name}_credentials")
                if creds_json:
                    self.credentials[service_name] = json.loads(creds_json)
            except Exception as e:
                print(f"Erreur lors du chargement des credentials {service_name}: {e}")
    
    def save_credentials(self, service_name: str, credentials: Dict):
        """Sauvegarder les credentials dans le keyring"""
        try:
            creds_json = json.dumps(credentials)
            keyring.set_password(self.service_name, f"{service_name}_credentials", creds_json)
            self.credentials[service_name] = credentials
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des credentials {service_name}: {e}")
            return False
    
    def get_credentials(self, service_name: str) -> Optional[Dict]:
        """Obtenir les credentials pour un service"""
        return self.credentials.get(service_name)
    
    def is_authenticated(self, service_name: str) -> bool:
        """Vérifier si l'utilisateur est authentifié pour un service"""
        creds = self.get_credentials(service_name)
        if not creds:
            return False
        
        # Vérifier si le token n'est pas expiré
        if 'expires_at' in creds:
            if time.time() >= creds['expires_at']:
                # Token expiré, essayer de le rafraîchir
                return self.refresh_token(service_name)
        
        return True
    
    def get_authorization_url(self, service_name: str, redirect_uri: str = "http://localhost:8080") -> Optional[str]:
        """Générer l'URL d'autorisation OAuth2"""
        service_config = cloud_config.get_service(service_name)
        if not service_config or not cloud_config.is_service_configured(service_name):
            return None
        
        if service_name == 'google_drive':
            return self._get_google_auth_url(service_config, redirect_uri)
        elif service_name == 'dropbox':
            return self._get_dropbox_auth_url(service_config, redirect_uri)
        
        return None
    
    def _get_google_auth_url(self, service_config, redirect_uri: str) -> str:
        """Générer l'URL d'autorisation Google"""
        try:
            # Créer un fichier temporaire pour les credentials OAuth
            client_config = {
                "web": {
                    "client_id": service_config.client_id,
                    "client_secret": service_config.client_secret,
                    "auth_uri": service_config.auth_url,
                    "token_uri": service_config.token_url,
                    "redirect_uris": [redirect_uri]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=service_config.scopes,
                redirect_uri=redirect_uri
            )
            
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Sauvegarder l'état pour la validation
            self.save_oauth_state('google_drive', state, flow)
            
            return auth_url
        except Exception as e:
            print(f"Erreur lors de la génération de l'URL Google: {e}")
            return None
    
    def _get_dropbox_auth_url(self, service_config, redirect_uri: str) -> str:
        """Générer l'URL d'autorisation Dropbox"""
        try:
            flow = DropboxOAuth2Flow(
                consumer_key=service_config.client_id,
                consumer_secret=service_config.client_secret,
                redirect_uri=redirect_uri,
                session={},
                csrf_token_session_key='dropbox-auth-csrf-token'
            )
            
            auth_url = flow.start()
            
            # Sauvegarder le flow pour récupérer le token plus tard
            self.save_oauth_state('dropbox', 'dropbox_flow', flow)
            
            return auth_url
        except Exception as e:
            print(f"Erreur lors de la génération de l'URL Dropbox: {e}")
            return None
    
    def save_oauth_state(self, service_name: str, state: str, flow_data):
        """Sauvegarder l'état OAuth temporairement"""
        # Pour la démo, on utilise des variables d'instance
        # En production, il faudrait utiliser un stockage temporaire plus robuste
        if not hasattr(self, '_oauth_states'):
            self._oauth_states = {}
        self._oauth_states[service_name] = {'state': state, 'flow': flow_data}
    
    def get_oauth_state(self, service_name: str):
        """Récupérer l'état OAuth"""
        if not hasattr(self, '_oauth_states'):
            return None
        return self._oauth_states.get(service_name)
    
    def handle_oauth_callback(self, service_name: str, authorization_response: str) -> bool:
        """Gérer le callback OAuth et échanger le code contre un token"""
        if service_name == 'google_drive':
            return self._handle_google_callback(authorization_response)
        elif service_name == 'dropbox':
            return self._handle_dropbox_callback(authorization_response)
        return False
    
    def _handle_google_callback(self, authorization_response: str) -> bool:
        """Gérer le callback Google OAuth"""
        try:
            oauth_state = self.get_oauth_state('google_drive')
            if not oauth_state:
                print("État OAuth Google non trouvé")
                return False
            
            flow = oauth_state['flow']
            flow.fetch_token(authorization_response=authorization_response)
            
            credentials = flow.credentials
            creds_dict = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'expires_at': credentials.expiry.timestamp() if credentials.expiry else None,
                'token_type': 'Bearer',
                'scopes': credentials.scopes
            }
            
            return self.save_credentials('google_drive', creds_dict)
        except Exception as e:
            print(f"Erreur lors du callback Google: {e}")
            return False
    
    def _handle_dropbox_callback(self, authorization_response: str) -> bool:
        """Gérer le callback Dropbox OAuth"""
        try:
            oauth_state = self.get_oauth_state('dropbox')
            if not oauth_state:
                print("État OAuth Dropbox non trouvé")
                return False
            
            flow = oauth_state['flow']
            
            # Extraire le code d'autorisation de l'URL
            parsed_url = urllib.parse.urlparse(authorization_response)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            auth_code = query_params.get('code', [None])[0]
            
            if not auth_code:
                print("Code d'autorisation Dropbox non trouvé")
                return False
            
            oauth_result = flow.finish(auth_code)
            
            creds_dict = {
                'access_token': oauth_result.access_token,
                'account_id': oauth_result.account_id,
                'user_id': oauth_result.user_id,
                'token_type': 'Bearer'
            }
            
            return self.save_credentials('dropbox', creds_dict)
        except Exception as e:
            print(f"Erreur lors du callback Dropbox: {e}")
            return False
    
    def refresh_token(self, service_name: str) -> bool:
        """Rafraîchir le token d'accès"""
        creds = self.get_credentials(service_name)
        if not creds:
            return False
        
        if service_name == 'google_drive':
            return self._refresh_google_token(creds)
        elif service_name == 'dropbox':
            # Dropbox tokens ne expirent généralement pas
            return True
        
        return False
    
    def _refresh_google_token(self, creds: Dict) -> bool:
        """Rafraîchir le token Google"""
        try:
            if 'refresh_token' not in creds:
                print("Refresh token Google non disponible")
                return False
            
            service_config = cloud_config.get_service('google_drive')
            if not service_config:
                return False
            
            # Préparer la requête de rafraîchissement
            data = {
                'client_id': service_config.client_id,
                'client_secret': service_config.client_secret,
                'refresh_token': creds['refresh_token'],
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(service_config.token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Mettre à jour les credentials
                creds.update({
                    'access_token': token_data['access_token'],
                    'expires_at': time.time() + token_data.get('expires_in', 3600)
                })
                
                return self.save_credentials('google_drive', creds)
            else:
                print(f"Erreur lors du rafraîchissement Google: {response.text}")
                return False
                
        except Exception as e:
            print(f"Erreur lors du rafraîchissement Google: {e}")
            return False
    
    def revoke_access(self, service_name: str) -> bool:
        """Révoquer l'accès à un service cloud"""
        try:
            # Supprimer les credentials du keyring
            keyring.delete_password(self.service_name, f"{service_name}_credentials")
            
            # Supprimer de la cache locale
            if service_name in self.credentials:
                del self.credentials[service_name]
            
            print(f"Accès révoqué pour {service_name}")
            return True
        except Exception as e:
            print(f"Erreur lors de la révocation pour {service_name}: {e}")
            return False
    
    def get_authenticated_client(self, service_name: str):
        """Obtenir un client authentifié pour un service"""
        if not self.is_authenticated(service_name):
            return None
        
        creds = self.get_credentials(service_name)
        
        try:
            if service_name == 'google_drive':
                # Créer les credentials Google
                credentials = Credentials(
                    token=creds['access_token'],
                    refresh_token=creds.get('refresh_token'),
                    id_token=creds.get('id_token'),
                    token_uri='https://accounts.google.com/o/oauth2/token',
                    client_id=cloud_config.get_service('google_drive').client_id,
                    client_secret=cloud_config.get_service('google_drive').client_secret,
                    scopes=creds.get('scopes', [])
                )
                
                return build('drive', 'v3', credentials=credentials)
                
            elif service_name == 'dropbox':
                return dropbox.Dropbox(creds['access_token'])
                
        except Exception as e:
            print(f"Erreur lors de la création du client {service_name}: {e}")
            return None
        
        return None

# Instance globale d'authentification
cloud_auth = CloudAuthenticator()