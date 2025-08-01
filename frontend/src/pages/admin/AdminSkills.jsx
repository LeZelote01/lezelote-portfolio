import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { 
  Plus, Edit, Trash2, Save, X, ArrowLeft, 
  Code, Shield, Network, Minus
} from 'lucide-react';

const AdminSkills = () => {
  const [skillCategories, setSkillCategories] = useState([]);
  const [editingCategory, setEditingCategory] = useState(null);
  const [newCategory, setNewCategory] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const initialCategoryState = {
    title: '',
    icon: 'Code',
    category_key: '',
    items: [{ name: '', level: 50 }]
  };

  const iconOptions = [
    { value: 'Code', label: 'Code', icon: Code },
    { value: 'Shield', label: 'Shield', icon: Shield },
    { value: 'Network', label: 'Network', icon: Network }
  ];

  useEffect(() => {
    fetchSkillCategories();
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

  const fetchSkillCategories = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/skills`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des compétences');
      }

      const data = await response.json();
      setSkillCategories(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCategory = async (categoryData) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const isNewCategory = !categoryData.id;
      const url = isNewCategory 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin/skills`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin/skills/${categoryData.id}`;

      const method = isNewCategory ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers,
        body: JSON.stringify({
          title: categoryData.title,
          icon: categoryData.icon,
          category_key: categoryData.category_key,
          items: categoryData.items
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la sauvegarde');
      }

      await fetchSkillCategories();
      setEditingCategory(null);
      setNewCategory(false);
      setSuccess(isNewCategory ? 'Catégorie créée avec succès' : 'Catégorie modifiée avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette catégorie de compétences ?')) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/skills/${categoryId}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      await fetchSkillCategories();
      setSuccess('Catégorie supprimée avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const CategoryForm = ({ category, onSave, onCancel }) => {
    const [formData, setFormData] = useState(category || initialCategoryState);

    const handleSubmit = (e) => {
      e.preventDefault();
      onSave(formData);
    };

    const addSkillItem = () => {
      setFormData(prev => ({
        ...prev,
        items: [...prev.items, { name: '', level: 50 }]
      }));
    };

    const removeSkillItem = (index) => {
      setFormData(prev => ({
        ...prev,
        items: prev.items.filter((_, i) => i !== index)
      }));
    };

    const updateSkillItem = (index, field, value) => {
      setFormData(prev => ({
        ...prev,
        items: prev.items.map((item, i) => 
          i === index ? { ...item, [field]: value } : item
        )
      }));
    };

    const generateKey = (title) => {
      return title.toLowerCase()
        .replace(/[éèêë]/g, 'e')
        .replace(/[àâ]/g, 'a')
        .replace(/[ç]/g, 'c')
        .replace(/[^a-z0-9]/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '');
    };

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>
            {category ? 'Modifier la catégorie' : 'Nouvelle catégorie'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Titre *</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => {
                    const newTitle = e.target.value;
                    setFormData(prev => ({ 
                      ...prev, 
                      title: newTitle,
                      category_key: generateKey(newTitle)
                    }));
                  }}
                  required
                  placeholder="Cybersécurité"
                />
              </div>
              <div>
                <Label>Icône</Label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.icon}
                  onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
                >
                  {iconOptions.map(icon => (
                    <option key={icon.value} value={icon.value}>
                      {icon.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Clé (auto-générée)</Label>
                <Input
                  value={formData.category_key}
                  onChange={(e) => setFormData(prev => ({ ...prev, category_key: e.target.value }))}
                  placeholder="cybersecurite"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-4">
                <Label>Compétences</Label>
                <Button type="button" onClick={addSkillItem} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Ajouter
                </Button>
              </div>
              
              <div className="space-y-4">
                {formData.items.map((item, index) => (
                  <div key={index} className="flex items-center space-x-4 p-4 border rounded-md">
                    <div className="flex-1">
                      <Input
                        value={item.name}
                        onChange={(e) => updateSkillItem(index, 'name', e.target.value)}
                        placeholder="Nom de la compétence"
                        required
                      />
                    </div>
                    <div className="w-32">
                      <div className="flex items-center space-x-2">
                        <Input
                          type="range"
                          min="0"
                          max="100"
                          value={item.level}
                          onChange={(e) => updateSkillItem(index, 'level', parseInt(e.target.value))}
                          className="flex-1"
                        />
                        <span className="text-sm font-medium w-10 text-center">
                          {item.level}%
                        </span>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => removeSkillItem(index)}
                      disabled={formData.items.length === 1}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex space-x-4">
              <Button type="submit">
                <Save className="w-4 h-4 mr-2" />
                Sauvegarder
              </Button>
              <Button type="button" variant="outline" onClick={onCancel}>
                <X className="w-4 h-4 mr-2" />
                Annuler
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <p>Chargement des compétences...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Button
                variant="outline"
                onClick={() => navigate('/admin/dashboard')}
                className="mr-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Gestion des compétences
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {skillCategories.length} catégorie{skillCategories.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <Button onClick={() => setNewCategory(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Nouvelle catégorie
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {(newCategory || editingCategory) && (
          <CategoryForm
            category={editingCategory}
            onSave={handleSaveCategory}
            onCancel={() => {
              setNewCategory(false);
              setEditingCategory(null);
            }}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {skillCategories.map((category) => {
            const IconComponent = iconOptions.find(opt => opt.value === category.icon)?.icon || Code;
            
            return (
              <Card key={category.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center">
                      <IconComponent className="w-6 h-6 mr-3 text-primary" />
                      <div>
                        <CardTitle className="text-lg">{category.title}</CardTitle>
                        <CardDescription>
                          {category.items.length} compétence{category.items.length !== 1 ? 's' : ''}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingCategory(category)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDeleteCategory(category.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {category.items.map((skill, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm font-medium">{skill.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-primary h-2 rounded-full" 
                              style={{ width: `${skill.level}%` }}
                            ></div>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {skill.level}%
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {skillCategories.length === 0 && !loading && (
          <Card>
            <CardContent className="text-center py-12">
              <Code className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucune compétence
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Commencez par créer votre première catégorie de compétences.
              </p>
              <Button onClick={() => setNewCategory(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Créer une catégorie
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default AdminSkills;