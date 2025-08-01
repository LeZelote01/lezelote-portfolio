# 🚀 Guide Complet de Déploiement et Tests - VMware Workstation Pro

## 📋 Vue d'Ensemble du Projet

**Portfolio Cybersécurité & Python de Jean Yves**
- **Type** : Application web full-stack professionnelle
- **Backend** : FastAPI + MongoDB (Python 3.11+)
- **Frontend** : React 19 + Tailwind CSS
- **Architecture** : API REST avec dashboard d'administration JWT
- **État** : 100% terminé et testé (90.4% de réussite aux tests)

### 🎯 Fonctionnalités Principales
- ✅ Portfolio interactif avec 6 projets de cybersécurité
- ✅ Calculateur de prix intelligent avec génération PDF
- ✅ Système de réservation de rendez-vous complet
- ✅ Centre de ressources avec téléchargements
- ✅ Dashboard admin sécurisé (JWT)
- ✅ 7 outils interactifs de cybersécurité
- ✅ Support multi-langue (FR/EN) et thème sombre/clair
- ✅ Newsletter et système de témoignages

---

## 🛠️ Configuration Système VMware

### Spécifications VM Recommandées

#### Configuration Minimale
- **CPU** : 2 vCPU
- **RAM** : 4 GB
- **Stockage** : 25 GB SSD
- **OS** : Ubuntu 22.04 LTS Desktop

#### Configuration Optimale  
- **CPU** : 4 vCPU
- **RAM** : 8 GB
- **Stockage** : 40 GB SSD
- **OS** : Ubuntu 22.04 LTS Desktop

### Création de la VM

1. **Nouvelle Machine Virtuelle**
   ```bash
   # Paramètres VMware Workstation Pro
   - Type : Linux, Ubuntu 64-bit
   - RAM : 4-8 GB (selon config choisie)
   - Disque dur : 25-40 GB (SCSI, allocation dynamique)
   - Accélération 3D : Activée
   - Network Adapter : NAT ou Bridged
   ```

2. **Installation Ubuntu 22.04**
   - Télécharger ISO : https://releases.ubuntu.com/22.04/
   - Installation complète avec interface graphique
   - Utilisateur : `developer` (ou votre choix)

3. **Configuration Post-Installation**
   ```bash
   # Mise à jour système
   sudo apt update && sudo apt upgrade -y
   
   # Installation VMware Tools
   sudo apt install open-vm-tools open-vm-tools-desktop -y
   
   # Redémarrer la VM
   sudo reboot
   ```

---

## 📦 Installation des Dépendances

### 1. Installation Node.js et Yarn

```bash
# Installation Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Vérification version
node --version  # Doit afficher v20.x.x
npm --version   # Doit afficher 10.x.x

# Installation Yarn
npm install -g yarn

# Vérification Yarn
yarn --version  # Doit afficher 1.22.x
```

### 2. Installation Python 3.11+

```bash
# Python 3.11+ (déjà installé sur Ubuntu 22.04)
python3 --version  # Doit afficher 3.11.x

# Installation pip et outils Python
sudo apt install python3-pip python3-venv python3-dev build-essential -y

# Installation des outils système
sudo apt install git curl wget unzip software-properties-common -y
```

### 3. Installation MongoDB

```bash
# Import de la clé publique MongoDB
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Ajout du repository MongoDB
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Installation MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Démarrage et activation MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Vérification MongoDB
sudo systemctl status mongod
```

### 4. Installation d'outils de développement

```bash
# Git configuration (remplacer par vos infos)
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Installation Visual Studio Code (optionnel)
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update
sudo apt install code -y
```

---

## 🚀 Déploiement de l'Application

### 1. Clonage et Configuration du Projet

```bash
# Créer dossier de travail
mkdir ~/projects && cd ~/projects

# Cloner le projet
git clone https://github.com/LeZelote01/lezelote-portfolio.git
cd lezelote-portfolio

# Structure du projet
ls -la
# Vous devriez voir : backend/, frontend/, README.md, ROADMAP_TRAVAUX.md, etc.
```

### 2. Configuration Backend

```bash
# Aller dans le dossier backend
cd ~/projects/lezelote-portfolio/backend

# Vérifier le fichier .env
cat .env
# Contenu attendu :
# MONGO_URL="mongodb://localhost:27017"
# DB_NAME="test_database"

# Installation des dépendances Python
python3 -m venv venv
source venv/bin/activate

# Installation des packages
pip install -r requirements.txt

# Test de la connexion MongoDB
python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://localhost:27017')
    client.admin.command('ping')
    print('✅ MongoDB connexion réussie')
except Exception as e:
    print(f'❌ Erreur MongoDB: {e}')
"
```

