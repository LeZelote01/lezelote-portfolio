#!/usr/bin/env python3
"""
🎭 DÉMONSTRATIONS - GESTIONNAIRE DE MOTS DE PASSE
===============================================

Ce fichier contient toutes les démonstrations du gestionnaire de mots de passe.
Séparé des scripts principaux pour maintenir un code de production propre.

Fonctionnalités démontrées :
- Authentification biométrique
- Surveillance des violations de données
- Synchronisation cloud
- API REST et mobile
- Audit de sécurité
- Partage sécurisé entre utilisateurs
"""

import sys
import os
import time
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Ajouter le répertoire parent au path pour imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gestionnaire_mdp import GestionnaireMDP
    from biometric_auth import BiometricAuthenticator
    from breach_monitor import BreachMonitor
    from security_audit import SecurityAuditor
    from cloud_sync import CloudSyncManager
    from secure_sharing import SecureSharingManager
    from passphrase_generator import PassphraseGenerator
    print("✅ Modules principaux importés avec succès")
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur d'importation: {e}")
    print(f"{Fore.YELLOW}💡 Exécutez ce script depuis le dossier parent")
    sys.exit(1)

init(autoreset=True)

def demo_biometric_auth():
    """Démonstration de l'authentification biométrique"""
    print(f"\n{Fore.CYAN}🔐 DÉMONSTRATION AUTHENTIFICATION BIOMÉTRIQUE")
    print("=" * 60)
    
    # Initialiser l'authenticateur biométrique
    auth = BiometricAuthenticator()
    
    print(f"\n{Fore.YELLOW}🔍 Détection des méthodes disponibles:")
    methods = auth.get_available_methods()
    for method, available in methods.items():
        status = "✅ Disponible" if available else "❌ Non disponible"
        print(f"   {method}: {status}")
    
    # Test avec méthode simulée
    print(f"\n{Fore.YELLOW}🧪 Test d'authentification simulée:")
    for method in ['touchid', 'windows_hello', 'linux_fprintd']:
        if methods.get(method, False):
            print(f"\n   Méthode testée: {method}")
            
            # Générer un token de démonstration
            master_password = "demo_master_password"
            token = auth.generate_biometric_token(master_password, method, expires_hours=1)
            
            if token:
                print(f"   ✅ Token généré: {token[:20]}...")
                
                # Vérifier le token
                is_valid = auth.verify_biometric_token(token, master_password)
                print(f"   ✅ Vérification token: {'Réussi' if is_valid else 'Échec'}")
                
                # Test avec token expiré (simulation)
                print(f"   📊 Statistiques d'utilisation:")
                stats = auth.get_usage_statistics()
                for key, value in stats.items():
                    print(f"      {key}: {value}")
            else:
                print(f"   ❌ Échec génération token")
            break
    else:
        print(f"   ⚠️ Aucune méthode biométrique disponible en démonstration")
    
    return auth

def demo_breach_monitoring():
    """Démonstration du système de surveillance des violations"""
    print(f"\n{Fore.BLUE}🚨 DÉMONSTRATION - SURVEILLANCE DES VIOLATIONS")
    print("=" * 60)
    
    # Initialiser le gestionnaire principal
    manager = GestionnaireMDP()
    
    # Tenter l'authentification avec mot de passe de démo
    demo_password = "demo123!"
    print(f"{Fore.YELLOW}🔑 Authentification avec mot de passe de démonstration...")
    
    if not manager.authenticate(demo_password):
        print(f"{Fore.CYAN}ℹ️ Création d'un compte de démonstration...")
        manager.create_account(demo_password)
        if not manager.authenticate(demo_password):
            print(f"{Fore.RED}❌ Impossible de s'authentifier avec le compte de démo")
            return None
    
    print(f"{Fore.GREEN}✅ Authentification réussie")
    
    # Initialiser le moniteur de violations
    breach_monitor = BreachMonitor(manager)
    
    # Ajouter quelques mots de passe de démonstration
    demo_passwords = [
        {"site": "demo-site1.com", "username": "user@demo1.com", "password": "password123"},
        {"site": "demo-site2.com", "username": "user@demo2.com", "password": "123456"},
        {"site": "demo-site3.com", "username": "user@demo3.com", "password": "qwerty"},
        {"site": "demo-site4.com", "username": "user@demo4.com", "password": "letmein"}
    ]
    
    print(f"\n{Fore.YELLOW}📝 Ajout de mots de passe de démonstration...")
    for pwd_data in demo_passwords:
        manager.add_password(
            pwd_data["site"], 
            pwd_data["username"], 
            pwd_data["password"],
            "Demo"
        )
        print(f"   ✅ Ajouté: {pwd_data['site']}")
    
    # Vérifier les violations
    print(f"\n{Fore.YELLOW}🔍 Vérification des violations de données...")
    violations_found = breach_monitor.check_all_passwords()
    
    print(f"\n{Fore.CYAN}📊 Résultats de la vérification:")
    print(f"   Violations détectées: {len(violations_found)}")
    
    for violation in violations_found:
        print(f"   🚨 {violation['site']}: {violation['breach_info'].get('Name', 'Violation détectée')}")
    
    # Générer un rapport
    print(f"\n{Fore.YELLOW}📋 Génération du rapport de violations...")
    report = breach_monitor.generate_breach_report()
    
    print(f"\n{Fore.CYAN}📈 Rapport de sécurité:")
    print(f"   Comptes surveillés: {report['total_accounts']}")
    print(f"   Violations trouvées: {report['breached_accounts']}")
    print(f"   Score de sécurité: {report['security_score']}/100")
    print(f"   Dernière vérification: {report['last_check']}")
    
    return breach_monitor

