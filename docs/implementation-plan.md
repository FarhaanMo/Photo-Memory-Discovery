# Implementation Plan: Google Photos Retrieval Discovery Engine

**Source of truth:** `docs/problemStatement.md`, `docs/architecture.md`  
**Constraint:** Implement **one phase at a time**. Each phase is small enough for Cursor to complete independently.  
**This document does not implement code.**

Phases are numbered **Phase 0 through Phase 6** (seven phases). Do not skip ahead. Do not add Docker, databases, auth, scraping, embeddings indexes, or a consumer-product solution.

---

## Cross-phase invariants

Every phase must preserve these rules:

1. Never overwrite `raw_text`, `record_id`, `source`, `date`, or `url`.
2. Never invent statistics in the LLM. Counts and percentages come from Pandas **within one `sampling_frame`**.
3. Missing evidence → `unknown` / `unclear`, not a guess.
4. Insights stay joinable on `record_id` and tagged with `sampling_frame` (`broad` or `targeted_direct`).
5. Successful classifications are not resent to Groq on a normal run.
6. Single Streamlit app (`app.py` + `src/`). No microservices.
7. Never overwrite Corpus A (`data/google_photos_retrieval_raw.csv`).
8. Never pool Corpus A and Corpus B to estimate prevalence of vague-memory retrieval.
9. Corpus B findings use the wording “Within the targeted vague-memory retrieval sample…”.
10. Do not describe Corpus B as representative of all Google Photos users.
11. Do not run additional LLM classification until a later task requests it (Corpus B is not collected yet).

**Recommended Groq model (Phase 2+):** set in `src/config.py` (e.g. a current Groq JSON-capable chat model). Change only in config, not scattered through prompts.

---

## Phase 0 — Project setup and Streamlit skeleton

### Objective

Create a runnable empty app with the agreed folder layout, dependencies, secret placeholders, and a professional but unfinished UI shell.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Create | `requirements.txt` |
| Create | `.env.example` |
| Create | `.gitignore` (if missing: include `.env`, `__pycache__/`, `.venv/`, `*.pyc`) |
| Create | `.streamlit/config.toml` |
| Create | `src/__init__.py` |
| Create | `src/config.py` |
| Create | `src/secrets.py` |
| Create | `app.py` |
| Create | `data/raw/.gitkeep` |
| Create | `data/processed/.gitkeep` |
| Create | `prompts/.gitkeep` |
| Modify | none of the research docs |

Do **not** create ingest/LLM/analytics modules in this phase.

### Functionality

- Pin dependencies: `streamlit`, `pandas`, `groq`, `plotly`, `python-dotenv`.
- `src/config.py`: paths to `data/raw` and `data/processed`, model name placeholder, `TOP_K=12`, `MIN_EVIDENCE=3`, `PROMPT_VERSION`, temperature `0.1`.
- `src/secrets.py`: `get_groq_api_key()` reads `os.environ` then `st.secrets`; never prints the key. Missing key returns `None`.
- `app.py`: page title **Google Photos Retrieval Discovery Engine**; wide layout; sidebar with app name and “Phase 0 skeleton”; five empty tabs matching the product: Dataset Overview, Retrieval Problem Map, Memory Clue Analysis, Evidence Explorer, Ask the Research; short caption that this is a PM research engine, not sentiment analysis.
- `.streamlit/config.toml`: wide layout / light professional theme only. No animation libraries.
- `.env.example`: `GROQ_API_KEY=` only.

### Acceptance criteria

- `streamlit run app.py` starts without import errors.
- All five tabs exist and show a placeholder message.
- `.env` is gitignored; `.env.example` has no real key.
- `get_groq_api_key()` does not crash when the key is absent.
- No Groq network calls.

### Manual test steps

1. Create a venv, `pip install -r requirements.txt`.
2. Run `streamlit run app.py`.
3. Confirm title, five tabs, sidebar.
4. Confirm the app loads with no `.env` file.
5. Confirm `.gitignore` lists `.env`.

### Dependencies on earlier phases

None.

---

## Phase 1 — CSV ingestion, validation, sample data, raw preview

### Objective

