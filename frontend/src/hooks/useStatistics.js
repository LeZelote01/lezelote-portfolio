import { useState, useEffect } from 'react';

const useStatistics = () => {
  const [statistics, setStatistics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/statistics`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des statistiques');
        }
        
        const data = await response.json();
        // Trier par order_index
        const sortedStats = data.sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
        
        setStatistics(sortedStats);
        setError(null);
      } catch (err) {
        setError(err.message);
        setStatistics([]);
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

  return { statistics, loading, error };
};

export default useStatistics;