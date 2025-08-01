import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Sun, Moon, Globe } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import Logo from './Logo';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const { theme, toggleTheme, isDark } = useTheme();
  const { language, toggleLanguage, t, isFrench } = useLanguage();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const navigation = [
    { name: t('home'), href: "/" },
    { name: t('about'), href: "/about" },
    { name: t('skills'), href: "/skills" },
    { name: t('projects'), href: "/projects" },
    { name: t('tools'), href: "/tools" },
    { name: t('services'), href: "/services" },
    { name: t('contact'), href: "/contact" }
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-md border-b border-gray-800">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="hover:opacity-80 transition-opacity">
            <Logo variant="minimal" size="md" />
          </Link>

          {/* Navigation Desktop */}
          <nav className="hidden md:flex items-center space-x-8">
            {navigation.map((item, index) => (
              <Link
                key={index}
                to={item.href}
                className={`text-sm font-medium transition-colors duration-200 hover:text-green-400 relative ${
                  isActive(item.href) 
                    ? 'text-green-400' 
                    : 'text-gray-300'
                }`}
              >
                {item.name}
                {isActive(item.href) && (
                  <div className="absolute -bottom-1 left-0 w-full h-0.5 bg-green-400 rounded-full"></div>
                )}
              </Link>
            ))}
          </nav>

          {/* Controls */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-300 hover:text-white"
              title={isDark ? "Mode clair" : "Mode sombre"}
            >
              {isDark ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1 p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-300 hover:text-white"
              title={isFrench ? "Switch to English" : "Passer en français"}
            >
              <Globe size={16} />
              <span className="text-sm font-medium">{language.toUpperCase()}</span>
            </button>

            {/* CTA Button */}
            <Link
              to="/contact"
              className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-2 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 transform hover:scale-105"
            >
              {t('requestQuote')}
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 py-4 border-t border-gray-800">
            <nav className="flex flex-col space-y-4">
              {navigation.map((item, index) => (
                <Link
                  key={index}
                  to={item.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={`text-left text-sm font-medium transition-colors duration-200 hover:text-green-400 ${
                    isActive(item.href) 
                      ? 'text-green-400' 
                      : 'text-gray-300'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
              
              {/* Mobile Controls */}
              <div className="flex items-center gap-4 pt-4 border-t border-gray-800">
                <button
                  onClick={toggleTheme}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-300 hover:text-white"
                >
                  {isDark ? <Sun size={16} /> : <Moon size={16} />}
                  <span className="text-sm">{isDark ? "Mode clair" : "Mode sombre"}</span>
                </button>

                <button
                  onClick={toggleLanguage}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-800 transition-colors text-gray-300 hover:text-white"
                >
                  <Globe size={16} />
                  <span className="text-sm">{language.toUpperCase()}</span>
                </button>
              </div>

              <Link
                to="/contact"
                onClick={() => setIsMenuOpen(false)}
                className="mt-4 bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-2 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 text-center inline-block"
              >
                {t('requestQuote')}
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;