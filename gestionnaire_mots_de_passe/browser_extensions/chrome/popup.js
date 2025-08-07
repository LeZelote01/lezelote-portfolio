/**
 * Popup Script - Gestionnaire de Mots de Passe
 * Interface utilisateur principale de l'extension
 */

// Configuration
const POPUP_CONFIG = {
  DEBUG: true,
  REFRESH_INTERVAL: 30000, // 30 secondes
  PASSWORD_STRENGTH: {
    WEAK: { min: 0, max: 25, class: 'weak', text: 'Faible' },
    MEDIUM: { min: 26, max: 50, class: 'medium', text: 'Moyen' },
    GOOD: { min: 51, max: 75, class: 'good', text: 'Bon' },
    STRONG: { min: 76, max: 100, class: 'strong', text: 'Fort' }
  }
};

// État de l'interface
let popupState = {
  isAuthenticated: false,
  currentDomain: '',
  passwords: [],
  generatorExpanded: false,
  refreshTimer: null
};

// Éléments DOM
let elements = {};

// Logging utilitaire
function log(...args) {
  if (POPUP_CONFIG.DEBUG) {
    console.log('🖥️ GMP Popup:', ...args);
  }
}

/**
 * Initialiser l'interface popup
 */
function initializePopup() {
  log('Initialisation du popup');
  
  // Récupérer les références des éléments DOM
  elements = {
    // Écrans
    loginScreen: document.getElementById('login-screen'),
    mainScreen: document.getElementById('main-screen'),
    
    // Connexion
    masterPasswordInput: document.getElementById('master-password'),
    loginBtn: document.getElementById('login-btn'),
    loginError: document.getElementById('login-error'),
    
    // Status
    status: document.getElementById('status'),
    statusText: document.getElementById('status-text'),
    apiStatus: document.getElementById('api-status'),
    
    // Actions rapides
    generateBtn: document.getElementById('generate-btn'),
    fillBtn: document.getElementById('fill-btn'),
    saveBtn: document.getElementById('save-btn'),
    
    // Domaine
    domainName: document.getElementById('domain-name'),
    refreshBtn: document.getElementById('refresh-btn'),
    domainPasswords: document.getElementById('domain-passwords'),
    
    // Générateur
    generatorToggle: document.getElementById('generator-toggle'),
    generatorContent: document.getElementById('generator-content'),
    lengthSlider: document.getElementById('length-slider'),
    lengthValue: document.getElementById('length-value'),
    uppercaseCheck: document.getElementById('uppercase-check'),
    lowercaseCheck: document.getElementById('lowercase-check'),
    numbersCheck: document.getElementById('numbers-check'),
    symbolsCheck: document.getElementById('symbols-check'),
    generatedPassword: document.getElementById('generated-password'),
    copyPassword: document.getElementById('copy-password'),
    strengthFill: document.getElementById('strength-fill'),
    strengthText: document.getElementById('strength-text'),
    generateAdvancedBtn: document.getElementById('generate-advanced-btn'),
    
    // Footer
    openAppBtn: document.getElementById('open-app-btn'),
    logoutBtn: document.getElementById('logout-btn')
  };
  
  // Ajouter les événements
  attachEventListeners();
  
  // Vérifier l'état d'authentification
  checkAuthenticationStatus();
  
  // Obtenir le domaine actuel
  getCurrentDomain();
  
  // Vérifier la santé de l'API
  checkApiHealth();
}

/**
 * Attacher les événements
 */
function attachEventListeners() {
  // Connexion
  elements.loginBtn.addEventListener('click', handleLogin);
  elements.masterPasswordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  });
  
  // Actions rapides
  elements.generateBtn.addEventListener('click', handleQuickGenerate);
  elements.fillBtn.addEventListener('click', handleQuickFill);
  elements.saveBtn.addEventListener('click', handleQuickSave);
  
  // Domaine
  elements.refreshBtn.addEventListener('click', refreshDomainPasswords);
  
  // Générateur
  elements.generatorToggle.addEventListener('click', toggleGenerator);
  elements.lengthSlider.addEventListener('input', updateLengthValue);
  elements.generateAdvancedBtn.addEventListener('click', generateAdvancedPassword);
  elements.copyPassword.addEventListener('click', copyGeneratedPassword);
  
  // Footer
  elements.openAppBtn.addEventListener('click', openMainApp);
  elements.logoutBtn.addEventListener('click', handleLogout);
  
  // Vérification santé API périodique
  setInterval(checkApiHealth, 10000); // Chaque 10 secondes
}

