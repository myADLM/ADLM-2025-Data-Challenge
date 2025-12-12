# Knowledge Graph Extraction Guide

This guide explains how to use the extraction system to build a unified knowledge graph from laboratory documentation (FDA regulatory submissions and Standard Operating Procedures).

## Overview

The extraction pipeline uses a **unified ontology** that captures entities and relationships from both FDA regulatory documents (510(k) clearances) and SOP (Standard Operating Procedures) documents in a single, integrated knowledge graph.

### Key Features

- **Single unified schema** - handles both FDA and SOP documents
- **Cross-document linking** - automatically identifies relationships between regulatory and procedural information
- **Document type tracking** - maintains metadata distinguishing FDA from SOP sources
- **Comprehensive entity coverage** - 30+ entity types covering devices, procedures, assays, and regulatory information
- **Relationship preservation** - 50+ relationship types capturing complex interdependencies

## Unified Ontology

The unified ontology combines entity types relevant to both FDA regulatory and laboratory operational contexts.

### Entity Types

**Regulatory & Device Entities:**
- `FDADocument` - FDA regulatory submission or clearance document
- `Device` - Medical device or laboratory equipment
- `Manufacturer` - Device/reagent manufacturer
- `ProductCode` - FDA product classification code
- `Classification` - Device class (I, II, III)
- `RegulatorySection` - CFR regulation section

**Laboratory Procedure Entities:**
- `SOP` - Standard Operating Procedure document
- `Assay` - Analytical method or test procedure
- `Analyte` - Biomarker or substance being measured
- `SpecimenType` - Sample type (serum, plasma, urine, CSF, etc.)

**Technical/Equipment Entities:**
- `Instrument` - Laboratory equipment or platform
- `ReagentKit` - Chemical reagents or test reagents
- `Calibrator` - Calibration material or standard
- `Control` - Quality control material
- `Standard` - Referenced standard (ISO, CLSI, etc.)

**Measurement & Performance Entities:**
- `Measurand` - Biomarker measured by device or assay
- `TestType` - Type of diagnostic test (CMIA, ELISA, PCR, etc.)
- `IntendedUse` - Intended purpose or clinical indication
- `PerformanceCharacteristic` - Analytical or clinical performance data
- `ClinicalStudy` - Supporting clinical evidence

**Organizational & Reference Entities:**
- `ProcedureStep` - Discrete procedural step
- `Guideline` - Referenced standard or guideline
- `GuidanceDocument` - FDA guidance document
- `PredicateDevice` - Device claimed as 510(k) predicate
- `Panel` - FDA review panel

### Relationship Types

**Device-Related Relationships:**
- `DEVICE_IMPLEMENTS_ASSAY` - FDA device has corresponding SOP procedure
- `DEVICE_MANUFACTURES` - Company manufactures device
- `DEVICE_HAS_PRODUCT_CODE` - Device has FDA product code
- `DEVICE_ANALYZES_SPECIMEN` - Device analyzes specimen type
- `DEVICE_MEASURES_ANALYTE` - Device measures specific analyte

**Procedure-Related Relationships:**
- `SOP_DESCRIBES_ASSAY` - SOP describes analytical method
- `SOP_IMPLEMENTS_DEVICE` - SOP procedure follows device requirements
- `ASSAY_DETECTS_ANALYTE` - Assay detects specific analyte
- `ASSAY_USES_SPECIMEN` - Assay requires specimen type
- `ASSAY_RUNS_ON_INSTRUMENT` - Assay uses specific instrument

**Equipment & Reagent Relationships:**
- `USES_REAGENT` - Procedure uses specific reagents
- `USES_INSTRUMENT` - Procedure uses specific equipment
- `INSTRUMENT_MANUFACTURER` - Equipment manufacturer
- `REAGENT_MANUFACTURER` - Reagent manufacturer

**Cross-Document Relationships:**
- `DEVICE_IMPLEMENTS_ASSAY` - FDA device has SOP implementation
- `ASSAY_IMPLEMENTS_DEVICE` - SOP implements FDA device
- `MEASURAND_IS_ANALYTE` - Same biomarker in regulatory and operational contexts
- `SPECIMEN_TYPE_MATCH` - Device and SOP use same sample type
- `INSTRUMENT_COMPATIBILITY` - Both reference same equipment platform

