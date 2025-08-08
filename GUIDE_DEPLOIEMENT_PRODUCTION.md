# 🚀 Guide Complet de Déploiement en Production
## Portfolio Cybersécurité Jean Yves

---

## 📋 **Table des Matières**

1. [Options de Déploiement](#1-options-de-déploiement)
2. [Prérequis Techniques](#2-prérequis-techniques)
3. [Préparation du Code](#3-préparation-du-code)
4. [Déploiement Gratuit - Option A (Vercel + Railway + MongoDB Atlas)](#4-déploiement-gratuit---option-a)
5. [Déploiement Semi-Gratuit - Option B (DigitalOcean + Netlify)](#5-déploiement-semi-gratuit---option-b)
6. [Déploiement Complet VPS - Option C (OVH/DigitalOcean)](#6-déploiement-complet-vps---option-c)
7. [Configuration des Domaines](#7-configuration-des-domaines)
8. [Monitoring et Maintenance](#8-monitoring-et-maintenance)
9. [Optimisations Performance](#9-optimisations-performance)
10. [Sécurisation Production](#10-sécurisation-production)

---

## 1. **Options de Déploiement**

### 🆓 **Option A - 100% Gratuit** (Recommandé pour démarrer)
- **Frontend** : Vercel (gratuit)
- **Backend** : Railway (gratuit avec limitations)
- **Base de données** : MongoDB Atlas (512MB gratuit)
- **Coût** : 0€/mois
- **Limitations** : Bande passante limitée, temps d'activité réduit

### 💰 **Option B - Semi-Gratuit** (Meilleur rapport qualité/prix)
- **Frontend** : Netlify (gratuit) 
- **Backend** : Railway/Render (5-7€/mois)
- **Base de données** : MongoDB Atlas (9€/mois)
- **Coût** : 15-20€/mois
- **Avantages** : Performance stable, support technique

### 🏢 **Option C - VPS Complet** (Production professionnelle)
- **Serveur** : DigitalOcean/OVH VPS (15-30€/mois)
- **Domaine** : Namecheap/OVH (10€/an)
- **SSL** : Let's Encrypt (gratuit)
- **Coût** : 20-35€/mois
- **Avantages** : Contrôle total, performance maximale

---

## 2. **Prérequis Techniques**

### 🛠️ **Outils Nécessaires**
```bash
# Installation des outils essentiels
npm install -g @vercel/cli
npm install -g netlify-cli
curl -L https://nixpacks.com/install.sh | sh
```

### 📝 **Comptes à Créer**
- GitHub (code source)
- Vercel ou Netlify (frontend)
- Railway ou Render (backend)
- MongoDB Atlas (base de données)
- Registraire de domaine (Namecheap, OVH)

### ⚙️ **Variables d'Environnement**
```env
# Production Backend
MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net/portfolio_prod
DB_NAME=portfolio_production
JWT_SECRET=votre_secret_jwt_super_securise_32_caracteres
NODE_ENV=production
ALLOWED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com

# Production Frontend  
REACT_APP_BACKEND_URL=https://votre-backend.railway.app
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
```

---

## 3. **Préparation du Code**

### 📦 **1. Structure de Production**
```bash
# Créer les fichiers de déploiement
cd /app

# Backend - Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

# Frontend - Configuration de build
cat > frontend/.env.production << 'EOF'
REACT_APP_BACKEND_URL=https://VOTRE_BACKEND_URL
GENERATE_SOURCEMAP=false
BUILD_PATH=build
EOF
```

### 🔧 **2. Configuration Docker Compose (Option C)**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: portfolio_production
    volumes:
      - mongodb_data:/data/db
      - ./backend/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
    ports:
      - "27017:27017"
    networks:
      - portfolio_network

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      MONGO_URL: mongodb://admin:${MONGO_ROOT_PASSWORD}@mongodb:27017/portfolio_production?authSource=admin
      DB_NAME: portfolio_production
      JWT_SECRET: ${JWT_SECRET}
      NODE_ENV: production
    depends_on:
      - mongodb
    ports:
      - "8001:8001"
    networks:
      - portfolio_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend  
      dockerfile: Dockerfile
      args:
        REACT_APP_BACKEND_URL: https://votre-domaine.com
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - portfolio_network
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - frontend
      - backend
    networks:
      - portfolio_network

volumes:
  mongodb_data:

networks:
  portfolio_network:
    driver: bridge
```

### 📁 **3. Frontend Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 4. **Déploiement Gratuit - Option A**

### 🎯 **Vercel + Railway + MongoDB Atlas**

#### **Étape 1 : MongoDB Atlas (Gratuit)**
```bash
# 1. Créer un compte sur MongoDB Atlas
# 2. Créer un cluster gratuit (M0 Sandbox - 512MB)
# 3. Créer une base de données "portfolio_production"
# 4. Configurer les accès réseau (0.0.0.0/0 pour dev)
# 5. Récupérer la connection string
```

**URL de connexion :**
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/portfolio_production?retryWrites=true&w=majority
```

#### **Étape 2 : Déploiement Backend sur Railway**
```bash
# Installation CLI Railway
npm install -g @railway/cli

# Login et initialisation
railway login
cd backend
railway init

# Configuration des variables d'environnement
railway variables set MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/portfolio_production"
railway variables set DB_NAME="portfolio_production"
railway variables set JWT_SECRET="votre_secret_jwt_super_securise_32_caracteres"

# Déploiement
git add .
git commit -m "Deploy to Railway"
git push

# Railway détectera automatiquement FastAPI et déploiera
```

#### **Étape 3 : Déploiement Frontend sur Vercel**
```bash
# Installation CLI Vercel
npm install -g vercel

cd frontend

# Configuration des variables d'environnement
cat > .env.production << EOF
REACT_APP_BACKEND_URL=https://votre-app.railway.app
GENERATE_SOURCEMAP=false
EOF

# Déploiement
vercel --prod

# Configuration des variables sur Vercel
vercel env add REACT_APP_BACKEND_URL
# Entrer: https://votre-backend.railway.app
```

#### **Étape 4 : Configuration DNS et Domaine**
```bash
# Si vous avez un domaine personnalisé
vercel domains add votre-domaine.com
vercel domains add www.votre-domaine.com

# Configuration DNS chez votre registraire :
# Type: A, Name: @, Value: 76.76.19.61
# Type: CNAME, Name: www, Value: cname.vercel-dns.com
```

---

## 5. **Déploiement Semi-Gratuit - Option B**

### 💎 **Netlify + Render + MongoDB Atlas**

#### **Étape 1 : Backend sur Render (7€/mois)**
```bash
# 1. Créer un compte Render.com
# 2. Connecter votre repository GitHub
# 3. Créer un nouveau Web Service

# render.yaml
version: "1"
services:
  - type: web
    name: portfolio-backend
    env: python
    region: frankfurt  # Plus proche de l'Europe
    plan: starter  # 7€/mois
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGO_URL
        sync: false
      - key: DB_NAME  
        value: portfolio_production
      - key: JWT_SECRET
        sync: false
```

#### **Étape 2 : Frontend sur Netlify (Gratuit)**
```bash
# Installation CLI Netlify
npm install -g netlify-cli

cd frontend

# Build de production
yarn build

# Déploiement
netlify deploy --prod --dir=build

# Configuration continue avec Git
netlify init
netlify env:set REACT_APP_BACKEND_URL https://portfolio-backend.onrender.com
```

#### **Étape 3 : Configuration Continue (CI/CD)**
```yaml
# netlify.toml
[build]
  publish = "build"
  command = "yarn build"

[build.environment]
  REACT_APP_BACKEND_URL = "https://portfolio-backend.onrender.com"
  GENERATE_SOURCEMAP = "false"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production]
  environment = { NODE_ENV = "production" }
```

---

## 6. **Déploiement Complet VPS - Option C**

### 🖥️ **DigitalOcean/OVH VPS (20-35€/mois)**

#### **Étape 1 : Création et Configuration VPS**
```bash
# 1. Créer un droplet Ubuntu 22.04 (2 vCPU, 2GB RAM, 50GB SSD)
# 2. Connexion SSH
ssh root@VOTRE_IP_VPS

# 3. Configuration initiale sécurité
apt update && apt upgrade -y
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable

# 4. Installation Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y

# 5. Création utilisateur non-root
adduser portfolio
usermod -aG sudo,docker portfolio
```

#### **Étape 2 : Configuration Nginx + SSL**
```bash
# Installation Nginx et Certbot
apt install nginx certbot python3-certbot-nginx -y

# Configuration Nginx
cat > /etc/nginx/sites-available/portfolio << 'EOF'
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;

    # Frontend (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Sécurité headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
}
EOF

# Activation du site
ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

#### **Étape 3 : Déploiement avec Docker**
```bash
# Clonage du repository
su - portfolio
git clone https://github.com/LeZelote01/lezelote-portfolio.git
cd lezelote-portfolio

# Configuration des variables d'environnement
cat > .env << 'EOF'
MONGO_ROOT_PASSWORD=votre_mot_de_passe_mongo_securise
JWT_SECRET=votre_secret_jwt_super_securise_32_caracteres
REACT_APP_BACKEND_URL=https://votre-domaine.com
EOF

# Lancement des services
docker-compose -f docker-compose.prod.yml up -d

# Vérification des services
docker-compose ps
```

#### **Étape 4 : Configuration SSL avec Let's Encrypt**
```bash
# Obtention du certificat SSL
certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Test de renouvellement automatique
certbot renew --dry-run

# Configuration du renouvellement automatique
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

---

## 7. **Configuration des Domaines**

### 🌐 **Enregistrement de Domaine**

#### **Fournisseurs Recommandés**
- **Namecheap** : 8-12€/an (.com)
- **OVH** : 10-15€/an (.com)
- **Cloudflare Registrar** : Prix coûtant (8€/an)

#### **Configuration DNS**
```bash
# Pour Option A (Vercel)
Type: A     Name: @       Value: 76.76.19.61
Type: CNAME Name: www     Value: cname.vercel-dns.com

# Pour Option B (Netlify)  
Type: A     Name: @       Value: 104.198.14.52
Type: CNAME Name: www     Value: xxx-xxx.netlify.app

# Pour Option C (VPS)
Type: A     Name: @       Value: VOTRE_IP_VPS
Type: A     Name: www     Value: VOTRE_IP_VPS
```

#### **Configuration Cloudflare (Recommandé)**
```bash
# Avantages Cloudflare :
# - Protection DDoS gratuite
# - CDN mondial gratuit  
# - Cache automatique
# - Analytics détaillées
# - SSL universel gratuit

# Configuration Cloudflare :
# 1. Ajouter votre domaine
# 2. Changer les nameservers chez votre registraire
# 3. Configurer les enregistrements DNS
# 4. Activer le mode "Full SSL"
# 5. Activer la compression et le cache
```

---

## 8. **Monitoring et Maintenance**

### 📊 **Outils de Monitoring Gratuits**

#### **UptimeRobot (Monitoring gratuit)**
```bash
# Configuration des alertes :
# 1. Créer un compte UptimeRobot
# 2. Ajouter votre site web
# 3. Configurer les alertes email/SMS
# 4. Vérification toutes les 5 minutes
```

#### **Google Analytics & Search Console**
```javascript
// Ajout dans frontend/public/index.html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

#### **Logs et Erreurs**
```bash
# Pour VPS (Option C)
# Monitoring des logs
sudo journalctl -u nginx -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Rotation des logs
cat > /etc/logrotate.d/portfolio << 'EOF'
/var/log/nginx/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
}
EOF
```

### 🔄 **Sauvegarde Automatisée**
```bash
# Script de sauvegarde MongoDB
cat > /home/portfolio/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/home/portfolio/backups"
mkdir -p $BACKUP_DIR

# Sauvegarde MongoDB
docker exec mongodb mongodump --db portfolio_production --out /tmp/backup
docker cp mongodb:/tmp/backup $BACKUP_DIR/mongodb_$DATE

# Sauvegarde des fichiers de configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/nginx/sites-available /home/portfolio/lezelote-portfolio/.env

# Nettoyage des sauvegardes anciennes (>30 jours)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Sauvegarde terminée : $DATE"
EOF

chmod +x /home/portfolio/backup.sh

# Configuration cron pour sauvegarde quotidienne
echo "0 3 * * * /home/portfolio/backup.sh" | crontab -
```

---

## 9. **Optimisations Performance**

### ⚡ **Frontend Optimizations**

#### **Configuration Webpack/Vite**
```javascript
// frontend/craco.config.js - Configuration optimisée
module.exports = {
  webpack: {
    configure: (webpackConfig, { env }) => {
      if (env === 'production') {
        // Optimisation du bundle
        webpackConfig.optimization.splitChunks = {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
          },
        };
        
        // Compression
        webpackConfig.optimization.minimize = true;
      }
      return webpackConfig;
    },
  },
};
```

#### **Optimisation des Images**
```bash
# Installation d'outils d'optimisation
npm install -g imagemin-cli imagemin-mozjpeg imagemin-pngquant

# Optimisation automatique
cd frontend/src/assets
imagemin *.jpg --out-dir=optimized --plugin=mozjpeg --plugin.mozjpeg.quality=80
imagemin *.png --out-dir=optimized --plugin=pngquant --plugin.pngquant.quality=65-80
```

### 🚀 **Backend Optimizations**

#### **Configuration FastAPI Production**
```python
# backend/server.py - Configuration optimisée
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(
    title="Portfolio API",
    version="1.0.0",
    docs_url=None,  # Désactiver en production
    redoc_url=None  # Désactiver en production
)

# Compression Gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Cache headers
@app.middleware("http")
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/public/"):
        response.headers["Cache-Control"] = "public, max-age=3600"  # 1 heure
    return response

# Pool de connexions MongoDB optimisé
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=20,
    minPoolSize=5,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000
)
```

#### **Configuration Redis Cache (Optionnel)**
```python
# backend/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Vérifier le cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Exécuter la fonction et mettre en cache
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## 10. **Sécurisation Production**

### 🔒 **Sécurité Backend**

#### **Middleware de Sécurité**
```python
# backend/security.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import asyncio
from collections import defaultdict

# Rate Limiting
class RateLimiter:
    def __init__(self, max_calls: int = 100, time_window: int = 3600):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)

    async def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        
        # Nettoyer les anciens appels
        self.calls[identifier] = [
            call_time for call_time in self.calls[identifier]
            if now - call_time < self.time_window
        ]
        
        # Vérifier la limite
        if len(self.calls[identifier]) >= self.max_calls:
            return False
            
        self.calls[identifier].append(now)
        return True

rate_limiter = RateLimiter()

@app.middleware("http") 
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Trop de requêtes")
    
    return await call_next(request)

# Validation des inputs
from pydantic import validator
import re

class SecureInput(BaseModel):
    @validator('*', pre=True)
    def sanitize_input(cls, v):
        if isinstance(v, str):
            # Supprimer les caractères dangereux
            v = re.sub(r'[<>\"\'%;()&+]', '', v)
            v = v.strip()
        return v
```

#### **Headers de Sécurité**
```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Headers de sécurité
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff" 
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:;"
    )
    
    return response
```

### 🛡️ **Sécurité Frontend**

#### **Configuration Content Security Policy**
```html
<!-- frontend/public/index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:; 
               font-src 'self' data:;">
```

#### **Validation des Inputs**
```javascript
// frontend/src/utils/security.js
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .trim()
    .replace(/[<>\"'%;()&+]/g, '') // Supprimer caractères dangereux
    .substring(0, 1000); // Limiter la longueur
};

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validateURL = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};
```

### 🔐 **Configuration SSL/TLS Avancée**

#### **Configuration Nginx SSL A+**
```nginx
# /etc/nginx/sites-available/portfolio
server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;

    # Certificats SSL
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    
    # Configuration SSL A+
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Configuration du reste...
}
```

---

## 11. **Checklist de Déploiement Final**

### ✅ **Pré-Déploiement**
- [ ] Code testé en local
- [ ] Variables d'environnement configurées
- [ ] Base de données sauvegardée
- [ ] Domaine acheté et configuré
- [ ] Certificats SSL prêts

### ✅ **Déploiement**
- [ ] Services déployés et fonctionnels
- [ ] API accessible et sécurisée
- [ ] Frontend chargé correctement
- [ ] Base de données connectée
- [ ] Monitoring configuré

### ✅ **Post-Déploiement**
- [ ] Tests de performance effectués
- [ ] Sauvegardes configurées
- [ ] SSL Grade A obtenu
- [ ] Analytics configurées
- [ ] Documentation mise à jour

### ✅ **Tests de Production**
```bash
# Tests automatisés de production
curl -f https://votre-domaine.com/api/ || echo "API down"
curl -f https://votre-domaine.com/ || echo "Frontend down"
curl -I https://votre-domaine.com/ | grep "200 OK" || echo "HTTP error"

# Test SSL
echo | openssl s_client -connect votre-domaine.com:443 2>/dev/null | openssl x509 -noout -dates

# Test Performance
curl -w "@curl-format.txt" -o /dev/null -s https://votre-domaine.com/
```

---

## 12. **Maintenance et Mises à Jour**

### 🔄 **Processus de Mise à Jour**

#### **Mise à Jour Sécurisée**
```bash
# Script de mise à jour sécurisée
#!/bin/bash
set -e

echo "🚀 Début de la mise à jour..."

# Sauvegarde avant mise à jour
/home/portfolio/backup.sh

# Récupération des dernières modifications
cd /home/portfolio/lezelote-portfolio
git fetch origin
git checkout main
git pull origin main

# Test de la configuration
docker-compose -f docker-compose.prod.yml config

# Mise à jour avec zero-downtime
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Vérification de santé
sleep 30
curl -f https://votre-domaine.com/api/ || (echo "❌ Déploiement échoué" && exit 1)

echo "✅ Mise à jour terminée avec succès"
```

### 📊 **Métriques de Performance**

#### **Objectifs de Performance**
- **Temps de chargement** : < 3 secondes
- **First Contentful Paint** : < 1.5 secondes  
- **Largest Contentful Paint** : < 2.5 secondes
- **Cumulative Layout Shift** : < 0.1
- **Time to Interactive** : < 3.5 secondes

#### **Surveillance Continue**
```javascript
// frontend/src/utils/performance.js
export const trackPerformance = () => {
  if ('performance' in window) {
    window.addEventListener('load', () => {
      const perfData = performance.getEntriesByType('navigation')[0];
      
      // Envoyer les métriques à votre service d'analytics
      const metrics = {
        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
      };
      
      console.log('Performance Metrics:', metrics);
      // analytics.track('performance', metrics);
    });
  }
};
```

---

## 13. **Support et Dépannage**

### 🔧 **Problèmes Courants**

#### **1. Erreur 502 Bad Gateway**
```bash
# Vérifications :
sudo systemctl status nginx
docker-compose ps
docker-compose logs backend

# Solutions :
docker-compose restart backend
sudo systemctl reload nginx
```

#### **2. Erreur de connexion à la base de données**
```bash
# Vérifications :
docker exec -it mongodb mongo --eval "db.adminCommand('ping')"

# Solutions :
docker-compose restart mongodb
# Vérifier les variables d'environnement MONGO_URL
```

#### **3. Certificat SSL expiré**
```bash
# Renouvellement manuel :
sudo certbot renew
sudo systemctl reload nginx

# Vérification de l'auto-renewal :
sudo systemctl status certbot.timer
```

### 📞 **Contacts d'Urgence**

#### **Support Technique**
- **DigitalOcean** : Support 24/7 (Option C)
- **Railway** : Support communautaire + documentation
- **Vercel** : Support premium pour les comptes payants
- **MongoDB Atlas** : Support technique intégré

#### **Monitoring des Services**
```bash
# Configuration d'alertes critiques
# UptimeRobot : Alerte immédiate si site down > 5 min
# CloudFlare : Alertes sur pics de trafic anormaux
# MongoDB Atlas : Alertes sur performances de la DB
```

---

## 🎯 **Résumé Exécutif**

### **Recommandation Principale**

Pour Jean Yves, **je recommande l'Option B (Semi-Gratuit)** pour commencer :

**Configuration Recommandée :**
- **Frontend** : Netlify (gratuit, CDN mondial, HTTPS automatique)
- **Backend** : Railway ou Render (7€/mois, déploiement simple)
- **Base de données** : MongoDB Atlas (9€/mois, cluster dédié)
- **Domaine** : Namecheap (.com à 10€/an)
- **Monitoring** : UptimeRobot + Google Analytics (gratuit)

**Coût Total : ~20€/mois**

**Avantages :**
- Déploiement en moins de 2 heures
- Performance mondiale avec CDN
- Sauvegardes automatiques
- Support technique disponible
- Scalabilité automatique
- Sécurité incluse (HTTPS, DDoS protection)

**Migration future :** L'architecture permet une migration facile vers un VPS (Option C) quand le business se développe.

---

### 🚀 **Prochaines Étapes Immédiates**

1. **Choisir l'option de déploiement** (recommandé : Option B)
2. **Acheter le domaine** (ex: jean-yves-cybersecurity.com)
3. **Créer les comptes nécessaires** (Netlify, Railway, MongoDB Atlas)
4. **Suivre le guide étape par étape** pour l'option choisie
5. **Configurer le monitoring** (UptimeRobot, Google Analytics)
6. **Tester en production** avec la checklist fournie

**Temps estimé pour déploiement complet : 3-4 heures**

---

*Guide créé pour le portfolio de Jean Yves - Spécialiste Cybersécurité & Développeur Python*
*Dernière mise à jour : Août 2025*