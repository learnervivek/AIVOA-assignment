# AI-Powered Root Cause Analysis (RCA) Module
## Demo & Video Presentation Scripts (Submission Ready)

This document provides complete, verbatim recording scripts, teleprompter text, screen action cues, and timing breakdowns for both required submission videos:
- **Video 1: Product Demonstration (5–8 Minutes)**
- **Video 2: Technical Walkthrough & Code Explanation (5–10 Minutes)**

---

> [!IMPORTANT]
> **Submission & Privacy Notice**:
> If your assignment guidelines strictly forbid uploading source code, demo videos, or materials to public repositories, **ensure your GitHub repository (`https://github.com/learnervivek/AIVOA-assignment.git`) is set to PRIVATE** in repository settings:
> `GitHub Repo -> Settings -> Danger Zone -> Change repository visibility -> Make private`.

---

## VIDEO 1: Product Demonstration (5–8 Minutes)

### Video Metadata & Quick Reference
- **Target Duration**: ~6 minutes 30 seconds (safe buffer within 5–8 min limit)
- **Goal**: Demonstrate the working application, highlighting the clinical pharma QMS design, AI-first auto-population, missing evidence detection, 5-Whys/Fishbone exploration, QA verification, and single-transaction persistence.
- **Pre-Recording Setup Checklist**:
  1. Backend running: `http://127.0.0.1:8000` (Health check returns `connected`).
  2. Frontend running: `http://127.0.0.1:5173`.
  3. Browser open at `http://127.0.0.1:5173` at 100% zoom.
  4. Ensure `sample_data/deviation_oos_assay.pdf` is accessible on Desktop or file picker, or use the built-in **"Quick Demo Scenarios"** dropdown.

---

### Step-by-Step Script & Storyboard

```
TIMELINE SUMMARY:
[0:00 - 1:00] Act 1: Introduction & The Problem in Pharma API Manufacturing
[1:00 - 2:30] Act 2: Document Ingestion & LangGraph AI Processing
[2:30 - 4:15] Act 3: Form Auto-Population & Deep Causal Exploration (5-Whys & 6M)
[4:15 - 5:45] Act 4: Human-in-the-Loop Review, QA Verification & CAPA Formulation
[5:45 - 6:45] Act 5: Single-Transaction PostgreSQL Save & Database Round-Trip
```

#### [0:00 - 1:00] Act 1: Introduction & The Problem in Pharma API Manufacturing
- **Screen**: Full view of the clean, clinical interface at `http://127.0.0.1:5173`. Mouse hovers over the navigation bar, Left Sidebar, Center Workspace, and Right AI Co-Pilot Panel.
- **Spoken Script**:
  > *"Hello everyone. Today I'm demonstrating our AI-Powered Root Cause Analysis and CAPA module, built specifically for pharmaceutical Active Pharmaceutical Ingredient (API) manufacturing plants under ICH Q7, ICH Q9, and ICH Q10 guidelines.*
  >
  > *In pharmaceutical manufacturing, when an Out-of-Specification or process deviation occurs, investigators are buried under dozens of pages of batch records, calibration logs, and analytical reports. Traditional QMS tools force quality investigators to manually type hundreds of form fields, leading to human error, missed regulatory evidence, and slow deviation closures.*
  >
  > *We built an AI-first, compliance-focused solution with three distinct workspaces: on the left, a collapsible history of saved deviations; in the center, our structured ICH Q7 investigation workspace; and on the right, our persistent AI Co-Pilot panel powered by a multi-node LangGraph state machine and Groq's Llama 3.3 70B model.*
  >
  > *Let's walk through an actual incident."*

---

