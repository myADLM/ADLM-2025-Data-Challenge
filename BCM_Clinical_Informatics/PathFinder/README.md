# PathFinder

**Primary SOP Agent for Laboratory Documentation Retrieval**

PathFinder is an AI-powered conversational agent built with Microsoft Copilot Studio, designed to help clinical and laboratory teams rapidly identify, navigate, and extract critical information from large repositories of scientific, clinical, and regulatory documents, with a focus on laboratory Standard Operating Procedures (SOPs).

---

## 🚀 Overview

PathFinder streamlines document interrogation across laboratory operations and regulatory domains. It is optimized for content-dense, process-oriented documents commonly used in clinical and diagnostic settings. As the primary agent in the dual-agent PathFinder system, it handles all SOP-related queries and routes FDA-specific requests to the specialized PathFinder FDA Documents agent.

The assistant can surface key insights, summarize workflows, generate structured outputs, and provide rapid reference linking without manual searching.

---

## 🏗️ Solution Architecture

### Publisher Information
- **Publisher**: BCM Clinical Informatics
- **Customization Prefix**: `bcmci`
- **Customization Option Value Prefix**: `34530`
- **Version**: `1.0.0.2`
- **Template**: `default-2.1.0`
- **Institution**: Baylor College of Medicine / Texas Children's Hospital

### Package Structure

The PathFinder solution is distributed as a Copilot Studio **managed solution package** containing the following components:

```
PathFinder/
├── [Content_Types].xml          # Package content type definitions
├── customizations.xml            # Solution customizations manifest
├── solution.xml                  # Solution metadata (publisher, version, etc.)
├── PathFinder.md                 # This documentation file
├── Assets/                       # Knowledge source configuration assets
│   └── botcomponent_dvtablesearchset.xml
├── bots/                         # Bot definitions and configurations
│   ├── auto_agent_c2hGx/         # Primary PathFinder agent definition
│   └── auto_agent_YWfmN/         # (Secondary/legacy agent)
├── botcomponents/                # Agent topics, configurations, and connected agents
│   ├── auto_agent_c2hGx.gpt.default/              # Core agent configuration (GPT-4.1)
│   ├── auto_agent_c2hGx.InvokeConnectedAgentTaskAction.PathfinderFDADocuments/  # FDA agent handoff
│   │
│   ├── [Conversation Management Topics]
│   ├── auto_agent_c2hGx.topic.ConversationStart/
│   ├── auto_agent_c2hGx.topic.EndofConversation/
│   ├── auto_agent_c2hGx.topic.Escalate/
│   ├── auto_agent_c2hGx.topic.Fallback/
│   ├── auto_agent_c2hGx.topic.Goodbye/
│   ├── auto_agent_c2hGx.topic.Greeting/
│   ├── auto_agent_c2hGx.topic.MultipleTopicsMatched/
│   ├── auto_agent_c2hGx.topic.OnError/
│   ├── auto_agent_c2hGx.topic.ResetConversation/
│   ├── auto_agent_c2hGx.topic.Search/
│   ├── auto_agent_c2hGx.topic.Signin/
│   ├── auto_agent_c2hGx.topic.StartOver/
│   ├── auto_agent_c2hGx.topic.ThankYou/
│   │
│   ├── [Legacy SOP Topics - Alphabetical Routing]
│   ├── auto_agent_c2hGx.topic.SOP1-9A-B/
│   ├── auto_agent_c2hGx.topic.SOP1-9C-E/
│   ├── auto_agent_c2hGx.topic.SOPF-K/
│   ├── auto_agent_c2hGx.topic.SOPF-KCopy/
│   ├── auto_agent_c2hGx.topic.SOPP-T/
│   ├── auto_agent_c2hGx.topic.SOPU-Z/
│   │
│   └── [Knowledge Source Topics - Alphabetical Partitioning]
│       ├── auto_agent_c2hGx.topic.SyntheticProceduresAB_IJJl6h6VtTGzIhzEHV3M2/
│       ├── auto_agent_c2hGx.topic.SyntheticProceduresCE_ifJfjdj4Uy0HXTBM5Pygi/
│       ├── auto_agent_c2hGx.topic.SyntheticProceduresFK_2t7opC9vwoKpqzORGSLLU/
│       ├── auto_agent_c2hGx.topic.SyntheticProceduresLO_HzV1e3M2Qx7t9omk3QgkJ/
│       ├── auto_agent_c2hGx.topic.SyntheticProceduresPT_SOOQw2GIYsDVJKThsF3De/
│       └── auto_agent_c2hGx.topic.SyntheticProceduresUZ_VC3dkgV8vME9oE7V27vZk/
│
└── dvtablesearchs/               # Dataverse table search configurations (6 total)
    ├── 0534935c-d61c-4b7e-9213-0f4005f6b3de/  # Synthetic Procedures L-O
    ├── 308a4a49-8622-454b-906a-6b9d345dea9a/
    ├── 8a110d78-dc29-43aa-8655-c666a0a9444b/
    ├── a319026c-c195-4783-8ab9-666a7c1bcd5d/
    ├── c2a70158-861f-4340-a9c5-c9252704c771/
    └── e795a218-6086-4d6e-924d-f644cdde5129/
```

