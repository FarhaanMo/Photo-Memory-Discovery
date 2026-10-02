# Evidence synthesis

Step 12. Counts are computed in Pandas from the processed research files. No model was called for this synthesis. Unlike samples are not pooled, and no figure below is a prevalence estimate for Google Photos users.

## 1. Research inputs

| Stream | What was loaded | Role |
|---|---|---|
| Corpus A | 225 public records, all triaged | Broad public retrieval landscape. Shows what public complaints contain. Not a sample of users. |
| Corpus B | 9 successfully processed of 18 | Targeted qualitative evidence of vague-memory retrieval. **Preliminary — processing incomplete.** |
| Survey | n = 15 | Primary research, convenience sample. |
| Interviews | n = 5 real observed retrieval tasks | Primary research. Synthetic interviews = 0. |

Corpus B status: 9 valid, 0 needs review, 1 processing error (DV010, Groq quota), 8 not started (DV011–DV018). Every Corpus B statement below is limited to those 9 rows and is preliminary. The synthesis is not blocked on the missing rows.

Survey caveats used throughout: two respondents (S04, S09) answered "No, I don't remember" on the screening question and still answered later questions. Counts below are for all 15, with the screened-in figure (n = 13) in parentheses where it differs. Multi-select questions do not sum to 15 and cannot show order. The question "What did you do first?" is treated only as **retrieval methods attempted**.

## 2. Triangulation

Confidence is based on agreement across independent sources, not on the largest count. Corpus B was collected because the records already described vague-memory retrieval, so a high Corpus B count cannot by itself confirm that a pattern is common.

### A. Expression friction

The person remembers useful context or appearance and does not turn it into an effective search input.

| Source | Evidence |
|---|---|
| Corpus A | Indirect and thin. Only 4 of 225 records are direct vague-memory retrieval. GP087 tried many descriptive combinations for a grandmother's calico cat and then scrolled. GP177 remembers one or two words from a screenshot among hundreds. The other 221 records are retrieval-adjacent (116) or not retrieval-related (105), so expression is not what broad public complaints are mostly about. |
| Corpus B (preliminary, 9 of 18) | 7 of 9 coded expression (DV001–DV004, DV006, DV008, DV009). Forgotten information is date/time in 5 of those. Search behaviour is unstated in 8 of 9, so these rows support a memory gap more clearly than they show the words someone typed. |
| Survey | "Didn't know what words to search" 10 of 15 (9 of 13 screened-in). "Couldn't remember when or where" 6 of 15 (5 of 13). People remembered are 14 of 15, so the gap is not an empty memory. |
| Interviews | INT001 and INT003 are coded expression. INT001 remembered friends, about 2021, a restaurant, a birthday and a red wall, and typed "birthday". INT003 knew the match and what the photo looked like, and typed "football". Both said, in their own words, that they knew what the photo looked like but did not know what to type. |

Supporting examples: INT001, INT003, GP087, DV003 (remembers the place, not when).

Counter-evidence: INT005 remembered 2022 and a graduation and did not have this friction. Survey: 2 of 15 found the photo quickly. Corpus A: this scenario is 4 of 225 public records.

Limitations: Corpus B over-represents the scenario by design, and most of its rows do not record the actual query. Survey answers are self-reported and multi-select.

**Confidence: high** that this friction occurs when memory is contextual and the first input is coarse. Not high as a share of all Google Photos complaints.

### B. Retrieval friction

A plausible clue or query is used, and the target still does not surface effectively.

| Source | Evidence |
|---|---|
| Corpus A | 116 retrieval-adjacent records are general search-quality complaints. They are not coded as this friction and are not counted as support. |
| Corpus B (preliminary) | 1 of 9: DV005, a remembered phrase about a daughter singing did not retrieve the photo. |
| Survey | "Search results were not relevant" 8 of 15 (8 of 13). |
| Interviews | INT002 searched "wedding" and got wedding cards, screenshots and other wedding content, then still needed a name and scrolling. Coded retrieval. About 10 minutes, 3 attempts. |

Supporting examples: INT002, DV005.

Counter-evidence: INT005's year/month navigation surfaced the photo on the first attempt. The other interviews' first results were crowded rather than empty.

Limitations: one observed task and one Corpus B row. "Not relevant" in the survey is not the same as "the target was missing from an otherwise plausible query".

**Confidence: medium.**

### C. Evaluation friction

Plausible or similar candidates are present, and the exact target is hard to pick out.

