import React from 'react';

export const Alert = ({ children, className = "", ...props }) => (
  <div 
    className={`relative w-full rounded-lg border p-4 ${className}`}
    {...props}
  >
    {children}
  </div>
);

export const AlertDescription = ({ children, className = "", ...props }) => (
  <div className={`text-sm ${className}`} {...props}>
    {children}
  </div>
);