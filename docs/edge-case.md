# Edge Cases: Google Photos Retrieval Discovery Engine

**Source of truth:** `docs/problemStatement.md`, `docs/architecture.md`  
**Purpose:** Corner cases the MVP must handle without inventing evidence, crashing, or silently corrupting `raw_text`.  
**This document does not implement code.**

Expected behaviour below matches the architecture: fail ingest on schema/id problems; skip Groq on empty text; coerce unknown labels; compute percentages in Pandas **within one sampling frame**; refuse weak Q&A conclusions; keep browsing usable without an API key.

---

## How to use this list

- Treat each case as a test or review checklist item when implementing Phases 1–6.
- **Scenario** is what happens. **Expected behaviour** is what the user should see. **Mitigation** is the design that produces that behaviour.
- Prefer `unknown` / `unclear` / `insufficient_evidence` over guessing.

---

## 1. Data

### D-01 Missing columns

- **Scenario:** Uploaded or default CSV lacks one or more required fields (`record_id`, `source`, `date`, `url`, `raw_text`). Extra unknown columns may also be present.
- **Expected behaviour:** Ingest stops. Streamlit shows a short error listing **which** required names are missing. No classification starts. Extra columns are ignored (not treated as `raw_text`).
- **Mitigation:** `ingest.py` checks an allowlist of required columns before any Groq call. Do not infer `raw_text` from a review-body column with another name.

### D-02 Blank `raw_text`

- **Scenario:** A row has a valid `record_id` but `raw_text` is empty, whitespace-only, or NaN.
- **Expected behaviour:** File can still load if other rows are valid. That row is **not** sent to Groq. Status is `error` or remains non-success with a clear `classification_error` (e.g. empty raw text). Explorer can still show the id and empty evidence. Analytics do not treat it as a relevant retrieval case.
- **Mitigation:** Flag empty text at ingest; pipeline skip list; never invent a conversation to classify.

### D-03 Duplicate records

- **Scenario:** Two or more rows share the same `record_id`, or two rows have different ids but identical `raw_text`+`url`.
- **Expected behaviour:** Duplicate **`record_id` fails ingest** (no silent drop, no last-row-wins). Identical text with different ids is allowed (real people repeat themselves); they remain two evidence rows. The UI does not merge them.
- **Mitigation:** Uniqueness check on `record_id` only. Optional later warning count of duplicate texts is analytics-only, not a load failure.

### D-04 Malformed URLs

- **Scenario:** `url` is blank, `"n/a"`, missing scheme, or not a URI (e.g. `"reddit thread"`).
- **Expected behaviour:** Ingest **succeeds** if other required columns exist. Classification may proceed. Explorer shows the string as text; do not crash on `st.link` — render as plain text if it is not a usable http(s) URL. Never fetch the URL.
- **Mitigation:** Store `url` as string. Linkify only values that parse as `http://` or `https://`. Blank URL → “No source URL”.

### D-05 Unknown dates

- **Scenario:** `date` is empty, a relative phrase (“last year”), a locale format, or unparseable.
- **Expected behaviour:** Ingest succeeds. Date is kept as the original string. No timezone conversion. Charts and filters do not require a parsed datetime for MVP. Sorting by date may be lexical and labelled as such, or omitted.
- **Mitigation:** Do not drop rows for bad dates. Do not ask the LLM to “fix” the date. Do not invent ISO timestamps.

### D-06 Unexpected source values

- **Scenario:** `source` is `TikTok`, `Discord`, mixed case (`Reddit` vs `reddit`), or blank.
- **Expected behaviour:** Row is accepted. Overview source chart includes the raw (or lightly normalised) label. Filters list actual values present. Blank source displays as `unknown` **in the UI only**; the stored cell stays as ingested unless it was actually empty, in which case store `unknown` as a display fill without inventing a community name.
- **Mitigation:** Do not restrict ingest to a closed source enum. Optional lowercase for grouping must not overwrite the original column; use a derived field if grouping is needed.

### D-07 Very long comments

- **Scenario:** `raw_text` is tens of thousands of characters (pasted thread, quoted replies).
- **Expected behaviour:** Full text is stored and shown in Explorer (scroll). Groq payload is truncated **for the model only** (head + tail or a documented character cap) with `extraction_notes` or pipeline metadata that truncation occurred. `raw_text` on disk is never truncated. Evidence card still shows the complete original.
- **Mitigation:** Config `MAX_CHARS_TO_LLM`. Truncation flag on the processed row. Citations still point at the full local text.

### D-08 Non-English text

- **Scenario:** Hindi, Arabic, mixed code-switching, or a translation plus original.
- **Expected behaviour:** Ingest and persist unchanged. Classification still runs. If the model cannot read the text, fields become `unknown` / `other_unclear`, not English paraphrases invented as facts. Do not drop non-English rows from the dataset. Analytics include them in totals; Q&A may cite them if retrieved.
- **Mitigation:** Prompts: classify from the given text; do not translate into fake English evidence. UI does not assume Latin-only wrapping.

### D-09 Fewer than expected records

- **Scenario:** File has 3 rows, or 10–20 sample rows, or Corpus B is still empty, instead of a large landscape dump.
- **Expected behaviour:** App runs. Overview shows the true **N** and the **sampling_frame**. Banners warn that statistics are fragile (see A-02). Ask-the-Research often returns `insufficient_evidence`. Charts still use Pandas on whatever exists. No padding with synthetic rows. Do not copy Corpus A rows into Corpus B to “fill” the targeted sample.
- **Mitigation:** Display N and `sampling_frame` on every analytics view. `MIN_EVIDENCE` for Q&A stays (default 3). Never upsample. Never treat Corpus A’s 4 triage hits as a completed Corpus B.

### D-10 Encoding and delimiter issues

- **Scenario:** UTF-8 BOM, Windows-1252, semicolon-delimited “CSV”, or a single-column paste.
- **Expected behaviour:** Prefer UTF-8. If parse yields one column or garbage headers, ingest fails with “could not read a valid CSV with required columns”. No partial classify.
- **Mitigation:** Pandas read with explicit encoding fallback only if it still yields required columns; otherwise fail closed.

### D-11 Whitespace-only or header-only file

- **Scenario:** Empty file or headers with zero data rows.
- **Expected behaviour:** Ingest error: empty dataset. UI empty state, not a blank Plotly exception.
- **Mitigation:** Check `len(df)==0` after a successful header parse.

### D-12 Mixing sampling frames

- **Scenario:** Researcher concatenates Corpus A (`broad`) and Corpus B (`targeted_direct`) and asks “what % of users have vague-memory retrieval?”
- **Expected behaviour:** Analytics and Ask-the-Research **refuse** a pooled prevalence. Charts are labelled with one `sampling_frame`. Corpus B copy uses “Within the targeted vague-memory retrieval sample…”.
- **Mitigation:** Require `sampling_frame` on load; filter analytics; Q&A prompt names the frame. Never treat targeted collection as a random sample of Google Photos users.

### D-13 Corpus B missing

- **Scenario:** `data/google_photos_direct_vague_targeted.csv` does not exist yet.
- **Expected behaviour:** App still loads Corpus A. Selecting the targeted corpus shows a clear empty/not-found state. Do not generate Corpus B with the LLM. Do not copy the four Corpus A triage hits into Corpus B automatically.
- **Mitigation:** Documented two-corpus design. Targeted file is collected later. No extra LLM classification until requested.

### D-14 Overwriting Corpus A

- **Scenario:** Classification or triage write path points at `google_photos_retrieval_raw.csv`.
- **Expected behaviour:** Treated as a **defect**. Writes go only to processed/triage/targeted output files. Corpus A size and `raw_text` stay unchanged.
- **Mitigation:** Separate paths in config; persist never uses the Corpus A path as an output.

---

## 2. AI classification

### C-01 Invalid JSON from the LLM

- **Scenario:** Model returns markdown fences, trailing commas, or prose instead of JSON.
- **Expected behaviour:** Client strips fences, parses; on failure, **one** repair call. If still invalid: `classification_status=error`, message stored, pipeline continues with the **next** row. UI does not crash. Row is retryable via “Retry errors”.
- **Mitigation:** JSON mode when available; repair prompt; never write half-parsed labels as success.

### C-02 Missing classification fields

- **Scenario:** JSON is valid but omits `primary_failure_stage` or clue flags.
- **Expected behaviour:** Fill missing keys with `unknown` / `other_unclear` per schema defaults **only if** the object is otherwise usable and `record_id` matches. If relevance JSON lacks `is_relevant`, treat as error, not “assume relevant”.
- **Mitigation:** Schema defaults after parse. Required key for relevance: `is_relevant`. Do not impute `true`.

