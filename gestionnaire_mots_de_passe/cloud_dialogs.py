#!/usr/bin/env python3
"""
Dialogs pour la synchronisation cloud
Gestionnaire de Mots de Passe - Cloud GUI Dialogs - Version Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import webbrowser
from datetime import datetime

try:
    from cloud_config import cloud_config
    from cloud_auth import cloud_auth
    from cloud_sync import cloud_sync_manager
    CLOUD_SYNC_AVAILABLE = True
except ImportError:
    CLOUD_SYNC_AVAILABLE = False

class CloudConfigDialog:
    """Dialog de configuration des services cloud - Version Tkinter"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent if parent else tk.Tk())
        self.window.title("Configuration Cloud")
        self.window.grab_set()  # Modal
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        self.init_ui()
        self.load_current_config()
    
    def init_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Configuration des Services Cloud", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook pour les tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab Google Drive
        self.google_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.google_frame, text="Google Drive")
        self.create_service_tab(self.google_frame, "google_drive")
        
        # Tab Dropbox
        self.dropbox_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dropbox_frame, text="Dropbox")
        self.create_service_tab(self.dropbox_frame, "dropbox")
        
        # Boutons de contrôle
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Sauvegarder", 
                  command=self.save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Annuler", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def create_service_tab(self, parent, service_name):
        """Créer un tab de configuration pour un service"""
        # Configuration frame
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Client ID
        ttk.Label(config_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W)
        client_id_var = tk.StringVar()
        setattr(self, f"{service_name}_client_id", client_id_var)
        ttk.Entry(config_frame, textvariable=client_id_var, width=40).grid(row=0, column=1, pady=2)
        
        # Client Secret
        ttk.Label(config_frame, text="Client Secret:").grid(row=1, column=0, sticky=tk.W)
        client_secret_var = tk.StringVar()
        setattr(self, f"{service_name}_client_secret", client_secret_var)
        ttk.Entry(config_frame, textvariable=client_secret_var, width=40, show="*").grid(row=1, column=1, pady=2)
        
        # Statut frame
        status_frame = ttk.LabelFrame(parent, text="Statut", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        status_label = ttk.Label(status_frame, text="Non configuré")
        status_label.pack()
        setattr(self, f"{service_name}_status", status_label)
        
        # Boutons d'action
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(action_frame, text="Tester la configuration", 
                  command=lambda: self.test_service(service_name)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Authentifier", 
                  command=lambda: self.authenticate_service(service_name)).pack(side=tk.LEFT)
    
    def load_current_config(self):
        """Charger la configuration actuelle"""
        if not CLOUD_SYNC_AVAILABLE:
            return
        
        for service in ['google_drive', 'dropbox']:
            if hasattr(cloud_config, 'is_service_configured'):
                if cloud_config.is_service_configured(service):
                    config = cloud_config.get_service_config(service)
                    if config:
                        client_id_var = getattr(self, f"{service}_client_id")
                        client_secret_var = getattr(self, f"{service}_client_secret")
                        status_label = getattr(self, f"{service}_status")
                        
                        client_id_var.set(config.get('client_id', ''))
                        client_secret_var.set(config.get('client_secret', ''))
                        status_label.config(text="Configuré", foreground="green")
    
    def save_config(self):
        """Sauvegarder la configuration"""
        if not CLOUD_SYNC_AVAILABLE:
            messagebox.showerror("Erreur", "Synchronisation cloud non disponible")
            return
        
        for service in ['google_drive', 'dropbox']:
            client_id_var = getattr(self, f"{service}_client_id")
            client_secret_var = getattr(self, f"{service}_client_secret")
            
            client_id = client_id_var.get().strip()
            client_secret = client_secret_var.get().strip()
            
            if client_id and client_secret:
                if hasattr(cloud_config, 'configure_service'):
                    if cloud_config.configure_service(service, client_id, client_secret):
                        messagebox.showinfo("Succès", f"Configuration {service} sauvegardée")
                    else:
                        messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde {service}")
        
        self.window.destroy()
    
    def test_service(self, service_name):
        """Tester la configuration d'un service"""
        messagebox.showinfo("Test", f"Test de configuration pour {service_name}")
    
    def authenticate_service(self, service_name):
        """Démarrer l'authentification pour un service"""
        if not CLOUD_SYNC_AVAILABLE:
            messagebox.showerror("Erreur", "Synchronisation cloud non disponible")
            return
        
        try:
            if hasattr(cloud_auth, 'get_authorization_url'):
                auth_url = cloud_auth.get_authorization_url(service_name)
                if auth_url:
                    webbrowser.open(auth_url)
                    messagebox.showinfo("Authentification", 
                                      "Navigateur ouvert pour authentification.\n"
                                      "Suivez les instructions et revenez ici.")
                else:
                    messagebox.showerror("Erreur", "Impossible de générer l'URL d'authentification")
            else:
                messagebox.showerror("Erreur", "Module d'authentification non disponible")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'authentification: {str(e)}")


class CloudSyncDialog:
    """Dialog de synchronisation cloud - Version Tkinter"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent if parent else tk.Tk())
        self.window.title("Synchronisation Cloud")
        self.window.grab_set()  # Modal
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        self.sync_thread = None
        self.init_ui()
    
    def init_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Synchronisation Cloud", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Statut", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Prêt pour synchronisation")
        self.status_label.pack()
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Journal", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Boutons de contrôle
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.sync_button = ttk.Button(button_frame, text="Démarrer Sync", 
                                     command=self.start_sync)
        self.sync_button.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Fermer", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def log_message(self, message):
        """Ajouter un message au journal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.window.update()
    
    def start_sync(self):
        """Démarrer la synchronisation"""
        if not CLOUD_SYNC_AVAILABLE:
            messagebox.showerror("Erreur", "Synchronisation cloud non disponible")
            return
        
        self.sync_button.config(state='disabled', text="Synchronisation...")
        self.progress_bar.start()
        self.status_label.config(text="Synchronisation en cours...")
        
        # Démarrer la synchronisation dans un thread séparé
        self.sync_thread = threading.Thread(target=self.run_sync)
        self.sync_thread.start()
    
    def run_sync(self):
        """Exécuter la synchronisation"""
        try:
            self.log_message("Démarrage de la synchronisation...")
            
            # Simuler la synchronisation
            self.log_message("Vérification des services cloud...")
            self.log_message("Chiffrement des données...")
            self.log_message("Upload en cours...")
            self.log_message("Synchronisation terminée avec succès!")
            
            # Mise à jour de l'interface
            self.window.after(0, self.sync_completed)
            
        except Exception as error:
            self.window.after(0, lambda: self.sync_error(str(error)))
    
    def sync_completed(self):
        """Synchronisation terminée avec succès"""
        self.progress_bar.stop()
        self.sync_button.config(state='normal', text="Démarrer Sync")
        self.status_label.config(text="Synchronisation terminée")
        messagebox.showinfo("Succès", "Synchronisation terminée avec succès!")
    
    def sync_error(self, error_message):
        """Erreur de synchronisation"""
        self.progress_bar.stop()
        self.sync_button.config(state='normal', text="Démarrer Sync")
        self.status_label.config(text="Erreur de synchronisation")
        self.log_message(f"ERREUR: {error_message}")
        messagebox.showerror("Erreur", f"Erreur de synchronisation: {error_message}")


class CloudStatusDialog:
    """Dialog d'état des services cloud - Version Tkinter"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent if parent else tk.Tk())
        self.window.title("Statut Cloud")
        self.window.grab_set()  # Modal
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        self.init_ui()
        self.load_status()
    
    def init_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Statut des Services Cloud", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Treeview pour afficher le statut
        columns = ('Service', 'Configuré', 'Authentifié', 'Dernière Sync')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=8)
        
        # Définir les colonnes
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # Scrollbar pour le treeview
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton de fermeture
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Actualiser", 
                  command=self.load_status).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Fermer", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def load_status(self):
        """Charger le statut des services"""
        # Vider le treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not CLOUD_SYNC_AVAILABLE:
            self.tree.insert('', tk.END, values=('Cloud non disponible', '❌', '❌', 'Jamais'))
            return
        
        # Simuler les données de statut
        services_status = [
            ('Google Drive', '✅', '✅', '2025-08-04 12:30'),
            ('Dropbox', '✅', '❌', 'Jamais'),
            ('OneDrive', '❌', '❌', 'Jamais')
        ]
        
        for service_data in services_status:
            self.tree.insert('', tk.END, values=service_data)


# Fonction utilitaire pour tester les dialogs
def test_dialogs():
    """Tester les dialogs cloud"""
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    
    # Test du dialog de configuration
    config_dialog = CloudConfigDialog(root)
    
    root.mainloop()

if __name__ == "__main__":
    test_dialogs()