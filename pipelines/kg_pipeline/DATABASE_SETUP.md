# Neo4j Database Isolation Guide

## Creating a Separate Database in Neo4j

To isolate your knowledge graph data from other databases in Neo4j, create a dedicated database.

### Prerequisites

- **Neo4j Community Edition** users: You can only use the default `neo4j` database

### Using Neo4j Browser
   - Navigate to `http://localhost:7474`
   - Log in with your credentials

## Configuring Your Pipeline

After creating the database, set it in your `.env` file:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=labdocs_kg  # Your new database name
```

All pipeline scripts (`02_load.py`, `03_refine.py`, `kg_query.py`) will automatically use this database.
