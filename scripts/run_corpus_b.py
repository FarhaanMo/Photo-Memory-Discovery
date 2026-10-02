"""Resumable Corpus B run: extractor -> auditor -> sanitizer -> gates.

Order: finish DV001-DV010, gate them, and only then process DV011-DV018.
On a Groq rate limit, wait the server-stated retry time once, then retry;
a second consecutive rate limit stops the run. Rows are saved one at a time.
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import TARGETED_CSV_PATH, TARGETED_PROCESSED_CSV_PATH  # noqa: E402
from src.ingest import load_targeted_csv  # noqa: E402
from src.persist import load_processed  # noqa: E402
from src.pipeline import run_first_n  # noqa: E402
from src.quality_checks import run_quality_checks  # noqa: E402

CALIBRATION_IDS = ["DV%03d" % i for i in range(1, 11)]
REST_IDS = ["DV%03d" % i for i in range(11, 19)]


def _wait_seconds(message):
    match = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", message or "")
    if not match:
        return None
    return int(match.group(1) or 0) * 60 + float(match.group(2)) + 15


def _quota_summary(message):
    match = re.search(r"Used \d+, Requested \d+\. Please try again in [\w.]+", message or "")
    return match.group(0) if match else (message or "")[:160]


def process(df, ids):
    """Process ids not yet successful. Returns None, or the quota error on stop."""
    subset = df[df["record_id"].isin(ids)]
    waited = False
    while True:
        summary = run_first_n(
            subset, len(subset), processed_path=TARGETED_PROCESSED_CSV_PATH,
            targeted=True, retry_errors=True,
            progress_cb=lambda d, t, r, s: print(s, r, flush=True) if s != "running" else None,
        )
        halt = summary["halt_message"]
        if not halt:
            return None
        wait = _wait_seconds(halt)
        if waited or wait is None:
            return _quota_summary(halt)
        print("rate limited; waiting {:.0f}s".format(wait), flush=True)
        time.sleep(wait)
        waited = True


def print_gates(frame, label):
    failures = run_quality_checks(frame)
    print("GATES {}: {}".format(label, {k: len(v) for k, v in failures.items()}), flush=True)
    for gate, items in failures.items():
        for rid, field, value, reason in items:
            print("  FAIL {} | {} | {} | {} | {}".format(gate, rid, field, value, reason), flush=True)
    return failures


def main():
    df = load_targeted_csv(TARGETED_CSV_PATH)
    stop = process(df, CALIBRATION_IDS)
    if stop:
        print("STOPPED (quota): " + stop)
        return
    processed = load_processed(TARGETED_PROCESSED_CSV_PATH)
    calib = processed[processed["record_id"].isin(CALIBRATION_IDS)]
    failures = print_gates(calib, "DV001-DV010")
    needs_review = calib[calib["processing_status"] == "needs_review"]["record_id"].tolist()
    if any(failures.values()) or needs_review or len(calib) != 10:
        print("STOPPED: DV001-DV010 failed hard gates; DV011-DV018 not processed. needs_review={}".format(needs_review))
        return
    stop = process(df, REST_IDS)
    if stop:
        print("STOPPED (quota) during DV011-DV018: " + stop)
    print_gates(load_processed(TARGETED_PROCESSED_CSV_PATH), "all rows")
    print("DONE")


if __name__ == "__main__":
    main()
