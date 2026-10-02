from collections import OrderedDict
from io import BytesIO
from pathlib import Path

import pandas as pd

from src.schema import (
    INGEST_DUPLICATE_RECORD_ID,
    INGEST_EMPTY_FILE,
    INGEST_INVALID_SAMPLING_FRAME,
    INGEST_MISSING_COLUMNS,
    INGEST_MISSING_TEXT_MODE,
    INGEST_UNEXPECTED_COLUMNS,
    INGEST_UNREADABLE,
    IngestError,
    REQUIRED_COLUMNS,
    SAMPLING_FRAME_TARGETED,
    TARGETED_COLUMNS,
)

DATASET_KIND_PRODUCTION = "production"
DATASET_KIND_DEVELOPMENT = "development"
DATASET_KIND_TARGETED = "targeted"


def _read_csv_preserve(path_or_buffer):
    read_kwargs = dict(
        dtype=str,
        keep_default_na=False,
        na_filter=False,
        encoding="utf-8-sig",
    )
    try:
        return pd.read_csv(path_or_buffer, **read_kwargs)
    except UnicodeDecodeError:
        if hasattr(path_or_buffer, "seek"):
            path_or_buffer.seek(0)
        return pd.read_csv(path_or_buffer, encoding="latin-1", **{
            k: v for k, v in read_kwargs.items() if k != "encoding"
        })
    except pd.errors.EmptyDataError:
        raise IngestError(INGEST_EMPTY_FILE, "The CSV file is empty.")
    except Exception as exc:
        raise IngestError(
            INGEST_UNREADABLE,
            "Could not read a valid CSV with the required columns.",
            {"error": str(exc)},
        )


def _read_file(path_or_buffer):
    if hasattr(path_or_buffer, "seek"):
        path_or_buffer.seek(0)
        df = _read_csv_preserve(path_or_buffer)
    else:
        path = Path(path_or_buffer)
        if not path.is_file():
            raise IngestError(INGEST_UNREADABLE, "CSV file was not found.")
        if path.stat().st_size == 0:
            raise IngestError(INGEST_EMPTY_FILE, "The CSV file is empty.")
        df = _read_csv_preserve(path)

    if df is None or len(df.columns) == 0:
        raise IngestError(INGEST_EMPTY_FILE, "The CSV file is empty.")
    return df


def _check_required(df, required):
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise IngestError(
            INGEST_MISSING_COLUMNS,
            "Missing required columns: {}.".format(", ".join(missing)),
            {"missing_columns": missing},
        )


def _check_unique_ids(df):
    record_ids = df["record_id"].astype(str)
    duplicated_mask = record_ids.duplicated(keep=False)
    if duplicated_mask.any():
        dupes = sorted(record_ids[duplicated_mask].unique().tolist())
        raise IngestError(
            INGEST_DUPLICATE_RECORD_ID,
            "Duplicate record_id values are not allowed: {}.".format(", ".join(dupes)),
            {"duplicate_record_ids": dupes},
        )


def _flag_empty_text(df):
    df = df.copy()
    df["raw_text_empty"] = df["raw_text"].astype(str).str.strip() == ""
    return df


def load_raw_csv(path_or_buffer):
    """Load a Corpus A style conversations CSV without changing cell values.

    Extra columns are kept. Required columns are not renamed or filled from
    other fields. Duplicate record_id values fail the load.
    """
    df = _read_file(path_or_buffer)
    _check_required(df, REQUIRED_COLUMNS)
    if len(df) == 0:
        raise IngestError(INGEST_EMPTY_FILE, "The CSV file has headers but no data rows.")
    _check_unique_ids(df)
    return _flag_empty_text(df)


def load_targeted_csv(path_or_buffer):
    """Load Corpus B (targeted_direct) independently of Corpus A.

    The file must have exactly TARGETED_COLUMNS. A header-only file is valid and
    returns zero rows, because Corpus B is collected incrementally.
    """
    df = _read_file(path_or_buffer)
    _check_required(df, TARGETED_COLUMNS)

    unexpected = [col for col in df.columns if col not in TARGETED_COLUMNS]
    if unexpected:
        raise IngestError(
            INGEST_UNEXPECTED_COLUMNS,
            "Unexpected columns in targeted corpus: {}.".format(", ".join(unexpected)),
            {"unexpected_columns": unexpected},
        )

    df = df[TARGETED_COLUMNS]
    if len(df) == 0:
        return _flag_empty_text(df)

    _check_unique_ids(df)

    frames = df["sampling_frame"].astype(str).str.strip()
    bad_frame = df.loc[frames != SAMPLING_FRAME_TARGETED, "record_id"].astype(str).tolist()
    if bad_frame:
        raise IngestError(
            INGEST_INVALID_SAMPLING_FRAME,
            "sampling_frame must be '{}' for every row. Invalid record_id: {}.".format(
                SAMPLING_FRAME_TARGETED, ", ".join(bad_frame)
            ),
            {"record_ids": bad_frame},
        )

    blank_mode = df.loc[df["text_mode"].astype(str).str.strip() == "", "record_id"].astype(str).tolist()
    if blank_mode:
        raise IngestError(
            INGEST_MISSING_TEXT_MODE,
            "text_mode is required (use 'paraphrase' unless noted otherwise). "
            "Missing for record_id: {}.".format(", ".join(blank_mode)),
            {"record_ids": blank_mode},
        )

    return _flag_empty_text(df)


def source_counts(df):
    counts = df["source"].value_counts(dropna=False)
    return OrderedDict((str(name), int(count)) for name, count in counts.items())


def infer_dataset_kind(path, df):
    name = ""
    if path is not None:
        name = Path(path).name.lower()
    if "direct_vague_targeted" in name:
        return DATASET_KIND_TARGETED
    if "dev_sample" in name or name == "conversations_sample.csv":
        return DATASET_KIND_DEVELOPMENT
    if "is_synthetic" in df.columns:
        flags = df["is_synthetic"].astype(str).str.strip().str.lower()
        if flags.isin(["true", "1", "yes"]).all() and len(df) > 0:
            return DATASET_KIND_DEVELOPMENT
    return DATASET_KIND_PRODUCTION


def load_uploaded_csv(uploaded_file):
    data = uploaded_file.getvalue()
    return load_raw_csv(BytesIO(data))
