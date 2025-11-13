import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Loader, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { parseMarkdownDocument, extractMetadataFields } from '../utils/markdown';
import { fetchDocument as apiFetchDocument } from '../services/api';

export default function DocumentViewer({ document, segment, onClose }) {
  const [content, setContent] = useState('');
  const [parsed, setParsed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (document.content) {
      // Document already has content loaded
      setContent(document.content);
      const parsed = parseMarkdownDocument(document.content);
      setParsed(parsed);
      setLoading(false);
    } else {
      // Need to fetch document
      fetchDocument();
    }
  }, [document]);

  const fetchDocument = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiFetchDocument(
        document.filename,
        document.filepath || '',
        segment ? segment.text : ''
      );
      
      const fullContent = data.content || document.preview;
      if (!fullContent) {
        throw new Error('Document content is empty');
      }
      
      setContent(fullContent);

      // Parse markdown to extract metadata and clean content
      const parsed = parseMarkdownDocument(fullContent);
      setParsed(parsed);
    } catch (err) {
      console.error('Error fetching document:', err);
      setError(err.message || 'Failed to load document');
      setContent(document.preview || '');
      setParsed(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col border border-gray-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-bold text-gray-900 truncate">{document.title || document.filename}</h2>
            <p className="text-xs text-gray-600 mt-1 font-mono truncate">{document.filepath}</p>
            {segment && (
              <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                <p className="font-semibold mb-1">Related Segment:</p>
                <p className="italic">{segment.text}</p>
              </div>
            )}
            {document.score && (
              <p className="text-xs text-blue-600 mt-2">
                Relevance: {Math.round(document.score * 100)}%
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors ml-4 flex-shrink-0"
          >
            <X className="h-6 w-6 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-white">
          {loading && (
            <div className="text-center py-12">
              <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Loading document...</p>
            </div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl flex items-start gap-3 text-yellow-700 mb-4"
            >
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </motion.div>
          )}

          {parsed && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {/* Metadata Section */}
              {Object.keys(parsed.metadata).length > 0 && (
                <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-3">
                  {extractMetadataFields(parsed.metadata).map((field) => (
                    <div key={field.key} className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
                      <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-1">
                        {field.label}
                      </p>
                      <p className="text-sm text-gray-900 font-medium">
                        {field.value}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Markdown Content */}
              <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-headings:font-bold prose-a:text-blue-600 prose-a:underline prose-code:bg-gray-100 prose-code:text-gray-900 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-ul:list-disc prose-ol:list-decimal">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({node, ...props}) => <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4 border-b pb-2" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-xl font-bold text-gray-900 mt-6 mb-3 text-blue-700" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props} />,
                    p: ({node, ...props}) => <p className="text-gray-700 leading-relaxed mb-3" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 space-y-1 text-gray-700" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-700" {...props} />,
                    li: ({node, ...props}) => <li className="ml-2 text-gray-700" {...props} />,
                    blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-blue-400 pl-4 py-2 italic text-gray-600 mb-3" {...props} />,
                    code: ({node, inline, ...props}) => inline
                      ? <code className="bg-gray-100 px-2 py-1 rounded text-gray-900 font-mono text-sm" {...props} />
                      : <code className="block bg-gray-100 p-4 rounded-lg overflow-x-auto mb-3 text-gray-900 font-mono text-sm" {...props} />,
                    table: ({node, ...props}) => <table className="w-full border-collapse mb-4 mt-4 shadow-sm" {...props} />,
                    thead: ({node, ...props}) => <thead className="bg-gray-100 border-b-2 border-gray-300" {...props} />,
                    tbody: ({node, ...props}) => <tbody className="bg-white" {...props} />,
                    tr: ({node, ...props}) => <tr className="border-b border-gray-200 hover:bg-gray-50" {...props} />,
                    th: ({node, ...props}) => <th className="border border-gray-300 px-4 py-2 text-left font-semibold text-gray-900" {...props} />,
                    td: ({node, ...props}) => <td className="border border-gray-300 px-4 py-2 text-gray-700" {...props} />,
                  }}
                >
                  {parsed.content}
                </ReactMarkdown>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

