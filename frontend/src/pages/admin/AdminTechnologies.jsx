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
  ArrowLeft, Plus, Edit2, Trash2, Save, X, 
  Code, Sun, Moon, CheckCircle, AlertCircle
} from 'lucide-react';

const AdminTechnologies = () => {
  const [technologies, setTechnologies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newTech, setNewTech] = useState({ name: '', category: '', level: 'intermediate', color: '#3b82f6' });
  const [showAddForm, setShowAddForm] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const categories = ['Frontend', 'Backend', 'Database', 'DevOps', 'Security', 'Other'];
  const levels = ['beginner', 'intermediate', 'advanced', 'expert'];

  useEffect(() => {
    fetchTechnologies();
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

  const fetchTechnologies = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/technologies`, { 
        headers 
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des technologies');
      }

      const data = await response.json();
      setTechnologies(data);
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

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/technologies`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newTech)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout de la technologie');
      }

      setSuccess('Technologie ajoutée avec succès');
      setNewTech({ name: '', category: '', level: 'intermediate', color: '#3b82f6' });
      setShowAddForm(false);
      fetchTechnologies();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdate = async (id, updatedTech) => {
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/technologies/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(updatedTech)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour');
      }

      setSuccess('Technologie mise à jour avec succès');
      setEditingId(null);
      fetchTechnologies();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette technologie ?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/technologies/${id}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      setSuccess('Technologie supprimée avec succès');
      fetchTechnologies();
    } catch (err) {
      setError(err.message);
    }
  };

  const getLevelColor = (level) => {
    if (!level) return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    
    const colors = {
      beginner: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      intermediate: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      advanced: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      expert: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    };
    return colors[level] || colors.intermediate;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Code className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Chargement des technologies...</p>
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
              <Code className="h-8 w-8 text-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Technologies
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Gérer les technologies et compétences techniques
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
                Ajouter une technologie
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
              <CardTitle>Ajouter une nouvelle technologie</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nom</Label>
                  <Input
                    id="name"
                    value={newTech.name}
                    onChange={(e) => setNewTech(prev => ({ ...prev, name: e.target.value }))}
                    required
                    placeholder="React, Python, MongoDB..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Catégorie</Label>
                  <select
                    id="category"
                    value={newTech.category}
                    onChange={(e) => setNewTech(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  >
                    <option value="">Sélectionner...</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="level">Niveau</Label>
                  <select
                    id="level"
                    value={newTech.level}
                    onChange={(e) => setNewTech(prev => ({ ...prev, level: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    {levels.map(level => (
                      <option key={level} value={level}>
                        {level ? level.charAt(0).toUpperCase() + level.slice(1) : 'Non défini'}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="color">Couleur</Label>
                  <Input
                    id="color"
                    type="color"
                    value={newTech.color}
                    onChange={(e) => setNewTech(prev => ({ ...prev, color: e.target.value }))}
                    className="h-10"
                  />
                </div>
                <div className="flex items-end space-x-2 md:col-span-2 lg:col-span-4">
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

        {/* Liste des technologies */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {technologies.map((tech) => (
            <Card key={tech.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                {editingId === tech.id ? (
                  <EditTechForm
                    tech={tech}
                    categories={categories}
                    levels={levels}
                    onSave={(updatedTech) => handleUpdate(tech.id, updatedTech)}
                    onCancel={() => setEditingId(null)}
                  />
                ) : (
                  <div>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: tech.color }}
                        />
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {tech.name}
                        </h3>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingId(tech.id)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(tech.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <Badge variant="secondary" className="mb-2">
                          {tech.category}
                        </Badge>
                      </div>
                      <div>
                        <Badge className={getLevelColor(tech.level)}>
                          {tech.level ? tech.level.charAt(0).toUpperCase() + tech.level.slice(1) : 'Non défini'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {technologies.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <Code className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucune technologie
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Commencez par ajouter vos premières technologies.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Ajouter une technologie
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

const EditTechForm = ({ tech, categories, levels, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: tech.name,
    category: tech.category,
    level: tech.level,
    color: tech.color
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="edit-name">Nom</Label>
        <Input
          id="edit-name"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="edit-category">Catégorie</Label>
        <select
          id="edit-category"
          value={formData.category}
          onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          required
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-level">Niveau</Label>
        <select
          id="edit-level"
          value={formData.level}
          onChange={(e) => setFormData(prev => ({ ...prev, level: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        >
          {levels.map(level => (
            <option key={level} value={level}>
              {level ? level.charAt(0).toUpperCase() + level.slice(1) : 'Non défini'}
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

export default AdminTechnologies;