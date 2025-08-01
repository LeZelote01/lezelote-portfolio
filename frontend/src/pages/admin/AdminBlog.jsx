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
  ArrowLeft, Plus, Edit2, Trash2, Save, X, BookOpen,
  Sun, Moon, CheckCircle, AlertCircle, Star, Eye
} from 'lucide-react';

const AdminBlog = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newPost, setNewPost] = useState({ 
    title: '', 
    slug: '',
    excerpt: '',
    content: '', 
    category: 'Cybersécurité', 
    tags: [],
    featured_image: '',
    published: false,
    featured: false,
    reading_time: 5
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const categories = ['Cybersécurité', 'Python', 'Tutoriel', 'Actualités', 'Outils', 'Conseils'];

  useEffect(() => {
    fetchPosts();
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

  const fetchPosts = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/blog`, { 
        headers 
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des articles');
      }

      const data = await response.json();
      setPosts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateSlug = (title) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      // Auto-generate slug if not provided
      const postData = {
        ...newPost,
        slug: newPost.slug || generateSlug(newPost.title)
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/blog`, {
        method: 'POST',
        headers,
        body: JSON.stringify(postData)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout de l\'article');
      }

      setSuccess('Article ajouté avec succès');
      setNewPost({ 
        title: '', 
        slug: '',
        excerpt: '',
        content: '', 
        category: 'Cybersécurité', 
        tags: [],
        featured_image: '',
        published: false,
        featured: false,
        reading_time: 5
      });
      setShowAddForm(false);
      fetchPosts();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdate = async (id, updatedPost) => {
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/blog/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(updatedPost)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour');
      }

      setSuccess('Article mis à jour avec succès');
      setEditingId(null);
      fetchPosts();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/blog/${id}`, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      setSuccess('Article supprimé avec succès');
      fetchPosts();
    } catch (err) {
      setError(err.message);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Cybersécurité': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      'Python': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      'Tutoriel': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'Actualités': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      'Outils': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      'Conseils': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300'
    };
    return colors[category] || colors.Cybersécurité;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <BookOpen className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Chargement des articles...</p>
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
              <BookOpen className="h-8 w-8 text-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Blog Technique
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Gérer les articles du blog
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
                Nouvel article
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
              <CardTitle>Nouvel article</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdd} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Titre</Label>
                    <Input
                      id="title"
                      value={newPost.title}
                      onChange={(e) => {
                        setNewPost(prev => ({ 
                          ...prev, 
                          title: e.target.value,
                          slug: generateSlug(e.target.value)
                        }));
                      }}
                      required
                      placeholder="Titre de l'article..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="slug">Slug (URL)</Label>
                    <Input
                      id="slug"
                      value={newPost.slug}
                      onChange={(e) => setNewPost(prev => ({ ...prev, slug: e.target.value }))}
                      required
                      placeholder="url-de-l-article"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Catégorie</Label>
                    <select
                      id="category"
                      value={newPost.category}
                      onChange={(e) => setNewPost(prev => ({ ...prev, category: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      required
                    >
                      {categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reading_time">Temps de lecture (min)</Label>
                    <Input
                      id="reading_time"
                      type="number"
                      value={newPost.reading_time}
                      onChange={(e) => setNewPost(prev => ({ ...prev, reading_time: parseInt(e.target.value) }))}
                      min="1"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="excerpt">Résumé</Label>
                  <textarea
                    id="excerpt"
                    value={newPost.excerpt}
                    onChange={(e) => setNewPost(prev => ({ ...prev, excerpt: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    rows="2"
                    required
                    placeholder="Résumé de l'article..."
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="content">Contenu</Label>
                  <textarea
                    id="content"
                    value={newPost.content}
                    onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    rows="10"
                    required
                    placeholder="Contenu de l'article en Markdown..."
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="featured_image">Image à la une (URL)</Label>
                  <Input
                    id="featured_image"
                    value={newPost.featured_image}
                    onChange={(e) => setNewPost(prev => ({ ...prev, featured_image: e.target.value }))}
                    placeholder="https://..."
                  />
                </div>

                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="published"
                      checked={newPost.published}
                      onChange={(e) => setNewPost(prev => ({ ...prev, published: e.target.checked }))}
                      className="mr-2"
                    />
                    <Label htmlFor="published">Publié</Label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="featured"
                      checked={newPost.featured}
                      onChange={(e) => setNewPost(prev => ({ ...prev, featured: e.target.checked }))}
                      className="mr-2"
                    />
                    <Label htmlFor="featured">Article mis en avant</Label>
                  </div>
                </div>

                <div className="flex items-end space-x-2">
                  <Button type="submit">
                    <Save className="h-4 w-4 mr-2" />
                    Publier
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

        {/* Liste des articles */}
        <div className="grid grid-cols-1 gap-6">
          {posts.map((post) => (
            <Card key={post.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                {editingId === post.id ? (
                  <EditPostForm
                    post={post}
                    categories={categories}
                    onSave={(updatedPost) => handleUpdate(post.id, updatedPost)}
                    onCancel={() => setEditingId(null)}
                  />
                ) : (
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge className={getCategoryColor(post.category)}>
                          {post.category}
                        </Badge>
                        {post.published ? (
                          <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                            Publié
                          </Badge>
                        ) : (
                          <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300">
                            Brouillon
                          </Badge>
                        )}
                        {post.featured && (
                          <Star className="h-4 w-4 text-yellow-500" />
                        )}
                      </div>
                      
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        {post.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        {post.excerpt}
                      </p>
                      
                      <div className="flex items-center text-sm text-gray-500 space-x-4">
                        <span>{formatDate(post.created_at)}</span>
                        <span>{post.reading_time} min de lecture</span>
                        <div className="flex items-center">
                          <Eye className="h-4 w-4 mr-1" />
                          {post.views || 0}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingId(post.id)}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(post.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {posts.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Aucun article
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Commencez par rédiger votre premier article.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nouvel article
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

const EditPostForm = ({ post, categories, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    title: post.title,
    slug: post.slug,
    excerpt: post.excerpt,
    content: post.content,
    category: post.category,
    tags: post.tags || [],
    featured_image: post.featured_image || '',
    published: post.published,
    featured: post.featured,
    reading_time: post.reading_time
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const generateSlug = (title) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="edit-title">Titre</Label>
          <Input
            id="edit-title"
            value={formData.title}
            onChange={(e) => {
              const newTitle = e.target.value;
              setFormData(prev => ({ 
                ...prev, 
                title: newTitle,
                slug: generateSlug(newTitle)
              }));
            }}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="edit-slug">Slug (URL)</Label>
          <Input
            id="edit-slug"
            value={formData.slug}
            onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          <Label htmlFor="edit-reading_time">Temps de lecture (min)</Label>
          <Input
            id="edit-reading_time"
            type="number"
            value={formData.reading_time}
            onChange={(e) => setFormData(prev => ({ ...prev, reading_time: parseInt(e.target.value) }))}
            min="1"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-excerpt">Résumé</Label>
        <textarea
          id="edit-excerpt"
          value={formData.excerpt}
          onChange={(e) => setFormData(prev => ({ ...prev, excerpt: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          rows="2"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-content">Contenu</Label>
        <textarea
          id="edit-content"
          value={formData.content}
          onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          rows="8"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-featured_image">Image à la une (URL)</Label>
        <Input
          id="edit-featured_image"
          value={formData.featured_image}
          onChange={(e) => setFormData(prev => ({ ...prev, featured_image: e.target.value }))}
          placeholder="https://..."
        />
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="edit-published"
            checked={formData.published}
            onChange={(e) => setFormData(prev => ({ ...prev, published: e.target.checked }))}
            className="mr-2"
          />
          <Label htmlFor="edit-published">Publié</Label>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="edit-featured"
            checked={formData.featured}
            onChange={(e) => setFormData(prev => ({ ...prev, featured: e.target.checked }))}
            className="mr-2"
          />
          <Label htmlFor="edit-featured">Article mis en avant</Label>
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

export default AdminBlog;