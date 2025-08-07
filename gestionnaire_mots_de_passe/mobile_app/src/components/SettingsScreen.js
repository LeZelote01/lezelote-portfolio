import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Alert,
  Switch,
  ActivityIndicator,
  Share,
} from 'react-native';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {StorageService} from '../services/StorageService';
import {BiometricService} from '../services/BiometricService';
import {ApiService} from '../services/ApiService';

const SettingsScreen = ({navigation, onLogout}) => {
  const [settings, setSettings] = useState({
    biometricEnabled: false,
    autoLockTimeout: 30,
    theme: 'light',
    syncEnabled: false,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [biometricAvailable, setBiometricAvailable] = useState(false);
  const [biometricType, setBiometricType] = useState('');
  const [masterPassword, setMasterPassword] = useState('');

  useEffect(() => {
    loadSettings();
    checkBiometricAvailability();
  }, []);

  const loadSettings = async () => {
    try {
      const savedSettings = await StorageService.getSettings();
      setSettings(savedSettings);
    } catch (error) {
      console.error('Erreur lors du chargement des paramètres:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkBiometricAvailability = async () => {
    try {
      const {available, type} = await BiometricService.isBiometricAvailable();
      setBiometricAvailable(available);
      if (available) {
        setBiometricType(await BiometricService.getBiometricTypeText());
      }
    } catch (error) {
      console.error('Erreur lors de la vérification de la biométrie:', error);
    }
  };

  const getMasterPassword = () => {
    return new Promise((resolve) => {
      if (masterPassword) {
        resolve(masterPassword);
      } else {
        Alert.prompt(
          'Mot de passe requis',
          'Entrez votre mot de passe maître:',
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

  const saveSettings = async (newSettings) => {
    try {
      await StorageService.saveSettings(newSettings);
      setSettings(newSettings);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des paramètres:', error);
      Alert.alert('Erreur', 'Impossible de sauvegarder les paramètres');
    }
  };

  const toggleBiometric = async (enabled) => {
    if (enabled) {
      // Activer la biométrie
      await BiometricService.setupBiometricAuthentication(
        async () => {
          const newSettings = {...settings, biometricEnabled: true};
          await saveSettings(newSettings);
          Alert.alert('Succès', 'Authentification biométrique activée');
        },
        (error) => {
          Alert.alert('Erreur', 'Impossible d\'activer la biométrie: ' + error);
        }
      );
    } else {
      // Désactiver la biométrie
      Alert.alert(
        'Désactiver la biométrie',
        'Voulez-vous vraiment désactiver l\'authentification biométrique ?',
        [
          {text: 'Annuler', style: 'cancel'},
          {
            text: 'Désactiver',
            onPress: async () => {
              try {
                await BiometricService.deleteBiometricKeys();
                const newSettings = {...settings, biometricEnabled: false};
                await saveSettings(newSettings);
                Alert.alert('Succès', 'Authentification biométrique désactivée');
              } catch (error) {
                Alert.alert('Erreur', 'Impossible de désactiver la biométrie');
              }
            }
          }
        ]
      );
    }
  };

  const changeAutoLockTimeout = () => {
    Alert.alert(
      'Délai de verrouillage automatique',
      'Choisissez le délai après lequel l\'application se verrouille automatiquement:',
      [
        {text: '5 minutes', onPress: () => updateTimeout(5)},
        {text: '15 minutes', onPress: () => updateTimeout(15)},
        {text: '30 minutes', onPress: () => updateTimeout(30)},
        {text: '1 heure', onPress: () => updateTimeout(60)},
        {text: 'Jamais', onPress: () => updateTimeout(0)},
      ]
    );
  };

  const updateTimeout = async (timeout) => {
    const newSettings = {...settings, autoLockTimeout: timeout};
    await saveSettings(newSettings);
  };

  const exportData = async () => {
    try {
      const masterPwd = await getMasterPassword();
      if (!masterPwd) return;

      Alert.alert(
        'Export des données',
        'Cette action va créer un fichier contenant tous vos mots de passe chiffrés. Gardez ce fichier en sécurité.',
        [
          {text: 'Annuler', style: 'cancel'},
          {
            text: 'Exporter',
            onPress: async () => {
              try {
                const exportData = await StorageService.exportData(masterPwd);
                const exportString = JSON.stringify(exportData, null, 2);
                
                await Share.share({
                  message: exportString,
                  title: 'Export Gestionnaire de Mots de Passe',
                });
              } catch (error) {
                Alert.alert('Erreur', 'Impossible d\'exporter les données: ' + error.message);
              }
            }
          }
        ]
      );
    } catch (error) {
      console.error('Erreur lors de l\'export:', error);
    }
  };

  const clearAllData = () => {
    Alert.alert(
      'Supprimer toutes les données',
      'Cette action est irréversible. Tous vos mots de passe seront définitivement supprimés.',
      [
        {text: 'Annuler', style: 'cancel'},
        {
          text: 'Supprimer tout',
          style: 'destructive',
          onPress: () => {
            Alert.alert(
              'Confirmation finale',
              'Êtes-vous absolument sûr ? Cette action ne peut pas être annulée.',
              [
                {text: 'Annuler', style: 'cancel'},
                {
                  text: 'Oui, tout supprimer',
                  style: 'destructive',
                  onPress: async () => {
                    try {
                      await StorageService.clearAllData();
                      Alert.alert(
                        'Données supprimées',
                        'Toutes vos données ont été supprimées.',
                        [{text: 'OK', onPress: onLogout}]
                      );
                    } catch (error) {
                      Alert.alert('Erreur', 'Impossible de supprimer les données');
                    }
                  }
                }
              ]
            );
          }
        }
      ]
    );
  };

  const syncWithServer = async () => {
    try {
      const isOnline = await ApiService.isOnline();
      if (!isOnline) {
        Alert.alert('Erreur', 'Impossible de se connecter au serveur');
        return;
      }

      const masterPwd = await getMasterPassword();
      if (!masterPwd) return;

      Alert.alert('Information', 'Fonctionnalité de synchronisation en cours de développement');
    } catch (error) {
      Alert.alert('Erreur', 'Erreur lors de la synchronisation');
    }
  };

  const renderSecuritySection = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>🔐 Sécurité</Text>
      
      {biometricAvailable && (
        <TouchableOpacity
          style={styles.settingRow}
          onPress={() => toggleBiometric(!settings.biometricEnabled)}>
          <View style={{flex: 1}}>
            <Text style={GlobalStyles.text}>Authentification {biometricType}</Text>
            <Text style={GlobalStyles.textSecondary}>
              Déverrouiller avec votre biométrie
            </Text>
          </View>
          <Switch
            value={settings.biometricEnabled}
            onValueChange={toggleBiometric}
            trackColor={{false: '#767577', true: Colors.primary}}
            thumbColor={settings.biometricEnabled ? Colors.secondary : '#f4f3f4'}
          />
        </TouchableOpacity>
      )}
      
      <TouchableOpacity style={styles.settingRow} onPress={changeAutoLockTimeout}>
        <View style={{flex: 1}}>
          <Text style={GlobalStyles.text}>Verrouillage automatique</Text>
          <Text style={GlobalStyles.textSecondary}>
            {settings.autoLockTimeout === 0 
              ? 'Jamais' 
              : `Après ${settings.autoLockTimeout} minute${settings.autoLockTimeout > 1 ? 's' : ''}`
            }
          </Text>
        </View>
        <Text style={{color: Colors.primary}}>Modifier</Text>
      </TouchableOpacity>
    </View>
  );

  const renderDataSection = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>💾 Données</Text>
      
      <TouchableOpacity style={styles.settingRow} onPress={exportData}>
        <View style={{flex: 1}}>
          <Text style={GlobalStyles.text}>Exporter les données</Text>
          <Text style={GlobalStyles.textSecondary}>
            Créer une sauvegarde de vos mots de passe
          </Text>
        </View>
        <Text style={{color: Colors.primary}}>📤</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.settingRow} onPress={syncWithServer}>
        <View style={{flex: 1}}>
          <Text style={GlobalStyles.text}>Synchronisation</Text>
          <Text style={GlobalStyles.textSecondary}>
            Synchroniser avec le serveur
          </Text>
        </View>
        <Text style={{color: Colors.primary}}>🔄</Text>
      </TouchableOpacity>
    </View>
  );

  const renderAboutSection = () => (
    <View style={GlobalStyles.card}>
      <Text style={GlobalStyles.subtitle}>ℹ️ À propos</Text>
      
      <View style={styles.infoRow}>
        <Text style={GlobalStyles.text}>Version</Text>
        <Text style={GlobalStyles.textSecondary}>1.0.0</Text>
      </View>
      
      <View style={styles.infoRow}>
        <Text style={GlobalStyles.text}>Chiffrement</Text>
        <Text style={GlobalStyles.textSecondary}>AES-256</Text>
      </View>
      
      <View style={styles.infoRow}>
        <Text style={GlobalStyles.text}>Stockage</Text>
        <Text style={GlobalStyles.textSecondary}>Local sécurisé</Text>
      </View>
    </View>
  );

  const renderDangerZone = () => (
    <View style={[GlobalStyles.card, {borderColor: Colors.error, borderWidth: 1}]}>
      <Text style={[GlobalStyles.subtitle, {color: Colors.error}]}>⚠️ Zone dangereuse</Text>
      
      <TouchableOpacity
        style={[styles.settingRow, {borderBottomWidth: 0}]}
        onPress={clearAllData}>
        <View style={{flex: 1}}>
          <Text style={[GlobalStyles.text, {color: Colors.error}]}>
            Supprimer toutes les données
          </Text>
          <Text style={GlobalStyles.textSecondary}>
            Action irréversible - Tous vos mots de passe seront perdus
          </Text>
        </View>
        <Text style={{color: Colors.error}}>🗑️</Text>
      </TouchableOpacity>
    </View>
  );

  if (isLoading) {
    return (
      <View style={GlobalStyles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={[GlobalStyles.text, {marginTop: 16}]}>
          Chargement des paramètres...
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={GlobalStyles.container}>
      <View style={{paddingBottom: 24}}>
        <Text style={[GlobalStyles.title, {textAlign: 'center', marginBottom: 24}]}>
          ⚙️ Paramètres
        </Text>

        {renderSecuritySection()}
        {renderDataSection()}
        {renderAboutSection()}
        {renderDangerZone()}

        <TouchableOpacity
          style={[GlobalStyles.buttonSecondary, {marginTop: 24}]}
          onPress={onLogout}>
          <Text style={GlobalStyles.buttonSecondaryText}>🚪 Se déconnecter</Text>
        </TouchableOpacity>

        <View style={{marginTop: 24, padding: 16, backgroundColor: '#E8F5E8', borderRadius: 8}}>
          <Text style={[GlobalStyles.textSecondary, {textAlign: 'center', color: '#2E7D32'}]}>
            🛡️ Vos données sont chiffrées et stockées localement sur votre appareil. 
            Aucune donnée n'est transmise sans votre autorisation explicite.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = {
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
};

export default SettingsScreen;