#### [1:00 - 2:30] Act 2: Document Ingestion & LangGraph AI Processing
- **Screen**: Move cursor to the right **AI Co-Pilot Panel**. Show the three input modes: "Upload PDF", "Paste Email", and "Paste Text". Click the **"Quick Demo Scenarios"** dropdown and select **"Atorvastatin HPLC Assay OOS (PDF)"**.
- **Spoken Script**:
  > *"Investigators receive information through multiple channels: PDF deviation tickets, supervisor handover emails, or raw equipment log pastes. Our platform natively supports all three.*
  >
  > *Here, I will load an authentic API deviation scenario: Batch BAT-ATC-2026-0914 of Atorvastatin Calcium failed its HPLC Assay specification with a 94.2% result following an unexplained temperature spike during crystallization in Reactor REACT-CR-01.*
  >
  > *Notice that we don't have to manually fill out the form. I'll simply click 'Analyze & Auto-Populate Form'.*
  >
  > *Watch the live execution stream in the AI Co-Pilot. The LangGraph state machine executes four sequential nodes:*
  > *1. First, `extract_deviation_fields` extracts the exact batch, equipment, date, and severity with strict zero-hallucination guardrails.*
  > *2. Next, `detect_missing_evidence` acts as a Senior GMP QA Auditor, scanning the input for critical investigation gaps.*
  > *3. Third, `perform_rca_analysis` generates both an empirical 5-Whys causal chain and a 6M Ishikawa Fishbone breakdown.*
  > *4. Finally, `recommend_capa` synthesizes actionable Corrective and Preventive actions.*
  >
  > *Now I click 'Apply AI Output to Form', and our entire investigation workspace is populated in seconds."*

---

#### [2:30 - 4:15] Act 3: Form Auto-Population & Deep Causal Exploration (5-Whys & 6M)
- **Screen**: Focus on Center Workspace. Scroll through Section 1 (Deviation Overview), Section 2 (Missing Evidence Callout), Section 3 (Root Cause Analysis - 5 Whys & Fishbone tabs).
- **Spoken Script**:
  > *"Let's examine how the form was populated.*
  >
  > *In Section 1, Deviation Overview, all core parameters—Deviation ID, Product Name, Lot Number, Equipment ID, Crystallization Stage, Critical Severity, and Immediate Containment—are cleanly entered. Notice the subtle blue 'AI Extracted' badges. This provides complete audit trail provenance.*
  >
  > *Now look at Section 2: Missing Evidence & Investigation Gaps. This is one of our flagship compliance features. Even though the incident text described the failure, the AI auditor recognized that 3 critical GMP records are missing before root cause can be legally proven:*
  > *1. The calibration certificate and service log for thermocouple TT-104.*
  > *2. Operator training and qualification records for the crystallization manual cooling bypass.*
  > *3. The raw HPLC chromatograms and system suitability run packets.*
  > *This immediately alerts QA to gather the right physical evidence before closing the deviation.*
  >
  > *Next, let's explore Section 3: Root Cause Analysis. We provide interactive dual methodologies.*
  > *In the '5 Whys' tab, we see a vertical connected stepper drilling down from the initial Assay OOS, to thermal excursion, to cooling water valve actuator failure, down to diaphragm rupture and lack of PM schedule. Every single step is directly editable, and investigators can even click 'Ask AI to Deepen Step' to dynamically explore a deeper root cause.*
  >
  > *Switching to the 'Fishbone (6M)' tab, the platform presents a clean 6-category Ishikawa grid: Man, Machine, Material, Method, Measurement, and Environment. Investigators can add, edit, or delete contributing factors under each dimension."*

---

#### [4:15 - 5:45] Act 4: Human-in-the-Loop Review, QA Verification & CAPA Formulation
- **Screen**: Click into the Title field or Immediate Containment field and edit the text slightly. Point out the badge transitioning from `"AI Extracted"` to `"Edited"`. Scroll down to the Potential Root Causes cards. Point out the `"Suggested – Unverified"` pill and the compliance notice. Check the `"Confirm Root Cause (QA Verified)"` toggle and type justification notes. Scroll down to Section 4 (CAPA).
- **Spoken Script**:
  > *"A critical tenet of 21 CFR Part 11 and cGMP is that AI cannot be a black box that unilaterally makes quality decisions. The qualified human investigator must remain in control.*
  >
  > *Notice what happens when I edit the Title or Immediate Containment field: the badge instantly updates from 'AI Extracted' to 'Edited', tracking investigator modifications.*
  >
  > *Below the 6M diagram, we have our Potential Root Causes cards. Notice the prominent regulatory notice: 'AI-generated root causes are suggestions only until verified against evidence by a qualified person.' Every AI cause defaults to 'Suggested – Unverified'.*
  >
  > *As the QA Lead, once I review the maintenance records, I toggle 'Confirm Root Cause (QA Verified)'. An evidence justification box appears where I enter: 'QA verified diaphragm failure against physical work order #WO-4921 and instrumentation log.' The cause is now formally verified.*
  >
  > *In Section 4, CAPA Recommendations, the AI has formulated balanced actions: a Corrective Action to rebuild and recalibrate reactor valve TT-104 prior to line release, and a Preventive Action to automate PLC interlock alarms and increase PM inspection frequency to quarterly. Each row allows full editing of owners, target due dates, and action types."*

