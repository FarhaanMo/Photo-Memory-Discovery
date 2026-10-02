# Architecture: Google Photos Retrieval Discovery Engine

**Document type:** Technical architecture for a research MVP  
**Build window:** 1–2 days  
**Status:** Design only (no implementation in this document)

This architecture implements the discovery engine defined in `docs/problemStatement.md`. It is a **single Streamlit application** with Python modules, CSV files, Pandas, and Groq. It does **not** select a consumer product solution. It classifies evidence, computes statistics in code, and keeps every insight tied to `record_id` and `sampling_frame`.

---

## 1. Design principles

1. **One process, one UI.** Streamlit runs ingestion, classification, analytics, and Q&A. No API gateway, workers, or extra services.
2. **CSV is the database.** Raw and processed datasets are files. Pandas DataFrames are the in-memory model.
3. **`raw_text` is immutable.** Classification never overwrites original columns. New fields are appended.
4. **LLM proposes labels; Python counts.** Groq must not emit percentages, rankings, or invented quotes.
5. **Skip work already done.** A processed CSV is the cache of LLM classifications. Records with a successful classification are not sent again.
6. **Small corpus retrieval.** Ask-the-Research uses Pandas filters plus lexical overlap **within the active sampling frame**. No vector database for MVP.
7. **Fail closed on evidence.** Missing or unparseable model output becomes `unknown` / `unclear`, not a guess.
8. **Demo without re-classifying.** A committed processed CSV lets the UI and charts load on Streamlit Community Cloud. Groq is required for first-time classification and for Ask-the-Research synthesis.
9. **Two sampling frames stay separate.** Corpus A (`broad`) and Corpus B (`targeted_direct`) are different files. Analytics and Q&A never pool them to estimate prevalence of vague-memory retrieval. Corpus A (`data/google_photos_retrieval_raw.csv`) is never overwritten.

**Out of architecture:** microservices, Docker, Redis, PostgreSQL, authentication, n8n, Zapier, LangGraph-style multi-agent systems, scraping pipelines.

---

## 2. Stack

| Layer | Choice | Role |
| --- | --- | --- |
| UI | Streamlit | Pages/tabs for overview, problem map, clues, explorer, Q&A, and a classify/run control |
| Language | Python 3.11+ | All application logic |
| Tabular data | Pandas + CSV | Ingest, join, filter, persist |
| LLM | Groq API (`groq` SDK) | Relevance, structured extraction, grounded Q&A |
| Secrets | `.env` locally; Streamlit secrets in cloud | `GROQ_API_KEY` only |
| Charts | Plotly Express (preferred) or `st.bar_chart` | Distributions; values always from Pandas |
| Optional (not required) | `python-dotenv` | Local env loading |

No embeddings service is required. If lexical retrieval proves too weak during implementation, a later optional TF-IDF step with scikit-learn is acceptable; it is **not** in the MVP critical path.

---

## 3. Folder structure

```text
Graduation Project/
├── app.py                          # Streamlit entry: layout, tabs, orchestration
├── requirements.txt
├── .env.example                    # GROQ_API_KEY=  (no real key)
├── .gitignore                      # .env, __pycache__, local scratch
├── .streamlit/
│   └── config.toml                 # Theme / wide layout only
├── data/
│   ├── google_photos_retrieval_raw.csv              # Corpus A (broad); never overwrite
│   ├── google_photos_direct_vague_targeted.csv      # Corpus B (targeted); not collected yet
│   ├── google_photos_retrieval_triage_225.csv       # Corpus A triage only
│   ├── google_photos_retrieval_processed.csv        # classifications; must retain sampling_frame
│   ├── raw/
│   └── processed/
├── prompts/
│   ├── relevance.md
│   ├── extract.md
│   └── qa.md
├── src/
│   ├── __init__.py
│   ├── config.py                   # Paths, model name, batch size, allowed enums
│   ├── secrets.py                  # Resolve Groq key (env then st.secrets)
│   ├── schema.py                   # Column lists, enums, JSON schema, validators
│   ├── ingest.py                   # CSV load + schema validation
│   ├── persist.py                  # Merge writes; never mutate raw_text
│   ├── llm_client.py               # Groq wrapper, JSON mode, retries
│   ├── relevance.py                # Relevance prompt + parse
│   ├── extract.py                  # Structured extraction + failure stage (one JSON)
│   ├── pipeline.py                 # Orchestrate classify-only-missing records
│   ├── analytics.py                # Deterministic Pandas aggregations
│   ├── retrieve.py                 # Ask-the-Research candidate selection
│   └── qa.py                       # Grounded synthesis + citation parse
├── docs/
│   ├── problemStatement.md
│   └── architecture.md
└── README.md                       # Run / deploy notes (later; not this task)
```

Keep Streamlit as **one** `app.py` with tabs rather than a `pages/` multi-app unless the file becomes unreadable. Tabs are faster to finish in 1–2 days.

---

## 4. Module responsibilities

| Module | Responsibility | Must not do |
| --- | --- | --- |
| `app.py` | Sidebar (dataset path, classify button, status), five research tabs, display of charts and evidence | Invent numbers; call Groq except via `pipeline` / `qa` |
| `config.py` | Model id, temperature, max tokens, `TOP_K` for Q&A, `MIN_EVIDENCE`, processed path | Hard-code API keys |
| `secrets.py` | `get_groq_api_key()`: `os.environ` / dotenv, else `st.secrets["GROQ_API_KEY"]` | Log the key |
| `schema.py` | Required raw columns; allowed enums; Pydantic or hand-written JSON validation; empty classification defaults | Change `raw_text` |
| `ingest.py` | `read_csv`, check required columns, unique `record_id`, coerce types, drop/flag empty `raw_text` | Scrape the web |
| `persist.py` | Left-join classifications onto a copy of raw rows; atomic write of processed CSV; skip list of already-done ids | Overwrite `raw_text`, `url`, `source`, `date`, `record_id`, or Corpus A |
| `llm_client.py` | Chat completion with JSON object response; timeout; retry on 429/5xx; return raw string + error flag | Compute statistics |
| `relevance.py` | Build relevance prompt; map model output to `is_relevant`, `relevance_reason`, `relevance_confidence` | Extract full research schema |
| `extract.py` | Build extraction prompt for **relevant** rows only; parse full classification JSON including `primary_failure_stage` | Classify irrelevant rows |
| `pipeline.py` | For each row: skip if already classified; call relevance; if relevant, call extract; after each success, persist | Re-send completed rows |
| `analytics.py` | Counts, percentages, clue frequencies from DataFrames **of one sampling_frame only** | Call the LLM; pool `broad` + `targeted_direct` for prevalence |
| `retrieve.py` | Filter relevant rows; score by keywords + optional label filters; return top K rows with `record_id` | Call the LLM |
| `qa.py` | Pack retrieved rows into a prompt; require JSON `{answer, cited_record_ids, insufficient_evidence}`; reject ids not in the pack; name the sampling frame | Use records not retrieved; mix frames as if they were one population |

**LLM call count (intentional):** two Groq calls per *new relevant* record (relevance, then extraction). Irrelevant records: one call. Failure stage lives **inside** the extraction JSON so a third classification pass is unnecessary. `relevance.py` and `extract.py` stay separate modules for prompts and tests; `pipeline.py` is the only orchestrator.

---

## 5. Data flow

```text
data/raw/conversations.csv
        │
        ▼
   ingest.validate()          # required columns, unique ids, non-empty raw_text
        │
        ▼
   persist.load_processed()   # if classified.csv exists, join on record_id
        │
        ▼
   pipeline.run()             # only rows where classification_status != success
        │
        ├─► relevance (Groq) ─► is_relevant
        │         │
        │         ├─ false ─► write classification_status=success, skip extract
        │         └─ true  ─► extract (Groq) ─► structured fields + failure stage
        │
        ▼
   data/processed/classified.csv     # raw columns copied verbatim + AI columns
        │
        ▼
   analytics.compute(df)             # Pandas only
        │
        ├── Dataset Overview
        ├── Retrieval Problem Map      # relevant analysed rows only
        ├── Memory Clue Analysis
        └── Evidence Explorer filters
                │
                ▼
        retrieve.select(question, df)  # lexical + filters, relevant rows
                │
                ▼
        qa.answer(question, rows)      # Groq grounded on those rows only
                │
                ▼
        UI: answer + cited record_ids → expander of raw_text / url
```

