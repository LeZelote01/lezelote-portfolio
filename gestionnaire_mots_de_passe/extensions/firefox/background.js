// Gestionnaire de Mots de Passe - Background Script Firefox
// Compatible WebExtensions API

// Polyfill pour Chrome si nécessaire
if (typeof browser === 'undefined') {
  window.browser = chrome;
}

class PasswordManagerBackground {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    console.log('🔐 Gestionnaire MDP Firefox - Background script initialisé');
  }

  setupEventListeners() {
    // Installation de l'extension
    browser.runtime.onInstalled.addListener((details) => {
      this.onInstalled(details);
    });

    // Messages des content scripts et popup
    browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
      return this.handleMessage(message, sender, sendResponse);
    });

    // Événements des onglets
    browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      this.onTabUpdated(tabId, changeInfo, tab);
    });

    // Menu contextuel
    this.setupContextMenus();
    
    // Notifications
    this.setupNotifications();
  }

  onInstalled(details) {
    if (details.reason === 'install') {
      console.log('🎉 Extension Firefox installée pour la première fois');
      this.showWelcomeNotification();
    } else if (details.reason === 'update') {
      console.log('🔄 Extension Firefox mise à jour');
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'openPasswordManager':
          await this.openPasswordManager(message.form);
          return { success: true };

        case 'formSubmitted':
          await this.handleFormSubmission(message.data, sender.tab);
          return { success: true };

        case 'checkApiConnection':
          const connected = await this.checkApiConnection();
          return { connected };

        case 'getTabInfo':
          const tabInfo = await this.getTabInfo(sender.tab.id);
          return tabInfo;

        case 'insertPassword':
          // Pour le menu contextuel
          await this.insertGeneratedPassword(message.password, sender.tab);
          return { success: true };

        default:
          console.warn('Action non reconnue:', message.action);
          return { error: 'Action non reconnue' };
      }
    } catch (error) {
      console.error('Erreur dans handleMessage:', error);
      return { error: error.message };
    }
  }

  async openPasswordManager(formData) {
    try {
      // Firefox utilise browserAction au lieu d'action
      await browser.browserAction.openPopup();
    } catch (error) {
      console.error('Erreur ouverture popup:', error);
      
      // Fallback: ouvrir dans un nouvel onglet
      await browser.tabs.create({
        url: browser.runtime.getURL('popup.html'),
        pinned: false
      });
    }
  }

  async handleFormSubmission(data, tab) {
    console.log('📝 Formulaire soumis:', data);
    
    // Sauvegarder les informations du formulaire
    await this.saveFormData(data, tab);
    
    // Proposer de sauvegarder le mot de passe
    if (data.username && data.formType === 'login') {
      await this.showSavePasswordNotification(data, tab);
    }
  }

  async saveFormData(data, tab) {
    try {
      const result = await browser.storage.local.get(['formHistory']);
      const history = result.formHistory || [];
      
      const formEntry = {
        url: data.url,
        domain: new URL(data.url).hostname,
        title: data.title,
        username: data.username,
        timestamp: Date.now(),
        tabId: tab.id
      };
      
      // Éviter les doublons
      const existingIndex = history.findIndex(item => 
        item.domain === formEntry.domain && item.username === formEntry.username
      );
      
      if (existingIndex >= 0) {
        history[existingIndex] = formEntry;
      } else {
        history.push(formEntry);
      }
      
      // Garder seulement les 100 dernières entrées
      if (history.length > 100) {
        history.splice(0, history.length - 100);
      }
      
      await browser.storage.local.set({ formHistory: history });
      
    } catch (error) {
      console.error('Erreur sauvegarde form data:', error);
    }
  }

  async showSavePasswordNotification(data, tab) {
    try {
      // Firefox supporte les notifications
      const notificationId = await browser.notifications.create(`save-password-${Date.now()}`, {
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'Sauvegarder le mot de passe ?',
        message: `Voulez-vous sauvegarder le mot de passe pour ${data.username} sur ${new URL(data.url).hostname} ?`
      });
      
      // Firefox ne supporte pas les boutons dans les notifications de base
      // Mais on peut écouter les clics
      browser.notifications.onClicked.addListener((clickedId) => {
        if (clickedId === notificationId) {
          // Ouvrir le popup pour sauvegarder
          browser.browserAction.openPopup().catch(() => {
            browser.tabs.create({
              url: browser.runtime.getURL('popup.html')
            });
          });
        }
      });
      
    } catch (error) {
      console.error('Erreur notification:', error);
    }
  }

  async checkApiConnection() {
    try {
      const response = await fetch('http://localhost:8002/api/health', {
        method: 'GET'
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  async getTabInfo(tabId) {
    try {
      const tab = await browser.tabs.get(tabId);
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
    // Quand une page est chargée, re-détecter les formulaires
    if (changeInfo.status === 'complete' && tab.url && 
        (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
      
      setTimeout(() => {
        browser.tabs.sendMessage(tabId, { action: 'detectForms' }).catch(() => {
          // Ignorer les erreurs (onglet fermé, etc.)
        });
      }, 1000);
    }
  }

  setupContextMenus() {
    // Firefox utilise contextMenus
    browser.contextMenus.create({
      id: 'fill-password',
      title: '🔐 Auto-remplir le mot de passe',
      contexts: ['editable'],
      documentUrlPatterns: ['http://*/*', 'https://*/*']
    });

    browser.contextMenus.create({
      id: 'generate-password',
      title: '🎲 Générer un mot de passe',
      contexts: ['editable'],
      documentUrlPatterns: ['http://*/*', 'https://*/*']
    });

    // Gestionnaire des clics
    browser.contextMenus.onClicked.addListener(async (info, tab) => {
      await this.handleContextMenuClick(info, tab);
    });
  }

  setupNotifications() {
    // Écouter les clics sur les notifications
    browser.notifications.onClicked.addListener((notificationId) => {
      console.log('Notification cliquée:', notificationId);
      
      if (notificationId === 'welcome') {
        // Ouvrir le gestionnaire
        browser.tabs.create({
          url: 'http://localhost:8002'
        }).catch((error) => {
          console.log('Gestionnaire local non accessible:', error);
        });
      }
    });
  }

  async handleContextMenuClick(info, tab) {
    try {
      switch (info.menuItemId) {
        case 'fill-password':
          // Ouvrir le popup pour sélectionner un mot de passe
          await browser.browserAction.openPopup();
          break;

        case 'generate-password':
          // Générer un mot de passe et l'insérer
          const password = this.generateRandomPassword();
          await browser.tabs.sendMessage(tab.id, {
            action: 'insertPassword',
            password: password
          });
          break;
      }
    } catch (error) {
      console.error('Erreur menu contextuel:', error);
    }
  }

  async insertGeneratedPassword(password, tab) {
    try {
      await browser.tabs.sendMessage(tab.id, {
        action: 'insertPassword',
        password: password
      });
    } catch (error) {
      console.error('Erreur insertion password:', error);
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
    browser.notifications.create('welcome', {
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: '🔐 Gestionnaire de Mots de Passe',
      message: 'Extension Firefox installée ! Cliquez pour ouvrir le gestionnaire local.'
    });
  }
}

// Initialiser le background script
new PasswordManagerBackground();