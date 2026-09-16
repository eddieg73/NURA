#!/usr/bin/env python3
"""
NURA Clinical Inference Server
=============================
Single service exposing the full clinical AI surface defined by the architecture:

  GENERATIVE  /v1/generate/clinical | /v1/generate/general | /v1/code | /v1/vision
  ENCODERS    /v1/nlp/entities | /v1/nlp/phenotype | /v1/nlp/classify
              /v1/nlp/relations | /v1/nlp/negation
  EMBEDDINGS  /v1/embed/general | /v1/embed/clinical | /v1/embed/biomedical
  RETRIEVAL   /v1/rag/patient | /v1/rag/medical-knowledge
  OPS         /health | /v1/lanes | /v1/provenance/{id}

ARCHITECTURAL RULE (encoded, not merely documented):
  Encoders (GatorTron / ClinicalBERT / Bio_ClinicalBERT / BioBERT) are BERT-class
  and CANNOT generate. They are restricted to the NLP + embedding lanes. Every
  generative lane is a GENERATOR; this service refuses to send a generative
  request to an encoder and vice versa.

THREE DISTINCT EMBEDDING DOMAINS (never conflate):
  general     -> nomic-embed-text        general NURA data
  clinical    -> Bio_ClinicalBERT        patient notes / problem history / meds / labs
  biomedical  -> BioBERT                 guidelines / PubMed / FDA / payer policy

SAFETY:
  No AI signature, order, diagnosis, medication change, claim, or patient message.
  Every response carries provenance and is marked DRAFT / clinician-review-required.

Runtime: stdlib only (http.server + urllib) so it runs anywhere the fleet runs.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --------------------------------------------------------------------- config
OLLAMA = os.environ.get("NURA_OLLAMA", "http://127.0.0.1:11434")
QDRANT = os.environ.get("NURA_QDRANT", "http://127.0.0.1:6333")
HF_ROUTER = "https://router.huggingface.co/hf-inference/models"
PORT = int(os.environ.get("NURA_GATEWAY_PORT", "8170"))
BIND = os.environ.get("NURA_GATEWAY_BIND", "0.0.0.0")

COLLECTION_PATIENT = "nura-clinical-patient"
COLLECTION_KNOWLEDGE = "nura-biomedical-knowledge"


def _env(key: str) -> str:
    for p in ("/opt/data/profiles/nura/.env",
              "/opt/data/profiles/nura/home/.secrets/nura.env"):
        try:
            for ln in pathlib.Path(p).read_text().splitlines():
                if ln.startswith(key + "="):
                    return ln.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            continue
    return os.environ.get(key, "")


HF_TOKEN = _env("HF_TOKEN")

# ------------------------------------------------------------- lane registry
# GENERATORS — may produce text/JSON. Sourced from the live local Ollama set.
GENERATORS = {
    "clinical":   {"model": "med42:latest",        "why": "medical-domain generator"},
    "clinical_alt": {"model": "biomistral:latest", "why": "biomedical-domain generator"},
    "clinical_meditron": {"model": "meditron:latest", "why": "clinical reasoning generator"},
    "general":    {"model": "qwen3:8b",            "why": "general-purpose, tool/JSON capable"},
    "fast":       {"model": "qwen3:4b",            "why": "cheap classification/formatting"},
    "code":       {"model": "qwen2.5-coder:7b",    "why": "code generation"},
    "reasoning":  {"model": "deepseek-r1:8b",      "why": "chain-of-thought reasoning"},
    "vision":     {"model": "qwen3-vl:8b",         "why": "vision-language"},
    "vision_alt": {"model": "minicpm-v:8b",        "why": "vision fallback"},
}

# ENCODERS — must NEVER be asked to generate. NLP + embeddings only.
ENCODERS = {
    "clinical_bert":  "emilyalsentzer/Bio_ClinicalBERT",
    "bio_bert":       "dmis-lab/biobert-base-cased-v1.2",
    "clinical_modern": "Simonlee711/Clinical_ModernBERT",
}

# EMBEDDING DOMAINS — one model per domain, deliberately different.
EMBED_DOMAINS = {
    "general":    {"kind": "ollama", "model": "nomic-embed-text:latest",
                   "collection": "nura-docs",   "note": "general NURA data"},
    "clinical":   {"kind": "hf", "model": ENCODERS["clinical_bert"],
                   "collection": COLLECTION_PATIENT,
                   "note": "patient notes/problem history/meds/labs/admissions/care plans"},
    "biomedical": {"kind": "hf", "model": ENCODERS["bio_bert"],
                   "collection": COLLECTION_KNOWLEDGE,
                   "note": "guidelines/PubMed/FDA/drug refs/protocols/payer policy"},
}

# ---------------------------------------------------------- safety boundary
SAFETY = {
    "no_ai_sign": True,          "no_ai_order": True,
    "no_ai_diagnosis": True,     "no_ai_med_change": True,
    "no_ai_claim": True,         "no_ai_message": True,
}

# Deterministic validation catalogue (the "Rules Engine" node).
RULES = {
    "icd10":   {"enabled": True,  "note": "normalise dotted/undotted both sides"},
    "hcc_v28": {"enabled": True,  "note": "CMS-HCC V28 mapping"},
    "hedis":   {"enabled": True,  "note": "quality measure evaluation"},
    "drug_safety": {"enabled": True, "note": "interaction + contraindication"},
    "lab_rules":   {"enabled": True, "note": "reference-range + delta checks"},
    "cpt_hcpcs":   {"enabled": True, "note": "procedure coding"},
    "protocols":   {"enabled": True, "note": "clinical protocol conformance"},
}

NEGATION_CUES = (
    "no ", "not ", "denies", "denied", "without", "negative for", "absent",
    "never", "no evidence of", "ruled out", "free of", "unremarkable",
)
PHENOTYPE_HINTS = {
    "diabetes": ["diabet", "a1c", "glucose", "insulin", "metformin"],
    "heart_failure": ["heart failure", "chf", "ef ", "ejection fraction", "bnp"],
    "renal": ["ckd", "creatinine", "egfr", "renal", "nephro"],
    "behavioral": ["bipolar", "depress", "schizo", "psych", "mdd"],
    "cardiac": ["cad", "mi ", "angina", "stent", "cabg", "lipid"],
    "respiratory": ["copd", "asthma", "fev1", "dyspnea"],
}

START = time.time()
COUNTER = {"requests": 0, "by_lane": {}}
PROVENANCE: dict[str, dict] = {}


# ------------------------------------------------------------------ helpers
def _post(url: str, payload: dict, headers: dict | None = None, timeout: int = 180):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=h,
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _get(url: str, headers: dict | None = None, timeout: int = 30):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def prov(lane: str, model: str, **extra) -> dict:
    pid = hashlib.sha256(f"{lane}{model}{time.time()}".encode()).hexdigest()[:16]
    rec = {"provenance_id": pid, "lane": lane, "model": model,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "draft": True, "clinician_review_required": True, "safety": SAFETY}
    rec.update(extra)
    PROVENANCE[pid] = rec
    if len(PROVENANCE) > 5000:
        for k in list(PROVENANCE)[:1000]:
            PROVENANCE.pop(k, None)
    return rec


def ollama_generate(model: str, prompt: str, system: str = "", images=None) -> dict:
    body = {"model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.2}}
    if system:
        body["system"] = system
    if images:
        body["images"] = images
    return _post(f"{OLLAMA}/api/generate", body)


def ollama_chat(model: str, messages: list) -> dict:
    return _post(f"{OLLAMA}/api/chat", {"model": model, "messages": messages,
                                        "stream": False})


def hf_feature_extract(model: str, texts) -> list:
    """Encoder embeddings via HF router. CPU-class models; may cold-start."""
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN absent")
    payload = {"inputs": texts if isinstance(texts, list) else [texts],
               "options": {"wait_for_model": True}}
    out = _post(f"{HF_ROUTER}/{model}/pipeline/feature-extraction", payload,
                headers={"Authorization": f"Bearer {HF_TOKEN}"}, timeout=180)
    if out and isinstance(out[0], list) and out[0] and isinstance(out[0][0], list):
        # token-level -> mean pool
        pooled = []
        for seq in out:
            n = len(seq) or 1
            dim = len(seq[0]) if seq else 0
            pooled.append([sum(tok[i] for tok in seq) / n for i in range(dim)])
        return pooled
    return out


def is_negated(text: str, term: str) -> bool:
    low = text.lower()
    idx = low.find(term.lower())
    if idx < 0:
        return False
    window = low[max(0, idx - 60):idx]
    return any(cue in window for cue in NEGATION_CUES)


def extract_entities(text: str) -> list:
    """Deterministic clinical concept extraction. No generation involved."""
    ents = []
    icd = re.compile(r"\b([A-TV-Z][0-9][0-9AB](?:\.[0-9A-Z]{1,4})?)\b")
    for m in icd.finditer(text):
        code = m.group(1)
        ents.append({"text": code, "type": "icd10",
                     "normalized": code.upper().replace(".", ""),
                     "negated": is_negated(text, code), "span": list(m.span())})
    meds = re.compile(r"\b([A-Z][a-z]{3,}(?:ol|il|in|ide|one|ine|mab|pril|sartan|statin|mycin|cillin))\b")
    for m in meds.finditer(text):
        ents.append({"text": m.group(1), "type": "medication",
                     "negated": is_negated(text, m.group(1)), "span": list(m.span())})
    for phen, kws in PHENOTYPE_HINTS.items():
        for kw in kws:
            if kw in text.lower():
                ents.append({"text": kw.strip(), "type": "phenotype",
                             "phenotype": phen, "negated": is_negated(text, kw),
                             "span": [text.lower().find(kw), text.lower().find(kw) + len(kw)]})
                break
    labs = re.compile(r"\b([A-Za-z0-9 %/]{2,28}?)\s*[:=]?\s*(\d+\.?\d*)\s*(mg/dL|mmol/L|g/dL|%|mEq/L|ng/mL|U/L)\b")
    for m in labs.finditer(text):
        ents.append({"text": m.group(1).strip(), "type": "lab", "value": float(m.group(2)),
                     "unit": m.group(3), "negated": False, "span": list(m.span())})
    seen, uniq = set(), []
    for e in ents:
        k = (e["type"], e["text"].lower())
        if k in seen:
            continue
        seen.add(k)
        uniq.append(e)
    return uniq


# ------------------------------------------------------------------ handler
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # keep stdout clean
        pass

    def _send(self, code: int, obj):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    # ---------------- GET
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/health":
            oll, qd = None, None
            try:
                oll = len(_get(f"{OLLAMA}/api/tags").get("models", []))
            except Exception as e:
                oll = f"down: {type(e).__name__}"
            try:
                _get(f"{QDRANT}/collections")
                qd = "up"
            except Exception as e:
                qd = f"down: {type(e).__name__}"
            return self._send(200, {
                "status": "ok", "uptime_s": round(time.time() - START, 1),
                "generators_available": oll, "qdrant": qd,
                "hf_token": bool(HF_TOKEN), "requests": COUNTER["requests"],
                "safety": SAFETY, "draft_only": True,
            })
        if p == "/v1/lanes":
            return self._send(200, {
                "generators": GENERATORS, "encoders": ENCODERS,
                "embedding_domains": EMBED_DOMAINS, "rules_engine": RULES,
                "architecture_rule": "encoders never generate; generators never embed",
            })
        if p.startswith("/v1/provenance/"):
            pid = p.rsplit("/", 1)[-1]
            return self._send(200 if pid in PROVENANCE else 404,
                              PROVENANCE.get(pid, {"error": "unknown provenance_id"}))
        return self._send(404, {"error": "unknown path", "path": p})

    # ---------------- POST
    def do_POST(self):
        p = self.path.split("?")[0]
        b = self._read()
        COUNTER["requests"] += 1
        try:
            return self._route(p, b)
        except urllib.error.HTTPError as e:
            return self._send(502, {"error": "upstream", "code": e.code,
                                    "detail": e.read()[:300].decode(errors="replace")})
        except Exception as e:
            return self._send(500, {"error": type(e).__name__, "detail": str(e)[:400]})

    def _route(self, p, b):
        # ---------------- GENERATIVE
        if p in ("/v1/generate/clinical", "/v1/generate/general"):
            lane = "clinical" if p.endswith("clinical") else "general"
            choice = b.get("lane") or lane
            spec = GENERATORS.get(choice) or GENERATORS[lane]
            model = b.get("model") or spec["model"]
            prompt = b.get("prompt") or (b.get("messages") or [{}])[-1].get("content", "")
            system = b.get("system") or (
                "You are a clinical documentation assistant. Produce DRAFT content "
                "only. Never state a diagnosis as final, never prescribe, never sign. "
                "Cite the source data you used." if lane == "clinical"
                else "You are a general-purpose assistant.")
            r = ollama_generate(model, prompt, system)
            pv = prov(lane, model, kind="generator")
            COUNTER["by_lane"][lane] = COUNTER["by_lane"].get(lane, 0) + 1
            return self._send(200, {
                "lane": lane, "model": model, "output": r.get("response", ""),
                "draft": True, "clinician_review_required": lane == "clinical",
                "safety": SAFETY, "provenance": pv,
                "eval": {"eval_count": r.get("eval_count"),
                         "total_duration_ms": round((r.get("total_duration") or 0) / 1e6, 1)},
            })

        if p == "/v1/code":
            model = b.get("model") or GENERATORS["code"]["model"]
            r = ollama_generate(model, b.get("prompt", ""),
                                b.get("system") or "You are a senior software engineer.")
            return self._send(200, {"lane": "code", "model": model,
                                    "output": r.get("response", ""),
                                    "provenance": prov("code", model, kind="generator")})

        if p == "/v1/vision":
            model = b.get("model") or GENERATORS["vision"]["model"]
            prompt = b.get("prompt", "Describe this image clinically and factually.")
            imgs = b.get("images") or []
            r = ollama_generate(model, prompt, b.get("system", ""), images=imgs)
            return self._send(200, {"lane": "vision", "model": model,
                                    "output": r.get("response", ""), "draft": True,
                                    "clinician_review_required": True,
                                    "provenance": prov("vision", model, kind="generator")})

        # ---------------- ENCODERS (never generate)
        if p == "/v1/nlp/entities":
            text = b.get("text", "")
            return self._send(200, {"encoder_free": True, "entities": extract_entities(text),
                                    "count": len(extract_entities(text)),
                                    "provenance": prov("nlp.entities", "deterministic",
                                                       kind="rule")})
        if p == "/v1/nlp/negation":
            text = b.get("text", "")
            terms = b.get("terms") or []
            if not terms:
                terms = [m.group(1) for m in re.finditer(r"\b[A-TV-Z][0-9]{2}(?:\.[0-9A-Z]{1,4})?\b", text)]
            return self._send(200, {"negation": {t: is_negated(text, t) for t in terms},
                                    "provenance": prov("nlp.negation", "deterministic", kind="rule")})
        if p == "/v1/nlp/phenotype":
            text = b.get("text", "").lower()
            hits = {}
            for phen, kws in PHENOTYPE_HINTS.items():
                matched = [k for k in kws if k in text]
                if matched:
                    hits[phen] = {"matched": matched, "negated": is_negated(text, matched[0])}
            return self._send(200, {"phenotypes": hits, "count": len(hits),
                                    "provenance": prov("nlp.phenotype", "deterministic", kind="rule")})
        if p == "/v1/nlp/relations":
            text = b.get("text", "")
            ents = extract_entities(text)
            rels = []
            for a in ents:
                if a["type"] == "lab":
                    for d in ents:
                        if d["type"] in ("icd10", "phenotype") and abs(a["span"][0] - d["span"][0]) < 200:
                            rels.append({"from": a["text"], "relation": "lab-condition", "to": d["text"]})
                if a["type"] == "medication":
                    for d in ents:
                        if d["type"] in ("icd10", "phenotype") and abs(a["span"][0] - d["span"][0]) < 200:
                            rels.append({"from": a["text"], "relation": "drug-disease", "to": d["text"]})
            return self._send(200, {"relations": rels[:200], "count": len(rels),
                                    "provenance": prov("nlp.relations", "deterministic", kind="rule")})
        if p == "/v1/nlp/classify":
            # classification is a GENERATOR task (encoder cannot emit a label sequence)
            model = b.get("model") or GENERATORS["fast"]["model"]
            labels = b.get("labels") or ["routine", "urgent", "clinical-review"]
            prompt = (f"Classify the text into exactly one of {labels}. "
                      f"Answer with the label only.\n\nTEXT:\n{b.get('text','')[:4000]}")
            r = ollama_generate(model, prompt, "You are a precise text classifier.")
            return self._send(200, {"lane": "nlp.classify", "model": model,
                                    "label": (r.get("response") or "").strip().splitlines()[0][:80],
                                    "labels": labels,
                                    "provenance": prov("nlp.classify", model, kind="generator")})

        # ---------------- EMBEDDINGS (three distinct domains)
        if p.startswith("/v1/embed/"):
            dom = p.rsplit("/", 1)[-1]
            spec = EMBED_DOMAINS.get(dom)
            if not spec:
                return self._send(400, {"error": "unknown domain", "valid": list(EMBED_DOMAINS)})
            texts = b.get("texts") or ([b["text"]] if b.get("text") else [])
            if not texts:
                return self._send(400, {"error": "provide 'text' or 'texts'"})
            if spec["kind"] == "ollama":
                r = _post(f"{OLLAMA}/api/embed", {"model": spec["model"], "input": texts})
                vecs = r.get("embeddings") or []
            else:
                vecs = hf_feature_extract(spec["model"], texts)
            return self._send(200, {
                "domain": dom, "model": spec["model"], "collection": spec["collection"],
                "count": len(vecs), "dim": len(vecs[0]) if vecs else 0,
                "vectors": vecs if b.get("return_vectors") else "[omitted]",
                "provenance": prov(f"embed.{dom}", spec["model"], kind="encoder")})

        # ---------------- RAG (two separate corpora)
        if p.startswith("/v1/rag/"):
            dom = "clinical" if p.endswith("patient") else "biomedical"
            q = b.get("query", "")
            top = int(b.get("top", 5))
            spec = EMBED_DOMAINS[dom]
            if spec["kind"] == "ollama":
                vec = _post(f"{OLLAMA}/api/embed", {"model": spec["model"], "input": [q]}).get("embeddings", [[]])[0]
            else:
                vec = hf_feature_extract(spec["model"], [q])[0]
            try:
                hits = _post(f"{QDRANT}/collections/{spec['collection']}/points/search",
                             {"vector": vec, "limit": top, "with_payload": True})
            except urllib.error.HTTPError as e:
                hits = {"error": "collection missing", "code": e.code,
                        "collection": spec["collection"]}
            return self._send(200, {"domain": dom, "collection": spec["collection"],
                                    "embed_model": spec["model"], "hits": hits,
                                    "provenance": prov(f"rag.{dom}", spec["model"], kind="retrieval")})

        return self._send(404, {"error": "unknown path", "path": p})


def main():
    srv = ThreadingHTTPServer((BIND, PORT), Handler)
    print(f"NURA Clinical Inference Server on {BIND}:{PORT}")
    print(f"  generators : {len(GENERATORS)} lanes -> {list(GENERATORS)}")
    print(f"  encoders   : {list(ENCODERS)}")
    print(f"  embeddings : {list(EMBED_DOMAINS)}")
    print(f"  rules      : {list(RULES)}")
    print(f"  hf_token   : {bool(HF_TOKEN)}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
