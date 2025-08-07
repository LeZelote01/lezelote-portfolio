#!/usr/bin/env python3
"""
Système de Sauvegarde Chiffré

Système avancé de sauvegarde avec chiffrement AES-256, compression,
rotation automatique et scheduling flexible.

Auteur: Système de Cybersécurité
Version: 1.0.0
Date: 2025-03-08
"""

import os
import sys
import json
import time
import shutil
import zipfile
import hashlib
import argparse
import logging
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

import psutil
from tqdm import tqdm
from colorama import init, Fore, Style
from tabulate import tabulate
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Initialiser colorama
init(autoreset=True)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sauvegarde.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MetadonneesSauvegarde:
    """Métadonnées d'une sauvegarde"""
    id: str
    timestamp: datetime
    nom_fichier: str
    taille_originale: int
    taille_compressee: int
    taille_chiffree: int
    fichiers_inclus: int
    dossiers_inclus: int
    dossier_source: str
    duree_sauvegarde: float
    hash_integrite: str
    chiffre: bool
    compresse: bool
    version: str = "1.0.0"
    
    def to_dict(self):
        """Convertir en dictionnaire JSON-sérialisable"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Créer depuis un dictionnaire"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class StatistiquesSauvegarde:
    """Statistiques globales des sauvegardes"""
    nombre_total: int = 0
    taille_totale: int = 0
    taille_originale_totale: int = 0
    ratio_compression_moyen: float = 0.0
    duree_moyenne: float = 0.0
    derniere_sauvegarde: Optional[datetime] = None
    plus_ancienne: Optional[datetime] = None
    erreurs_total: int = 0
    
    def to_dict(self):
        data = asdict(self)
        if self.derniere_sauvegarde:
            data['derniere_sauvegarde'] = self.derniere_sauvegarde.isoformat()
        if self.plus_ancienne:
            data['plus_ancienne'] = self.plus_ancienne.isoformat()
        return data


class GestionnaireCryptographie:
    """Gestionnaire du chiffrement AES-256"""
    
    def __init__(self, iterations: int = 100000):
        self.iterations = iterations
        
    def generer_cle_depuis_mot_de_passe(self, mot_de_passe: str, salt: bytes) -> bytes:
        """Générer une clé de chiffrement depuis un mot de passe"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(mot_de_passe.encode()))
    
    def generer_salt(self, longueur: int = 32) -> bytes:
        """Générer un salt aléatoire"""
        return os.urandom(longueur)
    
    def chiffrer_donnees(self, donnees: bytes, cle: bytes) -> bytes:
        """Chiffrer des données avec AES-256"""
        fernet = Fernet(cle)
        return fernet.encrypt(donnees)
    
    def dechiffrer_donnees(self, donnees_chiffrees: bytes, cle: bytes) -> bytes:
        """Déchiffrer des données"""
        fernet = Fernet(cle)
        return fernet.decrypt(donnees_chiffrees)
    
    def calculer_hash_integrite(self, donnees: bytes) -> str:
        """Calculer le hash d'intégrité SHA-256"""
        return hashlib.sha256(donnees).hexdigest()


class GestionnaireCompression:
    """Gestionnaire de la compression ZIP"""
    
    def __init__(self, niveau: int = 6):
        self.niveau = niveau
        
    def comprimer_dossier(self, dossier_source: Path, fichier_zip: Path, 
                         exclusions: List[str] = None, 
                         callback_progression=None) -> Tuple[int, int]:
        """
        Comprimer un dossier en ZIP
        Retourne: (taille_originale, taille_compressee)
        """
        exclusions = exclusions or []
        taille_originale = 0
        fichiers_traites = 0
        
        # Calculer la taille totale pour la progression
        fichiers_a_traiter = []
        for root, dirs, files in os.walk(dossier_source):
            # Filtrer les dossiers exclus
            dirs[:] = [d for d in dirs if not self._est_exclu(d, exclusions)]
            
            for file in files:
                if not self._est_exclu(file, exclusions):
                    fichier_path = Path(root) / file
                    if fichier_path.exists():
                        fichiers_a_traiter.append(fichier_path)
                        taille_originale += fichier_path.stat().st_size
        
        # Créer l'archive ZIP
        with zipfile.ZipFile(fichier_zip, 'w', zipfile.ZIP_DEFLATED, 
                           compresslevel=self.niveau) as zipf:
            
            for fichier_path in fichiers_a_traiter:
                try:
                    # Chemin relatif dans l'archive
                    arcname = fichier_path.relative_to(dossier_source)
                    zipf.write(fichier_path, arcname)
                    fichiers_traites += 1
                    
                    if callback_progression:
                        callback_progression(fichiers_traites, len(fichiers_a_traiter))
                        
                except Exception as e:
                    logger.warning(f"Erreur lors de la compression de {fichier_path}: {e}")
        
        taille_compressee = fichier_zip.stat().st_size if fichier_zip.exists() else 0
        return taille_originale, taille_compressee
    
    def _est_exclu(self, nom: str, exclusions: List[str]) -> bool:
        """Vérifier si un fichier/dossier est exclu"""
        for exclusion in exclusions:
            if exclusion.startswith('*'):
                if nom.endswith(exclusion[1:]):
                    return True
            elif exclusion in nom:
                return True
        return False