---

## 🔬 Core Capabilities

### Laboratory SOP Intelligence  
PathFinder can understand and extract details from standard operating procedures (SOPs), including:

- **Specimen collection and handling requirements**  
- **Step-by-step workflow instructions**  
- **Instrument and reagent usage**  
- **Quality control (QC) criteria and troubleshooting**  
- **Reportable, reference, and analytical measurement ranges**  
- **Safety and compliance elements**  

### Regulatory Navigation (via Connected Agent)
PathFinder automatically detects FDA-related queries (e.g., "510(k)", "K######") and hands off to the **PathFinder FDA Documents** specialist agent to interpret and summarize:

- 510(k) executive and abbreviated summaries  
- Decision letters and clearance pathways  
- Device classification and regulatory product codes  
- Predicate device mapping  
- Indications for use and limitations  

---

## 🗂️ Document Optimization & Knowledge Source Structure

### Alphabetical Partitioning Strategy

To improve both retrieval speed and semantic performance, the **LabDocs Synthetic Procedures** folder was **split into alphabetical subdirectories** based on document naming patterns:

| Range | Knowledge Source Topic | Description |
|-------|------------------------|-------------|
| **0–9, A–B** | `SyntheticProceduresAB` | SOPs for tests beginning with numerals (0–9) or letters A through B |
| **C–E** | `SyntheticProceduresCE` | SOPs for tests beginning with letters C through E |
| **F–K** | `SyntheticProceduresFK` | SOPs for tests beginning with letters F through K |
| **L–O** | `SyntheticProceduresLO` | SOPs for tests beginning with letters L through O |
| **P–T** | `SyntheticProceduresPT` | SOPs for tests beginning with letters P through T |
| **U–Z** | `SyntheticProceduresUZ` | SOPs for tests beginning with letters U through Z |

Each subdirectory was separately uploaded and indexed in **Dataverse** as an independent **knowledge source**, and integrated using **SharePoint-based file connectors** for the PathFinder agent.  

### Benefits of This Structure

- ✅ **Faster indexing and refresh cycles**  
- ✅ **Reduced query complexity**  
- ✅ **Improved semantic vector search accuracy**  
- ✅ **Parallelized knowledge ingestion**  
- ✅ **Easier change/version control tracking**  

### Knowledge Source Integration

Each knowledge source topic includes:
- **Description**: Clarifies scope and explicitly excludes FDA documents
- **SharePoint connection**: Links to specific alphabetical folders via Graph API
- **Dataverse search configuration**: Enables semantic search and citation retrieval

---

## 🤖 Agent Configuration

### Core Agent (`auto_agent_c2hGx.gpt.default`)

**Name**: PathFinder  
**Description**: AI-powered assistant that helps laboratory teams quickly locate and extract critical details from a large repository of documents. Specializes in laboratory SOPs and can navigate FDA 510(k) materials via connected agent.

**Model**: GPT-4.1 (Azure OpenAI)  
**Language**: English (1033)  
**Authentication Mode**: Integrated (Microsoft Entra ID SSO)  
**Runtime Provider**: Microsoft Copilot Studio  

### Connected Agent Handoff

**Topic**: `auto_agent_c2hGx.InvokeConnectedAgentTaskAction.PathfinderFDADocuments`  
**Target Agent**: PathFinder FDA Documents  
**Description**: Sub-agent that navigates FDA regulatory materials (510(k) clearance documents) and provides specialized retrieval for regulatory information.

**Handoff Triggers**:
- Queries containing "510(k)" or "K######" patterns
- Explicit FDA-related terminology
- Questions about device clearances, product codes, or regulatory classifications

---

## 📋 Topics Overview

### Conversation Management Topics
Standard Copilot Studio conversation flow management:
- **ConversationStart**: Initial greeting and context setting
- **Greeting/Goodbye/ThankYou**: Conversational pleasantries
- **Fallback**: Handles unmatched queries
- **Escalate**: Escalation to human support
- **OnError**: Error handling and recovery
- **ResetConversation/StartOver**: Session management
- **MultipleTopicsMatched**: Disambiguation when multiple topics match
- **Search**: General search functionality
- **Signin**: Authentication handling

### Knowledge Source Topics (Primary SOP Routing)
Six specialized topics that scope knowledge retrieval to specific alphabetical ranges:
- Each topic includes a detailed description clarifying scope
- Explicitly excludes FDA documents (redirects to FDA agent)
- Maps to corresponding Dataverse search configurations
- Optimizes retrieval by pre-filtering based on test name patterns

