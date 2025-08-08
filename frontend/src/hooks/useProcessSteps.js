import { useState, useEffect } from 'react';

const useProcessSteps = () => {
  const [processSteps, setProcessSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProcessSteps = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/process-steps`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des étapes du processus');
        }
        
        const data = await response.json();
        // Trier par numéro d'étape
        const sortedSteps = data.sort((a, b) => a.step - b.step);
        
        setProcessSteps(sortedSteps);
        setError(null);
      } catch (err) {
        setError(err.message);
        setProcessSteps([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProcessSteps();
  }, []);

  return { processSteps, loading, error };
};

export default useProcessSteps;