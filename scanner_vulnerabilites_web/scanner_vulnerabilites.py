#!/usr/bin/env python3
"""
Scanner de Vulnérabilités Web
Scanner automatisé pour détecter les vulnérabilités de sécurité web communes

Fonctionnalités:
- Scan des formulaires web
- Détection XSS (Reflected & Stored)
- Test d'injection SQL basique
- Vérification SSL/TLS
- Analyse des en-têtes de sécurité
- Détection de technologies utilisées
- Rapport HTML détaillé
- Mode batch pour plusieurs URLs
"""

import os
import sys
import sqlite3
import json
import re
import time
import urllib.parse
import ssl
import socket
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# Imports web et sécurité
import requests
from bs4 import BeautifulSoup
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Utilitaires
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama et désactiver les warnings SSL
init(autoreset=True)
urllib3.disable_warnings(InsecureRequestWarning)

@dataclass
class VulnerabiliteDetectee:
    """Classe pour représenter une vulnérabilité détectée"""
    id: str
    url: str
    type_vuln: str  # XSS, SQL_INJECTION, SSL_ISSUE, HEADER_MISSING, etc.
    severite: str   # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    details: Dict[str, Any]
    remediation: str
    timestamp: datetime
    confirmed: bool = False

@dataclass
class ResultatScan:
    """Classe pour représenter les résultats d'un scan"""
    url: str
    timestamp: datetime
    duree_scan: float
    status_code: int
    technologies: List[str]
    vulnerabilites: List[VulnerabiliteDetectee]
    en_tetes_securite: Dict[str, bool]
    formulaires_detectes: int
    certificat_ssl: Dict[str, Any]
    score_securite: int

class TechnologyDetector:
    """Détecteur de technologies web"""
    
    def __init__(self):
        self.signatures = {
            # Serveurs web
            'Apache': [r'Apache/[\d\.]+', r'Server.*Apache'],
            'Nginx': [r'nginx/[\d\.]+', r'Server.*nginx'],
            'IIS': [r'Microsoft-IIS/[\d\.]+', r'Server.*IIS'],
            
            # Frameworks
            'WordPress': [r'wp-content/', r'wp-includes/', r'/wp-json/'],
            'Drupal': [r'/sites/default/', r'Drupal.settings'],
            'Joomla': [r'/components/com_', r'Joomla!'],
            'Django': [r'csrfmiddlewaretoken', r'django'],
            'Flask': [r'flask', r'werkzeug'],
            'Express': [r'X-Powered-By.*Express'],
            'React': [r'react', r'_react'],
            'Vue.js': [r'vue\.js', r'__vue__'],
            'Angular': [r'ng-version', r'angular'],
            
            # CMS et plateformes
            'Shopify': [r'shopify', r'cdn.shopify.com'],
            'Magento': [r'magento', r'/skin/frontend/'],
            'PrestaShop': [r'prestashop', r'/modules/'],
            
            # Langages
            'PHP': [r'\.php', r'X-Powered-By.*PHP', r'PHPSESSID'],
            'ASP.NET': [r'\.aspx', r'X-AspNet-Version', r'ASP.NET'],
            'JSP': [r'\.jsp', r'jsessionid'],
            'Python': [r'X-Powered-By.*Python'],
            'Node.js': [r'X-Powered-By.*Node'],
            
            # Bases de données
            'MySQL': [r'mysql', r'phpMyAdmin'],
            'PostgreSQL': [r'postgresql', r'postgres'],
            'MongoDB': [r'mongodb', r'mongo'],
            
            # CDN et services
            'Cloudflare': [r'cloudflare', r'cf-ray'],
            'jQuery': [r'jquery', r'jQuery'],
            'Bootstrap': [r'bootstrap', r'Bootstrap'],
        }
    
    def detecter_technologies(self, response: requests.Response, soup: BeautifulSoup) -> List[str]:
        """Détecter les technologies utilisées"""
        technologies = []
        
        # Vérifier dans les en-têtes
        headers_str = ' '.join([f"{k}: {v}" for k, v in response.headers.items()])
        
        # Vérifier dans le contenu HTML
        html_content = response.text
        
        for tech, patterns in self.signatures.items():
            for pattern in patterns:
                if (re.search(pattern, headers_str, re.IGNORECASE) or 
                    re.search(pattern, html_content, re.IGNORECASE)):
                    technologies.append(tech)
                    break
        
        # Détecter via les meta tags
        meta_generator = soup.find('meta', {'name': 'generator'})
        if meta_generator and meta_generator.get('content'):
            technologies.append(f"Generator: {meta_generator['content']}")
        
        return list(set(technologies))

class SSLAnalyzer:
    """Analyseur SSL/TLS"""
    
    def analyser_ssl(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Analyser la configuration SSL d'un site"""
        try:
            # Connexion SSL
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        'valide': True,
                        'version_ssl': version,
                        'cipher_suite': cipher[0] if cipher else None,
                        'bits_chiffrement': cipher[2] if cipher else None,
                        'certificat': {
                            'subject': dict(x[0] for x in cert.get('subject', [])),
                            'issuer': dict(x[0] for x in cert.get('issuer', [])),
                            'version': cert.get('version'),
                            'not_before': cert.get('notBefore'),
                            'not_after': cert.get('notAfter'),
                            'serial_number': cert.get('serialNumber'),
                            'san': cert.get('subjectAltName', [])
                        }
                    }
                    
        except Exception as e:
            return {
                'valide': False,
                'erreur': str(e),
                'details': f'Erreur lors de la vérification SSL: {e}'
            }

