import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Calculator as CalcIcon, Download, FileText, Shield, Code, Server, Users, Check, User, Mail, Building, Phone, MessageSquare, Send } from 'lucide-react';
import jsPDF from 'jspdf';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Validation schema for contact form
const contactSchema = yup.object({
  name: yup.string().required('Le nom est requis'),
  email: yup.string().email('Email invalide').required('L\'email est requis'),
  company: yup.string(),
  phone: yup.string(),
  message: yup.string()
});

const Calculator = () => {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    projectType: '',
    complexity: '',
    timeline: '',
    teamSize: '',
    budget: '',
    features: [],
    companySize: '',
    industry: '',
    urgency: '',
    maintenance: false,
    training: false,
    documentation: false
  });

  const [quote, setQuote] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [showContactForm, setShowContactForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionSuccess, setSubmissionSuccess] = useState(false);

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    resolver: yupResolver(contactSchema)
  });

  const projectTypes = [
    { id: 'audit', name: 'Audit de sécurité', icon: Shield, basePrice: 1500 },
    { id: 'development', name: 'Développement Python', icon: Code, basePrice: 500 },
    { id: 'infrastructure', name: 'Infrastructure sécurisée', icon: Server, basePrice: 800 },
    { id: 'consulting', name: 'Consulting & Formation', icon: Users, basePrice: 600 }
  ];

  const complexityLevels = [
    { id: 'simple', name: 'Simple', multiplier: 1 },
    { id: 'moderate', name: 'Modéré', multiplier: 1.5 },
    { id: 'complex', name: 'Complexe', multiplier: 2 },
    { id: 'enterprise', name: 'Entreprise', multiplier: 2.5 }
  ];

  const timelineOptions = [
    { id: 'rush', name: 'Urgent (< 1 semaine)', multiplier: 1.5 },
    { id: 'normal', name: 'Normal (1-4 semaines)', multiplier: 1 },
    { id: 'flexible', name: 'Flexible (> 1 mois)', multiplier: 0.9 }
  ];

  const features = [
    { id: 'api', name: 'API Integration', price: 300 },
    { id: 'dashboard', name: 'Dashboard personnalisé', price: 800 },
    { id: 'mobile', name: 'Application mobile', price: 1200 },
    { id: 'automation', name: 'Automatisation avancée', price: 600 },
    { id: 'monitoring', name: 'Monitoring temps réel', price: 500 },
    { id: 'reporting', name: 'Rapports détaillés', price: 400 }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFeatureToggle = (featureId) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.includes(featureId)
        ? prev.features.filter(f => f !== featureId)
        : [...prev.features, featureId]
    }));
  };

  const calculateQuote = () => {
    setIsCalculating(true);
    
    setTimeout(() => {
      const projectType = projectTypes.find(p => p.id === formData.projectType);
      const complexity = complexityLevels.find(c => c.id === formData.complexity);
      const timeline = timelineOptions.find(t => t.id === formData.timeline);
      
      if (!projectType || !complexity || !timeline) {
        setIsCalculating(false);
        return;
      }

      let basePrice = projectType.basePrice;
      
      // Apply multipliers
      basePrice *= complexity.multiplier;
      basePrice *= timeline.multiplier;
      
      // Add features
      const featuresPrice = formData.features.reduce((total, featureId) => {
        const feature = features.find(f => f.id === featureId);
        return total + (feature ? feature.price : 0);
      }, 0);
      
      // Add extras
      let extrasPrice = 0;
      if (formData.maintenance) extrasPrice += basePrice * 0.15;
      if (formData.training) extrasPrice += 500;
      if (formData.documentation) extrasPrice += 300;
      
      const totalPrice = basePrice + featuresPrice + extrasPrice;
      const minPrice = Math.round(totalPrice * 0.9);
      const maxPrice = Math.round(totalPrice * 1.1);
      
      setQuote({
        projectType: projectType.name,
        complexity: complexity.name,
        timeline: timeline.name,
        basePrice,
        featuresPrice,
        extrasPrice,
        totalPrice,
        minPrice,
        maxPrice,
        features: formData.features.map(fId => features.find(f => f.id === fId)),
        hasExtras: formData.maintenance || formData.training || formData.documentation
      });
      
      setIsCalculating(false);
    }, 1500);
  };

  const generatePDF = () => {
    if (!quote) return;

    const doc = new jsPDF();
    
    // Header
    doc.setFontSize(20);
    doc.setTextColor(40, 40, 40);
    doc.text('DEVIS CYBERSÉCURITÉ', 105, 20, { align: 'center' });
    
    // Company info
    doc.setFontSize(12);
    doc.setTextColor(100, 100, 100);
    doc.text('Jean Yves - Spécialiste Cybersécurité & Python', 105, 30, { align: 'center' });
    doc.text('contact@jeanyves.dev | +33 6 12 34 56 78', 105, 40, { align: 'center' });
    
    // Date
    doc.setFontSize(10);
    doc.text(`Date: ${new Date().toLocaleDateString('fr-FR')}`, 20, 60);
    doc.text(`Référence: DEV-${Date.now()}`, 20, 70);
    
    // Project details
    doc.setFontSize(16);
    doc.setTextColor(40, 40, 40);
    doc.text('DÉTAILS DU PROJET', 20, 90);
    
    doc.setFontSize(11);
    doc.setTextColor(60, 60, 60);
    let yPos = 105;
    
    doc.text(`Type de projet: ${quote.projectType}`, 20, yPos);
    yPos += 10;
    doc.text(`Complexité: ${quote.complexity}`, 20, yPos);
    yPos += 10;
    doc.text(`Délais: ${quote.timeline}`, 20, yPos);
    yPos += 15;
    
    // Features
    if (quote.features.length > 0) {
      doc.text('Fonctionnalités incluses:', 20, yPos);
      yPos += 10;
      quote.features.forEach(feature => {
        doc.text(`• ${feature.name}`, 25, yPos);
        yPos += 8;
      });
      yPos += 5;
    }
    
    // Pricing
    doc.setFontSize(16);
    doc.setTextColor(40, 40, 40);
    doc.text('TARIFICATION', 20, yPos);
    yPos += 15;
    
    doc.setFontSize(11);
    doc.setTextColor(60, 60, 60);
    doc.text(`Prix de base: ${Math.round(quote.basePrice)}€`, 20, yPos);
    yPos += 10;
    
    if (quote.featuresPrice > 0) {
      doc.text(`Fonctionnalités supplémentaires: +${quote.featuresPrice}€`, 20, yPos);
      yPos += 10;
    }
    
    if (quote.extrasPrice > 0) {
      doc.text(`Services supplémentaires: +${Math.round(quote.extrasPrice)}€`, 20, yPos);
      yPos += 10;
    }
    
    // Total
    doc.setFontSize(14);
    doc.setTextColor(34, 197, 94);
    doc.text(`FOURCHETTE DE PRIX: ${quote.minPrice}€ - ${quote.maxPrice}€`, 20, yPos + 15);
    
    // Footer
    doc.setFontSize(9);
    doc.setTextColor(120, 120, 120);
    doc.text('Ce devis est valable 30 jours. TVA non applicable (auto-entrepreneur).', 20, 270);
    doc.text('Pour toute question, contactez-nous à contact@jeanyves.dev', 20, 280);
    
    // Save
    doc.save(`devis-cybersecurite-${Date.now()}.pdf`);
  };

  const saveQuoteToBackend = async (contactData = null) => {
    if (!quote) return null;

    const quoteData = {
      quote_data: {
        project_type: formData.projectType,
        complexity: formData.complexity,
        timeline: formData.timeline,
        features: formData.features,
        maintenance: formData.maintenance,
        training: formData.training,
        documentation: formData.documentation,
        base_price: quote.basePrice,
        features_price: quote.featuresPrice,
        extras_price: quote.extrasPrice,
        total_price: quote.totalPrice,
        min_price: quote.minPrice,
        max_price: quote.maxPrice
      },
      contact_info: contactData
    };

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/quotes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(quoteData),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la sauvegarde');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
      return null;
    }
  };

  const onSubmitContact = async (data) => {
    setIsSubmitting(true);
    
    try {
      const savedQuote = await saveQuoteToBackend(data);
      
      if (savedQuote) {
        setSubmissionSuccess(true);
        reset();
        setShowContactForm(false);
        
        // Generate and download PDF automatically
        generatePDF();
        
        setTimeout(() => {
          setSubmissionSuccess(false);
        }, 5000);
      } else {
        alert('Erreur lors de l\'envoi. Veuillez réessayer.');
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de l\'envoi. Veuillez réessayer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <CalcIcon size={32} className="text-gray-900" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Calculateur de <span className="text-green-400">Prix</span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              Obtenez une estimation instantanée pour votre projet de cybersécurité
            </p>
          </div>
        </div>
      </section>

      {/* Calculator Form */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12">
              {/* Form */}
              <div className="space-y-8">
                {/* Project Type */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-white mb-4">Type de projet</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {projectTypes.map(type => {
                      const Icon = type.icon;
                      return (
                        <button
                          key={type.id}
                          onClick={() => handleInputChange('projectType', type.id)}
                          className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                            formData.projectType === type.id
                              ? 'border-green-400 bg-green-400/10'
                              : 'border-gray-600 hover:border-gray-500'
                          }`}
                        >
                          <Icon size={24} className={`mx-auto mb-2 ${
                            formData.projectType === type.id ? 'text-green-400' : 'text-gray-400'
                          }`} />
                          <div className="text-sm font-medium text-white">{type.name}</div>
                          <div className="text-xs text-gray-400">À partir de {type.basePrice}€</div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Complexity */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-white mb-4">Complexité</h3>
                  <div className="space-y-3">
                    {complexityLevels.map(level => (
                      <button
                        key={level.id}
                        onClick={() => handleInputChange('complexity', level.id)}
                        className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                          formData.complexity === level.id
                            ? 'border-green-400 bg-green-400/10'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-white">{level.name}</span>
                          <span className="text-sm text-gray-400">×{level.multiplier}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Timeline */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-white mb-4">Délais</h3>
                  <div className="space-y-3">
                    {timelineOptions.map(option => (
                      <button
                        key={option.id}
                        onClick={() => handleInputChange('timeline', option.id)}
                        className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                          formData.timeline === option.id
                            ? 'border-green-400 bg-green-400/10'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-white">{option.name}</span>
                          <span className="text-sm text-gray-400">×{option.multiplier}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Features */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-white mb-4">Fonctionnalités supplémentaires</h3>
                  <div className="space-y-3">
                    {features.map(feature => (
                      <button
                        key={feature.id}
                        onClick={() => handleFeatureToggle(feature.id)}
                        className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                          formData.features.includes(feature.id)
                            ? 'border-green-400 bg-green-400/10'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                              formData.features.includes(feature.id)
                                ? 'border-green-400 bg-green-400'
                                : 'border-gray-400'
                            }`}>
                              {formData.features.includes(feature.id) && (
                                <Check size={12} className="text-gray-900" />
                              )}
                            </div>
                            <span className="font-medium text-white">{feature.name}</span>
                          </div>
                          <span className="text-sm text-gray-400">+{feature.price}€</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Extras */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-white mb-4">Services supplémentaires</h3>
                  <div className="space-y-3">
                    <button
                      onClick={() => handleInputChange('maintenance', !formData.maintenance)}
                      className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                        formData.maintenance
                          ? 'border-green-400 bg-green-400/10'
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-white">Maintenance (6 mois)</span>
                        <span className="text-sm text-gray-400">+15%</span>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => handleInputChange('training', !formData.training)}
                      className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                        formData.training
                          ? 'border-green-400 bg-green-400/10'
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-white">Formation équipe</span>
                        <span className="text-sm text-gray-400">+500€</span>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => handleInputChange('documentation', !formData.documentation)}
                      className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                        formData.documentation
                          ? 'border-green-400 bg-green-400/10'
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-white">Documentation complète</span>
                        <span className="text-sm text-gray-400">+300€</span>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Calculate Button */}
                <button
                  onClick={calculateQuote}
                  disabled={!formData.projectType || !formData.complexity || !formData.timeline || isCalculating}
                  className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
                >
                  {isCalculating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
                      Calcul en cours...
                    </>
                  ) : (
                    <>
                      <CalcIcon size={20} />
                      Calculer le devis
                    </>
                  )}
                </button>
              </div>

              {/* Quote Result */}
              <div className="space-y-6">
                {quote ? (
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                    <h3 className="text-2xl font-bold text-white mb-6">Estimation de prix</h3>
                    
                    <div className="space-y-4 mb-6">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Type de projet:</span>
                        <span className="text-white font-medium">{quote.projectType}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Complexité:</span>
                        <span className="text-white font-medium">{quote.complexity}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Délais:</span>
                        <span className="text-white font-medium">{quote.timeline}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-3 mb-6 border-t border-gray-700 pt-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Prix de base:</span>
                        <span className="text-white">{Math.round(quote.basePrice)}€</span>
                      </div>
                      {quote.featuresPrice > 0 && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-300">Fonctionnalités:</span>
                          <span className="text-white">+{quote.featuresPrice}€</span>
                        </div>
                      )}
                      {quote.extrasPrice > 0 && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-300">Services supplémentaires:</span>
                          <span className="text-white">+{Math.round(quote.extrasPrice)}€</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="bg-green-400/10 border border-green-400 rounded-lg p-4 mb-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-400 mb-2">
                          {quote.minPrice}€ - {quote.maxPrice}€
                        </div>
                        <div className="text-green-300 text-sm">
                          Fourchette de prix estimée
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-4">
                      <button
                        onClick={generatePDF}
                        className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        <Download size={16} />
                        Télécharger PDF
                      </button>
                      <button 
                        onClick={() => setShowContactForm(true)}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        <FileText size={16} />
                        Demander devis
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 text-center">
                    <CalcIcon size={48} className="text-gray-500 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-gray-300 mb-2">Estimation instantanée</h3>
                    <p className="text-gray-500">
                      Complétez le formulaire pour obtenir une estimation de prix personnalisée
                    </p>
                  </div>
                )}

                {/* Success Message */}
                {submissionSuccess && (
                  <div className="bg-green-600/20 border border-green-500 rounded-2xl p-6 text-center">
                    <Check size={48} className="text-green-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-green-300 mb-2">Devis envoyé !</h3>
                    <p className="text-green-200">
                      Votre demande a été envoyée avec succès. Nous vous recontacterons sous 24h.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Form Modal */}
      {showContactForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl p-8 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold text-white mb-6 text-center">
              Finaliser votre demande
            </h3>
            
            <form onSubmit={handleSubmit(onSubmitContact)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <User size={16} className="inline mr-2" />
                  Nom complet *
                </label>
                <input
                  {...register('name')}
                  type="text"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-green-400 focus:outline-none"
                  placeholder="Votre nom"
                />
                {errors.name && (
                  <p className="text-red-400 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Mail size={16} className="inline mr-2" />
                  Email *
                </label>
                <input
                  {...register('email')}
                  type="email"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-green-400 focus:outline-none"
                  placeholder="votre@email.com"
                />
                {errors.email && (
                  <p className="text-red-400 text-sm mt-1">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Building size={16} className="inline mr-2" />
                  Entreprise
                </label>
                <input
                  {...register('company')}
                  type="text"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-green-400 focus:outline-none"
                  placeholder="Nom de votre entreprise"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Phone size={16} className="inline mr-2" />
                  Téléphone
                </label>
                <input
                  {...register('phone')}
                  type="tel"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-green-400 focus:outline-none"
                  placeholder="+33 6 12 34 56 78"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <MessageSquare size={16} className="inline mr-2" />
                  Message
                </label>
                <textarea
                  {...register('message')}
                  rows={4}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-green-400 focus:outline-none resize-none"
                  placeholder="Détails supplémentaires sur votre projet..."
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowContactForm(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-500 text-white px-4 py-3 rounded-lg font-medium transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Envoi...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Envoyer le devis
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calculator;