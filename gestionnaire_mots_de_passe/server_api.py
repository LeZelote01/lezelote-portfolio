#!/usr/bin/env python3
"""
API REST pour le Gestionnaire de Mots de Passe - Version Test
Serveur simplifié pour tester les fonctionnalités de base
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
import os
import getpass
import jwt
import secrets

# Imports locaux
try:
    from gestionnaire_mdp import GestionnaireMDP
    print("✅ Module gestionnaire importé avec succès")
except ImportError as e:
    print(f"❌ Erreur import gestionnaire: {e}")
    exit(1)

# FastAPI app
app = FastAPI(
    title="Gestionnaire de Mots de Passe API",
    description="API REST pour la gestion sécurisée des mots de passe",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# JWT Configuration
JWT_SECRET_KEY = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Global manager instance
manager = None
authenticated_tokens = set()  # Simple token store

# Pydantic models
class AuthRequest(BaseModel):
    master_password: str = Field(..., description="Mot de passe maître")

class PasswordCreate(BaseModel):
    title: str = Field(..., description="Titre du compte")
    username: Optional[str] = Field(None, description="Nom d'utilisateur")
    password: Optional[str] = Field(None, description="Mot de passe (si None, sera généré)")
    url: Optional[str] = Field(None, description="URL du site")
    notes: Optional[str] = Field(None, description="Notes additionnelles")
    category: str = Field("Autre", description="Catégorie")

class PasswordResponse(BaseModel):
    id: str
    title: str
    username: Optional[str]
    url: Optional[str]
    category: str
    created_at: str
    updated_at: Optional[str]
    access_count: int

class PasswordResponseWithPassword(PasswordResponse):
    password: str
    notes: Optional[str]

def create_jwt_token(data: dict) -> str:
    """Créer un token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str) -> dict:
    """Vérifier un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtenir l'utilisateur actuel à partir du token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Vérifier si le token est dans notre store
    if token not in authenticated_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier la validité JWT
    payload = verify_jwt_token(token)
    if payload is None:
        # Supprimer le token invalide du store
        authenticated_tokens.discard(token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
@app.post("/api/auth/login", tags=["Authentification"])
async def authenticate(auth_request: AuthRequest):
    """
    Authentifier avec le mot de passe maître
    """
    global manager
    
    try:
        temp_manager = GestionnaireMDP()
        if temp_manager.authenticate(auth_request.master_password):
            manager = temp_manager
            
            # Créer un token JWT
            token_data = {
                "authenticated": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            token = create_jwt_token(token_data)
            
            # Ajouter au store de tokens valides
            authenticated_tokens.add(token)
            
            return {
                "status": "success",
                "message": "Authentification réussie",
                "token": token
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe maître incorrect"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 401) without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'authentification: {str(e)}"
        )

def get_password_manager():
    """Dépendance pour obtenir le gestionnaire authentifié"""
    if not manager or not manager.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise"
        )
    return manager

@app.get("/api/health", tags=["Système"])
async def health_check():
    """Vérifier l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "authenticated": manager is not None and manager.is_authenticated if manager else False
    }

@app.get("/api/passwords", response_model=List[PasswordResponse], tags=["Mots de passe"])
async def list_passwords(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Récupère tous les mots de passe (sans les mots de passe eux-mêmes)
    """
    try:
        passwords = manager.list_passwords(category=category, search_term=search)
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
            for pwd in passwords
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@app.get("/api/passwords/{password_id}", response_model=PasswordResponseWithPassword, tags=["Mots de passe"])
async def get_password(
    password_id: str,
    current_user: dict = Depends(get_current_user),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Récupère un mot de passe spécifique avec déchiffrement
    """
    try:
        password_data = manager.get_password(password_id)
        if not password_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mot de passe non trouvé"
            )
        
        return PasswordResponseWithPassword(
            id=password_data['id'],
            title=password_data['title'],
            username=password_data['username'],
            password=password_data['password'],
            url=password_data['url'],
            notes=password_data['notes'],
            category=password_data['category'],
            created_at=password_data['created_at'],
            updated_at=password_data.get('updated_at'),
            access_count=password_data['access_count']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@app.post("/api/passwords", response_model=PasswordResponse, tags=["Mots de passe"])
async def create_password(
    password_data: PasswordCreate,
    current_user: dict = Depends(get_current_user),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Crée un nouveau mot de passe
    """
    try:
        # Générer le mot de passe si non fourni
        if not password_data.password:
            password_data.password = manager.generate_password()
        
        password_id = manager.add_password(
            title=password_data.title,
            username=password_data.username or "",
            password=password_data.password,
            url=password_data.url or "",
            notes=password_data.notes or "",
            category=password_data.category
        )
        
        if not password_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de créer le mot de passe"
            )
        
        # Récupérer les données créées
        created_password = manager.get_password(password_id)
        return PasswordResponse(
            id=created_password['id'],
            title=created_password['title'],
            username=created_password['username'],
            url=created_password['url'],
            category=created_password['category'],
            created_at=created_password['created_at'],
            updated_at=created_password.get('updated_at'),
            access_count=created_password['access_count']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création: {str(e)}"
        )

@app.get("/api/stats", response_model=dict, tags=["Statistiques"])
async def get_statistics(
    current_user: dict = Depends(get_current_user),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Récupère les statistiques d'utilisation
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

@app.delete("/api/passwords/{password_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Mots de passe"])
async def delete_password(
    password_id: str,
    current_user: dict = Depends(get_current_user),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Supprime définitivement un mot de passe
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

@app.post("/api/generate/password", tags=["Génération"])
async def generate_password(
    options: Optional[dict] = None
):
    """
    Génère un mot de passe avec des options personnalisables
    """
    try:
        temp_manager = GestionnaireMDP()
        
        # Options par défaut
        default_options = {
            'length': 16,
            'include_uppercase': True,
            'include_lowercase': True,
            'include_numbers': True,
            'include_symbols': True
        }
        
        if options:
            default_options.update(options)
        
        password = temp_manager.generate_password(**default_options)
        
        return {
            "password": password,
            "strength": temp_manager.calculate_password_strength(password),
            "options_used": default_options
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )

@app.get("/api/passwords/search", tags=["Mots de passe"])
async def search_passwords(
    domain: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    manager: GestionnaireMDP = Depends(get_password_manager)
):
    """
    Recherche des mots de passe par domaine
    """
    try:
        if domain:
            passwords = manager.list_passwords(search_term=domain)
            # Filtrer par URL contenant le domaine
            filtered_passwords = []
            for pwd in passwords:
                if pwd.get('url', '').find(domain) != -1 or pwd.get('title', '').find(domain) != -1:
                    filtered_passwords.append(pwd)
            passwords = filtered_passwords
        else:
            passwords = manager.list_passwords()
        
        return [
            PasswordResponseWithPassword(
                id=pwd['id'],
                title=pwd['title'],
                username=pwd['username'],
                password=pwd['password'],
                url=pwd['url'],
                notes=pwd['notes'],
                category=pwd['category'],
                created_at=pwd['created_at'],
                updated_at=pwd.get('updated_at'),
                access_count=pwd['access_count']
            )
            for pwd in passwords
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )

def main():
    """Point d'entrée principal pour lancer l'API"""
    print("🚀 Démarrage du serveur API REST...")
    print("📍 API disponible sur: http://localhost:8002")
    print("📖 Documentation: http://localhost:8002/docs")
    
    uvicorn.run(
        "server_api:app", 
        host="0.0.0.0", 
        port=8002, 
        reload=False
    )

if __name__ == "__main__":
    main()