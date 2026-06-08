from __future__ import annotations
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="PII Detector & Anonymiser",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS injection ────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Imports ──────────────────────────────────────────────────────────────────
from streamlit_option_menu import option_menu
from utils.helpers import (
    entity_color, entity_label, risk_badge_color, build_highlighted_html,
    word_count, char_count, export_json, ENTITY_COLORS,
)
from utils.analyzer import analyze_text, analyze_dataframe, column_risk_summary
from utils.anonymizer import anonymize_text, anonymize_dataframe, restore_text, reset_counters
from utils.visualizations import (
    entity_pie_chart, entity_bar_chart, risk_heatmap,
    risk_gauge, session_timeline_chart,
)

# ── Session state init ───────────────────────────────────────────────────────
for key, default in {
    "analysis_history": [],
    "text_mapping": {},
    "text_anon": "",
    "text_results": [],
    "csv_mapping": {},
    "csv_anon_df": None,
    "csv_col_results": {},
    "analyzer_ready": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:20px 0 10px;">'
        '<div style="font-size:42px;">🔐</div>'
        '<div style="font-family:\'Playfair Display\',serif;font-size:18px;'
        'color:#c9a84c;font-weight:700;margin-top:8px;">PII Detector</div>'
        '<div style="font-size:11px;color:#6b7280;margin-top:4px;">'
        'Powered by Presidio &amp; spaCy</div></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("**Anonymisation Mode**")
    anon_mode = st.selectbox(
        "Select mode",
        options=["label", "fake", "redact"],
        format_func=lambda x: {
            "label": "🏷️  Replace with Label",
            "fake": "🎭  Replace with Fake Data",
            "redact": "⬛  Redact (***)",
        }[x],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Confidence Threshold**")
    threshold = st.slider("Min score", 0.1, 0.9, 0.35, 0.05, label_visibility="collapsed")

    st.divider()
    st.markdown(
        '<div style="text-align:center;padding:10px 0;">'
        '<div style="font-size:11px;color:#6b7280;line-height:1.6;">'
        'Cardiff Metropolitan University<br>'
        'MSc Data Science<br>'
        '<span style="color:#c9a84c;">Jamal Amro</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )


# ── Top navigation ───────────────────────────────────────────────────────────
selected = option_menu(
    menu_title=None,
    options=["Home", "Text Analyser", "CSV Analyser", "Results Dashboard", "About"],
    icons=["house-fill", "file-text-fill", "table", "bar-chart-fill", "info-circle-fill"],
    orientation="horizontal",
    styles={
        "container": {"background-color": "#111827", "border-bottom": "1px solid #374151", "padding": "4px 16px"},
        "icon": {"color": "#6b7280", "font-size": "15px"},
        "nav-link": {
            "font-family": "Inter", "font-size": "13px", "color": "#9ca3af",
            "padding": "8px 16px", "border-radius": "8px",
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg,#c9a84c,#a8853a)",
            "color": "#0a0f1e", "font-weight": "700",
        },
        "icon-selected": {"color": "#0a0f1e"},
    },
)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════════════════
if selected == "Home":
    st.markdown(
        '<div class="hero">'
        '<div class="particle-bg"></div>'
        '<div class="hero-title">PII Detector &amp; Anonymiser</div>'
        '<div class="hero-subtitle">'
        'Enterprise-grade Personally Identifiable Information detection and anonymisation '
        'powered by Microsoft Presidio and spaCy NLP. GDPR-compliant, bidirectional, '
        'and designed for social care data.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # Stat counters
    c1, c2, c3 = st.columns(3)
    for col, num, label in [
        (c1, "15+", "Entity Types Detected"),
        (c2, "3", "Anonymisation Modes"),
        (c3, "GDPR", "Compliant Design"),
    ]:
        with col:
            st.markdown(
                f'<div class="stat-counter"><div class="num">{num}</div>'
                f'<div class="label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown("### Core Features")
    f1, f2, f3 = st.columns(3)
    features = [
        ("🔍", "Real-time Detection", "Analyses text and structured data instantly using transformer-backed NER models with configurable confidence thresholds."),
        ("🎭", "Smart Anonymisation", "Three modes: label replacement, realistic fake data generation via Faker, or character-length redaction."),
        ("↩️", "Bidirectional Restore", "Every anonymisation is stored in a session mapping, allowing full one-click restoration to original values."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(
                f'<div class="pii-card"><div class="icon">{icon}</div>'
                f'<h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown("### How It Works")
    steps = [
        ("1", "Upload or Paste", "Provide free-text or upload a CSV/XLSX file containing data you want to analyse."),
        ("2", "Detect", "Presidio's NLP pipeline identifies PII entities — names, emails, phones, locations, and more."),
        ("3", "Anonymise", "Choose a mode and anonymise in one click. A bidirectional mapping is stored automatically."),
        ("4", "Export", "Download anonymised data or a full audit report. Restore originals any time this session."),
    ]
    for num, title, desc in steps:
        st.markdown(
            f'<div class="step-row"><div class="step-badge">{num}</div>'
            f'<div><strong style="color:#e5e7eb;">{title}</strong>'
            f'<div style="color:#6b7280;font-size:13px;margin-top:4px;">{desc}</div></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Entity badge grid
    st.markdown("### Detectable Entity Types")
    badge_html = ""
    for etype, color in ENTITY_COLORS.items():
        if etype == "DEFAULT":
            continue
        badge_html += (
            f'<span class="entity-badge" style="background:{color}22;'
            f'color:{color};border:1px solid {color}66;">'
            f'{entity_label(etype)}</span>'
        )
    st.markdown(
        f'<div style="background:#111827;border:1px solid #374151;border-radius:12px;padding:20px;">'
        f'{badge_html}</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: TEXT ANALYSER
# ════════════════════════════════════════════════════════════════════════════
elif selected == "Text Analyser":
    st.markdown('<h2 style="margin-top:0;">📄 Text Analyser</h2>', unsafe_allow_html=True)

    sample_path = Path(__file__).parent / "sample_data" / "sample_text.txt"

    col_input, col_meta = st.columns([4, 1])
    with col_input:
        text_input = st.text_area(
            "Paste text to analyse",
            height=220,
            placeholder="Paste any text containing PII here…",
            label_visibility="collapsed",
        )
    with col_meta:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📋 Load Sample", use_container_width=True):
            if sample_path.exists():
                st.session_state["_sample_text"] = sample_path.read_text(encoding="utf-8")
                st.rerun()
        if "_sample_text" in st.session_state:
            text_input = st.session_state.pop("_sample_text")

        wc = word_count(text_input)
        cc = char_count(text_input)
        st.markdown(
            f'<div style="background:#111827;border:1px solid #374151;border-radius:8px;'
            f'padding:12px;font-size:12px;color:#6b7280;text-align:center;">'
            f'<div style="color:#c9a84c;font-size:18px;font-weight:700;">{wc}</div>words'
            f'<div style="color:#c9a84c;font-size:18px;font-weight:700;margin-top:8px;">{cc}</div>chars'
            f'</div>',
            unsafe_allow_html=True,
        )

    run_btn = st.button("🔍 Analyse Text", type="primary", use_container_width=False)

    if run_btn:
        if not text_input.strip():
            st.warning("⚠️ Please enter some text before analysing.")
        else:
            with st.spinner("Running Presidio NLP analysis…"):
                try:
                    results = analyze_text(text_input, threshold)
                    reset_counters()
                    anon_text, mapping = anonymize_text(text_input, results, anon_mode, {})
                    st.session_state["text_results"] = results
                    st.session_state["text_anon"] = anon_text
                    st.session_state["text_mapping"] = mapping
                    st.session_state["_text_input_cache"] = text_input
                    st.session_state["analysis_history"].append({
                        "type": "Text",
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "pii_count": len(results),
                        "entity_types": list({r.entity_type for r in results}),
                        "mode": anon_mode,
                    })
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
                    if "Can't find model" in str(e) or "no such model" in str(e).lower():
                        st.info("Run: `python -m spacy download en_core_web_lg`")
                    st.stop()

    results = st.session_state.get("text_results", [])
    anon_text = st.session_state.get("text_anon", "")
    mapping = st.session_state.get("text_mapping", {})
    orig_text = st.session_state.get("_text_input_cache", text_input)

    if results:
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        entity_types = list({r.entity_type for r in results})
        avg_score = sum(r.score for r in results) / len(results)
        m1.metric("PII Entities", len(results))
        m2.metric("Unique Types", len(entity_types))
        m3.metric("Avg Confidence", f"{avg_score:.0%}")
        m4.metric("Words Analysed", word_count(orig_text))

        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns(2)

        with left:
            st.markdown('<div class="result-panel"><h4>🎨 Highlighted Original</h4>', unsafe_allow_html=True)
            st.markdown(build_highlighted_html(orig_text, results), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="result-panel"><h4>🔒 Anonymised Text</h4>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="background:#0a0f1e;border:1px solid #1f2937;border-radius:8px;'
                f'padding:16px;line-height:2;color:#d1d5db;font-size:14px;min-height:120px;">'
                f'{anon_text.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            dl_col, restore_col = st.columns(2)
            with dl_col:
                st.download_button(
                    "⬇️ Download",
                    data=anon_text,
                    file_name="anonymised_text.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with restore_col:
                if st.button("↩️ Restore", use_container_width=True):
                    st.session_state["text_anon"] = restore_text(anon_text, mapping)
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Detection table + pie
        tab1, tab2, tab3 = st.tabs(["📋 Detection Results", "📊 Distribution", "🗺️ Mapping Table"])

        with tab1:
            table_data = [
                {
                    "Entity Type": entity_label(r.entity_type),
                    "Detected Text": orig_text[r.start:r.end],
                    "Start": r.start,
                    "End": r.end,
                    "Confidence": f"{r.score:.0%}",
                }
                for r in results
            ]
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

        with tab2:
            st.plotly_chart(entity_pie_chart(results), use_container_width=True)

        with tab3:
            map_data = [
                {"Placeholder": ph, "Original Value": orig, "Entity Type": entity_label(next((r.entity_type for r in results if orig_text[r.start:r.end] == orig), "UNKNOWN"))}
                for ph, orig in mapping.items()
            ]
            if map_data:
                st.dataframe(pd.DataFrame(map_data), use_container_width=True, hide_index=True)
            else:
                st.info("No mapping generated.")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CSV ANALYSER
# ════════════════════════════════════════════════════════════════════════════
elif selected == "CSV Analyser":
    st.markdown('<h2 style="margin-top:0;">📊 CSV / Excel Analyser</h2>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop a CSV or XLSX file here",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
    )

    df = None
    if uploaded:
        if uploaded.size > 50 * 1024 * 1024:
            st.markdown(
                '<div style="background:#450a0a;border:1px solid #ef4444;border-radius:12px;'
                'padding:20px;text-align:center;">'
                '<div style="font-size:32px;">⚠️</div>'
                '<div style="color:#ef4444;font-weight:700;">File too large</div>'
                '<div style="color:#9ca3af;font-size:13px;margin-top:8px;">'
                'Maximum file size is 50 MB. Please upload a smaller file.</div></div>',
                unsafe_allow_html=True,
            )
            st.stop()

        try:
            if uploaded.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded, engine="openpyxl")
            else:
                df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read file: {e}")
            st.stop()

        st.markdown("**Preview (first 10 rows)**")
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown(f"*{len(df)} rows × {len(df.columns)} columns*")

        analyse_btn = st.button("🔍 Analyse Dataset", type="primary")

        if analyse_btn:
            with st.spinner("Analysing all columns with Presidio…"):
                try:
                    col_results = analyze_dataframe(df, threshold)
                    risk_summary = column_risk_summary(col_results)
                    reset_counters()
                    anon_df, master_mapping = anonymize_dataframe(df, col_results, anon_mode)
                    st.session_state["csv_col_results"] = col_results
                    st.session_state["csv_risk_summary"] = risk_summary
                    st.session_state["csv_anon_df"] = anon_df
                    st.session_state["csv_mapping"] = master_mapping
                    st.session_state["_csv_df_cache"] = df

                    total_pii = sum(len(v) for v in col_results.values())
                    high_risk_cols = sum(1 for v in risk_summary.values() if v["level"] == "HIGH")
                    records_aff = len(df)
                    risk_score = min(100, int((total_pii / max(len(df) * len(df.columns), 1)) * 400))

                    st.session_state["analysis_history"].append({
                        "type": "CSV",
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "pii_count": total_pii,
                        "entity_types": list({r.entity_type for res_list in col_results.values() for r in res_list}),
                        "mode": anon_mode,
                        "columns": len(df.columns),
                        "rows": len(df),
                    })
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
                    st.stop()

        col_results = st.session_state.get("csv_col_results", {})
        risk_summary = st.session_state.get("csv_risk_summary", {})
        anon_df = st.session_state.get("csv_anon_df")
        master_mapping = st.session_state.get("csv_mapping", {})
        orig_df = st.session_state.get("_csv_df_cache", df)

        if col_results and risk_summary:
            st.markdown("---")

            # Summary metrics
            total_pii = sum(len(v) for v in col_results.values())
            high_risk = sum(1 for v in risk_summary.values() if v["level"] == "HIGH")
            risk_score = min(100, int((total_pii / max(len(orig_df) * len(orig_df.columns), 1)) * 400))
            records_aff = len(orig_df)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total PII Detected", total_pii)
            m2.metric("High-Risk Columns", high_risk)
            m3.metric("Risk Score", f"{risk_score}%")
            m4.metric("Records Affected", records_aff)

            st.markdown("<br>**Column Risk Assessment**</br>", unsafe_allow_html=True)
            cols_per_row = 4
            col_names = list(risk_summary.keys())
            for i in range(0, len(col_names), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col_name in enumerate(col_names[i:i + cols_per_row]):
                    info = risk_summary[col_name]
                    lvl = info["level"]
                    color = risk_badge_color(lvl)
                    with row_cols[j]:
                        types_str = ", ".join(entity_label(t) for t in info["types"][:3]) or "—"
                        st.markdown(
                            f'<div style="background:#111827;border:1px solid #374151;'
                            f'border-radius:10px;padding:14px;margin-bottom:8px;">'
                            f'<div style="font-size:12px;font-weight:600;color:#e5e7eb;'
                            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{col_name}</div>'
                            f'<span class="risk-badge" style="background:{color}22;color:{color};'
                            f'border:1px solid {color}66;margin-top:6px;display:inline-block;">{lvl}</span>'
                            f'<div style="font-size:11px;color:#6b7280;margin-top:6px;">{info["count"]} hits</div>'
                            f'<div style="font-size:10px;color:#4b5563;margin-top:4px;">{types_str}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Heatmap", "📊 Bar Chart", "🥧 PII Types", "⚡ Risk Gauge"])
            with tab1:
                st.plotly_chart(risk_heatmap(orig_df, col_results), use_container_width=True)
            with tab2:
                st.plotly_chart(entity_bar_chart(col_results), use_container_width=True)
            with tab3:
                all_results = [r for res_list in col_results.values() for r in res_list]
                if all_results:
                    st.plotly_chart(entity_pie_chart(all_results), use_container_width=True)
            with tab4:
                st.plotly_chart(risk_gauge(risk_score), use_container_width=True)

            st.markdown("---")

            dl1, dl2 = st.columns(2)
            with dl1:
                if anon_df is not None:
                    csv_out = anon_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download Anonymised CSV",
                        data=csv_out,
                        file_name="anonymised_data.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
            with dl2:
                audit = {
                    "timestamp": datetime.now().isoformat(),
                    "total_pii": total_pii,
                    "risk_score": risk_score,
                    "column_summary": risk_summary,
                    "mapping": master_mapping,
                }
                st.download_button(
                    "📋 Download Audit Report (JSON)",
                    data=export_json(audit),
                    file_name="pii_audit_report.json",
                    mime="application/json",
                    use_container_width=True,
                )

    elif not uploaded:
        st.markdown(
            '<div style="background:#111827;border:2px dashed #374151;border-radius:16px;'
            'padding:60px;text-align:center;">'
            '<div style="font-size:48px;margin-bottom:16px;">📂</div>'
            '<div style="color:#9ca3af;font-size:16px;">Upload a CSV or XLSX file to begin</div>'
            '<div style="color:#6b7280;font-size:13px;margin-top:8px;">Max 50 MB · Supports .csv and .xlsx</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: RESULTS DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
elif selected == "Results Dashboard":
    st.markdown('<h2 style="margin-top:0;">📈 Results Dashboard</h2>', unsafe_allow_html=True)

    history = st.session_state.get("analysis_history", [])

    if not history:
        st.markdown(
            '<div style="background:#111827;border:1px solid #374151;border-radius:16px;'
            'padding:60px;text-align:center;">'
            '<div style="font-size:48px;">📭</div>'
            '<div style="color:#9ca3af;font-size:16px;margin-top:16px;">'
            'No analyses yet this session.</div>'
            '<div style="color:#6b7280;font-size:13px;margin-top:8px;">'
            'Run an analysis on the Text or CSV pages to see results here.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        total_runs = len(history)
        total_pii = sum(h["pii_count"] for h in history)
        text_runs = sum(1 for h in history if h["type"] == "Text")
        csv_runs = sum(1 for h in history if h["type"] == "CSV")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Runs", total_runs)
        m2.metric("Total PII Found", total_pii)
        m3.metric("Text Analyses", text_runs)
        m4.metric("CSV Analyses", csv_runs)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(session_timeline_chart(history), use_container_width=True)

        st.markdown("### Analysis Log")
        log_data = []
        for i, h in enumerate(history):
            log_data.append({
                "#": i + 1,
                "Time": h["timestamp"],
                "Type": h["type"],
                "PII Found": h["pii_count"],
                "Mode": h.get("mode", "—"),
                "Entity Types": ", ".join(entity_label(t) for t in h.get("entity_types", [])),
            })
        st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        export_data = export_json(history)
        st.download_button(
            "⬇️ Export All Results (JSON)",
            data=export_data,
            file_name="session_results.json",
            mime="application/json",
        )

        if st.button("🗑️ Clear Session History", type="secondary"):
            st.session_state["analysis_history"] = []
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ════════════════════════════════════════════════════════════════════════════
elif selected == "About":
    st.markdown('<h2 style="margin-top:0;">ℹ️ About This Project</h2>', unsafe_allow_html=True)

    st.markdown(
        '<div style="background:#111827;border:1px solid #374151;border-radius:12px;'
        'padding:24px;margin-bottom:24px;color:#d1d5db;font-size:15px;line-height:1.8;">'
        'This application was developed as part of a postgraduate dissertation in MSc Data Science '
        'at Cardiff Metropolitan University. It demonstrates a robust, machine-learning-based '
        'bidirectional anonymisation system for structured and unstructured social care data, '
        'built on Microsoft Presidio and spaCy NLP.<br><br>'
        'Social care records contain some of the most sensitive personal data, including health '
        'information, addresses, and financial details. This tool provides practitioners and '
        'researchers with a GDPR-compliant workflow for anonymising such data before analysis '
        'or sharing, while preserving the ability to restore original values when required.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Technology Stack")
    tech = [
        ("🐍", "Python 3.11", "Core language powering the application logic"),
        ("🔍", "Microsoft Presidio", "NLP-backed PII detection and anonymisation engine"),
        ("🧠", "spaCy en_core_web_lg", "Large English language model for Named Entity Recognition"),
        ("⚡", "Streamlit", "Rapid interactive web application framework"),
        ("📊", "Plotly", "Interactive data visualisation library"),
        ("🎭", "Faker", "Realistic synthetic data generation for fake-replace mode"),
    ]
    cols = st.columns(3)
    for i, (icon, name, desc) in enumerate(tech):
        with cols[i % 3]:
            st.markdown(
                f'<div class="tech-card"><div class="tech-icon">{icon}</div>'
                f'<div class="tech-name">{name}</div>'
                f'<div class="tech-desc">{desc}</div></div><br>',
                unsafe_allow_html=True,
            )

    st.markdown("### Author")
    st.markdown(
        '<div class="author-card">'
        '<div style="font-size:56px;margin-bottom:16px;">👨‍💻</div>'
        '<h3>Jamal Amro</h3>'
        '<div class="role">MSc Data Science · Cardiff Metropolitan University</div>'
        '<div class="diss">'
        '"A Robust Machine Learning-Based Bidirectional Anonymisation System '
        'for Structured and Unstructured Social Care Data"'
        '</div>'
        '<div style="margin-top:20px;display:flex;gap:12px;justify-content:center;">'
        '<a href="https://github.com/jamalamro25" target="_blank" style="text-decoration:none;">'
        '<div style="background:rgba(201,168,76,.15);border:1px solid rgba(201,168,76,.4);'
        'border-radius:8px;padding:8px 20px;color:#c9a84c;font-size:13px;font-weight:600;">'
        '🐙 GitHub</div></a>'
        '<a href="https://linkedin.com/in/jamalamro" target="_blank" style="text-decoration:none;">'
        '<div style="background:rgba(59,130,246,.15);border:1px solid rgba(59,130,246,.4);'
        'border-radius:8px;padding:8px 20px;color:#3b82f6;font-size:13px;font-weight:600;">'
        '💼 LinkedIn</div></a>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#4b5563;font-size:12px;">'
        'PII Detector &amp; Anonymiser · MIT Licence · 2024 · Jamal Amro</div>',
        unsafe_allow_html=True,
    )
