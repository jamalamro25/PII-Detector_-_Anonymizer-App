# PII Detector & Anonymiser

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)
![Presidio](https://img.shields.io/badge/Microsoft-Presidio-0078D4?logo=microsoft&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-en__core__web__lg-09A3D5?logo=spacy&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-MIT-green)
![GDPR](https://img.shields.io/badge/GDPR-Compliant-brightgreen)

A professional, enterprise-grade Personally Identifiable Information (PII) detection and anonymisation web application built with Microsoft Presidio, spaCy, and Streamlit.

---

## Features

- **15+ Entity Types** — Person, Email, Phone, Location, Date/Time, IP Address, Credit Card, IBAN, NHS Number, NI Number, Organisation, URL, and more
- **Three Anonymisation Modes** — Label replacement `[PERSON_1]`, realistic fake data via Faker, or character-length redaction `***`
- **Bidirectional Restore** — Every anonymisation stored in session; one-click restoration to originals
- **Text Analysis** — Colour-coded highlighted view with entity tooltips and confidence scores
- **CSV / Excel Analysis** — Column risk cards (HIGH/MEDIUM/LOW/SAFE), dataset heatmap, bar chart, pie chart, and risk gauge
- **Results Dashboard** — Session-wide analysis timeline, aggregate stats, and JSON export
- **GDPR-Compliant Design** — Built for social care and healthcare data workflows
- **Dark Glassmorphism UI** — Deep navy/gold design with Playfair Display headings and Inter body text

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Web Framework | Streamlit 1.35 |
| PII Detection | Microsoft Presidio Analyzer 2.2.355 |
| Anonymisation | Microsoft Presidio Anonymizer 2.2.355 |
| NLP Model | spaCy `en_core_web_lg` |
| Visualisation | Plotly 5.22 |
| Fake Data | Faker 25.2 |
| Excel Support | openpyxl 3.1 |
| Navigation | streamlit-option-menu |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jamalamro/pii-detector.git
cd pii-detector
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the spaCy language model

```bash
python -m spacy download en_core_web_lg
```

---

## How to Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Project Structure

```
pii-detector/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Pinned dependencies
├── README.md                     # This file
├── .gitignore
├── assets/
│   └── styles.css                # Custom CSS (dark theme, animations)
├── utils/
│   ├── __init__.py
│   ├── analyzer.py               # Presidio detection logic
│   ├── anonymizer.py             # Anonymisation & bidirectional restore
│   ├── visualizations.py         # Plotly chart functions
│   └── helpers.py                # Shared utility functions
└── sample_data/
    ├── sample_text.txt           # Fake social care letter with PII
    └── sample_pii_data.csv       # 50 rows × 10 columns of fake PII
```

---

## Screenshots

> *(Add screenshots here after first run)*

---

## Usage Guide

### Text Analyser

1. Navigate to **Text Analyser**
2. Paste text or click **Load Sample** to use the included example
3. Click **Analyse Text**
4. View colour-coded highlights, detection table, and entity distribution chart
5. Download anonymised text or click **Restore** to revert

### CSV Analyser

1. Navigate to **CSV Analyser**
2. Upload a `.csv` or `.xlsx` file (max 50 MB)
3. Preview the first 10 rows, then click **Analyse Dataset**
4. Inspect column risk cards, heatmap, and charts
5. Download the anonymised CSV or the JSON audit report

### Anonymisation Modes (sidebar)

| Mode | Example |
|---|---|
| Label | `[PERSON_1]`, `[EMAIL_ADDRESS_2]` |
| Fake | `Oliver Bennett`, `o.bennett@example.com` |
| Redact | `***`, `*****` |

---

## Dissertation Context

This application was developed as part of:

> **"A Robust Machine Learning-Based Bidirectional Anonymisation System for Structured and Unstructured Social Care Data"**
>
> Jamal Amro — MSc Data Science  
> Cardiff Metropolitan University, 2024

The system addresses GDPR compliance challenges in social care data management by providing a reproducible, auditable anonymisation pipeline that preserves analytical utility while protecting personal data.

---

## Author

**Jamal Amro**  
MSc Data Science, Cardiff Metropolitan University  
[GitHub](https://github.com/jamalamro) · [LinkedIn](https://linkedin.com/in/jamalamro)  
jamal.sa.omar@gmail.com

---

## Licence

MIT © 2024 Jamal Amro
