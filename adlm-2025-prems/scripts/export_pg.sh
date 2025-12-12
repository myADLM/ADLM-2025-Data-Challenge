#!/bin/bash
# cargo install pg2parquet
pg2parquet export --host localhost --dbname postgres --output-file exports/documents.parquet -t api_document
pg2parquet export --host localhost --dbname postgres --output-file exports/chunks.parquet -t api_chunk
pg2parquet export --host localhost --dbname postgres --output-file exports/entities.parquet -t graph_entity
pg2parquet export --host localhost --dbname postgres --output-file exports/nodes.parquet -t graph_node
pg2parquet export --host localhost --dbname postgres --output-file exports/relationships.parquet -t graph_relationship
pg2parquet export --host localhost --dbname postgres --output-file exports/labels.parquet -t graph_label