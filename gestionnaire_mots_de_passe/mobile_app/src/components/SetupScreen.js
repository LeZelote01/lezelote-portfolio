import React, {useState} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {StorageService} from '../services/StorageService';
import {BiometricService} from '../services/BiometricService';
import {CryptoUtils} from '../utils/CryptoUtils';

const SetupScreen = ({onSetupComplete}) => {
  const [masterPassword, setMasterPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const handlePasswordChange = (password) => {
    setMasterPassword(password);
    if (password.length > 0) {
      const strength = CryptoUtils.evaluatePasswordStrength(password);
      setPasswordStrength(strength);
    } else {
      setPasswordStrength(null);
    }
  };

  const validateInputs = () => {
    if (masterPassword.length < 8) {
      Alert.alert('Erreur', 'Le mot de passe maître doit contenir au moins 8 caractères');
      return false;
    }

    if (masterPassword !== confirmPassword) {
      Alert.alert('Erreur', 'Les mots de passe ne correspondent pas');
      return false;
    }

    if (passwordStrength && passwordStrength.score < 4) {
      Alert.alert(
        'Mot de passe faible',
        'Votre mot de passe est considéré comme faible. Voulez-vous continuer ?',
        [
          {text: 'Modifier', style: 'cancel'},
          {text: 'Continuer', onPress: () => proceedWithSetup()},
        ]
      );
      return false;
    }

    return true;
  };

  const proceedWithSetup = async () => {
    setIsLoading(true);
    
    try {
      // Initialiser le stockage sécurisé
      await StorageService.initializeStorage(masterPassword);
      
      // Proposer la configuration de la biométrie
      const {available} = await BiometricService.isBiometricAvailable();
      
      if (available) {
        Alert.alert(
          'Authentification Biométrique',
          'Voulez-vous configurer l\'authentification biométrique pour un accès plus rapide ?',
          [
            {
              text: 'Plus tard',
              onPress: () => finishSetup(),
            },
            {
              text: 'Configurer',
              onPress: () => setupBiometric(),
            },
          ]
        );
      } else {
        finishSetup();
      }
    } catch (error) {
      console.error('Erreur lors de la configuration:', error);
      Alert.alert('Erreur', 'Impossible de configurer l\'application: ' + error.message);
      setIsLoading(false);
    }
  };

  const setupBiometric = async () => {
    try {
      await BiometricService.setupBiometricAuthentication(
        async (biometricType) => {
          // Sauvegarder la préférence biométrique
          const settings = await StorageService.getSettings();
          settings.biometricEnabled = true;
          await StorageService.saveSettings(settings);
          
          Alert.alert(
            'Succès',
            'Authentification biométrique configurée avec succès !',
            [{text: 'OK', onPress: () => finishSetup()}]
          );
        },
        (error) => {
          console.error('Erreur configuration biométrique:', error);
          Alert.alert(
            'Erreur',
            'Impossible de configurer l\'authentification biométrique: ' + error,
            [{text: 'OK', onPress: () => finishSetup()}]
          );
        }
      );
    } catch (error) {
      console.error('Erreur lors de la configuration biométrique:', error);
      finishSetup();
    }
  };

  const finishSetup = () => {
    setIsLoading(false);
    Alert.alert(
      'Configuration Terminée',
      'Votre gestionnaire de mots de passe est maintenant configuré et prêt à l\'emploi !',
      [{text: 'Commencer', onPress: onSetupComplete}]
    );
  };

  const handleSetup = () => {
    if (validateInputs()) {
      proceedWithSetup();
    }
  };

  return (
    <KeyboardAvoidingView
      style={GlobalStyles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={{flexGrow: 1}}>
        <View style={GlobalStyles.centerContainer}>
          <Text style={GlobalStyles.title}>🔐</Text>
          <Text style={GlobalStyles.title}>Configuration Initiale</Text>
          <Text style={[GlobalStyles.textSecondary, {textAlign: 'center', marginBottom: 32}]}>
            Créez un mot de passe maître sécurisé pour protéger tous vos mots de passe
          </Text>

          <View style={{width: '100%'}}>
            <Text style={GlobalStyles.subtitle}>Mot de passe maître</Text>
            <TextInput
              style={[
                GlobalStyles.input,
                passwordStrength && {borderColor: passwordStrength.color}
              ]}
              placeholder="Entrez votre mot de passe maître"
              value={masterPassword}
              onChangeText={handlePasswordChange}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoComplete="password"
            />

            {passwordStrength && (
              <View style={{marginVertical: 8}}>
                <Text style={[GlobalStyles.textSecondary, {color: passwordStrength.color}]}>
                  Force: {passwordStrength.level}
                </Text>
                {passwordStrength.feedback.length > 0 && (
                  <View style={{marginTop: 4}}>
                    {passwordStrength.feedback.map((feedback, index) => (
                      <Text key={index} style={[GlobalStyles.textSecondary, {fontSize: 12}]}>
                        • {feedback}
                      </Text>
                    ))}
                  </View>
                )}
              </View>
            )}

            <TouchableOpacity
              style={{alignSelf: 'flex-end', marginVertical: 8}}
              onPress={() => setShowPassword(!showPassword)}>
              <Text style={{color: Colors.primary}}>
                {showPassword ? '🙈 Masquer' : '👁 Afficher'}
              </Text>
            </TouchableOpacity>

            <Text style={GlobalStyles.subtitle}>Confirmer le mot de passe</Text>
            <TextInput
              style={[
                GlobalStyles.input,
                confirmPassword && masterPassword !== confirmPassword && {borderColor: Colors.error}
              ]}
              placeholder="Confirmez votre mot de passe maître"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoComplete="password"
            />

            {confirmPassword && masterPassword !== confirmPassword && (
              <Text style={GlobalStyles.errorText}>
                Les mots de passe ne correspondent pas
              </Text>
            )}
          </View>

          <View style={{width: '100%', marginTop: 32}}>
            <TouchableOpacity
              style={[
                GlobalStyles.button,
                (!masterPassword || !confirmPassword || masterPassword !== confirmPassword) && {
                  backgroundColor: '#CCCCCC'
                }
              ]}
              onPress={handleSetup}
              disabled={!masterPassword || !confirmPassword || masterPassword !== confirmPassword || isLoading}>
              {isLoading ? (
                <ActivityIndicator color={Colors.onPrimary} />
              ) : (
                <Text style={GlobalStyles.buttonText}>Configurer l'Application</Text>
              )}
            </TouchableOpacity>
          </View>

          <View style={{marginTop: 32, padding: 16, backgroundColor: '#F5F5F5', borderRadius: 8}}>
            <Text style={[GlobalStyles.textSecondary, {textAlign: 'center'}]}>
              ⚠️ Important: Votre mot de passe maître ne peut pas être récupéré. 
              Assurez-vous de le mémoriser ou de le noter en lieu sûr.
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default SetupScreen;