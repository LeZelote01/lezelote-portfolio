/**
 * Inject Script - Gestionnaire de Mots de Passe
 * Script injecté dans le contexte de la page pour les interactions avancées
 */

// Éviter les injections multiples
if (!window.gmpInjected) {
  window.gmpInjected = true;

  // Configuration
  const INJECT_CONFIG = {
    DEBUG: true,
    STORAGE_KEY: 'gmp_form_data',
    DETECTION_DELAY: 1000
  };

  // État de l'injection
  let injectState = {
    forms: new Map(),
    observer: null,
    isActive: false
  };

  // Logging utilitaire  
  function log(...args) {
    if (INJECT_CONFIG.DEBUG) {
      console.log('💉 GMP Inject:', ...args);
    }
  }

  /**
   * Analyser un formulaire pour extraire ses métadonnées
   */
  function analyzeForm(form) {
    const formData = {
      id: form.id || generateFormId(form),
      action: form.action || window.location.href,
      method: form.method || 'GET',
      fields: [],
      isLoginForm: false,
      confidence: 0
    };

    // Analyser tous les champs input
    const inputs = form.querySelectorAll('input');
    inputs.forEach((input, index) => {
      if (input.type === 'hidden') return;

      const field = {
        index,
        type: input.type,
        name: input.name || `field_${index}`,
        id: input.id || `field_${index}`,
        placeholder: input.placeholder || '',
        autocomplete: input.autocomplete || '',
        required: input.required,
        value: input.value,
        labels: getFieldLabels(input)
      };

      // Classifier le champ
      field.classification = classifyField(field);
      
      formData.fields.push(field);

      // Calculer la confiance pour les formulaires de connexion
      if (field.classification.includes('username') || field.classification.includes('email')) {
        formData.confidence += 30;
      }
      if (field.type === 'password') {
        formData.confidence += 40;
        formData.isLoginForm = true;
      }
    });

    // Analyser les boutons de soumission
    const submitButtons = form.querySelectorAll('input[type="submit"], button[type="submit"], button:not([type])');
    formData.submitButtons = Array.from(submitButtons).map(btn => ({
      text: btn.textContent || btn.value || 'Submit',
      type: btn.type || 'submit'
    }));

    // Ajuster la confiance basée sur les boutons
    const buttonText = formData.submitButtons.map(btn => btn.text.toLowerCase()).join(' ');
    if (buttonText.includes('login') || buttonText.includes('sign in') || buttonText.includes('connect')) {
      formData.confidence += 20;
    }

    return formData;
  }

  /**
   * Générer un ID unique pour un formulaire
   */
  function generateFormId(form) {
    const formString = form.outerHTML.substring(0, 100);
    let hash = 0;
    for (let i = 0; i < formString.length; i++) {
      const char = formString.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convertir en 32bit integer
    }
    return `form_${Math.abs(hash)}`;
  }

  /**
   * Obtenir les labels associés à un champ
   */
  function getFieldLabels(input) {
    const labels = [];
    
    // Label explicite via l'attribut for
    if (input.id) {
      const explicitLabel = document.querySelector(`label[for="${input.id}"]`);
      if (explicitLabel) {
        labels.push(explicitLabel.textContent.trim());
      }
    }
    
    // Label parent
    const parentLabel = input.closest('label');
    if (parentLabel) {
      labels.push(parentLabel.textContent.replace(input.value, '').trim());
    }
    
    // Labels par proximité (siblings précédents)
    let prev = input.previousElementSibling;
    while (prev && labels.length < 2) {
      if (prev.tagName === 'LABEL' || prev.tagName === 'SPAN') {
        const text = prev.textContent.trim();
        if (text.length > 0 && text.length < 50) {
          labels.push(text);
        }
      }
      prev = prev.previousElementSibling;
    }

    return labels.filter((label, index, array) => array.indexOf(label) === index);
  }

  /**
   * Classifier un champ de formulaire
   */
  function classifyField(field) {
    const classifications = [];
    const allText = [
      field.name,
      field.id,
      field.placeholder,
      field.autocomplete,
      ...field.labels
    ].join(' ').toLowerCase();

    // Classification par type
    if (field.type === 'password') {
      classifications.push('password');
    } else if (field.type === 'email') {
      classifications.push('email', 'username');
    } else if (field.type === 'text' || field.type === '') {
      // Classification par contenu textuel
      if (allText.match(/email|e-mail|mail/)) {
        classifications.push('email', 'username');
      } else if (allText.match(/user|login|account|username|identifier/)) {
        classifications.push('username');
      } else if (allText.match(/phone|tel|mobile/)) {
        classifications.push('phone');
      } else if (allText.match(/name|nom|prenom|firstname|lastname/)) {
        classifications.push('name');
      } else {
        classifications.push('text');
      }
    }

    // Classification par autocomplete
    if (field.autocomplete) {
      if (field.autocomplete.includes('username')) {
        classifications.push('username');
      } else if (field.autocomplete.includes('email')) {
        classifications.push('email', 'username');
      } else if (field.autocomplete.includes('current-password')) {
        classifications.push('password', 'current');
      } else if (field.autocomplete.includes('new-password')) {
        classifications.push('password', 'new');
      }
    }

    return [...new Set(classifications)];
  }

  /**
   * Sauvegarder les données d'un formulaire
   */
  function saveFormData(form, formData) {
    try {
      // Données à sauvegarder (sans mots de passe)
      const safeData = {
        ...formData,
        fields: formData.fields.map(field => ({
          ...field,
          value: field.classification.includes('password') ? '' : field.value
        })),
        timestamp: Date.now(),
        url: window.location.href,
        domain: window.location.hostname
      };

      // Sauvegarder dans le localStorage
      const key = `${INJECT_CONFIG.STORAGE_KEY}_${formData.id}`;
      localStorage.setItem(key, JSON.stringify(safeData));
      
      log('Données de formulaire sauvegardées:', formData.id);
    } catch (error) {
      log('Erreur sauvegarde données formulaire:', error);
    }
  }

  /**
   * Surveiller les changements dans un formulaire
   */
  function monitorForm(form, formData) {
    // Surveiller les changements de valeur
    form.addEventListener('input', (e) => {
      if (e.target.tagName === 'INPUT') {
        log('Changement détecté dans le formulaire:', formData.id);
        
        // Mettre à jour les données si ce n'est pas un champ de mot de passe
        if (e.target.type !== 'password') {
          const field = formData.fields.find(f => f.name === e.target.name || f.id === e.target.id);
          if (field) {
            field.value = e.target.value;
            saveFormData(form, formData);
          }
        }
      }
    });

    // Surveiller la soumission
    form.addEventListener('submit', (e) => {
      log('Soumission de formulaire:', formData.id);
      
      // Mettre à jour toutes les valeurs avant soumission
      formData.fields.forEach((field, index) => {
        const input = form.elements[field.name] || form.elements[index];
        if (input && input.type !== 'password') {
          field.value = input.value;
        }
      });
      
      saveFormData(form, formData);
      
      // Envoyer un événement au content script
      window.dispatchEvent(new CustomEvent('gmp-form-submit', {
        detail: { formId: formData.id, formData: formData }
      }));
    });
  }

  /**
   * Détecter et analyser tous les formulaires
   */
  function detectForms() {
    const forms = document.querySelectorAll('form');
    let newFormsCount = 0;

    forms.forEach(form => {
      const formData = analyzeForm(form);
      
      if (!injectState.forms.has(formData.id)) {
        injectState.forms.set(formData.id, formData);
        newFormsCount++;
        
        log('Nouveau formulaire détecté:', {
          id: formData.id,
          isLoginForm: formData.isLoginForm,
          confidence: formData.confidence,
          fields: formData.fields.length
        });
        
        // Surveiller uniquement les formulaires de connexion probables
        if (formData.isLoginForm && formData.confidence > 50) {
          monitorForm(form, formData);
          saveFormData(form, formData);
        }
      }
    });

    if (newFormsCount > 0) {
      log(`${newFormsCount} nouveau(x) formulaire(s) détecté(s)`);
      
      // Envoyer les informations au content script
      window.dispatchEvent(new CustomEvent('gmp-forms-detected', {
        detail: {
          totalForms: forms.length,
          newForms: newFormsCount,
          loginForms: Array.from(injectState.forms.values()).filter(f => f.isLoginForm).length
        }
      }));
    }
  }

  /**
   * Nettoyer les anciennes données de formulaires
   */
  function cleanupOldData() {
    try {
      const keys = Object.keys(localStorage);
      const gmpKeys = keys.filter(key => key.startsWith(INJECT_CONFIG.STORAGE_KEY));
      const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);

      gmpKeys.forEach(key => {
        try {
          const data = JSON.parse(localStorage.getItem(key));
          if (data.timestamp < oneWeekAgo) {
            localStorage.removeItem(key);
            log('Données anciennes supprimées:', key);
          }
        } catch (error) {
          // Supprimer les données corrompues
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      log('Erreur nettoyage données:', error);
    }
  }

  /**
   * Observer les changements DOM
   */
  function startDOMObserver() {
    if (injectState.observer) {
      injectState.observer.disconnect();
    }

    injectState.observer = new MutationObserver((mutations) => {
      let shouldScan = false;

      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
              if (node.tagName === 'FORM' || node.querySelector('form')) {
                shouldScan = true;
              }
            }
          });
        }
      });

      if (shouldScan) {
        // Débounce la détection pour éviter les scans répétitifs
        clearTimeout(injectState.scanTimeout);
        injectState.scanTimeout = setTimeout(detectForms, INJECT_CONFIG.DETECTION_DELAY);
      }
    });

    injectState.observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    log('Observer DOM démarré');
  }

  /**
   * Initialiser le script d'injection
   */
  function initialize() {
    log('Script d\'injection initialisé');
    
    // Nettoyer les anciennes données
    cleanupOldData();
    
    // Détecter les formulaires existants
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        setTimeout(detectForms, INJECT_CONFIG.DETECTION_DELAY);
      });
    } else {
      setTimeout(detectForms, INJECT_CONFIG.DETECTION_DELAY);
    }
    
    // Démarrer l'observation des changements DOM
    startDOMObserver();
    
    injectState.isActive = true;
  }

  /**
   * Nettoyer avant déchargement
   */
  function cleanup() {
    if (injectState.observer) {
      injectState.observer.disconnect();
    }
    
    clearTimeout(injectState.scanTimeout);
    injectState.isActive = false;
    
    log('Script d\'injection nettoyé');
  }

  // API publique pour le content script
  window.gmpInject = {
    getForms: () => Array.from(injectState.forms.values()),
    getFormById: (id) => injectState.forms.get(id),
    refreshDetection: detectForms,
    isActive: () => injectState.isActive
  };

  // Événements de cycle de vie
  window.addEventListener('beforeunload', cleanup);
  
  // Démarrer l'initialisation
  initialize();

  log('Script d\'injection chargé et actif');
}