import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import { useState } from 'react';

export default function PathVisualization({ path, onNodeClick, onRelationshipClick }) {
  const [expanded, setExpanded] = useState(false);
  
  if (!path || !path.nodes || path.nodes.length === 0) {
    return null;
  }

  const nodes = path.nodes;
  const relationships = path.relationships || [];
  const isLongPath = nodes.length > 4;

  // Extract meaningful document organization from nodes
  const getDocumentLevel = (node, index) => {
    const nodeLower = node.toLowerCase();
    
    // Determine the organizational level
    if (index === 0) return { level: 'query', label: 'Query' };
    if (index === nodes.length - 1) return { level: 'document', label: 'Document' };
    
    // Map entity types to organizational levels
    if (nodeLower.includes('sop') || nodeLower.includes('procedure')) {
      return { level: 'procedure', label: 'Procedure' };
    }
    if (nodeLower.includes('step')) {
      return { level: 'step', label: 'Step' };
    }
    if (nodeLower.includes('assay') || nodeLower.includes('test')) {
      return { level: 'assay', label: 'Assay' };
    }
    if (nodeLower.includes('instrument') || nodeLower.includes('equipment')) {
      return { level: 'instrument', label: 'Instrument' };
    }
    if (nodeLower.includes('reagent') || nodeLower.includes('standard')) {
      return { level: 'reagent', label: 'Reagent' };
    }
    
    return { level: 'entity', label: 'Entity' };
  };

  // Simplify node names to show organization
  const simplifyNodeName = (node, level) => {
    // For document organization, show the type/category rather than full name
    if (level === 'document') {
      // Extract document type from name
      if (node.toLowerCase().includes('serum')) return 'Serum Analysis';
      if (node.toLowerCase().includes('plasma')) return 'Plasma Analysis';
      if (node.toLowerCase().includes('fda')) return 'FDA Document';
      return 'Document';
    }
    
    if (level === 'procedure') {
      return 'Procedure';
    }
    
    if (level === 'step') {
      return 'Process Step';
    }
    
    if (level === 'assay') {
      return 'Assay';
    }
    
    if (level === 'instrument') {
      return 'Instrument';
    }
    
    if (level === 'reagent') {
      return 'Reagent';
    }
    
    return level.charAt(0).toUpperCase() + level.slice(1);
  };

  const displayNodes = isLongPath && !expanded ? [...nodes.slice(0, 2), '...', ...nodes.slice(-2)] : nodes;

  const handleNodeClick = (node, actualIndex) => {
    if (onNodeClick && actualIndex > 0 && actualIndex < nodes.length - 1) {
      // Don't allow clicking on query or document nodes
      onNodeClick(node);
    }
  };

  const handleRelationshipClick = (rel, sourceNode, targetNode) => {
    if (onRelationshipClick) {
      onRelationshipClick(rel, sourceNode, targetNode);
    }
  };

  return (
    <div className="mt-3">
      <div className="bg-gray-50/50 rounded-lg border border-gray-200/60 p-3">
        {/* Minimal header */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">
            Document Path
          </span>
          {isLongPath && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-[11px] text-gray-400 hover:text-gray-600 font-medium transition-colors"
            >
              {expanded ? 'Show less' : `Show all (${nodes.length})`}
            </button>
          )}
        </div>
        
        {/* Path visualization - Apple-like minimal design */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {displayNodes.map((node, displayIndex) => {
            if (node === '...') {
              return (
                <div key="ellipsis" className="px-2 text-gray-300 text-xs">
                  ···
                </div>
              );
            }
            
            const actualIndex = isLongPath && !expanded && displayIndex > 1 
              ? nodes.length - (displayNodes.length - displayIndex)
              : displayIndex;
            
            const { level, label } = getDocumentLevel(node, actualIndex);
            const simplifiedLabel = simplifyNodeName(node, level);
            const rel = relationships[actualIndex];
            const nextNode = actualIndex < nodes.length - 1 ? nodes[actualIndex + 1] : null;
            const isClickable = onNodeClick && actualIndex > 0 && actualIndex < nodes.length - 1;
            
            return (
              <div key={actualIndex} className="flex items-center gap-1.5 flex-shrink-0">
                {/* Node - minimal Apple-style */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: actualIndex * 0.03 }}
                  onClick={() => handleNodeClick(node, actualIndex)}
                  className={`
                    px-2.5 py-1 rounded-md text-xs font-medium
                    transition-all duration-200
                    ${
                      level === 'query' 
                        ? 'bg-blue-50 text-blue-700 border border-blue-200/50' 
                        : level === 'document'
                        ? 'bg-gray-900 text-white'
                        : 'bg-white text-gray-700 border border-gray-200/60'
                    }
                    ${isClickable ? 'cursor-pointer hover:shadow-sm hover:scale-105' : ''}
                  `}
                  title={isClickable ? `Click to explore: ${node}` : node}
                >
                  {simplifiedLabel}
                </motion.div>
                
                {/* Connection */}
                {displayIndex < displayNodes.length - 1 && displayNodes[displayIndex + 1] !== '...' && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: actualIndex * 0.03 + 0.02 }}
                    className="flex items-center gap-1"
                  >
                    {rel && (
                      <span 
                        onClick={() => handleRelationshipClick(rel, node, nextNode)}
                        className={`text-[10px] text-gray-400 italic px-1.5 ${
                          onRelationshipClick ? 'cursor-pointer hover:text-gray-600 hover:underline' : ''
                        }`}
                        title={onRelationshipClick ? `Click to explore relationship: ${rel}` : rel.replace(/_/g, ' ').toLowerCase()}
                      >
                        {rel.replace(/_/g, ' ').toLowerCase()}
                      </span>
                    )}
                    <ChevronRight className="h-3 w-3 text-gray-300 flex-shrink-0" />
                  </motion.div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Subtle metadata */}
        <div className="mt-2.5 pt-2.5 border-t border-gray-100">
          <div className="flex items-center gap-3 text-[10px] text-gray-400">
            <span>{nodes.length} level{nodes.length !== 1 ? 's' : ''}</span>
            {relationships.length > 0 && (
              <>
                <span>·</span>
                <span>{relationships.length} connection{relationships.length !== 1 ? 's' : ''}</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