/**
 * Vérifier l'état d'authentification
 */
async function checkAuthenticationStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getState' });
    
    if (response && response.isAuthenticated) {
      showMainScreen();
      refreshDomainPasswords();
    } else {
      showLoginScreen();
    }
  } catch (error) {
    log('Erreur vérification état:', error);
    showLoginScreen();
  }
}

/**
 * Gérer la connexion
 */
async function handleLogin() {
  const masterPassword = elements.masterPasswordInput.value.trim();
  
  if (!masterPassword) {
    showError('Veuillez entrer votre mot de passe maître');
    return;
  }
  
  // Afficher l'état de chargement
  setLoginLoading(true);
  hideError();
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'authenticate',
      masterPassword: masterPassword
    });
    
    if (response.success) {
      log('Authentification réussie');
      showMainScreen();
      refreshDomainPasswords();
    } else {
      showError(response.error || 'Échec de l\'authentification');
    }
  } catch (error) {
    log('Erreur authentification:', error);
    showError('Impossible de se connecter');
  } finally {
    setLoginLoading(false);
  }
}

/**
 * Gérer la déconnexion
 */
async function handleLogout() {
  try {
    await chrome.runtime.sendMessage({ action: 'logout' });
    popupState.isAuthenticated = false;
    popupState.passwords = [];
    showLoginScreen();
    log('Déconnexion effectuée');
  } catch (error) {
    log('Erreur déconnexion:', error);
  }
}

/**
 * Obtenir le domaine actuel
 */
async function getCurrentDomain() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
      const url = new URL(tab.url);
      popupState.currentDomain = url.hostname;
      elements.domainName.textContent = popupState.currentDomain;
      log('Domaine actuel:', popupState.currentDomain);
    }
  } catch (error) {
    log('Erreur récupération domaine:', error);
    elements.domainName.textContent = 'Domaine non disponible';
  }
}

/**
 * Actualiser les mots de passe du domaine
 */
