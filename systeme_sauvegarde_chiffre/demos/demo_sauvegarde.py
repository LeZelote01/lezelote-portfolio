#!/usr/bin/env python3
"""
Démonstration du Système de Sauvegarde Chiffré

Script de démonstration interactive showcasant toutes les fonctionnalités
du système de sauvegarde avec chiffrement AES, compression et rotation.

Auteur: Système de Cybersécurité
Version: 1.0.0
Date: 2025-03-08
"""

import os
import sys
import json
import time
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# Ajouter le module principal au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sauvegarde_chiffree import (
    SystemeSauvegardeChiffre, formater_taille,
    afficher_liste_sauvegardes, afficher_statistiques
)
from colorama import init, Fore, Style

# Initialiser colorama
init(autoreset=True)


class DemonstrationsInteractives:
    """Classe pour gérer les démonstrations interactives"""
    
    def __init__(self):
        self.dossier_demo = None
        self.systeme = None
        self.config_demo = None
        self.mot_de_passe_demo = "DeモPassword2025!"
        
    def setup_environnement_demo(self):
        """Créer un environnement de démonstration complet"""
        print(f"{Fore.CYAN}🔧 Configuration de l'environnement de démonstration...")
        
        # Créer dossier temporaire pour la démo
        self.dossier_demo = Path(tempfile.mkdtemp(prefix="demo_sauvegarde_"))
        print(f"📁 Dossier de démonstration: {self.dossier_demo}")
        
        # Créer structure de données de test
        dossier_source = self.dossier_demo / "projet_exemple"
        dossier_backups = self.dossier_demo / "backups"
        
        dossier_source.mkdir(parents=True)
        dossier_backups.mkdir(parents=True)
        
        # Créer une structure de projet réaliste
        self._creer_projet_exemple(dossier_source)
        
        # Configuration de démonstration
        self.config_demo = {
            "sauvegarde": {
                "dossier_source": str(dossier_source),
                "dossier_destination": str(dossier_backups),
                "nom_base": "demo_backup",
                "compression_niveau": 6,
                "chiffrement_actif": True,
                "exclusions": ["*.tmp", "*.log", "__pycache__", "node_modules", ".git"]
            },
            "rotation": {
                "max_sauvegardes": 5,
                "conservation_jours": 30,
                "rotation_auto": True
            },
            "securite": {
                "iterations_pbkdf2": 10000,  # Réduit pour la démo
                "longueur_salt": 32,
                "verification_integrite": True,
                "effacement_securise": True
            },
            "planning": {
                "actif": False,
                "frequence": "daily",
                "heure": "02:00"
            },
            "avance": {
                "sauvegarde_incrementale": False,
                "compression_adaptive": True,
                "parallele": True,
                "max_workers": 2
            }
        }
        
        # Sauvegarder la configuration
        config_file = self.dossier_demo / "config_demo.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_demo, f, indent=2, ensure_ascii=False)
        
        # Initialiser le système
        self.systeme = SystemeSauvegardeChiffre(str(config_file))
        
        print(f"{Fore.GREEN}✅ Environnement de démonstration configuré!")
        return dossier_source
    
    def _creer_projet_exemple(self, dossier_source):
        """Créer un projet exemple réaliste"""
        print(f"{Fore.YELLOW}📝 Création d'un projet exemple...")
        
        # Structure de dossiers
        dossiers = [
            "src", "docs", "tests", "config", "assets/images", 
            "assets/styles", "logs", "temp", "build"
        ]
        
        for dossier in dossiers:
            (dossier_source / dossier).mkdir(parents=True, exist_ok=True)
        
        # Fichiers de code source
        (dossier_source / "src" / "main.py").write_text("""#!/usr/bin/env python3
\"\"\"
Application principale du projet de démonstration
\"\"\"

import os
import sys
from datetime import datetime

class ApplicationDemo:
    def __init__(self):
        self.nom = "Projet Démonstration"
        self.version = "1.0.0"
        self.auteur = "Équipe de Développement"
    
    def demarrer(self):
        print(f"🚀 Démarrage de {self.nom} v{self.version}")
        print(f"👤 Auteur: {self.auteur}")
        print(f"📅 Heure: {datetime.now()}")
        
        return "Application démarrée avec succès!"
    
    def traiter_donnees(self, donnees):
        \"\"\"Traiter un ensemble de données\"\"\"
        resultats = []
        for item in donnees:
            if isinstance(item, (int, float)):
                resultats.append(item * 2)
            elif isinstance(item, str):
                resultats.append(item.upper())
            else:
                resultats.append(str(item))
        return resultats

if __name__ == "__main__":
    app = ApplicationDemo()
    print(app.demarrer())
    
    # Test avec des données exemple
    test_data = [1, 2, 3, "hello", "world", 4.5]
    results = app.traiter_donnees(test_data)
    print(f"Résultats: {results}")
""" * 3)  # Répéter pour avoir plus de contenu
        
        (dossier_source / "src" / "utils.py").write_text("""#!/usr/bin/env python3
\"\"\"
Utilitaires pour le projet de démonstration
\"\"\"

import hashlib
import json
from pathlib import Path

def calculer_hash_fichier(chemin_fichier):
    \"\"\"Calculer le hash SHA-256 d'un fichier\"\"\"
    hash_sha256 = hashlib.sha256()
    with open(chemin_fichier, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def sauvegarder_json(donnees, fichier):
    \"\"\"Sauvegarder des données en JSON\"\"\"
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=2, ensure_ascii=False)

def charger_json(fichier):
    \"\"\"Charger des données depuis JSON\"\"\"
    with open(fichier, 'r', encoding='utf-8') as f:
        return json.load(f)

class ConfigurationManager:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = self._charger_config()
    
    def _charger_config(self):
        if self.config_file.exists():
            return charger_json(self.config_file)
        return self._config_par_defaut()
    
    def _config_par_defaut(self):
        return {
            "debug": True,
            "port": 8080,
            "host": "localhost",
            "database": {
                "type": "sqlite",
                "name": "demo.db"
            }
        }
    
    def sauvegarder(self):
        sauvegarder_json(self.config, self.config_file)
""" * 2)
        
        # Fichiers de configuration
        (dossier_source / "config" / "app.json").write_text(json.dumps({
            "application": {
                "nom": "Projet Démonstration Sauvegarde",
                "version": "1.0.0",
                "description": "Projet exemple pour démontrer le système de sauvegarde chiffré"
            },
            "database": {
                "type": "sqlite",
                "host": "localhost",
                "port": 5432,
                "name": "demo_database"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/application.log",
                "max_size": "10MB",
                "retention": 30
            },
            "security": {
                "encryption": True,
                "hash_algorithm": "SHA-256",
                "session_timeout": 3600
            }
        }, indent=2))
        
        (dossier_source / "config" / "development.ini").write_text("""[DEFAULT]
debug = true
port = 8080
host = localhost

[database]
url = sqlite:///demo.db
pool_size = 10
echo = false

[logging]
level = DEBUG
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s

[security]
secret_key = demo-secret-key-change-in-production
session_lifetime = 86400
""")
        
        # Documentation
        (dossier_source / "docs" / "README.md").write_text("""# Projet de Démonstration - Système de Sauvegarde Chiffré

## Description
Ce projet sert d'exemple pour démontrer les capacités du système de sauvegarde chiffré.
Il contient une structure typique d'application avec du code source, des configurations,
des tests et de la documentation.

## Structure du Projet
```
projet_exemple/
├── src/           # Code source principal
├── docs/          # Documentation  
├── tests/         # Tests unitaires
├── config/        # Fichiers de configuration
├── assets/        # Ressources (images, styles)
├── logs/          # Fichiers de logs (exclus des sauvegardes)
├── temp/          # Fichiers temporaires (exclus)
└── build/         # Fichiers de build
```

## Fonctionnalités
- ✅ Application principale avec traitement de données
- ✅ Utilitaires et gestionnaires de configuration  
- ✅ Tests unitaires complets
- ✅ Documentation détaillée
- ✅ Configuration multi-environnement

## Installation
```bash
pip install -r requirements.txt
python src/main.py
```

## Tests
```bash
python -m pytest tests/
```

## Contribution
1. Fork le projet
2. Créer une branche feature
3. Committer les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence
MIT License - Voir LICENSE pour plus de détails
""" * 2)
        
        (dossier_source / "docs" / "ARCHITECTURE.md").write_text("""# Architecture du Système

## Vue d'ensemble
L'architecture suit le pattern MVC (Model-View-Controller) avec séparation claire des responsabilités.

## Components Principaux

### 1. Application Layer (`src/main.py`)
- Point d'entrée principal
- Orchestration des composants
- Gestion du cycle de vie

### 2. Utilities Layer (`src/utils.py`)
- Fonctions utilitaires communes
- Gestionnaire de configuration
- Helpers pour fichiers et données

### 3. Configuration Layer (`config/`)
- Paramètres d'application
- Configuration par environnement
- Gestion des secrets (en production)

### 4. Tests Layer (`tests/`)
- Tests unitaires
- Tests d'intégration
- Mocks et fixtures

## Flux de Données
1. **Entrée** → Application reçoit les données
2. **Traitement** → Utilitaires transforment les données
3. **Stockage** → Sauvegarde dans la configuration
4. **Sortie** → Résultats formatés

## Sécurité
- Chiffrement des données sensibles
- Validation d'entrée
- Audit trail
- Gestion des sessions

## Performance
- Cache des configurations
- Traitement asynchrone
- Pooling des connexions
- Monitoring des métriques
""")
        
        # Tests
        (dossier_source / "tests" / "test_main.py").write_text("""#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import ApplicationDemo

class TestApplicationDemo(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationDemo()
    
    def test_creation_application(self):
        self.assertEqual(self.app.nom, "Projet Démonstration")
        self.assertEqual(self.app.version, "1.0.0")
    
    def test_demarrage(self):
        resultat = self.app.demarrer()
        self.assertIn("succès", resultat)
    
    def test_traitement_donnees_numeriques(self):
        donnees = [1, 2, 3]
        resultats = self.app.traiter_donnees(donnees)
        self.assertEqual(resultats, [2, 4, 6])
    
    def test_traitement_donnees_texte(self):
        donnees = ["hello", "world"]
        resultats = self.app.traiter_donnees(donnees)
        self.assertEqual(resultats, ["HELLO", "WORLD"])
    
    def test_traitement_donnees_mixtes(self):
        donnees = [1, "test", 2.5]
        resultats = self.app.traiter_donnees(donnees)
        self.assertEqual(resultats, [2, "TEST", 5.0])

if __name__ == "__main__":
    unittest.main()
""")
        
        (dossier_source / "tests" / "test_utils.py").write_text("""#!/usr/bin/env python3
import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import calculer_hash_fichier, sauvegarder_json, charger_json, ConfigurationManager

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_hash_fichier(self):
        fichier_test = self.temp_dir / "test.txt"
        fichier_test.write_text("contenu de test")
        
        hash1 = calculer_hash_fichier(fichier_test)
        hash2 = calculer_hash_fichier(fichier_test)
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA-256
    
    def test_sauvegarde_chargement_json(self):
        donnees = {"test": "valeur", "nombre": 42}
        fichier = self.temp_dir / "test.json"
        
        sauvegarder_json(donnees, fichier)
        donnees_chargees = charger_json(fichier)
        
        self.assertEqual(donnees, donnees_chargees)
    
    def test_configuration_manager(self):
        config_file = self.temp_dir / "config.json"
        manager = ConfigurationManager(config_file)
        
        # Configuration par défaut
        self.assertTrue(manager.config["debug"])
        self.assertEqual(manager.config["port"], 8080)
        
        # Modification et sauvegarde
        manager.config["debug"] = False
        manager.sauvegarder()
        
        # Rechargement
        manager2 = ConfigurationManager(config_file)
        self.assertFalse(manager2.config["debug"])

if __name__ == "__main__":
    unittest.main()
""")
        
        # Assets
        (dossier_source / "assets" / "styles" / "main.css").write_text("""/* Styles principaux pour l'application de démonstration */

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    background-color: #f4f4f4;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
}

h1, h2, h3 {
    color: #2c3e50;
    margin-bottom: 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 30px;
}

.button {
    background-color: #3498db;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}

.button:hover {
    background-color: #2980b9;
}

.status {
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.status.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.status.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.status.warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.progress-bar {
    width: 100%;
    height: 24px;
    background-color: #e0e0e0;
    border-radius: 12px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
    transition: width 0.3s ease;
}

@media (max-width: 768px) {
    .container {
        padding: 15px;
        margin: 10px;
    }
    
    .button {
        width: 100%;
        margin-bottom: 10px;
    }
}
""")
        
        # Fichiers de build et temporaires (à exclure)
        (dossier_source / "build" / "output.js").write_text("// Fichier de build généré automatiquement")
        (dossier_source / "temp" / "cache.tmp").write_text("Fichier cache temporaire")
        (dossier_source / "logs" / "debug.log").write_text("2025-03-08 10:00:00 - DEBUG - Application started")
        
        # Fichiers supplémentaires pour augmenter la taille
        for i in range(5):
            (dossier_source / f"docs" / f"documentation_{i+1}.md").write_text(f"""# Documentation {i+1}

## Section {i+1}.1
Contenu de la documentation partie {i+1}. Cette section contient des informations
importantes sur le fonctionnement du système.

### Sous-section {i+1}.1.1
Détails techniques et implémentation.

### Sous-section {i+1}.1.2  
Exemples et cas d'usage.

## Section {i+1}.2
Informations supplémentaires et références.
""" * 20)  # Répéter pour avoir plus de contenu
        
        print(f"{Fore.GREEN}✅ Projet exemple créé avec succès!")
        
        # Afficher statistiques du projet créé
        taille_totale = sum(f.stat().st_size for f in dossier_source.rglob('*') if f.is_file())
        nombre_fichiers = len([f for f in dossier_source.rglob('*') if f.is_file()])
        nombre_dossiers = len([d for d in dossier_source.rglob('*') if d.is_dir()])
        
        print(f"📊 Statistiques du projet:")
        print(f"   • Fichiers: {nombre_fichiers}")
        print(f"   • Dossiers: {nombre_dossiers}")  
        print(f"   • Taille totale: {formater_taille(taille_totale)}")
    
    def demonstration_creation_sauvegarde(self):
        """Démonstration de création de sauvegarde"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🔄 DÉMONSTRATION: Création de Sauvegarde Chiffrée")
        print(f"{Fore.CYAN}{'='*60}")
        
        print(f"\n{Fore.YELLOW}📝 Paramètres de sauvegarde:")
        print(f"   • Source: {self.systeme.config['sauvegarde']['dossier_source']}")
        print(f"   • Destination: {self.systeme.config['sauvegarde']['dossier_destination']}")
        print(f"   • Chiffrement: {'✅ Activé' if self.systeme.config['sauvegarde']['chiffrement_actif'] else '❌ Désactivé'}")
        print(f"   • Compression: Niveau {self.systeme.config['sauvegarde']['compression_niveau']}")
        print(f"   • Exclusions: {', '.join(self.systeme.config['sauvegarde']['exclusions'])}")
        
        input(f"\n{Fore.MAGENTA}🎯 Appuyez sur Entrée pour commencer la sauvegarde...")
        
        # Créer la sauvegarde
        debut = time.time()
        metadonnees = self.systeme.creer_sauvegarde(mot_de_passe=self.mot_de_passe_demo)
        fin = time.time()
        
        if metadonnees:
            print(f"\n{Fore.GREEN}✅ Sauvegarde créée avec succès!")
            print(f"\n📊 Résumé de la sauvegarde:")
            
            # Calculer le ratio de compression
            ratio_compression = (1 - metadonnees.taille_compressee / metadonnees.taille_originale) * 100 if metadonnees.taille_originale > 0 else 0
            
            donnees_resume = [
                ["ID de sauvegarde", metadonnees.id],
                ["Nom du fichier", metadonnees.nom_fichier],
                ["Taille originale", formater_taille(metadonnees.taille_originale)],
                ["Taille compressée", formater_taille(metadonnees.taille_compressee)],
                ["Taille chiffrée", formater_taille(metadonnees.taille_chiffree)],
                ["Ratio compression", f"{ratio_compression:.1f}%"],
                ["Fichiers inclus", f"{metadonnees.fichiers_inclus:,}"],
                ["Dossiers inclus", f"{metadonnees.dossiers_inclus:,}"],
                ["Durée", f"{metadonnees.duree_sauvegarde:.2f}s"],
                ["Hash d'intégrité", metadonnees.hash_integrite[:16] + "..." if metadonnees.hash_integrite else "N/A"],
                ["Chiffré", "🔒 Oui" if metadonnees.chiffre else "🔓 Non"],
                ["Date/Heure", metadonnees.timestamp.strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            from tabulate import tabulate
            print(tabulate(donnees_resume, headers=["Attribut", "Valeur"], tablefmt="grid"))
            
            return metadonnees
        else:
            print(f"{Fore.RED}❌ Échec de la création de sauvegarde!")
            return None
    
    def demonstration_liste_et_statistiques(self):
        """Démonstration de listage et statistiques"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}📋 DÉMONSTRATION: Liste et Statistiques")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Lister les sauvegardes
        sauvegardes = self.systeme.lister_sauvegardes()
        afficher_liste_sauvegardes(sauvegardes)
        
        # Afficher les statistiques
        stats = self.systeme.obtenir_statistiques()
        afficher_statistiques(stats)
        
        if sauvegardes:
            return sauvegardes[0]  # Retourner la plus récente
        return None
    
    def demonstration_restauration(self, metadonnees):
        """Démonstration de restauration"""
        if not metadonnees:
            print(f"{Fore.YELLOW}⚠️ Aucune sauvegarde disponible pour la restauration")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🔄 DÉMONSTRATION: Restauration de Sauvegarde")
        print(f"{Fore.CYAN}{'='*60}")
        
        print(f"\n{Fore.YELLOW}📝 Paramètres de restauration:")
        print(f"   • ID de sauvegarde: {metadonnees.id}")
        print(f"   • Fichier source: {metadonnees.nom_fichier}")
        print(f"   • Chiffrement: {'🔒 Oui' if metadonnees.chiffre else '🔓 Non'}")
        print(f"   • Date de création: {metadonnees.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        dossier_restauration = self.dossier_demo / f"restauration_{metadonnees.id}"
        print(f"   • Destination: {dossier_restauration}")
        
        input(f"\n{Fore.MAGENTA}🎯 Appuyez sur Entrée pour commencer la restauration...")
        
        # Effectuer la restauration
        succes = self.systeme.restaurer_sauvegarde(
            metadonnees.id,
            mot_de_passe=self.mot_de_passe_demo if metadonnees.chiffre else None,
            dossier_destination=str(dossier_restauration)
        )
        
        if succes:
            print(f"\n{Fore.GREEN}✅ Restauration terminée avec succès!")
            
            # Vérifier les fichiers restaurés
            fichiers_restaures = list(dossier_restauration.rglob('*'))
            fichiers_seulement = [f for f in fichiers_restaures if f.is_file()]
            dossiers_seulement = [d for d in fichiers_restaures if d.is_dir()]
            
            print(f"\n📊 Résumé de la restauration:")
            donnees_restauration = [
                ["Dossier de destination", str(dossier_restauration)],
                ["Fichiers restaurés", f"{len(fichiers_seulement):,}"],
                ["Dossiers restaurés", f"{len(dossiers_seulement):,}"],
                ["Taille totale", formater_taille(sum(f.stat().st_size for f in fichiers_seulement))]
            ]
            
            from tabulate import tabulate
            print(tabulate(donnees_restauration, headers=["Attribut", "Valeur"], tablefmt="grid"))
            
            # Afficher quelques fichiers restaurés
            print(f"\n{Fore.YELLOW}📁 Aperçu des fichiers restaurés (premiers 10):")
            for i, fichier in enumerate(fichiers_seulement[:10]):
                chemin_relatif = fichier.relative_to(dossier_restauration)
                taille = formater_taille(fichier.stat().st_size)
                print(f"   {i+1:2d}. {chemin_relatif} ({taille})")
            
            if len(fichiers_seulement) > 10:
                print(f"   ... et {len(fichiers_seulement) - 10} fichiers supplémentaires")
            
            return True
        else:
            print(f"{Fore.RED}❌ Échec de la restauration!")
            return False
    
    def demonstration_rotation(self):
        """Démonstration de la rotation automatique"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🔄 DÉMONSTRATION: Rotation Automatique")
        print(f"{Fore.CYAN}{'='*60}")
        
        print(f"\n{Fore.YELLOW}📝 Configuration de rotation:")
        print(f"   • Maximum de sauvegardes: {self.systeme.config['rotation']['max_sauvegardes']}")
        print(f"   • Conservation en jours: {self.systeme.config['rotation']['conservation_jours']}")
        print(f"   • Rotation automatique: {'✅ Activée' if self.systeme.config['rotation']['rotation_auto'] else '❌ Désactivée'}")
        
        # Afficher l'état actuel
        sauvegardes_avant = self.systeme.lister_sauvegardes()
        print(f"\n📊 État actuel: {len(sauvegardes_avant)} sauvegarde(s)")
        
        if len(sauvegardes_avant) < self.systeme.config['rotation']['max_sauvegardes']:
            print(f"\n{Fore.YELLOW}🔄 Création de sauvegardes supplémentaires pour démontrer la rotation...")
            
            # Créer des sauvegardes supplémentaires
            for i in range(3):
                print(f"   Création de la sauvegarde {i+1}/3...")
                metadonnees = self.systeme.creer_sauvegarde()
                if metadonnees:
                    print(f"   ✅ Sauvegarde {metadonnees.id} créée")
                time.sleep(1)  # Petit délai pour différencier les timestamps
        
        # Afficher l'état après rotation
        sauvegardes_apres = self.systeme.lister_sauvegardes()
        print(f"\n📊 État après rotation: {len(sauvegardes_apres)} sauvegarde(s)")
        
        if len(sauvegardes_apres) <= self.systeme.config['rotation']['max_sauvegardes']:
            print(f"{Fore.GREEN}✅ Rotation automatique fonctionnelle!")
        
        afficher_liste_sauvegardes(sauvegardes_apres)
    
    def demonstration_fonctionnalites_avancees(self):
        """Démonstration des fonctionnalités avancées"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}⚙️ DÉMONSTRATION: Fonctionnalités Avancées")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Test des différents niveaux de compression
        print(f"\n{Fore.YELLOW}🗜️ Test des niveaux de compression:")
        
        niveaux_test = [1, 6, 9]  # Rapide, équilibré, maximum
        resultats_compression = []
        
        for niveau in niveaux_test:
            print(f"   📊 Test compression niveau {niveau}...")
            
            # Modifier temporairement la configuration
            niveau_original = self.systeme.config['sauvegarde']['compression_niveau']
            self.systeme.config['sauvegarde']['compression_niveau'] = niveau
            self.systeme.compression.niveau = niveau
            
            # Créer une sauvegarde test
            debut = time.time()
            metadonnees = self.systeme.creer_sauvegarde()
            fin = time.time()
            
            if metadonnees:
                ratio = (1 - metadonnees.taille_compressee / metadonnees.taille_originale) * 100
                resultats_compression.append([
                    f"Niveau {niveau}",
                    formater_taille(metadonnees.taille_originale),
                    formater_taille(metadonnees.taille_compressee),
                    f"{ratio:.1f}%",
                    f"{fin - debut:.2f}s"
                ])
            
            # Restaurer la configuration
            self.systeme.config['sauvegarde']['compression_niveau'] = niveau_original
            self.systeme.compression.niveau = niveau_original
        
        if resultats_compression:
            from tabulate import tabulate
            print(f"\n📊 Résultats des tests de compression:")
            headers = ["Niveau", "Taille Orig.", "Taille Comp.", "Ratio", "Durée"]
            print(tabulate(resultats_compression, headers=headers, tablefmt="grid"))
        
        # Test de vérification d'intégrité
        print(f"\n{Fore.YELLOW}🔍 Test de vérification d'intégrité:")
        
        sauvegardes = self.systeme.lister_sauvegardes(limite=1)
        if sauvegardes and sauvegardes[0].hash_integrite:
            sauvegarde = sauvegardes[0]
            print(f"   • Sauvegarde: {sauvegarde.id}")
            print(f"   • Hash stocké: {sauvegarde.hash_integrite[:32]}...")
            print(f"   {Fore.GREEN}✅ Hash d'intégrité disponible - Vérification automatique lors de la restauration")
        else:
            print(f"   {Fore.YELLOW}⚠️ Aucune sauvegarde avec hash d'intégrité trouvée")
        
        # Information sur les exclusions
        print(f"\n{Fore.YELLOW}🚫 Configuration des exclusions:")
        exclusions = self.systeme.config['sauvegarde']['exclusions']
        for exclusion in exclusions:
            print(f"   • {exclusion}")
        
        print(f"\n{Fore.GREEN}✅ Démonstration des fonctionnalités avancées terminée!")
    
    def cleanup(self):
        """Nettoyer les fichiers de démonstration"""
        if self.dossier_demo and self.dossier_demo.exists():
            try:
                shutil.rmtree(self.dossier_demo)
                print(f"{Fore.GREEN}🧹 Environnement de démonstration nettoyé")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Erreur lors du nettoyage: {e}")


