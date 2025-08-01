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
  Briefcase, Euro, Clock, Minus
} from 'lucide-react';

const AdminServices = () => {
  const [services, setServices] = useState([]);
  const [editingService, setEditingService] = useState(null);
  const [newService, setNewService] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const initialServiceState = {
    title: '',
    icon: 'Briefcase',
    description: '',
    features: [''],
    price: '',
    duration: '',
    order_index: 0
  };

  const iconOptions = [
    { value: 'Briefcase', label: 'Briefcase' },
    { value: 'Shield', label: 'Shield' },
    { value: 'Code', label: 'Code' },
    { value: 'Users', label: 'Users' },
    { value: 'Server', label: 'Server' }
  ];

  useEffect(() => {
    fetchServices();
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

  const fetchServices = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/services`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des services');
      }

      const data = await response.json();
      setServices(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveService = async (serviceData) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const isNewService = !serviceData.id;
      const url = isNewService 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin/services`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin/services/${serviceData.id}`;

      const method = isNewService ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers,
        body: JSON.stringify({
          title: serviceData.title,
          icon: serviceData.icon,
          description: serviceData.description,
          features: serviceData.features.filter(f => f.trim() !== ''),
          price: serviceData.price,
          duration: serviceData.duration,
          order_index: serviceData.order_index
        })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la sauvegarde');
      }

      await fetchServices();
      setEditingService(null);
      setNewService(false);
      setSuccess(isNewService ? 'Service créé avec succès' : 'Service modifié avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteService = async (serviceId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce service ?')) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/services/${serviceId}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      await fetchServices();
      setSuccess('Service supprimé avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const ServiceForm = ({ service, onSave, onCancel }) => {
    const [formData, setFormData] = useState(service || initialServiceState);

    const handleSubmit = (e) => {
      e.preventDefault();
      onSave(formData);
    };

    const addFeature = () => {
      setFormData(prev => ({
        ...prev,
        features: [...prev.features, '']
      }));
    };

    const removeFeature = (index) => {
      setFormData(prev => ({
        ...prev,
        features: prev.features.filter((_, i) => i !== index)
      }));
    };

    const updateFeature = (index, value) => {
      setFormData(prev => ({
        ...prev,
        features: prev.features.map((feature, i) => 
          i === index ? value : feature
        )
      }));
    };

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>
            {service ? 'Modifier le service' : 'Nouveau service'}
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
                  placeholder="Audit de Sécurité"
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
            </div>

            <div>
              <Label>Description *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                required
                placeholder="Description détaillée du service..."
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-4">
                <Label>Fonctionnalités incluses</Label>
                <Button type="button" onClick={addFeature} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Ajouter
                </Button>
              </div>
              
              <div className="space-y-2">
                {formData.features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Input
                      value={feature}
                      onChange={(e) => updateFeature(index, e.target.value)}
                      placeholder="Fonctionnalité incluse"
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => removeFeature(index)}
                      disabled={formData.features.length === 1}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Prix</Label>
                <Input
                  value={formData.price}
                  onChange={(e) => setFormData(prev => ({ ...prev, price: e.target.value }))}
                  placeholder="À partir de 1500€"
                />
              </div>
              <div>
                <Label>Durée</Label>
                <Input
                  value={formData.duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration: e.target.value }))}
                  placeholder="1-2 semaines"
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
        <p>Chargement des services...</p>
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
                  Gestion des services
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {services.length} service{services.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <Button onClick={() => setNewService(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Nouveau service
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

        {(newService || editingService) && (
          <ServiceForm
            service={editingService}
            onSave={handleSaveService}
            onCancel={() => {
              setNewService(false);
              setEditingService(null);
            }}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {services.map((service) => (
            <Card key={service.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center">
                    <Briefcase className="w-6 h-6 mr-3 text-primary" />
                    <div>
                      <CardTitle className="text-lg">{service.title}</CardTitle>
                      <CardDescription className="flex items-center space-x-4 mt-1">
                        <span className="flex items-center">
                          <Euro className="w-4 h-4 mr-1" />
                          {service.price}
                        </span>
                        <span className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {service.duration}
                        </span>
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingService(service)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteService(service.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {service.description}
                  </p>

                  {service.features.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Fonctionnalités incluses :</p>
                      <ul className="space-y-1">
                        {service.features.map((feature, index) => (
                          <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                            <span className="w-1 h-1 bg-primary rounded-full mr-2"></span>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {services.length === 0 && !loading && (
          <Card>
            <CardContent className="text-center py-12">
              <Briefcase className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucun service
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Commencez par créer votre premier service.
              </p>
              <Button onClick={() => setNewService(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Créer un service
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default AdminServices;