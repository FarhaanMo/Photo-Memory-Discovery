Use only the provided raw_text. Do not invent facts. Do not recommend a product. Do not write statistics.

You assign a retrieval-research relevance_level. Do NOT assume fuzzy memory just because search is mentioned. When uncertain, prefer retrieval_adjacent or irrelevant, never direct_vague_retrieval.

relevance_level allowed values:

direct_vague_retrieval
The user knows or believes a particular photo/image exists, but begins retrieval with incomplete, uncertain or fuzzy memory about one or more searchable details (date, location, name, object, text, event, context, etc.).
Examples: remembers the event but not the date; remembers why it was taken but not what to search; remembers a rough place but not the venue; remembers visual/contextual clues but not precise searchable attributes.

retrieval_adjacent
The record concerns retrieving/searching photos, but incomplete memory is not clearly part of the problem.
Examples: user knows the exact date but search returns wrong results; visible text search fails despite knowing the text; an exact object query returns irrelevant results; generic search-quality complaints without evidence of fuzzy memory.

irrelevant
No meaningful evidence about retrieving an existing visual item.
Examples: settings/navigation issues; backup; storage; sync; editing; crashes; billing; general UI complaints; inability to find a setting or switch search modes without a target image.

Also set relevant_to_retrieval for compatibility:
- direct_vague_retrieval -> true
- retrieval_adjacent -> true
- irrelevant -> false

Return JSON only:

{
  "record_id": "must match the given record_id",
  "relevance_level": "direct_vague_retrieval | retrieval_adjacent | irrelevant",
  "relevant_to_retrieval": true,
  "relevance_reason": "short reason grounded in the text, or unknown",
  "relevance_confidence": "high | medium | low | unclear"
}
