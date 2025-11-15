import { motion } from 'framer-motion';
import { Network, FileText, ArrowRight, Heart, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import GraphVisualization from './GraphVisualization';
import PathVisualization from './PathVisualization';
import { useState } from 'react';

export default function ResultDisplay({ result, onDocumentClick, onFavoriteClick, isFavorited }) {
  const [showGraph, setShowGraph] = useState(false);
  const [activeTab, setActiveTab] = useState('results'); // 'results' or 'graph'
  // Extract potential document references from entities
  // Look for entities that might be document names (contain keywords like SOP, assay names, etc.)
  const extractDocumentReferences = (entities) => {
    if (!entities || entities.length === 0) return [];
    
    // More strict filtering - only entities that are very likely to be document names
    const documentKeywords = ['serum', 'plasma', 'assay', 'test', 'procedure'];
    const references = entities
      .filter(entity => {
        const entityLower = entity.toLowerCase();
        // Must contain document keywords AND either:
        // - Start with a number (like "11-Deoxycortisol Serum")
        // - Contain underscores (document ID format)
        // - Be longer than 10 chars (likely a procedure name, not equipment)
        const hasKeyword = documentKeywords.some(keyword => entityLower.includes(keyword));
        const looksLikeDoc = entity.match(/^\d/) || // Starts with number
                            entity.includes('_') || // Has underscores
                            (entity.length > 10 && !entityLower.includes('instrument') && !entityLower.includes('equipment')); // Long name, not equipment
        
        return hasKeyword && looksLikeDoc;
      })
      .slice(0, 10) // Limit to 10 references
      .map(entity => {
        // Extract core assay name from long procedure descriptions
        // Example: "Standard Operating Procedure for Analytical Phase of 11-Deoxycorticosterone, Serum Testing"
        // Should become: "11-DEOXYCORTICOSTERONE_SERUM.md"
        
        let filename = entity.trim();
        
        // Try to extract number-prefixed assay name (like "11-Deoxycorticosterone")
        // Match pattern: number followed by assay name, then comma/semicolon or specimen type
        // Improved regex to capture up to comma or specimen type
        const numberMatch = filename.match(/(\d+[-_]?\s*[A-Za-z][A-Za-z0-9\s-]*?)(?:[,;]|\s+(?:serum|plasma|blood|urine|csf|tissue|varies|testing|test))/i);
        if (numberMatch) {
          let assayName = numberMatch[1].trim();
          
          // Extract specimen type (look for it after the assay name)
          const afterMatch = filename.substring(filename.indexOf(numberMatch[0]) + numberMatch[0].length);
          const specimenMatch = afterMatch.match(/\b(serum|plasma|blood|urine|csf|cerebrospinal\s+fluid|tissue|varies|meconium|amniotic\s+fluid|pleural\s+fluid|pericardial\s+fluid|peritoneal\s+fluid|synovial\s+fluid|spinal\s+fluid)\b/i);
          let specimenType = '';
          if (specimenMatch) {
            specimenType = specimenMatch[1].toUpperCase().replace(/\s+/g, '_');
            // Handle special cases
            if (specimenType.includes('CEREBROSPINAL')) specimenType = 'CSF';
            if (specimenType.includes('AMNIOTIC')) specimenType = 'AMNIOTIC_FLUID';
            if (specimenType.includes('PLEURAL')) specimenType = 'PLEURAL_FLUID';
            if (specimenType.includes('PERICARDIAL')) specimenType = 'PERICARDIAL_FLUID';
            if (specimenType.includes('PERITONEAL')) specimenType = 'PERITONEAL_FLUID';
            if (specimenType.includes('SYNOVIAL')) specimenType = 'SYNOVIAL_FLUID';
            if (specimenType.includes('SPINAL') && !specimenType.includes('CSF')) specimenType = 'SPINAL_FLUID';
          }
          
          // Normalize assay name: uppercase, replace spaces/dashes with underscores, but keep number-dash pattern
          assayName = assayName.toUpperCase();
          // Handle number-dash pattern: "11-Deoxycorticosterone" -> "11-DEOXYCORTICOSTERONE"
          if (assayName.match(/^\d+\s*-/)) {
            // Has number-space-dash, normalize to number-dash
            assayName = assayName.replace(/^(\d+)\s*-\s*/, '$1-');
            // Replace remaining spaces with underscores
            assayName = assayName.replace(/\s+/g, '_');
          } else if (assayName.match(/^\d+-/)) {
            // Already has number-dash, just normalize spaces to underscores
            const parts = assayName.split('-');
            if (parts.length > 1) {
              assayName = parts[0] + '-' + parts.slice(1).join('_').replace(/\s+/g, '_');
            }
          } else {
            // No number-dash pattern, replace all spaces/dashes with underscores
            assayName = assayName.replace(/[\s-]+/g, '_');
          }
          
          // Remove commas and clean up
          assayName = assayName.replace(/[,;]/g, '').replace(/_+/g, '_').trim();
          
          // Combine: number-ASSAYNAME_SPECIMEN.md
          filename = assayName;
          if (specimenType && !filename.includes(specimenType)) {
            filename = filename + '_' + specimenType;
          }
        } else {
          // Fallback: try to extract just the number-prefixed part
          const simpleMatch = filename.match(/(\d+[-_]?\s*[A-Za-z][A-Za-z0-9\s-]+)/i);
          if (simpleMatch) {
            filename = simpleMatch[1].toUpperCase();
            // Preserve number-dash pattern
            if (filename.match(/^\d+\s*-/)) {
              filename = filename.replace(/^(\d+)\s*-\s*/, '$1-').replace(/\s+/g, '_');
            } else if (filename.match(/^\d+-/)) {
              const parts = filename.split('-');
              if (parts.length > 1) {
                filename = parts[0] + '-' + parts.slice(1).join('_').replace(/\s+/g, '_');
              }
            } else {
              filename = filename.replace(/[\s-]+/g, '_');
            }
          } else {
            // Last resort: normalize the whole thing
            filename = filename.toUpperCase().replace(/[\s-]+/g, '_');
          }
        }
        
        // Remove common prefixes
        filename = filename.replace(/^(STANDARD_OPERATING_PROCEDURE_FOR_|SOP_|ASSAY_|PROCEDURE_|ANALYTICAL_PHASE_OF_|PHASE_OF_)/i, '');
        
        // Clean up: remove trailing underscores, commas, etc.
        filename = filename.replace(/[,;]/g, '').replace(/_+/g, '_').replace(/_TESTING$|_TEST$/, '').replace(/^_+|_+$/g, '');
        
        // Ensure it ends with .md
        if (!filename.endsWith('.md')) {
          filename = filename + '.md';
        }
        
        return {
          filename: filename,
          title: entity,
          preview: `Entity from knowledge graph: ${entity}`,
          filepath: `./data/parsed/LabDocs/Procedures/${filename}`
        };
      });
    
    return references;
  };

  const documentReferences = extractDocumentReferences(result.entities);

  // Get path for a document reference if available
  const getPathForDocument = (entityTitle) => {
    if (result.document_paths && result.document_paths[entityTitle]) {
      return result.document_paths[entityTitle];
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Tabs */}
      {result.graph && (result.graph.nodes || result.graph.relationships) && (
        <div className="mb-6 border-b border-gray-200">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('results')}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'results'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Results
            </button>
            <button
              onClick={() => setActiveTab('graph')}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'graph'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Network className="h-4 w-4" />
              Graph View
            </button>
          </div>
        </div>
      )}

      {activeTab === 'results' && (
        <>
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
                  {result.answer}
                </ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Reference Documents Section */}
          {documentReferences && documentReferences.length > 0 ? (
            <div className="mb-8">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <FileText className="h-5 w-5 text-blue-500 mr-2" />
                Reference Documents ({documentReferences.length})
              </h3>

              <div className="space-y-4">
                {documentReferences.map((doc, index) => {
                  const path = getPathForDocument(doc.title);
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-gray-50 rounded-xl p-5 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-300"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          {/* Title */}
                          <div className="flex items-center gap-3 mb-2 flex-wrap">
                            <h4 className="font-semibold text-gray-900 text-sm">{doc.title}</h4>
                          </div>

                          {/* Graph Path Visualization */}
                          {path && <PathVisualization path={path} />}

                          {/* Filepath */}
                          <p className="text-xs text-gray-500 mb-3 font-mono break-all mt-3">
                            {doc.filepath}
                          </p>

                          {/* Preview */}
                          <div className="bg-white border border-gray-200 rounded-lg p-4 mb-3">
                            <p className="text-gray-700 text-sm italic">"{doc.preview}..."</p>
                          </div>

                          {/* Actions */}
                          <div className="flex gap-2 flex-wrap">
                            <button
                              onClick={() => onDocumentClick(doc)}
                              className="text-xs px-3 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors font-medium flex items-center gap-1"
                            >
                              <ArrowRight className="h-3 w-3" />
                              View Full
                            </button>
                            <button
                              onClick={() => onFavoriteClick(doc.filename)}
                              className={`text-xs px-3 py-2 rounded-lg transition-colors font-medium flex items-center gap-1 ${
                                isFavorited(doc.filename)
                                  ? 'bg-red-50 text-red-600 hover:bg-red-100'
                                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                              }`}
                            >
                              <Heart className={`h-3 w-3 ${isFavorited(doc.filename) ? 'fill-current' : ''}`} />
                              {isFavorited(doc.filename) ? 'Saved' : 'Save'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          ) : null}

          {/* Entities Section */}
          {result.entities && result.entities.length > 0 ? (
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Network className="h-5 w-5 text-blue-500 mr-2" />
                Related Entities ({result.entities.length})
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {result.entities.map((entity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-blue-50 rounded-lg p-3 border border-blue-100 hover:border-blue-300 hover:shadow-md transition-all duration-300"
                  >
                    <p className="text-sm font-medium text-gray-900 truncate">{entity}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          ) : null}
        </>
      )}

      {activeTab === 'graph' && result.graph && (
        <GraphVisualization graph={result.graph} />
      )}
    </motion.div>
  );
}

