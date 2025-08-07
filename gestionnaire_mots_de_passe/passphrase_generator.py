#!/usr/bin/env python3
"""
Générateur de Phrases de Passe XKCD pour le Gestionnaire de Mots de Passe
Inspiré du célèbre comic XKCD "correct horse battery staple"

Fonctionnalités:
- Génération de phrases de passe mémorables et sécurisées
- Dictionnaires multilingues (français et anglais)
- Options de personnalisation (séparateurs, nombre de mots, capitalisation)
- Calcul d'entropie et estimation de force
- Intégration avec le gestionnaire principal
"""

import random
import re
import secrets
import math
import json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from colorama import Fore, Style

class PassphraseLanguage(Enum):
    """Langues disponibles pour les phrases de passe"""
    FRENCH = "french"
    ENGLISH = "english"
    MIXED = "mixed"

class SeparatorStyle(Enum):
    """Styles de séparateurs disponibles"""
    DASH = "-"
    UNDERSCORE = "_"
    DOT = "."
    SPACE = " "
    CAMEL = "camel"  # Pas de séparateur, CamelCase
    NUMBERS = "numbers"  # Séparateurs numériques aléatoires
    SYMBOLS = "symbols"  # Symboles aléatoires

@dataclass
class PassphraseConfig:
    """Configuration pour la génération de phrases de passe"""
    num_words: int = 4
    language: PassphraseLanguage = PassphraseLanguage.FRENCH
    separator: SeparatorStyle = SeparatorStyle.DASH
    capitalize_words: bool = True
    add_numbers: bool = True
    add_symbols: bool = False
    min_word_length: int = 4
    max_word_length: int = 8
    custom_words: Optional[List[str]] = None

@dataclass
class PassphraseResult:
    """Résultat de génération d'une phrase de passe"""
    passphrase: str
    words_used: List[str]
    entropy: float
    strength_estimate: str
    crack_time_estimate: str
    config_used: PassphraseConfig
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'passphrase': self.passphrase,
            'words_used': self.words_used,
            'entropy': round(self.entropy, 2),
            'strength_estimate': self.strength_estimate,
            'crack_time_estimate': self.crack_time_estimate,
            'config': {
                'num_words': self.config_used.num_words,
                'language': self.config_used.language.value,
                'separator': self.config_used.separator.value,
                'capitalize_words': self.config_used.capitalize_words,
                'add_numbers': self.config_used.add_numbers,
                'add_symbols': self.config_used.add_symbols
            }
        }

