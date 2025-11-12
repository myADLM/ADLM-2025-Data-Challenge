import { motion } from 'framer-motion';
import { FileText, Heart, ArrowRight, AlertCircle } from 'lucide-react';

export default function ResultDisplay({ result, onDocumentClick, onFavoriteClick, isFavorited }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Question Display */}
      <div className="mb-8 p-4 bg-blue-50 rounded-xl border border-blue-100">
        <p className="text-sm text-blue-600 font-medium mb-1">Your Question</p>
        <p className="text-gray-900 font-medium">{result.question}</p>
      </div>

      {/* Answer Section */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
          Answer
        </h2>
        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <p className="text-gray-800 leading-relaxed text-base whitespace-pre-wrap">
            {result.answer}
          </p>
        </div>
      </div>

      {/* Sources Section */}
      {result.sources && result.sources.length > 0 ? (
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <FileText className="h-5 w-5 text-blue-500 mr-2" />
            Verified Sources ({result.sources.length})
          </h3>

          <div className="space-y-4">
            {result.sources.map((source, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-50 rounded-xl p-5 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-300"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    {/* Relevance Badge and Filename */}
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <div className="bg-blue-100 text-blue-800 text-xs font-medium px-3 py-1 rounded-full">
                        Relevance: {Math.round(source.score * 100)}%
                      </div>
                      <h4 className="font-semibold text-gray-900 text-sm">{source.filename}</h4>
                    </div>

                    {/* Filepath */}
                    <p className="text-xs text-gray-500 mb-3 font-mono break-all">
                      {source.filepath}
                    </p>

                    {/* Preview */}
                    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-3">
                      <p className="text-gray-700 text-sm italic">"{source.preview}..."</p>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 flex-wrap">
                      <button
                        onClick={() => onDocumentClick(source)}
                        className="text-xs px-3 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors font-medium flex items-center gap-1"
                      >
                        <ArrowRight className="h-3 w-3" />
                        View Full
                      </button>
                      <button
                        onClick={() => onFavoriteClick(source.filename)}
                        className={`text-xs px-3 py-2 rounded-lg transition-colors font-medium flex items-center gap-1 ${
                          isFavorited(source.filename)
                            ? 'bg-red-50 text-red-600 hover:bg-red-100'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        <Heart className={`h-3 w-3 ${isFavorited(source.filename) ? 'fill-current' : ''}`} />
                        {isFavorited(source.filename) ? 'Saved' : 'Save'}
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl flex items-start gap-3 text-yellow-700"
        >
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <p className="text-sm">No sources found for this query.</p>
        </motion.div>
      )}
    </motion.div>
  );
}