Load and validate a raw conversations CSV, reject bad files clearly, and preview original records in Streamlit. Include a **10–20 row** sample dataset so later phases can run without loading a full corpus. Corpus A (`google_photos_retrieval_raw.csv`, `sampling_frame=broad`) is the default production landscape file and must not be overwritten. Corpus B (`google_photos_direct_vague_targeted.csv`, `sampling_frame=targeted_direct`) is specified but **not collected yet**.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Create | `src/schema.py` |
| Create | `src/ingest.py` |
| Create | `data/raw/conversations_sample.csv` |
| Modify | `app.py` (sidebar file source + Overview raw preview) |
| Modify | `src/config.py` only if default raw path must point at the sample file |

Do **not** call Groq. Do **not** write `data/processed/classified.csv` yet.

### Functionality

- Required raw columns: `record_id`, `source`, `date`, `url`, `raw_text`.
- `ingest.load_raw_csv(path_or_buffer)` → DataFrame or a structured error (`missing_columns`, `duplicate_record_id`, `empty_file`).
- Duplicate `record_id` **fails** ingest (no silent drop).
- Empty `raw_text` rows are flagged (e.g. `raw_text_empty` boolean) but the file can still load; they must not be treated as classifiable later.
- Coerce all required columns to string; do not mutate text content.
- Sample CSV: **12–20 rows**, mixed:
  - at least 3 genuine “find an old photo / screenshot / vague memory” texts
  - at least 3 irrelevant (storage, backup, sync, crash, subscription)
  - multiple `source` values (e.g. `reddit`, `play_store`, `community`)
  - unique `record_id`s (`r001` …)
  - fictional but realistic public-style text; placeholder URLs allowed
- Streamlit: choose default sample path **or** upload CSV; on success show row count, column list, and a dataframe preview of the five raw columns; on failure show the validation message.

### Acceptance criteria

- Sample file loads and preview shows original `raw_text`.
- A CSV missing `url` is rejected with a named missing-column error.
- Duplicate ids are rejected.
- Upload of a valid extra CSV works in the same session.
- No processed/AI columns are required for preview.

### Manual test steps

1. Launch app, leave default sample, confirm preview of 12–20 rows.
2. Open `conversations_sample.csv` and confirm `raw_text` in the UI matches the file.
3. Upload a copy with `url` removed → error, no crash.
4. Upload a copy with two identical `record_id`s → error.
5. Confirm irrelevant and retrieval-like rows both appear (relevance is **not** classified yet).

### Dependencies on earlier phases

Requires **Phase 0** (`app.py`, `src/config.py`).

---

## Phase 2 — Groq integration, relevance, structured retrieval analysis

### Objective

Add Groq JSON classification for **one record at a time**: relevance first; if relevant, structured extraction including **primary failure stage** in the same extraction JSON. Wire a minimal “classify selected row” control so the pipeline can be proven before batch persistence.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Create | `src/llm_client.py` |
| Create | `src/relevance.py` |
| Create | `src/extract.py` |
| Create | `prompts/relevance.md` |
| Create | `prompts/extract.md` |
| Modify | `src/schema.py` (JSON validation, enums, defaults) |
| Modify | `src/secrets.py` if dotenv load-on-import was not done in Phase 0 |
| Modify | `app.py` (dev panel: pick one `record_id`, classify, show JSON/fields) |

Do **not** implement full-dataset batch loops, processed CSV writes, or analytics dashboards in this phase (those are Phase 3). Optional in-memory display of the last result is enough.

### Functionality

- `llm_client.complete_json(system, user, **kwargs)`: Groq chat, low temperature, JSON object if supported, 3 retries on 429/5xx, strip fences, return parsed dict or error.
- Prompts: do not invent; use `unknown`/`unclear`; this is retrieval-failure research, not sentiment; do not propose a product solution.
- Relevance JSON: `record_id`, `is_relevant`, `relevance_reason`, `relevance_confidence`.
- Extraction JSON: photo type, remembered clue flags, forgotten information, search strategy, `primary_failure_stage`, refinement, workaround, outcome, theme, evidence strength (exact keys in architecture §7.2).
- `schema.py` coerces illegal enums (`primary_failure_stage`, `workaround`, `retrieval_outcome`).
- Echo-check `record_id`; mismatch → error, do not keep labels.
- Irrelevant records: **skip extraction**.
- Empty `raw_text`: do not call Groq.
- UI: dropdown of sample `record_id`s; button “Classify this record”; show raw text + resulting fields; if no API key, disable button with a clear message.

### Acceptance criteria

- With a valid key, a retrieval-like sample row gets `is_relevant=true` and extraction fields (or explicit `unknown`s).
- A storage/backup sample row gets `is_relevant=false` and **no** invented extraction story (extraction not called, or fields left default/unknown).
- Invalid JSON from the model does not crash Streamlit.
- `raw_text` in the preview is unchanged after classify.
- No write to `classified.csv` required yet.

