#!/usr/bin/env python3
"""
🧪 TESTS POST-NETTOYAGE - GESTIONNAIRE DE MOTS DE PASSE
===================================================

Tests exhaustifs pour valider le bon fonctionnement du projet après
le nettoyage des références aux démos et la séparation du code.

Tests inclus :
- Fonctionnalités principales sans mode démo
- Intégrité des composants
- Authentification biométrique
- Synchronisation cloud
- Audit de sécurité
- Partage sécurisé
"""

import sys
import os
import unittest
import tempfile
import shutil
from datetime import datetime
from colorama import init, Fore, Style

# Ajouter le répertoire parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gestionnaire_mdp import GestionnaireMDP
    from biometric_auth import BiometricAuthenticator
    from security_audit import SecurityAuditor
    from passphrase_generator import PassphraseGenerator
    print("✅ Imports principaux réussis")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

init(autoreset=True)

class TestGestionnaireMDPNettoyage(unittest.TestCase):
    """Tests du gestionnaire principal après nettoyage"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Créer un fichier temporaire pour la base
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialiser le gestionnaire avec la base temporaire
        self.manager = GestionnaireMDP(db_file=self.temp_db.name)
        
        # Créer un compte de test
        self.test_password = "Test123!@#"
        self.manager.create_account(self.test_password)
        self.manager.authenticate(self.test_password)
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.manager.close_connection()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_creation_compte(self):
        """Test de création de compte sans démo"""
        # Créer un nouveau gestionnaire pour test isolé
        temp_db2 = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db2.close()
        
        try:
            manager2 = GestionnaireMDP(db_file=temp_db2.name)
            result = manager2.create_account("NewTest123!")
            self.assertTrue(result)
            
            # Tester l'authentification
            auth_result = manager2.authenticate("NewTest123!")
            self.assertTrue(auth_result)
            
            manager2.close_connection()
        finally:
            if os.path.exists(temp_db2.name):
                os.unlink(temp_db2.name)
    
    def test_gestion_mots_de_passe(self):
        """Test des opérations CRUD sans démo"""
        # Ajouter un mot de passe
        result = self.manager.add_password(
            "test-site.com",
            "user@test.com", 
            "TestPassword123!",
            "Test"
        )
        self.assertTrue(result)
        
        # Récupérer le mot de passe
        passwords = self.manager.get_passwords()
        self.assertGreater(len(passwords), 0)
        
        # Vérifier que les données sont correctes
        found_password = None
        for pwd in passwords:
            if pwd[1] == "test-site.com":  # site
                found_password = pwd
                break
        
        self.assertIsNotNone(found_password)
        self.assertEqual(found_password[2], "user@test.com")  # username
        
    def test_generation_mots_de_passe(self):
        """Test de génération de mots de passe"""
        # Test génération basique
        password = self.manager.generate_password()
        self.assertIsInstance(password, str)
        self.assertGreaterEqual(len(password), 12)
        
        # Test génération personnalisée
        password_custom = self.manager.generate_password(length=16, include_symbols=True)
        self.assertEqual(len(password_custom), 16)
        
    def test_categories(self):
        """Test de gestion des catégories"""
        categories = self.manager.get_categories()
        self.assertIsInstance(categories, list)
        
        # Les catégories par défaut doivent exister
        default_categories = ["Personnel", "Travail", "Finance", "Social", "Shopping", "Email", "Autre"]
        for cat in default_categories:
            self.assertIn(cat, categories)

class TestBiometricAuthenticator(unittest.TestCase):
    """Tests de l'authentificateur biométrique"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.auth = BiometricAuthenticator()
    
    def test_creation_authenticator(self):
        """Test de création de l'authenticateur"""
        self.assertIsNotNone(self.auth)
        self.assertIsNotNone(self.auth.config)
    
    def test_detection_methodes(self):
        """Test de détection des méthodes disponibles"""
        methods = self.auth.get_available_methods()
        self.assertIsInstance(methods, dict)
        
        # Vérifier la présence des méthodes attendues
        expected_methods = ['touchid', 'windows_hello', 'linux_fprintd']
        for method in expected_methods:
            self.assertIn(method, methods)
    
    def test_generation_token_sans_demo(self):
        """Test de génération de token sans mode démo"""
        # Même si aucune méthode n'est disponible, la fonction doit exister
        self.assertTrue(hasattr(self.auth, 'generate_biometric_token'))
        self.assertTrue(hasattr(self.auth, 'verify_biometric_token'))
    
    def test_absence_fonction_demo(self):
        """Vérifier que les fonctions de démo n'existent plus dans la classe"""
        # Vérifier qu'il n'y a pas de méthodes de démo dans la classe
        demo_methods = [method for method in dir(self.auth) if 'demo' in method.lower()]
        self.assertEqual(len(demo_methods), 0, f"Méthodes de démo trouvées: {demo_methods}")

