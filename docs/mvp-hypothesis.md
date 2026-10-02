# MVP hypothesis

Step 13. The prototype is not built. The direction is Concept A from `docs/solution-exploration.md`: one closed question after a coarse retrieval, chosen to split the current candidate set.

Corpus B is preliminary (9 of 18) and is not a test baseline. The baseline is the behaviour already observed: coarse search or folder browsing, then a self-chosen second clue, then scrolling.

## Hypothesis

For users trying to retrieve one specific photo from an incomplete memory, if we ask one clarification chosen to split the current candidate set and then refresh that set, then more of those attempts should reach the intended photo without prolonged manual browsing, because the four observed friction tasks already depended on a second clue the person had to invent, and that second clue still left them scanning a wide set for about 3 to 10 minutes.

## What the prototype lets a person do

1. Start from an incomplete memory with a coarse handle, as in the interviews ("birthday", "wedding", "football", a screenshot category).
2. See an initial candidate set.
3. Answer one closed question about a detail they may remember.
4. See the set update.
5. Identify the target, or see that the question did not separate the set.

The question is generated from differences in the current set. The person does not get an empty chat box. A second question is out of the first test unless the first answer clearly shrinks the set and a second split is obvious. That limit is deliberate: survey respondents said they did not know how to refine (9 of 15), and several vague questions would recreate the effort the outcome is meant to remove.

## Baseline

Same person, same target photo, same library.

**Baseline path.** Coarse search or category browsing, then whatever they would normally do next, including scrolling. This is the path INT001–INT004 took: one broad action, a self-chosen refinement, then manual scrolling. INT005's year/month path is recorded if it occurs and is not scored as a failure of the MVP. If someone begins with a precise anchor and finds the photo immediately, the trial is a boundary case, not evidence against the hypothesis.

**MVP path.** The same coarse start, then the single clarification, then recognition on the updated set. Scrolling is still allowed and is counted if they need it.

Order: baseline first, then MVP, on two different target photos, so the MVP does not teach the baseline. With only three people this does not remove order effects. It is noted, not "controlled."

## Measures

Primary, because it is the product outcome in behavioural form:

**The target is reached without a manual-scrolling fallback.**

Yes or no on each attempt. "Prolonged" in the outcome statement is operationalised from the interviews: scrolling used to hunt through a set that the first actions did not isolate. INT005's intentional year/month scrolling is not this fallback. With three people the result is a count, not a percentage to generalise.

Secondary:

| Measure | Why it is secondary |
|---|---|
| Time to target | Friction tasks were about 3, 4, 5 and 10 minutes. INT005 was about 2. Times in the research were approximate; the test should use a clock. |
| Interactions until the target is identified | Baseline attempts were 2 or 3 on the friction tasks and 1 on INT005. Count queries, the clarification answer, and scrolling bursts. |
| Whether the clarification reduced ambiguity | Did the updated set drop photos that lacked the answered attribute, and did the person say the question was something they could answer? A shorter list that still feels random is not a reduction. |
| Perceived usefulness of that question | One question after the attempt: did it help, hinder, or make no difference? Not a satisfaction score for the product. |

Not used: feature adoption, clicks on the control for its own sake, or a 1–10 preference score.

## Test with three users

Three people, each with a real "one specific past photo" they cannot start from a precise date, filename, or exact place. A prepared library is acceptable only if it contains that photo plus enough neighbours to make a coarse query genuinely wide (other birthdays, other weddings, other screenshots). A library of five unrelated images cannot test narrowing.

For each person, two tasks:

1. Baseline on target A.
2. MVP on target B.

Stop a task at identification, at give-up, or at a pre-set cap of 10 minutes, which is the longest observed friction time (INT002). Record give-up explicitly. Two survey respondents gave up; a test that only logs success will hide that.

After both tasks, ask only:

- Could you answer the question from memory?
- Did the set get easier to scan?
- Did any photo on screen change what you thought you remembered?

The third question is there to catch contamination, which is a risk in `docs/mvp-risk-register.md`.

Pass for continuing to build past this test: on at least two of the three MVP tasks, the target was in the initial set, the person could answer the question, and they either found the photo without scrolling or the set visibly dropped non-matching photos. One of three is treated as inconclusive, not as a win. This is a build gate for a student prototype, not a statistical test.

## What the MVP will not include

- Open chat, follow-up small talk, or a general "ask anything" box.
- Cluster browsing (Concept B) and the pre-search clue card (Concept C).
- A prompt when the opening action is already a specific year or other precise anchor.
- More than one clarification in the first test build, except a manual second round if the first round is being debugged.
- Any claim that the prototype reproduces Google Photos ranking.
- Corpus B rows as the photo library. Those texts are paraphrased public reports, not a user's photos.
