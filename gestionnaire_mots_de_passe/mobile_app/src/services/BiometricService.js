import ReactNativeBiometrics from 'react-native-biometrics';
import {Alert} from 'react-native';

/**
 * Service d'authentification biométrique
 */
export class BiometricService {
  static biometrics = new ReactNativeBiometrics();

  /**
   * Vérifie si la biométrie est disponible sur l'appareil
   */
  static async isBiometricAvailable() {
    try {
      const { available, biometryType } = await this.biometrics.isSensorAvailable();
      return {
        available,
        type: biometryType,
      };
    } catch (error) {
      console.error('Erreur lors de la vérification de la biométrie:', error);
      return {
        available: false,
        type: null,
      };
    }
  }

  /**
   * Crée une clé biométrique pour l'authentification
   */
  static async createBiometricKey() {
    try {
      const { available } = await this.isBiometricAvailable();
      if (!available) {
        throw new Error('Biométrie non disponible');
      }

      const { keysExist } = await this.biometrics.biometricKeysExist();
      
      if (keysExist) {
        await this.biometrics.deleteKeys();
      }

      const { publicKey } = await this.biometrics.createKeys();
      return publicKey;
    } catch (error) {
      console.error('Erreur lors de la création de la clé biométrique:', error);
      throw new Error('Impossible de créer la clé biométrique');
    }
  }

  /**
   * Authentifie l'utilisateur avec la biométrie
   * @param {string} promptMessage - Message à afficher lors de l'authentification
   */
  static async authenticateWithBiometrics(promptMessage = 'Authentifiez-vous avec votre biométrie') {
    try {
      const { available, type } = await this.isBiometricAvailable();
      
      if (!available) {
        throw new Error('Biométrie non disponible');
      }

      const { keysExist } = await this.biometrics.biometricKeysExist();
      
      if (!keysExist) {
        throw new Error('Aucune clé biométrique configurée');
      }

      // Créer une charge utile à signer
      const epochTimeSeconds = Math.round((new Date()).getTime() / 1000).toString();
      const payload = epochTimeSeconds + 'auth_request';

      let title = 'Authentification Biométrique';
      let subtitle = promptMessage;

      // Personnaliser selon le type de biométrie
      switch (type) {
        case ReactNativeBiometrics.Biometrics.TouchID:
          title = 'Authentification Touch ID';
          subtitle = 'Placez votre doigt sur le capteur Touch ID';
          break;
        case ReactNativeBiometrics.Biometrics.FaceID:
          title = 'Authentification Face ID';
          subtitle = 'Regardez votre appareil pour l\'authentification Face ID';
          break;
        case ReactNativeBiometrics.Biometrics.Biometrics:
          title = 'Authentification Biométrique';
          subtitle = 'Utilisez votre biométrie pour vous authentifier';
          break;
      }

      const { success, signature } = await this.biometrics.createSignature({
        promptMessage: title,
        payload: payload,
        cancelButtonText: 'Annuler',
        fallbackPromptMessage: 'Utilisez votre code PIN',
      });

      if (success && signature) {
        return {
          success: true,
          signature,
          payload,
        };
      } else {
        return {
          success: false,
          error: 'Authentification annulée',
        };
      }
    } catch (error) {
      console.error('Erreur lors de l\'authentification biométrique:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Supprime les clés biométriques
   */
  static async deleteBiometricKeys() {
    try {
      const { keysExist } = await this.biometrics.biometricKeysExist();
      
      if (keysExist) {
        await this.biometrics.deleteKeys();
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Erreur lors de la suppression des clés biométriques:', error);
      throw new Error('Impossible de supprimer les clés biométriques');
    }
  }

  /**
   * Configure la biométrie pour l'utilisateur
   * @param {Function} onSuccess - Callback en cas de succès
   * @param {Function} onError - Callback en cas d'erreur
   */
  static async setupBiometricAuthentication(onSuccess, onError) {
    try {
      const { available, type } = await this.isBiometricAvailable();
      
      if (!available) {
        onError('La biométrie n\'est pas disponible sur cet appareil');
        return;
      }

      let biometricType = 'biométrique';
      switch (type) {
        case ReactNativeBiometrics.Biometrics.TouchID:
          biometricType = 'Touch ID';
          break;
        case ReactNativeBiometrics.Biometrics.FaceID:
          biometricType = 'Face ID';
          break;
        case ReactNativeBiometrics.Biometrics.Biometrics:
          biometricType = 'empreinte digitale';
          break;
      }

      Alert.alert(
        'Configuration de l\'authentification biométrique',
        `Voulez-vous activer l'authentification ${biometricType} pour un accès plus rapide à vos mots de passe ?`,
        [
          {
            text: 'Annuler',
            style: 'cancel',
            onPress: () => onError('Configuration annulée'),
          },
          {
            text: 'Activer',
            onPress: async () => {
              try {
                await this.createBiometricKey();
                
                // Tester l'authentification
                const authResult = await this.authenticateWithBiometrics(
                  'Confirmez votre identité pour activer l\'authentification biométrique'
                );
                
                if (authResult.success) {
                  onSuccess(type);
                } else {
                  onError(authResult.error || 'Échec de l\'authentification de test');
                }
              } catch (error) {
                onError(error.message);
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error('Erreur lors de la configuration de la biométrie:', error);
      onError('Erreur lors de la configuration: ' + error.message);
    }
  }

  /**
   * Obtient le type de biométrie disponible sous forme de texte
   */
  static async getBiometricTypeText() {
    try {
      const { available, type } = await this.isBiometricAvailable();
      
      if (!available) {
        return 'Non disponible';
      }

      switch (type) {
        case ReactNativeBiometrics.Biometrics.TouchID:
          return 'Touch ID';
        case ReactNativeBiometrics.Biometrics.FaceID:
          return 'Face ID';
        case ReactNativeBiometrics.Biometrics.Biometrics:
          return 'Empreinte digitale';
        default:
          return 'Biométrie';
      }
    } catch (error) {
      console.error('Erreur lors de la récupération du type biométrique:', error);
      return 'Erreur';
    }
  }

  /**
   * Vérifie si les clés biométriques existent
   */
  static async biometricKeysExist() {
    try {
      const { keysExist } = await this.biometrics.biometricKeysExist();
      return keysExist;
    } catch (error) {
      console.error('Erreur lors de la vérification des clés biométriques:', error);
      return false;
    }
  }
}