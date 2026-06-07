from __future__ import annotations
import streamlit as st
from typing import Any

_analyzer = None


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = _load_analyzer()
    return _analyzer


def _load_analyzer():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    config = {"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]}
    provider = NlpEngineProvider(nlp_configuration=config)
    nlp_engine = provider.create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])


def analyze_text(text: str, score_threshold: float = 0.35) -> list[Any]:
    if not text.strip():
        return []
    analyzer = get_analyzer()
    results = analyzer.analyze(
        text=text,
        language="en",
        score_threshold=score_threshold,
        entities=[
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION",
            "DATE_TIME", "NRP", "IP_ADDRESS", "CREDIT_CARD", "IBAN_CODE",
            "MEDICAL_LICENSE", "URL", "US_SSN", "UK_NHS", "UK_NINO", "ORGANIZATION",
        ],
    )
    return sorted(results, key=lambda r: r.start)


def analyze_dataframe(df, score_threshold: float = 0.35) -> dict[str, list[Any]]:
    """Return per-column analysis results."""
    col_results: dict[str, list[Any]] = {}
    for col in df.columns:
        combined_texts = " [SEP] ".join(df[col].dropna().astype(str).tolist())
        col_results[col] = analyze_text(combined_texts, score_threshold)
    return col_results


def column_risk_summary(col_results: dict[str, list[Any]]) -> dict[str, dict]:
    from utils.helpers import risk_level, RISK_ENTITY_TYPES

    summary = {}
    for col, results in col_results.items():
        if not results:
            summary[col] = {"level": "SAFE", "count": 0, "types": []}
            continue

        types = list({r.entity_type for r in results})
        max_level = "LOW"
        for res in results:
            lvl = risk_level(res.entity_type)
            if lvl == "HIGH":
                max_level = "HIGH"
                break
            if lvl == "MEDIUM":
                max_level = "MEDIUM"

        summary[col] = {"level": max_level, "count": len(results), "types": types}

    return summary