---

#### [5:45 - 6:45] Act 5: Single-Transaction PostgreSQL Save & Database Round-Trip
- **Screen**: Click the **"Save Investigation"** button in the header. Point out the floating green **21 CFR Part 11 Audit Confirmation Toast**. Show the Left Sidebar updating with the new deviation. Click a different deviation in the sidebar, then click back to `DEV-2026-0914` to show instant reloading from PostgreSQL.
- **Spoken Script**:
  > *"Now that our review is complete, I click 'Save Investigation' in the top header.*
  >
  > *Notice the confirmation toast: the entire investigation—including the deviation metadata, the 5-Whys causal chain, the 6M Fishbone JSONB data, the QA-confirmed root causes with verification notes, and all CAPA action items—was persisted to PostgreSQL in a single atomic transaction. No orphaned records, no partial saves.*
  >
  > *In the Left Sidebar, our saved deviation appears immediately with its 'Critical' severity pill and 'Under Review' status badge.*
  >
  > *If I click on another saved investigation and then reopen DEV-2026-0914, all fields, verified toggles, and CAPA dates reload instantly from the database with 100% fidelity.*
  >
  > *That concludes our product demonstration. Thank you!"*

---

## VIDEO 2: Technical Walkthrough & Code Explanation (5–10 Minutes)

### Video Metadata & Quick Reference
- **Target Duration**: ~8 minutes (safe buffer within 5–10 min limit)
- **Goal**: Walk through the codebase architecture, explaining the frontend Redux Toolkit state, document extraction service, LangGraph multi-node state machine, Pydantic v2 schemas, Groq integration, and PostgreSQL atomic single-transaction persistence.
- **Pre-Recording Setup Checklist**:
  1. Open VS Code / IDE with the `aivoa-assignment` repository open.
  2. Have terminal ready showing passing tests: `backend/venv/bin/pytest -v` (21 passed) and `frontend/` build green.
  3. Pre-open key files in IDE tabs:
     - `README.md` (Architecture diagram)
     - `backend/app/models/investigation.py` & `rca_analysis.py` & `capa.py`
     - `backend/app/services/extractor.py`
     - `backend/app/ai/graph.py` & `backend/app/ai/nodes/`
     - `backend/app/api/v1/endpoints/investigations.py`
     - `frontend/src/store/slices/rcaSlice.ts`
     - `frontend/src/components/RCAForm/RCAAnalysisSection.tsx`

---

### Step-by-Step Script & Code Walkthrough

```
TIMELINE SUMMARY:
[0:00 - 1:15] Module 1: Monorepo Architecture, Tech Stack & Architecture Flow Diagram
[1:15 - 2:45] Module 2: Document & Email Ingestion Engine (extractor.py)
[2:45 - 5:15] Module 3: LangGraph Multi-Node Workflow & Groq Structured Outputs
[5:15 - 6:45] Module 4: Frontend State Management & AI Provenance (Redux Toolkit)
[6:45 - 8:00] Module 5: PostgreSQL Database Integration & Single-Transaction ACID Persistence
```

