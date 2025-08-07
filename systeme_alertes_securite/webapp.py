#!/usr/bin/env python3
"""
Interface Web pour le Système d'Alertes Sécurité
Dashboard Flask avec Socket.IO pour les mises à jour temps réel
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from alertes_securite import SystemeAlertes, Alerte

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'alertes_securite_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Instance globale du système d'alertes
systeme_alertes = None

# Variables globales pour le monitoring temps réel
monitoring_thread = None
monitoring_active = False

def init_systeme_alertes(db_path="alertes.db", config_path="config.json"):
    """Initialiser le système d'alertes"""
    global systeme_alertes
    systeme_alertes = SystemeAlertes(db_path=db_path, config_path=config_path)
    return systeme_alertes

def background_monitoring():
    """Thread de background pour envoyer les mises à jour temps réel"""
    global monitoring_active
    
    derniere_verification = time.time()
    
    while monitoring_active:
        try:
            maintenant = time.time()
            
            # Vérifier les nouvelles alertes toutes les 5 secondes
            if maintenant - derniere_verification >= 5:
                alertes_recentes = systeme_alertes.lister_alertes(limite=10)
                
                # Envoyer les nouvelles alertes via WebSocket
                for alerte in alertes_recentes:
                    socketio.emit('nouvelle_alerte', {
                        'id': alerte.id,
                        'timestamp': alerte.timestamp.isoformat(),
                        'niveau': alerte.niveau,
                        'source': alerte.source,
                        'message': alerte.message,
                        'details': alerte.details,
                        'resolu': alerte.resolu
                    })
                
                # Envoyer les statistiques mises à jour
                stats = systeme_alertes.obtenir_statistiques()
                socketio.emit('stats_update', stats)
                
                derniere_verification = maintenant
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erreur background monitoring: {e}")
            time.sleep(5)

@app.route('/')
def dashboard():
    """Page principale du dashboard"""
    return render_template('dashboard.html')

@app.route('/api/alertes')
def api_alertes():
    """API pour récupérer les alertes"""
    try:
        limite = request.args.get('limite', 50, type=int)
        niveau = request.args.get('niveau')
        resolu = request.args.get('resolu')
        
        if resolu is not None:
            resolu = resolu.lower() == 'true'
        
        alertes = systeme_alertes.lister_alertes(
            limite=limite,
            niveau=niveau,
            resolu=resolu
        )
        
        alertes_json = []
        for alerte in alertes:
            alertes_json.append({
                'id': alerte.id,
                'timestamp': alerte.timestamp.isoformat(),
                'niveau': alerte.niveau,
                'source': alerte.source,
                'message': alerte.message,
                'details': alerte.details,
                'resolu': alerte.resolu
            })
        
        return jsonify({
            'success': True,
            'alertes': alertes_json,
            'total': len(alertes_json)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def api_stats():
    """API pour récupérer les statistiques"""
    try:
        stats = systeme_alertes.obtenir_statistiques()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alertes/<alerte_id>/resolve', methods=['POST'])
def api_resolve_alerte(alerte_id):
    """API pour marquer une alerte comme résolue"""
    try:
        success = systeme_alertes.marquer_resolu(alerte_id)
        
        if success:
            # Notifier via WebSocket
            socketio.emit('alerte_resolue', {'id': alerte_id})
            
            return jsonify({
                'success': True,
                'message': 'Alerte marquée comme résolue'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Alerte introuvable'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/regles')
def api_regles():
    """API pour récupérer les règles d'alerte"""
    try:
        regles = systeme_alertes.regles_actives()
        
        regles_json = []
        for regle in regles:
            regles_json.append({
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
            'success': True,
            'regles': regles_json
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-alerte', methods=['POST'])
def api_test_alerte():
    """API pour créer une alerte de test"""
    try:
        data = request.get_json()
        
        alerte_test = Alerte(
            id=f"test_{int(time.time())}",
            timestamp=datetime.now(),
            niveau=data.get('niveau', 'INFO'),
            source="test",
            message=data.get('message', 'Alerte de test'),
            details={
                'test': True,
                'user_data': data.get('details', {}),
                'timestamp': datetime.now().isoformat()
            }
        )
        
        systeme_alertes.enregistrer_alerte(alerte_test)
        
        # Notifier via WebSocket
        socketio.emit('nouvelle_alerte', {
            'id': alerte_test.id,
            'timestamp': alerte_test.timestamp.isoformat(),
            'niveau': alerte_test.niveau,
            'source': alerte_test.source,
            'message': alerte_test.message,
            'details': alerte_test.details,
            'resolu': alerte_test.resolu
        })
        
        return jsonify({
            'success': True,
            'alerte_id': alerte_test.id,
            'message': 'Alerte de test créée'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitoring/start', methods=['POST'])
def api_start_monitoring():
    """API pour démarrer le monitoring"""
    try:
        systeme_alertes.demarrer_monitoring()
        
        # Démarrer le monitoring temps réel pour les WebSockets
        global monitoring_thread, monitoring_active
        if not monitoring_active:
            monitoring_active = True
            monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
            monitoring_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring démarré'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitoring/stop', methods=['POST'])
def api_stop_monitoring():
    """API pour arrêter le monitoring"""
    try:
        systeme_alertes.arreter_monitoring()
        
        # Arrêter le monitoring temps réel
        global monitoring_active
        monitoring_active = False
        
        return jsonify({
            'success': True,
            'message': 'Monitoring arrêté'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Routes pour servir les fichiers statiques
@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir les fichiers statiques"""
    return send_from_directory('static', filename)

# Événements WebSocket
@socketio.on('connect')
def handle_connect():
    """Client connecté via WebSocket"""
    print(f"Client connecté: {request.sid}")
    
    # Envoyer les statistiques actuelles
    try:
        stats = systeme_alertes.obtenir_statistiques()
        emit('stats_update', stats)
    except Exception as e:
        print(f"Erreur envoi stats: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Client déconnecté"""
    print(f"Client déconnecté: {request.sid}")

@socketio.on('get_alertes')
def handle_get_alertes(data):
    """Récupérer les alertes via WebSocket"""
    try:
        limite = data.get('limite', 20)
        niveau = data.get('niveau')
        resolu = data.get('resolu')
        
        alertes = systeme_alertes.lister_alertes(
            limite=limite,
            niveau=niveau,
            resolu=resolu
        )
        
        alertes_json = []
        for alerte in alertes:
            alertes_json.append({
                'id': alerte.id,
                'timestamp': alerte.timestamp.isoformat(),
                'niveau': alerte.niveau,
                'source': alerte.source,
                'message': alerte.message,
                'details': alerte.details,
                'resolu': alerte.resolu
            })
        
        emit('alertes_data', {
            'alertes': alertes_json,
            'total': len(alertes_json)
        })
        
    except Exception as e:
        emit('error', {'message': str(e)})

# Template pour la page principale
def create_dashboard_template():
    """Créer le template HTML pour le dashboard"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    dashboard_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚨 Système d'Alertes Sécurité</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --error-color: #e74c3c;
            --critical-color: #8e44ad;
            --background-color: #ecf0f1;
            --card-background: #ffffff;
            --text-color: #2c3e50;
            --border-color: #bdc3c7;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2rem;
            font-weight: 300;
        }

        .header .status {
            margin-top: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .status-indicator {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .status-online {
            background-color: var(--success-color);
        }

        .status-offline {
            background-color: var(--error-color);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .card {
            background: var(--card-background);
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border: 1px solid var(--border-color);
        }

        .card h3 {
            margin-bottom: 1rem;
            color: var(--primary-color);
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
        }

        .stat-item {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            background: #f8f9fa;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #6c757d;
        }

        .level-critical { color: var(--critical-color); }
        .level-error { color: var(--error-color); }
        .level-warning { color: var(--warning-color); }
        .level-info { color: var(--success-color); }

        .alertes-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }

        .alertes-table th,
        .alertes-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .alertes-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: var(--primary-color);
        }

        .alertes-table tr:hover {
            background-color: #f8f9fa;
        }

        .level-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
            color: white;
        }

        .level-badge.critical { background-color: var(--critical-color); }
        .level-badge.error { background-color: var(--error-color); }
        .level-badge.warning { background-color: var(--warning-color); }
        .level-badge.info { background-color: var(--success-color); }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background-color: var(--secondary-color);
            color: white;
        }

        .btn-primary:hover {
            background-color: #2980b9;
        }

        .btn-success {
            background-color: var(--success-color);
            color: white;
        }

        .btn-success:hover {
            background-color: #229954;
        }

        .btn-warning {
            background-color: var(--warning-color);
            color: white;
        }

        .btn-small {
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
        }

        .controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .form-group label {
            font-size: 0.9rem;
            font-weight: 500;
        }

        .form-group select,
        .form-group input {
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            font-size: 0.9rem;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 5px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification.success {
            background-color: var(--success-color);
        }

        .notification.error {
            background-color: var(--error-color);
        }

        .notification.warning {
            background-color: var(--warning-color);
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .controls {
                flex-direction: column;
            }
            
            .alertes-table {
                font-size: 0.8rem;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>🚨 Système d'Alertes Sécurité</h1>
        <div class="status">
            <span class="status-indicator status-offline" id="connection-status">🔴 Déconnecté</span>
            <span>Dernière mise à jour: <span id="last-update">--</span></span>
        </div>
    </header>

    <div class="container">
        <!-- Statistiques -->
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Statistiques Globales</h3>
                <div class="stats-grid" id="stats-globales">
                    <div class="stat-item">
                        <div class="stat-number" id="stat-total">0</div>
                        <div class="stat-label">Total</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number level-critical" id="stat-critiques">0</div>
                        <div class="stat-label">Critiques</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number level-error" id="stat-erreurs">0</div>
                        <div class="stat-label">Erreurs</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number level-warning" id="stat-warnings">0</div>
                        <div class="stat-label">Warnings</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number level-info" id="stat-info">0</div>
                        <div class="stat-label">Info</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="stat-non-resolues">0</div>
                        <div class="stat-label">Non résolues</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📈 Graphique des Alertes</h3>
                <div class="chart-container">
                    <canvas id="alertes-chart"></canvas>
                </div>
            </div>

            <div class="card">
                <h3>⚙️ Contrôles</h3>
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <button class="btn btn-success" onclick="startMonitoring()">▶️ Démarrer Monitoring</button>
                    <button class="btn btn-warning" onclick="stopMonitoring()">⏹️ Arrêter Monitoring</button>
                    <button class="btn btn-primary" onclick="testAlerte()">🧪 Alerte de Test</button>
                    <button class="btn btn-primary" onclick="refreshData()">🔄 Actualiser</button>
                </div>
            </div>
        </div>

        <!-- Contrôles des alertes -->
        <div class="card">
            <h3>🔍 Filtres des Alertes</h3>
            <div class="controls">
                <div class="form-group">
                    <label for="niveau-filter">Niveau:</label>
                    <select id="niveau-filter" onchange="filterAlertes()">
                        <option value="">Tous</option>
                        <option value="CRITICAL">Critique</option>
                        <option value="ERROR">Erreur</option>
                        <option value="WARNING">Warning</option>
                        <option value="INFO">Info</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="resolu-filter">État:</label>
                    <select id="resolu-filter" onchange="filterAlertes()">
                        <option value="">Tous</option>
                        <option value="false">Non résolues</option>
                        <option value="true">Résolues</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="limite-filter">Limite:</label>
                    <select id="limite-filter" onchange="filterAlertes()">
                        <option value="20">20</option>
                        <option value="50">50</option>
                        <option value="100">100</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Table des alertes -->
        <div class="card">
            <h3>📋 Alertes Récentes</h3>
            <div style="overflow-x: auto;">
                <table class="alertes-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Niveau</th>
                            <th>Source</th>
                            <th>Message</th>
                            <th>État</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="alertes-tbody">
                        <!-- Les alertes seront insérées ici par JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Notification toast -->
    <div id="notification" class="notification"></div>

    <script>
        // Connexion WebSocket
        const socket = io();
        let chart = null;

        // État de connexion
        socket.on('connect', function() {
            document.getElementById('connection-status').innerHTML = '🟢 Connecté';
            document.getElementById('connection-status').className = 'status-indicator status-online';
            updateLastUpdate();
        });

        socket.on('disconnect', function() {
            document.getElementById('connection-status').innerHTML = '🔴 Déconnecté';
            document.getElementById('connection-status').className = 'status-indicator status-offline';
        });

        // Mise à jour des statistiques
        socket.on('stats_update', function(stats) {
            updateStats(stats);
            updateLastUpdate();
        });

        // Nouvelle alerte
        socket.on('nouvelle_alerte', function(alerte) {  
            showNotification(`Nouvelle alerte ${alerte.niveau}: ${alerte.message}`, getNotificationClass(alerte.niveau));
            loadAlertes(); // Recharger la liste
        });

        // Alerte résolue
        socket.on('alerte_resolue', function(data) {
            showNotification('Alerte marquée comme résolue', 'success');
            loadAlertes(); // Recharger la liste
        });

        // Fonctions utilitaires
        function updateStats(stats) {
            const globales = stats.globales;
            document.getElementById('stat-total').textContent = globales.total;
            document.getElementById('stat-critiques').textContent = globales.critiques;
            document.getElementById('stat-erreurs').textContent = globales.erreurs;
            document.getElementById('stat-warnings').textContent = globales.warnings;
            document.getElementById('stat-info').textContent = globales.info;
            document.getElementById('stat-non-resolues').textContent = globales.non_resolues;

            // Mettre à jour le graphique
            updateChart(stats);
        }

        function updateChart(stats) {
            const ctx = document.getElementById('alertes-chart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }

            const labels = stats.journalieres.map(d => d.date).reverse();
            const critiques = stats.journalieres.map(d => d.critiques).reverse();
            const erreurs = stats.journalieres.map(d => d.erreurs).reverse();
            const warnings = stats.journalieres.map(d => d.warnings).reverse();
            const info = stats.journalieres.map(d => d.info).reverse();

            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Critiques',
                            data: critiques,
                            borderColor: '#8e44ad',
                            backgroundColor: 'rgba(142, 68, 173, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Erreurs',
                            data: erreurs,
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Warnings',
                            data: warnings,
                            borderColor: '#f39c12',
                            backgroundColor: 'rgba(243, 156, 18, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Info',
                            data: info,
                            borderColor: '#27ae60',
                            backgroundColor: 'rgba(39, 174, 96, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        function loadAlertes() {
            const niveau = document.getElementById('niveau-filter').value;
            const resolu = document.getElementById('resolu-filter').value;
            const limite = parseInt(document.getElementById('limite-filter').value);

            const params = new URLSearchParams();
            if (niveau) params.append('niveau', niveau);
            if (resolu) params.append('resolu', resolu);
            params.append('limite', limite);

            fetch(`/api/alertes?${params}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateAlertesTable(data.alertes);
                    } else {
                        showNotification('Erreur: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    showNotification('Erreur de chargement: ' + error.message, 'error');
                });
        }

        function updateAlertesTable(alertes) {
            const tbody = document.getElementById('alertes-tbody');
            tbody.innerHTML = '';

            alertes.forEach(alerte => {
                const row = document.createElement('tr');
                
                const timestamp = new Date(alerte.timestamp).toLocaleString('fr-FR');
                const niveau = alerte.niveau.toLowerCase();
                const resolu = alerte.resolu ? '✅' : '❌';
                
                row.innerHTML = `
                    <td>${timestamp}</td>
                    <td><span class="level-badge ${niveau}">${alerte.niveau}</span></td>
                    <td>${alerte.source}</td>
                    <td title="${alerte.message}">${alerte.message.length > 50 ? alerte.message.substr(0, 50) + '...' : alerte.message}</td>
                    <td>${resolu}</td>
                    <td>
                        ${!alerte.resolu ? `<button class="btn btn-success btn-small" onclick="resolveAlerte('${alerte.id}')">Résoudre</button>` : ''}
                        <button class="btn btn-primary btn-small" onclick="showDetails('${alerte.id}')">Détails</button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }

        function filterAlertes() {
            loadAlertes();
        }

        function resolveAlerte(alerteId) {
            fetch(`/api/alertes/${alerteId}/resolve`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Alerte résolue', 'success');
                    loadAlertes();
                } else {
                    showNotification('Erreur: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showNotification('Erreur: ' + error.message, 'error');
            });
        }

        function showDetails(alerteId) {
            // Trouver l'alerte dans les données actuelles
            fetch(`/api/alertes?limite=1000`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const alerte = data.alertes.find(a => a.id === alerteId);
                        if (alerte) {
                            alert(`Détails de l'alerte:

ID: ${alerte.id}
Timestamp: ${new Date(alerte.timestamp).toLocaleString('fr-FR')}
Niveau: ${alerte.niveau}
Source: ${alerte.source}
Message: ${alerte.message}
Résolu: ${alerte.resolu ? 'Oui' : 'Non'}

Détails:
${JSON.stringify(alerte.details, null, 2)}`);
                        }
                    }
                });
        }

        function startMonitoring() {
            fetch('/api/monitoring/start', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Monitoring démarré', 'success');
                } else {
                    showNotification('Erreur: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showNotification('Erreur: ' + error.message, 'error');
            });
        }

        function stopMonitoring() {
            fetch('/api/monitoring/stop', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Monitoring arrêté', 'warning');
                } else {
                    showNotification('Erreur: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showNotification('Erreur: ' + error.message, 'error');
            });
        }

        function testAlerte() {
            const niveau = prompt('Niveau de l\'alerte (INFO, WARNING, ERROR, CRITICAL):', 'WARNING');
            if (!niveau) return;
            
            const message = prompt('Message de l\'alerte:', 'Test d\'alerte depuis le dashboard');
            if (!message) return;

            fetch('/api/test-alerte', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    niveau: niveau.toUpperCase(),
                    message: message,
                    details: {
                        source: 'dashboard',
                        user_initiated: true
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Alerte de test créée', 'success');
                } else {
                    showNotification('Erreur: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showNotification('Erreur: ' + error.message, 'error');
            });
        }

        function refreshData() {
            loadAlertes();
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStats(data.stats);
                        showNotification('Données actualisées', 'success');
                    }
                })
                .catch(error => {
                    showNotification('Erreur: ' + error.message, 'error');
                });
        }

        function showNotification(message, type) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 4000);
        }

        function getNotificationClass(niveau) {
            switch(niveau) {
                case 'CRITICAL': return 'error';
                case 'ERROR': return 'error';
                case 'WARNING': return 'warning';
                case 'INFO': return 'success';
                default: return 'success';
            }
        }

        function updateLastUpdate() {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString('fr-FR');
        }

        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            loadAlertes();
            refreshData();
        });
    </script>
</body>
</html>"""
    
    with open(os.path.join(template_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

def main():
    """Point d'entrée principal pour l'application web"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interface Web - Système d'Alertes Sécurité")
    parser.add_argument("--config", default="config.json", help="Fichier de configuration")
    parser.add_argument("--db", default="alertes.db", help="Base de données SQLite")
    parser.add_argument("--port", type=int, default=5000, help="Port du serveur web")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse d'écoute")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    
    args = parser.parse_args()
    
    print(f"🌐 Interface Web - Système d'Alertes Sécurité")
    print("=" * 50)
    
    # Initialiser le système d'alertes
    init_systeme_alertes(db_path=args.db, config_path=args.config)
    
    # Créer le template si nécessaire
    create_dashboard_template()
    
    print(f"🚀 Démarrage du serveur web...")
    print(f"📡 URL: http://{args.host}:{args.port}")
    print(f"🔧 Configuration: {args.config}")
    print(f"💾 Base de données: {args.db}")
    
    # Lancer l'application Flask avec Socket.IO
    socketio.run(
        app,
        host=args.host,
        port=args.port,
        debug=args.debug,
        allow_unsafe_werkzeug=True
    )

if __name__ == "__main__":
    main()