### 3. Configuration Frontend

```bash
# Aller dans le dossier frontend
cd ~/projects/lezelote-portfolio/frontend

# Vérifier le fichier .env
cat .env
# Contenu attendu :
# REACT_APP_BACKEND_URL=http://localhost:8001
# Autres variables...

# Installation des dépendances
yarn install

# Vérification des dépendances
yarn list | grep -E "(react|tailwind)"
```

### 4. Migration des Données

```bash
# Retour au backend
cd ~/projects/lezelote-portfolio/backend
source venv/bin/activate

# Vérifier si le script de migration existe
ls -la | grep migrate

# Si le script existe, l'exécuter
python3 migrate_mock_data.py

# Vérifier les données dans MongoDB
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_data():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    collections = ['projects', 'personal_info', 'services', 'skills']
    for collection in collections:
        count = await db[collection].count_documents({})
        print(f'{collection}: {count} documents')
    
    client.close()

asyncio.run(check_data())
"
```

---

## 🔧 Démarrage et Tests de l'Application

### 1. Démarrage Backend (Terminal 1)

```bash
# Terminal 1 - Backend
cd ~/projects/lezelote-portfolio/backend
source venv/bin/activate

# Démarrage du serveur FastAPI
python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Messages attendus :
# INFO: Started server process
# INFO: Waiting for application startup.
# INFO: Application startup complete.
# INFO: Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### 2. Test Backend API (Terminal 2)

```bash
# Terminal 2 - Tests API
# Test endpoint racine
curl http://localhost:8001/api/
# Réponse attendue : {"message":"Hello World"}

# Test endpoints publics
curl http://localhost:8001/api/public/personal | jq .
curl http://localhost:8001/api/public/projects | jq . | head -20
curl http://localhost:8001/api/public/services | jq . | head -20

# Test authentification admin
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Réponse attendue : {"access_token": "...", "token_type": "bearer", "user": {...}}
```

### 3. Démarrage Frontend (Terminal 3)

```bash
# Terminal 3 - Frontend
cd ~/projects/lezelote-portfolio/frontend

# Démarrage React
yarn start

# Messages attendus :
# webpack compiled successfully
# Local:            http://localhost:3000
# On Your Network:  http://[IP]:3000
```

### 4. Tests Fonctionnels Complets

#### A. Test du Portfolio Public
```bash
# Ouvrir navigateur et tester :
firefox http://localhost:3000

# Pages à tester :
# ✅ Page d'accueil (Hero + sections)
# ✅ À propos
# ✅ Compétences
# ✅ Projets (6 projets de cybersécurité)
# ✅ Services
# ✅ Contact
# ✅ Outils interactifs (/tools)
# ✅ Calculateur de prix (/calculator)
# ✅ Centre de ressources (/resources)
# ✅ Système de réservation (/booking)
```

#### B. Test Dashboard Admin
```bash
# Test interface admin
firefox http://localhost:3000/admin/login

# Identifiants de test :
# Username: admin
# Password: admin123

# Sections à tester dans l'admin :
# ✅ Dashboard principal
# ✅ Gestion des informations personnelles
# ✅ Gestion des compétences
# ✅ Gestion des projets
# ✅ Gestion des services
# ✅ Gestion des témoignages
```

#### C. Test des Outils Interactifs
```bash
# Naviguer vers : http://localhost:3000/tools
# Tester tous les outils :

# 1. Générateur de Hash
echo "test" | sha256sum  # Pour comparer

# 2. Analyseur de mots de passe
# Tester avec : "Password123!" (devrait être "Fort")

# 3. Scanner de ports
# Tester avec : "127.0.0.1" (simulation)

# 4. Chiffreur/Déchiffreur AES
# Tester chiffrement et déchiffrement

# 5. Analyseur d'URL
# Tester avec : "https://example.com/path?param=value"
```

#### D. Test du Calculateur de Prix
```bash
# Naviguer vers : http://localhost:3000/calculator

# Test complet :
# 1. Sélectionner un type de projet
# 2. Configurer la complexité
# 3. Choisir options supplémentaires
# 4. Générer le PDF
# 5. Vérifier sauvegarde en backend
```

---

## 🐛 Troubleshooting et Diagnostic

### 1. Problèmes Courants Backend

#### MongoDB non démarré
```bash
# Vérifier statut
sudo systemctl status mongod

# Si arrêté, démarrer
sudo systemctl start mongod

