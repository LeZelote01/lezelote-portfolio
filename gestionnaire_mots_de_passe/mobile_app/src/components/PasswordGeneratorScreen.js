import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Alert,
  Switch,
} from 'react-native';
import Clipboard from '@react-native-clipboard/clipboard';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {CryptoUtils} from '../utils/CryptoUtils';

const PasswordGeneratorScreen = ({navigation, route}) => {
  const {onPasswordGenerated} = route.params || {};
  
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [passwordLength, setPasswordLength] = useState(12);
  const [includeUppercase, setIncludeUppercase] = useState(true);
  const [includeLowercase, setIncludeLowercase] = useState(true);
  const [includeNumbers, setIncludeNumbers] = useState(true);
  const [includeSymbols, setIncludeSymbols] = useState(true);
  const [excludeSimilar, setExcludeSimilar] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(null);

  const generatePassword = () => {
    try {
      const options = {
        includeUppercase,
        includeLowercase,
        includeNumbers,
        includeSymbols,
        excludeSimilar,
      };

      const password = CryptoUtils.generatePassword(passwordLength, options);
      setGeneratedPassword(password);
      
      const strength = CryptoUtils.evaluatePasswordStrength(password);
      setPasswordStrength(strength);
    } catch (error) {
      Alert.alert('Erreur', error.message);
    }
  };

  const copyToClipboard = () => {
    if (!generatedPassword) {
      Alert.alert('Erreur', 'Aucun mot de passe à copier');
      return;
    }
    
    Clipboard.setString(generatedPassword);
    Alert.alert('Copié', 'Mot de passe copié dans le presse-papier');
  };

  const usePassword = () => {
    if (!generatedPassword) {
      Alert.alert('Erreur', 'Aucun mot de passe généré');
      return;
    }

    if (onPasswordGenerated) {
      onPasswordGenerated(generatedPassword);
      navigation.goBack();
    } else {
      copyToClipboard();
    }
  };

  const adjustLength = (increment) => {
    const newLength = passwordLength + increment;
    if (newLength >= 4 && newLength <= 128) {
      setPasswordLength(newLength);
    }
  };

  const renderLengthControl = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>Longueur du mot de passe</Text>
      <View style={{flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 12}}>
        <TouchableOpacity
          style={{
            backgroundColor: passwordLength <= 4 ? '#CCCCCC' : Colors.primary,
            width: 40,
            height: 40,
            borderRadius: 20,
            justifyContent: 'center',
            alignItems: 'center',
          }}
          onPress={() => adjustLength(-1)}
          disabled={passwordLength <= 4}>
          <Text style={{color: 'white', fontSize: 18, fontWeight: 'bold'}}>-</Text>
        </TouchableOpacity>
        
        <View style={{alignItems: 'center'}}>
          <Text style={[GlobalStyles.title, {fontSize: 32, marginBottom: 0}]}>
            {passwordLength}
          </Text>
          <Text style={GlobalStyles.textSecondary}>caractères</Text>
        </View>
        
        <TouchableOpacity
          style={{
            backgroundColor: passwordLength >= 128 ? '#CCCCCC' : Colors.primary,
            width: 40,
            height: 40,
            borderRadius: 20,
            justifyContent: 'center',
            alignItems: 'center',
          }}
          onPress={() => adjustLength(1)}
          disabled={passwordLength >= 128}>
          <Text style={{color: 'white', fontSize: 18, fontWeight: 'bold'}}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderOptions = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>Options de génération</Text>
      
      <View style={{marginTop: 16}}>
        <View style={styles.optionRow}>
          <Text style={GlobalStyles.text}>Lettres majuscules (A-Z)</Text>
          <Switch
            value={includeUppercase}
            onValueChange={setIncludeUppercase}
            trackColor={{false: '#767577', true: Colors.primary}}
            thumbColor={includeUppercase ? Colors.secondary : '#f4f3f4'}
          />
        </View>
        
        <View style={styles.optionRow}>
          <Text style={GlobalStyles.text}>Lettres minuscules (a-z)</Text>
          <Switch
            value={includeLowercase}
            onValueChange={setIncludeLowercase}
            trackColor={{false: '#767577', true: Colors.primary}}
            thumbColor={includeLowercase ? Colors.secondary : '#f4f3f4'}
          />
        </View>
        
        <View style={styles.optionRow}>
          <Text style={GlobalStyles.text}>Chiffres (0-9)</Text>
          <Switch
            value={includeNumbers}
            onValueChange={setIncludeNumbers}
            trackColor={{false: '#767577', true: Colors.primary}}
            thumbColor={includeNumbers ? Colors.secondary : '#f4f3f4'}
          />
        </View>
        
        <View style={styles.optionRow}>
          <Text style={GlobalStyles.text}>Symboles (!@#$%...)</Text>
          <Switch
            value={includeSymbols}
            onValueChange={setIncludeSymbols}
            trackColor={{false: '#767577', true: Colors.primary}}
            thumbColor={includeSymbols ? Colors.secondary : '#f4f3f4'}
          />
        </View>
        
        <View style={styles.optionRow}>
          <Text style={GlobalStyles.text}>Exclure caractères similaires</Text>
          <Switch
            value={excludeSimilar}
            onValueChange={setExcludeSimilar}
            trackColor={{false: '#767577', true: Colors.primary}}
            thumbColor={excludeSimilar ? Colors.secondary : '#f4f3f4'}
          />
        </View>
      </View>
      
      {excludeSimilar && (
        <Text style={[GlobalStyles.textSecondary, {fontSize: 12, marginTop: 8}]}>
          Exclut: 0, O, l, 1, I
        </Text>
      )}
    </View>
  );

  const renderGeneratedPassword = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>Mot de passe généré</Text>
      
      <View style={{
        backgroundColor: '#F5F5F5',
        borderRadius: 8,
        padding: 16,
        marginVertical: 16,
        minHeight: 60,
        justifyContent: 'center',
      }}>
        {generatedPassword ? (
          <Text style={{
            fontSize: 16,
            fontFamily: 'monospace',
            textAlign: 'center',
            lineHeight: 24,
          }}>
            {generatedPassword}
          </Text>
        ) : (
          <Text style={[GlobalStyles.textSecondary, {textAlign: 'center'}]}>
            Appuyez sur "Générer" pour créer un mot de passe
          </Text>
        )}
      </View>

      {passwordStrength && (
        <View style={{marginBottom: 16}}>
          <Text style={[GlobalStyles.textSecondary, {color: passwordStrength.color}]}>
            Force: {passwordStrength.level}
          </Text>
          <View style={{
            height: 4,
            backgroundColor: '#E0E0E0',
            borderRadius: 2,
            marginTop: 4,
          }}>
            <View style={{
              height: 4,
              backgroundColor: passwordStrength.color,
              borderRadius: 2,
              width: `${(passwordStrength.score / 7) * 100}%`,
            }} />
          </View>
        </View>
      )}

      <View style={{flexDirection: 'row', justifyContent: 'space-between'}}>
        <TouchableOpacity
          style={[GlobalStyles.buttonSecondary, {flex: 0.45}]}
          onPress={copyToClipboard}
          disabled={!generatedPassword}>
          <Text style={GlobalStyles.buttonSecondaryText}>📋 Copier</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[GlobalStyles.button, {flex: 0.45}]}
          onPress={usePassword}
          disabled={!generatedPassword}>
          <Text style={GlobalStyles.buttonText}>
            {onPasswordGenerated ? '✓ Utiliser' : '📋 Copier'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderPresets = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>Préréglages rapides</Text>
      
      <View style={{flexDirection: 'row', flexWrap: 'wrap', marginTop: 12}}>
        <TouchableOpacity
          style={styles.presetButton}
          onPress={() => {
            setPasswordLength(8);
            setIncludeUppercase(true);
            setIncludeLowercase(true);
            setIncludeNumbers(true);
            setIncludeSymbols(false);
            setExcludeSimilar(false);
          }}>
          <Text style={styles.presetButtonText}>🔓 Simple</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.presetButton}
          onPress={() => {
            setPasswordLength(12);
            setIncludeUppercase(true);
            setIncludeLowercase(true);
            setIncludeNumbers(true);
            setIncludeSymbols(true);
            setExcludeSimilar(false);
          }}>
          <Text style={styles.presetButtonText}>🔒 Standard</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.presetButton}
          onPress={() => {
            setPasswordLength(16);
            setIncludeUppercase(true);
            setIncludeLowercase(true);
            setIncludeNumbers(true);
            setIncludeSymbols(true);
            setExcludeSimilar(true);
          }}>
          <Text style={styles.presetButtonText}>🛡️ Sécurisé</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.presetButton}
          onPress={() => {
            setPasswordLength(24);
            setIncludeUppercase(true);
            setIncludeLowercase(true);
            setIncludeNumbers(true);
            setIncludeSymbols(true);
            setExcludeSimilar(true);
          }}>
          <Text style={styles.presetButtonText}>🔐 Maximum</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScrollView style={GlobalStyles.container}>
      <View style={{paddingBottom: 24}}>
        <Text style={[GlobalStyles.title, {textAlign: 'center', marginBottom: 24}]}>
          🎲 Générateur de Mot de Passe
        </Text>

        {renderLengthControl()}
        {renderOptions()}
        {renderPresets()}
        {renderGeneratedPassword()}

        <TouchableOpacity
          style={[GlobalStyles.button, {marginTop: 16}]}
          onPress={generatePassword}>
          <Text style={GlobalStyles.buttonText}>🎲 Générer un Mot de Passe</Text>
        </TouchableOpacity>

        <View style={{marginTop: 24, padding: 16, backgroundColor: '#E3F2FD', borderRadius: 8}}>
          <Text style={[GlobalStyles.textSecondary, {textAlign: 'center'}]}>
            💡 Pour une sécurité optimale, utilisez un mot de passe d'au moins 12 caractères 
            avec tous les types de caractères activés.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = {
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  presetButton: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.primary,
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    margin: 4,
    elevation: 1,
  },
  presetButtonText: {
    color: Colors.primary,
    fontSize: 14,
    fontWeight: '600',
  },
};

export default PasswordGeneratorScreen;