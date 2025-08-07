#!/usr/bin/env python3
"""
Tests unitaires pour le Système de Sauvegarde Chiffré

Tests exhaustifs de toutes les fonctionnalités du système de sauvegarde
avec chiffrement AES, compression et rotation automatique.

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
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajouter le module principal au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sauvegarde_chiffree import (
    SystemeSauvegardeChiffre, GestionnaireCryptographie, 
    GestionnaireCompression, GestionnaireRotation,
    MetadonneesSauvegarde, StatistiquesSauvegarde,
    formater_taille
)


class TestGestionnaireCryptographie(unittest.TestCase):
    """Tests pour le gestionnaire de cryptographie"""
    
    def setUp(self):
        self.crypto = GestionnaireCryptographie(iterations=1000)  # Moins d'itérations pour les tests
        self.mot_de_passe = "test_password_123"
        self.donnees_test = b"Ceci est un test de donnees a chiffrer"
    
    def test_generation_salt(self):
        """Test génération de salt"""
        salt1 = self.crypto.generer_salt(32)
        salt2 = self.crypto.generer_salt(32)
        
        self.assertEqual(len(salt1), 32)
        self.assertEqual(len(salt2), 32)
        self.assertNotEqual(salt1, salt2)  # Salts doivent être uniques
    
    def test_generation_cle_depuis_mot_de_passe(self):
        """Test génération de clé depuis mot de passe"""
        salt = self.crypto.generer_salt(32)
        cle1 = self.crypto.generer_cle_depuis_mot_de_passe(self.mot_de_passe, salt)
        cle2 = self.crypto.generer_cle_depuis_mot_de_passe(self.mot_de_passe, salt)
        
        self.assertEqual(cle1, cle2)  # Même mot de passe + salt = même clé
        
        # Test avec salt différent
        salt_different = self.crypto.generer_salt(32)
        cle3 = self.crypto.generer_cle_depuis_mot_de_passe(self.mot_de_passe, salt_different)
        self.assertNotEqual(cle1, cle3)  # Salt différent = clé différente
    
    def test_chiffrement_dechiffrement(self):
        """Test chiffrement et déchiffrement"""
        salt = self.crypto.generer_salt(32)
        cle = self.crypto.generer_cle_depuis_mot_de_passe(self.mot_de_passe, salt)
        
        # Chiffrer
        donnees_chiffrees = self.crypto.chiffrer_donnees(self.donnees_test, cle)
        self.assertNotEqual(donnees_chiffrees, self.donnees_test)
        
        # Déchiffrer
        donnees_dechiffrees = self.crypto.dechiffrer_donnees(donnees_chiffrees, cle)
        self.assertEqual(donnees_dechiffrees, self.donnees_test)
    
    def test_chiffrement_avec_mauvaise_cle(self):
        """Test déchiffrement avec une mauvaise clé"""
        salt = self.crypto.generer_salt(32)
        cle_correcte = self.crypto.generer_cle_depuis_mot_de_passe(self.mot_de_passe, salt)
        cle_incorrecte = self.crypto.generer_cle_depuis_mot_de_passe("mauvais_password", salt)
        
        donnees_chiffrees = self.crypto.chiffrer_donnees(self.donnees_test, cle_correcte)
        
        # Déchiffrement avec mauvaise clé doit lever une exception
        with self.assertRaises(Exception):
            self.crypto.dechiffrer_donnees(donnees_chiffrees, cle_incorrecte)
    
    def test_hash_integrite(self):
        """Test calcul de hash d'intégrité"""
        hash1 = self.crypto.calculer_hash_integrite(self.donnees_test)
        hash2 = self.crypto.calculer_hash_integrite(self.donnees_test)
        
        self.assertEqual(hash1, hash2)  # Même données = même hash
        self.assertEqual(len(hash1), 64)  # SHA-256 = 64 caractères hex
        
        # Données différentes = hash différent
        hash3 = self.crypto.calculer_hash_integrite(b"donnees differentes")
        self.assertNotEqual(hash1, hash3)


