#!/usr/bin/env python3
"""
Native Host - Extension Gestionnaire de Mots de Passe
Communication native entre l'extension et l'application principale
"""

import sys
import json
import struct
import logging
import asyncio
import aiohttp
from pathlib import Path

# Configuration
NATIVE_HOST_CONFIG = {
    'api_base_url': 'http://localhost:8002/api',
    'log_file': '/tmp/gmp_native_host.log',
    'timeout': 30
}

# Configuration du logging
logging.basicConfig(
    filename=NATIVE_HOST_CONFIG['log_file'],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class NativeHost:
    """Gestionnaire de communication native"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=NATIVE_HOST_CONFIG['timeout'])
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def read_message(self):
        """Lire un message depuis l'extension"""
        try:
            # Lire la longueur du message (4 bytes)
            raw_length = sys.stdin.buffer.read(4)
            if len(raw_length) == 0:
                return None
                
            message_length = struct.unpack('=I', raw_length)[0]
            
            # Lire le message JSON
            raw_message = sys.stdin.buffer.read(message_length)
            message = json.loads(raw_message.decode('utf-8'))
            
            logger.info(f"Message reçu: {message.get('action', 'unknown')}")
            return message
            
        except Exception as e:
            logger.error(f"Erreur lecture message: {e}")
            return None
    
    def send_message(self, message):
        """Envoyer un message vers l'extension"""
        try:
            encoded_message = json.dumps(message).encode('utf-8')
            message_length = len(encoded_message)
            
            # Envoyer la longueur puis le message
            sys.stdout.buffer.write(struct.pack('=I', message_length))
            sys.stdout.buffer.write(encoded_message)
            sys.stdout.buffer.flush()
            
            logger.info(f"Message envoyé: {message.get('type', 'response')}")
            
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}")
    
    async def authenticate(self, master_password):
        """Authentifier avec l'API"""
        try:
            async with self.session.post(
                f"{NATIVE_HOST_CONFIG['api_base_url']}/auth/login",
                json={
                    'master_password': master_password,
                    'source': 'native_host'
                }
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get('access_token')
                    logger.info("Authentification réussie")
                    return {'success': True, 'token': self.auth_token}
                else:
                    error_text = await response.text()
                    logger.error(f"Échec authentification: {response.status} - {error_text}")
                    return {'success': False, 'error': 'Authentification échouée'}
                    
        except Exception as e:
            logger.error(f"Erreur authentification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_passwords(self, domain=None):
        """Récupérer les mots de passe"""
        if not self.auth_token:
            return {'success': False, 'error': 'Non authentifié'}
        
        try:
            url = f"{NATIVE_HOST_CONFIG['api_base_url']}/passwords"
            if domain:
                url += f"/search?domain={domain}"
            
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    passwords = await response.json()
                    logger.info(f"Récupération de {len(passwords)} mots de passe")
                    return {'success': True, 'passwords': passwords}
                else:
                    error_text = await response.text()
                    logger.error(f"Erreur récupération: {response.status} - {error_text}")
                    return {'success': False, 'error': 'Erreur de récupération'}
                    
        except Exception as e:
            logger.error(f"Erreur get_passwords: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_password(self, options=None):
        """Générer un mot de passe"""
        try:
            default_options = {
                'length': 16,
                'include_uppercase': True,
                'include_lowercase': True,
                'include_numbers': True,
                'include_symbols': True,
                'exclude_ambiguous': True
            }
            
            if options:
                default_options.update(options)
            
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            async with self.session.post(
                f"{NATIVE_HOST_CONFIG['api_base_url']}/generate/password",
                json=default_options,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info("Génération de mot de passe réussie")
                    return {'success': True, 'password': result}
                else:
                    error_text = await response.text()
                    logger.error(f"Erreur génération: {response.status} - {error_text}")
                    return {'success': False, 'error': 'Erreur de génération'}
                    
        except Exception as e:
            logger.error(f"Erreur generate_password: {e}")
            return {'success': False, 'error': str(e)}
    
    async def save_password(self, password_data):
        """Sauvegarder un mot de passe"""
        if not self.auth_token:
            return {'success': False, 'error': 'Non authentifié'}
        
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            async with self.session.post(
                f"{NATIVE_HOST_CONFIG['api_base_url']}/passwords",
                json=password_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Mot de passe sauvegardé: {result.get('id')}")
                    return {'success': True, 'id': result.get('id')}
                else:
                    error_text = await response.text()
                    logger.error(f"Erreur sauvegarde: {response.status} - {error_text}")
                    return {'success': False, 'error': 'Erreur de sauvegarde'}
                    
        except Exception as e:
            logger.error(f"Erreur save_password: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_health(self):
        """Vérifier la santé de l'API"""
        try:
            async with self.session.get(
                f"{NATIVE_HOST_CONFIG['api_base_url']}/health"
            ) as response:
                
                if response.status == 200:
                    return {'success': True, 'status': 'healthy'}
                else:
                    return {'success': False, 'status': 'unhealthy'}
                    
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {'success': False, 'error': str(e)}
    
    async def handle_message(self, message):
        """Traiter un message de l'extension"""
        action = message.get('action', 'unknown')
        data = message.get('data', {})
        
        try:
            if action == 'authenticate':
                result = await self.authenticate(data.get('master_password'))
                
            elif action == 'get_passwords':
                result = await self.get_passwords(data.get('domain'))
                
            elif action == 'generate_password':
                result = await self.generate_password(data.get('options'))
                
            elif action == 'save_password':
                result = await self.save_password(data)
                
            elif action == 'health_check':
                result = await self.check_health()
                
            elif action == 'logout':
                self.auth_token = None
                result = {'success': True, 'message': 'Déconnecté'}
                
            else:
                result = {'success': False, 'error': f'Action inconnue: {action}'}
            
            # Envoyer la réponse
            response = {
                'id': message.get('id'),
                'type': 'response',
                'action': action,
                'result': result
            }
            
            self.send_message(response)
            
        except Exception as e:
            logger.error(f"Erreur traitement message {action}: {e}")
            
            error_response = {
                'id': message.get('id'),
                'type': 'error',
                'action': action,
                'error': str(e)
            }
            
            self.send_message(error_response)
    
    async def run(self):
        """Boucle principale du native host"""
        logger.info("Démarrage du Native Host GMP")
        
        try:
            while True:
                message = self.read_message()
                
                if message is None:
                    logger.info("Fin de communication, arrêt du native host")
                    break
                
                await self.handle_message(message)
                
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
            
        except Exception as e:
            logger.error(f"Erreur fatale: {e}")
            
        finally:
            logger.info("Native Host GMP arrêté")

def install_native_host():
    """Installer le native host pour Chrome/Firefox"""
    import os
    import platform
    
    system = platform.system().lower()
    script_dir = Path(__file__).parent.absolute()
    
    # Manifeste pour Chrome
    chrome_manifest = {
        "name": "com.gestionnaire.mdp.native",
        "description": "Native Host pour Gestionnaire de Mots de Passe",
        "path": str(script_dir / "native_host.py"),
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://*/",
        ]
    }
    
    # Manifeste pour Firefox
    firefox_manifest = {
        "name": "com.gestionnaire.mdp.native",
        "description": "Native Host pour Gestionnaire de Mots de Passe",
        "path": str(script_dir / "native_host.py"),
        "type": "stdio",
        "allowed_extensions": [
            "gestionnaire-mdp@cybersec.local"
        ]
    }
    
    if system == "linux":
        # Chrome Linux
        chrome_dir = Path.home() / ".config/google-chrome/NativeMessagingHosts"
        chrome_dir.mkdir(parents=True, exist_ok=True)
        
        with open(chrome_dir / "com.gestionnaire.mdp.native.json", "w") as f:
            json.dump(chrome_manifest, f, indent=2)
        
        # Firefox Linux
        firefox_dir = Path.home() / ".mozilla/native-messaging-hosts"
        firefox_dir.mkdir(parents=True, exist_ok=True)
        
        with open(firefox_dir / "com.gestionnaire.mdp.native.json", "w") as f:
            json.dump(firefox_manifest, f, indent=2)
            
        print("✅ Native Host installé pour Linux (Chrome et Firefox)")
        
    elif system == "darwin":  # macOS
        # Chrome macOS
        chrome_dir = Path.home() / "Library/Application Support/Google/Chrome/NativeMessagingHosts"
        chrome_dir.mkdir(parents=True, exist_ok=True)
        
        with open(chrome_dir / "com.gestionnaire.mdp.native.json", "w") as f:
            json.dump(chrome_manifest, f, indent=2)
        
        # Firefox macOS
        firefox_dir = Path.home() / "Library/Application Support/Mozilla/NativeMessagingHosts"
        firefox_dir.mkdir(parents=True, exist_ok=True)
        
        with open(firefox_dir / "com.gestionnaire.mdp.native.json", "w") as f:
            json.dump(firefox_manifest, f, indent=2)
            
        print("✅ Native Host installé pour macOS (Chrome et Firefox)")
        
    elif system == "windows":
        # Windows Registry (nécessite des privilèges admin)
        import winreg
        
        try:
            # Chrome Windows
            chrome_key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Google\Chrome\NativeMessagingHosts\com.gestionnaire.mdp.native"
            )
            winreg.SetValueEx(chrome_key, "", 0, winreg.REG_SZ, 
                str(script_dir / "com.gestionnaire.mdp.native.json"))
            winreg.CloseKey(chrome_key)
            
            # Créer le fichier manifeste
            with open(script_dir / "com.gestionnaire.mdp.native.json", "w") as f:
                json.dump(chrome_manifest, f, indent=2)
            
            print("✅ Native Host installé pour Windows (Chrome)")
            
        except Exception as e:
            print(f"❌ Erreur installation Windows: {e}")
            print("Exécutez en tant qu'administrateur ou installez manuellement")
    
    else:
        print(f"❌ Système non supporté: {system}")

async def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_native_host()
        return
    
    # Démarrer le native host
    async with NativeHost() as host:
        await host.run()

if __name__ == "__main__":
    asyncio.run(main())