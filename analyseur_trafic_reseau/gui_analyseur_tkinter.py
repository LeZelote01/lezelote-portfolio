#!/usr/bin/env python3
"""
Interface Graphique Tkinter pour l'Analyseur de Trafic Réseau
GUI moderne avec visualisations temps réel et gestion de base de données
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from analyseur_trafic import AnalyseurTrafic
from database_manager import DatabaseManager
from ml_detector import MLAnomalyDetector

class AnalyseurGUI:
    """Interface graphique principale pour l'analyseur de trafic"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("🌐 Analyseur de Trafic Réseau - Interface Avancée")
        self.master.geometry("1400x900")
        
        # Variables
        self.analyseur_thread = None
        self.db_manager = DatabaseManager()
        self.ml_detector = MLAnomalyDetector()
        self.current_session_id = None
        self.is_capturing = False
        
        # Configuration du style
        self.setup_style()
        
        # Initialiser l'interface
        self.create_widgets()
        
        # Timer pour les mises à jour automatiques
        self.update_database_stats()
        self.master.after(5000, self.update_database_stats)  # Mise à jour toutes les 5 secondes
        
        # Charger les données initiales
        self.load_sessions_list()
        
    def setup_style(self):
        """Configurer le style de l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs personnalisées
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Stats.TLabel', font=('Arial', 12, 'bold'), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='#e74c3c')
        style.configure('Success.TButton', background='#27ae60')
        style.configure('Danger.TButton', background='#e74c3c')
        
    def create_widgets(self):
        """Créer tous les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # PanedWindow principal
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Panel de contrôle (gauche)
        control_frame = self.create_control_panel()
        main_paned.add(control_frame, weight=1)
        
        # Zone principale avec notebook (centre)
        notebook_frame = self.create_notebook()
        main_paned.add(notebook_frame, weight=4)
        
    def create_control_panel(self):
        """Créer le panel de contrôle"""
        frame = ttk.LabelFrame(self.master, text="⚙️ Configuration", padding=10)
        
        # Configuration de capture
        capture_frame = ttk.LabelFrame(frame, text="📡 Capture Configuration", padding=10)
        capture_frame.pack(fill=tk.X, pady=5)
        
        # Interface
        ttk.Label(capture_frame, text="Interface:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.interface_var = tk.StringVar(value="eth0")
        interface_combo = ttk.Combobox(capture_frame, textvariable=self.interface_var, 
                                     values=["eth0", "wlan0", "lo", "any"], state="readonly")
        interface_combo.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5,0))
        
        # Durée
        ttk.Label(capture_frame, text="Durée (s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.duration_var = tk.IntVar(value=60)
        duration_spin = ttk.Spinbox(capture_frame, from_=10, to=3600, textvariable=self.duration_var, width=10)
        duration_spin.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(5,0))
        
        # Max paquets
        ttk.Label(capture_frame, text="Max paquets:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.packets_var = tk.IntVar(value=1000)
        packets_spin = ttk.Spinbox(capture_frame, from_=100, to=10000, textvariable=self.packets_var, width=10)
        packets_spin.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=(5,0))
        
        
        capture_frame.columnconfigure(1, weight=1)
        
        # Boutons de contrôle
        controls_frame = ttk.LabelFrame(frame, text="🎮 Contrôles", padding=10)
        controls_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(controls_frame, text="▶️ Démarrer Capture", 
                                   command=self.start_capture, style='Success.TButton')
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.stop_btn = ttk.Button(controls_frame, text="⏹️ Arrêter Capture", 
                                  command=self.stop_capture, state=tk.DISABLED, style='Danger.TButton')
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        self.save_btn = ttk.Button(controls_frame, text="💾 Sauvegarder Session", 
                                  command=self.save_current_session, state=tk.DISABLED)
        self.save_btn.pack(fill=tk.X, pady=2)
        
        # Statistiques en temps réel
        stats_frame = ttk.LabelFrame(frame, text="📊 Statistiques Live", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.packets_label = ttk.Label(stats_frame, text="Paquets: 0", style='Stats.TLabel')
        self.packets_label.pack(anchor=tk.W)
        
        self.bytes_label = ttk.Label(stats_frame, text="Bytes: 0", style='Stats.TLabel')
        self.bytes_label.pack(anchor=tk.W)
        
        self.anomalies_label = ttk.Label(stats_frame, text="Anomalies: 0", style='Stats.TLabel')
        self.anomalies_label.pack(anchor=tk.W)
        
        ttk.Label(stats_frame, text="Progression:").pack(anchor=tk.W, pady=(10,2))
        self.progress_bar = ttk.Progressbar(stats_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        # Base de données
        db_frame = ttk.LabelFrame(frame, text="🗄️ Base de Données", padding=10)
        db_frame.pack(fill=tk.X, pady=5)
        
        self.db_stats_label = ttk.Label(db_frame, text="Sessions: 0\nPaquets totaux: 0")
        self.db_stats_label.pack(anchor=tk.W)
        
        cleanup_btn = ttk.Button(db_frame, text="🧹 Nettoyer Anciennes", command=self.cleanup_old_sessions)
        cleanup_btn.pack(fill=tk.X, pady=2)
        
        export_btn = ttk.Button(db_frame, text="📤 Export Complet", command=self.export_all_data)
        export_btn.pack(fill=tk.X, pady=2)
        
        return frame
    
    def create_notebook(self):
        """Créer le notebook avec onglets"""
        notebook = ttk.Notebook(self.master)
        
        # Onglet Dashboard Live
        live_frame = self.create_live_dashboard()
        notebook.add(live_frame, text="📊 Dashboard Live")
        
        # Onglet Historique
        history_frame = self.create_history_tab()
        notebook.add(history_frame, text="📚 Historique")
        
        # Onglet Logs
        logs_frame = self.create_logs_tab()
        notebook.add(logs_frame, text="📝 Logs")
        
        # Onglet ML Analytics
        ml_frame = self.create_ml_tab()
        notebook.add(ml_frame, text="🤖 ML Analytics")
        
        return notebook
    
    def create_live_dashboard(self):
        """Créer le dashboard temps réel"""
        frame = ttk.Frame(self.master)
        
        # PanedWindow pour séparer graphiques et tableau
        paned = ttk.PanedWindow(frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pour les graphiques
        charts_frame = ttk.Frame(paned)
        paned.add(charts_frame, weight=3)
        
        # Configuration matplotlib pour thème sombre
        plt.style.use('dark_background')
        
        # Graphiques
        self.fig = Figure(figsize=(12, 6), facecolor='#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Créer les sous-graphiques
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)
        
        # Initialiser les graphiques vides
        self.init_charts()
        
        # Frame pour la table des paquets
        table_frame = ttk.LabelFrame(paned, text="📦 Paquets Récents", padding=5)
        paned.add(table_frame, weight=1)
        
        # Tableau des paquets
        columns = ("Timestamp", "Protocole", "IP Source", "IP Dest", "Port Src", "Port Dst", "Taille")
        self.packets_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.packets_tree.heading(col, text=col)
            self.packets_tree.column(col, width=100)
        
        # Scrollbar pour le tableau
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.packets_tree.yview)
        self.packets_tree.configure(yscrollcommand=scrollbar.set)
        
        self.packets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame
    
    def create_history_tab(self):
        """Créer l'onglet historique"""
        frame = ttk.Frame(self.master)
        
        # Contrôles de l'historique
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = ttk.Button(controls_frame, text="🔄 Actualiser", command=self.load_sessions_list)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = ttk.Button(controls_frame, text="🗑️ Supprimer Session", command=self.delete_selected_session)
        delete_btn.pack(side=tk.RIGHT, padx=2)
        
        # Table des sessions
        sessions_frame = ttk.Frame(frame)
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Date", "Interface", "Durée", "Paquets", "Bytes", "Anomalies", "Description")
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=120)
        
        # Scrollbars
        sessions_scrollbar_y = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        sessions_scrollbar_x = ttk.Scrollbar(sessions_frame, orient=tk.HORIZONTAL, command=self.sessions_tree.xview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar_y.set, xscrollcommand=sessions_scrollbar_x.set)
        
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        sessions_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind selection event
        self.sessions_tree.bind('<<TreeviewSelect>>', self.on_session_selected)
        
        # Détails de la session
        details_frame = ttk.LabelFrame(frame, text="📋 Détails de la Session", padding=5)
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.session_details = scrolledtext.ScrolledText(details_frame, height=6, wrap=tk.WORD)
        self.session_details.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_logs_tab(self):
        """Créer l'onglet des logs"""
        frame = ttk.Frame(self.master)
        
        # Contrôles des logs
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        clear_btn = ttk.Button(controls_frame, text="🗑️ Vider Logs", command=self.clear_logs)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        save_logs_btn = ttk.Button(controls_frame, text="💾 Sauvegarder Logs", command=self.save_logs)
        save_logs_btn.pack(side=tk.RIGHT, padx=2)
        
        # Zone de logs
        logs_frame = ttk.Frame(frame)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, font=('Courier', 10))
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_ml_tab(self):
        """Créer l'onglet ML Analytics"""
        frame = ttk.Frame(self.master)
        
        # Configuration ML
        config_frame = ttk.LabelFrame(frame, text="🤖 Configuration ML", padding=10)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Seuil de détection
        ttk.Label(config_frame, text="Seuil d'anomalie:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.threshold_var = tk.DoubleVar(value=0.1)
        threshold_scale = ttk.Scale(config_frame, from_=0.01, to=0.5, variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5,0))
        self.threshold_label = ttk.Label(config_frame, text="0.1")
        self.threshold_label.grid(row=0, column=2, pady=2, padx=(5,0))
        
        # Bind pour mettre à jour le label
        threshold_scale.configure(command=self.update_threshold_label)
        
        # Retrain model
        retrain_btn = ttk.Button(config_frame, text="🔄 Réentraîner Modèle", command=self.retrain_ml_model)
        retrain_btn.grid(row=1, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Statistiques ML
        stats_frame = ttk.LabelFrame(frame, text="📊 Statistiques ML", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.ml_stats_text = scrolledtext.ScrolledText(stats_frame, height=20, wrap=tk.WORD)
        self.ml_stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialiser les stats ML
        self.update_ml_stats()
        
        return frame
    
    def init_charts(self):
        """Initialiser les graphiques vides"""
        # Graphique des protocoles (camembert)
        self.ax1.set_title('Distribution des Protocoles', color='white')
        
        # Graphique des IPs (barres)
        self.ax2.set_title('Top 10 IPs Sources', color='white')
        self.ax2.set_ylabel('Paquets', color='white')
        
        # Graphique des ports (barres)
        self.ax3.set_title('Top 10 Ports', color='white')
        self.ax3.set_ylabel('Paquets', color='white')
        
        # Graphique temporel
        self.ax4.set_title('Évolution Temporelle', color='white')
        self.ax4.set_ylabel('Paquets/min', color='white')
        
        # Améliorer l'apparence
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def start_capture(self):
        """Démarrer la capture"""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        
        # Configuration
        interface = self.interface_var.get()
        duration = self.duration_var.get()
        max_packets = self.packets_var.get()
        demo_mode = False  # Production mode only
        
        # Mettre à jour l'interface
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        
        # Démarrer le thread
        self.analyseur_thread = threading.Thread(
            target=self.capture_worker,
            args=(interface, duration, max_packets, demo_mode),
            daemon=True
        )
        self.analyseur_thread.start()
        
        self.add_log_message("🎯 Capture démarrée", "info")
    
    def stop_capture(self):
        """Arrêter la capture"""
        self.is_capturing = False
        self.on_capture_finished()
    
    def capture_worker(self, interface, duration, max_packets, demo_mode):
        """Worker thread pour la capture"""
        try:
            self.add_log_message(f"🎯 Démarrage analyse sur {interface}", "info")
            
            # Initialiser l'analyseur
            self.analyseur = AnalyseurTrafic(interface=interface)
            
            if demo_mode:
                # Demo mode has been removed - use demos/ folder for demonstrations
                self.add_log_message("❌ Demo mode has been disabled for production", "error")
                return
            else:
                # Capture réelle
                success = self.analyseur.start_capture(duration=duration, packet_count=max_packets)
                if not success:
                    self.add_log_message("❌ Échec de la capture", "error")
                    return
            
            packets_count = len(self.analyseur.packets) if self.analyseur.packets else 0
            self.add_log_message(f"✅ Capture terminée - {packets_count} paquets", "success")
            self.master.after_idle(self.on_capture_finished)
            
        except Exception as e:
            self.add_log_message(f"❌ Erreur: {str(e)}", "error")
        finally:
            self.is_capturing = False
    
    def update_interface(self, current, total):
        """Mettre à jour l'interface pendant la capture"""
        # Mettre à jour les statistiques
        if hasattr(self, 'analyseur') and self.analyseur:
            packets_count = len(self.analyseur.packets) if self.analyseur.packets else 0
            bytes_count = sum(p.get('length', 0) for p in self.analyseur.packets) if self.analyseur.packets else 0
            anomalies_count = len(self.analyseur.anomalies) if hasattr(self.analyseur, 'anomalies') and self.analyseur.anomalies else 0
            
            self.packets_label.config(text=f"Paquets: {packets_count:,}")
            self.bytes_label.config(text=f"Bytes: {bytes_count:,}")
            self.anomalies_label.config(text=f"Anomalies: {anomalies_count}")
            
            # Barre de progression
            progress = (current / total) * 100 if total > 0 else 0
            self.progress_bar['value'] = progress
            
            # Mettre à jour les graphiques
            self.update_charts()
            
            # Mettre à jour la table des paquets (derniers 50)
            self.update_packets_table()
    
    def update_charts(self):
        """Mettre à jour les graphiques en temps réel"""
        if not hasattr(self, 'analyseur') or not self.analyseur:
            return
        
        # Nettoyer les axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
            ax.set_facecolor('#2b2b2b')
        
        # Graphique des protocoles
        if hasattr(self.analyseur, 'protocol_stats') and self.analyseur.protocol_stats:
            protocols = dict(self.analyseur.protocol_stats.most_common(6))
            if protocols:
                colors = plt.cm.Set3(np.linspace(0, 1, len(protocols)))
                wedges, texts, autotexts = self.ax1.pie(protocols.values(), labels=protocols.keys(), 
                                                       autopct='%1.1f%%', colors=colors)
                for text in texts + autotexts:
                    text.set_color('white')
        
        self.ax1.set_title('Distribution des Protocoles', color='white')
        
        # Graphique des IPs
        if hasattr(self.analyseur, 'ip_stats') and self.analyseur.ip_stats:
            top_ips = dict(self.analyseur.ip_stats.most_common(10))
            if top_ips:
                self.ax2.bar(range(len(top_ips)), list(top_ips.values()), color='#3498db')
                self.ax2.set_xticks(range(len(top_ips)))
                self.ax2.set_xticklabels(list(top_ips.keys()), rotation=45, ha='right', color='white')
        
        self.ax2.set_title('Top 10 IPs Sources', color='white')
        self.ax2.set_ylabel('Paquets', color='white')
        self.ax2.tick_params(colors='white')
        
        # Graphique des ports
        if hasattr(self.analyseur, 'port_stats') and self.analyseur.port_stats:
            top_ports = dict(self.analyseur.port_stats.most_common(10))
            if top_ports:
                self.ax3.bar(range(len(top_ports)), list(top_ports.values()), color='#27ae60')
                self.ax3.set_xticks(range(len(top_ports)))
                self.ax3.set_xticklabels([str(p) for p in top_ports.keys()], rotation=45, ha='right', color='white')
        
        self.ax3.set_title('Top 10 Ports', color='white')
        self.ax3.set_ylabel('Paquets', color='white')
        self.ax3.tick_params(colors='white')
        
        # Graphique temporel (simulation)
        if hasattr(self.analyseur, 'packets') and self.analyseur.packets:
            # Grouper par minute pour simuler l'évolution temporelle
            time_data = [i for i in range(min(len(self.analyseur.packets) // 10, 60))]
            packet_counts = [10 + np.random.randint(-5, 15) for _ in time_data]
            self.ax4.plot(time_data, packet_counts, color='#e74c3c', linewidth=2)
        
        self.ax4.set_title('Évolution Temporelle', color='white')
        self.ax4.set_ylabel('Paquets/min', color='white')
        self.ax4.tick_params(colors='white')
        
        # Améliorer l'apparence
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            for spine in ax.spines.values():
                spine.set_color('white')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_packets_table(self):
        """Mettre à jour la table des paquets"""
        if not hasattr(self, 'analyseur') or not self.analyseur or not self.analyseur.packets:
            return
        
        # Vider la table
        for item in self.packets_tree.get_children():
            self.packets_tree.delete(item)
        
        # Ajouter les derniers paquets (max 50)
        recent_packets = self.analyseur.packets[-50:]
        
        for packet in recent_packets:
            timestamp = packet.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                timestamp_str = timestamp.strftime("%H:%M:%S")
            else:
                timestamp_str = str(timestamp)
            
            values = (
                timestamp_str,
                packet.get('protocol', ''),
                packet.get('src_ip', ''),
                packet.get('dst_ip', ''),
                str(packet.get('src_port', '')),
                str(packet.get('dst_port', '')),
                str(packet.get('length', 0))
            )
            
            self.packets_tree.insert('', tk.END, values=values)
    
    def on_capture_finished(self):
        """Actions à effectuer quand la capture est terminée"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        
        self.add_log_message("✅ Capture terminée", "success")
        
        # Mettre à jour les stats ML si des anomalies ont été détectées
        if hasattr(self, 'analyseur'):
            self.update_ml_stats()
    
    def save_current_session(self):
        """Sauvegarder la session actuelle"""
        if not hasattr(self, 'analyseur') or not self.analyseur:
            messagebox.showwarning("Attention", "Aucune session active à sauvegarder")
            return
        
        try:
            session_id = self.db_manager.save_capture_session(self.analyseur)
            if session_id:
                self.current_session_id = session_id
                self.add_log_message(f"💾 Session sauvegardée: {session_id}", "success")
                self.load_sessions_list()  # Actualiser la liste
                messagebox.showinfo("Succès", f"Session sauvegardée avec l'ID: {session_id}")
            else:
                messagebox.showerror("Erreur", "Échec de la sauvegarde")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def load_sessions_list(self):
        """Charger la liste des sessions depuis la base de données"""
        try:
            # Vider la table
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            sessions = self.db_manager.get_capture_sessions(50)
            
            for session in sessions:
                values = (
                    session.id[:8] + "...",
                    session.timestamp.strftime("%Y-%m-%d %H:%M"),
                    session.interface,
                    f"{session.duration:.1f}s",
                    f"{session.packets_captured:,}",
                    f"{session.bytes_captured:,}",
                    str(session.anomalies_detected),
                    session.description
                )
                
                item = self.sessions_tree.insert('', tk.END, values=values)
                # Stocker l'ID complet
                self.sessions_tree.set(item, '#0', session.id)
            
        except Exception as e:
            self.add_log_message(f"❌ Erreur chargement sessions: {str(e)}", "error")
    
    def on_session_selected(self, event):
        """Quand une session est sélectionnée dans l'historique"""
        selection = self.sessions_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        session_id = self.sessions_tree.item(item, '#0')
        
        try:
            sessions = self.db_manager.get_capture_sessions(50)
            selected_session = next((s for s in sessions if s.id == session_id), None)
            
            if selected_session:
                details = f"ID: {selected_session.id}\n"
                details += f"Date: {selected_session.timestamp}\n"
                details += f"Interface: {selected_session.interface}\n"
                details += f"Durée: {selected_session.duration:.2f}s\n"
                details += f"Paquets capturés: {selected_session.packets_captured:,}\n"
                details += f"Bytes capturés: {selected_session.bytes_captured:,}\n"
                details += f"Anomalies détectées: {selected_session.anomalies_detected}\n\n"
                
                # Protocoles
                if selected_session.protocol_distribution:
                    details += "Protocoles:\n"
                    for protocol, count in selected_session.protocol_distribution.items():
                        details += f"  - {protocol}: {count}\n"
                
                self.session_details.delete(1.0, tk.END)
                self.session_details.insert(1.0, details)
        except Exception as e:
            self.add_log_message(f"❌ Erreur chargement détails: {str(e)}", "error")
    
    def delete_selected_session(self):
        """Supprimer la session sélectionnée"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une session à supprimer")
            return
        
        item = selection[0]
        session_id = self.sessions_tree.item(item, '#0')
        
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer la session {session_id[:8]}... ?"):
            try:
                if self.db_manager.delete_session(session_id):
                    self.add_log_message(f"🗑️ Session {session_id[:8]}... supprimée", "info")
                    self.load_sessions_list()
                else:
                    messagebox.showerror("Erreur", "Échec de la suppression")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def update_database_stats(self):
        """Mettre à jour les statistiques de la base de données"""
        try:
            stats = self.db_manager.get_statistics_summary()
            
            text = f"Sessions: {stats['total_sessions']}\n"
            text += f"Paquets totaux: {stats['total_packets']:,}\n"
            text += f"Bytes totaux: {stats['total_bytes']:,}\n"
            text += f"Anomalies: {stats['total_anomalies']}\n"
            text += f"Sessions récentes: {stats['recent_sessions']}"
            
            self.db_stats_label.config(text=text)
        except Exception as e:
            self.add_log_message(f"❌ Erreur stats DB: {str(e)}", "error")
        
        # Programmer la prochaine mise à jour
        self.master.after(5000, self.update_database_stats)
    
    def cleanup_old_sessions(self):
        """Nettoyer les anciennes sessions"""
        if messagebox.askyesno("Confirmation", "Supprimer les sessions de plus de 30 jours ?"):
            try:
                deleted_count = self.db_manager.cleanup_old_sessions(30)
                self.add_log_message(f"🧹 {deleted_count} anciennes sessions supprimées", "info")
                self.load_sessions_list()
                messagebox.showinfo("Nettoyage", f"{deleted_count} sessions supprimées")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du nettoyage: {str(e)}")
    
    def export_all_data(self):
        """Exporter toutes les données"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"traffic_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if file_path:
            try:
                sessions = self.db_manager.get_capture_sessions(1)
                if sessions:
                    success = self.db_manager.export_session_to_csv(sessions[0].id, file_path)
                    if success:
                        self.add_log_message(f"📤 Données exportées vers: {file_path}", "success")
                        messagebox.showinfo("Export", f"Données exportées vers:\n{file_path}")
                    else:
                        messagebox.showerror("Erreur", "Échec de l'export")
                else:
                    messagebox.showwarning("Attention", "Aucune session à exporter")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def update_threshold_label(self, value):
        """Mettre à jour le label du seuil"""
        self.threshold_label.config(text=f"{float(value):.3f}")
        # Mettre à jour le seuil du détecteur ML
        self.ml_detector.threshold = float(value)
    
    def retrain_ml_model(self):
        """Réentraîner le modèle ML"""
        try:
            self.add_log_message("🤖 Réentraînement du modèle ML...", "info")
            
            # Charger des données d'entraînement depuis la base
            sessions = self.db_manager.get_capture_sessions(10)
            training_data = []
            
            for session in sessions:
                packets = self.db_manager.get_session_packets(session.id, 100)
                for packet in packets:
                    features = self.ml_detector.extract_features({
                        'protocol': packet.protocol,
                        'src_ip': packet.src_ip,
                        'dst_ip': packet.dst_ip,
                        'src_port': packet.src_port,
                        'dst_port': packet.dst_port,
                        'length': packet.length
                    })
                    training_data.append(features)
            
            if training_data:
                self.ml_detector.train(training_data)
                self.add_log_message("✅ Modèle ML réentraîné avec succès", "success")
                self.update_ml_stats()
            else:
                self.add_log_message("⚠️ Pas assez de données pour l'entraînement", "warning")
                
        except Exception as e:
            self.add_log_message(f"❌ Erreur réentraînement ML: {str(e)}", "error")
    
    def update_ml_stats(self):
        """Mettre à jour les statistiques ML"""
        try:
            stats_text = "🤖 STATISTIQUES MACHINE LEARNING\n"
            stats_text += "=" * 50 + "\n\n"
            
            # Informations sur le modèle
            stats_text += f"Modèle utilisé: {type(self.ml_detector.model).__name__}\n"
            stats_text += f"Seuil d'anomalie: {self.ml_detector.threshold:.3f}\n"
            stats_text += f"Modèle entraîné: {'Oui' if self.ml_detector.is_trained else 'Non'}\n\n"
            
            # Statistiques des détections
            if hasattr(self, 'analyseur') and hasattr(self.analyseur, 'anomalies'):
                ml_anomalies = [a for a in self.analyseur.anomalies if 'ML' in a.get('type', '')]
                stats_text += f"Anomalies ML détectées: {len(ml_anomalies)}\n"
                
                if ml_anomalies:
                    stats_text += "\nDernières détections ML:\n"
                    for i, anomaly in enumerate(ml_anomalies[-5:], 1):
                        timestamp = anomaly.get('timestamp', datetime.now())
                        if isinstance(timestamp, datetime):
                            time_str = timestamp.strftime("%H:%M:%S")
                        else:
                            time_str = str(timestamp)
                        stats_text += f"{i}. {time_str} - {anomaly.get('source_ip', 'N/A')} - {anomaly.get('details', '')}\n"
            
            # Informations sur les features
            stats_text += f"\nFeatures utilisées:\n"
            stats_text += "- Longueur du paquet\n"
            stats_text += "- Type de protocole (encodé)\n"
            stats_text += "- Hash des IPs source/destination\n"
            stats_text += "- Ports source/destination\n\n"
            
            # Conseils d'utilisation
            stats_text += "💡 CONSEILS D'UTILISATION:\n"
            stats_text += "- Seuil bas (0.01-0.05): Plus sensible, plus de détections\n"
            stats_text += "- Seuil élevé (0.1-0.5): Moins sensible, moins de faux positifs\n"
            stats_text += "- Réentraîner régulièrement avec de nouvelles données\n"
            stats_text += "- Combiner avec les règles traditionnelles pour plus d'efficacité\n"
            
            self.ml_stats_text.delete(1.0, tk.END)
            self.ml_stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.add_log_message(f"❌ Erreur mise à jour stats ML: {str(e)}", "error")
    
    def add_log_message(self, message, level):
        """Ajouter un message de log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.logs_text.insert(tk.END, formatted_message)
        self.logs_text.see(tk.END)
        
        # Limiter le nombre de lignes
        lines = self.logs_text.get(1.0, tk.END).split('\n')
        if len(lines) > 1000:
            self.logs_text.delete(1.0, f"{len(lines)-1000}.0")
    
    def clear_logs(self):
        """Vider les logs"""
        self.logs_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Sauvegarder les logs"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialname=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                self.add_log_message(f"💾 Logs sauvegardés: {file_path}", "success")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur sauvegarde logs: {str(e)}")

def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    
    # Configuration de la fenêtre
    root.title("🌐 Analyseur de Trafic Réseau - Interface Avancée")
    root.geometry("1400x900")
    
    # Créer l'interface
    app = AnalyseurGUI(root)
    
    # Démarrer la boucle principale
    root.mainloop()

if __name__ == "__main__":
    main()