# PathFinder FDA Documents

**Specialist FDA Regulatory Intelligence Agent**

PathFinder FDA Documents is an AI-powered conversational agent built with Microsoft Copilot Studio, designed to provide rapid, section-level retrieval of FDA 510(k) regulatory documentation. This specialist agent works in conjunction with the primary [PathFinder](../PathFinder/README.md) agent to deliver precise regulatory information across clinical chemistry, hematology, microbiology, molecular genetics, and other laboratory specialty domains.

---

## 🚀 Overview

PathFinder FDA Documents is a specialized sub-agent that handles all FDA regulatory queries within the dual-agent PathFinder system. When users query FDA 510(k) documents, device clearances, or regulatory classifications, the primary PathFinder agent automatically hands off to this specialist for optimized FDA-specific retrieval.

The assistant excels at extracting critical regulatory information from FDA 510(k) materials, including:

- **510(k) executive and abbreviated summaries**  
- **Decision letters and clearance dates**  
- **Device classification and product codes**  
- **Predicate device identification**  
- **Indications for use and limitations**  
- **Regulatory submission pathways**  

For overall system context and dual-agent architecture, see the main [README](../README.md).

---

## 🏗️ Solution Architecture

### Publisher Information
- **Publisher**: BCM Clinical Informatics
- **Customization Prefix**: `bcmci`
- **Customization Option Value Prefix**: `34530`
- **Version**: `1.0.0.3`
- **Institution**: Baylor College of Medicine / Texas Children's Hospital

### Package Structure

The PathFinder FDA Documents solution is distributed as a Copilot Studio **managed solution package** containing the following components:

