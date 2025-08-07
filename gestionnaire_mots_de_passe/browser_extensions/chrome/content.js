/**
 * Content Script - Gestionnaire de Mots de Passe  
 * Script d'injection pour la détection et l'auto-remplissage des formulaires
 */

// Configuration
const CONTENT_CONFIG = {
  DEBUG: true,
  SELECTORS: {
    USERNAME: 'input[type="text"], input[type="email"], input[name*="user"], input[name*="login"], input[name*="email"]',
    PASSWORD: 'input[type="password"]',
    FORMS: 'form'
  },
  ICONS: {
    USERNAME: '👤',
    PASSWORD: '🔐',
    GENERATE: '⚡'
  }
};

// État du content script
let contentState = {
  isAuthenticated: false,
  currentDomain: window.location.hostname,
  detectedForms: [],
  injectedElements: []
};

// Logging utilitaire
function log(...args) {
  if (CONTENT_CONFIG.DEBUG) {
    console.log('📝 GMP Content:', ...args);
  }
}

/**
 * Créer une icône d'action pour un champ
 */
function createFieldIcon(type, input) {
  const icon = document.createElement('div');
  icon.className = 'gmp-field-icon';
  icon.innerHTML = CONTENT_CONFIG.ICONS[type];
  icon.title = type === 'USERNAME' ? 'Auto-remplir nom d\'utilisateur' : 'Actions mot de passe';
  
  // Positionnement
  const rect = input.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
  
  Object.assign(icon.style, {
    position: 'absolute',
    top: `${rect.top + scrollTop + 5}px`,
    right: `${window.innerWidth - (rect.right + scrollLeft) + 5}px`,
    zIndex: '10000',
    cursor: 'pointer',
    backgroundColor: '#4f46e5',
    color: 'white',
    borderRadius: '50%',
    width: '20px',
    height: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
  });
  
  // Événement de clic
  icon.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (type === 'USERNAME') {
      handleUsernameIconClick(input);
    } else if (type === 'PASSWORD') {
      handlePasswordIconClick(input);
    }
  });
  
  document.body.appendChild(icon);
  contentState.injectedElements.push(icon);
  
  return icon;
}

/**
 * Gérer le clic sur l'icône nom d'utilisateur
 */
async function handleUsernameIconClick(input) {
  try {
    // Récupérer les mots de passe pour ce domaine
    const response = await chrome.runtime.sendMessage({
      action: 'getPasswords',
      domain: contentState.currentDomain
    });
    
    if (response.success && response.passwords.length > 0) {
      // Utiliser le premier mot de passe trouvé
      const credential = response.passwords[0];
      input.value = credential.username || '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      log('Nom d\'utilisateur rempli:', credential.username);
    } else {
      showNotification('Aucun mot de passe trouvé pour ce site');
    }
  } catch (error) {
    log('Erreur récupération nom d\'utilisateur:', error);
    showNotification('Erreur lors de la récupération');
  }
}

/**
 * Gérer le clic sur l'icône mot de passe
 */
function handlePasswordIconClick(input) {
  // Créer un menu contextuel
  const menu = createPasswordMenu(input);
  document.body.appendChild(menu);
  contentState.injectedElements.push(menu);
}

/**
 * Créer le menu des actions mot de passe
 */
