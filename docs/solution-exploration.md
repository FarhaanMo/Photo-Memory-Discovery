# Solution exploration

Step 13. The problem from Step 12 is frozen. Concepts are compared against that problem. Corpus B remains preliminary (9 of 18 processed) and is not used as a prevalence estimate. No model was called for this step. Nothing here is a build.

## Frozen problem

**Segment.** Someone looking for one specific past photo in a substantial personal library who remembers contextual or visual information but does not begin with a precise retrieval anchor.

**Scenario.** The first handle is coarse: an event, a person, a category, a rough time, a rough context, or a folder.

**Observed failure.** That action produces a broad or crowded set, or it fails to isolate the target. The person then reformulates, adds another clue, browses, scrolls, or gives up.

**Outcome.** Increase the share of incomplete-memory retrieval attempts that reach the intended photo without prolonged manual browsing.

**Root cause (wording corrected in Step 13).** Users often retain richer contextual and visual memories than they express in their initial retrieval action. When the first action is broad or incomplete, they receive a large or insufficiently discriminating candidate set, and the current journey gives limited support for progressively converting remembered context into signals that narrow toward the target.

This replaces an earlier sentence that said retrieval is "keyed to precise metadata and keywords." The research does not establish Google's ranking architecture, and Google Photos already supports descriptive search. The gap the interviews show is behavioural: unused memory, then a wide set, then an unsupported next step.

**Problem statement, unchanged.** When someone with a large personal photo library tries to retrieve one specific past photo, they often remember the people, the occasion, or what it looked like, but not a precise date, place, or distinctive search term. The first attempt then returns a broad or crowded set, and they spend minutes reformulating and scrolling, or they give up.

**Out of scope for every concept.** INT005. A usable year plus the graduation was enough for year/month browsing to finish in about 2 minutes and one attempt. A concept that inserts itself in front of an already precise anchor solves a problem that task did not have.

## How might we

How might we help someone progressively turn contextual and visual details they already remember into signals that narrow a wide candidate set toward one specific photo, without requiring the perfect query at the start?

## Three concepts

The same root cause, three mechanisms. One of them does not use a chatbot.

### Concept A — Next useful question

**Core mechanism.** After a coarse first action, retrieve a candidate set, then ask one clarification chosen because it is likely to split that set. The answer updates the set. Ask again only if another question would still separate the remaining photos. The intelligence is which question to ask, not an open conversation.

**Moment of intervention.** After the first broad or incomplete result, during recovery. Not before the user has tried anything, and not instead of a first action that is already precise.

**User flow.**

1. The person starts as they do now: "birthday", "wedding", "football", or Screenshots.
2. They see a bounded candidate set, not an invitation to keep typing.
3. One question uses something the set can actually separate and the person may remember. Examples grounded in the interviews: "Was there a red wall?", "Was your sister in it?", "Was this a match rather than any football photo?", "Was this around the month you have in mind?"
4. The set shrinks or is reranked. If it is still wide, one more question. If it is small, stop asking.
5. They recognise the photo, or they are told the question did not separate the set and scrolling remains available.

**Research signal.** INT001 remembered five clues and typed one word. INT002 remembered 2018 and a sister and typed "wedding". INT003 knew the look of a match and typed "football". INT004 knew the category and only later used the month. In all four, the second clue was invented by the person after a bad set. Survey: 10 of 15 did not know what words to search, while 14 of 15 remembered people. "Didn't know how to refine" was 9 of 15.

**Why it could work.** The observed recovery is already "add one more specific clue." The missing support is choosing the clue that would discriminate, and offering it at the moment the set is still wide.

**How it differs from normal search and Ask Photos.** Keyword search and descriptive search both wait for the user to produce the next phrase. Ask Photos is a conversation about the library. This concept asks one closed question selected from differences inside the current candidate set. If the only value were "describe the photo in a sentence," it would not be different enough, and it is not the design.

**AI-native element.** Score candidate questions by how they would split the current set (people present or absent, time bands, places, visual attributes such as indoor/outdoor or a dominant colour) and by whether that attribute is the kind of thing the person has already hinted they remember. The model does not invent a memory. It proposes a split.

**MVP scope.** A small personal-scale library, a coarse opening query, one round of candidates, one generated question, an updated set, and a stop. Not an open chat. Not a second and third question unless the first one demonstrably shrinks the set.

**Key assumption.** For a wide set, there exists a question the person can answer that actually removes many of the wrong photos.

**Key failure mode.** The question asks for something they do not remember, or the true photo was never in the first set, so later answers only rearrange misses.

**Why this is not a generic wrapper.** A wrapper can ask "tell me more." It cannot know which detail splits this library. That choice depends on this person's photos, who is in them, when they cluster, and how similar the current candidates are. Those signals sit inside the library, not in a general chat model.

### Concept B — Recognition clusters