class TestGestionnaireCompression(unittest.TestCase):
    """Tests pour le gestionnaire de compression"""
    
    def setUp(self):
        self.compression = GestionnaireCompression(niveau=6)
        self.dossier_temp = Path(tempfile.mkdtemp())
        self.fichier_zip_temp = Path(tempfile.mktemp(suffix='.zip'))
        
        # Créer des fichiers de test
        (self.dossier_temp / "test1.txt").write_text("Contenu du fichier test 1" * 100)
        (self.dossier_temp / "test2.txt").write_text("Contenu du fichier test 2" * 50)
        (self.dossier_temp / "subdir").mkdir()
        (self.dossier_temp / "subdir" / "test3.txt").write_text("Fichier dans sous-dossier")
        
        # Fichier à exclure
        (self.dossier_temp / "fichier.tmp").write_text("Fichier temporaire")
        (self.dossier_temp / "__pycache__").mkdir()
        (self.dossier_temp / "__pycache__" / "cache.pyc").write_text("Cache Python")
    
    def tearDown(self):
        # Nettoyer les fichiers temporaires
        if self.dossier_temp.exists():
            shutil.rmtree(self.dossier_temp)
        if self.fichier_zip_temp.exists():
            self.fichier_zip_temp.unlink()
    
    def test_compression_dossier(self):
        """Test compression d'un dossier"""
        taille_originale, taille_compressee = self.compression.comprimer_dossier(
            self.dossier_temp, self.fichier_zip_temp
        )
        
        self.assertGreater(taille_originale, 0)
        self.assertGreater(taille_compressee, 0)
        self.assertLess(taille_compressee, taille_originale)  # Compression effective
        self.assertTrue(self.fichier_zip_temp.exists())
    
    def test_exclusions(self):
        """Test exclusion de fichiers/dossiers"""
        exclusions = ["*.tmp", "__pycache__"]
        
        taille_originale, taille_compressee = self.compression.comprimer_dossier(
            self.dossier_temp, self.fichier_zip_temp, exclusions
        )
        
        # Vérifier que l'archive ne contient pas les fichiers exclus
        import zipfile
        with zipfile.ZipFile(self.fichier_zip_temp, 'r') as zipf:
            noms_fichiers = zipf.namelist()
            
            # Fichiers exclus ne doivent pas être présents
            self.assertNotIn("fichier.tmp", noms_fichiers)
            self.assertNotIn("__pycache__/cache.pyc", noms_fichiers)
            
            # Fichiers normaux doivent être présents
            self.assertIn("test1.txt", noms_fichiers)
            self.assertIn("test2.txt", noms_fichiers)
            self.assertIn("subdir/test3.txt", noms_fichiers)
    
    def test_est_exclu(self):
        """Test fonction d'exclusion"""
        exclusions = ["*.tmp", "*.log", "__pycache__", "node_modules"]
        
        self.assertTrue(self.compression._est_exclu("fichier.tmp", exclusions))
        self.assertTrue(self.compression._est_exclu("debug.log", exclusions))
        self.assertTrue(self.compression._est_exclu("__pycache__", exclusions))
        self.assertTrue(self.compression._est_exclu("node_modules", exclusions))
        
        self.assertFalse(self.compression._est_exclu("fichier.txt", exclusions))
        self.assertFalse(self.compression._est_exclu("script.py", exclusions))


