import { motion } from 'framer-motion';
import { Clock, X } from 'lucide-react';

export default function SearchHistory({ history, onSelect }) {
  if (!history || history.length === 0) {
    return null;
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

    return date.toLocaleDateString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mt-6 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200"
    >
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Clock className="h-4 w-4 text-blue-600" />
        Recent Searches
      </h3>

      <div className="space-y-2 max-h-80 overflow-y-auto">
        {history.map((item, index) => (
          <motion.button
            key={item.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => onSelect(item.query)}
            className="w-full text-left p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors border border-gray-200 group"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <p className="text-sm text-gray-900 font-medium truncate group-hover:text-blue-600">
                  {item.query}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatTime(item.timestamp)} • {item.sourceCount} sources
                </p>
              </div>
            </div>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}
