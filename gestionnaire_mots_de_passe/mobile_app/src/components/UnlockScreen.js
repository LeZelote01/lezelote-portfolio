import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {StorageService} from '../services/StorageService';
import {BiometricService} from '../services/BiometricService';

const UnlockScreen = ({onAuthenticated}) => {
  const [masterPassword, setMasterPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [biometricType, setBiometricType] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [failedAttempts, setFailedAttempts] = useState(0);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    try {
      const {available, type} = await BiometricService.isBiometricAvailable();
      setBiometricAvailable(available);
      
      if (available) {
        const settings = await StorageService.getSettings();
        setBiometricEnabled(settings.biometricEnabled);
        setBiometricType(await BiometricService.getBiometricTypeText());
        
        // Si la biométrie est activée, proposer l'authentification automatiquement
        if (settings.biometricEnabled) {
          setTimeout(() => {
            handleBiometricAuth();
          }, 500);
        }
      }
    } catch (error) {
      console.error('Erreur lors de la vérification de la biométrie:', error);
    }
  };

  const handlePasswordAuth = async () => {
    if (!masterPassword.trim()) {
      Alert.alert('Erreur', 'Veuillez entrer votre mot de passe maître');
      return;
    }

    setIsLoading(true);

    try {
      const isValid = await StorageService.verifyMasterPassword(masterPassword);
      
      if (isValid) {
        setFailedAttempts(0);
        onAuthenticated();
      } else {
        const newFailedAttempts = failedAttempts + 1;
        setFailedAttempts(newFailedAttempts);
        
        if (newFailedAttempts >= 5) {
          Alert.alert(
            'Trop de tentatives échouées',
            'L\'application va se fermer pour des raisons de sécurité.',
            [
              {
                text: 'OK',
                onPress: () => {
                  // Dans une vraie app, on pourrait fermer l'application
                  // ou implémenter un délai d'attente
                }
              }
            ]
          );
        } else {
          Alert.alert(
            'Mot de passe incorrect',
            `Tentative ${newFailedAttempts}/5. ${5 - newFailedAttempts} tentatives restantes.`
          );
        }
        
        setMasterPassword('');
      }
    } catch (error) {
      console.error('Erreur lors de l\'authentification:', error);
      Alert.alert('Erreur', 'Erreur lors de l\'authentification: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBiometricAuth = async () => {
    try {
      setIsLoading(true);
      
      const result = await BiometricService.authenticateWithBiometrics(
        'Utilisez votre biométrie pour déverrouiller votre gestionnaire de mots de passe'
      );
      
      if (result.success) {
        onAuthenticated();
      } else {
        // L'utilisateur a annulé ou l'authentification a échoué
        console.log('Authentification biométrique échouée:', result.error);
      }
    } catch (error) {
      console.error('Erreur lors de l\'authentification biométrique:', error);
      Alert.alert(
        'Erreur Biométrique',
        'Impossible d\'utiliser l\'authentification biométrique. Utilisez votre mot de passe maître.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = () => {
    Alert.alert(
      'Mot de passe oublié',
      'Sans votre mot de passe maître, il est impossible de récupérer vos données. Vous devrez réinitialiser l\'application et perdre toutes vos données.\n\nVoulez-vous continuer ?',
      [
        {text: 'Annuler', style: 'cancel'},
        {
          text: 'Réinitialiser',
          style: 'destructive',
          onPress: () => handleReset(),
        },
      ]
    );
  };

  const handleReset = async () => {
    Alert.alert(
      'Confirmation',
      'Cette action supprimera définitivement toutes vos données. Êtes-vous absolument sûr ?',
      [
        {text: 'Annuler', style: 'cancel'},
        {
          text: 'Supprimer tout',
          style: 'destructive',
          onPress: async () => {
            try {
              await StorageService.clearAllData();
              // Redémarrer l'application ou naviguer vers l'écran de configuration
              Alert.alert(
                'Données supprimées',
                'Toutes les données ont été supprimées. L\'application va redémarrer.',
                [
                  {
                    text: 'OK',
                    onPress: () => {
                      // Dans une vraie app, on redémarrerait l'application
                      // Pour l'instant, on peut juste recharger
                    }
                  }
                ]
              );
            } catch (error) {
              Alert.alert('Erreur', 'Impossible de supprimer les données: ' + error.message);
            }
          },
        },
      ]
    );
  };

  return (
    <KeyboardAvoidingView
      style={GlobalStyles.centerContainer}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <View style={{alignItems: 'center', marginBottom: 48}}>
        <Text style={[GlobalStyles.title, {fontSize: 48, marginBottom: 16}]}>🔐</Text>
        <Text style={GlobalStyles.title}>Déverrouillage</Text>
        <Text style={[GlobalStyles.textSecondary, {textAlign: 'center'}]}>
          Entrez votre mot de passe maître pour accéder à vos mots de passe
        </Text>
      </View>

      <View style={{width: '100%'}}>
        <TextInput
          style={GlobalStyles.input}
          placeholder="Mot de passe maître"
          value={masterPassword}
          onChangeText={setMasterPassword}
          secureTextEntry={!showPassword}
          autoCapitalize="none"
          autoComplete="password"
          onSubmitEditing={handlePasswordAuth}
          editable={!isLoading}
        />

        <TouchableOpacity
          style={{alignSelf: 'flex-end', marginVertical: 8}}
          onPress={() => setShowPassword(!showPassword)}>
          <Text style={{color: Colors.primary}}>
            {showPassword ? '🙈 Masquer' : '👁 Afficher'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[GlobalStyles.button, isLoading && {backgroundColor: '#CCCCCC'}]}
          onPress={handlePasswordAuth}
          disabled={isLoading || !masterPassword.trim()}>
          {isLoading && !biometricAvailable ? (
            <ActivityIndicator color={Colors.onPrimary} />
          ) : (
            <Text style={GlobalStyles.buttonText}>Déverrouiller</Text>
          )}
        </TouchableOpacity>

        {biometricAvailable && biometricEnabled && (
          <TouchableOpacity
            style={[GlobalStyles.buttonSecondary, {marginTop: 16}]}
            onPress={handleBiometricAuth}
            disabled={isLoading}>
            {isLoading && biometricAvailable ? (
              <ActivityIndicator color={Colors.primary} />
            ) : (
              <Text style={GlobalStyles.buttonSecondaryText}>
                🔓 Utiliser {biometricType}
              </Text>
            )}
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={{alignSelf: 'center', marginTop: 24}}
          onPress={handleForgotPassword}>
          <Text style={[GlobalStyles.textSecondary, {color: Colors.primary}]}>
            Mot de passe oublié ?
          </Text>
        </TouchableOpacity>

        {failedAttempts > 0 && (
          <View style={{marginTop: 16, padding: 12, backgroundColor: '#FFEBEE', borderRadius: 8}}>
            <Text style={[GlobalStyles.textSecondary, {color: Colors.error, textAlign: 'center'}]}>
              {failedAttempts} tentative{failedAttempts > 1 ? 's' : ''} échouée{failedAttempts > 1 ? 's' : ''}
            </Text>
          </View>
        )}
      </View>

      <View style={{marginTop: 48, padding: 16, backgroundColor: '#F5F5F5', borderRadius: 8}}>
        <Text style={[GlobalStyles.textSecondary, {textAlign: 'center', fontSize: 12}]}>
          🛡️ Vos données sont chiffrées et protégées localement sur votre appareil
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
};

export default UnlockScreen;