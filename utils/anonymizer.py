from __future__ import annotations
import re
import uuid
from typing import Any
from faker import Faker

_fake = Faker("en_GB")


# ---------- core engine ----------

def get_anonymizer():
    from presidio_anonymizer import AnonymizerEngine
    return AnonymizerEngine()


# ---------- mapping store ----------

def _new_mapping() -> dict:
    return {}


def anonymize_text(
    text: str,
    results: list[Any],
    mode: str = "label",
    existing_mapping: dict | None = None,
) -> tuple[str, dict]:
    """
    Returns (anonymised_text, bidirectional_mapping).
    mapping: { placeholder -> original }
    mode: 'label' | 'fake' | 'redact'
    """
    if not results or not text.strip():
        return text, existing_mapping or {}

    mapping: dict = existing_mapping or {}
    sorted_results = sorted(results, key=lambda r: r.start, reverse=True)
    output = text

    for res in sorted_results:
        original = text[res.start:res.end]
        placeholder = _make_placeholder(res.entity_type, original, mode, mapping)
        mapping[placeholder] = original
        output = output[: res.start] + placeholder + output[res.end :]

    return output, mapping


def restore_text(anonymised_text: str, mapping: dict) -> str:
    result = anonymised_text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result


def anonymize_dataframe(df, col_results: dict[str, list[Any]], mode: str = "label"):
    import pandas as pd

    anon_df = df.copy()
    master_mapping: dict = {}

    for col, results in col_results.items():
        if not results:
            continue

        col_values = df[col].astype(str).tolist()
        sep = " [SEP] "
        combined = sep.join(col_values)

        # Adjust offsets to per-cell
        anon_combined, mapping = anonymize_text(combined, results, mode, {})
        master_mapping.update(mapping)

        # Split back
        anon_cells = anon_combined.split(sep)
        if len(anon_cells) == len(col_values):
            anon_df[col] = anon_cells

    return anon_df, master_mapping


# ---------- placeholder factory ----------

_counters: dict[str, int] = {}


def _make_placeholder(entity_type: str, original: str, mode: str, mapping: dict) -> str:
    # Reuse existing placeholder for same original value
    for ph, orig in mapping.items():
        if orig == original:
            return ph

    if mode == "label":
        tag = entity_type.replace("_ADDRESS", "").replace("_", "")
        _counters[entity_type] = _counters.get(entity_type, 0) + 1
        return f"[{entity_type}_{_counters[entity_type]}]"

    elif mode == "fake":
        return _fake_value(entity_type)

    elif mode == "redact":
        return "*" * len(original)

    return f"[{entity_type}]"


def _fake_value(entity_type: str) -> str:
    mapping = {
        "PERSON": _fake.name,
        "EMAIL_ADDRESS": _fake.email,
        "PHONE_NUMBER": _fake.phone_number,
        "LOCATION": _fake.city,
        "DATE_TIME": lambda: _fake.date(pattern="%d/%m/%Y"),
        "IP_ADDRESS": _fake.ipv4,
        "CREDIT_CARD": _fake.credit_card_number,
        "URL": _fake.url,
        "ORGANIZATION": _fake.company,
        "UK_NHS": lambda: f"{_fake.random_int(100,999)} {_fake.random_int(100,999)} {_fake.random_int(1000,9999)}",
        "UK_NINO": lambda: f"{_fake.random_letter().upper()}{_fake.random_letter().upper()} {_fake.random_int(10,99)} {_fake.random_int(10,99)} {_fake.random_int(10,99)} {_fake.random_letter().upper()}",
    }
    fn = mapping.get(entity_type)
    if fn:
        try:
            return str(fn())
        except Exception:
            pass
    return f"[{entity_type}]"


def reset_counters():
    _counters.clear()
