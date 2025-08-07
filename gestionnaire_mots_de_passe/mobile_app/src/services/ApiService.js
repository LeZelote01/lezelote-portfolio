import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Service de communication avec l'API backend
 */
export class ApiService {
  static BASE_URL = 'http://localhost:8001/api'; // URL du backend
  static TIMEOUT = 10000; // 10 secondes

  // Instance Axios configurée
  static client = axios.create({
    baseURL: this.BASE_URL,
    timeout: this.TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  /**
   * Configure les intercepteurs pour l'authentification
   */
  static setupInterceptors() {
    // Intercepteur de requête pour ajouter le token
    this.client.interceptors.request.use(
      async (config) => {
        try {
          const token = await AsyncStorage.getItem('authToken');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.error('Erreur lors de la récupération du token:', error);
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Intercepteur de réponse pour gérer les erreurs d'authentification
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expiré ou invalide
          await AsyncStorage.removeItem('authToken');
          // Rediriger vers l'écran de connexion si nécessaire
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Vérifie si l'API est accessible
   */
  static async checkApiHealth() {
    try {
      const response = await this.client.get('/health');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de santé de l\'API:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Authentifie l'utilisateur auprès de l'API
   * @param {string} username - Nom d'utilisateur
   * @param {string} password - Mot de passe
   */
  static async authenticate(username, password) {
    try {
      const response = await this.client.post('/auth/login', {
        username,
        password,
      });

      if (response.data.token) {
        await AsyncStorage.setItem('authToken', response.data.token);
        await AsyncStorage.setItem('userId', response.data.userId.toString());
      }

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur d\'authentification:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Enregistre un nouvel utilisateur
   * @param {object} userData - Données de l'utilisateur
   */
  static async register(userData) {
    try {
      const response = await this.client.post('/auth/register', userData);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur d\'enregistrement:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Synchronise les mots de passe avec le serveur
   * @param {Array} passwords - Liste des mots de passe locaux
   */
  static async syncPasswords(passwords) {
    try {
      const response = await this.client.post('/passwords/sync', {
        passwords,
        lastSync: await AsyncStorage.getItem('lastSync'),
      });

      if (response.data.lastSync) {
        await AsyncStorage.setItem('lastSync', response.data.lastSync);
      }

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de synchronisation:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Récupère les mots de passe depuis le serveur
   */
  static async getServerPasswords() {
    try {
      const response = await this.client.get('/passwords');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de récupération des mots de passe:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Sauvegarde un mot de passe sur le serveur
   * @param {object} passwordData - Données du mot de passe
   */
  static async savePasswordToServer(passwordData) {
    try {
      const response = await this.client.post('/passwords', passwordData);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de sauvegarde sur le serveur:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Met à jour un mot de passe sur le serveur
   * @param {string} passwordId - ID du mot de passe
   * @param {object} updatedData - Données mises à jour
   */
  static async updatePasswordOnServer(passwordId, updatedData) {
    try {
      const response = await this.client.put(`/passwords/${passwordId}`, updatedData);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de mise à jour sur le serveur:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Supprime un mot de passe du serveur
   * @param {string} passwordId - ID du mot de passe
   */
  static async deletePasswordFromServer(passwordId) {
    try {
      await this.client.delete(`/passwords/${passwordId}`);
      return {
        success: true,
      };
    } catch (error) {
      console.error('Erreur de suppression sur le serveur:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Vérifie si un mot de passe a été compromis
   * @param {string} password - Le mot de passe à vérifier
   */
  static async checkPasswordBreach(password) {
    try {
      const response = await this.client.post('/security/check-breach', {
        password,
      });
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de vérification de compromission:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Génère un mot de passe sécurisé via l'API
   * @param {object} options - Options de génération
   */
  static async generatePasswordFromServer(options) {
    try {
      const response = await this.client.post('/passwords/generate', options);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de génération de mot de passe:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Obtient les statistiques de sécurité
   */
  static async getSecurityStats() {
    try {
      const response = await this.client.get('/security/stats');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Erreur de récupération des statistiques:', error);
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Déconnecte l'utilisateur
   */
  static async logout() {
    try {
      await this.client.post('/auth/logout');
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
    } finally {
      // Nettoyer les données locales même en cas d'erreur
      await AsyncStorage.multiRemove([
        'authToken',
        'userId',
        'lastSync',
      ]);
    }
  }

  /**
   * Configure l'URL de base de l'API
   * @param {string} baseUrl - La nouvelle URL de base
   */
  static setBaseURL(baseUrl) {
    this.BASE_URL = baseUrl;
    this.client.defaults.baseURL = baseUrl;
  }

  /**
   * Vérifie la connectivité réseau
   */
  static async isOnline() {
    try {
      const response = await this.client.get('/ping', { timeout: 3000 });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

// Initialiser les intercepteurs
ApiService.setupInterceptors();