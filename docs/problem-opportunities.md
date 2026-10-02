# Problem opportunity

Step 12. This defines the problem and the outcome to measure. It does not propose a feature, a solution, or an MVP. Corpus B is preliminary (9 of 18 processed). Survey figures are a convenience sample of 15, not a market estimate.

## Opportunity

**Target user.** Someone looking for one specific past photo in a large personal library, who remembers contextual or visual detail (people, occasion, look, rough era, category) and does not have a precise searchable or navigational anchor when they start.

**Trigger / scenario.** They know the photo exists and start from a coarse handle: one event or category word, or the folder they know it lives in.

**What they remember.** People, the occasion, what it looked like, a rough time, or the category. In the five tasks: friends and a red wall; a sister's wedding and 2018; a football match and its look; that it was a screenshot; a graduation in 2022.

**What they lack.** A precise anchor they can use on the first attempt: exact date, place name, filename, or a distinctive term. A rough year was sometimes remembered and still not what they typed (INT002 remembered 2018 and searched "wedding").

**Observed failure.** The first result set is broad, noisy, or full of similar items. Four of five observed tasks then needed a second, more specific input and still ended in scrolling. Time was about 3 to 10 minutes and 2 or 3 attempts. In the survey, 8 of 15 reached the photo only by scrolling or browsing, and 2 gave up.

**Root cause.** Users often retain richer contextual and visual memories than they express in their initial retrieval action. When that action is broad or incomplete, the candidate set stays large or poorly separated, and the journey does little to turn the remaining memory into a narrowing signal. See `docs/root-cause-analysis.md`. This does not assume how Google ranks photos internally.

**Current fallback.** A second query using a name or a month, then manual scrolling. Giving up is the unsuccessful end of the same path (2 of 15).

**User cost.** Minutes of reformulation and scanning for a photo the person already knows exists. In the one clean success, INT005, the same kind of task took about 2 minutes and one attempt because the year was usable from the start.

**Product outcome.** Of incomplete-memory retrieval attempts, a larger share reach the intended photo without prolonged manual browsing. Measured by successful reach, time to target, attempts to target, and whether scanning was a fallback after a miss. Not by feature adoption.

**Business relevance.** In this survey, looking up a specific past photo is a repeated activity (7 of 15 several times a week, 5 a few times a month), and 13 of 15 said they have struggled at least once because a date, place or name was missing. That is salience inside a convenience sample. It is not a revenue or retention estimate. No Google usage or storage figures are available here.

**Counter-evidence.** INT005: 2022 and a graduation, year/month browsing, about 2 minutes, one attempt, coded no_failure. Survey: 2 of 15 found the photo quickly. Of the 7 frequent retrievers, 2 also found it quickly, so frequency alone does not mark the failure. Corpus A: only 4 of 225 public records are this scenario; the public complaint landscape is mostly other search-quality issues (116 retrieval-adjacent). All five observed tasks did find the photo, so the problem is the cost of the path, not a universal failure to find.

**Limitations.**

- Corpus B is 9 of 18 and was sampled for vague-memory cases, so its stage mix cannot estimate how often this happens.
- The survey is n = 15, convenience, not representative. S04 and S09 failed the screen and still answered; screened-in figures do not change the ordering.
- "What did you do first?" allowed several answers, so survey methods are not a sequence.
- Interview times are approximate. Five tasks, all of which ended found.
- DV007 is iOS Photos. It supports the evaluation pattern and is not a Google Photos complaint.
- No library-size measurement except one stated "more than two million" (DV007) and qualitative "very large" / "hundreds".
- Whether results reminded people of new details was not observed (unknown on all five interviews).

## Outcome to measure

Primary:

> Increase the share of incomplete-memory retrieval attempts that reach the intended photo without prolonged manual browsing.

An incomplete-memory attempt is one where the person starts without a precise date, place, filename, or distinctive term, and with some contextual or visual memory.

Companion measures, from the journey in `docs/evidence-synthesis-final.md`:

| Measure | What it captures | Baseline in this project |
|---|---|---|
| Successful reach | Intended photo found on that attempt | Interviews 5 of 5 found. Survey 13 of 15 found by some path, 2 gave up. Not a product baseline. |
| Time to target | Cost of the path | Friction tasks about 3, 4, 5, 10 minutes. INT005 about 2. Approximate. |
| Attempts to target | Expression plus recovery | Friction tasks 2 or 3. INT005 1. |
| Manual-browsing fallback | Scanning used because the first method did not isolate the photo | INT001–INT004 yes. INT005 no (scanning was the method). Survey outcome 8 of 15. |
| Recovery after a first miss | A second input gets closer | 4 of 5 interviews refined; all 4 still scanned afterwards. |

No adoption metric is defined. There is no feature to adopt.

## Impact sizing

Addressable vague-memory retrieval attempts ≈ active users × historical-retrieval attempt rate × incomplete-memory start rate × friction rate.

| Input | Status | What this project can say |
|---|---|---|
| Active users | Unknown. Requires Google internal data. | Not estimated. No user or install number is invented. |
| Historical-retrieval attempt rate | Directional survey estimate only. | 7 of 15 several times a week, 5 of 15 a few times a month, in a convenience sample. Not a population rate. |
| Incomplete-memory start rate | Directional survey estimate only. | 13 of 15 said they have at least once known a photo existed and struggled for lack of date, place or name. 10 of 15 said they did not know what words to search, on a recalled attempt. Neither is the share of all retrieval attempts that start this way. |
| Friction or failure rate | Known only inside this project. | 4 of 5 observed tasks had friction and still found the photo. Survey: 2 of 15 gave up; 8 of 15 found it only after scrolling. Not a failure rate for Google Photos. |

The product of these four is not computed. Three inputs are not population rates, and one is unknown. The sizing frame is recorded so a later estimate can be filled with internal data rather than with guesses.

## Problem statement

When someone with a large personal photo library tries to retrieve one specific past photo, they often remember the people, the occasion, or what it looked like, but not a precise date, place, or distinctive search term. The first attempt then returns a broad or crowded set, and they spend minutes reformulating and scrolling, or they give up.

## Decision summary

| Item | Decision |
|---|---|
| Target segment | One specific past photo, large personal library, contextual or visual memory, no precise anchor at the start |
| Scenario | First action is a coarse word or a category folder |
| Root cause | Richer memory than the first action uses; little help turning the rest into a signal that narrows the current set |
| Problem statement | As above |
| Product outcome | A larger share of incomplete-memory attempts reach the intended photo without prolonged manual browsing |
| Strongest support | INT001 and INT003 quotes and codings; survey "didn't know what words" 10 of 15 beside people remembered 14 of 15; INT001–INT004 times of 3–10 minutes ending in scrolling; survey outcome 8 of 15 only after scrolling; Corpus B date/time forgotten in 5 of 9 preliminary rows |
| Strongest counter-evidence | INT005, about 2 minutes, one attempt, no_failure |
| Sharpest limitation | Corpus B is preliminary and purpose-sampled; the survey is a convenience sample of 15; this is cost of retrieval, not universal failure to find |