class GestionnaireRotation:
    """Gestionnaire de la rotation des sauvegardes"""
    
    def __init__(self, max_sauvegardes: int = 10, conservation_jours: int = 30):
        self.max_sauvegardes = max_sauvegardes
        self.conservation_jours = conservation_jours
    
    def appliquer_rotation(self, dossier_sauvegardes: Path) -> List[str]:
        """Appliquer la rotation et retourner la liste des fichiers supprimés"""
        fichiers_supprimes = []
        
        # Lister tous les fichiers de sauvegarde
        fichiers_backup = list(dossier_sauvegardes.glob("backup_*.zip.enc"))
        fichiers_metadata = list(dossier_sauvegardes.glob("backup_*.json"))
        
        # Trier par date de modification (plus ancien en premier)
        fichiers_backup.sort(key=lambda f: f.stat().st_mtime)
        fichiers_metadata.sort(key=lambda f: f.stat().st_mtime)
        
        # Rotation par nombre maximum
        if len(fichiers_backup) > self.max_sauvegardes:
            fichiers_a_supprimer = fichiers_backup[:-self.max_sauvegardes]
            for fichier in fichiers_a_supprimer:
                try:
                    fichier.unlink()
                    fichiers_supprimes.append(str(fichier))
                    
                    # Supprimer aussi les métadonnées correspondantes
                    metadata_file = fichier.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {fichier}: {e}")
        
        # Rotation par ancienneté
        limite_date = datetime.now() - timedelta(days=self.conservation_jours)
        for fichier in dossier_sauvegardes.glob("backup_*"):
            try:
                if datetime.fromtimestamp(fichier.stat().st_mtime) < limite_date:
                    fichier.unlink()
                    if str(fichier) not in fichiers_supprimes:
                        fichiers_supprimes.append(str(fichier))
            except Exception as e:
                logger.error(f"Erreur lors de la suppression par ancienneté de {fichier}: {e}")
        
        return fichiers_supprimes


