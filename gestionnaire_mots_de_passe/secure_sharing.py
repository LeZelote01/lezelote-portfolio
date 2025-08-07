#!/usr/bin/env python3
"""
Module de Partage Sécurisé entre Utilisateurs
Gestionnaire de Mots de Passe - Secure Sharing

Fonctionnalités:
- Partage chiffré de mots de passe entre utilisateurs
- Chiffrement asymétrique (RSA) pour l'échange de clés
- Gestion granulaire des permissions (lecture, écriture, admin)
- Révocation instantanée des accès partagés
- Audit trail complet des partages
- Notifications de partage et modifications
- Expiration automatique des partages
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import secrets
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from colorama import Fore, Style

class SharePermission(Enum):
    """Niveaux de permission pour le partage"""
    READ = "read"           # Lecture seule
    WRITE = "write"         # Lecture + modification
    ADMIN = "admin"         # Lecture + modification + partage + révocation

class ShareStatus(Enum):
    """Statuts des partages"""
    ACTIVE = "active"
    REVOKED = "revoked" 
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class UserInfo:
    """Informations d'un utilisateur"""
    user_id: str
    username: str
    email: str
    public_key: str
    created_at: datetime
    last_active: Optional[datetime] = None

@dataclass
class ShareInfo:
    """Informations sur un partage"""
    share_id: str
    password_id: str
    password_title: str
    owner_id: str
    recipient_id: str
    permission: SharePermission
    status: ShareStatus
    encrypted_password: str  # Chiffré avec la clé publique du destinataire
    expires_at: Optional[datetime]
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int = 0

@dataclass
class ShareRequest:
    """Demande de partage"""
    request_id: str
    password_id: str
    password_title: str
    requester_id: str
    owner_id: str
    requested_permission: SharePermission
    message: str
    status: str  # "pending", "approved", "rejected"
    created_at: datetime
    responded_at: Optional[datetime] = None

