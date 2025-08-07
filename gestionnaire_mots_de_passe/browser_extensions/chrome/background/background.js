/**
 * Background Script - Gestionnaire de Mots de Passe
 * Communication avec l'application native et gestion des événements
 */

// Configuration de l'API REST locale
const API_BASE_URL = 'http://localhost:8002/api';
let authToken = null;

// États de l'extension
const extensionState = {
  isConnected: false,
  isAuthenticated: false,
  activeTab: null,
  lastActivity: Date.now()
};

/**
 * Initialisation de l'extension
 */
chrome.runtime.onStartup.addListener(async () => {
  console.log('🚀 Extension Gestionnaire MDP - Démarrage');
  await initializeExtension();
});

chrome.runtime.onInstalled.addListener(async () => {
  console.log('✅ Extension Gestionnaire MDP - Installation');
  await initializeExtension();
  await createContextMenus();
});

/**
 * Initialisation des composants
 */
async function initializeExtension() {
  try {
    // Vérifier la connexion à l'API
    await checkApiConnection();
    
    // Charger le token d'authentification si existant
    const result = await chrome.storage.local.get(['authToken', 'lastAuth']);
    if (result.authToken && isTokenValid(result.lastAuth)) {
      authToken = result.authToken;
      extensionState.isAuthenticated = true;
      console.log('🔐 Authentification restaurée');
    }
    
    // Configurer les alarmes de sécurité
    await setupSecurityAlarms();
    
  } catch (error) {
    console.error('❌ Erreur initialisation:', error);
    extensionState.isConnected = false;
  }
}

/**
 * Vérification de la connexion API
 */
async function checkApiConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      extensionState.isConnected = true;
      console.log('🌐 Connexion API établie');
    } else {
      throw new Error(`API non disponible: ${response.status}`);
    }
  } catch (error) {
    console.error('❌ Connexion API échouée:', error);
    extensionState.isConnected = false;
    throw error;
  }
}

/**
 * Création des menus contextuels
 */
async function createContextMenus() {
  await chrome.contextMenus.removeAll();
  
  chrome.contextMenus.create({
    id: "generate-password",
    title: "🔐 Générer un mot de passe",
    contexts: ["editable"]
  });
  
  chrome.contextMenus.create({
    id: "fill-password",
    title: "📝 Remplir le mot de passe",
    contexts: ["editable"]
  });
  
  chrome.contextMenus.create({
    id: "save-password",
    title: "💾 Sauvegarder ce mot de passe",
    contexts: ["page"]
  });
}

/**
 * Gestion des menus contextuels
 */
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  try {
    switch (info.menuItemId) {
      case "generate-password":
        await handleGeneratePassword(tab);
        break;
      case "fill-password":
        await handleFillPassword(tab);
        break;
      case "save-password":
        await handleSavePassword(tab);
        break;
    }
  } catch (error) {
    console.error('❌ Erreur menu contextuel:', error);
    showNotification('Erreur', error.message, 'error');
  }
});

/**
 * Communication avec les content scripts
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  (async () => {
    try {
      const response = await handleMessage(request, sender);
      sendResponse({ success: true, data: response });
    } catch (error) {
      console.error('❌ Erreur message:', error);
      sendResponse({ success: false, error: error.message });
    }
  })();
  return true; // Réponse asynchrone
});

/**
 * Gestionnaire de messages
 */
async function handleMessage(request, sender) {
  const { action, data } = request;
  
  switch (action) {
    case 'authenticate':
      return await authenticateUser(data.masterPassword);
      
    case 'getPasswords':
      return await getPasswordsForDomain(data.domain);
      
    case 'generatePassword':
      return await generateSecurePassword(data.options);
      
    case 'savePassword':
      return await savePassword(data);
      
    case 'checkAuthentication':
      return { 
        isAuthenticated: extensionState.isAuthenticated,
        isConnected: extensionState.isConnected 
      };
      
    case 'logout':
      return await logoutUser();
      
    default:
      throw new Error(`Action non reconnue: ${action}`);
  }
}

/**
 * Authentification utilisateur
 */
async function authenticateUser(masterPassword) {
  if (!extensionState.isConnected) {
    throw new Error('Connexion à l\'API non disponible');
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        master_password: masterPassword,
        source: 'browser_extension'
      })
    });
    
    if (!response.ok) {
      throw new Error('Authentification échouée');
    }
    
    const result = await response.json();
    authToken = result.access_token;
    
    // Sauvegarder le token
    await chrome.storage.local.set({
      authToken: authToken,
      lastAuth: Date.now()
    });
    
    extensionState.isAuthenticated = true;
    console.log('✅ Authentification réussie');
    
    showNotification('Succès', 'Authentifié avec succès', 'success');
    return { authenticated: true };
    
  } catch (error) {
    console.error('❌ Erreur authentification:', error);
    throw new Error('Échec de l\'authentification');
  }
}

/**
 * Récupération des mots de passe pour un domaine
 */
async function getPasswordsForDomain(domain) {
  if (!extensionState.isAuthenticated) {
    throw new Error('Authentification requise');
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/passwords/search?domain=${encodeURIComponent(domain)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Erreur récupération mots de passe');
    }
    
    const passwords = await response.json();
    console.log(`🔍 ${passwords.length} mots de passe trouvés pour ${domain}`);
    
    return passwords;
    
  } catch (error) {
    console.error('❌ Erreur récupération:', error);
    throw error;
  }
}

