#!/usr/bin/env python3
"""
Interface graphique Tkinter pour le Gestionnaire de Mots de Passe
Version adaptée pour remplacer PyQt5
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
import sys
import os
import getpass
import json
from threading import Timer
from datetime import datetime

# Ajouter le chemin du module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gestionnaire_mdp import GestionnaireMDP
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class LoginDialog:
    """Dialogue de connexion"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connexion - Gestionnaire de Mots de Passe")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Titre
        title_label = tk.Label(
            self.dialog, 
            text="🔐 Gestionnaire de Mots de Passe", 
            font=("Arial", 16, "bold"),
            fg="#2E86AB"
        )
        title_label.pack(pady=20)
        
        # Instructions
        info_label = tk.Label(
            self.dialog,
            text="Saisissez votre mot de passe maître pour continuer",
            font=("Arial", 10),
            fg="#666666"
        )
        info_label.pack(pady=10)
        
        # Frame pour les champs
        fields_frame = tk.Frame(self.dialog)
        fields_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Champ mot de passe
        tk.Label(fields_frame, text="Mot de passe maître:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.password_entry = tk.Entry(fields_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill=tk.X, pady=(5, 15))
        self.password_entry.focus()
        
        # Boutons
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=20)
        
        tk.Button(
            buttons_frame,
            text="Se connecter",
            command=self.login,
            bg="#2E86AB",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Annuler",
            command=self.cancel,
            bg="#A13333",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Setup initial
        tk.Button(
            buttons_frame,
            text="Configuration initiale",
            command=self.setup_master,
            bg="#F18F01",
            fg="white",
            font=("Arial", 9),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.login())
        
    def login(self):
        """Tenter la connexion"""
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("Erreur", "Veuillez saisir le mot de passe maître")
            return
        
        self.result = password
        self.dialog.destroy()
        
    def cancel(self):
        """Annuler la connexion"""
        self.result = None
        self.dialog.destroy()
        
    def setup_master(self):
        """Configurer le mot de passe maître"""
        setup_dialog = MasterPasswordSetupDialog(self.dialog)
        if setup_dialog.result:
            messagebox.showinfo("Succès", "Mot de passe maître configuré avec succès!")

class MasterPasswordSetupDialog:
    """Dialogue de configuration du mot de passe maître"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration du Mot de Passe Maître")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"450x350+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Titre
        title_label = tk.Label(
            self.dialog, 
            text="🔧 Configuration Initiale", 
            font=("Arial", 16, "bold"),
            fg="#F18F01"
        )
        title_label.pack(pady=20)
        
        # Instructions
        info_label = tk.Label(
            self.dialog,
            text="Créez un mot de passe maître sécurisé\n(minimum 8 caractères)",
            font=("Arial", 10),
            fg="#666666",
            justify=tk.CENTER
        )
        info_label.pack(pady=10)
        
        # Frame pour les champs
        fields_frame = tk.Frame(self.dialog)
        fields_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Mot de passe
        tk.Label(fields_frame, text="Nouveau mot de passe maître:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.password_entry = tk.Entry(fields_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Confirmation
        tk.Label(fields_frame, text="Confirmez le mot de passe:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.confirm_entry = tk.Entry(fields_frame, show="*", font=("Arial", 12))
        self.confirm_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Force du mot de passe
        self.strength_label = tk.Label(fields_frame, text="Force: ", font=("Arial", 9))
        self.strength_label.pack(anchor="w")
        
        self.password_entry.bind('<KeyRelease>', self.check_strength)
        
        # Boutons
        buttons_frame = tk.Frame(self.dialog)
        buttons_frame.pack(pady=20)
        
        tk.Button(
            buttons_frame,
            text="Créer",
            command=self.create_master,
            bg="#2E86AB",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Annuler",
            command=self.cancel,
            bg="#A13333",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        self.password_entry.focus()
        
    def check_strength(self, event=None):
        """Vérifier la force du mot de passe"""
        password = self.password_entry.get()
        
        if not password:
            self.strength_label.config(text="Force: ", fg="black")
            return
        
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("8+ caractères")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("majuscules")
            
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("minuscules")
            
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("chiffres")
            
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            feedback.append("symboles")
        
        if score <= 2:
            strength_text = "Force: FAIBLE"
            color = "red"
        elif score <= 3:
            strength_text = "Force: MOYEN"
            color = "orange"
        elif score <= 4:
            strength_text = "Force: BON"
            color = "blue"
        else:
            strength_text = "Force: EXCELLENT"
            color = "green"
        
        if feedback:
            strength_text += f" (manque: {', '.join(feedback)})"
        
        self.strength_label.config(text=strength_text, fg=color)
        
    def create_master(self):
        """Créer le mot de passe maître"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password or not confirm:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        if password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
            return
        
        if len(password) < 8:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 8 caractères")
            return
        
        # Créer le gestionnaire et configurer le mot de passe maître
        try:
            manager = GestionnaireMDP()
            if manager.setup_master_password(password):
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible de configurer le mot de passe maître")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la configuration: {str(e)}")
        
    def cancel(self):
        """Annuler la création"""
        self.result = False
        self.dialog.destroy()