class SecurityHeadersChecker:
    """Vérificateur d'en-têtes de sécurité"""
    
    def __init__(self):
        self.headers_securite = {
            'Strict-Transport-Security': {
                'description': 'Force HTTPS pour toutes les connexions futures',
                'severite': 'MEDIUM'
            },
            'Content-Security-Policy': {
                'description': 'Prévient les attaques XSS et injection de code',
                'severite': 'HIGH'
            },
            'X-Content-Type-Options': {
                'description': 'Empêche le sniffing de type MIME',
                'severite': 'MEDIUM'
            },
            'X-Frame-Options': {
                'description': 'Protection contre le clickjacking',
                'severite': 'MEDIUM'
            },
            'X-XSS-Protection': {
                'description': 'Protection XSS intégrée du navigateur',
                'severite': 'LOW'
            },
            'Referrer-Policy': {
                'description': 'Contrôle les informations de référent envoyées',
                'severite': 'LOW'
            },
            'Feature-Policy': {
                'description': 'Contrôle les fonctionnalités du navigateur',
                'severite': 'LOW'
            }
        }
    
    def verifier_headers(self, headers: Dict[str, str]) -> Dict[str, bool]:
        """Vérifier la présence des en-têtes de sécurité"""
        resultats = {}
        
        for header, info in self.headers_securite.items():
            present = any(header.lower() == h.lower() for h in headers.keys())
            resultats[header] = present
            
        return resultats