function createPasswordMenu(input) {
  const menu = document.createElement('div');
  menu.className = 'gmp-password-menu';
  
  // Position du menu
  const rect = input.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
  
  Object.assign(menu.style, {
    position: 'absolute',
    top: `${rect.bottom + scrollTop + 5}px`,
    left: `${rect.left + scrollLeft}px`,
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    padding: '8px 0',
    minWidth: '200px',
    zIndex: '10001'
  });
  
  // Options du menu
  const options = [
    { text: '🔐 Remplir le mot de passe', action: 'fill' },
    { text: '⚡ Générer un nouveau mot de passe', action: 'generate' },
    { text: '💾 Sauvegarder ce mot de passe', action: 'save' }
  ];
  
  options.forEach(option => {
    const item = document.createElement('div');
    item.textContent = option.text;
    item.className = 'gmp-menu-item';
    
    Object.assign(item.style, {
      padding: '8px 16px',
      cursor: 'pointer',
      fontSize: '14px',
      transition: 'background-color 0.2s'
    });
    
    item.addEventListener('mouseenter', () => {
      item.style.backgroundColor = '#f3f4f6';
    });
    
    item.addEventListener('mouseleave', () => {
      item.style.backgroundColor = 'transparent';
    });
    
    item.addEventListener('click', () => {
      handleMenuAction(option.action, input);
      menu.remove();
    });
    
    menu.appendChild(item);
  });
  
  // Fermer le menu si on clique ailleurs
  const closeHandler = (e) => {
    if (!menu.contains(e.target)) {
      menu.remove();
      document.removeEventListener('click', closeHandler);
    }
  };
  
  setTimeout(() => {
    document.addEventListener('click', closeHandler);
  }, 100);
  
  return menu;
}

/**
 * Gérer les actions du menu mot de passe
 */
async function handleMenuAction(action, input) {
  try {
    switch (action) {
      case 'fill':
        await fillPassword(input);
        break;
        
      case 'generate':
        await generateAndFillPassword(input);
        break;
        
      case 'save':
        await saveCurrentPassword(input);
        break;
    }
  } catch (error) {
    log('Erreur action menu:', error);
    showNotification('Erreur lors de l\'action');
  }
}

/**
 * Remplir le mot de passe existant
 */
async function fillPassword(input) {
  const response = await chrome.runtime.sendMessage({
    action: 'getPasswords',
    domain: contentState.currentDomain
  });
  
  if (response.success && response.passwords.length > 0) {
    const credential = response.passwords[0];
    input.value = credential.password || '';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    
    showNotification('Mot de passe rempli');
    log('Mot de passe rempli pour:', credential.title);
  } else {
    showNotification('Aucun mot de passe trouvé pour ce site');
  }
}

/**
 * Générer et remplir un nouveau mot de passe
 */
async function generateAndFillPassword(input) {
  const response = await chrome.runtime.sendMessage({
    action: 'generatePassword',
    options: {
      length: 16,
      include_uppercase: true,
      include_lowercase: true,
      include_numbers: true,
      include_symbols: true
    }
  });
  
  if (response.success) {
    input.value = response.password;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    
    showNotification('Nouveau mot de passe généré');
    log('Mot de passe généré et inséré');
  } else {
    showNotification('Erreur lors de la génération');
  }
}

/**
 * Sauvegarder le mot de passe actuel
 */
async function saveCurrentPassword(input) {
  const form = input.closest('form');
  if (!form) {
    showNotification('Impossible de trouver le formulaire');
    return;
  }
  
  // Trouver les champs du formulaire
  const usernameField = form.querySelector(CONTENT_CONFIG.SELECTORS.USERNAME);
  const passwordValue = input.value;
  const usernameValue = usernameField ? usernameField.value : '';
  
  if (!passwordValue) {
    showNotification('Aucun mot de passe à sauvegarder');
    return;
  }
  
  const passwordData = {
    title: `${contentState.currentDomain} - ${new Date().toLocaleDateString()}`,
    username: usernameValue,
    password: passwordValue,
    url: window.location.origin,
    category: 'Web',
    notes: `Sauvegardé depuis ${window.location.href}`
  };
  
  const response = await chrome.runtime.sendMessage({
    action: 'savePassword',
    passwordData: passwordData
  });
  
  if (response.success) {
    showNotification('Mot de passe sauvegardé');
    log('Mot de passe sauvegardé:', response.id);
  } else {
    showNotification('Erreur lors de la sauvegarde');
  }
}

/**
 * Afficher une notification
 */
function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'gmp-notification';
  notification.textContent = message;
  
  Object.assign(notification.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    backgroundColor: '#4f46e5',
    color: 'white',
    padding: '12px 20px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    zIndex: '10002',
    fontSize: '14px',
    fontWeight: '500',
    transform: 'translateX(100%)',
    transition: 'transform 0.3s ease'
  });
  
  document.body.appendChild(notification);
  
  // Animation d'entrée
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // Suppression automatique
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

