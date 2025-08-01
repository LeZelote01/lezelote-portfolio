import React, { useState, useEffect } from 'react';
import { Hash, Lock, Network, Shield, Link, Code, Play, Copy, CheckCircle, AlertTriangle, CheckCircle2, ExternalLink, Save, History, Download, Trash2 } from 'lucide-react';
import CryptoJS from 'crypto-js';
import { useLanguage } from '../context/LanguageContext';

const InteractiveTools = () => {
  const { t } = useLanguage();
  
  const [activeTab, setActiveTab] = useState('hash');
  const [copiedText, setCopiedText] = useState('');

  // Hash Generator State
  const [hashInput, setHashInput] = useState('');
  const [hashResults, setHashResults] = useState({});

  // Password Checker State
  const [password, setPassword] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(null);

  // Port Scanner State (simulation)
  const [targetHost, setTargetHost] = useState('');
  const [portScanResults, setPortScanResults] = useState([]);
  const [isScanning, setIsScanning] = useState(false);

  // Cipher Tool State
  const [cipherText, setCipherText] = useState('');
  const [cipherKey, setCipherKey] = useState('');
  const [cipherResult, setCipherResult] = useState('');
  const [cipherMode, setCipherMode] = useState('encrypt');

  // URL Analyzer State
  const [urlInput, setUrlInput] = useState('');
  const [urlAnalysis, setUrlAnalysis] = useState(null);

  // XSS Detector State
  const [xssInput, setXssInput] = useState('');
  const [xssResults, setXssResults] = useState(null);

  // JSON Validator State
  const [jsonInput, setJsonInput] = useState('');
  const [jsonResults, setJsonResults] = useState(null);

  // Results History State
  const [savedResults, setSavedResults] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const tools = [
    { id: 'hash', name: t('hashGenerator'), icon: Hash, description: t('hashGeneratorDesc') },
    { id: 'password', name: t('passwordAnalyzer'), icon: Lock, description: t('passwordAnalyzerDesc') },
    { id: 'ports', name: t('portScanner'), icon: Network, description: t('portScannerDesc') },
    { id: 'cipher', name: t('cipherTool'), icon: Shield, description: t('cipherToolDesc') },
    { id: 'url', name: t('urlAnalyzer'), icon: Link, description: t('urlAnalyzerDesc') },
    { id: 'xss', name: t('xssDetector'), icon: Shield, description: t('xssDetectorDesc') },
    { id: 'json', name: t('jsonValidator'), icon: Code, description: t('jsonValidatorDesc') }
  ];

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(text);
      setTimeout(() => setCopiedText(''), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Load saved results from localStorage on component mount
  useEffect(() => {
    const saved = localStorage.getItem('cybersecurity-tools-results');
    if (saved) {
      try {
        setSavedResults(JSON.parse(saved));
      } catch (e) {
        console.error('Error loading saved results:', e);
      }
    }
  }, []);

  const saveResult = (toolName, input, result, metadata = {}) => {
    const newResult = {
      id: Date.now().toString(),
      toolName,
      input: input.substring(0, 200), // Limit input length for storage
      result: typeof result === 'string' ? result : JSON.stringify(result, null, 2),
      metadata,
      timestamp: new Date().toISOString(),
      date: new Date().toLocaleDateString(t('language') === 'fr' ? 'fr-FR' : 'en-US'),
      time: new Date().toLocaleTimeString(t('language') === 'fr' ? 'fr-FR' : 'en-US')
    };

    const updatedResults = [newResult, ...savedResults].slice(0, 50); // Keep only last 50 results
    setSavedResults(updatedResults);
    localStorage.setItem('cybersecurity-tools-results', JSON.stringify(updatedResults));
    
    // Show success message
    setCopiedText('saved');
    setTimeout(() => setCopiedText(''), 2000);
  };

  // Delete a saved result
  const deleteSavedResult = (id) => {
    const updatedResults = savedResults.filter(result => result.id !== id);
    setSavedResults(updatedResults);
    localStorage.setItem('cybersecurity-tools-results', JSON.stringify(updatedResults));
  };

  // Clear all saved results
  const clearAllResults = () => {
    setSavedResults([]);
    localStorage.removeItem('cybersecurity-tools-results');
  };

  // Export results as JSON
  const exportResults = () => {
    const dataStr = JSON.stringify(savedResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `cybersecurity-tools-results-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Hash Generator Functions
  const generateHashes = () => {
    if (!hashInput.trim()) return;

    const results = {
      md5: CryptoJS.MD5(hashInput).toString(),
      sha1: CryptoJS.SHA1(hashInput).toString(),
      sha256: CryptoJS.SHA256(hashInput).toString(),
      sha512: CryptoJS.SHA512(hashInput).toString()
    };
    setHashResults(results);
  };

  const saveHashResults = () => {
    if (Object.keys(hashResults).length > 0) {
      saveResult(t('hashGenerator'), hashInput, hashResults, {
        algorithms: Object.keys(hashResults),
        inputLength: hashInput.length
      });
    }
  };

  // Password Strength Checker
  const checkPasswordStrength = (pwd) => {
    setPassword(pwd);
    
    if (!pwd) {
      setPasswordStrength(null);
      return;
    }

    let score = 0;
    let feedback = [];
    
    // Length check
    if (pwd.length >= 8) score += 1;
    else feedback.push(t('atLeast8Chars'));
    
    if (pwd.length >= 12) score += 1;
    
    // Character variety
    if (/[a-z]/.test(pwd)) score += 1;
    else feedback.push(t('lowercaseLetters'));
    
    if (/[A-Z]/.test(pwd)) score += 1;
    else feedback.push(t('uppercaseLetters'));
    
    if (/[0-9]/.test(pwd)) score += 1;
    else feedback.push(t('numbers'));
    
    if (/[^A-Za-z0-9]/.test(pwd)) score += 1;
    else feedback.push(t('specialChars'));

    // Common patterns check
    if (!/(.)\1{2,}/.test(pwd)) score += 1;
    else feedback.push(t('avoidRepetitions'));

    const strength = {
      score,
      level: score <= 2 ? t('passwordStrengthWeak') : 
             score <= 4 ? t('passwordStrengthMedium') : 
             score <= 6 ? t('passwordStrengthStrong') : 
             t('passwordStrengthVeryStrong'),
      color: score <= 2 ? 'red' : score <= 4 ? 'yellow' : score <= 6 ? 'green' : 'emerald',
      feedback,
      entropy: Math.log2(Math.pow(95, pwd.length)).toFixed(1)
    };

    setPasswordStrength(strength);
  };

  const savePasswordResults = () => {
    if (passwordStrength) {
      saveResult(t('passwordAnalyzer'), password.replace(/./g, '*'), passwordStrength, {
        level: passwordStrength.level,
        score: passwordStrength.score,
        entropy: passwordStrength.entropy
      });
    }
  };

  // Save port scan results
  const savePortScanResults = () => {
    if (portScanResults.length > 0) {
      const openPorts = portScanResults.filter(result => result.status === 'Open');
      saveResult(t('portScanner'), targetHost, portScanResults, {
        target: targetHost,
        totalPorts: portScanResults.length,
        openPorts: openPorts.length,
        services: openPorts.map(p => p.service)
      });
    }
  };

  // Save cipher results
  const saveCipherResults = () => {
    if (cipherResult && cipherResult !== t('errorCipherOperation')) {
      saveResult(t('cipherTool'), cipherText, cipherResult, {
        mode: cipherMode,
        inputLength: cipherText.length,
        outputLength: cipherResult.length
      });
    }
  };

  // Save URL analysis results
  const saveUrlAnalysisResults = () => {
    if (urlAnalysis && !urlAnalysis.error) {
      saveResult(t('urlAnalyzer'), urlInput, urlAnalysis, {
        protocol: urlAnalysis.protocol,
        hostname: urlAnalysis.hostname,
        isSecure: urlAnalysis.isSecure,
        hasQuery: urlAnalysis.hasQuery
      });
    }
  };

  // Save XSS detection results
  const saveXssResults = () => {
    if (xssResults) {
      saveResult(t('xssDetector'), xssInput, xssResults, {
        riskLevel: xssResults.riskLevel,
        securityScore: xssResults.securityScore,
        threatsFound: xssResults.threatsFound
      });
    }
  };

  // Save JSON validation results
  const saveJsonResults = () => {
    if (jsonResults) {
      saveResult(t('jsonValidator'), jsonInput, jsonResults, {
        isValid: jsonResults.isValid,
        type: jsonResults.analysis?.type,
        size: jsonResults.analysis?.size
      });
    }
  };

  // Port Scanner Simulation
  const simulatePortScan = async () => {
    if (!targetHost.trim()) return;
    
    setIsScanning(true);
    setPortScanResults([]);
    
    const commonPorts = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306];
    const results = [];
    
    for (let i = 0; i < commonPorts.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 200)); // Simulate scan delay
      
      const port = commonPorts[i];
      const isOpen = Math.random() > 0.7; // 30% chance of being open
      const service = getServiceName(port);
      
      results.push({
        port,
        status: isOpen ? 'Open' : 'Closed',
        service: isOpen ? service : 'Unknown'
      });
      
      setPortScanResults([...results]);
    }
    
    setIsScanning(false);
  };

  const getServiceName = (port) => {
    const services = {
      21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
      80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
      993: 'IMAPS', 995: 'POP3S', 3389: 'RDP', 5432: 'PostgreSQL', 3306: 'MySQL'
    };
    return services[port] || 'Unknown';
  };

  // Cipher Functions
  const performCipher = () => {
    if (!cipherText.trim() || !cipherKey.trim()) return;

    try {
      let result;
      if (cipherMode === 'encrypt') {
        result = CryptoJS.AES.encrypt(cipherText, cipherKey).toString();
      } else {
        const bytes = CryptoJS.AES.decrypt(cipherText, cipherKey);
        result = bytes.toString(CryptoJS.enc.Utf8);
        if (!result) {
          result = t('errorIncorrectKey');
        }
      }
      setCipherResult(result);
    } catch (error) {
      setCipherResult(t('errorCipherOperation'));
    }
  };

  // URL Analyzer
  const analyzeURL = () => {
    if (!urlInput.trim()) return;

    try {
      const url = new URL(urlInput);
      const analysis = {
        protocol: url.protocol,
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? '443' : '80'),
        pathname: url.pathname,
        search: url.search,
        hash: url.hash,
        origin: url.origin,
        isSecure: url.protocol === 'https:',
        hasQuery: !!url.search,
        pathSegments: url.pathname.split('/').filter(Boolean),
        queryParams: Object.fromEntries(url.searchParams)
      };
      setUrlAnalysis(analysis);
    } catch (error) {
      setUrlAnalysis({ error: t('invalidUrl') });
    }
  };

  // XSS Detector
  const detectXSS = () => {
    if (!xssInput.trim()) return;

    const xssPatterns = [
      // Script tags
      { pattern: /<script[\s\S]*?>[\s\S]*?<\/script>/gi, threat: 'Script Tag', level: 'high' },
      { pattern: /<script[^>]*>/gi, threat: 'Script Tag (unclosed)', level: 'high' },
      
      // Event handlers
      { pattern: /on\w+\s*=\s*['"]/gi, threat: 'Event Handler', level: 'medium' },
      
      // JavaScript URLs
      { pattern: /javascript\s*:/gi, threat: 'JavaScript URL', level: 'high' },
      
      // Data URLs with script
      { pattern: /data\s*:\s*[^,]*script/gi, threat: 'Data URL Script', level: 'high' },
      
      // HTML entities that could be XSS
      { pattern: /&[#x]\w+;/gi, threat: 'HTML Entity Encoding', level: 'low' },
      
      // Iframe tags
      { pattern: /<iframe[\s\S]*?>/gi, threat: 'IFrame Tag', level: 'medium' },
      
      // Object/embed tags
      { pattern: /<(object|embed)[\s\S]*?>/gi, threat: 'Object/Embed Tag', level: 'medium' },
      
      // Form tags with suspicious attributes
      { pattern: /<form[\s\S]*?action\s*=\s*['"][^'"]*javascript/gi, threat: 'Form with JS action', level: 'high' },
      
      // Meta refresh
      { pattern: /<meta[\s\S]*?http-equiv\s*=\s*['"]refresh['"][\s\S]*?>/gi, threat: 'Meta Refresh', level: 'medium' },
      
      // SVG with script
      { pattern: /<svg[\s\S]*?<script/gi, threat: 'SVG with Script', level: 'high' },
      
      // Style with expression
      { pattern: /style\s*=\s*['"][^'"]*expression/gi, threat: 'CSS Expression', level: 'medium' }
    ];

    const threats = [];
    let riskLevel = 'low';
    let securityScore = 100;

    xssPatterns.forEach(({ pattern, threat, level }) => {
      const matches = xssInput.match(pattern);
      if (matches) {
        matches.forEach(match => {
          threats.push({
            type: threat,
            level,
            match: match.substring(0, 100) + (match.length > 100 ? '...' : ''),
            position: xssInput.indexOf(match)
          });
          
          // Adjust security score
          if (level === 'high') {
            securityScore -= 30;
            riskLevel = 'high';
          } else if (level === 'medium') {
            securityScore -= 15;
            if (riskLevel !== 'high') riskLevel = 'medium';
          } else {
            securityScore -= 5;
          }
        });
      }
    });

    securityScore = Math.max(0, securityScore);

    const analysis = {
      isClean: threats.length === 0,
      riskLevel,
      securityScore,
      threatsFound: threats.length,
      threats,
      recommendations: generateXSSRecommendations(threats)
    };

    setXssResults(analysis);
  };

  const generateXSSRecommendations = (threats) => {
    const recommendations = [];
    
    if (threats.some(t => t.type.includes('Script'))) {
      recommendations.push(t('escapeScriptTags'));
    }
    if (threats.some(t => t.type.includes('Event Handler'))) {
      recommendations.push(t('removeEventHandlers'));
    }
    if (threats.some(t => t.type.includes('JavaScript URL'))) {
      recommendations.push(t('avoidJsUrls'));
    }
    if (threats.some(t => t.type.includes('IFrame'))) {
      recommendations.push(t('validateIframeSources'));
    }
    if (threats.length === 0) {
      recommendations.push(t('contentSafe'));
    }
    
    recommendations.push(t('useHtmlEscaping'));
    recommendations.push(t('implementCSP'));
    
    return recommendations;
  };

  // JSON Validator
  const validateJSON = () => {
    if (!jsonInput.trim()) return;

    try {
      const parsed = JSON.parse(jsonInput);
      const formatted = JSON.stringify(parsed, null, 2);
      
      // Analyze JSON structure
      const analysis = analyzeJSONStructure(parsed);
      
      setJsonResults({
        isValid: true,
        formatted,
        original: jsonInput,
        analysis,
        error: null
      });
    } catch (error) {
      setJsonResults({
        isValid: false,
        formatted: null,
        original: jsonInput,
        analysis: null,
        error: {
          message: error.message,
          line: getJSONErrorLine(error.message),
          suggestions: getJSONSuggestions(error.message)
        }
      });
    }
  };

  const analyzeJSONStructure = (obj, path = '') => {
    const analysis = {
      type: Array.isArray(obj) ? 'array' : typeof obj,
      size: 0,
      depth: 0,
      keys: [],
      structure: {}
    };

    if (typeof obj === 'object' && obj !== null) {
      if (Array.isArray(obj)) {
        analysis.size = obj.length;
        analysis.structure.arrayLength = obj.length;
        if (obj.length > 0) {
          analysis.structure.itemTypes = [...new Set(obj.map(item => 
            Array.isArray(item) ? 'array' : typeof item
          ))];
        }
      } else {
        const keys = Object.keys(obj);
        analysis.size = keys.length;
        analysis.keys = keys;
        analysis.structure.properties = {};
        
        keys.forEach(key => {
          const value = obj[key];
          analysis.structure.properties[key] = {
            type: Array.isArray(value) ? 'array' : typeof value,
            isNull: value === null
          };
        });
      }
      
      // Calculate depth
      const getDepth = (o) => {
        if (typeof o !== 'object' || o === null) return 0;
        return 1 + Math.max(0, ...Object.values(o).map(v => getDepth(v)));
      };
      analysis.depth = getDepth(obj);
    }

    return analysis;
  };

  const getJSONErrorLine = (errorMessage) => {
    const match = errorMessage.match(/position (\d+)/);
    if (match) {
      const position = parseInt(match[1]);
      const lines = jsonInput.substring(0, position).split('\n');
      return lines.length;
    }
    return null;
  };

  const getJSONSuggestions = (errorMessage) => {
    const suggestions = [];
    
    if (errorMessage.includes('Unexpected token')) {
      suggestions.push(t('checkMissingCommas'));
      suggestions.push(t('useDoubleQuotes'));
    }
    if (errorMessage.includes('Unexpected end')) {
      suggestions.push(t('checkMissingBrackets'));
    }
    if (errorMessage.includes('string')) {
      suggestions.push(t('stringsNeedQuotes'));
    }
    
    suggestions.push(t('useOnlineValidator'));
    
    return suggestions;
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Code size={32} className="text-gray-900" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              {t('interactiveToolsTitle')} <span className="text-green-400"></span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed mb-8">
              {t('interactiveToolsSubtitle')}
            </p>
            
            {/* Integration link to projects */}
            <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-xl p-4 max-w-2xl mx-auto">
              <p className="text-gray-300 text-sm mb-3">
                {t('interactiveToolsDesc')}
              </p>
              <a 
                href="/projects" 
                className="inline-flex items-center gap-2 bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-4 py-2 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 text-sm"
              >
                <Shield size={16} />
                {t('freeOnlineTools')}
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Tools Navigation */}
      <section className="py-12 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            {/* Tools History & Save Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 mb-8 p-4 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-semibold text-white">{t('interactiveToolsTitle')}</h3>
                <span className="text-sm text-gray-400">
                  {savedResults.length} {t('savedResults')}
                </span>
              </div>
              
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200"
                >
                  <History size={16} />
                  {showHistory ? t('hideHistory') : t('showHistory')}
                </button>
                
                {savedResults.length > 0 && (
                  <>
                    <button
                      onClick={exportResults}
                      className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200"
                    >
                      <Download size={16} />
                      {t('exportResults')}
                    </button>
                    
                    <button
                      onClick={clearAllResults}
                      className="flex items-center gap-2 bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200"
                    >
                      <Trash2 size={16} />
                      {t('clearAllResults')}
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* History Panel */}
            {showHistory && (
              <div className="mb-8 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <History className="text-green-400" />
                  {t('resultsHistory')}
                </h3>
                
                {savedResults.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                      <History size={24} className="text-gray-500" />
                    </div>
                    <p className="text-gray-400">{t('noSavedResults')}</p>
                    <p className="text-sm text-gray-500">{t('useToolsBelow')}</p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {savedResults.map((result) => (
                      <div key={result.id} className="bg-gray-900/50 border border-gray-600 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="text-white font-semibold">{result.toolName}</h4>
                            <p className="text-xs text-gray-400">{result.date} à {result.time}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => copyToClipboard(result.result)}
                              className="text-gray-400 hover:text-white transition-colors"
                              title={t('copyResult')}
                            >
                              <Copy size={14} />
                            </button>
                            <button
                              onClick={() => deleteSavedResult(result.id)}
                              className="text-gray-400 hover:text-red-400 transition-colors"
                              title={t('deleteResult')}
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </div>
                        
                        <div className="text-sm">
                          <div className="text-gray-400 mb-1">
                            <strong>Entrée:</strong> {result.input}
                            {result.input.length >= 200 && '...'}
                          </div>
                          <div className="text-gray-300 bg-gray-800 p-2 rounded font-mono text-xs max-h-20 overflow-y-auto">
                            {typeof result.result === 'string' 
                              ? result.result.substring(0, 300) + (result.result.length > 300 ? '...' : '')
                              : JSON.stringify(result.result, null, 2).substring(0, 300) + '...'
                            }
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div className="flex flex-wrap gap-4 justify-center mb-8">
              {tools.map(tool => {
                const Icon = tool.icon;
                return (
                  <button
                    key={tool.id}
                    onClick={() => setActiveTab(tool.id)}
                    className={`flex items-center gap-3 px-6 py-4 rounded-xl font-medium transition-all duration-200 ${
                      activeTab === tool.id
                        ? 'bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    <Icon size={20} />
                    <div className="text-left">
                      <div className="font-semibold">{tool.name}</div>
                      <div className="text-xs opacity-75">{tool.description}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Tool Content */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            
            {/* Hash Generator */}
            {activeTab === 'hash' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Hash className="text-green-400" />
                  {t('hashGeneratorTitle')}
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('enterTextToHash')}
                    </label>
                    <div className="flex gap-4">
                      <input
                        type="text"
                        value={hashInput}
                        onChange={(e) => setHashInput(e.target.value)}
                        placeholder={t('enterTextPlaceholder')}
                        className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                      />
                      <button
                        onClick={generateHashes}
                        className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 flex items-center gap-2"
                      >
                        <Play size={16} />
                        {t('generate')}
                      </button>
                    </div>
                  </div>

                  {Object.keys(hashResults).length > 0 && (
                    <div className="space-y-4">
                      {Object.entries(hashResults).map(([algorithm, hash]) => (
                        <div key={algorithm} className="bg-gray-900/50 border border-gray-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-green-400 font-semibold uppercase">{algorithm}</span>
                            <button
                              onClick={() => copyToClipboard(hash)}
                              className="flex items-center gap-1 text-gray-400 hover:text-white transition-colors"
                            >
                              {copiedText === hash ? <CheckCircle size={16} /> : <Copy size={16} />}
                              {copiedText === hash ? t('copied') : t('copy')}
                            </button>
                          </div>
                          <code className="text-gray-300 text-sm break-all font-mono">{hash}</code>
                        </div>
                      ))}
                      
                      {/* Save Results Button */}
                      <div className="flex justify-center pt-4">
                        <button
                          onClick={saveHashResults}
                          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                        >
                          {copiedText === 'saved' ? (
                            <>
                              <CheckCircle size={16} />
                              {t('saved')}
                            </>
                          ) : (
                            <>
                              <Save size={16} />
                              {t('saveHashResults')}
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Password Checker */}
            {activeTab === 'password' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Lock className="text-green-400" />
                  {t('passwordAnalyzerTitle')}
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('passwordToAnalyze')}
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => checkPasswordStrength(e.target.value)}
                      placeholder={t('passwordPlaceholder')}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                    />
                  </div>

                  {passwordStrength && (
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">{t('analysisResult')}</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                          passwordStrength.color === 'red' ? 'bg-red-500 text-white' :
                          passwordStrength.color === 'yellow' ? 'bg-yellow-500 text-gray-900' :
                          passwordStrength.color === 'green' ? 'bg-green-500 text-white' :
                          'bg-emerald-500 text-white'
                        }`}>
                          {passwordStrength.level}
                        </span>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Score de sécurité</h4>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-700 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full transition-all duration-300 ${
                                  passwordStrength.color === 'red' ? 'bg-red-500' :
                                  passwordStrength.color === 'yellow' ? 'bg-yellow-500' :
                                  passwordStrength.color === 'green' ? 'bg-green-500' :
                                  'bg-emerald-500'
                                }`}
                                style={{ width: `${(passwordStrength.score / 7) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-white font-medium">{passwordStrength.score}/7</span>
                          </div>
                          <p className="text-sm text-gray-400 mt-2">
                            Entropie: {passwordStrength.entropy} bits
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Améliorations suggérées</h4>
                          <ul className="space-y-1">
                            {passwordStrength.feedback.map((item, index) => (
                              <li key={index} className="text-sm text-gray-400 flex items-center gap-2">
                                <span className="w-1 h-1 bg-gray-500 rounded-full"></span>
                                {item}
                              </li>
                            ))}
                            {passwordStrength.feedback.length === 0 && (
                              <li className="text-sm text-green-400">Excellent mot de passe!</li>
                            )}
                          </ul>
                        </div>
                      </div>
                      
                      {/* Save Results Button */}
                      <div className="flex justify-center pt-6">
                        <button
                          onClick={savePasswordResults}
                          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                        >
                          {copiedText === 'saved' ? (
                            <>
                              <CheckCircle size={16} />
                              Sauvegardé!
                            </>
                          ) : (
                            <>
                              <Save size={16} />
                              Sauvegarder l'analyse
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Add other tools here... */}
            
            {/* Port Scanner */}
            {activeTab === 'ports' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Network className="text-green-400" />
                  {t('portScannerSimulation')}
                </h2>
                
                <div className="space-y-6">
                  <div className="bg-yellow-600/20 border border-yellow-500 rounded-lg p-4">
                    <p className="text-yellow-200 text-sm">
                      {t('educationalSimulation')}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('targetHostLabel')}
                    </label>
                    <div className="flex gap-4">
                      <input
                        type="text"
                        value={targetHost}
                        onChange={(e) => setTargetHost(e.target.value)}
                        placeholder={t('targetHostPlaceholder')}
                        className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                      />
                      <button
                        onClick={simulatePortScan}
                        disabled={isScanning}
                        className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 flex items-center gap-2 disabled:opacity-50"
                      >
                        {isScanning ? (
                          <>
                            <div className="w-4 h-4 border-2 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
                            Scan...
                          </>
                        ) : (
                          <>
                            <Play size={16} />
                            Scanner
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {portScanResults.length > 0 && (
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-white mb-4">
                        Résultats du scan ({portScanResults.length} ports testés)
                      </h3>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {portScanResults.map((result, index) => (
                          <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-800 rounded">
                            <span className="text-gray-300">Port {result.port}</span>
                            <div className="flex items-center gap-4">
                              <span className="text-gray-400 text-sm">{result.service}</span>
                              <span className={`px-2 py-1 rounded text-xs font-bold ${
                                result.status === 'Open' 
                                  ? 'bg-red-500 text-white' 
                                  : 'bg-gray-600 text-gray-300'
                              }`}>
                                {result.status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {/* Save Results Button */}
                      <div className="flex justify-center pt-4">
                        <button
                          onClick={savePortScanResults}
                          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                        >
                          {copiedText === 'saved' ? (
                            <>
                              <CheckCircle size={16} />
                              Sauvegardé!
                            </>
                          ) : (
                            <>
                              <Save size={16} />
                              Sauvegarder le scan
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Cipher Tool */}
            {activeTab === 'cipher' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Shield className="text-green-400" />
                  {t('cipherToolAES')}
                </h2>
                
                <div className="space-y-6">
                  <div className="flex gap-4 mb-6">
                    <button
                      onClick={() => setCipherMode('encrypt')}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                        cipherMode === 'encrypt'
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {t('encryptMode')}
                    </button>
                    <button
                      onClick={() => setCipherMode('decrypt')}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                        cipherMode === 'decrypt'
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {t('decryptMode')}
                    </button>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        {cipherMode === 'encrypt' ? 'Texte à chiffrer' : 'Texte chiffré'}
                      </label>
                      <textarea
                        value={cipherText}
                        onChange={(e) => setCipherText(e.target.value)}
                        placeholder={cipherMode === 'encrypt' ? 'Entrez votre message...' : 'Entrez le texte chiffré...'}
                        rows={4}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 resize-none"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Clé de chiffrement
                      </label>
                      <input
                        type="password"
                        value={cipherKey}
                        onChange={(e) => setCipherKey(e.target.value)}
                        placeholder="Clé secrète..."
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 mb-4"
                      />
                      
                      <button
                        onClick={performCipher}
                        className="w-full bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 flex items-center justify-center gap-2"
                      >
                        <Play size={16} />
                        {cipherMode === 'encrypt' ? 'Chiffrer' : 'Déchiffrer'}
                      </button>
                    </div>
                  </div>

                  {cipherResult && (
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-green-400 font-semibold">Résultat</span>
                        <button
                          onClick={() => copyToClipboard(cipherResult)}
                          className="flex items-center gap-1 text-gray-400 hover:text-white transition-colors"
                        >
                          {copiedText === cipherResult ? <CheckCircle size={16} /> : <Copy size={16} />}
                          {copiedText === cipherResult ? 'Copié!' : 'Copier'}
                        </button>
                      </div>
                      <textarea
                        value={cipherResult}
                        readOnly
                        rows={4}
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-gray-300 font-mono text-sm resize-none"
                      />
                      
                      {/* Save Results Button */}
                      <div className="flex justify-center pt-4">
                        <button
                          onClick={saveCipherResults}
                          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                        >
                          {copiedText === 'saved' ? (
                            <>
                              <CheckCircle size={16} />
                              Sauvegardé!
                            </>
                          ) : (
                            <>
                              <Save size={16} />
                              Sauvegarder le résultat
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* URL Analyzer */}
            {activeTab === 'url' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Link className="text-green-400" />
                  {t('urlAnalyzerTitle')}
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('urlToAnalyze')}
                    </label>
                    <div className="flex gap-4">
                      <input
                        type="url"
                        value={urlInput}
                        onChange={(e) => setUrlInput(e.target.value)}
                        placeholder="https://example.com/path?param=value"
                        className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                      />
                      <button
                        onClick={analyzeURL}
                        className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 flex items-center gap-2"
                      >
                        <Play size={16} />
                        Analyser
                      </button>
                    </div>
                  </div>

                  {urlAnalysis && (
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                      {urlAnalysis.error ? (
                        <div className="text-red-400 text-center py-4">
                          <p>{urlAnalysis.error}</p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <h3 className="text-lg font-semibold text-white mb-4">Analyse de l'URL</h3>
                          
                          <div className="grid md:grid-cols-2 gap-6">
                            <div className="space-y-3">
                              <div>
                                <span className="text-gray-400 text-sm">Protocole:</span>
                                <div className={`font-mono ${urlAnalysis.isSecure ? 'text-green-400' : 'text-yellow-400'}`}>
                                  {urlAnalysis.protocol}
                                  {urlAnalysis.isSecure && ' ✓ Sécurisé'}
                                </div>
                              </div>
                              
                              <div>
                                <span className="text-gray-400 text-sm">Nom d'hôte:</span>
                                <div className="text-white font-mono">{urlAnalysis.hostname}</div>
                              </div>
                              
                              <div>
                                <span className="text-gray-400 text-sm">Port:</span>
                                <div className="text-white font-mono">{urlAnalysis.port}</div>
                              </div>
                              
                              <div>
                                <span className="text-gray-400 text-sm">Chemin:</span>
                                <div className="text-white font-mono">{urlAnalysis.pathname || '/'}</div>
                              </div>
                            </div>
                            
                            <div className="space-y-3">
                              <div>
                                <span className="text-gray-400 text-sm">Origine:</span>
                                <div className="text-white font-mono text-sm break-all">{urlAnalysis.origin}</div>
                              </div>
                              
                              {urlAnalysis.hasQuery && (
                                <div>
                                  <span className="text-gray-400 text-sm">Paramètres de requête:</span>
                                  <div className="mt-2 space-y-1">
                                    {Object.entries(urlAnalysis.queryParams).map(([key, value]) => (
                                      <div key={key} className="text-sm">
                                        <span className="text-green-400">{key}:</span>
                                        <span className="text-white ml-2">{value}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                              
                              {urlAnalysis.pathSegments.length > 0 && (
                                <div>
                                  <span className="text-gray-400 text-sm">Segments du chemin:</span>
                                  <div className="flex flex-wrap gap-2 mt-2">
                                    {urlAnalysis.pathSegments.map((segment, index) => (
                                      <span key={index} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs font-mono">
                                        {segment}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Save Results Button */}
                          <div className="flex justify-center pt-6">
                            <button
                              onClick={saveUrlAnalysisResults}
                              className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                            >
                              {copiedText === 'saved' ? (
                                <>
                                  <CheckCircle size={16} />
                                  Sauvegardé!
                                </>
                              ) : (
                                <>
                                  <Save size={16} />
                                  Sauvegarder l'analyse
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* XSS Detector */}
            {activeTab === 'xss' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Shield className="text-green-400" />
                  {t('xssDetectorTitle')}
                </h2>
                
                <div className="space-y-6">
                  <div className="bg-blue-600/20 border border-blue-500 rounded-lg p-4">
                    <p className="text-blue-200 text-sm">
                      {t('xssEducationalNote')}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Code HTML/JavaScript à analyser
                    </label>
                    <div className="space-y-4">
                      <textarea
                        value={xssInput}
                        onChange={(e) => setXssInput(e.target.value)}
                        placeholder="Collez votre code HTML ou JavaScript ici..."
                        rows={8}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 font-mono text-sm resize-none"
                      />
                      
                      <button
                        onClick={detectXSS}
                        className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 flex items-center gap-2"
                      >
                        <Play size={16} />
                        Analyser les menaces XSS
                      </button>
                    </div>
                  </div>

                  {xssResults && (
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-white">Rapport d'analyse XSS</h3>
                        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-bold ${
                          xssResults.riskLevel === 'high' ? 'bg-red-500 text-white' :
                          xssResults.riskLevel === 'medium' ? 'bg-yellow-500 text-gray-900' :
                          'bg-green-500 text-white'
                        }`}>
                          {xssResults.riskLevel === 'high' ? <AlertTriangle size={16} /> : 
                           xssResults.riskLevel === 'medium' ? <AlertTriangle size={16} /> :
                           <CheckCircle2 size={16} />}
                          {xssResults.riskLevel === 'high' ? 'RISQUE ÉLEVÉ' :
                           xssResults.riskLevel === 'medium' ? 'RISQUE MOYEN' : 'SÉCURISÉ'}
                        </div>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-6 mb-6">
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Score de sécurité</h4>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-700 rounded-full h-3">
                              <div 
                                className={`h-3 rounded-full transition-all duration-300 ${
                                  xssResults.securityScore >= 80 ? 'bg-green-500' :
                                  xssResults.securityScore >= 50 ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`}
                                style={{ width: `${xssResults.securityScore}%` }}
                              ></div>
                            </div>
                            <span className="text-white font-bold">{xssResults.securityScore}/100</span>
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Menaces détectées</h4>
                          <div className="text-2xl font-bold text-white">
                            {xssResults.threatsFound}
                            <span className="text-sm font-normal text-gray-400 ml-2">vulnérabilités</span>
                          </div>
                        </div>
                      </div>

                      {xssResults.threats.length > 0 && (
                        <div className="mb-6">
                          <h4 className="text-sm font-medium text-gray-300 mb-3">Vulnérabilités détectées</h4>
                          <div className="space-y-3 max-h-64 overflow-y-auto">
                            {xssResults.threats.map((threat, index) => (
                              <div key={index} className="bg-gray-800 border border-gray-600 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-white font-semibold">{threat.type}</span>
                                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                                    threat.level === 'high' ? 'bg-red-500 text-white' :
                                    threat.level === 'medium' ? 'bg-yellow-500 text-gray-900' :
                                    'bg-gray-500 text-white'
                                  }`}>
                                    {threat.level.toUpperCase()}
                                  </span>
                                </div>
                                <div className="text-gray-300 text-sm font-mono bg-gray-900 p-2 rounded border-l-4 border-red-400">
                                  {threat.match}
                                </div>
                                <div className="text-xs text-gray-400 mt-1">
                                  Position: {threat.position}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-3">Recommandations</h4>
                        <ul className="space-y-2">
                          {xssResults.recommendations.map((rec, index) => (
                            <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                              <CheckCircle2 size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Save Results Button */}
                      <div className="flex justify-center pt-6">
                        <button
                          onClick={saveXssResults}
                          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                        >
                          {copiedText === 'saved' ? (
                            <>
                              <CheckCircle size={16} />
                              Sauvegardé!
                            </>
                          ) : (
                            <>
                              <Save size={16} />
                              Sauvegarder l'analyse
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* JSON Validator */}
            {activeTab === 'json' && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
                <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
                  <Code className="text-green-400" />
                  {t('jsonValidatorTitle')}
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      JSON à valider et formater
                    </label>
                    <div className="space-y-4">
                      <textarea
                        value={jsonInput}
                        onChange={(e) => setJsonInput(e.target.value)}
                        placeholder='{"exemple": "Collez votre JSON ici...", "tableau": [1, 2, 3]}'
                        rows={10}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400 font-mono text-sm resize-none"
                      />
                      
                      <div className="flex gap-4">
                        <button
                          onClick={validateJSON}
                          className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 flex items-center gap-2"
                        >
                          <Play size={16} />
                          Valider JSON
                        </button>
                        
                        {jsonResults && jsonResults.formatted && (
                          <button
                            onClick={() => copyToClipboard(jsonResults.formatted)}
                            className="bg-gray-600 hover:bg-gray-500 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2"
                          >
                            {copiedText === jsonResults.formatted ? 
                              <><CheckCircle size={16} /> Copié!</> : 
                              <><Copy size={16} /> Copier JSON formaté</>
                            }
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {jsonResults && (
                    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-white">Résultat de validation</h3>
                        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-bold ${
                          jsonResults.isValid ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                        }`}>
                          {jsonResults.isValid ? 
                            <><CheckCircle2 size={16} /> JSON VALIDE</> : 
                            <><AlertTriangle size={16} /> JSON INVALIDE</>
                          }
                        </div>
                      </div>

                      {jsonResults.isValid ? (
                        <div className="space-y-6">
                          {/* Structure Analysis */}
                          <div>
                            <h4 className="text-sm font-medium text-gray-300 mb-3">Analyse de la structure</h4>
                            <div className="grid md:grid-cols-3 gap-4">
                              <div className="bg-gray-800 p-3 rounded">
                                <div className="text-xs text-gray-400">Type</div>
                                <div className="text-white font-semibold capitalize">{jsonResults.analysis.type}</div>
                              </div>
                              <div className="bg-gray-800 p-3 rounded">
                                <div className="text-xs text-gray-400">Taille</div>
                                <div className="text-white font-semibold">
                                  {jsonResults.analysis.size} {jsonResults.analysis.type === 'array' ? 'éléments' : 'propriétés'}
                                </div>
                              </div>
                              <div className="bg-gray-800 p-3 rounded">
                                <div className="text-xs text-gray-400">Profondeur</div>
                                <div className="text-white font-semibold">{jsonResults.analysis.depth} niveaux</div>
                              </div>
                            </div>
                            
                            {jsonResults.analysis.keys.length > 0 && (
                              <div className="mt-4">
                                <div className="text-xs text-gray-400 mb-2">Clés principales</div>
                                <div className="flex flex-wrap gap-2">
                                  {jsonResults.analysis.keys.map(key => (
                                    <span key={key} className="px-2 py-1 bg-blue-600 text-blue-100 rounded text-xs font-mono">
                                      {key}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Formatted JSON */}
                          <div>
                            <h4 className="text-sm font-medium text-gray-300 mb-3">JSON formaté</h4>
                            <div className="bg-gray-800 rounded-lg p-4 max-h-96 overflow-auto">
                              <pre className="text-sm text-gray-100 font-mono whitespace-pre-wrap">
                                {jsonResults.formatted}
                              </pre>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {/* Error Details */}
                          <div className="bg-red-900/30 border border-red-600 rounded-lg p-4">
                            <h4 className="text-red-400 font-semibold mb-2">Erreur de syntaxe</h4>
                            <p className="text-red-300 text-sm mb-2">{jsonResults.error.message}</p>
                            {jsonResults.error.line && (
                              <p className="text-red-300 text-sm">Ligne approximative: {jsonResults.error.line}</p>
                            )}
                          </div>

                          {/* Suggestions */}
                          <div>
                            <h4 className="text-sm font-medium text-gray-300 mb-3">Suggestions pour corriger</h4>
                            <ul className="space-y-2">
                              {jsonResults.error.suggestions.map((suggestion, index) => (
                                <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                                  <CheckCircle2 size={16} className="text-yellow-400 mt-0.5 flex-shrink-0" />
                                  {suggestion}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                      
                      {/* Save Results Button */}
                      <div className="flex justify-center pt-6">
                        <button
                          onClick={saveJsonResults}
                          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-all duration-200"
                        >
                          {copiedText === 'saved' ? (
                            <>
                              <CheckCircle size={16} />
                              Sauvegardé!
                            </>
                          ) : (
                            <>
                              <Save size={16} />
                              Sauvegarder l'analyse
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
            
          </div>
        </div>
      </section>

      {/* Related Projects Section */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-white mb-6">
                Projets <span className="text-green-400">Connexes</span>
              </h2>
              <p className="text-xl text-gray-300">
                Découvrez d'autres projets de cybersécurité que j'ai développés
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Current Project Card */}
              <div className="bg-gray-900/50 backdrop-blur-sm border border-green-400/50 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-cyan-400 rounded-lg flex items-center justify-center">
                    <Code size={20} className="text-gray-900" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-green-400">
                      Plateforme d'Outils Interactifs
                    </h3>
                    <span className="text-sm text-gray-400">Cybersécurité • Avancé</span>
                  </div>
                </div>
                
                <p className="text-gray-300 mb-4 leading-relaxed">
                  Cette collection de 7 outils interactifs démontre l'expertise technique 
                  en cybersécurité avec des fonctionnalités éducatives avancées.
                </p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {['React', 'JavaScript', 'CryptoJS', 'Tailwind CSS'].map((tech, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-medium">
                      {tech}
                    </span>
                  ))}
                </div>
                
                <div className="flex gap-3">
                  <a
                    href="/projects"
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 rounded-lg hover:from-green-500 hover:to-cyan-500 transition-all duration-200 text-sm font-medium"
                  >
                    <ExternalLink size={16} />
                    Voir dans Portfolio
                  </a>
                </div>
              </div>

              {/* Other Projects Suggestion */}
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
                    <Shield size={20} className="text-gray-900" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      Autres Projets Cybersécurité
                    </h3>
                    <span className="text-sm text-gray-400">Collection complète</span>
                  </div>
                </div>
                
                <p className="text-gray-300 mb-4 leading-relaxed">
                  Explorez ma collection complète de projets : analyseurs de logs, 
                  scanners de vulnérabilités, outils de forensique et plus encore.
                </p>
                
                <div className="space-y-2 mb-4">
                  <div className="text-sm text-gray-400 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                    Scanner de Vulnérabilités Web
                  </div>
                  <div className="text-sm text-gray-400 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                    Analyseur de Logs de Sécurité
                  </div>
                  <div className="text-sm text-gray-400 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                    Vérificateur d'Intégrité de Fichiers
                  </div>
                </div>
                
                <div className="flex gap-3">
                  <a
                    href="/projects"
                    className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-200 text-sm font-medium"
                  >
                    <ExternalLink size={16} />
                    Voir tous les projets
                  </a>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="text-center mt-12">
              <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 max-w-2xl mx-auto">
                <h3 className="text-2xl font-bold text-white mb-4">
                  Besoin d'outils personnalisés ?
                </h3>
                <p className="text-gray-300 mb-6 leading-relaxed">
                  Je développe des outils de cybersécurité sur mesure pour vos besoins spécifiques.
                  Contactez-moi pour discuter de votre projet.
                </p>
                <a
                  href="/contact"
                  className="bg-gradient-to-r from-green-400 to-cyan-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:from-green-500 hover:to-cyan-500 transition-all duration-200 inline-flex items-center gap-2"
                >
                  <ExternalLink size={16} />
                  Demander un devis
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default InteractiveTools;