### Manual test steps

1. Put `GROQ_API_KEY` in local `.env`. Restart app.
2. Classify a “can’t find that café photo” sample id. Inspect JSON.
3. Classify a “storage full” sample id. Confirm not relevant; extraction skipped.
4. Temporarily break the key / remove `.env` and confirm the button is disabled with a message.
5. Confirm the five research tabs still exist (placeholders OK).

### Dependencies on earlier phases

Requires **Phase 0** and **Phase 1** (sample CSV + ingest).

---

## Phase 3 — Batch processing, processed CSV, deterministic analytics

### Objective

Run classification over unclassified rows, persist additive columns to `data/processed/classified.csv` after **each** record, skip successes on rerun, and compute dashboard statistics **only in Pandas**. Show Overview, Problem Map, and Memory Clue Analysis from those numbers.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Create | `src/persist.py` |
| Create | `src/pipeline.py` |
| Create | `src/analytics.py` |
| Modify | `app.py` (sidebar classify-all + progress; fill Overview, Problem Map, Clue tabs) |
| Modify | `src/schema.py` if processed column list helpers are still incomplete |
| Create (optional, empty OK) | `data/processed/classified.csv` after first successful local run; do not hand-invent labels |

Do **not** build Evidence Explorer filters (Phase 4) or Ask-the-Research (Phase 5).

### Functionality

- `persist.load_processed()` / `save_processed()`: join on `record_id`; copy raw columns from **raw** every save; write only architecture AI/metadata columns besides raw.
- `classification_status`: `pending` \| `success` \| `error`; store `classification_error`, `classified_at`, `model_name`, `prompt_version`.
- `pipeline.run(raw_df, processed_df, progress_cb)`: iterate rows where status ≠ `success`; relevance → maybe extract; checkpoint CSV per record.
- Skip empty `raw_text` with `error` or leave pending per architecture (empty text is not sent).
- Sidebar: remaining count; “Classify unclassified records”; `st.progress`; checkbox “Retry errors” (off by default). **Force reclassify all** may exist but **off by default**.
- `analytics.py` (no LLM):
  - total / relevant / irrelevant / unclear / error
  - source distribution
  - failure-stage counts and **percentages of analysed relevant rows**
  - `remembers_*` frequencies
  - workaround and outcome distributions
- Charts: Plotly or Streamlit native, fed only by `analytics` return values.
- Captions: “Calculated from N analysed records” vs “AI classification”.
- App must still open and chart a processed file **without** calling Groq.

### Acceptance criteria

- First full run on the sample writes `classified.csv` with unmodified `raw_text`.
- Second run with the same file makes **zero** Groq calls for `success` rows (watch progress: remaining starts at 0).
- Interrupting mid-run leaves successes on disk; resume continues the rest.
- Overview numbers match a manual Pandas count of the processed file.
- Problem map % uses relevant analysed rows as denominator, not the full dump.
- Irrelevant rows are counted in overview but excluded from the problem map slice.
- LLM is never asked for percentages.

### Manual test steps

1. Delete processed CSV if present. Classify unclassified on the sample (needs API key).
2. Open `classified.csv` and diff `raw_text` against the raw sample — must match.
3. Restart app, click classify again — remaining = 0, no new spend.
4. On Overview, add relevant + irrelevant (+ unclear/error) and match total rows.
5. On Problem Map, confirm percentages sum to 100% of the relevant-analysed slice (or documented exclusion of `other_unclear` if you split display — prefer showing all stages including `other_unclear`).
6. Launch with API key removed: Overview/Map/Clues still render from processed CSV.

### Dependencies on earlier phases

Requires **Phases 0–2**.

---

## Phase 4 — Evidence Explorer

### Objective

Let a Product Manager filter classified records and inspect **one record**: original text, URL, and AI labels, with clear separation of raw evidence vs classification.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Modify | `app.py` (Evidence Explorer tab only, plus a small shared evidence-card helper if useful) |
| Create | `src/explorer.py` **or** keep filter logic inside `app.py` if it stays short; prefer `src/explorer.py` with `filter_records(df, filters) -> DataFrame` |

Do **not** implement Ask-the-Research. Do not recompute analytics in the LLM.

### Functionality

- Filters (multi-select / selectbox, with “All”):
  - `source`
  - `primary_failure_stage`
  - `photo_type`
  - remembered clue (`remembers_*` == `true`)
  - `retrieval_outcome`
  - `primary_problem_theme`
- Results table: `record_id`, `source`, `is_relevant`, `primary_failure_stage`, `photo_type`, `retrieval_outcome`.
- Selecting a row (or expander per row) shows: `record_id`, `source`, `date`, clickable `url`, full `raw_text`, all classification fields, `evidence_strength`, `classification_status` / error.
- Labels: “Raw evidence” vs “AI classification”.
- Empty filter result: explicit “No records match”.
- Irrelevant records remain filterable (e.g. `is_relevant`) so dataset quality is inspectable; default view may start at relevant-only with a checkbox **Show irrelevant**.

### Acceptance criteria

- Filtering by `expression_failure` shows only that stage.
- Opening a row shows the same `raw_text` as the raw CSV for that `record_id`.
- URL is visible.
- Charts are not replaced; Explorer is its own tab.
- No Groq calls when browsing Explorer.

### Manual test steps

1. With processed sample loaded, open Evidence Explorer.
2. Filter failure stage to one value; count rows vs Problem Map count for that stage.
3. Filter remembered clue “time”; spot-check that `remembers_time` is `true`.
4. Expand a record; compare `raw_text` to `data/raw/conversations_sample.csv`.
5. Enable show-irrelevant; find a `is_relevant=false` row; confirm extraction is empty/unknown.
6. Confirm Network/Groq is not needed (key can be absent).

### Dependencies on earlier phases

Requires **Phase 3** processed DataFrame in session (or loaded classified CSV). Phases 0–2 for app/ingest/classify.

---

## Phase 5 — Grounded Ask-the-Research

### Objective

Answer researcher questions **only** from retrieved dataset rows. Cite `record_id`s. Refuse when evidence is thin. Never let the model invent statistics or a product solution.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Create | `src/retrieve.py` |
| Create | `src/qa.py` |
| Create | `prompts/qa.md` |
| Modify | `app.py` (Ask the Research tab) |
| Modify | `src/config.py` if `TOP_K` / `MIN_EVIDENCE` not already used |

Do **not** add a vector database. Do not polish global navigation/deployment (Phase 6) beyond making this tab usable.

### Functionality

- `retrieve.select(question, df)`:
  - relevant + `classification_status==success` only
  - tokenize question; lexical overlap on `raw_text` and theme/clue detail
  - boost/filter on known enums (`screenshot`, failure-stage words, etc.)
  - return top `TOP_K` (12, max 20) with scores
  - all scores 0 → empty list, **no Groq call**
- `qa.answer(question, rows, optional_stats)`:
  - pack `{record_id, source, raw_text, key labels}`
  - optional `CALCULATED_STATS_DO_NOT_RECOMPUTE` from `analytics` (counts only)
  - Groq JSON: `insufficient_evidence`, `answer`, `cited_record_ids`, `notes_on_limits`
  - drop cited ids not in the packed set
  - if remaining citations &lt; `MIN_EVIDENCE` (3), force insufficient evidence / weak conclusion
- Prompt: no product recommendation; no new percentages; say when evidence is insufficient.
- UI: text box; examples as captions (“What do users remember when they cannot remember the date?”); Run; banner if insufficient; answer text; each cited `record_id` expands to the **same evidence card** as Explorer (`raw_text`, url, labels).
- Persist Q&A only in `st.session_state`, not CSV.

### Acceptance criteria

- Answer cites only ids that exist in the retrieved pack and processed CSV.
- Clicking a citation shows that row’s original text.
- Empty retrieval or &lt;3 valid citations → insufficient-evidence state, no confident narrative.
- Model-invented extra ids are stripped.
- Asking for “which product should we build?” yields a refusal to choose a solution (prompt + post-check if cheap: still OK to only prompt).
- Percentages in the answer, if any, match optional injected analytics — not new LLM math.

### Manual test steps

1. Ask: “Which retrieval problems occur most often with screenshots?” Inspect citations.
2. Open each citation; confirm texts mention screenshots or were retrieved by photo_type.
3. Ask a nonsense question unrelated to the corpus → insufficient evidence, no fake records.
4. Ask: “Compare expression failure and recovery failure.” Confirm cited ids and that any counts match the Problem Map if stats were injected.
5. Disable API key → classify-all still skipped; Ask shows missing-key error; Explorer still works.
6. Confirm processed CSV unchanged after Q&A.

