#!/usr/bin/env python3
"""Create the RATCHET project page in Notion (CTO Suite) — NURA first humanoid blueprint.
Uses the auth.json (Notion CLI) token, which owns the CTO Suite DBs. Verifies read-back.
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
CTO_SUITE = "3bea9b14-e498-816e-84c5-d9cda0497f87"   # NURA-Engineering-CTO-Suite
HDR = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VER, "Content-Type": "application/json"}
API = "https://api.notion.com/v1"

def api(path, method, body=None):
    r = requests.request(method, API + path, headers=HDR, json=body, timeout=40)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:260]}")
    return r.json()

def _t(text):
    return [{"type": "text", "text": {"content": text}}]

def para(t):  return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _t(t)}}
def head(t, l): return {"object": "block", "type": f"heading_{l}", f"heading_{l}": {"rich_text": _t(t)}}
def bullet(t): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": _t(t)}}
def num(t):  return {"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": _t(t)}}
def callout(t, emoji="🏗"): return {"object": "block", "type": "callout", "callout": {"rich_text": _t(t), "icon": {"type": "emoji", "emoji": emoji}}}
def code(t, lang="text"): return {"object": "block", "type": "code", "code": {"rich_text": _t(t), "language": lang}}
def divider(): return {"object": "block", "type": "divider", "divider": {}}

TITLE = "RATCHET — NURA Humanoid v1 (Embodied AI for EMS/Field Ops)"
B = [
    callout("RATCHET: the embodied-AI layer for NURA field ops. NURA Agent OS = the brain; Hermes = the interchangeable runtime; RATCHET = the humanoid/robotic body & policy. NUR-59.","🤖"),
    head("Mission", 2),
    para("Build and field NURA's first humanoid as a governed, safety-first embodied agent — using an open generalist foundation model (GR00T) as the policy body, the NURA Agent OS as the reasoning brain, and a hard safety kernel the model can never override. Deploys sim-first; real-world motion is gated."),
    head("Architecture (component map)", 2),
    num("Policy / body — NVIDIA Isaac GR00T N1.7 (open VLA, Apache-2.0 code, commercial-licensable weights)"),
    num("Brain / reasoning — NURA Agent OS + Hermes runtime (task decomposition, multi-step planning, mission context)"),
    num("Safety kernel — independent supervisor; e-stop, geofence, torque/force limits, human override. LLM CANNOT override."),
    num("Sim + RL — Isaac Lab + Newton + COMPASS (sim-to-real, zero-shot transfer, stress-tested before deploy)"),
    num("Perception — ego camera + stereo + proprioceptive joints; cuVSLAM/cuVGL localization in the field"),
    num("Data flywheel — every permitted sim/traj/failure/human-correction → structured eval + training data"),
    head("GR00T N1.7 integration (the build-on decision)", 2),
    bullet("3B VLA; AI inputs = RGB + language + joint state → action chunks. Relative-EEF action space (cross-embodiment)."),
    bullet("20k-hr EgoScale human-video pretraining → dexterity scaling law (22-DoF hands, contact-rich tasks)."),
    bullet("Action Cascade: System-2 (Cosmos-Reason2-2B VLM) reasons/decomposes → System-1 (diffusion) denoises motor commands."),
    bullet("NOT a reasoning/VQA model (that's future N2) — use it to DO. The thinking stays in the NURA Agent OS brain. This is the intended split."),
    bullet("License gate set: we assimilate the open base, own the NURA integration/clinical-EMS data + workflows as defensible IP."),
    head("First-humanoid hardware (embodiment)", 2),
    bullet("Policy layer targets GR00T pre-registered embodiments: Unitree G1, AGIBot Genie-1, Fourier GR-1."),
    bullet("Whole-body control via GR00T-WholeBodyControl controller (legs+arms+hands, coordinated locomotion+manipulation)."),
    bullet("Edge inference: DGX Spark (ours) or Jetson AGX Thor — 16GB+ VRAM for inference (feasible on our stack)."),
    bullet("Fine-tune (40GB+ VRAM) = rented node (RunPod) or time-boxed; ~2,000+ trajs for high-DoF humanoid tasks."),
    head("Safety & authorization (non-negotiable)", 2),
    bullet("Safety kernel independent of the policy; hard e-stop + limits; human override absolute."),
    bullet("SIM-FIRST: validate in Isaac Lab/Arena before any real-robot motion. No sim pass = no deploy."),
    bullet("Separation of tracks: clinical autonomy, robotics autonomy, corporate automation ≠ one authorization envelope."),
    bullet("Field-ops (EMS) use = provider-gated/supervisor-gated; every physical action black-box logged + auditable."),
    head("Phase plan", 2),
    bullet("P0 — Research gate: clone GR00T (submodules) + HF access + DGX Spark inference spike (build-on proof)"),
    bullet("P1 — Sim: Isaac Lab policy eval on a tracked embodiment; register RATCHET in the AI product registry"),
    bullet("P2 — Data: first humanoid trajectory set + human-video pretraining bridge; dexterity baseline"),
    bullet("P3 — Embodiment: fine-tune to v1 configuration; sim-to-real transfer to the first humanoid"),
    bullet("P4 — Field: supervised field-ops pilot (EMS aid delivery), safety-kernel-gated, auditable rollout"),
    head("Status", 2),
    bullet("P0 — Scoping (research gate + DGX Spark inference spike next). Owner: Hermes (CTO). Priority: P1. NUR-59."),
    divider(),
    para("Registry: run as candidate lane in docs/AI-Product-Registry.md + docs/CTO-Session-Ledger. All sources keyless; GR00T gated model needs HF_TOKEN."),
]

def create_page(parent_id, title, blocks):
    body = {"parent": {"page_id": parent_id},
            "properties": {"title": {"title": _t(title)}},
            "children": blocks[:100]}
    return api("/pages", "POST", body)

out = create_page(CTO_SUITE, TITLE, B)
pid = out.get("id")
print(json.dumps({"ok": True, "id": pid, "url": out.get("url")}, indent=2))

# verify read-back
if pid:
    r = api(f"/blocks/{pid}/children", "GET")
    bl = r.get("results", [])
    print("read-back blocks:", len(bl))
    for b in bl[:6]:
        bt = b.get("type")
        rt = b.get(bt, {}).get("rich_text", [])
        txt = "".join(x.get("plain_text","") for x in rt)
        print(f"  [{bt}] {txt[:70]}")
