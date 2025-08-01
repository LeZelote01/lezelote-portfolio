import React from 'react';
import { Shield, Code, Server, Users, ArrowRight, Clock, Euro } from 'lucide-react';
import useServices from '../hooks/useServices';
import useTestimonials from '../hooks/useTestimonials';
import useProcessSteps from '../hooks/useProcessSteps';
import LoadingSpinner from './LoadingSpinner';

const Services = () => {
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
    <section id="services" className="py-20 bg-gray-800">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Mes <span className="text-green-400">services</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Solutions professionnelles en cybersécurité, développement Python et infrastructure
            </p>
          </div>

          {/* Services Grid */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {services.map((service, index) => {
              const ServiceIcon = getServiceIcon(service.icon);
              return (
                <div
                  key={service.id}
                  className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-green-400/50 transition-all duration-300 group hover:transform hover:scale-105"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Service Header */}
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <ServiceIcon size={32} className="text-gray-900" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white group-hover:text-green-400 transition-colors">
                        {service.title}
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
                    {service.description}
                  </p>

                  {/* Features */}
                  <div className="space-y-3 mb-8">
                    {service.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA */}
                  <button
                    onClick={() => {
                      const element = document.getElementById('contact');
                      if (element) element.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 flex items-center justify-center gap-2"
                  >
                    Demander un devis
                    <ArrowRight size={16} />
                  </button>
                </div>
              );
            })}
          </div>

          {/* Testimonials */}
          <div className="mb-16">
            <h3 className="text-3xl font-bold text-white text-center mb-12">
              Ce que disent mes <span className="text-green-400">clients</span>
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <div
                  key={testimonial.id}
                  className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
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

                  {/* Rating */}
                  <div className="flex gap-1 mt-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <div key={i} className="w-4 h-4 bg-green-400 rounded-full"></div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Process Preview */}
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 text-center">
            <h3 className="text-2xl font-bold text-white mb-4">
              Processus de collaboration
            </h3>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              Une méthodologie éprouvée pour garantir la réussite de vos projets,
              de l'analyse initiale à la livraison finale.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              {processSteps.slice(0, 3).map((step, index) => (
                <div key={index} className="flex items-center gap-2 bg-gray-800/50 rounded-lg px-4 py-2">
                  <div className="w-6 h-6 bg-green-400 rounded-full flex items-center justify-center">
                    <span className="text-gray-900 font-bold text-sm">{step.step}</span>
                  </div>
                  <span className="text-gray-300 text-sm">{step.title}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Services;