### Legacy SOP Topics
Earlier alphabetical routing topics (maintained for compatibility):
- `SOP1-9A-B`, `SOP1-9C-E`, `SOPF-K`, etc.
- May be consolidated or deprecated in future versions

---

## 🔧 Technical Implementation Details

### Dataverse Table Search Configurations

Each `dvtablesearch` entity maps to a SharePoint folder and defines:
- **Connection reference**: SharePoint Online connector
- **Knowledge config**: JSON configuration with Graph API details
  - `driveId`, `itemId`, `sharepointIds`
  - Display name and web URL
- **Search type**: `1` (ingestion-based semantic search)

**Example** (`0534935c-d61c-4b7e-9213-0f4005f6b3de`):
- **Name**: `SyntheticProceduresLO_S0_wsHOI8zOpmlNA5Hota`
- **Display Name**: "Synthetic Procedures L-O"
- **SharePoint Path**: `/sites/BCMClinicalInformaticsFellowship/Shared Documents/2025 ADLM Data Challenge/LabDocs/Synthetic Procedures L-O`

### Channel Integration

PathFinder is published to:
- ✅ **Microsoft Teams** (synchronized)
- ✅ **Microsoft 365 Copilot** (synchronized)
- 🌐 **Web channel** (optional)

**Last Published**: 2025-11-16 00:46:44 UTC  
**Synchronization Status**: Synchronized  
**Application ID**: `167f6a27-950f-4b6d-8977-2547edcd54d6`

---

## 🧠 Intended Users

- **Clinical laboratories**  
- **Molecular and anatomic pathology teams**  
- **Quality and compliance officers**  
- **Laboratory informatics teams**  
- **Point-of-care coordinators**  
- **Training and education staff**

---

## 🎯 Benefits

- **Time-saving**: Reduces manual review of long PDFs and SOP binders  
- **Accuracy-focused**: Extracts key operational and regulatory elements with citations  
- **Standardization**: Enables consistent interpretation and reuse  
- **Scalable**: Operates across large document repositories  
- **Context-aware**: Routes queries to appropriate knowledge sources automatically  
- **Multi-agent**: Seamlessly hands off FDA queries to specialist agent  

---

## 📂 Example Use Cases

| Domain | Task | PathFinder Response |
|--------|------|---------------------|
| Clinical Lab SOPs | "What is the reportable range for TSH?" | Extracts range from SOP with citation (page/section) |
| Molecular Genetics | "Summarize QC criteria for BRCA testing" | Bullet summary with accept/reject thresholds |
| Regulatory Affairs | "Find 510(k) for Abbott Alinity" | Hands off to FDA agent → returns K number, clearance date, predicate |
| Quality Management | "Show specimen requirements for CBC" | Lists specimen type, volume, container, storage |
| Training | "What are the steps for glucose testing?" | Step-by-step procedure with QC checkpoints |

---

## 📌 Disclaimer

PathFinder is an informational and knowledge-assistance tool. It does **not** replace laboratory accreditation requirements, regulatory review, or professional validation. All outputs must be verified by qualified personnel per institutional and regulatory standards (CAP, CLIA, ISO 15189, etc.).

---

## 🚀 Deployment Instructions

### Prerequisites
- Microsoft Copilot Studio license
- Power Platform environment (recommended: dedicated environment)
- SharePoint Online with SOP folders structured alphabetically
- Excel Online Business (for FDA agent integration)

### Import Steps

1. **Download solution package**: `PathFinder_1_0_0_2_managed.zip`
2. **Import to Copilot Studio**:
   - Navigate to **Solutions** → **Import**
   - Upload the `.zip` file
   - Accept publisher prefix (`bcmci`)
3. **Configure connections**:
   - SharePoint Online: Map to your SOP repository
   - Excel Online Business: Connect for FDA routing
4. **Attach knowledge sources**:
   - Upload or link alphabetized SOP folders to SharePoint
   - Verify Dataverse search configurations
5. **Configure connected agent**:
   - Import `PathFinderFDADocuments` solution
   - Enable agent-to-agent handoff
6. **Test and publish**:
   - Test in Copilot Studio authoring canvas
   - Publish to desired channels (Teams, Web, M365 Copilot)

---

## 🔗 Related Components

- **PathFinder FDA Documents**: Specialist agent for FDA 510(k) retrieval  
  - Location: `BCM_Clinical_Informatics/PathFinderFDADocuments/`
  - Features Excel-based K-number routing and specialty-specific topics

- **Python Processing Utilities**: PDF preprocessing tools  
  - Location: `BCM_Clinical_Informatics/Python_Code/`
  - Merges paired FDA PDFs to reduce file count

