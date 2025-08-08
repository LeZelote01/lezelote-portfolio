import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Badge } from '../../components/ui/badge';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { 
  Plus, Edit, Trash2, Save, X, ArrowLeft, 
  FolderOpen, ExternalLink, Github 
} from 'lucide-react';

const AdminProjects = () => {
  const [projects, setProjects] = useState([]);
  const [editingProject, setEditingProject] = useState(null);
  const [newProject, setNewProject] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const initialProjectState = {
    title: '',
    category: 'Cybersécurité',
    level: 'Débutant',
    description: '',
    technologies: [],
    features: [],
    status: 'En cours',
    duration: '',
    github: '',
    demo: '',
    order_index: 0
  };

  useEffect(() => {
    fetchProjects();
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

  const fetchProjects = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/projects`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des projets');
      }

      const data = await response.json();
      setProjects(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProject = async (projectData) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const isNewProject = !projectData.id;
      const url = isNewProject 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin/projects`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin/projects/${projectData.id}`;

      const method = isNewProject ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers,
        body: JSON.stringify({
          title: projectData.title,
          category: projectData.category,
          level: projectData.level,
          description: projectData.description,
          technologies: projectData.technologies,
          features: projectData.features,
          status: projectData.status,
          duration: projectData.duration,
          github: projectData.github || null,
          demo: projectData.demo || null,
          order_index: projectData.order_index
        })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la sauvegarde');
      }

      await fetchProjects();
      setEditingProject(null);
      setNewProject(false);
      setSuccess(isNewProject ? 'Projet créé avec succès' : 'Projet modifié avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce projet ?')) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/projects/${projectId}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      await fetchProjects();
      setSuccess('Projet supprimé avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const ProjectForm = ({ project, onSave, onCancel }) => {
    const [formData, setFormData] = useState(project || initialProjectState);

    const handleSubmit = (e) => {
      e.preventDefault();
      onSave(formData);
    };

    const handleArrayChange = (field, value) => {
      const array = value.split('\n').filter(item => item.trim() !== '');
      setFormData(prev => ({ ...prev, [field]: array }));
    };

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>
            {project ? 'Modifier le projet' : 'Nouveau projet'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Titre *</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  required
                />
              </div>
              <div>
                <Label>Catégorie</Label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                >
                  <option value="Cybersécurité">Cybersécurité</option>
                  <option value="Python">Python</option>
                  <option value="Réseaux">Réseaux</option>
                  <option value="Forensique">Forensique</option>
                </select>
              </div>
              <div>
                <Label>Niveau</Label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.level}
                  onChange={(e) => setFormData(prev => ({ ...prev, level: e.target.value }))}
                >
                  <option value="Débutant">Débutant</option>
                  <option value="Intermédiaire">Intermédiaire</option>
                  <option value="Avancé">Avancé</option>
                </select>
              </div>
              <div>
                <Label>Statut</Label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                >
                  <option value="En cours">En cours</option>
                  <option value="Terminé">Terminé</option>
                  <option value="Planifié">Planifié</option>
                </select>
              </div>
            </div>

            <div>
              <Label>Description *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Technologies (une par ligne)</Label>
                <Textarea
                  value={formData.technologies.join('\n')}
                  onChange={(e) => handleArrayChange('technologies', e.target.value)}
                  rows={4}
                  placeholder="Python&#10;FastAPI&#10;MongoDB"
                />
              </div>
              <div>
                <Label>Fonctionnalités (une par ligne)</Label>
                <Textarea
                  value={formData.features.join('\n')}
                  onChange={(e) => handleArrayChange('features', e.target.value)}
                  rows={4}
                  placeholder="Interface utilisateur&#10;API REST&#10;Base de données"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Durée</Label>
                <Input
                  value={formData.duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration: e.target.value }))}
                  placeholder="2 semaines"
                />
              </div>
              <div>
                <Label>Lien GitHub</Label>
                <Input
                  value={formData.github}
                  onChange={(e) => setFormData(prev => ({ ...prev, github: e.target.value }))}
                  placeholder="https://github.com/..."
                />
              </div>
              <div>
                <Label>Lien démo</Label>
                <Input
                  value={formData.demo}
                  onChange={(e) => setFormData(prev => ({ ...prev, demo: e.target.value }))}
                  placeholder="https://demo.example.com"
                />
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
        <p>Chargement des projets...</p>
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
                  Gestion des projets
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {projects.length} projet{projects.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <Button onClick={() => setNewProject(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Nouveau projet
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

        {(newProject || editingProject) && (
          <ProjectForm
            project={editingProject}
            onSave={handleSaveProject}
            onCancel={() => {
              setNewProject(false);
              setEditingProject(null);
            }}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {projects.map((project) => (
            <Card key={project.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{project.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {project.category} • {project.level} • {project.duration}
                    </CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingProject(project)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteProject(project.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Badge 
                    variant={project.status === 'Terminé' ? 'default' : 
                            project.status === 'En cours' ? 'secondary' : 'outline'}
                  >
                    {project.status}
                  </Badge>

                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {project.description}
                  </p>

                  {project.technologies.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Technologies :</p>
                      <div className="flex flex-wrap gap-1">
                        {project.technologies.map((tech, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-4">
                    {project.github && (
                      <a
                        href={project.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                      >
                        <Github className="w-4 h-4 mr-1" />
                        GitHub
                      </a>
                    )}
                    {project.demo && (
                      <a
                        href={project.demo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        Démo
                      </a>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {projects.length === 0 && !loading && (
          <Card>
            <CardContent className="text-center py-12">
              <FolderOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucun projet
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Commencez par créer votre premier projet.
              </p>
              <Button onClick={() => setNewProject(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Créer un projet
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default AdminProjects;