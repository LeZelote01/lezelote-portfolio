import React from "react";

const ProjectGallery = () => {
  return (
    <section className="max-w-5xl mx-auto py-16 animate-fade-in">
      {/* Ajoutez ici le contenu de votre galerie de projets */}
      <h2 className="text-3xl font-bold text-center mb-8">Projets Réalisés</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Exemple de projet */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <img
            src="https://via.placeholder.com/600x400"
            alt="Nom du Projet"
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h3 className="text-xl font-semibold mb-2">Nom du Projet</h3>
            <p className="text-gray-700">
              Description concise du projet. Technologies utilisées, défis relevés, etc.
            </p>
            <a
              href="#"
              className="inline-block mt-4 bg-primary text-primary-foreground py-2 px-4 rounded hover:bg-primary/80 transition-colors"
            >
              Voir le Projet
            </a>
          </div>
        </div>
        {/* Répétez ce bloc pour chaque projet */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <img
            src="https://via.placeholder.com/600x400"
            alt="Nom du Projet"
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h3 className="text-xl font-semibold mb-2">Nom du Projet</h3>
            <p className="text-gray-700">
              Description concise du projet. Technologies utilisées, défis relevés, etc.
            </p>
            <a
              href="#"
              className="inline-block mt-4 bg-primary text-primary-foreground py-2 px-4 rounded hover:bg-primary/80 transition-colors"
            >
              Voir le Projet
            </a>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <img
            src="https://via.placeholder.com/600x400"
            alt="Nom du Projet"
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h3 className="text-xl font-semibold mb-2">Nom du Projet</h3>
            <p className="text-gray-700">
              Description concise du projet. Technologies utilisées, défis relevés, etc.
            </p>
            <a
              href="#"
              className="inline-block mt-4 bg-primary text-primary-foreground py-2 px-4 rounded hover:bg-primary/80 transition-colors"
            >
              Voir le Projet
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProjectGallery;
