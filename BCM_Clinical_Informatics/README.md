# PathFinder: AI‑Powered Laboratory Documentation Retrieval

## ADLM 2025 Data Science Challenge Submission

**Team members**: Mikael Guzman Karlsson, Matthew Bayes, Thomas Chong
**Institution**: Baylor College of Medicine / Texas Children's Hospital

---

## Overview

PathFinder is a **dual‑agent** solution built with **Microsoft Copilot Studio** that helps laboratory professionals instantly find information in **SOPs** and **FDA 510(k)** documents. Queries are automatically routed to the right agent and answers return the **exact section** with **verbatim** values for safety‑critical details.

### The challenge

Lab teams lose time paging through SOPs, package inserts, and FDA documents. Keyword search often returns entire files or misses key sections.

### Our solution

* **PathFinder** — primary agent for SOPs/procedures 
* **PathFinder FDA Documents** — specialist agent for FDA 510(k) retrieval with **Excel‑based FDA ID routing**
* **Python utilities** — preprocess FDA PDFs (pair + merge) to stay within **knowledge‑source file caps** while preserving complete content

---

## Technology: Microsoft Copilot Studio

### What is Copilot Studio?

[**Microsoft Copilot Studio**](https://aka.ms/CopilotStudio) is an enterprise platform for building **AI agents** with:

* **Generative AI** (Azure OpenAI models incl. GPT‑4.1, GPT-5, and other)
* **Knowledge** (RAG with citations from SharePoint, Excel, direct file uploads, dataverse, SQL databases, and others)
* **Multi‑agent orchestration** (parent/child agents, handoffs)
* **Low‑code + pro‑code** (visual design + [Microsoft 365 Agents SDK](https://github.com/microsoft/Agents))
* **Enterprise integration** (Teams publishing, Entra ID SSO, hundreds of connectors)

**Resources**: [Docs](https://aka.ms/CopilotStudioDocs) • [Community](https://aka.ms/CopilotStudioCommunity) • [Try](https://aka.ms/TryCopilotStudio) • [Samples](https://github.com/microsoft/CopilotStudioSamples)

### Why Copilot Studio for laboratories?

| Requirement               | Copilot Studio fit                                                                                                                                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Security & compliance** | Microsoft enterprise compliance portfolio (e.g., ISO/IEC 27001, SOC); HIPAA BAA availability depending on services. Supports **audit logging** and controls to help implement **21 CFR Part 11–aligned processes**. |
| **Integration**           | SharePoint, Excel Online, Teams, Power Platform connectors—works with existing lab IT.                                                                                                                              |
| **Knowledge fidelity**    | Built‑in RAG with citations and versioned knowledge sources.                                                                                                                                                        |
| **Governance**            | Dev→Test→Prod via **Solutions** (managed/unmanaged), analytics, DLP policies.                                                                                                                                       |
| **Rapid deployment**      | Low‑code authoring; days instead of months for scaffolding and channels.                                                                                                                                            |
| **Extensibility**         | Pro‑code via **Agents SDK** and **Azure AI Studio** (advanced flows, custom models).                                                                                                                                |

> Alternatives (e.g., raw SDKs or bespoke RAG stacks) can be excellent, but typically require extra time to add governance, identity, telemetry, and enterprise distribution.

---

## Model & runtime configuration (shared across agents)

* **Model**: **GPT‑4.1** (Azure OpenAI). We rely on its **long‑context** capability (up to **1M tokens**), stronger **instruction‑following**, and improved **long‑context comprehension**—ideal for multi‑PDF SOPs and FDA dossiers. It’s designed to power **agentic tool use** and multi‑step workflows. ([OpenAI Platform][1])
* **Generative orchestration**: **On**. The agent **chooses topics, tools, connected agents, and knowledge sources**, can ask clarifying questions, and **sequences** multiple steps automatically. ([Microsoft Learn][2])
* **Connected agents**: **On**. PathFinder hands off FDA intents to **PathFinder FDA Documents** and returns the result (preview feature). ([Microsoft Learn][3])
* **User feedback**: **On**. End‑users can give **thumbs‑up/down + comment**; feedback appears in Copilot Studio analytics. ([Microsoft Learn][4])
* **Tenant Graph grounding**: **On (when available)**. With **Semantic Index for Copilot**, we enable **Enhanced search results** so retrieval benefits from **tenant Graph semantic search** for content the user can access. ([Microsoft Learn][5])
* **Strict grounding**: **General/foundational knowledge = Off** (answers draw **only** from our sources). **Web/Bing search = Off** (no public web). Both are optional features that we intentionally disabled for auditability. ([Microsoft Learn][6])

> *Note:* Effective context/limits can vary by channel and tenant configuration.

---

## System architecture

**Why dual agents + topic routing?**
Focused agents reduce noise and speed retrieval.

**How it works**

1. **PathFinder** evaluates the query. FDA signals (e.g., `K######`, “510(k)”) → **handoff** to FDA agent; otherwise continue in SOP topics.
2. Within each agent, **topic descriptions** scope which **knowledge sources** are searched first; if no match, fall back to global sources.
3. **Excel‑based FDA routing**: given a `K######`, the FDA agent maps to the right specialty topic (Chemistry, Hematology, Microbiology, etc.) before searching the 510(k) corpus.

```
User
  ↓
PathFinder (SOP agent, 6 A–Z topics)
  ├─ FDA signals? → PathFinder FDA Documents
  │   ├─ Excel lookup (K###### → topic)
  │   ├─ Topic‑scoped search over FDA PDFs
  │   └─ Return: indications, class, product code, etc. + citations
  └─ Else SOP flow:
      ├─ Topic match (A–Z)
      ├─ Scoped search over SOPs
      └─ Return: specimen/QC/steps + citations
```

---

## Solution components

### 1) PathFinder — primary agent

**[PathFinder/](PathFinder/)** | **[Documentation](PathFinder/README.md)**

* Copilot Studio **solution package**
* 6 alphabetized SOP topics (0-9/A-B, C-E, F-K, L-O, P-T, U-Z); conversation management (greetings, fallback, escalation)
* 400+ data table search entity configurations
* Connected agent handoff to FDA specialist
* **Version**: 1.0.0.2

**Agent rules**: Return **full SOP** for broad queries; **section‑only** for specifics; **preserve** numeric values/units/tables; **always cite** source + page/section; route FDA terms to the FDA agent.

### 2) PathFinder FDA Documents — specialist agent

**[PathFinderFDADocuments/](PathFinderFDADocuments/)** | **[Documentation](PathFinderFDADocuments/README.md)**

* Copilot Studio **solution package**
* Specialty topics (Cardiovascular, Clinical Chemistry [3 parts], Hematology, Immunology, Microbiology [2 parts], Molecular Genetics, Obstetrics, Pathology, Toxicology)
* **Excel Online Business** integration via [`FDA_file_map.xlsx`](FDA_file_map.xlsx) for `K######` → topic routing
* 13 specialty-specific Dataverse search configurations
* 1000+ FDA document search entities
* **Version**: 1.0.0.3

**Agent rules**: Section‑level 510(k) retrieval with verbatim **product codes**, **regulatory class**, **regulation number**, **decision date**; **always cite** source + page/section.

### 3) Python PDF processing

**[Python_Code/](Python_Code/)** | **[Documentation](Python_Code/README.md)**

Python utilities for FDA PDF preprocessing:
* **[merge_paired_fda_files.py](Python_Code/merge_paired_fda_files.py)** — Main driver script for end-to-end FDA PDF processing
* **[FDA_PDF_Functions/](Python_Code/FDA_PDF_Functions/)** — Core library with modules:
  - `pairing.py` — Find BASE/BASE_REVIEW pairs
  - `merge.py` — Merge paired PDFs
  - `copying.py` — Copy unpaired/failed-merge PDFs
  - `validate.py` — Validate PDF readability
  - `report.py` — Generate directory summaries

**Purpose**: Scan/pair **BASE + BASE_REVIEW** PDFs, **merge** pairs (mirror structure), **validate**, and **report**. Reduces file count while preserving complete dossiers for indexing.

---

## Quick start

**Import packaged solutions**

1. In Copilot Studio → **Solutions** → **Import**: 
   - **[PathFinder](PathFinder/)** (managed, v1.0.0.2) 
   - **[PathFinderFDADocuments](PathFinderFDADocuments/)** (managed, v1.0.0.3)
2. Configure **Excel Online Business** connection (FDA agent) pointing to [`FDA_file_map.xlsx`](FDA_file_map.xlsx).
3. Attach SOP and FDA knowledge sources to SharePoint; **connect agents** for handoff.
4. Upload preprocessed FDA PDFs (merged using [Python utilities](Python_Code/)) organized by specialty.
5. Publish (web/Teams/Microsoft 365 Copilot) and test.

**Publisher**: BCM Clinical Informatics • **Customization prefix**: `bcmci` • **Option value prefix**: `34530`  
**Institution**: Baylor College of Medicine / Texas Children's Hospital

### File structure

```
BCM_Clinical_Informatics/
├── README.md                           # This file
├── FDA_file_map.xlsx                   # K-number to specialty routing table
│
├── PathFinder/                         # Primary SOP agent solution package
│   ├── README.md                       # Detailed PathFinder documentation
│   ├── [Content_Types].xml
│   ├── customizations.xml
│   ├── solution.xml
│   ├── Assets/                         # Knowledge source configurations
│   ├── bots/                           # Bot definitions (2 agents)
│   ├── botcomponents/                  # Topics, actions, configurations
│   │   ├── auto_agent_c2hGx.gpt.default/
│   │   ├── auto_agent_c2hGx.InvokeConnectedAgentTaskAction.PathfinderFDADocuments/
│   │   ├── [Conversation management topics]
│   │   ├── [6 SOP alphabetical range topics]
│   │   └── [Legacy SOP routing topics]
│   ├── dvtablesearchentities/          # 400+ search entities
│   └── dvtablesearchs/                 # 6 knowledge source configs
│
├── PathFinderFDADocuments/             # FDA specialist agent solution package
│   ├── README.md                       # Detailed FDA agent documentation
│   ├── [Content_Types].xml
│   ├── customizations.xml
│   ├── solution.xml
│   ├── Assets/                         # Connection references & knowledge configs
│   ├── bots/                           # FDA agent bot definition
│   ├── botcomponents/                  # Topics, actions, Excel integration
│   │   ├── auto_agent_YWfmN.gpt.default/
│   │   ├── auto_agent_YWfmN.action.ExcelOnlineBusiness-Listrowspresentinatable/
│   │   ├── [Conversation management topics]
│   │   ├── [7 FDA specialty topics]
│   │   ├── [14 knowledge source topics]
│   │   └── [FDA ID to Topic Mapper]
│   ├── dvtablesearchentities/          # 1000+ FDA document search entities
│   └── dvtablesearchs/                 # 13 specialty-specific search configs
│
└── Python_Code/                        # FDA PDF preprocessing utilities
    ├── README.md                       # Python utilities documentation
    ├── merge_paired_fda_files.py       # Main driver script
    └── FDA_PDF_Functions/              # Core library
        ├── __init__.py
        ├── pairing.py                  # Pair BASE/REVIEW PDFs
        ├── merge.py                    # Merge paired PDFs
        ├── copying.py                  # Copy unpaired PDFs
        ├── validate.py                 # Validate PDF readability
        └── report.py                   # Generate summaries
```

---

## Additional resources

**PathFinder components**:
- [PathFinder README](PathFinder/README.md) — Detailed primary agent documentation
- [PathFinder FDA Documents README](PathFinderFDADocuments/README.md) — FDA specialist agent documentation
- [Python Processing README](Python_Code/README.md) — PDF preprocessing utilities guide

**External references**:
* GPT‑4.1 long‑context + agentic/tool use: OpenAI & Azure announcements. ([OpenAI Platform][1])
* Generative orchestration & knowledge behavior: Copilot Studio docs. ([Microsoft Learn][2])
* Connected agents (handoff): Copilot Studio docs (preview). ([Microsoft Learn][3])
* User feedback (thumbs‑up/down + comment): release plan. ([Microsoft Learn][4])
* Tenant Graph grounding / Semantic Index: Microsoft 365 & Copilot Studio docs. ([Microsoft Learn][5])
* Strict grounding & knowledge-only mode: Copilot Studio guidance. ([Microsoft Learn][6])
* Web search is optional; we leave it **off**: Copilot Studio guidance. ([Microsoft Learn][7])

---

[1]: https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4
[2]: https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers
[3]: https://learn.microsoft.com/microsoft-copilot-studio/copilot-ai-plugins
[4]: https://learn.microsoft.com/microsoft-copilot-studio/analytics-user-satisfaction
[5]: https://learn.microsoft.com/microsoft-365-copilot/extensibility/overview-graph-connector
[6]: https://learn.microsoft.com/microsoft-copilot-studio/nlu-boost-conversations
[7]: https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers-bing