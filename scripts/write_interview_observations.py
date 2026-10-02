"""Write the three researcher-conducted interviews to data/interview_observations.csv.

Values are exactly as recorded by the researcher. Unsupported fields are "unknown".
If the file already has rows, only missing participant_ids are appended.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics_interviews import INTERVIEW_COLUMNS  # noqa: E402
from src.config import INTERVIEW_CSV_PATH  # noqa: E402

ROWS = [
    {
        "participant_id": "INT001",
        "participant_name": "Nikhil",
        "target_description": "Photo with school friends at a restaurant",
        "remembered_before_retrieval": "friends; approximately 2021; restaurant context; birthday; red wall",
        "observed_sequence": "1. searched \"birthday\" | 2. results contained many unrelated birthday photos | "
                             "3. refined by searching a friend's name | 4. manually scrolled | 5. eventually found the target",
        "remembered_people": "true",
        "remembered_time": "true",
        "remembered_place": "true",
        "remembered_object": "false",
        "remembered_text": "false",
        "remembered_event": "true",
        "remembered_purpose": "false",
        "remembered_sequence": "false",
        "remembered_association": "false",
        "remembered_visual": "true",
        "first_observed_action": "search",
        "first_query": "birthday",
        "first_result_quality": "broad / largely irrelevant",
        "new_memory_triggered_by_results": "unknown",
        "refinement_attempted": "yes",
        "refinement_description": "searched friend's name",
        "fallback_or_workaround": "timeline_scrolling",
        "manual_scrolling": "yes",
        "failure_stage_observed": "expression",
        "failure_stage_reason": "The user possessed multiple contextual and visual memories but struggled to "
                                "translate them into a sufficiently discriminating query.",
        "retrieval_outcome": "found",
        "time_to_target_minutes": "4",
        "time_is_approximate": "true",
        "attempts_to_target": "3",
        "hardest_moment_quote": "I knew what the photo looked like but didn't know what to type",
        "researcher_observation": "User began with a broad event query despite remembering richer contextual and "
                                  "visual clues. After noisy results, he refined using a friend's name and "
                                  "eventually fell back to scrolling.",
    },
    {
        "participant_id": "INT002",
        "participant_name": "Raja",
        "target_description": "Specific family photo from his sister's wedding",
        "remembered_before_retrieval": "family; sister; 2018; sister's wedding",
        "observed_sequence": "1. searched \"wedding\" | 2. results contained many unrelated wedding cards, screenshots "
                             "and other wedding-related content | 3. refined using sister's name | "
                             "4. manually scrolled | 5. eventually found the target",
        "remembered_people": "true",
        "remembered_time": "true",
        "remembered_place": "false",
        "remembered_object": "false",
        "remembered_text": "false",
        "remembered_event": "true",
        "remembered_purpose": "false",
        "remembered_sequence": "false",
        "remembered_association": "false",
        "remembered_visual": "false",
        "first_observed_action": "search",
        "first_query": "wedding",
        "first_result_quality": "noisy / mixed with irrelevant wedding-related content",
        "new_memory_triggered_by_results": "unknown",
        "refinement_attempted": "yes",
        "refinement_description": "searched sister's name",
        "fallback_or_workaround": "timeline_scrolling",
        "manual_scrolling": "yes",
        "failure_stage_observed": "retrieval",
        "failure_stage_reason": "The user provided a meaningful event query, but the returned set was noisy and did "
                                "not efficiently surface the specific target.",
        "retrieval_outcome": "found",
        "time_to_target_minutes": "10",
        "time_is_approximate": "true",
        "attempts_to_target": "3",
        "hardest_moment_quote": "I remember when the photo was taken but there were a lot of photos taken so it "
                                "was hard to find this exact one",
        "researcher_observation": "Initial search produced broad wedding-related content including cards and "
                                  "screenshots. Even with remembered time and event context, locating the exact "
                                  "target required further refinement and manual browsing. The user's final comment "
                                  "also indicates later evaluation difficulty among many photos from the same event.",
    },
    {
        "participant_id": "INT003",
        "participant_name": "Pranav",
        "target_description": "Photo from a football team match",
        "remembered_before_retrieval": "football fixture / match context; football team; knew approximately what "
                                       "the target photo looked like",
        "observed_sequence": "1. searched \"football\" | 2. results contained many football-related images because "
                             "the participant has many football photos | 3. refined using his football team's name | "
                             "4. manually scrolled | 5. eventually found the target",
        "remembered_people": "false",
        "remembered_time": "false",
        "remembered_place": "false",
        "remembered_object": "false",
        "remembered_text": "false",
        "remembered_event": "true",
        "remembered_purpose": "false",
        "remembered_sequence": "false",
        "remembered_association": "true",
        "remembered_visual": "true",
        "first_observed_action": "search",
        "first_query": "football",
        "first_result_quality": "relevant but too broad / too many similar candidates",
        "new_memory_triggered_by_results": "unknown",
        "refinement_attempted": "yes",
        "refinement_description": "searched football team name",
        "fallback_or_workaround": "timeline_scrolling",
        "manual_scrolling": "yes",
        "failure_stage_observed": "expression",
        "failure_stage_reason": "The user knew the target context and appearance but initially could not formulate "
                                "a query specific enough to distinguish it from many other football photos.",
        "retrieval_outcome": "found",
        "time_to_target_minutes": "3",
        "time_is_approximate": "true",
        "attempts_to_target": "3",
        "hardest_moment_quote": "I knew what the photo looked like but didn't know what to type as I have many "
                                "football pics as I am a football fan",
        "researcher_observation": "User's first query represented the broad category rather than the distinctive "
                                  "memory. The result set contained many plausible football photos, creating "
                                  "additional evaluation effort before refinement and scrolling.",
    },
    {
        "participant_id": "INT004",
        "participant_name": "Meeth",
        "target_description": "Screenshot containing sales targets",
        "remembered_before_retrieval": "it was a screenshot; approximate month/time context was remembered later during refinement",
        "observed_sequence": "1. opened / checked the Screenshots folder | 2. found a very large number of screenshots | "
                             "3. could not identify the exact target | 4. refined by using the month he believed the "
                             "screenshot was from | 5. eventually found the target",
        "remembered_people": "false",
        "remembered_time": "true",
        "remembered_place": "false",
        "remembered_object": "false",
        "remembered_text": "false",
        "remembered_event": "false",
        "remembered_purpose": "false",
        "remembered_sequence": "false",
        "remembered_association": "true",
        "remembered_visual": "false",
        "first_observed_action": "folder_browsing",
        "first_query": "unknown",
        "first_result_quality": "relevant category but too many similar candidates",
        "new_memory_triggered_by_results": "unknown",
        "refinement_attempted": "yes",
        "refinement_description": "narrowed using the month associated with the screenshot",
        "fallback_or_workaround": "time_based_narrowing",
        "manual_scrolling": "yes",
        "failure_stage_observed": "evaluation",
        "failure_stage_reason": "The participant reached the correct screenshot category, but the large number of "
                                "plausible candidates made identifying the exact screenshot difficult.",
        "retrieval_outcome": "found",
        "time_to_target_minutes": "5",
        "time_is_approximate": "true",
        "attempts_to_target": "2",
        "hardest_moment_quote": "I remember when the screenshot was taken but there were a lot of photos taken so it "
                                "was hard to find this exact one",
        "researcher_observation": "The participant knew the target was a screenshot and entered the correct category, "
                                  "but category-level retrieval still produced too many plausible candidates. He "
                                  "eventually narrowed the search using remembered temporal context.",
    },
    {
        "participant_id": "INT005",
        "participant_name": "Mahesh",
        "target_description": "Graduation photo",
        "remembered_before_retrieval": "2022; graduation event; the photo was personally memorable",
        "observed_sequence": "1. navigated using the year | 2. used year/month chronological browsing | "
                             "3. found the target photo | 4. afterwards saved it to Favourites",
        "remembered_people": "unknown",
        "remembered_time": "true",
        "remembered_place": "false",
        "remembered_object": "false",
        "remembered_text": "false",
        "remembered_event": "true",
        "remembered_purpose": "false",
        "remembered_sequence": "false",
        "remembered_association": "false",
        "remembered_visual": "unknown",
        "first_observed_action": "chronological_browsing",
        "first_query": "unknown",
        "first_result_quality": "effective",
        "new_memory_triggered_by_results": "unknown",
        "refinement_attempted": "no",
        "refinement_description": "none",
        "fallback_or_workaround": "none",
        "manual_scrolling": "yes",
        "failure_stage_observed": "no_failure",
        "failure_stage_reason": "The participant remembered useful temporal and event context, navigated directly "
                                "using year/month, and found the target in approximately two minutes without needing "
                                "a failed query or recovery attempt.",
        "retrieval_outcome": "found",
        "time_to_target_minutes": "2",
        "time_is_approximate": "true",
        "attempts_to_target": "1",
        "hardest_moment_quote": "I remember this photo and was easy to find as it hold many memories, i just used by "
                                "year and month to scroll and found it , was easy",
        "researcher_observation": "Manual scrolling was the participant's intended retrieval method, not a fallback "
                                  "after failure.",
    },
]


def main():
    """Append missing participants. Existing rows are never rewritten."""
    import csv

    path = INTERVIEW_CSV_PATH
    existing_ids = set()
    if path.is_file() and path.stat().st_size > 0:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            existing_ids = {row["participant_id"] for row in csv.DictReader(handle)}
        mode = "a"
        write_header = False
    else:
        mode = "w"
        write_header = True
    added = [row for row in ROWS if row["participant_id"] not in existing_ids]
    with path.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INTERVIEW_COLUMNS, lineterminator="\n")
        if write_header:
            writer.writeheader()
        writer.writerows(added)
    print("appended {} row(s); left {} existing id(s) untouched".format(len(added), len(existing_ids)))


if __name__ == "__main__":
    main()