class TestGestionnaireRotation(unittest.TestCase):
    """Tests pour le gestionnaire de rotation"""
    
    def setUp(self):
        self.rotation = GestionnaireRotation(max_sauvegardes=3, conservation_jours=7)
        self.dossier_temp = Path(tempfile.mkdtemp())
        
        # Créer des fichiers de sauvegarde fictifs
        timestamps = [
            datetime.now() - timedelta(days=10),  # Très ancien
            datetime.now() - timedelta(days=5),   # Ancien
            datetime.now() - timedelta(days=2),   # Récent
            datetime.now() - timedelta(hours=1),  # Très récent
            datetime.now() - timedelta(minutes=30) # Le plus récent
        ]
        
        for i, ts in enumerate(timestamps):
            backup_id = ts.strftime("%Y%m%d_%H%M%S")
            
            # Créer fichier de sauvegarde
            fichier_backup = self.dossier_temp / f"backup_{backup_id}.zip.enc"
            fichier_backup.write_text(f"Contenu sauvegarde {i}")
            
            # Créer fichier métadonnées
            fichier_metadata = self.dossier_temp / f"backup_{backup_id}.json"
            fichier_metadata.write_text(f'{{"id": "{backup_id}"}}')
            
            # Modifier les temps de fichier
            timestamp_unix = ts.timestamp()
            os.utime(fichier_backup, (timestamp_unix, timestamp_unix))
            os.utime(fichier_metadata, (timestamp_unix, timestamp_unix))
    
    def tearDown(self):
        if self.dossier_temp.exists():
            shutil.rmtree(self.dossier_temp)
    
    def test_rotation_par_nombre(self):
        """Test rotation par nombre maximum de sauvegardes"""
        # Avant rotation: 5 fichiers
        fichiers_avant = list(self.dossier_temp.glob("backup_*.zip.enc"))
        self.assertEqual(len(fichiers_avant), 5)
        
        # Appliquer rotation (max 3)
        fichiers_supprimes = self.rotation.appliquer_rotation(self.dossier_temp)
        
        # Après rotation: 3 fichiers maximum
        fichiers_apres = list(self.dossier_temp.glob("backup_*.zip.enc"))
        self.assertLessEqual(len(fichiers_apres), 3)
        self.assertGreater(len(fichiers_supprimes), 0)
    
    def test_rotation_par_anciennete(self):
        """Test rotation par ancienneté"""
        rotation_ancienne = GestionnaireRotation(max_sauvegardes=10, conservation_jours=3)
        
        fichiers_supprimes = rotation_ancienne.appliquer_rotation(self.dossier_temp)
        
        # Les fichiers de plus de 3 jours doivent être supprimés
        fichiers_restants = list(self.dossier_temp.glob("backup_*.zip.enc"))
        
        for fichier in fichiers_restants:
            mtime = datetime.fromtimestamp(fichier.stat().st_mtime)
            age = datetime.now() - mtime
            self.assertLessEqual(age.days, 3)


class TestMetadonneesSauvegarde(unittest.TestCase):
    """Tests pour les métadonnées de sauvegarde"""
    
    def test_creation_metadonnees(self):
        """Test création des métadonnées"""
        metadonnees = MetadonneesSauvegarde(
            id="test_123",
            timestamp=datetime.now(),
            nom_fichier="backup_test.zip.enc",
            taille_originale=1000,
            taille_compressee=800,
            taille_chiffree=850,
            fichiers_inclus=10,
            dossiers_inclus=2,
            dossier_source="/test/source",
            duree_sauvegarde=5.5,
            hash_integrite="abc123",
            chiffre=True,
            compresse=True
        )
        
        self.assertEqual(metadonnees.id, "test_123")
        self.assertTrue(metadonnees.chiffre)
        self.assertTrue(metadonnees.compresse)
    
    def test_serialisation_json(self):
        """Test sérialisation/désérialisation JSON"""
        timestamp_original = datetime.now()
        metadonnees_original = MetadonneesSauvegarde(
            id="test_serialize",
            timestamp=timestamp_original,
            nom_fichier="test.zip",
            taille_originale=1000,
            taille_compressee=800,
            taille_chiffree=850,
            fichiers_inclus=5,
            dossiers_inclus=1,
            dossier_source="/test",
            duree_sauvegarde=2.5,
            hash_integrite="hash123",
            chiffre=False,
            compresse=True
        )
        
        # Sérialiser
        dict_data = metadonnees_original.to_dict()
        self.assertIsInstance(dict_data['timestamp'], str)
        
        # Désérialiser
        metadonnees_deserialize = MetadonneesSauvegarde.from_dict(dict_data)
        
        self.assertEqual(metadonnees_original.id, metadonnees_deserialize.id)
        self.assertEqual(metadonnees_original.timestamp, metadonnees_deserialize.timestamp)
        self.assertEqual(metadonnees_original.chiffre, metadonnees_deserialize.chiffre)


