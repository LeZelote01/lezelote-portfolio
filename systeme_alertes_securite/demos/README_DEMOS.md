# 📋 DÉMONSTRATIONS - Système d'Alertes Sécurité

## 🎯 Vue d'ensemble

Ce dossier contient **toutes les démonstrations** du Système d'Alertes Sécurité, séparées du code de production selon les directives strictes de nettoyage.

**⚠️ IMPORTANT :** Aucun code de démonstration n'est présent dans les scripts principaux. Toutes les fonctionnalités de démo sont isolées dans ce dossier.

---

## 📁 Contenu du dossier

### 🐍 Scripts de démonstration

- **`demo_alertes.py`** - Démonstration complète de toutes les fonctionnalités
  - Génération d'alertes de test
  - Test des notifications multi-canaux
  - Démonstration du machine learning
  - Interface web et API
  - Génération de rapports

### 📊 Données de démonstration

- **`demo_rapport_alertes.json`** - Rapport de démonstration généré
  - Statistiques d'exemple
  - Données de test formatées
  - Résultats d'analyse ML

---

## 🚀 Utilisation des démonstrations

### Démonstration complète

```bash
# Lancer la démonstration complète
python3 demos/demo_alertes.py

# La démo va :
# 1. Créer une configuration temporaire
# 2. Générer des alertes de test variées
# 3. Tester les notifications (mock)
# 4. Démontrer les capacités ML
# 5. Générer un rapport complet
```

### Fonctionnalités démontrées

#### 🚨 **Génération d'alertes**
- Alertes SSH (tentatives échouées)
- Alertes web (injections SQL, XSS)
- Alertes système (CPU, mémoire, disque)
- Alertes sécurité (trafic suspect)

#### 📱 **Notifications multi-canaux**
- Email SMTP (mode test)
- Telegram Bot (mode test)
- Webhooks (Slack, Discord)

#### 🤖 **Machine Learning**
- Détection d'anomalies
- Classification automatique
- Analyse comportementale
- Réduction des faux positifs

#### 🌐 **Interface web et API**
- Dashboard temps réel
- API REST complète
- WebSockets pour mises à jour
- Documentation interactive

---

## ⚙️ Configuration des démos

### Configuration temporaire

Les démos utilisent une configuration temporaire qui **ne modifie pas** la configuration de production :

```json
{
  "email": {
    "enabled": true,
    "username": "demo@exemple.com",
    "password": "demo_password"
  },
  "telegram": {
    "enabled": true,
    "token": "DEMO_BOT_TOKEN"
  },
  "webhook": {
    "enabled": true,
    "url": "https://hooks.slack.com/services/DEMO/WEBHOOK/URL"
  }
}
```

### Base de données temporaire

- Les démos utilisent une base SQLite temporaire
- Aucune modification des données de production
- Nettoyage automatique après démonstration

---

## 🧪 Tests et validation

### Tests automatisés

```bash
# Valider les démonstrations
python3 -c "
from demos.demo_alertes import demo_complete
demo_complete()
"
```

### Métriques de démonstration

Les démos génèrent des métriques complètes :

- **Alertes générées** : 50+ alertes de test
- **Types d'alertes** : 6 catégories différentes
- **Notifications** : Test de tous les canaux
- **ML** : Analyse de 100% des alertes
- **Performance** : Temps de traitement < 5s

---

## 📈 Scénarios de démonstration

### 🔴 **Scénario 1 : Attaque SSH**
- Simulation de tentatives de connexion échouées
- Génération d'alertes WARNING puis ERROR
- Notifications immédiates
- Analyse ML pour détection de patterns

### 🟠 **Scénario 2 : Attaque Web**
- Injection SQL détectée
- Alerte CRITICAL générée
- Notifications multi-canaux
- Corrélation avec autres incidents

### 🟡 **Scénario 3 : Surcharge système**
- CPU > 90% pendant 5 minutes
- Alertes progressives (WARNING → ERROR → CRITICAL)
- Prédiction ML de panne imminente
- Recommandations automatiques

### 🟢 **Scénario 4 : Faux positif**
- Alert bénigne détectée par règle
- ML identifie comme faux positif
- Réduction automatique de priorité
- Amélioration continue des modèles

---

## 🔧 Développement et extension

### Ajouter de nouvelles démos

1. **Créer un nouveau script** dans ce dossier
2. **Importer les modules** nécessaires depuis le dossier parent
3. **Utiliser la configuration temporaire** pour éviter les conflits
4. **Documenter** les nouvelles fonctionnalités

### Structure recommandée

```python
#!/usr/bin/env python3
"""
Nouvelle démonstration - [Description]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from alertes_securite import SystemeAlertes
# ... autres imports

def nouvelle_demo():
    """Description de la nouvelle démo"""
    # Configuration temporaire
    # Logique de démonstration
    # Nettoyage automatique
    pass

if __name__ == "__main__":
    nouvelle_demo()
```

---

## 📊 Rapports de démonstration

### Génération automatique

Les démos génèrent automatiquement :

- **Rapport JSON** avec métriques détaillées
- **Logs de démonstration** avec horodatage
- **Captures d'écran** des interfaces (si applicable)
- **Métriques de performance** complètes

### Format du rapport

```json
{
  "demo_info": {
    "nom": "Démonstration complète",
    "version": "3.0.0",
    "date": "2025-01-XX",
    "durée": "45 secondes"
  },
  "statistiques": {
    "alertes_generees": 52,
    "notifications_envoyees": 15,
    "anomalies_detectees": 8,
    "faux_positifs_reduits": 3
  },
  "resultats_ml": {
    "precision": 0.94,
    "recall": 0.88,
    "f1_score": 0.91
  }
}
```

---

## ✅ Conformité et validation

### Directives respectées

- ✅ **Séparation complète** du code de production
- ✅ **Aucune référence** aux démos dans les scripts principaux
- ✅ **Documentation complète** des démonstrations
- ✅ **Tests automatisés** de validation
- ✅ **Configuration isolée** pour éviter les conflits

### Tests de conformité

```bash
# Vérifier l'absence de références aux démos
python3 tests_post_nettoyage.py

# Résultat attendu : ✅ TOUS LES TESTS RÉUSSIS
```

---

## 🔮 Évolutions futures

### Démonstrations avancées prévues

- **Intégration Kubernetes** - Monitoring de clusters
- **Analyse prédictive** - Prévision de pannes
- **Corrélation d'événements** - Chaînes d'attaque
- **Intelligence artificielle** - Classification automatique

### Améliorations techniques

- **Visualisations 3D** des données de sécurité
- **Réalité augmentée** pour les dashboards
- **API GraphQL** pour requêtes complexes
- **Streaming temps réel** avec Apache Kafka

---

**🚨 RAPPEL IMPORTANT :** Ce dossier contient **uniquement** les démonstrations. Le code de production est dans le dossier parent et ne contient **aucune référence** aux démos selon les directives strictes de nettoyage.

---

*Dernière mise à jour : 2025 - Système d'Alertes Sécurité v3.0.0*