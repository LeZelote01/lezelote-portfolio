#!/usr/bin/env python3
"""
API REST pour le Gestionnaire de Mots de Passe
Intégration FastAPI avec la classe GestionnaireMDP existante
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import sys
import uuid
from pathlib import Path

# Ajouter le chemin du gestionnaire existant
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from gestionnaire_mdp import GestionnaireMDP

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "votre-cle-secrete-jwt-changez-ceci-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="API Gestionnaire de Mots de Passe",
    description="""
    API REST sécurisée pour la gestion de mots de passe avec chiffrement AES-256.
    
    ## Fonctionnalités
    * **Authentification JWT** - Sécurisation des accès
    * **Gestion des mots de passe** - CRUD complet
    * **Chiffrement AES-256** - Sécurité maximale
    * **Catégories** - Organisation des mots de passe
    """,
    version="1.0.0"
)

# Configuration CORS pour les extensions navigateur futures
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "chrome-extension://*",
        "moz-extension://*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Modèles Pydantic
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=1)
    url: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field("Autre", max_length=100)
    notes: Optional[str] = None
    
    @field_validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        return v

class PasswordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=1)
    url: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class PasswordResponse(BaseModel):
    id: str
    title: str
    username: Optional[str]
    url: Optional[str]
    category: str
    created_at: Optional[str]
    updated_at: Optional[str]
    access_count: int

class PasswordWithDecrypted(PasswordResponse):
    decrypted_password: str

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = "#607D8B"

class CategoryResponse(BaseModel):
    name: str
    description: Optional[str]
    color: str

# Fonctions utilitaires JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Gestionnaire singleton - simulation d'une session utilisateur
user_managers = {}

def get_password_manager(username: str = Depends(verify_token)) -> GestionnaireMDP:
    """Obtient une instance du gestionnaire pour l'utilisateur authentifié."""
    if username not in user_managers:
        manager = GestionnaireMDP()
        # Simuler l'authentification (en production, ceci viendrait d'une vraie DB)
        user_managers[username] = manager
    return user_managers[username]

# Endpoints d'authentification
@app.post("/api/auth/login", response_model=Token, tags=["Authentification"])
async def login(user_data: UserLogin):
    """
    Authentifie un utilisateur et retourne un token JWT.
    
    - **username**: Nom d'utilisateur (3-50 caractères)
    - **password**: Mot de passe maître (8+ caractères)
    """
    try:
        # Créer une instance temporaire pour vérifier l'authentification
        manager = GestionnaireMDP()
        
        # Vérifier si l'utilisateur a un mot de passe maître configuré
        if not manager.has_master_password():
            # Pour la démo, configurer automatiquement
            manager.setup_master_password(user_data.password)
        
        # Authentifier l'utilisateur
        if manager.authenticate(user_data.password):
            # Stocker le gestionnaire authentifié
            user_managers[user_data.username] = manager
            
            # Créer le token JWT
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user_data.username}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe incorrect"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'authentification: {str(e)}"
        )