### C-03 `record_id` mismatch

- **Scenario:** Model returns labels for a different or missing `record_id`.
- **Expected behaviour:** Discard the payload. Status `error`. Do not attach those labels to the current row or any other row.
- **Mitigation:** Echo-check in `relevance.py` / `extract.py`.

### C-04 Ambiguous retrieval problems

- **Scenario:** User mentions Photos and “can’t find things” with no specific image, or mixes backup and search in one post.
- **Expected behaviour:** If the post is not clearly about retrieving an **existing** old photo/image, `is_relevant` is `false` or `unclear` (prefer `unclear` when mixed). Extraction is skipped unless `is_relevant` is strictly true. Failure stage is not guessed.
- **Mitigation:** Relevance prompt lists irrelevant topics (backup, sync, storage, subscription, access, crash, edit, upload). `unclear` is a first-class relevance value. Researchers inspect `relevance_reason` in Explorer.

### C-05 Multiple failure stages in one record

- **Scenario:** The user both cannot name the query **and** cannot recognise results **and** gives up.
- **Expected behaviour:** Store **one** `primary_failure_stage` (the dominant stage supported by the text). If none is dominant, `other_unclear`. Do not invent a second column in MVP. `extraction_notes` may mention other stages **only if** they appear in `raw_text`.
- **Mitigation:** Prompt: pick primary or `other_unclear`. Analytics use the single field. Explorer shows notes + raw text so a PM can disagree.

### C-06 Irrelevant complaint classified as retrieval

- **Scenario:** Storage-full or crash review is labelled `is_relevant=true` with a fake failure stage.
- **Expected behaviour:** This is a **known model failure**. Human must see it in Explorer (`relevance_reason` vs `raw_text`). Analytics would be wrong if left uncorrected. MVP does not auto-scrape a gold set; researcher can mark retry / we do not silently “fix” via a second unsupervised agent.
- **Mitigation:** Tight relevance prompt + examples of irrelevant classes. Default Explorer checkbox to relevant-only but allow show-irrelevant. Optional later: manual override column is **out of MVP** unless cheap; at minimum, error/retry and evidence display. Count `relevance_confidence=low` in overview if useful.

### C-07 LLM invents remembered clues not in `raw_text`

- **Scenario:** Text never mentions people or place; model sets `remembers_people=true` or writes a café name.
- **Expected behaviour:** Prompts forbid invention. If it still happens, the row is inspectable: PM compares flags to `raw_text`. There is no automatic “truth” model. Q&A must quote packed `raw_text`, not extraction-only claims, when answering.
- **Mitigation:** Fail-closed prompt; `unknown` default; evidence strength `weak` when text is thin. Q&A pack includes `raw_text`. Do not let clue flags override empty source text in synthesis.

### C-08 Rate limits (429)

- **Scenario:** Groq returns 429 mid-batch.
- **Expected behaviour:** Up to **3** retries with exponential backoff for that call. If still failing: mark **that row** `error`, continue. Do not wipe prior successes. Progress bar stays honest. User can rerun unclassified/errors later.
- **Mitigation:** Retries in `llm_client.py`; per-row persist; remaining count in sidebar.

### C-09 API failures (4xx/5xx, auth)

- **Scenario:** 401 bad key, 500 upstream, network DNS error.
- **Expected behaviour:** 401/invalid key: stop or disable further calls with a **global** message (do not mark every remaining row error in a tight loop of 200 auth failures — fail the run after repeated auth errors). 5xx: retry 3× then per-row `error`. App remains up. Processed successes stay on disk.
- **Mitigation:** Distinguish auth vs transient in the client. Sidebar shows last pipeline error.

### C-10 Timeouts

- **Scenario:** A completion hangs beyond the client timeout.
- **Expected behaviour:** Treat as failed call for that row (retry then `error`). Do not block Streamlit forever without progress. Other rows still process after the timeout.
- **Mitigation:** Explicit timeout on the Groq client. Per-row checkpoint. Progress callback.

### C-11 Extraction run on irrelevant rows

- **Scenario:** Pipeline bug or manual force sends a backup complaint through `extract.py`.
- **Expected behaviour:** Intended path: extraction **skipped** when `is_relevant` is not true. If extraction is wrongly stored, labels should still be ignored in problem-map / clue analytics (slice = relevant + success only).
- **Mitigation:** Pipeline branch; analytics filters; do not chart failure stages for `is_relevant=false`.