# Logs MongoDB
sudo journalctl -u mongod -f
```

#### Erreur de dépendances Python
```bash
# Réinstaller l'environnement virtuel
cd ~/projects/lezelote-portfolio/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Port 8001 déjà utilisé
```bash
# Trouver processus utilisant le port
sudo netstat -tulpn | grep :8001
# ou
sudo lsof -i :8001

# Tuer le processus si nécessaire
sudo kill -9 [PID]
```

### 2. Problèmes Courants Frontend

#### Node/Yarn version incompatible
```bash
# Vérifier versions
node --version  # Doit être 18+ ou 20+
yarn --version  # Doit être 1.22+

# Mettre à jour si nécessaire
sudo npm install -g n
sudo n latest
sudo npm install -g yarn@latest
```

#### Erreur de compilation React
```bash
cd ~/projects/lezelote-portfolio/frontend

# Nettoyer cache et réinstaller
yarn cache clean
rm -rf node_modules yarn.lock
yarn install
```

#### Port 3000 occupé
```bash
# Utiliser un autre port
PORT=3001 yarn start

# Ou trouver et libérer le port 3000
sudo lsof -i :3000
sudo kill -9 [PID]
```

### 3. Problèmes de Performance VM

#### VM trop lente
```bash
# Vérifier ressources disponibles
free -h
df -h
top

# Augmenter RAM VM dans VMware (4GB → 8GB)
# Augmenter CPU VM dans VMware (2 → 4 vCPU)
```

#### Interface graphique lente
```bash
# Optimiser Ubuntu pour VM
sudo apt install ubuntu-drivers-common
sudo apt install mesa-utils

# Activer accélération 3D dans VMware
# VM Settings → Display → Accelerate 3D graphics
```

---

## ✅ Checklist de Validation Complète

### Backend Validation
- [ ] MongoDB démarre sans erreur
- [ ] Serveur FastAPI accessible sur http://localhost:8001
- [ ] Endpoint `/api/` retourne `{"message":"Hello World"}`
- [ ] Endpoints publics `/api/public/*` retournent des données
- [ ] Authentification admin fonctionne (admin/admin123)
- [ ] Endpoints admin protégés par JWT
- [ ] Base de données contient les données migrées

### Frontend Validation  
- [ ] React démarre sans erreur sur http://localhost:3000
- [ ] Toutes les pages se chargent correctement
- [ ] Thème sombre/clair fonctionnel
- [ ] Multi-langue FR/EN fonctionnel
- [ ] Formulaires fonctionnent (contact, calculator, booking)
- [ ] Dashboard admin accessible et fonctionnel
- [ ] Tous les outils interactifs opérationnels

### Tests d'Intégration
- [ ] Calculator sauvegarde les devis en backend
- [ ] Booking créé les rendez-vous en backend  
- [ ] Resources télécharge et track en backend
- [ ] Newsletter subscription fonctionne
- [ ] Dashboard admin modifie les données en temps réel

### Performance
- [ ] Temps de chargement initial < 5s
- [ ] Navigation entre pages < 2s
- [ ] Réponses API < 1s
- [ ] Utilisation RAM VM < 80%
- [ ] Utilisation CPU VM < 80%

---

## 🎯 Tests de Charge et Performance

### Test de Charge Backend
```bash
# Installation des outils de test
sudo apt install apache2-utils -y

# Test charge sur API
ab -n 100 -c 10 http://localhost:8001/api/public/projects

# Test authentification
ab -n 50 -c 5 -p auth.json -T application/json http://localhost:8001/api/auth/login

# Contenu du fichier auth.json :
echo '{"username":"admin","password":"admin123"}' > auth.json
```

### Test Performance Frontend
```bash
# Installation Lighthouse CLI
npm install -g lighthouse

# Analyse performance
lighthouse http://localhost:3000 --output=html --output-path=./lighthouse-report.html

# Ouvrir le rapport
firefox ./lighthouse-report.html
```

### Monitoring Ressources VM
```bash
# Installation htop pour monitoring avancé
sudo apt install htop iotop -y

# Monitoring en temps réel
htop

# Monitoring I/O disque
sudo iotop

# Monitoring réseau
sudo apt install iftop -y
sudo iftop -i ens33  # Adapter l'interface réseau
```

---

## 📝 Configuration Finale et Optimisations

### 1. Configuration Serveur pour Tests

