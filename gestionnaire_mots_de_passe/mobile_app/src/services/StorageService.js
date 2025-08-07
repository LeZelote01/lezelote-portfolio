import AsyncStorage from '@react-native-async-storage/async-storage';
import {CryptoUtils} from '../utils/CryptoUtils';

/**
 * Service de stockage sécurisé pour l'application mobile
 */
export class StorageService {
  static KEYS = {
    MASTER_PASSWORD_HASH: 'masterPasswordHash',
    ENCRYPTION_SALT: 'encryptionSalt',
    PASSWORDS: 'passwords',
    SETTINGS: 'settings',
    BIOMETRIC_ENABLED: 'biometricEnabled',
    LAST_SYNC: 'lastSync',
    USER_DATA: 'userData',
  };

  /**
   * Initialise le stockage avec un mot de passe maître
   * @param {string} masterPassword - Le mot de passe maître
   */
  static async initializeStorage(masterPassword) {
    try {
      // Générer un sel pour la dérivation de clé
      const salt = CryptoUtils.generateSalt();
      
      // Hacher le mot de passe maître pour la vérification
      const hashedPassword = CryptoUtils.hashPassword(masterPassword + salt);
      
      // Sauvegarder le hash et le sel
      await AsyncStorage.multiSet([
        [this.KEYS.MASTER_PASSWORD_HASH, hashedPassword],
        [this.KEYS.ENCRYPTION_SALT, salt],
        [this.KEYS.PASSWORDS, JSON.stringify([])],
        [this.KEYS.SETTINGS, JSON.stringify({
          biometricEnabled: false,
          autoLockTimeout: 30, // minutes
          theme: 'light',
          syncEnabled: false,
        })],
      ]);

      return true;
    } catch (error) {
      console.error('Erreur lors de l\'initialisation du stockage:', error);
      throw new Error('Impossible d\'initialiser le stockage sécurisé');
    }
  }

  /**
   * Vérifie si le stockage est initialisé
   */
  static async isInitialized() {
    try {
      const hash = await AsyncStorage.getItem(this.KEYS.MASTER_PASSWORD_HASH);
      return hash !== null;
    } catch (error) {
      console.error('Erreur lors de la vérification d\'initialisation:', error);
      return false;
    }
  }

  /**
   * Vérifie le mot de passe maître
   * @param {string} masterPassword - Le mot de passe à vérifier
   * @returns {boolean} True si le mot de passe est correct
   */
  static async verifyMasterPassword(masterPassword) {
    try {
      const [storedHash, salt] = await AsyncStorage.multiGet([
        this.KEYS.MASTER_PASSWORD_HASH,
        this.KEYS.ENCRYPTION_SALT,
      ]);

      if (!storedHash[1] || !salt[1]) {
        return false;
      }

      const hashedInput = CryptoUtils.hashPassword(masterPassword + salt[1]);
      return hashedInput === storedHash[1];
    } catch (error) {
      console.error('Erreur lors de la vérification du mot de passe:', error);
      return false;
    }
  }

  /**
   * Obtient la clé de chiffrement dérivée du mot de passe maître
   * @param {string} masterPassword - Le mot de passe maître
   * @returns {string} La clé de chiffrement
   */
  static async getEncryptionKey(masterPassword) {
    try {
      const salt = await AsyncStorage.getItem(this.KEYS.ENCRYPTION_SALT);
      if (!salt) {
        throw new Error('Sel de chiffrement non trouvé');
      }
      return CryptoUtils.deriveKey(masterPassword, salt);
    } catch (error) {
      console.error('Erreur lors de la génération de la clé:', error);
      throw error;
    }
  }