**Immutability rule:** `ingest` and `persist` copy `record_id`, `source`, `date`, `url`, `raw_text` from the raw file. Classification writers may only write columns listed in §7. If a raw file is re-ingested, classifications match by `record_id`; `raw_text` in processed output is always taken from **raw**, not from a previous processed copy that might have been edited.

---

## 6. Column contract

### 6.0 Sampling frames (two corpora)

| Corpus | File | `sampling_frame` | Role |
| --- | --- | --- | --- |
| A | `data/google_photos_retrieval_raw.csv` | `broad` | Public retrieval landscape. **Never overwrite.** |
| B | `data/google_photos_direct_vague_targeted.csv` | `targeted_direct` | Targeted qualitative vague-memory sample. **File not collected yet.** |

Load one corpus at a time (or tag every row). Pandas aggregations, charts, and Ask-the-Research must filter to a single `sampling_frame`. Do not concatenate A+B to produce a prevalence of vague-memory retrieval.

Triage of Corpus A lives in `data/google_photos_retrieval_triage_225.csv` and is **not** a substitute for Corpus B.

### 6.1 Raw CSV (required)

| Column | Type | Notes |
| --- | --- | --- |
| `record_id` | string | Unique, stable **within a sampling frame** |
| `source` | string | e.g. reddit, play_store |
| `date` | string | ISO or original; keep as string if messy |
| `url` | string | Public source URL; preserve |
| `raw_text` | string | Never overwritten |
| `sampling_frame` | string | `broad` \| `targeted_direct` (set from which file was loaded if the column is absent) |

### 6.2 Processed CSV (raw columns + these)

Pipeline metadata:

| Column | Meaning |
| --- | --- |
| `classification_status` | `pending` \| `success` \| `error` |
| `classification_error` | Empty or last error message |
| `classified_at` | ISO timestamp when last successful LLM write happened |
| `model_name` | Groq model used |
| `prompt_version` | e.g. `extract_v1` so cache can be invalidated deliberately |
| `sampling_frame` | Copied from source corpus; never inferred from labels |

Relevance:

| Column | Meaning |
| --- | --- |
| `is_relevant` | `true` / `false` / `unclear` |
| `relevance_reason` | Short quote-grounded reason or `unclear` |
| `relevance_confidence` | `high` / `medium` / `low` / `unclear` |

Extraction (relevant rows; others `unknown` / empty):

| Column | Meaning |
| --- | --- |
| `photo_type` | Type of image sought, or `unknown` |
| `remembers_people` | boolean or `unknown` |
| `remembers_time` | boolean or `unknown` |
| `remembers_place` | boolean or `unknown` |
| `remembers_object` | boolean or `unknown` |
| `remembers_text` | boolean or `unknown` |
| `remembers_event` | boolean or `unknown` |
| `remembers_purpose` | boolean or `unknown` |
| `remembers_sequence` | boolean or `unknown` |
| `remembers_association` | boolean or `unknown` |
| `remembers_visual` | boolean or `unknown` |
| `remembered_clues_detail` | Short free text, or `unknown` |
| `forgotten_information` | Short free text, or `unknown` |
| `search_strategy` | What they tried, or `unknown` |
| `primary_failure_stage` | Enum in §6.3 |
| `attempted_refinement` | `yes` / `no` / `unknown` |
| `workaround` | Enum in §6.3 |
| `retrieval_outcome` | Enum in §6.3 |
| `primary_problem_theme` | Short theme label, or `unknown` |
| `evidence_strength` | `strong` / `moderate` / `weak` / `unclear` |
| `extraction_notes` | Optional; must not invent facts |

Boolean clue columns stored as strings `true` / `false` / `unknown` in CSV to avoid NaN ambiguity.

### 6.3 Allowed enums (enforced in `schema.py` after the model returns)

