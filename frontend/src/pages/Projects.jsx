import React, { useState } from 'react';
import { Github, ExternalLink, Code, Shield, Network, Globe, Filter, Clock, Star } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import useProjects from '../hooks/useProjects';
import LoadingSpinner from '../components/LoadingSpinner';

const Projects = () => {
  const { t, td } = useLanguage();
  const { projects, loading } = useProjects();
  const [activeFilter, setActiveFilter] = useState('all');
  const [activeLevelFilter, setActiveLevelFilter] = useState('all');

  if (loading) {
    return <LoadingSpinner />;
  }

  const categories = [
    { id: 'all', name: t('allProjects'), icon: Globe },
    { id: 'Cybersécurité', name: td('Cybersécurité'), icon: Shield },
    { id: 'Python', name: 'Python', icon: Code },
    { id: 'Réseaux', name: td('Réseaux'), icon: Network },
    { id: 'Forensique', name: td('Forensique'), icon: Shield }
  ];

  const levels = [
    { id: 'all', name: t('allLevels') },
    { id: 'Débutant', name: td('Débutant') },
    { id: 'Intermédiaire', name: td('Intermédiaire') },
    { id: 'Avancé', name: td('Avancé') }
  ];

  const filteredProjects = projects.filter(project => {
    const matchesCategory = activeFilter === 'all' || project.category === activeFilter;
    const matchesLevel = activeLevelFilter === 'all' || project.level === activeLevelFilter;
    return matchesCategory && matchesLevel;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'Terminé': return 'bg-green-500';
      case 'En cours': return 'bg-yellow-500';
      case 'Planifié': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'Débutant': return 'bg-green-500';
      case 'Intermédiaire': return 'bg-yellow-500';
      case 'Avancé': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Cybersécurité': return Shield;
      case 'Python': return Code;
      case 'Réseaux': return Network;
      case 'Forensique': return Shield;
      default: return Code;
    }
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {t('myProjects')}
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              {t('projectsSubtitle')}
            </p>
          </div>
        </div>
      </section>

      {/* Filters */}
      <section className="py-12 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            {/* Category Filters */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Filter size={20} />
                {t('filterByCategory')}
              </h3>
              <div className="flex flex-wrap gap-4">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setActiveFilter(category.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                      activeFilter === category.id
                        ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    <category.icon size={16} />
                    {category.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Level Filters */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Star size={20} />
                {t('filterByLevel')}
              </h3>
              <div className="flex flex-wrap gap-4">
                {levels.map((level) => (
                  <button
                    key={level.id}
                    onClick={() => setActiveLevelFilter(level.id)}
                    className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                      activeLevelFilter === level.id
                        ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {level.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Projects Count */}
            <div className="mb-8">
              <p className="text-gray-400">
                {filteredProjects.length} {t('allProjects').toLowerCase()}{filteredProjects.length !== 1 ? 's' : ''} {t('dataNotAvailable').includes('trouvé') ? 'trouvé' : 'found'}{filteredProjects.length !== 1 ? 's' : ''}
              </p>
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
                          <span className="text-sm text-gray-400">{td(project.category)}</span>
                        </div>
                      </div>
                      <div className="flex flex-col gap-2">
                        <div className={`px-2 py-1 rounded-full text-xs font-semibold text-white ${getStatusColor(project.status)}`}>
                          {td(project.status)}
                        </div>
                        <div className={`px-2 py-1 rounded-full text-xs font-semibold text-white ${getLevelColor(project.level)}`}>
                          {td(project.level)}
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-gray-300 mb-4 leading-relaxed">
                      {td(project.description)}
                    </p>

                    {/* Duration */}
                    <div className="flex items-center gap-2 mb-4 text-gray-400">
                      <Clock size={14} />
                      <span className="text-sm">{t('duration')}: {project.duration}</span>
                    </div>

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
                      <h4 className="text-sm font-semibold text-white mb-2">{t('keyFeatures')} :</h4>
                      <ul className="space-y-1">
                        {project.features.slice(0, 3).map((feature, featureIndex) => (
                          <li key={featureIndex} className="text-sm text-gray-400 flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                            {td(feature)}
                          </li>
                        ))}
                        {project.features.length > 3 && (
                          <li className="text-sm text-gray-500 italic">
                            +{project.features.length - 3} {t('seeMore').toLowerCase()}
                          </li>
                        )}
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
                          {t('preview')}
                        </a>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Empty State */}
            {filteredProjects.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Code size={32} className="text-gray-500" />
                </div>
                <h3 className="text-xl font-bold text-gray-300 mb-2">{t('dataNotAvailable')}</h3>
                <p className="text-gray-500">{t('tryAgainLater')}</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Project Stats */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold text-white text-center mb-12">
              {t('myProjects')} <span className="text-green-400">{t('dataNotAvailable').toLowerCase()}</span>
            </h2>
            
            <div className="grid md:grid-cols-4 gap-8">
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 text-center">
                <div className="text-4xl font-bold text-green-400 mb-2">
                  {projects.length}
                </div>
                <div className="text-gray-400">{t('allProjects')}</div>
              </div>
              
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 text-center">
                <div className="text-4xl font-bold text-green-400 mb-2">
                  {projects.filter(p => p.status === 'Terminé').length}
                </div>
                <div className="text-gray-400">{td('Terminé')}</div>
              </div>
              
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 text-center">
                <div className="text-4xl font-bold text-yellow-400 mb-2">
                  {projects.filter(p => p.status === 'En cours').length}
                </div>
                <div className="text-gray-400">{td('En cours')}</div>
              </div>
              
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 text-center">
                <div className="text-4xl font-bold text-blue-400 mb-2">
                  {projects.filter(p => p.status === 'Planifié').length}
                </div>
                <div className="text-gray-400">{td('Planifié')}</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Projects;