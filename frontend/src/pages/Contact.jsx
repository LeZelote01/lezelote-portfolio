import React, { useState } from 'react';
import { Mail, Phone, MapPin, Send, Linkedin, Github, Twitter, Clock, Check, MessageCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import usePersonalInfo from '../hooks/usePersonalInfo';
import useSocialLinks from '../hooks/useSocialLinks';
import LoadingSpinner from '../components/LoadingSpinner';
import TestimonialForm from '../components/TestimonialForm';

const Contact = () => {
  const { t, td } = useLanguage();
  const { personalInfo, loading: personalLoading } = usePersonalInfo();
  const { socialLinks, loading: socialLoading } = useSocialLinks();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    service: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  if (personalLoading || socialLoading) {
    return <LoadingSpinner />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'envoi du message');
      }

      const data = await response.json();
      
      setIsSubmitted(true);
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: '',
        service: ''
      });
      
      // Reset success message after 5 seconds
      setTimeout(() => {
        setIsSubmitted(false);
      }, 5000);
      
    } catch (error) {
      console.error('Erreur:', error);
      alert('Une erreur est survenue lors de l\'envoi du message. Veuillez réessayer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const getSocialIcon = (name) => {
    const icons = {
      LinkedIn: Linkedin,
      GitHub: Github,
      Twitter: Twitter
    };
    return icons[name] || Mail;
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {t('contactMe')}
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              {t('contactSubtitle')}
            </p>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12">
              {/* Contact Info */}
              <div className="space-y-8">
                {/* Contact Details */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h2 className="text-3xl font-bold text-white mb-6">
                    {t('contactInfo')}
                  </h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                        <Mail size={24} className="text-gray-900" />
                      </div>
                      <div>
                        <h4 className="text-white font-semibold">{t('email')}</h4>
                        <p className="text-gray-300">{personalInfo?.email || 'contact@jeanyves.dev'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                        <Phone size={24} className="text-gray-900" />
                      </div>
                      <div>
                        <h4 className="text-white font-semibold">{t('phone')}</h4>
                        <p className="text-gray-300">{personalInfo?.phone || '+33 6 12 34 56 78'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                        <MapPin size={24} className="text-gray-900" />
                      </div>
                      <div>
                        <h4 className="text-white font-semibold">{t('location')}</h4>
                        <p className="text-gray-300">{personalInfo?.location || 'Paris, France'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                        <Clock size={24} className="text-gray-900" />
                      </div>
                      <div>
                        <h4 className="text-white font-semibold">{t('availability')}</h4>
                        <p className="text-gray-300">{personalInfo?.availability || 'Disponible pour missions freelance'}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Social Links */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-6">
                    {t('socialNetworks')}
                  </h3>
                  
                  <div className="flex gap-4">
                    {socialLinks.map((social, index) => {
                      const SocialIcon = getSocialIcon(social.name);
                      return (
                        <a
                          key={index}
                          href={social.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-12 h-12 bg-gray-700 hover:bg-gradient-to-br hover:from-green-400 hover:to-cyan-400 rounded-lg flex items-center justify-center transition-all duration-200 group"
                        >
                          <SocialIcon size={20} className="text-gray-300 group-hover:text-gray-900" />
                        </a>
                      );
                    })}
                  </div>
                </div>

                {/* Quick Response */}
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <MessageCircle size={24} />
                    {t('quickResponse')}
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Check size={16} className="text-green-400" />
                      <span className="text-gray-300">{t('responseWithin24h')}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Check size={16} className="text-green-400" />
                      <span className="text-gray-300">{t('freeQuoteNoCommitment')}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Check size={16} className="text-green-400" />
                      <span className="text-gray-300">{t('freeInitialConsultation')}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Check size={16} className="text-green-400" />
                      <span className="text-gray-300">{t('technicalSupportIncluded')}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Contact Form */}
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h3 className="text-3xl font-bold text-white mb-6">
                  {t('sendMessage')}
                </h3>

                {isSubmitted && (
                  <div className="mb-6 p-4 bg-green-500/20 border border-green-500 rounded-lg flex items-center gap-3">
                    <Check size={20} className="text-green-400" />
                    <span className="text-green-400">
                      {t('messageSentSuccess')}
                    </span>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                        {t('fullName')} *
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent transition-all duration-200"
                        placeholder={t('yourName')}
                      />
                    </div>
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                        {t('email')} *
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent transition-all duration-200"
                        placeholder={t('yourEmail')}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="service" className="block text-sm font-medium text-gray-300 mb-2">
                      {t('serviceOfInterest')}
                    </label>
                    <select
                      id="service"
                      name="service"
                      value={formData.service}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">{t('selectService')}</option>
                      <option value="audit">{t('securityAudit')}</option>
                      <option value="development">{t('pythonDevelopment')}</option>
                      <option value="infrastructure">{t('infrastructureSecurity')}</option>
                      <option value="consulting">{t('consultingTraining')}</option>
                      <option value="other">{t('other')}</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-gray-300 mb-2">
                      {t('subject')} *
                    </label>
                    <input
                      type="text"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent transition-all duration-200"
                      placeholder={t('subjectOfMessage')}
                    />
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2">
                      {t('message')} *
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows={6}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent resize-none transition-all duration-200"
                      placeholder={t('describeProject')}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
                        {t('sendingMessage')}
                      </>
                    ) : (
                      <>
                        <Send size={20} />
                        {t('sendMessageBtn')}
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t('shareExperience')}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              {t('helpOthers')}
            </p>
          </div>
          
          <TestimonialForm />
        </div>
      </section>
    </div>
  );
};

export default Contact;