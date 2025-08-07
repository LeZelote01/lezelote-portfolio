/**
 * JavaScript - Popup Extension Gestionnaire de Mots de Passe
 * Logique de l'interface utilisateur de l'extension
 */

// État de l'application
const appState = {
  isAuthenticated: false,
  isConnected: false,
  currentDomain: '',
  passwords: [],
  generatedPassword: null
};

// Éléments DOM
const elements = {
  // Écrans
  loginScreen: document.getElementById('loginScreen'),
  mainScreen: document.getElementById('mainScreen'),
  
  // Statut
  statusIndicator: document.getElementById('statusIndicator'),
  statusText: document.getElementById('statusText'),
  
  // Connexion
  masterPassword: document.getElementById('masterPassword'),
  togglePassword: document.getElementById('togglePassword'),
  loginBtn: document.getElementById('loginBtn'),
  
  // Actions rapides
  generateBtn: document.getElementById('generateBtn'),
  fillBtn: document.getElementById('fillBtn'),
  saveBtn: document.getElementById('saveBtn'),
  
  // Domaine et mots de passe
  currentDomain: document.getElementById('currentDomain'),
  passwordsList: document.getElementById('passwordsList'),
  refreshBtn: document.getElementById('refreshBtn'),
  
  // Générateur
  settingsBtn: document.getElementById('settingsBtn'),
  generatorOptions: document.getElementById('generatorOptions'),
  lengthSlider: document.getElementById('lengthSlider'),
  lengthValue: document.getElementById('lengthValue'),
  includeUpper: document.getElementById('includeUpper'),
  includeLower: document.getElementById('includeLower'),
  includeNumbers: document.getElementById('includeNumbers'),
  includeSymbols: document.getElementById('includeSymbols'),
  excludeAmbiguous: document.getElementById('excludeAmbiguous'),
  generatedPassword: document.getElementById('generatedPassword'),
  copyBtn: document.getElementById('copyBtn'),
  strengthFill: document.getElementById('strengthFill'),
  strengthText: document.getElementById('strengthText'),
  
  // Actions secondaires
  openAppBtn: document.getElementById('openAppBtn'),
  logoutBtn: document.getElementById('logoutBtn'),
  
  // Messages
  message: document.getElementById('message')
};

/**
 * Initialisation de l'extension
 */
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Popup Extension - Initialisation');
  
  try {
    await initializePopup();
    setupEventListeners();
    await checkAuthenticationStatus();
    await getCurrentDomain();
    
    console.log('✅ Popup Extension initialisée');
  } catch (error) {
    console.error('❌ Erreur initialisation popup:', error);
    showMessage('Erreur d\'initialisation', 'error');
  }
});

/**
 * Initialisation du popup
 */
async function initializePopup() {
  // Charger les préférences sauvegardées
  const preferences = await chrome.storage.local.get([
    'generatorLength',
    'includeUpper',
    'includeLower', 
    'includeNumbers',
    'includeSymbols',
    'excludeAmbiguous'
  ]);
  
  // Appliquer les préférences
  if (preferences.generatorLength) {
    elements.lengthSlider.value = preferences.generatorLength;
    elements.lengthValue.textContent = preferences.generatorLength;
  }
  
  elements.includeUpper.checked = preferences.includeUpper !== false;
  elements.includeLower.checked = preferences.includeLower !== false;
  elements.includeNumbers.checked = preferences.includeNumbers !== false;
  elements.includeSymbols.checked = preferences.includeSymbols !== false;
  elements.excludeAmbiguous.checked = preferences.excludeAmbiguous !== false;
}

/**
 * Configuration des événements
 */