class PasswordDialog:
    """Dialogue d'ajout/édition de mot de passe"""
    
    def __init__(self, parent, manager, password_data=None):
        self.parent = parent
        self.manager = manager
        self.password_data = password_data
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau mot de passe" if not password_data else "Modifier le mot de passe")
        self.dialog.geometry("500x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"500x550+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Titre
        title = "Nouveau mot de passe" if not self.password_data else "Modifier le mot de passe"
        title_label = tk.Label(
            self.dialog, 
            text=f"🔑 {title}", 
            font=("Arial", 16, "bold"),
            fg="#2E86AB"
        )
        title_label.pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Titre
        tk.Label(main_frame, text="Titre:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.title_entry = tk.Entry(main_frame, font=("Arial", 11))
        self.title_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Nom d'utilisateur
        tk.Label(main_frame, text="Nom d'utilisateur:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.username_entry = tk.Entry(main_frame, font=("Arial", 11))
        self.username_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Mot de passe avec générateur
        password_frame = tk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(password_frame, text="Mot de passe:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        password_input_frame = tk.Frame(password_frame)
        password_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.password_entry = tk.Entry(password_input_frame, font=("Arial", 11), show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            password_input_frame,
            text="👁",
            command=self.toggle_password_visibility,
            width=3
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(
            password_input_frame,
            text="🎲",
            command=self.generate_password,
            width=3
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # URL
        tk.Label(main_frame, text="URL:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.url_entry = tk.Entry(main_frame, font=("Arial", 11))
        self.url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Catégorie
        tk.Label(main_frame, text="Catégorie:", font=("Arial", 10, "bold")).pack(anchor="w")
        categories = ["Personnel", "Travail", "Réseaux Sociaux", "Email", "Banque", "Streaming", "Autre"]
        self.category_combo = ttk.Combobox(main_frame, values=categories, font=("Arial", 11))
        self.category_combo.pack(fill=tk.X, pady=(5, 10))
        self.category_combo.set("Autre")
        
        # Notes
        tk.Label(main_frame, text="Notes:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.notes_text = ScrolledText(main_frame, height=4, font=("Arial", 10))
        self.notes_text.pack(fill=tk.X, pady=(5, 15))
        
        # Boutons
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            buttons_frame,
            text="Sauvegarder",
            command=self.save,
            bg="#2E86AB",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            buttons_frame,
            text="Annuler",
            command=self.cancel,
            bg="#A13333",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Remplir les champs si modification
        if self.password_data:
            self.fill_fields()
        
        self.title_entry.focus()
        
    def fill_fields(self):
        """Remplir les champs avec les données existantes"""
        self.title_entry.insert(0, self.password_data.get('title', ''))
        self.username_entry.insert(0, self.password_data.get('username', ''))
        self.password_entry.insert(0, self.password_data.get('password', ''))
        self.url_entry.insert(0, self.password_data.get('url', ''))
        self.category_combo.set(self.password_data.get('category', 'Autre'))
        self.notes_text.insert('1.0', self.password_data.get('notes', ''))
        
    def toggle_password_visibility(self):
        """Basculer la visibilité du mot de passe"""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
            
    def generate_password(self):
        """Générer un nouveau mot de passe"""
        generator_dialog = PasswordGeneratorDialog(self.dialog, self.manager)
        if generator_dialog.result:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, generator_dialog.result)
            
    def save(self):
        """Sauvegarder le mot de passe"""
        title = self.title_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        url = self.url_entry.get().strip()
        category = self.category_combo.get()
        notes = self.notes_text.get('1.0', tk.END).strip()
        
        if not title:
            messagebox.showerror("Erreur", "Le titre est obligatoire")
            return
            
        if not password:
            messagebox.showerror("Erreur", "Le mot de passe est obligatoire")
            return
        
        try:
            if self.password_data:
                # Modification
                success = self.manager.update_password(
                    self.password_data['id'],
                    title=title,
                    username=username,
                    password=password,
                    url=url,
                    category=category,
                    notes=notes
                )
            else:
                # Création
                success = self.manager.add_password(
                    title=title,
                    username=username,
                    password=password,
                    url=url,
                    category=category,
                    notes=notes
                )
            
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible de sauvegarder le mot de passe")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
            
    def cancel(self):
        """Annuler l'opération"""
        self.result = False
        self.dialog.destroy()

class PasswordGeneratorDialog:
    """Dialogue de génération de mot de passe"""
    
    def __init__(self, parent, manager):
        self.parent = parent
        self.manager = manager
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Générateur de Mots de Passe")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")
        
        self.setup_ui()
        self.generate_preview()
        
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Titre
        title_label = tk.Label(
            self.dialog, 
            text="🎲 Générateur de Mots de Passe", 
            font=("Arial", 16, "bold"),
            fg="#F18F01"
        )
        title_label.pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Longueur
        length_frame = tk.Frame(main_frame)
        length_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(length_frame, text="Longueur:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.length_var = tk.IntVar(value=16)
        self.length_scale = tk.Scale(
            length_frame,
            from_=8,
            to=32,
            orient=tk.HORIZONTAL,
            variable=self.length_var,
            command=self.generate_preview
        )
        self.length_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Options
        options_frame = tk.LabelFrame(main_frame, text="Options", font=("Arial", 10, "bold"))
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.include_uppercase = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Majuscules (A-Z)",
            variable=self.include_uppercase,
            command=self.generate_preview,
            font=("Arial", 10)
        ).pack(anchor="w", padx=10, pady=2)
        
        self.include_lowercase = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Minuscules (a-z)",
            variable=self.include_lowercase,
            command=self.generate_preview,
            font=("Arial", 10)
        ).pack(anchor="w", padx=10, pady=2)
        
        self.include_numbers = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Chiffres (0-9)",
            variable=self.include_numbers,
            command=self.generate_preview,
            font=("Arial", 10)
        ).pack(anchor="w", padx=10, pady=2)
        
        self.include_symbols = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Symboles (!@#$%^&*)",
            variable=self.include_symbols,
            command=self.generate_preview,
            font=("Arial", 10)
        ).pack(anchor="w", padx=10, pady=2)
        
        # Aperçu
        preview_frame = tk.LabelFrame(main_frame, text="Aperçu", font=("Arial", 10, "bold"))
        preview_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.preview_entry = tk.Entry(preview_frame, font=("Courier", 12), state='readonly')
        self.preview_entry.pack(fill=tk.X, padx=10, pady=10)
        
        # Boutons d'action
        action_frame = tk.Frame(preview_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(
            action_frame,
            text="🔄 Régénérer",
            command=self.generate_preview,
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        tk.Button(
            action_frame,
            text="📋 Copier",
            command=self.copy_preview,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Boutons principaux
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            buttons_frame,
            text="Utiliser ce mot de passe",
            command=self.use_password,
            bg="#2E86AB",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT)
        
        tk.Button(
            buttons_frame,
            text="Annuler",
            command=self.cancel,
            bg="#A13333",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=(10, 0))
        
    def generate_preview(self, event=None):
        """Générer l'aperçu du mot de passe"""
        try:
            password = self.manager.generate_password(
                length=self.length_var.get(),
                include_symbols=self.include_symbols.get(),
                include_numbers=self.include_numbers.get(),
                include_uppercase=self.include_uppercase.get(),
                include_lowercase=self.include_lowercase.get()
            )
            
            self.preview_entry.config(state='normal')
            self.preview_entry.delete(0, tk.END)
            self.preview_entry.insert(0, password)
            self.preview_entry.config(state='readonly')
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération: {str(e)}")
            
    def copy_preview(self):
        """Copier l'aperçu dans le presse-papier"""
        password = self.preview_entry.get()
        if password:
            try:
                import pyperclip
                pyperclip.copy(password)
                messagebox.showinfo("Succès", "Mot de passe copié dans le presse-papier")
            except Exception:
                # Fallback avec clipboard de tkinter
                self.dialog.clipboard_clear()
                self.dialog.clipboard_append(password)
                messagebox.showinfo("Succès", "Mot de passe copié dans le presse-papier")
            
    def use_password(self):
        """Utiliser ce mot de passe"""
        self.result = self.preview_entry.get()
        self.dialog.destroy()
        
    def cancel(self):
        """Annuler la génération"""
        self.result = None
        self.dialog.destroy()

class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestionnaire de Mots de Passe")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.manager = None
        self.session_timer = None
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
        self.authenticate()
        
        if self.manager and self.manager.is_authenticated:
            self.setup_ui()
            self.load_passwords()
            self.update_statistics()
            self.start_session_timer()
        else:
            self.root.quit()
    
    def authenticate(self):
        """Authentifier l'utilisateur"""
        self.manager = GestionnaireMDP()
        
        if not self.manager.has_master_password():
            messagebox.showinfo(
                "Première utilisation",
                "Bienvenue dans le Gestionnaire de Mots de Passe!\n"
                "Vous devez d'abord configurer un mot de passe maître."
            )
            setup_dialog = MasterPasswordSetupDialog(self.root)
            if not setup_dialog.result:
                return
        
        # Dialogue de connexion
        login_dialog = LoginDialog(self.root)
        self.root.wait_window(login_dialog.dialog)
        
        if login_dialog.result:
            if not self.manager.authenticate(login_dialog.result):
                messagebox.showerror("Erreur", "Mot de passe incorrect")
                self.authenticate()  # Recommencer
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Menu
        self.create_menu()
        
        # Barre d'outils
        toolbar = tk.Frame(self.root, bg="#E8E8E8", height=40)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        toolbar.pack_propagate(False)
        
        tk.Button(
            toolbar,
            text="➕ Nouveau",
            command=self.add_password,
            bg="#2E86AB",
            fg="white",
            font=("Arial", 9, "bold"),
            pady=5,
            padx=10
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            toolbar,
            text="✏️ Modifier",
            command=self.edit_password,
            bg="#F18F01",
            fg="white",
            font=("Arial", 9),
            pady=5,
            padx=10
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            toolbar,
            text="🗑️ Supprimer",
            command=self.delete_password,
            bg="#A13333",
            fg="white",
            font=("Arial", 9),
            pady=5,
            padx=10
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            toolbar,
            text="📋 Copier",
            command=self.copy_password,
            bg="#6B7280",
            fg="white",
            font=("Arial", 9),
            pady=5,
            padx=10
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame principal avec PanedWindow
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief="raised")
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel gauche - Liste des mots de passe
        left_frame = tk.Frame(main_paned)
        main_paned.add(left_frame, width=650)
        
        # Filtres
        filter_frame = tk.LabelFrame(left_frame, text="Filtres", font=("Arial", 10, "bold"))
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        filter_inner = tk.Frame(filter_frame)
        filter_inner.pack(fill=tk.X, padx=10, pady=5)
        
        # Recherche
        tk.Label(filter_inner, text="Recherche:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_inner, textvariable=self.search_var, font=("Arial", 9))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.filter_passwords)
        
        # Catégorie
        tk.Label(filter_inner, text="Catégorie:", font=("Arial", 9)).pack(side=tk.LEFT)
        categories = ["Toutes", "Personnel", "Travail", "Réseaux Sociaux", "Email", "Banque", "Streaming", "Autre"]
        self.category_var = tk.StringVar(value="Toutes")
        category_combo = ttk.Combobox(filter_inner, textvariable=self.category_var, values=categories, width=12, font=("Arial", 9))
        category_combo.pack(side=tk.LEFT, padx=(5, 0))
        category_combo.bind('<<ComboboxSelected>>', self.filter_passwords)
        
        # Liste des mots de passe
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview avec scrollbars
        tree_frame = tk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('title', 'username', 'url', 'category', 'created')
        self.password_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        self.password_tree.heading('title', text='Titre', command=lambda: self.sort_column('title'))
        self.password_tree.heading('username', text='Utilisateur', command=lambda: self.sort_column('username'))
        self.password_tree.heading('url', text='URL', command=lambda: self.sort_column('url'))
        self.password_tree.heading('category', text='Catégorie', command=lambda: self.sort_column('category'))
        self.password_tree.heading('created', text='Créé le', command=lambda: self.sort_column('created'))
        
        self.password_tree.column('title', width=200)
        self.password_tree.column('username', width=150)
        self.password_tree.column('url', width=150)
        self.password_tree.column('category', width=100)
        self.password_tree.column('created', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.password_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.password_tree.xview)
        
        self.password_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack du treeview et scrollbars
        self.password_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind événements
        self.password_tree.bind('<Double-1>', self.on_double_click)
        self.password_tree.bind('<Button-3>', self.show_context_menu)
        
        # Panel droit - Statistiques
        right_frame = tk.Frame(main_paned)
        main_paned.add(right_frame, width=300)
        
        stats_frame = tk.LabelFrame(right_frame, text="Statistiques", font=("Arial", 10, "bold"))
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Contenu des statistiques
        self.stats_content = tk.Frame(stats_frame)
        self.stats_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barre de statut
        self.status_bar = tk.Label(
            self.root,
            text="Prêt",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_menu(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau mot de passe", command=self.add_password, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exporter...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Menu Édition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Modifier", command=self.edit_password, accelerator="Ctrl+E")
        edit_menu.add_command(label="Supprimer", command=self.delete_password, accelerator="Delete")
        edit_menu.add_command(label="Copier le mot de passe", command=self.copy_password, accelerator="Ctrl+C")
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Générateur de mots de passe", command=self.show_password_generator)
        tools_menu.add_command(label="Statistiques", command=self.show_statistics)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Raccourcis clavier
        self.root.bind('<Control-n>', lambda e: self.add_password())
        self.root.bind('<Control-e>', lambda e: self.edit_password())
        self.root.bind('<Control-c>', lambda e: self.copy_password())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Delete>', lambda e: self.delete_password())
        
    def load_passwords(self):
        """Charger la liste des mots de passe"""
        # Effacer le contenu existant
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
        
        try:
            # Filtres
            search_term = self.search_var.get() if hasattr(self, 'search_var') else None
            category = self.category_var.get() if hasattr(self, 'category_var') and self.category_var.get() != "Toutes" else None
            
            passwords = self.manager.list_passwords(category=category, search_term=search_term)
            
            for pwd in passwords:
                # Formatage de la date
                created_date = pwd.get('created_at', '')
                if created_date:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_date)
                        created_date = dt.strftime('%d/%m/%Y')
                    except:
                        pass
                
                self.password_tree.insert('', 'end', values=(
                    pwd.get('title', ''),
                    pwd.get('username', ''),
                    pwd.get('url', ''),
                    pwd.get('category', ''),
                    created_date
                ), tags=(pwd.get('id', ''),))
            
            # Mettre à jour la barre de statut
            count = len(passwords)
            self.status_bar.config(text=f"{count} mot(s) de passe affiché(s)")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def filter_passwords(self, event=None):
        """Filtrer la liste des mots de passe"""
        self.load_passwords()
    
    def sort_column(self, col):
        """Trier par colonne"""
        # Simple tri - peut être amélioré
        self.load_passwords()
    
    def get_selected_password_id(self):
        """Obtenir l'ID du mot de passe sélectionné"""
        selection = self.password_tree.selection()
        if selection:
            item = selection[0]
            return self.password_tree.item(item)['tags'][0]
        return None
    
    def add_password(self):
        """Ajouter un nouveau mot de passe"""
        dialog = PasswordDialog(self.root, self.manager)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_passwords()
            self.update_statistics()
    
    def edit_password(self):
        """Modifier le mot de passe sélectionné"""
        password_id = self.get_selected_password_id()
        if not password_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un mot de passe à modifier")
            return
        
        # Récupérer les données complètes
        password_data = self.manager.get_password(password_id)
        if password_data:
            dialog = PasswordDialog(self.root, self.manager, password_data)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                self.load_passwords()
                self.update_statistics()
    
    def delete_password(self):
        """Supprimer le mot de passe sélectionné"""
        password_id = self.get_selected_password_id()
        if not password_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un mot de passe à supprimer")
            return
        
        # Récupérer le titre pour confirmation
        password_data = self.manager.get_password(password_id)
        if not password_data:
            return
        
        if messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer '{password_data['title']}'?",
            icon='warning'
        ):
            if self.manager.delete_password(password_id):
                self.load_passwords()
                self.update_statistics()
                self.status_bar.config(text="Mot de passe supprimé")
    
    def copy_password(self):
        """Copier le mot de passe dans le presse-papier"""
        password_id = self.get_selected_password_id()
        if not password_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un mot de passe à copier")
            return
        
        if self.manager.copy_to_clipboard(password_id):
            self.status_bar.config(text="Mot de passe copié dans le presse-papier")
    
    def on_double_click(self, event):
        """Gérer le double-clic sur un élément"""
        self.copy_password()
    
    def show_context_menu(self, event):
        """Afficher le menu contextuel"""
        # Simple implementation
        pass
    
    def show_password_generator(self):
        """Afficher le générateur de mots de passe"""
        generator_dialog = PasswordGeneratorDialog(self.root, self.manager)
        if generator_dialog.result:
            messagebox.showinfo("Générateur", f"Mot de passe généré: {generator_dialog.result}")
    
    def update_statistics(self):
        """Mettre à jour les statistiques"""
        if not self.manager.check_session():
            return
        
        try:
            stats = self.manager.get_statistics()
            if stats:
                # Effacer le contenu existant
                for widget in self.stats_content.winfo_children():
                    widget.destroy()
                
                # Total
                total_label = tk.Label(
                    self.stats_content,
                    text=f"📊 Total: {stats['total_passwords']} mots de passe",
                    font=("Arial", 11, "bold"),
                    fg="#2E86AB"
                )
                total_label.pack(anchor="w", pady=(0, 10))
                
                # Par catégorie
                if stats['by_category']:
                    cat_label = tk.Label(
                        self.stats_content,
                        text="📁 Par catégorie:",
                        font=("Arial", 10, "bold")
                    )
                    cat_label.pack(anchor="w", pady=(0, 5))
                    
                    for cat, count in stats['by_category'][:5]:
                        cat_item = tk.Label(
                            self.stats_content,
                            text=f"  • {cat}: {count}",
                            font=("Arial", 9)
                        )
                        cat_item.pack(anchor="w")
                
                # Plus accessés
                if stats['most_accessed']:
                    access_label = tk.Label(
                        self.stats_content,
                        text="🔥 Plus utilisés:",
                        font=("Arial", 10, "bold")
                    )
                    access_label.pack(anchor="w", pady=(15, 5))
                    
                    for title, count in stats['most_accessed'][:3]:
                        access_item = tk.Label(
                            self.stats_content,
                            text=f"  • {title}: {count} accès",
                            font=("Arial", 9)
                        )
                        access_item.pack(anchor="w")
                
                # Répartition par âge
                if stats['age_distribution']:
                    age_label = tk.Label(
                        self.stats_content,
                        text="⏰ Par ancienneté:",
                        font=("Arial", 10, "bold")
                    )
                    age_label.pack(anchor="w", pady=(15, 5))
                    
                    age_dist = stats['age_distribution']
                    age_items = [
                        (f"Récents (< 30j): {age_dist['recent']}", "#4CAF50"),
                        (f"Moyens (30-90j): {age_dist['medium']}", "#FF9800"),
                        (f"Anciens (> 90j): {age_dist['old']}", "#F44336")
                    ]
                    
                    for text, color in age_items:
                        age_item = tk.Label(
                            self.stats_content,
                            text=f"  • {text}",
                            font=("Arial", 9),
                            fg=color
                        )
                        age_item.pack(anchor="w")
                        
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques: {e}")
    
    def show_statistics(self):
        """Afficher les statistiques détaillées"""
        self.update_statistics()
        messagebox.showinfo("Statistiques", "Statistiques mises à jour dans le panneau de droite")
    
    def export_data(self):
        """Exporter les données"""
        filepath = filedialog.asksaveasfilename(
            title="Exporter les données",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filepath:
            include_passwords = messagebox.askyesno(
                "Options d'export",
                "Voulez-vous inclure les mots de passe dans l'export?\n\n"
                "⚠️ ATTENTION: Ceci peut être dangereux si le fichier\n"
                "tombe entre de mauvaises mains.",
                icon='warning'
            )
            
            if self.manager.export_data(filepath, include_passwords):
                messagebox.showinfo("Succès", f"Données exportées vers:\n{filepath}")
    
    def show_about(self):
        """Afficher les informations de l'application"""
        about_text = """🔐 Gestionnaire de Mots de Passe
Version 2.0 - Interface Tkinter

Application sécurisée pour la gestion de mots de passe
avec chiffrement AES-256 et authentification maître.

Fonctionnalités:
• Chiffrement AES-256 avec Fernet
• Génération de mots de passe sécurisés
• Catégorisation flexible
• Interface intuitive
• Export/Import sécurisé
• Statistiques d'utilisation

Développé pour la cybersécurité et la protection des données."""
        
        messagebox.showinfo("À propos", about_text)
    
    def start_session_timer(self):
        """Démarrer le timer de session"""
        if self.session_timer:
            self.session_timer.cancel()
        
        # Vérifier la session toutes les minutes
        self.session_timer = Timer(60.0, self.check_session)
        self.session_timer.start()
    
    def check_session(self):
        """Vérifier la session périodiquement"""
        if not self.manager.check_session():
            messagebox.showwarning(
                "Session expirée",
                "Votre session a expiré pour des raisons de sécurité.\n"
                "Vous allez être déconnecté."
            )
            self.quit_app()
        else:
            self.start_session_timer()  # Redémarrer le timer
    
    def quit_app(self):
        """Quitter l'application"""
        if self.session_timer:
            self.session_timer.cancel()
        
        if self.manager:
            self.manager.logout()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Lancer l'application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

def main():
    """Point d'entrée de l'application GUI"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()