### C-12 Model proposes a product solution during classification

- **Scenario:** `extraction_notes` says “build a chatbot”.
- **Expected behaviour:** Notes may be stored but UI copy and Q&A prompt forbid treating them as research findings. Classification fields stay taxonomies, not roadmaps.
- **Mitigation:** Prompt: discovery only, no solution. Phase 6 captions remind the PM the engine does not choose a product.

---

## 3. Analytics

### A-01 Division by zero

- **Scenario:** Zero relevant analysed rows (all irrelevant, all pending, or empty processed file). Problem map computes `%`.
- **Expected behaviour:** No `NaN` / `inf` in the UI. Show “No analysed relevant records yet” (or N=0). Do not call Groq to fill percentages.
- **Mitigation:** If denominator is 0, skip percentage or display em dash. Guard every `n / denom` in `analytics.py`.

### A-02 Tiny sample sizes

- **Scenario:** 2 relevant rows; one is `expression_failure` → 50%.
- **Expected behaviour:** Show count **and** N **and sampling_frame**. Caption that percentages are unstable in small slices (including Corpus A’s few `direct_vague_retrieval` triage rows, and any future small Corpus B). Do not round into false precision that hides N=2. Do not present a targeted-sample % as a Google Photos population rate.
- **Mitigation:** Always show **count (percentage, N=…, frame=…)**. Banner when the analysed slice is small.

### A-03 `unknown` / `unclear` dominating a category

- **Scenario:** Most rows are `other_unclear` or `forgotten_information=unknown`.
- **Expected behaviour:** Charts include the unknown bucket (do not drop it to make a prettier story). Caption that unclear is a result, not a rounding error. Problem map must be able to **disprove** a favourite failure mode.
- **Mitigation:** Enums always plotted. No “other” hidden by default.

### A-04 Percentages not summing to 100

- **Scenario:** Rounding 33.3×3, or filtering a subset, or mixing denominators (all rows vs relevant).
- **Expected behaviour:** Each chart states its denominator. Displayed percents may sum to 99–101 after rounding; do not rescale with hidden leftovers. Never mix relevant-only stages with full-corpus totals on one unmarked chart.
- **Mitigation:** One denominator per chart. Round at display time; compute from integers. Test: sum of stage counts equals relevant analysed N.

### A-05 Filters returning no records

- **Scenario:** Explorer or a chart slice has zero rows (e.g. `photo_type=screenshot` ∩ `evaluation_failure` empty).
- **Expected behaviour:** Empty table and “No records match”. No fake average. Plotly empty → friendly message, not a Python traceback.
- **Mitigation:** Check empty DataFrame before `px.bar`. Explorer empty state in Phase 4.

### A-06 Mixing pending/error rows into “analysed” percentages

- **Scenario:** 100 rows, 10 classified, UI shows failure-stage % as if N=100.
- **Expected behaviour:** Problem map and clue analysis use **relevant + `classification_status=success` only**. Overview separately shows pending/error counts.
- **Mitigation:** Documented slices in `analytics.py`. Sidebar remaining count.

### A-07 LLM asked to “summarise the dashboard”

- **Scenario:** Future UI mistake sends totals to Groq to rewrite percentages.
- **Expected behaviour:** Out of spec. Dashboards stay Pandas-only.
- **Mitigation:** `analytics.py` must not import `llm_client`. Q&A may **quote** injected `CALCULATED_STATS` but not recompute.

### A-08 Prevalence from mixed corpora

- **Scenario:** Dashboard or Q&A computes one “vague-memory share” from 225 broad rows plus targeted examples.
- **Expected behaviour:** That statistic **does not ship**. Report A and B separately. Targeted findings use the required wording.
- **Mitigation:** `analytics.compute` takes a frame filter. Tests: concatenating frames is not a supported prevalence path.

---

## 4. Ask the Research

### Q-01 Question unsupported by the dataset

- **Scenario:** “What share of iOS 18 users fail Places search?” when the CSV has no OS version.
- **Expected behaviour:** Retrieval scores near zero or packed rows lack the attribute → `insufficient_evidence: true`. Answer says the dataset does not contain that information. No web facts.
- **Mitigation:** Empty or weak retrieve → skip or constrain Groq. Prompt + `MIN_EVIDENCE`.