function setupEventListeners() {
  // Connexion
  elements.togglePassword.addEventListener('click', togglePasswordVisibility);
  elements.masterPassword.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  });
  elements.loginBtn.addEventListener('click', handleLogin);
  
  // Actions rapides
  elements.generateBtn.addEventListener('click', handleQuickGenerate);
  elements.fillBtn.addEventListener('click', handleQuickFill);
  elements.saveBtn.addEventListener('click', handleQuickSave);
  
  // Mots de passe
  elements.refreshBtn.addEventListener('click', loadPasswordsForDomain);
  
  // Générateur
  elements.settingsBtn.addEventListener('click', toggleGeneratorSettings);
  elements.lengthSlider.addEventListener('input', updateLengthValue);
  
  // Sauvegarde des préférences du générateur
  [elements.includeUpper, elements.includeLower, elements.includeNumbers, 
   elements.includeSymbols, elements.excludeAmbiguous].forEach(checkbox => {
    checkbox.addEventListener('change', saveGeneratorPreferences);
  });
  
  elements.lengthSlider.addEventListener('change', saveGeneratorPreferences);
  
  // Autres actions
  elements.copyBtn.addEventListener('click', copyGeneratedPassword);
  elements.openAppBtn.addEventListener('click', openMainApplication);
  elements.logoutBtn.addEventListener('click', handleLogout);
}

/**
 * Vérifier le statut d'authentification
 */
async function checkAuthenticationStatus() {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'checkAuthentication'
    });
    
    if (response.success) {
      appState.isConnected = response.data.isConnected;
      appState.isAuthenticated = response.data.isAuthenticated;
      
      updateStatusDisplay();
      
      if (appState.isAuthenticated) {
        showMainScreen();
      } else {
        showLoginScreen();
      }
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    console.error('❌ Erreur vérification auth:', error);
    updateStatusDisplay(false);
    showLoginScreen();
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
      appState.currentDomain = url.hostname;
      elements.currentDomain.textContent = appState.currentDomain;
    }
  } catch (error) {
    console.error('❌ Erreur récupération domaine:', error);
    appState.currentDomain = 'Domaine inconnu';
    elements.currentDomain.textContent = appState.currentDomain;
  }
}

/**
 * Basculer la visibilité du mot de passe
 */
function togglePasswordVisibility() {
  const input = elements.masterPassword;
  const button = elements.togglePassword;
  
  if (input.type === 'password') {
    input.type = 'text';
    button.textContent = '🙈';
  } else {
    input.type = 'password';
    button.textContent = '👁️';
  }
}

/**
 * Gérer la connexion
 */
async function handleLogin() {
  const masterPassword = elements.masterPassword.value.trim();
  
  if (!masterPassword) {
    showMessage('Veuillez entrer votre mot de passe maître', 'error');
    return;
  }
  
  setLoginLoading(true);
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'authenticate',
      data: { masterPassword }
    });
    
    if (response.success) {
      appState.isAuthenticated = true;
      showMessage('Authentification réussie!', 'success');
      showMainScreen();
      await loadPasswordsForDomain();
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    console.error('❌ Erreur authentification:', error);
    showMessage('Échec de l\'authentification', 'error');
  } finally {
    setLoginLoading(false);
  }
}

/**
 * Configurer l'état de chargement de la connexion
 */
function setLoginLoading(isLoading) {
  elements.loginBtn.disabled = isLoading;
  elements.loginBtn.querySelector('.btn-text').style.display = isLoading ? 'none' : 'inline';
  elements.loginBtn.querySelector('.btn-loading').style.display = isLoading ? 'inline' : 'none';
}

/**
 * Afficher l'écran de connexion
 */
function showLoginScreen() {
  elements.loginScreen.style.display = 'block';
  elements.mainScreen.style.display = 'none';
  elements.masterPassword.focus();
}

/**
 * Afficher l'écran principal
 */
function showMainScreen() {
  elements.loginScreen.style.display = 'none';
  elements.mainScreen.style.display = 'block';
  updateStatusDisplay(true);
}

/**
 * Mettre à jour l'affichage du statut
 */
