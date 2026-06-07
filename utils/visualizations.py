from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from collections import Counter
from utils.helpers import entity_color, entity_label, risk_badge_color

_DARK_BG = "#0a0f1e"
_SURFACE = "#111827"
_GOLD = "#c9a84c"
_TEXT = "#d1d5db"

_LAYOUT_BASE = dict(
    paper_bgcolor=_SURFACE,
    plot_bgcolor=_SURFACE,
    font=dict(family="Inter", color=_TEXT),
    margin=dict(l=20, r=20, t=40, b=20),
)


def entity_pie_chart(results: list) -> go.Figure:
    counts = Counter(r.entity_type for r in results)
    labels = [entity_label(k) for k in counts.keys()]
    values = list(counts.values())
    colors = [entity_color(k) for k in counts.keys()]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color=_DARK_BG, width=2)),
        hole=0.4,
        textinfo="label+percent",
        textfont=dict(color=_TEXT, size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Entity Type Distribution", font=dict(color=_GOLD, size=16)),
        showlegend=True,
        legend=dict(font=dict(color=_TEXT)),
    )
    return fig


def entity_bar_chart(col_results: dict[str, list]) -> go.Figure:
    data = []
    for col, results in col_results.items():
        counts = Counter(r.entity_type for r in results)
        for etype, cnt in counts.items():
            data.append({"Column": col, "Entity": entity_label(etype), "Count": cnt, "Color": entity_color(etype)})

    if not data:
        return _empty_fig("No PII detected")

    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        x="Column",
        y="Count",
        color="Entity",
        barmode="stack",
        color_discrete_map={row["Entity"]: row["Color"] for _, row in df.iterrows()},
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="PII Detections per Column", font=dict(color=_GOLD, size=16)),
        xaxis=dict(title="Column", color=_TEXT, gridcolor="#1f2937"),
        yaxis=dict(title="Count", color=_TEXT, gridcolor="#1f2937"),
        legend=dict(font=dict(color=_TEXT)),
    )
    return fig


def risk_heatmap(df: pd.DataFrame, col_results: dict[str, list]) -> go.Figure:
    pii_cols = [c for c, r in col_results.items() if r]
    if not pii_cols:
        return _empty_fig("No PII columns found")

    rows_sample = min(len(df), 30)
    matrix = []
    for col in pii_cols:
        col_hits = set()
        for res in col_results[col]:
            col_hits.add(0)
        row_vals = []
        for i in range(rows_sample):
            val = str(df[col].iloc[i]) if i < len(df) else ""
            row_vals.append(1 if any(
                val.lower() in str(df[col].iloc[i]).lower() for _ in [1]
            ) else 0)
        matrix.append(row_vals)

    z = [[1 if col_results.get(pii_cols[ci], []) else 0 for ci in range(len(pii_cols))] for _ in range(rows_sample)]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=pii_cols,
        y=[f"Row {i+1}" for i in range(rows_sample)],
        colorscale=[[0, _SURFACE], [1, "#ef4444"]],
        showscale=True,
        colorbar=dict(title="PII", tickvals=[0, 1], ticktext=["Clean", "PII"], tickfont=dict(color=_TEXT)),
        hovertemplate="Column: %{x}<br>%{y}<br>PII Detected: %{z}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Dataset PII Heatmap", font=dict(color=_GOLD, size=16)),
        xaxis=dict(color=_TEXT),
        yaxis=dict(color=_TEXT, autorange="reversed"),
    )
    return fig


def risk_gauge(score: float) -> go.Figure:
    if score < 30:
        color = "#10b981"
    elif score < 60:
        color = "#f59e0b"
    else:
        color = "#ef4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Overall Risk Score", "font": {"color": _GOLD, "size": 16}},
        number={"suffix": "%", "font": {"color": _TEXT, "size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": _TEXT, "tickfont": {"color": _TEXT}},
            "bar": {"color": color},
            "bgcolor": _SURFACE,
            "borderwidth": 1,
            "bordercolor": "#1f2937",
            "steps": [
                {"range": [0, 30], "color": "#052e16"},
                {"range": [30, 60], "color": "#422006"},
                {"range": [60, 100], "color": "#450a0a"},
            ],
            "threshold": {"line": {"color": _GOLD, "width": 3}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(**_LAYOUT_BASE, height=250)
    return fig


def session_timeline_chart(history: list[dict]) -> go.Figure:
    if not history:
        return _empty_fig("No analysis history yet")

    labels = [f"{h['type']} #{i+1}" for i, h in enumerate(history)]
    counts = [h.get("pii_count", 0) for h in history]
    times = [h.get("timestamp", "") for h in history]

    fig = go.Figure(go.Scatter(
        x=list(range(len(history))),
        y=counts,
        mode="lines+markers",
        line=dict(color=_GOLD, width=2),
        marker=dict(size=8, color=_GOLD),
        text=labels,
        hovertemplate="<b>%{text}</b><br>PII found: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text="Analysis Timeline — PII Detected per Run", font=dict(color=_GOLD, size=16)),
        xaxis=dict(title="Run", color=_TEXT, gridcolor="#1f2937", tickvals=list(range(len(history))), ticktext=labels),
        yaxis=dict(title="PII Count", color=_TEXT, gridcolor="#1f2937"),
    )
    return fig


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False, font=dict(color=_TEXT, size=14))
    fig.update_layout(**_LAYOUT_BASE, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig
