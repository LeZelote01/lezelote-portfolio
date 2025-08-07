// Gestionnaire de Mots de Passe - Content Script Firefox
// Compatible WebExtensions (identique à Chrome mais avec polyfill)

// Polyfill pour compatibilité Chrome
if (typeof browser === 'undefined') {
  window.browser = chrome;
}

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
    
    console.log('🔐 Gestionnaire MDP Firefox - Content script chargé');
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
          password: passwordFields[0],
          confirmPassword: passwordFields[1] || null
        }
      };
      
      this.forms.push(formData);
      this.addFormIndicator(formData);
    }
  }

  analyzeIsolatedInput(input) {
    const container = input.closest('div, section, main') || document.body;
    
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

    const text = form.textContent.toLowerCase();
    if (text.includes('créer un compte') || text.includes('s\'inscrire') || text.includes('register')) {
      return 'register';
    }
    
    return 'login';
  }

  findBestUsernameField(form, emailFields, usernameFields) {
    if (emailFields.length > 0) {
      return emailFields[0];
    }
    
    if (usernameFields.length > 0) {
      for (let field of usernameFields) {
        if (field.type !== 'password') {
          return field;
        }
      }
    }
    
    const allInputs = Array.from(form.querySelectorAll('input[type="text"], input[type="email"]'));
    const passwordField = form.querySelector('input[type="password"]');
    
    if (passwordField && allInputs.length > 0) {
      for (let i = allInputs.length - 1; i >= 0; i--) {
        const input = allInputs[i];
        const passwordRect = passwordField.getBoundingClientRect();
        const inputRect = input.getBoundingClientRect();
        
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
    
    const passwordField = formData.fields.password;
    
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
    
    const fieldRect = passwordField.getBoundingClientRect();
    const parentElement = passwordField.parentElement;
    
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

    formData.indicator = indicator;
  }

  addFormListeners() {
    document.addEventListener('focusin', (e) => {
      if (e.target.matches('input[type="password"], input[type="email"], input[name*="user"], input[name*="login"]')) {
        this.lastFocusedInput = e.target;
      }
    });

    document.addEventListener('submit', (e) => {
      this.handleFormSubmit(e);
    });
  }

  addMessageListener() {
    browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === 'fillPassword') {
        this.fillPassword(message.data);
        sendResponse({ success: true });
      }
      
      if (message.action === 'detectForms') {
        this.detectForms();
        sendResponse({ formsFound: this.forms.length });
      }
      
      if (message.action === 'insertPassword') {
        this.insertPassword(message.password);
        sendResponse({ success: true });
      }
    });
  }

  fillPassword(data) {
    const activeForm = this.findActiveForm();
    
    if (activeForm && activeForm.fields) {
      if (activeForm.fields.username && data.username) {
        this.setFieldValue(activeForm.fields.username, data.username);
      }
      
      if (activeForm.fields.password && data.password) {
        this.setFieldValue(activeForm.fields.password, data.password);
      }
      
      this.showFillAnimation(activeForm);
      console.log('✅ Mot de passe auto-rempli');
    } else {
      console.warn('⚠️ Aucun formulaire actif trouvé pour l\'auto-remplissage');
      
      if (this.lastFocusedInput) {
        this.setFieldValue(this.lastFocusedInput, data.password);
        console.log('✅ Champ focalisé rempli en fallback');
      }
    }
  }

  insertPassword(password) {
    // Pour l'insertion via menu contextuel
    if (this.lastFocusedInput) {
      this.setFieldValue(this.lastFocusedInput, password);
      this.showNotification('Mot de passe généré et inséré !', 'success');
    } else {
      // Chercher un champ password visible
      const passwordFields = document.querySelectorAll('input[type="password"]:not([style*="display: none"])');
      if (passwordFields.length > 0) {
        this.setFieldValue(passwordFields[0], password);
        this.showNotification('Mot de passe généré et inséré !', 'success');
      } else {
        this.showNotification('Aucun champ de mot de passe trouvé', 'error');
      }
    }
  }

  findActiveForm() {
    if (this.lastFocusedInput) {
      for (let form of this.forms) {
        if (form.fields.username === this.lastFocusedInput || 
            form.fields.password === this.lastFocusedInput) {
          return form;
        }
      }
    }
    
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
    
    field.focus();
    
    field.value = value;
    
    const inputEvent = new Event('input', { bubbles: true, cancelable: true });
    const changeEvent = new Event('change', { bubbles: true, cancelable: true });
    
    field.dispatchEvent(inputEvent);
    field.dispatchEvent(changeEvent);
    
    // Support React/Vue
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
    browser.runtime.sendMessage({
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
        browser.runtime.sendMessage({
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

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `password-manager-notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
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