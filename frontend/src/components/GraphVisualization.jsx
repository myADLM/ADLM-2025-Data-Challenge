import { useMemo, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Network, ZoomIn, ZoomOut, RotateCcw, X } from 'lucide-react';
import ReactForceGraph2d from 'react-force-graph-2d';

export default function GraphVisualization({ graph, onClose, centerNode }) {
  const fgRef = useRef();

  // Parse relationships string format into graph data structure
  const graphData = useMemo(() => {
    if (!graph || (!graph.nodes && !graph.relationships)) return null;

    // If already structured (from API)
    if (graph.nodes && graph.edges) {
      return {
        nodes: graph.nodes.map(node => ({
          id: node.id || node,
          name: node.label || node.id || node,
          isCenter: node.isCenter || (centerNode && (node.id === centerNode || node.name === centerNode || node.label === centerNode)),
          ...node
        })),
        links: graph.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.type || edge.label || '',
          ...edge
        }))
      };
    }

    // Parse from relationships strings: "source -[rel_type]-> target"
    const nodes = new Map();
    const links = [];

    // Add nodes from entities
    if (graph.entities) {
      graph.entities.forEach(entity => {
        if (!nodes.has(entity)) {
          nodes.set(entity, {
            id: entity,
            name: entity,
            group: 1
          });
        }
      });
    }

    // Parse relationships
    if (graph.relationships) {
      graph.relationships.forEach(relStr => {
        const match = relStr.match(/^(.+?)\s+-\[(.+?)\]\->\s+(.+?)$/);
        if (match) {
          const [, source, relType, target] = match;
          const sourceName = source.trim();
          const targetName = target.trim();

          // Add nodes
          if (!nodes.has(sourceName)) {
            nodes.set(sourceName, {
              id: sourceName,
              name: sourceName,
              group: 1
            });
          }
          if (!nodes.has(targetName)) {
            nodes.set(targetName, {
              id: targetName,
              name: targetName,
              group: 2
            });
          }

          // Add link
          links.push({
            source: sourceName,
            target: targetName,
            label: relType.trim(),
            value: 1
          });
        }
      });
    }

    return {
      nodes: Array.from(nodes.values()),
      links: links
    };
  }, [graph]);

  const handleZoomIn = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoom(1.5, 300);
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoom(0.75, 300);
    }
  }, []);

  const handleReset = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
  }, []);

  if (!graphData || graphData.nodes.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="mb-8 bg-white rounded-xl border border-gray-200 overflow-hidden shadow-lg"
    >
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-bold text-gray-900">
            Knowledge Graph Visualization
          </h3>
          <span className="text-sm text-gray-600">
            ({graphData.nodes.length} nodes, {graphData.links.length} relationships)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4 text-blue-600" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4 text-blue-600" />
          </button>
          <button
            onClick={handleReset}
            className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
            title="Reset View"
          >
            <RotateCcw className="h-4 w-4 text-blue-600" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
              title="Close"
            >
              <X className="h-4 w-4 text-blue-600" />
            </button>
          )}
        </div>
      </div>

      <div className="relative bg-gray-50" style={{ height: '600px', width: '100%' }}>
        <ReactForceGraph2d
          ref={fgRef}
          graphData={graphData}
          nodeLabel="name"
          nodeAutoColorBy="group"
          linkLabel="label"
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}
          linkCurvature={0.15}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name || node.id;
            const fontSize = Math.max(10, 14 / Math.sqrt(globalScale));
            const nodeSize = node.isCenter ? 15 : 10;
            ctx.font = `bold ${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Draw node circle with border
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI);
            ctx.fillStyle = node.color || '#2563eb';
            ctx.fill();
            ctx.strokeStyle = node.isCenter ? '#ffffff' : '#ffffff';
            ctx.lineWidth = node.isCenter ? 3 : 2;
            ctx.stroke();
            
            // Draw label below node
            ctx.fillStyle = '#1f2937';
            ctx.fillText(label, node.x, node.y + nodeSize + 5);
          }}
          nodeCanvasObjectMode={() => 'after'}
          onNodeClick={(node) => {
            // Highlight node on click - could expand to show details
            console.log('Node clicked:', node);
          }}
          nodeColor={(node) => {
            // Highlight center node
            if (node.isCenter) {
              return '#dc2626'; // Red for center node
            }
            // Color nodes by type or group
            const colors = ['#2563eb', '#7c3aed', '#059669', '#ea580c', '#ca8a04'];
            return colors[(node.group || 0) % colors.length] || '#6b7280';
          }}
          linkColor={() => '#94a3b8'}
          linkWidth={2}
          nodeRelSize={(node) => node.isCenter ? 15 : 10}
          cooldownTicks={100}
          onEngineStop={() => {
            if (fgRef.current) {
              fgRef.current.zoomToFit(400, 20);
            }
          }}
        />
      </div>
    </motion.div>
  );
}

