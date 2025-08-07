#!/usr/bin/env python3
"""
GESTIONNAIRE PRINCIPAL - PROJET 2
Orchestrateur unifié pour le Gestionnaire de Mots de Passe

Ce fichier sert de point d'entrée principal et unifie tous les modules du projet :
- Interface CLI (gestionnaire_mdp.py)
- Interface GUI Tkinter (gui_tkinter_gestionnaire.py)
- Synchronisation cloud (cloud_sync.py si disponible)
- API REST (server_api.py si disponible)

Usage:
    python3 gestionnaire_principal.py [MODE] [OPTIONS]

Modes disponibles:
    cli      - Interface en ligne de commande (défaut)
    gui      - Interface graphique Tkinter
    api      - Serveur API REST (si disponible)
    status   - Statut du système
    all      - Tous les composants (GUI + API)
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Ajouter le chemin du module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Afficher la bannière du gestionnaire"""
    print(f"{Fore.BLUE}╔══════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.BLUE}║                    🔐 GESTIONNAIRE DE MOTS DE PASSE                  ║")
    print(f"{Fore.BLUE}║                         PROJET CYBERSÉCURITÉ 2                       ║")
    print(f"{Fore.BLUE}╠══════════════════════════════════════════════════════════════════════╣")
    print(f"{Fore.GREEN}║  🎯 Gestion sécurisée des mots de passe avec chiffrement AES-256    ║")
    print(f"{Fore.GREEN}║  🔒 Authentification maître et sessions sécurisées                  ║")
    print(f"{Fore.GREEN}║  🎨 Interface CLI et GUI unifiées                                   ║")
    print(f"{Fore.GREEN}║  📊 Statistiques et export de données                               ║")
    print(f"{Fore.BLUE}╚══════════════════════════════════════════════════════════════════════╝")
    print()

def check_dependencies():
    """Vérifier les dépendances du système"""
    print(f"{Fore.CYAN}🔍 Vérification des dépendances...")
    
    dependencies = {
        'cryptography': 'Chiffrement AES-256',
        'bcrypt': 'Hachage sécurisé',
        'pyperclip': 'Presse-papier',
        'colorama': 'Sortie colorée',
        'tabulate': 'Tableaux formatés',
        'tkinter': 'Interface graphique'
    }
    
    missing = []
    available = []
    
    for dep, description in dependencies.items():
        try:
            if dep == 'tkinter':
                import tkinter
            else:
                __import__(dep)
            available.append((dep, description))
            print(f"{Fore.GREEN}✓ {dep:<15} - {description}")
        except ImportError:
            missing.append((dep, description))
            print(f"{Fore.RED}✗ {dep:<15} - {description}")
    
    print()
    
    if missing:
        print(f"{Fore.YELLOW}⚠️  Dépendances manquantes détectées:")
        for dep, desc in missing:
            print(f"   - {dep}: {desc}")
        print(f"\n{Fore.CYAN}💡 Pour installer les dépendances manquantes:")
        print(f"   pip install -r requirements.txt")
        print()
    
    return len(missing) == 0

def check_modules():
    """Vérifier la disponibilité des modules du projet"""
    print(f"{Fore.CYAN}🧩 Vérification des modules du projet...")
    
    modules = {
        'gestionnaire_mdp': 'Moteur principal et CLI',
        'gui_gestionnaire': 'Interface graphique Tkinter',
        'cloud_sync': 'Synchronisation cloud (optionnel)',
        'server_api': 'API REST (optionnel)',
        'security_audit': 'Audit de sécurité (optionnel)'
    }
    
    available = []
    optional_missing = []
    required_missing = []
    
    required = ['gestionnaire_mdp', 'gui_gestionnaire']
    
    for module, description in modules.items():
        try:
            __import__(module)
            available.append((module, description))
            print(f"{Fore.GREEN}✓ {module:<25} - {description}")
        except ImportError as e:
            if module in required:
                required_missing.append((module, description))
                print(f"{Fore.RED}✗ {module:<25} - {description} (REQUIS)")
            else:
                optional_missing.append((module, description))
                print(f"{Fore.YELLOW}⚠ {module:<25} - {description} (optionnel)")
    
    print()
    
    if required_missing:
        print(f"{Fore.RED}❌ Modules requis manquants:")
        for module, desc in required_missing:
            print(f"   - {module}: {desc}")
        return False
    
    if optional_missing:
        print(f"{Fore.YELLOW}💡 Modules optionnels non disponibles:")
        for module, desc in optional_missing:
            print(f"   - {module}: {desc}")
    
    return True

