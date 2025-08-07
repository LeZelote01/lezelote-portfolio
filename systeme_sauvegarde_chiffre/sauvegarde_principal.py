#!/usr/bin/env python3
"""
💾 SYSTÈME DE SAUVEGARDE CHIFFRÉ - FICHIER PRINCIPAL UNIFIÉ
===========================================================

Orchestrateur centralisé pour toutes les fonctionnalités du système de sauvegarde chiffré.
Cette version intègre toutes les fonctionnalités dans une architecture modulaire unifiée.

🎯 FONCTIONNALITÉS INTÉGRÉES:
- ✅ Création de sauvegardes chiffrées AES-256
- ✅ Compression intelligente avec exclusions personnalisables
- ✅ Restauration sécurisée avec vérification d'intégrité
- ✅ Planification automatique (horaire, quotidienne, hebdomadaire)
- ✅ Rotation automatique par nombre et ancienneté
- ✅ Gestion des métadonnées avec SQLite
- ✅ Interface CLI complète avec statistiques

🚀 MODES D'UTILISATION:
- CREATE: Créer une nouvelle sauvegarde
- RESTORE: Restaurer une sauvegarde existante  
- LIST: Lister toutes les sauvegardes
- STATS: Statistiques détaillées
- SCHEDULE: Gestion de la planification
- STATUS: Statut du système

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
    from sauvegarde_chiffree import SystemeSauvegardeChiffre
    print("✅ Module sauvegarde principal importé avec succès")
except ImportError as e:
    print(f"{Fore.RED}❌ Erreur d'importation du module principal: {e}")
    print(f"{Fore.YELLOW}💡 Vérifiez que sauvegarde_chiffree.py est présent dans le même dossier")
    sys.exit(1)

class SauvegardeChiffreePrincipale:
    """Orchestrateur principal pour le système de sauvegarde chiffré"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.systeme = None
        self.running = False
        self.scheduler_thread = None
        
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
        print(f"{Fore.BLUE}💾 SYSTÈME DE SAUVEGARDE CHIFFRÉ - VERSION ORCHESTRÉE v{self.version}")
        print(f"{Fore.BLUE}{'='*80}")
        print(f"{Fore.CYAN}🎯 Sauvegarde sécurisée avec chiffrement AES-256")
        print(f"{Fore.CYAN}✨ Compression, planification et rotation automatique")
        print(f"{Fore.BLUE}{'='*80}\n")
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        print(f"\n{Fore.YELLOW}🛑 Signal d'arrêt reçu ({signum})...")
        if self.systeme and self.systeme.scheduler_actif:
            self.systeme.arreter_planification()
        self.running = False
        sys.exit(0)
    
    def initialize_system(self, config_file: str = "config.json") -> bool:
        """Initialiser le système de sauvegarde"""
        try:
            print(f"{Fore.CYAN}⚙️ Initialisation du système de sauvegarde...")
            print(f"{Fore.YELLOW}📝 Fichier de configuration: {config_file}")
            
            self.systeme = SystemeSauvegardeChiffre(config_file)
            print(f"{Fore.GREEN}✅ Système initialisé avec succès")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'initialisation: {e}")
            return False
    
    def create_backup(self, args) -> bool:
        """Créer une nouvelle sauvegarde"""
        try:
            print(f"\n{Fore.CYAN}💾 CRÉATION D'UNE NOUVELLE SAUVEGARDE")
            print("=" * 50)
            
            # Paramètres de la sauvegarde
            source = args.source or input(f"{Fore.CYAN}📁 Dossier source à sauvegarder: ")
            
            # Mot de passe
            if args.password:
                mot_de_passe = args.password
            else:
                import getpass
                mot_de_passe = getpass.getpass(f"{Fore.CYAN}🔐 Mot de passe de chiffrement: ")
            
            print(f"{Fore.CYAN}🚀 Création de la sauvegarde en cours...")
            
            # Créer la sauvegarde
            metadonnees = self.systeme.creer_sauvegarde(
                mot_de_passe=mot_de_passe,
                dossier_source=source
            )
            
            if metadonnees:
                print(f"\n{Fore.GREEN}✅ Sauvegarde créée avec succès!")
                print(f"{Fore.CYAN}📦 ID: {metadonnees.id}")
                print(f"{Fore.CYAN}📁 Fichier: {metadonnees.nom_fichier}")
                print(f"{Fore.CYAN}📊 Taille: {metadonnees.taille_compresse:,} bytes")
                print(f"{Fore.CYAN}🗜️ Ratio compression: {metadonnees.ratio_compression:.1%}")
                print(f"{Fore.CYAN}⏱️ Durée: {metadonnees.duree_creation:.2f}s")
                return True
            else:
                print(f"{Fore.RED}❌ Échec de la création de la sauvegarde")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la création: {e}")
            return False
    
    def restore_backup(self, args) -> bool:
        """Restaurer une sauvegarde"""
        try:
            print(f"\n{Fore.CYAN}🔄 RESTAURATION D'UNE SAUVEGARDE")
            print("=" * 50)
            
            # ID de la sauvegarde
            backup_id = args.backup_id
            if not backup_id:
                self.list_backups(args)
                backup_id = input(f"\n{Fore.CYAN}🆔 ID de la sauvegarde à restaurer: ")
            
            # Destination
            destination = args.destination or input(f"{Fore.CYAN}📁 Dossier de destination: ")
            
            # Mot de passe
            if args.password:
                mot_de_passe = args.password
            else:
                import getpass
                mot_de_passe = getpass.getpass(f"{Fore.CYAN}🔐 Mot de passe de déchiffrement: ")
            
            print(f"{Fore.CYAN}🔄 Restauration en cours...")
            
            # Restaurer la sauvegarde
            succes = self.systeme.restaurer_sauvegarde(
                backup_id,
                mot_de_passe=mot_de_passe,
                dossier_destination=destination
            )
            
            if succes:
                print(f"\n{Fore.GREEN}✅ Sauvegarde restaurée avec succès!")
                print(f"{Fore.CYAN}📁 Destination: {destination}")
                return True
            else:
                print(f"{Fore.RED}❌ Échec de la restauration")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la restauration: {e}")
            return False
    
    def list_backups(self, args) -> bool:
        """Lister les sauvegardes existantes"""
        try:
            print(f"\n{Fore.CYAN}📋 LISTE DES SAUVEGARDES")
            print("=" * 50)
            
            limit = args.limit if hasattr(args, 'limit') else 10
            sauvegardes = self.systeme.lister_sauvegardes(limit)
            
            if not sauvegardes:
                print(f"{Fore.YELLOW}⚠️ Aucune sauvegarde trouvée")
                return True
            
            print(f"{Fore.CYAN}📦 {len(sauvegardes)} sauvegarde(s) trouvée(s):")
            print()
            
            # En-tête du tableau
            print(f"{Fore.YELLOW}{'ID':<20} {'Date':<19} {'Source':<25} {'Taille':<12} {'Compression':<12}")
            print("-" * 90)
            
            # Afficher chaque sauvegarde
            for sauvegarde in sauvegardes:
                taille_mb = sauvegarde.taille_compresse / (1024 * 1024)
                print(f"{sauvegarde.id:<20} "
                      f"{sauvegarde.date_creation.strftime('%Y-%m-%d %H:%M'):<19} "
                      f"{sauvegarde.dossier_source[-25:]:<25} "
                      f"{taille_mb:.1f}MB{'':<6} "
                      f"{sauvegarde.ratio_compression:.1%}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'affichage: {e}")
            return False
    
    def show_statistics(self) -> bool:
        """Afficher les statistiques du système"""
        try:
            print(f"\n{Fore.CYAN}📊 STATISTIQUES DU SYSTÈME")
            print("=" * 50)
            
            stats = self.systeme.obtenir_statistiques()
            
            if not stats:
                print(f"{Fore.YELLOW}⚠️ Aucune statistique disponible")
                return True
            
            print(f"{Fore.CYAN}📈 Statistiques générales:")
            print(f"  Total sauvegardes: {stats.get('total_sauvegardes', 0)}")
            print(f"  Espace total occupé: {stats.get('espace_total_mb', 0):.1f} MB")
            print(f"  Ratio de compression moyen: {stats.get('ratio_compression_moyen', 0):.1%}")
            print(f"  Durée moyenne de création: {stats.get('duree_moyenne', 0):.1f}s")
            
            # Statistiques par période
            if 'derniere_semaine' in stats:
                print(f"\n{Fore.CYAN}📅 Dernière semaine:")
                print(f"  Sauvegardes créées: {stats['derniere_semaine'].get('count', 0)}")
                print(f"  Espace utilisé: {stats['derniere_semaine'].get('taille_mb', 0):.1f} MB")
            
            # Sauvegarde la plus récente
            if 'derniere_sauvegarde' in stats:
                derniere = stats['derniere_sauvegarde']
                print(f"\n{Fore.CYAN}🕒 Dernière sauvegarde:")
                print(f"  ID: {derniere.get('id', 'N/A')}")
                print(f"  Date: {derniere.get('date', 'N/A')}")
                print(f"  Source: {derniere.get('source', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'affichage des statistiques: {e}")
            return False
    
    def manage_schedule(self, args) -> bool:
        """Gérer la planification automatique"""
        try:
            print(f"\n{Fore.CYAN}⏰ GESTION DE LA PLANIFICATION")
            print("=" * 50)
            
            if hasattr(args, 'start') and args.start:
                print(f"{Fore.CYAN}🚀 Démarrage de la planification...")
                self.systeme.demarrer_planification()
                self.running = True
                
                print(f"{Fore.GREEN}✅ Planification active!")
                print(f"{Fore.YELLOW}⏰ Appuyez sur Ctrl+C pour arrêter")
                
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.systeme.arreter_planification()
                    print(f"\n{Fore.YELLOW}👋 Planification arrêtée")
                
            elif hasattr(args, 'stop') and args.stop:
                print(f"{Fore.YELLOW}⏹️ Arrêt de la planification...")
                self.systeme.arreter_planification()
                print(f"{Fore.GREEN}✅ Planification arrêtée")
                
            elif hasattr(args, 'status') and args.status:
                if self.systeme.scheduler_actif:
                    print(f"{Fore.GREEN}✅ Planification active")
                    try:
                        import schedule
                        if schedule.jobs:
                            print(f"⏰ Prochaine exécution: {schedule.next_run()}")
                        else:
                            print(f"📅 Aucune tâche planifiée")
                    except:
                        print(f"📅 Informations de planification non disponibles")
                else:
                    print(f"{Fore.YELLOW}⏹️ Planification inactive")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la gestion de la planification: {e}")
            return False
    
    def show_system_status(self):
        """Afficher le statut complet du système"""
        print(f"\n{Fore.CYAN}📊 STATUT DU SYSTÈME DE SAUVEGARDE CHIFFRÉ")
        print("=" * 60)
        
        # Statut du système
        print(f"{Fore.YELLOW}🔧 Système:")
        system_status = "✅ Actif" if self.systeme is not None else "❌ Inactif"
        color = Fore.GREEN if self.systeme is not None else Fore.RED
        print(f"  {color}Système principal     : {system_status}")
        
        # Statut de la planification
        if self.systeme:
            scheduler_status = "✅ Actif" if self.systeme.scheduler_actif else "⏹️ Inactif"
            scheduler_color = Fore.GREEN if self.systeme.scheduler_actif else Fore.YELLOW
            print(f"  {scheduler_color}Planification         : {scheduler_status}")
        
        # Informations système
        print(f"\n{Fore.YELLOW}💻 Système:")
        print(f"  {Fore.CYAN}Version              : {self.version}")
        print(f"  {Fore.CYAN}Configuration        : {'✅ Disponible' if os.path.exists('config.json') else '⚠️ Non trouvée'}")
        
        # Vérifier les dépendances
        print(f"\n{Fore.YELLOW}📦 Dépendances:")
        dependencies = ['cryptography', 'schedule', 'colorama', 'tabulate']
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                print(f"  {Fore.GREEN}✅ {dep}")
            except ImportError:
                print(f"  {Fore.RED}❌ {dep}")
        
        # Statistiques si disponibles
        if self.systeme:
            try:
                stats = self.systeme.obtenir_statistiques()
                if stats:
                    print(f"\n{Fore.YELLOW}📊 Statistiques:")
                    print(f"  {Fore.CYAN}Sauvegardes          : {stats.get('total_sauvegardes', 0)}")
                    print(f"  {Fore.CYAN}Espace occupé        : {stats.get('espace_total_mb', 0):.1f} MB")
                    print(f"  {Fore.CYAN}Compression moyenne  : {stats.get('ratio_compression_moyen', 0):.1%}")
            except:
                print(f"  {Fore.RED}Erreur lors de la récupération des stats")

