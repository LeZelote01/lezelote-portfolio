import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Calendar, Clock, User, Mail, Phone, MessageSquare, Check, ChevronLeft, ChevronRight } from 'lucide-react';

const Booking = () => {
  const { t } = useLanguage();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedService, setSelectedService] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isBooked, setIsBooked] = useState(false);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingAvailability, setLoadingAvailability] = useState(false);

  const services = [
    {
      id: 'audit',
      name: 'Audit de sécurité',
      duration: '1h',
      description: 'Consultation pour évaluer vos besoins en audit de sécurité',
      price: 'Gratuit'
    },
    {
      id: 'consulting',
      name: 'Consultation cybersécurité',
      duration: '45min',
      description: 'Discussion sur vos défis de sécurité et solutions possibles',
      price: 'Gratuit'
    },
    {
      id: 'development',
      name: 'Projet de développement',
      duration: '1h',
      description: 'Évaluation de votre projet de développement Python',
      price: 'Gratuit'
    },
    {
      id: 'training',
      name: 'Formation équipe',
      duration: '30min',
      description: 'Présentation de nos formations en cybersécurité',
      price: 'Gratuit'
    }
  ];

  // Load available slots when date is selected
  const loadAvailability = async (dateStr) => {
    setLoadingAvailability(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/bookings/availability/${dateStr}`);
      
      if (response.ok) {
        const data = await response.json();
        setAvailableSlots(data.available_slots);
      } else {
        // Fallback to default slots if API fails
        setAvailableSlots([
          '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
          '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
        ]);
      }
    } catch (error) {
      console.error('Error loading availability:', error);
      // Fallback to default slots
      setAvailableSlots([
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
      ]);
    } finally {
      setLoadingAvailability(false);
    }
  };

  const timeSlots = availableSlots;

  const generateCalendar = () => {
    const today = new Date();
    const dates = [];
    
    for (let i = 1; i <= 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      
      // Skip weekends
      if (date.getDay() !== 0 && date.getDay() !== 6) {
        dates.push(date);
      }
    }
    
    return dates;
  };

  const availableDates = generateCalendar();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const selectedServiceData = services.find(s => s.id === selectedService);
      
      const bookingData = {
        booking_data: {
          service_id: selectedService,
          service_name: selectedServiceData.name,
          date: selectedDate,
          time: selectedTime,
          duration: selectedServiceData.duration
        },
        contact_info: {
          name: formData.name,
          email: formData.email,
          phone: formData.phone || null,
          company: formData.company || null,
          message: formData.message || null
        }
      };

      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/bookings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData),
      });

      if (response.ok) {
        const booking = await response.json();
        console.log('Booking created:', booking);
        setIsBooked(true);
      } else {
        alert('Erreur lors de la réservation. Veuillez réessayer.');
      }
    } catch (error) {
      console.error('Error creating booking:', error);
      alert('Erreur lors de la réservation. Veuillez réessayer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDateShort = (date) => {
    return date.toLocaleDateString('fr-FR', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    });
  };

  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return selectedService !== '';
      case 2:
        return selectedDate !== '' && selectedTime !== '';
      case 3:
        return formData.name && formData.email;
      default:
        return false;
    }
  };

  if (isBooked) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
              <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <Check size={32} className="text-white" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-4">
                Rendez-vous confirmé !
              </h1>
              <p className="text-gray-300 mb-6">
                Votre rendez-vous a été programmé avec succès. Vous recevrez un email de confirmation avec le lien de visioconférence.
              </p>
              
              <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6 mb-6 text-left">
                <h3 className="text-lg font-semibold text-white mb-4">Détails du rendez-vous</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <User size={16} className="text-green-400" />
                    <span className="text-gray-300">Service: {services.find(s => s.id === selectedService)?.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Calendar size={16} className="text-green-400" />
                    <span className="text-gray-300">Date: {formatDate(new Date(selectedDate))}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock size={16} className="text-green-400" />
                    <span className="text-gray-300">Heure: {selectedTime}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail size={16} className="text-green-400" />
                    <span className="text-gray-300">Email: {formData.email}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => {
                    setCurrentStep(1);
                    setSelectedService('');
                    setSelectedDate('');
                    setSelectedTime('');
                    setFormData({ name: '', email: '', phone: '', company: '', message: '' });
                    setIsBooked(false);
                  }}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Nouveau rendez-vous
                </button>
                <button
                  onClick={() => window.location.href = '/'}
                  className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200"
                >
                  Retour à l'accueil
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Prendre <span className="text-green-400">rendez-vous</span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              Programmez une consultation gratuite pour discuter de vos besoins
            </p>
          </div>
        </div>
      </section>

      {/* Booking Process */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            {/* Progress Bar */}
            <div className="mb-12">
              <div className="flex items-center justify-between mb-4">
                <div className={`flex items-center gap-2 ${currentStep >= 1 ? 'text-green-400' : 'text-gray-500'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 1 ? 'bg-green-400 text-gray-900' : 'bg-gray-700 text-gray-300'}`}>
                    1
                  </div>
                  <span className="text-sm font-medium">Service</span>
                </div>
                <div className={`flex items-center gap-2 ${currentStep >= 2 ? 'text-green-400' : 'text-gray-500'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 2 ? 'bg-green-400 text-gray-900' : 'bg-gray-700 text-gray-300'}`}>
                    2
                  </div>
                  <span className="text-sm font-medium">Date & Heure</span>
                </div>
                <div className={`flex items-center gap-2 ${currentStep >= 3 ? 'text-green-400' : 'text-gray-500'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 3 ? 'bg-green-400 text-gray-900' : 'bg-gray-700 text-gray-300'}`}>
                    3
                  </div>
                  <span className="text-sm font-medium">Informations</span>
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-400 to-cyan-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(currentStep / 3) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Step 1: Service Selection */}
            {currentStep === 1 && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6">
                  Choisissez le type de consultation
                </h2>
                <div className="grid gap-4">
                  {services.map(service => (
                    <button
                      key={service.id}
                      onClick={() => setSelectedService(service.id)}
                      className={`p-6 rounded-lg border-2 transition-all duration-200 text-left ${
                        selectedService === service.id
                          ? 'border-green-400 bg-green-400/10'
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xl font-bold text-white">{service.name}</h3>
                        <div className="flex items-center gap-4">
                          <span className="text-green-400 font-semibold">{service.price}</span>
                          <span className="text-gray-400 text-sm flex items-center gap-1">
                            <Clock size={14} />
                            {service.duration}
                          </span>
                        </div>
                      </div>
                      <p className="text-gray-300">{service.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Step 2: Date & Time Selection */}
            {currentStep === 2 && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6">
                  Choisissez la date et l'heure
                </h2>
                
                {/* Date Selection */}
                <div className="mb-8">
                  <h3 className="text-xl font-semibold text-white mb-4">Date</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                    {availableDates.map(date => (
                      <button
                        key={date.toISOString()}
                        onClick={() => {
                          const dateStr = date.toISOString().split('T')[0];
                          setSelectedDate(date.toISOString());
                          setSelectedTime(''); // Reset time selection
                          loadAvailability(dateStr);
                        }}
                        className={`p-3 rounded-lg border-2 transition-all duration-200 text-center ${
                          selectedDate === date.toISOString()
                            ? 'border-green-400 bg-green-400/10'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                      >
                        <div className="text-white font-medium text-sm">
                          {formatDateShort(date)}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Time Selection */}
                {selectedDate && (
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-4">
                      Heure 
                      {loadingAvailability && (
                        <span className="text-sm text-gray-400 ml-2">
                          (Chargement des disponibilités...)
                        </span>
                      )}
                    </h3>
                    {loadingAvailability ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="w-8 h-8 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    ) : timeSlots.length > 0 ? (
                      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                        {timeSlots.map(time => (
                          <button
                            key={time}
                            onClick={() => setSelectedTime(time)}
                            className={`p-3 rounded-lg border-2 transition-all duration-200 text-center ${
                              selectedTime === time
                                ? 'border-green-400 bg-green-400/10'
                                : 'border-gray-600 hover:border-gray-500'
                            }`}
                          >
                            <div className="text-white font-medium">{time}</div>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-400">Aucun créneau disponible pour cette date.</p>
                        <p className="text-gray-500 text-sm mt-2">Veuillez choisir une autre date.</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Contact Information */}
            {currentStep === 3 && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6">
                  Vos informations
                </h2>
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Nom complet *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                        placeholder="Votre nom"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Email *
                      </label>
                      <input
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                        placeholder="votre@email.com"
                      />
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Téléphone
                      </label>
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({...formData, phone: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                        placeholder="+33 6 12 34 56 78"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Entreprise
                      </label>
                      <input
                        type="text"
                        value={formData.company}
                        onChange={(e) => setFormData({...formData, company: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"
                        placeholder="Nom de votre entreprise"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Message (optionnel)
                    </label>
                    <textarea
                      rows={4}
                      value={formData.message}
                      onChange={(e) => setFormData({...formData, message: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent resize-none"
                      placeholder="Décrivez brièvement vos besoins..."
                    />
                  </div>

                  {/* Booking Summary */}
                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Récapitulatif</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-300">Service:</span>
                        <span className="text-white">{services.find(s => s.id === selectedService)?.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Date:</span>
                        <span className="text-white">{formatDate(new Date(selectedDate))}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Heure:</span>
                        <span className="text-white">{selectedTime}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Durée:</span>
                        <span className="text-white">{services.find(s => s.id === selectedService)?.duration}</span>
                      </div>
                      <div className="flex justify-between font-semibold">
                        <span className="text-gray-300">Prix:</span>
                        <span className="text-green-400">{services.find(s => s.id === selectedService)?.price}</span>
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between items-center mt-8">
              <button
                onClick={prevStep}
                disabled={currentStep === 1}
                className="flex items-center gap-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={20} />
                Précédent
              </button>

              {currentStep < 3 ? (
                <button
                  onClick={nextStep}
                  disabled={!canProceed()}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Suivant
                  <ChevronRight size={20} />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={!canProceed() || isSubmitting}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
                      Confirmation...
                    </>
                  ) : (
                    <>
                      <Calendar size={20} />
                      Confirmer le rendez-vous
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Booking;