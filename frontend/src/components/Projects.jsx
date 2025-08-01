import React, { useState } from 'react';
import { Github, ExternalLink, Code, Shield, Network, Globe } from 'lucide-react';
import useProjects from '../hooks/useProjects';
import LoadingSpinner from './LoadingSpinner';

const Projects = () => {
  const { projects, loading } = useProjects();
  const [activeFilter, setActiveFilter] = useState('all');

  if (loading) {
    return <LoadingSpinner />;
  }

  const categories = [
    { id: 'all', name: 'Tous les projets', icon: Globe },
    { id: 'Cybersécurité', name: 'Cybersécurité', icon: Shield },
    { id: 'Python', name: 'Python', icon: Code },
    { id: 'Full Stack', name: 'Full Stack', icon: Globe },
    { id: 'Réseaux', name: 'Réseaux', icon: Network }
  ];

  const filteredProjects = activeFilter === 'all' 
    ? projects 
    : projects.filter(project => project.category === activeFilter);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Terminé': return 'bg-green-500';
      case 'En cours': return 'bg-yellow-500';
      case 'Planifié': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Cybersécurité': return Shield;
      case 'Python': return Code;
      case 'Full Stack': return Globe;
      case 'Réseaux': return Network;
      default: return Code;
    }
  };

  return (
    <section id="projects" className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Mes <span className="text-green-400">projets</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Découvrez mes réalisations techniques en cybersécurité, Python et développement web
            </p>
          </div>

          {/* Filter Buttons */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveFilter(category.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                  activeFilter === category.id
                    ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <category.icon size={18} />
                {category.name}
              </button>
            ))}
          </div>

          {/* Projects Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredProjects.map((project, index) => {
              const CategoryIcon = getCategoryIcon(project.category);
              return (
                <div
                  key={project.id}
                  className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Project Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                        <CategoryIcon size={20} className="text-gray-900" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-white group-hover:text-green-400 transition-colors">
                          {project.title}
                        </h3>
                        <span className="text-sm text-gray-400">{project.category}</span>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-semibold text-white ${getStatusColor(project.status)}`}>
                      {project.status}
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-gray-300 mb-4 leading-relaxed">
                    {project.description}
                  </p>

                  {/* Technologies */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.technologies.map((tech, techIndex) => (
                      <span
                        key={techIndex}
                        className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-medium"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>

                  {/* Features */}
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-white mb-2">Fonctionnalités clés :</h4>
                    <ul className="space-y-1">
                      {project.features.slice(0, 3).map((feature, featureIndex) => (
                        <li key={featureIndex} className="text-sm text-gray-400 flex items-center gap-2">
                          <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3">
                    {project.github && (
                      <a
                        href={project.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-200 text-sm font-medium"
                      >
                        <Github size={16} />
                        Code
                      </a>
                    )}
                    {project.demo && (
                      <a
                        href={project.demo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 rounded-lg hover:from-green-500 hover:to-cyan-500 transition-all duration-200 text-sm font-medium"
                      >
                        <ExternalLink size={16} />
                        Démo
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* CTA Section */}
          <div className="text-center mt-16">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 max-w-3xl mx-auto">
              <h3 className="text-2xl font-bold text-white mb-4">
                Vous avez un projet en tête ?
              </h3>
              <p className="text-gray-300 mb-6 leading-relaxed">
                Je suis disponible pour de nouveaux projets et collaborations. 
                Discutons de vos besoins en cybersécurité et développement Python.
              </p>
              <button
                onClick={() => {
                  const element = document.getElementById('contact');
                  if (element) element.scrollIntoView({ behavior: 'smooth' });
                }}
                className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105"
              >
                Contactez-moi
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Projects;