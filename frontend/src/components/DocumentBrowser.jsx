import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, FileText, Filter, X, ChevronRight, BookOpen, FileCheck, Loader, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { getDocuments, fetchDocument } from '../services/api';
import { documentsCache, filterDocuments } from '../utils/documentCache';
import DocumentViewer from './DocumentViewer';

export default function DocumentBrowser() {
  const [documents, setDocuments] = useState([]);
  const [allDocuments, setAllDocuments] = useState([]); // Store all documents for client-side filtering
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [sectionFilter, setSectionFilter] = useState('');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});
  const [stats, setStats] = useState({ total: 0, sop: 0, fda: 0 });
  const [cacheAge, setCacheAge] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load documents on mount - check cache first
  useEffect(() => {
    loadDocuments(true);
  }, []);

  // Filter documents when filters change (client-side)
  useEffect(() => {
    if (allDocuments.length > 0) {
      const filtered = filterDocuments(allDocuments, {
        doc_type: docTypeFilter,
        section: sectionFilter,
        search: searchQuery
      });

      setDocuments(filtered);
      setStats({
        total: filtered.length,
        sop: filtered.filter(d => d.document_type === 'sop').length,
        fda: filtered.filter(d => d.document_type === 'fda').length
      });
    }
  }, [docTypeFilter, sectionFilter, searchQuery, allDocuments]);

  const loadDocuments = async (useCache = true) => {
    // Check cache first
    if (useCache) {
      const cached = documentsCache.get();
      if (cached && Array.isArray(cached) && cached.length > 0) {
        setAllDocuments(cached);
        setCacheAge(documentsCache.getAge());
        setLoading(false);
        return;
      }
    }

    setLoading(true);
    setIsRefreshing(!useCache);
    try {
      // Fetch all documents without filters (we'll filter client-side)
      const data = await getDocuments({});
      const fetchedDocs = data.documents || [];
      
      // Store in cache
      documentsCache.set(fetchedDocs);
      setCacheAge(0);
      
      // Update state
      setAllDocuments(fetchedDocs);
      // Filtering will happen automatically via useEffect
    } catch (error) {
      console.error('Failed to load documents:', error);
      // If API fails but we have cache, use cache
      const cached = documentsCache.get();
      if (cached && Array.isArray(cached) && cached.length > 0) {
        setAllDocuments(cached);
        setCacheAge(documentsCache.getAge());
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    documentsCache.clear();
    loadDocuments(false);
  };

  const handleDocumentClick = async (doc) => {
    try {
      // If content is already available in the document, use it directly
      if (doc.content) {
        setSelectedDocument({
          ...doc,
          content: doc.content
        });
        return;
      }
      
      // Otherwise, fetch it
      const data = await fetchDocument(doc.filename, doc.filepath);
      setSelectedDocument({
        ...doc,
        content: data.content
      });
    } catch (error) {
      console.error('Failed to load document:', error);
      alert(`Failed to load document: ${error.message}`);
    }
  };

  const toggleSection = (docIndex) => {
    setExpandedSections(prev => ({
      ...prev,
      [docIndex]: !prev[docIndex]
    }));
  };

  const clearFilters = () => {
    setSearchQuery('');
    setDocTypeFilter('all');
    setSectionFilter('');
  };

  return (
    <div className="flex h-[calc(100vh-120px)] gap-4">
      {/* Left: Document List */}
      <div className="flex-1 flex flex-col bg-white rounded-lg shadow-sm border border-einstein-gray-200 overflow-hidden">
        {/* Header */}
        <div className="p-5 bg-einstein-blue-light border-b border-einstein-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-einstein-gray-800">Document Browser</h2>
            <div className="flex items-center gap-2">
              {cacheAge !== null && (
                <span className="text-xs text-einstein-gray-500">
                  Cached {cacheAge}m ago
                </span>
              )}
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="p-1.5 text-einstein-gray-600 hover:text-einstein-blue hover:bg-white rounded-md transition-colors disabled:opacity-50"
                title="Refresh documents"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
          
          {/* Search */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-einstein-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents..."
              className="w-full pl-10 pr-4 py-2 border border-einstein-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-einstein-blue focus:border-einstein-blue text-sm"
            />
          </div>

          {/* Filters */}
          <div className="flex gap-2 flex-wrap">
            <select
              value={docTypeFilter}
              onChange={(e) => setDocTypeFilter(e.target.value)}
              className="px-3 py-1.5 border border-einstein-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-einstein-blue"
            >
              <option value="all">All Types</option>
              <option value="sop">Procedures (SOP)</option>
              <option value="fda">FDA Documents</option>
            </select>
            
            {(searchQuery || docTypeFilter !== 'all' || sectionFilter) && (
              <button
                onClick={clearFilters}
                className="px-3 py-1.5 text-sm text-einstein-gray-600 hover:text-einstein-gray-800 flex items-center gap-1"
              >
                <X className="h-3 w-3" />
                Clear
              </button>
            )}
          </div>

          {/* Stats */}
          <div className="mt-3 flex gap-4 text-xs text-einstein-gray-600">
            <span>Total: <strong>{stats.total}</strong></span>
            <span>SOP: <strong>{stats.sop}</strong></span>
            <span>FDA: <strong>{stats.fda}</strong></span>
          </div>
        </div>

        {/* Document List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="h-6 w-6 animate-spin text-einstein-blue" />
              <span className="ml-2 text-sm text-einstein-gray-600">Loading documents...</span>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-einstein-gray-500">
              <FileText className="h-10 w-10 text-einstein-gray-400 mx-auto mb-3" />
              <p className="text-sm font-medium">No documents found</p>
              <p className="text-xs mt-1">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {documents.map((doc, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className="bg-einstein-gray-50 rounded-lg border border-einstein-gray-200 hover:border-einstein-blue hover:shadow-sm transition-all"
                >
                  <div className="p-4">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {doc.document_type === 'sop' ? (
                            <FileCheck className="h-4 w-4 text-einstein-green" />
                          ) : (
                            <BookOpen className="h-4 w-4 text-einstein-blue" />
                          )}
                          <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                            doc.document_type === 'sop' 
                              ? 'bg-einstein-green-light text-einstein-green-dark' 
                              : 'bg-einstein-blue-light text-einstein-blue-dark'
                          }`}>
                            {doc.document_type === 'sop' ? 'SOP' : 'FDA'}
                          </span>
                        </div>
                        <h3 className="font-semibold text-sm text-einstein-gray-800 mb-1">
                          {doc.title}
                        </h3>
                        <p className="text-xs text-einstein-gray-500 font-mono truncate">
                          {doc.filename}
                        </p>
                      </div>
                    </div>

                    {/* Preview */}
                    {doc.preview && (
                      <p className="text-xs text-einstein-gray-600 line-clamp-2 mb-3">
                        {doc.preview}
                      </p>
                    )}

                    {/* Sections */}
                    {doc.sections && doc.sections.length > 0 && (
                      <div className="mb-3">
                        <button
                          onClick={() => toggleSection(index)}
                          className="flex items-center gap-1 text-xs text-einstein-gray-600 hover:text-einstein-blue transition-colors"
                        >
                          <ChevronRight 
                            className={`h-3 w-3 transition-transform ${expandedSections[index] ? 'rotate-90' : ''}`} 
                          />
                          <span>{doc.sections.length} section{doc.sections.length > 1 ? 's' : ''}</span>
                        </button>
                        {expandedSections[index] && (
                          <div className="mt-2 ml-4 space-y-1">
                            {doc.sections.map((section, secIdx) => (
                              <div key={secIdx} className="text-xs text-einstein-gray-600">
                                • {section.title}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Actions */}
                    <button
                      onClick={() => handleDocumentClick(doc)}
                      className="w-full text-xs px-3 py-2 bg-einstein-blue-light text-einstein-blue hover:bg-einstein-blue hover:text-white rounded-md transition-colors font-medium flex items-center justify-center gap-1.5"
                    >
                      <FileText className="h-3 w-3" />
                      View Document
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
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

