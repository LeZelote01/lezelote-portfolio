import CryptoJS from 'crypto-js';

/**
 * Utilitaires de chiffrement pour l'application mobile
 */
export class CryptoUtils {
  
  /**
   * Génère une clé de chiffrement à partir d'un mot de passe et d'un sel
   * @param {string} password - Le mot de passe maître
   * @param {string} salt - Le sel pour la dérivation de clé
   * @returns {string} La clé dérivée
   */
  static deriveKey(password, salt) {
    return CryptoJS.PBKDF2(password, salt, {
      keySize: 256 / 32,
      iterations: 100000,
    }).toString();
  }

  /**
   * Génère un sel aléatoire
   * @returns {string} Le sel généré
   */
  static generateSalt() {
    return CryptoJS.lib.WordArray.random(256 / 8).toString();
  }

  /**
   * Génère un IV (Initialization Vector) aléatoire
   * @returns {string} L'IV généré
   */
  static generateIV() {
    return CryptoJS.lib.WordArray.random(128 / 8).toString();
  }

  /**
   * Chiffre des données avec AES-256
   * @param {string} data - Les données à chiffrer
   * @param {string} key - La clé de chiffrement
   * @returns {object} L'objet contenant les données chiffrées et l'IV
   */
  static encrypt(data, key) {
    const iv = this.generateIV();
    const encrypted = CryptoJS.AES.encrypt(data, key, {
      iv: CryptoJS.enc.Hex.parse(iv),
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    }).toString();

    return {
      data: encrypted,
      iv: iv,
    };
  }

  /**
   * Déchiffre des données avec AES-256
   * @param {string} encryptedData - Les données chiffrées
   * @param {string} key - La clé de déchiffrement
   * @param {string} iv - L'IV utilisé pour le chiffrement
   * @returns {string} Les données déchiffrées
   */
  static decrypt(encryptedData, key, iv) {
    try {
      const decrypted = CryptoJS.AES.decrypt(encryptedData, key, {
        iv: CryptoJS.enc.Hex.parse(iv),
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7,
      });

      return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      throw new Error('Erreur de déchiffrement: ' + error.message);
    }
  }

  /**
   * Hache un mot de passe avec SHA-256
   * @param {string} password - Le mot de passe à hacher
   * @returns {string} Le hash du mot de passe
   */
  static hashPassword(password) {
    return CryptoJS.SHA256(password).toString();
  }

  /**
   * Génère un mot de passe sécurisé
   * @param {number} length - La longueur du mot de passe
   * @param {object} options - Les options de génération
   * @returns {string} Le mot de passe généré
   */
  static generatePassword(length = 12, options = {}) {
    const {
      includeUppercase = true,
      includeLowercase = true,
      includeNumbers = true,
      includeSymbols = true,
      excludeSimilar = false,
    } = options;

    let charset = '';
    
    if (includeLowercase) {
      charset += excludeSimilar ? 'abcdefghjkmnpqrstuvwxyz' : 'abcdefghijklmnopqrstuvwxyz';
    }
    
    if (includeUppercase) {
      charset += excludeSimilar ? 'ABCDEFGHJKMNPQRSTUVWXYZ' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    }
    
    if (includeNumbers) {
      charset += excludeSimilar ? '23456789' : '0123456789';
    }
    
    if (includeSymbols) {
      charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';
    }

    if (charset === '') {
      throw new Error('Au moins une option de caractères doit être sélectionnée');
    }

    let password = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * charset.length);
      password += charset[randomIndex];
    }

    return password;
  }

  /**
   * Évalue la force d'un mot de passe
   * @param {string} password - Le mot de passe à évaluer
   * @returns {object} L'évaluation de la force du mot de passe
   */
  static evaluatePasswordStrength(password) {
    let score = 0;
    let feedback = [];

    // Longueur
    if (password.length >= 8) score += 1;
    else feedback.push('Le mot de passe doit contenir au moins 8 caractères');

    if (password.length >= 12) score += 1;

    // Caractères minuscules
    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('Ajoutez des lettres minuscules');

    // Caractères majuscules
    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('Ajoutez des lettres majuscules');

    // Chiffres
    if (/[0-9]/.test(password)) score += 1;
    else feedback.push('Ajoutez des chiffres');

    // Symboles
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else feedback.push('Ajoutez des symboles');

    // Éviter les répétitions
    if (!/(.)\1{2,}/.test(password)) score += 1;
    else feedback.push('Évitez les répétitions de caractères');

    // Déterminer le niveau de sécurité
    let level = 'Très faible';
    let color = '#f44336';

    if (score >= 6) {
      level = 'Très fort';
      color = '#4caf50';
    } else if (score >= 5) {
      level = 'Fort';
      color = '#8bc34a';
    } else if (score >= 4) {
      level = 'Moyen';
      color = '#ff9800';
    } else if (score >= 2) {
      level = 'Faible';
      color = '#ff5722';
    }

    return {
      score,
      level,
      color,
      feedback,
    };
  }

  /**
   * Vérifie si une chaîne est un hash valide
   * @param {string} hash - Le hash à vérifier
   * @returns {boolean} True si le hash est valide
   */
  static isValidHash(hash) {
    return /^[a-f0-9]{64}$/i.test(hash);
  }

  /**
   * Génère un UUID v4
   * @returns {string} L'UUID généré
   */
  static generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}