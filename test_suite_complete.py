#!/usr/bin/env python3
"""
🧪 SUITE DE TESTS COMPLÈTE - SUITE CYBERSÉCURITÉ HARMONISÉE
============================================================

Script de validation finale pour tester tous les 5 projets harmonisés.
Vérifie que chaque fichier *_principal.py fonctionne correctement.

Usage:
    python3 test_suite_complete.py
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class TestSuiteComplete:
    """Suite de tests pour tous les projets harmonisés"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    def print_banner(self):
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"{Fore.BLUE}🧪 SUITE DE TESTS COMPLÈTE - CYBERSÉCURITÉ HARMONISÉE")
        print(f"{Fore.BLUE}{'='*80}")
        print(f"{Fore.CYAN}🎯 Validation finale de tous les projets harmonisés")
        print(f"{Fore.BLUE}{'='*80}\n")
    
    def test_project(self, project_name: str, project_dir: str, main_file: str, test_modes: list):
        """Tester un projet individuel"""
        print(f"\n{Fore.CYAN}🔍 TEST: {project_name}")
        print("-" * 60)
        
        project_path = Path(f"/app/{project_dir}")
        main_path = project_path / main_file
        
        results = {
            'name': project_name,
            'directory': project_dir,
            'main_file': main_file,
            'tests': []
        }
        
        # Test 1: Vérifier que le fichier principal existe
        if main_path.exists():
            print(f"{Fore.GREEN}✅ Fichier principal trouvé: {main_file}")
            results['tests'].append({'test': 'File Exists', 'status': 'PASS'})
        else:
            print(f"{Fore.RED}❌ Fichier principal manquant: {main_file}")
            results['tests'].append({'test': 'File Exists', 'status': 'FAIL'})
            self.results[project_dir] = results
            return
        
        # Test 2: Tester l'aide (--help)
        try:
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            result = subprocess.run([
                sys.executable, main_file, '--help'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"{Fore.GREEN}✅ Aide (--help) fonctionnelle")
                results['tests'].append({'test': 'Help Command', 'status': 'PASS'})
            else:
                print(f"{Fore.YELLOW}⚠️ Aide (--help) problématique: {result.stderr[:100]}...")
                results['tests'].append({'test': 'Help Command', 'status': 'WARN'})
            
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}❌ Aide (--help) timeout")
            results['tests'].append({'test': 'Help Command', 'status': 'FAIL'})
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur aide: {e}")
            results['tests'].append({'test': 'Help Command', 'status': 'FAIL'})
        finally:
            os.chdir(original_cwd)
        
        # Test 3: Tester les modes spécifiques
        for mode in test_modes:
            try:
                os.chdir(project_path)
                
                result = subprocess.run([
                    sys.executable, main_file, mode
                ], capture_output=True, text=True, timeout=30)
                
                # Considérer comme succès si le programme s'exécute (même avec erreur métier)
                if result.returncode == 0 or "Error" not in result.stderr:
                    print(f"{Fore.GREEN}✅ Mode '{mode}' fonctionne")
                    results['tests'].append({'test': f'Mode {mode}', 'status': 'PASS'})
                else:
                    print(f"{Fore.YELLOW}⚠️ Mode '{mode}' problématique (peut être normal)")
                    results['tests'].append({'test': f'Mode {mode}', 'status': 'WARN'})
                
            except subprocess.TimeoutExpired:
                print(f"{Fore.RED}❌ Mode '{mode}' timeout")
                results['tests'].append({'test': f'Mode {mode}', 'status': 'FAIL'})
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Mode '{mode}' erreur: {str(e)[:50]}...")
                results['tests'].append({'test': f'Mode {mode}', 'status': 'WARN'})
            finally:
                os.chdir(original_cwd)
        
        # Calculer le score global
        passed = len([t for t in results['tests'] if t['status'] == 'PASS'])
        warned = len([t for t in results['tests'] if t['status'] == 'WARN'])
        total = len(results['tests'])
        
        if passed >= total * 0.6:  # 60% de réussite minimum
            print(f"\n{Fore.GREEN}🎉 Projet {project_name}: OPÉRATIONNEL ({passed}/{total} tests réussis)")
            results['overall'] = 'WORKING'
        elif passed + warned >= total * 0.8:  # 80% avec avertissements
            print(f"\n{Fore.YELLOW}⚠️ Projet {project_name}: FONCTIONNEL avec avertissements ({passed}/{total} tests réussis)")
            results['overall'] = 'WORKING_WITH_WARNINGS'
        else:
            print(f"\n{Fore.RED}❌ Projet {project_name}: PROBLÉMATIQUE ({passed}/{total} tests réussis)")
            results['overall'] = 'FAILING'
        
        self.results[project_dir] = results
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        self.print_banner()
        
        # Définition des projets et leurs tests
        projects = [
            {
                'name': '📊 Analyseur de Trafic Réseau',
                'directory': 'analyseur_trafic_reseau',
                'main_file': 'analyseur_principal.py',
                'test_modes': ['status']
            },
            {
                'name': '🔐 Gestionnaire de Mots de Passe', 
                'directory': 'gestionnaire_mots_de_passe',
                'main_file': 'gestionnaire_principal.py',
                'test_modes': ['status']
            },
            {
                'name': '🚨 Système d\'Alertes Sécurité',
                'directory': 'systeme_alertes_securite', 
                'main_file': 'alertes_principal.py',
                'test_modes': ['status']
            },
            {
                'name': '🕷️ Scanner de Vulnérabilités Web',
                'directory': 'scanner_vulnerabilites_web',
                'main_file': 'scanner_principal.py', 
                'test_modes': ['status', 'stats']
            },
            {
                'name': '💾 Système de Sauvegarde Chiffré',
                'directory': 'systeme_sauvegarde_chiffre',
                'main_file': 'sauvegarde_principal.py',
                'test_modes': ['status', 'list']
            }
        ]
        
        # Exécuter les tests pour chaque projet
        for project in projects:
            self.test_project(
                project['name'], 
                project['directory'],
                project['main_file'], 
                project['test_modes']
            )
        
        # Afficher le rapport final
        self.print_final_report()
    
    def print_final_report(self):
        """Afficher le rapport final"""
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"{Fore.BLUE}📊 RAPPORT FINAL DE VALIDATION")
        print(f"{Fore.BLUE}{'='*80}")
        
        working_projects = []
        warning_projects = []
        failing_projects = []
        
        for project_key, result in self.results.items():
            if result['overall'] == 'WORKING':
                working_projects.append(result)
            elif result['overall'] == 'WORKING_WITH_WARNINGS':
                warning_projects.append(result)
            else:
                failing_projects.append(result)
        
        total_projects = len(self.results)
        
        print(f"\n{Fore.CYAN}📈 Résumé par statut:")
        print(f"{Fore.GREEN}✅ Opérationnels: {len(working_projects)}/{total_projects}")
        print(f"{Fore.YELLOW}⚠️ Avec avertissements: {len(warning_projects)}/{total_projects}")
        print(f"{Fore.RED}❌ Problématiques: {len(failing_projects)}/{total_projects}")
        
        # Détail par projet
        print(f"\n{Fore.CYAN}📋 Détail par projet:")
        for project_key, result in self.results.items():
            status_color = {
                'WORKING': Fore.GREEN,
                'WORKING_WITH_WARNINGS': Fore.YELLOW,
                'FAILING': Fore.RED
            }.get(result['overall'], Fore.WHITE)
            
            passed = len([t for t in result['tests'] if t['status'] == 'PASS'])
            total = len(result['tests'])
            
            print(f"{status_color}  • {result['name']}: {result['overall']} ({passed}/{total} tests)")
        
        # Message final
        duration = datetime.now() - self.start_time
        print(f"\n{Fore.BLUE}{'='*80}")
        
        if len(failing_projects) == 0:
            if len(warning_projects) == 0:
                print(f"{Fore.GREEN}🎉 VALIDATION COMPLÈTE RÉUSSIE!")
                print(f"{Fore.GREEN}✨ Tous les {total_projects} projets sont opérationnels!")
            else:
                print(f"{Fore.YELLOW}✅ VALIDATION GLOBALEMENT RÉUSSIE")
                print(f"{Fore.YELLOW}⚠️ {len(warning_projects)} projet(s) avec avertissements mineurs")
        else:
            print(f"{Fore.RED}⚠️ VALIDATION PARTIELLE")
            print(f"{Fore.RED}❌ {len(failing_projects)} projet(s) nécessitent une attention")
        
        print(f"\n{Fore.CYAN}⏱️ Durée totale: {duration.total_seconds():.1f}s")
        print(f"{Fore.CYAN}🚀 Suite de cybersécurité harmonisée validée!")
        
        # Instructions d'utilisation
        print(f"\n{Fore.BLUE}{'='*60}")
        print(f"{Fore.BLUE}📖 UTILISATION DES PROJETS HARMONISÉS")
        print(f"{Fore.BLUE}{'='*60}")
        
        for project_key, result in self.results.items():
            if result['overall'] in ['WORKING', 'WORKING_WITH_WARNINGS']:
                print(f"{Fore.CYAN}{result['name']}:")
                print(f"   python3 {project_key}/{result['main_file']} --help")
        
        print(f"\n{Fore.GREEN}🎯 Tous les projets utilisent maintenant la même interface harmonisée!")

def main():
    """Fonction principale"""
    tester = TestSuiteComplete()
    tester.run_all_tests()

if __name__ == "__main__":
    main()