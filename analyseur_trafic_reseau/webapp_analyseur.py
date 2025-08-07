#!/usr/bin/env python3
"""
Interface Web pour l'Analyseur de Trafic Réseau
Dashboard moderne avec Flask et temps réel via WebSockets
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import threading
import time
import json
import os
from datetime import datetime
from analyseur_trafic import AnalyseurTrafic

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'analyseur_trafic_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales
analyseur = None
is_capturing = False
capture_thread = None
clients_connected = []

@app.route('/')
def index():
    """Page principale du dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API pour obtenir le statut actuel"""
    global analyseur, is_capturing
    
    if not analyseur:
        return jsonify({
            'status': 'not_initialized',
            'packets': 0,
            'bytes': 0,
            'anomalies': 0,
            'capturing': False
        })
    
    packets_count = len(analyseur.packets) if analyseur.packets else 0
    total_bytes = sum(p.get('length', 0) for p in analyseur.packets) if analyseur.packets else 0
    anomalies_count = len(analyseur.anomalies) if hasattr(analyseur, 'anomalies') and analyseur.anomalies else 0
    
    return jsonify({
        'status': 'ready',
        'packets': packets_count,
        'bytes': total_bytes,
        'anomalies': anomalies_count,
        'capturing': is_capturing
    })

@app.route('/api/start', methods=['POST'])
def api_start_capture():
    """API pour démarrer la capture"""
    global analyseur, is_capturing, capture_thread
    
    if is_capturing:
        return jsonify({'success': False, 'message': 'Capture déjà en cours'})
    
    try:
        # Paramètres
        data = request.get_json() or {}
        interface = data.get('interface', 'eth0')
        duration = int(data.get('duration', 60))
        max_packets = int(data.get('max_packets', 1000))
        production_mode = data.get('production_mode', True)
        
        # Initialiser l'analyseur
        analyseur = AnalyseurTrafic(interface=interface)
        is_capturing = True
        
        # Démarrer le thread de capture
        capture_thread = threading.Thread(
            target=capture_worker,
            args=(duration, max_packets, production_mode),
            daemon=True
        )
        capture_thread.start()
        
        # Notifier les clients
        socketio.emit('capture_started', {
            'interface': interface,
            'duration': duration,
            'max_packets': max_packets,
            'production_mode': production_mode
        })
        
        return jsonify({'success': True, 'message': 'Capture démarrée'})
        
    except Exception as e:
        is_capturing = False
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
def api_stop_capture():
    """API pour arrêter la capture"""
    global is_capturing
    
    if not is_capturing:
        return jsonify({'success': False, 'message': 'Aucune capture en cours'})
    
    is_capturing = False
    socketio.emit('capture_stopped', {'message': 'Capture arrêtée'})
    
    return jsonify({'success': True, 'message': 'Capture arrêtée'})

@app.route('/api/data')
def api_get_data():
    """API pour obtenir les données de capture"""
    global analyseur
    
    if not analyseur or not analyseur.packets:
        return jsonify({'packets': [], 'statistics': {}, 'anomalies': []})
    
    try:
        # Derniers paquets (limiter pour les performances)
        recent_packets = analyseur.packets[-500:]
        packets_data = []
        
        for packet in recent_packets:
            packets_data.append({
                'timestamp': packet.get('timestamp').isoformat() if packet.get('timestamp') else '',
                'protocol': packet.get('protocol', ''),
                'src_ip': packet.get('src_ip', ''),
                'dst_ip': packet.get('dst_ip', ''),
                'src_port': packet.get('src_port', ''),
                'dst_port': packet.get('dst_port', ''),
                'length': packet.get('length', 0)
            })
        
        # Statistiques pour les graphiques
        protocol_stats = dict(analyseur.protocol_stats) if hasattr(analyseur, 'protocol_stats') else {}
        ip_stats = dict(analyseur.ip_stats.most_common(10)) if hasattr(analyseur, 'ip_stats') else {}
        port_stats = dict(analyseur.port_stats.most_common(10)) if hasattr(analyseur, 'port_stats') else {}
        
        # Anomalies
        anomalies_data = []
        if hasattr(analyseur, 'anomalies') and analyseur.anomalies:
            for anomaly in analyseur.anomalies:
                anomalies_data.append({
                    'timestamp': anomaly.get('timestamp').isoformat() if anomaly.get('timestamp') else '',
                    'type': anomaly.get('type', ''),
                    'source_ip': anomaly.get('source_ip', ''),
                    'details': anomaly.get('details', '')
                })
        
        return jsonify({
            'packets': packets_data,
            'statistics': {
                'protocols': protocol_stats,
                'top_ips': ip_stats,
                'top_ports': port_stats
            },
            'anomalies': anomalies_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur récupération données: {str(e)}'})

@app.route('/api/export/<format>')
def api_export_data(format):
    """API pour exporter les données"""
    global analyseur
    
    if not analyseur or not analyseur.packets:
        return jsonify({'success': False, 'message': 'Aucune donnée à exporter'})
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"traffic_capture_{timestamp}.{format}"
        
        exported_file = analyseur.export_data(format_type=format, filename=filename)
        
        if exported_file and os.path.exists(exported_file):
            return send_file(exported_file, as_attachment=True)
        else:
            return jsonify({'success': False, 'message': 'Erreur lors de l\'export'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur export: {str(e)}'})

def capture_worker(duration, max_packets, production_mode):
    """Worker thread pour la capture"""
    global analyseur, is_capturing
    
    try:
        start_time = time.time()
        
        if not production_mode:
            socketio.emit('log_message', {'message': '🎯 Mode test activé', 'level': 'info'})
            # Utiliser la capture normale en mode test
            success = analyseur.start_capture(duration=10, packet_count=100)  # Paramètres de test
        else:
            socketio.emit('log_message', {'message': f'🎯 Démarrage capture sur {analyseur.interface}', 'level': 'info'})
            success = analyseur.start_capture(duration=duration, packet_count=max_packets)
            if not success:
                socketio.emit('log_message', {'message': '❌ Échec de la capture', 'level': 'error'})
                is_capturing = False
                return
        
        # Émissions périodiques des statistiques pendant la capture
        update_thread = threading.Thread(target=stats_updater, args=(start_time, duration), daemon=True)
        update_thread.start()
        
        # Attendre la fin
        if not production_mode:
            time.sleep(2)  # Simulation courte pour les tests
        
        packets_count = len(analyseur.packets) if analyseur.packets else 0
        socketio.emit('log_message', {
            'message': f'✓ Capture terminée - {packets_count} paquets capturés',
            'level': 'success'
        })
        
        socketio.emit('capture_finished', {'packets': packets_count})
        
    except Exception as e:
        socketio.emit('log_message', {'message': f'❌ Erreur capture: {str(e)}', 'level': 'error'})
    finally:
        is_capturing = False

def stats_updater(start_time, duration):
    """Mise à jour des statistiques en temps réel"""
    global analyseur, is_capturing
    
    while is_capturing:
        try:
            if analyseur and hasattr(analyseur, 'packets'):
                elapsed = time.time() - start_time
                progress = min((elapsed / duration) * 100, 100)
                
                packets_count = len(analyseur.packets)
                total_bytes = sum(p.get('length', 0) for p in analyseur.packets)
                anomalies_count = len(analyseur.anomalies) if hasattr(analyseur, 'anomalies') else 0
                
                socketio.emit('stats_update', {
                    'packets': packets_count,
                    'bytes': total_bytes,
                    'anomalies': anomalies_count,
                    'progress': progress,
                    'elapsed': int(elapsed)
                })
            
            time.sleep(1)
            
        except Exception as e:
            socketio.emit('log_message', {'message': f'❌ Erreur stats: {str(e)}', 'level': 'error'})
            break

@socketio.on('connect')
def handle_connect():
    """Nouveau client connecté"""
    clients_connected.append(request.sid)
    emit('connected', {'message': 'Connecté au serveur'})
    print(f"✓ Client connecté: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Client déconnecté"""
    if request.sid in clients_connected:
        clients_connected.remove(request.sid)
    print(f"✓ Client déconnecté: {request.sid}")

