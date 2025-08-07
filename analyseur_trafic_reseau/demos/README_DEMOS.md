# 🎭 DÉMONSTRATIONS - ANALYSEUR DE TRAFIC RÉSEAU

## 📋 Description

Ce dossier contient toutes les **démonstrations et exemples** du système d'analyse de trafic réseau, séparés des scripts principaux pour maintenir un code de production propre et professionnel.

## 🎯 Fichiers de Démonstration

### `demo_analyseur_complet.py`
**Script principal de démonstration** contenant toutes les fonctions de test et d'exemple :

- ✅ **Génération de données simulées** IPv4/IPv6
- ✅ **Démonstration ML** - Détection d'anomalies
- ✅ **Système de notifications** - Tests d'alertes
- ✅ **Filtres avancés** - Exemples BPF
- ✅ **Analyseur intégré** - Workflow complet
- ✅ **Menu interactif** - Navigation facile

## 🚀 Utilisation

### Exécution du Menu Interactif
```bash
cd /app/analyseur_trafic_reseau
python3 demos/demo_analyseur_complet.py
```

### Démos Spécifiques en Python
```python
# Depuis le dossier parent
import sys
sys.path.append('.')
from demos.demo_analyseur_complet import demo_basic_analysis

# Exécuter une démonstration
demo_basic_analysis()
```

## 📊 Types de Démonstrations

### 1. 🎯 **Analyse de Base**
- Génération de 800 paquets simulés IPv4/IPv6
- Calcul des statistiques complètes
- Visualisation graphique (4 graphiques)
- Export des données JSON/CSV

### 2. 🤖 **Machine Learning**
- Test de détection d'anomalies sur 3 paquets types
- Affichage des scores de confiance
- Support IPv4 et IPv6

### 3. 📧 **Notifications**
- Simulation d'alerte d'anomalie
- Envoi de rapport de statut
- Affichage des statistiques du système

### 4. 🔍 **Filtres Avancés**
- Liste des 25+ filtres prédéfinis
- Création de filtre personnalisé
- Validation BPF automatique

### 5. 🚀 **Analyseur Intégré**
- Initialisation de tous les composants
- Démonstration du workflow complet
- Statut détaillé du système

### 6. 🎯 **Workflow Complet**
Exécute toutes les démonstrations en séquence avec temporisation.

## 📁 Fichiers Générés

Les démonstrations créent plusieurs fichiers de sortie :

```
demos/
├── demo_basic_analysis.png      # Graphiques d'analyse
├── demo_basic_export.json       # Données exportées
├── demo_integrated_analysis.png # Graphiques intégrés  
├── demo_integrated_export.json  # Export intégré
└── README_DEMOS.md              # Cette documentation
```

## 🔧 Configuration

Les démonstrations utilisent des paramètres optimisés :

- **Interface** : `lo` (loopback) pour éviter les permissions
- **Durée** : Simulations rapides (30 secondes max)
- **Données** : 800 paquets synthétiques réalistes
- **Protocoles** : TCP, UDP, ICMP, IPv6, ARP
- **Anomalies** : 3 types simulées (port scan, IPv6, etc.)

## 💡 Cas d'Usage

### Pour les Développeurs
- Test des nouvelles fonctionnalités
- Validation des algorithmes ML
- Débogage des composants

### Pour les Formateurs
- Formation sur l'analyse réseau
- Démonstration des capacités
- Exemples pédagogiques

### Pour les Utilisateurs
- Découverte des fonctionnalités
- Test avant utilisation réelle
- Compréhension du système

## ⚠️ Notes Importantes

- **Pas de capture réelle** : Les démos utilisent des données simulées
- **Pas de permissions requises** : Fonctionne sans sudo
- **Isolé des scripts principaux** : Aucun impact sur le code de production
- **Données temporaires** : Les fichiers générés peuvent être supprimés

## 🛠️ Maintenance

Ce dossier de démonstrations est maintenu séparément des scripts principaux :

- ✅ **Ajouts de nouvelles démos** : Facile sans impacter la production
- ✅ **Tests des fonctionnalités** : Environnement isolé
- ✅ **Documentation à jour** : Exemples synchronisés avec le code

---

**🎭 Profitez des démonstrations pour découvrir toutes les capacités de l'analyseur de trafic réseau !**