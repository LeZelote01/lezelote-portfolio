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
  MessageSquare, Star, Building, User, Check, Clock
} from 'lucide-react';

const AdminTestimonials = () => {
  const [testimonials, setTestimonials] = useState([]);
  const [pendingTestimonials, setPendingTestimonials] = useState([]);
  const [editingTestimonial, setEditingTestimonial] = useState(null);
  const [newTestimonial, setNewTestimonial] = useState(false);
  const [showPending, setShowPending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const initialTestimonialState = {
    name: '',
    role: '',
    company: '',
    content: '',
    rating: 5,
    order_index: 0,
    featured: false
  };

  useEffect(() => {
    fetchTestimonials();
    fetchPendingTestimonials();
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

  const fetchTestimonials = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des témoignages');
      }

      const data = await response.json();
      setTestimonials(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingTestimonials = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials/pending`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des témoignages en attente');
      }

      const data = await response.json();
      setPendingTestimonials(data);
    } catch (err) {
      console.error('Erreur lors du chargement des témoignages en attente:', err);
    }
  };

  const handleSaveTestimonial = async (testimonialData) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const isNewTestimonial = !testimonialData.id;
      const url = isNewTestimonial 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials`
        : `${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials/${testimonialData.id}`;

      const method = isNewTestimonial ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers,
        body: JSON.stringify({
          name: testimonialData.name,
          role: testimonialData.role,
          company: testimonialData.company,
          content: testimonialData.content,
          rating: parseInt(testimonialData.rating),
          order_index: testimonialData.order_index,
          featured: testimonialData.featured
        })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la sauvegarde');
      }

      await fetchTestimonials();
      setEditingTestimonial(null);
      setNewTestimonial(false);
      setSuccess(isNewTestimonial ? 'Témoignage créé avec succès' : 'Témoignage modifié avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteTestimonial = async (testimonialId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce témoignage ?')) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials/${testimonialId}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      await fetchTestimonials();
      setSuccess('Témoignage supprimé avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleApproveTestimonial = async (testimonialId) => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials/pending/${testimonialId}/approve`, {
        method: 'PUT',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'approbation');
      }

      await fetchTestimonials();
      await fetchPendingTestimonials();
      setSuccess('Témoignage approuvé et publié');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRejectTestimonial = async (testimonialId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir rejeter ce témoignage ?')) {
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials/pending/${testimonialId}/reject`, {
        method: 'PUT',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du rejet');
      }

      await fetchPendingTestimonials();
      setSuccess('Témoignage rejeté');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const TestimonialForm = ({ testimonial, onSave, onCancel }) => {
    const [formData, setFormData] = useState(testimonial || initialTestimonialState);

    const handleSubmit = (e) => {
      e.preventDefault();
      onSave(formData);
    };

    const renderStars = (rating) => {
      return Array.from({ length: 5 }, (_, i) => (
        <Star
          key={i}
          className={`w-5 h-5 ${i < rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
        />
      ));
    };

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>
            {testimonial ? 'Modifier le témoignage' : 'Nouveau témoignage'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Nom *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                  placeholder="Marie Dubois"
                />
              </div>
              <div>
                <Label>Poste *</Label>
                <Input
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  required
                  placeholder="CTO"
                />
              </div>
              <div>
                <Label>Entreprise *</Label>
                <Input
                  value={formData.company}
                  onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
                  required
                  placeholder="TechStart Solutions"
                />
              </div>
            </div>

            <div>
              <Label>Témoignage *</Label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                rows={4}
                required
                placeholder="Écrivez le témoignage du client..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Note (1-5 étoiles)</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="range"
                    min="1"
                    max="5"
                    value={formData.rating}
                    onChange={(e) => setFormData(prev => ({ ...prev, rating: parseInt(e.target.value) }))}
                    className="flex-1"
                  />
                  <div className="flex items-center space-x-1">
                    {renderStars(formData.rating)}
                    <span className="ml-2 text-sm font-medium">{formData.rating}/5</span>
                  </div>
                </div>
              </div>
              <div>
                <Label>Ordre d'affichage</Label>
                <Input
                  type="number"
                  value={formData.order_index}
                  onChange={(e) => setFormData(prev => ({ ...prev, order_index: parseInt(e.target.value) || 0 }))}
                  placeholder="0"
                />
              </div>
              <div className="flex items-center space-x-2 pt-6">
                <input
                  type="checkbox"
                  id="featured"
                  checked={formData.featured}
                  onChange={(e) => setFormData(prev => ({ ...prev, featured: e.target.checked }))}
                  className="rounded"
                />
                <Label htmlFor="featured">Témoignage mis en avant</Label>
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

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <p>Chargement des témoignages...</p>
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
                  Gestion des témoignages
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {testimonials.length} témoignage{testimonials.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                variant={showPending ? "default" : "outline"} 
                onClick={() => setShowPending(!showPending)}
              >
                <Clock className="w-4 h-4 mr-2" />
                Témoignages en attente ({pendingTestimonials.length})
              </Button>
              <Button onClick={() => setNewTestimonial(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Nouveau témoignage
              </Button>
            </div>
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

        {(newTestimonial || editingTestimonial) && (
          <TestimonialForm
            testimonial={editingTestimonial}
            onSave={handleSaveTestimonial}
            onCancel={() => {
              setNewTestimonial(false);
              setEditingTestimonial(null);
            }}
          />
        )}

        {/* Témoignages en attente */}
        {showPending && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                Témoignages en attente d'approbation
              </CardTitle>
              <CardDescription>
                Témoignages soumis par les visiteurs qui nécessitent votre validation
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pendingTestimonials.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  Aucun témoignage en attente
                </p>
              ) : (
                <div className="space-y-4">
                  {pendingTestimonials.map((pending) => (
                    <div key={pending.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {pending.name}
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {pending.role} {pending.company && `chez ${pending.company}`}
                          </p>
                          <p className="text-xs text-gray-500">
                            {pending.email} • Soumis le {new Date(pending.submitted_at).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                        <div className="flex items-center space-x-1">
                          {renderStars(pending.rating)}
                        </div>
                      </div>
                      
                      <blockquote className="text-sm text-gray-600 dark:text-gray-400 italic border-l-4 border-gray-300 pl-4 mb-4">
                        "{pending.content}"
                      </blockquote>
                      
                      {pending.service_used && (
                        <div className="mb-4">
                          <Badge variant="outline" className="text-xs">
                            Service utilisé: {pending.service_used}
                          </Badge>
                        </div>
                      )}
                      
                      <div className="flex space-x-2">
                        <Button 
                          size="sm" 
                          onClick={() => handleApproveTestimonial(pending.id)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Check className="w-4 h-4 mr-1" />
                          Approuver
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleRejectTestimonial(pending.id)}
                          className="text-red-600 border-red-600 hover:bg-red-50"
                        >
                          <X className="w-4 h-4 mr-1" />
                          Rejeter
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {testimonials.map((testimonial) => (
            <Card key={testimonial.id} className={testimonial.featured ? 'ring-2 ring-primary' : ''}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center">
                    <MessageSquare className="w-6 h-6 mr-3 text-primary" />
                    <div>
                      <CardTitle className="text-lg flex items-center">
                        {testimonial.name}
                        {testimonial.featured && (
                          <Badge variant="secondary" className="ml-2 text-xs">
                            En avant
                          </Badge>
                        )}
                      </CardTitle>
                      <CardDescription className="flex items-center space-x-2">
                        <User className="w-4 h-4" />
                        <span>{testimonial.role}</span>
                        <Building className="w-4 h-4 ml-2" />
                        <span>{testimonial.company}</span>
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingTestimonial(testimonial)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteTestimonial(testimonial.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-1">
                    {renderStars(testimonial.rating)}
                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                      {testimonial.rating}/5
                    </span>
                  </div>

                  <blockquote className="text-sm text-gray-600 dark:text-gray-400 italic border-l-4 border-primary pl-4">
                    "{testimonial.content}"
                  </blockquote>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {testimonials.length === 0 && !loading && (
          <Card>
            <CardContent className="text-center py-12">
              <MessageSquare className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucun témoignage
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Commencez par ajouter votre premier témoignage client.
              </p>
              <Button onClick={() => setNewTestimonial(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Ajouter un témoignage
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default AdminTestimonials;