/**
 * Génération de mot de passe sécurisé
 */
async function generateSecurePassword(options = {}) {
  try {
    const defaultOptions = {
      length: 16,
      include_uppercase: true,
      include_lowercase: true,
      include_numbers: true,
      include_symbols: true,
      exclude_ambiguous: true
    };
    
    const generateOptions = { ...defaultOptions, ...options };
    
    const response = await fetch(`${API_BASE_URL}/generate/password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authToken ? `Bearer ${authToken}` : undefined
      },
      body: JSON.stringify(generateOptions)
    });
    
    if (!response.ok) {
      throw new Error('Erreur génération mot de passe');
    }
    
    const result = await response.json();
    console.log('🔐 Mot de passe généré avec succès');
    
    return { password: result.password, strength: result.strength };
    
  } catch (error) {
    console.error('❌ Erreur génération:', error);
    throw error;
  }
}

/**
 * Sauvegarde d'un mot de passe
 */
async function savePassword(passwordData) {
  if (!extensionState.isAuthenticated) {
    throw new Error('Authentification requise');
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/passwords`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        title: passwordData.title,
        username: passwordData.username,
        password: passwordData.password,
        url: passwordData.url,
        category: passwordData.category || 'Web',
        notes: `Sauvegardé depuis l'extension navigateur - ${new Date().toISOString()}`
      })
    });
    
    if (!response.ok) {
      throw new Error('Erreur sauvegarde mot de passe');
    }
    
    const result = await response.json();
    console.log('💾 Mot de passe sauvegardé:', result.id);
    
    showNotification('Succès', 'Mot de passe sauvegardé', 'success');
    return { saved: true, id: result.id };
    
  } catch (error) {
    console.error('❌ Erreur sauvegarde:', error);
    throw error;
  }
}

/**
 * Actions des menus contextuels
 */
async function handleGeneratePassword(tab) {
  const password = await generateSecurePassword();
  
  await chrome.tabs.sendMessage(tab.id, {
    action: 'fillPassword',
    password: password.password
  });
  
  showNotification('Succès', 'Mot de passe généré et inséré', 'success');
}

async function handleFillPassword(tab) {
  const url = new URL(tab.url);
  const domain = url.hostname;
  
  const passwords = await getPasswordsForDomain(domain);
  
  if (passwords.length === 0) {
    showNotification('Info', 'Aucun mot de passe trouvé pour ce site', 'info');
    return;
  }
  
  // Utiliser le premier mot de passe trouvé
  const password = passwords[0];
  
  await chrome.tabs.sendMessage(tab.id, {
    action: 'fillCredentials',
    username: password.username,
    password: password.password
  });
  
  showNotification('Succès', 'Identifiants remplis', 'success');
}

async function handleSavePassword(tab) {
  await chrome.tabs.sendMessage(tab.id, {
    action: 'detectCredentials'
  });
}

/**
 * Déconnexion
 */
async function logoutUser() {
  authToken = null;
  extensionState.isAuthenticated = false;
  
  await chrome.storage.local.remove(['authToken', 'lastAuth']);
  
  console.log('👋 Déconnexion effectuée');
  showNotification('Info', 'Déconnexion effectuée', 'info');
  
  return { loggedOut: true };
}

/**
 * Sécurité - Vérification de validité du token
 */
function isTokenValid(lastAuth) {
  const MAX_TOKEN_AGE = 8 * 60 * 60 * 1000; // 8 heures
  return lastAuth && (Date.now() - lastAuth) < MAX_TOKEN_AGE;
}

/**
 * Configuration des alarmes de sécurité
 */
async function setupSecurityAlarms() {
  // Auto-déconnexion après 30 minutes d'inactivité
  chrome.alarms.create('security-timeout', { 
    delayInMinutes: 30,
    periodInMinutes: 30
  });
  
  // Vérification de connexion API toutes les 5 minutes
  chrome.alarms.create('api-health-check', {
    delayInMinutes: 5,
    periodInMinutes: 5
  });
}

/**
 * Gestionnaire d'alarmes
 */
chrome.alarms.onAlarm.addListener(async (alarm) => {
  switch (alarm.name) {
    case 'security-timeout':
      if (Date.now() - extensionState.lastActivity > 30 * 60 * 1000) {
        await logoutUser();
      }
      break;
      
    case 'api-health-check':
      try {
        await checkApiConnection();
      } catch (error) {
        if (extensionState.isConnected) {
          extensionState.isConnected = false;
          showNotification('Attention', 'Connexion API perdue', 'warning');
        }
      }
      break;
  }
});

/**
 * Notifications
 */
function showNotification(title, message, type = 'info') {
  const iconMap = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: `../popup/icons/icon48.png`,
    title: `${iconMap[type]} ${title}`,
    message: message
  });
}

/**
 * Mise à jour de l'activité
 */
chrome.tabs.onActivated.addListener(() => {
  extensionState.lastActivity = Date.now();
});

chrome.tabs.onUpdated.addListener(() => {
  extensionState.lastActivity = Date.now();
});

console.log('🔐 Background Script - Gestionnaire MDP initialisé');