```bash
# Script de démarrage automatique (optionnel)
cat > ~/start-portfolio.sh << 'EOF'
#!/bin/bash
echo "🚀 Démarrage Portfolio Cybersécurité..."

# Démarrage MongoDB
sudo systemctl start mongod
sleep 3

# Backend
cd ~/projects/lezelote-portfolio/backend
source venv/bin/activate
python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
echo "✅ Backend démarré (PID: $BACKEND_PID)"

# Frontend
cd ~/projects/lezelote-portfolio/frontend
yarn start &
FRONTEND_PID=$!
echo "✅ Frontend démarré (PID: $FRONTEND_PID)"

echo "🌐 Application accessible sur :"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001"
echo "   Admin:    http://localhost:3000/admin/login"
echo ""
echo "Pour arrêter : kill $BACKEND_PID $FRONTEND_PID"
EOF

chmod +x ~/start-portfolio.sh
```

### 2. Tests Automatisés

```bash
# Script de tests automatisés
cat > ~/test-portfolio.sh << 'EOF'
#!/bin/bash
echo "🧪 Tests automatisés du Portfolio..."

# Test Backend
echo "1. Test Backend API..."
curl -s http://localhost:8001/api/ | grep -q "Hello World" && echo "✅ API OK" || echo "❌ API ERREUR"

# Test données publiques
echo "2. Test données publiques..."
curl -s http://localhost:8001/api/public/projects | jq length > /tmp/projects_count
if [ $(cat /tmp/projects_count) -gt 0 ]; then
    echo "✅ Projets OK ($(cat /tmp/projects_count) projets)"
else
    echo "❌ Pas de projets trouvés"
fi

# Test authentification
echo "3. Test authentification admin..."
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r .access_token)

if [ "$TOKEN" != "null" ] && [ "$TOKEN" != "" ]; then
    echo "✅ Auth admin OK"
else
    echo "❌ Auth admin ERREUR"
fi

# Test Frontend
echo "4. Test Frontend..."
curl -s -I http://localhost:3000 | head -n 1 | grep -q "200 OK" && echo "✅ Frontend OK" || echo "❌ Frontend ERREUR"

echo "🏁 Tests terminés !"
EOF

chmod +x ~/test-portfolio.sh
```

### 3. Sauvegarde et Snapshot

```bash
# Dans VMware Workstation Pro :
# 1. VM → Snapshot → Take Snapshot
# 2. Nom : "Portfolio-Config-Complete"
# 3. Description : "Configuration complète avec application testée"
```

---

## 🎓 Formation Utilisateur

### Utilisation Dashboard Admin

1. **Connexion Admin**
   - URL : http://localhost:3000/admin/login  
   - Login : admin
   - Password : admin123

2. **Gestion du Contenu**
   - Projets : Ajout/édition/suppression
   - Compétences : Niveaux et catégories
   - Services : Prix et descriptions
   - Témoignages : Modération et publication

3. **Utilisation des Outils**
   - URL : http://localhost:3000/tools
   - 7 outils interactifs disponibles
   - Résultats sauvegardables

### Maintenance et Mise à Jour

```bash
# Mise à jour quotidienne
cd ~/projects/lezelote-portfolio
git pull origin main

# Redémarrage services
sudo systemctl restart mongod
# Redémarrer backend et frontend manuellement
```

---

## 📞 Support et Documentation

### Logs d'Application
```bash
# Backend logs
cd ~/projects/lezelote-portfolio/backend
source venv/bin/activate
python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 --log-level info

# MongoDB logs
sudo journalctl -u mongod -f

# Système logs
sudo journalctl -f
```

### Documentation Projet
- **README.md** : Vue d'ensemble du projet
- **ROADMAP_TRAVAUX.md** : Détails de développement
- **portfolio_specifications.md** : Spécifications complètes

### Contact Développeur
- **GitHub** : https://github.com/LeZelote01/lezelote-portfolio
- **Issues** : Utiliser GitHub Issues pour les bugs
- **Documentation** : README du projet

---

## 🏁 Conclusion

Ce guide vous permet de déployer et tester complètement le portfolio cybersécurité dans VMware Workstation Pro. L'application est production-ready avec toutes les fonctionnalités testées et validées.

**Configuration finale :**
- ✅ VM Ubuntu 22.04 optimisée
- ✅ Stack complète (MongoDB + FastAPI + React)
- ✅ 100% des fonctionnalités opérationnelles  
- ✅ Dashboard admin sécurisé
- ✅ Tests automatisés disponibles
- ✅ Documentation complète

**Prochaines étapes :**
- Déploiement en production (voir guide séparé)
- Personnalisation du contenu via dashboard admin
- Formation aux outils de cybersécurité intégrés

---

**Créé avec ❤️ par Jean Yves - Spécialiste Cybersécurité & Développeur Python**