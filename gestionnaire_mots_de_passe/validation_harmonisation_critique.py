#!/usr/bin/env python3
"""
Test d'harmonisation - Fonctionnalités principales
Validation des composants critiques harmonisés
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def test_orchestrator_functionality():
    """Test complet de l'orchestrateur principal"""
    print(f"{Fore.CYAN}🧪 Test de l'orchestrateur principal...")
    
    try:
        sys.path.append("/app/gestionnaire_mots_de_passe")
        from gestionnaire_principal import main
        
        # Test des imports principaux
        from gestionnaire_mdp import GestionnaireMDP
        from api_rest import app
        from security_audit import SecurityAuditor
        
        print(f"{Fore.GREEN}✅ Tous les modules principaux importés avec succès")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur d'import: {e}")
        return False

def test_authentication_and_operations():
    """Test complet des opérations avec authentification"""
    print(f"{Fore.CYAN}🧪 Test des opérations avec authentification...")
    
    try:
        sys.path.append("/app/gestionnaire_mots_de_passe")
        from gestionnaire_mdp import GestionnaireMDP
        
        manager = GestionnaireMDP()
        
        # Test authentification avec mot de passe de test
        if not manager.authenticate("test_password_123!"):
            print(f"{Fore.RED}❌ Échec d'authentification")
            return False
        
        # Test génération de mot de passe
        password = manager.generate_password(16)
        if len(password) != 16:
            print(f"{Fore.RED}❌ Génération de mot de passe incorrecte")
            return False
        
        # Test ajout de mot de passe
        pwd_id = manager.add_password(
            title="Test Harmonisation",
            username="testuser",
            password=password,
            category="Autre"
        )
        
        if not pwd_id:
            print(f"{Fore.RED}❌ Échec d'ajout de mot de passe")
            return False
        
        # Test récupération
        pwd_data = manager.get_password(pwd_id)
        if not pwd_data or pwd_data['title'] != "Test Harmonisation":
            print(f"{Fore.RED}❌ Échec de récupération de mot de passe")
            return False
        
        # Test statistiques
        stats = manager.get_statistics()
        if not stats or 'total_passwords' not in stats:
            print(f"{Fore.RED}❌ Échec de récupération des statistiques")
            return False
        
        # Test suppression
        if not manager.delete_password(pwd_id):
            print(f"{Fore.RED}❌ Échec de suppression de mot de passe")
            return False
        
        print(f"{Fore.GREEN}✅ Toutes les opérations CRUD validées")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors des opérations: {e}")
        return False

def test_security_audit_integration():
    """Test de l'intégration de l'audit de sécurité"""
    print(f"{Fore.CYAN}🧪 Test de l'audit de sécurité intégré...")
    
    try:
        sys.path.append("/app/gestionnaire_mots_de_passe")
        from security_audit import SecurityAuditor
        from gestionnaire_mdp import GestionnaireMDP
        
        manager = GestionnaireMDP()
        if not manager.authenticate("test_password_123!"):
            return False
        
        auditor = SecurityAuditor(manager)
        
        # Test analyse d'un mot de passe
        analysis = auditor.analyze_password(
            "test123", "Test Password", "user", "TestPassword123!"
        )
        
        if not analysis or analysis.strength_score < 0:
            print(f"{Fore.RED}❌ Échec d'analyse de mot de passe")
            return False
        
        # Test calcul d'entropie
        entropy = auditor.calculate_password_entropy("ComplexPassword123!")
        if entropy <= 0:
            print(f"{Fore.RED}❌ Calcul d'entropie invalide")
            return False
        
        print(f"{Fore.GREEN}✅ Audit de sécurité fonctionnel")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur d'audit de sécurité: {e}")
        return False

def test_api_rest_structure():
    """Test de la structure de l'API REST"""
    print(f"{Fore.CYAN}🧪 Test de la structure API REST...")
    
    try:
        sys.path.append("/app/gestionnaire_mots_de_passe")
        from api_rest import app
        
        # Vérifier les routes principales
        routes = [str(route) for route in app.routes]
        
        expected_routes = [
            "/api/auth/login",
            "/api/passwords",
            "/api/categories",
            "/api/stats",
            "/api/health"
        ]
        
        for expected_route in expected_routes:
            if not any(expected_route in route for route in routes):
                print(f"{Fore.RED}❌ Route manquante: {expected_route}")
                return False
        
        print(f"{Fore.GREEN}✅ Structure API REST validée")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur structure API: {e}")
        return False