def get_system_status():
    """Obtenir le statut du système"""
    print(f"{Fore.CYAN}📊 Statut du système...")
    
    status = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd()
    }
    
    # Vérifier la base de données
    db_path = "passwords.db"
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        status['database'] = {
            'exists': True,
            'size': db_size,
            'path': os.path.abspath(db_path)
        }
        print(f"{Fore.GREEN}✓ Base de données: {db_path} ({db_size:,} bytes)")
    else:
        status['database'] = {
            'exists': False,
            'path': os.path.abspath(db_path)
        }
        print(f"{Fore.YELLOW}⚠ Base de données: non initialisée")
    
    # Vérifier les fichiers de configuration
    config_files = ['cloud_sync_config.json', 'biometric_auth.json']
    status['config_files'] = {}
    
    for config_file in config_files:
        if os.path.exists(config_file):
            status['config_files'][config_file] = True
            print(f"{Fore.GREEN}✓ Configuration: {config_file}")
        else:
            status['config_files'][config_file] = False
            print(f"{Fore.YELLOW}⚠ Configuration: {config_file} (optionnel)")
    
    # Vérifier les permissions
    try:
        test_file = 'test_permissions.tmp'
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        status['write_permissions'] = True
        print(f"{Fore.GREEN}✓ Permissions d'écriture: OK")
    except Exception:
        status['write_permissions'] = False
        print(f"{Fore.RED}✗ Permissions d'écriture: ERREUR")
    
    return status

def run_cli_mode(args):
    """Lancer le mode CLI"""
    print(f"{Fore.GREEN}🖥️  Lancement du mode CLI...")
    
    try:
        from gestionnaire_mdp import main
        
        # Préparer les arguments pour le module CLI
        cli_args = []
        if hasattr(args, 'setup') and args.setup:
            cli_args.append('--setup')
        if hasattr(args, 'db') and args.db:
            cli_args.extend(['--db', args.db])
        
        # Ajouter les sous-commandes si présentes
        if hasattr(args, 'command') and args.command:
            cli_args.append(args.command)
            
            # Arguments de la sous-commande
            if args.command == 'add':
                if hasattr(args, 'title') and args.title:
                    cli_args.append(args.title)
                if hasattr(args, 'username') and args.username:
                    cli_args.extend(['--username', args.username])
                if hasattr(args, 'generate') and args.generate:
                    cli_args.append('--generate')
        
        # Sauvegarder les arguments originaux
        original_argv = sys.argv
        
        try:
            # Remplacer sys.argv pour le module CLI
            sys.argv = ['gestionnaire_mdp.py'] + cli_args
            main()
        finally:
            # Restaurer les arguments originaux
            sys.argv = original_argv
            
    except ImportError as e:
        print(f"{Fore.RED}❌ Erreur: Module CLI non disponible - {e}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors du lancement CLI: {e}")
        return False
    
    return True

def run_gui_mode(args):
    """Lancer le mode GUI"""
    print(f"{Fore.GREEN}🎨 Lancement de l'interface graphique...")
    
    try:
        from gui_gestionnaire import main
        main()
    except ImportError as e:
        print(f"{Fore.RED}❌ Erreur: Interface GUI non disponible - {e}")
        print(f"{Fore.YELLOW}💡 Assurez-vous que Tkinter est installé:")
        print(f"   sudo apt-get install python3-tk")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors du lancement GUI: {e}")
        return False
    
    return True

