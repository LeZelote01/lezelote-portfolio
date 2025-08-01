import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin, ArrowUp, Heart, Linkedin, Github, Twitter } from 'lucide-react';
import usePersonalInfo from '../hooks/usePersonalInfo';
import useSocialLinks from '../hooks/useSocialLinks';
import LoadingSpinner from './LoadingSpinner';
import { useLanguage } from '../context/LanguageContext';

const Footer = () => {
  const { personalInfo, loading: personalLoading } = usePersonalInfo();
  const { socialLinks, loading: socialLoading } = useSocialLinks();
  const { t } = useLanguage();

  if (personalLoading || socialLoading) {
    return <LoadingSpinner />;
  }

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getSocialIcon = (name) => {
    const icons = {
      LinkedIn: Linkedin,
      GitHub: Github,
      Twitter: Twitter
    };
    return icons[name] || Mail;
  };

  const navigationItems = [
    { name: t('home'), href: '/' },
    { name: t('about'), href: '/about' },
    { name: t('skills'), href: '/skills' },
    { name: t('projects'), href: '/projects' },
    { name: t('services'), href: '/services' },
    { name: t('contact'), href: '/contact' }
  ];

  const serviceItems = [
    { name: t('securityAudit'), href: '/services' },
    { name: t('pythonDevelopment'), href: '/services' },
    { name: t('secureInfrastructure'), href: '/services' },
    { name: t('consultingTraining'), href: '/services' }
  ];

  return (
    <footer className="bg-gray-900 border-t border-gray-800">
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Main Footer Content */}
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            {/* Brand & Description */}
            <div className="md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                  <span className="text-gray-900 font-bold text-sm">JY</span>
                </div>
                <span className="text-xl font-bold text-white">Jean Yves</span>
              </div>
              <p className="text-gray-400 leading-relaxed mb-6 max-w-md">
                {t('footerDescription')}
              </p>
              
              {/* Contact Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-gray-400">
                  <Mail size={16} className="text-green-400" />
                  <span>{personalInfo?.email || 'contact@jeanyves.dev'}</span>
                </div>
                <div className="flex items-center gap-3 text-gray-400">
                  <Phone size={16} className="text-green-400" />
                  <span>{personalInfo?.phone || '+33 6 12 34 56 78'}</span>
                </div>
                <div className="flex items-center gap-3 text-gray-400">
                  <MapPin size={16} className="text-green-400" />
                  <span>{personalInfo?.location || 'Paris, France'}</span>
                </div>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">{t('navigation')}</h3>
              <ul className="space-y-2">
                {navigationItems.map((item, index) => (
                  <li key={index}>
                    <Link
                      to={item.href}
                      className="text-gray-400 hover:text-green-400 transition-colors duration-200"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Services */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">{t('services')}</h3>
              <ul className="space-y-2">
                {serviceItems.map((item, index) => (
                  <li key={index}>
                    <Link
                      to={item.href}
                      className="text-gray-400 hover:text-green-400 transition-colors duration-200"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Social Media & Newsletter */}
          <div className="border-t border-gray-800 pt-8 mb-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              {/* Social Links */}
              <div className="flex items-center gap-4">
                <span className="text-gray-400">{t('followMe')} :</span>
                <div className="flex gap-3">
                  {socialLinks.map((social, index) => {
                    const SocialIcon = getSocialIcon(social.name);
                    return (
                      <a
                        key={index}
                        href={social.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-gray-800 hover:bg-gradient-to-br hover:from-green-400 hover:to-cyan-400 rounded-lg flex items-center justify-center transition-all duration-200 group"
                      >
                        <SocialIcon size={18} className="text-gray-300 group-hover:text-gray-900" />
                      </a>
                    );
                  })}
                </div>
              </div>

              {/* Back to Top */}
              <button
                onClick={scrollToTop}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg transition-all duration-200 group"
              >
                <ArrowUp size={16} className="group-hover:transform group-hover:-translate-y-1 transition-transform" />
                {t('backToTop')}
              </button>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-800 pt-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-2 text-gray-400">
                <span>© 2024 Jean Yves. {t('allRightsReserved')}.</span>
              </div>
              
              <div className="flex items-center gap-1 text-gray-400">
                <span>{t('createdWith')}</span>
                <Heart size={16} className="text-red-500 animate-pulse" />
                <span>{t('andCoffee')}</span>
              </div>
            </div>
          </div>

          {/* Skills Tags */}
          <div className="mt-8 pt-6 border-t border-gray-800">
            <div className="flex flex-wrap gap-2 justify-center">
              {t('skillsTags').map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-800 text-gray-400 rounded-full text-sm hover:bg-gray-700 hover:text-green-400 transition-all duration-200 cursor-default"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;