```
PathFinderFDADocuments/
├── [Content_Types].xml                    # Package content type definitions
├── customizations.xml                     # Solution customizations manifest
├── solution.xml                           # Solution metadata (publisher, version, etc.)
├── PathFinder_FDA_Documents.md            # This documentation file
│
├── Assets/                                # Configuration and connection references
│   ├── botcomponent_connectionreferenceset.xml  # Excel Online Business connection
│   └── botcomponent_dvtablesearchset.xml        # Knowledge source configurations
│
├── bots/                                  # Bot definitions
│   └── auto_agent_YWfmN/                  # PathFinder FDA Documents agent definition
│
├── botcomponents/                         # Agent topics, actions, and configurations
│   ├── auto_agent_YWfmN.gpt.default/                                    # Core agent configuration (GPT-4.1)
│   ├── auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable/  # Excel ID-to-Topic routing action
│   │
│   ├── [Conversation Management Topics]
│   ├── auto_agent_YWfmN.topic.ConversationStart/
│   ├── auto_agent_YWfmN.topic.EndofConversation/
│   ├── auto_agent_YWfmN.topic.Escalate/
│   ├── auto_agent_YWfmN.topic.Fallback/
│   ├── auto_agent_YWfmN.topic.Goodbye/
│   ├── auto_agent_YWfmN.topic.Greeting/
│   ├── auto_agent_YWfmN.topic.MultipleTopicsMatched/
│   ├── auto_agent_YWfmN.topic.OnError/
│   ├── auto_agent_YWfmN.topic.ResetConversation/
│   ├── auto_agent_YWfmN.topic.Search/
│   ├── auto_agent_YWfmN.topic.Signin/
│   ├── auto_agent_YWfmN.topic.StartOver/
│   ├── auto_agent_YWfmN.topic.ThankYou/
│   │
│   ├── [FDA Specialty Topics - Optimized Knowledge Sources]
│   ├── auto_agent_YWfmN.topic.FDACardiovascular/
│   ├── auto_agent_YWfmN.topic.FDAClinicalChemistry/
│   ├── auto_agent_YWfmN.topic.FDAImmunology/
│   ├── auto_agent_YWfmN.topic.FDAMolecularGenetics/
│   ├── auto_agent_YWfmN.topic.FDAObstetricsandgynecologyOBGYN/
│   ├── auto_agent_YWfmN.topic.FDAPathology/
│   ├── auto_agent_YWfmN.topic.FDAToxicology/
│   │
│   ├── [Knowledge Source Topics - Specialty Partitioning]
│   ├── auto_agent_YWfmN.topic.Cardiovascular_tCSxXJs75VcbKlq6HWiEd/
│   ├── auto_agent_YWfmN.topic.ClinicalChemistryPart1_TwSrlGRYPCOUDxX7S2KF_/
│   ├── auto_agent_YWfmN.topic.ClinicalChemistryPart2_75xS23yjLcC0Ir5e5Mcav/
│   ├── auto_agent_YWfmN.topic.ClinicalChemistryPart3_2yWFTT3bK_qo9qt3MusIO/
│   ├── auto_agent_YWfmN.topic.Hematology/
│   ├── auto_agent_YWfmN.topic.Hematology_jmBj9NJ55pQ82svsAxH_G/
│   ├── auto_agent_YWfmN.topic.Immunology_tlMSbQkgLOWv7FzWbqRvm/
│   ├── auto_agent_YWfmN.topic.Microbiology/
│   ├── auto_agent_YWfmN.topic.MicrobiologyPart1_Z5h1Lf4JLG6SAb4N70KeI/
│   ├── auto_agent_YWfmN.topic.MicrobiologyPart2_xBqQMcxsZga4zrhK3aWfd/
│   ├── auto_agent_YWfmN.topic.MolecularGenetics_aWvYbt1_gH38BIhXpCN4u/
│   ├── auto_agent_YWfmN.topic.Obstetrics_SiDkMRJUdla92VF3FFkIu/
│   ├── auto_agent_YWfmN.topic.Pathology_dbOw_FdPg8T883fRXIqTU/
│   ├── auto_agent_YWfmN.topic.Toxicology_wTDUzHhIiS1sT59P25Qbp/
│   │
│   └── [FDA ID to Topic Mapper]
│       └── auto_agent_YWfmN.topic.FDA_file_mapxlsx_HCAGOQuld_ChZK1dO5ySc/  # Excel-based K# routing
│
├── dvtablesearchs/                        # Dataverse table search configurations (13 total)
│   ├── 0bb6baf7-f920-45b2-a4ef-490ee25901c1/  # Molecular Genetics
│   ├── 0d4c381c-b18f-43e9-a3a8-87141cc19287/  # Clinical Chemistry Part 1
│   ├── 0f36e652-4031-4943-bdad-743a3d27a8a1/  # Clinical Chemistry Part 2
│   ├── 3f3cb599-87c9-4eca-aff1-d1c5a6e55c1a/  # Clinical Chemistry Part 3
│   ├── 4060b3c4-b001-4657-b804-d01dd008c7c5/  # Hematology
│   ├── 4dbc395e-68c1-4fa8-b1e8-a98d24901173/  # Immunology
│   ├── 5be7d29c-5488-4092-935a-dd147ca98298/  # Microbiology Part 1
│   ├── 87f76a4d-ab93-4409-b9c3-ca9ee6e94aa9/  # Microbiology Part 2
│   ├── 9311bd42-681f-49d3-a4be-2e1f21c19377/  # Pathology
│   ├── c87d86dd-0f2f-4eb9-a477-430efbab5760/  # Toxicology
│   ├── d83c0429-fe01-4083-a89c-a40657d550f2/  # Cardiovascular
│   ├── df56b716-5cb7-4979-a14d-1c00b42e20b0/  # Obstetrics & Gynecology
│   └── ea7c03d0-c10d-4022-b3bb-6d4197f0fd69/  # (Additional specialty)
│
└── dvtablesearchentities/                 # Dataverse search entity configurations (1000+)
    ├── [UUID-based entity folders...]     # Individual FDA document search entities
    └── ...                                # Comprehensive FDA 510(k) index
```

---

## 🔬 Core Capabilities

### FDA-Specific Document Intelligence  
PathFinder FDA Documents extracts precise regulatory information from FDA 510(k) submissions:

- **Device identification** (K-numbers, trade names, manufacturers)  
- **Product codes and regulatory classifications**  
- **Indications for use and intended patient populations**  
- **Technological characteristics and substantial equivalence**  
- **Decision summaries and clearance dates**  
- **Predicate device mapping**  
- **Performance data and clinical studies**  

### Smart Query Routing

The agent employs a **dual-routing strategy** for optimal FDA document retrieval:

#### 1. FDA ID → Topic Mapper (Excel-Based Routing)

