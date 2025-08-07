# Scanner de Vulnérabilités Web 🕷️

## Description

Scanner automatisé de vulnérabilités web conçu pour détecter les failles de sécurité communes dans les applications web. Outil professionnel pour l'audit de sécurité et les tests de pénétration.

## Fonctionnalités

### 🔍 Détection de Vulnérabilités
- **XSS (Cross-Site Scripting)** - Reflected & Stored
- **Injection SQL** - Tests avec payloads multiples
- **CSRF (Cross-Site Request Forgery)** - Détection absence de tokens
- **Fichiers sensibles** - Recherche de fichiers exposés (.env, config, admin)
- **En-têtes de sécurité manquants** - Vérification complète des headers

### 🔧 Détection de Technologies
- **Serveurs web** - Apache, Nginx, IIS
- **Frameworks** - WordPress, Drupal, Django, Flask, React, Angular
- **Langages** - PHP, ASP.NET, Python, Node.js
- **CMS & Plateformes** - Shopify, Magento, PrestaShop
- **Bibliothèques** - jQuery, Bootstrap, etc.
- **CDN & Services** - Cloudflare, etc.

### 🛡️ Analyse de Sécurité
- **SSL/TLS** - Vérification certificats et configuration
- **En-têtes HTTP** - HSTS, CSP, X-Frame-Options, etc.
- **Score de sécurité** - Évaluation globale sur 100 points
- **Analyse des formulaires** - Détection et tests automatisés

### 📊 Rapports & Stockage
- **Rapports HTML** - Interface moderne et détaillée
- **Base SQLite** - Stockage persistant des résultats
- **Statistiques** - Analyses temporelles et tendances
- **API CLI** - Interface en ligne de commande complète

### ⚡ Performance & Scalabilité
- **Scan parallèle** - Support multi-threading
- **Batch processing** - Scan de multiples URLs
- **Timeout configurable** - Optimisation des performances
- **Cache intelligent** - Évite les requêtes redondantes

## Installation

### Prérequis Système
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip sqlite3 libxml2-dev libxslt-dev

# CentOS/RHEL
sudo yum install python3-devel python3-pip sqlite3 libxml2-devel libxslt-devel
```

### Installation des Dépendances
```bash
pip install -r requirements.txt
```

### Dépendances Principales
- **requests 2.31.0** - Client HTTP avancé
- **beautifulsoup4 4.12.2** - Parser HTML/XML
- **urllib3 2.0.7** - Bibliothèque HTTP bas niveau
- **lxml 4.9.3** - Parser XML/HTML rapide
- **colorama 0.4.6** - Couleurs terminal
- **tabulate 0.9.0** - Formatage tableaux
- **Pillow 10.1.0** - Traitement d'images
- **Jinja2 3.1.6** - Templates
- **markdown 3.5.1** - Génération markdown

## Utilisation

### 🚀 Démarrage Rapide

#### Scanner une URL simple
```bash
# Scan basique avec rapport HTML
python3 scanner_vulnerabilites.py scan https://example.com

# Scan sans génération de rapport
python3 scanner_vulnerabilites.py scan https://example.com --no-report

# Scan avec timeout personnalisé
python3 scanner_vulnerabilites.py scan https://example.com --timeout 15
```

#### Scanner plusieurs URLs
```bash
# Créer un fichier urls.txt avec une URL par ligne
echo "https://site1.com" > urls.txt
echo "https://site2.com" >> urls.txt
echo "https://site3.com" >> urls.txt

# Lancer le scan multiple
python3 scanner_vulnerabilites.py multiple urls.txt

# Avec nombre de workers personnalisé
python3 scanner_vulnerabilites.py multiple urls.txt --workers 5
```

#### Gestion des résultats
```bash
# Afficher les statistiques
python3 scanner_vulnerabilites.py stats

# Lister les derniers scans
python3 scanner_vulnerabilites.py list

# Lister avec limite personnalisée
python3 scanner_vulnerabilites.py list --limit 20
```

### 📋 Interface en Ligne de Commande

#### Commandes Principales
```bash
# Scanner une URL
python3 scanner_vulnerabilites.py scan [URL]

