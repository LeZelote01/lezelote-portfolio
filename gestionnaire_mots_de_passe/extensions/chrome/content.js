// Gestionnaire de Mots de Passe - Content Script Chrome
// Script injecté dans toutes les pages pour l'auto-remplissage

class PasswordManagerContent {
  constructor() {
    this.forms = [];
    this.lastFocusedInput = null;
    
    this.init();
  }

  init() {
    this.detectForms();
    this.addFormListeners();
    this.addMessageListener();
    
    // Re-détecter les forms sur changements DOM
    this.observeDOM();
    
    console.log('🔐 Gestionnaire MDP - Content script chargé');
  }

  detectForms() {
    this.forms = [];
    
    // Détecter tous les formulaires
    const forms = document.querySelectorAll('form');
    forms.forEach(form => this.analyzeForm(form));
    
    // Détecter les champs isolés (sans form parent)
    const isolatedInputs = document.querySelectorAll('input[type="password"], input[type="email"], input[name*="password"], input[name*="email"], input[name*="user"], input[name*="login"]');
    isolatedInputs.forEach(input => {
      if (!input.closest('form')) {
        this.analyzeIsolatedInput(input);
      }
    });

    console.log(`🔍 ${this.forms.length} formulaire(s) de connexion détecté(s)`);
  }

  analyzeForm(form) {
    const passwordFields = form.querySelectorAll('input[type="password"]');
    const emailFields = form.querySelectorAll('input[type="email"]');
    const usernameFields = form.querySelectorAll('input[name*="user"], input[name*="login"], input[name*="email"]');
    
    if (passwordFields.length > 0) {
      const formData = {
        element: form,
        type: this.getFormType(form),
        fields: {
          username: this.findBestUsernameField(form, emailFields, usernameFields),
          password: passwordFields[0], // Premier champ password
          confirmPassword: passwordFields[1] || null // Deuxième champ si présent
        }
      };
      
      this.forms.push(formData);
      this.addFormIndicator(formData);
    }
  }

  analyzeIsolatedInput(input) {
    const container = input.closest('div, section, main') || document.body;
    
    // Chercher d'autres champs dans le même conteneur
    const passwordField = input.type === 'password' ? input : 
      container.querySelector('input[type="password"]');
    
    const usernameField = input.type !== 'password' ? input :
      container.querySelector('input[type="email"], input[name*="user"], input[name*="login"]');

    if (passwordField) {
      const formData = {
        element: container,
        type: 'isolated',
        fields: {
          username: usernameField,
          password: passwordField,
          confirmPassword: null
        }
      };
      
      this.forms.push(formData);
      this.addFormIndicator(formData);
    }
  }

  getFormType(form) {
    const action = form.action.toLowerCase();
    const classes = form.className.toLowerCase();
    const id = form.id.toLowerCase();
    
    if (action.includes('register') || action.includes('signup') || 
        classes.includes('register') || classes.includes('signup') ||
        id.includes('register') || id.includes('signup')) {
      return 'register';
    }
    
    if (action.includes('login') || action.includes('signin') || 
        classes.includes('login') || classes.includes('signin') ||
        id.includes('login') || id.includes('signin')) {
      return 'login';
    }

    // Analyser le contenu des labels et textes
    const text = form.textContent.toLowerCase();
    if (text.includes('créer un compte') || text.includes('s\'inscrire') || text.includes('register')) {
      return 'register';
    }
    
    return 'login'; // Par défaut
  }

  findBestUsernameField(form, emailFields, usernameFields) {
    // Priorité aux champs email
    if (emailFields.length > 0) {
      return emailFields[0];
    }
    
    // Ensuite les champs username/login
    if (usernameFields.length > 0) {
      // Exclure les champs password
      for (let field of usernameFields) {
        if (field.type !== 'password') {
          return field;
        }
      }
    }
    
    // Chercher d'autres champs text avant le password
    const allInputs = Array.from(form.querySelectorAll('input[type="text"], input[type="email"]'));
    const passwordField = form.querySelector('input[type="password"]');
    
    if (passwordField && allInputs.length > 0) {
      // Retourner le dernier champ text avant le password
      for (let i = allInputs.length - 1; i >= 0; i--) {
        const input = allInputs[i];
        const passwordRect = passwordField.getBoundingClientRect();
        const inputRect = input.getBoundingClientRect();
        
        // Si le champ est au-dessus ou à gauche du password
        if (inputRect.top <= passwordRect.top) {
          return input;
        }
      }
      
      return allInputs[0];
    }
    
    return null;
  }

