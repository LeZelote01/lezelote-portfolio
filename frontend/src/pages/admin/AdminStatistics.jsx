import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useTheme } from '../../context/ThemeContext';
import { 
  ArrowLeft, Plus, Edit2, Trash2, Save, X, 
  BarChart3, Sun, Moon, CheckCircle, AlertCircle,
  TrendingUp, Users, Award, Clock
} from 'lucide-react';

const AdminStatistics = () => {
  const [statistics, setStatistics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newStat, setNewStat] = useState({ 
    title: '', 
    value: '', 
    suffix: '', 
    description: '', 
    icon: 'TrendingUp', 
    color: '#3b82f6',
    order_index: 0
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const iconOptions = [
    { value: 'TrendingUp', label: 'Tendance', icon: TrendingUp },
    { value: 'Users', label: 'Utilisateurs', icon: Users },
    { value: 'Award', label: 'Récompense', icon: Award },
    { value: 'Clock', label: 'Temps', icon: Clock },
    { value: 'BarChart3', label: 'Graphique', icon: BarChart3 }
  ];

  useEffect(() => {
    fetchStatistics();
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    const tokenType = localStorage.getItem('admin_token_type');
    
    if (!token) {
      navigate('/admin/login');
      return null;
    }
    
    return {
      'Authorization': `${tokenType} ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const handleAuthError = (response) => {
    if (response.status === 401) {
      // Token expiré ou invalide, nettoyer le localStorage et rediriger
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_token_type');
      navigate('/admin/login');
      return true;
    }
    return false;
  };

  const fetchStatistics = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/statistics`, { 
        headers 
      });

      // Gérer les erreurs d'authentification
      if (handleAuthError(response)) {
        return;
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      setStatistics(data.sort((a, b) => a.order_index - b.order_index));
      setError(''); // Nettoyer les erreurs précédentes
    } catch (err) {
      console.error('Erreur fetchStatistics:', err);
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Erreur de connexion réseau. Vérifiez que le serveur backend est accessible.');
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/statistics`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ ...newStat, order_index: statistics.length })
      });

      // Gérer les erreurs d'authentification
      if (handleAuthError(response)) {
        return;
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      setSuccess('Statistique ajoutée avec succès');
      setNewStat({ 
        title: '', 
        value: '', 
        suffix: '', 
        description: '', 
        icon: 'TrendingUp', 
        color: '#3b82f6',
        order_index: 0
      });
      setShowAddForm(false);
      fetchStatistics(); // Recharger les statistiques
    } catch (err) {
      console.error('Erreur handleAdd:', err);
      setError(err.message);
    }
  };

  const handleUpdate = async (id, updatedStat) => {
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/statistics/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(updatedStat)
      });

      // Gérer les erreurs d'authentification
      if (handleAuthError(response)) {
        return;
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      setSuccess('Statistique mise à jour avec succès');
      setEditingId(null);
      fetchStatistics();
    } catch (err) {
      console.error('Erreur handleUpdate:', err);
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette statistique ?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/statistics/${id}`, {
        method: 'DELETE',
        headers
      });

      // Gérer les erreurs d'authentification
      if (handleAuthError(response)) {
        return;
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      setSuccess('Statistique supprimée avec succès');
      fetchStatistics();
    } catch (err) {
      console.error('Erreur handleDelete:', err);
      setError(err.message);
    }
  };

  const getIconComponent = (iconName) => {
    const iconOption = iconOptions.find(opt => opt.value === iconName);
    return iconOption ? iconOption.icon : TrendingUp;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Chargement des statistiques...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Button
                variant="ghost"
                onClick={() => navigate('/admin/dashboard')}
                className="mr-4"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Retour
              </Button>
              <BarChart3 className="h-8 w-8 text-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Statistiques
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Gérer les statistiques du portfolio
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                onClick={toggleTheme}
                className="hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
              <Button onClick={() => setShowAddForm(!showAddForm)}>
                <Plus className="h-4 w-4 mr-2" />
                Ajouter une statistique
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50 dark:bg-green-900/20">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800 dark:text-green-200">{success}</AlertDescription>
          </Alert>
        )}

        {/* Formulaire d'ajout */}
        {showAddForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Ajouter une nouvelle statistique</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Titre</Label>
                  <Input
                    id="title"
                    value={newStat.title}
                    onChange={(e) => setNewStat(prev => ({ ...prev, title: e.target.value }))}
                    required
                    placeholder="Projets réalisés, Clients satisfaits..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="value">Valeur</Label>
                  <Input
                    id="value"
                    value={newStat.value}
                    onChange={(e) => setNewStat(prev => ({ ...prev, value: e.target.value }))}
                    required
                    placeholder="150, 95, 2..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="suffix">Suffixe</Label>
                  <Input
                    id="suffix"
                    value={newStat.suffix}
                    onChange={(e) => setNewStat(prev => ({ ...prev, suffix: e.target.value }))}
                    placeholder="+, %, ans d'expérience..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newStat.description}
                    onChange={(e) => setNewStat(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Description courte de la statistique"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="icon">Icône</Label>
                  <select
                    id="icon"
                    value={newStat.icon}
                    onChange={(e) => setNewStat(prev => ({ ...prev, icon: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    {iconOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="color">Couleur</Label>
                  <Input
                    id="color"
                    type="color"
                    value={newStat.color}
                    onChange={(e) => setNewStat(prev => ({ ...prev, color: e.target.value }))}
                    className="h-10"
                  />
                </div>
                <div className="flex items-end space-x-2 md:col-span-2">
                  <Button type="submit">
                    <Save className="h-4 w-4 mr-2" />
                    Ajouter
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                    <X className="h-4 w-4 mr-2" />
                    Annuler
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Liste des statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {statistics.map((stat) => {
            const IconComponent = getIconComponent(stat.icon);
            
            return (
              <Card key={stat.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  {editingId === stat.id ? (
                    <EditStatForm
                      stat={stat}
                      iconOptions={iconOptions}
                      onSave={(updatedStat) => handleUpdate(stat.id, updatedStat)}
                      onCancel={() => setEditingId(null)}
                    />
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div 
                            className="p-3 rounded-lg"
                            style={{ backgroundColor: `${stat.color}20` }}
                          >
                            <IconComponent 
                              className="h-6 w-6" 
                              style={{ color: stat.color }}
                            />
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingId(stat.id)}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(stat.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-baseline space-x-1">
                          <span className="text-2xl font-bold text-gray-900 dark:text-white">
                            {stat.value}
                          </span>
                          {stat.suffix && (
                            <span className="text-lg font-medium text-gray-600 dark:text-gray-400">
                              {stat.suffix}
                            </span>
                          )}
                        </div>
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                          {stat.title}
                        </h3>
                        {stat.description && (
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {stat.description}
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {statistics.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucune statistique
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Commencez par ajouter vos premières statistiques.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Ajouter une statistique
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

const EditStatForm = ({ stat, iconOptions, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    title: stat.title,
    value: stat.value,
    suffix: stat.suffix || '',
    description: stat.description || '',
    icon: stat.icon,
    color: stat.color,
    order_index: stat.order_index
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="edit-title">Titre</Label>
        <Input
          id="edit-title"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          required
        />
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-2">
          <Label htmlFor="edit-value">Valeur</Label>
          <Input
            id="edit-value"
            value={formData.value}
            onChange={(e) => setFormData(prev => ({ ...prev, value: e.target.value }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="edit-suffix">Suffixe</Label>
          <Input
            id="edit-suffix"
            value={formData.suffix}
            onChange={(e) => setFormData(prev => ({ ...prev, suffix: e.target.value }))}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-description">Description</Label>
        <Input
          id="edit-description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
        />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-2">
          <Label htmlFor="edit-icon">Icône</Label>
          <select
            id="edit-icon"
            value={formData.icon}
            onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            {iconOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="edit-color">Couleur</Label>
          <Input
            id="edit-color"
            type="color"
            value={formData.color}
            onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
            className="h-10"
          />
        </div>
      </div>

      <div className="flex space-x-2">
        <Button type="submit" size="sm">
          <Save className="h-4 w-4 mr-2" />
          Sauvegarder
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={onCancel}>
          <X className="h-4 w-4 mr-2" />
          Annuler
        </Button>
      </div>
    </form>
  );
};

export default AdminStatistics;