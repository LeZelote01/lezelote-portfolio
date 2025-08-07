#!/usr/bin/env python3
"""
🕷️ SCANNER DE VULNÉRABILITÉS WEB - FICHIER PRINCIPAL UNIFIÉ
============================================================

Orchestrateur centralisé pour toutes les fonctionnalités du scanner de vulnérabilités web.
Cette version intègre toutes les fonctionnalités dans une architecture modulaire unifiée.

🎯 FONCTIONNALITÉS INTÉGRÉES:
- ✅ Scanner de vulnérabilités web (XSS, SQL Injection, SSL/TLS)
- ✅ Détection de technologies et frameworks
- ✅ Analyse des en-têtes de sécurité
- ✅ Génération de rapports HTML détaillés
- ✅ Base de données SQLite pour historique
- ✅ Mode batch pour scans multiples
- ✅ Interface CLI complète avec statistiques

🚀 MODES D'UTILISATION:
- CLI: Scan en ligne de commande
- SINGLE: Scan d'une URL unique
- MULTIPLE: Scan de plusieurs URLs depuis un fichier
- STATS: Statistiques des scans précédents
- REPORT: Génération de rapports détaillés

Auteur: Système de Cybersécurité Avancé
Version: 1.0.0 - Production Ready
"""

import argparse
import sys
import os
import threading
import time
import signal
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from colorama import init, Fore, Style

# Configuration de colorama pour Windows/Linux
init(autoreset=True)

# Import du module principal
try:
    from scanner_vulnerabilites import WebVulnScanner, ResultatScan
    print("✅ Module scanner principal importé avec succès")
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur d'importation du module principal: {e}")
    print(f"{Fore.YELLOW}💡 Vérifiez que scanner_vulnerabilites.py est présent dans le même dossier")
    sys.exit(1)