class TestSystemeSauvegardeChiffre(unittest.TestCase):
    """Tests pour le système principal"""
    
    def setUp(self):
        self.dossier_temp = Path(tempfile.mkdtemp())
        self.dossier_source = self.dossier_temp / "source"
        self.dossier_backup = self.dossier_temp / "backups"
        
        # Créer structure de test
        self.dossier_source.mkdir()  
        self.dossier_backup.mkdir()
        
        # Créer des fichiers de test
        (self.dossier_source / "fichier1.txt").write_text("Contenu fichier 1 " * 50)
        (self.dossier_source / "fichier2.txt").write_text("Contenu fichier 2 " * 30)
        (self.dossier_source / "subdir").mkdir()
        (self.dossier_source / "subdir" / "fichier3.txt").write_text("Fichier sous-dossier")
        
        # Configuration de test
        self.config_test = {
            "sauvegarde": {
                "dossier_source": str(self.dossier_source),
                "dossier_destination": str(self.dossier_backup),
                "nom_base": "test_backup",
                "compression_niveau": 6,
                "chiffrement_actif": True,
                "exclusions": ["*.tmp"]
            },
            "rotation": {
                "max_sauvegardes": 5,
                "conservation_jours": 30,
                "rotation_auto": True
            },
            "securite": {
                "iterations_pbkdf2": 1000,  # Moins pour les tests
                "longueur_salt": 32,
                "verification_integrite": True
            },
            "planning": {
                "actif": False
            }
        }
        
        # Créer fichier de configuration temporaire
        self.config_file = self.dossier_temp / "test_config.json"
        with open(self.config_file, 'w') as f:
            json.dump(self.config_test, f)
            
        self.systeme = SystemeSauvegardeChiffre(str(self.config_file))
    
    def tearDown(self):
        if hasattr(self, 'systeme'):
            self.systeme.arreter_planification()
        if self.dossier_temp.exists():
            shutil.rmtree(self.dossier_temp)
    
    def test_chargement_configuration(self):
        """Test chargement de la configuration"""
        self.assertEqual(self.systeme.config['sauvegarde']['nom_base'], "test_backup")
        self.assertEqual(self.systeme.config['rotation']['max_sauvegardes'], 5)
    
    def test_configuration_par_defaut(self):
        """Test utilisation de la configuration par défaut"""
        # Supprimer le fichier de config
        self.config_file.unlink()
        
        systeme_defaut = SystemeSauvegardeChiffre(str(self.config_file))
        
        # Doit utiliser la config par défaut
        self.assertEqual(systeme_defaut.config['sauvegarde']['nom_base'], "backup")
        self.assertEqual(systeme_defaut.config['rotation']['max_sauvegardes'], 10)
    
    def test_creation_sauvegarde_sans_chiffrement(self):
        """Test création de sauvegarde sans chiffrement"""
        # Désactiver le chiffrement
        self.systeme.config['sauvegarde']['chiffrement_actif'] = False
        
        metadonnees = self.systeme.creer_sauvegarde()
        
        self.assertIsNotNone(metadonnees)
        self.assertFalse(metadonnees.chiffre)
        self.assertTrue(metadonnees.compresse)
        self.assertGreater(metadonnees.taille_originale, 0)
        self.assertGreater(metadonnees.fichiers_inclus, 0)
        
        # Vérifier que le fichier existe
        fichier_backup = self.dossier_backup / metadonnees.nom_fichier
        self.assertTrue(fichier_backup.exists())
    
    def test_creation_sauvegarde_avec_chiffrement(self):
        """Test création de sauvegarde avec chiffrement"""
        mot_de_passe = "test_password_123"
        
        metadonnees = self.systeme.creer_sauvegarde(mot_de_passe=mot_de_passe)
        
        self.assertIsNotNone(metadonnees)
        self.assertTrue(metadonnees.chiffre)
        self.assertTrue(metadonnees.compresse)
        self.assertGreater(metadonnees.taille_chiffree, 0)
        self.assertNotEqual(metadonnees.hash_integrite, "")
        
        # Vérifier que le fichier chiffré existe
        fichier_backup = self.dossier_backup / metadonnees.nom_fichier
        self.assertTrue(fichier_backup.exists())
    
    def test_liste_sauvegardes(self):
        """Test listage des sauvegardes"""
        # Créer quelques sauvegardes
        self.systeme.config['sauvegarde']['chiffrement_actif'] = False
        
        metadonnees1 = self.systeme.creer_sauvegarde()
        time.sleep(1)  # Attendre pour différencier les timestamps
        metadonnees2 = self.systeme.creer_sauvegarde()
        
        # Lister
        sauvegardes = self.systeme.lister_sauvegardes()
        
        self.assertEqual(len(sauvegardes), 2)
        
        # Vérifier l'ordre (plus récent en premier)
        self.assertGreater(sauvegardes[0].timestamp, sauvegardes[1].timestamp)
    
    def test_restauration_sans_chiffrement(self):
        """Test restauration d'une sauvegarde non chiffrée"""
        # Créer sauvegarde
        self.systeme.config['sauvegarde']['chiffrement_actif'] = False
        metadonnees = self.systeme.creer_sauvegarde()
        
        # Restaurer
        dossier_restauration = self.dossier_temp / "restore_test"
        succes = self.systeme.restaurer_sauvegarde(
            metadonnees.id, 
            dossier_destination=str(dossier_restauration)
        )
        
        self.assertTrue(succes)
        self.assertTrue(dossier_restauration.exists())
        
        # Vérifier que les fichiers ont été restaurés
        self.assertTrue((dossier_restauration / "fichier1.txt").exists())
        self.assertTrue((dossier_restauration / "fichier2.txt").exists())
        self.assertTrue((dossier_restauration / "subdir" / "fichier3.txt").exists())
        
        # Vérifier le contenu
        contenu = (dossier_restauration / "fichier1.txt").read_text()
        self.assertIn("Contenu fichier 1", contenu)
    
    def test_restauration_avec_chiffrement(self):
        """Test restauration d'une sauvegarde chiffrée"""
        mot_de_passe = "test_restore_password"
        
        # Créer sauvegarde chiffrée
        metadonnees = self.systeme.creer_sauvegarde(mot_de_passe=mot_de_passe)
        
        # Restaurer
        dossier_restauration = self.dossier_temp / "restore_encrypted"
        succes = self.systeme.restaurer_sauvegarde(
            metadonnees.id,
            mot_de_passe=mot_de_passe,
            dossier_destination=str(dossier_restauration)
        )
        
        self.assertTrue(succes)
        self.assertTrue(dossier_restauration.exists())
        
        # Vérifier que les fichiers ont été restaurés
        self.assertTrue((dossier_restauration / "fichier1.txt").exists())
        self.assertTrue((dossier_restauration / "subdir" / "fichier3.txt").exists())
    
    def test_restauration_mauvais_mot_de_passe(self):
        """Test restauration avec mauvais mot de passe"""
        mot_de_passe_correct = "password_correct"
        mot_de_passe_incorrect = "password_incorrect"
        
        # Créer sauvegarde chiffrée
        metadonnees = self.systeme.creer_sauvegarde(mot_de_passe=mot_de_passe_correct)
        
        # Tenter restauration avec mauvais mot de passe
        dossier_restauration = self.dossier_temp / "restore_fail"
        succes = self.systeme.restaurer_sauvegarde(  
            metadonnees.id,
            mot_de_passe=mot_de_passe_incorrect,
            dossier_destination=str(dossier_restauration)
        )
        
        self.assertFalse(succes)
    
    def test_statistiques(self):
        """Test calcul des statistiques"""
        # Créer quelques sauvegardes
        self.systeme.config['sauvegarde']['chiffrement_actif'] = False
        
        metadonnees1 = self.systeme.creer_sauvegarde()
        time.sleep(1)
        metadonnees2 = self.systeme.creer_sauvegarde()
        
        # Obtenir statistiques
        stats = self.systeme.obtenir_statistiques()
        
        self.assertEqual(stats.nombre_total, 2)
        self.assertGreater(stats.taille_totale, 0)
        self.assertGreater(stats.taille_originale_totale, 0)
        self.assertGreater(stats.ratio_compression_moyen, 0)
        self.assertIsNotNone(stats.derniere_sauvegarde)
        self.assertIsNotNone(stats.plus_ancienne)
    
    def test_compter_elements(self):
        """Test comptage des fichiers et dossiers"""
        fichiers, dossiers = self.systeme._compter_elements(self.dossier_source)
        
        # 3 fichiers: fichier1.txt, fichier2.txt, subdir/fichier3.txt
        # 1 dossier: subdir
        self.assertEqual(fichiers, 3)
        self.assertEqual(dossiers, 1)
    
    @patch('schedule.every')
    def test_planification(self, mock_schedule):
        """Test système de planification"""
        # Activer la planification
        self.systeme.config['planning']['actif'] = True
        self.systeme.config['planning']['frequence'] = 'daily'
        self.systeme.config['planning']['heure'] = '02:00'
        
        # Mock du schedule
        mock_day = MagicMock()
        mock_schedule.return_value.day = mock_day
        mock_day.at.return_value.do = MagicMock()
        
        # Démarrer planification
        self.systeme.demarrer_planification()
        
        self.assertTrue(self.systeme.scheduler_actif)
        mock_day.at.assert_called_with('02:00')
    
    def test_source_inexistant(self):
        """Test avec dossier source inexistant"""
        metadonnees = self.systeme.creer_sauvegarde(
            dossier_source="/dossier/inexistant"
        )
        
        self.assertIsNone(metadonnees)


