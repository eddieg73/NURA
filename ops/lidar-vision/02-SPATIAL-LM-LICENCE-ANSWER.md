# SPATIAL LM — IS THERE AN ALTERNATIVE TO META'S CODE?
Asked 2026-09-12. **Answer: no, you do not have to copy Meta's code.** Licences below read
from the actual LICENSE files, not the API's `spdx_id`.

---

## PERMISSIVELY LICENSED SPATIAL / 3D LANGUAGE MODELS — these exist

| Repo | ★ | License | What it is |
|---|---|---|---|
| **`InternRobotics/G2VLM`** | 354 | **Apache-2.0** ✅ | **CVPR 2026** — Geometry-Grounded VLM with unified 3D reconstruction and spatial reasoning. **Most current, clean licence.** |
| **`ZiyuGuo99/Point-Bind_Point-LLM`** | 465 | **MIT** ✅ | Aligns 3D point clouds with multi-modalities for LLMs. |
| **`PzySeere/MetaSpatial`** | 322 | **Apache-2.0** ✅ | **ICLR 2026** — RL to enhance 3D spatial reasoning in VLMs. |
| **`LaVi-Lab/Video-3D-LLM`** | 223 | **Apache-2.0** ✅ | CVPR 2025 — position-aware video representation for 3D. |
| **`W-Ted/N3D-VLM`** | 119 | **Apache-2.0** ✅ | Native 3D grounding for accurate spatial reasoning. |
| **`embodied-generalist` (LEO)** | 489 | **MIT** ✅ | ICML 2024 — embodied generalist agent in 3D world. |

**And the permissive general VLMs are far larger and more mature:**

| Repo | ★ | License |
|---|---|---|
| `OpenBMB/MiniCPM-V` | 26,359 | **Apache-2.0** ✅ |
| `QwenLM/Qwen3-VL` · `Qwen2.5-VL` | 19,935 | **Apache-2.0** ✅ |
| `OpenGVLab/InternVL` | 10,155 | **MIT** ✅ |
| `deepseek-ai/DeepSeek-VL2` | 5,373 | **MIT** ✅ |
| `facebookresearch/dinov2` | 13,322 | **Apache-2.0** ✅ |

**Blocked, for contrast:** `manycore-research/SpatialLM` (Llama 3.2 Community —
commercially usable but proprietary), `OpenRobotLab/PointLLM` (**no licence**),
`TangYuan96/MiniGPT-3D` (**no licence**).

So the premise of the question is wrong in a useful way: **there is a whole field of permissive
options, and SpatialLM is the *restricted* one, not the default.**

---

## BUT — the better answer is that we probably shouldn't use a spatial LM at all

A spatial LM asks a neural network to *interpret* geometry. For NURA that is the wrong shape of
solution, and not mainly for licensing reasons.

**The argument that actually decides it — auditability, not licence:**

> *"The model said the landing zone is clear"* — **not auditable.**
> *"The point cloud shows 0 returns below 1.2 m within a 3 m radius; ground-plane RANSAC inlier
> ratio 0.94; max obstacle height 0.11 m"* — **auditable.**

This is an EMS product on an aircraft, with a black box and FAA/audit expectations written into
its own spec. A neural net's spatial interpretation is not a defensible record for a
landing-zone clearance decision. **Deterministic geometry is.**

## The architecture that is both safer AND licence-clean

**Layer 1 — geometry, deterministic, on the Orin-Nano (0.9–few W):**
`Pointcept` (MIT) / `CSF` (Apache-2.0) / `patchwork` (MIT) compute the spatial facts as
**numbers and structured JSON**: ground plane, obstacle field, clearances, LZ bounds.
Real-time, auditable, permissive. **This is the safety layer, and no LLM is in it.**

**Layer 2 — semantics, LLM-facing (the part you consume):**
Render the point cloud (**BEV top-down, depth map, or a few synthetic views**) and pass that
image **plus the structured geometry** to a permissive VLM — `Qwen3-VL` (Apache-2.0) locally, or
your existing lane. It produces the narrative: *"driveway clear, one vehicle at north edge,
overhead wire crossing east-west at 4.2 m."*

**Why this is better on every axis:**

| | Spatial LM | Geometry + permissive VLM |
|---|---|---|
| Licence | Llama Community (proprietary, attribution duties) | **Apache-2.0 / MIT throughout** |
| Auditable | ✗ model interpretation | ✅ numeric, replayable |
| Real-time onboard | ✗ far too heavy for Orin-Nano | ✅ geometry is cheap |
| Local-first | ✗ | ✅ Qwen3-VL on the LAB Ollama lane |
| Clinical defensibility | weak | **strong** |
| "Built with Llama" entanglement in a clinical product | yes | **none** |

---

## RECOMMENDATION

1. **Do not build on SpatialLM.** Not because it's bad — it's the closest thing to the ask — but
   because it is proprietary *and* unauditable for a clearance decision. **Study the paper's
   architecture, implement the concept on permissive parts.**
2. **Layer 1 = deterministic geometry** (Pointcept/CSF/patchwork). This is the safety layer and it
   is fully open.
3. **Layer 2 = permissive VLM over a rendered point cloud + structured nouns.** Qwen3-VL or
   InternVL, local.
4. **If you want a genuine spatial-LM to evaluate**, the permissive ones to test are
   **`G2VLM`** (Apache-2.0, CVPR 2026) and **`LEO`** (MIT) — not Meta's.

**So: no, we don't copy Meta's code. We don't need to, and for a clinical EMS product we
shouldn't want to.**