class XKCDPassphraseGenerator:
    """Générateur de phrases de passe XKCD"""
    
    def __init__(self):
        # Dictionnaire français de mots courants mais pas trop simples
        self.french_words = [
            # Noms communs
            "maison", "jardin", "soleil", "lune", "étoile", "océan", "montagne", "rivière",
            "forêt", "fleur", "arbre", "oiseau", "chat", "chien", "livre", "musique",
            "voyage", "aventure", "rêve", "espoir", "liberté", "bonheur", "amitié", "famille",
            "temps", "histoire", "nature", "science", "art", "culture", "langue", "mot",
            "couleur", "rouge", "bleu", "vert", "jaune", "orange", "violet", "rose",
            "blanc", "noir", "gris", "marron", "café", "thé", "pain", "fromage",
            "fruit", "pomme", "orange", "banane", "fraise", "raisin", "citron", "poire",
            
            # Adjectifs
            "grand", "petit", "beau", "joli", "fort", "doux", "rapide", "lent",
            "nouveau", "ancien", "moderne", "simple", "complexe", "facile", "difficile",
            "chaud", "froid", "tiède", "sec", "humide", "clair", "sombre", "brillant",
            "calme", "agité", "heureux", "triste", "content", "fier", "brave", "sage",
            
            # Verbes à l'infinitif
            "marcher", "courir", "voler", "nager", "danser", "chanter", "rire", "pleurer",
            "dormir", "rêver", "penser", "créer", "construire", "découvrir", "explorer",
            "apprendre", "enseigner", "aider", "partager", "donner", "recevoir", "aimer",
            
            # Concepts
            "énergie", "lumière", "ombre", "silence", "bruit", "musique", "rythme",
            "harmonie", "équilibre", "mouvement", "vitesse", "force", "pouvoir",
            "magie", "mystère", "secret", "surprise", "cadeau", "trésor", "perle"
        ]
        
        # Dictionnaire anglais
        self.english_words = [
            # Common nouns
            "house", "garden", "sun", "moon", "star", "ocean", "mountain", "river",
            "forest", "flower", "tree", "bird", "cat", "dog", "book", "music",
            "travel", "adventure", "dream", "hope", "freedom", "happiness", "friend",
            "family", "time", "story", "nature", "science", "art", "culture",
            
            # Colors
            "red", "blue", "green", "yellow", "orange", "purple", "pink",
            "white", "black", "gray", "brown", "silver", "gold",
            
            # Foods
            "apple", "orange", "banana", "grape", "lemon", "bread", "cheese",
            "coffee", "tea", "cake", "honey", "sugar", "salt", "pepper",
            
            # Adjectives
            "big", "small", "beautiful", "strong", "gentle", "fast", "slow",
            "new", "old", "modern", "simple", "easy", "hard", "warm", "cold",
            "bright", "dark", "calm", "happy", "proud", "wise", "brave",
            
            # Verbs
            "walk", "run", "fly", "swim", "dance", "sing", "laugh", "smile",
            "sleep", "dream", "think", "create", "build", "discover", "explore",
            "learn", "teach", "help", "share", "give", "love", "play",
            
            # Concepts
            "energy", "light", "shadow", "silence", "sound", "rhythm", "harmony",
            "balance", "motion", "speed", "power", "magic", "mystery", "secret",
            "surprise", "gift", "treasure", "pearl", "crystal", "diamond"
        ]
        
        # Symboles pour les séparateurs
        self.separator_symbols = ["!", "@", "#", "$", "%", "&", "*", "+", "=", "?"]
        
        print(f"{Fore.GREEN}🎯 Générateur de Phrases de Passe XKCD initialisé")
        print(f"   📚 {len(self.french_words)} mots français, {len(self.english_words)} mots anglais")
    
    def get_word_list(self, language: PassphraseLanguage) -> List[str]:
        """Obtenir la liste de mots selon la langue"""
        if language == PassphraseLanguage.FRENCH:
            return self.french_words
        elif language == PassphraseLanguage.ENGLISH:
            return self.english_words
        elif language == PassphraseLanguage.MIXED:
            return self.french_words + self.english_words
        else:
            return self.french_words  # Par défaut
    
    def filter_words(self, words: List[str], min_length: int, max_length: int) -> List[str]:
        """Filtrer les mots selon la longueur"""
        return [word for word in words if min_length <= len(word) <= max_length]
    
    def calculate_passphrase_entropy(self, config: PassphraseConfig) -> float:
        """Calculer l'entropie estimée d'une phrase de passe"""
        word_list = self.get_word_list(config.language)
        filtered_words = self.filter_words(word_list, config.min_word_length, config.max_word_length)
        
        # Entropie de base des mots
        word_entropy = math.log2(len(filtered_words)) * config.num_words
        
        # Entropie additionnelle selon les options
        additional_entropy = 0
        
        # Capitalisation (double les possibilités pour chaque mot)
        if config.capitalize_words:
            additional_entropy += config.num_words  # 1 bit par mot
        
        # Nombres (ajoute généralement 1-2 chiffres)
        if config.add_numbers:
            additional_entropy += 6.64  # log2(100) pour 2 chiffres
        
        # Symboles
        if config.add_symbols:
            additional_entropy += 3.32  # log2(10) pour environ 10 symboles
        
        # Séparateur (si aléatoire)
        if config.separator == SeparatorStyle.SYMBOLS:
            additional_entropy += math.log2(len(self.separator_symbols)) * (config.num_words - 1)
        elif config.separator == SeparatorStyle.NUMBERS:
            additional_entropy += 3.32 * (config.num_words - 1)  # chiffre aléatoire
        
        return word_entropy + additional_entropy
    
    def estimate_strength(self, entropy: float) -> Tuple[str, str]:
        """Estimer la force et le temps de crack"""
        if entropy >= 80:
            strength = "Excellent"
            crack_time = "Plusieurs siècles"
        elif entropy >= 60:
            strength = "Très Bon"
            crack_time = "Plusieurs décennies"
        elif entropy >= 50:
            strength = "Bon"
            crack_time = "Plusieurs années"
        elif entropy >= 40:
            strength = "Moyen"
            crack_time = "Plusieurs mois"
        elif entropy >= 30:
            strength = "Faible"
            crack_time = "Quelques semaines"
        else:
            strength = "Très Faible"
            crack_time = "Quelques jours"
        
        return strength, crack_time
    
    def apply_capitalization(self, words: List[str], config: PassphraseConfig) -> List[str]:
        """Appliquer la capitalisation selon la configuration"""
        if not config.capitalize_words:
            return words
        
        capitalized = []
        for word in words:
            # Capitalisation aléatoire : première lettre, tout en majuscules, ou normal
            choice = secrets.randbelow(3)
            if choice == 0:
                capitalized.append(word.lower())
            elif choice == 1:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word.upper())
        
        return capitalized
    
    def generate_separator(self, config: PassphraseConfig) -> str:
        """Générer un séparateur selon le style"""
        if config.separator == SeparatorStyle.NUMBERS:
            return str(secrets.randbelow(10))
        elif config.separator == SeparatorStyle.SYMBOLS:
            return secrets.choice(self.separator_symbols)
        else:
            return config.separator.value
    
    def add_numbers_and_symbols(self, passphrase: str, config: PassphraseConfig) -> str:
        """Ajouter des nombres et symboles si demandé"""
        result = passphrase
        
        if config.add_numbers:
            # Ajouter 1-3 chiffres au début ou à la fin
            num_digits = secrets.randbelow(3) + 1
            number = ''.join([str(secrets.randbelow(10)) for _ in range(num_digits)])
            
            if secrets.randbelow(2):  # Au début
                result = number + result
            else:  # À la fin
                result = result + number
        
        if config.add_symbols:
            # Ajouter 1-2 symboles
            num_symbols = secrets.randbelow(2) + 1
            symbols = ''.join([secrets.choice(self.separator_symbols) for _ in range(num_symbols)])
            
            if secrets.randbelow(2):  # Au début
                result = symbols + result
            else:  # À la fin
                result = result + symbols
        
        return result
    
    def generate(self, config: Optional[PassphraseConfig] = None) -> PassphraseResult:
        """Générer une phrase de passe selon la configuration"""
        if config is None:
            config = PassphraseConfig()
        
        # Obtenir et filtrer les mots
        word_list = self.get_word_list(config.language)
        filtered_words = self.filter_words(word_list, config.min_word_length, config.max_word_length)
        
        if len(filtered_words) < config.num_words:
            raise ValueError(f"Pas assez de mots disponibles ({len(filtered_words)} < {config.num_words})")
        
        # Utiliser des mots personnalisés si fournis
        if config.custom_words:
            available_words = config.custom_words + filtered_words
        else:
            available_words = filtered_words
        
        # Sélectionner les mots aléatoirement
        selected_words = secrets.SystemRandom().sample(available_words, config.num_words)
        
        # Appliquer la capitalisation
        words = self.apply_capitalization(selected_words, config)
        
        # Construire la phrase de passe
        if config.separator == SeparatorStyle.CAMEL:
            # CamelCase sans séparateur
            passphrase = ''.join(word.capitalize() for word in words)
        elif config.separator in [SeparatorStyle.NUMBERS, SeparatorStyle.SYMBOLS]:
            # Séparateurs aléatoires
            separators = [self.generate_separator(config) for _ in range(config.num_words - 1)]
            passphrase = words[0]
            for i, sep in enumerate(separators):
                passphrase += sep + words[i + 1]
        else:
            # Séparateur fixe
            separator = config.separator.value
            passphrase = separator.join(words)
        
        # Ajouter nombres et symboles
        passphrase = self.add_numbers_and_symbols(passphrase, config)
        
        # Calculer l'entropie et la force
        entropy = self.calculate_passphrase_entropy(config)
        strength, crack_time = self.estimate_strength(entropy)
        
        return PassphraseResult(
            passphrase=passphrase,
            words_used=selected_words,
            entropy=entropy,
            strength_estimate=strength,
            crack_time_estimate=crack_time,
            config_used=config
        )
    
    def generate_multiple(self, count: int, config: Optional[PassphraseConfig] = None) -> List[PassphraseResult]:
        """Générer plusieurs phrases de passe"""
        results = []
        for _ in range(count):
            results.append(self.generate(config))
        return results
    
    def interactive_generator(self):
        """Interface interactive pour générer des phrases de passe"""
        print(f"\n{Fore.CYAN}🎯 GÉNÉRATEUR INTERACTIF DE PHRASES DE PASSE XKCD")
        print("=" * 55)
        
        # Configuration par l'utilisateur
        config = PassphraseConfig()
        
        try:
            # Nombre de mots
            num_words = input(f"\n📝 Nombre de mots (défaut: {config.num_words}): ").strip()
            if num_words:
                config.num_words = max(2, min(8, int(num_words)))
            
            # Langue
            print(f"\n🌍 Langues disponibles:")
            print(f"   1. Français (défaut)")
            print(f"   2. Anglais")
            print(f"   3. Mélangé")
            
            lang_choice = input("Choix (1-3): ").strip()
            if lang_choice == "2":
                config.language = PassphraseLanguage.ENGLISH
            elif lang_choice == "3":
                config.language = PassphraseLanguage.MIXED
            
            # Séparateur
            print(f"\n🔗 Séparateurs disponibles:")
            print(f"   1. Tiret '-' (défaut)")
            print(f"   2. Underscore '_'")
            print(f"   3. Point '.'")
            print(f"   4. Espace ' '")
            print(f"   5. CamelCase (pas de séparateur)")
            print(f"   6. Chiffres aléatoires")
            print(f"   7. Symboles aléatoires")
            
            sep_choice = input("Choix (1-7): ").strip()
            sep_map = {
                "2": SeparatorStyle.UNDERSCORE,
                "3": SeparatorStyle.DOT,
                "4": SeparatorStyle.SPACE,
                "5": SeparatorStyle.CAMEL,
                "6": SeparatorStyle.NUMBERS,
                "7": SeparatorStyle.SYMBOLS
            }
            config.separator = sep_map.get(sep_choice, SeparatorStyle.DASH)
            
            # Options additionnelles
            config.add_numbers = input(f"\n🔢 Ajouter des chiffres? (O/n): ").strip().lower() != 'n'
            config.add_symbols = input(f"🔣 Ajouter des symboles? (o/N): ").strip().lower() == 'o'
            config.capitalize_words = input(f"🔤 Capitalisation aléatoire? (O/n): ").strip().lower() != 'n'
            
            # Générer plusieurs options
            count = 5
            print(f"\n🎲 Génération de {count} phrases de passe...")
            
            results = self.generate_multiple(count, config)
            
            print(f"\n{Fore.GREEN}✨ PHRASES DE PASSE GÉNÉRÉES:")
            print("=" * 50)
            
            for i, result in enumerate(results, 1):
                color = Fore.GREEN if result.entropy >= 60 else Fore.YELLOW if result.entropy >= 40 else Fore.RED
                
                print(f"\n{i}. {color}{result.passphrase}{Style.RESET_ALL}")
                print(f"   📊 Force: {result.strength_estimate} (Entropie: {result.entropy:.1f} bits)")
                print(f"   ⏱️ Temps de crack estimé: {result.crack_time_estimate}")
                print(f"   📝 Mots: {', '.join(result.words_used)}")
            
            # Permettre à l'utilisateur de choisir
            print(f"\n{Fore.CYAN}💾 Voulez-vous utiliser une de ces phrases de passe?")
            choice = input("Entrez le numéro (1-5) ou 'n' pour annuler: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= 5:
                selected = results[int(choice) - 1]
                print(f"\n{Fore.GREEN}✅ Phrase de passe sélectionnée:")
                print(f"🔐 {selected.passphrase}")
                
                # Optionnel: ajouter directement au gestionnaire
                add_to_manager = input(f"\n💾 Ajouter au gestionnaire? (o/N): ").strip().lower() == 'o'
                if add_to_manager:
                    return selected.passphrase
            
        except (ValueError, KeyboardInterrupt):
            print(f"\n{Fore.YELLOW}⚠️ Génération annulée")
        
        return None

if __name__ == "__main__":
    print("Passphrase Generator - Mode production uniquement")