# Unified Knowledge Graph Guide

Use a **single graph** containing both SOP and FDA documents for cross-document queries.

## Quick Start

```bash
# Extract all SOP and FDA documents into unified graph
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs \
  --output-dir ./graphdb_unified
```

Output:
- `graphdb_unified/extractions/` - JSON files with entities and relationships
- Each entity includes `doc_type` field ("fda" or "sop")
- Cross-document relationships automatically generated

## Architecture

### Unified Schema Contains

**33 Entity Types:**
- FDA entities: FDADocument, Device, Measurand, TestType, Manufacturer, ProductCode, Classification, RegulatorySection, Panel, IntendedUse, Indication, PredicateDevice, PerformanceCharacteristic, ClinicalStudy, GuidanceDocument
- SOP entities: SOP, Assay, Analyte, SpecimenType, ProcedureStep, ResultInterpretation, CutoffValue, PatientPopulation, Limitation
- Shared entities: Instrument, Reagent, ReagentKit, Calibrator, Control, ControlType, Guideline, Standard, ReferenceDocument

**57 Relationship Types:**
- FDA relationships: DOCUMENT_DESCRIBES_DEVICE, DEVICE_HAS_MEASURAND, DEVICE_COMPARED_TO_PREDICATE
- SOP relationships: SOP_DESCRIBES_ASSAY, ASSAY_HAS_PROCEDURE_STEP, STEP_PRECEDES
- **Cross-document relationships:**
  - `DEVICE_IMPLEMENTS_ASSAY`: FDA device has corresponding SOP procedure
  - `ASSAY_IMPLEMENTS_DEVICE`: SOP assay implements FDA device
  - `MEASURAND_IS_ANALYTE`: Same biomarker in regulatory and operational contexts
  - `SOP_IMPLEMENTS_DEVICE`: SOP follows FDA device requirements
  - `ASSAY_FOLLOWS_SOP`: Procedure has formal documented SOP

### Document Type Tracking

Every entity includes `doc_type`:
```json
{
  "@id": "DEVICE_ARCHITECT_SHBG",
  "@type": "Device",
  "title": "Architect SHBG Assay",
  "doc_type": "fda",  // marks source document type
  "relations": [...]
}
```

## CSV Data Structure

### entities.csv
| entity_id | entity_type | title | description | doc_type | source_document |
|-----------|-------------|-------|-------------|----------|-----------------|
| FDA_DOC_K060818 | FDADocument | 510(k) K060818 | SHBG assay submission | fda | K060818_REVIEW.md |
| DEVICE_ARCHITECT_SHBG | Device | Architect SHBG Assay | FDA device submission | fda | K060818_REVIEW.md |
| ASSAY_SHBG_Serum | Assay | SHBG Serum Assay | Lab procedure | sop | SOP_SHBG_Assay.md |
| SOP_SHBG_Serum_Assay | SOP | SHBG Serum Assay SOP | Standard operating procedure | sop | SOP_SHBG_Assay.md |

### relationships.csv
| source_id | target_id | relationship_type | source_text | source_document |
|-----------|-----------|-------------------|-------------|-----------------|
| FDA_DOC_K060818 | DEVICE_ARCHITECT_SHBG | DOCUMENT_DESCRIBES_DEVICE | "510(k) describes..." | K060818_REVIEW.md |
| DEVICE_ARCHITECT_SHBG | ASSAY_SHBG_Serum | DEVICE_IMPLEMENTS_ASSAY | "Implementation via assay..." | [inferred from unified schema] |
| ASSAY_SHBG_Serum | MEASURAND_SHBG | ASSAY_DETECTS_ANALYTE | "Assay measures SHBG..." | SOP_SHBG_Assay.md |
| SOP_SHBG_Serum_Assay | ASSAY_SHBG_Serum | SOP_DESCRIBES_ASSAY | "Procedure for SHBG assay..." | SOP_SHBG_Assay.md |

## Configuration

### Extraction Command
```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/LabDocs \
  --output-dir ./graphdb_unified \
  --max-docs 0
```

### Command Options
| Option | Description | Default |
|--------|-------------|---------|
| `--input-folder` | Directory with markdown documents | Required |
| `--output-dir` | Output directory for extractions | Required |
| `--max-docs` | Limit documents to process (0 = all) | 0 |

### Graph Loading
After extraction, load into Neo4j:
```bash
uv run python pipelines/kg_pipeline/02_load.py \
  --extraction-dir ./graphdb_unified/extractions
```
