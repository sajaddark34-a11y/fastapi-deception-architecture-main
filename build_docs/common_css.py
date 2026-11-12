"""
Common CSS styling for Enterprise Cybersecurity Documentation PDFs.
Bilingual (Arabic RTL with English LTR code spans and technical terms).
"""

CYBER_THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap');

@page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
}

@page :first {
    margin: 0;
}

* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    font-family: 'Cairo', 'Segoe UI', Tahoma, -apple-system, sans-serif;
    color: #1e293b;
    background: #ffffff;
    font-size: 10pt;
    line-height: 1.65;
    direction: rtl;
    text-align: right;
}

/* Page Break Controls */
.page-break {
    page-break-before: always;
}

.no-break {
    page-break-inside: avoid;
}

/* Cover Page */
.cover-page {
    height: 100vh;
    padding: 60px 45px;
    background: linear-gradient(135deg, #090d16 0%, #0f172a 50%, #1e1b4b 100%);
    color: #f8fafc;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
    page-break-after: always;
}

.cover-header {
    border-bottom: 2px solid rgba(14, 165, 233, 0.4);
    padding-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.cover-badge {
    display: inline-block;
    background: rgba(14, 165, 233, 0.2);
    color: #38bdf8;
    border: 1px solid rgba(14, 165, 233, 0.5);
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 1px;
}

.cover-title-box {
    margin: 40px 0;
}

.cover-title-en {
    font-size: 24pt;
    font-weight: 800;
    color: #38bdf8;
    line-height: 1.25;
    margin: 0 0 12px 0;
    font-family: 'Segoe UI', sans-serif;
    direction: ltr;
    text-align: right;
    letter-spacing: -0.5px;
}

.cover-title-ar {
    font-size: 20pt;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1.35;
    margin: 0 0 20px 0;
}

.cover-subtitle {
    font-size: 13pt;
    color: #94a3b8;
    margin: 0 0 15px 0;
    font-weight: 600;
}

.cover-meta-grid {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(51, 65, 85, 0.8);
    border-radius: 10px;
    padding: 20px 25px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    backdrop-filter: blur(8px);
}

.cover-meta-item {
    display: flex;
    flex-direction: column;
}

.cover-meta-label {
    font-size: 8pt;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
}

.cover-meta-val {
    font-size: 10.5pt;
    color: #f1f5f9;
    font-weight: 700;
}

.cover-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(51, 65, 85, 0.5);
    padding-top: 20px;
    font-size: 8.5pt;
    color: #64748b;
}

/* Headings */
h1 {
    font-size: 18pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 8px;
    margin-top: 25px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #0369a1;
    margin-top: 20px;
    margin-bottom: 12px;
    border-right: 4px solid #0284c7;
    padding-right: 10px;
}

h3 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 16px;
    margin-bottom: 8px;
}

h4 {
    font-size: 10pt;
    font-weight: 700;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 6px;
}

/* Section Header Badges */
.section-badge {
    display: inline-block;
    font-size: 8pt;
    padding: 3px 8px;
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 4px;
    font-weight: bold;
    margin-left: 8px;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    text-transform: uppercase;
}
.badge-crit { background: #fee2e2; color: #b91c1c; border: 1px solid #f87171; }
.badge-high { background: #ffedd5; color: #c2410c; border: 1px solid #fb923c; }
.badge-med  { background: #fef9c3; color: #a16207; border: 1px solid #facc15; }
.badge-low  { background: #dcfce7; color: #15803d; border: 1px solid #4ade80; }
.badge-ok   { background: #e0f2fe; color: #0369a1; border: 1px solid #38bdf8; }
.badge-arch { background: #f3e8ff; color: #6b21a8; border: 1px solid #c084fc; }

/* Callout Alert Boxes */
.alert-box {
    margin: 14px 0;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 9.5pt;
    border-right: 5px solid;
    page-break-inside: avoid;
}

.alert-note {
    background: #f0f9ff;
    border-color: #0284c7;
    color: #075985;
}

.alert-tip {
    background: #f0fdf4;
    border-color: #16a34a;
    color: #166534;
}

.alert-warn {
    background: #fffbeb;
    border-color: #d97706;
    color: #92400e;
}

.alert-crit {
    background: #fef2f2;
    border-color: #dc2626;
    color: #991b1b;
}

.alert-title {
    font-weight: 700;
    font-size: 10pt;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 8.5pt;
    page-break-inside: auto;
}

tr {
    page-break-inside: avoid;
    page-break-after: auto;
}

th, td {
    padding: 7px 10px;
    border: 1px solid #cbd5e1;
    text-align: right;
    vertical-align: middle;
}

th {
    background: #0f172a;
    color: #f8fafc;
    font-weight: 700;
    font-size: 8.5pt;
}

tr:nth-child(even) {
    background: #f8fafc;
}

tr:hover {
    background: #f1f5f9;
}

/* Code Blocks */
pre, .code-block {
    background: #0f172a;
    color: #f1f5f9;
    padding: 12px 16px;
    border-radius: 8px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 8pt;
    line-height: 1.5;
    direction: ltr;
    text-align: left;
    overflow-x: auto;
    border: 1px solid #334155;
    margin: 12px 0;
    page-break-inside: avoid;
}

code {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    direction: ltr;
    display: inline-block;
    border: 1px solid #e2e8f0;
}

/* Architecture & SVG Diagrams Container */
.diagram-container {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
    text-align: center;
    page-break-inside: avoid;
}

.diagram-caption {
    font-size: 8.5pt;
    font-weight: 700;
    color: #475569;
    margin-top: 8px;
}

/* Cards & Grids */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin: 12px 0;
    page-break-inside: avoid;
}

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 12px 0;
    page-break-inside: avoid;
}

.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.card-title {
    font-weight: 700;
    color: #0369a1;
    font-size: 9.5pt;
    margin-bottom: 6px;
}

/* Document Header/Footer Running simulation */
.doc-running-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7.5pt;
    color: #94a3b8;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    margin-bottom: 16px;
}

.doc-running-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7.5pt;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    padding-top: 6px;
    margin-top: 20px;
}
"""