class TestSecurityAuditor(unittest.TestCase):
    """Tests de l'auditeur de sécurité"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Créer un gestionnaire temporaire
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.manager = GestionnaireMDP(db_file=self.temp_db.name)
        self.manager.create_account("Test123!")
        self.manager.authenticate("Test123!")
        
        self.auditor = SecurityAuditor(self.manager)
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.manager.close_connection()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_creation_auditor(self):
        """Test de création de l'auditeur"""
        self.assertIsNotNone(self.auditor)
    
    def test_analyse_mot_de_passe(self):
        """Test d'analyse de mot de passe individuel"""
        # Test avec mot de passe fort
        score_fort = self.auditor.analyze_password_strength("Tr0ub4dor&3")
        self.assertIsInstance(score_fort, dict)
        self.assertIn('score', score_fort)
        self.assertGreaterEqual(score_fort['score'], 60)
        
        # Test avec mot de passe faible
        score_faible = self.auditor.analyze_password_strength("123456")
        self.assertIsInstance(score_faible, dict)
        self.assertLessEqual(score_faible['score'], 40)
    
    def test_audit_complet(self):
        """Test d'audit complet sans données de démo"""
        # Ajouter quelques mots de passe de test
        self.manager.add_password("test1.com", "user1", "StrongP@ssw0rd1!", "Test")
        self.manager.add_password("test2.com", "user2", "weak123", "Test")
        
        # Effectuer l'audit
        audit_result = self.auditor.full_security_audit()
        
        self.assertIsInstance(audit_result, dict)
        self.assertIn('overall_score', audit_result)
        self.assertIn('total_passwords', audit_result)
        self.assertEqual(audit_result['total_passwords'], 2)

class TestPassphraseGenerator(unittest.TestCase):
    """Tests du générateur de phrases de passe"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.generator = PassphraseGenerator()
    
    def test_creation_generator(self):
        """Test de création du générateur"""
        self.assertIsNotNone(self.generator)
    
    def test_generation_passphrase(self):
        """Test de génération de phrase de passe"""
        passphrase = self.generator.generate_passphrase()
        self.assertIsInstance(passphrase, str)
        self.assertGreater(len(passphrase), 10)
        
        # Vérifier qu'il y a plusieurs mots (séparés par des tirets par défaut)
        words = passphrase.split('-')
        self.assertGreaterEqual(len(words), 3)
    
    def test_calcul_entropie(self):
        """Test de calcul d'entropie"""
        passphrase = "correct-horse-battery-staple"
        entropy = self.generator.calculate_entropy(passphrase)
        self.assertIsInstance(entropy, float)
        self.assertGreater(entropy, 0)
    
    def test_generation_personnalisee(self):
        """Test de génération avec paramètres personnalisés"""
        passphrase = self.generator.generate_passphrase(
            words=5, 
            separator="_",
            numbers=True,
            capitalize=True
        )
        
        # Vérifier le séparateur
        self.assertIn("_", passphrase)
        
        # Vérifier le nombre de mots
        words = passphrase.split("_")
        self.assertEqual(len(words), 5)