function updateStatusDisplay(connected = appState.isConnected) {
  if (connected && appState.isAuthenticated) {
    elements.statusIndicator.textContent = '🟢';
    elements.statusIndicator.className = 'status-indicator connected';
    elements.statusText.textContent = 'Connecté';
  } else if (connected) {
    elements.statusIndicator.textContent = '🟡';
    elements.statusIndicator.className = 'status-indicator connecting';
    elements.statusText.textContent = 'Non authentifié';
  } else {
    elements.statusIndicator.textContent = '🔴';
    elements.statusIndicator.className = 'status-indicator disconnected';
    elements.statusText.textContent = 'Déconnecté';
  }
}

/**
 * Charger les mots de passe pour le domaine actuel
 */
async function loadPasswordsForDomain() {
  if (!appState.currentDomain) {
    await getCurrentDomain();
  }
  
  elements.passwordsList.innerHTML = '<div class="loading">⏳ Chargement...</div>';
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getPasswords',
      data: { domain: appState.currentDomain }
    });
    
    if (response.success) {
      appState.passwords = response.data;
      displayPasswords(response.data);
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    console.error('❌ Erreur chargement mots de passe:', error);
    elements.passwordsList.innerHTML = 
      '<div class="empty-state">❌ Erreur de chargement</div>';
  }
}

/**
 * Afficher la liste des mots de passe
 */
function displayPasswords(passwords) {
  if (passwords.length === 0) {
    elements.passwordsList.innerHTML = 
      '<div class="empty-state">🔍 Aucun mot de passe pour ce domaine</div>';
    return;
  }
  
  elements.passwordsList.innerHTML = '';
  
  passwords.forEach(password => {
    const item = document.createElement('div');
    item.className = 'password-item';
    item.innerHTML = `
      <div class="password-info">
        <div class="password-title">${escapeHtml(password.title)}</div>
        <div class="password-username">${escapeHtml(password.username || password.email || 'Pas d\'utilisateur')}</div>
      </div>
      <div class="password-actions">
        <button class="icon-btn" title="Remplir" onclick="fillPassword('${password.id}')">📝</button>
        <button class="icon-btn" title="Copier" onclick="copyPasswordFromList('${password.id}')">📋</button>
      </div>
    `;
    
    elements.passwordsList.appendChild(item);
  });
}

/**
 * Actions rapides
 */
async function handleQuickGenerate() {
  try {
    const options = getGeneratorOptions();
    const response = await chrome.runtime.sendMessage({
      action: 'generatePassword',
      data: { options }
    });
    
    if (response.success) {
      appState.generatedPassword = response.data.password;
      elements.generatedPassword.value = response.data.password;
      updateStrengthIndicator(response.data.strength || 'strong');
      showMessage('Mot de passe généré!', 'success');
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    console.error('❌ Erreur génération:', error);
    showMessage('Erreur de génération', 'error');
  }
}

async function handleQuickFill() {
  if (appState.passwords.length === 0) {
    showMessage('Aucun mot de passe disponible', 'info');
    return;
  }
  
  // Utiliser le premier mot de passe disponible
  await fillPassword(appState.passwords[0].id);
}

async function handleQuickSave() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.sendMessage(tab.id, {
      action: 'detectCredentials'
    });
    
    showMessage('Détection des identifiants...', 'info');
  } catch (error) {
    console.error('❌ Erreur sauvegarde rapide:', error);
    showMessage('Erreur de sauvegarde', 'error');
  }
}

/**
 * Remplir un mot de passe spécifique
 */
async function fillPassword(passwordId) {
  try {
    const password = appState.passwords.find(p => p.id === passwordId);
    if (!password) {
      throw new Error('Mot de passe non trouvé');
    }
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.sendMessage(tab.id, {
      action: 'fillCredentials',
      username: password.username,
      password: password.password
    });
    
    showMessage('Identifiants remplis!', 'success');
    
    // Fermer le popup après un délai
    setTimeout(() => {
      window.close();
    }, 1500);
    
  } catch (error) {
    console.error('❌ Erreur remplissage:', error);
    showMessage('Erreur de remplissage', 'error');
  }
}

/**
 * Copier un mot de passe de la liste
 */
