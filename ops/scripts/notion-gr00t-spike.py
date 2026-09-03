#!/usr/bin/env python3
"""1) Append GR00T staged-state to the RATCHET Notion page.
2) Add an actionable 'run GR00T inference on GPU box' task to the Master Tasks DB.
Both via auth.json token. Verifies read-back."""
import os, json, sys, importlib.util
import requests

def _token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return next(iter(d.values()))
    for k in ("NOTION_API_TOKEN", "NOTION_PAT_NURATECH"):
        v = os.environ.get(k)
        if v:
            return v
    raise SystemExit("no token")

TOKEN = _token()
VER = "2022-06-28"
HDR = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VER, "Content-Type": "application/json"}
API = "https://api.notion.com/v1"
PAGE = "3d0a9b14-e498-8151-a6fb-ceae9d9d4065"  # RATCHET project page

def api(path, method="GET", body=None):
    r = requests.request(method, API + path, headers=HDR, json=body, timeout=40)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:260]}")
    return r.json()

def _t(t): return [{"type": "text", "text": {"content": t}}]
def para(t): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _t(t)}}
def head(t, l=2): return {"object": "block", "type": f"heading_{l}", f"heading_{l}": {"rich_text": _t(t)}}
def bullet(t): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": _t(t)}}
def callout(t, e="📦"): return {"object": "block", "type": "callout", "callout": {"rich_text": _t(t), "icon": {"type": "emoji", "emoji": e}}}
def code(t): return {"object": "block", "type": "code", "code": {"rich_text": _t(t), "language": "bash"}}
def divider(): return {"object": "block", "type": "divider", "divider": {}}

# --- 1) append staged-state to RATCHET page ---
B = [
    divider(),
    callout("GR00T P0 SPIKE — staged on the control host; inference GATED on GPU hardware (DGX Spark / CUDA dGPU). This host is x86_64 CPU-only and cannot run the model.", "⚠️"),
    head("Spike status (09-03, verify-before-declare)", 2),
    bullet("**Staged (done, verified):** GR00T `N1.7` repo cloned to `/opt/data/isaac-gr00t` (27MB, submodule blueprint read). HF access confirmed — token returns 200/200 on both gated models (`nvidia/GR00T-N1.7-3B` + `nvidia/Cosmos-Reason2-2B`). Fine-tune data → B2 (`nura-datasets`), checkpoints → B2 (`nura-models`)."),
    bullet("**GATED (hardware boundary):** inference requires a GPU box. Verified this host is `x86_64 CPU-only` (no GPU) and the repo's Spark install script hard-exits unless `ARCH == aarch64`. Cannot run here — not fabricated."),
    code("# on the GPU box (DGX Spark aarch64 or CUDA dGPU):\nbash scripts/deployment/spark/install_deps.sh   # or dgpu/install_deps.sh\nsource scripts/activate_spark.sh\npython scripts/deployment/standalone_inference_script.py \\\n  --model-path nvidia/GR00T-N1.7-3B \\\n  --dataset-path demo_data/droid_sample \\\n  --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \\\n  --execution-horizon 8"),
    bullet("**Next action:** provide DGX Spark / GPU host access → run the spike (one command set), then proceed to P1 sim (Isaac Lab) eval."),
]

# --- 2) add a task to the Master Tasks DB ---
spec = importlib.util.spec_from_file_location("nte", "/opt/data/scripts/notion_exec_tools.py")
nte = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nte)
task = nte._add_task(
    title="Run GR00T inference spike on the GPU box (DGX Spark aarch64 or CUDA dGPU) — GR00T N1.7 cloned + staged on control host; HF access confirmed. One command set (install_deps.sh + standalone_inference_script.py).",
    status="To Do", priority="P1", owner="Eddie", source="Decision", project="RATCHET", commitment=True,
)

# --- apply page update ---
api(f"/blocks/{PAGE}/children", "PATCH", {"children": B})
print("appended", len(B), "blocks to RATCHET page")
r = api(f"/blocks/{PAGE}/children")
print("total children:", len(r.get("results", [])))
print("task:", json.dumps(task, default=str)[:160])
