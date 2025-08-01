import { useState, useEffect } from 'react';

const usePersonalInfo = () => {
  const [personalInfo, setPersonalInfo] = useState({
    name: "Jean-Yves LeZelote",
    title: "Expert en Cybersécurité",
    subtitle: "Spécialiste en sécurité informatique et audit",
    bio: "Expert passionné en cybersécurité avec plus de 15 ans d'expérience.",
    email: "contact@jeanyves.dev",
    phone: "+33123456789",
    location: "France",
    availability: "Disponible",
    website: "https://jeanyves.dev"
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPersonalInfo = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/personal`);
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des informations personnelles');
        }
        
        const data = await response.json();
        
        // Si on a des données, les utiliser, sinon garder les données par défaut
        if (data && Object.keys(data).length > 0) {
          setPersonalInfo(data);
        }
        
        setError(null);
      } catch (err) {
        console.warn('Utilisation des données par défaut:', err.message);
        setError(null); // Ne pas afficher d'erreur, utiliser les données par défaut
      } finally {
        setLoading(false);
      }
    };

    fetchPersonalInfo();
  }, []);

  return { personalInfo, loading, error };
};

export default usePersonalInfo;