| Source | Evidence |
|---|---|
| Corpus A | GP177: hundreds of screenshots, only one or two remembered words. |
| Corpus B (preliminary) | 1 of 9: DV007, similar baptism photos from the same day, exact one not identified. DV007 is an iOS Photos analogue, not a Google Photos complaint. |
| Survey | "Too many similar photos" 6 of 15 (6 of 13). |
| Interviews | INT004 is coded evaluation: the Screenshots folder was the right category and still too large; the month was used afterwards. About 5 minutes, 2 attempts. INT003's first results were relevant but too broad. INT002's researcher note describes a later difficulty among many photos from the same wedding; the coded stage for INT002 remains retrieval. |

Supporting examples: INT004, DV007, GP177.

Counter-evidence: INT005 did not face a crowded set. INT001's first results were largely irrelevant, which is retrieval noise rather than evaluation.

Limitations: evaluation is the coded first break in only one interview and one Corpus B row. In INT002 and INT003 it appears after an earlier break.

**Confidence: medium.**

### D. Recovery friction

After a miss, the person struggles to get closer and has to reformulate or switch method.

| Source | Evidence |
|---|---|
| Corpus A | Not stage-coded. GP087's many descriptive combinations are a recovery sequence ending in scrolling. |
| Corpus B (preliminary) | Refinement is unknown on all 9 valid rows. The paraphrases do not describe what happened after the first attempt. One workaround is recorded (DV009, timeline scrolling). |
| Survey | "Didn't know how to improve or refine my search" 9 of 15 (9 of 13). "Yes, but only after several attempts" 3 of 15. |
| Interviews | 4 of 5 refined: a friend's name, a sister's name, a team name, a month. All four then still scrolled, and all four found the photo. INT005 did not need a second attempt. |

Supporting examples: INT001–INT004, survey refine signal, GP087.

Counter-evidence: recovery in the interviews eventually worked. It is rarely the first break (no interview is coded recovery). Corpus B cannot confirm the sequence.

Limitations: survey "didn't know how to refine" and interview "did refine" can both be true; they are not a contradiction, and they are not the same measurement.

**Confidence: medium** that a second attempt is common and often still insufficient. Low as a claim that recovery is the primary failure stage.

### E. Manual-browsing cost

Scrolling or browsing is used because the other method did not isolate the target.

| Source | Evidence |
|---|---|
| Corpus A | GP087 scrolled through years of photos after descriptive search failed. |
| Corpus B (preliminary) | Only DV009 states manual scrolling. Absence elsewhere means the paraphrase did not say, not that scrolling did not happen. |
| Survey | Outcome "yes, after manual scrolling / browsing" 8 of 15 (7 of 13). Difficulty "ended up scrolling manually" 8 of 15. "Scrolled timeline" as a method attempted is 12 of 15, but that question cannot show whether scrolling was first, intended, or a fallback. |
| Interviews | INT001–INT004 scrolled after an insufficient first attempt (3, 4, 5 and 10 minutes; 2 or 3 attempts). INT005 also scrolled, for about 2 minutes, as the intended year/month method, and is not counted as this cost. |

Supporting examples: INT001–INT004, survey scrolling outcome, GP087, DV009.

Counter-evidence: INT005. Survey: 2 of 15 found the photo quickly. Among the 7 respondents who look for a specific past photo several times a week, only 2 of 7 had scrolling as the eventual outcome (2 found it quickly, 2 after several attempts, 1 gave up).

Limitations: interview times are approximate. Survey scrolling-as-method is not scrolling-as-fallback.

**Confidence: high** that manual browsing is the costly fallback when the first attempt does not isolate the photo. Not a claim that browsing is always costly.

## 3. What the counter-evidence changes

INT005 remembered a year and a graduation, went straight to year/month browsing, and found the photo in about 2 minutes on one attempt. No failed query, no reformulation. Coded `no_failure`.

INT004 reached the correct category, Screenshots, and still could not pick the sales-target screenshot out of a very large set until a month was applied.

Together they rule out "Google Photos cannot find old photos." All five observed tasks ended with the photo found. The cost appears when the memory at search time does not include a precise searchable or navigational anchor: an exact or usable date, a place, or a distinctive term. A strong time anchor plus chronological navigation can be enough. Reaching the right category is not enough when many plausible candidates remain.

## 4. Observed journey

This is the sequence the interviews actually showed, with the other sources placed beside each stage. It is a decomposition for later measurement, not a funnel with a single denominator.

