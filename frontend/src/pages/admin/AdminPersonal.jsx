import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { ArrowLeft, Save, User, Image, Plus, X } from 'lucide-react';

const AdminPersonal = () => {
  const [personalInfo, setPersonalInfo] = useState({
    name: '',
    title: '',
    subtitle: '',
    bio: '',
    email: '',
    phone: '',
    location: '',
    availability: '',
    website: '',
    age: '',
    birth_date: '',
    profile_image_url: '',
    years_experience: '',
    certifications: [],
    languages: [],
    education: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newCertification, setNewCertification] = useState('');
  const [newLanguage, setNewLanguage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPersonalInfo();
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

  const fetchPersonalInfo = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/personal`, {
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setPersonalInfo({
          ...data,
          age: data.age || '',
          birth_date: data.birth_date || '',
          profile_image_url: data.profile_image_url || '',
          years_experience: data.years_experience || '',
          certifications: data.certifications || [],
          languages: data.languages || [],
          education: data.education || ''
        });
      } else if (response.status === 404) {
        // Pas encore d'informations personnelles créées
        console.log('Aucune information personnelle trouvée');
      } else {
        throw new Error('Erreur lors du chargement');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const hasId = personalInfo.id;
      const url = `${process.env.REACT_APP_BACKEND_URL}/api/admin/personal`;
      const method = hasId ? 'PUT' : 'POST';

      const dataToSend = {
        name: personalInfo.name,
        title: personalInfo.title,
        subtitle: personalInfo.subtitle,
        bio: personalInfo.bio,
        email: personalInfo.email,
        phone: personalInfo.phone || null,
        location: personalInfo.location || null,
        availability: personalInfo.availability || null,
        website: personalInfo.website || null,
        age: personalInfo.age ? parseInt(personalInfo.age) : null,
        birth_date: personalInfo.birth_date || null,
        profile_image_url: personalInfo.profile_image_url || null,
        years_experience: personalInfo.years_experience ? parseInt(personalInfo.years_experience) : null,
        certifications: personalInfo.certifications,
        languages: personalInfo.languages,
        education: personalInfo.education || null
      };

      const response = await fetch(url, {
        method,
        headers,
        body: JSON.stringify(dataToSend)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la sauvegarde');
      }

      const updatedData = await response.json();
      setPersonalInfo({
        ...updatedData,
        age: updatedData.age || '',
        birth_date: updatedData.birth_date || '',
        profile_image_url: updatedData.profile_image_url || '',
        years_experience: updatedData.years_experience || '',
        certifications: updatedData.certifications || [],
        languages: updatedData.languages || [],
        education: updatedData.education || ''
      });
      setSuccess('Informations personnelles sauvegardées avec succès');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPersonalInfo(prev => ({ ...prev, [name]: value }));
  };

  const addCertification = () => {
    if (newCertification.trim()) {
      setPersonalInfo(prev => ({
        ...prev,
        certifications: [...prev.certifications, newCertification.trim()]
      }));
      setNewCertification('');
    }
  };

  const removeCertification = (index) => {
    setPersonalInfo(prev => ({
      ...prev,
      certifications: prev.certifications.filter((_, i) => i !== index)
    }));
  };

  const addLanguage = () => {
    if (newLanguage.trim()) {
      setPersonalInfo(prev => ({
        ...prev,
        languages: [...prev.languages, newLanguage.trim()]
      }));
      setNewLanguage('');
    }
  };

  const removeLanguage = (index) => {
    setPersonalInfo(prev => ({
      ...prev,
      languages: prev.languages.filter((_, i) => i !== index)
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <p>Chargement des informations personnelles...</p>
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
                  Informations personnelles
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Gérer votre profil et vos coordonnées
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <Alert variant="destructive" className="mb-6 border-red-200 bg-red-50 dark:bg-red-900/20">
            <AlertDescription className="text-red-800 dark:text-red-200">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50 dark:bg-green-900/20">
            <AlertDescription className="text-green-800 dark:text-green-200">{success}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Informations de base */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="w-5 h-5 mr-2" />
                Profil professionnel
              </CardTitle>
              <CardDescription>
                Ces informations apparaîtront sur votre portfolio public
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="name">Nom complet *</Label>
                  <Input
                    id="name"
                    name="name"
                    value={personalInfo.name}
                    onChange={handleChange}
                    required
                    placeholder="Jean Yves"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={personalInfo.email}
                    onChange={handleChange}
                    required
                    placeholder="contact@example.com"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="title">Titre professionnel *</Label>
                <Input
                  id="title"
                  name="title"
                  value={personalInfo.title}
                  onChange={handleChange}
                  required
                  placeholder="Spécialiste Cybersécurité & Développeur Python"
                />
              </div>

              <div>
                <Label htmlFor="subtitle">Sous-titre</Label>
                <Input
                  id="subtitle"
                  name="subtitle"
                  value={personalInfo.subtitle}
                  onChange={handleChange}
                  placeholder="Expert en sécurité numérique et développement d'applications Python"
                />
              </div>

              <div>
                <Label htmlFor="bio">Biographie *</Label>
                <Textarea
                  id="bio"
                  name="bio"
                  value={personalInfo.bio}
                  onChange={handleChange}
                  rows={5}
                  required
                  placeholder="Présentez-vous professionnellement..."
                />
              </div>
            </CardContent>
          </Card>

          {/* Informations personnelles */}
          <Card>
            <CardHeader>
              <CardTitle>Informations personnelles</CardTitle>
              <CardDescription>
                Détails personnels et professionnels
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="age">Âge</Label>
                  <Input
                    id="age"
                    name="age"
                    type="number"
                    value={personalInfo.age}
                    onChange={handleChange}
                    placeholder="28"
                  />
                </div>
                <div>
                  <Label htmlFor="birth_date">Date de naissance</Label>
                  <Input
                    id="birth_date"
                    name="birth_date"
                    type="date"
                    value={personalInfo.birth_date}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <Label htmlFor="years_experience">Années d'expérience</Label>
                  <Input
                    id="years_experience"
                    name="years_experience"
                    type="number"
                    value={personalInfo.years_experience}
                    onChange={handleChange}
                    placeholder="5"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="education">Formation</Label>
                <Input
                  id="education"
                  name="education"
                  value={personalInfo.education}
                  onChange={handleChange}
                  placeholder="Master 2 en Cybersécurité - École Supérieure d'Informatique Paris"
                />
              </div>
            </CardContent>
          </Card>

          {/* Photo de profil */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Image className="w-5 h-5 mr-2" />
                Photo de profil
              </CardTitle>
              <CardDescription>
                URL de votre photo de profil (recommandé : 400x400px)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="profile_image_url">URL de l'image</Label>
                <Input
                  id="profile_image_url"
                  name="profile_image_url"
                  type="url"
                  value={personalInfo.profile_image_url}
                  onChange={handleChange}
                  placeholder="/images/profile/default-profile.svg"
                />
              </div>
              {personalInfo.profile_image_url && (
                <div className="flex justify-center">
                  <img
                    src={personalInfo.profile_image_url}
                    alt="Aperçu"
                    className="w-32 h-32 rounded-full object-cover border-2 border-gray-300"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Contact */}
          <Card>
            <CardHeader>
              <CardTitle>Coordonnées</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="phone">Téléphone</Label>
                  <Input
                    id="phone"
                    name="phone"
                    value={personalInfo.phone}
                    onChange={handleChange}
                    placeholder="+33 6 12 34 56 78"
                  />
                </div>
                <div>
                  <Label htmlFor="location">Localisation</Label>
                  <Input
                    id="location"
                    name="location"
                    value={personalInfo.location}
                    onChange={handleChange}
                    placeholder="Paris, France"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="availability">Disponibilité</Label>
                  <Input
                    id="availability"
                    name="availability"
                    value={personalInfo.availability}
                    onChange={handleChange}
                    placeholder="Disponible pour missions freelance"
                  />
                </div>
                <div>
                  <Label htmlFor="website">Site web</Label>
                  <Input
                    id="website"
                    name="website"
                    type="url"
                    value={personalInfo.website}
                    onChange={handleChange}
                    placeholder="https://votre-site.com"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Certifications */}
          <Card>
            <CardHeader>
              <CardTitle>Certifications</CardTitle>
              <CardDescription>
                Ajoutez vos certifications professionnelles
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newCertification}
                  onChange={(e) => setNewCertification(e.target.value)}
                  placeholder="CISSP - Certified Information Systems Security Professional"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCertification())}
                />
                <Button type="button" onClick={addCertification}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-2">
                {personalInfo.certifications.map((cert, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded">
                    <span className="text-sm">{cert}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeCertification(index)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Langues */}
          <Card>
            <CardHeader>
              <CardTitle>Langues</CardTitle>
              <CardDescription>
                Ajoutez les langues que vous parlez
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newLanguage}
                  onChange={(e) => setNewLanguage(e.target.value)}
                  placeholder="Français (natif)"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLanguage())}
                />
                <Button type="button" onClick={addLanguage}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-2">
                {personalInfo.languages.map((lang, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded">
                    <span className="text-sm">{lang}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLanguage(index)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button type="submit" disabled={saving}>
              <Save className="w-4 h-4 mr-2" />
              {saving ? 'Sauvegarde...' : 'Sauvegarder'}
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default AdminPersonal;