  /**
   * Sauvegarde un mot de passe de manière chiffrée
   * @param {object} passwordEntry - L'entrée de mot de passe
   * @param {string} masterPassword - Le mot de passe maître
   */
  static async savePassword(passwordEntry, masterPassword) {
    try {
      const encryptionKey = await this.getEncryptionKey(masterPassword);
      const passwords = await this.getAllPasswords(masterPassword);

      // Ajouter un ID unique si pas présent
      if (!passwordEntry.id) {
        passwordEntry.id = CryptoUtils.generateUUID();
      }

      // Ajouter la date de création
      passwordEntry.createdAt = new Date().toISOString();
      passwordEntry.updatedAt = new Date().toISOString();

      // Chiffrer les données sensibles
      const encryptedPassword = CryptoUtils.encrypt(passwordEntry.password, encryptionKey);
      const encryptedNotes = passwordEntry.notes ? 
        CryptoUtils.encrypt(passwordEntry.notes, encryptionKey) : null;

      const encryptedEntry = {
        ...passwordEntry,
        password: encryptedPassword,
        notes: encryptedNotes,
      };

      passwords.push(encryptedEntry);
      
      await AsyncStorage.setItem(this.KEYS.PASSWORDS, JSON.stringify(passwords));
      return passwordEntry.id;
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du mot de passe:', error);
      throw new Error('Impossible de sauvegarder le mot de passe');
    }
  }

  /**
   * Met à jour un mot de passe existant
   * @param {string} passwordId - L'ID du mot de passe
   * @param {object} updatedData - Les données mises à jour
   * @param {string} masterPassword - Le mot de passe maître
   */
  static async updatePassword(passwordId, updatedData, masterPassword) {
    try {
      const encryptionKey = await this.getEncryptionKey(masterPassword);
      const passwords = await this.getAllPasswords(masterPassword, false);

      const passwordIndex = passwords.findIndex(p => p.id === passwordId);
      if (passwordIndex === -1) {
        throw new Error('Mot de passe non trouvé');
      }

      // Mettre à jour les données
      const updatedEntry = {
        ...passwords[passwordIndex],
        ...updatedData,
        updatedAt: new Date().toISOString(),
      };

      // Chiffrer les nouvelles données sensibles si nécessaire
      if (updatedData.password) {
        updatedEntry.password = CryptoUtils.encrypt(updatedData.password, encryptionKey);
      }
      if (updatedData.notes) {
        updatedEntry.notes = CryptoUtils.encrypt(updatedData.notes, encryptionKey);
      }

      passwords[passwordIndex] = updatedEntry;
      
      await AsyncStorage.setItem(this.KEYS.PASSWORDS, JSON.stringify(passwords));
      return true;
    } catch (error) {
      console.error('Erreur lors de la mise à jour du mot de passe:', error);
      throw new Error('Impossible de mettre à jour le mot de passe');
    }
  }

  /**
   * Supprime un mot de passe
   * @param {string} passwordId - L'ID du mot de passe à supprimer
   * @param {string} masterPassword - Le mot de passe maître
   */
  static async deletePassword(passwordId, masterPassword) {
    try {
      const passwords = await this.getAllPasswords(masterPassword, false);
      const filteredPasswords = passwords.filter(p => p.id !== passwordId);
      
      await AsyncStorage.setItem(this.KEYS.PASSWORDS, JSON.stringify(filteredPasswords));
      return true;
    } catch (error) {
      console.error('Erreur lors de la suppression du mot de passe:', error);
      throw new Error('Impossible de supprimer le mot de passe');
    }
  }

