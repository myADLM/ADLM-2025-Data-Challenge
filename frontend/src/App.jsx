import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader, FileText, AlertCircle, ArrowRight, X, Clock, Heart } from 'lucide-react';
import SearchBar from './components/SearchBar';
import ResultDisplay from './components/ResultDisplay';
import DocumentViewer from './components/DocumentViewer';
import SearchHistory from './components/SearchHistory';
import { queryAPI } from './services/api';

const API_BASE = '/api';

export default function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [apiHealth, setApiHealth] = useState(null);

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  // Load saved data from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('searchHistory');
    if (saved) setSearchHistory(JSON.parse(saved));
    const savedFavs = localStorage.getItem('favorites');
    if (savedFavs) setFavorites(JSON.parse(savedFavs));
  }, []);

  // Save history to localStorage
  useEffect(() => {
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
  }, [searchHistory]);

  useEffect(() => {
    localStorage.setItem('favorites', JSON.stringify(favorites));
  }, [favorites]);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      setApiHealth(response.ok ? 'ok' : 'down');
    } catch (err) {
      setApiHealth('down');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    if (apiHealth !== 'ok') {
      setError('API is not available. Please try again later.');
      return;
    }

    setError('');
    setLoading(true);
    setResult(null);
    setShowHistory(false);

    try {
      const data = await queryAPI(query);
      setResult(data);

      // Add to search history
      const newEntry = {
        id: Date.now(),
        query: data.question,
        timestamp: new Date().toISOString(),
        sourceCount: data.sources.length
      };
      setSearchHistory([newEntry, ...searchHistory.slice(0, 19)]);
      setQuery('');
    } catch (err) {
      setError(err.message || 'Failed to get response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = (historyQuery) => {
    setQuery(historyQuery);
    setShowHistory(false);
  };

  const toggleFavorite = (sourceFilename) => {
    setFavorites(prev => {
      const isFav = prev.includes(sourceFilename);
      return isFav ? prev.filter(f => f !== sourceFilename) : [...prev, sourceFilename];
    });
  };

  const isFavorited = (filename) => favorites.includes(filename);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* API Status Banner */}
      {apiHealth === 'down' && (
        <motion.div
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          className="bg-yellow-50 border-b border-yellow-200 px-4 py-3"
        >
          <div className="max-w-3xl mx-auto flex items-center text-yellow-800">
            <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0" />
            <p className="text-sm">API server is currently unavailable. Please check your connection.</p>
          </div>
        </motion.div>
      )}

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="text-center mb-12">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-block p-3 bg-blue-50 rounded-2xl mb-4"
          >
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
          </motion.div>
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-700 mb-3">
            Lab Knowledge Base
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Ask questions about laboratory procedures and safety protocols to get instant answers with verified sources
          </p>
        </header>

        {/* Main Content */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100"
        >
          {/* Search Section */}
          <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-100">
            <SearchBar
              query={query}
              setQuery={setQuery}
              onSubmit={handleSubmit}
              loading={loading}
              onHistoryClick={() => setShowHistory(!showHistory)}
              historyCount={searchHistory.length}
            />
          </div>

          {/* Results Section */}
          <div className="p-6 min-h-[400px]">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start text-red-700 gap-3"
              >
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </motion.div>
            )}

            <AnimatePresence mode="wait">
              {loading && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center py-12"
                >
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-2 border-blue-500 border-t-transparent mb-4"></div>
                  <p className="text-gray-600 font-medium">Searching knowledge base...</p>
                </motion.div>
              )}

              {!loading && !result && !error && (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center py-12 text-gray-500"
                >
                  <div className="inline-block p-4 bg-gray-50 rounded-2xl mb-4">
                    <FileText className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-lg font-medium">No results yet</p>
                  <p className="mt-2 max-w-md mx-auto text-sm">
                    Enter your question above to search our laboratory documentation and safety procedures
                  </p>
                </motion.div>
              )}

              {result && !loading && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ResultDisplay
                    result={result}
                    onDocumentClick={setSelectedDocument}
                    onFavoriteClick={toggleFavorite}
                    isFavorited={isFavorited}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Search History */}
            {showHistory && searchHistory.length > 0 && (
              <SearchHistory
                history={searchHistory}
                onSelect={handleHistorySelect}
              />
            )}
          </div>
        </motion.div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Lab Knowledge Base • Powered by AI • For internal use only</p>
        </footer>
      </div>

      {/* Document Viewer Modal */}
      <AnimatePresence>
        {selectedDocument && (
          <DocumentViewer
            document={selectedDocument}
            onClose={() => setSelectedDocument(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