def demo_cloud_sync():
    """Démonstration de la synchronisation cloud"""
    print(f"\n{Fore.BLUE}☁️ DÉMONSTRATION - SYNCHRONISATION CLOUD")
    print("=" * 60)
    
    # Initialiser le gestionnaire principal
    manager = GestionnaireMDP()
    
    # Authentification
    demo_password = "demo123!"
    if not manager.authenticate(demo_password):
        manager.create_account(demo_password)
        manager.authenticate(demo_password)
    
    # Initialiser le gestionnaire de sync cloud
    cloud_sync = CloudSyncManager(manager)
    
    print(f"\n{Fore.YELLOW}⚙️ Configuration des services cloud:")
    
    # Simuler la configuration des services
    services_config = {
        "google_drive": {
            "enabled": True,
            "client_id": "demo-client-id",
            "status": "Configuré (simulation)"
        },
        "dropbox": {
            "enabled": True,
            "app_key": "demo-app-key",
            "status": "Configuré (simulation)"
        }
    }
    
    for service, config in services_config.items():
        status_icon = "✅" if config["enabled"] else "❌"
        print(f"   {status_icon} {service}: {config['status']}")
    
    # Simulation de synchronisation
    print(f"\n{Fore.YELLOW}🔄 Simulation de synchronisation...")
    
    sync_operations = [
        "Chiffrement des données locales",
        "Upload vers Google Drive", 
        "Upload vers Dropbox",
        "Vérification de l'intégrité",
        "Mise à jour des métadonnées"
    ]
    
    for operation in sync_operations:
        print(f"   🔄 {operation}...")
        time.sleep(0.5)  # Simulation du temps de traitement
        print(f"   ✅ {operation} - Terminé")
    
    # Statistiques de synchronisation
    print(f"\n{Fore.CYAN}📊 Statistiques de synchronisation:")
    stats = {
        "Dernière sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Données synchronisées": "2.3 MB",
        "Conflits résolus": 0,
        "Services actifs": "Google Drive, Dropbox"
    }
    
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return cloud_sync

def demo_security_audit():
    """Démonstration de l'audit de sécurité"""
    print(f"\n{Fore.BLUE}🔍 DÉMONSTRATION - AUDIT DE SÉCURITÉ")
    print("=" * 60)
    
    # Initialiser le gestionnaire principal
    manager = GestionnaireMDP()
    
    # Authentification
    demo_password = "demo123!"
    if not manager.authenticate(demo_password):
        manager.create_account(demo_password)
        manager.authenticate(demo_password)
    
    # Initialiser l'auditeur de sécurité
    auditor = SecurityAuditor(manager)
    
    # Ajouter des mots de passe avec différents niveaux de sécurité
    test_passwords = [
        {"site": "bank-demo.com", "username": "user@bank.com", "password": "Tr0ub4dor&3", "category": "Banque"},
        {"site": "social-demo.com", "username": "user@social.com", "password": "password123", "category": "Social"},
        {"site": "work-demo.com", "username": "user@work.com", "password": "P@ssw0rd2024!", "category": "Travail"},
        {"site": "email-demo.com", "username": "user@email.com", "password": "123456", "category": "Email"},
        {"site": "secure-demo.com", "username": "user@secure.com", "password": "Xy9$mK#nB@4vL&8qZ", "category": "Sécurité"}
    ]
    
    print(f"\n{Fore.YELLOW}📝 Ajout de mots de passe de test...")
    for pwd_data in test_passwords:
        manager.add_password(
            pwd_data["site"],
            pwd_data["username"], 
            pwd_data["password"],
            pwd_data["category"]
        )
        print(f"   ✅ {pwd_data['site']}")
    
    # Effectuer l'audit complet
    print(f"\n{Fore.YELLOW}🔍 Audit de sécurité complet...")
    audit_result = auditor.full_security_audit()
    
    # Afficher les résultats
    print(f"\n{Fore.CYAN}📊 RÉSULTATS DE L'AUDIT:")
    print("=" * 40)
    print(f"Score global: {audit_result['overall_score']}/100")
    print(f"Mots de passe analysés: {audit_result['total_passwords']}")
    print(f"Mots de passe compromis: {audit_result['compromised_count']}")
    print(f"Mots de passe faibles: {audit_result['weak_passwords']}")
    print(f"Mots de passe réutilisés: {audit_result['reused_passwords']}")
    
    print(f"\n{Fore.YELLOW}🏷️ ANALYSE PAR CATÉGORIE:")
    for category, data in audit_result['by_category'].items():
        print(f"   {category}: {data['count']} mots de passe, score moyen: {data['avg_score']:.1f}")
    
    print(f"\n{Fore.RED}⚠️ RECOMMANDATIONS:")
    for recommendation in audit_result['recommendations']:
        print(f"   • {recommendation}")
    
    return auditor

