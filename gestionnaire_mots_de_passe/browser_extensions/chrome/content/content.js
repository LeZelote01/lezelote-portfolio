/**
 * Content Script - Gestionnaire de Mots de Passe
 * Interaction avec les pages web pour auto-remplissage et détection
 */

// État du content script
const contentState = {
  isInitialized: false,
  detectedForms: [],
  currentDomain: window.location.hostname,
  lastFormCheck: 0
};

/**
 * Initialisation du content script
 */
(function initContentScript() {
  if (contentState.isInitialized) return;
  
  console.log('🚀 Content Script - Gestionnaire MDP initialisé');
  contentState.isInitialized = true;
  
  // Attendre que le DOM soit prêt
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupContentScript);
  } else {
    setupContentScript();
  }
})();

/**
 * Configuration du content script
 */
function setupContentScript() {
  try {
    // Scanner les formulaires existants
    scanForForms();
    
    // Observer les changements DOM
    setupDOMObserver();
    
    // Écouter les événements de formulaires
    setupFormListeners();
    
    // Ajouter les styles CSS
    injectStyles();
    
    console.log(`✅ Content Script configuré pour ${contentState.currentDomain}`);
    
  } catch (error) {
    console.error('❌ Erreur configuration content script:', error);
  }
}

/**
 * Scanner pour détecter les formulaires de connexion
 */
function scanForForms() {
  const forms = document.querySelectorAll('form');
  contentState.detectedForms = [];
  
  forms.forEach((form, index) => {
    const formData = analyzeForm(form);
    if (formData.isLoginForm) {
      contentState.detectedForms.push({
        id: `form_${index}`,
        element: form,
        ...formData
      });
      
      // Ajouter des indicateurs visuels
      addPasswordManagerIndicators(form, formData);
    }
  });
  
  if (contentState.detectedForms.length > 0) {
    console.log(`🔍 ${contentState.detectedForms.length} formulaire(s) de connexion détecté(s)`);
  }
  
  contentState.lastFormCheck = Date.now();
}

/**
 * Analyser un formulaire pour déterminer s'il s'agit d'une connexion
 */
function analyzeForm(form) {
  const inputs = form.querySelectorAll('input');
  let usernameField = null;
  let passwordField = null;
  let emailField = null;
  
  inputs.forEach(input => {
    const type = input.type.toLowerCase();
    const name = input.name.toLowerCase();
    const id = input.id.toLowerCase();
    const placeholder = (input.placeholder || '').toLowerCase();
    
    // Détection champ mot de passe
    if (type === 'password') {
      passwordField = input;
    }
    
    // Détection champ email
    else if (type === 'email' || 
             name.includes('email') || 
             id.includes('email') ||
             placeholder.includes('email')) {
      emailField = input;
    }
    
    // Détection champ nom d'utilisateur
    else if (type === 'text' && (
             name.includes('user') || 
             name.includes('login') ||
             name.includes('username') ||
             id.includes('user') ||
             id.includes('login') ||
             placeholder.includes('utilisateur') ||
             placeholder.includes('username'))) {
      usernameField = input;
    }
  });
  
  const isLoginForm = passwordField && (usernameField || emailField);
  
  return {
    isLoginForm,
    usernameField: usernameField || emailField,
    passwordField,
    formElement: form,
    domain: contentState.currentDomain
  };
}

/**
 * Ajouter des indicateurs visuels pour le gestionnaire de mots de passe
 */
function addPasswordManagerIndicators(form, formData) {
  // Ajouter l'icône sur le champ de mot de passe
  if (formData.passwordField) {
    addFieldIcon(formData.passwordField, 'password');
  }
  
  // Ajouter l'icône sur le champ utilisateur/email
  if (formData.usernameField) {
    addFieldIcon(formData.usernameField, 'username');
  }
}

/**
 * Ajouter une icône à un champ de saisie
 */
