# Quick Start Guide

Get a unified knowledge graph from laboratory documents in 4 steps.

## 1. Prepare Markdown Documents

Place your markdown files in a folder:
```
./data/parsed/LabDocs/
├── FDA/
│   ├── Device_A.md
│   └── Device_B.md
└── Procedures/
    ├── SOP_Test1.md
    └── SOP_Test2.md
```

## 2. Extract Entities & Relationships

Run extraction with unified ontology:

```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs \
  --output-dir ./graphdb_unified
```

Output: `graphdb_unified/extractions/*.json` with entities and relationships

### Options
- `--max-docs 10` - Limit to first 10 documents (for testing)
- `--max-docs 0` - Process all documents (default)

## 3. Load into Neo4j

```bash
uv run python pipelines/kg_pipeline/02_load.py \
  --extraction-dir ./graphdb_unified/extractions
```

This:
- Creates nodes for all entities
- Builds relationships
- Generates embeddings for semantic search
- Deduplicates similar entities

## 4. Query the Graph

Via Flask API:
```bash
./start.sh
```
Then open `http://localhost:3001`

Or directly in Neo4j Browser (`http://localhost:7687`):

## Learn More

- **[EXTRACTION_GUIDE.md](./EXTRACTION_GUIDE.md)** - Complete extraction reference
- **[UNIFIED_GRAPH_GUIDE.md](./UNIFIED_GRAPH_GUIDE.md)** - Advanced queries and patterns
- **[HOWTO.md](./HOWTO.md)** - Full workflow from PDFs to Neo4j
