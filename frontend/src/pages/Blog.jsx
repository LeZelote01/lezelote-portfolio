import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Search, Calendar, User, Tag, ArrowRight, Clock, Loader } from 'lucide-react';

const Blog = () => {
  const { t } = useLanguage();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [blogPosts, setBlogPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterStatus, setNewsletterStatus] = useState('');
  const [isSubscribing, setIsSubscribing] = useState(false);

  useEffect(() => {
    fetchBlogPosts();
  }, []);

  const fetchBlogPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/blog`);
      
      if (!response.ok) {
        console.warn('No blog posts available from API, using default empty array');
        setBlogPosts([]);
        return;
      }
      
      const data = await response.json();
      
      if (Array.isArray(data)) {
        // Filter only published posts for public display
        const publishedPosts = data.filter(post => post.published);
        setBlogPosts(publishedPosts);
      } else {
        console.warn('Invalid blog data received');
        setBlogPosts([]);
      }
    } catch (err) {
      console.warn('Error fetching blog posts:', err.message);
      setBlogPosts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewsletterSubmit = async (e) => {
    e.preventDefault();
    setIsSubscribing(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/newsletter/subscribe`, {
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

  // Get unique categories from blog posts
  const categories = [
    { id: 'all', name: 'Toutes les catégories', count: blogPosts.length },
    ...Array.from(new Set(blogPosts.map(p => p.category))).map(category => ({
      id: category,
      name: category,
      count: blogPosts.filter(p => p.category === category).length
    }))
  ];

  const filteredPosts = blogPosts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || post.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const featuredPosts = blogPosts.filter(post => post.featured);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {t('technicalBlog')}
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              {t('blogSubtitle')}
            </p>
          </div>
        </div>
      </section>

      {loading ? (
        <section className="py-20 bg-gray-900">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto text-center">
              <div className="flex items-center justify-center mb-4">
                <Loader className="animate-spin text-green-400" size={48} />
              </div>
              <h3 className="text-xl font-bold text-gray-300 mb-2">Chargement des articles</h3>
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
                    placeholder="Rechercher un article..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                  />
                </div>

                {/* Categories */}
                <div className="flex flex-wrap gap-4 mb-8">
                  {categories.map(category => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                        selectedCategory === category.id
                          ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      {category.name} ({category.count})
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Featured Posts */}
          {selectedCategory === 'all' && featuredPosts.length > 0 && (
            <section className="py-12 bg-gray-800">
              <div className="container mx-auto px-6">
                <div className="max-w-6xl mx-auto">
                  <h2 className="text-3xl font-bold text-white mb-8">
                    Articles <span className="text-green-400">en vedette</span>
                  </h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {featuredPosts.map(post => (
                      <div key={post.id} className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
                        <div className="flex items-center justify-between mb-4">
                          <span className="px-3 py-1 bg-green-400/20 text-green-400 rounded-full text-sm font-medium">
                            {post.category}
                          </span>
                          <span className="text-xs bg-yellow-500 text-gray-900 px-2 py-1 rounded-full font-bold">
                            FEATURED
                          </span>
                        </div>
                        
                        <h3 className="text-xl font-bold text-white mb-3 group-hover:text-green-400 transition-colors">
                          {post.title}
                        </h3>
                        
                        <p className="text-gray-400 mb-4 leading-relaxed">
                          {post.excerpt}
                        </p>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                          <div className="flex items-center gap-1">
                            <Calendar size={14} />
                            {formatDate(post.created_at)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock size={14} />
                            {post.reading_time} min
                          </div>
                        </div>
                        
                        {post.tags && post.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-4">
                            {post.tags.slice(0, 3).map((tag, tagIndex) => (
                              <span key={tagIndex} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        <button className="text-green-400 hover:text-green-300 transition-colors flex items-center gap-1 text-sm font-medium">
                          Lire l'article <ArrowRight size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* All Posts */}
          <section className="py-20 bg-gray-900">
            <div className="container mx-auto px-6">
              <div className="max-w-6xl mx-auto">
                <h2 className="text-3xl font-bold text-white mb-8">
                  {selectedCategory === 'all' ? 'Tous les articles' : `Articles - ${selectedCategory}`}
                </h2>
                
                {filteredPosts.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Search size={32} className="text-gray-500" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-300 mb-2">
                      {blogPosts.length === 0 ? 'Aucun article publié' : 'Aucun article trouvé'}
                    </h3>
                    <p className="text-gray-500">
                      {blogPosts.length === 0 ? 
                        'Les articles du blog technique seront bientôt disponibles.' :
                        'Essayez de modifier votre recherche ou vos filtres'
                      }
                    </p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {filteredPosts.map(post => (
                      <article key={post.id} className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
                        <div className="flex items-center justify-between mb-4">
                          <span className="px-3 py-1 bg-green-400/20 text-green-400 rounded-full text-sm font-medium">
                            {post.category}
                          </span>
                          {post.featured && (
                            <span className="text-xs bg-yellow-500 text-gray-900 px-2 py-1 rounded-full font-bold">
                              FEATURED
                            </span>
                          )}
                        </div>
                        
                        <h3 className="text-xl font-bold text-white mb-3 group-hover:text-green-400 transition-colors">
                          {post.title}
                        </h3>
                        
                        <p className="text-gray-400 mb-4 leading-relaxed">
                          {post.excerpt}
                        </p>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                          <div className="flex items-center gap-1">
                            <User size={14} />
                            Jean Yves
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar size={14} />
                            {formatDate(post.created_at)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock size={14} />
                            {post.reading_time} min
                          </div>
                        </div>
                        
                        {post.tags && post.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-4">
                            {post.tags.map((tag, tagIndex) => (
                              <span key={tagIndex} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        <button className="text-green-400 hover:text-green-300 transition-colors flex items-center gap-1 text-sm font-medium">
                          Lire l'article <ArrowRight size={14} />
                        </button>
                      </article>
                    ))}
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
                    Restez informé des dernières actualités
                  </h3>
                  <p className="text-gray-300 mb-6 leading-relaxed">
                    Recevez mes derniers articles et conseils en cybersécurité directement dans votre boîte mail.
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

export default Blog;