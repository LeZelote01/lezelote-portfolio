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
  GitBranch, Sun, Moon, CheckCircle, AlertCircle,
  Search, FileText, Code, CheckSquare, Zap
} from 'lucide-react';

const AdminProcessSteps = () => {
  const [processSteps, setProcessSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newStep, setNewStep] = useState({ 
    step: 1,
    title: '', 
    description: '', 
    icon: 'Search', 
    color: '#3b82f6',
    duration: ''
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const iconOptions = [
    { value: 'Search', label: 'Recherche', icon: Search },
    { value: 'FileText', label: 'Analyse', icon: FileText },
    { value: 'Code', label: 'Développement', icon: Code },
    { value: 'CheckSquare', label: 'Test', icon: CheckSquare },
    { value: 'Zap', label: 'Déploiement', icon: Zap },
    { value: 'GitBranch', label: 'Processus', icon: GitBranch }
  ];

  useEffect(() => {
    fetchProcessSteps();
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

  const fetchProcessSteps = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/process-steps`, { 
        headers 
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des étapes de processus');
      }

      const data = await response.json();
      setProcessSteps(data.sort((a, b) => a.step - b.step));
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

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/process-steps`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newStep)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout de l\'étape');
      }

      setSuccess('Étape ajoutée avec succès');
      setNewStep({ 
        step: Math.max(...processSteps.map(s => s.step), 0) + 1,
        title: '', 
        description: '', 
        icon: 'Search', 
        color: '#3b82f6',
        duration: ''
      });
      setShowAddForm(false);
      fetchProcessSteps();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdate = async (id, updatedStep) => {
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/process-steps/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(updatedStep)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour');
      }

      setSuccess('Étape mise à jour avec succès');
      setEditingId(null);
      fetchProcessSteps();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette étape ?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/process-steps/${id}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      setSuccess('Étape supprimée avec succès');
      fetchProcessSteps();
    } catch (err) {
      setError(err.message);
    }
  };

  const getIconComponent = (iconName) => {
    const iconOption = iconOptions.find(opt => opt.value === iconName);
    return iconOption ? iconOption.icon : GitBranch;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <GitBranch className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Chargement des étapes de processus...</p>
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
              <GitBranch className="h-8 w-8 text-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Étapes de Processus
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Gérer les étapes du processus de travail
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
                Ajouter une étape
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
              <CardTitle>Ajouter une nouvelle étape de processus</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="step">Numéro d'étape</Label>
                  <Input
                    id="step"
                    type="number"
                    min="1"
                    value={newStep.step}
                    onChange={(e) => setNewStep(prev => ({ ...prev, step: parseInt(e.target.value) }))}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="title">Titre</Label>
                  <Input
                    id="title"
                    value={newStep.title}
                    onChange={(e) => setNewStep(prev => ({ ...prev, title: e.target.value }))}
                    required
                    placeholder="Analyse des besoins, Développement..."
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="description">Description</Label>
                  <textarea
                    id="description"
                    value={newStep.description}
                    onChange={(e) => setNewStep(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 min-h-[100px]"
                    placeholder="Description détaillée de l'étape..."
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="icon">Icône</Label>
                  <select
                    id="icon"
                    value={newStep.icon}
                    onChange={(e) => setNewStep(prev => ({ ...prev, icon: e.target.value }))}
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
                  <Label htmlFor="duration">Durée estimée</Label>
                  <Input
                    id="duration"
                    value={newStep.duration}
                    onChange={(e) => setNewStep(prev => ({ ...prev, duration: e.target.value }))}
                    placeholder="2-3 jours, 1 semaine..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="color">Couleur</Label>
                  <Input
                    id="color"
                    type="color"
                    value={newStep.color}
                    onChange={(e) => setNewStep(prev => ({ ...prev, color: e.target.value }))}
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

        {/* Liste des étapes de processus */}
        <div className="space-y-6">
          {processSteps.map((step, index) => {
            const IconComponent = getIconComponent(step.icon);
            
            return (
              <Card key={step.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  {editingId === step.id ? (
                    <EditStepForm
                      step={step}
                      iconOptions={iconOptions}
                      onSave={(updatedStep) => handleUpdate(step.id, updatedStep)}
                      onCancel={() => setEditingId(null)}
                    />
                  ) : (
                    <div className="flex items-start space-x-6">
                      {/* Step indicator */}
                      <div className="flex flex-col items-center">
                        <div 
                          className="p-4 rounded-full mb-2"
                          style={{ backgroundColor: `${step.color}20` }}
                        >
                          <IconComponent 
                            className="h-8 w-8" 
                            style={{ color: step.color }}
                          />
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          Étape {step.step}
                        </Badge>
                      </div>

                      {/* Content */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                              {step.title}
                            </h3>
                            {step.duration && (
                              <Badge variant="outline" className="mb-3">
                                {step.duration}
                              </Badge>
                            )}
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setEditingId(step.id)}
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(step.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        
                        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                          {step.description}
                        </p>
                      </div>

                      {/* Connector line */}
                      {index < processSteps.length - 1 && (
                        <div className="absolute left-[2.5rem] mt-20 h-12 w-0.5 bg-gray-200 dark:bg-gray-700 -z-10"></div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {processSteps.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <GitBranch className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucune étape de processus
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Commencez par ajouter vos premières étapes de processus.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Ajouter une étape
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

const EditStepForm = ({ step, iconOptions, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    step: step.step,
    title: step.title,
    description: step.description,
    icon: step.icon,
    color: step.color,
    duration: step.duration || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="edit-step">Numéro d'étape</Label>
          <Input
            id="edit-step"
            type="number"
            min="1"
            value={formData.step}
            onChange={(e) => setFormData(prev => ({ ...prev, step: parseInt(e.target.value) }))}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="edit-title">Titre</Label>
          <Input
            id="edit-title"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            required
          />
        </div>
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="edit-description">Description</Label>
        <textarea
          id="edit-description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 min-h-[100px]"
          required
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
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
          <Label htmlFor="edit-duration">Durée</Label>
          <Input
            id="edit-duration"
            value={formData.duration}
            onChange={(e) => setFormData(prev => ({ ...prev, duration: e.target.value }))}
          />
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

export default AdminProcessSteps;