class TestFonctionsUtilitaires(unittest.TestCase):
    """Tests pour les fonctions utilitaires"""
    
    def test_formater_taille(self):
        """Test formatage des tailles"""
        self.assertEqual(formater_taille(512), "512.0 B")
        self.assertEqual(formater_taille(1024), "1.0 KB")
        self.assertEqual(formater_taille(1048576), "1.0 MB")
        self.assertEqual(formater_taille(1073741824), "1.0 GB")
        
        # Test avec valeurs non rondes
        self.assertEqual(formater_taille(1536), "1.5 KB")
        self.assertEqual(formater_taille(2621440), "2.5 MB")


class TestIntegrationComplete(unittest.TestCase):
    """Tests d'intégration complète"""
    
    def setUp(self):
        self.dossier_temp = Path(tempfile.mkdtemp())
        self.setup_environnement_test()
    
    def tearDown(self):
        if self.dossier_temp.exists():
            shutil.rmtree(self.dossier_temp)
    
    def setup_environnement_test(self):
        """Créer un environnement de test complet"""
        # Structure de dossiers
        self.dossier_source = self.dossier_temp / "data"
        self.dossier_backups = self.dossier_temp / "backups"
        
        self.dossier_source.mkdir(parents=True)
        
        # Créer une structure complexe
        (self.dossier_source / "documents").mkdir()
        (self.dossier_source / "images").mkdir()
        (self.dossier_source / "code").mkdir()
        (self.dossier_source / "temp").mkdir()
        
        # Fichiers de différents types
        (self.dossier_source / "readme.txt").write_text("Documentation du projet" * 100)
        (self.dossier_source / "config.json").write_text('{"setting": "value"}')
        (self.dossier_source / "documents" / "rapport.docx").write_text("Contenu rapport" * 200)
        (self.dossier_source / "images" / "photo.jpg").write_bytes(b"fake_image_data" * 1000)
        (self.dossier_source / "code" / "script.py").write_text("print('Hello World')" * 50)
        
        # Fichiers à exclure
        (self.dossier_source / "temp" / "cache.tmp").write_text("Fichier temporaire")
        (self.dossier_source / "debug.log").write_text("Logs de debug")
        
        # Configuration
        self.config_complete = {
            "sauvegarde": {
                "dossier_source": str(self.dossier_source),
                "dossier_destination": str(self.dossier_backups),
                "nom_base": "backup_integration",
                "compression_niveau": 9,
                "chiffrement_actif": True,
                "exclusions": ["*.tmp", "*.log", "temp"]
            },
            "rotation": {
                "max_sauvegardes": 3,
                "conservation_jours": 15,
                "rotation_auto": True
            },
            "securite": {
                "iterations_pbkdf2": 1000,
                "longueur_salt": 32,
                "verification_integrite": True
            },
            "planning": {
                "actif": False
            }
        }
        
        self.config_file = self.dossier_temp / "config_integration.json"
        with open(self.config_file, 'w') as f:
            json.dump(self.config_complete, f)
    
    def test_cycle_complet_sauvegarde_restauration(self):
        """Test d'un cycle complet sauvegarde -> restauration"""
        systeme = SystemeSauvegardeChiffre(str(self.config_file))
        mot_de_passe = "integration_test_password_2025"
        
        # Étape 1: Créer sauvegarde
        print("🔄 Test d'intégration: Création de sauvegarde...")
        metadonnees = systeme.creer_sauvegarde(mot_de_passe=mot_de_passe)
        
        self.assertIsNotNone(metadonnees)
        self.assertTrue(metadonnees.chiffre)
        self.assertGreater(metadonnees.fichiers_inclus, 0)
        self.assertGreater(metadonnees.taille_originale, 0)
        
        # Vérifier que les exclusions ont fonctionné
        # (on ne peut pas facilement vérifier le contenu de l'archive chiffrée,
        # mais on le vérifiera lors de la restauration)
        
        # Étape 2: Lister sauvegardes
        sauvegardes = systeme.lister_sauvegardes()
        self.assertEqual(len(sauvegardes), 1)
        self.assertEqual(sauvegardes[0].id, metadonnees.id)
        
        # Étape 3: Statistiques
        stats = systeme.obtenir_statistiques()
        self.assertEqual(stats.nombre_total, 1)
        self.assertGreater(stats.ratio_compression_moyen, 0)
        
        # Étape 4: Restauration
        print("🔄 Test d'intégration: Restauration...")
        dossier_restore = self.dossier_temp / "restored_data"
        succes = systeme.restaurer_sauvegarde(
            metadonnees.id,
            mot_de_passe=mot_de_passe,
            dossier_destination=str(dossier_restore)
        )
        
        self.assertTrue(succes)
        
        # Étape 5: Vérifier les fichiers restaurés
        self.assertTrue((dossier_restore / "readme.txt").exists())
        self.assertTrue((dossier_restore / "config.json").exists())
        self.assertTrue((dossier_restore / "documents" / "rapport.docx").exists())
        self.assertTrue((dossier_restore / "images" / "photo.jpg").exists())
        self.assertTrue((dossier_restore / "code" / "script.py").exists())
        
        # Vérifier que les fichiers exclus ne sont PAS restaurés
        self.assertFalse((dossier_restore / "debug.log").exists())
        self.assertFalse((dossier_restore / "temp" / "cache.tmp").exists())
        
        # Vérifier l'intégrité du contenu 
        contenu_readme = (dossier_restore / "readme.txt").read_text()
        self.assertIn("Documentation du projet", contenu_readme)
        
        contenu_config = (dossier_restore / "config.json").read_text()
        self.assertIn("setting", contenu_config)
        
        print("✅ Test d'intégration complet réussi!")
    
    def test_rotation_automatique(self):
        """Test de la rotation automatique"""
        systeme = SystemeSauvegardeChiffre(str(self.config_file))
        
        # Créer plus de sauvegardes que le maximum autorisé
        sauvegardes_creees = []
        for i in range(5):  # Max configuré: 3
            metadonnees = systeme.creer_sauvegarde()
            if metadonnees:
                sauvegardes_creees.append(metadonnees)
            time.sleep(0.1)  # Petit délai pour différencier les timestamps
        
        # Vérifier que la rotation a eu lieu
        sauvegardes_finales = systeme.lister_sauvegardes()
        self.assertLessEqual(len(sauvegardes_finales), 3)  # Maximum configuré
        
        # Vérifier que ce sont les plus récentes qui sont conservées
        if len(sauvegardes_finales) > 1:
            for i in range(len(sauvegardes_finales) - 1):
                self.assertGreater(
                    sauvegardes_finales[i].timestamp,
                    sauvegardes_finales[i + 1].timestamp
                )
    
    def test_gestion_erreurs(self):
        """Test de la gestion d'erreurs"""
        systeme = SystemeSauvegardeChiffre(str(self.config_file))
        
        # Test avec ID inexistant
        succes = systeme.restaurer_sauvegarde("inexistant_123")
        self.assertFalse(succes)
        
        # Test avec dossier source inexistant
        metadonnees = systeme.creer_sauvegarde(dossier_source="/inexistant")
        self.assertIsNone(metadonnees)