### Q-02 Retrieved evidence not relevant enough

- **Scenario:** Keyword overlap hits “photo” in a storage rant that leaked into relevant=true, or weak tokens.
- **Expected behaviour:** If packed rows do not actually support the claim, the model must say so; citations still shown so the PM can judge. If all scores are 0, **no Groq call**.
- **Mitigation:** Retrieve only `is_relevant=true` successes. Label boosts. Score 0 short-circuit. Prompt: do not stretch.

### Q-03 Conflicting evidence

- **Scenario:** Some cited users found the photo; others gave up; failure stages disagree.
- **Expected behaviour:** Answer describes **disagreement** and cites both sides. It does not pick a winner or a product. Injected Pandas counts, if any, remain the only percentages.
- **Mitigation:** Prompt: report conflict; cite ids on each side; no forced consensus.

### Q-04 Question outside the dataset / outside the research

- **Scenario:** “What’s the weather?” or “Should we build conversational search?”
- **Expected behaviour:** Weather → insufficient evidence / out of scope. Solution-choice → refuse to select a product; may point at failure-stage **evidence** if asked as research, without recommending the intervention.
- **Mitigation:** Q&A system prompt: dataset only; no solution selection. Architecture non-goal.

### Q-05 LLM uses outside knowledge

- **Scenario:** Model cites Google Help Centre, or record ids not in the pack (`r999`).
- **Expected behaviour:** Strip foreign ids. If none remain, insufficient evidence. UI never shows a citation that does not join to processed CSV. Help Centre URLs are not evidence.
- **Mitigation:** Intersection of `cited_record_ids` with packed ids. Prompt: only packed records. Do not enable browsing tools.

### Q-06 Too few records to draw a conclusion

- **Scenario:** One or two supporting rows (below `MIN_EVIDENCE`, default 3).
- **Expected behaviour:** `insufficient_evidence` true. Weak or no conclusion. Still show the 1–2 evidence cards so the PM can read them as anecdotes, labelled as **not** a finding.
- **Mitigation:** Enforce `MIN_EVIDENCE` in `qa.py` even if the model is confident.

### Q-07 Empty relevant corpus

- **Scenario:** Ask runs before any successful relevant classification.
- **Expected behaviour:** No Groq call. Message: classify data first / no relevant records.
- **Mitigation:** Guard in Ask tab.

### Q-08 Citation id exists but row missing `raw_text` in UI lookup

- **Scenario:** Join bug or processed file out of sync.
- **Expected behaviour:** Show “Record not found in processed data” for that id; do not display another row’s text.
- **Mitigation:** Lookup by exact `record_id`; no fallback to first row.

### Q-09 Mixing sampling frames in an answer

- **Scenario:** User asks “How common is vague-memory retrieval?” with both corpora loaded, or the retriever packs `broad` and `targeted_direct` ids together.
- **Expected behaviour:** Insufficient evidence for a prevalence claim. If answering from Corpus B only, the text must begin from “Within the targeted vague-memory retrieval sample…”. Corpus B is not described as all Google Photos users.
- **Mitigation:** Retrieve from one frame. Prompt forbids pooled prevalence. Strip citations from the other frame.

---

## 5. UX

### U-01 CSV not uploaded (and no default file)

- **Scenario:** First run without `data/raw/conversations_sample.csv` and no uploader file.
- **Expected behaviour:** Empty state explaining how to upload or place a CSV. Tabs do not throw. Classify disabled.
- **Mitigation:** Phase 1 default sample should exist in-repo; if missing, explicit CTA.

### U-02 Processing partially completed

- **Scenario:** User stops the run, browser refresh, or Groq dies at row 17 of 40.
- **Expected behaviour:** Successes already in processed CSV / session. Sidebar: remaining &gt; 0. Classify unclassified continues **without** resending successes. Error rows stay until retry checkbox.
- **Mitigation:** Per-row persist (architecture §8.2, §16). Progress bar.

### U-03 Application restarted

- **Scenario:** Local Streamlit rerun or process restart. Cloud restart (ephemeral disk).
- **Expected behaviour:** **Local:** reload raw + processed from disk; Q&A session history may vanish (OK). **Cloud:** committed processed sample still loads; in-session classifications not written to durable disk may be lost — message if write failed. Charts work without re-calling Groq for success rows.
- **Mitigation:** Load processed CSV on boot. Cloud: session_state fallback + README. Never require reclassify of successes.