**`primary_failure_stage`**

- `expression_failure`
- `retrieval_interpretation_failure`
- `evaluation_failure`
- `recovery_refinement_failure`
- `other_unclear`

**`workaround`**

- `timeline_scrolling`
- `albums`
- `people_pets`
- `places_maps`
- `another_application`
- `asking_another_person`
- `giving_up`
- `unknown`
- `none_mentioned`

**`retrieval_outcome`**

- `found`
- `not_found`
- `partial`
- `unclear`
- `abandoned`

Unknown/invalid enum values from the model are coerced to `other_unclear` or `unknown`.

### 6.4 Methodology — Corpus B extraction and audit

Corpus B (`sampling_frame = targeted_direct`) is classified in two LLM passes, then gated by deterministic checks. Corpus A is not affected.

1. **Inclusion.** The relevance gate is not run; inclusion was decided at collection time. Rows carry `relevance_level = direct_vague_retrieval` and `relevance_confidence = not_assessed`.
2. **First pass** (`prompts/extract.md`, `retrieval_classify_v4`) produces the structured fields from `raw_text` and `platform`.
3. **Audit pass** (`prompts/audit.md`, `audit_v1`) receives `raw_text`, `platform` and the first-pass JSON, checks every field against `raw_text`, and may correct it. The audited version is the final processed result. It adds `audit_note` (the most important correction, or "no correction required").
4. **Quality gates** (`src/quality_checks.py`, lexical, no LLM): unsupported forgotten-information terms, placeholder search strategies, refinement marked `no` without explicit evidence, duplicated strategy/workaround without sequence evidence, processing errors. Any failure stops further processing.

**Remembered-clue booleans in audited Corpus B output.** `true` means the clue about the target is explicitly evidenced in `raw_text`. `false` means the clue is *not evidenced* in `raw_text`. `false` does **not** mean the user forgot that clue, and false flags must never be counted or described as "forgotten". Only `forgotten_information` records what the user explicitly or strongly indicates they do not remember.

Audited Corpus B adds `failure_stage_reason`, `extraction_warning` and `audit_note` to processed output only; the source Corpus B CSV schema is unchanged. Corpus B findings are qualitative and are never pooled with Corpus A for prevalence.

---

## 7. Structured JSON response schemas

The Groq client should request JSON object output. Prompts instruct: *if not in `raw_text`, use `unknown` / `unclear`; do not invent.*

### 7.1 Relevance response

```json
{
  "record_id": "string",
  "is_relevant": true,
  "relevance_reason": "string",
  "relevance_confidence": "high | medium | low | unclear"
}
```

`is_relevant` is true only when the text is about **finding or retrieving an existing old photo/image**. Backup, sync, storage, subscription, login, crash, edit, upload, and unrelated complaints are false.

### 7.2 Extraction + failure-stage response (relevant records only)

```json
{
  "record_id": "string",
  "photo_type": "string",
  "remembered_clues": {
    "people": "true | false | unknown",
    "time": "true | false | unknown",
    "place": "true | false | unknown",
    "object": "true | false | unknown",
    "text": "true | false | unknown",
    "event": "true | false | unknown",
    "purpose": "true | false | unknown",
    "sequence": "true | false | unknown",
    "association": "true | false | unknown",
    "visual": "true | false | unknown"
  },
  "remembered_clues_detail": "string",
  "forgotten_information": "string",
  "search_strategy": "string",
  "primary_failure_stage": "expression_failure | retrieval_interpretation_failure | evaluation_failure | recovery_refinement_failure | other_unclear",
  "attempted_refinement": "yes | no | unknown",
  "workaround": "timeline_scrolling | albums | people_pets | places_maps | another_application | asking_another_person | giving_up | unknown | none_mentioned",
  "retrieval_outcome": "found | not_found | partial | unclear | abandoned",
  "primary_problem_theme": "string",
  "evidence_strength": "strong | moderate | weak | unclear",
  "extraction_notes": "string"
}
```

The client **echo-checks** `record_id` against the record just sent. Mismatch → treat as `error`, do not write labels.

### 7.3 Ask-the-Research response

