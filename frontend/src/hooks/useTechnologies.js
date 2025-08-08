import { useState, useEffect } from 'react';

const useTechnologies = () => {
  const [technologies, setTechnologies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTechnologies = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/technologies`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des technologies');
        }
        
        const data = await response.json();
        // Trier par nom
        const sortedTechnologies = data.sort((a, b) => a.name.localeCompare(b.name));
        
        setTechnologies(sortedTechnologies);
        setError(null);
      } catch (err) {
        setError(err.message);
        setTechnologies([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTechnologies();
  }, []);

  // Fonction pour obtenir les technologies par catégorie
  const getTechnologiesByCategory = (category) => {
    return technologies.filter(tech => tech.category === category);
  };

  return { technologies, loading, error, getTechnologiesByCategory };
};

export default useTechnologies;