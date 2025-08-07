/**
 * Script d'injection - Extension Gestionnaire de Mots de Passe
 * Script injecté dans le contexte de la page pour accès avancé
 */

(function() {
    'use strict';
    
    // Éviter les injections multiples
    if (window.gmpInjected) {
        return;
    }
    window.gmpInjected = true;
    
    console.log('🔐 Script d\'injection GMP activé');
    
    // Configuration
    const GMP_CONFIG = {
        detectFormChanges: true,
        autoDetectPasswords: true,
        enhancedDetection: true
    };
    
    /**
     * Détection avancée des formulaires
     */
    function enhancedFormDetection() {
        const forms = document.querySelectorAll('form');
        const detectedForms = [];
        
        forms.forEach((form, index) => {
            const formData = analyzeFormAdvanced(form, index);
            if (formData.isCredentialForm) {
                detectedForms.push(formData);
                
                // Notifier le content script
                window.postMessage({
                    type: 'GMP_FORM_DETECTED',
                    formData: formData
                }, '*');
            }
        });
        
        return detectedForms;
    }
    
    /**
     * Analyse avancée des formulaires
     */
    function analyzeFormAdvanced(form, index) {
        const inputs = Array.from(form.querySelectorAll('input'));
        const textareas = Array.from(form.querySelectorAll('textarea'));
        const allFields = [...inputs, ...textareas];
        
        const analysis = {
            id: `enhanced_form_${index}`,
            element: form,
            isCredentialForm: false,
            isLoginForm: false,
            isRegisterForm: false,
            isChangePasswordForm: false,
            fields: {
                username: null,
                email: null,
                password: null,
                confirmPassword: null,
                newPassword: null
            },
            confidence: 0
        };
        
        // Analyse des champs
        allFields.forEach(field => {
            const fieldInfo = analyzeField(field);
            
            switch (fieldInfo.type) {
                case 'username':
                    if (!analysis.fields.username || fieldInfo.confidence > analysis.fields.username.confidence) {
                        analysis.fields.username = { element: field, ...fieldInfo };
                    }
                    break;
                    
                case 'email':
                    if (!analysis.fields.email || fieldInfo.confidence > analysis.fields.email.confidence) {
                        analysis.fields.email = { element: field, ...fieldInfo };
                    }
                    break;
                    
                case 'password':
                    if (!analysis.fields.password || fieldInfo.confidence > analysis.fields.password.confidence) {
                        analysis.fields.password = { element: field, ...fieldInfo };
                    }
                    break;
                    
                case 'confirm_password':
                    if (!analysis.fields.confirmPassword || fieldInfo.confidence > analysis.fields.confirmPassword.confidence) {
                        analysis.fields.confirmPassword = { element: field, ...fieldInfo };
                    }
                    break;
                    
                case 'new_password':
                    if (!analysis.fields.newPassword || fieldInfo.confidence > analysis.fields.newPassword.confidence) {
                        analysis.fields.newPassword = { element: field, ...fieldInfo };
                    }
                    break;
            }
        });
        
        // Déterminer le type de formulaire
        const hasPassword = analysis.fields.password !== null;
        const hasUsername = analysis.fields.username !== null || analysis.fields.email !== null;
        const hasConfirmPassword = analysis.fields.confirmPassword !== null;
        const hasNewPassword = analysis.fields.newPassword !== null;
        
        if (hasPassword) {
            analysis.isCredentialForm = true;
            
            if (hasConfirmPassword || hasNewPassword) {
                analysis.isRegisterForm = true;
                analysis.confidence = 90;
            } else if (hasUsername) {
                analysis.isLoginForm = true;
                analysis.confidence = 95;
            } else {
                analysis.isChangePasswordForm = true;
                analysis.confidence = 80;
            }
        }
        
        return analysis;
    }
    
    /**
     * Analyse d'un champ individuel
     */
    function analyzeField(field) {
        const type = field.type ? field.type.toLowerCase() : 'text';
        const name = field.name ? field.name.toLowerCase() : '';
        const id = field.id ? field.id.toLowerCase() : '';
        const placeholder = field.placeholder ? field.placeholder.toLowerCase() : '';
        const className = field.className ? field.className.toLowerCase() : '';
        const ariaLabel = field.getAttribute('aria-label') ? field.getAttribute('aria-label').toLowerCase() : '';
        
        const allText = `${name} ${id} ${placeholder} ${className} ${ariaLabel}`.toLowerCase();
        
        let fieldType = 'unknown';
        let confidence = 0;
        
        // Détection du mot de passe
        if (type === 'password') {
            if (allText.includes('confirm') || allText.includes('repeat') || allText.includes('retype')) {
                fieldType = 'confirm_password';
                confidence = 95;
            } else if (allText.includes('new') || allText.includes('nouveau')) {
                fieldType = 'new_password';
                confidence = 90;
            } else {
                fieldType = 'password';
                confidence = 100;
            }
        }
        
        // Détection de l'email
        else if (type === 'email' || allText.includes('email') || allText.includes('mail')) {
            fieldType = 'email';
            confidence = 95;
        }
        
        // Détection du nom d'utilisateur
        else if (type === 'text' && (
            allText.includes('user') || allText.includes('login') || allText.includes('username') ||
            allText.includes('utilisateur') || allText.includes('identifiant')
        )) {
            fieldType = 'username';
            confidence = 85;
        }
        
        return {
            type: fieldType,
            confidence: confidence,
            htmlType: type,
            name: name,
            id: id,
            placeholder: placeholder
        };
    }
    
    /**
     * Détection automatique des mots de passe faibles
     */
    function detectWeakPasswords() {
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach(field => {
            field.addEventListener('input', function() {
                const password = this.value;
                if (password.length > 0) {
                    const strength = calculatePasswordStrength(password);
                    
                    if (strength.score < 3) {
                        // Notifier que le mot de passe est faible
                        window.postMessage({
                            type: 'GMP_WEAK_PASSWORD_DETECTED',
                            strength: strength,
                            field: {
                                id: this.id,
                                name: this.name,
                                placeholder: this.placeholder
                            }
                        }, '*');
                    }
                }
            });
        });
    }
    
    /**
     * Calcul de la force d'un mot de passe
     */
    function calculatePasswordStrength(password) {
        let score = 0;
        const checks = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            symbols: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\?]/.test(password),
            noCommon: !isCommonPassword(password)
        };
        
        Object.values(checks).forEach(check => {
            if (check) score++;
        });
        
        const strength = {
            score: score,
            checks: checks,
            level: score < 3 ? 'weak' : score < 5 ? 'medium' : 'strong'
        };
        
        return strength;
    }
    
    /**
     * Vérifier si c'est un mot de passe commun
     */
    function isCommonPassword(password) {
        const commonPasswords = [
            'password', '123456', '123456789', 'qwerty', 'abc123', 
            'password123', 'admin', 'letmein', 'welcome', '123123'
        ];
        
        return commonPasswords.includes(password.toLowerCase());
    }
    
    /**
     * Détection des changements de DOM
     */
    function observeFormChanges() {
        const observer = new MutationObserver((mutations) => {
            let shouldRecheck = false;
            
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.tagName === 'FORM' || 
                                node.querySelector('form') || 
                                node.querySelector('input[type="password"]')) {
                                shouldRecheck = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldRecheck) {
                // Délai pour permettre au DOM de se stabiliser
                setTimeout(() => {
                    enhancedFormDetection();
                    if (GMP_CONFIG.autoDetectPasswords) {
                        detectWeakPasswords();
                    }
                }, 500);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        return observer;
    }
    
    /**
     * Gestion des événements de soumission
     */
    function handleFormSubmissions() {
        document.addEventListener('submit', function(event) {
            const form = event.target;
            if (form.tagName === 'FORM') {
                const formAnalysis = analyzeFormAdvanced(form, 'submitted');
                
                if (formAnalysis.isCredentialForm) {
                    // Extraire les valeurs du formulaire
                    const formData = {
                        url: window.location.href,
                        title: document.title,
                        domain: window.location.hostname,
                        username: '',
                        email: '',
                        password: ''
                    };
                    
                    if (formAnalysis.fields.username && formAnalysis.fields.username.element.value) {
                        formData.username = formAnalysis.fields.username.element.value;
                    }
                    
                    if (formAnalysis.fields.email && formAnalysis.fields.email.element.value) {
                        formData.email = formAnalysis.fields.email.element.value;
                    }
                    
                    if (formAnalysis.fields.password && formAnalysis.fields.password.element.value) {
                        formData.password = formAnalysis.fields.password.element.value;
                    }
                    
                    // Notifier le content script
                    window.postMessage({
                        type: 'GMP_FORM_SUBMITTED',
                        formData: formData,
                        formAnalysis: formAnalysis
                    }, '*');
                }
            }
        });
    }
    
    /**
     * Interface de communication avec le content script
     */
    window.addEventListener('message', function(event) {
        if (event.source !== window) return;
        
        const { type, data } = event.data;
        
        switch (type) {
            case 'GMP_INJECT_PASSWORD':
                injectPasswordIntoForm(data.password, data.selector);
                break;
                
            case 'GMP_FILL_CREDENTIALS':
                fillCredentialsInForm(data.username, data.password);
                break;
                
            case 'GMP_GET_FORM_DATA':
                const currentFormData = getCurrentFormData();
                window.postMessage({
                    type: 'GMP_FORM_DATA_RESPONSE',
                    formData: currentFormData
                }, '*');
                break;
        }
    });
    
    /**
     * Injecter un mot de passe dans un formulaire
     */
    function injectPasswordIntoForm(password, selector) {
        let targetField;
        
        if (selector) {
            targetField = document.querySelector(selector);
        } else {
            // Chercher le champ de mot de passe le plus approprié
            targetField = document.querySelector('input[type="password"]:not([disabled]):not([readonly])');
        }
        
        if (targetField) {
            targetField.value = password;
            
            // Déclencher les événements nécessaires
            ['input', 'change', 'keyup'].forEach(eventType => {
                targetField.dispatchEvent(new Event(eventType, { bubbles: true }));
            });
            
            // Focus sur le champ
            targetField.focus();
        }
    }
    
    /**
     * Remplir les identifiants dans un formulaire
     */
    function fillCredentialsInForm(username, password) {
        const forms = enhancedFormDetection();
        
        if (forms.length > 0) {
            const form = forms[0]; // Utiliser le premier formulaire trouvé
            
            // Remplir le nom d'utilisateur
            if (username && (form.fields.username || form.fields.email)) {
                const usernameField = form.fields.username || form.fields.email;
                usernameField.element.value = username;
                
                ['input', 'change', 'keyup'].forEach(eventType => {
                    usernameField.element.dispatchEvent(new Event(eventType, { bubbles: true }));
                });
            }
            
            // Remplir le mot de passe
            if (password && form.fields.password) {
                form.fields.password.element.value = password;
                
                ['input', 'change', 'keyup'].forEach(eventType => {
                    form.fields.password.element.dispatchEvent(new Event(eventType, { bubbles: true }));
                });
            }
        }
    }
    
    /**
     * Obtenir les données du formulaire actuel
     */
    function getCurrentFormData() {
        const forms = enhancedFormDetection();
        
        if (forms.length > 0) {
            const form = forms[0];
            
            return {
                url: window.location.href,
                title: document.title,
                domain: window.location.hostname,
                username: form.fields.username ? form.fields.username.element.value : '',
                email: form.fields.email ? form.fields.email.element.value : '',
                password: form.fields.password ? form.fields.password.element.value : '',
                formType: form.isLoginForm ? 'login' : form.isRegisterForm ? 'register' : 'password_change'
            };
        }
        
        return null;
    }
    
    /**
     * Initialisation du script d'injection
     */
    function initializeInjection() {
        console.log('🚀 Initialisation du script d\'injection GMP');
        
        // Attendre que le DOM soit prêt
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', startInjection);
        } else {
            startInjection();
        }
    }
    
    /**
     * Démarrer l'injection
     */
    function startInjection() {
        try {
            // Détection initiale des formulaires
            enhancedFormDetection();
            
            // Configuration de l'observation des changements
            if (GMP_CONFIG.detectFormChanges) {
                observeFormChanges();
            }
            
            // Détection automatique des mots de passe faibles
            if (GMP_CONFIG.autoDetectPasswords) {
                detectWeakPasswords();
            }
            
            // Gestion des soumissions de formulaires
            handleFormSubmissions();
            
            console.log('✅ Script d\'injection GMP configuré avec succès');
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'initialisation du script d\'injection:', error);
        }
    }
    
    // Démarrer l'initialisation
    initializeInjection();
    
})();