def demo_rapide():
    """Démonstration rapide et automatisée"""
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🚀 DÉMONSTRATION RAPIDE - Système de Sauvegarde Chiffré")
    print(f"{Fore.CYAN}{'='*80}")
    
    demo = DemonstrationsInteractives()
    
    try:
        # Setup
        demo.setup_environnement_demo()
        
        # Créer quelques sauvegardes
        print(f"\n{Fore.YELLOW}🔄 Création de sauvegardes de démonstration...")
        for i in range(3):
            print(f"   Sauvegarde {i+1}/3...")
            metadonnees = demo.systeme.creer_sauvegarde(mot_de_passe=demo.mot_de_passe_demo)
            if metadonnees:
                print(f"   ✅ ID: {metadonnees.id}")
            time.sleep(0.5)
        
        # Statistiques finales
        print(f"\n{Fore.CYAN}📊 RÉSUMÉ FINAL")
        print(f"{Fore.CYAN}{'='*40}")
        
        sauvegardes = demo.systeme.lister_sauvegardes()
        stats = demo.systeme.obtenir_statistiques()
        
        donnees_finales = [
            ["Sauvegardes créées", f"{len(sauvegardes):,}"],
            ["Taille totale sauvegardée", formater_taille(stats.taille_totale)],
            ["Taille originale totale", formater_taille(stats.taille_originale_totale)],
            ["Ratio compression moyen", f"{stats.ratio_compression_moyen:.1f}%"],
            ["Durée moyenne par sauvegarde", f"{stats.duree_moyenne:.2f}s"],
            ["Dernière sauvegarde", stats.derniere_sauvegarde.strftime('%H:%M:%S') if stats.derniere_sauvegarde else "N/A"]
        ]
        
        from tabulate import tabulate
        print(tabulate(donnees_finales, headers=["Métrique", "Valeur"], tablefmt="grid"))
        
        print(f"\n{Fore.GREEN}✅ Démonstration rapide terminée avec succès!")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la démonstration: {e}")
    finally:
        demo.cleanup()