class VulnerabilityScanner:
    """Scanner principal de vulnérabilités"""
    
    def __init__(self, timeout=10, user_agent=None):
        self.timeout = timeout
        self.user_agent = user_agent or "WebVulnScanner/1.0 (Security Testing)"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.session.verify = False  # Pour les tests SSL
        
        # Composants
        self.tech_detector = TechnologyDetector()
        self.ssl_analyzer = SSLAnalyzer()
        self.headers_checker = SecurityHeadersChecker()
        
        # Payloads pour les tests
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            "';alert('XSS');//",
            '<iframe src="javascript:alert(\'XSS\')"></iframe>'
        ]
        
        self.sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "' OR 'a'='a",
            "admin'--",
            "' OR 1=1#",
            "') OR ('1'='1"
        ]
        
        self.vulnerabilites_detectees = []
    
    def scan_url(self, url: str) -> ResultatScan:
        """Scanner une URL complète"""
        print(f"{Fore.CYAN}🔍 Scan de: {url}")
        debut_scan = time.time()
        
        try:
            # Requête initiale
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire le hostname pour SSL
            parsed_url = urllib.parse.urlparse(url)
            hostname = parsed_url.hostname
            
            # Détection des technologies
            technologies = self.tech_detector.detecter_technologies(response, soup)
            print(f"{Fore.YELLOW}📋 Technologies détectées: {', '.join(technologies)}")
            
            # Vérification SSL/TLS
            certificat_ssl = {}
            if parsed_url.scheme == 'https':
                certificat_ssl = self.ssl_analyzer.analyser_ssl(hostname)
                if certificat_ssl.get('valide'):
                    print(f"{Fore.GREEN}🔒 SSL/TLS: Valide ({certificat_ssl.get('version_ssl')})")
                else:
                    print(f"{Fore.RED}🔓 SSL/TLS: Problèmes détectés")
                    self._ajouter_vulnerabilite(
                        url, 'SSL_ISSUE', 'HIGH',
                        f"Problème SSL/TLS: {certificat_ssl.get('erreur', 'Configuration invalide')}",
                        certificat_ssl,
                        "Configurer correctement SSL/TLS avec un certificat valide"
                    )
            
            # Vérification des en-têtes de sécurité
            headers_securite = self.headers_checker.verifier_headers(response.headers)
            headers_manquants = [h for h, present in headers_securite.items() if not present]
            
            if headers_manquants:
                print(f"{Fore.YELLOW}⚠️  En-têtes de sécurité manquants: {len(headers_manquants)}")
                for header in headers_manquants:
                    info = self.headers_checker.headers_securite[header]
                    self._ajouter_vulnerabilite(
                        url, 'HEADER_MISSING', info['severite'],
                        f"En-tête de sécurité manquant: {header}",
                        {'header': header, 'description': info['description']},
                        f"Ajouter l'en-tête {header} à la configuration du serveur"
                    )
            
            # Recherche et test des formulaires
            formulaires = soup.find_all('form')
            print(f"{Fore.BLUE}📝 Formulaires détectés: {len(formulaires)}")
            
            for i, form in enumerate(formulaires):
                print(f"{Fore.CYAN}   📝 Test du formulaire {i+1}...")
                self._tester_formulaire(url, form, soup)
            
            # Tests de détection XSS dans les paramètres URL
            self._tester_xss_parametres(url)
            
            # Recherche de fichiers sensibles
            self._tester_fichiers_sensibles(url)
            
            # Calcul du score de sécurité
            score_securite = self._calculer_score_securite(len(headers_manquants), len(self.vulnerabilites_detectees))
            
            duree_scan = time.time() - debut_scan
            
            resultat = ResultatScan(
                url=url,
                timestamp=datetime.now(),
                duree_scan=duree_scan,
                status_code=response.status_code,
                technologies=technologies,
                vulnerabilites=self.vulnerabilites_detectees.copy(),
                en_tetes_securite=headers_securite,
                formulaires_detectes=len(formulaires),
                certificat_ssl=certificat_ssl,
                score_securite=score_securite
            )
            
            self.vulnerabilites_detectees.clear()  # Reset pour le prochain scan
            
            print(f"{Fore.GREEN}✅ Scan terminé en {duree_scan:.2f}s")
            print(f"{Fore.BLUE}📊 Score de sécurité: {score_securite}/100")
            
            return resultat
            
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Erreur lors du scan: {e}")
            return ResultatScan(
                url=url,
                timestamp=datetime.now(),
                duree_scan=time.time() - debut_scan,
                status_code=0,
                technologies=[],
                vulnerabilites=[],
                en_tetes_securite={},
                formulaires_detectes=0,
                certificat_ssl={'valide': False, 'erreur': str(e)},
                score_securite=0
            )
    
    def _tester_formulaire(self, base_url: str, form: BeautifulSoup, soup: BeautifulSoup):
        """Tester un formulaire pour les vulnérabilités"""
        action = form.get('action', '')
        method = form.get('method', 'get').lower()
        
        # URL complète du formulaire
        if action.startswith('http'):
            form_url = action
        elif action.startswith('/'):
            parsed = urllib.parse.urlparse(base_url)
            form_url = f"{parsed.scheme}://{parsed.netloc}{action}"
        else:
            form_url = urllib.parse.urljoin(base_url, action)
        
        # Récupérer les champs du formulaire
        inputs = form.find_all(['input', 'textarea', 'select'])
        form_data = {}
        
        for input_field in inputs:
            name = input_field.get('name')
            if name:
                input_type = input_field.get('type', 'text')
                if input_type in ['text', 'email', 'search', 'url']:
                    form_data[name] = 'test_value'
                elif input_field.name == 'textarea':
                    form_data[name] = 'test_textarea'
        
        if not form_data:
            return
        
        # Test XSS
        self._tester_xss_formulaire(form_url, method, form_data)
        
        # Test SQL Injection
        self._tester_sql_injection_formulaire(form_url, method, form_data)
        
        # Vérifier les protections CSRF
        csrf_token = form.find('input', {'name': re.compile(r'csrf|token', re.I)})
        if not csrf_token:
            self._ajouter_vulnerabilite(
                form_url, 'CSRF_MISSING', 'MEDIUM',
                'Aucune protection CSRF détectée sur ce formulaire',
                {'form_action': action, 'method': method},
                'Implémenter des tokens CSRF pour protéger contre les attaques Cross-Site Request Forgery'
            )
    
    def _tester_xss_formulaire(self, form_url: str, method: str, form_data: Dict[str, str]):
        """Tester les vulnérabilités XSS sur un formulaire"""
        for field_name, original_value in form_data.items():
            for payload in self.xss_payloads[:3]:  # Limiter les tests pour la performance
                test_data = form_data.copy()
                test_data[field_name] = payload
                
                try:
                    if method == 'post':
                        response = self.session.post(form_url, data=test_data, timeout=self.timeout)
                    else:
                        response = self.session.get(form_url, params=test_data, timeout=self.timeout)
                    
                    # Vérifier si le payload est reflété dans la réponse
                    if payload in response.text and response.status_code == 200:
                        self._ajouter_vulnerabilite(
                            form_url, 'XSS_REFLECTED', 'HIGH',
                            f'XSS Reflected détecté dans le champ "{field_name}"',
                            {
                                'field': field_name,
                                'payload': payload,
                                'method': method,
                                'reflected_in_response': True
                            },
                            'Filtrer et encoder toutes les entrées utilisateur avant affichage'
                        )
                        print(f"{Fore.RED}🚨 XSS détecté dans {field_name}")
                        break
                        
                except requests.exceptions.RequestException:
                    continue
    
    def _tester_sql_injection_formulaire(self, form_url: str, method: str, form_data: Dict[str, str]):
        """Tester les vulnérabilités SQL Injection sur un formulaire"""
        for field_name, original_value in form_data.items():
            for payload in self.sql_payloads[:3]:  # Limiter les tests
                test_data = form_data.copy()
                test_data[field_name] = payload
                
                try:
                    if method == 'post':
                        response = self.session.post(form_url, data=test_data, timeout=self.timeout)
                    else:
                        response = self.session.get(form_url, params=test_data, timeout=self.timeout)
                    
                    # Vérifier les signes d'erreur SQL
                    sql_errors = [
                        'mysql_fetch_array()', 'ORA-01756', 'Microsoft OLE DB Provider',
                        'mysql_fetch_assoc()', 'pg_query()', 'sqlite_query()',
                        'SQL syntax', 'MySQL server version', 'Warning: mysql_',
                        'ORA-00933', 'PostgreSQL query failed', 'SQLite/JDBCDriver'
                    ]
                    
                    response_text = response.text.lower()
                    for error in sql_errors:
                        if error.lower() in response_text:
                            self._ajouter_vulnerabilite(
                                form_url, 'SQL_INJECTION', 'CRITICAL',
                                f'Injection SQL possible dans le champ "{field_name}"',
                                {
                                    'field': field_name,
                                    'payload': payload,
                                    'error_found': error,
                                    'method': method
                                },
                                'Utiliser des requêtes préparées et valider toutes les entrées'
                            )
                            print(f"{Fore.RED}🚨 SQL Injection détectée dans {field_name}")
                            break
                            
                except requests.exceptions.RequestException:
                    continue
    
    def _tester_xss_parametres(self, url: str):
        """Tester XSS via les paramètres GET"""
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.query:
            return
        
        params = urllib.parse.parse_qs(parsed_url.query)
        
        for param_name, param_values in params.items():
            for payload in self.xss_payloads[:2]:  # Tests limités
                test_params = {param_name: payload}
                test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                
                try:
                    response = self.session.get(test_url, params=test_params, timeout=self.timeout)
                    
                    if payload in response.text and response.status_code == 200:
                        self._ajouter_vulnerabilite(
                            test_url, 'XSS_REFLECTED', 'HIGH',
                            f'XSS Reflected détecté dans le paramètre "{param_name}"',
                            {
                                'parameter': param_name,
                                'payload': payload,
                                'method': 'GET'
                            },
                            'Filtrer et encoder tous les paramètres avant affichage'
                        )
                        print(f"{Fore.RED}🚨 XSS détecté dans le paramètre {param_name}")
                        break
                        
                except requests.exceptions.RequestException:
                    continue
    
    def _tester_fichiers_sensibles(self, url: str):
        """Tester l'accès à des fichiers sensibles"""
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        fichiers_sensibles = [
            '/robots.txt', '/.htaccess', '/web.config', '/sitemap.xml',
            '/admin', '/admin.php', '/administrator', '/wp-admin',
            '/phpmyadmin', '/mysql', '/database',
            '/.env', '/config.php', '/config.json',
            '/backup.sql', '/dump.sql', '/.git/config',
            '/server-status', '/server-info'
        ]
        
        for fichier in fichiers_sensibles:
            test_url = base_url + fichier
            
            try:
                response = self.session.get(test_url, timeout=5)
                
                if response.status_code == 200:
                    # Vérifier si c'est vraiment sensible (pas une page d'erreur)
                    if len(response.text) > 50 and 'not found' not in response.text.lower():
                        severite = 'HIGH' if any(x in fichier for x in ['.env', 'config', 'admin', 'backup', 'dump']) else 'MEDIUM'
                        
                        self._ajouter_vulnerabilite(
                            test_url, 'SENSITIVE_FILE', severite,
                            f'Fichier sensible accessible: {fichier}',
                            {
                                'file_path': fichier,
                                'file_size': len(response.text),
                                'status_code': response.status_code
                            },
                            f'Restreindre l\'accès au fichier {fichier} ou le supprimer'
                        )
                        print(f"{Fore.YELLOW}⚠️  Fichier sensible trouvé: {fichier}")
                        
            except requests.exceptions.RequestException:
                continue
    
    def _ajouter_vulnerabilite(self, url: str, type_vuln: str, severite: str, 
                              description: str, details: Dict[str, Any], remediation: str):
        """Ajouter une vulnérabilité détectée"""
        vuln = VulnerabiliteDetectee(
            id=f"{type_vuln}_{int(time.time() * 1000000)}_{len(self.vulnerabilites_detectees)}_{hash(url) % 10000}",
            url=url,
            type_vuln=type_vuln,
            severite=severite,
            description=description,
            details=details,
            remediation=remediation,
            timestamp=datetime.now()
        )
        
        self.vulnerabilites_detectees.append(vuln)
    
    def _calculer_score_securite(self, headers_manquants: int, nb_vulnerabilites: int) -> int:
        """Calculer un score de sécurité sur 100"""
        score = 100
        
        # Pénalités pour en-têtes manquants
        score -= headers_manquants * 5
        
        # Pénalités pour vulnérabilités
        for vuln in self.vulnerabilites_detectees:
            if vuln.severite == 'CRITICAL':
                score -= 25
            elif vuln.severite == 'HIGH':
                score -= 15
            elif vuln.severite == 'MEDIUM':
                score -= 10
            elif vuln.severite == 'LOW':
                score -= 5
        
        return max(0, score)