When users provide a specific **K-number** (e.g., "K123456"), the agent:

1. Invokes the **Excel Online Business connector** action ([`auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable`](botcomponents/auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable/))
2. Looks up the K-number in the **FDA_file_map.xlsx** mapping table
3. Routes to the appropriate specialty topic (Chemistry, Hematology, Microbiology, etc.)
4. Executes scoped search within that specialty's knowledge source

**Benefits:**
- ✅ **Direct K-number-to-specialty mapping** for precision
- ✅ **Reduced search space** improves speed and accuracy
- ✅ **Maintains single source of truth** in Excel mapping file
- ✅ **Easy updates** when new FDA documents are added

#### 2. Device/Assay Keywords → Topic-Scoped Knowledge

When users describe devices or assays by **clinical terms** (e.g., "glucose meters," "multiplex PCR panels"):

1. Natural language understanding maps keywords to specialty domains
2. Topic descriptions pre-filter knowledge sources by specialty
3. Semantic search executes within scoped FDA document sets
4. Results include citations and verbatim regulatory language

**Benefits:**
- ✅ **Natural language queries** without requiring K-numbers
- ✅ **Topic-level filtering** reduces noise
- ✅ **Semantic matching** finds relevant devices across variations

---

## 📂 Data Source Optimization

### PDF Preprocessing Strategy

The FDA 510(k) document corpus was optimized using the [Python preprocessing utilities](../Python_Code/) located in the [`Python_Code/`](../Python_Code/) directory:

#### Utilities Used:
- **[`FDA_PDF_Functions/`](../Python_Code/FDA_PDF_Functions/)** — Core library for PDF operations  
- **[`merge_paired_fda_files.py`](../Python_Code/merge_paired_fda_files.py)** — Automated pairing and merging script  

#### Processing Workflow:

1. **Scan** FDA repository for paired files:
   - `K######_BASE.pdf` (primary submission)
   - `K######_REVIEW.pdf` (FDA reviewer comments)

2. **Merge** paired PDFs into single combined files:
   - Output: `K######_combined.pdf`
   - Preserves complete dossier content
   - Maintains page numbering and structure

3. **Organize** by specialty domains:
   - Clinical Chemistry
   - Hematology
   - Microbiology
   - Molecular Genetics
   - Toxicology
   - Cardiovascular
   - Pathology
   - Obstetrics & Gynecology

#### Optimization Outcomes:
- ✅ **Reduced file count** — stayed within Copilot Studio knowledge source file caps  
- ✅ **Faster indexing** — fewer files to process per specialty  
- ✅ **Complete context** — BASE + REVIEW in single searchable document  
- ✅ **Simplified maintenance** — one file per K-number  

For detailed preprocessing documentation, see the [`Python_Code/README.md`](../Python_Code/README.md).

---

## 🗂️ Specialty Partitioning Strategy

### Why Partition by Specialty?

FDA 510(k) documents span diverse laboratory domains with distinct terminologies, devices, and regulatory pathways. **Specialty-based partitioning** improves:

- **Retrieval precision** — matches align with domain context  
- **Semantic accuracy** — terms like "panel" mean different things in Chemistry vs. Molecular Genetics  
- **Query performance** — smaller search spaces reduce latency  
- **Knowledge source management** — independent versioning per specialty  

### Specialty Knowledge Sources

Each specialty topic maps to a **SharePoint folder** containing merged FDA PDFs:

| Specialty | Topic(s) | Example Devices |
|-----------|----------|-----------------|
| **Clinical Chemistry** | `ClinicalChemistryPart1`, `ClinicalChemistryPart2`, `ClinicalChemistryPart3` | Glucose meters, lipid panels, electrolyte analyzers |
| **Hematology** | `Hematology` | CBC analyzers, coagulation instruments, flow cytometers |
| **Microbiology** | `MicrobiologyPart1`, `MicrobiologyPart2` | ID/AST systems, blood culture instruments, rapid antigen tests |
| **Molecular Genetics** | `MolecularGenetics` | NGS panels, PCR assays, FISH probes |
| **Immunology** | `Immunology` | Immunoassay analyzers, allergy testing, autoimmune panels |
| **Toxicology** | `Toxicology` | Drug screens, therapeutic drug monitoring, heavy metals |
| **Cardiovascular** | `Cardiovascular` | Cardiac markers, troponin assays, BNP tests |
| **Pathology** | `Pathology` | Tissue staining kits, IHC assays, digital pathology systems |
| **Obstetrics & Gynecology** | `Obstetrics` | Pregnancy tests, fetal monitoring, prenatal screening |

