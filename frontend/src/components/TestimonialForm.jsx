import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { MessageSquare, Star, CheckCircle, AlertCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const TestimonialForm = () => {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    role: '',
    content: '',
    rating: 5,
    service_used: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const services = [
    'Audit de sécurité',
    'Développement Python',
    'Formation cybersécurité',
    'Conseil en sécurité IT',
    'Audit de code',
    'Autre'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/testimonials/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de l\'envoi du témoignage');
      }

      setSuccess('Merci pour votre témoignage ! Il sera examiné avant publication.');
      setFormData({
        name: '',
        email: '',
        company: '',
        role: '',
        content: '',
        rating: 5,
        service_used: ''
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStars = () => {
    return Array.from({ length: 5 }, (_, index) => (
      <Star
        key={index}
        className={`h-6 w-6 cursor-pointer transition-colors ${
          index < formData.rating
            ? 'text-yellow-400 fill-current'
            : 'text-gray-300 dark:text-gray-600'
        }`}
        onClick={() => setFormData(prev => ({ ...prev, rating: index + 1 }))}
      />
    ));
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
            <MessageSquare className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <CardTitle className="text-2xl">{t('testimonialFormTitle')}</CardTitle>
        <CardDescription>
          {t('testimonialFormDesc')}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50 dark:bg-green-900/20">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800 dark:text-green-200">
              {success}
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">{t('fullName')} *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Votre nom"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">{t('email')} *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="votre@email.com"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="company">{t('company')}</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
                placeholder="Nom de votre entreprise"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">{t('role')}</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                placeholder="Votre poste"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="service_used">{t('serviceUsed')}</Label>
            <select
              id="service_used"
              value={formData.service_used}
              onChange={(e) => setFormData(prev => ({ ...prev, service_used: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">{t('selectService')}...</option>
              {services.map(service => (
                <option key={service} value={service}>{service}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label>{t('rating')} *</Label>
            <div className="flex space-x-1">
              {renderStars()}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('ratingHelper')}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="content">{t('yourTestimonial')} *</Label>
            <textarea
              id="content"
              value={formData.content}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              rows="5"
              placeholder={t('testimonialPlaceholder')}
              required
            />
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              <strong>Note :</strong> {t('testimonialNote')}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              {t('testimonialConsent')}
            </p>
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={isSubmitting}
          >
            {isSubmitting ? t('sendingTestimonial') : t('sendTestimonial')}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default TestimonialForm;