**Regulatory & Standard Relationships:**
- `REGULATED_BY_SECTION` - Governed by regulatory section
- `FOLLOWS_STANDARD` - Implements standard (ISO, CLSI, etc.)
- `REFERENCES_GUIDELINE` - References FDA guidance
- `PREDICATE_DEVICE_RELATIONSHIP` - 510(k) predicate device

## Usage

### Basic Extraction

Extract entities and relationships from markdown documents using the unified ontology:

```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs/Procedures \
  --output-dir ./graphdb_unified
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-folder` | Directory containing markdown documents | Required |
| `--output-dir` | Output directory for JSON extractions | Required |
| `--max-docs` | Limit number of documents to process (0 = all) | 0 |

### Examples

**Extract from FDA regulatory documents:**
```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs/FDA \
  --output-dir ./graphdb_unified
```

**Extract from SOP procedures:**
```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs/Procedures \
  --output-dir ./graphdb_unified
```

**Extract with limit for testing:**
```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs \
  --output-dir ./graphdb_unified \
  --max-docs 10
```

### Output Files

The extraction process generates JSON files in the `--output-dir/extractions/` directory:

```
./graphdb_unified/extractions/
├── FDA_document_1.json
├── SOP_document_1.json
├── SOP_document_2.json
└── ...
```

Each JSON file contains:
- **entities** - Extracted entities with types, IDs, and properties
- **relationships** - Relationships between entities with supporting source text
- **source_document** - Reference to the original markdown file
- **document_type** - Type indicator ("fda" or "sop")

### JSON Output Structure

```json
{
  "source_document": "path/to/markdown/file.md",
  "entities": [
    {
      "@id": "ASSAY_Example_Test",
      "@type": "Assay",
      "title": "Example Test",
      "description": "Description of the assay",
      "doc_type": "sop",
      "relations": [
        {
          "predicate": "ASSAY_USES_SPECIMEN",
          "object": "SPECIMEN_SERUM",
          "source_text": "Supporting text from document"
        }
      ]
    }
  ],
  "relationships": []
}
```

## Entity ID Conventions

Entity IDs follow a canonical pattern: `TYPE_CanonicalName`

**FDA Documents:**
```
FDA_DOC_K<number>           # FDA 510(k) submission
DEVICE_<DeviceName>         # Medical device
MANUFACTURER_<CompanyName>  # Device manufacturer
MEASURAND_<BiomarkerName>   # Measured analyte
```

**SOP Documents:**
```
SOP_<ProcedureName>         # Standard operating procedure
ASSAY_<AssayName>           # Analytical method
ANALYTE_<AnalyteName>       # Substance being measured
SPECIMEN_<SpecimenType>     # Sample type
```

**Shared Entity Types:**
```
INSTRUMENT_<EquipmentName>  # Laboratory equipment
REAGENT_<ReagentName>       # Chemical reagent or kit
STANDARD_<StandardName>     # Reference standard
CONTROL_<ControlType>       # QC material
```

### ID Guidelines

- Use full names, not abbreviations
- Use PascalCase or underscores for readability
- Ensure consistency - same entity always has same ID
- If an entity appears in multiple documents, use identical ID across documents

## Schema Files

**Location:** `src/labdocs/prompts/`

- **unified_ontology_schema.json** - Complete entity and relationship types
- **unified_kg_extraction_user.j2** - Extraction prompt template
- **unified_kg_extraction_system.j2** - System instructions (reference only, merged into user template)


## Validation
Extracted entities are validated to ensure:
- All entity IDs match the canonical format
- All entity types exist in the schema
- All relationships connect valid entity types
- Source text is provided for traceability

## Integration with Graph Loading

After extraction, load the JSON files into Neo4j:

```bash
uv run python pipelines/kg_pipeline/02_load.py \
  --extraction-dir ./graphdb_unified/extractions
```

This will:
- Create nodes for all extracted entities
- Create relationships between entities
- Generate embeddings for semantic search
- Deduplicate similar entities
- Build the searchable knowledge graph

## Document Type Tracking

Each extracted entity includes a `doc_type` field indicating its source:

```json
{
  "@id": "ASSAY_Vitamin_D_Test",
  "@type": "Assay",
  "doc_type": "sop",  // "fda" or "sop"
  ...
}
```

This enables:
- Filtering queries by document type
- Identifying cross-document relationships
- Tracing entity provenance
- Analyzing regulatory vs. operational contexts
