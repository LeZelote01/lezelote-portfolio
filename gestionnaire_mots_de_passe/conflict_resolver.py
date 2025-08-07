#!/usr/bin/env python3
"""
Résolveur de conflits pour la synchronisation cloud
Gestionnaire de Mots de Passe - Conflict Resolution Module
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class ConflictType(Enum):
    """Types de conflits possibles"""
    CONTENT_CONFLICT = "content_conflict"
    TIMESTAMP_CONFLICT = "timestamp_conflict"
    DELETE_MODIFY_CONFLICT = "delete_modify_conflict"
    METADATA_CONFLICT = "metadata_conflict"

class ResolutionStrategy(Enum):
    """Stratégies de résolution de conflits"""
    ASK_USER = "ask_user"
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    KEEP_BOTH = "keep_both"
    MERGE_DATA = "merge_data"
    MOST_RECENT = "most_recent"

@dataclass
class ConflictInfo:
    """Information sur un conflit détecté"""
    password_id: str
    conflict_type: ConflictType
    local_version: Dict
    remote_version: Dict
    local_modified: str
    remote_modified: str
    description: str

@dataclass
class ResolutionResult:
    """Résultat de la résolution d'un conflit"""
    resolution_strategy: ResolutionStrategy
    final_version: Dict
    backup_versions: List[Dict]
    notes: str

class ConflictResolver:
    """Résolveur de conflits pour la synchronisation cloud"""
    
    def __init__(self):
        self.resolution_history = []
    
    def detect_conflicts(self, local_data: Dict, remote_data: Dict) -> List[ConflictInfo]:
        """Détecter les conflits entre les données locales et distantes"""
        conflicts = []
        
        # Obtenir tous les IDs uniques
        local_ids = set(local_data.keys())
        remote_ids = set(remote_data.keys())
        all_ids = local_ids.union(remote_ids)
        
        for password_id in all_ids:
            local_password = local_data.get(password_id)
            remote_password = remote_data.get(password_id)
            
            # Cas 1: Mot de passe existe seulement localement
            if local_password and not remote_password:
                continue  # Pas de conflit, sera ajouté au cloud
            
            # Cas 2: Mot de passe existe seulement dans le cloud
            if remote_password and not local_password:
                continue  # Pas de conflit, sera téléchargé localement
            
            # Cas 3: Mot de passe existe dans les deux, vérifier les conflits
            if local_password and remote_password:
                conflict = self._analyze_password_conflict(password_id, local_password, remote_password)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _analyze_password_conflict(self, password_id: str, local_data: Dict, remote_data: Dict) -> Optional[ConflictInfo]:
        """Analyser un conflit spécifique entre deux versions d'un mot de passe"""
        
        # Calculer les checksums pour détecter les différences de contenu
        local_content = self._get_password_content_hash(local_data)
        remote_content = self._get_password_content_hash(remote_data)
        
        # Si les contenus sont identiques, pas de conflit
        if local_content == remote_content:
            return None
        
        local_modified = local_data.get('updated_at', local_data.get('created_at', ''))
        remote_modified = remote_data.get('updated_at', remote_data.get('created_at', ''))
        
        # Déterminer le type de conflit
        conflict_type = ConflictType.CONTENT_CONFLICT
        description = f"Le mot de passe '{local_data.get('title', password_id)}' a été modifié à la fois localement et dans le cloud."
        
        # Analyser les différences spécifiques
        differences = self._get_field_differences(local_data, remote_data)
        if differences:
            description += f" Champs différents: {', '.join(differences)}"
        
        return ConflictInfo(
            password_id=password_id,
            conflict_type=conflict_type,
            local_version=local_data,
            remote_version=remote_data,
            local_modified=local_modified,
            remote_modified=remote_modified,
            description=description
        )
    
    def _get_password_content_hash(self, password_data: Dict) -> str:
        """Calculer un hash du contenu d'un mot de passe pour détecter les modifications"""
        # Créer une version normalisée des données pour le hash
        normalized_data = {
            'title': password_data.get('title', ''),
            'username': password_data.get('username', ''),
            'password': password_data.get('password', ''),
            'url': password_data.get('url', ''),
            'notes': password_data.get('notes', ''),
            'category': password_data.get('category', '')
        }
        
        # Convertir en JSON stable et calculer le hash
        json_str = json.dumps(normalized_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _get_field_differences(self, local_data: Dict, remote_data: Dict) -> List[str]:
        """Obtenir la liste des champs qui diffèrent entre les deux versions"""
        differences = []
        fields_to_check = ['title', 'username', 'password', 'url', 'notes', 'category']
        
        for field in fields_to_check:
            local_value = local_data.get(field, '')
            remote_value = remote_data.get(field, '')
            if local_value != remote_value:
                differences.append(field)
        
        return differences
    
    def resolve_conflict(self, conflict: ConflictInfo, strategy: ResolutionStrategy, user_choice: Dict = None) -> ResolutionResult:
        """Résoudre un conflit selon la stratégie choisie"""
        
        if strategy == ResolutionStrategy.LOCAL_WINS:
            return self._resolve_local_wins(conflict)
        
        elif strategy == ResolutionStrategy.REMOTE_WINS:
            return self._resolve_remote_wins(conflict)
        
        elif strategy == ResolutionStrategy.KEEP_BOTH:
            return self._resolve_keep_both(conflict)
        
        elif strategy == ResolutionStrategy.MOST_RECENT:
            return self._resolve_most_recent(conflict)
        
        elif strategy == ResolutionStrategy.MERGE_DATA:
            return self._resolve_merge_data(conflict)
        
        elif strategy == ResolutionStrategy.ASK_USER and user_choice:
            return self._resolve_user_choice(conflict, user_choice)
        
        else:
            # Par défaut, utiliser la version la plus récente
            return self._resolve_most_recent(conflict)
    
    def _resolve_local_wins(self, conflict: ConflictInfo) -> ResolutionResult:
        """Résolution: la version locale gagne"""
        return ResolutionResult(
            resolution_strategy=ResolutionStrategy.LOCAL_WINS,
            final_version=conflict.local_version,
            backup_versions=[conflict.remote_version],
            notes=f"Version locale conservée pour '{conflict.local_version.get('title', conflict.password_id)}'"
        )
    
    def _resolve_remote_wins(self, conflict: ConflictInfo) -> ResolutionResult:
        """Résolution: la version distante gagne"""
        return ResolutionResult(
            resolution_strategy=ResolutionStrategy.REMOTE_WINS,
            final_version=conflict.remote_version,
            backup_versions=[conflict.local_version],
            notes=f"Version cloud conservée pour '{conflict.remote_version.get('title', conflict.password_id)}'"
        )
    
    def _resolve_keep_both(self, conflict: ConflictInfo) -> ResolutionResult:
        """Résolution: garder les deux versions"""
        # Créer une version renommée pour éviter la collision
        local_version = conflict.local_version.copy()
        remote_version = conflict.remote_version.copy()
        
        # Renommer la version locale
        original_title = local_version.get('title', 'Mot de passe')
        local_version['title'] = f"{original_title} (Local)"
        remote_version['title'] = f"{original_title} (Cloud)"
        
        return ResolutionResult(
            resolution_strategy=ResolutionStrategy.KEEP_BOTH,
            final_version=local_version,  # La version locale garde l'ID original
            backup_versions=[remote_version],  # La version cloud sera ajoutée avec un nouvel ID
            notes=f"Les deux versions de '{original_title}' ont été conservées"
        )
    
    def _resolve_most_recent(self, conflict: ConflictInfo) -> ResolutionResult:
        """Résolution: garder la version la plus récente"""
        local_time = self._parse_timestamp(conflict.local_modified)
        remote_time = self._parse_timestamp(conflict.remote_modified)
        
        if local_time >= remote_time:
            final_version = conflict.local_version
            backup_version = conflict.remote_version
            source = "locale"
        else:
            final_version = conflict.remote_version
            backup_version = conflict.local_version
            source = "cloud"
        
        return ResolutionResult(
            resolution_strategy=ResolutionStrategy.MOST_RECENT,
            final_version=final_version,
            backup_versions=[backup_version],
            notes=f"Version {source} plus récente conservée pour '{final_version.get('title', conflict.password_id)}'"
        )
    
    def _resolve_merge_data(self, conflict: ConflictInfo) -> ResolutionResult:
        """Résolution: fusionner les données intelligemment"""
        merged_version = conflict.local_version.copy()
        
        # Stratégie de fusion intelligente
        # 1. Prendre le titre et l'URL les plus longs (plus d'informations)
        if len(conflict.remote_version.get('title', '')) > len(merged_version.get('title', '')):
            merged_version['title'] = conflict.remote_version['title']
        
        if len(conflict.remote_version.get('url', '')) > len(merged_version.get('url', '')):
            merged_version['url'] = conflict.remote_version['url']
        
        # 2. Fusionner les notes
        local_notes = merged_version.get('notes', '').strip()
        remote_notes = conflict.remote_version.get('notes', '').strip()
        
        if local_notes and remote_notes and local_notes != remote_notes:
            merged_version['notes'] = f"{local_notes}\n---\n{remote_notes}"
        elif remote_notes and not local_notes:
            merged_version['notes'] = remote_notes
        
        # 3. Garder le mot de passe le plus récent
        local_time = self._parse_timestamp(conflict.local_modified)
        remote_time = self._parse_timestamp(conflict.remote_modified)
        
        if remote_time > local_time:
            merged_version['password'] = conflict.remote_version.get('password', merged_version['password'])
        
        return ResolutionResult(
            resolution_strategy=ResolutionStrategy.MERGE_DATA,
            final_version=merged_version,
            backup_versions=[conflict.local_version, conflict.remote_version],
            notes=f"Données fusionnées intelligemment pour '{merged_version.get('title', conflict.password_id)}'"
        )
    
    def _resolve_user_choice(self, conflict: ConflictInfo, user_choice: Dict) -> ResolutionResult:
        """Résolution: selon le choix de l'utilisateur"""
        choice = user_choice.get('choice', 'local')
        
        if choice == 'local':
            return self._resolve_local_wins(conflict)
        elif choice == 'remote':
            return self._resolve_remote_wins(conflict)
        elif choice == 'both':
            return self._resolve_keep_both(conflict)
        elif choice == 'merge':
            return self._resolve_merge_data(conflict)
        else:
            return self._resolve_most_recent(conflict)
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Parser un timestamp en format datetime"""
        try:
            if not timestamp_str:
                return 0.0
            
            # Essayer différents formats de timestamp
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%f'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str.split('.')[0], fmt.split('.')[0])
                    return dt.timestamp()
                except ValueError:
                    continue
            
            # Si aucun format ne fonctionne, essayer de parser directement comme timestamp
            return float(timestamp_str)
            
        except (ValueError, TypeError):
            return 0.0
    
    def get_conflict_summary(self, conflicts: List[ConflictInfo]) -> Dict:
        """Obtenir un résumé des conflits détectés"""
        if not conflicts:
            return {
                'total_conflicts': 0,
                'conflict_types': {},
                'affected_passwords': []
            }
        
        summary = {
            'total_conflicts': len(conflicts),
            'conflict_types': {},
            'affected_passwords': []
        }
        
        for conflict in conflicts:
            # Compter par type
            conflict_type = conflict.conflict_type.value
            summary['conflict_types'][conflict_type] = summary['conflict_types'].get(conflict_type, 0) + 1
            
            # Ajouter les mots de passe affectés
            summary['affected_passwords'].append({
                'id': conflict.password_id,
                'title': conflict.local_version.get('title', 'Mot de passe sans titre'),
                'type': conflict_type,
                'description': conflict.description
            })
        
        return summary
    
    def save_resolution_history(self, conflict: ConflictInfo, result: ResolutionResult):
        """Sauvegarder l'historique de résolution pour analyse future"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'password_id': conflict.password_id,
            'conflict_type': conflict.conflict_type.value,
            'resolution_strategy': result.resolution_strategy.value,
            'notes': result.notes
        }
        
        self.resolution_history.append(history_entry)
        
        # Garder seulement les 100 dernières résolutions
        if len(self.resolution_history) > 100:
            self.resolution_history = self.resolution_history[-100:]

# Instance globale du résolveur de conflits
conflict_resolver = ConflictResolver()