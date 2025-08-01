import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Download, FileText, Shield, Code, Network, Search, Star, Calendar, Eye, Loader } from 'lucide-react';
import jsPDF from 'jspdf';

const Resources = () => {
  const { t } = useLanguage();
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterStatus, setNewsletterStatus] = useState('');
  const [isSubscribing, setIsSubscribing] = useState(false);

  // Load resources from backend
  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      // First try to get existing resources
      let response = await fetch(`${backendUrl}/api/resources`);
      let data = await response.json();
      
      // If no resources exist, initialize them
      if (!Array.isArray(data) || data.length === 0) {
        console.log('No resources found, initializing defaults...');
        await fetch(`${backendUrl}/api/resources/init`, { method: 'POST' });
        response = await fetch(`${backendUrl}/api/resources`);
        data = await response.json();
      }
      
      if (Array.isArray(data)) {
        setResources(data);
      } else {
        console.error('Invalid resources data:', data);
        setResources([]);
      }
    } catch (error) {
      console.error('Error loading resources:', error);
      setResources([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (resource) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      // Record download
      await fetch(`${backendUrl}/api/resources/${resource.id}/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Generate actual PDF content based on resource type
      if (resource.type === 'PDF') {
        generatePDF(resource);
      } else {
        // For other types, just show a success message
        alert(`Téléchargement de "${resource.title}" commencé !`);
      }
      
      // Update local resource data to reflect new download count
      setResources(prev => prev.map(r => 
        r.id === resource.id 
          ? { ...r, downloads: r.downloads + 1 }
          : r
      ));
      
    } catch (error) {
      console.error('Error downloading resource:', error);
      alert('Erreur lors du téléchargement. Veuillez réessayer.');
    }
  };

  const generatePDF = (resource) => {
    const doc = new jsPDF();
    
    // Header
    doc.setFontSize(20);
    doc.setTextColor(40, 40, 40);
    doc.text(resource.title, 105, 20, { align: 'center' });
    
    // Author info
    doc.setFontSize(12);
    doc.setTextColor(100, 100, 100);
    doc.text('Par Jean Yves - Spécialiste Cybersécurité & Python', 105, 30, { align: 'center' });
    doc.text('contact@jeanyves.dev', 105, 40, { align: 'center' });
    
    // Content based on resource category
    doc.setFontSize(16);
    doc.setTextColor(40, 40, 40);
    doc.text('DESCRIPTION', 20, 60);
    
    doc.setFontSize(11);
    doc.setTextColor(60, 60, 60);
    const description = doc.splitTextToSize(resource.description, 170);
    doc.text(description, 20, 75);
    
    let yPos = 90 + (description.length * 5);
    
    if (resource.category === 'Guide') {
      doc.setFontSize(16);
      doc.setTextColor(40, 40, 40);
      doc.text('SOMMAIRE', 20, yPos);
      yPos += 15;
      
      const chapters = [
        '1. Introduction à la cybersécurité',
        '2. Évaluation des risques',
        '3. Mise en place des protections',
        '4. Formation des équipes',
        '5. Monitoring et surveillance',
        '6. Plan de réponse aux incidents'
      ];
      
      doc.setFontSize(11);
      chapters.forEach(chapter => {
        doc.text(chapter, 25, yPos);
        yPos += 8;
      });
      
    } else if (resource.category === 'Checklist') {
      doc.setFontSize(16);
      doc.setTextColor(40, 40, 40);
      doc.text('POINTS DE CONTRÔLE', 20, yPos);
      yPos += 15;
      
      const checkpoints = [
        '☐ Authentification multi-facteurs activée',
        '☐ Mots de passe complexes imposés',
        '☐ Mises à jour de sécurité appliquées',
        '☐ Sauvegardes régulières programmées',
        '☐ Antivirus/Anti-malware installé',
        '☐ Pare-feu configuré correctement'
      ];
      
      doc.setFontSize(11);
      checkpoints.forEach(point => {
        doc.text(point, 25, yPos);
        yPos += 10;
      });
    }
    
    // Footer
    doc.setFontSize(9);
    doc.setTextColor(120, 120, 120);
    doc.text('Document généré depuis le centre de ressources - jeanyves.dev', 20, 270);
    doc.text(`Téléchargé le ${new Date().toLocaleDateString('fr-FR')}`, 20, 280);
    
    // Save
    doc.save(`${resource.title.toLowerCase().replace(/\s+/g, '-')}.pdf`);
  };

  const handleNewsletterSubmit = async (e) => {
    e.preventDefault();
    setIsSubscribing(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/newsletter/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: newsletterEmail })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setNewsletterStatus(data.status === 'existing' ? 'already_subscribed' : 'success');
        setNewsletterEmail('');
      } else {
        setNewsletterStatus('error');
      }
    } catch (error) {
      console.error('Newsletter subscription error:', error);
      setNewsletterStatus('error');
    } finally {
      setIsSubscribing(false);
      
      // Clear status after 5 seconds
      setTimeout(() => {
        setNewsletterStatus('');
      }, 5000);
    }
  };

  const categories = [
    { id: 'all', name: 'Toutes les ressources', icon: FileText },
    { id: 'Guide', name: 'Guides', icon: Shield },
    { id: 'Checklist', name: 'Checklists', icon: Code },
    { id: 'Scripts', name: 'Scripts', icon: Network },
    { id: 'Template', name: 'Templates', icon: FileText },
    { id: 'Outils', name: 'Outils', icon: Shield }
  ];

  const filteredResources = resources.filter(resource => {
    const matchesCategory = activeCategory === 'all' || resource.category === activeCategory;
    const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const featuredResources = resources.filter(resource => resource.featured);

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Débutant': return 'bg-green-500';
      case 'Intermédiaire': return 'bg-yellow-500';
      case 'Avancé': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'PDF': return <FileText size={20} className="text-red-400" />;
      case 'ZIP': return <Download size={20} className="text-blue-400" />;
      case 'DOC': return <FileText size={20} className="text-green-400" />;
      default: return <FileText size={20} className="text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Centre de <span className="text-green-400">Ressources</span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              Téléchargez gratuitement des guides, scripts et outils pour améliorer votre sécurité
            </p>
          </div>
        </div>
      </section>

      {/* Loading State */}
      {loading ? (
        <section className="py-20 bg-gray-900">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto text-center">
              <div className="flex items-center justify-center mb-4">
                <Loader className="animate-spin text-green-400" size={48} />
              </div>
              <h3 className="text-xl font-bold text-gray-300 mb-2">Chargement des ressources</h3>
              <p className="text-gray-500">Veuillez patienter...</p>
            </div>
          </div>
        </section>
      ) : (
        <>
          {/* Search and Filters */}
          <section className="py-12 bg-gray-900">
            <div className="container mx-auto px-6">
              <div className="max-w-6xl mx-auto">
                {/* Search Bar */}
                <div className="relative mb-8">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Rechercher une ressource..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                  />
                </div>

                {/* Categories */}
                <div className="flex flex-wrap gap-4 mb-8">
                  {categories.map(category => {
                    const Icon = category.icon;
                    return (
                      <button
                        key={category.id}
                        onClick={() => setActiveCategory(category.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                          activeCategory === category.id
                            ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        <Icon size={16} />
                        {category.name}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </section>

          {/* Featured Resources */}
          {activeCategory === 'all' && (
            <section className="py-12 bg-gray-800">
              <div className="container mx-auto px-6">
                <div className="max-w-6xl mx-auto">
                  <h2 className="text-3xl font-bold text-white mb-8">
                    Ressources <span className="text-green-400">en vedette</span>
                  </h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {featuredResources.map(resource => (
                      <div key={resource.id} className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-2">
                            {getTypeIcon(resource.type)}
                            <span className="text-sm font-medium text-gray-300">{resource.type}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs bg-yellow-500 text-gray-900 px-2 py-1 rounded-full font-bold">
                              FEATURED
                            </span>
                            <span className={`text-xs text-white px-2 py-1 rounded-full font-bold ${getDifficultyColor(resource.difficulty)}`}>
                              {resource.difficulty}
                            </span>
                          </div>
                        </div>
                        
                        <h3 className="text-xl font-bold text-white mb-3 group-hover:text-green-400 transition-colors">
                          {resource.title}
                        </h3>
                        
                        <p className="text-gray-400 mb-4 leading-relaxed">
                          {resource.description}
                        </p>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                          <div className="flex items-center gap-1">
                            <Download size={14} />
                            {resource.downloads}
                          </div>
                          <div className="flex items-center gap-1">
                            <Star size={14} className="text-yellow-400" />
                            {resource.rating}
                          </div>
                          <div className="flex items-center gap-1">
                            <FileText size={14} />
                            {resource.size}
                          </div>
                        </div>
                        
                        <div className="flex flex-wrap gap-2 mb-4">
                          {resource.tags.slice(0, 3).map(tag => (
                            <span key={tag} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        <button 
                          onClick={() => handleDownload(resource)}
                          className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-4 py-2 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 flex items-center justify-center gap-2"
                        >
                          <Download size={16} />
                          Télécharger gratuitement
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* All Resources */}
          <section className="py-20 bg-gray-900">
            <div className="container mx-auto px-6">
              <div className="max-w-6xl mx-auto">
                <h2 className="text-3xl font-bold text-white mb-8">
                  {activeCategory === 'all' ? 'Toutes les ressources' : `Ressources - ${activeCategory}`}
                </h2>
                
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {filteredResources.map(resource => (
                    <div key={resource.id} className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          {getTypeIcon(resource.type)}
                          <span className="text-sm font-medium text-gray-300">{resource.type}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {resource.featured && (
                            <span className="text-xs bg-yellow-500 text-gray-900 px-2 py-1 rounded-full font-bold">
                              FEATURED
                            </span>
                          )}
                          <span className={`text-xs text-white px-2 py-1 rounded-full font-bold ${getDifficultyColor(resource.difficulty)}`}>
                            {resource.difficulty}
                          </span>
                        </div>
                      </div>
                      
                      <h3 className="text-xl font-bold text-white mb-3 group-hover:text-green-400 transition-colors">
                        {resource.title}
                      </h3>
                      
                      <p className="text-gray-400 mb-4 leading-relaxed">
                        {resource.description}
                      </p>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                        <div className="flex items-center gap-1">
                          <Download size={14} />
                          {resource.downloads}
                        </div>
                        <div className="flex items-center gap-1">
                          <Star size={14} className="text-yellow-400" />
                          {resource.rating}
                        </div>
                        <div className="flex items-center gap-1">
                          <FileText size={14} />
                          {resource.size}
                        </div>
                        {resource.pages && (
                          <div className="flex items-center gap-1">
                            <Eye size={14} />
                            {resource.pages}p
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        {resource.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                            {tag}
                          </span>
                        ))}
                      </div>
                      
                      <button 
                        onClick={() => handleDownload(resource)}
                        className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-4 py-2 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 flex items-center justify-center gap-2"
                      >
                        <Download size={16} />
                        Télécharger gratuitement
                      </button>
                    </div>
                  ))}
                </div>

                {/* Empty State */}
                {filteredResources.length === 0 && (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Search size={32} className="text-gray-500" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-300 mb-2">Aucune ressource trouvée</h3>
                    <p className="text-gray-500">Essayez de modifier votre recherche ou vos filtres</p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Newsletter Signup */}
          <section className="py-20 bg-gray-800">
            <div className="container mx-auto px-6">
              <div className="max-w-4xl mx-auto text-center">
                <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h3 className="text-3xl font-bold text-white mb-4">
                    Restez informé des nouvelles ressources
                  </h3>
                  <p className="text-gray-300 mb-6 leading-relaxed">
                    Recevez un email dès qu'une nouvelle ressource est disponible au téléchargement.
                  </p>
                  
                  {newsletterStatus && (
                    <div className={`mb-6 p-4 rounded-lg ${
                      newsletterStatus === 'success' ? 'bg-green-600/20 border border-green-500' :
                      newsletterStatus === 'already_subscribed' ? 'bg-yellow-600/20 border border-yellow-500' :
                      'bg-red-600/20 border border-red-500'
                    }`}>
                      <p className={`${
                        newsletterStatus === 'success' ? 'text-green-200' :
                        newsletterStatus === 'already_subscribed' ? 'text-yellow-200' :
                        'text-red-200'
                      }`}>
                        {newsletterStatus === 'success' && 'Merci ! Vous êtes maintenant abonné à notre newsletter.'}
                        {newsletterStatus === 'already_subscribed' && 'Cet email est déjà abonné à notre newsletter.'}
                        {newsletterStatus === 'error' && 'Erreur lors de l\'inscription. Veuillez réessayer.'}
                      </p>
                    </div>
                  )}
                  
                  <form onSubmit={handleNewsletterSubmit} className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
                    <input
                      type="email"
                      placeholder="Votre email"
                      value={newsletterEmail}
                      onChange={(e) => setNewsletterEmail(e.target.value)}
                      required
                      className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                    />
                    <button 
                      type="submit"
                      disabled={isSubscribing}
                      className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {isSubscribing ? (
                        <>
                          <Loader className="animate-spin" size={16} />
                          Inscription...
                        </>
                      ) : (
                        'S\'abonner'
                      )}
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
};

export default Resources;