### Knowledge Source Integration

Each specialty knowledge source includes:
- **SharePoint connection** — Links to organized FDA PDF folders via Graph API  
- **Dataverse search configuration** — Enables semantic search and citation retrieval  
- **Topic description** — Clarifies scope and guides routing logic  

---

## 🤖 Agent Configuration

### Core Agent ([`auto_agent_YWfmN.gpt.default`](botcomponents/auto_agent_YWfmN.gpt.default/))

**Name**: Pathfinder FDA Documents  
**Description**: An AI-powered assistant specialized in Food and Drug Administration (FDA) regulatory content, including 510(k) summaries, decision letters, and classifications. It routes queries by FDA ID using the FDA ID to Topic Mapper or by device/assay keywords to topic-scoped knowledge, ensuring precise, section-level retrieval with citations.

**Model**: GPT-4.1 (Azure OpenAI)  
**Language**: English (1033)  
**Authentication Mode**: Integrated (Microsoft Entra ID SSO)  
**Runtime Provider**: Microsoft Copilot Studio  

### Excel Online Business Integration

**Action**: [`auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable`](botcomponents/auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable/)  
**Purpose**: K-number → Specialty Topic routing  
**Connection**: Excel Online Business (Power Platform connector)  

**Mapping File**: `FDA_file_map.xlsx`  
**Structure**:
- **Column A**: K-number (e.g., K123456)
- **Column B**: Specialty Topic (e.g., "Clinical Chemistry", "Hematology")
- **Column C**: (Optional) Device name/description

**Routing Logic**:
1. User query contains K-number pattern (`K######`)
2. Agent invokes Excel action to query mapping file
3. Returns specialty topic name
4. Routes to corresponding FDA knowledge source topic
5. Executes scoped search and returns citations

---

## 📋 Topics Overview

### Conversation Management Topics
Standard Copilot Studio conversation flow management:
- **[`ConversationStart`](botcomponents/auto_agent_YWfmN.topic.ConversationStart/)**: Initial greeting and FDA domain context setting
- **[`Greeting`](botcomponents/auto_agent_YWfmN.topic.Greeting/) / [`Goodbye`](botcomponents/auto_agent_YWfmN.topic.Goodbye/) / [`ThankYou`](botcomponents/auto_agent_YWfmN.topic.ThankYou/)**: Conversational pleasantries
- **[`Fallback`](botcomponents/auto_agent_YWfmN.topic.Fallback/)**: Handles unmatched queries
- **[`Escalate`](botcomponents/auto_agent_YWfmN.topic.Escalate/)**: Escalation to human support
- **[`OnError`](botcomponents/auto_agent_YWfmN.topic.OnError/)**: Error handling and recovery
- **[`ResetConversation`](botcomponents/auto_agent_YWfmN.topic.ResetConversation/) / [`StartOver`](botcomponents/auto_agent_YWfmN.topic.StartOver/)**: Session management
- **[`MultipleTopicsMatched`](botcomponents/auto_agent_YWfmN.topic.MultipleTopicsMatched/)**: Disambiguation when multiple topics match
- **[`Search`](botcomponents/auto_agent_YWfmN.topic.Search/)**: General search functionality
- **[`Signin`](botcomponents/auto_agent_YWfmN.topic.Signin/)**: Authentication handling

