#!/usr/bin/env python3
"""
Tests unitaires pour le Scanner de Vulnérabilités Web
Tests complets de toutes les fonctionnalités du scanner
"""

import os
import sys
import unittest
import tempfile
import json
import time
from datetime import datetime
import sqlite3

# Ajouter le chemin du module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner_vulnerabilites import (
    VulnerabilityScanner, TechnologyDetector, SSLAnalyzer, 
    SecurityHeadersChecker, DatabaseManager, ReportGenerator,
    VulnerabiliteDetectee, ResultatScan, WebVulnScanner
)

import requests
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch, MagicMock

class TestTechnologyDetector(unittest.TestCase):
    """Tests pour le détecteur de technologies"""
    
    def setUp(self):
        self.detector = TechnologyDetector()
    
    def test_detection_technologies_headers(self):
        """Test détection via les en-têtes HTTP"""
        # Mock response avec en-têtes
        mock_response = Mock()
        mock_response.headers = {
            'Server': 'Apache/2.4.41',
            'X-Powered-By': 'PHP/7.4.3'
        }
        mock_response.text = '<html><body>Test</body></html>'
        
        mock_soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        technologies = self.detector.detecter_technologies(mock_response, mock_soup)
        
        self.assertIn('Apache', technologies)
        self.assertIn('PHP', technologies)
    
    def test_detection_technologies_contenu(self):
        """Test détection via le contenu HTML"""
        mock_response = Mock()
        mock_response.headers = {}
        mock_response.text = '''
        <html>
        <head>
            <script src="/wp-content/themes/test/script.js"></script>
            <link rel="stylesheet" href="/wp-includes/css/style.css">
        </head>
        <body>Test</body>
        </html>
        '''
        
        mock_soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        technologies = self.detector.detecter_technologies(mock_response, mock_soup)
        
        self.assertIn('WordPress', technologies)
    
    def test_detection_meta_generator(self):
        """Test détection via meta generator"""
        mock_response = Mock()
        mock_response.headers = {}
        mock_response.text = '''
        <html>
        <head>
            <meta name="generator" content="Drupal 9.2.0">
        </head>
        <body>Test</body>
        </html>
        '''
        
        mock_soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        technologies = self.detector.detecter_technologies(mock_response, mock_soup)
        
        # Devrait détecter le generator
        generator_found = any('Generator: Drupal' in tech for tech in technologies)
        self.assertTrue(generator_found)

class TestSecurityHeadersChecker(unittest.TestCase):
    """Tests pour le vérificateur d'en-têtes de sécurité"""
    
    def setUp(self):
        self.checker = SecurityHeadersChecker()
    
    def test_headers_presents(self):
        """Test avec tous les en-têtes présents"""
        headers = {
            'Strict-Transport-Security': 'max-age=31536000',
            'Content-Security-Policy': "default-src 'self'",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Feature-Policy': "camera 'none'"
        }
        
        resultats = self.checker.verifier_headers(headers)
        
        # Tous les en-têtes de sécurité devraient être détectés comme présents
        for header in self.checker.headers_securite.keys():
            self.assertTrue(resultats[header], f"Header {header} devrait être présent")
    
    def test_headers_manquants(self):
        """Test avec des en-têtes manquants"""
        headers = {
            'Content-Type': 'text/html',
            'Server': 'Apache'
        }
        
        resultats = self.checker.verifier_headers(headers)
        
        # Aucun en-tête de sécurité ne devrait être détecté
        for header, present in resultats.items():
            self.assertFalse(present, f"Header {header} ne devrait pas être présent")
    
    def test_headers_case_insensitive(self):
        """Test insensibilité à la casse"""
        headers = {
            'strict-transport-security': 'max-age=31536000',
            'CONTENT-SECURITY-POLICY': "default-src 'self'"
        }
        
        resultats = self.checker.verifier_headers(headers)
        
        self.assertTrue(resultats['Strict-Transport-Security'])
        self.assertTrue(resultats['Content-Security-Policy'])