class DatabaseManager:
    """Gestionnaire de base de données pour les résultats"""
    
    def __init__(self, db_path="scans_vulnerabilites.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des scans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                duree_scan REAL,
                status_code INTEGER,
                technologies TEXT,
                score_securite INTEGER,
                formulaires_detectes INTEGER,
                certificat_ssl TEXT,
                en_tetes_securite TEXT
            )
        ''')
        
        # Table des vulnérabilités
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilites (
                id TEXT PRIMARY KEY,
                scan_id INTEGER,
                url TEXT NOT NULL,
                type_vuln TEXT NOT NULL,
                severite TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT,
                remediation TEXT,
                timestamp DATETIME NOT NULL,
                confirmed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def sauvegarder_scan(self, resultat: ResultatScan) -> int:
        """Sauvegarder un résultat de scan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insérer le scan
        cursor.execute('''
            INSERT INTO scans (
                url, timestamp, duree_scan, status_code, technologies,
                score_securite, formulaires_detectes, certificat_ssl, en_tetes_securite
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resultat.url,
            resultat.timestamp,
            resultat.duree_scan,
            resultat.status_code,
            json.dumps(resultat.technologies),
            resultat.score_securite,
            resultat.formulaires_detectes,
            json.dumps(resultat.certificat_ssl),
            json.dumps(resultat.en_tetes_securite)
        ))
        
        scan_id = cursor.lastrowid
        
        # Insérer les vulnérabilités
        for vuln in resultat.vulnerabilites:
            cursor.execute('''
                INSERT INTO vulnerabilites (
                    id, scan_id, url, type_vuln, severite, description,
                    details, remediation, timestamp, confirmed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vuln.id, scan_id, vuln.url, vuln.type_vuln, vuln.severite,
                vuln.description, json.dumps(vuln.details), vuln.remediation,
                vuln.timestamp, vuln.confirmed
            ))
        
        conn.commit()
        conn.close()
        
        return scan_id

class ReportGenerator:
    """Générateur de rapports HTML"""
    
    def __init__(self):
        self.template_html = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Sécurité Web - {{url}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header .meta { opacity: 0.9; font-size: 1.1rem; }
        .score-section { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .score-card { background: white; padding: 1.5rem; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .score-number { font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem; }
        .score-critical { color: #e74c3c; }
        .score-high { color: #f39c12; }
        .score-medium { color: #f1c40f; }
        .score-good { color: #27ae60; }
        .section { background: white; margin-bottom: 2rem; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section-header { background: #34495e; color: white; padding: 1rem 1.5rem; font-size: 1.2rem; font-weight: 600; }
        .section-content { padding: 1.5rem; }
        .vuln-item { border-left: 4px solid; padding: 1rem; margin-bottom: 1rem; border-radius: 0 5px 5px 0; }
        .vuln-critical { border-color: #e74c3c; background: #ffebee; }
        .vuln-high { border-color: #f39c12; background: #fff8e1; }
        .vuln-medium { border-color: #f1c40f; background: #fffde7; }
        .vuln-low { border-color: #95a5a6; background: #f5f5f5; }
        .vuln-title { font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem; }
        .vuln-description { margin-bottom: 0.5rem; }
        .vuln-remediation { background: rgba(39, 174, 96, 0.1); padding: 0.5rem; border-radius: 5px; border-left: 3px solid #27ae60; font-size: 0.9rem; }
        .tech-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .tech-tag { background: #3498db; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
        .headers-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
        .header-item { display: flex; align-items: center; padding: 0.5rem; border-radius: 5px; }
        .header-present { background: #d5edda; color: #155724; }
        .header-missing { background: #f8d7da; color: #721c24; }
        .status-icon { margin-right: 0.5rem; font-weight: bold; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
        .stat-item { text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 5px; }
        .stat-number { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }
        .stat-label { font-size: 0.9rem; color: #6c757d; }
        .footer { text-align: center; margin-top: 2rem; padding: 1rem; color: #6c757d; }
        @media (max-width: 768px) { 
            .header h1 { font-size: 2rem; }
            .container { padding: 10px; }
            .section-content { padding: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ Rapport de Sécurité Web</h1>
            <div class="meta">
                <strong>URL:</strong> {{url}}<br>
                <strong>Scan effectué le:</strong> {{timestamp}}<br>
                <strong>Durée:</strong> {{duree}}s
            </div>
        </div>

        <div class="score-section">
            <div class="score-card">
                <div class="score-number {{score_class}}">{{score}}/100</div>
                <div>Score de Sécurité</div>
            </div>
            <div class="score-card">
                <div class="score-number">{{nb_vulnerabilites}}</div>
                <div>Vulnérabilités</div>
            </div>
            <div class="score-card">
                <div class="score-number">{{nb_formulaires}}</div>
                <div>Formulaires</div>
            </div>
            <div class="score-card">
                <div class="score-number">{{nb_technologies}}</div>
                <div>Technologies</div>
            </div>
        </div>

        {{#vulnerabilites}}
        <div class="section">
            <div class="section-header">🚨 Vulnérabilités Détectées ({{nb_vulnerabilites}})</div>
            <div class="section-content">
                {{#vuln_list}}
                <div class="vuln-item vuln-{{severite_class}}">
                    <div class="vuln-title">{{severite}} - {{type_vuln}}</div>
                    <div class="vuln-description">{{description}}</div>
                    <div class="vuln-remediation"><strong>Remédiation:</strong> {{remediation}}</div>
                </div>
                {{/vuln_list}}
            </div>
        </div>
        {{/vulnerabilites}}

        <div class="section">
            <div class="section-header">🛡️ En-têtes de Sécurité</div>
            <div class="section-content">
                <div class="headers-grid">
                    {{#headers}}
                    <div class="header-item {{#present}}header-present{{/present}}{{^present}}header-missing{{/present}}">
                        <span class="status-icon">{{#present}}✅{{/present}}{{^present}}❌{{/present}}</span>
                        {{name}}
                    </div>
                    {{/headers}}
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">🔧 Technologies Détectées</div>
            <div class="section-content">
                <div class="tech-list">
                    {{#technologies}}
                    <span class="tech-tag">{{.}}</span>
                    {{/technologies}}
                </div>
            </div>
        </div>

        {{#ssl_info}}
        <div class="section">
            <div class="section-header">🔒 Information SSL/TLS</div>
            <div class="section-content">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{{#valide}}✅{{/valide}}{{^valide}}❌{{/valide}}</div>
                        <div class="stat-label">Certificat Valide</div>
                    </div>
                    {{#valide}}
                    <div class="stat-item">
                        <div class="stat-number">{{version}}</div>
                        <div class="stat-label">Version SSL</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{bits}}bits</div>
                        <div class="stat-label">Chiffrement</div>
                    </div>
                    {{/valide}}
                </div>
            </div>
        </div>
        {{/ssl_info}}

        <div class="footer">
            <p>Rapport généré par WebVulnScanner - {{date_generation}}</p>
            <p>⚠️ Ce rapport est à des fins de test de sécurité uniquement. Utilisez de manière responsable.</p>
        </div>
    </div>
</body>
</html>'''
    
    def generer_rapport(self, resultat: ResultatScan, output_path: str = None) -> str:
        """Générer un rapport HTML"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parsed_url = urllib.parse.urlparse(resultat.url)
            safe_domain = re.sub(r'[^a-zA-Z0-9.-]', '_', parsed_url.netloc)
            output_path = f"rapport_securite_{safe_domain}_{timestamp}.html"
        
        # Déterminer la classe CSS pour le score
        if resultat.score_securite >= 80:
            score_class = "score-good"
        elif resultat.score_securite >= 60:
            score_class = "score-medium"
        elif resultat.score_securite >= 40:
            score_class = "score-high"
        else:
            score_class = "score-critical"
        
        # Préparer les données pour le template
        context = {
            'url': resultat.url,
            'timestamp': resultat.timestamp.strftime('%d/%m/%Y à %H:%M:%S'),
            'duree': f"{resultat.duree_scan:.2f}",
            'score': resultat.score_securite,
            'score_class': score_class,
            'nb_vulnerabilites': len(resultat.vulnerabilites),
            'nb_formulaires': resultat.formulaires_detectes,
            'nb_technologies': len(resultat.technologies),
            'date_generation': datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
        }
        
        # Générer le HTML simplement (sans template engine)
        html = self.template_html
        
        # Remplacer les variables simples
        for key, value in context.items():
            html = html.replace('{{' + key + '}}', str(value))
        
        # Traiter les vulnérabilités
        if resultat.vulnerabilites:
            vulns_html = ''
            for vuln in resultat.vulnerabilites:
                severite_class = vuln.severite.lower()
                vuln_html = f'''
                <div class="vuln-item vuln-{severite_class}">
                    <div class="vuln-title">{vuln.severite} - {vuln.type_vuln}</div>
                    <div class="vuln-description">{vuln.description}</div>
                    <div class="vuln-remediation"><strong>Remédiation:</strong> {vuln.remediation}</div>
                </div>
                '''
                vulns_html += vuln_html
            
            section_vulns = f'''
        <div class="section">
            <div class="section-header">🚨 Vulnérabilités Détectées ({len(resultat.vulnerabilites)})</div>
            <div class="section-content">
                {vulns_html}
            </div>
        </div>
            '''
            html = html.replace('{{#vulnerabilites}}', '').replace('{{/vulnerabilites}}', section_vulns)
            html = html.replace('{{#vuln_list}}', '').replace('{{/vuln_list}}', '')
        else:
            # Pas de vulnérabilités
            section_vulns = '''
        <div class="section">
            <div class="section-header">🚨 Vulnérabilités Détectées (0)</div>
            <div class="section-content">
                <p style="color: #27ae60; font-weight: bold;">✅ Aucune vulnérabilité détectée!</p>
            </div>
        </div>
            '''
            html = html.replace('{{#vulnerabilites}}', '').replace('{{/vulnerabilites}}', section_vulns)
        
        # Traiter les en-têtes de sécurité
        headers_html = ''
        for header, present in resultat.en_tetes_securite.items():
            status_class = "header-present" if present else "header-missing"
            icon = "✅" if present else "❌"
            headers_html += f'''
                    <div class="header-item {status_class}">
                        <span class="status-icon">{icon}</span>
                        {header}
                    </div>
            '''
        
        html = html.replace('{{#headers}}', '').replace('{{/headers}}', headers_html)
        
        # Traiter les technologies
        tech_html = ''
        for tech in resultat.technologies:
            tech_html += f'<span class="tech-tag">{tech}</span>\n                    '
        
        html = html.replace('{{#technologies}}', '').replace('{{/technologies}}', tech_html)
        
        # Traiter les infos SSL
        if resultat.certificat_ssl.get('valide'):
            ssl_html = f'''
        <div class="section">
            <div class="section-header">🔒 Information SSL/TLS</div>
            <div class="section-content">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">✅</div>
                        <div class="stat-label">Certificat Valide</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{resultat.certificat_ssl.get('version_ssl', 'N/A')}</div>
                        <div class="stat-label">Version SSL</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{resultat.certificat_ssl.get('bits_chiffrement', 'N/A')}bits</div>
                        <div class="stat-label">Chiffrement</div>
                    </div>
                </div>
            </div>
        </div>
            '''
        else:
            ssl_html = f'''
        <div class="section">
            <div class="section-header">🔒 Information SSL/TLS</div>
            <div class="section-content">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">❌</div>
                        <div class="stat-label">Certificat Invalide</div>
                    </div>
                </div>
                <p style="color: #e74c3c;">Erreur: {resultat.certificat_ssl.get('erreur', 'Configuration SSL invalide')}</p>
            </div>
        </div>
            '''
        
        html = html.replace('{{#ssl_info}}', '').replace('{{/ssl_info}}', ssl_html)
        
        # Nettoyer les balises template restantes
        html = re.sub(r'\{\{[^}]*\}\}', '', html)
        html = re.sub(r'\{\{[/#^][^}]*\}\}', '', html)
        
        # Sauvegarder le fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path

class WebVulnScanner:
    """Scanner principal de vulnérabilités web"""
    
    def __init__(self):
        self.scanner = VulnerabilityScanner()
        self.db_manager = DatabaseManager()
        self.report_generator = ReportGenerator()
    
    def scanner_url(self, url: str, generer_rapport: bool = True) -> ResultatScan:
        """Scanner une URL et optionnellement générer un rapport"""
        print(f"\n{Fore.BLUE}🕷️ WebVulnScanner - Scan de sécurité")
        print("=" * 50)
        
        # Validation de l'URL
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Scanner l'URL
        resultat = self.scanner.scan_url(url)
        
        # Sauvegarder en base
        scan_id = self.db_manager.sauvegarder_scan(resultat)
        print(f"{Fore.GREEN}💾 Scan sauvegardé avec l'ID: {scan_id}")
        
        # Générer le rapport HTML
        if generer_rapport:
            rapport_path = self.report_generator.generer_rapport(resultat)
            print(f"{Fore.CYAN}📄 Rapport généré: {rapport_path}")
        
        # Afficher le résumé
        self._afficher_resume(resultat)
        
        return resultat
    
    def scanner_multiple(self, urls: List[str], max_workers: int = 3) -> List[ResultatScan]:
        """Scanner plusieurs URLs en parallèle"""
        print(f"\n{Fore.BLUE}🕷️ WebVulnScanner - Scan multiple ({len(urls)} URLs)")
        print("=" * 50)
        
        resultats = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scanner_url, url, False): url for url in urls}
            
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    resultat = future.result()
                    resultats.append(resultat)
                except Exception as e:
                    print(f"{Fore.RED}❌ Erreur lors du scan de {url}: {e}")
        
        # Générer un rapport consolidé
        if resultats:
            self._generer_rapport_multiple(resultats)
        
        return resultats

    def _afficher_resume(self, resultat: ResultatScan):
        """Afficher un résumé du scan"""
        print(f"\n{Fore.YELLOW}📊 RÉSUMÉ DU SCAN")
        print("=" * 30)
        
        # Score de sécurité avec couleur
        if resultat.score_securite >= 80:
            score_color = Fore.GREEN
        elif resultat.score_securite >= 60:
            score_color = Fore.YELLOW
        else:
            score_color = Fore.RED
        
        print(f"🏆 Score de sécurité: {score_color}{resultat.score_securite}/100{Style.RESET_ALL}")
        print(f"🚨 Vulnérabilités: {len(resultat.vulnerabilites)}")
        print(f"📝 Formulaires: {resultat.formulaires_detectes}")
        print(f"🔧 Technologies: {len(resultat.technologies)}")
        print(f"⏱️  Durée du scan: {resultat.duree_scan:.2f}s")
        
        # Détail des vulnérabilités par sévérité
        if resultat.vulnerabilites:
            severites = {}
            for vuln in resultat.vulnerabilites:
                severites[vuln.severite] = severites.get(vuln.severite, 0) + 1
            
            print(f"\n{Fore.RED}🚨 Détail des vulnérabilités:")
            for severite, count in sorted(severites.items()):
                color = {
                    'CRITICAL': Fore.RED,
                    'HIGH': Fore.MAGENTA,
                    'MEDIUM': Fore.YELLOW,
                    'LOW': Fore.CYAN
                }.get(severite, Fore.WHITE)
                print(f"  {color}• {severite}: {count}{Style.RESET_ALL}")
        
        # Technologies principales
        if resultat.technologies:
            print(f"\n{Fore.BLUE}🔧 Technologies principales:")
            for tech in resultat.technologies[:5]:  # Top 5
                print(f"  • {tech}")
        
        print()

    def _generer_rapport_multiple(self, resultats: List[ResultatScan]):
        """Générer un rapport consolidé pour plusieurs scans"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rapport_path = f"rapport_securite_multiple_{timestamp}.html"
        
        # Pour simplifier, on génère juste les rapports individuels
        print(f"\n{Fore.CYAN}📄 Génération des rapports individuels...")
        for resultat in resultats:
            self.report_generator.generer_rapport(resultat)
        
        print(f"{Fore.GREEN}✅ Rapports générés pour {len(resultats)} sites")

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scanner de Vulnérabilités Web - Détection automatisée des failles de sécurité",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 scanner_vulnerabilites.py scan https://example.com
  python3 scanner_vulnerabilites.py scan https://example.com --no-report
  python3 scanner_vulnerabilites.py multiple urls.txt
  python3 scanner_vulnerabilites.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande scan
    scan_parser = subparsers.add_parser('scan', help='Scanner une URL')
    scan_parser.add_argument('url', help='URL cible à scanner')
    scan_parser.add_argument('--no-report', action='store_true', help='Ne pas générer de rapport HTML')
    scan_parser.add_argument('--timeout', type=int, default=10, help='Timeout des requêtes (secondes)')
    
    # Commande multiple
    multiple_parser = subparsers.add_parser('multiple', help='Scanner plusieurs URLs')
    multiple_parser.add_argument('file', help='Fichier contenant les URLs (une par ligne)')
    multiple_parser.add_argument('--workers', type=int, default=3, help='Nombre de workers parallèles')
    
    # Commande stats
    stats_parser = subparsers.add_parser('stats', help='Afficher les statistiques des scans')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Lister les scans précédents')
    list_parser.add_argument('--limit', type=int, default=10, help='Nombre de scans à afficher')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialiser le scanner
    scanner = WebVulnScanner()
    
    if args.command == 'scan':
        scanner.scanner_url(args.url, not args.no_report)
        
    elif args.command == 'multiple':
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                print(f"{Fore.RED}❌ Aucune URL trouvée dans le fichier {args.file}")
                return
            
            print(f"{Fore.GREEN}📋 {len(urls)} URLs trouvées dans {args.file}")
            scanner.scanner_multiple(urls, args.workers)
            
        except FileNotFoundError:
            print(f"{Fore.RED}❌ Fichier introuvable: {args.file}")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur: {e}")
    
    elif args.command == 'stats':
        afficher_statistiques(scanner.db_manager)
    
    elif args.command == 'list':
        lister_scans(scanner.db_manager, args.limit)

def afficher_statistiques(db_manager: DatabaseManager):
    """Afficher les statistiques des scans"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    print(f"\n{Fore.BLUE}📊 STATISTIQUES DES SCANS")
    print("=" * 30)
    
    # Statistiques générales
    cursor.execute('SELECT COUNT(*) FROM scans')
    total_scans = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM vulnerabilites')
    total_vulns = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(score_securite) FROM scans WHERE score_securite > 0')
    avg_score = cursor.fetchone()[0] or 0
    
    print(f"🔍 Total des scans: {total_scans}")
    print(f"🚨 Total des vulnérabilités: {total_vulns}")
    print(f"🏆 Score moyen: {avg_score:.1f}/100")
    
    # Top vulnérabilités
    cursor.execute('''
        SELECT type_vuln, COUNT(*) as count 
        FROM vulnerabilites 
        GROUP BY type_vuln 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    
    top_vulns = cursor.fetchall()
    if top_vulns:
        print(f"\n{Fore.RED}🚨 Top vulnérabilités:")
        for vuln_type, count in top_vulns:
            print(f"  • {vuln_type}: {count}")
    
    # Technologies les plus détectées
    cursor.execute('SELECT technologies FROM scans WHERE technologies != "[]"')
    all_techs = []
    for row in cursor.fetchall():
        try:
            techs = json.loads(row[0])
            all_techs.extend(techs)
        except:
            continue
    
    if all_techs:
        from collections import Counter
        tech_counter = Counter(all_techs)
        print(f"\n{Fore.BLUE}🔧 Technologies les plus détectées:")
        for tech, count in tech_counter.most_common(5):
            print(f"  • {tech}: {count}")
    
    conn.close()

def lister_scans(db_manager: DatabaseManager, limit: int = 10):
    """Lister les scans précédents"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT url, timestamp, score_securite, duree_scan,
               (SELECT COUNT(*) FROM vulnerabilites WHERE scan_id = scans.id) as nb_vulns
        FROM scans 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    scans = cursor.fetchall()
    
    if not scans:
        print(f"{Fore.YELLOW}📋 Aucun scan trouvé")
        return
    
    print(f"\n{Fore.BLUE}📋 DERNIERS SCANS ({len(scans)})")
    print("=" * 50)
    
    # Préparer les données pour tabulate
    headers = ["URL", "Date", "Score", "Durée", "Vulns"]
    rows = []
    
    for scan in scans:
        url, timestamp, score, duree, nb_vulns = scan
        
        # Formater la date
        try:
            date_obj = datetime.fromisoformat(timestamp)
            date_str = date_obj.strftime("%d/%m/%Y %H:%M")
        except:
            date_str = timestamp
        
        # Colorer le score
        if score >= 80:
            score_str = f"{Fore.GREEN}{score}/100{Style.RESET_ALL}"
        elif score >= 60:
            score_str = f"{Fore.YELLOW}{score}/100{Style.RESET_ALL}"
        else:
            score_str = f"{Fore.RED}{score}/100{Style.RESET_ALL}"
        
        # Limiter l'URL si trop longue
        display_url = url if len(url) <= 30 else url[:27] + "..."
        
        rows.append([
            display_url,
            date_str,
            score_str,
            f"{duree:.1f}s",
            nb_vulns
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    conn.close()

if __name__ == "__main__":
    main()