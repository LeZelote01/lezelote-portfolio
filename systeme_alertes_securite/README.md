# Système d'Alertes Sécurité 🚨

## Description
Système de monitoring avec alertes en temps réel, dashboard web interactif et notifications multi-canaux pour la surveillance de la sécurité système.

## Fonctionnalités

### 🔍 Monitoring Avancé
- **Surveillance des logs** en temps réel avec watchdog
- **Monitoring système** (CPU, mémoire, disque) avec psutil
- **Détection de patterns** personnalisables avec regex
- **Règles d'alerte configurables** par source et niveau
- **Cooldown intelligent** pour éviter le spam d'alertes

### 📱 Notifications Multi-Canaux  
- **Email SMTP** avec templates HTML formatés
- **Telegram Bot** avec messages formatés Markdown
- **Webhooks HTTP** pour intégrations personnalisées
- **Configuration flexible** par type d'alerte
- **Retry automatique** en cas d'échec de notification

### 🌐 Dashboard Web Temps Réel
- **Interface Flask moderne** avec Socket.IO
- **Graphiques interactifs** avec Chart.js
- **Mises à jour temps réel** via WebSockets
- **Filtrage avancé** des alertes
- **Contrôles de monitoring** intégrés
- **Design responsive** pour mobile/desktop

### 💾 Gestion des Données
- **Base SQLite** avec schéma optimisé
- **Historique complet** des alertes et incidents
- **Statistiques temporelles** avec agrégation
- **Recherche et filtrage** multi-critères
- **Marquage de résolution** des alertes

### ⚙️ Configuration Flexible
- **Fichier JSON** de configuration centralisée
- **Règles d'alerte dynamiques** modifiables à chaud
- **Templates de notifications** personnalisables
- **Intégration modulaire** facile

## Installation

### Prérequis Système
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip sqlite3

# CentOS/RHEL
sudo yum install python3-devel python3-pip sqlite3
```

### Installation des Dépendances
```bash
pip install -r requirements.txt
```

### Dépendances Principales
- **Flask 3.0.0** - Framework web moderne
- **Flask-SocketIO 5.3.6** - WebSockets temps réel
- **SQLAlchemy 2.0.23** - ORM pour la base de données
- **watchdog 3.0.0** - Surveillance des fichiers
- **psutil 5.9.6** - Monitoring système
- **python-telegram-bot 20.7** - API Telegram
- **requests 2.31.0** - Client HTTP pour webhooks

## Configuration

### Fichier de Configuration (config.json)
```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "votre.email@gmail.com",
    "password": "mot_de_passe_app",
    "destinataires": ["admin@entreprise.com", "security@entreprise.com"]
  },
  "telegram": {
    "enabled": true,
    "token": "BOT_TOKEN_FROM_BOTFATHER",
    "chat_ids": [-123456789, 987654321]
  },
  "webhook": {
    "enabled": true,
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer YOUR_TOKEN"
    }
  },
  "monitoring": {
    "log_directories": ["/var/log", "/opt/app/logs", "./logs"],
    "system_monitoring": true,
    "check_interval": 30
  },
  "regles": [
    {
      "id": "failed_login",
      "nom": "Tentatives de connexion échouées",
      "actif": true,
      "source": "log_file",
      "pattern": "(failed|failure|authentication failed|login failed)",
      "niveau": "WARNING",
      "description": "Détecte les tentatives de connexion échouées",
      "canaux": ["email", "telegram"],
      "cooldown": 300
    },
    {
      "id": "cpu_high",
      "nom": "CPU Utilisation Élevée",
      "actif": true,
      "source": "system",
      "pattern": "CPU_HIGH",
      "niveau": "WARNING",
      "description": "CPU utilisation > 90%",
      "canaux": ["telegram"],
      "cooldown": 600
    }
  ]
}
```

### Configuration Telegram
1. Créer un bot avec [@BotFather](https://t.me/botfather)
2. Récupérer le token du bot
3. Obtenir votre chat_id en envoyant `/start` au bot
4. Ajouter le token et chat_id dans la configuration

### Configuration Email
1. Activer l'authentification à 2 facteurs sur Gmail
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans la configuration

## Utilisation

### 🚀 Démarrage Rapide

#### Mode Daemon (Monitoring Continu)
```bash
# Démarrer le monitoring en arrière-plan
python3 alertes_securite.py --daemon

# Avec fichier de configuration personnalisé
python3 alertes_securite.py --daemon --config production.json --db prod_alertes.db
```

#### Interface Web (Dashboard)
```bash
# Lancer l'interface web
python3 webapp.py

# Avec port personnalisé
python3 webapp.py --port 8080 --host 0.0.0.0

# Mode debug pour développement
python3 webapp.py --debug
```

#### Interface en Ligne de Commande
```bash
# Lister les alertes récentes
python3 alertes_securite.py list --limite 10

# Filtrer par niveau
python3 alertes_securite.py list --niveau ERROR --non-resolues