class TestVulnerabilityScanner(unittest.TestCase):
    """Tests pour le scanner principal"""
    
    def setUp(self):
        self.scanner = VulnerabilityScanner(timeout=5)
    
    @patch('requests.Session.get')
    def test_scan_url_basique(self, mock_get):
        """Test scan basique d'une URL"""
        # Mock de la réponse
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Server': 'Apache/2.4.41'}
        mock_response.text = '<html><body><form method="post"><input name="test" type="text"></form></body></html>'
        mock_response.content = mock_response.text.encode()
        mock_get.return_value = mock_response
        
        resultat = self.scanner.scan_url('http://example.com')
        
        self.assertEqual(resultat.url, 'http://example.com')
        self.assertEqual(resultat.status_code, 200)
        self.assertGreater(len(resultat.technologies), 0)
        self.assertEqual(resultat.formulaires_detectes, 1)
    
    @patch('requests.Session.get')
    def test_detection_formulaires_multiples(self, mock_get):
        """Test détection de multiples formulaires"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = '''
        <html><body>
            <form method="post" action="/login">
                <input name="username" type="text">
                <input name="password" type="password">
            </form>
            <form method="get" action="/search">
                <input name="q" type="text">
            </form>
            <form method="post" action="/contact">
                <textarea name="message"></textarea>
            </form>
        </body></html>
        '''
        mock_response.content = mock_response.text.encode()
        mock_get.return_value = mock_response
        
        resultat = self.scanner.scan_url('http://example.com')
        
        self.assertEqual(resultat.formulaires_detectes, 3)
    
    def test_calcul_score_securite(self):
        """Test du calcul du score de sécurité"""
        # Score parfait (pas de vulnérabilités ni en-têtes manquants)
        score = self.scanner._calculer_score_securite(0, 0)
        self.assertEqual(score, 100)
        
        # Score avec en-têtes manquants
        score = self.scanner._calculer_score_securite(3, 0)
        self.assertEqual(score, 85)  # 100 - 3*5
        
        # Score avec vulnérabilités
        self.scanner.vulnerabilites_detectees = [
            VulnerabiliteDetectee(
                id="test1", url="test", type_vuln="XSS", severite="HIGH",
                description="test", details={}, remediation="test", timestamp=datetime.now()
            ),
            VulnerabiliteDetectee(
                id="test2", url="test", type_vuln="SQL", severite="CRITICAL",
                description="test", details={}, remediation="test", timestamp=datetime.now()
            )
        ]
        
        score = self.scanner._calculer_score_securite(0, 2)
        self.assertEqual(score, 60)  # 100 - 15 (HIGH) - 25 (CRITICAL)
        
        # Score ne peut pas être négatif
        self.scanner.vulnerabilites_detectees = [
            VulnerabiliteDetectee(
                id=f"test{i}", url="test", type_vuln="XSS", severite="CRITICAL",
                description="test", details={}, remediation="test", timestamp=datetime.now()
            ) for i in range(10)
        ]
        
        score = self.scanner._calculer_score_securite(10, 10)
        self.assertEqual(score, 0)  # Ne peut pas être négatif
    
    def test_ajouter_vulnerabilite(self):
        """Test ajout de vulnérabilité"""
        initial_count = len(self.scanner.vulnerabilites_detectees)
        
        self.scanner._ajouter_vulnerabilite(
            'http://test.com', 'XSS_REFLECTED', 'HIGH',
            'Test XSS', {'test': 'data'}, 'Fix XSS'
        )
        
        self.assertEqual(len(self.scanner.vulnerabilites_detectees), initial_count + 1)
        
        vuln = self.scanner.vulnerabilites_detectees[-1]
        self.assertEqual(vuln.url, 'http://test.com')
        self.assertEqual(vuln.type_vuln, 'XSS_REFLECTED')
        self.assertEqual(vuln.severite, 'HIGH')

class TestSSLAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur SSL"""
    
    def setUp(self):
        self.analyzer = SSLAnalyzer()
    
    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_ssl_valide(self, mock_ssl_context, mock_socket):
        """Test analyse SSL valide"""
        # Mock du certificat
        mock_cert = {
            'subject': [['CN', 'example.com']],
            'issuer': [['CN', 'Test CA']],
            'version': 3,
            'notBefore': 'Jan 1 00:00:00 2024 GMT',
            'notAfter': 'Dec 31 23:59:59 2024 GMT',
            'serialNumber': '123456789',
            'subjectAltName': [['DNS', 'example.com'], ['DNS', '*.example.com']]
        }
        
        # Mock de la connexion SSL
        mock_ssl_socket = Mock()
        mock_ssl_socket.getpeercert.return_value = mock_cert
        mock_ssl_socket.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
        mock_ssl_socket.version.return_value = 'TLSv1.3'
        
        mock_context = Mock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssl_socket
        mock_ssl_context.return_value = mock_context
        
        mock_socket.return_value.__enter__ = Mock(return_value=Mock())
        mock_socket.return_value.__exit__ = Mock(return_value=None)
        
        resultat = self.analyzer.analyser_ssl('example.com')
        
        self.assertTrue(resultat['valide'])
        self.assertEqual(resultat['version_ssl'], 'TLSv1.3')
        self.assertEqual(resultat['cipher_suite'], 'TLS_AES_256_GCM_SHA384')
        self.assertEqual(resultat['bits_chiffrement'], 256)
    
    def test_ssl_erreur(self):
        """Test gestion erreur SSL"""
        # Test avec un hostname invalide qui va causer une erreur
        resultat = self.analyzer.analyser_ssl('hostname-invalide-test-12345.com')
        
        self.assertFalse(resultat['valide'])
        self.assertIn('erreur', resultat)