def run_production_mode(args):
    """Production mode only - Use demos/ folder for demonstrations"""
    print(f"{Fore.YELLOW}⚠️  Demo mode has been moved to demos/ folder")
    print(f"{Fore.CYAN}💡 For demonstrations, use the dedicated demos folder")
    return False

def run_api_mode(args):
    """Lancer le mode API REST"""
    print(f"{Fore.GREEN}🚀 Lancement du serveur API REST...")
    
    try:
        from server_api import main
        main()
    except ImportError:
        print(f"{Fore.YELLOW}⚠️  Module API REST non disponible")
        print(f"{Fore.CYAN}💡 Pour activer l'API REST:")
        print(f"   pip install fastapi uvicorn")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors du lancement API: {e}")
        return False
    
    return True

def run_all_mode(args):
    """Lancer tous les composants"""
    print(f"{Fore.GREEN}🚀 Lancement de tous les composants...")
    
    processes = []
    
    try:
        # Lancer l'API en arrière-plan
        try:
            print(f"{Fore.CYAN}📡 Démarrage du serveur API...")
            api_process = subprocess.Popen([
                sys.executable, 
                os.path.join(os.path.dirname(__file__), 'server_api.py')
            ])
            processes.append(('API', api_process))
            print(f"{Fore.GREEN}✓ API démarrée (PID: {api_process.pid})")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ API non disponible: {e}")
        
        # Lancer la GUI en premier plan
        print(f"{Fore.CYAN}🎨 Démarrage de l'interface graphique...")
        gui_success = run_gui_mode(args)
        
        if not gui_success:
            print(f"{Fore.YELLOW}⚠ GUI non disponible, lancement en mode CLI...")
            run_cli_mode(args)
    
    finally:
        # Nettoyer les processus
        for name, process in processes:
            try:
                print(f"{Fore.CYAN}🧹 Arrêt du processus {name}...")
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

def display_help():
    """Afficher l'aide détaillée"""
    help_text = f"""{Fore.BLUE}
🔐 GESTIONNAIRE DE MOTS DE PASSE - AIDE DÉTAILLÉE

{Fore.CYAN}MODES D'UTILISATION:{Style.RESET_ALL}

{Fore.GREEN}1. Interface Graphique (GUI):{Style.RESET_ALL}
   python3 gestionnaire_principal.py gui
   - Interface Tkinter moderne et intuitive
   - Gestion complète des mots de passe
   - Statistiques visuelles

{Fore.GREEN}2. Interface en Ligne de Commande (CLI):{Style.RESET_ALL}
   python3 gestionnaire_principal.py cli
   - Mode par défaut si aucun mode spécifié
   - Toutes les fonctionnalités en ligne de commande
   - Parfait pour les scripts et l'automatisation

{Fore.GREEN}3. Serveur API REST:{Style.RESET_ALL}
   python3 gestionnaire_principal.py api
   - Interface API REST pour intégrations
   - Documentation Swagger automatique
   - Authentification JWT

{Fore.GREEN}5. Tous les composants:{Style.RESET_ALL}
   python3 gestionnaire_principal.py all
   - Lance GUI + API simultanément
   - Mode complet pour développement

{Fore.GREEN}6. Statut du système:{Style.RESET_ALL}
   python3 gestionnaire_principal.py status
   - Vérification des dépendances
   - État de la base de données
   - Diagnostics complets

{Fore.CYAN}EXEMPLES D'UTILISATION:{Style.RESET_ALL}

{Fore.YELLOW}Configuration initiale:{Style.RESET_ALL}
python3 gestionnaire_principal.py cli --setup

{Fore.YELLOW}Ajouter un mot de passe:{Style.RESET_ALL}
python3 gestionnaire_principal.py cli add "Mon Compte" --username "user" --generate

{Fore.YELLOW}Lancer la démonstration complète:{Style.RESET_ALL}
python3 gestionnaire_principal.py demo complete

{Fore.YELLOW}Interface graphique:{Style.RESET_ALL}
python3 gestionnaire_principal.py gui

{Fore.CYAN}FONCTIONNALITÉS PRINCIPALES:{Style.RESET_ALL}
• 🔒 Chiffrement AES-256 avec Fernet
• 🔑 Génération de mots de passe sécurisés
• 📁 Catégorisation flexible des comptes
• 🔍 Recherche et filtrage avancés
• 📊 Statistiques d'utilisation détaillées
• 💾 Export/Import sécurisé des données
• ⏱️ Gestion des sessions avec timeout
• 🌐 Synchronisation cloud (optionnelle)
• 🔐 Authentification biométrique (optionnelle)

{Fore.CYAN}SÉCURITÉ:{Style.RESET_ALL}
• Mot de passe maître avec hachage bcrypt
• Dérivation de clé PBKDF2 (100k itérations)
• Sessions sécurisées avec timeout automatique
• Pas de stockage en clair des données sensibles
• Génération cryptographiquement sécurisée

{Fore.YELLOW}Pour plus d'aide sur un mode spécifique:{Style.RESET_ALL}
python3 gestionnaire_principal.py [MODE] --help
"""
    print(help_text)

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de Mots de Passe - Orchestrateur Principal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes disponibles:
  cli      Interface en ligne de commande (défaut)
  gui      Interface graphique Tkinter
  api      Serveur API REST
  status   Statut et diagnostics du système
  all      Tous les composants (GUI + API)
  help     Aide détaillée

Exemples:
  python3 gestionnaire_principal.py gui
  python3 gestionnaire_principal.py cli --setup
        """
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        choices=['cli', 'gui', 'api', 'status', 'all', 'help'],
        default='cli',
        help='Mode de fonctionnement'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Configurer le mot de passe maître (mode CLI)'
    )
    
    parser.add_argument(
        '--production',
        action='store_true',
        help='Mode production (mode CLI)'
    )
    
    parser.add_argument(
        '--db',
        default="passwords.db",
        help='Chemin vers la base de données'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Désactiver la bannière d\'accueil'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Affichage détaillé'
    )
    
    # Arguments pour le mode CLI (pass-through)
    parser.add_argument(
        'command',
        nargs='?',
        help='Commande CLI (add, list, get, stats, export)'
    )
    
    parser.add_argument('title', nargs='?', help='Titre du compte (pour add)')
    parser.add_argument('--username', help='Nom d\'utilisateur')
    parser.add_argument('--generate', action='store_true', help='Générer un mot de passe')
    
    args = parser.parse_args()
    
    # Afficher la bannière sauf si désactivée
    if not args.no_banner and args.mode != 'help':
        print_banner()
    
    # Mode aide
    if args.mode == 'help':
        display_help()
        return
    
    # Vérifications initiales
    if args.verbose or args.mode == 'status':
        deps_ok = check_dependencies()
        modules_ok = check_modules()
        
        if args.mode == 'status':
            status = get_system_status()
            print(f"\n{Fore.CYAN}📋 Statut global:")
            if deps_ok and modules_ok:
                print(f"{Fore.GREEN}✅ Système opérationnel")
            else:
                print(f"{Fore.YELLOW}⚠️  Système partiellement opérationnel")
            return
        
        if not (deps_ok and modules_ok):
            print(f"\n{Fore.YELLOW}⚠️  Certaines fonctionnalités peuvent ne pas être disponibles.")
            print(f"{Fore.CYAN}💡 Continuez avec le mode {args.mode}...\n")
    
    # Lancer le mode approprié
    try:
        success = False
        
        if args.mode == 'cli':
            success = run_cli_mode(args)
        elif args.mode == 'gui':
            success = run_gui_mode(args)
        elif args.mode == 'production':
            success = run_production_mode(args)
        elif args.mode == 'api':
            success = run_api_mode(args)
        elif args.mode == 'all':
            success = run_all_mode(args)
        
        if success:
            print(f"\n{Fore.GREEN}✅ Opération terminée avec succès")
        else:
            print(f"\n{Fore.YELLOW}⚠️  Opération terminée avec des avertissements")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Opération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erreur inattendue: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()