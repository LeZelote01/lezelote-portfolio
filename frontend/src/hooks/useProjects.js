import { useState, useEffect } from 'react';

const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/projects`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des projets');
        }
        
        const data = await response.json();
        // Trier par order_index puis par date de création
        const sortedProjects = data.sort((a, b) => {
          if (a.order_index !== b.order_index) {
            return (a.order_index || 0) - (b.order_index || 0);
          }
          return new Date(b.created_at) - new Date(a.created_at);
        });
        
        setProjects(sortedProjects);
        setError(null);
      } catch (err) {
        setError(err.message);
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  // Fonctions utilitaires pour filtrer les projets
  const getProjectsByLevel = (level) => {
    return projects.filter(project => project.level === level);
  };

  const getProjectsByCategory = (category) => {
    return projects.filter(project => project.category === category);
  };

  const getProjectsByStatus = (status) => {
    return projects.filter(project => project.status === status);
  };

  return { 
    projects, 
    loading, 
    error,
    getProjectsByLevel,
    getProjectsByCategory,
    getProjectsByStatus
  };
};

export default useProjects;