class ScannerVulnerabilitesWeb:
    """Orchestrateur principal pour le scanner de vulnérabilités web"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.scanner = None
        self.running = False
        
        # Configuration du gestionnaire de signaux pour arrêt propre
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Configuration signaux échouée: {e}")
        
        self._print_banner()
        
    def _print_banner(self):
        """Afficher la bannière du système"""
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"{Fore.BLUE}🕷️ SCANNER DE VULNÉRABILITÉS WEB - VERSION ORCHESTRÉE v{self.version}")
        print(f"{Fore.BLUE}{'='*80}")
        print(f"{Fore.CYAN}🎯 Scanner automatisé pour vulnérabilités de sécurité web")
        print(f"{Fore.CYAN}✨ XSS, SQL Injection, SSL/TLS, En-têtes de sécurité et plus")
        print(f"{Fore.BLUE}{'='*80}\n")
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        print(f"\n{Fore.YELLOW}🛑 Signal d'arrêt reçu ({signum})...")
        self.running = False
        sys.exit(0)
    
    def initialize_scanner(self) -> bool:
        """Initialiser le scanner"""
        try:
            print(f"{Fore.CYAN}⚙️ Initialisation du scanner...")
            
            self.scanner = WebVulnScanner()
            print(f"{Fore.GREEN}✅ Scanner initialisé avec succès")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'initialisation: {e}")
            return False
    
    def scan_single_url(self, args) -> bool:
        """Scanner une URL unique"""
        try:
            print(f"\n{Fore.CYAN}🔍 SCAN D'URL UNIQUE")
            print("=" * 50)
            
            url = args.url
            print(f"{Fore.CYAN}🎯 Scan de: {url}")
            
            # Effectuer le scan
            resultat = self.scanner.scanner_url(url)
            
            if resultat:
                print(f"{Fore.GREEN}✓ Scan terminé avec succès")
                print(f"{Fore.CYAN}📊 Vulnerabilités détectées: {len(resultat.vulnerabilites)}")
                print(f"{Fore.CYAN}⏱️ Durée: {resultat.duree_scan:.2f}s")
                print(f"{Fore.CYAN}🏆 Score sécurité: {resultat.score_securite}/100")
                
                # Générer le rapport HTML si demandé
                if not args.no_report:
                    rapport_path = self.scanner.generer_rapport_html(resultat)
                    print(f"{Fore.GREEN}✓ Rapport généré: {rapport_path}")
                
                # Afficher le résumé des vulnérabilités
                if resultat.vulnerabilites:
                    print(f"\n{Fore.YELLOW}🚨 Vulnérabilités détectées:")
                    for vuln in resultat.vulnerabilites:
                        severity_color = {
                            'LOW': Fore.YELLOW,
                            'MEDIUM': Fore.YELLOW,
                            'HIGH': Fore.RED,
                            'CRITICAL': Fore.RED
                        }.get(vuln.severite, Fore.WHITE)
                        print(f"  {severity_color}• [{vuln.severite}] {vuln.type_vuln}: {vuln.description}")
                else:
                    print(f"\n{Fore.GREEN}🛡️ Aucune vulnérabilité détectée")
                
                return True
            else:
                print(f"{Fore.RED}❌ Échec du scan")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du scan: {e}")
            return False
    
    def scan_multiple_urls(self, args) -> bool:
        """Scanner plusieurs URLs depuis un fichier"""
        try:
            print(f"\n{Fore.CYAN}🔍 SCAN MULTIPLE D'URLS")
            print("=" * 50)
            
            file_path = args.file
            if not os.path.exists(file_path):
                print(f"{Fore.RED}❌ Fichier non trouvé: {file_path}")
                return False
            
            # Lire les URLs depuis le fichier
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                print(f"{Fore.RED}❌ Aucune URL trouvée dans le fichier")
                return False
            
            print(f"{Fore.CYAN}📁 {len(urls)} URL(s) trouvée(s) dans le fichier")
            
            # Scanner chaque URL
            resultats = []
            for i, url in enumerate(urls, 1):
                print(f"\n{Fore.CYAN}🎯 [{i}/{len(urls)}] Scan de: {url}")
                
                try:
                    resultat = self.scanner.scanner_url(url)
                    if resultat:
                        resultats.append(resultat)
                        print(f"  {Fore.GREEN}✓ Scan réussi - {len(resultat.vulnerabilites)} vulnérabilité(s)")
                        
                        # Générer le rapport pour cette URL
                        if not args.no_report:
                            self.scanner.generer_rapport_html(resultat)
                    else:
                        print(f"  {Fore.RED}✗ Scan échoué")
                except Exception as e:
                    print(f"  {Fore.RED}✗ Erreur: {e}")
            
            # Résumé final
            print(f"\n{Fore.CYAN}📊 RÉSUMÉ DU SCAN MULTIPLE:")
            print(f"  URLs scannées avec succès: {len(resultats)}/{len(urls)}")
            
            total_vuln = sum(len(r.vulnerabilites) for r in resultats)
            print(f"  Total vulnérabilités détectées: {total_vuln}")
            
            if resultats:
                score_moyen = sum(r.score_securite for r in resultats) / len(resultats)
                print(f"  Score de sécurité moyen: {score_moyen:.1f}/100")
            
            return len(resultats) > 0
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du scan multiple: {e}")
            return False
    
    def show_statistics(self) -> bool:
        """Afficher les statistiques des scans précédents"""
        try:
            print(f"\n{Fore.CYAN}📊 STATISTIQUES DES SCANS")
            print("=" * 50)
            
            stats = self.scanner.obtenir_statistiques()
            
            if not stats:
                print(f"{Fore.YELLOW}⚠️ Aucune donnée statistique disponible")
                return False
            
            print(f"{Fore.CYAN}📈 Statistiques générales:")
            print(f"  Total scans effectués: {stats.get('total_scans', 0)}")
            print(f"  Total vulnérabilités: {stats.get('total_vulnerabilites', 0)}")
            print(f"  Score sécurité moyen: {stats.get('score_moyen', 0):.1f}/100")
            
            # Répartition par type de vulnérabilité
            if 'types_vulnerabilites' in stats:
                print(f"\n{Fore.CYAN}🔍 Répartition par type:")
                for type_vuln, count in stats['types_vulnerabilites'].items():
                    print(f"  {type_vuln}: {count}")
            
            # Répartition par sévérité
            if 'severites' in stats:
                print(f"\n{Fore.CYAN}⚠️ Répartition par sévérité:")
                for severite, count in stats['severites'].items():
                    color = {
                        'LOW': Fore.YELLOW,
                        'MEDIUM': Fore.YELLOW,
                        'HIGH': Fore.RED,
                        'CRITICAL': Fore.RED
                    }.get(severite, Fore.WHITE)
                    print(f"  {color}{severite}: {count}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'affichage des statistiques: {e}")
            return False
    
    def show_system_status(self):
        """Afficher le statut complet du système"""
        print(f"\n{Fore.CYAN}📊 STATUT DU SCANNER DE VULNÉRABILITÉS WEB")
        print("=" * 60)
        
        # Statut du scanner
        print(f"{Fore.YELLOW}🔧 Scanner:")
        scanner_status = "✅ Actif" if self.scanner is not None else "❌ Inactif"
        color = Fore.GREEN if self.scanner is not None else Fore.RED
        print(f"  {color}Scanner principal     : {scanner_status}")
        
        # Informations système
        print(f"\n{Fore.YELLOW}💻 Système:")
        print(f"  {Fore.CYAN}Version              : {self.version}")
        print(f"  {Fore.CYAN}Base de données      : {'✅ Disponible' if os.path.exists('scans_vulnerabilites.db') else '⚠️ Non initialisée'}")
        
        # Vérifier les dépendances
        print(f"\n{Fore.YELLOW}📦 Dépendances:")
        dependencies = ['requests', 'beautifulsoup4', 'colorama', 'tabulate']
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                print(f"  {Fore.GREEN}✅ {dep}")
            except ImportError:
                print(f"  {Fore.RED}❌ {dep}")
        
        # Statistiques si disponibles
        if self.scanner:
            try:
                stats = self.scanner.obtenir_statistiques()
                if stats:
                    print(f"\n{Fore.YELLOW}📊 Statistiques:")
                    print(f"  {Fore.CYAN}Scans effectués      : {stats.get('total_scans', 0)}")
                    print(f"  {Fore.CYAN}Vulnérabilités       : {stats.get('total_vulnerabilites', 0)}")
                    print(f"  {Fore.CYAN}Score moyen          : {stats.get('score_moyen', 0):.1f}/100")
            except:
                print(f"  {Fore.RED}Erreur lors de la récupération des stats")

def create_parser():
    """Créer le parser d'arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="🕷️ Scanner de Vulnérabilités Web - Version Orchestrée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 MODES D'UTILISATION:

