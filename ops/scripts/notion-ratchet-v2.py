#!/usr/bin/env python3
"""Upgrade the RATCHET Notion page with the refined GTC + GR00T-repo stack.
Appends a 'v2 refined stack' section (Unitree H2 reference, Cosmos 3 data flywheel,
Isaac Lab 3.0, GR00T N2 watch, GR00T-H healthcare, request-tracing lane) to the existing page.
Uses the auth.json token (owns the CTO Suite). Verifies read-back.
"""
import os, json, requests

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
# the RATCHET project page created earlier
PAGE = "3d0a9b14-e498-8151-a6fb-ceae9d9d4065"

def api(path, method="GET", body=None):
    r = requests.request(method, API + path, headers=HDR, json=body, timeout=40)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:260]}")
    return r.json()

def _t(t): return [{"type": "text", "text": {"content": t}}]
def para(t): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _t(t)}}
def head(t, l=2): return {"object": "block", "type": f"heading_{l}", f"heading_{l}": {"rich_text": _t(t)}}
def bullet(t): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": _t(t)}}
def callout(t, e="🤖"): return {"object": "block", "type": "callout", "callout": {"rich_text": _t(t), "icon": {"type": "emoji", "emoji": e}}}
def code(t): return {"object": "block", "type": "code", "code": {"rich_text": _t(t), "language": "text"}}
def divider(): return {"object": "block", "type": "divider", "divider": {}}

B = [
    divider(),
    callout("RATCHET v2 — refined stack after NVIDIA GTC 2026 keynote + Isaac GR00T repo deep-dive. Same mission, upgraded build plan.", "🚀"),
    head("Refined policy target (supersedes G1/AGIBot list)", 2),
    bullet("**Isaac GR00T Reference Humanoid** — Unitree H2 (6ft, 31-DoF body) + Sharpa tactile 5-finger hands (22-DoF) = 75-DoF total, on Jetson AGX Thor T5000 (2,070 FP4 TFLOPS, 128GB unified). The single open reference design. P3 embodiment target."),
    bullet("Whole-body control via GEAR-SONIC (`UNITREE_G1_SONIC` tag): VLA predicts latent action tokens → learned whole-body controller decodes to full-body joint cmds (legs+arms+hands)."),
    bullet("GR00T N2 (preview, DreamZero world-action model, #1 RoboArena, 2× better) — **WATCH, don't build on N1.7 yet.** Keep RATCHET on the GR00T line; evaluate N2 at GA."),
    head("Data flywheel (the hard problem — now solvable)", 2),
    bullet("**Cosmos 3** world foundation model — synthetic world generation + vision reasoning + action simulation. Generate diverse long-tail robot data from limited real inputs."),
    bullet("**Physical AI Data Factory Blueprint** — open reference architecture: compute → large-scale training data (curation, augmentation, evaluation in one pipeline)."),
    bullet("**Isaac Lab 3.0** — Newton physics engine 1.0, multiphysics, dexterous manipulation, faster large-scale robot learning on DGX-class infra."),
    bullet("GR00T data format = LeRobot v2 + `meta/modality.json`. Use `scripts/lerobot_conversion` for v3→v2. Demo datasets ship ready (DROID, LIBERO, SimplerEnv, SO100)."),
    head("Capabilities mined from the GR00T repo (adoptable today)", 2),
    bullet("**Teleop data capture** (VR teleoperation, SONIC) → demo collection for training; Isaac Teleop for high-quality demos."),
    bullet("**NEW_EMBODIMENT** path — finetune GR00T on our own robot via `--modality-config-path`. Single-GPU OK; 8×H100 for scale. ~2,000+ trajs for high-DoF humanoid."),
    bullet("**Server-client inference** (ZMQ) for real deployment — policy on GPU server, light client gets actions. TensorRT/ONNX export for edge. `--execution-horizon`."),
    bullet("**Deployment matrix:** dGPU (CUDA 12.8) · DGX Spark · Jetson Thor/Orin (JetPack 7.2) — matches our DGX Spark. FFmpeg <8 + torchcodec gotcha; `patch_triton_cuda13.sh` for CUDA 13."),
    bullet("**Mask-guided background suppression**, multi-dataset mixture weights, state-dropout prob for robustness — all in the finetune config."),
    bullet("**LeRobot/HuggingFace integration** — trains/eval/rollout via LeRobot; connects NVIDIA's 2M devs to HF's 13M builders."),
    head("Healthcare-robotics lane (DIRECT NURA domain)", 2),
    bullet("**GR00T-H** — clinical VLA: text → motion commands for healthcare robots. **Cosmos-H** — synthetic surgical video gen. **Rheo** — hospital simulation blueprint. **Open-H** — surgical video dataset. All on GitHub/HuggingFace."),
    bullet("PeritasAI + Advent Health already training humanoid surgical robots on Isaac. This is the near-term, open, buildable path for NURA's clinical/EMS robotics."),
    head("Tracing/audit lane (the gap to close, from Logging vs Tracing)", 2),
    bullet("**Non-negotiable before clinical agents ship**: every model call → tool → retrieval → agent decision traceable end-to-end (RadIntel 'event spine' + 'black-box logged')."),
    bullet("This is the #1 build from the AI Eng Fundamentals 7-pairs (Logging vs Tracing). Logs record events; a trace follows the whole request so you can audit exactly what happened over a patient."),
    bullet("Implementation: wrap each agent/tool/retrieval call with a trace-id span → emit to an audit store (Qdrant/Postgres) keyed by run/patient/decision. Slot into the existing event backbone."),
    head("Decision: assimilate, don't compete", 2),
    bullet("NVIDIA owns the generalist robot base model race — the compute/data to compete there is theirs. NURA's defensible IP = clinical/EMS embodiment + data + workflow on top of the open base (GR00T N2 + Cosmos 3 + Isaac Lab 3.0). Borg-assimilation."),
    bullet("No lock-in: Nemotron/Cosmos/GR00T/Alpamayo/BioNeMo/Earth-2 open model coalition. RATCHET's reasoning/brain stays NURA Agent OS (Hermes runtime); GR00T = the embodied policy body."),
]

# append blocks to the existing page
api(f"/blocks/{PAGE}/children", "PATCH", {"children": B})
print("appended", len(B), "blocks to RATCHET page")

# verify read-back
r = api(f"/blocks/{PAGE}/children")
bl = r.get("results", [])
print("total children now:", len(bl))
for b in bl[-8:]:
    bt = b.get("type"); rt = b.get(bt, {}).get("rich_text", [])
    txt = "".join(x.get("plain_text","") for x in rt)
    if txt:
        print("  ", txt[:70])