@app.post("/api/auth/register", response_model=dict, tags=["Authentification"])
async def register(user_data: UserLogin):
    """
    Enregistre un nouvel utilisateur.
    
    - **username**: Nom d'utilisateur unique
    - **password**: Mot de passe maître sécurisé
    """
    try:
        manager = GestionnaireMDP()
        
        if manager.has_master_password():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur existe déjà pour cette base"
            )
        
        # Configurer le mot de passe maître
        if manager.setup_master_password(user_data.password):
            return {
                "message": "Utilisateur créé avec succès",
                "username": user_data.username
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de créer l'utilisateur"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

# Endpoints de gestion des mots de passe
@app.post("/api/passwords", response_model=PasswordResponse, tags=["Mots de passe"])
async def create_password(
    password_data: PasswordCreate,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Crée un nouveau mot de passe chiffré.
    
    - **title**: Nom du site ou service (obligatoire)
    - **username**: Nom d'utilisateur (optionnel)
    - **password**: Mot de passe à chiffrer (obligatoire, 8+ caractères)
    - **url**: URL du site (optionnel)
    - **category**: Catégorie (optionnel, défaut: "Autre")
    - **notes**: Notes additionnelles (optionnel)
    """
    try:
        password_id = manager.add_password(
            title=password_data.title,
            username=password_data.username or "",
            password=password_data.password,
            url=password_data.url or "",
            category=password_data.category or "Autre",
            notes=password_data.notes or ""
        )
        
        if password_id:
            # Récupérer les données complètes pour la réponse
            saved_password = manager.get_password(password_id)
            if saved_password:
                return PasswordResponse(
                    id=saved_password['id'],
                    title=saved_password['title'],
                    username=saved_password['username'],
                    url=saved_password['url'],
                    category=saved_password['category'],
                    created_at=saved_password['created_at'],
                    updated_at=saved_password.get('updated_at'),
                    access_count=saved_password['access_count']
                )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Impossible de créer le mot de passe"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création: {str(e)}"
        )

@app.get("/api/passwords", response_model=List[PasswordResponse], tags=["Mots de passe"])
async def get_passwords(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    search: Optional[str] = Query(None, description="Recherche dans les titres"),
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments"),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Récupère la liste des mots de passe avec filtrage et pagination.
    
    - **category**: Filtrer par catégorie spécifique
    - **search**: Recherche textuelle dans les titres
    - **skip**: Nombre d'éléments à ignorer (pagination)
    - **limit**: Nombre maximum d'éléments à retourner
    """
    try:
        passwords = manager.list_passwords(category=category, search_term=search)
        
        # Pagination manuelle
        total = len(passwords)
        paginated = passwords[skip:skip + limit]
        
        return [
            PasswordResponse(
                id=pwd['id'],
                title=pwd['title'],
                username=pwd['username'],
                url=pwd['url'],
                category=pwd['category'],
                created_at=pwd['created_at'],
                updated_at=pwd.get('updated_at'),
                access_count=pwd['access_count']
            )
            for pwd in paginated
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@app.get("/api/passwords/{password_id}", response_model=PasswordResponse, tags=["Mots de passe"])
async def get_password(
    password_id: str,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Récupère un mot de passe spécifique par son ID.
    
    - **password_id**: Identifiant unique du mot de passe
    """
    try:
        password = manager.get_password(password_id)
        if not password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mot de passe non trouvé"
            )
        
        return PasswordResponse(
            id=password['id'],
            title=password['title'],
            username=password['username'],
            url=password['url'],
            category=password['category'],
            created_at=password['created_at'],
            updated_at=password.get('updated_at'),
            access_count=password['access_count']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@app.get("/api/passwords/{password_id}/decrypt", response_model=PasswordWithDecrypted, tags=["Mots de passe"])
async def decrypt_password(
    password_id: str,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Déchiffre et retourne un mot de passe spécifique.
    
    ⚠️ **Attention**: Cette endpoint retourne le mot de passe en clair.
    
    - **password_id**: Identifiant unique du mot de passe
    """
    try:
        password = manager.get_password(password_id)
        if not password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mot de passe non trouvé"
            )
        
        return PasswordWithDecrypted(
            id=password['id'],
            title=password['title'],
            username=password['username'],
            url=password['url'],
            category=password['category'],
            created_at=password['created_at'],
            updated_at=password.get('updated_at'),
            access_count=password['access_count'],
            decrypted_password=password['password']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du déchiffrement: {str(e)}"
        )

@app.put("/api/passwords/{password_id}", response_model=PasswordResponse, tags=["Mots de passe"])
async def update_password(
    password_id: str,
    password_data: PasswordUpdate,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Met à jour un mot de passe existant.
    
    - **password_id**: Identifiant unique du mot de passe
    - Tous les champs sont optionnels lors de la mise à jour
    """
    try:
        # Préparer les données pour la mise à jour
        update_data = {}
        if password_data.title is not None:
            update_data['title'] = password_data.title
        if password_data.username is not None:
            update_data['username'] = password_data.username
        if password_data.password is not None:
            update_data['password'] = password_data.password
        if password_data.url is not None:
            update_data['url'] = password_data.url
        if password_data.category is not None:
            update_data['category'] = password_data.category
        if password_data.notes is not None:
            update_data['notes'] = password_data.notes
        
        success = manager.update_password(password_id, **update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mot de passe non trouvé"
            )
        
        # Récupérer les données mises à jour
        updated_password = manager.get_password(password_id)
        return PasswordResponse(
            id=updated_password['id'],
            title=updated_password['title'],
            username=updated_password['username'],
            url=updated_password['url'],
            category=updated_password['category'],
            created_at=updated_password['created_at'],
            updated_at=updated_password.get('updated_at'),
            access_count=updated_password['access_count']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@app.delete("/api/passwords/{password_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Mots de passe"])
async def delete_password(
    password_id: str,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Supprime définitivement un mot de passe.
    
    ⚠️ **Attention**: Cette action est irréversible.
    
    - **password_id**: Identifiant unique du mot de passe à supprimer
    """
    try:
        success = manager.delete_password(password_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mot de passe non trouvé"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

# Endpoints de gestion des catégories
@app.get("/api/categories", response_model=List[CategoryResponse], tags=["Catégories"])
async def get_categories(manager: GestionnaireMDP = Depends(get_password_manager)):
    """
    Récupère toutes les catégories disponibles.
    """
    try:
        categories = manager.list_categories()
        return [
            CategoryResponse(
                name=cat[0],
                description=cat[1],
                color=cat[2]
            )
            for cat in categories
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des catégories: {str(e)}"
        )

@app.post("/api/categories", response_model=CategoryResponse, tags=["Catégories"])
async def create_category(
    category_data: CategoryCreate,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Crée une nouvelle catégorie.
    
    - **name**: Nom de la catégorie (obligatoire, unique)
    - **description**: Description de la catégorie (optionnel)
    - **color**: Code couleur hex (optionnel, défaut: #607D8B)
    """
    try:
        success = manager.add_category(
            category_data.name,
            category_data.description or "",
            category_data.color or "#607D8B"
        )
        
        if success:
            return CategoryResponse(
                name=category_data.name,
                description=category_data.description,
                color=category_data.color or "#607D8B"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de créer la catégorie (nom déjà existant?)"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la catégorie: {str(e)}"
        )

# Endpoints de statistiques
@app.get("/api/stats", response_model=dict, tags=["Statistiques"])
async def get_statistics(manager: GestionnaireMDP = Depends(get_password_manager)):
    """
    Récupère les statistiques d'utilisation du gestionnaire.
    """
    try:
        stats = manager.get_statistics()
        if stats:
            return {
                "total_passwords": stats['total_passwords'],
                "by_category": dict(stats['by_category']),
                "most_accessed": dict(stats['most_accessed']),
                "age_distribution": stats['age_distribution']
            }
        else:
            return {
                "total_passwords": 0,
                "by_category": {},
                "most_accessed": {},
                "age_distribution": {"recent": 0, "medium": 0, "old": 0}
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

# Modèles pour la synchronisation cloud
class CloudSyncConfig(BaseModel):
    provider: str = Field(..., description="Fournisseur cloud (dropbox, google_drive)")
    access_token: str = Field(..., description="Token d'accès au service cloud")
    encryption_password: str = Field(..., description="Mot de passe pour chiffrer les données")

class CloudSyncStatus(BaseModel):
    provider: str
    last_sync: Optional[str]
    status: str
    message: str

# Endpoints de synchronisation cloud
@app.post("/api/sync/to-cloud", response_model=CloudSyncStatus, tags=["Synchronisation Cloud"])
async def sync_to_cloud(
    sync_config: CloudSyncConfig,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Synchronise les données vers le cloud (Dropbox ou Google Drive).
    
    - **provider**: Fournisseur cloud (dropbox ou google_drive)
    - **access_token**: Token d'accès au service cloud
    - **encryption_password**: Mot de passe pour chiffrer les données
    """
    try:
        # Import dynamique pour éviter les erreurs si le module n'est pas disponible
        from cloud_sync import DropboxSync, GoogleDriveSync
        
        if sync_config.provider.lower() == "dropbox":
            sync_manager = DropboxSync(manager, sync_config.access_token, sync_config.encryption_password)
        elif sync_config.provider.lower() == "google_drive":
            sync_manager = GoogleDriveSync(manager, sync_config.access_token, sync_config.encryption_password)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fournisseur non supporté. Utilisez 'dropbox' ou 'google_drive'"
            )
        
        # Effectuer la synchronisation
        success = sync_manager.sync_to_cloud()
        
        if success:
            return CloudSyncStatus(
                provider=sync_config.provider,
                last_sync=datetime.utcnow().isoformat(),
                status="success",
                message="Synchronisation vers le cloud réussie"
            )
        else:
            return CloudSyncStatus(
                provider=sync_config.provider,
                last_sync=None,
                status="error",
                message="Échec de la synchronisation vers le cloud"
            )
            
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Module de synchronisation cloud non disponible"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )

@app.post("/api/sync/from-cloud", response_model=CloudSyncStatus, tags=["Synchronisation Cloud"])
async def sync_from_cloud(
    sync_config: CloudSyncConfig,
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Synchronise les données depuis le cloud (Dropbox ou Google Drive).
    
    - **provider**: Fournisseur cloud (dropbox ou google_drive)
    - **access_token**: Token d'accès au service cloud
    - **encryption_password**: Mot de passe pour déchiffrer les données
    """
    try:
        from cloud_sync import DropboxSync, GoogleDriveSync
        
        if sync_config.provider.lower() == "dropbox":
            sync_manager = DropboxSync(manager, sync_config.access_token, sync_config.encryption_password)
        elif sync_config.provider.lower() == "google_drive":
            sync_manager = GoogleDriveSync(manager, sync_config.access_token, sync_config.encryption_password)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fournisseur non supporté. Utilisez 'dropbox' ou 'google_drive'"
            )
        
        # Effectuer la synchronisation
        success = sync_manager.sync_from_cloud()
        
        if success:
            return CloudSyncStatus(
                provider=sync_config.provider,
                last_sync=datetime.utcnow().isoformat(),
                status="success",
                message="Synchronisation depuis le cloud réussie"
            )
        else:
            return CloudSyncStatus(
                provider=sync_config.provider,
                last_sync=None,
                status="error",
                message="Échec de la synchronisation depuis le cloud"
            )
            
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Module de synchronisation cloud non disponible"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )

@app.get("/api/sync/status", response_model=dict, tags=["Synchronisation Cloud"])
async def get_sync_status(manager: GestionnaireMDP = Depends(get_password_manager)):
    """
    Récupère le statut de synchronisation cloud.
    """
    try:
        from cloud_sync import CloudSyncManager
        import json
        from pathlib import Path
        
        # Charger la configuration de synchronisation
        config_file = Path.home() / '.password_manager_sync.json'
        sync_status = {
            "dropbox": {"enabled": False, "last_sync": None},
            "google_drive": {"enabled": False, "last_sync": None}
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            if 'dropbox' in config:
                sync_status['dropbox'] = {
                    "enabled": config['dropbox'].get('enabled', False),
                    "last_sync": config['dropbox'].get('last_sync')
                }
                
            if 'google_drive' in config:
                sync_status['google_drive'] = {
                    "enabled": config['google_drive'].get('enabled', False),
                    "last_sync": config['google_drive'].get('last_sync')
                }
        
        return sync_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )

# Endpoint de santé
@app.get("/api/health", tags=["Système"])
async def health_check():
    """
    Vérifie l'état de santé de l'API.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)