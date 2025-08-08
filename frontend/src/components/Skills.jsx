import React, { useState } from 'react';
import { Shield, Code, Network, ChevronRight, AlertCircle } from 'lucide-react';
import useSkills from '../hooks/useSkills';
import useTechnologies from '../hooks/useTechnologies';
import LoadingSpinner from './LoadingSpinner';
import { useLanguage } from '../context/LanguageContext';

const Skills = () => {
  const { skills, loading: skillsLoading } = useSkills();
  const { technologies, loading: techLoading } = useTechnologies();
  const [activeSkillTab, setActiveSkillTab] = useState('cybersecurity');
  const { t } = useLanguage();

  if (skillsLoading || techLoading) {
    return <LoadingSpinner />;
  }

  // Vérifier si les compétences sont disponibles
  const hasSkills = skills && Object.keys(skills).length > 0;
  const hasTechnologies = technologies && technologies.length > 0;

  const skillCategories = hasSkills ? {
    cybersecurity: {
      ...skills.cybersecurity,
      icon: Shield,
      color: 'from-red-500 to-orange-500'
    },
    python: {
      ...skills.python,
      icon: Code,
      color: 'from-blue-500 to-cyan-500'
    },
    network: {
      ...skills.network,
      icon: Network,
      color: 'from-green-500 to-emerald-500'
    }
  } : {};

  // Vérifier si la catégorie active existe, sinon prendre la première disponible
  const availableCategories = Object.keys(skillCategories);
  const currentActiveTab = availableCategories.includes(activeSkillTab) 
    ? activeSkillTab 
    : availableCategories[0];

  const SkillBar = ({ skill, index }) => (
    <div className="space-y-2" style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="flex justify-between items-center">
        <span className="text-white font-medium">{skill.name}</span>
        <span className="text-green-400 font-bold">{skill.level}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
        <div
          className="bg-gradient-to-r from-green-400 to-cyan-400 h-2 rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${skill.level}%` }}
        ></div>
      </div>
    </div>
  );

  const EmptyStateMessage = ({ title, message }) => (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl">
      <AlertCircle className="h-12 w-12 text-gray-500 mb-4" />
      <h3 className="text-xl font-semibold text-gray-300 mb-2">{title}</h3>
      <p className="text-gray-500">{message}</p>
    </div>
  );

  return (
    <section id="skills" className="py-20 bg-gray-800">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              {t('mySkills').split(' ')[0]} <span className="text-green-400">{t('mySkills').split(' ')[1]}</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              {t('technicalExpertiseSubtitle')}
            </p>
          </div>

          {/* Skills Navigation */}
          {hasSkills && availableCategories.length > 0 && (
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              {availableCategories.map((key) => {
                const category = skillCategories[key];
                if (!category) return null;
                
                return (
                  <button
                    key={key}
                    onClick={() => setActiveSkillTab(key)}
                    className={`flex items-center gap-3 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                      currentActiveTab === key
                        ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <category.icon size={20} />
                    {category.title}
                  </button>
                );
              })}
            </div>
          )}

          {/* Skills Content */}
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Skills List */}
            <div className="space-y-6">
              {hasSkills && skillCategories[currentActiveTab] ? (
                <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                      {React.createElement(skillCategories[currentActiveTab].icon, { size: 24, className: "text-gray-900" })}
                    </div>
                    <h3 className="text-2xl font-bold text-white">
                      {skillCategories[currentActiveTab].title}
                    </h3>
                  </div>
                  
                  <div className="space-y-6">
                    {skillCategories[currentActiveTab].items && skillCategories[currentActiveTab].items.length > 0 ? (
                      skillCategories[currentActiveTab].items.map((skill, index) => (
                        <SkillBar key={index} skill={skill} index={index} />
                      ))
                    ) : (
                      <EmptyStateMessage 
                        title={t('skillsNotConfigured')}
                        message={t('noSkillsMessage')}
                      />
                    )}
                  </div>
                </div>
              ) : (
                <EmptyStateMessage 
                  title={t('skillsNotAvailable')}
                  message={t('skillsContactAdmin')}
                />
              )}
            </div>

            {/* Technologies & Tools */}
            <div className="space-y-6">
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h3 className="text-2xl font-bold text-white mb-6">
                  {t('technologiesTools')}
                </h3>
                
                {hasTechnologies ? (
                  <div className="grid grid-cols-2 gap-4">
                    {technologies.map((tech, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-all duration-200 group"
                      >
                        <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                          <span className="text-gray-900 text-xs font-bold">
                            {tech.name.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <div className="text-white font-medium text-sm">{tech.name}</div>
                          <div className="text-gray-400 text-xs">{tech.category}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyStateMessage 
                    title={t('technologiesNotConfigured')}
                    message={t('technologiesNotConfiguredMessage')}
                  />
                )}
              </div>

              {/* Certifications & Formation */}
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h3 className="text-2xl font-bold text-white mb-6">
                  {t('continuousTraining')}
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                    <ChevronRight size={16} className="text-green-400" />
                    <span className="text-gray-300">Veille technologique quotidienne</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                    <ChevronRight size={16} className="text-green-400" />
                    <span className="text-gray-300">Participation à des CTF (Capture The Flag)</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                    <ChevronRight size={16} className="text-green-400" />
                    <span className="text-gray-300">Formations en ligne spécialisées</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                    <ChevronRight size={16} className="text-green-400" />
                    <span className="text-gray-300">Contribution à des projets open source</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Skills;