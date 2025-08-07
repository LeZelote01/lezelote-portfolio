#!/usr/bin/env python3
"""
Module d'Audit de Sécurité pour le Gestionnaire de Mots de Passe
Analyse de la force des mots de passe et détection des mots de passe compromis

Fonctionnalités:
- Analyse de la force des mots de passe (entropie, complexité)
- Détection de mots de passe compromis via HaveIBeenPwned API
- Détection de mots de passe dupliqués
- Analyse de l'ancienneté des mots de passe
- Recommandations automatiques d'amélioration
- Rapports détaillés de sécurité
"""

import re
import math
import hashlib
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from colorama import Fore, Style
import json

class SecurityLevel(Enum):
    """Niveaux de sécurité pour les mots de passe"""
    CRITICAL = "critical"      # Score 0-30
    LOW = "low"               # Score 31-50
    MEDIUM = "medium"         # Score 51-70
    GOOD = "good"            # Score 71-85
    EXCELLENT = "excellent"   # Score 86-100

@dataclass
class PasswordAnalysis:
    """Résultats de l'analyse d'un mot de passe"""
    password_id: str
    title: str
    username: str
    strength_score: int
    security_level: SecurityLevel
    entropy: float
    issues: List[str]
    recommendations: List[str]
    is_compromised: bool
    pwned_count: int
    last_analysis: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'password_id': self.password_id,
            'title': self.title,
            'username': self.username,
            'strength_score': self.strength_score,
            'security_level': self.security_level.value,
            'entropy': round(self.entropy, 2),
            'issues': self.issues,
            'recommendations': self.recommendations,
            'is_compromised': self.is_compromised,
            'pwned_count': self.pwned_count,
            'last_analysis': self.last_analysis.isoformat()
        }

@dataclass
class SecurityReport:
    """Rapport de sécurité complet"""
    total_passwords: int
    analyzed_passwords: int
    overall_score: int
    security_distribution: Dict[str, int]
    compromised_count: int
    duplicate_count: int
    weak_passwords: List[PasswordAnalysis]
    compromised_passwords: List[PasswordAnalysis]
    recommendations: List[str]
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_passwords': self.total_passwords,
            'analyzed_passwords': self.analyzed_passwords,
            'overall_score': self.overall_score,
            'security_distribution': self.security_distribution,
            'compromised_count': self.compromised_count,
            'duplicate_count': self.duplicate_count,
            'weak_passwords': [pwd.to_dict() for pwd in self.weak_passwords],
            'compromised_passwords': [pwd.to_dict() for pwd in self.compromised_passwords],
            'recommendations': self.recommendations,
            'generated_at': self.generated_at.isoformat()
        }

