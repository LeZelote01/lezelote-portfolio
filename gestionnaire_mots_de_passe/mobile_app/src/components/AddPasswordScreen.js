import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {StorageService} from '../services/StorageService';
import {CryptoUtils} from '../utils/CryptoUtils';

const AddPasswordScreen = ({navigation, route}) => {
  const {editMode = false, passwordData = null, onSave} = route.params || {};
  
  const [title, setTitle] = useState('');
  const [website, setWebsite] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [notes, setNotes] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(null);
  const [masterPassword, setMasterPassword] = useState('');

  useEffect(() => {
    // Configurer le titre de l'écran
    navigation.setOptions({
      title: editMode ? 'Modifier le mot de passe' : 'Ajouter un mot de passe'
    });

    // Si on est en mode édition, pré-remplir les champs
    if (editMode && passwordData) {
      setTitle(passwordData.title || '');
      setWebsite(passwordData.website || '');
      setUsername(passwordData.username || '');
      setPassword(passwordData.password || '');
      setNotes(passwordData.notes || '');
    }
  }, [editMode, passwordData, navigation]);

  useEffect(() => {
    if (password) {
      const strength = CryptoUtils.evaluatePasswordStrength(password);
      setPasswordStrength(strength);
    } else {
      setPasswordStrength(null);
    }
  }, [password]);

  const getMasterPassword = () => {
    return new Promise((resolve) => {
      if (masterPassword) {
        resolve(masterPassword);
      } else {
        Alert.prompt(
          'Mot de passe requis',
          'Entrez votre mot de passe maître pour sauvegarder:',
          [
            {text: 'Annuler', style: 'cancel'},
            {
              text: 'OK',
              onPress: (pwd) => {
                setMasterPassword(pwd);
                resolve(pwd);
              }
            }
          ],
          'secure-text'
        );
      }
    });
  };

  const validateForm = () => {
    if (!title.trim()) {
      Alert.alert('Erreur', 'Le titre est obligatoire');
      return false;
    }

    if (!password.trim()) {
      Alert.alert('Erreur', 'Le mot de passe est obligatoire');
      return false;
    }

    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const masterPwd = await getMasterPassword();
      if (!masterPwd) {
        setIsLoading(false);
        return;
      }

      const passwordEntry = {
        title: title.trim(),
        website: website.trim(),
        username: username.trim(),
        password: password.trim(),
        notes: notes.trim(),
      };

      if (editMode && passwordData) {
        // Mode édition
        await StorageService.updatePassword(passwordData.id, passwordEntry, masterPwd);
        Alert.alert('Succès', 'Mot de passe mis à jour avec succès', [
          {text: 'OK', onPress: () => {
            if (onSave) onSave();
            navigation.goBack();
          }}
        ]);
      } else {
        // Mode ajout
        await StorageService.savePassword(passwordEntry, masterPwd);
        Alert.alert('Succès', 'Mot de passe ajouté avec succès', [
          {text: 'OK', onPress: () => {
            if (onSave) onSave();
            navigation.goBack();
          }}
        ]);
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      Alert.alert('Erreur', 'Impossible de sauvegarder le mot de passe: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const generatePassword = () => {
    navigation.navigate('PasswordGenerator', {
      onPasswordGenerated: (generatedPassword) => {
        setPassword(generatedPassword);
      }
    });
  };

  const handleCancel = () => {
    if (title || website || username || password || notes) {
      Alert.alert(
        'Annuler les modifications',
        'Vos modifications seront perdues. Continuer ?',
        [
          {text: 'Non', style: 'cancel'},
          {text: 'Oui', onPress: () => navigation.goBack()}
        ]
      );
    } else {
      navigation.goBack();
    }
  };

  return (
    <KeyboardAvoidingView
      style={GlobalStyles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={{paddingBottom: 100}}>
          
          {/* Titre */}
          <View style={{marginBottom: 16}}>
            <Text style={GlobalStyles.subtitle}>Titre *</Text>
            <TextInput
              style={GlobalStyles.input}
              placeholder="ex: Gmail, Netflix, Banque..."
              value={title}
              onChangeText={setTitle}
              autoCapitalize="words"
            />
          </View>

          {/* Site web */}
          <View style={{marginBottom: 16}}>
            <Text style={GlobalStyles.subtitle}>Site web</Text>
            <TextInput
              style={GlobalStyles.input}
              placeholder="ex: https://gmail.com"
              value={website}
              onChangeText={setWebsite}
              keyboardType="url"
              autoCapitalize="none"
              autoComplete="url"
            />
          </View>

          {/* Nom d'utilisateur */}
          <View style={{marginBottom: 16}}>
            <Text style={GlobalStyles.subtitle}>Nom d'utilisateur</Text>
            <TextInput
              style={GlobalStyles.input}
              placeholder="ex: john.doe@gmail.com"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              autoComplete="username"
            />
          </View>

          {/* Mot de passe */}
          <View style={{marginBottom: 16}}>
            <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'}}>
              <Text style={GlobalStyles.subtitle}>Mot de passe *</Text>
              <TouchableOpacity
                onPress={generatePassword}
                style={{flexDirection: 'row', alignItems: 'center'}}>
                <Text style={{color: Colors.primary, marginRight: 4}}>🎲 Générer</Text>
              </TouchableOpacity>
            </View>
            
            <View style={{position: 'relative'}}>
              <TextInput
                style={[
                  GlobalStyles.input,
                  passwordStrength && {borderColor: passwordStrength.color}
                ]}
                placeholder="Entrez le mot de passe"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoComplete="password"
              />
              
              <TouchableOpacity
                style={{
                  position: 'absolute',
                  right: 12,
                  top: 12,
                  padding: 4,
                }}
                onPress={() => setShowPassword(!showPassword)}>
                <Text style={{fontSize: 16}}>
                  {showPassword ? '🙈' : '👁'}
                </Text>
              </TouchableOpacity>
            </View>

            {passwordStrength && (
              <View style={{marginTop: 8}}>
                <Text style={[GlobalStyles.textSecondary, {color: passwordStrength.color}]}>
                  Force: {passwordStrength.level}
                </Text>
                {passwordStrength.feedback.length > 0 && (
                  <View style={{marginTop: 4}}>
                    {passwordStrength.feedback.slice(0, 2).map((feedback, index) => (
                      <Text key={index} style={[GlobalStyles.textSecondary, {fontSize: 12}]}>
                        • {feedback}
                      </Text>
                    ))}
                  </View>
                )}
              </View>
            )}
          </View>

          {/* Notes */}
          <View style={{marginBottom: 24}}>
            <Text style={GlobalStyles.subtitle}>Notes</Text>
            <TextInput
              style={[GlobalStyles.input, {height: 80, textAlignVertical: 'top'}]}
              placeholder="Notes supplémentaires (optionnel)"
              value={notes}
              onChangeText={setNotes}
              multiline
              numberOfLines={4}
            />
          </View>

          {/* Boutons d'action */}
          <View style={{flexDirection: 'row', justifyContent: 'space-between'}}>
            <TouchableOpacity
              style={[GlobalStyles.buttonSecondary, {flex: 0.45}]}
              onPress={handleCancel}
              disabled={isLoading}>
              <Text style={GlobalStyles.buttonSecondaryText}>Annuler</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                GlobalStyles.button,
                {flex: 0.45},
                (!title.trim() || !password.trim() || isLoading) && {backgroundColor: '#CCCCCC'}
              ]}
              onPress={handleSave}
              disabled={!title.trim() || !password.trim() || isLoading}>
              {isLoading ? (
                <ActivityIndicator color={Colors.onPrimary} />
              ) : (
                <Text style={GlobalStyles.buttonText}>
                  {editMode ? 'Mettre à jour' : 'Sauvegarder'}
                </Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Informations sur la sécurité */}
          <View style={{marginTop: 24, padding: 16, backgroundColor: '#E8F5E8', borderRadius: 8}}>
            <Text style={[GlobalStyles.textSecondary, {textAlign: 'center', color: '#2E7D32'}]}>
              🔒 Toutes vos données sont chiffrées avec AES-256 avant d'être stockées
            </Text>
          </View>

        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default AddPasswordScreen;