#!/usr/bin/env python3
"""
API REST complète pour le Système d'Alertes Sécurité
Amélioration prioritaire : API REST avec authentification et documentation OpenAPI
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import secrets
import sqlite3
from typing import Dict, List, Optional, Any

from alertes_securite import SystemeAlertes, Alerte

# Configuration de l'API
app = Flask(__name__)
CORS(app)

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
API_KEY_HEADER = 'X-API-Key'
API_KEYS_DB = 'api_keys.db'

def init_api_keys_db():
    """Initialiser la base des clés API"""
    conn = sqlite3.connect(API_KEYS_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            key_hash TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            permissions TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_used DATETIME,
            active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Créer une clé par défaut si aucune n'existe
    cursor.execute('SELECT COUNT(*) FROM api_keys WHERE active = TRUE')
    if cursor.fetchone()[0] == 0:
        default_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(default_key.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO api_keys (key_hash, name, permissions)
            VALUES (?, ?, ?)
        ''', (key_hash, 'default_admin', 'admin'))
        
        print(f"🔑 Clé API par défaut générée: {default_key}")
        print("⚠️  Sauvegardez cette clé, elle ne sera plus affichée !")
    
    conn.commit()
    conn.close()

def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Valider une clé API"""
    if not api_key:
        return None
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    conn = sqlite3.connect(API_KEYS_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, permissions FROM api_keys 
        WHERE key_hash = ? AND active = TRUE
    ''', (key_hash,))
    
    result = cursor.fetchone()
    if result:
        # Mettre à jour last_used
        cursor.execute('''
            UPDATE api_keys SET last_used = CURRENT_TIMESTAMP 
            WHERE key_hash = ?
        ''', (key_hash,))
        conn.commit()
        
        conn.close()
        return {
            'name': result[0],
            'permissions': result[1]
        }
    
    conn.close()
    return None

def require_api_key(permissions: List[str] = None):
    """Décorateur pour vérifier l'authentification API"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get(API_KEY_HEADER)
            
            if not api_key:
                return jsonify({
                    'error': 'API key required',
                    'message': f'Please provide API key in {API_KEY_HEADER} header'
                }), 401
            
            key_info = validate_api_key(api_key)
            if not key_info:
                return jsonify({
                    'error': 'Invalid API key',
                    'message': 'The provided API key is invalid or inactive'
                }), 401
            
            # Vérifier les permissions
            if permissions:
                user_permissions = key_info['permissions'].split(',')
                if not any(perm in user_permissions or 'admin' in user_permissions for perm in permissions):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'message': f'Required permissions: {", ".join(permissions)}'
                    }), 403
            
            # Ajouter les infos utilisateur à la requête
            request.api_user = key_info
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Initialiser le système d'alertes
systeme_alertes = SystemeAlertes()

# Routes API

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': 'operational',
            'ml_detector': 'operational' if systeme_alertes.ml_detector and systeme_alertes.ml_detector.models_trained else 'not_trained'
        }
    })

@app.route('/api/v1/alerts', methods=['GET'])
@require_api_key(['read', 'admin'])
@limiter.limit("30 per minute")
def get_alerts():
    """Récupérer la liste des alertes avec pagination et filtres"""
    try:
        # Paramètres de requête
        limit = min(int(request.args.get('limit', 50)), 100)
        niveau = request.args.get('niveau')
        source = request.args.get('source')
        resolu = request.args.get('resolu')
        since = request.args.get('since')  # ISO format
        
        # Convertir resolu en booléen
        resolu_bool = None
        if resolu is not None:
            resolu_bool = resolu.lower() == 'true'
        
        # Filtrer par date si spécifié
        alertes = systeme_alertes.lister_alertes(limite=limit, niveau=niveau, resolu=resolu_bool)
        
        if since:
            since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
            alertes = [a for a in alertes if a.timestamp >= since_date.replace(tzinfo=None)]
        
        if source:
            alertes = [a for a in alertes if source.lower() in a.source.lower()]
        
        # Convertir en dictionnaire
        alertes_dict = []
        for alerte in alertes:
            alertes_dict.append({
                'id': alerte.id,
                'timestamp': alerte.timestamp.isoformat(),
                'niveau': alerte.niveau,
                'source': alerte.source,
                'message': alerte.message,
                'details': alerte.details,
                'resolu': alerte.resolu
            })
        
        return jsonify({
            'alerts': alertes_dict,
            'count': len(alertes_dict),
            'total': len(systeme_alertes.lister_alertes(limite=1000)),
            'filters': {
                'niveau': niveau,
                'source': source,
                'resolu': resolu,
                'since': since,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/alerts/<alert_id>', methods=['GET'])
@require_api_key(['read', 'admin'])
def get_alert(alert_id):
    """Récupérer une alerte spécifique"""
    try:
        alertes = systeme_alertes.lister_alertes(limite=1000)
        alerte = next((a for a in alertes if a.id == alert_id), None)
        
        if not alerte:
            return jsonify({'error': 'Alert not found'}), 404
        
        return jsonify({
            'id': alerte.id,
            'timestamp': alerte.timestamp.isoformat(),
            'niveau': alerte.niveau,
            'source': alerte.source,
            'message': alerte.message,
            'details': alerte.details,
            'resolu': alerte.resolu
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/alerts/<alert_id>/resolve', methods=['POST'])
@require_api_key(['write', 'admin'])
def resolve_alert(alert_id):
    """Marquer une alerte comme résolue"""
    try:
        success = systeme_alertes.marquer_resolu(alert_id)
        
        if success:
            return jsonify({
                'message': 'Alert marked as resolved',
                'alert_id': alert_id,
                'resolved_at': datetime.now().isoformat(),
                'resolved_by': request.api_user['name']
            })
        else:
            return jsonify({'error': 'Alert not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/alerts', methods=['POST'])
@require_api_key(['write', 'admin'])
def create_alert():
    """Créer une nouvelle alerte"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['niveau', 'source', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if data['niveau'] not in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            return jsonify({'error': 'Invalid niveau. Must be: INFO, WARNING, ERROR, CRITICAL'}), 400
        
        # Créer l'alerte
        alerte = Alerte(
            id=f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}",
            timestamp=datetime.now(),
            niveau=data['niveau'],
            source=data['source'],
            message=data['message'],
            details=data.get('details', {}),
            resolu=False
        )
        
        # Enregistrer
        systeme_alertes.enregistrer_alerte(alerte)
        
        return jsonify({
            'message': 'Alert created successfully',
            'alert': {
                'id': alerte.id,
                'timestamp': alerte.timestamp.isoformat(),
                'niveau': alerte.niveau,
                'source': alerte.source,
                'message': alerte.message,
                'details': alerte.details,
                'resolu': alerte.resolu
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/statistics', methods=['GET'])
@require_api_key(['read', 'admin'])
def get_statistics():
    """Récupérer les statistiques des alertes"""
    try:
        stats = systeme_alertes.obtenir_statistiques()
        return jsonify({
            'statistics': stats,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/ml/analyze', methods=['POST'])
@require_api_key(['read', 'admin'])
def ml_analyze():
    """Analyser une alerte avec ML"""
    try:
        if not systeme_alertes.ml_detector or not systeme_alertes.ml_detector.models_trained:
            return jsonify({
                'error': 'ML detector not available or not trained'
            }), 503
        
        data = request.get_json()
        
        # Analyser avec ML
        result = systeme_alertes.ml_detector.detect_anomaly(data)
        
        return jsonify({
            'ml_analysis': {
                'is_anomaly': result.is_anomaly,
                'confidence_score': result.confidence_score,
                'anomaly_type': result.anomaly_type,
                'cluster_id': result.cluster_id,
                'explanation': result.explanation,
                'features_importance': result.features_importance,
                'analyzed_at': result.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/ml/report', methods=['GET'])
@require_api_key(['read', 'admin'])
def ml_report():
    """Obtenir le rapport d'analyse ML"""
    try:
        if not systeme_alertes.ml_detector or not systeme_alertes.ml_detector.models_trained:
            return jsonify({
                'error': 'ML detector not available or not trained'
            }), 503
        
        report = systeme_alertes.ml_detector.generate_analytics_report()
        return jsonify({'ml_report': report})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/rules', methods=['GET'])
@require_api_key(['read', 'admin'])
def get_rules():
    """Récupérer les règles d'alerte actives"""
    try:
        regles = systeme_alertes.regles_actives()
        
        regles_dict = []
        for regle in regles:
            regles_dict.append({
                'id': regle.id,
                'nom': regle.nom,
                'actif': regle.actif,
                'source': regle.source,
                'pattern': regle.pattern,
                'niveau': regle.niveau,
                'description': regle.description,
                'canaux': regle.canaux,
                'cooldown': regle.cooldown
            })
        
        return jsonify({
            'rules': regles_dict,
            'count': len(regles_dict)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Documentation OpenAPI
@app.route('/api/v1/docs', methods=['GET'])
def api_documentation():
    """Documentation interactive de l'API"""
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Système d'Alertes Sécurité - Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .method { display: inline-block; padding: 4px 8px; color: white; border-radius: 3px; font-weight: bold; }
            .get { background: #28a745; }
            .post { background: #007bff; }
            .put { background: #ffc107; }
            .delete { background: #dc3545; }
            code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 API Système d'Alertes Sécurité</h1>
            <p>Documentation complète de l'API REST v1.0.0</p>
            
            <h2>🔐 Authentification</h2>
            <p>Toutes les requêtes nécessitent un en-tête <code>X-API-Key</code> avec une clé valide.</p>
            
            <h2>📡 Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/v1/health</h3>
                <p>Vérification de l'état de l'API</p>
                <p><strong>Authentification:</strong> Non requise</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/v1/alerts</h3>
                <p>Récupérer la liste des alertes avec pagination et filtres</p>
                <p><strong>Paramètres:</strong> limit, niveau, source, resolu, since</p>
                <p><strong>Permissions:</strong> read, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/v1/alerts/{id}</h3>
                <p>Récupérer une alerte spécifique par son ID</p>
                <p><strong>Permissions:</strong> read, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/v1/alerts</h3>
                <p>Créer une nouvelle alerte</p>
                <p><strong>Body:</strong> { "niveau": "ERROR", "source": "api", "message": "Test alert", "details": {} }</p>
                <p><strong>Permissions:</strong> write, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/v1/alerts/{id}/resolve</h3>
                <p>Marquer une alerte comme résolue</p>
                <p><strong>Permissions:</strong> write, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/v1/statistics</h3>
                <p>Récupérer les statistiques des alertes</p>
                <p><strong>Permissions:</strong> read, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /api/v1/ml/analyze</h3>
                <p>Analyser une alerte avec Machine Learning</p>
                <p><strong>Body:</strong> Données de l'alerte à analyser</p>
                <p><strong>Permissions:</strong> read, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/v1/ml/report</h3>
                <p>Obtenir le rapport d'analyse ML</p>
                <p><strong>Permissions:</strong> read, admin</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /api/v1/rules</h3>
                <p>Récupérer les règles d'alerte actives</p>
                <p><strong>Permissions:</strong> read, admin</p>
            </div>
            
            <h2>📊 Codes de Réponse</h2>
            <ul>
                <li><strong>200:</strong> Succès</li>
                <li><strong>201:</strong> Créé</li>
                <li><strong>400:</strong> Requête invalide</li>
                <li><strong>401:</strong> Non authentifié</li>
                <li><strong>403:</strong> Non autorisé</li>
                <li><strong>404:</strong> Non trouvé</li>
                <li><strong>429:</strong> Trop de requêtes</li>
                <li><strong>500:</strong> Erreur serveur</li>
            </ul>
            
            <h2>💡 Exemples d'utilisation</h2>
            <pre><code>
# Récupérer toutes les alertes ERROR
curl -H "X-API-Key: YOUR_API_KEY" "http://localhost:5000/api/v1/alerts?niveau=ERROR&limit=10"

# Créer une nouvelle alerte
curl -X POST -H "X-API-Key: YOUR_API_KEY" -H "Content-Type: application/json" \
  -d '{"niveau":"WARNING","source":"api","message":"Test from API"}' \
  http://localhost:5000/api/v1/alerts

# Marquer une alerte comme résolue
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:5000/api/v1/alerts/ALERT_ID/resolve
            </code></pre>
        </div>
    </body>
    </html>
    """
    return docs_html

# Gestion des erreurs
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please slow down.'
    }), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

def run_api_server(host='0.0.0.0', port=5001, debug=False):
    """Lancer le serveur API"""
    print(f"🚀 Démarrage du serveur API sur http://{host}:{port}")
    print(f"📖 Documentation disponible sur http://{host}:{port}/api/v1/docs")
    
    init_api_keys_db()
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="API REST Système d'Alertes Sécurité")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute")
    parser.add_argument("--port", type=int, default=5001, help="Port d'écoute")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    
    args = parser.parse_args()
    run_api_server(host=args.host, port=args.port, debug=args.debug)