### FDA Specialty Topics
High-level FDA domain topics for initial routing:
- **[`FDACardiovascular`](botcomponents/auto_agent_YWfmN.topic.FDACardiovascular/)**: Cardiac markers and cardiovascular devices
- **[`FDAClinicalChemistry`](botcomponents/auto_agent_YWfmN.topic.FDAClinicalChemistry/)**: Chemistry analyzers and assays
- **[`FDAImmunology`](botcomponents/auto_agent_YWfmN.topic.FDAImmunology/)**: Immunoassays and allergy testing
- **[`FDAMolecularGenetics`](botcomponents/auto_agent_YWfmN.topic.FDAMolecularGenetics/)**: Genetic testing and NGS panels
- **[`FDAObstetricsandgynecologyOBGYN`](botcomponents/auto_agent_YWfmN.topic.FDAObstetricsandgynecologyOBGYN/)**: Prenatal and OB/GYN devices
- **[`FDAPathology`](botcomponents/auto_agent_YWfmN.topic.FDAPathology/)**: Histology and IHC assays
- **[`FDAToxicology`](botcomponents/auto_agent_YWfmN.topic.FDAToxicology/)**: Drug screening and toxicology assays

### Knowledge Source Topics (Specialty Partitioning)
Topics that scope knowledge retrieval to specific FDA specialty domains:
- **[`Cardiovascular_tCSxXJs75VcbKlq6HWiEd`](botcomponents/auto_agent_YWfmN.topic.Cardiovascular_tCSxXJs75VcbKlq6HWiEd/)**
- **[`ClinicalChemistryPart1_TwSrlGRYPCOUDxX7S2KF_`](botcomponents/auto_agent_YWfmN.topic.ClinicalChemistryPart1_TwSrlGRYPCOUDxX7S2KF_/)** — Chemistry Part 1 (A-M devices)
- **[`ClinicalChemistryPart2_75xS23yjLcC0Ir5e5Mcav`](botcomponents/auto_agent_YWfmN.topic.ClinicalChemistryPart2_75xS23yjLcC0Ir5e5Mcav/)** — Chemistry Part 2 (N-Z devices)
- **[`ClinicalChemistryPart3_2yWFTT3bK_qo9qt3MusIO`](botcomponents/auto_agent_YWfmN.topic.ClinicalChemistryPart3_2yWFTT3bK_qo9qt3MusIO/)** — Chemistry Part 3 (overflow/recent)
- **[`Hematology`](botcomponents/auto_agent_YWfmN.topic.Hematology/)** / **[`Hematology_jmBj9NJ55pQ82svsAxH_G`](botcomponents/auto_agent_YWfmN.topic.Hematology_jmBj9NJ55pQ82svsAxH_G/)**
- **[`Immunology_tlMSbQkgLOWv7FzWbqRvm`](botcomponents/auto_agent_YWfmN.topic.Immunology_tlMSbQkgLOWv7FzWbqRvm/)**
- **[`Microbiology`](botcomponents/auto_agent_YWfmN.topic.Microbiology/)** / **[`MicrobiologyPart1_Z5h1Lf4JLG6SAb4N70KeI`](botcomponents/auto_agent_YWfmN.topic.MicrobiologyPart1_Z5h1Lf4JLG6SAb4N70KeI/)** / **[`MicrobiologyPart2_xBqQMcxsZga4zrhK3aWfd`](botcomponents/auto_agent_YWfmN.topic.MicrobiologyPart2_xBqQMcxsZga4zrhK3aWfd/)**
- **[`MolecularGenetics_aWvYbt1_gH38BIhXpCN4u`](botcomponents/auto_agent_YWfmN.topic.MolecularGenetics_aWvYbt1_gH38BIhXpCN4u/)**
- **[`Obstetrics_SiDkMRJUdla92VF3FFkIu`](botcomponents/auto_agent_YWfmN.topic.Obstetrics_SiDkMRJUdla92VF3FFkIu/)**
- **[`Pathology_dbOw_FdPg8T883fRXIqTU`](botcomponents/auto_agent_YWfmN.topic.Pathology_dbOw_FdPg8T883fRXIqTU/)**
- **[`Toxicology_wTDUzHhIiS1sT59P25Qbp`](botcomponents/auto_agent_YWfmN.topic.Toxicology_wTDUzHhIiS1sT59P25Qbp/)**

### FDA ID to Topic Mapper
Excel-based routing topic:
- **[`FDA_file_mapxlsx_HCAGOQuld_ChZK1dO5ySc`](botcomponents/auto_agent_YWfmN.topic.FDA_file_mapxlsx_HCAGOQuld_ChZK1dO5ySc/)**: K-number lookup and specialty routing

---

## 🔧 Technical Implementation Details

### Dataverse Table Search Configurations