def demo_secure_sharing():
    """Démonstration du partage sécurisé"""
    print(f"\n{Fore.BLUE}🤝 DÉMONSTRATION - PARTAGE SÉCURISÉ")
    print("=" * 60)
    
    # Initialiser le gestionnaire principal
    manager = GestionnaireMDP()
    
    # Authentification
    demo_password = "demo123!"
    if not manager.authenticate(demo_password):
        manager.create_account(demo_password)
        manager.authenticate(demo_password)
    
    # Initialiser le gestionnaire de partage
    sharing_manager = SecureSharingManager(manager)
    
    # Ajouter un mot de passe à partager
    print(f"\n{Fore.YELLOW}📝 Création d'un mot de passe à partager...")
    manager.add_password(
        "shared-demo.com",
        "shared-user@demo.com", 
        "SharedP@ssw0rd123!",
        "Partage"
    )
    
    # Simuler le partage avec un utilisateur
    print(f"\n{Fore.YELLOW}👥 Partage avec utilisateur démonstration...")
    
    share_details = {
        "password_id": "shared-demo.com",
        "recipient": "colleague@demo.com",
        "permissions": ["read", "use"],
        "expires": datetime.now() + timedelta(days=7)
    }
    
    print(f"   Destinataire: {share_details['recipient']}")
    print(f"   Permissions: {', '.join(share_details['permissions'])}")
    print(f"   Expire le: {share_details['expires'].strftime('%Y-%m-%d')}")
    
    # Simulation des étapes de partage
    sharing_steps = [
        "Génération de clés de chiffrement asymétrique",
        "Chiffrement du mot de passe avec clé publique",
        "Création du lien de partage sécurisé",
        "Envoi de la notification au destinataire",
        "Configuration des permissions d'accès"
    ]
    
    for step in sharing_steps:
        print(f"   🔄 {step}...")
        time.sleep(0.3)
        print(f"   ✅ {step} - Terminé")
    
    # Afficher les statistiques de partage
    print(f"\n{Fore.CYAN}📊 Statistiques de partage:")
    sharing_stats = {
        "Mots de passe partagés": 1,
        "Utilisateurs autorisés": 1,
        "Liens actifs": 1,
        "Accès cette semaine": 0
    }
    
    for key, value in sharing_stats.items():
        print(f"   {key}: {value}")
    
    return sharing_manager

def demo_passphrase_generation():
    """Démonstration du générateur de phrases de passe"""
    print(f"\n{Fore.BLUE}🎲 DÉMONSTRATION - GÉNÉRATEUR DE PHRASES DE PASSE")
    print("=" * 60)
    
    # Initialiser le générateur
    generator = PassphraseGenerator()
    
    print(f"\n{Fore.YELLOW}🔤 Génération de phrases de passe XKCD:")
    
    # Générer différents types de phrases de passe
    passphrase_configs = [
        {"words": 4, "separator": "-", "numbers": False, "capitalize": False},
        {"words": 5, "separator": " ", "numbers": True, "capitalize": True},
        {"words": 3, "separator": "_", "numbers": True, "capitalize": True},
        {"words": 6, "separator": ".", "numbers": False, "capitalize": False}
    ]
    
    for i, config in enumerate(passphrase_configs, 1):
        print(f"\n   Configuration {i}:")
        print(f"   Mots: {config['words']}, Séparateur: '{config['separator']}'")
        print(f"   Chiffres: {config['numbers']}, Capitalisation: {config['capitalize']}")
        
        passphrase = generator.generate_passphrase(**config)
        entropy = generator.calculate_entropy(passphrase)
        
        print(f"   ✅ Phrase: {passphrase}")
        print(f"   🔒 Entropie: {entropy:.1f} bits")
        print(f"   ⏱️ Temps de crack estimé: {generator.estimate_crack_time(entropy)}")
    
    # Statistiques du générateur
    print(f"\n{Fore.CYAN}📊 Statistiques du générateur:")
    stats = generator.get_generator_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return generator