class TestDatabaseManager(unittest.TestCase):
    """Tests pour le gestionnaire de base de données"""
    
    def setUp(self):
        # Créer une base temporaire
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        # Nettoyer le fichier temporaire
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_init_database(self):
        """Test initialisation de la base"""
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Vérifier que les tables existent
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('scans', tables)
        self.assertIn('vulnerabilites', tables)
        
        conn.close()
    
    def test_sauvegarde_scan(self):
        """Test sauvegarde d'un scan"""
        # Créer un résultat de test
        vulnerabilites = [
            VulnerabiliteDetectee(
                id="test_vuln_1",
                url="http://test.com",
                type_vuln="XSS_REFLECTED",
                severite="HIGH",
                description="Test XSS",
                details={"test": "data"},
                remediation="Fix XSS",
                timestamp=datetime.now()
            )
        ]
        
        resultat = ResultatScan(
            url="http://test.com",
            timestamp=datetime.now(),
            duree_scan=5.5,
            status_code=200,
            technologies=["Apache", "PHP"],
            vulnerabilites=vulnerabilites,
            en_tetes_securite={"HSTS": True, "CSP": False},
            formulaires_detectes=2,
            certificat_ssl={"valide": True},
            score_securite=75
        )
        
        scan_id = self.db_manager.sauvegarder_scan(resultat)
        
        # Vérifier que le scan a été sauvegardé
        self.assertIsInstance(scan_id, int)
        self.assertGreater(scan_id, 0)
        
        # Vérifier le contenu en base
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
        scan_data = cursor.fetchone()
        self.assertIsNotNone(scan_data)
        
        cursor.execute('SELECT * FROM vulnerabilites WHERE scan_id = ?', (scan_id,))
        vuln_data = cursor.fetchall()
        self.assertEqual(len(vuln_data), 1)
        
        conn.close()

