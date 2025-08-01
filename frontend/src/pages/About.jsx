import React from 'react';
import { Link } from 'react-router-dom';
import { User, Award, Target, Zap, ArrowRight } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import usePersonalInfo from '../hooks/usePersonalInfo';
import useProcessSteps from '../hooks/useProcessSteps';
import useStatistics from '../hooks/useStatistics';
import LoadingSpinner from '../components/LoadingSpinner';

const About = () => {
  const { t, td } = useLanguage();
  const { personalInfo, loading: personalLoading } = usePersonalInfo();
  const { processSteps, loading: processLoading } = useProcessSteps();
  const { statistics, loading: statsLoading } = useStatistics();

  if (personalLoading || processLoading || statsLoading) {
    return <LoadingSpinner />;
  }

  const features = [
    {
      icon: User,
      title: t('personalizedApproach'),
      description: t('personalizedApproachDesc')
    },
    {
      icon: Award,
      title: t('technicalExpertise'),
      description: t('technicalExpertiseDesc')
    },
    {
      icon: Target,
      title: t('concreteResults'),
      description: t('concreteResultsDesc')
    },
    {
      icon: Zap,
      title: t('reactivity'),
      description: t('reactivityDesc')
    }
  ];

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {t('aboutMe')}
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              {t('aboutMeSubtitle')}
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-start mb-20">
              {/* Photo et informations de base */}
              <div className="space-y-6">
                {/* Photo de profil */}
                {personalInfo?.profile_image_url && (
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 text-center">
                    <img
                      src={personalInfo.profile_image_url}
                      alt={personalInfo.name}
                      className="w-48 h-48 rounded-full border-4 border-green-400/50 shadow-2xl shadow-green-400/25 object-cover mx-auto mb-6 hover:scale-105 transition-transform duration-300"
                    />
                    <h2 className="text-3xl font-bold text-white mb-2">{personalInfo.name}</h2>
                    <p className="text-green-400 text-lg font-medium mb-2">{personalInfo.title}</p>
                    <p className="text-gray-400">{personalInfo.location}</p>
                  </div>
                )}

                {/* Informations personnelles détaillées */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-6">Informations personnelles</h3>
                  <div className="space-y-4">
                    {personalInfo?.age && (
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Âge</span>
                        <span className="text-white font-medium">{personalInfo.age} ans</span>
                      </div>
                    )}
                    {personalInfo?.years_experience && (
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Expérience</span>
                        <span className="text-white font-medium">{personalInfo.years_experience} ans</span>
                      </div>
                    )}
                    {personalInfo?.education && (
                      <div className="space-y-2">
                        <span className="text-gray-400">Formation</span>
                        <p className="text-white font-medium">{personalInfo.education}</p>
                      </div>
                    )}
                    {personalInfo?.availability && (
                      <div className="space-y-2">
                        <span className="text-gray-400">Disponibilité</span>
                        <p className="text-green-400 font-medium">{personalInfo.availability}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Langues */}
                {personalInfo?.languages && personalInfo.languages.length > 0 && (
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                    <h3 className="text-2xl font-bold text-white mb-6">Langues</h3>
                    <div className="space-y-3">
                      {personalInfo.languages.map((language, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                          <span className="text-gray-300">{language}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Certifications */}
                {personalInfo?.certifications && personalInfo.certifications.length > 0 && (
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                    <h3 className="text-2xl font-bold text-white mb-6">Certifications</h3>
                    <div className="space-y-3">
                      {personalInfo.certifications.map((cert, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-cyan-400 rounded-full"></div>
                          <span className="text-gray-300">{cert}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Contenu existant */}
              <div className="space-y-6">
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h2 className="text-3xl font-bold text-white mb-4">{t('myJourney')}</h2>
                  <p className="text-gray-300 leading-relaxed mb-6">
                    {personalInfo?.bio || t('aboutMeSubtitle')}
                  </p>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-gray-300">{t('constantTechWatch')}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-gray-300">{t('ethicalResponsibleApproach')}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-gray-300">{t('pedagogyTransmission')}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-4">{t('myMission')}</h3>
                  <p className="text-gray-300 leading-relaxed">
                    {t('myMissionDesc')}
                  </p>
                </div>

                {/* Features Grid */}
                <div className="grid sm:grid-cols-2 gap-6">
                  {features.map((feature, index) => (
                    <div
                      key={index}
                      className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group"
                    >
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                          <feature.icon size={24} className="text-gray-900" />
                        </div>
                        <h4 className="text-xl font-bold text-white">{feature.title}</h4>
                      </div>
                      <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Process Timeline */}
            <div className="mb-20">
              <h3 className="text-4xl font-bold text-white text-center mb-12">
                {t('workProcess')}
              </h3>
              <div className="grid md:grid-cols-5 gap-6">
                {processSteps.map((step, index) => (
                  <div key={index} className="text-center relative">
                    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                        <span className="text-gray-900 font-bold">{step.step}</span>
                      </div>
                      <h4 className="text-lg font-bold text-white mb-2">{td(step.title)}</h4>
                      <p className="text-gray-400 text-sm leading-relaxed">{td(step.description)}</p>
                    </div>
                    {index < processSteps.length - 1 && (
                      <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2 w-6 h-0.5 bg-green-400/30"></div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Statistics */}
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 mb-12">
              <h3 className="text-3xl font-bold text-white text-center mb-8">
                {t('someNumbers')}
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                {statistics.map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="text-4xl font-bold text-green-400 mb-2">
                      {stat.value}{stat.suffix}
                    </div>
                    <div className="text-gray-400">
                      {td(stat.title)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* CTA Section */}
            <div className="text-center">
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 max-w-3xl mx-auto">
                <h3 className="text-3xl font-bold text-white mb-4">
                  {t('readyToCollaborate')}
                </h3>
                <p className="text-gray-300 mb-6 leading-relaxed">
                  {t('readyToCollaborateDesc')}
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link
                    to="/contact"
                    className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 inline-flex items-center justify-center gap-2"
                  >
                    {t('contactMe')}
                    <ArrowRight size={20} />
                  </Link>
                  <Link
                    to="/projects"
                    className="border-2 border-green-400 text-green-400 px-8 py-4 rounded-lg font-semibold hover:bg-green-400 hover:text-gray-900 transition-all duration-200 transform hover:scale-105 inline-flex items-center justify-center gap-2"
                  >
                    {t('viewMyProjects')}
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;