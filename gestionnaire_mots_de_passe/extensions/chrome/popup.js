// Gestionnaire de Mots de Passe - Extension Chrome
// Popup principal pour l'interface utilisateur

class PasswordManagerPopup {
  constructor() {
    this.apiUrl = 'http://localhost:8002/api';
    this.authToken = null;
    this.passwords = [];
    this.selectedPassword = null;
    
    this.init();
  }

  async init() {
    this.bindEvents();
    await this.loadAuthToken();
    this.updateStatus();
  }

  bindEvents() {
    // Authentification
    document.getElementById('auth-btn').addEventListener('click', () => this.authenticate());
    document.getElementById('master-password').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.authenticate();
    });

    // Recherche
    document.getElementById('search-input').addEventListener('input', (e) => {
      this.searchPasswords(e.target.value);
    });
    document.getElementById('refresh-btn').addEventListener('click', () => this.refreshPasswords());

    // Actions principales
    document.getElementById('generate-btn').addEventListener('click', () => this.showGenerator());
    document.getElementById('fill-btn').addEventListener('click', () => this.fillPassword());

    // Générateur
    document.getElementById('length-slider').addEventListener('input', (e) => {
      document.getElementById('length-value').textContent = e.target.value;
    });
    document.getElementById('new-generate').addEventListener('click', () => this.generatePassword());
    document.getElementById('copy-generated').addEventListener('click', () => this.copyGenerated());
    document.getElementById('save-generated').addEventListener('click', () => this.saveGenerated());

    // Générer un mot de passe initial
    setTimeout(() => this.generatePassword(), 100);
  }

  async loadAuthToken() {
    try {
      const result = await chrome.storage.session.get(['authToken']);
      if (result.authToken) {
        this.authToken = result.authToken;
        await this.verifyAuth();
      }
    } catch (error) {
      console.error('Erreur chargement token:', error);
    }
  }

  async saveAuthToken() {
    if (this.authToken) {
      await chrome.storage.session.set({ authToken: this.authToken });
    }
  }

  async authenticate() {
    const masterPassword = document.getElementById('master-password').value;
    
    if (!masterPassword) {
      this.showError('Veuillez entrer le mot de passe maître');
      return;
    }

    try {
      const response = await fetch(`${this.apiUrl}/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ master_password: masterPassword })
      });

      if (response.ok) {
        const data = await response.json();
        this.authToken = data.token;
        await this.saveAuthToken();
        
        this.showSuccess('Connexion réussie !');
        this.showMainSection();
        await this.loadPasswords();
      } else {
        const error = await response.json();
        this.showError(error.detail || 'Erreur d\'authentification');
      }
    } catch (error) {
      console.error('Erreur authentification:', error);
      this.showError('Impossible de se connecter au gestionnaire local');
    }
  }

  async verifyAuth() {
    try {
      const response = await fetch(`${this.apiUrl}/passwords`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });

      if (response.ok) {
        this.showMainSection();
        await this.loadPasswords();
      } else {
        this.authToken = null;
        await chrome.storage.session.remove(['authToken']);
      }
    } catch (error) {
      console.error('Erreur vérification auth:', error);
      this.authToken = null;
    }
  }

  async loadPasswords() {
    if (!this.authToken) return;

    try {
      const response = await fetch(`${this.apiUrl}/passwords`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });

      if (response.ok) {
        this.passwords = await response.json();
        this.displayPasswords();
      } else {
        this.showError('Erreur de chargement des mots de passe');
      }
    } catch (error) {
      console.error('Erreur chargement passwords:', error);
      this.showError('Impossible de charger les mots de passe');
    }
  }

  displayPasswords(filteredPasswords = null) {
    const list = document.getElementById('passwords-list');
    const passwords = filteredPasswords || this.passwords;
    
    if (passwords.length === 0) {
      list.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">Aucun mot de passe trouvé</div>';
      return;
    }

    list.innerHTML = passwords.map(pwd => `
      <div class="password-item" data-id="${pwd.id}">
        <div class="password-icon">${this.getPasswordIcon(pwd)}</div>
        <div class="password-info">
          <div class="password-title">${this.escapeHtml(pwd.title)}</div>
          <div class="password-username">${this.escapeHtml(pwd.username || 'Aucun utilisateur')}</div>
        </div>
      </div>
    `).join('');

    // Ajouter les événements de clic
    list.querySelectorAll('.password-item').forEach(item => {
      item.addEventListener('click', () => this.selectPassword(item.dataset.id));
    });
  }

  getPasswordIcon(password) {
    const title = password.title.toLowerCase();
    
    if (title.includes('gmail') || title.includes('email')) return '📧';
    if (title.includes('facebook')) return '📘';
    if (title.includes('twitter')) return '🐦';
    if (title.includes('linkedin')) return '💼';
    if (title.includes('github')) return '🐙';
    if (title.includes('netflix')) return '🎬';
    if (title.includes('spotify')) return '🎵';
    if (title.includes('bank') || title.includes('banque')) return '🏦';
    if (title.includes('amazon')) return '📦';
    if (title.includes('google')) return '🔍';
    
    return password.title.charAt(0).toUpperCase();
  }

  selectPassword(passwordId) {
    // Désélectionner tous
    document.querySelectorAll('.password-item').forEach(item => {
      item.classList.remove('selected');
    });

    // Sélectionner le nouveau
    const item = document.querySelector(`[data-id="${passwordId}"]`);
    if (item) {
      item.classList.add('selected');
      this.selectedPassword = this.passwords.find(p => p.id === passwordId);
    }
  }

  async fillPassword() {
    if (!this.selectedPassword) {
      this.showError('Veuillez sélectionner un mot de passe');
      return;
    }

    try {
      // Récupérer le mot de passe complet avec déchiffrement
      const response = await fetch(`${this.apiUrl}/passwords/${this.selectedPassword.id}`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });

      if (response.ok) {
        const passwordData = await response.json();
        
        // Fermer le popup et envoyer le message au content script
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        await chrome.tabs.sendMessage(tab.id, {
          action: 'fillPassword',
          data: {
            username: passwordData.username,
            password: passwordData.password,
            url: passwordData.url
          }
        });

        this.showSuccess('Auto-remplissage effectué !');
        
        // Fermer le popup après 1 seconde
        setTimeout(() => window.close(), 1000);
        
      } else {
        this.showError('Erreur lors de la récupération du mot de passe');
      }
    } catch (error) {
      console.error('Erreur fill password:', error);
      this.showError('Erreur lors de l\'auto-remplissage');
    }
  }

  searchPasswords(query) {
    if (!query.trim()) {
      this.displayPasswords();
      return;
    }

    const filtered = this.passwords.filter(pwd => 
      pwd.title.toLowerCase().includes(query.toLowerCase()) ||
      (pwd.username && pwd.username.toLowerCase().includes(query.toLowerCase())) ||
      (pwd.url && pwd.url.toLowerCase().includes(query.toLowerCase()))
    );

    this.displayPasswords(filtered);
  }

  showGenerator() {
    const section = document.getElementById('generator-section');
    section.classList.toggle('hidden');
    
    if (!section.classList.contains('hidden')) {
      this.generatePassword();
    }
  }

  generatePassword() {
    const length = parseInt(document.getElementById('length-slider').value);
    const uppercase = document.getElementById('uppercase').checked;
    const lowercase = document.getElementById('lowercase').checked;
    const numbers = document.getElementById('numbers').checked;
    const symbols = document.getElementById('symbols').checked;

    let charset = '';
    let required = [];

    if (lowercase) {
      charset += 'abcdefghijklmnopqrstuvwxyz';
      required.push(this.randomChar('abcdefghijklmnopqrstuvwxyz'));
    }
    
    if (uppercase) {
      charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
      required.push(this.randomChar('ABCDEFGHIJKLMNOPQRSTUVWXYZ'));
    }
    
    if (numbers) {
      charset += '0123456789';
      required.push(this.randomChar('0123456789'));
    }
    
    if (symbols) {
      charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';
      required.push(this.randomChar('!@#$%^&*()_+-=[]{}|;:,.<>?'));
    }

    if (!charset) {
      charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    }

    // Générer le reste du mot de passe
    const remainingLength = length - required.length;
    let password = required.join('');
    
    for (let i = 0; i < remainingLength; i++) {
      password += this.randomChar(charset);
    }

    // Mélanger le mot de passe
    password = this.shuffleString(password);

    document.getElementById('generated-pwd').value = password;
  }

  randomChar(charset) {
    return charset.charAt(Math.floor(Math.random() * charset.length));
  }

  shuffleString(str) {
    return str.split('').sort(() => Math.random() - 0.5).join('');
  }

  async copyGenerated() {
    const password = document.getElementById('generated-pwd').value;
    if (password) {
      await navigator.clipboard.writeText(password);
      this.showSuccess('Mot de passe copié !');
    }
  }

  async saveGenerated() {
    const password = document.getElementById('generated-pwd').value;
    if (!password) {
      this.showError('Aucun mot de passe généré');
      return;
    }

    // Pour l'instant, on copie juste le mot de passe
    // Dans une version complète, on ouvrirait un formulaire de sauvegarde
    await this.copyGenerated();
    this.showSuccess('Utilisez ce mot de passe dans le gestionnaire principal pour le sauvegarder');
  }

  async refreshPasswords() {
    await this.loadPasswords();
    this.showSuccess('Liste actualisée !');
  }

  showMainSection() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('main-section').classList.remove('hidden');
    this.updateStatus(true);
  }

  updateStatus(connected = false) {
    const status = document.getElementById('status');
    if (connected || this.authToken) {
      status.classList.add('connected');
      status.title = 'Connecté au gestionnaire local';
    } else {
      status.classList.remove('connected');
      status.title = 'Non connecté';
    }
  }

  showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    setTimeout(() => {
      errorDiv.classList.add('hidden');
    }, 4000);
  }

  showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.classList.remove('hidden');
    
    setTimeout(() => {
      successDiv.classList.add('hidden');
    }, 3000);
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialiser l'extension
document.addEventListener('DOMContentLoaded', () => {
  new PasswordManagerPopup();
});