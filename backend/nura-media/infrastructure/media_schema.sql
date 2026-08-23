-- NURA Media Engine — storage/ledger/registry schema (the "all databases" record)
-- Durable record: Postgres. Dispatch: Celery+Redis (transient). Media assets: Backblaze B2.
-- No PHI in media-generation prompts by default; medical-edu uses synthetic/de-identified only.

-- Generation Ledger: every generated asset is reproducible + accounted (spec §12)
CREATE TABLE IF NOT EXISTS generation_ledger (
    asset_id         TEXT PRIMARY KEY,
    job_id           TEXT,
    tenant_id        TEXT,
    provider         TEXT,          -- comfyui | wan | ltx | flux | heygem | musetalk | heygen | higgsfield | ffmpeg ...
    model            TEXT,
    model_version    TEXT,
    task             TEXT,          -- script | image | video | avatar | voice | lipsync | edit | render
    prompt           TEXT,
    seed             TEXT,
    workflow         TEXT,          -- e.g. script->edit->qa
    input_hash       TEXT,
    output_hash      TEXT,
    generation_time  NUMERIC,
    cost             NUMERIC,       -- 0.0 = local/free; >0 = paid API (logged per §7)
    license          TEXT,
    storage_uri      TEXT,
    duration_sec     NUMERIC,
    resolution       TEXT,
    status           TEXT,          -- queued | running | done | failed | approved | published
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- Media model registry (spec §13) — no model auto-published without benchmark + license review
CREATE TABLE IF NOT EXISTS media_model_registry (
    model_id         TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    version          TEXT,
    provider         TEXT,
    task             TEXT,
    license          TEXT,
    commercial_use   TEXT,          -- allowed | requires-review | prohibited
    vram_requirement TEXT,          -- e.g. "8GB", "none"
    quality_score    NUMERIC,
    speed_score      NUMERIC,
    cost_score       NUMERIC,
    reliability_score NUMERIC,
    enabled          BOOLEAN DEFAULT FALSE,   -- gated: enforced by the provider router
    last_benchmark   TIMESTAMPTZ,
    benchmark_ref    TEXT
);

-- Media job queue metadata (durable record; Celery+Redis carries dispatch)
CREATE TABLE IF NOT EXISTS media_job (
    job_id       TEXT PRIMARY KEY,
    tenant_id    TEXT,
    queue        TEXT,              -- media.script | media.video | media.avatar | media.edit | media.render | media.qa | media.publish
    priority     INT DEFAULT 5,
    status       TEXT DEFAULT 'queued',   -- queued | running | retrying | done | failed | cancelled
    provider     TEXT,
    model        TEXT,
    attempt      INT DEFAULT 0,
    error        TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Authorized identity registry (spec §20) — no voice/face/avatar cloning without documented authorization
CREATE TABLE IF NOT EXISTS authorized_identity_registry (
    identity_id    TEXT PRIMARY KEY,
    name           TEXT,
    type           TEXT,            -- voice | face | avatar
    authorization_doc TEXT,
    authorized_by  TEXT,
    authorized_at  TIMESTAMPTZ DEFAULT now(),
    expiry         TIMESTAMPTZ
);
