#!/usr/bin/env python3
"""
API REST Complète - Analyseur de Trafic Réseau
API RESTful avec authentification JWT pour intégrations externes

Fonctionnalités:
- Endpoints RESTful complets (CRUD)
- Authentification JWT
- Documentation OpenAPI/Swagger
- Rate limiting
- Versioning API
- Gestion des sessions de capture
- Export de données
- Statistiques en temps réel
"""

from flask import Flask, request, jsonify, g
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from colorama import Fore, Style
import logging
from functools import wraps
import threading
import time
import uuid

# Importer nos modules locaux
try:
    from database_manager import DatabaseManager
    from ml_detector import MLAnomalyDetector
    from notification_system import NotificationSystem
    from advanced_filters import AdvancedPacketFilters
except ImportError as e:
    print(f"{Fore.YELLOW}⚠ Modules locaux non disponibles: {e}")

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-string-change-this-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Extensions
jwt = JWTManager(app)
api = Api(app)
CORS(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

class TrafficAnalyzerAPI:
    """API principale pour l'analyseur de trafic"""
    
    def __init__(self):
        self.db_manager = None
        self.ml_detector = None
        self.notification_system = None
        self.filter_system = None
        self.users_db = "api_users.db"
        self.active_captures = {}
        self.logger = self._setup_logger()
        
        # Initialiser les composants
        self._init_components()
        self._init_database()
        
        print(f"{Fore.GREEN}✓ API REST initialisée")
    
    def _setup_logger(self):
        """Configuration du logger pour l'API"""
        logger = logging.getLogger('TrafficAnalyzerAPI')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _init_components(self):
        """Initialiser les composants optionnels"""
        try:
            self.db_manager = DatabaseManager("api_traffic.db")
            self.ml_detector = MLAnomalyDetector()
            self.notification_system = NotificationSystem()
            self.filter_system = AdvancedPacketFilters()
        except Exception as e:
            self.logger.warning(f"Certains composants non disponibles: {e}")
    
    def _init_database(self):
        """Initialiser la base de données des utilisateurs"""
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    api_key TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Créer un utilisateur admin par défaut
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role, api_key)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin', str(uuid.uuid4())))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la BDD: {e}")

# Instance globale
traffic_api = TrafficAnalyzerAPI()

# Décorateurs pour l'authentification
def api_key_required(f):
    """Décorateur pour vérifier l'API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return {'error': 'API key manquante'}, 401
        
        # Vérifier l'API key en base
        try:
            conn = sqlite3.connect(traffic_api.users_db)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, role FROM users WHERE api_key = ? AND is_active = 1', (api_key,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return {'error': 'API key invalide'}, 401
            
            g.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[2]
            }
            
        except Exception as e:
            return {'error': 'Erreur de validation'}, 500
        
        return f(*args, **kwargs)
    return decorated_function

# Endpoints d'authentification
class AuthResource(Resource):
    def post(self):
        """Authentification par username/password"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return {'error': 'Username et password requis'}, 400
            
            conn = sqlite3.connect(traffic_api.users_db)
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash, role FROM users WHERE username = ? AND is_active = 1', (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and check_password_hash(user[1], password):
                access_token = create_access_token(identity=username)
                return {
                    'access_token': access_token,
                    'user': {
                        'id': user[0],
                        'username': username,
                        'role': user[2]
                    }
                }
            
            return {'error': 'Credentials invalides'}, 401
            
        except Exception as e:
            return {'error': str(e)}, 500

class UsersResource(Resource):
    @api_key_required
    def get(self):
        """Lister les utilisateurs (admin seulement)"""
        if g.current_user['role'] != 'admin':
            return {'error': 'Accès interdit'}, 403
        
        try:
            conn = sqlite3.connect(traffic_api.users_db)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, role, created_at, is_active FROM users')
            users = cursor.fetchall()
            conn.close()
            
            return {
                'users': [
                    {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'role': user[3],
                        'created_at': user[4],
                        'is_active': bool(user[5])
                    } for user in users
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @api_key_required
    def post(self):
        """Créer un nouvel utilisateur (admin seulement)"""
        if g.current_user['role'] != 'admin':
            return {'error': 'Accès interdit'}, 403
        
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            role = data.get('role', 'user')
            
            if not username or not password:
                return {'error': 'Username et password requis'}, 400
            
            password_hash = generate_password_hash(password)
            api_key = str(uuid.uuid4())
            
            conn = sqlite3.connect(traffic_api.users_db)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role, api_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, role, api_key))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return {
                'message': 'Utilisateur créé avec succès',
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'api_key': api_key
                }
            }, 201
            
        except sqlite3.IntegrityError:
            return {'error': 'Username déjà existant'}, 409
        except Exception as e:
            return {'error': str(e)}, 500