function addFieldIcon(field, type) {
  // Éviter les doublons
  if (field.dataset.gmpIconAdded) return;
  
  const wrapper = document.createElement('div');
  wrapper.className = 'gmp-field-wrapper';
  wrapper.style.position = 'relative';
  wrapper.style.display = 'inline-block';
  wrapper.style.width = '100%';
  
  const icon = document.createElement('div');
  icon.className = `gmp-field-icon gmp-${type}-icon`;
  icon.innerHTML = type === 'password' ? '🔐' : '👤';
  icon.title = type === 'password' ? 'Générer/Remplir mot de passe' : 'Remplir nom d\'utilisateur';
  
  // Style de l'icône
  Object.assign(icon.style, {
    position: 'absolute',
    right: '8px',
    top: '50%',
    transform: 'translateY(-50%)',
    cursor: 'pointer',
    fontSize: '16px',
    zIndex: '10000',
    background: 'white',
    padding: '2px',
    borderRadius: '3px',
    userSelect: 'none'
  });
  
  // Insérer le wrapper
  field.parentNode.insertBefore(wrapper, field);
  wrapper.appendChild(field);
  wrapper.appendChild(icon);
  
  // Événements de l'icône
  icon.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (type === 'password') {
      showPasswordMenu(field, icon);
    } else {
      fillUsernameFromSavedPasswords(field);
    }
  });
  
  field.dataset.gmpIconAdded = 'true';
}

/**
 * Afficher le menu contextuel pour les mots de passe
 */
function showPasswordMenu(passwordField, icon) {
  // Supprimer le menu existant
  const existingMenu = document.querySelector('.gmp-password-menu');
  if (existingMenu) {
    existingMenu.remove();
  }
  
  const menu = document.createElement('div');
  menu.className = 'gmp-password-menu';
  
  // Position du menu
  const iconRect = icon.getBoundingClientRect();
  Object.assign(menu.style, {
    position: 'fixed',
    top: `${iconRect.bottom + 5}px`,
    left: `${iconRect.left - 100}px`,
    background: 'white',
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    padding: '8px 0',
    zIndex: '99999',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
    minWidth: '200px'
  });
  
  // Options du menu
  const options = [
    { text: '🔐 Générer un mot de passe', action: 'generate' },
    { text: '📝 Remplir mot de passe sauvé', action: 'fill' },
    { text: '💾 Sauvegarder ce mot de passe', action: 'save' }
  ];
  
  options.forEach(option => {
    const item = document.createElement('div');
    item.textContent = option.text;
    item.style.cssText = `
      padding: 8px 16px;
      cursor: pointer;
      transition: background 0.2s;
    `;
    
    item.addEventListener('mouseover', () => {
      item.style.background = '#f0f0f0';
    });
    
    item.addEventListener('mouseout', () => {
      item.style.background = 'transparent';
    });
    
    item.addEventListener('click', async () => {
      menu.remove();
      await handlePasswordAction(option.action, passwordField);
    });
    
    menu.appendChild(item);
  });
  
  document.body.appendChild(menu);
  
  // Fermer le menu en cliquant ailleurs
  setTimeout(() => {
    document.addEventListener('click', function closeMenu(e) {
      if (!menu.contains(e.target)) {
        menu.remove();
        document.removeEventListener('click', closeMenu);
      }
    });
  }, 100);
}

/**
 * Gérer les actions du menu mot de passe
 */
async function handlePasswordAction(action, passwordField) {
  try {
    switch (action) {
      case 'generate':
        await generateAndFillPassword(passwordField);
        break;
        
      case 'fill':
        await fillSavedPassword(passwordField);
        break;
        
      case 'save':
        await saveCurrentPassword(passwordField);
        break;
    }
  } catch (error) {
    console.error('❌ Erreur action mot de passe:', error);
    showToast('Erreur: ' + error.message, 'error');
  }
}

/**
 * Générer et remplir un mot de passe
 */
async function generateAndFillPassword(passwordField) {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'generatePassword',
      data: { options: { length: 16 } }
    });
    
    if (response.success) {
      passwordField.value = response.data.password;
      passwordField.dispatchEvent(new Event('input', { bubbles: true }));
      passwordField.dispatchEvent(new Event('change', { bubbles: true }));
      
      showToast('Mot de passe généré avec succès!', 'success');
      
      // Proposer de sauvegarder
      setTimeout(() => {
        if (confirm('Voulez-vous sauvegarder ce mot de passe généré?')) {
          saveCurrentPassword(passwordField);
        }
      }, 1000);
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    console.error('❌ Erreur génération:', error);
    showToast('Erreur génération mot de passe', 'error');
  }
}

/**
 * Remplir avec un mot de passe sauvegardé
 */