def test_harmonization_architecture():
    """Test de l'architecture d'harmonisation"""
    print(f"{Fore.CYAN}🧪 Test de l'architecture d'harmonisation...")
    
    # Vérifier la présence des fichiers clés
    key_files = [
        "/app/gestionnaire_mots_de_passe/gestionnaire_principal.py",
        "/app/gestionnaire_mots_de_passe/gestionnaire_mdp.py",
        "/app/gestionnaire_mots_de_passe/api_rest.py",
        "/app/gestionnaire_mots_de_passe/security_audit.py",
        "/app/gestionnaire_mots_de_passe/cloud_sync.py"
    ]
    
    for file_path in key_files:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}❌ Fichier manquant: {file_path}")
            return False
    
    # Vérifier le fichier orchestrateur
    try:
        with open("/app/gestionnaire_mots_de_passe/gestionnaire_principal.py", "r") as f:
            content = f.read()
            
        # Vérifier les modes d'utilisation essentiels
        expected_modes = ["cli", "gui", "api", "status", "all"]
        for mode in expected_modes:
            if mode not in content:
                print(f"{Fore.RED}❌ Mode manquant dans l'orchestrateur: {mode}")
                return False
        
        print(f"{Fore.GREEN}✅ Architecture d'harmonisation validée")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur architecture: {e}")
        return False

def test_cli_integration():
    """Test d'intégration CLI via l'orchestrateur"""
    print(f"{Fore.CYAN}🧪 Test d'intégration CLI...")
    
    try:
        # Test de lancement de l'aide
        result = subprocess.run(
            ["python3", "gestionnaire_principal.py", "--help"],
            cwd="/app/gestionnaire_mots_de_passe",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"{Fore.RED}❌ Échec du lancement CLI")
            return False
        
        # Vérifier la présence des modes dans l'aide
        if "modes disponibles" not in result.stdout.lower():
            print(f"{Fore.RED}❌ Aide CLI incomplète")
            return False
        
        print(f"{Fore.GREEN}✅ Intégration CLI validée")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur intégration CLI: {e}")
        return False

def main():
    """Test principal d'harmonisation"""
    print(f"{Fore.BLUE}╔══════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.BLUE}║         🎯 VALIDATION HARMONISATION - FONCTIONNALITÉS CRITIQUES     ║")
    print(f"{Fore.BLUE}║                    GESTIONNAIRE DE MOTS DE PASSE                     ║")
    print(f"{Fore.BLUE}╚══════════════════════════════════════════════════════════════════════╝")
    
    print(f"\n{Fore.CYAN}📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{Fore.CYAN}🎯 Focus: Composants critiques de l'harmonisation\n")
    
    tests = [
        ("Architecture d'harmonisation", test_harmonization_architecture),
        ("Orchestrateur principal", test_orchestrator_functionality),
        ("Opérations avec authentification", test_authentication_and_operations),
        ("Intégration audit de sécurité", test_security_audit_integration),
        ("Structure API REST", test_api_rest_structure),
        ("Intégration CLI", test_cli_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{Fore.YELLOW}⏳ {test_name}...")
        try:
            success = test_func()
            results.append(success)
            if success:
                print(f"{Fore.GREEN}✅ {test_name} - RÉUSSI\n")
            else:
                print(f"{Fore.RED}❌ {test_name} - ÉCHEC\n")
        except Exception as e:
            print(f"{Fore.RED}❌ {test_name} - ERREUR: {e}\n")
            results.append(False)
    
    # Résultats finaux
    total_tests = len(results)
    passed_tests = sum(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"{Fore.BLUE}{'='*60}")
    print(f"{Fore.CYAN}📊 RÉSULTATS DE VALIDATION:")
    print(f"   • Tests exécutés: {total_tests}")
    print(f"   • Tests réussis: {Fore.GREEN}{passed_tests}")
    print(f"   • Tests échoués: {Fore.RED}{total_tests - passed_tests}")
    print(f"   • Taux de réussite: {Fore.CYAN}{success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n{Fore.GREEN}🎉 HARMONISATION EXCELLENTE!")
        print(f"{Fore.GREEN}✅ Le Projet 2 est parfaitement harmonisé")
        print(f"{Fore.GREEN}🚀 Prêt pour les améliorations avancées (Phase 2)")
        status = "EXCELLENT"
    elif success_rate >= 80:
        print(f"\n{Fore.YELLOW}✅ HARMONISATION RÉUSSIE!")
        print(f"{Fore.YELLOW}📝 Quelques améliorations mineures possibles")
        print(f"{Fore.GREEN}🚀 Prêt pour les améliorations avancées")
        status = "RÉUSSI"
    else:
        print(f"\n{Fore.RED}❌ HARMONISATION INCOMPLÈTE")
        print(f"{Fore.RED}🔧 Corrections nécessaires avant Phase 2")
        status = "ÉCHEC"
    
    # Rapport JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "Gestionnaire de Mots de Passe - Projet 2",
        "phase": "Phase 1 - Harmonisation",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(success_rate, 1),
        "status": status,
        "ready_for_phase_2": success_rate >= 80,
        "recommendations": [
            "Harmonisation des composants critiques validée",
            "Architecture modulaire opérationnelle",
            "Orchestrateur principal fonctionnel",
            "APIs et sécurité intégrées"
        ] if success_rate >= 80 else [
            "Corriger les tests échoués",
            "Vérifier l'intégration des modules",
            "Valider l'architecture d'harmonisation"
        ]
    }
    
    with open("validation_harmonisation_critique.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Fore.CYAN}📄 Rapport détaillé: validation_harmonisation_critique.json")
    print(f"{Fore.BLUE}{'='*60}")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)