### Dependencies on earlier phases

Requires **Phases 0–4** (classified data + evidence card pattern). Needs Groq key for synthesis only.

---

## Phase 6 — Polished UI, error handling, deployment readiness

### Objective

Make the app demonstration-ready: consistent navigation, empty/error states, research-integrity labelling, README/run notes, and Streamlit Community Cloud configuration. Prefer shipping a processed sample CSV so Cloud can render charts without classifying on boot.

### Exact files to create or modify

| Action | Path |
| --- | --- |
| Modify | `app.py` (layout, captions, empty states, classify/Q&A guards) |
| Modify | `.streamlit/config.toml` (final theme) |
| Create | `README.md` (local run, secrets, Cloud deploy, what the app is / is not) |
| Modify | `.gitignore` if processed scratch files should stay local |
| Create or commit | `data/processed/classified_sample.csv` **from a real pipeline run on the sample** (not hand-labelled fiction that contradicts `raw_text`) |
| Modify | `src/pipeline.py` / `persist.py` only for Cloud-safe behaviour: if disk is not writable, keep results in `st.session_state` and say so |
| Modify | `requirements.txt` versions if needed for Cloud |

Do **not** add auth, Docker, or new product features.

### Functionality

- Sidebar information hierarchy: dataset status (total / classified / remaining), key present/absent, classify controls, then tabs for research.
- Empty states: no processed data; no filter matches; Q&A insufficient evidence; Groq missing.
- Mid-pipeline errors stay per-row (`classification_status=error`) and are visible in Explorer.
- UI copy: distinguish raw evidence, AI classification, calculated statistics, AI synthesis.
- No excessive animation; readable charts; graduation-project professional tone.
- README: `pip install`, `streamlit run app.py`, `.env`, Cloud main file `app.py`, `[secrets] GROQ_API_KEY`, note that Cloud disk is ephemeral so **commit processed sample** for demo charts; Groq still needed to classify new uploads and for Ask-the-Research.
- Optional file uploader remains; session classification must not assume Cloud disk survives restart.
- `Force reclassify all` remains off by default and warns about API cost.

### Acceptance criteria

- New user can follow README and see Overview charts from committed processed sample **without** a Groq key.
- With a key, Ask-the-Research and classify-unclassified still work locally.
- No uncaught exceptions on: missing key, empty upload, zero relevant rows, filter-all-empty.
- `raw_text` still immutable after a full demo path.
- Docs still do not claim a chosen consumer solution.
- App is suitable as Streamlit Community Cloud main file (`app.py`).

### Manual test steps

1. Fresh clone simulation: no `.env`; run app; confirm overview from processed sample; Ask explains missing key.
2. Add `.env`; classify should show 0 remaining if sample already processed; Ask one question with citations.
3. Evidence Explorer → open a citation from Q&A → same `record_id` text.
4. Upload a 1-row invalid CSV → ingest error, app remains usable.
5. Read README; confirm Cloud secrets snippet matches `src/secrets.py`.
6. Visual pass: all five tabs, sidebar status, no broken layout at desktop width.

### Dependencies on earlier phases

Requires **Phases 0–5** complete.

---

## Phase independence rules (for Cursor)

When implementing **Phase N**:

1. Read this section and the listed files for Phase N only, plus invariants.
2. Do not implement file lists from later phases.
3. Placeholder UI from earlier phases may remain until the phase that owns that tab.
4. If a file is listed as “modify”, keep existing behaviour unless the phase explicitly replaces it.
5. Stop when that phase’s acceptance criteria pass. Do not start the next phase in the same change set unless asked.

---

## Suggested verification dataset sizes

| Stage | Rows |
| --- | --- |
| Phases 1–6 daily dev | development sample (12–20) |
| Broad landscape (Corpus A) | `data/google_photos_retrieval_raw.csv` (~225), `sampling_frame=broad` |
| Targeted vague-memory (Corpus B) | `data/google_photos_direct_vague_targeted.csv` when collected; `sampling_frame=targeted_direct` |
| Cloud demo | processed file(s) labelled by sampling frame |

Do **not** concatenate A and B for a single prevalence statistic.

---

## Out of scope for all phases

- Web scraping
- Conversational photo search as a product
- Sentiment-only analysis
- Invented statistics
- PostgreSQL, Redis, Docker, n8n, multi-agent graphs
- Overwriting original user text
- Overwriting Corpus A
- Combining sampling frames to estimate how common vague-memory retrieval is
