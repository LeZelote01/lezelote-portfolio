import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useTheme } from '../../context/ThemeContext';
import { 
  Users, Code, Shield, Clock, LogOut, User, 
  FolderOpen, Briefcase, MessageSquare, Settings,
  BarChart3, Activity, TrendingUp, Sun, Moon, FileText, BookOpen
} from 'lucide-react';

const AdminDashboard = () => {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    projects: 0,
    skills: 0,
    services: 0,
    testimonials: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  useEffect(() => {
    fetchUserData();
    fetchStats();
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

  const fetchUserData = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/me`, {
        headers
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/admin/login');
          return;
        }
        throw new Error('Erreur lors de la récupération des données utilisateur');
      }

      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchStats = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const [projectsRes, skillsRes, servicesRes, testimonialsRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/projects`, { headers }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/skills`, { headers }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/services`, { headers }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/testimonials`, { headers })
      ]);

      const [projects, skills, services, testimonials] = await Promise.all([
        projectsRes.json(),
        skillsRes.json(),
        servicesRes.json(),
        testimonialsRes.json()
      ]);

      setStats({
        projects: projects.length || 0,
        skills: skills.length || 0,
        services: services.length || 0,
        testimonials: testimonials.length || 0
      });
    } catch (err) {
      console.error('Erreur lors du chargement des statistiques:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_token_type');
    navigate('/admin/login');
  };

  const quickActions = [
    {
      title: 'Informations personnelles',
      description: 'Modifier le profil et les coordonnées',
      icon: User,
      path: '/admin/personal',
      color: 'bg-blue-500'
    },
    {
      title: 'Gérer les projets',
      description: 'Ajouter, modifier ou supprimer des projets',
      icon: FolderOpen,
      path: '/admin/projects',
      color: 'bg-green-500'
    },
    {
      title: 'Gérer les compétences',
      description: 'Organiser les compétences par catégories',
      icon: Code,
      path: '/admin/skills',
      color: 'bg-purple-500'
    },
    {
      title: 'Gérer les services',
      description: 'Configurer les offres de services',
      icon: Briefcase,
      path: '/admin/services',
      color: 'bg-orange-500'
    },
    {
      title: 'Gérer les témoignages',
      description: 'Modérer et organiser les témoignages',
      icon: MessageSquare,
      path: '/admin/testimonials',
      color: 'bg-pink-500'
    },
    {
      title: 'Technologies',
      description: 'Gérer les technologies et outils',
      icon: Code,
      path: '/admin/technologies',
      color: 'bg-indigo-500'
    },
    {
      title: 'Statistiques',
      description: 'Gérer les statistiques du portfolio',
      icon: BarChart3,
      path: '/admin/statistics',
      color: 'bg-cyan-500'
    },
    {
      title: 'Liens sociaux',
      description: 'Gérer les réseaux sociaux',
      icon: Users,
      path: '/admin/social-links',
      color: 'bg-teal-500'
    },
    {
      title: 'Étapes de processus',
      description: 'Gérer le processus de travail',
      icon: Activity,
      path: '/admin/process-steps',
      color: 'bg-emerald-500'
    },
    {
      title: 'Ressources',
      description: 'Gérer les ressources téléchargeables',
      icon: FileText,
      path: '/admin/resources',
      color: 'bg-blue-600'
    },
    {
      title: 'Blog Technique',
      description: 'Gérer les articles du blog',
      icon: BookOpen,
      path: '/admin/blog',
      color: 'bg-purple-600'
    },
    {
      title: 'Messages de Contact',
      description: 'Consulter et gérer les messages reçus',
      icon: MessageSquare,
      path: '/admin/contacts',
      color: 'bg-red-500'
    },
    {
      title: 'Paramètres',
      description: 'Gestion du compte administrateur et préférences',
      icon: Settings,
      path: '/admin/settings',
      color: 'bg-gray-500'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Activity className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p>Chargement du dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg dark:bg-gray-800/80 shadow-lg border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                  Administration
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Panneau de gestion du portfolio
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Theme Toggle */}
              <Button
                variant="outline"
                onClick={toggleTheme}
                className="hover:bg-gray-100 dark:hover:bg-gray-700"
                title={isDark ? "Mode clair" : "Mode sombre"}
              >
                {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
              
              {user && (
                <div className="text-right px-4 py-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.username}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {user.email}
                  </p>
                </div>
              )}
              <Button variant="outline" onClick={handleLogout} className="hover:bg-red-50 hover:border-red-300 hover:text-red-600 transition-colors">
                <LogOut className="h-4 w-4 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        {error && (
          <Alert variant="destructive" className="mb-6 border-red-200 bg-red-50 dark:bg-red-900/20">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80 border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <CardContent className="flex items-center p-6">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <FolderOpen className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Projets
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.projects}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80 border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <CardContent className="flex items-center p-6">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Code className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Compétences
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.skills}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80 border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <CardContent className="flex items-center p-6">
              <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <Briefcase className="h-8 w-8 text-orange-600 dark:text-orange-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Services
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.services}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80 border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <CardContent className="flex items-center p-6">
              <div className="p-3 bg-pink-100 dark:bg-pink-900/30 rounded-lg">
                <MessageSquare className="h-8 w-8 text-pink-600 dark:text-pink-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Témoignages
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.testimonials}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Actions rapides */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-500" />
            Actions rapides
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <Card 
                key={index} 
                className="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80 border-0 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer hover:-translate-y-1 group"
                onClick={() => navigate(action.path)}
              >
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className={`p-3 rounded-xl ${action.color} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <action.icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="ml-4 text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {action.title}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Activité récente */}
        <Card className="bg-white/80 backdrop-blur-sm dark:bg-gray-800/80 border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center text-gray-900 dark:text-white">
              <BarChart3 className="h-5 w-5 mr-2 text-blue-500" />
              Activité récente
            </CardTitle>
            <CardDescription>
              Dernières modifications apportées au portfolio
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Données migrées vers MongoDB</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Il y a quelques minutes
                  </p>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">Système</Badge>
              </div>
              <div className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Dashboard admin amélioré</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Il y a quelques minutes
                  </p>
                </div>
                <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">Développement</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default AdminDashboard;