  /**
   * Récupère tous les mots de passe
   * @param {string} masterPassword - Le mot de passe maître
   * @param {boolean} decrypt - Si true, déchiffre les mots de passe
   * @returns {Array} La liste des mots de passe
   */
  static async getAllPasswords(masterPassword, decrypt = true) {
    try {
      const passwordsJson = await AsyncStorage.getItem(this.KEYS.PASSWORDS);
      if (!passwordsJson) {
        return [];
      }

      const passwords = JSON.parse(passwordsJson);
      
      if (!decrypt) {
        return passwords;
      }

      const encryptionKey = await this.getEncryptionKey(masterPassword);
      
      return passwords.map(entry => {
        try {
          const decryptedEntry = { ...entry };
          
          if (entry.password && entry.password.data && entry.password.iv) {
            decryptedEntry.password = CryptoUtils.decrypt(
              entry.password.data, 
              encryptionKey, 
              entry.password.iv
            );
          }
          
          if (entry.notes && entry.notes.data && entry.notes.iv) {
            decryptedEntry.notes = CryptoUtils.decrypt(
              entry.notes.data, 
              encryptionKey, 
              entry.notes.iv
            );
          }
          
          return decryptedEntry;
        } catch (decryptError) {
          console.error('Erreur de déchiffrement pour l\'entrée:', entry.id, decryptError);
          return {
            ...entry,
            password: '[ERREUR DE DÉCHIFFREMENT]',
            notes: entry.notes ? '[ERREUR DE DÉCHIFFREMENT]' : '',
          };
        }
      });
    } catch (error) {
      console.error('Erreur lors de la récupération des mots de passe:', error);
      throw new Error('Impossible de récupérer les mots de passe');
    }
  }

  /**
   * Recherche des mots de passe par titre ou site
   * @param {string} query - La requête de recherche
   * @param {string} masterPassword - Le mot de passe maître
   */
  static async searchPasswords(query, masterPassword) {
    try {
      const passwords = await this.getAllPasswords(masterPassword);
      const lowercaseQuery = query.toLowerCase();
      
      return passwords.filter(entry => 
        entry.title?.toLowerCase().includes(lowercaseQuery) ||
        entry.website?.toLowerCase().includes(lowercaseQuery) ||
        entry.username?.toLowerCase().includes(lowercaseQuery)
      );
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      throw new Error('Erreur lors de la recherche');
    }
  }

  /**
   * Sauvegarde les paramètres de l'application
   * @param {object} settings - Les paramètres à sauvegarder
   */
  static async saveSettings(settings) {
    try {
      await AsyncStorage.setItem(this.KEYS.SETTINGS, JSON.stringify(settings));
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des paramètres:', error);
      throw new Error('Impossible de sauvegarder les paramètres');
    }
  }

  /**
   * Récupère les paramètres de l'application
   */
  static async getSettings() {
    try {
      const settingsJson = await AsyncStorage.getItem(this.KEYS.SETTINGS);
      if (!settingsJson) {
        return {
          biometricEnabled: false,
          autoLockTimeout: 30,
          theme: 'light',
          syncEnabled: false,
        };
      }
      return JSON.parse(settingsJson);
    } catch (error) {
      console.error('Erreur lors de la récupération des paramètres:', error);
      return {
        biometricEnabled: false,
        autoLockTimeout: 30,
        theme: 'light',
        syncEnabled: false,
      };
    }
  }

  /**
   * Exporte toutes les données (pour sauvegarde)
   * @param {string} masterPassword - Le mot de passe maître
   */
  static async exportData(masterPassword) {
    try {
      const passwords = await this.getAllPasswords(masterPassword);
      const settings = await this.getSettings();
      
      return {
        passwords,
        settings,
        exportDate: new Date().toISOString(),
        appVersion: '1.0.0',
      };
    } catch (error) {
      console.error('Erreur lors de l\'export:', error);
      throw new Error('Erreur lors de l\'export des données');
    }
  }

  /**
   * Efface toutes les données de l'application
   */
  static async clearAllData() {
    try {
      await AsyncStorage.multiRemove([
        this.KEYS.MASTER_PASSWORD_HASH,
        this.KEYS.ENCRYPTION_SALT,
        this.KEYS.PASSWORDS,
        this.KEYS.SETTINGS,
        this.KEYS.BIOMETRIC_ENABLED,
        this.KEYS.LAST_SYNC,
        this.KEYS.USER_DATA,
      ]);
      return true;
    } catch (error) {
      console.error('Erreur lors de l\'effacement des données:', error);
      throw new Error('Impossible d\'effacer les données');
    }
  }
}