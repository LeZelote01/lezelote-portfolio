import { useState, useEffect } from 'react';

const useTestimonials = () => {
  const [testimonials, setTestimonials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTestimonials = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/testimonials`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des témoignages');
        }
        
        const data = await response.json();
        // Trier par order_index puis par date de création
        const sortedTestimonials = data.sort((a, b) => {
          if (a.order_index !== b.order_index) {
            return (a.order_index || 0) - (b.order_index || 0);
          }
          return new Date(b.created_at) - new Date(a.created_at);
        });
        
        setTestimonials(sortedTestimonials);
        setError(null);
      } catch (err) {
        setError(err.message);
        setTestimonials([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTestimonials();
  }, []);

  // Fonction pour obtenir les témoignages mis en avant
  const getFeaturedTestimonials = () => {
    return testimonials.filter(testimonial => testimonial.featured);
  };

  return { testimonials, loading, error, getFeaturedTestimonials };
};

export default useTestimonials;