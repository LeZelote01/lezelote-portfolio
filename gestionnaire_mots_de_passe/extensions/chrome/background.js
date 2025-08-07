// Gestionnaire de Mots de Passe - Background Script Chrome
// Service Worker pour la gestion des événements en arrière-plan

class PasswordManagerBackground {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    console.log('🔐 Gestionnaire MDP - Background script initialisé');
  }

  setupEventListeners() {
    // Installation de l'extension
    chrome.runtime.onInstalled.addListener((details) => {
      this.onInstalled(details);
    });

    // Messages des content scripts et popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Garde la connexion ouverte pour les réponses asynchrones
    });

    // Événements des onglets
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      this.onTabUpdated(tabId, changeInfo, tab);
    });

    // Événements de contexte (clic droit)
    this.setupContextMenus();
  }

  onInstalled(details) {
    if (details.reason === 'install') {
      console.log('🎉 Extension installée pour la première fois');
      this.showWelcomeNotification();
    } else if (details.reason === 'update') {
      console.log('🔄 Extension mise à jour');
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'openPasswordManager':
          await this.openPasswordManager(message.form);
          sendResponse({ success: true });
          break;

        case 'formSubmitted':
          await this.handleFormSubmission(message.data, sender.tab);
          sendResponse({ success: true });
          break;

        case 'checkApiConnection':
          const connected = await this.checkApiConnection();
          sendResponse({ connected });
          break;

        case 'getTabInfo':
          const tabInfo = await this.getTabInfo(sender.tab.id);
          sendResponse(tabInfo);
          break;

        default:
          console.warn('Action non reconnue:', message.action);
          sendResponse({ error: 'Action non reconnue' });
      }
    } catch (error) {
      console.error('Erreur dans handleMessage:', error);
      sendResponse({ error: error.message });
    }
  }

  async openPasswordManager(formData) {
    try {
      // Ouvrir le popup de l'extension
      await chrome.action.openPopup();
    } catch (error) {
      console.error('Erreur ouverture popup:', error);
      
      // Fallback: ouvrir dans un nouvel onglet
      await chrome.tabs.create({
        url: chrome.runtime.getURL('popup.html'),
        pinned: false
      });
    }
  }

  async handleFormSubmission(data, tab) {
    console.log('📝 Formulaire soumis:', data);
    
    // Sauvegarder les informations du formulaire pour suggestion ultérieure
    await this.saveFormData(data, tab);
    
    // Optionnel: Proposer de sauvegarder le mot de passe
    if (data.username && data.formType === 'login') {
      await this.showSavePasswordNotification(data, tab);
    }
  }

  async saveFormData(data, tab) {
    try {
      // Sauvegarder dans le storage local pour suggestions
      const formHistory = await chrome.storage.local.get(['formHistory']) || { formHistory: [] };
      const history = formHistory.formHistory || [];
      
      const formEntry = {
        url: data.url,
        domain: new URL(data.url).hostname,
        title: data.title,
        username: data.username,
        timestamp: Date.now(),
        tabId: tab.id
      };
      
      // Éviter les doublons (même domaine + username)
      const existingIndex = history.findIndex(item => 
        item.domain === formEntry.domain && item.username === formEntry.username
      );
      
      if (existingIndex >= 0) {
        history[existingIndex] = formEntry; // Mettre à jour
      } else {
        history.push(formEntry);
      }
      
      // Garder seulement les 100 dernières entrées
      if (history.length > 100) {
        history.splice(0, history.length - 100);
      }
      
      await chrome.storage.local.set({ formHistory: history });
      
    } catch (error) {
      console.error('Erreur sauvegarde form data:', error);
    }
  }

  async showSavePasswordNotification(data, tab) {
    try {
      await chrome.notifications.create(`save-password-${Date.now()}`, {
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'Sauvegarder le mot de passe ?',
        message: `Voulez-vous sauvegarder le mot de passe pour ${data.username} sur ${new URL(data.url).hostname} ?`,
        buttons: [
          { title: 'Sauvegarder' },
          { title: 'Ignorer' }
        ],
        requireInteraction: true
      });
    } catch (error) {
      console.error('Erreur notification:', error);
    }
  }

  async checkApiConnection() {
    try {
      const response = await fetch('http://localhost:8002/api/health', {
        method: 'GET',
        timeout: 5000
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  async getTabInfo(tabId) {
    try {
      const tab = await chrome.tabs.get(tabId);
      return {
        url: tab.url,
        title: tab.title,
        domain: new URL(tab.url).hostname
      };
    } catch (error) {
      console.error('Erreur getTabInfo:', error);
      return null;
    }
  }

  onTabUpdated(tabId, changeInfo, tab) {
    // Quand une page est entièrement chargée, injecter le content script si nécessaire
    if (changeInfo.status === 'complete' && tab.url && 
        (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
      
      // Le content script est déjà injecté automatiquement via le manifest
      // Mais on peut envoyer un message pour re-détecter les formulaires
      setTimeout(() => {
        chrome.tabs.sendMessage(tabId, { action: 'detectForms' }).catch(() => {
          // Ignorer les erreurs (onglet fermé, etc.)
        });
      }, 1000);
    }
  }

  setupContextMenus() {
    // Menu contextuel sur les champs de mot de passe
    chrome.contextMenus.create({
      id: 'fill-password',
      title: '🔐 Auto-remplir le mot de passe',
      contexts: ['editable'],
      documentUrlPatterns: ['http://*/*', 'https://*/*']
    });

    chrome.contextMenus.create({
      id: 'generate-password',
      title: '🎲 Générer un mot de passe',
      contexts: ['editable'],
      documentUrlPatterns: ['http://*/*', 'https://*/*']
    });

    // Gestionnaire des clics sur le menu contextuel
    chrome.contextMenus.onClicked.addListener(async (info, tab) => {
      await this.handleContextMenuClick(info, tab);
    });
  }

  async handleContextMenuClick(info, tab) {
    try {
      switch (info.menuItemId) {
        case 'fill-password':
          // Ouvrir le popup pour sélectionner un mot de passe
          await chrome.action.openPopup();
          break;

        case 'generate-password':
          // Générer un mot de passe et l'insérer
          const password = this.generateRandomPassword();
          await chrome.tabs.sendMessage(tab.id, {
            action: 'insertPassword',
            password: password
          });
          break;
      }
    } catch (error) {
      console.error('Erreur menu contextuel:', error);
    }
  }

  generateRandomPassword(length = 16) {
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    
    const allChars = lowercase + uppercase + numbers + symbols;
    const required = [
      lowercase[Math.floor(Math.random() * lowercase.length)],
      uppercase[Math.floor(Math.random() * uppercase.length)],
      numbers[Math.floor(Math.random() * numbers.length)],
      symbols[Math.floor(Math.random() * symbols.length)]
    ];
    
    let password = required.join('');
    
    for (let i = password.length; i < length; i++) {
      password += allChars[Math.floor(Math.random() * allChars.length)];
    }
    
    // Mélanger le mot de passe
    return password.split('').sort(() => Math.random() - 0.5).join('');
  }

  showWelcomeNotification() {
    chrome.notifications.create('welcome', {
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: '🔐 Gestionnaire de Mots de Passe',
      message: 'Extension installée ! Assurez-vous que le gestionnaire local est démarré sur le port 8002.',
      buttons: [
        { title: 'Ouvrir le gestionnaire' }
      ]
    });
  }
}

// Initialiser le background script
new PasswordManagerBackground();