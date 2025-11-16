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

**[View API Docs](PathFinder/README.md)]**

* Copilot Studio **solution package**
* 6 alphabetized SOP topics; conversation management (greetings, fallback, escalation)
* Data table search configurations

**Agent rules**: Return **full SOP** for broad queries; **section‑only** for specifics; **preserve** numeric values/units/tables; **always cite** source + page/section; route FDA terms to the FDA agent.

### 2) PathFinder FDA Documents — specialist agent

**[View API Docs](PathFinderFDADocuments/README.md)]**

* Copilot Studio **solution package**
* Specialty topics (Chemistry, Hematology, Microbiology, Toxicology, …)
* **Excel Online Business** integration for `K######` → topic routing
* FDA‑specific search entities + connection references

**Agent rules**: Section‑level 510(k) retrieval with verbatim **product codes**, **regulatory class**, **regulation number**, **decision date**; **always cite** source + page/section.

### 3) Python PDF processing

**[View API Docs](Python_Code/README.md)]**

Utilities to scan/pair **BASE + BASE_REVIEW** PDFs, **merge** pairs (mirror structure), **validate**, and **report**. Purpose: reduce file count while preserving complete dossiers for indexing.

---

## Quick start

**Import packaged solutions**

1. In Copilot Studio → **Solutions** → **Import**:  (managed) and  (managed).
2. Configure **Excel Online Business** connection (FDA agent).
3. Attach SOP and FDA knowledge sources; (optional) **connect agents** for handoff.
4. Publish (web/Teams) and test.

**Publisher**: BCM Clinical Informatics • **Customization prefix**: `bcmci`
**Institution**: Baylor College of Medicine / Texas Children's Hospital

### Notes on sources

* GPT‑4.1 long‑context + agentic/tool use: OpenAI & Azure announcements. ([OpenAI Platform][1])
* Generative orchestration & knowledge behavior: Copilot Studio docs. ([Microsoft Learn][2])
* Connected agents (handoff): Copilot Studio docs (preview). ([Microsoft Learn][3])
* User feedback (thumbs‑up/down + comment): release plan. ([Microsoft Learn][4])
* Tenant Graph grounding / Semantic Index: Microsoft 365 & Copilot Studio docs. ([Microsoft Learn][5])
* Web search is optional; we leave it **off**: Copilot Studio guidance. ([Microsoft Learn][7])