# Endpoints pour les captures
class CapturesResource(Resource):
    @api_key_required
    @limiter.limit("10 per minute")
    def get(self):
        """Lister les sessions de capture"""
        try:
            if not traffic_api.db_manager:
                return {'error': 'Database manager non disponible'}, 503
            
            limit = request.args.get('limit', 50, type=int)
            sessions = traffic_api.db_manager.get_capture_sessions(limit)
            
            return {
                'sessions': [
                    {
                        'id': session[0],
                        'start_time': session[1],
                        'end_time': session[2],
                        'interface': session[3],
                        'total_packets': session[4],
                        'anomalies_count': session[5],
                        'status': session[6]
                    } for session in sessions
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @api_key_required
    @limiter.limit("5 per minute")
    def post(self):
        """Démarrer une nouvelle capture"""
        try:
            data = request.get_json()
            interface = data.get('interface', 'eth0')
            duration = data.get('duration', 60)
            filters = data.get('filters', '')
            
            # Générer un ID unique pour la capture
            capture_id = str(uuid.uuid4())
            
            # Simuler le démarrage de capture (en production, utiliser threading)
            capture_info = {
                'id': capture_id,
                'interface': interface,
                'duration': duration,
                'filters': filters,
                'start_time': datetime.now().isoformat(),
                'status': 'running',
                'user_id': g.current_user['id']
            }
            
            traffic_api.active_captures[capture_id] = capture_info
            
            return {
                'message': 'Capture démarrée',
                'capture': capture_info
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

class CaptureResource(Resource):
    @api_key_required
    def get(self, capture_id):
        """Obtenir les détails d'une capture"""
        try:
            if capture_id in traffic_api.active_captures:
                return {'capture': traffic_api.active_captures[capture_id]}
            
            if traffic_api.db_manager:
                # Rechercher dans la base de données
                session = traffic_api.db_manager.get_capture_session(capture_id)
                if session:
                    return {
                        'capture': {
                            'id': session[0],
                            'start_time': session[1],
                            'end_time': session[2],
                            'interface': session[3],
                            'total_packets': session[4],
                            'status': 'completed'
                        }
                    }
            
            return {'error': 'Capture non trouvée'}, 404
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @api_key_required
    def delete(self, capture_id):
        """Arrêter une capture"""
        try:
            if capture_id in traffic_api.active_captures:
                capture = traffic_api.active_captures[capture_id]
                capture['status'] = 'stopped'
                capture['end_time'] = datetime.now().isoformat()
                
                return {
                    'message': 'Capture arrêtée',
                    'capture': capture
                }
            
            return {'error': 'Capture non trouvée ou déjà arrêtée'}, 404
            
        except Exception as e:
            return {'error': str(e)}, 500

# Endpoints pour les statistiques
class StatsResource(Resource):
    @api_key_required
    @limiter.limit("20 per minute")
    def get(self):
        """Obtenir les statistiques globales"""
        try:
            if not traffic_api.db_manager:
                return {'error': 'Database manager non disponible'}, 503
            
            stats = traffic_api.db_manager.get_statistics_summary()
            
            # Ajouter des statistiques API
            api_stats = {
                'active_captures': len(traffic_api.active_captures),
                'total_api_calls': getattr(g, 'api_call_count', 0),
                'system_status': 'operational'
            }
            
            return {
                'database_stats': stats,
                'api_stats': api_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

# Endpoints pour les anomalies
class AnomaliesResource(Resource):
    @api_key_required
    def get(self):
        """Lister les anomalies détectées"""
        try:
            if not traffic_api.db_manager:
                return {'error': 'Database manager non disponible'}, 503
            
            limit = request.args.get('limit', 100, type=int)
            severity = request.args.get('severity', None)
            
            # Simuler des anomalies (en production, récupérer depuis la DB)
            anomalies = [
                {
                    'id': 1,
                    'type': 'Port Scan Detected',
                    'severity': 'high',
                    'source_ip': '192.168.1.100',
                    'timestamp': datetime.now().isoformat(),
                    'details': 'Multiple port scan attempts detected'
                },
                {
                    'id': 2,
                    'type': 'High Traffic Volume',
                    'severity': 'medium',
                    'source_ip': '10.0.1.50',
                    'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                    'details': 'Traffic volume exceeded threshold'
                }
            ]
            
            if severity:
                anomalies = [a for a in anomalies if a['severity'] == severity]
            
            return {
                'anomalies': anomalies[:limit],
                'total': len(anomalies)
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

# Endpoints pour les filtres
class FiltersResource(Resource):
    @api_key_required
    def get(self):
        """Lister les filtres disponibles"""
        try:
            if not traffic_api.filter_system:
                return {'error': 'Filter system non disponible'}, 503
            
            filters = traffic_api.filter_system.list_available_filters()
            
            return {
                'filters': [
                    {
                        'name': name,
                        'bpf_expression': expression,
                        'type': 'predefined'
                    } for name, expression in filters.items()
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @api_key_required
    def post(self):
        """Créer un filtre personnalisé"""
        try:
            if not traffic_api.filter_system:
                return {'error': 'Filter system non disponible'}, 503
            
            data = request.get_json()
            name = data.get('name')
            bpf_expression = data.get('bpf_expression')
            description = data.get('description', '')
            
            if not name or not bpf_expression:
                return {'error': 'Name et bpf_expression requis'}, 400
            
            success = traffic_api.filter_system.create_custom_filter(name, bpf_expression, description)
            
            if success:
                return {
                    'message': 'Filtre créé avec succès',
                    'filter': {
                        'name': name,
                        'bpf_expression': bpf_expression,
                        'description': description
                    }
                }, 201
            else:
                return {'error': 'Échec de création du filtre'}, 400
            
        except Exception as e:
            return {'error': str(e)}, 500

# Endpoints d'export
class ExportResource(Resource):
    @api_key_required
    @limiter.limit("5 per minute")
    def post(self):
        """Exporter des données de capture"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            format_type = data.get('format', 'json')
            
            if not session_id:
                return {'error': 'session_id requis'}, 400
            
            if format_type not in ['json', 'csv']:
                return {'error': 'Format supporté: json, csv'}, 400
            
            # Simuler l'export (en production, récupérer les vraies données)
            export_data = {
                'session_id': session_id,
                'format': format_type,
                'data': {
                    'packets': [
                        {
                            'timestamp': datetime.now().isoformat(),
                            'src_ip': '192.168.1.10',
                            'dst_ip': '192.168.1.1',
                            'protocol': 'TCP',
                            'src_port': 54321,
                            'dst_port': 80,
                            'length': 1024
                        }
                    ],
                    'statistics': {
                        'total_packets': 1,
                        'total_bytes': 1024
                    }
                },
                'exported_at': datetime.now().isoformat(),
                'exported_by': g.current_user['username']
            }
            
            return export_data
            
        except Exception as e:
            return {'error': str(e)}, 500

# Endpoint de santé du système
class HealthResource(Resource):
    def get(self):
        """Vérification de santé de l'API"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'components': {
                    'database': 'available' if traffic_api.db_manager else 'unavailable',
                    'ml_detector': 'available' if traffic_api.ml_detector else 'unavailable',
                    'notifications': 'available' if traffic_api.notification_system else 'unavailable',
                    'filters': 'available' if traffic_api.filter_system else 'unavailable'
                },
                'active_captures': len(traffic_api.active_captures)
            }
            
            return health_status
            
        except Exception as e:
            return {'error': str(e), 'status': 'unhealthy'}, 500

# Enregistrement des routes
api.add_resource(AuthResource, '/api/v1/auth')
api.add_resource(UsersResource, '/api/v1/users')
api.add_resource(CapturesResource, '/api/v1/captures')
api.add_resource(CaptureResource, '/api/v1/captures/<string:capture_id>')
api.add_resource(StatsResource, '/api/v1/stats')
api.add_resource(AnomaliesResource, '/api/v1/anomalies')
api.add_resource(FiltersResource, '/api/v1/filters')
api.add_resource(ExportResource, '/api/v1/export')
api.add_resource(HealthResource, '/api/v1/health')

# Documentation Swagger
@app.route('/api/v1/docs')
def swagger_docs():
    """Documentation Swagger de l'API"""
    swagger_spec = {
        "swagger": "2.0",
        "info": {
            "title": "Traffic Analyzer API",
            "version": "1.0.0",
            "description": "API REST pour l'Analyseur de Trafic Réseau"
        },
        "host": "localhost:5000",
        "schemes": ["http"],
        "basePath": "/api/v1",
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        },
        "paths": {
            "/auth": {
                "post": {
                    "summary": "Authentification",
                    "parameters": [
                        {
                            "name": "credentials",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {"description": "Succès"},
                        "401": {"description": "Credentials invalides"}
                    }
                }
            },
            "/captures": {
                "get": {
                    "summary": "Lister les captures",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {
                        "200": {"description": "Liste des captures"}
                    }
                },
                "post": {
                    "summary": "Démarrer une capture",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {
                        "201": {"description": "Capture démarrée"}
                    }
                }
            },
            "/stats": {
                "get": {
                    "summary": "Statistiques globales",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {
                        "200": {"description": "Statistiques"}
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Santé du système",
                    "responses": {
                        "200": {"description": "Status de santé"}
                    }
                }
            }
        }
    }
    
    return jsonify(swagger_spec)

def main():
    """Démarrer le serveur API"""
    print(f"{Fore.BLUE}🌐 API REST - ANALYSEUR DE TRAFIC RÉSEAU")
    print("=" * 60)
    print(f"{Fore.GREEN}✓ Serveur démarré sur http://localhost:5000")
    print(f"{Fore.CYAN}📚 Documentation: http://localhost:5000/api/v1/docs")
    print(f"{Fore.CYAN}🏥 Health check: http://localhost:5000/api/v1/health")
    print(f"\n{Fore.YELLOW}Credentials par défaut:")
    print(f"Username: admin")
    print(f"Password: admin123")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()