from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

DEV_SAMPLE_CSV_PATH = DATA_DIR / "google_photos_retrieval_dev_sample.csv"
PRODUCTION_CSV_PATH = DATA_DIR / "google_photos_retrieval_raw.csv"
PROCESSED_CSV_PATH = DATA_DIR / "google_photos_retrieval_processed.csv"
TRIAGE_CSV_PATH = DATA_DIR / "google_photos_retrieval_triage_225.csv"
TARGETED_CSV_PATH = DATA_DIR / "google_photos_direct_vague_targeted.csv"
TARGETED_CALIBRATION_CSV_PATH = DATA_DIR / "google_photos_direct_vague_calibration_10.csv"
TARGETED_PROCESSED_CSV_PATH = DATA_DIR / "google_photos_direct_vague_processed_18.csv"
SURVEY_CSV_PATH = DATA_DIR / "survey_responses_raw.csv"
INTERVIEW_CSV_PATH = DATA_DIR / "interview_observations.csv"

GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_TEMPERATURE = 0.1
GROQ_TIMEOUT_SECONDS = 60
# Groq's documented default for max_completion_tokens is 1024. This call site
# previously omitted the parameter, so JSON mode stopped with
# "max completion tokens reached before generating a valid document".
# The model maximum is 65536. 4096 stays inside that limit and above a
# compact extraction, without reserving the full maximum against the token budget.
GROQ_STRUCTURED_MAX_COMPLETION_TOKENS = 4096
# gpt-oss default reasoning effort is medium, and those tokens count toward
# the completion budget. Extraction and audit must not chain-of-thought.
GROQ_STRUCTURED_REASONING_EFFORT = "low"
PROMPT_VERSION = "retrieval_classify_v4"
AUDIT_PROMPT_VERSION = "audit_v1"

TOP_K = 12
MIN_EVIDENCE = 3
MAX_CHARS_TO_LLM = 8000
MAX_CLASSIFY_N = 20
DEFAULT_CLASSIFY_N = 20
LLM_MAX_RETRIES = 3
JSON_REPAIR_ATTEMPTS = 1
TRIAGE_PROMPT_VERSION = "triage_v1"
TRIAGE_BATCH_SIZE = 8


def production_csv_candidates():
    return (
        PRODUCTION_CSV_PATH,
        DATA_RAW_DIR / "google_photos_retrieval_raw.csv",
        DATA_RAW_DIR / "google_photos_retrieval_raw.csv.csv",
    )


def resolve_production_csv_path():
    for path in production_csv_candidates():
        if path.is_file():
            return path
    return None


def resolve_survey_csv_path():
    for path in (SURVEY_CSV_PATH, DATA_DIR / "datasurvey_responses_raw.csv.csv"):
        if path.is_file():
            return path
    return None