# Scanner multiple URLs
python3 scanner_vulnerabilites.py multiple [FICHIER]

# Afficher statistiques
python3 scanner_vulnerabilites.py stats

# Lister les scans
python3 scanner_vulnerabilites.py list
```

#### Options Avancées
```bash
# Options du scan simple
--no-report          # Ne pas générer de rapport HTML
--timeout [SECONDS]  # Timeout des requêtes (défaut: 10s)

# Options du scan multiple  
--workers [NUMBER]   # Nombre de workers parallèles (défaut: 3)

# Options de listage
--limit [NUMBER]     # Nombre de résultats à afficher (défaut: 10)
```

### 🐍 Utilisation Programmatique

#### Scanner Simple
```python
from scanner_vulnerabilites import WebVulnScanner

# Initialiser le scanner
scanner = WebVulnScanner()

# Scanner une URL
resultat = scanner.scanner_url('https://example.com')

# Accéder aux résultats
print(f"Score de sécurité: {resultat.score_securite}/100")
print(f"Vulnérabilités: {len(resultat.vulnerabilites)}")
print(f"Technologies: {', '.join(resultat.technologies)}")

# Parcourir les vulnérabilités
for vuln in resultat.vulnerabilites:
    print(f"- {vuln.severite}: {vuln.description}")
```

#### Scanner Avancé
```python
from scanner_vulnerabilites import VulnerabilityScanner, DatabaseManager

# Configuration personnalisée
scanner = VulnerabilityScanner(timeout=15, user_agent="MonScanner/1.0")

# Scanner avec base de données personnalisée
db_manager = DatabaseManager("mes_scans.db")

# Effectuer le scan
resultat = scanner.scan_url('https://target.com')

# Sauvegarder
scan_id = db_manager.sauvegarder_scan(resultat)
print(f"Scan sauvegardé avec l'ID: {scan_id}")
```

#### Composants Individuels
```python
# Détecteur de technologies uniquement
from scanner_vulnerabilites import TechnologyDetector
import requests
from bs4 import BeautifulSoup

detector = TechnologyDetector()
response = requests.get('https://example.com')
soup = BeautifulSoup(response.content, 'html.parser')
technologies = detector.detecter_technologies(response, soup)

# Vérificateur d'en-têtes de sécurité
from scanner_vulnerabilites import SecurityHeadersChecker

checker = SecurityHeadersChecker()
headers_results = checker.verifier_headers(response.headers)

# Analyseur SSL
from scanner_vulnerabilites import SSLAnalyzer

ssl_analyzer = SSLAnalyzer()
ssl_results = ssl_analyzer.analyser_ssl('example.com')
```

## Structure des Données

### Modèle de Vulnérabilité
```python
@dataclass
class VulnerabiliteDetectee:
    id: str                    # Identifiant unique
    url: str                   # URL où la vulnérabilité a été trouvée
    type_vuln: str            # Type: XSS, SQL_INJECTION, HEADER_MISSING, etc.
    severite: str             # LOW, MEDIUM, HIGH, CRITICAL
    description: str          # Description détaillée
    details: Dict[str, Any]   # Détails techniques (JSON)
    remediation: str          # Instructions de correction
    timestamp: datetime       # Moment de la détection
    confirmed: bool           # Vulnérabilité confirmée
```

### Modèle de Résultat
```python
@dataclass
class ResultatScan:
    url: str                          # URL scannée
    timestamp: datetime               # Moment du scan
    duree_scan: float                # Durée en secondes
    status_code: int                 # Code de réponse HTTP
    technologies: List[str]          # Technologies détectées
    vulnerabilites: List[VulnerabiliteDetectee]
    en_tetes_securite: Dict[str, bool] # État des en-têtes
    formulaires_detectes: int        # Nombre de formulaires
    certificat_ssl: Dict[str, Any]   # Info SSL/TLS
    score_securite: int              # Score sur 100
