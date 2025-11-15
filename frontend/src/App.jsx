import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Network, AlertCircle, MessageSquare, FileText } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import DocumentBrowser from './components/DocumentBrowser';

const API_BASE = '/api';

export default function App() {
  const [favorites, setFavorites] = useState([]);
  const [apiHealth, setApiHealth] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  // Load saved favorites from localStorage
  useEffect(() => {
    const savedFavs = localStorage.getItem('kg_favorites');
    if (savedFavs) setFavorites(JSON.parse(savedFavs));
  }, []);

  // Save favorites to localStorage
  useEffect(() => {
    localStorage.setItem('kg_favorites', JSON.stringify(favorites));
  }, [favorites]);

  const checkApiHealth = async () => {
    try {
      // Add timeout and retry logic
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch(`${API_BASE}/health`, {
        signal: controller.signal,
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      setApiHealth(response.ok ? 'ok' : 'down');
    } catch (err) {
      console.error('API health check failed:', err);
      setApiHealth('down');
      // Retry after 3 seconds
      setTimeout(() => {
        checkApiHealth();
      }, 3000);
    }
  };

  const toggleFavorite = (entityName) => {
    setFavorites(prev => {
      const isFav = prev.includes(entityName);
      return isFav ? prev.filter(f => f !== entityName) : [...prev, entityName];
    });
  };

  const isFavorited = (name) => favorites.includes(name);

  return (
    <div className="min-h-screen bg-white">
      {/* API Status Banner */}
      {apiHealth === 'down' && (
        <motion.div
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          className="bg-yellow-50 border-b border-yellow-200 px-4 py-3"
        >
          <div className="max-w-7xl mx-auto flex items-center text-yellow-800">
            <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0" />
            <p className="text-sm font-medium">API server is currently unavailable. Please check your connection.</p>
          </div>
        </motion.div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header with Logo and Title */}
        <header className="flex items-center gap-6 mb-6 py-3 border-b border-einstein-gray-200">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="flex-shrink-0"
          >
            <img
              src="/ui_team_logo.png"
              alt="LabR Logo"
              className="h-20 w-auto drop-shadow-sm"
            />
          </motion.div>

          <motion.div
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex-1"
          >
            <h1 className="text-3xl md:text-4xl font-bold text-einstein-gray-800 mb-1 tracking-tight">
              Knowledge Graph Based Search
            </h1>
            <p className="text-base text-einstein-gray-600 font-normal">
              Chat to explore laboratory procedures, devices, and relationships.
            </p>
          </motion.div>
        </header>

        {/* Tabs */}
        <div className="mb-4 border-b border-einstein-gray-200">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
                activeTab === 'chat'
                  ? 'border-einstein-blue text-einstein-blue'
                  : 'border-transparent text-einstein-gray-600 hover:text-einstein-gray-800'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Chat
              </div>
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
                activeTab === 'documents'
                  ? 'border-einstein-blue text-einstein-blue'
                  : 'border-transparent text-einstein-gray-600 hover:text-einstein-gray-800'
              }`}
            >
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Documents
              </div>
            </button>
          </div>
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {activeTab === 'chat' ? (
            <ChatInterface
              onFavoriteClick={toggleFavorite}
              isFavorited={isFavorited}
            />
          ) : (
            <DocumentBrowser />
          )}
        </motion.div>

        {/* Footer */}
        <footer className="mt-6 pt-4 border-t border-einstein-gray-200 text-center text-einstein-gray-500 text-xs">
          <p className="font-medium">Knowledge Graph Chat Interface • Lab Knowledge Base • ADLM Data Challenge 2025</p>
        </footer>
      </div>
    </div>
  );
}