# Template HTML intégré
def create_template():
    """Créer le template HTML si nécessaire"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    template_path = os.path.join(templates_dir, 'dashboard.html')
    
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(get_dashboard_template())

def get_dashboard_template():
    """Template HTML du dashboard"""
    return '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 Analyseur de Trafic Réseau</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; color: #333; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 2fr 1fr; gap: 20px; margin-bottom: 20px; }
        .panel { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .control-panel { display: flex; flex-direction: column; gap: 15px; }
        .form-group { display: flex; flex-direction: column; gap: 5px; }
        .form-group label { font-weight: bold; color: #555; }
        .form-group input, .form-group select { padding: 8px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-danger:hover { background: #c0392b; }
        .btn-success { background: #27ae60; color: white; }
        .btn-success:hover { background: #219a52; }
        .btn:disabled { background: #bdc3c7; cursor: not-allowed; }
        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .stat-card { background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 0.9em; }
        .progress-bar { width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #3498db, #2ecc71); transition: width 0.3s; }
        .charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }
        .chart-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .logs-panel { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); height: 400px; }
        .logs-content { height: 320px; overflow-y: auto; background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.9em; }
        .log-entry { margin-bottom: 5px; }
        .log-info { color: #3498db; }
        .log-success { color: #27ae60; }
        .log-error { color: #e74c3c; }
        .log-warning { color: #f39c12; }
        .table-container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .anomaly-row { background: #ffebee; }
        .status { padding: 5px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }
        .status-ready { background: #d4edda; color: #155724; }
        .status-capturing { background: #fff3cd; color: #856404; }
        .status-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Analyseur de Trafic Réseau</h1>
            <div class="status" id="connectionStatus">Connexion...</div>
        </div>

        <div class="grid">
            <!-- Panel de contrôle -->
            <div class="panel">
                <h3>⚙️ Configuration</h3>
                <div class="control-panel">
                    <div class="form-group">
                        <label>Interface réseau:</label>
                        <select id="interface">
                            <option value="eth0">eth0</option>
                            <option value="wlan0">wlan0</option>
                            <option value="lo">lo</option>
                            <option value="any">any</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Durée (secondes):</label>
                        <input type="number" id="duration" value="60" min="10" max="3600">
                    </div>
                    <div class="form-group">
                        <label>Max paquets:</label>
                        <input type="number" id="maxPackets" value="1000" min="100" max="10000">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="productionMode" checked> Mode production
                        </label>
                    </div>
                    <button class="btn btn-primary" id="startBtn" onclick="startCapture()">▶️ Démarrer</button>
                    <button class="btn btn-danger" id="stopBtn" onclick="stopCapture()" disabled>⏹️ Arrêter</button>
                    <button class="btn btn-success" onclick="exportData('json')">💾 Export JSON</button>
                    <button class="btn btn-success" onclick="exportData('csv')">📊 Export CSV</button>
                </div>
            </div>

            <!-- Statistiques -->
            <div class="panel">
                <h3>📊 Statistiques Temps Réel</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressBar" style="width: 0%"></div>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="packetsCount">0</div>
                        <div class="stat-label">Paquets</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="bytesCount">0</div>
                        <div class="stat-label">Bytes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="elapsedTime">0s</div>
                        <div class="stat-label">Durée</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="anomaliesCount">0</div>
                        <div class="stat-label">Anomalies</div>
                    </div>
                </div>
            </div>

            <!-- Logs -->
            <div class="panel">
                <h3>📝 Logs</h3>
                <div class="logs-content" id="logsContent"></div>
                <button class="btn" onclick="clearLogs()" style="margin-top: 10px;">🗑️ Vider</button>
            </div>
        </div>

        <!-- Graphiques -->
        <div class="charts-grid">
            <div class="chart-container">
                <h4>Protocoles</h4>
                <canvas id="protocolChart"></canvas>
            </div>
            <div class="chart-container">
                <h4>Top IPs Sources</h4>
                <canvas id="ipsChart"></canvas>
            </div>
            <div class="chart-container">
                <h4>Top Ports</h4>
                <canvas id="portsChart"></canvas>
            </div>
            <div class="chart-container">
                <h4>Évolution Temporelle</h4>
                <canvas id="timeChart"></canvas>
            </div>
        </div>

        <!-- Tableaux de données -->
        <div class="table-container">
            <h3>📋 Paquets Capturés</h3>
            <div style="max-height: 300px; overflow-y: auto;">
                <table id="packetsTable">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Protocole</th>
                            <th>IP Source</th>
                            <th>IP Dest</th>
                            <th>Port Source</th>
                            <th>Port Dest</th>
                            <th>Taille</th>
                        </tr>
                    </thead>
                    <tbody id="packetsTableBody"></tbody>
                </table>
            </div>
        </div>

        <div class="table-container">
            <h3>🚨 Anomalies Détectées</h3>
            <div style="max-height: 200px; overflow-y: auto;">
                <table id="anomaliesTable">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Type</th>
                            <th>IP Source</th>
                            <th>Détails</th>
                        </tr>
                    </thead>
                    <tbody id="anomaliesTableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection
        const socket = io();
        
        // Charts variables
        let protocolChart, ipsChart, portsChart, timeChart;
        
        // Connection handlers
        socket.on('connect', function() {
            document.getElementById('connectionStatus').textContent = 'Connecté';
            document.getElementById('connectionStatus').className = 'status status-ready';
            addLog('✓ Connecté au serveur', 'success');
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').textContent = 'Déconnecté';
            document.getElementById('connectionStatus').className = 'status status-error';
            addLog('❌ Connexion perdue', 'error');
        });
        
        // Capture events
        socket.on('capture_started', function(data) {
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            addLog('🎯 Capture démarrée', 'info');
        });
        
        socket.on('capture_stopped', function(data) {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            addLog('⏹️ Capture arrêtée', 'warning');
        });
        
        socket.on('capture_finished', function(data) {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            addLog('✅ Capture terminée - ' + data.packets + ' paquets', 'success');
            updateData();
        });
        
        // Stats updates
        socket.on('stats_update', function(data) {
            updateStats(data);
        });
        
        // Log messages
        socket.on('log_message', function(data) {
            addLog(data.message, data.level);
        });
        
        // Functions
        function startCapture() {
            const data = {
                interface: document.getElementById('interface').value,
                duration: parseInt(document.getElementById('duration').value),
                max_packets: parseInt(document.getElementById('maxPackets').value),
                production_mode: document.getElementById('productionMode').checked
            };
            
            fetch('/api/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    addLog('❌ ' + data.message, 'error');
                }
            });
        }
        
        function stopCapture() {
            fetch('/api/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    addLog('❌ ' + data.message, 'error');
                }
            });
        }
        
        function exportData(format) {
            window.open('/api/export/' + format, '_blank');
        }
        
        function updateStats(data) {
            document.getElementById('packetsCount').textContent = data.packets.toLocaleString();
            document.getElementById('bytesCount').textContent = data.bytes.toLocaleString();
            document.getElementById('elapsedTime').textContent = data.elapsed + 's';
            document.getElementById('anomaliesCount').textContent = data.anomalies;
            document.getElementById('progressBar').style.width = data.progress + '%';
        }
        
        function updateData() {
            fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                updateCharts(data.statistics);
                updatePacketsTable(data.packets);
                updateAnomaliesTable(data.anomalies);
            });
        }
        
        function updateCharts(stats) {
            // Protocol chart
            if (protocolChart) protocolChart.destroy();
            const protocolCtx = document.getElementById('protocolChart').getContext('2d');
            protocolChart = new Chart(protocolCtx, {
                type: 'pie',
                data: {
                    labels: Object.keys(stats.protocols || {}),
                    datasets: [{
                        data: Object.values(stats.protocols || {}),
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
            // IPs chart
            if (ipsChart) ipsChart.destroy();
            const ipsCtx = document.getElementById('ipsChart').getContext('2d');
            ipsChart = new Chart(ipsCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(stats.top_ips || {}),
                    datasets: [{
                        label: 'Paquets',
                        data: Object.values(stats.top_ips || {}),
                        backgroundColor: '#36A2EB'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
            // Ports chart
            if (portsChart) portsChart.destroy();
            const portsCtx = document.getElementById('portsChart').getContext('2d');
            portsChart = new Chart(portsCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(stats.top_ports || {}),
                    datasets: [{
                        label: 'Paquets',
                        data: Object.values(stats.top_ports || {}),
                        backgroundColor: '#4BC0C0'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        function updatePacketsTable(packets) {
            const tbody = document.getElementById('packetsTableBody');
            tbody.innerHTML = '';
            
            packets.slice(-50).forEach(packet => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = new Date(packet.timestamp).toLocaleTimeString();
                row.insertCell(1).textContent = packet.protocol;
                row.insertCell(2).textContent = packet.src_ip || '';
                row.insertCell(3).textContent = packet.dst_ip || '';
                row.insertCell(4).textContent = packet.src_port || '';
                row.insertCell(5).textContent = packet.dst_port || '';
                row.insertCell(6).textContent = packet.length;
            });
        }
        
        function updateAnomaliesTable(anomalies) {
            const tbody = document.getElementById('anomaliesTableBody');
            tbody.innerHTML = '';
            
            anomalies.forEach(anomaly => {
                const row = tbody.insertRow();
                row.className = 'anomaly-row';
                row.insertCell(0).textContent = new Date(anomaly.timestamp).toLocaleTimeString();
                row.insertCell(1).textContent = anomaly.type;
                row.insertCell(2).textContent = anomaly.source_ip;
                row.insertCell(3).textContent = anomaly.details;
            });
        }
        
        function addLog(message, level) {
            const logsContent = document.getElementById('logsContent');
            const timestamp = new Date().toLocaleTimeString();
            const logClass = 'log-' + (level || 'info');
            
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry ' + logClass;
            logEntry.textContent = '[' + timestamp + '] ' + message;
            
            logsContent.appendChild(logEntry);
            logsContent.scrollTop = logsContent.scrollHeight;
            
            // Limiter le nombre de logs
            while (logsContent.children.length > 100) {
                logsContent.removeChild(logsContent.firstChild);
            }
        }
        
        function clearLogs() {
            document.getElementById('logsContent').innerHTML = '';
        }
        
        // Initial load
        document.addEventListener('DOMContentLoaded', function() {
            updateData();
            setInterval(updateData, 5000); // Refresh every 5 seconds
        });
    </script>
</body>
</html>'''

def main():
    """Fonction principale"""
    print("🌐 Démarrage de l'interface web...")
    print("📍 Interface disponible sur: http://localhost:5000")
    
    # Créer le template avant le premier démarrage
    create_template()
    
    # Démarrer l'application
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()