def demo_interactive():
    """Démonstration interactive complète"""
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🎮 DÉMONSTRATION INTERACTIVE - Système de Sauvegarde Chiffré")
    print(f"{Fore.CYAN}{'='*80}")
    
    print(f"\n{Fore.YELLOW}Cette démonstration vous guidera à travers toutes les fonctionnalités:")
    print(f"✅ Création d'un projet exemple")
    print(f"✅ Sauvegarde avec chiffrement AES-256")
    print(f"✅ Compression intelligente")
    print(f"✅ Gestion des exclusions")
    print(f"✅ Rotation automatique")
    print(f"✅ Restauration complète")
    print(f"✅ Statistiques détaillées")
    print(f"✅ Fonctionnalités avancées")
    
    reponse = input(f"\n{Fore.MAGENTA}🚀 Voulez-vous continuer? (o/N): ").lower().strip()
    if reponse not in ['o', 'oui', 'y', 'yes']:
        print(f"{Fore.YELLOW}👋 Démonstration annulée")
        return
    
    demo = DemonstrationsInteractives()
    
    try:
        # 1. Setup environnement
        demo.setup_environnement_demo()
        input(f"\n{Fore.MAGENTA}📋 Environnement prêt. Appuyez sur Entrée pour continuer...")
        
        # 2. Création de sauvegarde
        metadonnees = demo.demonstration_creation_sauvegarde()
        
        # 3. Liste et statistiques
        if metadonnees:
            input(f"\n{Fore.MAGENTA}📊 Appuyez sur Entrée pour voir la liste et les statistiques...")
            sauvegarde_recente = demo.demonstration_liste_et_statistiques()
            
            # 4. Restauration
            input(f"\n{Fore.MAGENTA}🔄 Appuyez sur Entrée pour démontrer la restauration...")
            demo.demonstration_restauration(sauvegarde_recente)
            
            # 5. Rotation
            input(f"\n{Fore.MAGENTA}🔄 Appuyez sur Entrée pour démontrer la rotation...")
            demo.demonstration_rotation()
            
            # 6. Fonctionnalités avancées
            input(f"\n{Fore.MAGENTA}⚙️ Appuyez sur Entrée pour les fonctionnalités avancées...")
            demo.demonstration_fonctionnalites_avancees()
        
        print(f"\n{Fore.GREEN}🌟 Démonstration interactive terminée avec succès!")
        print(f"{Fore.CYAN}💡 Le système de sauvegarde chiffré est prêt pour la production!")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la démonstration: {e}")
    finally:
        demo.cleanup()


def demo_complet():
    """Point d'entrée principal pour les démonstrations"""
    print(f"{Fore.CYAN}🎯 SYSTÈME DE SAUVEGARDE CHIFFRÉ - Démonstrations")
    print(f"{Fore.CYAN}{'='*60}")
    
    print(f"\n{Fore.YELLOW}Choisissez le type de démonstration:")
    print(f"1. 🚀 Démonstration rapide (automatique)")
    print(f"2. 🎮 Démonstration interactive (guidée)")
    print(f"3. ❌ Quitter")
    
    while True:
        choix = input(f"\n{Fore.MAGENTA}Votre choix (1-3): ").strip()
        
        if choix == '1':
            demo_rapide()
            break
        elif choix == '2':
            demo_interactive()
            break
        elif choix == '3':
            print(f"{Fore.YELLOW}👋 Au revoir!")
            break
        else:
            print(f"{Fore.RED}❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")


if __name__ == "__main__":
    demo_complet()