import React from 'react';
import { User, Award, Target, Zap } from 'lucide-react';
import usePersonalInfo from '../hooks/usePersonalInfo';
import useProcessSteps from '../hooks/useProcessSteps';
import LoadingSpinner from './LoadingSpinner';

const About = () => {
  const { personalInfo, loading: personalLoading } = usePersonalInfo();
  const { processSteps, loading: processLoading } = useProcessSteps();

  if (personalLoading || processLoading) {
    return <LoadingSpinner />;
  }

  const features = [
    {
      icon: User,
      title: "Approche personnalisée",
      description: "Chaque projet est unique, j'adapte mes solutions à vos besoins spécifiques."
    },
    {
      icon: Award,
      title: "Expertise technique",
      description: "Formation continue aux dernières technologies et menaces émergentes."
    },
    {
      icon: Target,
      title: "Résultats concrets",
      description: "Focus sur l'efficacité et la sécurité mesurable de vos systèmes."
    },
    {
      icon: Zap,
      title: "Réactivité",
      description: "Disponibilité et réponse rapide pour vos urgences sécuritaires."
    }
  ];

  return (
    <section id="about" className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              À propos de <span className="text-green-400">moi</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Découvrez mon parcours et ma passion pour la cybersécurité
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Content */}
            <div className="space-y-6">
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h3 className="text-2xl font-bold text-white mb-4">Mon parcours</h3>
                <p className="text-gray-300 leading-relaxed mb-6">
                  {personalInfo?.bio || "Passionné par la cybersécurité et le développement Python, je mets mon expertise technique au service de votre sécurité numérique."}
                </p>
                
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-gray-300">Veille technologique constante</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-gray-300">Approche éthique et responsable</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-gray-300">Pédagogie et transmission</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h3 className="text-2xl font-bold text-white mb-4">Ma mission</h3>
                <p className="text-gray-300 leading-relaxed">
                  Démocratiser la cybersécurité et rendre les technologies sûres et accessibles 
                  à tous. Mon objectif est d'accompagner les entreprises dans leur transformation 
                  digitale sécurisée, en mettant l'accent sur la prévention et l'éducation.
                </p>
              </div>
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

          {/* Process Timeline */}
          <div className="mt-20">
            <h3 className="text-3xl font-bold text-white text-center mb-12">
              Mon processus de <span className="text-green-400">travail</span>
            </h3>
            <div className="grid md:grid-cols-5 gap-6">
              {processSteps.map((step, index) => (
                <div key={index} className="text-center relative">
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-green-400/50 transition-all duration-300 group">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                      <span className="text-gray-900 font-bold">{step.step}</span>
                    </div>
                    <h4 className="text-lg font-bold text-white mb-2">{step.title}</h4>
                    <p className="text-gray-400 text-sm leading-relaxed">{step.description}</p>
                  </div>
                  {index < processSteps.length - 1 && (
                    <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2 w-6 h-0.5 bg-green-400/30"></div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;