The [`dvtablesearchs/`](dvtablesearchs/) directory contains **13 specialty-specific search configurations**. Each configuration maps to a SharePoint folder containing merged FDA PDFs for a specific laboratory specialty.

**Example** ([`0bb6baf7-f920-45b2-a4ef-490ee25901c1`](dvtablesearchs/0bb6baf7-f920-45b2-a4ef-490ee25901c1/)):

```xml
<dvtablesearch dvtablesearchid="0bb6baf7-f920-45b2-a4ef-490ee25901c1">
  <connectionreference>
    <connectionreferencelogicalname>auto_agent_YWfmN.cr.x_NIIosN</connectionreferencelogicalname>
  </connectionreference>
  <knowledgeconfig>{
    "$kind": "IngestionBasedGraphSearchConfiguration",
    "driveItems": [{
      "$kind": "GraphDriveItemSyncDetails",
      "displayName": "Molecular Genetics",
      "webUrl": "https://bcmedu.sharepoint.com/.../FDA_Merged/Molecular Genetics",
      "driveId": "",
      "itemId": "01P2OUHBNB43TBWWO22JAIT7S6Z22JC7ZN",
      "sharepointIds": { ... }
    }]
  }</knowledgeconfig>
  <name>MolecularGenetics_LYUAL6sCDYKIYGlPYBC6f</name>
  <searchtype>1</searchtype>
</dvtablesearch>
```

**Key Fields**:
- **`dvtablesearchid`**: Unique identifier for the knowledge source
- **`connectionreference`**: Links to SharePoint connector
- **`knowledgeconfig`**: Graph API configuration with SharePoint paths
- **`displayName`**: Human-readable specialty name (e.g., "Molecular Genetics")
- **`webUrl`**: Direct SharePoint folder path
- **`itemId`**: SharePoint unique item ID for folder
- **`searchtype`**: `1` = ingestion-based semantic search (RAG)

### Dataverse Search Entities

The [`dvtablesearchentities/`](dvtablesearchentities/) directory contains **1000+ entity configurations** representing individual FDA documents and search indices. These are automatically generated by Dataverse as the knowledge sources are ingested.

**Structure**:
- Each UUID-based folder (e.g., [`85802997-96be-f011-bbd2-000d3a5a9505`](dvtablesearchentities/85802997-96be-f011-bbd2-000d3a5a9505/)) represents a search entity
- Entities map individual documents or document chunks for semantic search
- Used by the RAG (Retrieval-Augmented Generation) pipeline

### Connection References

The [`Assets/botcomponent_connectionreferenceset.xml`](Assets/botcomponent_connectionreferenceset.xml) file defines the **Excel Online Business connection** used for K-number routing:

```xml
<botcomponent_connectionreference 
  botcomponentid.schemaname="auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable" 
  connectionreferenceid.connectionreferencelogicalname="auto_agent_YWfmN.shared_excelonlinebusiness.f9a82191a5744a4ebccb58fbb648a832">
  <iscustomizable>1</iscustomizable>
</botcomponent_connectionreference>
```

This connection enables the agent to:
1. Query the FDA mapping Excel file
2. Look up K-numbers and return specialty topics
3. Route queries to appropriate knowledge sources

---

## 🧠 Intended Users

- **Regulatory affairs professionals**  
- **Clinical laboratory directors**  
- **Laboratory quality and compliance teams**  
- **Pathologists and laboratory physicians**  
- **Laboratory informatics and IT teams**  
- **Research and development engineers**  
- **Vendor management and procurement teams**  

---

## 🎯 Benefits

- **Time-saving**: Eliminates manual FDA database searches and PDF review  
- **Precision**: Returns section-level results with exact citations  
- **Regulatory accuracy**: Provides verbatim FDA language for audit trails  
- **Specialty-aware**: Understands domain-specific terminology and context  
- **Scalable**: Handles 1000+ FDA documents across multiple specialties  
- **Connected agent architecture**: Seamlessly integrates with primary PathFinder agent  
- **Excel-based routing**: Easy to update and maintain K-number mappings  

---

## 📂 Example Use Cases