def create_parser():
    """Créer le parser d'arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="💾 Système de Sauvegarde Chiffré - Version Orchestrée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 MODES D'UTILISATION:

Créer une sauvegarde:
  python3 sauvegarde_principal.py create --source ./data --password "motdepasse"
  
Restaurer une sauvegarde:
  python3 sauvegarde_principal.py restore --backup-id 20250308_143022 --destination ./restore
  
Lister les sauvegardes:
  python3 sauvegarde_principal.py list --limit 20
  
Statistiques:
  python3 sauvegarde_principal.py stats
  
Planification:
  python3 sauvegarde_principal.py schedule --start
  python3 sauvegarde_principal.py schedule --status
  
Status système:
  python3 sauvegarde_principal.py status

🔧 EXEMPLES D'USAGE AVANCÉS:
  
# Sauvegarde interactive
python3 sauvegarde_principal.py create

# Restauration avec destination personnalisée  
python3 sauvegarde_principal.py restore --backup-id 20250308_143022 --destination /backup/restore

# Planification en arrière-plan
python3 sauvegarde_principal.py schedule --start &
        """
    )
    
    # Mode principal
    parser.add_argument('mode', choices=['create', 'restore', 'list', 'stats', 'schedule', 'status'],
                       help='Mode de fonctionnement')
    
    # Arguments pour create
    parser.add_argument('--source', '-s',
                       help='Dossier source à sauvegarder')
    parser.add_argument('--password', '-p',
                       help='Mot de passe de chiffrement')
    
    # Arguments pour restore
    parser.add_argument('--backup-id',
                       help='ID de la sauvegarde à restaurer')
    parser.add_argument('--destination', '-d',
                       help='Dossier de destination pour la restauration')
    
    # Arguments pour list
    parser.add_argument('--limit', '-l', type=int, default=10,
                       help='Nombre maximum de sauvegardes à afficher (défaut: 10)')
    
    # Arguments pour schedule
    parser.add_argument('--start', action='store_true',
                       help='Démarrer la planification')
    parser.add_argument('--stop', action='store_true',
                       help='Arrêter la planification')
    parser.add_argument('--status-schedule', action='store_true', dest='status',
                       help='Statut de la planification')
    
    # Arguments généraux
    parser.add_argument('--config', '-c', default='config.json',
                       help='Fichier de configuration (défaut: config.json)')
    
    return parser

def main():
    """Fonction principale"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Créer l'orchestrateur principal
    orchestrator = SauvegardeChiffreePrincipale()
    
    # Initialiser le système
    if not orchestrator.initialize_system(args.config):
        print(f"{Fore.RED}❌ Échec de l'initialisation du système")
        sys.exit(1)
    
    # Traitement selon le mode demandé
    success = True
    
    if args.mode == 'create':
        success = orchestrator.create_backup(args)
        
    elif args.mode == 'restore':
        success = orchestrator.restore_backup(args)
        
    elif args.mode == 'list':
        success = orchestrator.list_backups(args)
        
    elif args.mode == 'stats':
        success = orchestrator.show_statistics()
        
    elif args.mode == 'schedule':
        success = orchestrator.manage_schedule(args)
        
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