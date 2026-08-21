"""One-time extraction: PrimaryCare MA RAF V28 workbook -> JSON sidecar for nura-coding-agent.py.

Run:  uv run --with openpyxl nura-coding-ref-extract.py [out.json]
Defaults to the sidecar next to nura-coding-agent.py.
"""
import openpyxl, json, sys, os

XLSX = "/opt/data/profiles/nura/cache/documents/doc_28a3a6c42fe8_PrimaryCare_MA_RAF_V28_LLM_Reference.xlsx"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "nura-coding-ref.json")

wb = openpyxl.load_workbook(XLSX, data_only=True)

def dump(name, max_col):
    ws = wb[name]
    out = []
    for row in ws.iter_rows(min_row=1, values_only=True):
        cells = [("" if c is None else str(c).strip()) for c in row[:max_col]]
        if any(cells):
            out.append(cells)
    return out

sheets = {
    "quick_reference": dump("\U0001FA7A Quick Reference", 10),
    "icd10_hcc_map": dump("\U0001F4CB ICD-10 \u2192 HCC Mapping", 8),
    "v28_traps": dump("\U0001F6AB V28 Traps \u2014 No Longer Counts", 7),
    "interactions": dump("\u2795 RAF Interaction Bonuses", 6),
    "prompt_library": dump("\U0001F9E0 Clinical Prompt Library", 5),
    "tips_warnings": dump("\u26A0\uFE0F Coding Tips & Warnings", 6),
    "guardrails": dump("\U0001F6E1\uFE0F Compliance Guardrails", 4),
    "meat_guide": dump("\U0001F4DD MEAT Documentation Guide", 8),
}
with open(OUT, "w") as f:
    json.dump(sheets, f, indent=1, ensure_ascii=False)
print(json.dumps({k: len(v) for k, v in sheets.items()}, indent=1))
print("saved:", OUT)
