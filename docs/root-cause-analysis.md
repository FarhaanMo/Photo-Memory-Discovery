# Root-cause analysis

Step 12. The chain below uses only the processed research. No product feature is introduced at any level. Corpus B figures are preliminary (9 of 18).

## Symptom

A person who knows a specific past photo exists takes repeated attempts and manual scanning to reach it.

Across the five observed tasks, four took about 3, 4, 5 and 10 minutes and 2 or 3 attempts, and ended in scrolling. In the survey, 8 of 15 found the photo only after manual scrolling or browsing, 3 only after several attempts, and 2 gave up. Two of 15 found it quickly.

This is not "the photo cannot be found." All five observed tasks ended found.

## Five whys

### Why 1 — observed behaviour

The first action is coarse, and what comes back is too wide to be the answer.

INT001 typed "birthday" and got many unrelated birthday photos. INT002 typed "wedding" and got cards, screenshots and other wedding content. INT003 typed "football" and got many football photos. INT004 opened the Screenshots folder and could not see the right one. Each of those first inputs is one category word or one folder.

### Why 2 — immediate reason

The first input is thinner than the memory the person already has.

INT001 also remembered the friends, about 2021, the restaurant and a red wall. INT003 knew which match and what the photo looked like. INT002 remembered family, a sister and 2018, and searched the event word rather than the sister or the year. In the survey, 14 of 15 remembered people and 10 of 15 still said they did not know what words to search. Within the 9 processed Corpus B records, date/time is the explicitly forgotten item in 5, while people, time, association or visual clues are still evidenced in several of those same rows.

### Why 3 — memory and search mismatch

The memory available at the start is episodic and visual: who was there, the occasion, the look, a rough era, a category such as "screenshot". The key that would isolate one item is precise: an exact or usable date, a place name, a filename, or a distinctive term.

Those are different kinds of information. Remembering "about 2021" or "a red wall" does not by itself produce the string that narrows a large library. INT004's month became usable only at the second step. INT005 is the boundary case: 2022 was precise enough to navigate with, and the event was remembered with it, so there was no mismatch to begin with.

### Why 4 — current interaction constraint

The library is asked through a text query, a person or place facet, a folder, or a position on the timeline. When the person cannot supply one of those precisely, each of them returns a wide slice: every birthday, every wedding, every football photo, every screenshot. Telling the target apart is then left to looking.

The interviews show the second step is often a facet the product already has. A friend's name, a sister's name, a team name, a month. That second key helps and, in these four tasks, still did not finish the job. Scanning remained.

### Why 5 — root problem

The person already holds more context and appearance than the first action uses. After that broad or incomplete action, the candidate set stays large or poorly separated, and nothing in the journey helps them turn the rest of what they remember into the next narrowing signal. They invent the next clue themselves (a name, a month) and then scan.

This is not a claim about Google's internal retrieval architecture. Google Photos already accepts descriptive and semantic queries. The observed gap is earlier and later than that: the first action under-uses memory, and the follow-up does not help choose which remembered detail would actually separate the current candidates.

**Root cause:** users often retain richer contextual and visual memories than they express in their initial retrieval action. When the first action is broad or incomplete, they receive a large or insufficiently discriminating candidate set, and the current journey gives limited support for progressively converting remembered context into signals that narrow toward the target.

## What this is not

- It is not "old photos are unfindable." INT005 took about 2 minutes and one attempt. Two survey respondents found the photo quickly.
- It is not "search results are generally bad." Corpus A's 116 retrieval-adjacent records are a broad complaint class and were not used as evidence for this cause.
- It is not a missing feature. The four refinements that worked used mechanisms that already exist (names, a month, scrolling). The cost is getting to a precise enough key, and then still scanning what remains.

## Workarounds

### Fallback after the first attempt was not enough

Observed in INT001–INT004 and in the survey outcomes. These are workarounds:

| Fallback | Where |
|---|---|
| Retype with a person or team name | INT001 friend, INT002 sister, INT003 team |
| Narrow a correct category by month | INT004 |
| Scroll the timeline or the result set | INT001–INT004; survey outcome 8 of 15; GP087 scrolled through years; DV009 |
| Try several descriptive wordings | GP087 |
| Stop | Survey: gave up, 2 of 15 (1 of 13 screened-in) |

In the four friction interviews the name or month refinement was not the end. Scrolling still followed. So refinement and browsing are one path, not two alternative successes.

### Intentional navigation, not a workaround

INT005 chose year/month browsing because that matched the memory, found the photo, and then saved it to Favourites. The scrolling was the method, not a recovery. It is evidence that chronological navigation works when the temporal anchor is strong enough. It is not listed as a workaround.
