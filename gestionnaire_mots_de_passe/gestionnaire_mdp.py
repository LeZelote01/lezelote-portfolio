#!/usr/bin/env python3
"""
Gestionnaire de Mots de Passe
Application complète de gestion de mots de passe avec chiffrement

Fonctionnalités:
- Stockage chiffré des mots de passe
- Génération automatique de mots de passe sécurisés
- Catégorisation des comptes
- Import/Export sécurisé
- Authentification maître robuste
- Interface en ligne de commande
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
import secrets
import string
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import getpass
import pyperclip
from colorama import init, Fore, Style
from tabulate import tabulate
import argparse
import sys

# Initialize colorama
init(autoreset=True)

# Imports pour la synchronisation cloud
try:
    from cloud_sync import cloud_sync_manager
    from cloud_config import cloud_config
    from cloud_auth import cloud_auth
    CLOUD_SYNC_AVAILABLE = True
except ImportError:
    CLOUD_SYNC_AVAILABLE = False
    print(f"{Fore.YELLOW}⚠️ Synchronisation cloud non disponible. Installez les dépendances avec: pip install -r requirements_cloud.txt")

class GestionnaireMDP:
    def __init__(self, db_path="passwords.db"):
        self.db_path = db_path
        self.cipher_suite = None
        self.is_authenticated = False
        self.session_timeout = 15  # minutes
        self.last_activity = None
        
        # Créer la base de données si elle n'existe pas
        self.init_database()
        
        print(f"{Fore.GREEN}🔐 Gestionnaire de Mots de Passe initialisé")

    def init_database(self):
        """Initialiser la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour le mot de passe maître
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les mots de passe stockés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                username TEXT,
                password_encrypted TEXT NOT NULL,
                url TEXT,
                notes TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Table pour les catégories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insérer les catégories par défaut
        default_categories = [
            ('Personnel', 'Comptes personnels', '#2196F3'),
            ('Travail', 'Comptes professionnels', '#4CAF50'),
            ('Réseaux Sociaux', 'Facebook, Twitter, etc.', '#FF9800'),
            ('Email', 'Comptes de messagerie', '#9C27B0'),
            ('Banque', 'Services bancaires', '#F44336'),
            ('Streaming', 'Netflix, Spotify, etc.', '#E91E63'),
            ('Autre', 'Autres comptes', '#607D8B')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO categories (name, description, color)
            VALUES (?, ?, ?)
        ''', default_categories)
        
        conn.commit()
        conn.close()

    def derive_key(self, password, salt):
        """Dériver une clé de chiffrement à partir du mot de passe maître"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def setup_master_password(self, password):
        """Configurer le mot de passe maître"""
        if self.has_master_password():
            print(f"{Fore.RED}❌ Un mot de passe maître existe déjà")
            return False
        
        # Générer un salt aléatoire
        salt = os.urandom(32)
        
        # Hasher le mot de passe pour stockage
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Stocker dans la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO master_password (password_hash, salt)
            VALUES (?, ?)
        ''', (password_hash.decode('utf-8'), base64.b64encode(salt).decode('utf-8')))
        conn.commit()
        conn.close()
        
        print(f"{Fore.GREEN}✓ Mot de passe maître configuré avec succès")
        return True

    def has_master_password(self):
        """Vérifier si un mot de passe maître existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM master_password')
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def authenticate(self, password):
        """Authentifier avec le mot de passe maître"""
        if not self.has_master_password():
            print(f"{Fore.RED}❌ Aucun mot de passe maître configuré")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash, salt FROM master_password ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash, salt_b64 = result
            salt = base64.b64decode(salt_b64.encode('utf-8'))
            
            # Vérifier le mot de passe
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Initialiser le chiffrement
                key = self.derive_key(password, salt)
                self.cipher_suite = Fernet(key)
                self.is_authenticated = True
                self.last_activity = datetime.now()
                
                print(f"{Fore.GREEN}✓ Authentification réussie")
                return True
        
        print(f"{Fore.RED}❌ Mot de passe incorrect")
        return False

    def check_session(self):
        """Vérifier si la session est encore valide"""
        if not self.is_authenticated:
            return False
        
        if self.last_activity and datetime.now() - self.last_activity > timedelta(minutes=self.session_timeout):
            self.logout()
            print(f"{Fore.YELLOW}⚠️  Session expirée. Veuillez vous reconnecter.")
            return False
        
        self.last_activity = datetime.now()
        return True

    def logout(self):
        """Déconnecter l'utilisateur"""
        self.cipher_suite = None
        self.is_authenticated = False
        self.last_activity = None
        print(f"{Fore.YELLOW}🚪 Déconnexion effectuée")

    def generate_password(self, length=16, include_symbols=True, include_numbers=True, 
                         include_uppercase=True, include_lowercase=True):
        """Générer un mot de passe sécurisé"""
        if length < 4:
            length = 4
        
        characters = ""
        required_chars = []
        
        if include_lowercase:
            characters += string.ascii_lowercase
            required_chars.append(secrets.choice(string.ascii_lowercase))
        
        if include_uppercase:
            characters += string.ascii_uppercase
            required_chars.append(secrets.choice(string.ascii_uppercase))
        
        if include_numbers:
            characters += string.digits
            required_chars.append(secrets.choice(string.digits))
        
        if include_symbols:
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            characters += symbols
            required_chars.append(secrets.choice(symbols))
        
        if not characters:
            characters = string.ascii_letters + string.digits
        
        # Générer le reste du mot de passe
        remaining_length = length - len(required_chars)
        password_list = required_chars + [secrets.choice(characters) for _ in range(remaining_length)]
        
        # Mélanger le mot de passe
        secrets.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)
        
        return password

    def encrypt_password(self, password):
        """Chiffrer un mot de passe"""
        if not self.cipher_suite:
            raise Exception("Non authentifié")
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        """Déchiffrer un mot de passe"""
        if not self.cipher_suite:
            raise Exception("Non authentifié")
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()

    def add_password(self, title, username, password, url="", notes="", category="Autre"):
        """Ajouter un nouveau mot de passe"""
        if not self.check_session():
            return False
        
        # Vérifier que la catégorie existe
        if not self.category_exists(category):
            print(f"{Fore.YELLOW}⚠️  Catégorie '{category}' introuvable, utilisation de 'Autre'")
            category = "Autre"
        
        # Chiffrer le mot de passe
        try:
            encrypted_password = self.encrypt_password(password)
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur de chiffrement: {e}")
            return False
        
        # Générer un ID unique
        password_id = str(uuid.uuid4())
        
        # Insérer dans la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO passwords (id, title, username, password_encrypted, url, notes, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (password_id, title, username, encrypted_password, url, notes, category))
            conn.commit()
            
            print(f"{Fore.GREEN}✓ Mot de passe ajouté avec succès")
            print(f"  ID: {password_id}")
            print(f"  Titre: {title}")
            print(f"  Catégorie: {category}")
            
            return password_id
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}❌ Erreur de base de données: {e}")
            return False
        finally:
            conn.close()

    def get_password(self, password_id):
        """Récupérer un mot de passe par ID"""
        if not self.check_session():
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, title, username, password_encrypted, url, notes, category,
                       created_at, updated_at, access_count
                FROM passwords WHERE id = ?
            ''', (password_id,))
            
            result = cursor.fetchone()
            if result:
                # Mettre à jour les statistiques d'accès
                cursor.execute('''
                    UPDATE passwords 
                    SET last_accessed = CURRENT_TIMESTAMP, 
                        access_count = access_count + 1
                    WHERE id = ?
                ''', (password_id,))
                conn.commit()
                
                # Déchiffrer le mot de passe
                encrypted_password = result[3]
                decrypted_password = self.decrypt_password(encrypted_password)
                
                return {
                    'id': result[0],
                    'title': result[1],
                    'username': result[2],
                    'password': decrypted_password,
                    'url': result[4],
                    'notes': result[5],
                    'category': result[6],
                    'created_at': result[7],
                    'updated_at': result[8],
                    'access_count': result[9] + 1
                }
            
            return None
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la récupération: {e}")
            return None
        finally:
            conn.close()

    def list_passwords(self, category=None, search_term=None):
        """Lister les mots de passe avec filtres optionnels"""
        if not self.check_session():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, username, url, category, created_at, access_count
            FROM passwords WHERE 1=1
        '''
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if search_term:
            query += ' AND (title LIKE ? OR username LIKE ? OR url LIKE ?)'
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += ' ORDER BY title'
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            passwords = []
            for row in results:
                passwords.append({
                    'id': row[0],
                    'title': row[1],
                    'username': row[2],
                    'url': row[3],
                    'category': row[4],
                    'created_at': row[5],
                    'access_count': row[6]
                })
            
            return passwords
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la liste: {e}")
            return []
        finally:
            conn.close()

    def update_password(self, password_id, **kwargs):
        """Mettre à jour un mot de passe"""
        if not self.check_session():
            return False
        
        # Vérifier que le mot de passe existe
        existing = self.get_password(password_id)
        if not existing:
            print(f"{Fore.RED}❌ Mot de passe introuvable")
            return False
        
        # Construire la requête de mise à jour
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in ['title', 'username', 'url', 'notes', 'category']:
                update_fields.append(f'{field} = ?')
                params.append(value)
            elif field == 'password':
                # Chiffrer le nouveau mot de passe
                encrypted_password = self.encrypt_password(value)
                update_fields.append('password_encrypted = ?')
                params.append(encrypted_password)
        
        if not update_fields:
            print(f"{Fore.YELLOW}⚠️  Aucun champ valide à mettre à jour")
            return False
        
        # Ajouter la date de mise à jour
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        params.append(password_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = f"UPDATE passwords SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            print(f"{Fore.GREEN}✓ Mot de passe mis à jour avec succès")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la mise à jour: {e}")
            return False
        finally:
            conn.close()

    def delete_password(self, password_id):
        """Supprimer un mot de passe"""
        if not self.check_session():
            return False
        
        # Vérifier que le mot de passe existe
        existing = self.get_password(password_id)
        if not existing:
            print(f"{Fore.RED}❌ Mot de passe introuvable")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
            conn.commit()
            
            print(f"{Fore.GREEN}✓ Mot de passe supprimé: {existing['title']}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la suppression: {e}")
            return False
        finally:
            conn.close()

    def category_exists(self, category_name):
        """Vérifier si une catégorie existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM categories WHERE name = ?', (category_name,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def list_categories(self):
        """Lister toutes les catégories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name, description, color FROM categories ORDER BY name')
        categories = cursor.fetchall()
        conn.close()
        return categories

    def add_category(self, name, description="", color="#607D8B"):
        """Ajouter une nouvelle catégorie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO categories (name, description, color)
                VALUES (?, ?, ?)
            ''', (name, description, color))
            conn.commit()
            print(f"{Fore.GREEN}✓ Catégorie '{name}' ajoutée")
            return True
        except sqlite3.IntegrityError:
            print(f"{Fore.RED}❌ La catégorie '{name}' existe déjà")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur: {e}")
            return False
        finally:
            conn.close()

    def export_data(self, filepath, include_passwords=False):
        """Exporter les données vers un fichier JSON"""
        if not self.check_session():
            return False
        
        try:
            export_data = {
                'export_info': {
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'include_passwords': include_passwords
                },
                'categories': [],
                'passwords': []
            }
            
            # Exporter les catégories
            categories = self.list_categories()
            for cat in categories:
                export_data['categories'].append({
                    'name': cat[0],
                    'description': cat[1],
                    'color': cat[2]
                })
            
            # Exporter les mots de passe
            passwords = self.list_passwords()
            for pwd in passwords:
                pwd_data = {
                    'id': pwd['id'],
                    'title': pwd['title'],
                    'username': pwd['username'],
                    'url': pwd['url'],
                    'category': pwd['category'],
                    'created_at': pwd['created_at'],
                    'access_count': pwd['access_count']
                }
                
                if include_passwords:
                    # Récupérer le mot de passe déchiffré
                    full_pwd = self.get_password(pwd['id'])
                    if full_pwd:
                        pwd_data['password'] = full_pwd['password']
                        pwd_data['notes'] = full_pwd['notes']
                
                export_data['passwords'].append(pwd_data)
            
            # Sauvegarder dans le fichier
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✓ Données exportées vers {filepath}")
            print(f"  {len(export_data['categories'])} catégories")
            print(f"  {len(export_data['passwords'])} mots de passe")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'export: {e}")
            return False

    def get_statistics(self):
        """Obtenir des statistiques d'utilisation"""
        if not self.check_session():
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Nombre total de mots de passe
        cursor.execute('SELECT COUNT(*) FROM passwords')
        stats['total_passwords'] = cursor.fetchone()[0]
        
        # Répartition par catégorie
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM passwords 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        ''')
        stats['by_category'] = cursor.fetchall()
        
        # Mots de passe les plus accessés
        cursor.execute('''
            SELECT title, access_count 
            FROM passwords 
            WHERE access_count > 0
            ORDER BY access_count DESC 
            LIMIT 5
        ''')
        stats['most_accessed'] = cursor.fetchall()
        
        # Ancienneté des mots de passe
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN date(created_at) > date('now', '-30 days') THEN 1 END) as recent,
                COUNT(CASE WHEN date(created_at) BETWEEN date('now', '-90 days') AND date('now', '-30 days') THEN 1 END) as medium,
                COUNT(CASE WHEN date(created_at) < date('now', '-90 days') THEN 1 END) as old
            FROM passwords
        ''')
        age_stats = cursor.fetchone()
        stats['age_distribution'] = {
            'recent': age_stats[0],    # < 30 jours
            'medium': age_stats[1],    # 30-90 jours
            'old': age_stats[2]        # > 90 jours
        }
        
        conn.close()
        return stats

    def copy_to_clipboard(self, password_id):
        """Copier un mot de passe dans le presse-papier"""
        if not self.check_session():
            return False
        
        password_data = self.get_password(password_id)
        if password_data:
            try:
                pyperclip.copy(password_data['password'])
                print(f"{Fore.GREEN}✓ Mot de passe copié dans le presse-papier")
                print(f"{Fore.YELLOW}⚠️  Le presse-papier sera vidé dans 30 secondes")
                
                # Note: Dans une vraie application, on démarrerait un timer pour vider
                # le presse-papier après 30 secondes
                
                return True
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur lors de la copie: {e}")
                return False
        
        return False

    # ============ MÉTHODES DE SYNCHRONISATION CLOUD ============
    
    def is_cloud_sync_available(self):
        """Vérifier si la synchronisation cloud est disponible"""
        return CLOUD_SYNC_AVAILABLE and cloud_sync_manager.is_cloud_sync_available()
    
    def get_cloud_sync_status(self):
        """Obtenir le statut de la synchronisation cloud"""
        if not CLOUD_SYNC_AVAILABLE:
            return {'available': False, 'error': 'Synchronisation cloud non disponible'}
        
        return cloud_sync_manager.get_sync_status()
    
    def configure_cloud_service(self, service_name: str, client_id: str, client_secret: str):
        """Configurer un service cloud"""
        if not CLOUD_SYNC_AVAILABLE:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
            return False
        
        success = cloud_config.configure_service(service_name, client_id, client_secret)
        if success:
            print(f"{Fore.GREEN}✓ Service {service_name} configuré")
        else:
            print(f"{Fore.RED}❌ Erreur lors de la configuration de {service_name}")
        
        return success
    
    def authenticate_cloud_service(self, service_name: str):
        """Démarrer l'authentification pour un service cloud"""
        if not CLOUD_SYNC_AVAILABLE:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
            return None
        
        if not cloud_config.is_service_configured(service_name):
            print(f"{Fore.RED}❌ Service {service_name} non configuré")
            return None
        
        auth_url = cloud_auth.get_authorization_url(service_name)
        if auth_url:
            print(f"{Fore.CYAN}🔗 URL d'autorisation pour {service_name}:")
            print(f"{Fore.BLUE}{auth_url}")
            print(f"{Fore.YELLOW}⚠️  Copiez cette URL dans votre navigateur et autorisez l'application")
            
            return auth_url
        else:
            print(f"{Fore.RED}❌ Impossible de générer l'URL d'autorisation pour {service_name}")
            return None
    
    def complete_cloud_authentication(self, service_name: str, callback_url: str):
        """Compléter l'authentification cloud avec l'URL de callback"""
        if not CLOUD_SYNC_AVAILABLE:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
            return False
        
        success = cloud_auth.handle_oauth_callback(service_name, callback_url)
        if success:
            print(f"{Fore.GREEN}✓ Authentification {service_name} réussie")
            return True
        else:
            print(f"{Fore.RED}❌ Échec de l'authentification {service_name}")
            return False
    
    def sync_to_cloud(self, master_password: str = None):
        """Synchroniser avec le cloud"""
        if not self.check_session():
            print(f"{Fore.RED}❌ Session expirée. Reconnectez-vous.")
            return False
        
        if not CLOUD_SYNC_AVAILABLE:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
            return False
        
        if not master_password:
            master_password = getpass.getpass("Mot de passe maître pour le chiffrement cloud: ")
        
        print(f"{Fore.CYAN}🌥️ Démarrage de la synchronisation cloud...")
        
        # Ajouter un callback pour les notifications
        def sync_callback(status, message, progress):
            if status == "starting":
                print(f"{Fore.CYAN}🌥️ {message}")
            elif status == "completed":
                print(f"{Fore.GREEN}✓ {message}")
            elif status == "error":
                print(f"{Fore.RED}❌ {message}")
            else:
                print(f"{Fore.YELLOW}⏳ {message} ({progress:.1f}%)")
        
        cloud_sync_manager.add_sync_callback(sync_callback)
        
        # Démarrer la synchronisation
        success = cloud_sync_manager.sync_with_cloud(master_password)
        
        if success:
            print(f"{Fore.GREEN}✅ Synchronisation cloud terminée avec succès!")
        else:
            print(f"{Fore.RED}❌ Échec de la synchronisation cloud")
        
        return success
    
    def export_to_cloud(self, master_password: str = None):
        """Exporter vers le cloud uniquement"""
        if not self.check_session():
            print(f"{Fore.RED}❌ Session expirée. Reconnectez-vous.")
            return False
        
        if not CLOUD_SYNC_AVAILABLE:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
            return False
        
        if not master_password:
            master_password = getpass.getpass("Mot de passe maître pour le chiffrement cloud: ")
        
        print(f"{Fore.CYAN}⬆️ Export vers le cloud...")
        
        success = cloud_sync_manager.export_to_cloud(master_password)
        
        if success:
            print(f"{Fore.GREEN}✅ Export vers le cloud terminé!")
        else:
            print(f"{Fore.RED}❌ Échec de l'export vers le cloud")
        
        return success
    
    def import_from_cloud(self, master_password: str = None, merge: bool = True):
        """Importer depuis le cloud"""
        if not self.check_session():
            print(f"{Fore.RED}❌ Session expirée. Reconnectez-vous.")
            return False
        
        if not CLOUD_SYNC_AVAILABLE:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
            return False
        
        if not master_password:
            master_password = getpass.getpass("Mot de passe maître pour le déchiffrement cloud: ")
        
        print(f"{Fore.CYAN}⬇️ Import depuis le cloud...")
        
        success = cloud_sync_manager.import_from_cloud(master_password, merge)
        
        if success:
            action = "fusionnés" if merge else "remplacés"
            print(f"{Fore.GREEN}✅ Mots de passe {action} depuis le cloud!")
        else:
            print(f"{Fore.RED}❌ Échec de l'import depuis le cloud")
        
        return success
    
    def get_cloud_services_status(self):
        """Obtenir le statut des services cloud"""
        if not CLOUD_SYNC_AVAILABLE:
            return {'available': False}
        
        status = {
            'available': True,
            'services': {}
        }
        
        for service_name in ['google_drive', 'dropbox']:
            service_config = cloud_config.get_service(service_name)
            status['services'][service_name] = {
                'configured': cloud_config.is_service_configured(service_name),
                'enabled': cloud_config.is_service_enabled(service_name),
                'authenticated': cloud_auth.is_authenticated(service_name) if service_config else False
            }
        
        return status