```

## Types de Vulnérabilités Détectées

### 🚨 XSS (Cross-Site Scripting)
```python
# Payloads testés
payloads_xss = [
    '<script>alert("XSS")</script>',
    '"><script>alert("XSS")</script>',
    "javascript:alert('XSS')",
    '<img src=x onerror=alert("XSS")>',
    '<svg onload=alert("XSS")>',
    "';alert('XSS');//",
    '<iframe src="javascript:alert(\'XSS\')"></iframe>'
]

# Détection
# - XSS Reflected: Payload reflété dans la réponse
# - Tests sur formulaires GET/POST
# - Tests sur paramètres URL
```

### 💉 Injection SQL
```python
# Payloads testés
payloads_sql = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' UNION SELECT NULL--",
    "'; DROP TABLE users--",
    "' OR 'a'='a",
    "admin'--",
    "' OR 1=1#",
    "') OR ('1'='1"
]

# Détection par erreurs SQL
sql_errors = [
    'mysql_fetch_array()', 'ORA-01756', 'Microsoft OLE DB Provider',
    'mysql_fetch_assoc()', 'pg_query()', 'sqlite_query()',
    'SQL syntax', 'MySQL server version', 'Warning: mysql_'
]
```

### 🛡️ En-têtes de Sécurité
```python
headers_securite = {
    'Strict-Transport-Security': 'Force HTTPS (MEDIUM)',
    'Content-Security-Policy': 'Prévention XSS (HIGH)',
    'X-Content-Type-Options': 'Anti MIME-sniffing (MEDIUM)',
    'X-Frame-Options': 'Anti clickjacking (MEDIUM)',
    'X-XSS-Protection': 'Protection XSS navigateur (LOW)',
    'Referrer-Policy': 'Contrôle référent (LOW)',
    'Feature-Policy': 'Contrôle fonctionnalités (LOW)'
}
```

### 📁 Fichiers Sensibles
```python
fichiers_sensibles = [
    '/robots.txt', '/.htaccess', '/web.config',
    '/admin', '/admin.php', '/administrator',
    '/phpmyadmin', '/mysql', '/database',
    '/.env', '/config.php', '/config.json',
    '/backup.sql', '/dump.sql', '/.git/config',
    '/server-status', '/server-info'
]
```

## Calcul du Score de Sécurité

### Algorithme de Scoring
```python
def calculer_score_securite(headers_manquants, vulnerabilites):
    score = 100
    
    # Pénalités pour en-têtes manquants
    score -= headers_manquants * 5
    
    # Pénalités pour vulnérabilités
    for vuln in vulnerabilites:
        if vuln.severite == 'CRITICAL':
            score -= 25
        elif vuln.severite == 'HIGH':
            score -= 15
        elif vuln.severite == 'MEDIUM':
            score -= 10
        elif vuln.severite == 'LOW':
            score -= 5
    
    return max(0, score)  # Score minimum: 0
```

### Interprétation des Scores
- **90-100**: Excellente sécurité
- **80-89**: Bonne sécurité
- **60-79**: Sécurité moyenne
- **40-59**: Sécurité faible
- **0-39**: Sécurité critique

## Rapports HTML

### Fonctionnalités des Rapports
- **Design responsive** - Compatible mobile/desktop
- **Visualisations interactives** - Graphiques et statistiques
- **Code couleur** - Sévérités différenciées
- **Détails techniques** - Payloads et preuves
- **Recommandations** - Instructions de correction
- **Export facile** - Format HTML standard

### Structure du Rapport
```html
<!DOCTYPE html>
<html>
<head>
    <title>Rapport de Sécurité - [URL]</title>
    <!-- CSS intégré pour portabilité -->
</head>
<body>
    <!-- En-tête avec informations générales -->
    <!-- Section score et métriques -->
    <!-- Liste des vulnérabilités détaillées -->
    <!-- Analyse des en-têtes de sécurité -->
    <!-- Technologies détectées -->
    <!-- Informations SSL/TLS -->
    <!-- Recommandations générales -->
</body>
</html>
```

## Base de Données

### Schéma SQLite
```sql
-- Table des scans
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    duree_scan REAL,
    status_code INTEGER,
    technologies TEXT,           -- JSON array
    score_securite INTEGER,
    formulaires_detectes INTEGER,
    certificat_ssl TEXT,        -- JSON object
    en_tetes_securite TEXT      -- JSON object
);

-- Table des vulnérabilités
CREATE TABLE vulnerabilites (
    id TEXT PRIMARY KEY,
    scan_id INTEGER,
    url TEXT NOT NULL,
    type_vuln TEXT NOT NULL,
    severite TEXT NOT NULL,
    description TEXT NOT NULL,
    details TEXT,               -- JSON object
    remediation TEXT,
    timestamp DATETIME NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (scan_id) REFERENCES scans (id)
);
```

### Requêtes d'Exemple
```sql
-- Top vulnérabilités par type
SELECT type_vuln, COUNT(*) as count 
FROM vulnerabilites 
GROUP BY type_vuln 
ORDER BY count DESC;

-- Scans avec score faible
SELECT url, score_securite, timestamp 
FROM scans 
WHERE score_securite < 50 
ORDER BY score_securite ASC;

-- Technologies les plus communes
SELECT technologies, COUNT(*) 
FROM scans 
WHERE technologies != '[]' 
GROUP BY technologies;
```

## Exemples d'Usage Avancés

### Script de Scan Automatisé
```python
#!/usr/bin/env python3
"""
Script de scan automatisé pour surveillance continue
"""
import json
from datetime import datetime
from scanner_vulnerabilites import WebVulnScanner

def scan_automatise():
    scanner = WebVulnScanner()
    
    # Liste des sites à surveiller
    sites = [
        'https://monsite.com',
        'https://app.monsite.com',
        'https://api.monsite.com'
    ]
    
    resultats = []
    for url in sites:
        print(f"🔍 Scan de {url}...")
        resultat = scanner.scanner_url(url)
        resultats.append({
            'url': url,
            'score': resultat.score_securite,
            'vulns': len(resultat.vulnerabilites),
            'timestamp': datetime.now().isoformat()
        })
    
    # Sauvegarder le résumé
    with open('scan_summary.json', 'w') as f:
        json.dump(resultats, f, indent=2)
    
    print("✅ Scan automatisé terminé")

if __name__ == "__main__":
    scan_automatise()
```

### Intégration CI/CD
```bash
#!/bin/bash
# Script pour intégration CI/CD

# Scanner l'application déployée
python3 scanner_vulnerabilites.py scan $DEPLOYED_URL --no-report

# Vérifier le score minimum
SCORE=$(sqlite3 scans_vulnerabilites.db "SELECT score_securite FROM scans ORDER BY id DESC LIMIT 1")

if [ "$SCORE" -lt 70 ]; then
    echo "❌ Score de sécurité trop faible: $SCORE/100"
    exit 1
else
    echo "✅ Score de sécurité acceptable: $SCORE/100"
fi
```

### Monitoring Continu
```python
import schedule
import time
from scanner_vulnerabilites import WebVulnScanner

def scan_quotidien():
    """Scan quotidien de surveillance"""
    scanner = WebVulnScanner()
    
    sites_critiques = [
        'https://production.monsite.com',
        'https://api.monsite.com'
    ]
    
    for url in sites_critiques:
        resultat = scanner.scanner_url(url)
        
        # Alerter si score faible ou vulnérabilités critiques
        if resultat.score_securite < 80:
            send_alert(f"Score faible détecté: {url} - {resultat.score_securite}/100")
        
        vulns_critiques = [v for v in resultat.vulnerabilites if v.severite == 'CRITICAL']
        if vulns_critiques:
            send_alert(f"Vulnérabilités critiques détectées sur {url}: {len(vulns_critiques)}")

def send_alert(message):
    """Envoyer une alerte (email, Slack, etc.)"""
    print(f"🚨 ALERTE: {message}")
    # Implémenter l'envoi d'alerte