# Afficher les statistiques
python3 alertes_securite.py stats

# Marquer une alerte comme résolue
python3 alertes_securite.py resolve alerte_id_12345

# Tester les notifications
python3 alertes_securite.py test --canal email
python3 alertes_securite.py test --canal telegram
```

### 📊 Dashboard Web

#### Fonctionnalités Principales
- **Vue d'ensemble** : Statistiques globales et tendances
- **Alertes temps réel** : Liste filtrée avec actions rapides
- **Graphiques interactifs** : Évolution des alertes par jour
- **Contrôles de monitoring** : Start/Stop des services
- **Filtrage avancé** : Par niveau, état, période
- **Actions en lot** : Résolution multiple d'alertes

#### URLs Principales
- **Dashboard principal** : `http://localhost:5000/`
- **API alertes** : `http://localhost:5000/api/alertes`
- **API statistiques** : `http://localhost:5000/api/stats`
- **WebSocket** : Connexion automatique pour temps réel

### 🔧 API REST

#### Endpoints Disponibles
```http
GET /api/alertes?limite=50&niveau=ERROR&resolu=false
GET /api/stats
GET /api/regles
POST /api/alertes/{id}/resolve
POST /api/test-alerte
POST /api/monitoring/start
POST /api/monitoring/stop
```

#### Exemple d'Utilisation API
```bash
# Récupérer les alertes critiques non résolues
curl "http://localhost:5000/api/alertes?niveau=CRITICAL&resolu=false"

# Marquer une alerte comme résolue
curl -X POST "http://localhost:5000/api/alertes/alert_123/resolve"

# Créer une alerte de test
curl -X POST "http://localhost:5000/api/test-alerte" \
  -H "Content-Type: application/json" \
  -d '{"niveau":"WARNING","message":"Test API","details":{"source":"api"}}'
```

## Structure des Données

### Modèle d'Alerte
```python
@dataclass
class Alerte:
    id: str              # Identifiant unique
    timestamp: datetime  # Moment de création
    niveau: str         # INFO, WARNING, ERROR, CRITICAL
    source: str         # Source de l'alerte (log:auth.log, system, etc.)
    message: str        # Message descriptif
    details: Dict       # Détails techniques (JSON)
    resolu: bool        # État de résolution
    canal_notification: List[str]  # Canaux utilisés
```

### Modèle de Règle
```python
@dataclass
class RegleAlerte:
    id: str           # Identifiant unique
    nom: str          # Nom descriptif
    actif: bool       # Activé/désactivé
    source: str       # log_file, system, network, custom
    pattern: str      # Regex ou condition de déclenchement
    niveau: str       # Niveau d'alerte généré
    description: str  # Description détaillée
    canaux: List[str] # Canaux de notification
    cooldown: int     # Délai entre alertes similaires (secondes)
```

## Règles d'Alerte Prédéfinies

### Sécurité Système
```json
{
  "id": "failed_ssh",
  "nom": "Tentatives SSH échouées",
  "pattern": "Failed password for .* from .* port",
  "niveau": "WARNING",
  "source": "log_file"
}
```

### Monitoring Ressources
```json
{
  "id": "disk_full",
  "nom": "Espace disque critique",
  "pattern": "DISK_HIGH",
  "niveau": "ERROR",
  "source": "system"
}
```

### Sécurité Web
```json
{
  "id": "http_attack",
  "nom": "Tentative d'attaque web",
  "pattern": "(sql injection|xss|csrf|path traversal)",
  "niveau": "CRITICAL",
  "source": "log_file"
}
```

## Exemples d'Usage

### Surveillance des Logs d'Authentification
```bash
# Surveiller les logs SSH en temps réel
sudo python3 alertes_securite.py --daemon

# Les tentatives échouées déclencheront automatiquement des alertes
# Exemple de log détecté:
# "Failed password for admin from 192.168.1.100 port 22"
```

### Monitoring de Performance
```python
# Le système surveille automatiquement:
# - CPU > 90% pendant 1 minute → WARNING
# - Mémoire > 90% → WARNING  
# - Disque > 90% → ERROR
# - Disque > 95% → CRITICAL
```

### Intégration avec Nagios/Zabbix
```bash
# Envoyer des alertes externes via webhook
curl -X POST "http://localhost:5000/api/test-alerte" \
  -H "Content-Type: application/json" \
  -d '{
    "niveau": "ERROR",
    "message": "Service MySQL down",
    "details": {
      "service": "mysql",
      "status": "stopped",
      "last_seen": "2025-03-08T10:30:00Z"
    }
  }'
```

## Déploiement

### Production avec Systemd
```ini
# /etc/systemd/system/alertes-securite.service
[Unit]
Description=Système d'Alertes Sécurité
After=network.target

[Service]
Type=simple
User=alertes
WorkingDirectory=/opt/alertes-securite
ExecStart=/usr/bin/python3 alertes_securite.py --daemon --config production.json
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Activation du service
sudo systemctl enable alertes-securite
sudo systemctl start alertes-securite
sudo systemctl status alertes-securite
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python3", "webapp.py", "--host", "0.0.0.0"]
```

