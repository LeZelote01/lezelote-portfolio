/**
 * Background Script - Gestionnaire de Mots de Passe
 * Service Worker pour Chrome Extension (Manifest V3)
 */

// Configuration
const CONFIG = {
  API_BASE_URL: 'http://localhost:8002/api',
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  DEBUG: true
};

// État global de l'extension
let extensionState = {
  isAuthenticated: false,
  authToken: null,
  sessionTimeout: null,
  passwords: [],
  lastSync: null
};

// Logging utilitaire
function log(...args) {
  if (CONFIG.DEBUG) {
    console.log('🔐 GMP Background:', ...args);
  }
}

/**
 * Authentification avec l'API
 */
async function authenticate(masterPassword) {
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        master_password: masterPassword,
        source: 'browser_extension'
      })
    });

    if (response.ok) {
      const data = await response.json();
      extensionState.isAuthenticated = true;
      extensionState.authToken = data.access_token;
      
      // Programmer l'expiration de session
      setSessionTimeout();
      
      log('Authentification réussie');
      return { success: true, token: data.access_token };
    } else {
      const error = await response.text();
      log('Échec authentification:', error);
      return { success: false, error: 'Mot de passe incorrect' };
    }
  } catch (error) {
    log('Erreur authentification:', error);
    return { success: false, error: 'Impossible de se connecter à l\'API' };
  }
}

/**
 * Déconnexion
 */
function logout() {
  extensionState.isAuthenticated = false;
  extensionState.authToken = null;
  extensionState.passwords = [];
  
  if (extensionState.sessionTimeout) {
    clearTimeout(extensionState.sessionTimeout);
  }
  
  log('Déconnexion effectuée');
  
  // Notifier tous les onglets
  notifyAllTabs({ action: 'logout' });
}

/**
 * Définir le timeout de session
 */
function setSessionTimeout() {
  if (extensionState.sessionTimeout) {
    clearTimeout(extensionState.sessionTimeout);
  }
  
  extensionState.sessionTimeout = setTimeout(() => {
    logout();
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Session expirée',
      message: 'Votre session a expiré. Veuillez vous reconnecter.'
    });
  }, CONFIG.SESSION_TIMEOUT);
}

/**
 * Récupérer les mots de passe pour un domaine
 */