| Stage | What it is | Survey | Corpus B (preliminary, 9) | Interviews |
|---|---|---|---|---|
| Memory | What the person knows before starting | People 14, rough location 9, event 9, rough time 8, before/after 8, object 4, visual appearance 3, of 15 | Clues evidenced: people 4, time 4, association 4, visual 3, place 1, object 1, event 1, of 9. Forgotten date/time in 5 | INT001: 5 clues. INT002: people, year, wedding. INT003: match, team, appearance. INT004: screenshot; month used later. INT005: 2022 and graduation. People and visual are unknown for INT005 |
| Expression | What they actually enter or select | Did not know what words to search: 10 of 15. Methods attempted cannot show the first input | Search strategy unknown in 8 of 9. DV005 searched a remembered phrase | INT001 "birthday", INT002 "wedding", INT003 "football", each one term. INT004 opened Screenshots. INT005 went to the year |
| Retrieval | What comes back | Results not relevant: 8 of 15 | DV005: phrase search did not retrieve the photo. Other rows mostly do not describe the result set | INT001 largely irrelevant. INT002 noisy wedding content. INT003 relevant but too broad. INT004 right category, far too many. INT005 effective |
| Evaluation | Whether the exact item can be recognised | Too many similar photos: 6 of 15 | DV007: similar same-day baptism photos | INT004 coded here. INT003's set was full of similar football photos. INT002's note describes this later in the task |
| Recovery | What happens if the first attempt is not enough | Did not know how to refine: 9 of 15. Found only after several attempts: 3 of 15 | Not described in the 9 paraphrases | INT001–INT004 each added one more specific clue (name or month) and still were not done |
| Outcome | Found, not found, or fallback | Quickly 2, after several attempts 3, after scrolling 8, gave up 2, of 15 | not_found 4, unclear 5, found 0, of 9. Public posts rarely record success | All 5 found. INT001–INT004 via scrolling after the refinement (3–10 min). INT005 via the original chronological path (about 2 min, 1 attempt) |

## 5. Behavioural segments

Age is not used.

### 1. One specific old photo in a large personal library

Behaviour: looking for a single known item inside a library big enough that scanning is slow.

Scenario: a wedding photo, a match photo, one screenshot among a large screenshot library.

Need: to land on that item without scanning a wide slice of the library.

Evidence: all five interviews; DV007 (a library of more than two million photos, iOS analogue); GP177 (hundreds of screenshots); survey retrieval frequency of several times a week (7 of 15) or a few times a month (5 of 15).

Why it is distinct: the cost depends on library size. The same coarse query is cheap in a small library.

Limitations: nobody measured library size except DV007's stated figure and the qualitative "very large" screenshot set. This segment includes INT005, who succeeded, so size alone does not define the problem.

### 2. Contextual or visual memory, missing a precise anchor

Behaviour: the person can describe the photo in life terms (who, occasion, look, rough era) and does not have, or does not use, a precise date, place, filename, or distinctive term.

Scenario: "I know what it looked like but not what to type."

Need: a way through the library that can start from partial context rather than from a precise key.

Evidence: INT001 and INT003 quotes and codings; survey "didn't know what words" (10 of 15) alongside high people/event/location memory; Corpus B forgotten date/time (5 of 9) with expression coded on 7 of 9. INT005 shows the boundary: with a usable year, this segment does not apply.

Why it is distinct: the failure is in the match between memory and retrieval key, not in the photo being missing.

Limitations: "rough time" in the survey (8 of 15) means some people do have a temporal clue. The interviews show that a rough era is not always what they type first.

### 3. Many similar photos in the same category

Behaviour: the person reaches a relevant set and cannot pick the exact item out of near-matches.

Scenario: screenshots, one wedding, one football season, one day's baptism photos.

Need: to distinguish the target from neighbours that share the category.

Evidence: INT004; INT003's result quality; INT002's later note; survey 6 of 15; DV007; GP177.

Why it is distinct: getting to the right neighbourhood is not the end of the task.

Limitations: in three of the interviews this follows a coarse first input, so it is often a consequence of segment 2 rather than a separate population.

### 4. Frequent historical retrievers who fall back to browsing

Behaviour: people who often look up old photos and whose attempts regularly end in scrolling.

Scenario: repeated weekly lookup.

Evidence for frequency: 7 of 15 look for a specific past photo several times a week. Evidence against the fallback half: of those 7, the eventual outcome was scrolling for 2, several attempts for 2, quickly for 2, and gave up for 1. Five of the 7 did *mention* scrolling as one difficulty, which the multi-select question cannot turn into "their attempts end in scrolling".

Why it would have been distinct: repetition would raise the cost per person.

Limitations: the cross-check does not support "repeatedly fall back to browsing" as the defining behaviour. Not selected.

### Target segment

**People looking for one specific past photo in a large personal library, who remember contextual or visual detail and do not have a precise searchable or navigational anchor at the moment they start.**

This is segment 2, inside the setting of segment 1. Segment 3 is treated as a common consequence, not as the segment itself. The choice is not "10 of 15 didn't know what to type." That survey item is one of four agreeing sources. Segment 4 was rejected because the frequent-retriever outcomes do not concentrate on browsing.
