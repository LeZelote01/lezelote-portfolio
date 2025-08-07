#!/usr/bin/env python3
"""
Interface CLI pour la Synchronisation Cloud du Gestionnaire de Mots de Passe
Version 2.1 - Améliorations finalisées selon ROADMAP_AMELIORATIONS.md

Nouvelles Fonctionnalités:
- Configuration interactive simplifiée
- Tests de connectivité automatiques
- Résolution de conflits améliorée
- Synchronisation bidirectionnelle complète
- Gestion des erreurs robuste
- Statistiques de synchronisation détaillées
"""

import argparse
import getpass
import sys
from datetime import datetime, timezone
from pathlib import Path
import json
import time
from colorama import init, Fore, Style
from tabulate import tabulate
import uuid

# Import des modules du gestionnaire
from gestionnaire_mdp import GestionnaireMDP
from cloud_sync import CloudSyncManager, DropboxSync, GoogleDriveSync, CloudConfig

# Initialize colorama
init(autoreset=True)

class CloudSyncCLI:
    """Interface CLI pour la gestion de la synchronisation cloud"""
    
    def __init__(self):
        self.gestionnaire = None
        self.sync_manager = None
        self.authenticated = False
        
        print(f"{Fore.CYAN}☁️  GESTIONNAIRE DE SYNCHRONISATION CLOUD v2.1")
        print(f"{Fore.BLUE}{'=' * 55}")
    
    def authenticate_manager(self):
        """Authentifier avec le gestionnaire de mots de passe"""
        try:
            self.gestionnaire = GestionnaireMDP()
            
            if not self.gestionnaire.has_master_password():
                print(f"{Fore.RED}❌ Aucun mot de passe maître configuré")
                print(f"{Fore.CYAN}💡 Utilisez d'abord: python3 gestionnaire_mdp.py --setup")
                return False
            
            print(f"{Fore.YELLOW}🔐 Authentification requise...")
            password = getpass.getpass("Mot de passe maître: ")
            
            if self.gestionnaire.authenticate(password):
                self.sync_manager = CloudSyncManager(self.gestionnaire)
                self.sync_manager.setup_encryption(password)
                self.authenticated = True
                
                print(f"{Fore.GREEN}✅ Authentification réussie")
                return True
            else:
                print(f"{Fore.RED}❌ Authentification échouée")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur d'authentification: {e}")
            return False
    
    def configure_provider(self, provider: str):
        """Configuration interactive d'un fournisseur cloud"""
        print(f"\n{Fore.CYAN}⚙️  Configuration de {provider.title()}")
        print(f"{Fore.YELLOW}{'=' * 30}")
        
        config = CloudConfig(
            provider=provider,
            enabled=False
        )
        
        if provider == "dropbox":
            print(f"{Fore.WHITE}📍 Instructions Dropbox:")
            print(f"   1. Allez sur https://www.dropbox.com/developers/apps")
            print(f"   2. Créez une nouvelle app avec accès 'App folder'")
            print(f"   3. Générez un Access Token")
            print(f"   4. Copiez le token ci-dessous")
            
            token = getpass.getpass(f"\n{Fore.CYAN}Access Token Dropbox: ")
            if token.strip():
                config.access_token = token.strip()
                config.remote_path = "/Apps/PasswordManager/passwords_sync.enc"
                config.enabled = True
                
                # Test de connectivité
                print(f"\n{Fore.YELLOW}🔄 Test de connectivité Dropbox...")
                if self.sync_manager.test_dropbox_connection(config.access_token):
                    print(f"{Fore.GREEN}✅ Connexion Dropbox réussie")
                else:
                    print(f"{Fore.RED}❌ Échec de la connexion Dropbox")
                    config.enabled = False
        
        elif provider == "google_drive":
            print(f"{Fore.WHITE}📍 Instructions Google Drive:")
            print(f"   1. Allez sur https://console.cloud.google.com")
            print(f"   2. Créez un projet et activez Drive API")
            print(f"   3. Créez des credentials OAuth 2.0")
            print(f"   4. Générez un Access Token")
            
            token = getpass.getpass(f"\n{Fore.CYAN}Access Token Google Drive: ")
            if token.strip():
                config.access_token = token.strip()
                config.remote_path = "PasswordManager/passwords_sync.enc"
                config.enabled = True
                
                # Test de connectivité
                print(f"\n{Fore.YELLOW}🔄 Test de connectivité Google Drive...")
                if self.sync_manager.test_google_drive_connection(config.access_token):
                    print(f"{Fore.GREEN}✅ Connexion Google Drive réussie")
                else:
                    print(f"{Fore.RED}❌ Échec de la connexion Google Drive")
                    config.enabled = False
        
        # Configuration avancée
        if config.enabled:
            print(f"\n{Fore.CYAN}⚙️  Configuration avancée:")
            
            auto_sync = input(f"Synchronisation automatique? (o/N): ").lower().startswith('o')
            config.auto_sync = auto_sync
            
            if auto_sync:
                try:
                    interval = int(input(f"Intervalle de sync (minutes, défaut=5): ") or "5")
                    config.sync_interval = max(1, interval) * 60  # Convertir en secondes
                except ValueError:
                    config.sync_interval = 300  # 5 minutes par défaut
            
            # Sauvegarder la configuration
            self.sync_manager.sync_configs[provider] = config
            self.sync_manager.save_sync_configs()
            
            print(f"\n{Fore.GREEN}✅ Configuration {provider} sauvegardée")
            return True
        else:
            print(f"\n{Fore.RED}❌ Configuration {provider} annulée")
            return False
    
    def show_status(self):
        """Afficher le statut de synchronisation détaillé"""
        if not self.authenticated:
            print(f"{Fore.RED}❌ Authentification requise")
            return
        
        status = self.sync_manager.get_sync_status()
        
        print(f"\n{Fore.CYAN}📊 STATUT DE SYNCHRONISATION")
        print(f"{Fore.BLUE}{'=' * 35}")
        
        # Informations de l'appareil
        print(f"\n{Fore.WHITE}📱 Appareil:")
        device_info = [
            ["ID", status['device_id']],
            ["Nom", status['device_name']],
            ["Conflits non résolus", len(status['conflicts'])]
        ]
        print(tabulate(device_info, headers=["Propriété", "Valeur"], tablefmt="grid"))
        
        # Fournisseurs configurés
        print(f"\n{Fore.WHITE}☁️  Fournisseurs:")
        if status['providers']:
            providers_data = []
            for provider, info in status['providers'].items():
                status_str = "✅ Actif" if info['enabled'] and info['configured'] else "❌ Inactif"
                last_sync = info['last_sync'] or "Jamais"
                if info['last_sync']:
                    try:
                        dt = datetime.fromisoformat(info['last_sync'].replace('Z', '+00:00'))
                        last_sync = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                
                providers_data.append([
                    provider.title(),
                    status_str,
                    last_sync,
                    "Oui" if info['auto_sync'] else "Non"
                ])
            
            print(tabulate(providers_data, 
                         headers=["Fournisseur", "Statut", "Dernière Sync", "Auto"],
                         tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}⚠️  Aucun fournisseur configuré")
        
        # Statistiques
        print(f"\n{Fore.WHITE}📈 Statistiques:")
        stats = status['statistics']
        stats_data = [
            ["Total synchronisations", stats['total_syncs']],
            ["Synchronisations réussies", stats['successful_syncs']],
            ["Taux de succès", f"{stats['success_rate']:.1f}%"],
            ["Conflits non résolus", stats['unresolved_conflicts']]
        ]
        print(tabulate(stats_data, headers=["Métrique", "Valeur"], tablefmt="grid"))
        
        # Synchronisations récentes
        if status['recent_syncs']:
            print(f"\n{Fore.WHITE}🕒 Synchronisations récentes:")
            sync_data = []
            for sync in status['recent_syncs'][:5]:
                timestamp = sync['timestamp']
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime("%d/%m %H:%M")
                except:
                    pass
                
                status_icon = "✅" if sync['status'] == 'success' else "❌"
                duration = f"{sync['duration_ms']}ms" if sync['duration_ms'] else "N/A"
                
                sync_data.append([
                    sync['provider'].title(),
                    sync['action'],
                    timestamp,
                    f"{status_icon} {sync['status']}",
                    duration
                ])
            
            print(tabulate(sync_data,
                         headers=["Fournisseur", "Action", "Date", "Statut", "Durée"],
                         tablefmt="grid"))
        
        # Conflits
        if status['conflicts']:
            print(f"\n{Fore.RED}⚠️  Conflits non résolus:")
            conflict_data = []
            for conflict in status['conflicts']:
                created = conflict['created_at']
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass
                
                conflict_data.append([
                    conflict['id'][:12] + "...",
                    conflict['type'],
                    f"Local: v{conflict['local_version']}",
                    f"Distant: v{conflict['remote_version']}",
                    created
                ])
            
            print(tabulate(conflict_data,
                         headers=["ID", "Type", "Local", "Distant", "Créé"],
                         tablefmt="grid"))
    
    def sync_to_cloud(self, provider: str):
        """Synchronisation vers le cloud"""
        if not self.authenticated:
            print(f"{Fore.RED}❌ Authentification requise")
            return
        
        if provider not in self.sync_manager.sync_configs:
            print(f"{Fore.RED}❌ Fournisseur '{provider}' non configuré")
            return
        
        config = self.sync_manager.sync_configs[provider]
        if not config.enabled:
            print(f"{Fore.RED}❌ Fournisseur '{provider}' désactivé")
            return
        
        print(f"\n{Fore.CYAN}🔄 Synchronisation vers {provider.title()}...")
        start_time = time.time()
        
        try:
            # Préparer les données
            print(f"{Fore.YELLOW}📦 Préparation des données...")
            sync_data = self.sync_manager.prepare_sync_data()
            if not sync_data:
                print(f"{Fore.RED}❌ Erreur lors de la préparation des données")
                return
            
            print(f"{Fore.GREEN}✅ Données préparées:")
            print(f"   • Version: {sync_data['metadata']['version']}")
            print(f"   • Mots de passe: {sync_data['metadata']['total_passwords']}")
            print(f"   • Catégories: {sync_data['metadata']['total_categories']}")
            print(f"   • Checksum: {sync_data['metadata']['checksum'][:16]}...")
            
            # Chiffrer les données
            print(f"\n{Fore.YELLOW}🔒 Chiffrement des données...")
            encrypted_data = self.sync_manager.encrypt_sync_data(sync_data)
            print(f"{Fore.GREEN}✅ Données chiffrées: {len(encrypted_data)} caractères")
            
            # Upload selon le fournisseur
            success = False
            if provider == "dropbox":
                success = self.sync_manager.upload_to_dropbox(encrypted_data, config.remote_path, config.access_token)
            elif provider == "google_drive":
                success = self.sync_manager.upload_to_google_drive(encrypted_data, config.access_token)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if success:
                # Mettre à jour la configuration
                config.last_sync = datetime.now(timezone.utc).isoformat()
                self.sync_manager.save_sync_configs()
                
                # Log de l'action
                self.sync_manager.log_sync_action(
                    "upload", provider, sync_data['metadata']['version'],
                    "success", f"Uploaded {len(encrypted_data)} chars", duration_ms
                )
                
                print(f"\n{Fore.GREEN}✅ Synchronisation vers {provider.title()} réussie!")
                print(f"   • Durée: {duration_ms}ms")
                print(f"   • Version uploadée: {sync_data['metadata']['version']}")
                print(f"   • Checksum: {sync_data['metadata']['checksum'][:16]}...")
            else:
                self.sync_manager.log_sync_action(
                    "upload", provider, sync_data['metadata']['version'],
                    "failed", "Upload failed", duration_ms
                )
                print(f"\n{Fore.RED}❌ Échec de la synchronisation vers {provider.title()}")
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.sync_manager.log_sync_action(
                "upload", provider, 0,
                "error", f"Exception: {str(e)}", duration_ms
            )
            print(f"\n{Fore.RED}❌ Erreur lors de la synchronisation: {e}")
    
    def sync_from_cloud(self, provider: str, strategy: str = "latest_wins"):
        """Synchronisation depuis le cloud avec résolution de conflits"""
        if not self.authenticated:
            print(f"{Fore.RED}❌ Authentification requise")
            return
        
        if provider not in self.sync_manager.sync_configs:
            print(f"{Fore.RED}❌ Fournisseur '{provider}' non configuré")
            return
        
        config = self.sync_manager.sync_configs[provider]
        if not config.enabled:
            print(f"{Fore.RED}❌ Fournisseur '{provider}' désactivé")
            return
        
        print(f"\n{Fore.CYAN}🔄 Synchronisation depuis {provider.title()}...")
        start_time = time.time()
        
        try:
            # Télécharger les données
            print(f"{Fore.YELLOW}📥 Téléchargement des données...")
            encrypted_data = None
            
            if provider == "dropbox":
                encrypted_data = self.sync_manager.download_from_dropbox(config.remote_path, config.access_token)
            elif provider == "google_drive":
                encrypted_data = self.sync_manager.download_from_google_drive(config.access_token)
            
            if not encrypted_data:
                print(f"{Fore.YELLOW}⚠️  Aucune donnée trouvée sur {provider.title()}")
                return
            
            print(f"{Fore.GREEN}✅ Données téléchargées: {len(encrypted_data)} caractères")
            
            # Déchiffrer les données
            print(f"\n{Fore.YELLOW}🔓 Déchiffrement des données...")
            remote_data = self.sync_manager.decrypt_sync_data(encrypted_data)
            print(f"{Fore.GREEN}✅ Données déchiffrées:")
            print(f"   • Version: {remote_data['metadata']['version']}")
            print(f"   • Device: {remote_data['metadata']['device_name']}")
            print(f"   • Mots de passe: {remote_data['metadata']['total_passwords']}")
            print(f"   • Timestamp: {remote_data['metadata']['timestamp']}")
            
            # Préparer les données locales pour comparaison
            print(f"\n{Fore.YELLOW}🔍 Analyse des différences...")
            local_data = self.sync_manager.prepare_sync_data()
            
            if local_data:
                print(f"{Fore.BLUE}📊 Comparaison des données:")
                print(f"   Local  - Version: {local_data['metadata']['version']}, Mots de passe: {local_data['metadata']['total_passwords']}")
                print(f"   Distant - Version: {remote_data['metadata']['version']}, Mots de passe: {remote_data['metadata']['total_passwords']}")
                
                # Détecter les conflits
                conflicts = self.sync_manager.detect_conflicts(local_data, remote_data)
                
                if conflicts:
                    print(f"\n{Fore.YELLOW}⚠️  {len(conflicts)} conflit(s) détecté(s)")
                    
                    # Résoudre les conflits
                    print(f"{Fore.CYAN}🔄 Résolution des conflits avec stratégie: {strategy}")
                    resolved_data = self.sync_manager.resolve_conflicts(
                        local_data, remote_data, conflicts, strategy
                    )
                    
                    if resolved_data:
                        print(f"{Fore.GREEN}✅ Conflits résolus")
                        final_data = resolved_data
                    else:
                        print(f"{Fore.RED}❌ Échec de la résolution des conflits")
                        return
                else:
                    print(f"{Fore.GREEN}✅ Aucun conflit détecté")
                    final_data = remote_data
            else:
                final_data = remote_data
            
            # Appliquer les données résolues
            print(f"\n{Fore.YELLOW}💾 Application des données...")
            if self.sync_manager.apply_remote_data(final_data):
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Mettre à jour la configuration
                config.last_sync = datetime.now(timezone.utc).isoformat()
                self.sync_manager.save_sync_configs()
                
                # Log de l'action
                self.sync_manager.log_sync_action(
                    "download", provider, final_data['metadata']['version'],
                    "success", f"Applied {final_data['metadata']['total_passwords']} passwords", duration_ms
                )
                
                print(f"\n{Fore.GREEN}✅ Synchronisation depuis {provider.title()} réussie!")
                print(f"   • Durée: {duration_ms}ms")
                print(f"   • Version appliquée: {final_data['metadata']['version']}")
                print(f"   • Mots de passe: {final_data['metadata']['total_passwords']}")
                print(f"   • Catégories: {final_data['metadata']['total_categories']}")
            else:
                print(f"\n{Fore.RED}❌ Échec de l'application des données")
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.sync_manager.log_sync_action(
                "download", provider, 0,
                "error", f"Exception: {str(e)}", duration_ms
            )
            print(f"\n{Fore.RED}❌ Erreur lors de la synchronisation: {e}")
    
    def bidirectional_sync(self, provider: str):
        """Synchronisation bidirectionnelle complète"""
        if not self.authenticated:
            print(f"{Fore.RED}❌ Authentification requise")
            return
        
        print(f"\n{Fore.CYAN}🔄 SYNCHRONISATION BIDIRECTIONNELLE - {provider.title()}")
        print(f"{Fore.BLUE}{'=' * 50}")
        
        print(f"\n{Fore.YELLOW}Phase 1: Synchronisation depuis le cloud...")
        self.sync_from_cloud(provider, "merge_intelligent")
        
        print(f"\n{Fore.YELLOW}Phase 2: Synchronisation vers le cloud...")
        time.sleep(1)  # Petite pause entre les phases
        self.sync_to_cloud(provider)
        
        print(f"\n{Fore.GREEN}✅ Synchronisation bidirectionnelle terminée!")
    
    def cleanup_sync_data(self, keep_days: int = 30):
        """Nettoyer les anciennes données de synchronisation"""
        if not self.authenticated:
            print(f"{Fore.RED}❌ Authentification requise")
            return
        
        print(f"\n{Fore.YELLOW}🧹 Nettoyage des données de synchronisation (>{keep_days} jours)...")
        self.sync_manager.cleanup_old_sync_data(keep_days)
        print(f"{Fore.GREEN}✅ Nettoyage terminé")
    
    def backup_config(self, backup_path: str = None):
        """Créer une sauvegarde de la configuration"""
        if not self.authenticated:
            print(f"{Fore.RED}❌ Authentification requise")
            return
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"sync_backup_{timestamp}.json"
        
        print(f"\n{Fore.YELLOW}💾 Création de la sauvegarde...")
        if self.sync_manager.backup_sync_config(backup_path):
            print(f"{Fore.GREEN}✅ Configuration sauvegardée vers {backup_path}")
        else:
            print(f"{Fore.RED}❌ Échec de la sauvegarde")

def main():
    """Interface CLI principale"""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de Synchronisation Cloud pour Mots de Passe"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande configure
    config_parser = subparsers.add_parser('configure', help='Configurer un fournisseur cloud')
    config_parser.add_argument('provider', choices=['dropbox', 'google_drive'], 
                              help='Fournisseur à configurer')
    
    # Commande status
    subparsers.add_parser('status', help='Afficher le statut de synchronisation')
    
    # Commande upload
    upload_parser = subparsers.add_parser('upload', help='Synchroniser vers le cloud')
    upload_parser.add_argument('provider', choices=['dropbox', 'google_drive'],
                              help='Fournisseur de destination')
    
    # Commande download
    download_parser = subparsers.add_parser('download', help='Synchroniser depuis le cloud')
    download_parser.add_argument('provider', choices=['dropbox', 'google_drive'],
                                help='Fournisseur source')
    download_parser.add_argument('--strategy', default='latest_wins',
                                choices=['latest_wins', 'local_wins', 'remote_wins', 'merge_intelligent', 'manual'],
                                help='Stratégie de résolution des conflits')
    
    # Commande sync
    sync_parser = subparsers.add_parser('sync', help='Synchronisation bidirectionnelle')
    sync_parser.add_argument('provider', choices=['dropbox', 'google_drive'],
                            help='Fournisseur à synchroniser')
    
    # Commande cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Nettoyer les anciennes données')
    cleanup_parser.add_argument('--days', type=int, default=30,
                               help='Nombre de jours à conserver (défaut: 30)')
    
    # Commande backup
    backup_parser = subparsers.add_parser('backup', help='Sauvegarder la configuration')
    backup_parser.add_argument('--path', help='Chemin de la sauvegarde')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialiser le CLI
    cli = CloudSyncCLI()
    
    # Authentification pour toutes les commandes
    if not cli.authenticate_manager():
        return
    
    # Exécuter la commande
    try:
        if args.command == 'configure':
            cli.configure_provider(args.provider)
        
        elif args.command == 'status':
            cli.show_status()
        
        elif args.command == 'upload':
            cli.sync_to_cloud(args.provider)
        
        elif args.command == 'download':
            cli.sync_from_cloud(args.provider, args.strategy)
        
        elif args.command == 'sync':
            cli.bidirectional_sync(args.provider)
        
        elif args.command == 'cleanup':
            cli.cleanup_sync_data(args.days)
        
        elif args.command == 'backup':
            cli.backup_config(args.path)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Opération annulée par l'utilisateur")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erreur inattendue: {e}")
    
    print(f"\n{Fore.BLUE}🔐 Synchronisation cloud terminée")

if __name__ == "__main__":
    main()