**Core mechanism.** No chatbot. Group the current candidates into a few visual clusters. The person marks a group or a photo as closer, not this, same people wrong moment, or wrong event. Those recognition signals rerank the rest.

**Moment of intervention.** After a candidate set exists, when the hard part is telling the target apart from neighbours. This is the evaluation moment (INT004, and the later stretch of INT002 and INT003).

**User flow.**

1. Coarse start, as now.
2. Instead of a long scroll, a handful of clusters.
3. One tap: "closer" or "not this" or "right people, wrong moment."
4. Clusters update. Repeat until one photo is identifiable or the feedback stops changing the set.

**Research signal.** INT004 reached Screenshots and still could not find the sales-target image until a month was applied. INT003's football results were relevant and too numerous. Survey: "too many similar photos" 6 of 15. Corpus B, preliminary: DV007, similar baptism photos from the same day (an iOS analogue, not a Google Photos complaint). INT001 and INT003 both said they knew what the photo looked like.

**Why it could work.** Recognition of a face, a wall, or a moment is what they already do while scrolling. Clustering asks for that judgment on a few groups instead of a linear pass.

**How it differs from normal search, Ask Photos, and timeline scrolling.** It does not ask for more text. It is not People, Places, or albums, which require the person to know the facet name first. The new signal is a judgment on a photo, used to rerank.

**AI-native element.** Cluster by visual similarity and rerank from the judgments. The model is doing grouping and update, not dialogue.

**MVP scope.** One coarse query, clusters over a fixed library, two rounds of closer/not-this, then a short list. No chat field.

**Key assumption.** The target is already inside the first retrieved set, and the clusters are different enough that "not this" removes the right photos.

**Key failure mode.** The first set missed the target, so every tap reinforces a wrong neighbourhood. Or the clusters are so alike that the taps become a slower form of scrolling.

**Why this is not a generic wrapper.** Cluster quality and the meaning of "same people, wrong moment" depend on this library's embeddings and on faces and times that co-occur. A general vision chat looking at uploaded screenshots does not hold that structure between sessions.

### Concept C — Clue card before search

**Core mechanism.** Before any search, a short card asks only for what they remember: who, rough when, where or context, event, look, what happened around it. Empty fields stay empty. The filled fields become the retrieval signals.

**Moment of intervention.** Before the first broad query. This is the expression moment, not the recovery moment.

**User flow.**

1. They open the card instead of the search box.
2. They fill what they know. INT001 could enter friends, about 2021, restaurant, birthday, red wall, and leave the rest blank.
3. One search runs from those fields.
4. They get a result list. Further narrowing is ordinary search or scrolling.

**Research signal.** The same unused-memory facts as Concept A, caught earlier. Survey "didn't know what words to search" (10 of 15) is the expression form of this. Corpus B, preliminary: 7 of 9 coded expression, and date/time was the stated gap in 5 of 9, so a card must allow "I don't know when."

**Why it could work.** The interviews show the memory was available before the first keystroke. A card makes those fields legitimate answers, including blanks, so the first query is not forced down to one category word.

**How it differs from normal search and Ask Photos.** The difference is the structured prompt and the permission to leave fields unknown. The retrieval step itself is still "combine clues and search." That is close to a better query, which descriptive search and Ask Photos already move toward. It does not choose a follow-up from the candidate set.

**AI-native element.** Map partial, messy field text onto people, time bands, and visual attributes, and ignore blank fields rather than treating them as constraints. The intelligence is interpretation of partial input, not a next action.

**MVP scope.** The card, a search over a fixed library, one result list. No clarification loop.

**Key assumption.** People will fill more than they would have typed, and those extra fields are discriminative rather than just more broad words ("birthday", "friends", "nice").

**Key failure mode.** The card feels like a form they must complete, so someone who already has a year (the INT005 situation) is slowed down. Or they still only fill the coarse word, and the result set is unchanged.

**Why this is not a generic wrapper.** Weakest of the three on this test. A form plus a search API is straightforward to copy. The only hard part is mapping partial memory onto a private library, and this concept does little with the library beyond the first query.

## Comparison

No numeric scores. Each cell is a judgment from the evidence above.