### Reverse Proxy Nginx
```nginx
server {
    listen 80;
    server_name alertes.mondomaine.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Surveillance Avancée

### Intégration Fail2Ban
```bash
# Surveiller les bans Fail2Ban
tail -f /var/log/fail2ban.log | grep "Ban" | \
while read line; do
  curl -X POST "http://localhost:5000/api/test-alerte" \
    -H "Content-Type: application/json" \
    -d "{\"niveau\":\"WARNING\",\"message\":\"Fail2Ban: $line\"}"
done
```

### Monitoring Docker
```python
# Règle personnalisée pour containers Docker
{
  "id": "docker_container_down",
  "nom": "Container Docker arrêté",
  "pattern": "container died",
  "niveau": "ERROR",
  "source": "log_file",
  "canaux": ["telegram", "email"]
}
```

### Surveillance Réseau
```python
# Intégration avec surveillance réseau
import subprocess

def check_network_connectivity():
    result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        # Créer une alerte de connectivité
        alerte = Alerte(
            id=f"network_{int(time.time())}",
            niveau="ERROR",
            source="network",
            message="Perte de connectivité Internet",
            details={"target": "8.8.8.8", "status": "unreachable"}
        )
```

## Troubleshooting

### Problèmes Courants

**Permissions sur les logs**
```bash
# Ajouter l'utilisateur au groupe adm
sudo usermod -a -G adm votre_utilisateur

# Ou modifier les permissions
sudo chmod 644 /var/log/auth.log
```

**Configuration Telegram**
```bash
# Tester la connexion Telegram
python3 -c "
from telegram import Bot
bot = Bot('VOTRE_TOKEN')
print(bot.get_me())
"
```

**Problèmes SMTP**
```bash
# Tester la configuration email
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('email@gmail.com', 'mot_de_passe_app')
print('SMTP OK')
"
```

## Technologies Utilisées

### Backend
- **Python 3.8+** - Langage principal
- **Flask 3.0** - Framework web moderne
- **SQLAlchemy 2.0** - ORM avancé
- **Socket.IO** - WebSockets bidirectionnels
- **SQLite** - Base de données embarquée

### Monitoring
- **watchdog** - Surveillance fichiers temps réel
- **psutil** - Monitoring ressources système
- **schedule** - Tâches programmées
- **threading** - Parallélisation des tâches

### Notifications
- **python-telegram-bot** - API Telegram officielle
- **smtplib** - Client SMTP intégré Python
- **requests** - Client HTTP pour webhooks

### Frontend
- **HTML5/CSS3/JavaScript** - Interface moderne
- **Chart.js** - Graphiques interactifs
- **Socket.IO Client** - Temps réel côté client
- **Responsive Design** - Compatible mobile

## Apprentissage

Ce projet vous permettra de maîtriser :

### 🔍 Monitoring & Observabilité
- **Surveillance temps réel** de fichiers et système
- **Pattern matching** avec expressions régulières
- **Agrégation de métriques** et alerting intelligent
- **Corrélation d'événements** multi-sources

### 🌐 Développement Web Full-Stack
- **API REST** avec Flask et validation
- **WebSockets temps réel** avec Socket.IO
- **Dashboard interactif** avec JavaScript moderne
- **Architecture MVC** séparée et maintenable

### 📱 Intégrations & Notifications
- **APIs externes** (Telegram, SMTP, Webhooks)
- **Gestion d'erreurs** et retry automatique
- **Configuration flexible** multi-environnements
- **Templates de messages** personnalisables

### 💾 Gestion des Données
- **Base de données relationnelle** avec SQLAlchemy
- **Requêtes optimisées** et indexation
- **Statistiques temporelles** et agrégation
- **Migration de schéma** et versioning

## Améliorations Possibles

- [ ] **Machine Learning** pour détection d'anomalies avancée
- [ ] **Alertes prédictives** basées sur les tendances
- [ ] **Intégration Kubernetes** pour monitoring de clusters
- [ ] **Plugin system** pour extensions personnalisées  
- [ ] **Authentification LDAP/SSO** pour l'interface web
- [ ] **Mobile app** pour notifications push natives
- [ ] **Corrélation d'événements** inter-systèmes
- [ ] **Tableaux de bord** personnalisables par utilisateur
- [ ] **Export Prometheus/Grafana** pour métriques
- [ ] **Intelligence artificielle** pour classification automatique

## Licence

Ce projet est destiné à l'apprentissage des systèmes de monitoring et d'alerting en cybersécurité.

---

**🚨 IMPORTANT:** Ce système traite des données de sécurité sensibles. Assurez-vous de sécuriser les communications, chiffrer les configurations sensibles et limiter les accès selon le principe du moindre privilège.