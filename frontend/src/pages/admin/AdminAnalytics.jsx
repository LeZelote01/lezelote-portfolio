import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useTheme } from '../../context/ThemeContext';
import { 
  ArrowLeft, BarChart3, Sun, Moon, TrendingUp, TrendingDown, 
  RefreshCw, Download, Lightbulb, AlertCircle, CheckCircle,
  Users, Award, Clock, FolderOpen, FileText, Code, Star,
  Calendar, Mail, Zap, Briefcase, Activity
} from 'lucide-react';

const AdminAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  // Mapping des icônes
  const iconMap = {
    TrendingUp, TrendingDown, Users, Award, Clock, FolderOpen, 
    FileText, Code, Star, Calendar, Mail, Zap, Briefcase, 
    Activity, BarChart3, CheckCircle, Download
  };

  // Mapping des couleurs de priorité pour les recommandations
  const priorityColors = {
    high: 'border-red-200 bg-red-50 dark:bg-red-900/20',
    medium: 'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20',
    low: 'border-blue-200 bg-blue-50 dark:bg-blue-900/20'
  };

  const priorityTextColors = {
    high: 'text-red-800 dark:text-red-200',
    medium: 'text-yellow-800 dark:text-yellow-200',
    low: 'text-blue-800 dark:text-blue-200'
  };

  const priorityLabels = {
    high: 'Priorité Haute',
    medium: 'Priorité Moyenne',
    low: 'Priorité Basse'
  };

  useEffect(() => {
    fetchAnalytics();
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

  const handleAuthError = (response) => {
    if (response.status === 401) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_token_type');
      navigate('/admin/login');
      return true;
    }
    return false;
  };

  const fetchAnalytics = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/dashboard`, { 
        headers 
      });

      if (handleAuthError(response)) {
        return;
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      setAnalytics(data);
      setError('');
    } catch (err) {
      console.error('Erreur fetchAnalytics:', err);
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Erreur de connexion réseau. Vérifiez que le serveur backend est accessible.');
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAnalytics();
  };

  const handleExportReport = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/export`, { 
        headers 
      });

      if (handleAuthError(response)) {
        return;
      }

      if (!response.ok) {
        throw new Error('Erreur lors de l\'export du rapport');
      }

      const data = await response.json();
      
      // Créer et télécharger le fichier JSON
      const dataStr = JSON.stringify(data, null, 2);
      const dataBlob = new Blob([dataStr], {type: 'application/json'});
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
    } catch (err) {
      console.error('Erreur export:', err);
      setError(err.message);
    }
  };

  const getIconComponent = (iconName) => {
    return iconMap[iconName] || BarChart3;
  };

  const getTrendIcon = (trend) => {
    switch(trend) {
      case 'positive': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'negative': return <TrendingDown className="h-4 w-4 text-red-600" />;
      default: return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Calcul des analyses en cours...</p>
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
              <BarChart3 className="h-8 w-8 text-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Analyses Intelligentes
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Statistiques automatiques et recommandations IA
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
              <Button
                variant="outline"
                onClick={handleRefresh}
                disabled={refreshing}
                className="hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Actualiser
              </Button>
              <Button onClick={handleExportReport}>
                <Download className="h-4 w-4 mr-2" />
                Exporter Rapport
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

        {analytics && (
          <>
            {/* Informations de mise à jour */}
            <div className="mb-6">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Dernière mise à jour: {new Date(analytics.last_updated).toLocaleString('fr-FR')}
                      </span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {analytics.total_stats} statistiques calculées
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Statistiques automatiques */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                📊 Statistiques du Site (Calculées Automatiquement)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {analytics.statistics.map((stat, index) => {
                  const IconComponent = getIconComponent(stat.icon);
                  
                  return (
                    <Card key={index} className="hover:shadow-lg transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="p-3 rounded-lg"
                              style={{ backgroundColor: `${stat.color}20` }}
                            >
                              <IconComponent 
                                className="h-6 w-6" 
                                style={{ color: stat.color }}
                              />
                            </div>
                          </div>
                          <div className="flex items-center space-x-1">
                            {getTrendIcon(stat.trend)}
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-baseline space-x-1">
                            <span className="text-2xl font-bold text-gray-900 dark:text-white">
                              {stat.value}
                            </span>
                            {stat.suffix && (
                              <span className="text-lg font-medium text-gray-600 dark:text-gray-400">
                                {stat.suffix}
                              </span>
                            )}
                          </div>
                          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                            {stat.title}
                          </h3>
                          {stat.description && (
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              {stat.description}
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            {/* Recommandations IA */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Lightbulb className="h-6 w-6 text-yellow-500 mr-2" />
                🤖 Recommandations Intelligentes
              </h2>
              
              {analytics.recommendations.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {analytics.recommendations.map((rec, index) => (
                    <Card key={index} className={`border-l-4 ${priorityColors[rec.priority]}`}>
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                            {rec.title}
                          </CardTitle>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityTextColors[rec.priority]} bg-opacity-20`}>
                            {priorityLabels[rec.priority]}
                          </span>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {rec.description}
                        </p>
                        
                        <div className="space-y-2">
                          <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                            <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                              📋 Action recommandée:
                            </p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {rec.action}
                            </p>
                          </div>
                          
                          <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
                            <p className="text-sm font-medium text-green-800 dark:text-green-200 mb-1">
                              💡 Impact attendu:
                            </p>
                            <p className="text-sm text-green-700 dark:text-green-300">
                              {rec.impact}
                            </p>
                          </div>
                        </div>
                        
                        <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                          Catégorie: {rec.category}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className="text-center py-8">
                    <Lightbulb className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      Excellent travail !
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Aucune recommandation critique. Votre site performe bien !
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Résumé des insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Résumé des Performances
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 mb-1">
                      {analytics.statistics.filter(s => s.trend === 'positive').length}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Indicateurs Positifs
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600 mb-1">
                      {analytics.recommendations.filter(r => r.priority === 'high').length}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Actions Prioritaires
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {analytics.total_stats}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Métriques Analysées
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </main>
    </div>
  );
};

export default AdminAnalytics;