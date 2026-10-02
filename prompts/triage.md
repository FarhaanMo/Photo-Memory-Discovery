Classify ONLY relevance_level for each record. This is triage, not full extraction.

Do not invent facts. Classify from semantic meaning of the given text, which may be a paraphrase. Literal phrases such as "don't remember" are not required.

Do not extract photo_type, remembered clues, forgotten information, failure_stage, workaround, outcome, or problem theme.

Allowed relevance_level values:

direct_vague_retrieval
Evidence that the user knows or believes a target photo/image exists AND retrieval begins with incomplete, uncertain, approximate, contextual, or fuzzy memory about searchable attributes (date, place, name, object, text, event, sequence, purpose, weak contextual clues, or having to browse because they cannot formulate a precise search).

retrieval_adjacent
Genuinely about finding/retrieving an existing visual item, but incomplete memory is not clearly part of the problem (exact query/date/object/text fails; too few results; poor AI search; ordering; precise attributes but system fails). Prefer this over direct_vague_retrieval when incomplete memory is uncertain.

irrelevant
Not meaningfully about retrieving a particular existing photo/image (backup, storage, sync, billing, editing, crashes, general UI/settings, switching search modes without a concrete retrieval task, account recovery, missing/deleted content as data loss). Prefer irrelevant when there is no concrete retrieval task.

Edge rules:
- "after" or "before" alone does not indicate vague memory.
- UI/navigation without a real retrieval task is irrelevant.
- A failed exact search is retrieval_adjacent, not direct_vague_retrieval.
- Missing/deleted content is normally not vague-memory retrieval.

triage_reason: one short sentence using evidence from the text.
triage_confidence: high | medium | low

Return JSON:
{
  "items": [
    {
      "record_id": "must match an input id",
      "relevance_level": "direct_vague_retrieval | retrieval_adjacent | irrelevant",
      "triage_reason": "one sentence",
      "triage_confidence": "high | medium | low"
    }
  ]
}

Return exactly one item per input record.
