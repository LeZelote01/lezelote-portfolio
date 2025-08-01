import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import { useTheme } from '../../context/ThemeContext';
import { 
  ArrowLeft, Plus, Edit2, Trash2, Save, X, Download,
  FileText, Sun, Moon, CheckCircle, AlertCircle, Star
} from 'lucide-react';

const AdminResources = () => {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newResource, setNewResource] = useState({ 
    title: '', 
    description: '', 
    category: 'Guide', 
    type: 'PDF', 
    size: '',
    download_url: '',
    featured: false,
    tags: []
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const categories = ['Guide', 'Template', 'Script', 'Tool', 'Checklist', 'Formation'];
  const types = ['PDF', 'DOC', 'ZIP', 'DOCX', 'XLS', 'PPT'];

  useEffect(() => {
    fetchResources();
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

  const fetchResources = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/resources`, { 
        headers 
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des ressources');
      }

      const data = await response.json();
      setResources(data);
    } catch (err) {
      setError(err.message);
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

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/resources`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newResource)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout de la ressource');
      }

      setSuccess('Ressource ajoutée avec succès');
      setNewResource({ 
        title: '', 
        description: '', 
        category: 'Guide', 
        type: 'PDF', 
        size: '',
        download_url: '',
        featured: false,
        tags: []
      });
      setShowAddForm(false);
      fetchResources();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdate = async (id, updatedResource) => {
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/resources/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(updatedResource)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour');
      }

      setSuccess('Ressource mise à jour avec succès');
      setEditingId(null);
      fetchResources();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette ressource ?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/resources/${id}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      setSuccess('Ressource supprimée avec succès');
      fetchResources();
    } catch (err) {
      setError(err.message);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Guide': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      'Template': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'Script': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      'Tool': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      'Checklist': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
      'Formation': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300'
    };
    return colors[category] || colors.Guide;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <FileText className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Chargement des ressources...</p>
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
              <FileText className="h-8 w-8 text-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Ressources
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Gérer les ressources téléchargeables
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
                Ajouter une ressource
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
              <CardTitle>Ajouter une nouvelle ressource</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Titre</Label>
                  <Input
                    id="title"
                    value={newResource.title}
                    onChange={(e) => setNewResource(prev => ({ ...prev, title: e.target.value }))}
                    required
                    placeholder="Guide complet de..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Catégorie</Label>
                  <select
                    id="category"
                    value={newResource.category}
                    onChange={(e) => setNewResource(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="type">Type de fichier</Label>
                  <select
                    id="type"
                    value={newResource.type}
                    onChange={(e) => setNewResource(prev => ({ ...prev, type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    {types.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="size">Taille</Label>
                  <Input
                    id="size"
                    value={newResource.size}
                    onChange={(e) => setNewResource(prev => ({ ...prev, size: e.target.value }))}
                    placeholder="2.5 MB"
                    required
                  />
                </div>
                <div className="md:col-span-2 space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <textarea
                    id="description"
                    value={newResource.description}
                    onChange={(e) => setNewResource(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    rows="3"
                    required
                    placeholder="Description détaillée de la ressource..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="download_url">URL de téléchargement</Label>
                  <Input
                    id="download_url"
                    value={newResource.download_url}
                    onChange={(e) => setNewResource(prev => ({ ...prev, download_url: e.target.value }))}
                    placeholder="https://..."
                  />
                </div>
                <div className="space-y-2 flex items-center">
                  <input
                    type="checkbox"
                    id="featured"
                    checked={newResource.featured}
                    onChange={(e) => setNewResource(prev => ({ ...prev, featured: e.target.checked }))}
                    className="mr-2"
                  />
                  <Label htmlFor="featured">Ressource mise en avant</Label>
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

        {/* Liste des ressources */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resources.map((resource) => (
            <Card key={resource.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {resource.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {resource.description}
                    </p>
                  </div>
                  {resource.featured && (
                    <Star className="h-4 w-4 text-yellow-500" />
                  )}
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge className={getCategoryColor(resource.category)}>
                      {resource.category}
                    </Badge>
                    <span className="text-xs text-gray-500">{resource.type} • {resource.size}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center">
                      <Download className="h-4 w-4 mr-1" />
                      {resource.downloads || 0} téléchargements
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2 mt-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setEditingId(resource.id)}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(resource.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {resources.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucune ressource
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Commencez par ajouter vos premières ressources.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Ajouter une ressource
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default AdminResources;