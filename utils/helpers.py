from __future__ import annotations
import re
import json
from pathlib import Path
from typing import Any


ENTITY_COLORS: dict[str, str] = {
    "PERSON": "#f59e0b",
    "EMAIL_ADDRESS": "#3b82f6",
    "PHONE_NUMBER": "#10b981",
    "LOCATION": "#f97316",
    "DATE_TIME": "#8b5cf6",
    "NRP": "#ec4899",
    "IP_ADDRESS": "#06b6d4",
    "CREDIT_CARD": "#ef4444",
    "IBAN_CODE": "#ef4444",
    "MEDICAL_LICENSE": "#6366f1",
    "URL": "#84cc16",
    "US_SSN": "#ef4444",
    "UK_NHS": "#e11d48",
    "UK_NINO": "#be185d",
    "ORGANIZATION": "#0ea5e9",
    "DEFAULT": "#dc2626",
}

ENTITY_LABELS: dict[str, str] = {
    "PERSON": "Person",
    "EMAIL_ADDRESS": "Email",
    "PHONE_NUMBER": "Phone",
    "LOCATION": "Location",
    "DATE_TIME": "Date/Time",
    "NRP": "Nationality/Religion",
    "IP_ADDRESS": "IP Address",
    "CREDIT_CARD": "Credit Card",
    "IBAN_CODE": "IBAN",
    "MEDICAL_LICENSE": "Medical ID",
    "URL": "URL",
    "US_SSN": "SSN",
    "UK_NHS": "NHS Number",
    "UK_NINO": "NI Number",
    "ORGANIZATION": "Organisation",
}

RISK_ENTITY_TYPES = {
    "HIGH": ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IBAN_CODE", "US_SSN", "UK_NHS", "UK_NINO"],
    "MEDIUM": ["LOCATION", "DATE_TIME", "MEDICAL_LICENSE", "IP_ADDRESS"],
    "LOW": ["NRP", "URL", "ORGANIZATION"],
}


def entity_color(entity_type: str) -> str:
    return ENTITY_COLORS.get(entity_type, ENTITY_COLORS["DEFAULT"])


def entity_label(entity_type: str) -> str:
    return ENTITY_LABELS.get(entity_type, entity_type.replace("_", " ").title())


def risk_level(entity_type: str) -> str:
    for level, types in RISK_ENTITY_TYPES.items():
        if entity_type in types:
            return level
    return "LOW"


def risk_badge_color(level: str) -> str:
    return {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981", "SAFE": "#6b7280"}[level]


def load_css(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def truncate_text(text: str, max_len: int = 80) -> str:
    return text if len(text) <= max_len else text[:max_len] + "…"


def word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def char_count(text: str) -> int:
    return len(text)


def confidence_bar(score: float) -> str:
    pct = int(score * 100)
    color = "#10b981" if score >= 0.8 else "#f59e0b" if score >= 0.5 else "#ef4444"
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<div style="background:#1f2937;border-radius:4px;width:80px;height:8px;">'
        f'<div style="background:{color};width:{pct}%;height:8px;border-radius:4px;"></div>'
        f'</div><span style="color:{color};font-size:12px;">{pct}%</span></div>'
    )


def build_highlighted_html(text: str, results: list[Any]) -> str:
    if not results:
        return f'<p style="color:#d1d5db;line-height:1.8;">{_escape(text)}</p>'

    sorted_results = sorted(results, key=lambda r: r.start)
    html_parts: list[str] = []
    cursor = 0

    for res in sorted_results:
        if res.start > cursor:
            html_parts.append(_escape(text[cursor:res.start]))
        color = entity_color(res.entity_type)
        label = entity_label(res.entity_type)
        pct = int(res.score * 100)
        span_text = _escape(text[res.start:res.end])
        html_parts.append(
            f'<span style="background:{color}33;border:1px solid {color};border-radius:4px;'
            f'padding:1px 4px;cursor:pointer;position:relative;" '
            f'title="{label} ({pct}% confidence)">'
            f'<span style="color:{color};font-weight:600;">{span_text}</span>'
            f'<sup style="font-size:9px;color:{color};margin-left:2px;">{label}</sup>'
            f'</span>'
        )
        cursor = res.end

    if cursor < len(text):
        html_parts.append(_escape(text[cursor:]))

    return (
        '<div style="background:#111827;border:1px solid #1f2937;border-radius:8px;'
        'padding:16px;line-height:2;color:#d1d5db;font-size:14px;">'
        + "".join(html_parts)
        + "</div>"
    )


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


def results_to_dict(results: list[Any]) -> list[dict]:
    return [
        {
            "entity_type": r.entity_type,
            "text": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": round(r.score, 3),
        }
        for r in results
    ]


def export_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)
