#!/usr/bin/env python3
"""
📦 SCRIPT D'INSTALLATION DES DÉPENDANCES - SUITE CYBERSÉCURITÉ
=============================================================

Script automatisé pour installer toutes les dépendances de tous les projets
de la suite de cybersécurité.

Usage:
    python3 install_all_dependencies.py
"""

import os
import sys
import subprocess
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_banner():
    print(f"\n{Fore.BLUE}{'='*80}")
    print(f"{Fore.BLUE}📦 INSTALLATION DES DÉPENDANCES - SUITE CYBERSÉCURITÉ")
    print(f"{Fore.BLUE}{'='*80}")
    print(f"{Fore.CYAN}🎯 Installation automatisée de tous les requirements.txt")
    print(f"{Fore.BLUE}{'='*80}\n")

def install_requirements(project_name: str, requirements_path: Path) -> bool:
    """Installer les requirements d'un projet"""
    try:
        print(f"{Fore.CYAN}📦 Installation des dépendances pour: {project_name}")
        
        if not requirements_path.exists():
            print(f"{Fore.RED}❌ Fichier requirements.txt non trouvé: {requirements_path}")
            return False
        
        # Commande pip install
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        
        print(f"{Fore.YELLOW}⚙️ Exécution: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ Installation réussie pour {project_name}")
            return True
        else:
            print(f"{Fore.RED}❌ Erreur lors de l'installation pour {project_name}")
            print(f"{Fore.RED}Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur inattendue pour {project_name}: {e}")
        return False

def main():
    print_banner()
    
    # Définir les projets avec leurs requirements.txt
    projets = {
        "Analyseur de Trafic Réseau": Path("analyseur_trafic_reseau/requirements.txt"),
        "Gestionnaire de Mots de Passe": Path("gestionnaire_mots_de_passe/requirements.txt"),
        "Système d'Alertes Sécurité": Path("systeme_alertes_securite/requirements.txt"),
        "Scanner de Vulnérabilités Web": Path("scanner_vulnerabilites_web/requirements.txt"),
        "Système de Sauvegarde Chiffré": Path("systeme_sauvegarde_chiffre/requirements.txt")
    }
    
    success_count = 0
    total_count = len(projets)
    
    print(f"{Fore.CYAN}🎯 Installation des dépendances pour {total_count} projets...\n")
    
    # Installer pip et upgrade si nécessaire
    print(f"{Fore.CYAN}📦 Mise à jour de pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print(f"{Fore.GREEN}✅ Pip mis à jour avec succès")
    except:
        print(f"{Fore.YELLOW}⚠️ Impossible de mettre à jour pip")
    
    print()
    
    # Installer les dépendances pour chaque projet
    for i, (project_name, requirements_path) in enumerate(projets.items(), 1):
        print(f"{Fore.BLUE}[{i}/{total_count}] {project_name}")
        print("-" * 50)
        
        if install_requirements(project_name, requirements_path):
            success_count += 1
        
        print()  # Ligne vide entre les projets
    
    # Résumé final
    print(f"{Fore.BLUE}{'='*60}")
    print(f"{Fore.BLUE}📊 RÉSUMÉ DE L'INSTALLATION")
    print(f"{Fore.BLUE}{'='*60}")
    
    if success_count == total_count:
        print(f"{Fore.GREEN}🎉 Toutes les dépendances installées avec succès!")
        print(f"{Fore.GREEN}✅ {success_count}/{total_count} projets configurés")
    else:
        print(f"{Fore.YELLOW}⚠️ Installation partiellement réussie")
        print(f"{Fore.YELLOW}📊 {success_count}/{total_count} projets configurés")
        
        if success_count < total_count:
            print(f"\n{Fore.RED}❌ {total_count - success_count} projet(s) ont échoué")
            print(f"{Fore.CYAN}💡 Vérifiez les erreurs ci-dessus et relancez si nécessaire")
    
    print(f"\n{Fore.CYAN}🚀 Vous pouvez maintenant tester les projets:")
    print(f"   python3 analyseur_trafic_reseau/analyseur_principal.py --help")
    print(f"   python3 gestionnaire_mots_de_passe/gestionnaire_principal.py --help")
    print(f"   python3 systeme_alertes_securite/alertes_principal.py --help")
    print(f"   python3 scanner_vulnerabilites_web/scanner_principal.py --help")
    print(f"   python3 systeme_sauvegarde_chiffre/sauvegarde_principal.py --help")

if __name__ == "__main__":
    main()