```json
{
  "insufficient_evidence": false,
  "answer": "string",
  "cited_record_ids": ["id1", "id2"],
  "notes_on_limits": "string"
}
```

Rules in the prompt and in `qa.py`:

- Use **only** the packed records.
- `cited_record_ids` must be a subset of packed ids; drop any other id.
- If fewer than `MIN_EVIDENCE` (recommend **3**) supporting records, set `insufficient_evidence: true` and refuse a strong conclusion.
- **Do not** output percentages unless they were supplied in a `precomputed_stats` block from Pandas (optional; default is qualitative + counts passed in by Python).
- Do not recommend a product solution.

---

## 8. LLM request flow

### 8.1 Shared client (`llm_client.py`)

1. Resolve API key via `secrets.py`.
2. Call Groq chat completions with:
   - system prompt from `prompts/*.md`
   - user payload: `record_id` + `raw_text` (+ `source` if useful)
   - `temperature` near 0 (e.g. 0.1)
   - JSON response format if the chosen Groq model supports it; otherwise instruct “return JSON only” and parse with a fence stripper
3. Retry: 3 attempts, exponential backoff on 429 and 5xx.
4. On success: parse JSON; validate against `schema.py`.
5. On parse/validation failure: one repair call (“fix this into valid JSON”) then give up → `classification_status=error`.

### 8.2 Classification (batch of new rows)

```text
for record in rows_missing_success:
    rel = relevance.classify(record)
    persist.update(record_id, relevance fields)   # checkpoint
    if rel.is_relevant is not True:
        persist.mark_success(record_id)
        continue
    ext = extract.classify(record)
    persist.update(record_id, extraction fields)
    persist.mark_success(record_id)
```

Checkpoint **per record** so a crash mid-run does not redo completed ids. Streamlit shows a progress bar (`st.progress`) and a count of remaining records.

Do **not** send the full 250-row corpus in one prompt.

### 8.3 Ask-the-Research

```text
question
  → retrieve.select(question, relevant_df) → K rows (default 12, max 20)
  → qa.build_prompt(question, rows as {record_id, source, raw_text, key labels})
  → Groq JSON
  → strip illegal citations
  → UI renders answer + linked evidence
```

Python may attach **precomputed** counts (e.g. failure-stage value_counts) as a small JSON block labelled `CALCULATED_STATS_DO_NOT_RECOMPUTE`. The model may quote those numbers but must not invent new ones.

---

## 9. Ask-the-Research retrieval

**Method (MVP):** lexical + structured filters **within the active sampling frame**. No Pinecone, Chroma, or Groq embedding index required.

1. Restrict to the selected `sampling_frame`, then `is_relevant == true` (or equivalent) and `classification_status == success`.
2. Tokenise the question (lowercase, split, drop stopwords).
3. **Label boosts:** if the question mentions known enums (e.g. “screenshot”, “expression”, “date”), filter or boost rows whose `photo_type` / `primary_failure_stage` / clue flags match.
4. **Score:** count overlapping tokens in `raw_text` + `primary_problem_theme` + `remembered_clues_detail`.
5. Take top **K = 12**. If all scores are 0, return the empty set → `insufficient_evidence`.
6. Pass those rows to Groq. The model never sees the other sampling frame or the rest of the corpus.
7. If the frame is `targeted_direct`, the synthesis prompt requires the phrase “Within the targeted vague-memory retrieval sample”.

This is appropriate for a few hundred short forum posts: the full relevant set still fits in memory; only the prompt is truncated.

---

## 10. Deterministic analytics

`analytics.py` operates only on the processed DataFrame **for one `sampling_frame`**. Captions must name the frame. Corpus B charts use the wording “Within the targeted vague-memory retrieval sample…”.

| Function | Input slice | Output |
| --- | --- | --- |
| `overview_counts` | all rows | total, relevant, irrelevant, unclear, error |
| `source_distribution` | all rows | count by `source` |
| `failure_stage_distribution` | relevant + success | count and **percentage** of that slice |
| `clue_frequencies` | relevant + success | count of `true` per `remembers_*` |
| `forgotten_summary` | relevant + success | value counts / top themes from `forgotten_information` (programmatic; no LLM) |
| `workaround_distribution` | relevant + success | counts |
| `outcome_distribution` | relevant + success | counts |
| `theme_distribution` | relevant + success | counts of `primary_problem_theme` |