#### [0:00 - 1:15] Module 1: Monorepo Architecture & Tech Stack
- **Screen**: Open `README.md` in VS Code preview showing the Mermaid architecture diagram. Briefly show the folder tree in the explorer (`/backend`, `/frontend`, `docker-compose.yml`, `scripts/`).
- **Spoken Script**:
  > *"Welcome to the technical code walkthrough of our AI-Powered Root Cause Analysis module. I'll walk you through our architecture, design patterns, and end-to-end data flow.*
  >
  > *The project is organized as a clean monorepo:*
  > *- `/backend`: Python 3.11 with FastAPI, SQLAlchemy 2.0 async, Pydantic v2, and LangGraph.*
  > *- `/frontend`: React 18 with Vite, Redux Toolkit, TypeScript, and Tailwind CSS.*
  > *- `docker-compose.yml`: Provisions an isolated PostgreSQL 16 database.*
  > *- `/scripts`: Houses automated sample data generators and our end-to-end verification script.*
  >
  > *As shown in our architecture diagram, the frontend communicates with FastAPI endpoints for document extraction, AI orchestration, and persistence. The backend executes a 4-node LangGraph state machine backed by Groq's Llama 3.3 70B model with structured outputs, persisting data to PostgreSQL."*

---

#### [1:15 - 2:45] Module 2: Document & Email Ingestion Engine (`extractor.py`)
- **Screen**: Open `backend/app/services/extractor.py`. Highlight `extract_text_from_pdf` and `extract_text_from_raw_or_email`.
- **Spoken Script**:
  > *"Let's start at the ingestion layer in `backend/app/services/extractor.py`.*
  >
  > *When an investigator uploads a PDF, `extract_text_from_pdf` validates the file headers, uses `pypdf` to extract text page by page, and normalizes excessive whitespace.*
  >
  > *Notice `detect_pharma_entities`: we run high-precision regular expressions tailored to pharma conventions to immediately detect deviation numbers like `DEV-YYYY-XXXX`, lot numbers, equipment IDs, and severity keywords.*
  >
  > *For pasted emails or shift handover notes, `extract_text_from_raw_or_email` parses standard RFC email headers—Subject, From, Date, and To—separating the header metadata from the narrative body.*
  >
  > *These services are exposed through `POST /api/investigations/extract-file` and `POST /api/investigations/extract-text`, returning clean text and detected entities to the client."*

---

#### [2:45 - 5:15] Module 3: LangGraph Multi-Node Workflow & Groq Structured Outputs
- **Screen**: Open `backend/app/ai/graph.py`, then `backend/app/ai/state.py`, and briefly open `backend/app/ai/nodes/extract.py`, `audit.py`, `rca.py`, and `capa.py`.
- **Spoken Script**:
  > *"Now let's examine the AI engine in `backend/app/ai/`.*
  >
  > *In `graph.py`, we construct a LangGraph `StateGraph` parameterized by `RCAWorkflowState`. The execution graph runs 4 sequential nodes:*
  > *`START -> extract_deviation_fields -> detect_missing_evidence -> perform_rca_analysis -> recommend_capa -> END`.*
  >
  > *Let's look at each node:*
  > *1. `extract_deviation_fields` in `nodes/extract.py`: We invoke Groq's `llama-3.3-70b-versatile` using LangChain's `.with_structured_output()` bound to our Pydantic schema `DeviationFieldsOutput`. We enforce strict GMP prompts: if a batch number or date is not in the text, it must be returned as null—never hallucinated.*
  > *2. `detect_missing_evidence` in `nodes/audit.py`: The LLM is instructed to adopt the persona of a Senior GMP QA Auditor. It scans the extracted facts and systematically flags missing calibration logs, operator training records, and analytical chromatograms.*
  > *3. `perform_rca_analysis` in `nodes/rca.py`: This node concurrently generates both a 5-Whys causal chain and a 6M Ishikawa breakdown (Man, Machine, Material, Method, Measurement, Environment). Crucially, every identified root cause defaults to `is_ai_suggested: True` and `is_confirmed_by_qa: False` with supporting evidence citations.*
  > *4. `recommend_capa` in `nodes/capa.py`: Formulates Corrective and Preventive actions tied to the root causes with ICH Q10 rationales.*
  >
  > *In addition, we have an interactive `refine_rca` node in `nodes/refine.py` triggered by `POST /api/ai/refine`, allowing investigators to ask the AI to deepen a specific why-level or propose specialized CAPAs.*
  >
  > *Notice our resilience pattern in `backend/app/ai/client.py`: if Groq API keys are not supplied or hit rate limits, the system seamlessly falls back to a deterministic, rule-based ICH Q7 analyzer so development, CI, and demos never fail."*

---

#### [5:15 - 6:45] Module 4: Frontend State Management & AI Provenance (Redux Toolkit)
- **Screen**: Open `frontend/src/store/slices/rcaSlice.ts`. Highlight `aiPopulatedFields`, `setFormField`, `applyAIPayload`, and `confirmRootCause`. Then open `frontend/src/components/RCAForm/RCAAnalysisSection.tsx`.
- **Spoken Script**:
  > *"Moving to the frontend, state management is cleanly centralized using Redux Toolkit in `frontend/src/store/`.*
  >
  > *In `rcaSlice.ts`, we track: `investigationForm`, `rcaAnalysis`, `capaRecommendations`, `savedInvestigations`, and `aiPopulatedFields`.*
  >
  > *Notice how provenance tracking works: when the AI payload is applied via `applyAIPayload`, all auto-populated field keys are recorded in `aiPopulatedFields`. When the user edits any field via `setFormField`, that key is automatically removed from `aiPopulatedFields`. In `DeviationOverviewSection.tsx`, this instantly changes the UI badge from 'AI Extracted' to 'Edited'.*
  >
  > *For regulatory compliance, `confirmRootCause` takes the index of a potential root cause, marks `is_confirmed_by_qa: true`, and stores the investigator's explicit QA justification notes.*
  >
  > *In `RCAAnalysisSection.tsx`, we built custom interactive components: a vertical connected 5-Whys stepper with dynamic deepening, and a responsive 6M Fishbone grid."*

---

#### [6:45 - 8:00] Module 5: PostgreSQL Database Integration & Single-Transaction ACID Persistence
- **Screen**: Open `backend/app/models/investigation.py`, `rca_analysis.py`, `capa.py`, and `backend/app/api/v1/endpoints/investigations.py` at `create_investigation`.
- **Spoken Script**:
  > *"Finally, let's examine the persistence layer.*
  >
  > *In `backend/app/models/`, we define our three relational models:*
  > *- `Investigation`: stores core deviation parameters, severity, and status.*
  > *- `RCAAnalysis`: linked via foreign key with `CASCADE` delete. We leverage PostgreSQL's native `JSONB` type for `five_whys_data`, `fishbone_6m_data`, `potential_root_causes`, and `missing_evidence`. This provides rich JSON schema querying without excessive relational joins.*
  > *- `CAPARecommendation`: stores corrective and preventive actions with owners and due dates.*
  >
  > *Now look at `create_investigation` in `endpoints/investigations.py`.*
  > *We accept `InvestigationCreateFull`, which bundles the deviation, nested RCA analysis, and CAPA list into a single payload. In line 218 to 259, we insert the investigation, the RCA record, and the CAPA items within an `AsyncSession`, calling `await db.commit()` only once. This guarantees complete ACID atomicity—either the full investigation saves, or nothing saves.*
  >
  > *We also have a full test suite in `backend/tests/` where all 21 unit and integration tests pass in 0.11 seconds, and our end-to-end verification script `scripts/verify_e2e.py` validates the complete round-trip.*
  >
  > *This concludes our code walkthrough. Thank you!"*

---

## Deliverables & Submission Checklist

- [x] **Working Application**:
  - Backend running on `http://127.0.0.1:8000` (FastAPI + LangGraph + PostgreSQL).
  - Frontend running on `http://127.0.0.1:5173` (React 18 + Redux Toolkit + Tailwind CSS).
  - Database schema initialized and seeded (`docker-compose.yml` / PostgreSQL).
- [x] **Video 1: Product Demonstration (5–8 minutes)**:
  - Follow the exact 5-act script in Section 1 above.
  - Demonstrates PDF upload / text paste, LangGraph AI analysis, auto-population, 5-Whys stepper, 6M Fishbone, missing evidence detection, human-in-the-loop edits, QA confirmation, and PostgreSQL persistence.
- [x] **Video 2: Technical Walkthrough (5–10 minutes)**:
  - Follow the exact 5-module script in Section 2 above.
  - Explains monorepo architecture, document extraction, LangGraph state machine, Redux state & provenance badges, Pydantic schemas, and single-transaction database persistence.
- [x] **Privacy & Repository Notice**:
  - Ensure the repository is set to **Private** on GitHub to adhere to submission policies.
