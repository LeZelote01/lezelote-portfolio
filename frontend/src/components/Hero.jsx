import React from 'react';
import { ChevronDown, Shield, Code, Network } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import usePersonalInfo from '../hooks/usePersonalInfo';
import useStatistics from '../hooks/useStatistics';
import LoadingSpinner from './LoadingSpinner';

const Hero = () => {
  const { t, td } = useLanguage();
  const { personalInfo, loading: personalLoading } = usePersonalInfo();
  const { statistics, loading: statsLoading } = useStatistics();
  
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (personalLoading || statsLoading) {
    return <LoadingSpinner />;
  }

  return (
    <section id="hero" className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"></div>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/5 to-transparent"></div>
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-green-400/5 to-transparent"></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 text-center">
        <div className="max-w-4xl mx-auto">
          {/* Badges */}
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <div className="flex items-center gap-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full px-4 py-2">
              <Shield size={16} className="text-green-400" />
              <span className="text-sm text-gray-300">{t('cybersecurity')}</span>
            </div>
            <div className="flex items-center gap-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full px-4 py-2">
              <Code size={16} className="text-green-400" />
              <span className="text-sm text-gray-300">Python</span>
            </div>
            <div className="flex items-center gap-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full px-4 py-2">
              <Network size={16} className="text-green-400" />
              <span className="text-sm text-gray-300">{td('Réseaux')}</span>
            </div>
          </div>

          {/* Main Title */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="text-white">{t('specialist')}</span>{' '}
            <span className="bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">
              {t('cybersecurity')}
            </span>
            <br />
            <span className="text-white">& {t('developer')}</span>{' '}
            <span className="bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">
              Python
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            {personalInfo?.subtitle || t('heroDescription')}
          </p>

          {/* Description */}
          <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            {t('heroDescription')}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <button
              onClick={() => scrollToSection('projects')}
              className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 hover:shadow-lg hover:shadow-green-400/25"
            >
              {t('discoverProjects')}
            </button>
            <button
              onClick={() => scrollToSection('services')}
              className="border-2 border-green-400 text-green-400 px-8 py-4 rounded-lg font-semibold hover:bg-green-400 hover:text-gray-900 transition-all duration-200 transform hover:scale-105"
            >
              {t('myServices')}
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
            {statistics.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-green-400 mb-2">
                  {stat.value}{stat.suffix}
                </div>
                <div className="text-sm text-gray-400">
                  {td(stat.title)}
                </div>
              </div>
            ))}
          </div>

          {/* Scroll Indicator */}
          <div className="flex justify-center">
            <button
              onClick={() => scrollToSection('about')}
              className="animate-bounce text-green-400 hover:text-green-300 transition-colors"
            >
              <ChevronDown size={32} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;