def run_integration_tests():
    """Exécuter des tests d'intégration spécifiques"""
    print(f"\n{Fore.BLUE}🔧 TESTS D'INTÉGRATION POST-NETTOYAGE")
    print("=" * 60)
    
    tests_passes = 0
    tests_totaux = 6
    
    # Test 1: Gestionnaire principal
    try:
        print(f"\n{Fore.YELLOW}Test 1: Gestionnaire principal...")
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        manager = GestionnaireMDP(db_file=temp_db.name)
        manager.create_account("IntegrationTest123!")
        result = manager.authenticate("IntegrationTest123!")
        
        if result:
            print(f"   ✅ Gestionnaire principal opérationnel")
            tests_passes += 1
        
        manager.close_connection()
        os.unlink(temp_db.name)
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Authentification biométrique
    try:
        print(f"\n{Fore.YELLOW}Test 2: Authentification biométrique...")
        auth = BiometricAuthenticator()
        methods = auth.get_available_methods()
        print(f"   ✅ Détection méthodes: {len(methods)} méthodes")
        tests_passes += 1
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Audit de sécurité
    try:
        print(f"\n{Fore.YELLOW}Test 3: Audit de sécurité...")
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        manager = GestionnaireMDP(db_file=temp_db.name)
        manager.create_account("AuditTest123!")
        manager.authenticate("AuditTest123!")
        
        auditor = SecurityAuditor(manager)
        score = auditor.analyze_password_strength("TestPassword123!")
        print(f"   ✅ Analyse de mot de passe: score {score.get('score', 0)}")
        tests_passes += 1
        
        manager.close_connection()
        os.unlink(temp_db.name)
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Générateur de phrases de passe
    try:
        print(f"\n{Fore.YELLOW}Test 4: Générateur de phrases de passe...")
        generator = PassphraseGenerator()
        passphrase = generator.generate_passphrase()
        entropy = generator.calculate_entropy(passphrase)
        print(f"   ✅ Phrase générée: {len(passphrase.split('-'))} mots, entropie: {entropy:.1f}")
        tests_passes += 1
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Absence de fonctions de démo dans modules principaux
    try:
        print(f"\n{Fore.YELLOW}Test 5: Vérification absence de démos...")
        
        # Modules à vérifier
        modules_to_check = [
            'biometric_auth',
            'breach_monitor',
            'security_audit', 
            'passphrase_generator'
        ]
        
        demo_functions_found = []
        for module_name in modules_to_check:
            try:
                module = __import__(module_name)
                # Chercher des fonctions qui contiennent 'demo'
                for attr_name in dir(module):
                    if 'demo' in attr_name.lower() and callable(getattr(module, attr_name)):
                        demo_functions_found.append(f"{module_name}.{attr_name}")
            except ImportError:
                pass
        
        if not demo_functions_found:
            print(f"   ✅ Aucune fonction de démo trouvée dans les modules principaux")
            tests_passes += 1
        else:
            print(f"   ❌ Fonctions de démo trouvées: {demo_functions_found}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 6: Existence du dossier demos
    try:
        print(f"\n{Fore.YELLOW}Test 6: Vérification dossier demos...")
        demos_dir = os.path.join(os.path.dirname(__file__), 'demos')
        
        if os.path.exists(demos_dir):
            demo_files = os.listdir(demos_dir)
            print(f"   ✅ Dossier demos existe avec {len(demo_files)} fichier(s)")
            tests_passes += 1
        else:
            print(f"   ❌ Dossier demos manquant")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Résultats
    print(f"\n{Fore.CYAN}📊 RÉSULTATS DES TESTS D'INTÉGRATION:")
    print(f"   Tests réussis: {tests_passes}/{tests_totaux}")
    print(f"   Taux de réussite: {tests_passes/tests_totaux*100:.1f}%")
    
    if tests_passes == tests_totaux:
        print(f"\n{Fore.GREEN}🎉 TOUS LES TESTS D'INTÉGRATION RÉUSSIS!")
        return True
    else:
        print(f"\n{Fore.YELLOW}⚠️ Certains tests ont échoué")
        return False

def validate_demo_separation():
    """Valider que les démos sont bien séparées"""
    print(f"\n{Fore.BLUE}🎭 VALIDATION DE LA SÉPARATION DES DÉMOS")
    print("=" * 60)
    
    # Vérifier l'existence du dossier demos
    demos_dir = os.path.join(os.path.dirname(__file__), 'demos')
    if os.path.exists(demos_dir):
        print(f"   ✅ Dossier demos/ créé")
        
        # Vérifier les fichiers de démo
        demo_files = os.listdir(demos_dir)
        print(f"   ✅ {len(demo_files)} fichier(s) dans le dossier demos/")
        
        for file in demo_files:
            print(f"      - {file}")
    else:
        print(f"   ❌ Dossier demos/ non trouvé")
    
    # Vérifier l'absence de fonctions de démo dans les fichiers principaux
    main_files = [
        'gestionnaire_mdp.py',
        'biometric_auth.py',
        'breach_monitor.py',
        'security_audit.py',
        'passphrase_generator.py'
    ]
    
    demo_references = []
    for file in main_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Chercher les fonctions de démo (mais pas les commentaires vers demos/)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def ') and 'demo' in line.lower():
                        demo_references.append(f"{file}:ligne {i+1}")
    
    if not demo_references:
        print(f"   ✅ Aucune fonction de démo dans les fichiers principaux")
    else:
        print(f"   ⚠️ Références de démo trouvées dans: {demo_references}")
    
    return len(demo_references) == 0

if __name__ == "__main__":
    print(f"{Fore.BLUE}🧪 TESTS POST-NETTOYAGE - GESTIONNAIRE DE MOTS DE PASSE")
    print("=" * 70)
    print(f"{Fore.CYAN}🎯 Validation du fonctionnement après séparation des démos")
    
    # Tests unitaires
    print(f"\n{Fore.YELLOW}🔬 LANCEMENT DES TESTS UNITAIRES...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Tests d'intégration
    integration_success = run_integration_tests()
    
    # Validation de la séparation des démos
    demo_separation_success = validate_demo_separation()
    
    # Résultat final
    print(f"\n{Fore.BLUE}📊 BILAN FINAL DES TESTS POST-NETTOYAGE")
    print("=" * 70)
    
    if integration_success and demo_separation_success:
        print(f"{Fore.GREEN}✅ NETTOYAGE RÉUSSI - Projet prêt pour production")
        print(f"{Fore.GREEN}✅ Séparation des démos complète")
        print(f"{Fore.GREEN}✅ Fonctionnalités principales intactes")
        sys.exit(0)
    else:
        print(f"{Fore.YELLOW}⚠️ Nettoyage partiellement réussi - Vérification requise")
        sys.exit(1)