def demo_complete_workflow():
    """Démonstration du workflow complet"""
    print(f"\n{Fore.BLUE}🎯 DÉMONSTRATION - WORKFLOW COMPLET")
    print("=" * 70)
    
    print(f"{Fore.CYAN}Phase 1: Authentification biométrique...")
    auth = demo_biometric_auth()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 2: Audit de sécurité...")
    auditor = demo_security_audit()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 3: Surveillance des violations...")
    breach_monitor = demo_breach_monitoring()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 4: Synchronisation cloud...")
    cloud_sync = demo_cloud_sync()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 5: Partage sécurisé...")
    sharing = demo_secure_sharing()
    time.sleep(1)
    
    print(f"\n{Fore.CYAN}Phase 6: Génération de phrases de passe...")
    generator = demo_passphrase_generation()
    
    print(f"\n{Fore.GREEN}🎉 DÉMONSTRATION COMPLÈTE TERMINÉE!")
    print("=" * 70)
    print(f"{Fore.YELLOW}📋 Résumé des fonctionnalités testées:")
    print(f"   ✅ Authentification biométrique")
    print(f"   ✅ Audit de sécurité complet") 
    print(f"   ✅ Surveillance des violations")
    print(f"   ✅ Synchronisation cloud chiffrée")
    print(f"   ✅ Partage sécurisé entre utilisateurs")
    print(f"   ✅ Génération de phrases de passe")
    
    return {
        'auth': auth,
        'auditor': auditor,
        'breach_monitor': breach_monitor,
        'cloud_sync': cloud_sync,
        'sharing': sharing,
        'generator': generator
    }

def interactive_demo_menu():
    """Menu interactif pour les démonstrations"""
    while True:
        print(f"\n{Fore.CYAN}🎭 MENU DES DÉMONSTRATIONS - GESTIONNAIRE DE MOTS DE PASSE")
        print("=" * 70)
        print(f"{Fore.YELLOW}1. Authentification biométrique")
        print(f"{Fore.YELLOW}2. Audit de sécurité")
        print(f"{Fore.YELLOW}3. Surveillance des violations")
        print(f"{Fore.YELLOW}4. Synchronisation cloud")
        print(f"{Fore.YELLOW}5. Partage sécurisé")
        print(f"{Fore.YELLOW}6. Génération de phrases de passe")
        print(f"{Fore.YELLOW}7. Workflow complet (toutes les démos)")
        print(f"{Fore.YELLOW}0. Quitter")
        
        try:
            choice = input(f"\n{Fore.WHITE}Votre choix: ").strip()
            
            if choice == "1":
                demo_biometric_auth()
            elif choice == "2":
                demo_security_audit()
            elif choice == "3":
                demo_breach_monitoring()
            elif choice == "4":
                demo_cloud_sync()
            elif choice == "5":
                demo_secure_sharing()
            elif choice == "6":
                demo_passphrase_generation()
            elif choice == "7":
                demo_complete_workflow()
            elif choice == "0":
                print(f"\n{Fore.GREEN}👋 Au revoir!")
                break
            else:
                print(f"\n{Fore.RED}❌ Choix invalide. Veuillez recommencer.")
            
            if choice != "0":
                input(f"\n{Fore.CYAN}📝 Appuyez sur Entrée pour continuer...")
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}🛑 Arrêt demandé par l'utilisateur")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Erreur: {e}")
            input(f"\n{Fore.CYAN}📝 Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    print(f"{Fore.BLUE}🔐 DÉMONSTRATIONS - GESTIONNAIRE DE MOTS DE PASSE")
    print("=" * 70)
    print(f"{Fore.CYAN}📁 Fichier de démonstration séparé des scripts principaux")
    print(f"{Fore.CYAN}🎯 Contient toutes les fonctions de test et de démonstration")
    
    # Lancer le menu interactif par défaut
    interactive_demo_menu()