import React, {useState} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {ApiService} from '../services/ApiService';

const LoginScreen = ({navigation, onAuthenticated}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState('');
  const [email, setEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setIsLoading(true);

    try {
      const result = await ApiService.authenticate(username, password);
      
      if (result.success) {
        Alert.alert(
          'Connexion réussie',
          'Vous êtes maintenant connecté au service de synchronisation',
          [{text: 'OK', onPress: onAuthenticated}]
        );
      } else {
        Alert.alert('Erreur de connexion', result.error);
      }
    } catch (error) {
      console.error('Erreur lors de la connexion:', error);
      Alert.alert('Erreur', 'Erreur inattendue lors de la connexion');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!username.trim() || !password.trim() || !email.trim()) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Erreur', 'Les mots de passe ne correspondent pas');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Erreur', 'Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    setIsLoading(true);

    try {
      const result = await ApiService.register({
        username,
        password,
        email,
      });
      
      if (result.success) {
        Alert.alert(
          'Inscription réussie',
          'Votre compte a été créé. Vous pouvez maintenant vous connecter.',
          [
            {
              text: 'OK',
              onPress: () => {
                setIsRegistering(false);
                setPassword('');
                setConfirmPassword('');
              }
            }
          ]
        );
      } else {
        Alert.alert('Erreur d\'inscription', result.error);
      }
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
      Alert.alert('Erreur', 'Erreur inattendue lors de l\'inscription');
    } finally {
      setIsLoading(false);
    }
  };

  const skipLogin = () => {
    Alert.alert(
      'Mode Hors Ligne',
      'Vous pouvez utiliser l\'application sans vous connecter, mais la synchronisation ne sera pas disponible.',
      [
        {text: 'Annuler', style: 'cancel'},
        {text: 'Continuer', onPress: onAuthenticated},
      ]
    );
  };

  return (
    <KeyboardAvoidingView
      style={GlobalStyles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={{flexGrow: 1}}>
        <View style={GlobalStyles.centerContainer}>
          <Text style={[GlobalStyles.title, {fontSize: 48, marginBottom: 16}]}>🌐</Text>
          <Text style={GlobalStyles.title}>
            {isRegistering ? 'Créer un Compte' : 'Connexion'}
          </Text>
          <Text style={[GlobalStyles.textSecondary, {textAlign: 'center', marginBottom: 32}]}>
            {isRegistering 
              ? 'Créez un compte pour synchroniser vos mots de passe sur plusieurs appareils'
              : 'Connectez-vous pour synchroniser vos mots de passe'
            }
          </Text>

          <View style={{width: '100%'}}>
            <Text style={GlobalStyles.subtitle}>Nom d'utilisateur</Text>
            <TextInput
              style={GlobalStyles.input}
              placeholder="Votre nom d'utilisateur"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              autoComplete="username"
              editable={!isLoading}
            />

            {isRegistering && (
              <>
                <Text style={GlobalStyles.subtitle}>Email</Text>
                <TextInput
                  style={GlobalStyles.input}
                  placeholder="Votre adresse email"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoComplete="email"
                  editable={!isLoading}
                />
              </>
            )}

            <Text style={GlobalStyles.subtitle}>Mot de passe</Text>
            <TextInput
              style={GlobalStyles.input}
              placeholder="Votre mot de passe"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoComplete="password"
              editable={!isLoading}
            />

            {isRegistering && (
              <>
                <Text style={GlobalStyles.subtitle}>Confirmer le mot de passe</Text>
                <TextInput
                  style={[
                    GlobalStyles.input,
                    confirmPassword && password !== confirmPassword && {borderColor: Colors.error}
                  ]}
                  placeholder="Confirmez votre mot de passe"
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoComplete="password"
                  editable={!isLoading}
                />
              </>
            )}

            <TouchableOpacity
              style={{alignSelf: 'flex-end', marginVertical: 8}}
              onPress={() => setShowPassword(!showPassword)}>
              <Text style={{color: Colors.primary}}>
                {showPassword ? '🙈 Masquer' : '👁 Afficher'}
              </Text>
            </TouchableOpacity>
          </View>

          <View style={{width: '100%', marginTop: 24}}>
            <TouchableOpacity
              style={[GlobalStyles.button, isLoading && {backgroundColor: '#CCCCCC'}]}
              onPress={isRegistering ? handleRegister : handleLogin}
              disabled={isLoading}>
              {isLoading ? (
                <ActivityIndicator color={Colors.onPrimary} />
              ) : (
                <Text style={GlobalStyles.buttonText}>
                  {isRegistering ? 'Créer le Compte' : 'Se Connecter'}
                </Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[GlobalStyles.buttonSecondary, {marginTop: 16}]}
              onPress={() => {
                setIsRegistering(!isRegistering);
                setPassword('');
                setConfirmPassword('');
                setEmail('');
              }}
              disabled={isLoading}>
              <Text style={GlobalStyles.buttonSecondaryText}>
                {isRegistering ? 'Déjà un compte ? Se connecter' : 'Créer un nouveau compte'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={{alignSelf: 'center', marginTop: 24}}
              onPress={skipLogin}
              disabled={isLoading}>
              <Text style={[GlobalStyles.textSecondary, {color: Colors.primary}]}>
                Continuer sans connexion
              </Text>
            </TouchableOpacity>
          </View>

          <View style={{marginTop: 32, padding: 16, backgroundColor: '#E3F2FD', borderRadius: 8}}>
            <Text style={[GlobalStyles.textSecondary, {textAlign: 'center'}]}>
              ℹ️ La connexion est optionnelle. Vous pouvez utiliser l'application 
              localement sans créer de compte.
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default LoginScreen;