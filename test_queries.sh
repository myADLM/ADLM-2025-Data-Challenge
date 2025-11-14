#!/bin/bash
# test queries for the knowledge graph query system
# based on actual entities and relationships in neo4j

echo "==============================================="
echo "Test Query 1"
echo "What instruments are used in the 11-Deoxycorticosterone serum testing procedure?"
uv run pipelines/kg_pipeline/kg_query.py --query "What instruments are used in the 11-Deoxycorticosterone serum testing procedure?"

echo ""
echo "=========================================="
echo "Test Query 2"
echo "What is the Philips IntelliSite Pathology Solution device and what is its FDA classification?"
uv run pipelines/kg_pipeline/kg_query.py --query "What is the Philips IntelliSite Pathology Solution device and what is its FDA classification?"

echo ""
echo "=========================================="
echo "Test Query 3"
echo "What are the procedure steps for 25-Hydroxyvitamin D analysis?"
uv run pipelines/kg_pipeline/kg_query.py --query "What are the procedure steps for 25-Hydroxyvitamin D analysis?"
