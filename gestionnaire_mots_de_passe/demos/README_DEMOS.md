# 🎭 DÉMONSTRATIONS - GESTIONNAIRE DE MOTS DE PASSE

## 📋 Description

Ce dossier contient toutes les **démonstrations et exemples** du gestionnaire de mots de passe, séparés des scripts principaux pour maintenir un code de production propre et professionnel.

## 🎯 Fichiers de Démonstration

### `demo_gestionnaire_complet.py`
**Script principal de démonstration** contenant toutes les fonctions de test et d'exemple :

- ✅ **Authentification biométrique** - Tests TouchID, Windows Hello, Linux
- ✅ **Surveillance des violations** - Vérification avec HaveIBeenPwned
- ✅ **Synchronisation cloud** - Google Drive et Dropbox
- ✅ **Audit de sécurité** - Analyse de force et recommandations
- ✅ **Partage sécurisé** - Chiffrement asymétrique entre utilisateurs
- ✅ **Génération de phrases de passe** - Style XKCD avec entropie
- ✅ **Menu interactif** - Navigation facile

## 🚀 Utilisation

### Exécution du Menu Interactif
```bash
cd /app/gestionnaire_mots_de_passe
python3 demos/demo_gestionnaire_complet.py
```

### Démos Spécifiques en Python
```python
# Depuis le dossier parent
import sys
sys.path.append('.')
from demos.demo_gestionnaire_complet import demo_biometric_auth

# Exécuter une démonstration
demo_biometric_auth()
```

## 📊 Types de Démonstrations

### 1. 🔐 **Authentification Biométrique**
- Détection des méthodes disponibles (TouchID, Windows Hello, Linux)
- Génération et vérification de tokens biométriques
- Statistiques d'utilisation et cache sécurisé
- Support multi-plateforme automatique

### 2. 🔍 **Audit de Sécurité**
- Analyse de 5+ mots de passe avec différents niveaux de sécurité
- Calcul de scores de sécurité individuels et globaux
- Vérification avec base HaveIBeenPwned
- Recommandations automatiques d'amélioration
- Analyse par catégorie (Banque, Social, Travail, etc.)

### 3. 🚨 **Surveillance des Violations**
- Ajout de mots de passe de démonstration vulnérables
- Vérification automatique contre les bases de violations connues
- Génération de rapports de sécurité détaillés
- Notifications d'alertes de sécurité

### 4. ☁️ **Synchronisation Cloud**
- Configuration simulée Google Drive et Dropbox
- Processus de chiffrement et synchronisation
- Gestion des conflits et résolution automatique
- Statistiques de synchronisation en temps réel

### 5. 🤝 **Partage Sécurisé**
- Chiffrement asymétrique pour partage entre utilisateurs
- Gestion des permissions granulaires (lecture, utilisation)
- Liens de partage avec expiration
- Révocation d'accès instantanée

### 6. 🎲 **Génération de Phrases de Passe**
- Styles XKCD avec 4-6 mots du dictionnaire français
- Calcul d'entropie et estimation temps de crack
- Personnalisation des séparateurs et options
- Multiple configurations pour différents cas d'usage

### 7. 🎯 **Workflow Complet**
Exécute toutes les démonstrations en séquence avec rapport final.

## 📁 Fichiers Générés

Les démonstrations créent une base de données temporaire avec données de test :

```
gestionnaire_mots_de_passe/
├── passwords.db              # Base de données avec données de démo
└── demos/
    ├── demo_gestionnaire_complet.py  # Script principal
    └── README_DEMOS.md              # Cette documentation
```

## 🔧 Configuration

Les démonstrations utilisent des paramètres optimisés :

- **Mot de passe maître** : `demo123!` (pour les tests uniquement)
- **Base de données** : Créée automatiquement avec données de test
- **Services cloud** : Simulation sans vraies credentials
- **Authentification biométrique** : Détection automatique des méthodes

## 💡 Cas d'Usage

### Pour les Développeurs
- Test des nouvelles fonctionnalités de sécurité
- Validation des algorithmes de chiffrement
- Débogage des composants d'authentification

### Pour les Formateurs
- Formation sur la sécurité des mots de passe
- Démonstration des bonnes pratiques
- Sensibilisation aux violations de données

### Pour les Utilisateurs
- Découverte des fonctionnalités avancées
- Test avant utilisation avec vraies données
- Compréhension des scores de sécurité

## ⚠️ Notes Importantes

- **Données de démonstration** : Tous les mots de passe sont fictifs
- **Pas de vraies credentials** : Services cloud simulés
- **Isolé des scripts principaux** : Aucun impact sur le code de production
- **Base temporaire** : Les données de démo peuvent être supprimées

## 🛠️ Maintenance

Ce dossier de démonstrations est maintenu séparément des scripts principaux :

- ✅ **Ajouts de nouvelles démos** : Facile sans impacter la production
- ✅ **Tests des fonctionnalités** : Environnement isolé et sécurisé
- ✅ **Documentation à jour** : Exemples synchronisés avec le code

## 🔒 Sécurité des Démonstrations

- Toutes les démonstrations utilisent des données fictives
- Aucune vraie credential ou API key nécessaire
- Chiffrement complet même pour les données de test
- Isolation totale des données de production

---

**🎭 Profitez des démonstrations pour découvrir toutes les capacités du gestionnaire de mots de passe !**