import { useState, useEffect } from 'react';

const useSocialLinks = () => {
  const [socialLinks, setSocialLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSocialLinks = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/social-links`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des liens sociaux');
        }
        
        const data = await response.json();
        // Trier par order_index
        const sortedLinks = data.sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
        
        setSocialLinks(sortedLinks);
        setError(null);
      } catch (err) {
        setError(err.message);
        setSocialLinks([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSocialLinks();
  }, []);

  return { socialLinks, loading, error };
};

export default useSocialLinks;