import React, {useState, useEffect, useCallback} from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Alert,
  TextInput,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import Clipboard from '@react-native-clipboard/clipboard';
import {GlobalStyles, Colors} from '../styles/GlobalStyles';
import {StorageService} from '../services/StorageService';
import {ApiService} from '../services/ApiService';

const PasswordListScreen = ({navigation, onLogout}) => {
  const [passwords, setPasswords] = useState([]);
  const [filteredPasswords, setFilteredPasswords] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [masterPassword, setMasterPassword] = useState('');

  // Simuler la récupération du mot de passe maître depuis la session
  // Dans une vraie app, ceci serait géré par un contexte d'authentification
  const getMasterPassword = () => {
    // Pour cette démonstration, on demande le mot de passe une fois
    return new Promise((resolve) => {
      if (masterPassword) {
        resolve(masterPassword);
      } else {
        Alert.prompt(
          'Mot de passe requis',
          'Entrez votre mot de passe maître pour accéder aux données:',
          [
            {text: 'Annuler', style: 'cancel'},
            {
              text: 'OK',
              onPress: (password) => {
                setMasterPassword(password);
                resolve(password);
              }
            }
          ],
          'secure-text'
        );
      }
    });
  };

  useEffect(() => {
    loadPasswords();
  }, []);

  useEffect(() => {
    filterPasswords();
  }, [searchQuery, passwords]);

  const loadPasswords = async () => {
    try {
      setIsLoading(true);
      const masterPwd = await getMasterPassword();
      if (!masterPwd) return;

      const passwordList = await StorageService.getAllPasswords(masterPwd);
      setPasswords(passwordList);
    } catch (error) {
      console.error('Erreur lors du chargement des mots de passe:', error);
      Alert.alert('Erreur', 'Impossible de charger les mots de passe: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const filterPasswords = () => {
    if (searchQuery.trim() === '') {
      setFilteredPasswords(passwords);
    } else {
      const filtered = passwords.filter(item =>
        item.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.website?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.username?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredPasswords(filtered);
    }
  };

  const refreshPasswords = useCallback(async () => {
    setIsRefreshing(true);
    await loadPasswords();
    setIsRefreshing(false);
  }, []);

  const copyToClipboard = (text, label) => {
    Clipboard.setString(text);
    Alert.alert('Copié', `${label} copié dans le presse-papier`);
  };

  const handleDeletePassword = (passwordId, title) => {
    Alert.alert(
      'Supprimer le mot de passe',
      `Êtes-vous sûr de vouloir supprimer "${title}" ?`,
      [
        {text: 'Annuler', style: 'cancel'},
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: () => deletePassword(passwordId)
        }
      ]
    );
  };

  const deletePassword = async (passwordId) => {
    try {
      const masterPwd = await getMasterPassword();
      if (!masterPwd) return;

      await StorageService.deletePassword(passwordId, masterPwd);
      await loadPasswords();
      Alert.alert('Succès', 'Mot de passe supprimé');
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      Alert.alert('Erreur', 'Impossible de supprimer le mot de passe');
    }
  };

  const handleEditPassword = (passwordItem) => {
    navigation.navigate('AddPassword', {
      editMode: true,
      passwordData: passwordItem,
      onSave: loadPasswords
    });
  };

  const renderPasswordItem = ({item}) => (
    <View style={GlobalStyles.card}>
      <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start'}}>
        <View style={{flex: 1}}>
          <Text style={GlobalStyles.listItemTitle}>{item.title || 'Sans titre'}</Text>
          {item.website && (
            <Text style={GlobalStyles.listItemSubtitle}>🌐 {item.website}</Text>
          )}
          {item.username && (
            <Text style={GlobalStyles.listItemSubtitle}>👤 {item.username}</Text>
          )}
          {item.notes && (
            <Text style={[GlobalStyles.listItemSubtitle, {marginTop: 4}]}>
              📝 {item.notes.length > 50 ? item.notes.substring(0, 50) + '...' : item.notes}
            </Text>
          )}
        </View>
        
        <View style={{flexDirection: 'row', alignItems: 'center', marginLeft: 8}}>
          <TouchableOpacity
            style={{padding: 8, marginRight: 4}}
            onPress={() => copyToClipboard(item.username || '', 'Nom d\'utilisateur')}>
            <Text style={{fontSize: 18}}>👤</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={{padding: 8, marginRight: 4}}
            onPress={() => copyToClipboard(item.password || '', 'Mot de passe')}>
            <Text style={{fontSize: 18}}>🔑</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={{padding: 8, marginRight: 4}}
            onPress={() => handleEditPassword(item)}>
            <Text style={{fontSize: 18}}>✏️</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={{padding: 8}}
            onPress={() => handleDeletePassword(item.id, item.title)}>
            <Text style={{fontSize: 18}}>🗑️</Text>
          </TouchableOpacity>
        </View>
      </View>
      
      {item.createdAt && (
        <Text style={[GlobalStyles.textSecondary, {fontSize: 11, marginTop: 8}]}>
          Créé le {new Date(item.createdAt).toLocaleDateString('fr-FR')}
        </Text>
      )}
    </View>
  );

  const renderEmptyState = () => (
    <View style={GlobalStyles.emptyState}>
      <Text style={{fontSize: 48, marginBottom: 16}}>🔐</Text>
      <Text style={GlobalStyles.emptyStateText}>
        Aucun mot de passe enregistré
      </Text>
      <Text style={[GlobalStyles.textSecondary, {textAlign: 'center', marginTop: 8}]}>
        Appuyez sur le bouton + pour ajouter votre premier mot de passe
      </Text>
    </View>
  );

  if (isLoading) {
    return (
      <View style={GlobalStyles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={[GlobalStyles.text, {marginTop: 16}]}>
          Chargement de vos mots de passe...
        </Text>
      </View>
    );
  }

  return (
    <View style={GlobalStyles.container}>
      {/* Barre de recherche */}
      <View style={{marginBottom: 16}}>
        <TextInput
          style={GlobalStyles.input}
          placeholder="Rechercher un mot de passe..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          autoCapitalize="none"
        />
      </View>

      {/* Liste des mots de passe */}
      <FlatList
        data={filteredPasswords}
        renderItem={renderPasswordItem}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={refreshPasswords}
            colors={[Colors.primary]}
          />
        }
        showsVerticalScrollIndicator={false}
      />

      {/* Bouton d'ajout flottant */}
      <TouchableOpacity
        style={GlobalStyles.fab}
        onPress={() => navigation.navigate('AddPassword', {onSave: loadPasswords})}>
        <Text style={GlobalStyles.fabText}>+</Text>
      </TouchableOpacity>

      {/* Menu d'options */}
      <View style={{
        position: 'absolute',
        top: 0,
        right: 0,
        flexDirection: 'row',
        padding: 16,
      }}>
        <TouchableOpacity
          style={{padding: 8, marginRight: 8, backgroundColor: Colors.surface, borderRadius: 20, elevation: 2}}
          onPress={() => navigation.navigate('PasswordGenerator')}>
          <Text style={{fontSize: 20}}>🎲</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={{padding: 8, marginRight: 8, backgroundColor: Colors.surface, borderRadius: 20, elevation: 2}}
          onPress={() => navigation.navigate('Settings')}>
          <Text style={{fontSize: 20}}>⚙️</Text>
        </TouchableOpacity>
      </View>

      {/* Informations sur le nombre de mots de passe */}
      {filteredPasswords.length > 0 && (
        <View style={{
          padding: 8,
          backgroundColor: Colors.surface,
          borderTopWidth: 1,
          borderTopColor: '#E0E0E0',
        }}>
          <Text style={[GlobalStyles.textSecondary, {textAlign: 'center'}]}>
            {filteredPasswords.length} mot{filteredPasswords.length > 1 ? 's' : ''} de passe
            {searchQuery && ` (sur ${passwords.length} total)`}
          </Text>
        </View>
      )}
    </View>
  );
};

export default PasswordListScreen;