async function fillSavedPassword(passwordField) {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getPasswords',
      data: { domain: contentState.currentDomain }
    });
    
    if (response.success && response.data.length > 0) {
      const passwords = response.data;
      
      if (passwords.length === 1) {
        // Un seul mot de passe - remplir directement
        await fillCredentials(passwords[0]);
        showToast('Identifiants remplis!', 'success');
      } else {
        // Plusieurs mots de passe - proposer le choix
        showPasswordSelection(passwords, passwordField);
      }
    } else {
      showToast('Aucun mot de passe sauvegardé pour ce site', 'info');
    }
  } catch (error) {
    console.error('❌ Erreur remplissage:', error);
    showToast('Erreur lors du remplissage', 'error');
  }
}

/**
 * Afficher la sélection de mots de passe multiples
 */
function showPasswordSelection(passwords, passwordField) {
  const modal = document.createElement('div');
  modal.className = 'gmp-password-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999999;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: Arial, sans-serif;
  `;
  
  const content = document.createElement('div');
  content.style.cssText = `
    background: white;
    border-radius: 12px;
    padding: 24px;
    max-width: 400px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  `;
  
  const title = document.createElement('h3');
  title.textContent = 'Choisir un mot de passe';
  title.style.cssText = 'margin: 0 0 16px 0; color: #333;';
  content.appendChild(title);
  
  passwords.forEach((pwd, index) => {
    const item = document.createElement('div');
    item.style.cssText = `
      padding: 12px;
      border: 1px solid #ddd;
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
    `;
    
    item.innerHTML = `
      <div style="font-weight: bold; color: #333;">${pwd.title}</div>
      <div style="color: #666; font-size: 12px;">${pwd.username || pwd.email}</div>
    `;
    
    item.addEventListener('mouseover', () => {
      item.style.background = '#f5f5f5';
      item.style.borderColor = '#007bff';
    });
    
    item.addEventListener('mouseout', () => {
      item.style.background = 'transparent';
      item.style.borderColor = '#ddd';
    });
    
    item.addEventListener('click', async () => {
      modal.remove();
      await fillCredentials(pwd);
      showToast('Identifiants remplis!', 'success');
    });
    
    content.appendChild(item);
  });
  
  // Bouton fermer
  const closeBtn = document.createElement('button');
  closeBtn.textContent = 'Fermer';
  closeBtn.style.cssText = `
    background: #6c757d;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    float: right;
    margin-top: 16px;
  `;
  
  closeBtn.addEventListener('click', () => modal.remove());
  content.appendChild(closeBtn);
  
  modal.appendChild(content);
  document.body.appendChild(modal);
  
  // Fermer en cliquant sur le fond
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}

/**
 * Remplir les identifiants dans le formulaire
 */
async function fillCredentials(passwordData) {
  const currentForm = findCurrentForm();
  if (!currentForm) {
    throw new Error('Formulaire non trouvé');
  }
  
  // Remplir le nom d'utilisateur/email
  if (currentForm.usernameField && passwordData.username) {
    currentForm.usernameField.value = passwordData.username;
    currentForm.usernameField.dispatchEvent(new Event('input', { bubbles: true }));
    currentForm.usernameField.dispatchEvent(new Event('change', { bubbles: true }));
  }
  
  // Remplir le mot de passe
  if (currentForm.passwordField && passwordData.password) {
    currentForm.passwordField.value = passwordData.password;
    currentForm.passwordField.dispatchEvent(new Event('input', { bubbles: true }));
    currentForm.passwordField.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

/**
 * Sauvegarder le mot de passe actuel
 */
async function saveCurrentPassword(passwordField) {
  try {
    const currentForm = findCurrentForm();
    if (!currentForm) {
      throw new Error('Formulaire non trouvé');
    }
    
    const title = prompt('Nom pour ce mot de passe:', document.title || contentState.currentDomain);
    if (!title) return;
    
    const username = currentForm.usernameField ? currentForm.usernameField.value : '';
    const password = passwordField.value;
    
    if (!password) {
      throw new Error('Aucun mot de passe à sauvegarder');
    }
    
    const response = await chrome.runtime.sendMessage({
      action: 'savePassword',
      data: {
        title,
        username,
        password,
        url: window.location.href,
        category: 'Web'
      }
    });
    
    if (response.success) {
      showToast('Mot de passe sauvegardé avec succès!', 'success');
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    console.error('❌ Erreur sauvegarde:', error);
    showToast('Erreur sauvegarde: ' + error.message, 'error');
  }
}

/**
 * Trouver le formulaire actuel
 */
function findCurrentForm() {
  return contentState.detectedForms.find(form => 
    document.contains(form.element)
  );
}

/**
 * Observer les changements DOM
 */
function setupDOMObserver() {
  const observer = new MutationObserver((mutations) => {
    let shouldRescan = false;
    
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.tagName === 'FORM' || node.querySelector('form')) {
              shouldRescan = true;
            }
          }
        });
      }
    });
    
    if (shouldRescan && Date.now() - contentState.lastFormCheck > 1000) {
      setTimeout(scanForForms, 500);
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

/**
 * Configuration des listeners de formulaires
 */
function setupFormListeners() {
  // Détecter les soumissions de formulaires
  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (form.tagName === 'FORM') {
      const formData = analyzeForm(form);
      if (formData.isLoginForm && formData.passwordField.value) {
        // Proposer de sauvegarder après un délai
        setTimeout(() => {
          if (confirm('Voulez-vous sauvegarder ce mot de passe?')) {
            saveCurrentPassword(formData.passwordField);
          }
        }, 2000);
      }
    }
  });
}

/**
 * Communication avec le background script
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  (async () => {
    try {
      const result = await handleContentMessage(request);
      sendResponse({ success: true, data: result });
    } catch (error) {
      console.error('❌ Erreur message content:', error);
      sendResponse({ success: false, error: error.message });
    }
  })();
  return true;
});

/**
 * Gestionnaire de messages pour le content script
 */
async function handleContentMessage(request) {
  const { action } = request;
  
  switch (action) {
    case 'fillPassword':
      await fillPasswordInActiveField(request.password);
      break;
      
    case 'fillCredentials':
      await fillCredentials({
        username: request.username,
        password: request.password
      });
      break;
      
    case 'detectCredentials':
      return detectCurrentCredentials();
      
    default:
      throw new Error(`Action non reconnue: ${action}`);
  }
}

/**
 * Remplir le mot de passe dans le champ actif
 */
async function fillPasswordInActiveField(password) {
  const activeElement = document.activeElement;
  if (activeElement && activeElement.type === 'password') {
    activeElement.value = password;
    activeElement.dispatchEvent(new Event('input', { bubbles: true }));
    activeElement.dispatchEvent(new Event('change', { bubbles: true }));
  } else {
    // Chercher le premier champ de mot de passe visible
    const passwordField = document.querySelector('input[type="password"]:not([style*="display: none"])');
    if (passwordField) {
      passwordField.value = password;
      passwordField.dispatchEvent(new Event('input', { bubbles: true }));
      passwordField.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
}

/**
 * Détecter les identifiants actuels
 */
function detectCurrentCredentials() {
  const currentForm = findCurrentForm();
  if (!currentForm) return null;
  
  return {
    username: currentForm.usernameField ? currentForm.usernameField.value : '',
    password: currentForm.passwordField ? currentForm.passwordField.value : '',
    url: window.location.href,
    title: document.title || contentState.currentDomain
  };
}

/**
 * Injecter les styles CSS
 */
function injectStyles() {
  if (document.getElementById('gmp-styles')) return;
  
  const styles = document.createElement('style');
  styles.id = 'gmp-styles';
  styles.textContent = `
    .gmp-field-wrapper {
      position: relative !important;
      display: inline-block !important;
    }
    
    .gmp-field-icon {
      transition: opacity 0.2s ease !important;
    }
    
    .gmp-field-icon:hover {
      opacity: 0.7 !important;
      transform: translateY(-50%) scale(1.1) !important;
    }
    
    .gmp-toast {
      position: fixed !important;
      top: 20px !important;
      right: 20px !important;
      background: white !important;
      border-radius: 8px !important;
      padding: 12px 16px !important;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
      z-index: 999999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
      max-width: 300px !important;
      animation: gmpSlideIn 0.3s ease !important;
    }
    
    .gmp-toast.success {
      border-left: 4px solid #28a745 !important;
    }
    
    .gmp-toast.error {
      border-left: 4px solid #dc3545 !important;
    }
    
    .gmp-toast.info {
      border-left: 4px solid #007bff !important;
    }
    
    @keyframes gmpSlideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes gmpSlideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  
  document.head.appendChild(styles);
}

/**
 * Afficher un toast de notification
 */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `gmp-toast ${type}`;
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'gmpSlideOut 0.3s ease';
    setTimeout(() => {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, 300);
  }, duration);
}

console.log('🔐 Content Script - Gestionnaire MDP chargé');