async function getPasswordsForDomain(domain) {
  if (!extensionState.isAuthenticated) {
    return { success: false, error: 'Non authentifié' };
  }

  try {
    const url = domain ? 
      `${CONFIG.API_BASE_URL}/passwords/search?domain=${encodeURIComponent(domain)}` :
      `${CONFIG.API_BASE_URL}/passwords`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${extensionState.authToken}`
      }
    });

    if (response.ok) {
      const passwords = await response.json();
      log(`Récupérés ${passwords.length} mots de passe pour ${domain}`);
      return { success: true, passwords: passwords };
    } else {
      log('Erreur récupération mots de passe:', response.status);
      return { success: false, error: 'Erreur de récupération' };
    }
  } catch (error) {
    log('Erreur getPasswordsForDomain:', error);
    return { success: false, error: 'Erreur de connexion' };
  }
}

/**
 * Générer un mot de passe
 */
async function generatePassword(options = {}) {
  try {
    const defaultOptions = {
      length: 16,
      include_uppercase: true,
      include_lowercase: true, 
      include_numbers: true,
      include_symbols: true
    };

    const finalOptions = { ...defaultOptions, ...options };

    const headers = { 'Content-Type': 'application/json' };
    if (extensionState.authToken) {
      headers['Authorization'] = `Bearer ${extensionState.authToken}`;
    }

    const response = await fetch(`${CONFIG.API_BASE_URL}/generate/password`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(finalOptions)
    });

    if (response.ok) {
      const data = await response.json();
      log('Mot de passe généré avec succès');
      return { success: true, password: data.password };
    } else {
      log('Erreur génération mot de passe:', response.status);
      return { success: false, error: 'Erreur de génération' };
    }
  } catch (error) {
    log('Erreur generatePassword:', error);
    return { success: false, error: 'Erreur de connexion' };
  }
}

/**
 * Sauvegarder un mot de passe
 */
async function savePassword(passwordData) {
  if (!extensionState.isAuthenticated) {
    return { success: false, error: 'Non authentifié' };
  }

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/passwords`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${extensionState.authToken}`
      },
      body: JSON.stringify(passwordData)
    });

    if (response.ok) {
      const data = await response.json();
      log('Mot de passe sauvegardé:', data.id);
      return { success: true, id: data.id };
    } else {
      log('Erreur sauvegarde mot de passe:', response.status);
      return { success: false, error: 'Erreur de sauvegarde' };
    }
  } catch (error) {
    log('Erreur savePassword:', error);
    return { success: false, error: 'Erreur de connexion' };
  }
}

/**
 * Vérifier la santé de l'API
 */
async function checkHealth() {
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    log('API non accessible:', error);
    return false;
  }
}

/**
 * Notifier tous les onglets
 */
function notifyAllTabs(message) {
  chrome.tabs.query({}, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, message).catch(() => {
        // Ignorer les erreurs pour les onglets sans content script
      });
    });
  });
}

/**
 * Obtenir le domaine depuis une URL
 */
function getDomainFromUrl(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch (error) {
    return null;
  }
}

// Installation de l'extension
chrome.runtime.onInstalled.addListener((details) => {
  log('Extension installée/mise à jour:', details.reason);
  
  // Créer le menu contextuel
  chrome.contextMenus.create({
    id: 'gmp-generate',
    title: 'Générer un mot de passe',
    contexts: ['editable']
  });
  
  chrome.contextMenus.create({
    id: 'gmp-fill',
    title: 'Remplir le mot de passe',
    contexts: ['editable']
  });
  
  chrome.contextMenus.create({
    id: 'gmp-save',
    title: 'Sauvegarder ce mot de passe',
    contexts: ['editable']
  });
});

// Gestion des messages des content scripts et popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  log('Message reçu:', message.action);
  
  (async () => {
    try {
      switch (message.action) {
        case 'authenticate':
          const authResult = await authenticate(message.masterPassword);
          sendResponse(authResult);
          break;
          
        case 'logout':
          logout();
          sendResponse({ success: true });
          break;
          
        case 'getPasswords':
          const passwordsResult = await getPasswordsForDomain(message.domain);
          sendResponse(passwordsResult);
          break;
          
        case 'generatePassword':
          const genResult = await generatePassword(message.options);
          sendResponse(genResult);
          break;
          
        case 'savePassword':
          const saveResult = await savePassword(message.passwordData);
          sendResponse(saveResult);
          break;
          
        case 'checkHealth':
          const isHealthy = await checkHealth();
          sendResponse({ success: true, healthy: isHealthy });
          break;
          
        case 'getState':
          sendResponse({
            isAuthenticated: extensionState.isAuthenticated,
            lastSync: extensionState.lastSync
          });
          break;
          
        default:
          sendResponse({ success: false, error: 'Action inconnue' });
      }
    } catch (error) {
      log('Erreur traitement message:', error);
      sendResponse({ success: false, error: error.message });
    }
  })();
  
  return true; // Réponse asynchrone
});

// Gestion du menu contextuel
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const domain = getDomainFromUrl(tab.url);
  
  switch (info.menuItemId) {
    case 'gmp-generate':
      const genResult = await generatePassword();
      if (genResult.success) {
        chrome.tabs.sendMessage(tab.id, {
          action: 'insertPassword',
          password: genResult.password
        });
      }
      break;
      
    case 'gmp-fill':
      const passwords = await getPasswordsForDomain(domain);
      if (passwords.success && passwords.passwords.length > 0) {
        chrome.tabs.sendMessage(tab.id, {
          action: 'fillCredentials',
          credentials: passwords.passwords[0]
        });
      }
      break;
      
    case 'gmp-save':
      chrome.tabs.sendMessage(tab.id, {
        action: 'requestSave'
      });
      break;
  }
});

// Gestion des changements d'onglets
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const tab = await chrome.tabs.get(activeInfo.tabId);
  const domain = getDomainFromUrl(tab.url);
  
  if (domain && extensionState.isAuthenticated) {
    // Précharger les mots de passe pour ce domaine
    await getPasswordsForDomain(domain);
  }
});

log('Background script chargé et prêt');