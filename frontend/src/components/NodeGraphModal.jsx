import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader, Network } from 'lucide-react';
import GraphVisualization from './GraphVisualization';
import { getNodeGraph } from '../services/api';

export default function NodeGraphModal({ nodeName, relationshipType, onClose }) {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!nodeName) return;

    const fetchGraph = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getNodeGraph(nodeName, relationshipType);
        setGraphData({
          nodes: data.graph.nodes || [],
          edges: data.graph.edges || [],
          centerNode: data.center_node
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [nodeName, relationshipType]);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Network className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {relationshipType ? `Relationships: ${relationshipType}` : `Node: ${nodeName}`}
                </h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  {relationshipType ? 'Connected nodes via this relationship' : 'Connected nodes and relationships'}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-3" />
                  <p className="text-sm text-gray-600">Loading graph...</p>
                </div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <p className="text-sm text-red-600 mb-2">Error loading graph</p>
                  <p className="text-xs text-gray-500">{error}</p>
                </div>
              </div>
            ) : graphData && graphData.nodes.length > 0 ? (
              <div className="h-full">
                <GraphVisualization graph={graphData} onClose={onClose} centerNode={graphData.centerNode} />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-sm text-gray-500">No connections found</p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