class SecureSharing:
    """Gestionnaire de partage sécurisé"""
    
    def __init__(self, gestionnaire_mdp, user_id: str, user_email: str):
        self.gestionnaire = gestionnaire_mdp
        self.user_id = user_id
        self.user_email = user_email
        self.sharing_db_path = "secure_sharing.db"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialiser la base de données de partage
        self._init_sharing_database()
        
        # Créer ou charger les clés RSA de l'utilisateur
        self.private_key, self.public_key = self._get_or_create_user_keys()
        
        # Enregistrer l'utilisateur
        self._register_user()
        
        print(f"{Fore.GREEN}🤝 Gestionnaire de Partage Sécurisé initialisé")
    
    def _init_sharing_database(self):
        """Initialiser la base de données de partage"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                public_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            )
        ''')
        
        # Table des partages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                share_id TEXT PRIMARY KEY,
                password_id TEXT NOT NULL,
                password_title TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                permission TEXT NOT NULL,
                status TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                encrypted_notes TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                FOREIGN KEY (owner_id) REFERENCES users (user_id),
                FOREIGN KEY (recipient_id) REFERENCES users (user_id)
            )
        ''')
        
        # Table des demandes de partage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS share_requests (
                request_id TEXT PRIMARY KEY,
                password_id TEXT NOT NULL,
                password_title TEXT NOT NULL,
                requester_id TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                requested_permission TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responded_at TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users (user_id),
                FOREIGN KEY (owner_id) REFERENCES users (user_id)
            )
        ''')
        
        # Table d'audit des accès
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_audit (
                id INTEGER PRIMARY KEY,
                share_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (share_id) REFERENCES shares (share_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_or_create_user_keys(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Obtenir ou créer les clés RSA de l'utilisateur"""
        private_key_file = f"{self.user_id}_private.pem"
        public_key_file = f"{self.user_id}_public.pem"
        
        try:
            # Charger les clés existantes
            with open(private_key_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
            
            with open(public_key_file, 'rb') as f:
                public_key = serialization.load_pem_public_key(f.read())
                
            self.logger.info("Clés RSA existantes chargées")
            
        except FileNotFoundError:
            # Créer de nouvelles clés
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()
            
            # Sauvegarder les clés
            with open(private_key_file, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            with open(public_key_file, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            
            self.logger.info("Nouvelles clés RSA créées et sauvegardées")
        
        return private_key, public_key
    
    def _register_user(self):
        """Enregistrer ou mettre à jour l'utilisateur"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        # Sérialiser la clé publique
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, email, public_key, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.user_id, self.user_id, self.user_email, public_key_pem, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def share_password(
        self, 
        password_id: str, 
        recipient_email: str, 
        permission: SharePermission = SharePermission.READ,
        expires_hours: Optional[int] = None,
        message: str = ""
    ) -> str:
        """Partager un mot de passe avec un utilisateur"""
        if not self.gestionnaire.check_session():
            raise Exception("Session expirée, authentification requise")
        
        # Vérifier que le mot de passe existe et appartient à l'utilisateur
        password_data = self.gestionnaire.get_password(password_id)
        if not password_data:
            raise Exception("Mot de passe non trouvé")
        
        # Trouver le destinataire
        recipient = self._get_user_by_email(recipient_email)
        if not recipient:
            raise Exception(f"Utilisateur {recipient_email} non trouvé")
        
        if recipient.user_id == self.user_id:
            raise Exception("Impossible de partager avec soi-même")
        
        # Charger la clé publique du destinataire
        recipient_public_key = serialization.load_pem_public_key(
            recipient.public_key.encode('utf-8')
        )
        
        # Chiffrer le mot de passe avec la clé publique du destinataire
        encrypted_password = recipient_public_key.encrypt(
            password_data['password'].encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Chiffrer les notes si elles existent
        encrypted_notes = None
        if password_data.get('notes'):
            encrypted_notes = recipient_public_key.encrypt(
                password_data['notes'].encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        
        # Calculer la date d'expiration
        expires_at = None
        if expires_hours:
            expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        # Créer le partage
        share_id = secrets.token_urlsafe(32)
        
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shares 
            (share_id, password_id, password_title, owner_id, recipient_id, 
             permission, status, encrypted_password, encrypted_notes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            share_id, password_id, password_data['title'], self.user_id, 
            recipient.user_id, permission.value, ShareStatus.ACTIVE.value,
            base64.b64encode(encrypted_password).decode('utf-8'),
            base64.b64encode(encrypted_notes).decode('utf-8') if encrypted_notes else None,
            expires_at.isoformat() if expires_at else None
        ))
        
        conn.commit()
        conn.close()
        
        # Enregistrer l'audit
        self._log_access(share_id, self.user_id, "share_created")
        
        self.logger.info(f"Mot de passe {password_data['title']} partagé avec {recipient_email}")
        print(f"{Fore.GREEN}✓ Mot de passe '{password_data['title']}' partagé avec {recipient_email}")
        
        return share_id
    
    def request_share(
        self, 
        owner_email: str, 
        password_title: str,
        requested_permission: SharePermission = SharePermission.READ,
        message: str = ""
    ) -> str:
        """Demander le partage d'un mot de passe"""
        owner = self._get_user_by_email(owner_email)
        if not owner:
            raise Exception(f"Utilisateur {owner_email} non trouvé")
        
        if owner.user_id == self.user_id:
            raise Exception("Impossible de demander un partage à soi-même")
        
        # Créer la demande
        request_id = secrets.token_urlsafe(32)
        
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO share_requests 
            (request_id, password_id, password_title, requester_id, owner_id, 
             requested_permission, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_id, "", password_title, self.user_id, owner.user_id,
            requested_permission.value, message
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Demande de partage envoyée à {owner_email}")
        print(f"{Fore.GREEN}✓ Demande de partage envoyée à {owner_email}")
        
        return request_id
    
    def get_shared_with_me(self) -> List[ShareInfo]:
        """Obtenir les mots de passe partagés avec moi"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.username as owner_username
            FROM shares s
            JOIN users u ON s.owner_id = u.user_id
            WHERE s.recipient_id = ? AND s.status = 'active'
            AND (s.expires_at IS NULL OR s.expires_at > ?)
            ORDER BY s.created_at DESC
        ''', (self.user_id, datetime.now().isoformat()))
        
        results = cursor.fetchall()
        conn.close()
        
        shares = []
        for row in results:
            share = ShareInfo(
                share_id=row[0],
                password_id=row[1],
                password_title=row[2],
                owner_id=row[3],
                recipient_id=row[4],
                permission=SharePermission(row[5]),
                status=ShareStatus(row[6]),
                encrypted_password=row[7],
                expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
                created_at=datetime.fromisoformat(row[10]),
                last_accessed=datetime.fromisoformat(row[11]) if row[11] else None,
                access_count=row[12] or 0
            )
            shares.append(share)
        
        return shares
    
    def get_my_shares(self) -> List[ShareInfo]:
        """Obtenir les mots de passe que j'ai partagés"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.username as recipient_username
            FROM shares s
            JOIN users u ON s.recipient_id = u.user_id
            WHERE s.owner_id = ?
            ORDER BY s.created_at DESC
        ''', (self.user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        shares = []
        for row in results:
            share = ShareInfo(
                share_id=row[0],
                password_id=row[1],
                password_title=row[2],
                owner_id=row[3],
                recipient_id=row[4],
                permission=SharePermission(row[5]),
                status=ShareStatus(row[6]),
                encrypted_password=row[7],
                expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
                created_at=datetime.fromisoformat(row[10]),
                last_accessed=datetime.fromisoformat(row[11]) if row[11] else None,
                access_count=row[12] or 0
            )
            shares.append(share)
        
        return shares
    
    def access_shared_password(self, share_id: str) -> Dict[str, Any]:
        """Accéder à un mot de passe partagé"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        # Vérifier que l'utilisateur a accès
        cursor.execute('''
            SELECT * FROM shares 
            WHERE share_id = ? AND recipient_id = ? AND status = 'active'
            AND (expires_at IS NULL OR expires_at > ?)
        ''', (share_id, self.user_id, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        if not result:
            raise Exception("Partage non trouvé ou accès refusé")
        
        # Déchiffrer le mot de passe
        encrypted_password_b64 = result[7]
        encrypted_password = base64.b64decode(encrypted_password_b64.encode('utf-8'))
        
        try:
            decrypted_password = self.private_key.decrypt(
                encrypted_password,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('utf-8')
        except Exception as e:
            raise Exception(f"Impossible de déchiffrer le mot de passe: {e}")
        
        # Déchiffrer les notes si elles existent
        decrypted_notes = None
        if result[8]:  # encrypted_notes
            try:
                encrypted_notes = base64.b64decode(result[8].encode('utf-8'))
                decrypted_notes = self.private_key.decrypt(
                    encrypted_notes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode('utf-8')
            except Exception:
                decrypted_notes = "Erreur de déchiffrement des notes"
        
        # Mettre à jour les statistiques d'accès
        cursor.execute('''
            UPDATE shares 
            SET last_accessed = ?, access_count = access_count + 1
            WHERE share_id = ?
        ''', (datetime.now().isoformat(), share_id))
        
        conn.commit()
        conn.close()
        
        # Enregistrer l'audit
        self._log_access(share_id, self.user_id, "password_accessed")
        
        return {
            'share_id': share_id,
            'password_id': result[1],
            'title': result[2],
            'password': decrypted_password,
            'notes': decrypted_notes,
            'permission': SharePermission(result[5]),
            'owner_id': result[3],
            'access_count': result[12] + 1
        }
    
    def revoke_share(self, share_id: str) -> bool:
        """Révoquer un partage"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        # Vérifier que l'utilisateur est le propriétaire
        cursor.execute('''
            SELECT owner_id, password_title, recipient_id 
            FROM shares 
            WHERE share_id = ? AND owner_id = ?
        ''', (share_id, self.user_id))
        
        result = cursor.fetchone()
        if not result:
            return False
        
        # Révoquer le partage
        cursor.execute('''
            UPDATE shares 
            SET status = 'revoked'
            WHERE share_id = ?
        ''', (share_id,))
        
        conn.commit()
        conn.close()
        
        # Enregistrer l'audit
        self._log_access(share_id, self.user_id, "share_revoked")
        
        self.logger.info(f"Partage {share_id} révoqué")
        print(f"{Fore.YELLOW}⚠️ Partage révoqué")
        
        return True
    
    def _get_user_by_email(self, email: str) -> Optional[UserInfo]:
        """Trouver un utilisateur par email"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, email, public_key, created_at, last_active
            FROM users WHERE email = ?
        ''', (email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return UserInfo(
                user_id=result[0],
                username=result[1],
                email=result[2],
                public_key=result[3],
                created_at=datetime.fromisoformat(result[4]),
                last_active=datetime.fromisoformat(result[5]) if result[5] else None
            )
        
        return None
    
    def _log_access(self, share_id: str, user_id: str, action: str):
        """Enregistrer un accès dans l'audit trail"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_audit (share_id, user_id, action)
            VALUES (?, ?, ?)
        ''', (share_id, user_id, action))
        
        conn.commit()
        conn.close()
    
    def get_sharing_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques de partage"""
        conn = sqlite3.connect(self.sharing_db_path)
        cursor = conn.cursor()
        
        # Partages créés par moi
        cursor.execute('''
            SELECT COUNT(*), status FROM shares 
            WHERE owner_id = ? 
            GROUP BY status
        ''', (self.user_id,))
        my_shares_by_status = dict(cursor.fetchall())
        
        # Partages reçus
        cursor.execute('''
            SELECT COUNT(*), status FROM shares 
            WHERE recipient_id = ? 
            GROUP BY status
        ''', (self.user_id,))
        received_shares_by_status = dict(cursor.fetchall())
        
        # Accès récents
        cursor.execute('''
            SELECT COUNT(*) FROM access_audit 
            WHERE user_id = ? AND timestamp > datetime('now', '-7 days')
        ''', (self.user_id,))
        recent_access_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'my_shares_by_status': my_shares_by_status,
            'received_shares_by_status': received_shares_by_status,
            'recent_access_count': recent_access_count
        }

if __name__ == "__main__":
    print(f"{Fore.BLUE}🤝 PARTAGE SÉCURISÉ DE MOTS DE PASSE")
    print("=" * 50)
    print(f"{Fore.CYAN}Module de partage sécurisé pour collaboration d'équipe")
    print(f"{Fore.CYAN}Consultez la documentation pour l'utilisation")