async function copyPasswordFromList(passwordId) {
  try {
    const password = appState.passwords.find(p => p.id === passwordId);
    if (!password) {
      throw new Error('Mot de passe non trouvé');
    }
    
    await navigator.clipboard.writeText(password.password);
    showMessage('Mot de passe copié!', 'success');
    
  } catch (error) {
    console.error('❌ Erreur copie:', error);
    showMessage('Erreur de copie', 'error');
  }
}

/**
 * Générateur de mot de passe
 */
function toggleGeneratorSettings() {
  const options = elements.generatorOptions;
  const isVisible = options.style.display !== 'none';
  options.style.display = isVisible ? 'none' : 'block';
  
  elements.settingsBtn.textContent = isVisible ? '⚙️' : '✖️';
}

function updateLengthValue() {
  elements.lengthValue.textContent = elements.lengthSlider.value;
}

function getGeneratorOptions() {
  return {
    length: parseInt(elements.lengthSlider.value),
    include_uppercase: elements.includeUpper.checked,
    include_lowercase: elements.includeLower.checked,
    include_numbers: elements.includeNumbers.checked,
    include_symbols: elements.includeSymbols.checked,
    exclude_ambiguous: elements.excludeAmbiguous.checked
  };
}

async function saveGeneratorPreferences() {
  const preferences = {
    generatorLength: elements.lengthSlider.value,
    includeUpper: elements.includeUpper.checked,
    includeLower: elements.includeLower.checked,
    includeNumbers: elements.includeNumbers.checked,
    includeSymbols: elements.includeSymbols.checked,
    excludeAmbiguous: elements.excludeAmbiguous.checked
  };
  
  await chrome.storage.local.set(preferences);
}

function updateStrengthIndicator(strength) {
  const strengthMap = {
    'weak': { class: 'weak', text: 'Faible' },
    'fair': { class: 'fair', text: 'Moyen' },
    'good': { class: 'good', text: 'Bon' },
    'strong': { class: 'strong', text: 'Fort' }
  };
  
  const strengthInfo = strengthMap[strength] || strengthMap['good'];
  
  elements.strengthFill.className = `strength-fill ${strengthInfo.class}`;
  elements.strengthText.textContent = strengthInfo.text;
}

async function copyGeneratedPassword() {
  if (!appState.generatedPassword) {
    showMessage('Aucun mot de passe à copier', 'info');
    return;
  }
  
  try {
    await navigator.clipboard.writeText(appState.generatedPassword);
    showMessage('Mot de passe copié!', 'success');
  } catch (error) {
    console.error('❌ Erreur copie:', error);
    showMessage('Erreur de copie', 'error');
  }
}

/**
 * Actions secondaires
 */
async function openMainApplication() {
  try {
    // Tenter d'ouvrir l'application principale
    const url = 'http://localhost:8002'; // Port de l'API
    await chrome.tabs.create({ url });
    
    showMessage('Ouverture de l\'application...', 'info');
    
    setTimeout(() => {
      window.close();
    }, 1000);
    
  } catch (error) {
    console.error('❌ Erreur ouverture app:', error);
    showMessage('Impossible d\'ouvrir l\'application', 'error');
  }
}

async function handleLogout() {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'logout'
    });
    
    if (response.success) {
      appState.isAuthenticated = false;
      appState.passwords = [];
      elements.masterPassword.value = '';
      
      showMessage('Déconnexion réussie', 'info');
      showLoginScreen();
      updateStatusDisplay(false);
    }
  } catch (error) {
    console.error('❌ Erreur déconnexion:', error);
    showMessage('Erreur de déconnexion', 'error');
  }
}

/**
 * Utilitaires
 */
function showMessage(text, type = 'info', duration = 3000) {
  elements.message.textContent = text;
  elements.message.className = `message ${type}`;
  elements.message.style.display = 'block';
  
  setTimeout(() => {
    elements.message.style.display = 'none';
  }, duration);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Fonctions globales pour les événements inline
window.fillPassword = fillPassword;
window.copyPasswordFromList = copyPasswordFromList;

console.log('🔐 Popup Script - Gestionnaire MDP chargé');