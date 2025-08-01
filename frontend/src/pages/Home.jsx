import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { ChevronRight, Shield, Code, Network, ArrowRight, Star, Calculator, FileText, BookOpen } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

// Import hooks
import usePersonalInfo from '../hooks/usePersonalInfo';
import useProjects from '../hooks/useProjects';
import useSkills from '../hooks/useSkills';
import useTestimonials from '../hooks/useTestimonials';
import useStatistics from '../hooks/useStatistics';

const Home = () => {
  const { t, td } = useLanguage();

  // Use hooks for data
  const { personalInfo, loading: personalLoading } = usePersonalInfo();
  const { projects, loading: projectsLoading } = useProjects();
  const { skills, loading: skillsLoading } = useSkills();
  const { testimonials, loading: testimonialsLoading } = useTestimonials();
  const { statistics, loading: statsLoading } = useStatistics();

  // Loading state for critical data
  if (personalLoading || skillsLoading || statsLoading) {
    return <LoadingSpinner message={t('loadingPortfolio')} />;
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden pt-20">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"></div>
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/5 to-transparent"></div>
        
        {/* Grid Pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-green-400/5 to-transparent"></div>
        </div>

        <div className="relative z-10 container mx-auto px-6 text-center">
          <div className="max-w-4xl mx-auto">
            {/* Photo de profil */}
            {personalInfo?.profile_image_url && (
              <div className="mb-8 flex justify-center">
                <div className="relative">
                  <img
                    src={personalInfo.profile_image_url}
                    alt={personalInfo.name}
                    className="w-40 h-40 md:w-48 md:h-48 rounded-full border-4 border-green-400/50 shadow-2xl shadow-green-400/25 object-cover hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 rounded-full bg-gradient-to-r from-green-400/20 to-cyan-400/20"></div>
                </div>
              </div>
            )}

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

            {/* Subtitle - Use static translations instead of API data */}
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              {t('heroDescription')}
            </p>

            {personalInfo && personalInfo.bio && (
              <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                {personalInfo.bio.substring(0, 200)}...
              </p>
            )}

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link
                to="/projects"
                className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 hover:shadow-lg hover:shadow-green-400/25"
              >
                {t('discoverProjects')}
              </Link>
              <Link
                to="/services"
                className="border-2 border-green-400 text-green-400 px-8 py-4 rounded-lg font-semibold hover:bg-green-400 hover:text-gray-900 transition-all duration-200 transform hover:scale-105"
              >
                {t('myServices')}
              </Link>
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
          </div>
        </div>
      </section>

      {/* Quick Tools */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-6">
                {t('freeTools')} <span className="text-green-400"></span>
              </h2>
              <p className="text-xl text-gray-400 max-w-3xl mx-auto">
                {t('freeToolsDesc')}
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <Link
                to="/calculator"
                className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
              >
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Calculator size={32} className="text-gray-900" />
                  </div>
                  <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                    {t('priceCalculator')}
                  </h3>
                </div>
                <p className="text-gray-400 leading-relaxed mb-4">
                  {t('priceCalculatorDesc')}
                </p>
                <div className="flex items-center gap-2 text-green-400 group-hover:gap-3 transition-all">
                  <span className="text-sm font-medium">{t('calculateNow')}</span>
                  <ArrowRight size={16} />
                </div>
              </Link>

              <Link
                to="/resources"
                className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
              >
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <FileText size={32} className="text-gray-900" />
                  </div>
                  <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                    {t('freeResourcesHome')}
                  </h3>
                </div>
                <p className="text-gray-400 leading-relaxed mb-4">
                  {t('freeResourcesHomeDesc')}
                </p>
                <div className="flex items-center gap-2 text-green-400 group-hover:gap-3 transition-all">
                  <span className="text-sm font-medium">{t('downloadNow')}</span>
                  <ArrowRight size={16} />
                </div>
              </Link>

              <Link
                to="/blog"
                className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
              >
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <BookOpen size={32} className="text-gray-900" />
                  </div>
                  <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                    {t('technicalBlogHome')}
                  </h3>
                </div>
                <p className="text-gray-400 leading-relaxed mb-4">
                  {t('technicalBlogHomeDesc')}
                </p>
                <div className="flex items-center gap-2 text-green-400 group-hover:gap-3 transition-all">
                  <span className="text-sm font-medium">{t('readArticles')}</span>
                  <ArrowRight size={16} />
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Overview */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-6">
                {t('skillsOverview')} <span className="text-green-400"></span>
              </h2>
              <p className="text-xl text-gray-400 max-w-3xl mx-auto">
                {t('skillsOverviewDesc')}
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {Object.entries(skills).map(([key, skill], index) => (
                <Link
                  key={key}
                  to="/skills"
                  className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
                >
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <span className="text-gray-900 text-2xl font-bold">
                        {skill.title.charAt(0)}
                      </span>
                    </div>
                    <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                      {td(skill.title)}
                    </h3>
                  </div>
                  
                  <div className="space-y-3">
                    {skill.items.slice(0, 3).map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-center justify-between">
                        <span className="text-gray-300">{td(item.name)}</span>
                        <span className="text-green-400 font-semibold">{item.level}%</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-6 flex items-center gap-2 text-green-400 group-hover:gap-3 transition-all">
                    <span className="text-sm font-medium">{t('seeMore')}</span>
                    <ArrowRight size={16} />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Featured Projects */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-6">
                {t('featuredProjects')} <span className="text-green-400"></span>
              </h2>
              <p className="text-xl text-gray-400 max-w-3xl mx-auto">
                {t('featuredProjectsDesc')}
              </p>
            </div>

            {projectsLoading ? (
              <LoadingSpinner message={t('loadingProjects')} />
            ) : (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                  {projects.slice(0, 6).map((project, index) => (
                    <div
                      key={project.id}
                      className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                            <Shield size={20} className="text-gray-900" />
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-white group-hover:text-green-400 transition-colors">
                              {project.title}
                            </h3>
                            <span className="text-sm text-gray-400">{project.category}</span>
                          </div>
                        </div>
                        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded-full">
                          {project.level}
                        </span>
                      </div>

                      <p className="text-gray-300 mb-4 text-sm leading-relaxed">
                        {project.description.substring(0, 100)}...
                      </p>

                      <div className="flex flex-wrap gap-2">
                        {project.technologies.slice(0, 3).map((tech, techIndex) => (
                          <span
                            key={techIndex}
                            className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="text-center">
                  <Link
                    to="/projects"
                    className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 inline-flex items-center gap-2"
                  >
                    {t('viewAllProjects')}
                    <ChevronRight size={20} />
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-6">
                {t('whatClientsSay')} <span className="text-green-400"></span>
              </h2>
            </div>

            {testimonialsLoading ? (
              <LoadingSpinner message={t('loadingTestimonials')} />
            ) : (
              <div className="grid md:grid-cols-3 gap-8">
                {testimonials.map((testimonial, index) => (
                  <div
                    key={testimonial.id}
                    className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300"
                  >
                    <div className="flex gap-1 mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} size={16} className="text-green-400 fill-current" />
                      ))}
                    </div>
                    
                    <p className="text-gray-300 mb-4 leading-relaxed">
                      "{testimonial.content}"
                    </p>
                    
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-full flex items-center justify-center">
                        <span className="text-gray-900 font-bold">
                          {testimonial.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <h4 className="text-white font-semibold">{testimonial.name}</h4>
                        <p className="text-gray-400 text-sm">{testimonial.role}</p>
                        <p className="text-gray-500 text-sm">{testimonial.company}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;