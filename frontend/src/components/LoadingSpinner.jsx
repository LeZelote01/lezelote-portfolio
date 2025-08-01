import React from 'react';
import { Activity } from 'lucide-react';

const LoadingSpinner = ({ message = "Chargement..." }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 min-h-screen bg-gray-900">
      <Activity className="h-8 w-8 animate-spin text-green-400 mb-4" />
      <p className="text-gray-300">{message}</p>
    </div>
  );
};

export default LoadingSpinner;