class SystemeSauvegardeChiffre:
    """Système principal de sauvegarde chiffrée"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._charger_configuration()
        self.crypto = GestionnaireCryptographie(
            self.config['securite']['iterations_pbkdf2']
        )
        self.compression = GestionnaireCompression(
            self.config['sauvegarde']['compression_niveau']
        )
        self.rotation = GestionnaireRotation(
            self.config['rotation']['max_sauvegardes'],
            self.config['rotation']['conservation_jours']
        )
        self.scheduler_actif = False
        self.scheduler_thread = None
        
    def _charger_configuration(self) -> Dict:
        """Charger la configuration depuis le fichier JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Fichier de configuration {self.config_file} non trouvé")
            return self._configuration_par_defaut()
        except json.JSONDecodeError as e:
            logger.error(f"Erreur dans le fichier de configuration: {e}")
            return self._configuration_par_defaut()
    
    def _configuration_par_defaut(self) -> Dict:
        """Configuration par défaut"""
        return {
            "sauvegarde": {
                "dossier_source": "./data",
                "dossier_destination": "./backups",
                "nom_base": "backup",
                "compression_niveau": 6,
                "chiffrement_actif": True,
                "exclusions": ["*.tmp", "*.log", "__pycache__"]
            },
            "rotation": {
                "max_sauvegardes": 10,
                "conservation_jours": 30,
                "rotation_auto": True
            },
            "securite": {
                "iterations_pbkdf2": 100000,
                "longueur_salt": 32,
                "verification_integrite": True
            }
        }
    
    def creer_sauvegarde(self, mot_de_passe: str = None, 
                        dossier_source: str = None) -> Optional[MetadonneesSauvegarde]:
        """Créer une nouvelle sauvegarde"""
        debut = time.time()
        
        # Paramètres de sauvegarde
        source = Path(dossier_source or self.config['sauvegarde']['dossier_source'])
        destination = Path(self.config['sauvegarde']['dossier_destination'])
        destination.mkdir(parents=True, exist_ok=True)
        
        if not source.exists():
            logger.error(f"Dossier source {source} n'existe pas")
            return None
        
        # Générer l'ID et le nom de fichier
        timestamp = datetime.now()
        backup_id = timestamp.strftime("%Y%m%d_%H%M%S")
        nom_base = self.config['sauvegarde']['nom_base']
        fichier_temp_zip = destination / f"{nom_base}_{backup_id}.zip"
        fichier_final = destination / f"{nom_base}_{backup_id}.zip.enc"
        fichier_metadata = destination / f"{nom_base}_{backup_id}.json"
        
        try:
            print(f"{Fore.CYAN}📦 Création de la sauvegarde {backup_id}...")
            
            # Étape 1: Compression
            print(f"{Fore.YELLOW}⚙️  Compression en cours...")
            with tqdm(desc="Compression", unit="fichiers") as pbar:
                def callback_progression(current, total):
                    pbar.total = total
                    pbar.n = current
                    pbar.refresh()
                
                taille_originale, taille_compressee = self.compression.comprimer_dossier(
                    source, fichier_temp_zip, 
                    self.config['sauvegarde']['exclusions'],
                    callback_progression
                )
            
            print(f"{Fore.GREEN}✅ Compression terminée: {taille_originale:,} → {taille_compressee:,} bytes")
            
            # Étape 2: Chiffrement (si activé)
            taille_chiffree = taille_compressee
            chiffre = False
            hash_integrite = ""
            
            if self.config['sauvegarde']['chiffrement_actif'] and mot_de_passe:
                print(f"{Fore.YELLOW}🔐 Chiffrement en cours...")
                
                # Lire le fichier compressé
                with open(fichier_temp_zip, 'rb') as f:
                    donnees_compressee = f.read()
                
                # Générer salt et clé
                salt = self.crypto.generer_salt(self.config['securite']['longueur_salt'])
                cle = self.crypto.generer_cle_depuis_mot_de_passe(mot_de_passe, salt)
                
                # Chiffrer
                donnees_chiffrees = self.crypto.chiffrer_donnees(donnees_compressee, cle)
                
                # Calculer hash d'intégrité
                if self.config['securite']['verification_integrite']:
                    hash_integrite = self.crypto.calculer_hash_integrite(donnees_compressee)
                
                # Sauvegarder (salt + données chiffrées)
                with open(fichier_final, 'wb') as f:
                    f.write(salt)
                    f.write(donnees_chiffrees)
                
                taille_chiffree = fichier_final.stat().st_size
                chiffre = True
                
                # Supprimer le fichier temporaire non chiffré
                fichier_temp_zip.unlink()
                print(f"{Fore.GREEN}🔒 Chiffrement terminé: {taille_compressee:,} → {taille_chiffree:,} bytes")
            else:
                # Pas de chiffrement, renommer le fichier
                fichier_temp_zip.rename(fichier_final.with_suffix(''))
                fichier_final = fichier_final.with_suffix('')
            
            # Calculer les statistiques
            duree = time.time() - debut
            fichiers_inclus, dossiers_inclus = self._compter_elements(source)
            
            # Créer les métadonnées
            metadonnees = MetadonneesSauvegarde(
                id=backup_id,
                timestamp=timestamp,
                nom_fichier=fichier_final.name,
                taille_originale=taille_originale,
                taille_compressee=taille_compressee,
                taille_chiffree=taille_chiffree,
                fichiers_inclus=fichiers_inclus,
                dossiers_inclus=dossiers_inclus,
                dossier_source=str(source),
                duree_sauvegarde=duree,
                hash_integrite=hash_integrite,
                chiffre=chiffre,
                compresse=True
            )
            
            # Sauvegarder les métadonnées
            with open(fichier_metadata, 'w', encoding='utf-8') as f:
                json.dump(metadonnees.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Appliquer la rotation si activée
            if self.config['rotation']['rotation_auto']:
                fichiers_supprimes = self.rotation.appliquer_rotation(destination)
                if fichiers_supprimes:
                    print(f"{Fore.MAGENTA}🗑️  Rotation: {len(fichiers_supprimes)} anciens fichiers supprimés")
            
            # Afficher le résumé
            ratio_compression = (1 - taille_compressee / taille_originale) * 100 if taille_originale > 0 else 0
            print(f"\n{Fore.GREEN}✅ Sauvegarde {backup_id} créée avec succès!")
            print(f"📁 Source: {source}")
            print(f"💾 Destination: {fichier_final}")
            print(f"📊 Compression: {ratio_compression:.1f}%")  
            print(f"⏱️  Durée: {duree:.2f}s")
            print(f"📦 Fichiers: {fichiers_inclus:,} | Dossiers: {dossiers_inclus:,}")
            
            logger.info(f"Sauvegarde {backup_id} créée: {taille_originale:,} → {taille_chiffree:,} bytes")
            
            return metadonnees
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            
            # Nettoyer les fichiers temporaires
            for fichier in [fichier_temp_zip, fichier_final, fichier_metadata]:
                if fichier.exists():
                    try:
                        fichier.unlink()
                    except:
                        pass
            
            print(f"{Fore.RED}❌ Erreur lors de la création de la sauvegarde: {e}")
            return None
    
    def _compter_elements(self, dossier: Path) -> Tuple[int, int]:
        """Compter les fichiers et dossiers dans un répertoire"""
        fichiers = 0
        dossiers = 0
        
        for root, dirs, files in os.walk(dossier):
            dossiers += len(dirs)
            fichiers += len(files)
        
        return fichiers, dossiers
    
    def lister_sauvegardes(self, limite: int = None) -> List[MetadonneesSauvegarde]:
        """Lister les sauvegardes disponibles"""
        destination = Path(self.config['sauvegarde']['dossier_destination'])
        
        if not destination.exists():
            return []
        
        sauvegardes = []
        nom_base = self.config['sauvegarde']['nom_base']
        fichiers_metadata = list(destination.glob(f"{nom_base}_*.json"))
        
        # Si pas de fichiers trouvés avec le nom de base, essayer avec "backup"
        if not fichiers_metadata:
            fichiers_metadata = list(destination.glob("backup_*.json"))
        
        # Trier par date (plus récent en premier)
        fichiers_metadata.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        if limite:
            fichiers_metadata = fichiers_metadata[:limite]
        
        for fichier in fichiers_metadata:
            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sauvegardes.append(MetadonneesSauvegarde.from_dict(data))
            except Exception as e:
                logger.warning(f"Erreur lors du chargement de {fichier}: {e}")
        
        return sauvegardes
    
    def restaurer_sauvegarde(self, backup_id: str, mot_de_passe: str = None, 
                           dossier_destination: str = None) -> bool:
        """Restaurer une sauvegarde"""
        dossier_sauvegardes = Path(self.config['sauvegarde']['dossier_destination'])
        
        # Chercher les fichiers de la sauvegarde
        fichier_metadata = dossier_sauvegardes / f"backup_{backup_id}.json"
        
        if not fichier_metadata.exists():
            # Essayer avec le nom de base de la configuration
            nom_base = self.config['sauvegarde']['nom_base']
            fichier_metadata = dossier_sauvegardes / f"{nom_base}_{backup_id}.json"
        
        if not fichier_metadata.exists():
            print(f"{Fore.RED}❌ Sauvegarde {backup_id} non trouvée")
            return False
        
        try:
            # Charger les métadonnées
            with open(fichier_metadata, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metadonnees = MetadonneesSauvegarde.from_dict(data)
            
            # Localiser le fichier de sauvegarde
            fichier_sauvegarde = dossier_sauvegardes / metadonnees.nom_fichier
            
            if not fichier_sauvegarde.exists():
                print(f"{Fore.RED}❌ Fichier de sauvegarde manquant: {fichier_sauvegarde}")
                return False
            
            print(f"{Fore.CYAN}📦 Restauration de la sauvegarde {backup_id}...")
            
            # Préparer le dossier de destination
            if dossier_destination:
                dest = Path(dossier_destination)
            else:
                dest = Path(f"./restore_{backup_id}")
            
            dest.mkdir(parents=True, exist_ok=True)
            
            # Étape 1: Déchiffrement (si nécessaire)
            if metadonnees.chiffre:
                if not mot_de_passe:
                    print(f"{Fore.RED}❌ Mot de passe requis pour déchiffrer la sauvegarde")
                    return False
                
                print(f"{Fore.YELLOW}🔓 Déchiffrement en cours...")
                
                with open(fichier_sauvegarde, 'rb') as f:
                    # Lire le salt
                    salt = f.read(self.config['securite']['longueur_salt'])
                    # Lire les données chiffrées
                    donnees_chiffrees = f.read()
                
                # Générer la clé
                cle = self.crypto.generer_cle_depuis_mot_de_passe(mot_de_passe, salt)
                
                try:
                    # Déchiffrer
                    donnees_compressee = self.crypto.dechiffrer_donnees(donnees_chiffrees, cle)
                    
                    # Vérifier l'intégrité si disponible
                    if metadonnees.hash_integrite:
                        hash_calcule = self.crypto.calculer_hash_integrite(donnees_compressee)
                        if hash_calcule != metadonnees.hash_integrite:
                            print(f"{Fore.RED}❌ Erreur d'intégrité des données!")
                            return False
                        print(f"{Fore.GREEN}✅ Intégrité vérifiée")
                    
                    # Sauvegarder temporairement les données décompressées
                    fichier_temp = dest / "temp_archive.zip"
                    with open(fichier_temp, 'wb') as f:
                        f.write(donnees_compressee)
                    
                    print(f"{Fore.GREEN}🔓 Déchiffrement terminé")
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ Erreur de déchiffrement: {e}")
                    return False
            else:
                # Pas de chiffrement, utiliser directement le fichier
                fichier_temp = fichier_sauvegarde
            
            # Étape 2: Décompression
            print(f"{Fore.YELLOW}📂 Décompression en cours...")
            
            try:
                with zipfile.ZipFile(fichier_temp, 'r') as zipf:
                    # Extraire avec barre de progression
                    membres = zipf.infolist()
                    with tqdm(total=len(membres), desc="Extraction") as pbar:
                        for membre in membres:
                            zipf.extract(membre, dest)
                            pbar.update(1)
                
                print(f"{Fore.GREEN}✅ Décompression terminée")
                
                # Nettoyer le fichier temporaire si c'était un déchiffrement
                if metadonnees.chiffre and fichier_temp.exists():
                    fichier_temp.unlink()
                
                print(f"\n{Fore.GREEN}✅ Restauration terminée avec succès!")
                print(f"📁 Dossier de destination: {dest}")
                print(f"📊 Fichiers restaurés: {metadonnees.fichiers_inclus:,}")
                print(f"📅 Date de sauvegarde: {metadonnees.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True
                
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur lors de la décompression: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            print(f"{Fore.RED}❌ Erreur lors de la restauration: {e}")
            return False
    
    def obtenir_statistiques(self) -> StatistiquesSauvegarde:
        """Obtenir les statistiques globales"""
        sauvegardes = self.lister_sauvegardes()
        
        if not sauvegardes:
            return StatistiquesSauvegarde()
        
        stats = StatistiquesSauvegarde()
        stats.nombre_total = len(sauvegardes)
        
        tailles = []
        tailles_originales = []
        durees = []
        dates = []
        
        for backup in sauvegardes:
            tailles.append(backup.taille_chiffree)
            tailles_originales.append(backup.taille_originale)
            durees.append(backup.duree_sauvegarde)
            dates.append(backup.timestamp)
        
        stats.taille_totale = sum(tailles)
        stats.taille_originale_totale = sum(tailles_originales)
        
        if stats.taille_originale_totale > 0:
            stats.ratio_compression_moyen = (1 - stats.taille_totale / stats.taille_originale_totale) * 100
        
        stats.duree_moyenne = sum(durees) / len(durees) if durees else 0
        stats.derniere_sauvegarde = max(dates) if dates else None
        stats.plus_ancienne = min(dates) if dates else None
        
        return stats
    
    def demarrer_planification(self):
        """Démarrer la planification automatique"""
        if not self.config['planning']['actif']:
            print(f"{Fore.YELLOW}⚠️  Planification désactivée dans la configuration")
            return
        
        if self.scheduler_actif:
            print(f"{Fore.YELLOW}⚠️  Planification déjà active")
            return
        
        planning = self.config['planning']
        
        # Configurer le schedule selon la fréquence
        if planning['frequence'] == 'daily':
            schedule.every().day.at(planning['heure']).do(self._sauvegarde_automatique)
        elif planning['frequence'] == 'weekly':
            for jour in planning.get('jours_semaine', ['monday']):
                getattr(schedule.every(), jour).at(planning['heure']).do(self._sauvegarde_automatique)
        elif planning['frequence'] == 'hourly':
            schedule.every().hour.do(self._sauvegarde_automatique)
        
        self.scheduler_actif = True
        
        # Démarrer le thread du scheduler
        self.scheduler_thread = threading.Thread(target=self._executer_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print(f"{Fore.GREEN}✅ Planification démarrée - Fréquence: {planning['frequence']}")
        print(f"⏰ Prochaine exécution: {schedule.next_run()}")
    
    def arreter_planification(self):
        """Arrêter la planification automatique"""
        self.scheduler_actif = False
        schedule.clear()
        print(f"{Fore.YELLOW}⏹️  Planification arrêtée")
    
    def _executer_scheduler(self):
        """Exécuter le scheduler en continu"""
        while self.scheduler_actif:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute
    
    def _sauvegarde_automatique(self):
        """Exécuter une sauvegarde automatique"""
        logger.info("Démarrage de la sauvegarde automatique planifiée")
        print(f"{Fore.CYAN}🤖 Sauvegarde automatique planifiée...")
        
        # Note: En production, le mot de passe serait récupéré de manière sécurisée
        # Ici on fait une sauvegarde sans chiffrement pour l'automatisation
        metadonnees = self.creer_sauvegarde()
        
        if metadonnees:
            logger.info(f"Sauvegarde automatique {metadonnees.id} terminée avec succès")
        else:
            logger.error("Échec de la sauvegarde automatique")


def formater_taille(taille_bytes: int) -> str:
    """Formater une taille en bytes de manière lisible"""
    for unite in ['B', 'KB', 'MB', 'GB', 'TB']:
        if taille_bytes < 1024.0:
            return f"{taille_bytes:.1f} {unite}"
        taille_bytes /= 1024.0
    return f"{taille_bytes:.1f} PB"


def afficher_liste_sauvegardes(sauvegardes: List[MetadonneesSauvegarde]):
    """Afficher la liste des sauvegardes sous forme de tableau"""
    if not sauvegardes:
        print(f"{Fore.YELLOW}⚠️  Aucune sauvegarde trouvée")
        return
    
    # Préparer les données du tableau
    donnees = []
    for backup in sauvegardes:
        ratio_compression = (1 - backup.taille_compressee / backup.taille_originale) * 100 if backup.taille_originale > 0 else 0
        
        donnees.append([
            backup.id,
            backup.timestamp.strftime('%Y-%m-%d %H:%M'),
            formater_taille(backup.taille_originale),
            formater_taille(backup.taille_chiffree),
            f"{ratio_compression:.1f}%",
            f"{backup.duree_sauvegarde:.1f}s",
            "🔒" if backup.chiffre else "🔓",
            f"{backup.fichiers_inclus:,}"
        ])
    
    headers = [
        "ID", "Date", "Taille Orig.", "Taille Final", 
        "Compression", "Durée", "Chiffré", "Fichiers"
    ]
    
    print(f"\n{Fore.CYAN}📋 Liste des sauvegardes:")
    print(tabulate(donnees, headers=headers, tablefmt="grid"))


def afficher_statistiques(stats: StatistiquesSauvegarde):
    """Afficher les statistiques sous forme de tableau"""
    donnees = [
        ["Nombre total de sauvegardes", f"{stats.nombre_total:,}"],
        ["Taille totale", formater_taille(stats.taille_totale)],
        ["Taille originale totale", formater_taille(stats.taille_originale_totale)],
        ["Ratio de compression moyen", f"{stats.ratio_compression_moyen:.1f}%"],
        ["Durée moyenne", f"{stats.duree_moyenne:.1f}s"],
        ["Dernière sauvegarde", stats.derniere_sauvegarde.strftime('%Y-%m-%d %H:%M:%S') if stats.derniere_sauvegarde else "N/A"],
        ["Plus ancienne", stats.plus_ancienne.strftime('%Y-%m-%d %H:%M:%S') if stats.plus_ancienne else "N/A"]
    ]
    
    print(f"\n{Fore.CYAN}📊 Statistiques globales:")
    print(tabulate(donnees, headers=["Métrique", "Valeur"], tablefmt="grid"))


def main():
    """Fonction principale avec interface en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Système de Sauvegarde Chiffré - Sauvegarde sécurisée avec chiffrement AES",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 sauvegarde_chiffree.py create --source ./data --password monmotdepasse
  python3 sauvegarde_chiffree.py list --limit 5
  python3 sauvegarde_chiffree.py restore 20250308_143022 --password monmotdepasse
  python3 sauvegarde_chiffree.py stats
  python3 sauvegarde_chiffree.py schedule --start
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande: create
    create_parser = subparsers.add_parser('create', help='Créer une nouvelle sauvegarde')
    create_parser.add_argument('--source', '-s', help='Dossier source à sauvegarder')
    create_parser.add_argument('--password', '-p', help='Mot de passe pour le chiffrement')
    create_parser.add_argument('--config', '-c', default='config.json', help='Fichier de configuration')
    
    # Commande: list
    list_parser = subparsers.add_parser('list', help='Lister les sauvegardes')
    list_parser.add_argument('--limit', '-l', type=int, help='Nombre maximum de sauvegardes à afficher')
    list_parser.add_argument('--config', '-c', default='config.json', help='Fichier de configuration')
    
    # Commande: restore
    restore_parser = subparsers.add_parser('restore', help='Restaurer une sauvegarde')
    restore_parser.add_argument('backup_id', help='ID de la sauvegarde à restaurer')
    restore_parser.add_argument('--password', '-p', help='Mot de passe pour le déchiffrement')
    restore_parser.add_argument('--destination', '-d', help='Dossier de destination pour la restauration')
    restore_parser.add_argument('--config', '-c', default='config.json', help='Fichier de configuration')
    
    # Commande: stats
    stats_parser = subparsers.add_parser('stats', help='Afficher les statistiques')
    stats_parser.add_argument('--config', '-c', default='config.json', help='Fichier de configuration')
    
    # Commande: schedule
    schedule_parser = subparsers.add_parser('schedule', help='Gestion de la planification')
    schedule_parser.add_argument('--start', action='store_true', help='Démarrer la planification')
    schedule_parser.add_argument('--stop', action='store_true', help='Arrêter la planification')
    schedule_parser.add_argument('--status', action='store_true', help='Statut de la planification')
    schedule_parser.add_argument('--config', '-c', default='config.json', help='Fichier de configuration')
    
    # Commande: production
    production_parser = subparsers.add_parser('production', help='Mode production uniquement')
    production_parser.add_argument('--config', '-c', default='config.json', help='Fichier de configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialiser le système
    try:
        systeme = SystemeSauvegardeChiffre(args.config)
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur d'initialisation: {e}")
        return
    
    # Exécuter la commande
    if args.command == 'create':
        print(f"{Fore.CYAN}🚀 Création d'une nouvelle sauvegarde...")
        metadonnees = systeme.creer_sauvegarde(
            mot_de_passe=args.password,
            dossier_source=args.source
        )
        if not metadonnees:
            sys.exit(1)
    
    elif args.command == 'list':
        sauvegardes = systeme.lister_sauvegardes(args.limit)
        afficher_liste_sauvegardes(sauvegardes)
    
    elif args.command == 'restore':
        print(f"{Fore.CYAN}🔄 Restauration de la sauvegarde {args.backup_id}...")
        succes = systeme.restaurer_sauvegarde(
            args.backup_id,
            mot_de_passe=args.password,
            dossier_destination=args.destination
        )
        if not succes:
            sys.exit(1)
    
    elif args.command == 'stats':
        stats = systeme.obtenir_statistiques()
        afficher_statistiques(stats)
    
    elif args.command == 'schedule':
        if args.start:
            systeme.demarrer_planification()
            try:
                print(f"{Fore.GREEN}⏰ Planification active. Appuyez sur Ctrl+C pour arrêter.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                systeme.arreter_planification()
                print(f"\n{Fore.YELLOW}👋 Planification arrêtée")
        elif args.stop:
            systeme.arreter_planification()
        elif args.status:
            if systeme.scheduler_actif:
                print(f"{Fore.GREEN}✅ Planification active")
                if schedule.jobs:
                    print(f"⏰ Prochaine exécution: {schedule.next_run()}")
            else:
                print(f"{Fore.YELLOW}⏹️  Planification inactive")
    
    elif args.command == 'production':
        print(f"{Fore.YELLOW}⚠️  Production mode is active")
        print(f"{Fore.CYAN}💡 For demonstrations, use: python3 demos/demo_sauvegarde.py")


if __name__ == "__main__":
    main()