  addFormIndicator(formData) {
    if (!formData.fields.password) return;
    
    // Ajouter un indicateur visuel sur le champ password
    const passwordField = formData.fields.password;
    
    // Créer l'icône du gestionnaire
    const indicator = document.createElement('div');
    indicator.innerHTML = '🔐';
    indicator.className = 'password-manager-indicator';
    indicator.style.cssText = `
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 14px;
      cursor: pointer;
      z-index: 10000;
      user-select: none;
      opacity: 0.7;
      transition: opacity 0.3s;
      pointer-events: auto;
    `;
    
    indicator.title = 'Gestionnaire de mots de passe - Cliquez pour auto-remplir';
    
    // Positionner relativement au champ
    const fieldRect = passwordField.getBoundingClientRect();
    const parentElement = passwordField.parentElement;
    
    // S'assurer que le parent est positionné
    const parentStyle = window.getComputedStyle(parentElement);
    if (parentStyle.position === 'static') {
      parentElement.style.position = 'relative';
    }
    
    parentElement.appendChild(indicator);
    
    // Événements
    indicator.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.showPasswordManager(formData);
    });
    
    indicator.addEventListener('mouseenter', () => {
      indicator.style.opacity = '1';
    });
    
    indicator.addEventListener('mouseleave', () => {
      indicator.style.opacity = '0.7';
    });

    // Stocker la référence
    formData.indicator = indicator;
  }

  addFormListeners() {
    // Écouter les focus sur les champs de formulaire
    document.addEventListener('focusin', (e) => {
      if (e.target.matches('input[type="password"], input[type="email"], input[name*="user"], input[name*="login"]')) {
        this.lastFocusedInput = e.target;
      }
    });

    // Écouter les soumissions de formulaire pour la capture
    document.addEventListener('submit', (e) => {
      this.handleFormSubmit(e);
    });
  }

  addMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === 'fillPassword') {
        this.fillPassword(message.data);
        sendResponse({ success: true });
      }
      
      if (message.action === 'detectForms') {
        this.detectForms();
        sendResponse({ formsFound: this.forms.length });
      }
    });
  }

  fillPassword(data) {
    const activeForm = this.findActiveForm();
    
    if (activeForm && activeForm.fields) {
      // Remplir le nom d'utilisateur
      if (activeForm.fields.username && data.username) {
        this.setFieldValue(activeForm.fields.username, data.username);
      }
      
      // Remplir le mot de passe
      if (activeForm.fields.password && data.password) {
        this.setFieldValue(activeForm.fields.password, data.password);
      }
      
      // Animation de confirmation
      this.showFillAnimation(activeForm);
      
      console.log('✅ Mot de passe auto-rempli');
    } else {
      console.warn('⚠️ Aucun formulaire actif trouvé pour l\'auto-remplissage');
      
      // Essayer de remplir le dernier champ focalisé
      if (this.lastFocusedInput) {
        this.setFieldValue(this.lastFocusedInput, data.password);
        console.log('✅ Champ focalisé rempli en fallback');
      }
    }
  }

  findActiveForm() {
    // Trouver le formulaire contenant le champ actuellement focalisé
    if (this.lastFocusedInput) {
      for (let form of this.forms) {
        if (form.fields.username === this.lastFocusedInput || 
            form.fields.password === this.lastFocusedInput) {
          return form;
        }
      }
    }
    
    // Fallback : retourner le premier formulaire visible
    return this.forms.find(form => this.isFormVisible(form)) || this.forms[0];
  }

  isFormVisible(formData) {
    const element = formData.element;
    const rect = element.getBoundingClientRect();
    
    return rect.width > 0 && rect.height > 0 && 
           window.getComputedStyle(element).display !== 'none';
  }

  setFieldValue(field, value) {
    if (!field || !value) return;
    
    // Méthodes multiples pour s'assurer que la valeur est définie
    field.focus();
    
    // Méthode 1: Propriété value directe
    field.value = value;
    
    // Méthode 2: Dispatching d'événements
    const inputEvent = new Event('input', { bubbles: true, cancelable: true });
    const changeEvent = new Event('change', { bubbles: true, cancelable: true });
    
    field.dispatchEvent(inputEvent);
    field.dispatchEvent(changeEvent);
    
    // Méthode 3: React/Vue support
    if (field._valueTracker || field.__reactInternalInstance) {
      const descriptor = Object.getOwnPropertyDescriptor(field.constructor.prototype, 'value') || 
                        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
      
      if (descriptor && descriptor.set) {
        descriptor.set.call(field, value);
        field.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
    
    // Animation du champ
    field.style.transition = 'background-color 0.3s';
    field.style.backgroundColor = '#e8f5e8';
    setTimeout(() => {
      field.style.backgroundColor = '';
      setTimeout(() => {
        field.style.transition = '';
      }, 300);
    }, 1000);
  }

  showFillAnimation(formData) {
    const indicator = formData.indicator;
    if (indicator) {
      indicator.innerHTML = '✅';
      indicator.style.color = '#2ed573';
      
      setTimeout(() => {
        indicator.innerHTML = '🔐';
        indicator.style.color = '';
      }, 2000);
    }
  }

  showPasswordManager(formData) {
    // Envoyer un message au background script pour ouvrir le popup
    chrome.runtime.sendMessage({
      action: 'openPasswordManager',
      form: {
        type: formData.type,
        url: window.location.href
      }
    });
  }

  handleFormSubmit(event) {
    const form = event.target;
    const formData = this.forms.find(f => f.element === form);
    
    if (formData && formData.fields.username && formData.fields.password) {
      const username = formData.fields.username.value;
      const password = formData.fields.password.value;
      
      if (username && password) {
        // Envoyer au background pour potentielle sauvegarde
        chrome.runtime.sendMessage({
          action: 'formSubmitted',
          data: {
            url: window.location.href,
            title: document.title,
            username: username,
            formType: formData.type
          }
        });
      }
    }
  }

  observeDOM() {
    const observer = new MutationObserver((mutations) => {
      let shouldRedetect = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.matches('form') || node.querySelector('form') ||
                  node.matches('input[type="password"]') || node.querySelector('input[type="password"]')) {
                shouldRedetect = true;
              }
            }
          });
        }
      });
      
      if (shouldRedetect) {
        setTimeout(() => this.detectForms(), 500);
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
}

// Initialiser le content script
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new PasswordManagerContent();
  });
} else {
  new PasswordManagerContent();
}