| Domain | Query | PathFinder FDA Documents Response |
|--------|-------|----------------------------------|
| **K-Number Lookup** | "What is K123456?" | Returns device name, manufacturer, indication, product code, clearance date (with citations) |
| **Device Search** | "Find 510(k)s for glucose meters" | Lists relevant K-numbers in Clinical Chemistry with summaries |
| **Product Code** | "Show devices with product code DKN" | Returns all 510(k)s with that product code, grouped by specialty |
| **Predicate Identification** | "What predicate did K234567 use?" | Extracts predicate K-number(s) and substantial equivalence claims |
| **Regulatory Pathway** | "Was K345678 cleared under traditional or special 510(k)?" | Returns submission type and regulatory pathway |
| **Indications for Use** | "What is K456789 indicated for?" | Extracts verbatim indications section with patient population |

---

## 📌 Agent Rules and Behavior

PathFinder FDA Documents follows strict output rules to ensure regulatory compliance and citation fidelity:

### Core Principles:

1. **Verbatim regulatory text** — Never paraphrase FDA language; quote directly  
2. **Always cite sources** — Include K-number, document section, and page  
3. **Section-level retrieval** — Return only relevant passages, not entire PDFs  
4. **Specialty routing** — Use Excel lookup for K-numbers; topic matching for keywords  
5. **Preserve numeric values** — Never round or estimate regulatory data  
6. **Include product codes** — Always state product code classification when available  
7. **Link predicates** — When mentioning predicate devices, include their K-numbers  

### Example Output Format:

```
Query: "What is K123456 indicated for?"

Response:
Device: Acme Glucose Monitoring System (K123456)
Manufacturer: Acme Medical Devices, Inc.
Product Code: NBW (Glucose Meter)
Regulatory Class: II

Indications for Use:
"The Acme Glucose Monitoring System is intended for the quantitative measurement 
of glucose in fresh capillary whole blood samples. The system is intended for 
prescription use in clinical settings and for over-the-counter use by persons 
with diabetes at home as an aid to monitor the effectiveness of diabetes control."

Source: K123456 510(k) Summary, Section 4.0 (Indications for Use), Page 6
Clearance Date: March 15, 2023
Decision: Substantially Equivalent (SE)
```

---

## 🚀 Deployment Instructions

### Prerequisites
- Microsoft Copilot Studio license
- Power Platform environment (recommended: dedicated environment)
- SharePoint Online with FDA PDF folders organized by specialty
- Excel Online Business connector (for K-number routing)
- Excel file (`FDA_file_map.xlsx`) with K-number → specialty mappings

### Import Steps

1. **Download solution package**: `PathFinderFDADocuments_1_0_0_3_managed.zip`
2. **Import to Copilot Studio**:
   - Navigate to **Solutions** → **Import**
   - Upload the `.zip` file
   - Accept publisher prefix (`bcmci`)
3. **Configure connections**:
   - **SharePoint Online**: Map to your FDA document repository
   - **Excel Online Business**: Connect to `FDA_file_map.xlsx`
4. **Attach knowledge sources**:
   - Upload merged FDA PDFs to SharePoint (organized by specialty)
   - Verify Dataverse search configurations point to correct folders
5. **Update Excel mapping**:
   - Populate `FDA_file_map.xlsx` with K-number → specialty mappings
   - Store in SharePoint or OneDrive accessible to the agent
6. **Connect to primary PathFinder agent** (optional):
   - Import [`PathFinder`](../PathFinder/) solution
   - Configure connected agent handoff
7. **Test and publish**:
   - Test K-number lookups and specialty routing
   - Test natural language device queries
   - Publish to desired channels (Teams, Web, M365 Copilot)

---

## 🔗 Related Components

- **[PathFinder (Primary Agent)](../PathFinder/)**: Main SOP agent; hands off FDA queries to this specialist  
  - Solution: `PathFinder_1_0_0_2_managed.zip`
  - Features: Alphabetized SOP topics, connected agent orchestration

- **[Python Preprocessing Utilities](../Python_Code/)**: PDF merging tools for FDA document preparation  
  - Script: [`merge_paired_fda_files.py`](../Python_Code/merge_paired_fda_files.py)
  - Library: [`FDA_PDF_Functions/`](../Python_Code/FDA_PDF_Functions/)

- **[Project README](../README.md)**: Overall system architecture and dual-agent design