"""
Master compiler script to generate all 7 professional enterprise PDF documents.
Uses Microsoft Edge headless new engine for high-resolution vector rendering and proper Arabic RTL shaping.
"""

import os
import sys
import subprocess
import zlib
import re

# Ensure workspace root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from build_docs.doc1_master_guide import get_html_content as get_doc1
from build_docs.doc2_sadjad_guide import get_html_content as get_doc2
from build_docs.doc3_ali_guide import get_html_content as get_doc3
from build_docs.doc4_yousif_guide import get_html_content as get_doc4
from build_docs.doc5_ammar_guide import get_html_content as get_doc5
from build_docs.doc6_integration_map import get_html_content as get_doc6
from build_docs.doc7_development_roadmap import get_html_content as get_doc7

DOCS = [
    ("TEAM_MASTER_GUIDE.pdf", get_doc1),
    ("SADJAD_TEAM_LEADER_GUIDE.pdf", get_doc2),
    ("ALI_DEVELOPER_GUIDE.pdf", get_doc3),
    ("YOUSIF_DEVELOPER_GUIDE.pdf", get_doc4),
    ("AMMAR_DEVELOPER_GUIDE.pdf", get_doc5),
    ("TEAM_INTEGRATION_MAP.pdf", get_doc6),
    ("TEAM_DEVELOPMENT_ROADMAP.pdf", get_doc7),
]

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "TEAM_DOCUMENTATION")
TEMP_DIR = os.path.join(CURRENT_DIR, "temp_html")


def count_pdf_pages(pdf_path: str) -> int:
    try:
        with open(pdf_path, "rb") as f:
            data = f.read()
        streams = re.findall(rb"stream[\r\n]+(.*?)[\r\n]+endstream", data, re.DOTALL)
        decompressed = b""
        for s in streams:
            try:
                decompressed += zlib.decompress(s)
            except Exception:
                pass
        return len(re.findall(rb"/Type\s*/Page\b", data + decompressed))
    except Exception as e:
        print(f"Error counting pages for {pdf_path}: {e}")
        return 0


def compile_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    print("=" * 70)
    print("STARTING BATCH PDF COMPILATION VIA HEADLESS CHROMIUM/EDGE")
    print("=" * 70)

    results = []

    for filename, generator_func in DOCS:
        print(f"\n[BUILD] Generating HTML for {filename}...")
        html_content = generator_func()
        temp_html_path = os.path.join(TEMP_DIR, f"{filename}.html")
        out_pdf_path = os.path.join(OUTPUT_DIR, filename)

        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[PRINT] Rendering to PDF: {filename}...")
        cmd = [
            EDGE_PATH,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf_path}",
            temp_html_path,
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[ERROR] Edge returned error code {res.returncode}: {res.stderr}")
            results.append((filename, False, 0, 0))
            continue

        if os.path.exists(out_pdf_path) and os.path.getsize(out_pdf_path) > 0:
            size_bytes = os.path.getsize(out_pdf_path)
            pages = count_pdf_pages(out_pdf_path)
            print(
                f"[SUCCESS] {filename} created: {size_bytes / 1024:.1f} KB, {pages} pages"
            )
            results.append((filename, True, size_bytes, pages))
        else:
            print(f"[ERROR] PDF not created or empty: {filename}")
            results.append((filename, False, 0, 0))

    # Cleanup temp HTML files
    for f in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, f))
        except Exception:
            pass
    try:
        os.rmdir(TEMP_DIR)
    except Exception:
        pass

    print("\n" + "=" * 70)
    print("SUMMARY OF GENERATED DOCUMENTATION PACKAGE")
    print("=" * 70)
    total_pages = 0
    total_size = 0
    all_ok = True

    for name, success, size, pages in results:
        status_str = "OK (VALID PDF)" if success else "FAILED"
        print(
            f"- {name:<32} | {status_str:<15} | Pages: {pages:>2} | Size: {size / 1024:>7.1f} KB"
        )
        if success:
            total_pages += pages
            total_size += size
        else:
            all_ok = False

    print("-" * 70)
    print(
        f"TOTAL: 7 Documents | Pages: {total_pages} | Total Size: {total_size / (1024 * 1024):.2f} MB"
    )
    print(f"OVERALL STATUS: {'ALL SUCCEEDED (100%)' if all_ok else 'SOME FAILED'}")
    print("=" * 70)


if __name__ == "__main__":
    compile_all()