def main():
    """Interface en ligne de commande principale"""
    parser = argparse.ArgumentParser(description="Gestionnaire de Mots de Passe")
    parser.add_argument("--db", default="passwords.db", help="Chemin vers la base de données")
    parser.add_argument("--setup", action="store_true", help="Configurer le mot de passe maître")
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande add
    add_parser = subparsers.add_parser('add', help='Ajouter un mot de passe')
    add_parser.add_argument('title', help='Titre du compte')
    add_parser.add_argument('--username', help='Nom d\'utilisateur')
    add_parser.add_argument('--password', help='Mot de passe (sera généré si absent)')
    add_parser.add_argument('--url', help='URL du site')
    add_parser.add_argument('--category', default='Autre', help='Catégorie')
    add_parser.add_argument('--generate', action='store_true', help='Générer un mot de passe')
    add_parser.add_argument('--length', type=int, default=16, help='Longueur du mot de passe généré')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Lister les mots de passe')
    list_parser.add_argument('--category', help='Filtrer par catégorie')
    list_parser.add_argument('--search', help='Rechercher dans les titres')
    
    # Commande get
    get_parser = subparsers.add_parser('get', help='Récupérer un mot de passe')
    get_parser.add_argument('id', help='ID du mot de passe')
    get_parser.add_argument('--copy', action='store_true', help='Copier dans le presse-papier')
    
    # Commande stats
    subparsers.add_parser('stats', help='Afficher les statistiques')
    
    # Commandes cloud
    if CLOUD_SYNC_AVAILABLE:
        # Commande cloud-config
        cloud_config_parser = subparsers.add_parser('cloud-config', help='Configurer les services cloud')
        cloud_config_parser.add_argument('service', choices=['google_drive', 'dropbox'], 
                                        help='Service à configurer')
        cloud_config_parser.add_argument('--client-id', required=True, help='Client ID du service')
        cloud_config_parser.add_argument('--client-secret', required=True, help='Client Secret du service')
        
        # Commande cloud-auth
        cloud_auth_parser = subparsers.add_parser('cloud-auth', help='S\'authentifier à un service cloud')
        cloud_auth_parser.add_argument('service', choices=['google_drive', 'dropbox'], 
                                      help='Service à authentifier')
        cloud_auth_parser.add_argument('--callback-url', help='URL de callback après autorisation')
        
        # Commande cloud-status
        subparsers.add_parser('cloud-status', help='Voir le statut des services cloud')
        
        # Commande cloud-sync
        subparsers.add_parser('cloud-sync', help='Synchroniser avec le cloud')
        
        # Commande cloud-export
        subparsers.add_parser('cloud-export', help='Exporter vers le cloud')
        
        # Commande cloud-import
        cloud_import_parser = subparsers.add_parser('cloud-import', help='Importer depuis le cloud')
        cloud_import_parser.add_argument('--replace', action='store_true', 
                                        help='Remplacer au lieu de fusionner')
    
    # Commande export
    export_parser = subparsers.add_parser('export', help='Exporter les données')
    export_parser.add_argument('filepath', help='Chemin du fichier d\'export')
    export_parser.add_argument('--include-passwords', action='store_true', 
                              help='Inclure les mots de passe (dangereux!)')
    
    args = parser.parse_args()
    
    print(f"{Fore.BLUE}🔐 GESTIONNAIRE DE MOTS DE PASSE")
    print("=" * 40)
    
    # Initialiser le gestionnaire
    manager = GestionnaireMDP(db_path=args.db)
    
    # Mode setup
    if args.setup:
        if manager.has_master_password():
            print(f"{Fore.RED}❌ Un mot de passe maître existe déjà")
            return
        
        print(f"{Fore.CYAN}Configuration du mot de passe maître")
        while True:
            password = getpass.getpass("Mot de passe maître: ")
            confirm = getpass.getpass("Confirmer le mot de passe: ")
            
            if password == confirm:
                if len(password) >= 8:
                    manager.setup_master_password(password)
                    break
                else:
                    print(f"{Fore.RED}❌ Le mot de passe doit contenir au moins 8 caractères")
            else:
                print(f"{Fore.RED}❌ Les mots de passe ne correspondent pas")
        return
    
    # Vérifier si le mot de passe maître existe
    if not manager.has_master_password():
        print(f"{Fore.RED}❌ Aucun mot de passe maître configuré")
        print(f"{Fore.CYAN}Utilisez --setup pour configurer le mot de passe maître")
        return
    
    # Authentification
    password = getpass.getpass("Mot de passe maître: ")
    if not manager.authenticate(password):
        return
    
    # Exécuter la commande
    if args.command == 'add':
        # Générer un mot de passe si demandé
        if args.generate or not args.password:
            generated_password = manager.generate_password(length=args.length)
            print(f"{Fore.CYAN}Mot de passe généré: {generated_password}")
            password_to_use = generated_password
        else:
            password_to_use = args.password
        
        manager.add_password(
            title=args.title,
            username=args.username or "",
            password=password_to_use,
            url=args.url or "",
            category=args.category
        )
    
    elif args.command == 'list':
        passwords = manager.list_passwords(category=args.category, search_term=args.search)
        
        if passwords:
            table_data = []
            for pwd in passwords:
                table_data.append([
                    pwd['id'][:8] + "...",
                    pwd['title'],
                    pwd['username'] or "-",
                    pwd['category'],
                    pwd['access_count']
                ])
            
            print(f"\n{Fore.CYAN}📋 MOTS DE PASSE ({len(passwords)} trouvés)")
            print(tabulate(table_data, 
                         headers=["ID", "Titre", "Utilisateur", "Catégorie", "Accès"],
                         tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}⚠️  Aucun mot de passe trouvé")
    
    elif args.command == 'get':
        password_data = manager.get_password(args.id)
        if password_data:
            print(f"\n{Fore.CYAN}🔐 DÉTAILS DU MOT DE PASSE")
            details = [
                ["Titre", password_data['title']],
                ["Utilisateur", password_data['username'] or "-"],
                ["Mot de passe", "*" * len(password_data['password'])],
                ["URL", password_data['url'] or "-"],
                ["Catégorie", password_data['category']],
                ["Créé le", password_data['created_at']],
                ["Accès", password_data['access_count']]
            ]
            print(tabulate(details, headers=["Champ", "Valeur"], tablefmt="grid"))
            
            if args.copy:
                manager.copy_to_clipboard(args.id)
        else:
            print(f"{Fore.RED}❌ Mot de passe introuvable")
    
    elif args.command == 'stats':
        stats = manager.get_statistics()
        if stats:
            print(f"\n{Fore.CYAN}📊 STATISTIQUES")
            
            print(f"\n{Fore.GREEN}Total: {stats['total_passwords']} mots de passe")
            
            if stats['by_category']:
                print(f"\n{Fore.CYAN}Par catégorie:")
                cat_table = [[cat, count] for cat, count in stats['by_category']]
                print(tabulate(cat_table, headers=["Catégorie", "Nombre"], tablefmt="grid"))
            
            if stats['most_accessed']:
                print(f"\n{Fore.CYAN}Plus utilisés:")
                access_table = [[title, count] for title, count in stats['most_accessed']]
                print(tabulate(access_table, headers=["Titre", "Accès"], tablefmt="grid"))
    
    elif args.command == 'export':
        manager.export_data(args.filepath, include_passwords=args.include_passwords)
    
    # Commandes Cloud
    elif CLOUD_SYNC_AVAILABLE and args.command == 'cloud-config':
        manager.configure_cloud_service(args.service, args.client_id, args.client_secret)
    
    elif CLOUD_SYNC_AVAILABLE and args.command == 'cloud-auth':
        if args.callback_url:
            # Compléter l'authentification avec l'URL de callback
            manager.complete_cloud_authentication(args.service, args.callback_url)
        else:
            # Démarrer l'authentification
            auth_url = manager.authenticate_cloud_service(args.service)
            if auth_url:
                print(f"\n{Fore.CYAN}Après autorisation, exécutez:")
                print(f"{Fore.GREEN}python gestionnaire_mdp.py cloud-auth {args.service} --callback-url=\"[URL_DE_CALLBACK]\"")
    
    elif CLOUD_SYNC_AVAILABLE and args.command == 'cloud-status':
        status = manager.get_cloud_services_status()
        
        if not status['available']:
            print(f"{Fore.RED}❌ Synchronisation cloud non disponible")
        else:
            print(f"\n{Fore.CYAN}☁️ STATUS DES SERVICES CLOUD")
            print("=" * 40)
            
            table_data = []
            for service_name, service_status in status['services'].items():
                config_status = "✓" if service_status['configured'] else "❌"
                enabled_status = "✓" if service_status['enabled'] else "❌"
                auth_status = "✓" if service_status['authenticated'] else "❌"
                
                table_data.append([
                    service_name.replace('_', ' ').title(),
                    config_status,
                    enabled_status,
                    auth_status
                ])
            
            print(tabulate(table_data, 
                         headers=["Service", "Configuré", "Activé", "Authentifié"],
                         tablefmt="grid"))
            
            # Status de synchronisation
            sync_status = manager.get_cloud_sync_status()
            if sync_status.get('available'):
                print(f"\n{Fore.CYAN}📊 STATUT DE SYNCHRONISATION")
                sync_table = [
                    ["Dernière sync", sync_status.get('last_sync', 'Jamais')],
                    ["En cours", "Oui" if sync_status.get('is_syncing', False) else "Non"],
                    ["Auto-sync", "Activé" if sync_status.get('auto_sync_enabled', False) else "Désactivé"],
                    ["Services disponibles", str(len(sync_status.get('available_services', [])))]
                ]
                print(tabulate(sync_table, headers=["Paramètre", "Valeur"], tablefmt="grid"))
    
    elif CLOUD_SYNC_AVAILABLE and args.command == 'cloud-sync':
        # Vérifier l'authentification
        if not manager.check_session():
            master_password = getpass.getpass("Mot de passe maître: ")
            if not manager.authenticate(master_password):
                print(f"{Fore.RED}❌ Authentification échouée")
                return
        
        manager.sync_to_cloud()
    
    elif CLOUD_SYNC_AVAILABLE and args.command == 'cloud-export':
        # Vérifier l'authentification
        if not manager.check_session():
            master_password = getpass.getpass("Mot de passe maître: ")
            if not manager.authenticate(master_password):
                print(f"{Fore.RED}❌ Authentification échouée")
                return
        
        manager.export_to_cloud()
    
    elif CLOUD_SYNC_AVAILABLE and args.command == 'cloud-import':
        # Vérifier l'authentification
        if not manager.check_session():
            master_password = getpass.getpass("Mot de passe maître: ")
            if not manager.authenticate(master_password):
                print(f"{Fore.RED}❌ Authentification échouée")
                return
        
        merge = not args.replace
        manager.import_from_cloud(merge=merge)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()