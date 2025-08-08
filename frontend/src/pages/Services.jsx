import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Code, Server, Users, ArrowRight, Clock, Euro, CheckCircle, Star } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import useServices from '../hooks/useServices';
import useTestimonials from '../hooks/useTestimonials';
import useProcessSteps from '../hooks/useProcessSteps';
import LoadingSpinner from '../components/LoadingSpinner';

const Services = () => {
  const { t, td } = useLanguage();
  const { services, loading: servicesLoading } = useServices();
  const { testimonials, loading: testimonialsLoading } = useTestimonials();
  const { processSteps, loading: processLoading } = useProcessSteps();

  if (servicesLoading || testimonialsLoading || processLoading) {
    return <LoadingSpinner />;
  }

  const getServiceIcon = (iconName) => {
    const icons = {
      Shield,
      Code,
      Server,
      Users
    };
    return icons[iconName] || Shield;
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {t('myServicesTitle')}
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              {t('servicesSubtitle')}
            </p>
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8 mb-16">
              {services.map((service, index) => {
                const ServiceIcon = getServiceIcon(service.icon);
                return (
                  <div
                    key={service.id}
                    className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    {/* Service Header */}
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <ServiceIcon size={32} className="text-gray-900" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                          {td(service.title)}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                          <span className="flex items-center gap-1">
                            <Euro size={14} />
                            {service.price}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock size={14} />
                            {service.duration}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-gray-300 mb-6 leading-relaxed">
                      {td(service.description)}
                    </p>

                    {/* Features */}
                    <div className="space-y-3 mb-8">
                      <h4 className="text-lg font-semibold text-white">{t('keyFeatures')} :</h4>
                      {service.features.map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-center gap-3">
                          <CheckCircle size={16} className="text-green-400" />
                          <span className="text-gray-300">{td(feature)}</span>
                        </div>
                      ))}
                    </div>

                    {/* CTA */}
                    <Link
                      to="/contact"
                      className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 flex items-center justify-center gap-2"
                    >
                      {t('requestQuote')}
                      <ArrowRight size={16} />
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold text-white text-center mb-12">
              {t('collaborationProcess')}
            </h2>
            
            <div className="grid md:grid-cols-5 gap-6">
              {processSteps.map((step, index) => (
                <div key={index} className="text-center relative">
                  <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
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
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold text-white text-center mb-12">
              {t('whatClientsSay')}
            </h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <div
                  key={testimonial.id}
                  className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Rating */}
                  <div className="flex gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} size={16} className="text-green-400 fill-current" />
                    ))}
                  </div>

                  {/* Quote */}
                  <div className="mb-4">
                    <div className="text-green-400 text-4xl mb-2">"</div>
                    <p className="text-gray-300 leading-relaxed">
                      {testimonial.content}
                    </p>
                  </div>

                  {/* Author */}
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
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-white text-center mb-12">
              {t('frequentlyAsked')}
            </h2>
            
            <div className="space-y-6">
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">
                  {t('quickResponse')} ?
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {t('quickResponse')} 24h. {t('tryAgainLater')}.
                </p>
              </div>

              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">
                  {t('technicalExpertise')} ?
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {t('concreteResults')}.
                </p>
              </div>

              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">
                  {t('requestQuote')} ?
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {t('personalizedApproach')}.
                </p>
              </div>

              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">
                  {t('reactivity')} ?
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {t('reactivity')}.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
              <h3 className="text-3xl font-bold text-white mb-4">
                {t('getStarted')} ?
              </h3>
              <p className="text-gray-300 mb-6 leading-relaxed">
                {t('contactSubtitle')}
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/contact"
                  className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 inline-flex items-center justify-center gap-2"
                >
                  {t('requestQuote')}
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
      </section>
    </div>
  );
};

export default Services;