class SecurityAuditor:
    """Auditeur de sécurité des mots de passe"""
    
    def __init__(self, gestionnaire_mdp):
        self.gestionnaire = gestionnaire_mdp
        self.hibp_api_url = "https://api.pwnedpasswords.com/range"
        self.cache_file = "password_audit_cache.json"
        self.cache = self._load_cache()
        
        print(f"{Fore.GREEN}🛡️ Auditeur de Sécurité initialisé")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Charger le cache des analyses précédentes"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'pwned_checks': {},
                'last_full_audit': None,
                'password_hashes': {}
            }
    
    def _save_cache(self):
        """Sauvegarder le cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Impossible de sauvegarder le cache: {e}")
    
    def calculate_password_entropy(self, password: str) -> float:
        """Calculer l'entropie d'un mot de passe"""
        if not password:
            return 0.0
        
        # Calculer la taille de l'alphabet utilisé
        charset_size = 0
        
        # Minuscules
        if re.search(r'[a-z]', password):
            charset_size += 26
        
        # Majuscules
        if re.search(r'[A-Z]', password):
            charset_size += 26
        
        # Chiffres
        if re.search(r'[0-9]', password):
            charset_size += 10
        
        # Symboles
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
            charset_size += 32
        
        # Caractères spéciaux étendus
        if re.search(r'[^\w\s!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
            charset_size += 50
        
        # Entropie = log2(charset_size^length)
        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
        else:
            entropy = 0
        
        return entropy
    
    def analyze_password_strength(self, password: str) -> Tuple[int, List[str], List[str]]:
        """Analyser la force d'un mot de passe et retourner score, problèmes, recommandations"""
        score = 0
        issues = []
        recommendations = []
        
        # Longueur (0-25 points)
        length = len(password)
        if length >= 16:
            score += 25
        elif length >= 12:
            score += 20
        elif length >= 8:
            score += 15
        elif length >= 6:
            score += 10
        else:
            score += 5
            issues.append("Mot de passe trop court")
            recommendations.append("Utilisez au moins 12 caractères")
        
        # Variété de caractères (0-25 points)
        char_types = 0
        if re.search(r'[a-z]', password):
            char_types += 1
        else:
            issues.append("Aucune minuscule")
            recommendations.append("Ajoutez des lettres minuscules")
        
        if re.search(r'[A-Z]', password):
            char_types += 1
        else:
            issues.append("Aucune majuscule")
            recommendations.append("Ajoutez des lettres majuscules")
        
        if re.search(r'[0-9]', password):
            char_types += 1
        else:
            issues.append("Aucun chiffre")
            recommendations.append("Ajoutez des chiffres")
        
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
            char_types += 1
        else:
            issues.append("Aucun caractère spécial")
            recommendations.append("Ajoutez des caractères spéciaux (!@#$%^&*)")
        
        score += char_types * 6
        
        # Entropie (0-20 points)
        entropy = self.calculate_password_entropy(password)
        if entropy >= 80:
            score += 20
        elif entropy >= 60:
            score += 15
        elif entropy >= 40:
            score += 10
        elif entropy >= 20:
            score += 5
        else:
            issues.append("Entropie trop faible")
            recommendations.append("Augmentez la complexité du mot de passe")
        
        # Patterns communs (-10 points chacun)
        common_patterns = [
            (r'123', "Séquence numérique simple"),
            (r'abc', "Séquence alphabétique simple"),
            (r'password', "Mot 'password' détecté"),
            (r'admin', "Mot 'admin' détecté"),
            (r'user', "Mot 'user' détecté"),
            (r'login', "Mot 'login' détecté"),
            (r'qwerty', "Pattern clavier détecté"),
            (r'(.)\1{2,}', "Caractères répétés"),
            (r'^(.{1,3})\1+$', "Pattern répétitif détecté")
        ]
        
        for pattern, description in common_patterns:
            if re.search(pattern, password.lower()):
                score -= 10
                issues.append(description)
                recommendations.append("Évitez les patterns prévisibles")
        
        # Mots du dictionnaire (-15 points)
        common_words = [
            'password', 'admin', 'user', 'login', 'guest', 'root', 'test',
            'welcome', 'hello', 'world', 'computer', 'internet', 'security',
            'secret', 'private', 'public', 'system', 'server', 'database'
        ]
        
        for word in common_words:
            if word in password.lower():
                score -= 15
                issues.append(f"Mot commun détecté: {word}")
                recommendations.append("Évitez les mots du dictionnaire")
                break
        
        # Années récentes (-5 points)
        current_year = datetime.now().year
        for year in range(current_year - 10, current_year + 2):
            if str(year) in password:
                score -= 5
                issues.append("Année détectée dans le mot de passe")
                recommendations.append("Évitez les années dans les mots de passe")
                break
        
        # Bonus pour longueur exceptionnelle
        if length >= 20:
            score += 10
        elif length >= 24:
            score += 15
        
        # Limiter le score entre 0 et 100
        score = max(0, min(100, score))
        
        return score, issues, recommendations
    
    def check_password_pwned(self, password: str) -> Tuple[bool, int]:
        """Vérifier si un mot de passe a été compromis via HaveIBeenPwned"""
        if not password:
            return False, 0
        
        # Créer le hash SHA-1
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        hash_prefix = sha1_hash[:5]
        hash_suffix = sha1_hash[5:]
        
        # Vérifier le cache
        if hash_prefix in self.cache['pwned_checks']:
            cache_entry = self.cache['pwned_checks'][hash_prefix]
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            
            # Cache valide 24 heures
            if datetime.now() - cache_time < timedelta(hours=24):
                suffixes = cache_entry['suffixes']
                for suffix_data in suffixes:
                    if suffix_data['suffix'] == hash_suffix:
                        return True, suffix_data['count']
                return False, 0
        
        try:
            # Requête à l'API HaveIBeenPwned
            response = requests.get(
                f"{self.hibp_api_url}/{hash_prefix}",
                timeout=10,
                headers={
                    'User-Agent': 'Password-Manager-Audit-Tool',
                    'Add-Padding': 'true'
                }
            )
            
            if response.status_code == 200:
                # Parser la réponse
                suffixes = []
                lines = response.text.strip().split('\n')
                
                for line in lines:
                    if ':' in line:
                        suffix, count = line.split(':', 1)
                        suffixes.append({
                            'suffix': suffix.strip(),
                            'count': int(count.strip())
                        })
                
                # Mettre en cache
                self.cache['pwned_checks'][hash_prefix] = {
                    'timestamp': datetime.now().isoformat(),
                    'suffixes': suffixes
                }
                self._save_cache()
                
                # Vérifier si notre mot de passe est compromis
                for suffix_data in suffixes:
                    if suffix_data['suffix'] == hash_suffix:
                        return True, suffix_data['count']
                
                return False, 0
            
            elif response.status_code == 429:
                print(f"{Fore.YELLOW}⚠️ Rate limit HaveIBeenPwned atteint, pause...")
                time.sleep(2)
                return False, 0
            
            else:
                print(f"{Fore.YELLOW}⚠️ Erreur API HaveIBeenPwned: {response.status_code}")
                return False, 0
                
        except requests.exceptions.RequestException as e:
            print(f"{Fore.YELLOW}⚠️ Erreur réseau HaveIBeenPwned: {e}")
            return False, 0
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Erreur inattendue HaveIBeenPwned: {e}")
            return False, 0
    
    def analyze_password(self, password_id: str, title: str, username: str, password: str) -> PasswordAnalysis:
        """Analyser un mot de passe complet"""
        # Analyse de force
        strength_score, issues, recommendations = self.analyze_password_strength(password)
        
        # Calcul de l'entropie
        entropy = self.calculate_password_entropy(password)
        
        # Détermination du niveau de sécurité
        if strength_score >= 86:
            security_level = SecurityLevel.EXCELLENT
        elif strength_score >= 71:
            security_level = SecurityLevel.GOOD
        elif strength_score >= 51:
            security_level = SecurityLevel.MEDIUM
        elif strength_score >= 31:
            security_level = SecurityLevel.LOW
        else:
            security_level = SecurityLevel.CRITICAL
        
        # Vérification compromission
        is_compromised, pwned_count = self.check_password_pwned(password)
        
        if is_compromised:
            issues.append(f"Mot de passe compromis ({pwned_count:,} fois)")
            recommendations.append("CHANGEZ IMMÉDIATEMENT ce mot de passe")
            if security_level != SecurityLevel.CRITICAL:
                security_level = SecurityLevel.LOW  # Dégrade au minimum
        
        return PasswordAnalysis(
            password_id=password_id,
            title=title,
            username=username,
            strength_score=strength_score,
            security_level=security_level,
            entropy=entropy,
            issues=issues,
            recommendations=recommendations,
            is_compromised=is_compromised,
            pwned_count=pwned_count,
            last_analysis=datetime.now()
        )
    
    def find_duplicate_passwords(self, passwords: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Trouver les mots de passe dupliqués"""
        password_groups = {}
        
        for pwd_data in passwords:
            password = pwd_data['password']
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash not in password_groups:
                password_groups[password_hash] = []
            password_groups[password_hash].append(pwd_data)
        
        # Retourner seulement les groupes avec des doublons
        duplicates = [group for group in password_groups.values() if len(group) > 1]
        return duplicates
    
    def run_full_audit(self) -> SecurityReport:
        """Exécuter un audit complet de sécurité"""
        if not self.gestionnaire.check_session():
            raise Exception("Session expirée, authentification requise")
        
        print(f"{Fore.CYAN}🔍 Démarrage de l'audit de sécurité complet...")
        
        # Récupérer tous les mots de passe
        password_list = self.gestionnaire.list_passwords()
        total_passwords = len(password_list)
        
        if total_passwords == 0:
            print(f"{Fore.YELLOW}⚠️ Aucun mot de passe à analyser")
            return SecurityReport(
                total_passwords=0,
                analyzed_passwords=0,
                overall_score=0,
                security_distribution={level.value: 0 for level in SecurityLevel},
                compromised_count=0,
                duplicate_count=0,
                weak_passwords=[],
                compromised_passwords=[],
                recommendations=[],
                generated_at=datetime.now()
            )
        
        print(f"📊 Analyse de {total_passwords} mots de passe...")
        
        # Analyser chaque mot de passe
        analyses = []
        full_passwords = []
        
        for i, pwd_info in enumerate(password_list, 1):
            print(f"   🔍 Analyse {i}/{total_passwords}: {pwd_info['title']}")
            
            # Récupérer le mot de passe complet avec déchiffrement
            full_pwd = self.gestionnaire.get_password(pwd_info['id'])
            if full_pwd:
                full_passwords.append(full_pwd)
                analysis = self.analyze_password(
                    password_id=full_pwd['id'],
                    title=full_pwd['title'],
                    username=full_pwd['username'] or '',
                    password=full_pwd['password']
                )
                analyses.append(analysis)
            
            # Pause pour éviter le rate limiting
            time.sleep(0.1)
        
        analyzed_passwords = len(analyses)
        
        # Calculer les statistiques
        security_distribution = {level.value: 0 for level in SecurityLevel}
        total_score = 0
        compromised_passwords = []
        weak_passwords = []
        
        for analysis in analyses:
            security_distribution[analysis.security_level.value] += 1
            total_score += analysis.strength_score
            
            if analysis.is_compromised:
                compromised_passwords.append(analysis)
            
            if analysis.security_level in [SecurityLevel.CRITICAL, SecurityLevel.LOW]:
                weak_passwords.append(analysis)
        
        overall_score = int(total_score / analyzed_passwords) if analyzed_passwords > 0 else 0
        
        # Détecter les doublons
        duplicates = self.find_duplicate_passwords(full_passwords)
        duplicate_count = sum(len(group) for group in duplicates) - len(duplicates)
        
        # Générer les recommandations globales
        recommendations = self._generate_global_recommendations(
            analyses, duplicates, security_distribution
        )
        
        # Mettre à jour le cache
        self.cache['last_full_audit'] = datetime.now().isoformat()
        self._save_cache()
        
        report = SecurityReport(
            total_passwords=total_passwords,
            analyzed_passwords=analyzed_passwords,
            overall_score=overall_score,
            security_distribution=security_distribution,
            compromised_count=len(compromised_passwords),
            duplicate_count=duplicate_count,
            weak_passwords=weak_passwords,
            compromised_passwords=compromised_passwords,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
        
        print(f"{Fore.GREEN}✅ Audit terminé!")
        return report
    
    def _generate_global_recommendations(
        self, 
        analyses: List[PasswordAnalysis], 
        duplicates: List[List[Dict[str, Any]]], 
        security_distribution: Dict[str, int]
    ) -> List[str]:
        """Générer des recommandations globales"""
        recommendations = []
        
        total = len(analyses)
        if total == 0:
            return recommendations
        
        # Recommandations basées sur la distribution de sécurité
        critical_count = security_distribution[SecurityLevel.CRITICAL.value]
        low_count = security_distribution[SecurityLevel.LOW.value]
        
        if critical_count > 0:
            recommendations.append(
                f"🚨 URGENT: {critical_count} mot(s) de passe critique(s) à changer immédiatement"
            )
        
        if low_count > 0:
            recommendations.append(
                f"⚠️ {low_count} mot(s) de passe faible(s) à améliorer"
            )
        
        weak_percentage = (critical_count + low_count) / total * 100
        if weak_percentage > 30:
            recommendations.append(
                f"🔧 {weak_percentage:.1f}% de vos mots de passe sont faibles - effectuez une mise à jour globale"
            )
        
        # Recommandations sur les doublons
        if duplicates:
            recommendations.append(
                f"🔄 {len(duplicates)} groupes de mots de passe dupliqués détectés - utilisez des mots de passe uniques"
            )
        
        # Recommandations basées sur l'entropie moyenne
        avg_entropy = sum(a.entropy for a in analyses) / total
        if avg_entropy < 40:
            recommendations.append(
                "📏 Entropie moyenne faible - augmentez la longueur et la complexité"
            )
        
        # Recommandations de bonnes pratiques
        if total < 10:
            recommendations.append(
                "📝 Créez des mots de passe uniques pour tous vos comptes importants"
            )
        
        recommendations.append(
            "🔄 Activez l'authentification à deux facteurs (2FA) quand c'est possible"
        )
        
        recommendations.append(
            "📅 Planifiez une mise à jour régulière de vos mots de passe (tous les 6-12 mois)"
        )
        
        return recommendations
    
    def print_security_report(self, report: SecurityReport):
        """Afficher un rapport de sécurité formaté"""
        print(f"\n{Fore.BLUE}🛡️ RAPPORT DE SÉCURITÉ - {report.generated_at.strftime('%d/%m/%Y %H:%M')}")
        print("=" * 60)
        
        # Score global
        score_color = Fore.RED
        if report.overall_score >= 80:
            score_color = Fore.GREEN
        elif report.overall_score >= 60:
            score_color = Fore.YELLOW
        
        print(f"\n📊 {Fore.CYAN}SCORE GLOBAL: {score_color}{report.overall_score}/100{Style.RESET_ALL}")
        
        # Statistiques générales
        print(f"\n📈 {Fore.CYAN}STATISTIQUES:")
        print(f"   • Total des mots de passe: {report.total_passwords}")
        print(f"   • Analysés: {report.analyzed_passwords}")
        print(f"   • Compromis: {Fore.RED}{report.compromised_count}{Style.RESET_ALL}")
        print(f"   • Dupliqués: {Fore.YELLOW}{report.duplicate_count}{Style.RESET_ALL}")
        
        # Distribution de sécurité
        print(f"\n🎯 {Fore.CYAN}DISTRIBUTION DE SÉCURITÉ:")
        for level, count in report.security_distribution.items():
            if count > 0:
                level_color = {
                    'excellent': Fore.GREEN,
                    'good': Fore.CYAN,
                    'medium': Fore.YELLOW,
                    'low': Fore.MAGENTA,
                    'critical': Fore.RED
                }.get(level, Fore.WHITE)
                
                percentage = (count / report.analyzed_passwords * 100) if report.analyzed_passwords > 0 else 0
                print(f"   • {level_color}{level.upper()}: {count} ({percentage:.1f}%){Style.RESET_ALL}")
        
        # Mots de passe compromis
        if report.compromised_passwords:
            print(f"\n🚨 {Fore.RED}MOTS DE PASSE COMPROMIS (URGENT):")
            for pwd in report.compromised_passwords:
                print(f"   • {pwd.title} ({pwd.username}) - Compromis {pwd.pwned_count:,} fois")
        
        # Mots de passe faibles
        if report.weak_passwords:
            print(f"\n⚠️ {Fore.YELLOW}MOTS DE PASSE FAIBLES (Top 5):")
            sorted_weak = sorted(report.weak_passwords, key=lambda x: x.strength_score)[:5]
            for pwd in sorted_weak:
                print(f"   • {pwd.title} - Score: {pwd.strength_score}/100")
                for issue in pwd.issues[:2]:  # Limiter à 2 problèmes principaux
                    print(f"     ↳ {issue}")
        
        # Recommandations
        if report.recommendations:
            print(f"\n💡 {Fore.CYAN}RECOMMANDATIONS:")
            for i, rec in enumerate(report.recommendations[:7], 1):  # Limiter à 7 recommandations
                print(f"   {i}. {rec}")
        
        print(f"\n{Style.RESET_ALL}" + "=" * 60)

if __name__ == "__main__":
    print(f"{Fore.BLUE}🛡️ AUDIT DE SÉCURITÉ")
    print("=" * 50)
    print(f"{Fore.CYAN}Module de sécurité pour analyse avancée des mots de passe")
    print(f"{Fore.CYAN}Consultez la documentation pour l'utilisation")