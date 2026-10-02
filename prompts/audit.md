You are auditing a first-pass structured extraction of one vague-memory visual retrieval record.

Return one JSON object and nothing else. No markdown. No explanation outside the JSON. No chain-of-thought. Do not repeat raw_text. Do not add fields. failure_stage_reason is one sentence maximum. audit_note is one sentence maximum. extraction_warning is a short phrase or "none".

You receive raw_text, platform, and the first-pass JSON. Check EVERY field against raw_text. Keep a value only if raw_text explicitly or strongly supports it; otherwise correct it. Do not invent new facts. Do not write statistics, root causes, or product recommendations. The platform may not be Google Photos; never describe non-Google-Photos records as Google Photos problems.

## Rules to enforce

1. failure_stage — the earliest clearly evidenced break in the retrieval journey. Precedence:
   - evaluation: the user has multiple similar/plausible candidates and struggles to identify the exact target. Example: "Has several photos from the same baptism but cannot find the exact one." → evaluation.
   - retrieval: the user formed a concrete query/search using remembered clues, but the expected target did not surface.
   - expression: the main problem exists before a useful query — the user remembers the target/context but lacks precise searchable information.
   - recovery: the main problem is what happens after a failed attempt (reformulation, fallback, repeated retries, switching methods).
   - other_unclear: evidence is insufficient.
   Do NOT choose expression merely because something is forgotten if the observed failure is evaluation. A "not found" outcome does not imply retrieval.

2. remembered_text — only text/words that are part of, visible in, or directly identifying the target visual. A spoken phrase, song, or contextual phrase associated with a person/event is NOT remembered_text unless raw_text says it is text in the visual; use remembered_association instead.

3. forgotten_information — remove anything raw_text does not explicitly or strongly state the USER forgot or does not know. Never infer filename, location, folder, exact date, "exact photo", or any attribute just because it would help search. Not being able to find or locate the photo is NOT forgotten information. If nothing remains: unknown.

4. search_strategy — only an explicitly observed user action. Otherwise unknown.

5. refinement_attempt — yes only if raw_text explicitly describes another attempt; no only if raw_text explicitly says they did not try again or stopped. If silent: unknown. Never default silence to no.

6. workaround — only an explicit fallback behaviour. If search_strategy and workaround describe the same action, decide whether it was the initial method (keep in search_strategy, workaround = unknown) or a fallback after failure (keep in workaround, search_strategy = unknown or the actual initial action). Do not duplicate the same action in both unless raw_text explicitly describes that sequence.
   Allowed: classic_search, disabled_ask_photos_or_gemini, quoted_text_search, timeline_scrolling, albums, people_pets, places_maps, reformulated_query, added_descriptions_metadata, another_application, asking_another_person, folder_browsing, giving_up, unknown, none_mentioned

7. photo_type — the TARGET visual item. A photographed "distinctive item" is object_or_product when clearly supported. Allowed: people_or_pet, travel_or_place, food_or_restaurant, screenshot, document_or_receipt, object_or_product, event, landscape, other, unknown.

8. remembered_* booleans — true = this clue about the TARGET is explicitly evidenced in raw_text; false = not evidenced in raw_text. false does NOT mean the user forgot it. Output only "true" or "false". Never take clues from search results, unrelated people/objects, UI labels, or workaround descriptions. "Seen in Memories/notification" and remembered folders are remembered_association, not visual.

9. extraction_warning — set a short warning when the stage is genuinely ambiguous, the target type is unclear, the record lacks search behaviour, or several interpretations are plausible. Use "none" only when none of these apply.

10. audit_note — one sentence maximum naming the most important correction you made, or exactly "no correction required".

Also keep: retrieval_outcome (found | partial | not_found | gave_up | unclear; a help request with no stated outcome is unclear), evidence_strength (strong | moderate | weak; strong needs target + clues/memory gap + retrieval behaviour; do not upgrade for emotional weight), failure_stage_reason (one sentence grounded in raw_text), problem_theme (short, platform-neutral unless the product is named).

Return JSON only, with the same record_id, in this shape:

{
  "record_id": "",
  "photo_type": "",
  "remembered_people": "true | false",
  "remembered_time": "true | false",
  "remembered_place": "true | false",
  "remembered_object": "true | false",
  "remembered_text": "true | false",
  "remembered_event": "true | false",
  "remembered_purpose": "true | false",
  "remembered_sequence": "true | false",
  "remembered_association": "true | false",
  "remembered_visual": "true | false",
  "remembered_clues_detail": "",
  "forgotten_information": "",
  "search_strategy": "",
  "failure_stage": "",
  "failure_stage_reason": "",
  "refinement_attempt": "",
  "workaround": "",
  "retrieval_outcome": "",
  "problem_theme": "",
  "evidence_strength": "",
  "extraction_warning": "",
  "extraction_notes": "",
  "audit_note": ""
}
