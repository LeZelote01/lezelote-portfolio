import { useState, useEffect } from 'react';

const useSkills = () => {
  const defaultSkills = {
    cybersecurity: {
      title: "Cybersécurité",
      icon: "shield-check",
      items: [
        { name: "Audit de sécurité", level: 95 },
        { name: "Pentesting", level: 90 },
        { name: "Forensique", level: 85 },
        { name: "Conformité RGPD", level: 88 },
        { name: "Sécurité des réseaux", level: 92 }
      ]
    },
    python: {
      title: "Développement Python",
      icon: "code",
      items: [
        { name: "Django/FastAPI", level: 95 },
        { name: "Automatisation", level: 92 },
        { name: "Data Science", level: 85 },
        { name: "APIs REST", level: 98 },
        { name: "Tests unitaires", level: 90 }
      ]
    },
    network: {
      title: "Réseau & Infrastructure",
      icon: "network",
      items: [
        { name: "Administration Linux", level: 90 },
        { name: "Configuration réseau", level: 88 },
        { name: "Firewalls", level: 85 },
        { name: "Monitoring", level: 87 },
        { name: "Virtualisation", level: 82 }
      ]
    }
  };

  const defaultSkillCategories = [
    {
      id: "1",
      title: "Cybersécurité",
      icon: "shield-check",
      category_key: "cybersecurity",
      items: defaultSkills.cybersecurity.items
    },
    {
      id: "2", 
      title: "Développement Python",
      icon: "code",
      category_key: "python",
      items: defaultSkills.python.items
    },
    {
      id: "3",
      title: "Réseau & Infrastructure", 
      icon: "network",
      category_key: "network",
      items: defaultSkills.network.items
    }
  ];

  const [skills, setSkills] = useState(defaultSkills);
  const [skillCategories, setSkillCategories] = useState(defaultSkillCategories);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/public/skills`);
        
        if (!response.ok) {
          console.warn('Failed to fetch skills from API, using default data');
          setError(null);
          return;
        }
        
        const data = await response.json();
        
        if (data && data.length > 0) {
          setSkillCategories(data);
          
          // Convertir le tableau en objet pour l'ancien format
          const skillsObj = {};
          data.forEach(category => {
            skillsObj[category.category_key] = {
              title: category.title,
              icon: category.icon,
              items: category.items || []
            };
          });
          setSkills(skillsObj);
          setError(null);
        } else {
          console.warn('No skills data received from API, using default data');
          // Garder les données par défaut
        }
      } catch (err) {
        console.warn('Error fetching skills, using default data:', err.message);
        setError(null); // Ne pas afficher d'erreur, utiliser les données par défaut
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, []);

  return { skills, skillCategories, loading, error };
};

export default useSkills;