# Programmer le scan quotidien
schedule.every().day.at("08:00").do(scan_quotidien)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Sécurité et Bonnes Pratiques

### ⚠️ Avertissements Légaux
- **Usage autorisé uniquement** - N'utilisez que sur vos propres sites ou avec permission explicite
- **Tests de pénétration** - Respectez les lois locales et les accords de service
- **Responsabilité** - L'utilisateur est seul responsable de l'usage de cet outil

### 🛡️ Sécurité de l'Outil
- **Pas de données personnelles** - Aucune donnée sensible n'est transmise
- **Stockage local** - Toutes les données restent sur votre machine
- **Payloads sûrs** - Tests non destructifs uniquement
- **Respect des robots.txt** - Option de respecter les directives

### 📏 Limitations
- **Faux positifs** - Certaines détections peuvent être incorrectes
- **Couverture partielle** - Ne détecte pas toutes les vulnérabilités possibles
- **Tests basiques** - Scans de surface, pas d'analyse en profondeur
- **Dépendant du réseau** - Performances liées à la connexion

## Déploiement en Production

### Configuration Serveur
```bash
# Créer un utilisateur dédié
sudo useradd -m -s /bin/bash vulnscanner
sudo su - vulnscanner

# Installation dans /opt
sudo mkdir -p /opt/vulnscanner
sudo chown vulnscanner:vulnscanner /opt/vulnscanner
cd /opt/vulnscanner

# Cloner et installer
git clone [REPOSITORY_URL] .
pip install -r requirements.txt

# Configuration des logs
mkdir -p /var/log/vulnscanner
```

### Service Systemd
```ini
# /etc/systemd/system/vulnscanner.service
[Unit]
Description=Vulnerability Scanner Service
After=network.target

[Service]
Type=simple
User=vulnscanner
WorkingDirectory=/opt/vulnscanner
ExecStart=/usr/bin/python3 scanner_vulnerabilites.py scan --batch /etc/vulnscanner/targets.txt
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

### Configuration avec Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Créer un utilisateur non-root
RUN useradd -m -s /bin/bash scanner
USER scanner

# Point d'entrée
ENTRYPOINT ["python3", "scanner_vulnerabilites.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  vulnscanner:
    build: .
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
    environment:
      - DB_PATH=/app/data/scans.db
    command: scan https://example.com
```

## Développement et Contribution

### Structure du Code
```
scanner_vulnerabilites_web/
├── scanner_vulnerabilites.py    # Module principal
├── test_scanner.py             # Tests unitaires
├── demo_scanner.py             # Démonstrations
├── requirements.txt            # Dépendances
├── README.md                   # Documentation
└── examples/                   # Exemples d'usage
    ├── batch_scan.py
    ├── monitoring.py
    └── ci_integration.sh
```

### Tests et Qualité
```bash
# Exécuter les tests
python3 test_scanner.py

# Tests avec couverture
pip install coverage
coverage run test_scanner.py
coverage report

# Linting du code
pip install flake8 black
flake8 scanner_vulnerabilites.py
black scanner_vulnerabilites.py
```

### Ajout de Nouvelles Vulnérabilités
```python
# Template pour nouvelle détection
def _tester_nouvelle_vuln(self, url: str, form_data: Dict[str, str]):
    """Détecter une nouvelle vulnérabilité"""
    payloads = ["payload1", "payload2"]
    
    for payload in payloads:
        # Effectuer le test
        response = self.session.post(url, data={'param': payload})
        
        # Analyser la réponse
        if self._detecter_signature_vuln(response):
            self._ajouter_vulnerabilite(
                url, 'NOUVELLE_VULN', 'HIGH',
                'Description de la vulnérabilité',
                {'payload': payload, 'response': response.text[:200]},
                'Instructions de correction'
            )
```

### Extension des Technologies
```python
# Ajouter de nouvelles signatures dans TechnologyDetector
def __init__(self):
    self.signatures.update({
        'MonFramework': [r'mon-framework', r'X-Powered-By.*MonFramework'],
        'MaLibrairie': [r'ma-lib\.js', r'MaLibrairie/[\d\.]+']
    })
```