/**
 * Détecter les formulaires de connexion
 */
function detectLoginForms() {
  const forms = document.querySelectorAll(CONTENT_CONFIG.SELECTORS.FORMS);
  let detectedCount = 0;
  
  forms.forEach(form => {
    const usernameFields = form.querySelectorAll(CONTENT_CONFIG.SELECTORS.USERNAME);
    const passwordFields = form.querySelectorAll(CONTENT_CONFIG.SELECTORS.PASSWORD);
    
    if (passwordFields.length > 0) {
      contentState.detectedForms.push({
        form: form,
        usernameFields: Array.from(usernameFields),
        passwordFields: Array.from(passwordFields)
      });
      
      detectedCount++;
      
      // Ajouter des icônes aux champs
      usernameFields.forEach(field => {
        createFieldIcon('USERNAME', field);
      });
      
      passwordFields.forEach(field => {
        createFieldIcon('PASSWORD', field);
      });
    }
  });
  
  if (detectedCount > 0) {
    log(`${detectedCount} formulaire(s) de connexion détecté(s)`);
  }
}

/**
 * Nettoyer les éléments injectés
 */
function cleanup() {
  contentState.injectedElements.forEach(element => {
    if (element.parentNode) {
      element.parentNode.removeChild(element);
    }
  });
  contentState.injectedElements = [];
  contentState.detectedForms = [];
}

/**
 * Actualiser la détection
 */
function refreshDetection() {
  cleanup();
  detectLoginForms();
}

// Messages du background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  log('Message reçu:', message.action);
  
  switch (message.action) {
    case 'fillCredentials':
      if (message.credentials) {
        const usernameField = document.querySelector(CONTENT_CONFIG.SELECTORS.USERNAME);
        const passwordField = document.querySelector(CONTENT_CONFIG.SELECTORS.PASSWORD);
        
        if (usernameField && message.credentials.username) {
          usernameField.value = message.credentials.username;
          usernameField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        if (passwordField && message.credentials.password) {
          passwordField.value = message.credentials.password;
          passwordField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        showNotification('Identifiants remplis');
      }
      break;
      
    case 'insertPassword':
      if (message.password) {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.type === 'password') {
          activeElement.value = message.password;
          activeElement.dispatchEvent(new Event('input', { bubbles: true }));
          showNotification('Mot de passe inséré');
        }
      }
      break;
      
    case 'requestSave':
      const activePasswordField = document.activeElement;
      if (activePasswordField && activePasswordField.type === 'password') {
        saveCurrentPassword(activePasswordField);
      }
      break;
      
    case 'refresh':
      refreshDetection();
      break;
      
    case 'logout':
      contentState.isAuthenticated = false;
      cleanup();
      break;
  }
  
  sendResponse({ success: true });
});

// Observer pour les changements DOM
const observer = new MutationObserver((mutations) => {
  let shouldRefresh = false;
  
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList') {
      // Vérifier si de nouveaux formulaires ont été ajoutés
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) { // Element node
          if (node.matches && node.matches('form')) {
            shouldRefresh = true;
          } else if (node.querySelector && node.querySelector('form')) {
            shouldRefresh = true;
          }
        }
      });
    }
  });
  
  if (shouldRefresh) {
    log('Changements DOM détectés, actualisation...');
    setTimeout(refreshDetection, 500);
  }
});

// Initialisation
function initialize() {
  log('Content script initialisé pour:', contentState.currentDomain);
  
  // Démarrer l'observation des changements DOM
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Détection initiale
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', detectLoginForms);
  } else {
    detectLoginForms();
  }
  
  // Vérifier l'état d'authentification
  chrome.runtime.sendMessage({ action: 'getState' }, (response) => {
    if (response && response.isAuthenticated) {
      contentState.isAuthenticated = true;
      log('Extension authentifiée');
    }
  });
}

// Nettoyage avant déchargement
window.addEventListener('beforeunload', cleanup);

// Démarrer l'initialisation
initialize();