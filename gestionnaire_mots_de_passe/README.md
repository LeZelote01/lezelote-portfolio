# Gestionnaire de Mots de Passe 🔐

## Description
Application complète de gestion de mots de passe avec chiffrement AES, authentification maître robuste et interface graphique moderne.

## Fonctionnalités

### 🔒 Sécurité Avancée
- **Chiffrement AES-256** avec Fernet (cryptography)
- **Dérivation de clé PBKDF2** avec 100,000 itérations
- **Hachage bcrypt** pour le mot de passe maître
- **Session timeout** configurable (15 minutes par défaut)
- **Salt unique** pour chaque base de données

### 🎯 Gestion des Mots de Passe
- **Stockage sécurisé** dans base SQLite chiffrée
- **Génération automatique** avec critères personnalisables
- **Catégorisation flexible** (Personnel, Travail, Banque, etc.)
- **Recherche avancée** par titre, utilisateur, URL
- **Historique d'accès** et statistiques d'utilisation
- **Notes chiffrées** pour informations supplémentaires

### 🎨 Interface Utilisateur
- **Interface en ligne de commande** complète
- **Interface graphique PyQt5** moderne et intuitive
- **Mode sombre** professionnel
- **Tableaux interactifs** avec tri et filtrage
- **Dialogue de génération** de mots de passe
- **Copie automatique** dans le presse-papier

### 💾 Import/Export
- **Export JSON** avec ou sans mots de passe
- **Métadonnées complètes** (dates, statistiques)
- **Structure préservée** pour la migration
- **Export sélectif** par catégorie

### 📊 Statistiques et Monitoring
- **Compteurs d'accès** par mot de passe
- **Répartition par catégorie** 
- **Analyse d'ancienneté** des mots de passe
- **Mots de passe les plus utilisés**
- **Dashboard temps réel**

## Installation

### Prérequis Système
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip python3-pyqt5

# CentOS/RHEL  
sudo yum install python3-devel python3-pip python3-qt5

# macOS
brew install python-tk
```

### Installation des Dépendances
```bash
pip install -r requirements.txt
```

### Dépendances Principales
- **cryptography 41.0.7** - Chiffrement AES et dérivation de clés
- **bcrypt 4.1.2** - Hachage sécurisé du mot de passe maître
- **PyQt5 5.15.10** - Interface graphique moderne
- **pyperclip 1.8.2** - Gestion du presse-papier
- **colorama 0.4.6** - Sortie colorée en CLI
- **tabulate 0.9.0** - Tableaux formatés

## Utilisation

### 🚀 Démarrage Rapide

#### Configuration Initiale
```bash
# Configurer le mot de passe maître
python3 gestionnaire_mdp.py --setup

# Lancer l'interface graphique
python3 gui_gestionnaire.py

# Mode démonstration complet
python3 gestionnaire_mdp.py --demo
```

#### Interface en Ligne de Commande
```bash
# Ajouter un mot de passe
python3 gestionnaire_mdp.py add "Gmail Personnel" --username "john@gmail.com" --generate --category "Email"

# Lister tous les mots de passe
python3 gestionnaire_mdp.py list

# Rechercher dans les mots de passe
python3 gestionnaire_mdp.py list --search "gmail"

# Filtrer par catégorie
python3 gestionnaire_mdp.py list --category "Banque"

# Récupérer un mot de passe spécifique
python3 gestionnaire_mdp.py get a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Copier directement dans le presse-papier
python3 gestionnaire_mdp.py get a1b2c3d4-e5f6-7890-abcd-ef1234567890 --copy

# Afficher les statistiques
python3 gestionnaire_mdp.py stats

# Exporter les données (sans mots de passe)
python3 gestionnaire_mdp.py export backup.json

# Export complet (avec mots de passe - DANGEREUX!)
python3 gestionnaire_mdp.py export backup_complete.json --include-passwords
```

### 🎮 Interface Graphique

#### Fonctionnalités GUI
- **Authentification sécurisée** au démarrage
- **Tableau interactif** avec tri par colonnes
- **Filtrage en temps réel** par recherche et catégorie
- **Formulaires modaux** pour ajout/édition
- **Générateur intégré** avec options avancées
- **Statistiques visuelles** dans le panneau latéral
- **Menu contextuel** et raccourcis clavier

#### Navigation
```
F1  - Aide
Ctrl+N  - Nouveau mot de passe  
Ctrl+E  - Éditer la sélection
Delete  - Supprimer la sélection
Ctrl+C  - Copier le mot de passe
Ctrl+Q  - Quitter l'application
```

## Structure de la Base de Données

### Table `master_password`
```sql
CREATE TABLE master_password (
    id INTEGER PRIMARY KEY,
    password_hash TEXT NOT NULL,      -- Hash bcrypt
    salt TEXT NOT NULL,               -- Salt pour dérivation AES
    created_at TIMESTAMP,
    last_changed TIMESTAMP
);
```

### Table `passwords`
```sql  
CREATE TABLE passwords (
    id TEXT PRIMARY KEY,              -- UUID unique
    title TEXT NOT NULL,
    username TEXT,
    password_encrypted TEXT NOT NULL, -- Chiffré avec AES
    url TEXT,
    notes TEXT,                       -- Notes chiffrées
    category TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0
);
```

### Table `categories`
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT,                       -- Code couleur hex
    created_at TIMESTAMP
);
```

## Sécurité

### Architecture de Chiffrement
1. **Mot de passe maître** → Hash bcrypt (salt automatique)
2. **Dérivation de clé** → PBKDF2-HMAC-SHA256 (100k itérations)  
3. **Chiffrement des données** → AES-256 via Fernet
4. **Salt unique** par base de données (32 bytes aléatoires)