## Performance et Optimisation

### Benchmarks Typiques
- **Détection technologies**: ~1000 ops/sec
- **Vérification en-têtes**: ~5000 ops/sec
- **Scan complet**: 2-10 sec/site selon taille
- **Sauvegarde BDD**: ~500 ops/sec
- **Génération rapport**: ~50 rapports/sec

### Optimisations Recommandées
```python
# Configuration pour meilleure performance
scanner = VulnerabilityScanner(
    timeout=5,                    # Timeout réduit
    user_agent="FastScanner/1.0"
)

# Scan parallèle optimisé
resultats = scanner.scanner_multiple(
    urls, 
    max_workers=10               # Plus de workers
)

# Utilisation de session réutilisable
with requests.Session() as session:
    # Réutiliser la même session TCP
    pass
```

### Monitoring des Performances
```python
import time
import psutil

def monitor_scan_performance():
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    # Effectuer le scan
    resultat = scanner.scan_url(url)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    print(f"Durée: {end_time - start_time:.2f}s")
    print(f"Mémoire utilisée: {(end_memory - start_memory) / 1024 / 1024:.1f} MB")
```

## Troubleshooting

### Problèmes Courants

**Erreur SSL/TLS**
```bash
# Solution 1: Désactiver la vérification SSL pour les tests
python3 scanner.py scan https://site-auto-signe.com --no-ssl-verify

# Solution 2: Configurer les certificats
export REQUESTS_CA_BUNDLE=/path/to/certificate.pem
```

**Timeout trop courts**
```bash
# Augmenter le timeout global
python3 scanner.py scan https://site-lent.com --timeout 30
```

**Trop de faux positifs**
```python
# Affiner les payloads dans le code
self.xss_payloads = [
    '<script>alert(1)</script>',  # Payload plus spécifique
]
```

**Problèmes de performance**
```bash
# Réduire le nombre de workers
python3 scanner.py multiple urls.txt --workers 1

# Utiliser une base en mémoire pour les tests
export DB_PATH=":memory:"
```

### Debug et Logs
```python
import logging

# Activer les logs détaillés
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Dans le scanner
logger.debug(f"Test XSS avec payload: {payload}")
logger.info(f"Vulnérabilité détectée: {vuln.type_vuln}")
```

## Intégrations

### API REST (Extension)
```python
from flask import Flask, jsonify, request

app = Flask(__name__)
scanner = WebVulnScanner()

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    resultat = scanner.scanner_url(url, generer_rapport=False)
    
    return jsonify({
        'url': resultat.url,
        'score': resultat.score_securite,
        'vulnerabilites': len(resultat.vulnerabilites),
        'technologies': resultat.technologies,
        'timestamp': resultat.timestamp.isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Webhook Notifications
```python
import requests

def send_webhook_notification(resultat):
    """Envoyer notification webhook après scan"""
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    payload = {
        "text": f"🕷️ Scan terminé: {resultat.url}",
        "attachments": [{
            "color": "danger" if resultat.score_securite < 70 else "good",
            "fields": [
                {"title": "Score", "value": f"{resultat.score_securite}/100", "short": True},
                {"title": "Vulnérabilités", "value": str(len(resultat.vulnerabilites)), "short": True}
            ]
        }]
    }
    
    requests.post(webhook_url, json=payload)
```

## Licence et Support

### Licence
Ce projet est destiné à l'apprentissage et à l'audit de sécurité autorisé uniquement.

### Support
- 📧 **Documentation**: README.md complet
- 🧪 **Tests**: Suite de tests automatisés
- 🎯 **Démonstrations**: Scripts de démo interactifs
- 📊 **Exemples**: Cas d'usage pratiques

### Contribution
Les contributions sont bienvenues ! Consultez les guidelines de développement pour participer au projet.

---

**⚠️ AVERTISSEMENT**: Cet outil est destiné aux tests de sécurité autorisés uniquement. L'utilisateur est responsable du respect des lois et règlementations locales. Utilisez de manière éthique et responsable.