### U-04 API key missing

- **Scenario:** No `.env` and no Streamlit secret.
- **Expected behaviour:** Overview/Explorer/charts work on processed data. Classify and Ask disabled with “Add GROQ_API_KEY”. Key never appears in logs or CSV.
- **Mitigation:** `secrets.py` returns `None`. Button guards.

### U-05 Slow classification

- **Scenario:** A long landscape or targeted run; UI looks frozen.
- **Expected behaviour:** Progress (`n / remaining`), status text of current `record_id`, no spinner-only void. User understands they should not spam the button. Rerun after interrupt is safe.
- **Mitigation:** `st.progress` + per-record save. Discourage force-reclassify.

### U-06 No evidence for a selected filter

- **Scenario:** User stacks Explorer filters until zero rows, or opens a Q&A citation after changing dataset.
- **Expected behaviour:** Explorer: “No records match these filters.” Q&A: stale citations either clear on dataset change or fail lookup (Q-08).
- **Mitigation:** Empty states. Clear Q&A session when processed data identity changes.

### U-07 Classify clicked twice

- **Scenario:** Double-click starts two pipelines.
- **Expected behaviour:** Second click ignored while a run is active, or both skip already-locked successes so duplicate Groq spend is minimised.
- **Mitigation:** `st.session_state["pipeline_running"]` flag.

### U-08 Streamlit Community Cloud cannot write `classified.csv`

- **Scenario:** Visitor classifies an upload; disk write fails or vanishes on reboot.
- **Expected behaviour:** Results remain for the **session** if kept in memory. Warning that Cloud storage is ephemeral. Demo relies on committed processed CSV.
- **Mitigation:** Architecture §17. Try persist; on failure, session_state + banner.

### U-09 Very wide / messy `raw_text` in the UI

- **Scenario:** Long lines, pasted tables, or HTML entities.
- **Expected behaviour:** Explorer uses a scrollable text area. Layout does not explode the sidebar. Text is shown as evidence, not executed as HTML.
- **Mitigation:** `st.text` / escaped markdown. Truncate **display** with “show more” only if needed; full text still available.

---

## 6. Traceability failures (cross-cutting)

### T-01 Insight without `record_id`

- **Scenario:** Q&A paragraph with no citations, or a chart tooltip that claims “users always…”
- **Expected behaviour:** Q&A without remaining legal citations → insufficient evidence. Charts caption N and point to Explorer. No uncited “always”.
- **Mitigation:** Architecture §20 checklist.

### T-02 Processed `raw_text` diverges from raw file

- **Scenario:** Bug writes summarised text into `raw_text`.
- **Expected behaviour:** Treated as a **defect**. Persist must copy `raw_text` from raw on every save. Tests/manual diff on sample CSV.
- **Mitigation:** Immutability rule; never assign model output to `raw_text`.

### T-03 Finding without sampling frame

- **Scenario:** A chart or Q&A sentence reports failure-stage mix with no `broad` / `targeted_direct` label.
- **Expected behaviour:** Does not ship. Add frame to caption or refuse the synthesis.
- **Mitigation:** Architecture two-corpus rules; Problem Statement §9.4.

---

## 7. Priority for MVP testing

Test these first; they protect research integrity and uptime:

1. Duplicate `record_id` / missing columns (D-01, D-03)  
2. Empty `raw_text` not sent to Groq (D-02)  
3. Invalid JSON and 429 without losing successes (C-01, C-08, U-02)  
4. Division by zero and empty filters (A-01, A-05, U-06)  
5. Q&A outside data, foreign citations, `MIN_EVIDENCE` (Q-01, Q-05, Q-06)  
6. Missing API key still shows processed charts (U-04)  
7. `raw_text` unchanged after classify (T-02)  
8. Sampling frames not pooled for prevalence (D-12, A-08, Q-09)  
9. Corpus A never overwritten (D-14)

---

## 8. Out of scope for these edge cases

- Repairing Google Photos itself  
- Scraping when a URL 404s  
- Multi-language translation pipelines  
- Human-in-the-loop gold annotation UI (nice-to-have after MVP)  
- Inventing rows to reach 200 records  
- Treating Corpus B as a representative sample of Google Photos users  
- Estimating vague-memory prevalence by merging Corpus A and Corpus B
