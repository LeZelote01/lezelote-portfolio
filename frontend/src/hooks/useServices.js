import { useState, useEffect } from 'react';

const useServices = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/services`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des services');
        }
        
        const data = await response.json();
        // Trier par order_index
        const sortedServices = data.sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
        
        setServices(sortedServices);
        setError(null);
      } catch (err) {
        setError(err.message);
        setServices([]);
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  return { services, loading, error };
};

export default useServices;