def run_all_tests():
    """Exécuter tous les tests avec rapport détaillé"""
    print("🧪 Démarrage des tests du Système de Sauvegarde Chiffré\n")
    
    # Créer une suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter toutes les classes de test
    test_classes = [
        TestGestionnaireCryptographie,
        TestGestionnaireCompression, 
        TestGestionnaireRotation,
        TestMetadonneesSauvegarde,
        TestSystemeSauvegardeChiffre,
        TestFonctionsUtilitaires,
        TestIntegrationComplete
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Rapport final
    print("\n" + "="*80)
    print("📊 RAPPORT FINAL DES TESTS")
    print("="*80)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"✅ Succès: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Échecs: {len(result.failures)}")
    print(f"🚨 Erreurs: {len(result.errors)}")    
    
    if result.failures:
        print("\n🔍 DÉTAILS DES ÉCHECS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print("\n🚨 DÉTAILS DES ERREURS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(chr(10))[-2]}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎯 Taux de réussite: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🌟 EXCELLENT - Système prêt pour la production!")
    elif success_rate >= 90:
        print("✅ TRÈS BIEN - Quelques améliorations mineures possibles")
    elif success_rate >= 80:
        print("⚠️ CORRECT - Correction des problèmes recommandée")
    else:
        print("❌ PROBLÉMATIQUE - Corrections majeures nécessaires")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Permettre l'exécution de tests individuels ou complets
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        success = run_all_tests()
        sys.exit(0 if success else 1)
    else:
        unittest.main(verbosity=2)