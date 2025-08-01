import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useTheme } from '../../context/ThemeContext';
import { 
  Mail, User, Calendar, MessageSquare, ExternalLink, 
  ArrowLeft, RefreshCw, Trash2, Eye, CheckCircle, X, 
  MoreVertical, FileText, Reply, MailOpen
} from 'lucide-react';

const AdminContacts = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedContact, setSelectedContact] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const navigate = useNavigate();
  const { isDark } = useTheme();

  useEffect(() => {
    fetchContacts();
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    const tokenType = localStorage.getItem('admin_token_type');
    
    if (!token) {
      navigate('/admin/login');
      return null;
    }
    
    return {
      'Authorization': `${tokenType} ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des messages');
      }

      const data = await response.json();
      setContacts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateContactStatus = async (contactId, status) => {
    try {
      setActionLoading(true);
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact/${contactId}/status`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ status })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour du statut');
      }

      // Refresh contacts list
      await fetchContacts();
      
      // Update the modal contact if it's currently displayed
      if (selectedContact && selectedContact.id === contactId) {
        setSelectedContact({...selectedContact, status});
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const openContactModal = (contact) => {
    setSelectedContact(contact);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedContact(null);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'new': { color: 'bg-red-500', text: 'Nouveau' },
      'read': { color: 'bg-yellow-500', text: 'Lu' },
      'replied': { color: 'bg-green-500', text: 'Répondu' }
    };
    
    const config = statusConfig[status] || { color: 'bg-gray-500', text: status };
    
    return (
      <Badge className={`${config.color} text-white`}>
        {config.text}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getServiceLabel = (service) => {
    const services = {
      'audit': 'Audit de sécurité',
      'development': 'Développement Python',
      'infrastructure': 'Sécurisation d\'infrastructure',
      'consulting': 'Consulting & Formation',
      'other': 'Autre'
    };
    return services[service] || service;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => navigate('/admin/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Retour au dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Messages de Contact
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Gérer les messages reçus via le formulaire de contact
              </p>
            </div>
          </div>
          <Button onClick={fetchContacts} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Actualiser
          </Button>
        </div>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50 dark:bg-red-900/20">
            <AlertDescription className="text-red-800 dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Statistics */}
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                  <p className="text-2xl font-bold">{contacts.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-red-600" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Nouveaux</p>
                  <p className="text-2xl font-bold">{contacts.filter(c => c.status === 'new').length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Lus</p>
                  <p className="text-2xl font-bold">{contacts.filter(c => c.status === 'read').length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Répondus</p>
                  <p className="text-2xl font-bold">{contacts.filter(c => c.status === 'replied').length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Messages List */}
        <div className="grid gap-4">
          {contacts.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Mail className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Aucun message de contact
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Les messages reçus via le formulaire de contact apparaîtront ici.
                </p>
              </CardContent>
            </Card>
          ) : (
            contacts.map((contact) => (
              <Card key={contact.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="flex items-center gap-3 mb-2">
                        <User className="h-5 w-5 text-blue-600" />
                        {contact.name}
                        {getStatusBadge(contact.status)}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <Mail className="h-4 w-4" />
                          {contact.email}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {formatDate(contact.submitted_at)}
                        </span>
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openContactModal(contact)}
                        className="flex items-center gap-2"
                      >
                        <FileText className="h-4 w-4" />
                        Voir détails
                      </Button>
                      
                      {contact.status === 'new' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateContactStatus(contact.id, 'read')}
                          disabled={actionLoading}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Marquer lu
                        </Button>
                      )}
                      
                      {contact.status === 'read' && (
                        <Button
                          size="sm"
                          onClick={() => updateContactStatus(contact.id, 'replied')}
                          disabled={actionLoading}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Marquer répondu
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                        Sujet: {contact.subject}
                      </h4>
                      {contact.service && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Service d'intérêt: <span className="font-medium">{getServiceLabel(contact.service)}</span>
                        </p>
                      )}
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                      <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap line-clamp-3">
                        {contact.message}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(`mailto:${contact.email}?subject=Re: ${contact.subject}`, '_blank')}
                        className="flex items-center gap-2"
                      >
                        <Reply className="h-4 w-4" />
                        Répondre par email
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Modal pour vue détaillée */}
        {showModal && selectedContact && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                {/* Header du modal */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                      <User className="h-6 w-6 text-blue-600" />
                      {selectedContact.name}
                      {getStatusBadge(selectedContact.status)}
                    </h2>
                    <div className="flex items-center gap-4 text-gray-600 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        {selectedContact.email}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(selectedContact.submitted_at)}
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={closeModal}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {/* Contenu du message */}
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Sujet: {selectedContact.subject}
                    </h3>
                    {selectedContact.service && (
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        Service d'intérêt: <span className="font-medium">{getServiceLabel(selectedContact.service)}</span>
                      </p>
                    )}
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Message :</h4>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                      {selectedContact.message}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex gap-3">
                      <Button
                        onClick={() => window.open(`mailto:${selectedContact.email}?subject=Re: ${selectedContact.subject}`, '_blank')}
                        className="flex items-center gap-2"
                      >
                        <Reply className="h-4 w-4" />
                        Répondre par email
                      </Button>
                    </div>

                    <div className="flex gap-2">
                      {selectedContact.status === 'new' && (
                        <Button
                          variant="outline"
                          onClick={() => updateContactStatus(selectedContact.id, 'read')}
                          disabled={actionLoading}
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          Marquer comme lu
                        </Button>
                      )}
                      
                      {selectedContact.status === 'read' && (
                        <>
                          <Button
                            variant="outline"
                            onClick={() => updateContactStatus(selectedContact.id, 'new')}
                            disabled={actionLoading}
                          >
                            <MailOpen className="h-4 w-4 mr-2" />
                            Marquer non lu
                          </Button>
                          <Button
                            onClick={() => updateContactStatus(selectedContact.id, 'replied')}
                            disabled={actionLoading}
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Marquer comme répondu
                          </Button>
                        </>
                      )}
                      
                      {selectedContact.status === 'replied' && (
                        <Button
                          variant="outline"
                          onClick={() => updateContactStatus(selectedContact.id, 'read')}
                          disabled={actionLoading}
                        >
                          <MailOpen className="h-4 w-4 mr-2" />
                          Marquer comme lu
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminContacts;