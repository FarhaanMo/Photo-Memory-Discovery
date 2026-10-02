# Problem Statement: Google Photos Retrieval Discovery Engine

**Document type:** Product Management research brief  
**Project:** AI-Powered Google Photos Retrieval Discovery Engine  
**Status:** Discovery / research MVP (no product solution selected)

This document restates the problem, research question, dataset, and MVP requirements. It does **not** select a product solution. The discovery engine must analyse evidence neutrally and remain capable of disproving initial hypotheses.

---

## 1. Background

Google Photos stores years of personal photos, videos, screenshots, documents, and other visual memories.

Users can often search effectively when they know exactly what they are looking for. Retrieval becomes significantly harder when a user **remembers that a particular photo exists** but cannot precisely remember its date, location, album, exact text, object name, or other searchable attributes.

Typical examples of this situation:

- “That small café we went to during our Goa trip.”
- “The picture of the medicine I took when I was sick last year.”
- “That screenshot I saved about a job but I don’t remember when.”
- “A restaurant photo from a holiday where I remember what happened before it, but not the restaurant name.”

This is a **vague-memory retrieval** problem: the user has a real target in mind, but the memory they can verbalise at the start of search is incomplete, imprecise, or poorly matched to existing search affordances.

The project is **not** intended to improve Google Photos search in general. The immediate purpose of this work is to build an AI-powered **discovery engine** that analyses real public user conversations about photo retrieval and identifies **why** vaguely remembered photo retrieval fails.

Semantic triage of the **broad** public corpus (Corpus A, N = 225) showed that this landscape contains few strong vague-memory examples (`direct_vague_retrieval` = 4; `retrieval_adjacent` = 116; `irrelevant` = 105). Those counts describe **this corpus**, not Google Photos users at large. The research therefore uses a **two-corpus** design (Section 9): Corpus A for the broad retrieval landscape; Corpus B (targeted) for deep qualitative analysis of vague-memory retrieval.

---

## 2. Business Goal

Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they begin searching.

The discovery engine does not implement that business goal as a consumer product. It produces evidence so a Product Manager can later decide **which part of the retrieval journey** is the strongest opportunity.

---

## 3. Research Question

**Why does retrieval fail when a Google Photos user remembers that a specific photo exists but cannot precisely describe when, where, or what it was when they begin searching?**

Supporting questions the engine should help a Product Manager answer from evidence (not from assumption):

- What types of old images do users struggle to retrieve?
- What do users remember about those images?
- What have they forgotten?
- How do they initially attempt retrieval?
- Where do retrieval journeys fail?
- What do users do after a failed search?
- Which failure stages occur most frequently **within a stated sampling frame**
- Which remembered clues are associated with different failure types **within the targeted vague-memory sample**
- Which retrieval problems appear repeatedly across different public sources **in the broad landscape**

---

## 4. Scope

### In scope

- Public user conversations that are **genuinely about finding or retrieving an existing old photo or image**.
- Classification of those conversations into retrieval-relevant vs. irrelevant.
- Structured analysis of remembered clues, forgotten information, search strategies, failure stages, workarounds, outcomes, and problem themes.
- Aggregation of **programmatically calculated** statistics from classified records.
- A lightweight research interface that lets a Product Manager inspect evidence behind every insight.

### Out of scope for relevance (treat as irrelevant unless the conversation is clearly about retrieval)

Discussions primarily about:

- backup problems
- syncing problems
- storage limits
- subscriptions
- account access
- crashes
- editing features
- upload problems
- general complaints unrelated to retrieval

### Analysis boundary

Only relevant retrieval records should feed failure-stage maps, clue analysis, and research Q&A **for the currently selected sampling frame**. Irrelevant records should still be counted in dataset overview so coverage and filtering quality remain visible.

**Never** pool Corpus A and Corpus B to estimate how common vague-memory retrieval is. Deep memory/clue/workaround analysis of the core research question uses Corpus B and must be worded as findings *within the targeted vague-memory retrieval sample*.

---

## 5. Users / Research Population

### Primary user of the application

A **Product Manager** (and reviewers of a Product Management graduation project) using the discovery engine to investigate vague-photo retrieval failure.

The interface must be professional, minimal, and suitable for demonstration. It should prioritise clear data, readable charts, evidence, simple filters, and a strong information hierarchy. Avoid excessive animation.

### Research population (data subjects)

The analysed population is **public user conversations** about trying to find existing photos or images, not a private Google Photos corpus and not a recruited lab panel.

There are **two sampling frames** (Section 9). Corpus A is a broad public dump (~225 records). Corpus B is a forthcoming targeted qualitative set of strong vague-memory examples. Corpus B is **not** representative of all Google Photos users.

During development, the application must also work correctly with a small test dataset of **10–20** records.

Potential sources include:

- Reddit
- Google Photos Community / Support discussions
- Google Play Store reviews
- Apple App Store reviews
- YouTube comments
- Other relevant public forums

The data may initially be supplied as a **CSV file**. Automatic scraping inside the application is not required for the MVP.

---

## 6. Current Retrieval Journey

The following journey is a **descriptive research frame**, not a proposed product flow. It is inferred from how people talk about finding old photos when memory is incomplete.

1. **Need to find an existing image**  
   The user believes a specific photo, screenshot, document image, or video still exists in Google Photos (or a similar library).

2. **Partial memory at search start**  
   The user may remember some combination of people, rough time, rough location, objects, visible text, event, purpose for saving, sequence of events, associations (for example sending it to someone), or visual characteristics (indoor/outdoor, colour, lighting). Some of these attributes may be missing, wrong, or too vague to type as a query.

3. **Attempt to express the memory as a search or retrieval action**  
   The user tries to convert what they remember into searchable words, dates, people, places, albums, or other library affordances.

4. **System returns a result set (or fails to)**  
   Results may be empty, off-target, or contain many similar candidates.

5. **User evaluates candidates**  
   The user must recognise the correct image among whatever is shown.

6. **Refine, switch strategy, or stop**  
   If the first attempt fails, the user may try to refine the search, switch to a workaround, or give up.

Observed workaround classes to capture when present in the source text:

- manual timeline scrolling
- albums
- People & Pets
- Places / Maps
- another application
- asking another person
- giving up

This journey is the object of study. **The engine must not assume** that conversational search, progressive memory reconstruction, or any other specific intervention is the correct fix.

---

## 7. Candidate Failure Modes

Failure stages are **hypotheses to be coded from evidence**. The engine must be able to show that some stages are rare, poorly evidenced, or secondary.

| Failure stage | Definition |
| --- | --- |
| **Expression failure** | The user remembers something about the photo but struggles to convert that memory into useful searchable words or attributes. |
| **Retrieval / interpretation failure** | The user provides reasonable clues but the expected or relevant photo does not appear. |
| **Evaluation failure** | Potentially relevant results appear but the user struggles to identify the correct photo among many similar candidates. |
| **Recovery / refinement failure** | The first attempt fails and the user does not know how to refine the search or make progress. |
| **Other / unclear** | There is not enough information to confidently identify the failure stage. |

If a conversation does not explicitly support a stage, the classification must be **unknown / unclear**, not a guess.

---

## 8. AI Discovery Engine Objective

Build a lightweight AI-powered research application named:

**Google Photos Retrieval Discovery Engine**

The engine’s job is **discovery and evidence generation**, not solution selection.

It must:

- Analyse public conversations about vaguely remembered photo retrieval.
- Extract structured fields from relevant records (see Functional Requirements).
- Help a Product Manager see **where** retrieval fails and **why**, grounded in source text.
- Remain neutral among candidate failure modes and product ideas.
- Be capable of **disproving** initial hypotheses if the classified dataset does not support them.
- **Not** choose the final product solution.

This is a Product Management research/discovery engine, **not** a generic sentiment-analysis application.

---

## 9. Dataset Definition

Research uses **two corpora**. They share the same minimum source schema (`record_id`, `source`, `date`, `url`, `raw_text`, plus optional metadata). They must **not** be treated as one prevalence sample.

### 9.1 Field: `sampling_frame`

Allowed values:

| Value | Meaning |
| --- | --- |
| `broad` | Corpus A — opportunistic public landscape of Google Photos / photo-library talk |
| `targeted_direct` | Corpus B — purposively collected strong examples of vague-memory retrieval |

Every ingested row, processed row, chart, and Ask-the-Research answer must remain tagged with its `sampling_frame`.

### 9.2 Corpus A — broad public retrieval landscape

| Attribute | Requirement |
| --- | --- |
| File | `data/google_photos_retrieval_raw.csv` |
| `sampling_frame` | `broad` |
| Role | Understand the **overall retrieval landscape** in public conversations (relevant search failures, adjacent search-quality issues, and irrelevant noise) |
| Size | Approximately **225** public-source records (existing file). **Do not delete or modify this file.** |
| Use | Compare broad retrieval problems; report triage/relevance mixes **only within this frame** |
| Not for | Estimating how common vague-memory retrieval is among Google Photos users |

Semantic triage of Corpus A found few `direct_vague_retrieval` rows. That is a property of **this sampling frame**, not a population rate.

### 9.3 Corpus B — targeted vague-memory retrieval sample

| Attribute | Requirement |
| --- | --- |
| File | `data/google_photos_direct_vague_targeted.csv` |
| `sampling_frame` | `targeted_direct` |
| Role | **Qualitative** corpus of **strong** vague-memory retrieval examples only |
| Status | **Does not exist yet.** Do not invent rows. Do not run additional LLM classification until this file is collected. |
| Use | Deep analysis of what users remember and forget, how they formulate searches, where retrieval fails, how they refine, and what workarounds they use |
| Wording of findings | Always: “Within the targeted vague-memory retrieval sample…” |
| Not for | Representing all Google Photos users; pooling with Corpus A for prevalence |

### 9.4 Research rules for the two frames

1. Never combine the two sampling frames to estimate prevalence of vague-memory retrieval.
2. Corpus A may be used to compare broad retrieval problems.
3. Corpus B will be used for deep analysis of remember / forget / search formulation / failure / refinement / workarounds.
4. Findings from Corpus B must be described as “Within the targeted vague-memory retrieval sample…”
5. Do not describe Corpus B as representative of all Google Photos users.
6. Preserve source URLs and source metadata on every record in both corpora.
7. Do not run additional LLM classification until Corpus B exists and a later phase requests it.

### 9.5 Shared ingestion rules

| Attribute | Requirement |
| --- | --- |
| Nature | Publicly available user conversations (both frames) |
| Ingestion | CSV supplied to the application (scraping not required in-app) |
| Provenance | Original user text and source URL must be preserved |
| Traceability | Every finding must be traceable to `record_id`, `sampling_frame`, and source text |

The LLM must not invent dataset statistics, sources, or quotes. Counts, percentages, and distributions are calculated from the stored classified data **within one sampling frame at a time**.

---

## 10. Data Schema

### Original record (minimum)

Each ingested record must contain at least:

| Field | Purpose |
| --- | --- |
| `record_id` | Stable identifier for traceability |
| `source` | Origin (e.g. Reddit, Play Store, community forum) |
| `date` | Date of the public conversation, as available |
| `url` | Link back to the original public post/comment/review |
| `raw_text` | Unaltered original user text |
| `sampling_frame` | `broad` or `targeted_direct` (required conceptually; may be implied by which file was loaded until Corpus B exists) |

### AI-extracted fields (per relevant record)

For every relevant record, the AI should extract and classify:

1. **Photo / image type** the user is trying to retrieve  
2. **What the user remembers**, using these clue types when present:
   - person / people
   - rough time
   - rough location
   - object
   - visible text
   - event / occasion
   - purpose for taking or saving the image
   - sequence of events before or after the image
   - association (e.g. sending it to someone)
   - visual characteristics (indoor/outdoor, colour, lighting, etc.)
3. **What information the user has forgotten**  
4. **Search or retrieval strategy attempted**  
5. **Primary failure stage** (expression; retrieval/interpretation; evaluation; recovery/refinement; other/unclear)  
6. **Whether the user attempted to refine the search**  
7. **Workaround used** (timeline, albums, People & Pets, Places/Maps, another app, asking another person, giving up, or unknown)  
8. **Retrieval outcome**  
9. **Primary problem theme**  
10. **Evidence strength**

Classifications must stay attached to the original `record_id` and `raw_text`. If a field is not explicitly supported by the conversation, store `unknown` / `unclear` rather than inferring.

---

## 11. Core Product Requirements

The application must provide these research surfaces.

### 11.1 Dataset Overview

Display (always labelled with the active `sampling_frame`):

- total records
- relevant retrieval records
- irrelevant records
- source distribution
- failure-stage distribution
- common remembered clues
- common workarounds
- retrieval outcomes

All of the above must be computed from the dataset, not generated as free-text LLM estimates.

### 11.2 Retrieval Problem Map

Allow comparison of:

- Expression Failure
- Retrieval / Interpretation Failure
- Evaluation Failure
- Recovery / Refinement Failure

Show **counts and percentages based only on analysed records**.

### 11.3 Memory Clue Analysis

Show which information users commonly remember:

- people
- time
- place
- object
- text
- event
- purpose
- sequence
- association
- visual characteristics

Also show what information users commonly forget.

### 11.4 Evidence Explorer

Allow the researcher to filter records by:

- source
- failure stage
- photo type
- remembered clue
- outcome
- problem theme

Each result must display:

- record ID
- source
- original user text
- classifications
- source URL

### 11.5 Ask the Research

Provide a question box where the researcher can ask questions such as:

- “What do users remember when they cannot remember the date?”
- “What happens after the first search attempt fails?”
- “Which retrieval problems occur most often with screenshots?”
- “Compare expression failure and recovery failure.”

Rules for answers:

- Grounded **only** in records in the dataset.
- Cite supporting **record IDs**.
- State when there is **insufficient evidence** instead of generating unsupported conclusions.

---

## 12. Functional Requirements

1. Accept a CSV dataset of public conversations matching the original-record schema.  
2. Distinguish relevant retrieval conversations from irrelevant Google Photos discussions.  
3. For each relevant record, run AI classification into the schema in Section 10, without inventing missing facts.  
4. Persist original text, URL, and classifications so any insight can be inspected.  
5. Compute overview metrics, failure-stage counts/percentages, clue frequencies, workaround frequencies, and outcome distributions **programmatically** (e.g. Pandas).  
6. Render Dataset Overview, Retrieval Problem Map, Memory Clue Analysis, Evidence Explorer, and Ask the Research.  
7. Support filtering in Evidence Explorer as specified.  
8. For Ask the Research, retrieve supporting records first; synthesise only from those records; cite `record_id`s; refuse to conclude when evidence is thin.  
9. Work correctly on a 10–20 record test file and scale to approximately 200–250 records.  
10. Remain usable as a public Streamlit Community Cloud demo.

---

## 13. Non-Functional Requirements

### Architecture (intentionally simple)

Recommended stack:

- Python
- Streamlit
- Pandas
- Groq API for LLM classification and grounded analysis
- CSV for storage
- Plotly or native Streamlit charts
- Optional lightweight semantic retrieval using embeddings **if needed**

Do **not** introduce unnecessary technologies such as:

- complex databases
- authentication
- microservices
- Docker
- n8n
- Zapier
- large multi-agent architectures

unless absolutely necessary.

### User experience

- Professional, minimal, graduation-project appropriate
- Clear data, readable charts, visible evidence, simple filters, strong information hierarchy
- No excessive animation

### Deployment

The final application must be deployable publicly using **Streamlit Community Cloud**.

### Completeness vs. ambition

The goal is a **functional research MVP** that can be completed quickly and demonstrated publicly—not a production consumer product.

---

## 14. Research Integrity Requirements

The application must clearly distinguish:

| Layer | Meaning |
| --- | --- |
| **Raw evidence** | Original `raw_text`, source, URL, date |
| **AI classification** | Structured labels extracted from that text |
| **Calculated statistics** | Counts and percentages computed from classified rows |
| **AI-generated synthesis** | Narrative answers that may only summarise cited records |

Additional rules:

- The LLM must **not invent information**.
- If something is not explicitly present in the user conversation, return **unknown / unclear** rather than guessing.
- All AI-generated classifications must remain connected to the original `record_id` and source text.
- The system must allow users to **inspect the underlying evidence** behind any insight.
- **Percentages must be calculated programmatically** from the classified dataset, never generated by the LLM.
- All insights should be traceable to supporting records **and their sampling frame**.
- Ask-the-Research answers must cite record IDs, state the sampling frame, and say when there is insufficient evidence.
- Never report a single percentage of “vague-memory retrieval” that mixes `broad` and `targeted_direct` rows.

---

## 15. Non-Goals

This project will **not**:

- Improve Google Photos search as a general-purpose ranking or indexing problem.
- Build a consumer-facing photo finder, conversational assistant, or “progressive memory reconstruction” product as the assumed solution.
- Treat conversational search (or any other intervention) as correct a priori.
- Perform generic sentiment analysis of Google Photos reviews.
- Auto-scrape the live web as a required MVP capability.
- Use private user photo libraries or authenticated Google Photos data.
- Invent statistics, quotes, or failure-mode rankings.
- Combine Corpus A and Corpus B to estimate prevalence of vague-memory retrieval.
- Describe Corpus B as representative of all Google Photos users.
- Choose the final product solution for the Product Manager.
- Add authentication, Docker, microservices, workflow tools, or a complex database unless later shown to be strictly necessary.

---

## 16. Expected Outputs

1. Classified outputs **per sampling frame**, with original text, URL, and metadata preserved. Corpus A file remains unmodified as the broad source. Corpus B is added later as its own CSV.  
2. A working Streamlit research application covering the five core surfaces in Section 11, with the active corpus / `sampling_frame` visible.  
3. Programmatic distributions computed **within one frame at a time**.  
4. An Evidence Explorer that makes every insight inspectable at record level, including source URL.  
5. Grounded, cited answers to researcher questions, or an explicit insufficient-evidence response; Corpus B answers must use the targeted-sample wording.  
6. Evidence the Product Manager can use to identify **which specific part of the vague-photo retrieval journey represents the strongest opportunity**—without the engine naming a product to build.

---

## 17. MVP Definition

**MVP name:** Google Photos Retrieval Discovery Engine

**Success condition:** A Product Manager can load a stated sampling frame, inspect evidence against original text and URLs, and use calculated (not LLM-invented) statistics **within that frame** to reason about retrieval problems. Deep vague-memory analysis uses Corpus B and is worded as targeted-sample findings.

**Included in MVP**

- Python + Streamlit + Pandas + CSV + Groq
- Charts via Plotly or native Streamlit
- Corpus A (~225) as the broad landscape; Corpus B as a separate targeted file when collected; 10–20 row development sample
- Frame-aware relevance filtering and per-record classification per Sections 10–12
- Dataset Overview, Retrieval Problem Map, Memory Clue Analysis, Evidence Explorer, Ask the Research
- Traceability from every insight to `record_id`, `sampling_frame`, `raw_text`, and `url`
- Public deployability on Streamlit Community Cloud

**Explicitly deferred**

- Automatic scraping pipelines
- Heavy infrastructure
- A chosen consumer-product solution
- Any assumption that conversational search is the answer

The engine analyses **why** vaguely remembered photo retrieval fails. It does not ship the fix.
