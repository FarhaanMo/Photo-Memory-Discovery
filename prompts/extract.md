Use only the provided raw_text. If a detail is not explicitly present, do not invent it. Do not write statistics or product recommendations. Preserve ambiguity instead of forcing a category.

Return one JSON object and nothing else. No markdown. No explanation outside the JSON. No chain-of-thought. Do not repeat raw_text in any field. Do not add fields. failure_stage_reason is one sentence maximum. extraction_warning is a short phrase or "none". extraction_notes is a short phrase or "unknown". List and text fields contain only concise supported values.

The platform field says where the retrieval happened (for example Google Photos, iOS Photos, a screenshot library, a personal archive). Do not describe non-Google-Photos records as Google Photos problems; keep problem_theme and search_strategy platform-neutral unless the text names the product.

## failure_stage — the FIRST observed break in the journey

failure_stage is the EARLIEST clearly evidenced point where retrieval breaks. A final outcome of "not found" does NOT imply retrieval. Apply this decision order:

- expression: the user has memory of the target but lacks precise searchable information, or cannot translate what they remember into an effective query. Evidence: remembers a scene but not date/folder/name; remembers a person/object but not when; has contextual details but no searchable attributes; resorts to broad browsing because they cannot formulate a precise search; incomplete memory is described before any concrete query. Example: "I remember the scene but not the date or folder." → expression.
- retrieval: ONLY when the text explicitly shows the user formed a usable/concrete query or supplied useful clues, and the system failed to return the expected target. Example: "I searched the remembered phrase but it did not find the photo." → retrieval.
- evaluation: plausible or similar candidates are available but the user cannot identify the exact target (many similar photos, several photos from the same event, target may be present but hard to distinguish). Example: "I found many photos from the baptism but cannot identify the exact one." → evaluation.
- recovery: ONLY when the text focuses on what happens AFTER a failed first attempt (repeated reformulation, switching tools after failure, falling back to manual scrolling, not knowing how to improve an unsuccessful attempt) and that is the dominant problem. A workaround existing is not enough.
- other_unclear: not enough behavioural evidence to identify the first failure stage confidently.

failure_stage_reason: one sentence maximum, naming the evidence for the chosen stage. Do not quote a long passage.

## Remembered clues (about the TARGET item only)

Mark a clue "true" only when raw_text explicitly or strongly states that the USER remembers that information about the TARGET visual item. Never infer a clue because it would be useful. Never take clues from returned search results, unrelated objects or people, UI labels, or workaround descriptions. Use "false" only when the text says the user does NOT remember that information. Otherwise "unknown".

- remembered_people: explicit remembered people/pets in the target.
- remembered_time: a remembered temporal clue ("around 2018", "a few years ago", "when daughter was little", "roughly ten years earlier"). If the user explicitly does not remember when, use false.
- remembered_place: an explicitly remembered place/location.
- remembered_object: an explicitly remembered target object/product.
- remembered_text: text that appeared in or identifies the target item. Spoken phrases, conversation context, or things somebody said are NOT text unless the source says the text is in the target visual.
- remembered_event: explicit event/occasion (baptism, wedding, birthday, holiday).
- remembered_purpose: why the user took/saved the image, only if explicitly stated.
- remembered_sequence: explicit before/after ordering around the target memory.
- remembered_association: contextual associations that fit no other type: a remembered folder/album, a remembered notification or Memories surface, sending/showing the image to someone, the source/conversation where the image appeared, an associated spoken phrase or song.
- remembered_visual: actual visual characteristics of the target (colour, clothing, background, scene, appearance, composition, visual style). "Seen in Memories" is association, not visual.

remembered_clues_detail: short text from the source naming the remembered clues, or unknown.

## forgotten_information

Only information the user explicitly or strongly indicates they do not remember or do not know. Never infer a missing attribute because it would help retrieval. Never describe search-engine behaviour, bad results, app errors, or system limitations. Valid values include: date/time, exact date, folder, album, location, source, notification type, filename, title/name, exact wording. If the text does not explicitly identify what is forgotten, return unknown.

Example: "I remember a phrase from my daughter singing but cannot find the photo." → do NOT invent forgotten location, filename, or exact date. Return unknown.

## search_strategy

Only an action explicitly described in raw_text (e.g. searched remembered phrase, browsed timeline, checked notification/memory surface, searched by object, manual scrolling). Never output placeholders such as "initial attempt", "search attempt", or "Photos memories search". If no search action is described, return unknown.

## refinement_attempt: yes | no | unknown

yes only when the user explicitly tries another query/method after an initial attempt. no only when the text explicitly says they did not refine or stopped after the first attempt. If the text is silent: unknown. Never default silence to no.

## workaround

Only an explicit fallback behaviour after the initial attempt. Do not copy the initial strategy. If none is explicitly present, return unknown. Allowed values:
classic_search, disabled_ask_photos_or_gemini, quoted_text_search, timeline_scrolling (includes manual scrolling), albums, people_pets, places_maps, reformulated_query, added_descriptions_metadata, another_application (includes another device), asking_another_person, folder_browsing, giving_up, unknown, none_mentioned

## retrieval_outcome: found | partial | not_found | gave_up | unclear

Use only what the record supports. A help-seeking post with no stated eventual outcome is unclear, not not_found. When uncertain: unclear.

## photo_type (TARGET visual item only)

people_or_pet, travel_or_place, food_or_restaurant, screenshot, document_or_receipt, object_or_product, event, landscape, other, unknown

## evidence_strength: strong | moderate | weak

- strong: clearly describes the target, the remembered clues or memory gap, AND the retrieval behaviour.
- moderate: useful evidence but some behavioural details are missing.
- weak: only limited evidence can be extracted.
Do not upgrade evidence strength because a record sounds emotionally important.

## extraction_warning

A short note when important information is ambiguous or unavailable; otherwise "none".

Return JSON only:

{
  "record_id": "must match the given record_id",
  "photo_type": "enum above",
  "remembered_people": "true | false | unknown",
  "remembered_time": "true | false | unknown",
  "remembered_place": "true | false | unknown",
  "remembered_object": "true | false | unknown",
  "remembered_text": "true | false | unknown",
  "remembered_event": "true | false | unknown",
  "remembered_purpose": "true | false | unknown",
  "remembered_sequence": "true | false | unknown",
  "remembered_association": "true | false | unknown",
  "remembered_visual": "true | false | unknown",
  "remembered_clues_detail": "short text from the source, or unknown",
  "forgotten_information": "user-forgotten attributes only, or unknown",
  "search_strategy": "observed action, or unknown",
  "failure_stage": "expression | retrieval | evaluation | recovery | other_unclear",
  "failure_stage_reason": "one short sentence grounded in raw_text",
  "refinement_attempt": "yes | no | unknown",
  "workaround": "enum above",
  "retrieval_outcome": "found | partial | not_found | gave_up | unclear",
  "problem_theme": "short theme or unknown",
  "evidence_strength": "strong | moderate | weak",
  "extraction_warning": "short note, or none",
  "extraction_notes": "short phrase or unknown; do not repeat raw_text"
}
