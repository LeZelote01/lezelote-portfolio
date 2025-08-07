#!/usr/bin/env python3
"""
Script de démonstration pour le Scanner de Vulnérabilités Web
Permet de tester toutes les fonctionnalités avec des scénarios réalistes
"""

import os
import sys
import json
import time
import tempfile
from datetime import datetime
from colorama import init, Fore, Style

# Initialiser colorama
init(autoreset=True)

# Ajouter le chemin du module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner_vulnerabilites import WebVulnScanner
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

def demo_complete():
    """Démonstration complète de toutes les fonctionnalités"""
    print(f"{Fore.BLUE}🕷️ DÉMONSTRATION COMPLÈTE - SCANNER DE VULNÉRABILITÉS WEB")
    print("=" * 70)
    
    # Créer des fichiers temporaires pour la démo
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='_demo.db')
    temp_db.close()
    
    try:
        # 1. Initialisation du scanner
        print(f"\n{Fore.CYAN}📋 ÉTAPE 1: Initialisation du scanner")
        scanner = WebVulnScanner()
        
        # Utiliser une base temporaire pour la démo
        from scanner_vulnerabilites import DatabaseManager
        scanner.db_manager = DatabaseManager(temp_db.name)
        
        print(f"{Fore.GREEN}✓ Scanner initialisé avec base de données temporaire")
        
        # 2. Test avec différents scénarios de sites web
        scenarios = [
            {
                'nom': 'Site vulnérable (XSS + SQL Injection)',
                'url': 'http://vulnerable-site.com',
                'status_code': 200,
                'headers': {
                    'Server': 'Apache/2.4.41',
                    'X-Powered-By': 'PHP/7.4.3'
                },
                'html': '''
                <html>
                <head><title>Vulnerable Site</title></head>
                <body>
                    <h1>Login Form</h1>
                    <form method="post" action="/login.php">
                        <input name="username" type="text" placeholder="Username">
                        <input name="password" type="password" placeholder="Password">
                        <input type="submit" value="Login">
                    </form>
                    
                    <h2>Search</h2>
                    <form method="get" action="/search.php">
                        <input name="query" type="text" placeholder="Search...">
                        <input type="submit" value="Search">
                    </form>
                </body>
                </html>
                ''',
                'vulnerabilites_attendues': ['HEADER_MISSING', 'CSRF_MISSING']
            },
            {
                'nom': 'Site WordPress sécurisé',
                'url': 'https://secure-wordpress.com',
                'status_code': 200,
                'headers': {
                    'Server': 'nginx/1.18.0',
                    'Strict-Transport-Security': 'max-age=31536000',
                    'Content-Security-Policy': "default-src 'self'",
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'SAMEORIGIN',
                    'X-XSS-Protection': '1; mode=block'
                },
                'html': '''
                <html>
                <head>
                    <title>Secure WordPress Site</title>
                    <meta name="generator" content="WordPress 6.1.1">
                    <link rel="stylesheet" href="/wp-content/themes/secure/style.css">
                </head>
                <body>
                    <h1>Secure WordPress Site</h1>
                    <form method="post" action="/wp-comments-post.php">
                        <input type="hidden" name="wp_nonce" value="abc123def456">
                        <textarea name="comment" placeholder="Leave a comment"></textarea>
                        <input type="submit" value="Post Comment">
                    </form>
                </body>
                </html>
                ''',
                'vulnerabilites_attendues': []  # Site sécurisé
            },
            {
                'nom': 'Application E-commerce avec failles',
                'url': 'http://shop-example.com',
                'status_code': 200,
                'headers': {
                    'Server': 'Microsoft-IIS/10.0',
                    'X-Powered-By': 'ASP.NET'
                },
                'html': '''
                <html>
                <head><title>Online Shop</title></head>
                <body>
                    <h1>Online Shop</h1>
                    
                    <form method="post" action="/checkout">
                        <input name="product_id" type="hidden" value="123">
                        <input name="quantity" type="number" value="1">
                        <input name="price" type="hidden" value="99.99">
                        <input type="submit" value="Add to Cart">
                    </form>
                    
                    <form method="get" action="/products">
                        <input name="category" type="text" placeholder="Category">
                        <input name="min_price" type="number" placeholder="Min Price">
                        <input name="max_price" type="number" placeholder="Max Price">
                        <input type="submit" value="Filter">
                    </form>
                </body>
                </html>
                ''',
                'vulnerabilites_attendues': ['HEADER_MISSING', 'CSRF_MISSING']
            }
        ]
        
        print(f"\n{Fore.CYAN}📋 ÉTAPE 2: Test de {len(scenarios)} scénarios différents")
        
        resultats_demo = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{Fore.YELLOW}🧪 Scénario {i}: {scenario['nom']}")
            print(f"   URL: {scenario['url']}")
            
            # Mock de la réponse HTTP
            with patch('requests.Session.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = scenario['status_code']
                mock_response.headers = scenario['headers']
                mock_response.text = scenario['html']
                mock_response.content = scenario['html'].encode()
                mock_get.return_value = mock_response
                
                # Mock additional requests pour les tests XSS/SQL
                with patch('requests.Session.post') as mock_post:
                    mock_post.return_value = mock_response
                    
                    # Exécuter le scan
                    resultat = scanner.scanner_url(scenario['url'], generer_rapport=False)
                    resultats_demo.append(resultat)
            
            # Analyser les résultats
            print(f"   📊 Score de sécurité: {resultat.score_securite}/100")
            print(f"   🚨 Vulnérabilités détectées: {len(resultat.vulnerabilites)}")
            print(f"   🔧 Technologies: {', '.join(resultat.technologies[:3])}...")
            print(f"   📝 Formulaires: {resultat.formulaires_detectes}")
            
            # Afficher les vulnérabilités trouvées
            if resultat.vulnerabilites:
                print(f"   {Fore.RED}🚨 Vulnérabilités:")
                for vuln in resultat.vulnerabilites[:3]:  # Limiter l'affichage
                    print(f"      • {vuln.severite}: {vuln.type_vuln}")
            else:
                print(f"   {Fore.GREEN}✅ Aucune vulnérabilité détectée")
        
        # 3. Test des fonctionnalités de détection spécifiques
        print(f"\n{Fore.CYAN}📋 ÉTAPE 3: Test des détecteurs spécialisés")
        
        # Test du détecteur de technologies
        print(f"\n{Fore.YELLOW}🔧 Test du détecteur de technologies")
        from scanner_vulnerabilites import TechnologyDetector
        
        detector = TechnologyDetector()
        
        # Test avec différents contenus
        test_cases = [
            {
                'nom': 'Site WordPress + jQuery + Bootstrap',
                'headers': {'Server': 'Apache/2.4.41', 'X-Powered-By': 'PHP/8.0.0'},
                'html': '''
                <html>
                <head>
                    <script src="/wp-content/themes/test/js/script.js"></script>
                    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                </html>
                '''
            },
            {
                'nom': 'Application React avec Node.js',
                'headers': {'X-Powered-By': 'Express', 'Server': 'nginx/1.18.0'},
                'html': '''
                <html>
                <head>
                    <script>window.__REACT_DEVTOOLS_GLOBAL_HOOK__</script>
                    <div id="root"></div>
                    <script src="/static/js/main.12345.js"></script>
                </head>
                </html>
                '''
            }
        ]
        
        for test_case in test_cases:
            mock_response = Mock()
            mock_response.headers = test_case['headers']
            mock_response.text = test_case['html']
            
            soup = BeautifulSoup(test_case['html'], 'html.parser')
            technologies = detector.detecter_technologies(mock_response, soup)
            
            print(f"   • {test_case['nom']}: {', '.join(technologies)}")
        
        # Test du vérificateur d'en-têtes de sécurité
        print(f"\n{Fore.YELLOW}🛡️ Test du vérificateur d'en-têtes de sécurité")
        from scanner_vulnerabilites import SecurityHeadersChecker
        
        headers_checker = SecurityHeadersChecker()
        
        # Test avec différents niveaux de sécurité
        headers_tests = [
            {
                'nom': 'Site très sécurisé',
                'headers': {
                    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'DENY',
                    'X-XSS-Protection': '1; mode=block',
                    'Referrer-Policy': 'strict-origin-when-cross-origin',
                    'Feature-Policy': "camera 'none'; microphone 'none'"
                }
            },
            {
                'nom': 'Site partiellement sécurisé',
                'headers': {
                    'X-Frame-Options': 'SAMEORIGIN',
                    'X-Content-Type-Options': 'nosniff'
                }
            },
            {
                'nom': 'Site non sécurisé',
                'headers': {
                    'Server': 'Apache/2.4.41',
                    'Content-Type': 'text/html'
                }
            }
        ]
        
        for test in headers_tests:
            resultats = headers_checker.verifier_headers(test['headers'])
            presents = sum(1 for present in resultats.values() if present)
            total = len(resultats)
            
            print(f"   • {test['nom']}: {presents}/{total} en-têtes présents")
        
        # 4. Test de l'analyseur SSL (simulation)
        print(f"\n{Fore.YELLOW}🔒 Test de l'analyseur SSL (simulation)")
        
        ssl_tests = [
            {
                'nom': 'Certificat valide TLS 1.3',
                'resultat': {
                    'valide': True,
                    'version_ssl': 'TLSv1.3',
                    'cipher_suite': 'TLS_AES_256_GCM_SHA384',
                    'bits_chiffrement': 256
                }
            },
            {
                'nom': 'Certificat expiré',
                'resultat': {
                    'valide': False,
                    'erreur': 'Certificate has expired',
                    'details': 'Le certificat SSL a expiré le 15/01/2024'
                }
            }
        ]
        
        for test in ssl_tests:
            if test['resultat']['valide']:
                print(f"   • {test['nom']}: ✅ {test['resultat']['version_ssl']} - {test['resultat']['bits_chiffrement']} bits")
            else:
                print(f"   • {test['nom']}: ❌ {test['resultat']['erreur']}")
        
        # 5. Simulation de génération de rapports
        print(f"\n{Fore.CYAN}📋 ÉTAPE 4: Génération des rapports de démonstration")
        
        for i, resultat in enumerate(resultats_demo, 1):
            # Générer un rapport pour chaque scan
            rapport_path = scanner.report_generator.generer_rapport(resultat)
            
            parsed_url = resultat.url.replace('http://', '').replace('https://', '').replace('/', '_')
            print(f"{Fore.GREEN}✓ Rapport {i} généré: {rapport_path}")
            
            # Afficher les statistiques du fichier
            if os.path.exists(rapport_path):
                taille = os.path.getsize(rapport_path)
                print(f"      Taille: {taille:,} bytes")
        
        # 6. Test des statistiques et de la base de données
        print(f"\n{Fore.CYAN}📋 ÉTAPE 5: Test des statistiques de base de données")
        
        # Vérifier que les scans ont été sauvegardés
        import sqlite3
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM scans')
        nb_scans = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vulnerabilites')
        nb_vulns = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(score_securite) FROM scans WHERE score_securite > 0')
        score_moyen = cursor.fetchone()[0] or 0
        
        print(f"{Fore.GREEN}📊 Statistiques de démonstration:")
        print(f"   • Scans effectués: {nb_scans}")
        print(f"   • Vulnérabilités détectées: {nb_vulns}")
        print(f"   • Score de sécurité moyen: {score_moyen:.1f}/100")
        
        # Top des types de vulnérabilités
        cursor.execute('''
            SELECT type_vuln, COUNT(*) as count 
            FROM vulnerabilites 
            GROUP BY type_vuln 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        
        top_vulns = cursor.fetchall()
        if top_vulns:
            print(f"\n{Fore.YELLOW}🚨 Top vulnérabilités détectées:")
            for vuln_type, count in top_vulns:
                print(f"   • {vuln_type}: {count}")
        
        conn.close()
        
        # 7. Test des capacités de scan multiple
        print(f"\n{Fore.CYAN}📋 ÉTAPE 6: Test du scan multiple (simulation)")
        
        urls_test = [
            'http://site1.example.com',
            'https://site2.example.com',
            'http://site3.example.com'
        ]
        
        print(f"{Fore.BLUE}🔄 Simulation de scan multiple pour {len(urls_test)} URLs...")
        
        # Simuler le temps de scan multiple
        import concurrent.futures
        from concurrent.futures import ThreadPoolExecutor
        
        def simulate_scan(url):
            time.sleep(0.5)  # Simuler le temps de scan
            return {
                'url': url,
                'score': 70 + (hash(url) % 30),  # Score pseudo-aléatoire
                'vulns': hash(url) % 5,  # Nombre de vulns pseudo-aléatoire
                'duration': 0.5 + (hash(url) % 100) / 200  # Durée pseudo-aléatoire
            }
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(simulate_scan, url): url for url in urls_test}
            
            for future in concurrent.futures.as_completed(futures):
                resultat = future.result()
                print(f"   ✓ {resultat['url']}: Score {resultat['score']}/100, {resultat['vulns']} vulns ({resultat['duration']:.2f}s)")
        
        # 8. Résumé final de la démonstration
        print(f"\n{Fore.CYAN}📋 ÉTAPE 7: Résumé de la démonstration")
        
        print(f"{Fore.GREEN}✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        
        print(f"\n{Fore.BLUE}📊 Résumé final:")
        print(f"  🕷️ {len(scenarios)} scénarios de scan testés")
        print(f"  🔧 Technologies détectées avec succès")
        print(f"  🛡️ En-têtes de sécurité analysés")
        print(f"  🔒 Analyse SSL/TLS simulée")
        print(f"  📄 {len(resultats_demo)} rapports HTML générés")
        print(f"  💾 Base de données avec {nb_scans} scans et {nb_vulns} vulnérabilités")
        print(f"  🔄 Scan multiple simulé avec succès")
        
        # Lister les fichiers créés
        print(f"\n{Fore.YELLOW}📁 FICHIERS CRÉÉS:")
        
        fichiers_demo = [temp_db.name]
        
        # Trouver les rapports générés
        for file in os.listdir('.'):
            if file.startswith('rapport_securite_') and file.endswith('.html'):
                fichiers_demo.append(file)
        
        for fichier in fichiers_demo:
            if os.path.exists(fichier):
                taille = os.path.getsize(fichier)
                nom_fichier = os.path.basename(fichier)
                print(f"  ✓ {nom_fichier} ({taille:,} bytes)")
        
        print(f"\n{Fore.CYAN}💻 Pour tester le scanner en ligne de commande:")
        print(f"  python3 scanner_vulnerabilites.py scan https://example.com")
        print(f"  python3 scanner_vulnerabilites.py stats")
        print(f"  python3 scanner_vulnerabilites.py list")
        
        print(f"\n{Fore.CYAN}🌐 Exemples d'URLs à tester:")
        print(f"  • Sites de test: http://testphp.vulnweb.com/")
        print(f"  • DVWA: http://dvwa.local/ (si installé localement)")
        print(f"  • WebGoat: http://localhost:8080/WebGoat/ (si installé)")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Note: On ne supprime pas les fichiers temporaires pour permettre l'exploration
        print(f"\n{Fore.YELLOW}💡 Les fichiers de démonstration sont conservés pour exploration")

def demo_detection_vulnerabilites():
    """Démonstration spécifique de la détection de vulnérabilités"""
    print(f"\n{Fore.BLUE}🚨 DÉMONSTRATION DÉTECTION DE VULNÉRABILITÉS")
    print("=" * 50)
    
    from scanner_vulnerabilites import VulnerabilityScanner
    from unittest.mock import Mock, patch
    
    scanner = VulnerabilityScanner()
    
    # Scénarios de test pour différents types de vulnérabilités
    scenarios_vulns = [
        {
            'nom': 'XSS Reflected - Formulaire de recherche',
            'url': 'http://test-xss.com/search',
            'form_html': '''
            <form method="get" action="/search">
                <input name="q" type="text" placeholder="Rechercher...">
                <input type="submit" value="Rechercher">
            </form>
            ''',
            'payload_response': 'Résultats pour: <script>alert("XSS")</script>',
            'vuln_type': 'XSS'
        },
        {
            'nom': 'SQL Injection - Formulaire de login',
            'url': 'http://test-sql.com/login',
            'form_html': '''
            <form method="post" action="/login">
                <input name="username" type="text" placeholder="Username">
                <input name="password" type="password" placeholder="Password">
                <input type="submit" value="Login">
            </form>
            ''',
            'payload_response': 'MySQL error: You have an error in your SQL syntax near "OR 1=1"',
            'vuln_type': 'SQL_INJECTION'
        },
        {
            'nom': 'CSRF - Formulaire sans protection',
            'url': 'http://test-csrf.com/transfer',
            'form_html': '''
            <form method="post" action="/transfer">
                <input name="to_account" type="text" placeholder="Compte destinataire">
                <input name="amount" type="number" placeholder="Montant">
                <input type="submit" value="Transférer">
            </form>
            ''',
            'payload_response': 'Transfert effectué avec succès',
            'vuln_type': 'CSRF'
        }
    ]
    
    print(f"{Fore.CYAN}🧪 Test de détection sur {len(scenarios_vulns)} types de vulnérabilités:")
    
    for scenario in scenarios_vulns:
        print(f"\n{Fore.YELLOW}🔍 Test: {scenario['nom']}")
        print(f"   URL: {scenario['url']}")
        
        # Créer la page HTML avec le formulaire
        html_page = f'''
        <html>
        <head><title>Test Vulnerability</title></head>
        <body>
            <h1>Test Page</h1>
            {scenario['form_html']}
        </body>
        </html>
        '''
        
        # Mock des réponses HTTP
        with patch('requests.Session.get') as mock_get, \
             patch('requests.Session.post') as mock_post:
            
            # Réponse pour la page principale
            main_response = Mock()
            main_response.status_code = 200
            main_response.headers = {'Server': 'Apache/2.4.41'}
            main_response.text = html_page
            main_response.content = html_page.encode()
            mock_get.return_value = main_response
            
            # Réponse pour les tests de payload (avec la vulnérabilité)
            payload_response = Mock()
            payload_response.status_code = 200
            payload_response.text = scenario['payload_response']
            mock_post.return_value = payload_response
            mock_get.return_value = payload_response  # Pour les GET aussi
            
            # Exécuter le scan
            resultat = scanner.scan_url(scenario['url'])
            
            # Analyser les résultats
            vulns_trouvees = [v for v in resultat.vulnerabilites if scenario['vuln_type'] in v.type_vuln]
            
            if vulns_trouvees:
                print(f"   {Fore.RED}🚨 Vulnérabilité détectée: {vulns_trouvees[0].type_vuln}")
                print(f"      Sévérité: {vulns_trouvees[0].severite}")
                print(f"      Description: {vulns_trouvees[0].description}")
            else:
                # Chercher d'autres types de vulnérabilités détectées
                autres_vulns = [v.type_vuln for v in resultat.vulnerabilites]
                if autres_vulns:
                    print(f"   {Fore.YELLOW}⚠️  Autres vulnérabilités détectées: {', '.join(set(autres_vulns))}")
                else:
                    print(f"   {Fore.GREEN}✅ Aucune vulnérabilité de ce type détectée")
    
    print(f"\n{Fore.GREEN}✅ Tests de détection de vulnérabilités terminés")

def demo_rapports():
    """Démonstration de génération de rapports"""
    print(f"\n{Fore.BLUE}📄 DÉMONSTRATION GÉNÉRATION DE RAPPORTS")
    print("=" * 50)
    
    from scanner_vulnerabilites import ReportGenerator, ResultatScan, VulnerabiliteDetectee
    from datetime import datetime
    
    generator = ReportGenerator()
    
    # Créer des données de test réalistes
    vulnerabilites_test = [
        VulnerabiliteDetectee(
            id="xss_001",
            url="http://demo.com/search",
            type_vuln="XSS_REFLECTED",
            severite="HIGH",
            description="XSS Reflected détecté dans le formulaire de recherche",
            details={
                "field": "search_query",
                "payload": '<script>alert("XSS")</script>',
                "reflected": True
            },
            remediation="Encoder toutes les entrées utilisateur avant affichage et implémenter une CSP stricte",
            timestamp=datetime.now()
        ),
        VulnerabiliteDetectee(
            id="sql_001",
            url="http://demo.com/login",
            type_vuln="SQL_INJECTION",
            severite="CRITICAL",
            description="Injection SQL possible dans le formulaire de connexion",
            details={
                "field": "username",
                "payload": "admin' OR '1'='1",
                "error_message": "MySQL syntax error detected"
            },
            remediation="Utiliser des requêtes préparées et valider toutes les entrées",
            timestamp=datetime.now()
        ),
        VulnerabiliteDetectee(
            id="header_001",
            url="http://demo.com",
            type_vuln="HEADER_MISSING",
            severite="MEDIUM",
            description="En-tête de sécurité Content-Security-Policy manquant",
            details={
                "header": "Content-Security-Policy",
                "impact": "Risque d'attaques XSS non mitigées"
            },
            remediation="Ajouter l'en-tête CSP avec une politique restrictive",
            timestamp=datetime.now()
        ),
        VulnerabiliteDetectee(
            id="file_001",
            url="http://demo.com/.env",
            type_vuln="SENSITIVE_FILE",
            severite="HIGH",
            description="Fichier sensible accessible publiquement",
            details={
                "file_path": "/.env",
                "file_size": 1024,
                "contains_secrets": True
            },
            remediation="Restreindre l'accès au fichier .env et le déplacer hors du webroot",
            timestamp=datetime.now()
        )
    ]
    
    # Créer différents types de résultats pour démonstration
    scenarios_rapports = [
        {
            'nom': 'Site très vulnérable',
            'url': 'http://vulnerable-demo.com',
            'score': 25,
            'vulnerabilites': vulnerabilites_test,
            'technologies': ['Apache', 'PHP', 'MySQL', 'WordPress'],
            'ssl': {'valide': False, 'erreur': 'Certificat auto-signé'},
            'headers': {
                'Strict-Transport-Security': False,
                'Content-Security-Policy': False,
                'X-Content-Type-Options': False,
                'X-Frame-Options': False,
                'X-XSS-Protection': False,
                'Referrer-Policy': False,
                'Feature-Policy': False
            }
        },
        {
            'nom': 'Site moyennement sécurisé',
            'url': 'https://medium-security.com',
            'score': 65,
            'vulnerabilites': vulnerabilites_test[:2],  # Moins de vulnérabilités
            'technologies': ['Nginx', 'Node.js', 'Express'],
            'ssl': {'valide': True, 'version_ssl': 'TLSv1.2', 'bits_chiffrement': 256},
            'headers': {
                'Strict-Transport-Security': True,
                'Content-Security-Policy': False,
                'X-Content-Type-Options': True,
                'X-Frame-Options': True,
                'X-XSS-Protection': True,
                'Referrer-Policy': False,
                'Feature-Policy': False
            }
        },
        {
            'nom': 'Site très sécurisé',
            'url': 'https://secure-demo.com',
            'score': 95,
            'vulnerabilites': [],  # Aucune vulnérabilité
            'technologies': ['Nginx', 'Python', 'Django'],
            'ssl': {'valide': True, 'version_ssl': 'TLSv1.3', 'bits_chiffrement': 256},
            'headers': {
                'Strict-Transport-Security': True,
                'Content-Security-Policy': True,
                'X-Content-Type-Options': True,
                'X-Frame-Options': True,
                'X-XSS-Protection': True,
                'Referrer-Policy': True,
                'Feature-Policy': True
            }
        }
    ]
    
    print(f"{Fore.CYAN}📋 Génération de {len(scenarios_rapports)} rapports de démonstration:")
    
    for i, scenario in enumerate(scenarios_rapports, 1):
        print(f"\n{Fore.YELLOW}📄 Rapport {i}: {scenario['nom']}")
        
        # Créer le résultat de scan
        resultat = ResultatScan(
            url=scenario['url'],
            timestamp=datetime.now(),
            duree_scan=2.5 + i * 0.5,
            status_code=200,
            technologies=scenario['technologies'],
            vulnerabilites=scenario['vulnerabilites'],
            en_tetes_securite=scenario['headers'],
            formulaires_detectes=2,
            certificat_ssl=scenario['ssl'],
            score_securite=scenario['score']
        )
        
        # Générer le rapport
        rapport_path = generator.generer_rapport(resultat)
        
        if os.path.exists(rapport_path):
            taille = os.path.getsize(rapport_path)
            print(f"   ✓ Généré: {rapport_path}")
            print(f"      Taille: {taille:,} bytes")
            print(f"      Score: {scenario['score']}/100")
            print(f"      Vulnérabilités: {len(scenario['vulnerabilites'])}")
            print(f"      Technologies: {len(scenario['technologies'])}")
        else:
            print(f"   {Fore.RED}❌ Erreur lors de la génération")
    
    print(f"\n{Fore.GREEN}✅ Tous les rapports de démonstration ont été générés")
    print(f"{Fore.CYAN}💡 Ouvrez les fichiers HTML dans votre navigateur pour voir les rapports")

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "complete":
            demo_complete()
        elif mode == "vulnerabilites":
            demo_detection_vulnerabilites()
        elif mode == "rapports":
            demo_rapports()
        else:
            print(f"{Fore.RED}Mode inconnu: {mode}")
            print(f"{Fore.CYAN}Modes disponibles: complete, vulnerabilites, rapports")
    else:
        # Menu interactif
        print(f"{Fore.BLUE}🕷️ DÉMONSTRATIONS SCANNER DE VULNÉRABILITÉS WEB")
        print("=" * 55)
        
        options = {
            "1": ("Démonstration complète", demo_complete),
            "2": ("Test détection vulnérabilités", demo_detection_vulnerabilites),
            "3": ("Génération de rapports", demo_rapports),
            "4": ("Quitter", None)
        }
        
        while True:
            print(f"\n{Fore.CYAN}Choisissez une démonstration:")
            for key, (description, _) in options.items():
                print(f"{Fore.YELLOW}{key}. {description}")
            
            choice = input(f"\n{Fore.WHITE}Votre choix (1-4): ").strip()
            
            if choice in options:
                description, func = options[choice]
                if func is None:
                    print(f"{Fore.GREEN}Au revoir!")
                    break
                else:
                    print(f"\n{Fore.BLUE}>>> {description}")
                    func()
                    input(f"\n{Fore.WHITE}Appuyez sur Entrée pour continuer...")
            else:
                print(f"{Fore.RED}Choix invalide. Veuillez choisir entre 1 et 4.")

if __name__ == "__main__":
    main()