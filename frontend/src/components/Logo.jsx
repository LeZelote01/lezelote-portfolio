import React from 'react';
import { Shield, Lock, Code } from 'lucide-react';

const Logo = ({ variant = 'full', size = 'md', className = '' }) => {
  const sizes = {
    sm: { container: 'h-8', text: 'text-lg', icon: 16 },
    md: { container: 'h-10', text: 'text-xl', icon: 18 },
    lg: { container: 'h-12', text: 'text-2xl', icon: 20 },
    xl: { container: 'h-16', text: 'text-3xl', icon: 24 }
  };

  const currentSize = sizes[size];

  if (variant === 'icon') {
    return (
      <div className={`${currentSize.container} aspect-square bg-gradient-to-br from-green-400 via-cyan-400 to-green-500 rounded-lg flex items-center justify-center shadow-lg ${className}`}>
        <div className="relative flex items-center justify-center w-full h-full">
          {/* Central JY */}
          <span className="text-gray-900 font-black text-sm z-10">JY</span>
          
          {/* Security Icons Overlay */}
          <div className="absolute inset-0 flex items-center justify-center opacity-20">
            <Shield className="w-6 h-6 text-gray-900" />
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'minimal') {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className={`${currentSize.container} aspect-square bg-gradient-to-br from-green-400 via-cyan-400 to-green-500 rounded-lg flex items-center justify-center shadow-lg`}>
          <span className="text-gray-900 font-black text-sm">JY</span>
        </div>
        <span className={`${currentSize.text} font-bold text-white`}>Jean Yves</span>
      </div>
    );
  }

  // Full logo variant
  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Logo Icon avec symboles cybersécurité */}
      <div className="relative">
        <div className={`${currentSize.container} aspect-square bg-gradient-to-br from-green-400 via-cyan-400 to-green-500 rounded-lg flex items-center justify-center shadow-lg border border-green-300/30`}>
          {/* Central JY */}
          <span className="text-gray-900 font-black text-sm z-10">JY</span>
        </div>
        
        {/* Floating Security Symbols */}
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-gray-800 rounded-full flex items-center justify-center border border-green-400/50">
          <Lock className="w-2.5 h-2.5 text-green-400" />
        </div>
        <div className="absolute -bottom-1 -left-1 w-4 h-4 bg-gray-800 rounded-full flex items-center justify-center border border-cyan-400/50">
          <Code className="w-2.5 h-2.5 text-cyan-400" />
        </div>
        <div className="absolute top-0 -left-2 w-4 h-4 bg-gray-800 rounded-full flex items-center justify-center border border-green-400/50">
          <Shield className="w-2.5 h-2.5 text-green-400" />
        </div>
      </div>

      {/* Texte */}
      <div className="flex flex-col">
        <span className={`${currentSize.text} font-bold text-white leading-tight`}>Jean Yves</span>
        <span className="text-xs text-green-400 font-medium tracking-wide">Cybersécurité & Python</span>
      </div>
    </div>
  );
};

// Alternative logo avec symboles intégrés
export const LogoSymbolic = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: { container: 'h-8 w-20', text: 'text-xs' },
    md: { container: 'h-10 w-24', text: 'text-sm' },
    lg: { container: 'h-12 w-28', text: 'text-base' },
    xl: { container: 'h-16 w-32', text: 'text-lg' }
  };

  const currentSize = sizes[size];

  return (
    <div className={`${currentSize.container} bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 rounded-lg border border-gray-700 flex items-center justify-center px-2 ${className}`}>
      <div className="flex items-center space-x-1 text-green-400">
        <span className="text-white font-mono font-bold">[JY]</span>
        <span className="text-yellow-400">+</span>
        <Lock className="w-3 h-3" />
        <span className="text-yellow-400">+</span>
        <Code className="w-3 h-3" />
        <span className="text-yellow-400">+</span>
        <Shield className="w-3 h-3" />
      </div>
    </div>
  );
};

// Logo animé pour le loading
export const LogoAnimated = ({ size = 'lg', className = '' }) => {
  return (
    <div className={`flex flex-col items-center space-y-2 ${className}`}>
      <div className="relative">
        <div className="w-16 h-16 bg-gradient-to-br from-green-400 via-cyan-400 to-green-500 rounded-2xl flex items-center justify-center shadow-2xl animate-pulse">
          <span className="text-gray-900 font-black text-lg">JY</span>
        </div>
        
        {/* Orbiting Security Icons */}
        <div className="absolute inset-0 animate-spin" style={{ animationDuration: '3s' }}>
          <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
            <Lock className="w-4 h-4 text-green-400" />
          </div>
          <div className="absolute top-1/2 -right-2 transform -translate-y-1/2">
            <Code className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
            <Shield className="w-4 h-4 text-green-400" />
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <div className="text-green-400 text-lg font-semibold">Jean Yves</div>
        <div className="text-gray-400 text-sm">Cybersécurité & Python</div>
      </div>
    </div>
  );
};

export default Logo;