| Question | A. Next useful question | B. Recognition clusters | C. Clue card |
|---|---|---|---|
| Fit to the root cause | Direct. Uses the unexpressed memory after a wide set, one signal at a time. | Partial. Uses recognition, not the contextual clues they never typed. | Partial. Pulls memory out before the search, then stops. |
| Expression friction (INT001, INT003; survey 10 of 15) | The question is a way to express one detail they could not turn into a query. | Does not help them state the red wall or the year if those are not visible as a choice. | Strongest before the first query. |
| Evaluation friction (INT004; survey 6 of 15; DV007 preliminary) | Helps only if a question splits similar photos. A month question fits INT004. A vague question does not. | Strongest. The task is judging neighbours. | Weak. The list after the card can still be crowded. |
| Recovery support | This is the recovery step the four friction interviews did alone. | Recovery by recognition, not by a new clue. | Ends before recovery. |
| Interaction effort | One closed question, then look. Low if the question is good. High if several questions miss. | Several judgments. Can become another browse if clusters are weak. | A form up front, including for people who did not need one. |
| Chance of beating manual scrolling | If one answer removes most of the wrong photos, the 3–10 minute scans in INT001–INT004 shrink. | If the target is on screen in an early cluster, scanning a timeline is unnecessary. | Only if the first combined query is already tight. The interviews still scanned after a second clue. |
| Different from current Google Photos search | Yes, if the question is chosen from the candidate set. No, if it is an open "describe it" box. | Yes. Closer/not-this is not search, People, Places, albums, or timeline order. | Mostly no. It is assisted query formulation. |
| AI-native value | High: the next question depends on this set. | High: clustering and rerank depend on this library. | Lower: partial-field interpretation, then ordinary retrieval. |
| Feasible as a graduation prototype | A fixed library, one query, one question, one refresh. Testable with 3 people. | Needs credible clusters over real images. Also testable with 3 people, more build. | Easiest build, weakest distinction. |
| Testable with 3 users | Yes. Compare coarse search plus scrolling against one clarifying question on the same target. | Yes, if the clusters are real. | Yes, but a null result is likely if they only fill the coarse field. |
| Major risk | Wrong or unanswerable question. Target absent from the first set. | Target absent from the first set, and taps make that worse. | Pre-search form does not match how the four friction tasks actually proceeded, and it taxes the INT005 case. |

## Overlap with what already exists

| Existing capability | A | B | C |
|---|---|---|---|
| Keyword search | Not the same, unless the "question" is just another empty text box. | Not the same. | The card compiles into a keyword or semantic query. Close. |
| Natural-language / descriptive search | Overlaps only if the user must compose the description. A closed question does not. | Does not overlap. | Overlaps. "Fill in what you remember" is a structured descriptive query. |
| Ask Photos | Overlaps if the MVP becomes an open chat. The concept forbids that. One chosen question is the difference. | Does not overlap. | A card is not Ask Photos, but the value proposition is similar: say more about the photo. |
| People, Places, albums | May use those facts as the content of a question. The person does not have to know to open that filter. | "Right people, wrong moment" is a judgment, not the People filter. | Who/where fields recreate those filters in a form. |
| Chronological browsing | A time question is not the timeline. INT005 should never be pushed out of chronological browsing into a question. | Not the timeline. | A "roughly when" field can feed a time filter. That is close to what INT005 already did successfully, without a card. |

A concept is weak if its only value is "describe the photo conversationally." C is the closest to that weakness. A is weak if it is built as open chat. B is not that weakness.

## Selected MVP direction

**Concept A, Next useful question.** One closed clarification after a coarse first retrieval, chosen to split the current candidate set. Not an open chatbot.

### Why this mechanism

The corrected root cause has two parts: memory is richer than the first action, and the journey does not help convert the rest into a narrowing signal. The four friction interviews already did the conversion by hand, after seeing a bad set, and then still scrolled for about 3 to 10 minutes.

- INT001 added a friend's name after "birthday."
- INT002 added a sister's name after "wedding."
- INT003 added a team name after "football."
- INT004 added a month after the Screenshots folder.

Concept A supports that observed second step and tries to make the clue a separating one. Concept C moves the same idea to before the search, which is not when these four people introduced the extra clue, and it adds a step INT005 did not need. Concept B is the right mechanism when the set is already the right neighbourhood and the problem is recognition (INT004, DV007). It does not elicit a red wall or a year that is not on screen, and it fails closed if the first retrieval missed the photo. B stays a plausible later complement, not this MVP.

A is also buildable as a functional prototype on a fixed library with one question. That feasibility matters. It is not the reason for the choice. C would be easier to build and is not selected.

### What behaviour should change

On an incomplete-memory attempt, the person answers one relevant question and reaches a set small enough to recognise, instead of scrolling a broad list. Time to target and attempts should drop relative to the coarse-search baseline. Scrolling as a fallback should become unnecessary when the question actually splits the set.

### What existing flow it improves

The gap after a coarse query and before timeline scrolling. It does not replace search, People, Places, albums, or year/month browsing.

### What must be true

The first retrieval includes the target often enough to be worth refining. The chosen question is one the person can answer. The answer removes wrong photos rather than only rephrasing the same wide set. People who already have a precise anchor are left on their current path.

### What we are not building

- An open-ended chat with the photo library, or another Ask Photos.
- Concept B's cluster browser, and Concept C's pre-search form, in this MVP.
- A new way to browse by year when the year is already known.
- Automatic claims about Google's current ranking.
- A population estimate from Corpus B or from the 15-person survey.
- Feature-adoption as the success measure.