Scan d'une URL unique:
  python3 scanner_principal.py single https://example.com
  
Scan multiple depuis un fichier:
  python3 scanner_principal.py multiple --file urls.txt
  
Statistiques des scans:
  python3 scanner_principal.py stats
  
Status du système:
  python3 scanner_principal.py status

🔧 EXEMPLES D'USAGE AVANCÉS:
  
# Scan sans génération de rapport
python3 scanner_principal.py single https://example.com --no-report

# Scan multiple avec workers parallèles
python3 scanner_principal.py multiple --file urls.txt --workers 5

# Afficher les statistiques
python3 scanner_principal.py stats
        """
    )
    
    # Mode principal
    parser.add_argument('mode', choices=['single', 'multiple', 'stats', 'status'],
                       help='Mode de fonctionnement')
    
    # Arguments pour le mode single
    parser.add_argument('url', nargs='?',
                       help='URL à scanner (mode single)')
    
    # Arguments pour le mode multiple
    parser.add_argument('-f', '--file',
                       help='Fichier contenant les URLs à scanner (mode multiple)')
    parser.add_argument('--workers', type=int, default=3,
                       help='Nombre de workers parallèles (défaut: 3)')
    
    # Arguments généraux
    parser.add_argument('--no-report', action='store_true',
                       help='Ne pas générer de rapport HTML')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Timeout pour les requêtes en secondes (défaut: 10)')
    
    return parser

def main():
    """Fonction principale"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Créer l'orchestrateur principal
    orchestrator = ScannerVulnerabilitesWeb()
    
    # Initialiser le scanner
    if not orchestrator.initialize_scanner():
        print(f"{Fore.RED}❌ Échec de l'initialisation du scanner")
        sys.exit(1)
    
    # Traitement selon le mode demandé
    success = True
    
    if args.mode == 'single':
        if not args.url:
            print(f"{Fore.RED}❌ URL requise pour le mode single")
            sys.exit(1)
        success = orchestrator.scan_single_url(args)
        
    elif args.mode == 'multiple':
        if not args.file:
            print(f"{Fore.RED}❌ Fichier requis pour le mode multiple")
            sys.exit(1)
        success = orchestrator.scan_multiple_urls(args)
        
    elif args.mode == 'stats':
        success = orchestrator.show_statistics()
        
    elif args.mode == 'status':
        orchestrator.show_system_status()
    
    # Code de sortie
    exit_code = 0 if success else 1
    if success:
        print(f"\n{Fore.GREEN}🎉 Opération terminée avec succès!")
    else:
        print(f"\n{Fore.RED}❌ Opération échouée")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()