class TestReportGenerator(unittest.TestCase):
    """Tests pour le générateur de rapports"""
    
    def setUp(self):
        self.generator = ReportGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Nettoyer les fichiers temporaires
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_generation_rapport_basique(self):
        """Test génération d'un rapport basique"""
        # Créer des données de test
        resultat = ResultatScan(
            url="http://example.com",
            timestamp=datetime.now(),
            duree_scan=3.5,
            status_code=200,
            technologies=["Apache", "PHP", "WordPress"],
            vulnerabilites=[],
            en_tetes_securite={
                "Strict-Transport-Security": True,
                "Content-Security-Policy": False
            },
            formulaires_detectes=2,
            certificat_ssl={"valide": True, "version_ssl": "TLSv1.3"},
            score_securite=85
        )
        
        output_path = os.path.join(self.temp_dir, "test_rapport.html")
        
        generated_path = self.generator.generer_rapport(resultat, output_path)
        
        self.assertEqual(generated_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Vérifier le contenu du rapport
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("example.com", content)
        self.assertIn("85/100", content)
        self.assertIn("Apache", content)
        self.assertIn("WordPress", content)
    
    def test_generation_rapport_avec_vulnerabilites(self):
        """Test génération de rapport avec vulnérabilités"""
        vulnerabilites = [
            VulnerabiliteDetectee(
                id="test_xss",
                url="http://example.com",
                type_vuln="XSS_REFLECTED",
                severite="HIGH",
                description="XSS détecté dans le formulaire",
                details={"field": "search"},
                remediation="Encoder les entrées utilisateur",
                timestamp=datetime.now()
            ),
            VulnerabiliteDetectee(
                id="test_header",
                url="http://example.com",
                type_vuln="HEADER_MISSING",
                severite="MEDIUM",
                description="En-tête CSP manquant",
                details={"header": "Content-Security-Policy"},
                remediation="Ajouter l'en-tête CSP",
                timestamp=datetime.now()
            )
        ]
        
        resultat = ResultatScan(
            url="http://example.com",
            timestamp=datetime.now(),
            duree_scan=4.2,
            status_code=200,
            technologies=["Nginx"],
            vulnerabilites=vulnerabilites,
            en_tetes_securite={"Content-Security-Policy": False},
            formulaires_detectes=1,
            certificat_ssl={"valide": False, "erreur": "Certificat expiré"},
            score_securite=45
        )
        
        output_path = os.path.join(self.temp_dir, "test_rapport_vulns.html")
        
        generated_path = self.generator.generer_rapport(resultat, output_path)
        
        # Vérifier le contenu
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("XSS_REFLECTED", content)
        self.assertIn("HIGH", content)
        self.assertIn("HEADER_MISSING", content)
        self.assertIn("MEDIUM", content)
        self.assertIn("45/100", content)
        self.assertIn("Certificat expiré", content)

class TestWebVulnScanner(unittest.TestCase):
    """Tests d'intégration pour le scanner complet"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Patcher le DatabaseManager pour utiliser notre DB temporaire
        with patch('scanner_vulnerabilites.DatabaseManager') as mock_db_class:
            mock_db_instance = DatabaseManager(self.temp_db.name)
            mock_db_class.return_value = mock_db_instance
            self.scanner = WebVulnScanner()
            self.scanner.db_manager = mock_db_instance
    
    def tearDown(self):
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    @patch('requests.Session.get')
    def test_scanner_url_complet(self, mock_get):
        """Test complet du scan d'une URL"""
        # Mock de la réponse
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Server': 'Apache/2.4.41',
            'X-Frame-Options': 'SAMEORIGIN'
        }
        mock_response.text = '''
        <html>
        <head><title>Test</title></head>
        <body>
            <form method="post" action="/test">
                <input name="search" type="text">
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode()
        mock_get.return_value = mock_response
        
        # Exécuter le scan
        resultat = self.scanner.scanner_url('http://test.com', generer_rapport=False)
        
        # Vérifications
        self.assertIsInstance(resultat, ResultatScan)
        self.assertEqual(resultat.url, 'http://test.com')
        self.assertEqual(resultat.status_code, 200)
        self.assertGreater(len(resultat.technologies), 0)
        self.assertEqual(resultat.formulaires_detectes, 1)
        
        # Vérifier que des vulnérabilités d'en-têtes manquants ont été détectées
        headers_missing_vulns = [v for v in resultat.vulnerabilites if v.type_vuln == 'HEADER_MISSING']
        self.assertGreater(len(headers_missing_vulns), 0)

def run_performance_tests():
    """Tests de performance du scanner"""
    print("\n🏃 TESTS DE PERFORMANCE")
    print("=" * 30)
    
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        scanner = WebVulnScanner()
        scanner.db_manager = DatabaseManager(temp_db.name)
        
        # Test 1: Performance de détection de technologies
        print("\n🧪 Test 1: Détection de technologies")
        detector = TechnologyDetector()
        
        mock_response = Mock()
        mock_response.headers = {
            'Server': 'Apache/2.4.41',
            'X-Powered-By': 'PHP/7.4.3'
        }
        mock_response.text = '''
        <html>
        <head>
            <script src="/wp-content/themes/test/script.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        </head>
        <body>
            <div class="container">Test WordPress site</div>
        </body>
        </html>
        '''
        
        soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        start_time = time.time()
        for _ in range(100):
            technologies = detector.detecter_technologies(mock_response, soup)
        detection_time = time.time() - start_time
        
        print(f"✓ 100 détections en {detection_time:.3f}s ({100/detection_time:.1f} détections/s)")
        print(f"   Technologies détectées: {', '.join(technologies)}")
        
        # Test 2: Performance de vérification des en-têtes
        print("\n🧪 Test 2: Vérification des en-têtes de sécurité")
        checker = SecurityHeadersChecker()
        
        test_headers = {
            'Strict-Transport-Security': 'max-age=31536000',
            'Content-Security-Policy': "default-src 'self'",
            'X-Content-Type-Options': 'nosniff',
            'Server': 'Apache/2.4.41'
        }
        
        start_time = time.time()
        for _ in range(1000):
            results = checker.verifier_headers(test_headers)
        headers_time = time.time() - start_time
        
        print(f"✓ 1000 vérifications en {headers_time:.3f}s ({1000/headers_time:.1f} vérifications/s)")
        
        # Test 3: Performance de sauvegarde en base
        print("\n🧪 Test 3: Sauvegarde en base de données")
        
        # Créer des données de test
        vulnerabilites = [
            VulnerabiliteDetectee(
                id=f"perf_test_{i}",
                url="http://test.com",
                type_vuln="XSS_REFLECTED",
                severite="HIGH",
                description=f"Test vulnerability {i}",
                details={"test": f"data_{i}"},
                remediation="Fix test issue",
                timestamp=datetime.now()
            ) for i in range(5)
        ]
        
        resultat_test = ResultatScan(
            url="http://performance-test.com",
            timestamp=datetime.now(),
            duree_scan=2.5,
            status_code=200,
            technologies=["Apache", "PHP", "WordPress"],
            vulnerabilites=vulnerabilites,
            en_tetes_securite={"HSTS": True, "CSP": False},
            formulaires_detectes=3,
            certificat_ssl={"valide": True},
            score_securite=75
        )
        
        start_time = time.time()
        for i in range(50):
            # Modifier l'ID pour éviter les doublons
            resultat_test_unique = ResultatScan(
                url=f"http://performance-test-{i}.com",
                timestamp=datetime.now(),
                duree_scan=2.5,
                status_code=200,
                technologies=["Apache", "PHP", "WordPress"],
                vulnerabilites=[
                    VulnerabiliteDetectee(
                        id=f"perf_test_{i}_{j}",
                        url=f"http://test-{i}.com",
                        type_vuln="XSS_REFLECTED",
                        severite="HIGH",
                        description=f"Test vulnerability {i}_{j}",
                        details={"test": f"data_{i}_{j}"},
                        remediation="Fix test issue",
                        timestamp=datetime.now()
                    ) for j in range(2)  # Réduire le nombre
                ],
                en_tetes_securite={"HSTS": True, "CSP": False},
                formulaires_detectes=3,
                certificat_ssl={"valide": True},
                score_securite=75
            )
            scanner.db_manager.sauvegarder_scan(resultat_test_unique)
        save_time = time.time() - start_time
        
        print(f"✓ 50 sauvegardes en {save_time:.3f}s ({50/save_time:.1f} sauvegardes/s)")
        
        print(f"\n🏆 RÉSUMÉ PERFORMANCE:")
        print(f"   Détection technologies: {100/detection_time:.1f} ops/s")
        print(f"   Vérification en-têtes: {1000/headers_time:.1f} ops/s")
        print(f"   Sauvegarde BDD: {50/save_time:.1f} ops/s")
        
    finally:
        try:
            os.unlink(temp_db.name)
        except:
            pass

def run_all_tests():
    """Exécuter tous les tests"""
    print("🧪 DÉMARRAGE DES TESTS DU SCANNER DE VULNÉRABILITÉS WEB")
    print("=" * 60)
    
    # Tests unitaires
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(TestTechnologyDetector))
    test_suite.addTest(loader.loadTestsFromTestCase(TestSecurityHeadersChecker))
    test_suite.addTest(loader.loadTestsFromTestCase(TestVulnerabilityScanner))
    test_suite.addTest(loader.loadTestsFromTestCase(TestSSLAnalyzer))
    test_suite.addTest(loader.loadTestsFromTestCase(TestDatabaseManager))
    test_suite.addTest(loader.loadTestsFromTestCase(TestReportGenerator))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWebVulnScanner))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Tests de performance
    run_performance_tests()
    
    # Résumé final
    print("\n" + "=" * 60)
    print(f"Tests unitaires exécutés: {result.testsRun}")
    print(f"Erreurs: {len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    
    if result.errors:
        print("\nERREURS:")
        for test, error in result.errors:
            print(f"- {test}: {error.strip().split('AssertionError: ')[-1] if 'AssertionError:' in error else 'Erreur technique'}")
    
    if result.failures:
        print("\nÉCHECS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure.strip().split('AssertionError: ')[-1] if 'AssertionError:' in failure else 'Test échoué'}")
    
    success = len(result.errors) == 0 and len(result.failures) == 0
    
    if success:
        print("\n✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("🕷️ Scanner de vulnérabilités web prêt pour utilisation")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
    
    return success

if __name__ == "__main__":
    run_all_tests()