Percentages = `100 * n / denominator` in Pandas. Denominator for the problem map is **analysed relevant records**, not the full dump.

Charts in Streamlit consume these Series/DataFrames. The LLM is not in this path.

---

## 11. Streamlit UI architecture

Single `app.py`, wide layout, no animation libraries.

**Sidebar**

- Path or file uploader for raw CSV (optional if `data/raw` exists)
- Status: n total, n classified, n remaining
- Button: “Classify unclassified records”
- Note that charts use processed data only

**Tabs**

1. **Dataset Overview** — metric row + source / outcome / workaround charts  
2. **Retrieval Problem Map** — failure-stage bar (count + %)  
3. **Memory Clue Analysis** — remembered flags vs forgotten text frequencies  
4. **Evidence Explorer** — filters (`source`, `failure stage`, `photo_type`, remembered clue, `outcome`, `theme`); table of `record_id`, source, classifications; expander with **full `raw_text`** and URL  
5. **Ask the Research** — question box, answer, `insufficient_evidence` banner, list of cited `record_id`s each expanding to the same evidence card as the Explorer  

Visual hierarchy: numbers and filters first, narrative last. Distinguish labels in the UI (badge or caption): *Raw evidence* vs *AI classification* vs *Calculated statistic* vs *AI synthesis*.

---

## 12. Evidence citations (`record_id`)

Citations are a **first-class join key**, not decorative footnotes.

1. Every classified row keeps the original `record_id`.
2. Explorer rows are keyed by `record_id`.
3. Q&A JSON must list `cited_record_ids`.
4. `qa.py` intersects that list with the retrieved pack. Drop unknowns.
5. UI looks up each id in the processed DataFrame and shows `raw_text`, `url`, `source`, `date`, and classification fields.
6. Charts do not cite individually; a caption states they are calculated from N analysed records, with a link/instruction to filter the Explorer to the same slice.

If the model quotes text, the UI still shows the full source row so a reviewer can verify.

---

## 13. Caching strategy

| Cache | Mechanism | Invalidate when |
| --- | --- | --- |
| LLM classifications | Processed CSV + `classification_status==success` | Manual “reclassify errors” or `prompt_version` bump |
| Analytics | `@st.cache_data` on `analytics.compute` hashed by processed file mtime or a content hash | Processed CSV changes |
| Raw ingest | `@st.cache_data` on file bytes / path mtime | Raw CSV changes |
| Q&A answers | Optional in-session `st.session_state` dict keyed by question string | New question or dataset change; **do not** persist Q&A to CSV (synthesis is not evidence) |
| Groq HTTP | None beyond processed CSV | — |

**Skip rule (critical):** `pipeline.py` selects `classification_status != success` **or** missing classification columns. Successful rows are never sent again in a normal run.

**Reprocess path (explicit only):** sidebar checkbox “Reclassify rows with status=error” and, separately, “Force reclassify all” (dangerous; off by default). Force reclassify still **does not** overwrite `raw_text`; it only replaces AI columns.

---

## 14. API-key handling

1. **Local:** `GROQ_API_KEY` in `.env`, loaded by `python-dotenv` if present, else already in the process environment. `.env` is gitignored. `.env.example` documents the variable name only.
2. **Streamlit Community Cloud:** `Settings → Secrets`:

   ```toml
   GROQ_API_KEY = "..."
   ```

3. **Resolution order:** `os.environ["GROQ_API_KEY"]` first, then `st.secrets["GROQ_API_KEY"]`.
4. **UI:** if classification or Q&A is requested and the key is missing, show a clear error; still allow browsing a precomputed processed CSV.
5. Never print, chart, or write the key into CSV.

---

## 15. Error handling

