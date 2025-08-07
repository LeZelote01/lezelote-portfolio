import React, {useEffect, useState} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {StatusBar, Alert} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import des écrans
import LoginScreen from './src/components/LoginScreen';
import PasswordListScreen from './src/components/PasswordListScreen';
import AddPasswordScreen from './src/components/AddPasswordScreen';
import PasswordGeneratorScreen from './src/components/PasswordGeneratorScreen';
import SettingsScreen from './src/components/SettingsScreen';
import SetupScreen from './src/components/SetupScreen';
import UnlockScreen from './src/components/UnlockScreen';

// Import des services
import {BiometricService} from './src/services/BiometricService';
import {StorageService} from './src/services/StorageService';

const Stack = createNativeStackNavigator();

const App = () => {
  const [isFirstLaunch, setIsFirstLaunch] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Vérifier si c'est le premier lancement
      const hasLaunched = await AsyncStorage.getItem('hasLaunched');
      if (hasLaunched === null) {
        setIsFirstLaunch(true);
      } else {
        setIsFirstLaunch(false);
        // Vérifier si l'utilisateur est déjà authentifié (session valide)
        const lastAuth = await AsyncStorage.getItem('lastAuthentication');
        if (lastAuth) {
          const authTime = parseInt(lastAuth);
          const now = Date.now();
          const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes
          
          if (now - authTime < SESSION_TIMEOUT) {
            setIsAuthenticated(true);
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors de l\'initialisation:', error);
      Alert.alert('Erreur', 'Erreur lors de l\'initialisation de l\'application');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFirstSetup = async () => {
    await AsyncStorage.setItem('hasLaunched', 'true');
    setIsFirstLaunch(false);
  };

  const handleAuthentication = async () => {
    await AsyncStorage.setItem('lastAuthentication', Date.now().toString());
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('lastAuthentication');
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return null; // Ou un écran de chargement
  }

  return (
    <NavigationContainer>
      <StatusBar 
        barStyle="dark-content" 
        backgroundColor="#6200EE" 
        translucent={false} 
      />
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#6200EE',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}>
        
        {isFirstLaunch ? (
          <Stack.Screen 
            name="Setup" 
            options={{title: 'Configuration Initiale'}}
          >
            {props => <SetupScreen {...props} onSetupComplete={handleFirstSetup} />}
          </Stack.Screen>
        ) : !isAuthenticated ? (
          <>
            <Stack.Screen 
              name="Unlock" 
              options={{title: 'Déverrouillage', headerShown: false}}
            >
              {props => <UnlockScreen {...props} onAuthenticated={handleAuthentication} />}
            </Stack.Screen>
            <Stack.Screen 
              name="Login" 
              options={{title: 'Connexion'}}
            >
              {props => <LoginScreen {...props} onAuthenticated={handleAuthentication} />}
            </Stack.Screen>
          </>
        ) : (
          <>
            <Stack.Screen 
              name="PasswordList" 
              options={{title: 'Mes Mots de Passe'}}
            >
              {props => <PasswordListScreen {...props} onLogout={handleLogout} />}
            </Stack.Screen>
            <Stack.Screen 
              name="AddPassword" 
              component={AddPasswordScreen}
              options={{title: 'Ajouter un Mot de Passe'}}
            />
            <Stack.Screen 
              name="PasswordGenerator" 
              component={PasswordGeneratorScreen}
              options={{title: 'Générateur de Mot de Passe'}}
            />
            <Stack.Screen 
              name="Settings" 
              options={{title: 'Paramètres'}}
            >
              {props => <SettingsScreen {...props} onLogout={handleLogout} />}
            </Stack.Screen>
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;