### Bonnes Pratiques Implémentées
- ✅ **Pas de stockage en plain text** du mot de passe maître
- ✅ **Session timeout** automatique 
- ✅ **Validation de complexité** des mots de passe
- ✅ **Effacement mémoire** des clés sensibles
- ✅ **Protection contre les attaques par dictionnaire**
- ✅ **Génération cryptographiquement sécurisée**

### Recommandations d'Usage
- **Mot de passe maître fort** (12+ caractères, mixte)
- **Sauvegarde régulière** de la base chiffrée
- **Export sans mots de passe** pour les backups
- **Environnement sécurisé** pour l'exécution
- **Mise à jour régulière** des dépendances

## Structure des Fichiers

```
gestionnaire_mots_de_passe/
├── gestionnaire_mdp.py      # Moteur principal et CLI
├── gui_gestionnaire.py      # Interface graphique PyQt5
├── test_gestionnaire.py     # Tests unitaires complets
├── demo_gestionnaire.py     # Script de démonstration
├── requirements.txt         # Dépendances Python
├── README.md               # Documentation complète
├── passwords.db            # Base SQLite (créée à l'usage)
└── exports/                # Dossier pour les exports
```

## Exemples d'Usage

### Script d'Automatisation
```bash
#!/bin/bash
# Backup quotidien automatisé

DB_PATH="/secure/passwords.db"
BACKUP_DIR="/backups/passwords"
DATE=$(date +%Y%m%d)

# Export sans mots de passe  
python3 gestionnaire_mdp.py --db "$DB_PATH" export "$BACKUP_DIR/structure_$DATE.json"

# Copie de la base chiffrée
cp "$DB_PATH" "$BACKUP_DIR/database_$DATE.db"

echo "Backup terminé: $DATE"
```

### Intégration avec Scripts
```python
from gestionnaire_mdp import GestionnaireMDP

# Utilisation programmatique
manager = GestionnaireMDP()
if manager.authenticate("mot_de_passe_maitre"):
    
    # Ajouter un compte automatiquement
    manager.add_password(
        title="API Server",
        username="service_account", 
        password=manager.generate_password(32),
        category="Travail",
        notes="Token généré automatiquement"
    )
    
    # Récupérer pour usage dans script
    pwd_data = manager.get_password(password_id)
    api_token = pwd_data['password']
```

## Tests et Qualité

### Suite de Tests Complète
```bash
# Tests unitaires complets
python3 test_gestionnaire.py

# Tests avec couverture
python3 -m pytest test_gestionnaire.py --cov=gestionnaire_mdp

# Tests de performance  
python3 test_gestionnaire.py --benchmark

# Tests de sécurité
python3 test_gestionnaire.py --security
```

### Tests Inclus
- ✅ **Chiffrement/déchiffrement** AES
- ✅ **Authentification** et gestion de session
- ✅ **CRUD complet** des mots de passe
- ✅ **Génération sécurisée** de mots de passe
- ✅ **Import/export** JSON
- ✅ **Intégrité de la base** de données
- ✅ **Gestion des erreurs** et récupération

## Technologies Utilisées

### Backend
- **Python 3.8+** - Langage principal
- **SQLite3** - Base de données embarquée
- **cryptography** - Chiffrement professionnel
- **bcrypt** - Hachage adaptatif sécurisé

### Interface
- **PyQt5** - Framework GUI cross-platform
- **colorama** - Sortie colorée en terminal
- **tabulate** - Mise en forme de tableaux
- **pyperclip** - Interaction avec le presse-papier

## Apprentissage

Ce projet vous permettra de maîtriser :

### 🔒 Sécurité & Cryptographie
- **Chiffrement symétrique** (AES-256)
- **Dérivation de clés** (PBKDF2)
- **Hachage adaptatif** (bcrypt)  
- **Génération aléatoire** sécurisée
- **Gestion de sessions** sécurisées

### 💾 Base de Données
- **SQLite avancé** (transactions, index)
- **Modélisation relationnelle**
- **Gestion des migrations**
- **Intégrité référentielle**
- **Optimisation des requêtes**

### 🎨 Interface Utilisateur
- **PyQt5 complet** (widgets, événements, layouts)
- **Architecture MVC** pour GUI
- **Interface responsive**
- **Gestion d'état** complexe
- **UX/UI professionnel**

### 🧪 Tests & Qualité
- **Tests unitaires** avec unittest
- **Tests d'intégration** complexes
- **Tests de sécurité** automatisés
- **Couverture de code** élevée
- **Tests de performance**

## Améliorations Possibles

- [ ] **Sync cloud** chiffré (Dropbox, Google Drive)
- [ ] **Application mobile** compagnon
- [ ] **Extensions navigateur** (Chrome, Firefox)
- [ ] **Authentification biométrique** (TouchID, Windows Hello)
- [ ] **Audit de sécurité** intégré des mots de passe
- [ ] **Générateur de phrases de passe** (XKCD style)
- [ ] **Partage sécurisé** entre utilisateurs
- [ ] **API REST** pour intégrations
- [ ] **Notifications** de violation de données
- [ ] **Mode hors ligne** avancé

## Licence

Ce projet est destiné à l'apprentissage de la cybersécurité et de la cryptographie appliquée.

---

**⚠️ IMPORTANT:** Ce gestionnaire de mots de passe a été conçu avec des pratiques de sécurité robustes, mais il est recommandé de faire un audit de sécurité professionnel avant un usage en production critique.