| Failure | Behaviour |
| --- | --- |
| Raw CSV missing required columns | Stop ingest; Streamlit error listing missing names |
| Duplicate `record_id` | Fail ingest (do not silently drop) |
| Empty `raw_text` | Row stays `pending`/`error`; not sent to Groq |
| Missing API key | Classify/Q&A disabled; rest of app works on processed data |
| Groq 429 / 5xx | Retry 3×; then `classification_status=error`, continue next row |
| Invalid JSON / schema | One repair call; then error status |
| `record_id` mismatch in JSON | Discard payload; error status |
| Partial run | Processed CSV already contains successes; rerun continues remainder |
| Q&A with zero retrieved rows | No Groq call; `insufficient_evidence` |
| Model cites foreign ids | Strip them; if none remain, insufficient evidence |
| Plotly empty slice | Show “No analysed relevant records yet” |

User-visible errors are short. Technical detail can sit in `classification_error` for the Explorer.

---

## 16. How processed classifications avoid repeat LLM calls

1. After each successful relevance (and extraction if needed), `persist.py` writes the **full** processed DataFrame to `data/processed/classified.csv`.
2. On startup, the app loads processed CSV and builds a set of `record_id`s with `classification_status == success`.
3. The pipeline iterator is `raw_ids - success_ids` (plus optional error retry).
4. `raw_text` in the written file is always the raw copy; AI columns are additive.
5. Prompt/model changes use `prompt_version` / `model_name`. A version bump does **not** auto-invalidate; the researcher must force reclassify so accidental spend does not happen.

For the public demo, commit a processed CSV of the research set so Cloud startup does not classify 250 records live.

---

## 17. Deployment architecture

```text
Developer laptop                         Streamlit Community Cloud
─────────────────                        ─────────────────────────
.gitignored .env  ── GROQ_API_KEY        Secrets: GROQ_API_KEY
data/raw/*.csv    ── optional commit     same repo
data/processed/classified.csv  ────────► cloned; app reads on boot
app.py + src/ + prompts/       ────────► main file: app.py
```

- **Host:** Streamlit Community Cloud, `app.py` as the main file.
- **Python packages:** `requirements.txt` (streamlit, pandas, groq, plotly, python-dotenv).
- **No** Docker, no reverse proxy, no auth wall.
- **Runtime:** one container/process provided by Streamlit; file writes to processed CSV on Cloud are **ephemeral**. Therefore:
  - Treat Cloud as **read-mostly**: ship classified data in git.
  - Optional: allow a visitor to upload a small CSV and classify in-session into `st.session_state` without expecting disk to survive restart.
- **Local demo:** `streamlit run app.py` with `.env` and writable `data/processed/`.

---

## 18. Build sequence (1–2 days)

**Day 1**

1. Folder skeleton, `schema.py`, `ingest.py`, `persist.py`, sample raw CSV (10–20 rows).  
2. `secrets.py`, `llm_client.py`, `relevance.py`, `extract.py`, `pipeline.py` on the sample.  
3. Confirm `raw_text` unchanged and reruns skip successes.

**Day 2**

4. `analytics.py` + Streamlit tabs 1–4 with Plotly.  
5. Evidence Explorer filters.  
6. `retrieve.py` + `qa.py` + Ask-the-Research tab with citations.  
7. Error/empty states; `requirements.txt`; verify app opens against processed CSV without a key.

---

## 19. Non-goals (architecture)

- Scraping Reddit/Play Store from the app  
- User login  
- Storing photos or Google account data  
- Multi-agent debate over labels  
- Letting Groq compute dashboard percentages  
- Pooling Corpus A and Corpus B for prevalence of vague-memory retrieval  
- Choosing a product solution in the Q&A prompt  

---

## 20. Traceability checklist

Every path a PM can see must satisfy:

| Surface | Evidence path |
| --- | --- |
| Overview metrics | Pandas on processed CSV |
| Problem map % | Pandas on relevant analysed rows |
| Clue bars | Pandas on `remembers_*` |
| Explorer card | `record_id` → `raw_text` + URL + labels |
| Q&A sentence | `cited_record_ids` ⊆ retrieved pack ⊆ processed CSV **of one `sampling_frame`** |

If a number or claim cannot be followed to rows, it does not ship.