async function refreshDomainPasswords() {
  if (!popupState.currentDomain) {
    await getCurrentDomain();
  }
  
  // Afficher l'état de chargement
  elements.domainPasswords.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <span>Chargement des mots de passe...</span>
    </div>
  `;
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getPasswords',
      domain: popupState.currentDomain
    });
    
    if (response.success) {
      popupState.passwords = response.passwords;
      displayDomainPasswords(response.passwords);
      log(`${response.passwords.length} mots de passe trouvés`);
    } else {
      showPasswordsError(response.error || 'Erreur de récupération');
    }
  } catch (error) {
    log('Erreur actualisation mots de passe:', error);
    showPasswordsError('Erreur de connexion');
  }
}

/**
 * Afficher les mots de passe du domaine
 */
function displayDomainPasswords(passwords) {
  if (passwords.length === 0) {
    elements.domainPasswords.innerHTML = `
      <div class="empty-state">
        <div class="icon">🔍</div>
        <div>Aucun mot de passe pour ce site</div>
      </div>
    `;
    return;
  }
  
  const passwordsHtml = passwords.map(password => `
    <div class="password-item" data-id="${password.id}">
      <div class="password-info">
        <div class="password-title">${escapeHtml(password.title)}</div>
        <div class="password-username">${escapeHtml(password.username || 'Pas de nom d\'utilisateur')}</div>
      </div>
      <div class="password-actions">
        <button class="action-icon-btn fill-action" onclick="fillPassword('${password.id}')" title="Remplir">
          📝
        </button>
        <button class="action-icon-btn copy-action" onclick="copyPassword('${password.id}')" title="Copier">
          📋
        </button>
      </div>
    </div>
  `).join('');
  
  elements.domainPasswords.innerHTML = passwordsHtml;
}

/**
 * Remplir un mot de passe spécifique
 */
async function fillPassword(passwordId) {
  try {
    const password = popupState.passwords.find(p => p.id === passwordId);
    if (!password) {
      showNotification('Mot de passe introuvable');
      return;
    }
    
    // Envoyer au content script
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.sendMessage(tab.id, {
      action: 'fillCredentials',
      credentials: password
    });
    
    showNotification('Identifiants remplis');
    window.close();
  } catch (error) {
    log('Erreur remplissage:', error);
    showNotification('Erreur lors du remplissage');
  }
}

/**
 * Copier un mot de passe dans le presse-papier
 */
async function copyPassword(passwordId) {
  try {
    const password = popupState.passwords.find(p => p.id === passwordId);
    if (!password) {
      showNotification('Mot de passe introuvable');
      return;
    }
    
    // Utiliser l'API Clipboard si disponible
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(password.password);
    } else {
      // Fallback pour les anciens navigateurs
      const textArea = document.createElement('textarea');
      textArea.value = password.password;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
    
    showNotification('Mot de passe copié');
  } catch (error) {
    log('Erreur copie:', error);
    showNotification('Erreur lors de la copie');
  }
}

/**
 * Actions rapides
 */
async function handleQuickGenerate() {
  try {
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
      // Insérer dans la page
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.tabs.sendMessage(tab.id, {
        action: 'insertPassword',
        password: response.password
      });
      
      showNotification('Mot de passe généré et inséré');
      window.close();
    } else {
      showNotification('Erreur lors de la génération');
    }
  } catch (error) {
    log('Erreur génération rapide:', error);
    showNotification('Erreur de connexion');
  }
}

async function handleQuickFill() {
  if (popupState.passwords.length > 0) {
    await fillPassword(popupState.passwords[0].id);
  } else {
    showNotification('Aucun mot de passe disponible');
  }
}

async function handleQuickSave() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.sendMessage(tab.id, { action: 'requestSave' });
    showNotification('Demande de sauvegarde envoyée');
    window.close();
  } catch (error) {
    log('Erreur sauvegarde rapide:', error);
    showNotification('Erreur lors de la sauvegarde');
  }
}

/**
 * Générateur avancé
 */
function toggleGenerator() {
  popupState.generatorExpanded = !popupState.generatorExpanded;
  
  if (popupState.generatorExpanded) {
    elements.generatorContent.classList.remove('hidden');
    elements.generatorToggle.classList.add('expanded');
  } else {
    elements.generatorContent.classList.add('hidden');
    elements.generatorToggle.classList.remove('expanded');
  }
}

function updateLengthValue() {
  elements.lengthValue.textContent = elements.lengthSlider.value;
}

async function generateAdvancedPassword() {
  const options = {
    length: parseInt(elements.lengthSlider.value),
    include_uppercase: elements.uppercaseCheck.checked,
    include_lowercase: elements.lowercaseCheck.checked,
    include_numbers: elements.numbersCheck.checked,
    include_symbols: elements.symbolsCheck.checked
  };
  
  // Vérifier qu'au moins une option est cochée
  if (!Object.values(options).slice(1).some(Boolean)) {
    showNotification('Sélectionnez au moins un type de caractère');
    return;
  }
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'generatePassword',
      options: options
    });
    
    if (response.success) {
      elements.generatedPassword.value = response.password;
      updateStrengthMeter(response.password);
      log('Mot de passe généré avec succès');
    } else {
      showNotification('Erreur lors de la génération');
    }
  } catch (error) {
    log('Erreur génération avancée:', error);
    showNotification('Erreur de connexion');
  }
}

async function copyGeneratedPassword() {
  const password = elements.generatedPassword.value;
  
  if (!password) {
    showNotification('Générez d\'abord un mot de passe');
    return;
  }
  
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(password);
    } else {
      elements.generatedPassword.select();
      document.execCommand('copy');
    }
    
    showNotification('Mot de passe copié');
  } catch (error) {
    log('Erreur copie mot de passe généré:', error);
    showNotification('Erreur lors de la copie');
  }
}

/**
 * Calculer la force d'un mot de passe
 */
function calculatePasswordStrength(password) {
  if (!password) return 0;
  
  let score = 0;
  
  // Longueur
  if (password.length >= 8) score += 20;
  if (password.length >= 12) score += 10;
  if (password.length >= 16) score += 10;
  
  // Types de caractères
  if (/[a-z]/.test(password)) score += 15;
  if (/[A-Z]/.test(password)) score += 15;
  if (/[0-9]/.test(password)) score += 15;
  if (/[^A-Za-z0-9]/.test(password)) score += 15;
  
  return Math.min(score, 100);
}

/**
 * Mettre à jour l'indicateur de force
 */
function updateStrengthMeter(password) {
  const strength = calculatePasswordStrength(password);
  
  let strengthInfo = POPUP_CONFIG.PASSWORD_STRENGTH.WEAK;
  
  for (const [key, info] of Object.entries(POPUP_CONFIG.PASSWORD_STRENGTH)) {
    if (strength >= info.min && strength <= info.max) {
      strengthInfo = info;
      break;
    }
  }
  
  elements.strengthFill.style.width = `${strength}%`;
  elements.strengthFill.className = `strength-fill ${strengthInfo.class}`;
  elements.strengthText.textContent = `${strengthInfo.text} (${strength}%)`;
}

/**
 * Vérifier la santé de l'API
 */
async function checkApiHealth() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'checkHealth' });
    
    if (response.success && response.healthy) {
      elements.apiStatus.classList.add('healthy');
      elements.apiStatus.title = 'API disponible';
    } else {
      elements.apiStatus.classList.remove('healthy');
      elements.apiStatus.title = 'API non disponible';
    }
  } catch (error) {
    elements.apiStatus.classList.remove('healthy');
    elements.apiStatus.title = 'API non disponible';
  }
}

/**
 * Ouvrir l'application principale
 */
function openMainApp() {
  chrome.tabs.create({ url: 'http://localhost:8002' });
  window.close();
}

/**
 * Interface utilisateur - Utilitaires
 */
function showLoginScreen() {
  elements.loginScreen.classList.remove('hidden');
  elements.mainScreen.classList.add('hidden');
  elements.status.classList.remove('connected');
  elements.status.classList.add('disconnected');
  elements.statusText.textContent = 'Déconnecté';
  elements.masterPasswordInput.focus();
}

function showMainScreen() {
  elements.loginScreen.classList.add('hidden');
  elements.mainScreen.classList.remove('hidden');
  elements.status.classList.add('connected');
  elements.status.classList.remove('disconnected');
  elements.statusText.textContent = 'Connecté';
  popupState.isAuthenticated = true;
}

function setLoginLoading(loading) {
  if (loading) {
    elements.loginBtn.querySelector('.btn-text').style.display = 'none';
    elements.loginBtn.querySelector('.btn-loader').classList.remove('hidden');
    elements.loginBtn.disabled = true;
    elements.status.classList.add('connecting');
    elements.statusText.textContent = 'Connexion...';
  } else {
    elements.loginBtn.querySelector('.btn-text').style.display = 'inline';
    elements.loginBtn.querySelector('.btn-loader').classList.add('hidden');
    elements.loginBtn.disabled = false;
    elements.status.classList.remove('connecting');
  }
}

function showError(message) {
  elements.loginError.textContent = message;
  elements.loginError.classList.remove('hidden');
}

function hideError() {
  elements.loginError.classList.add('hidden');
}

function showPasswordsError(message) {
  elements.domainPasswords.innerHTML = `
    <div class="empty-state">
      <div class="icon">❌</div>
      <div>${escapeHtml(message)}</div>
    </div>
  `;
}

function showNotification(message) {
  // Créer une notification temporaire
  const notification = document.createElement('div');
  notification.className = 'success-message';
  notification.textContent = message;
  notification.style.position = 'fixed';
  notification.style.top = '10px';
  notification.style.left = '10px';
  notification.style.right = '10px';
  notification.style.zIndex = '10000';
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 3000);
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

// Rendre les fonctions globales pour les événements onclick
window.fillPassword = fillPassword;
window.copyPassword = copyPassword;

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', initializePopup);

log('Popup script chargé');