# MVP risk register

Step 13. Applies to the selected direction only: one closed question chosen to split the current candidate set, after a coarse first retrieval. See `docs/mvp-hypothesis.md`. These are risks to check before and during the three-person test. They are not a backlog of features.

Corpus B (9 of 18, preliminary) is not evidence that any mitigation works.

## Why the mechanism is more than a wrapper

A general model can ask "what else do you remember?" That question does not depend on the photos. The selected mechanism does. The next question is worth asking only if it separates photos that are actually in this set.

Inside Google Photos that choice could draw on context a generic chatbot does not hold across a private library:

- the person's own images, not a public corpus
- visual similarity among the current candidates
- who recurs in them
- time clusters
- place or other context already attached to items
- which candidates are near-duplicates versus different events
- what this person already answered on this attempt

The research does not show that Google Photos ranks or asks questions this way today. The claim is narrower: a next-question policy that uses those personal signals would be stronger inside the library than the same chat prompt pointed at photos the model cannot organise. The prototype can only imitate a slice of this, on a fixed library, and should be described that way.

INT005 is the boundary. If the first action is already a strong time anchor, there is no wide set to split. Asking a question then is cost without a job. The MVP should not intervene on that path.

## Risks

### 1. The question asks for something the person does not remember

**Risk.** The split that most cleanly divides the set may be an exact date, a filename, or a detail they never stored. Survey: 6 of 15 could not remember when or where. Corpus B, preliminary: date/time was the explicit gap in 5 of 9. A perfect split on the forgotten attribute is a useless question.

**How we would detect it.** In the three-person test they say they cannot answer, or they guess. The set update is then noise.

**MVP mitigation.** Prefer questions about attributes they have already hinted at, or about coarse visual and event contrasts (indoor or outdoor, before or after a remembered year, a person they named). Do not ask for an exact date. If they skip, leave the set unchanged and count the question as a failed split.

### 2. The question does not discriminate

**Risk.** They can answer, and almost every candidate still matches. "Was it a photo?" after a photo search. The second clues in the interviews sometimes failed this way too: a name or a month still left a scan of about 3 to 10 minutes.

**How we would detect it.** The updated set drops few photos, or the remaining photos do not share the answered attribute. Ask them whether the list felt easier.

**MVP mitigation.** Before showing a question, require that both answers would keep a non-trivial share of the set and drop another share. If no question meets that bar, do not ask. Show the current set and allow scrolling. Record "no discriminating question" as an outcome, not as a successful interaction.

### 3. Wrong candidates change what the person thinks they remember

**Risk.** A plausible wrong photo supplies a detail they then "remember." Later answers chase that contamination. The interviews did not measure this. All five have `new_memory_triggered_by_results = unknown`.

**How we would detect it.** The debrief question: did any photo change what you thought you remembered? Also a switch in their description after seeing candidates, toward a detail that is only true of a shown non-target.

**MVP mitigation.** Keep the first candidate list short and labelled as possibilities, not as "your photo." Do not assert "this is the one." In the test, note contamination if it appears. Do not add a memory-editing feature to prevent it in this build.

### 4. Too many clarification steps

**Risk.** A chain of weak questions recreates the "didn't know how to refine" cost (9 of 15) as a wizard. The outcome is fewer minutes of browsing, not more taps.

**How we would detect it.** More than one question on a task, or they abandon during the questions. Time to target higher than their baseline.

**MVP mitigation.** The first test build asks once. A second question is allowed only when the first answer removed a visible part of the set and the stop rule still says the remainder is wide. Cap at two. Then stop and let them scan.

### 5. The set narrows away from the correct photo

**Risk.** They misremember a detail, or the attribute on the photo is wrong, and the true photo is filtered out. Later steps cannot recover it.

**How we would detect it.** The target was in the initial set and is absent after the answer. They cannot find it without widening again.

**MVP mitigation.** Filter only when the attribute is reliably present on the candidates. Otherwise rerank, leaving the target reachable. Always offer "show the previous set." Count a lost target as a failed attempt even if they later scroll to it in the old set.

### 6. Inferred context feels invasive

**Risk.** A question that reveals an inference they did not offer ("was this at your mother's house?") uses private context they did not expect a search box to surface. None of the five interviews tested comfort with inferred questions.

**How we would detect it.** They hesitate, refuse the question, or say it used something they had not mentioned. Ask once in the debrief if anything felt too inferred.

**MVP mitigation.** Questions may use an attribute they already stated, or a coarse visual contrast visible in the candidates. They may not use a named place, relationship, or event the person has not mentioned. No question text that states a sensitive inference as fact.

### 7. The model confidently misreads the memory

**Risk.** "Red wall" becomes a hard filter on the wrong colour. "Football" becomes every sport. The explanation sounds sure. The four friction interviews show people are already unsure how to phrase memory. An overconfident interpretation makes that worse.

**How we would detect it.** The question or the filter cites a detail that does not match what they said. They correct it immediately.

**MVP mitigation.** Show the interpretation in the question itself ("Keeping photos that look indoors") so a wrong reading is visible before the set changes. Apply the update only after they answer. Do not silently rewrite their opening query.

### 8. The correct photo is not in the initial set

**Risk.** Every later question rearranges a set that cannot succeed. INT001's first results were largely unrelated birthday photos. DV005, preliminary, never surfaced the phrase-search target. Recognition and clarification cannot recover a photo the first retrieval missed.

**How we would detect it.** Mark, before the session, whether the target is inside the initial candidate list. If it is absent, the clarification trial is invalid as a test of narrowing. Do not count it as evidence that questions fail.

**MVP mitigation.** Log membership of the target in the initial set as a separate result. If it is missing, stop the question flow and record a retrieval miss. Do not paper over that with more questions. Widening the first retrieval is a later problem, not this MVP.

## Top risks for the build gate

If the three-person test hits these, do not add scope. Revisit the mechanism.

1. Target absent from the initial set (risk 8).
2. Question the person cannot answer (risk 1).
3. Answer does not shrink the set (risk 2).
4. Update drops the true photo (risk 5).
5. Shown photos alter the memory (risk 3).
