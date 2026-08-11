#!/usr/bin/env python3
"""THE EXPERIENCE LEDGER — the Phase-1 core: every meaningful execution → the structured ExperienceRecord!
The 3-tier split: episodic (what-happened) · semantic (what-fact) · procedural (what-technique → the SKILL!)."""
import json, os, datetime, hashlib, sqlite3

LEDGER_DB = "/opt/data/profiles/nura/self-improve/experience.db"
os.makedirs(os.path.dirname(LEDGER_DB), exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiences (
    id TEXT PRIMARY KEY,
    task_type TEXT, input_hash TEXT, model TEXT,
    skills_loaded TEXT, tools_used TEXT,
    steps INTEGER, duration_ms INTEGER,
    input_tokens INTEGER, output_tokens INTEGER, estimated_cost REAL,
    objective_score REAL, user_feedback INTEGER,
    tool_errors TEXT, retries INTEGER,
    failure_modes TEXT, lessons TEXT,
    tier TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS skill_stats (
    name TEXT PRIMARY KEY,
    uses INTEGER DEFAULT 0, successes INTEGER DEFAULT 0, failures INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0.5, last_evaluated TEXT, eval_score REAL, status TEXT DEFAULT 'production'
);
"""

def init():
    con = sqlite3.connect(LEDGER_DB)
    con.executescript(SCHEMA)
    con.commit()
    con.close()

def record(exp):
    """exp: dict — the ExperienceRecord (the F1-F18-taxonomy-optional!)."""
    init()
    exp.setdefault("id", "exp_" + hashlib.sha256(f"{exp.get('task_type','')}{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:12])
    exp.setdefault("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
    exp.setdefault("tier", "episodic")
    con = sqlite3.connect(LEDGER_DB)
    con.execute("""INSERT OR REPLACE INTO experiences
        (id, task_type, input_hash, model, skills_loaded, tools_used, steps, duration_ms,
         input_tokens, output_tokens, estimated_cost, objective_score, user_feedback,
         tool_errors, retries, failure_modes, lessons, tier, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (exp["id"], exp.get("task_type"), exp.get("input_hash"), exp.get("model"),
         json.dumps(exp.get("skills_loaded", [])), json.dumps(exp.get("tools_used", [])),
         exp.get("steps"), exp.get("duration_ms"), exp.get("input_tokens"), exp.get("output_tokens"),
         exp.get("estimated_cost"), exp.get("objective_score"), exp.get("user_feedback"),
         json.dumps(exp.get("tool_errors", [])), exp.get("retries"),
         json.dumps(exp.get("failure_modes", [])), json.dumps(exp.get("lessons", [])),
         exp.get("tier"), exp["created_at"]))
    con.commit()
    con.close()
    # the procedural-tier → the skill-candidate-flag!
    if exp.get("tier") == "procedural" and exp.get("lessons"):
        print(f"📚 PROCEDURAL-CANDIDATE: {exp['id']} — lessons: {exp['lessons'][:1]}")
    return exp["id"]

def update_skill(name, success=True):
    """The skill-confidence-updater: every use/outcome feeds the stats."""
    init()
    con = sqlite3.connect(LEDGER_DB)
    row = con.execute("SELECT uses, successes, failures FROM skill_stats WHERE name=?", (name,)).fetchone()
    if row:
        uses, succ, fail = row
        uses += 1
        succ += 1 if success else 0
        fail += 0 if success else 1
    else:
        uses, succ, fail = 1, 1 if success else 0, 0 if success else 1
    conf = round(succ / uses, 3) if uses else 0.5
    con.execute("""INSERT OR REPLACE INTO skill_stats (name, uses, successes, failures, confidence, last_evaluated, status)
                   VALUES (?,?,?,?,?,?, 'production')""",
                (name, uses, succ, fail, conf, datetime.datetime.now(datetime.timezone.utc).isoformat()))
    con.commit()
    con.close()
    return conf

if __name__ == "__main__":
    # the self-test!
    exp = {"task_type": "wiring", "model": "deepseek-flash", "skills_loaded": ["watchdog-patterns"],
           "tools_used": ["terminal", "ssh"], "steps": 9, "duration_ms": 41000,
           "input_tokens": 8200, "output_tokens": 1400, "estimated_cost": 0.09,
           "objective_score": 0.95, "user_feedback": 1, "retries": 1,
           "failure_modes": [], "lessons": ["Absolute-paths in cron-scripts — the HOME differs!"],
           "tier": "procedural"}
    eid = record(exp)
    print("LEDGER-TEST:", eid, "✓")
    print("SKILL-CONF:", update_skill("watchdog-patterns", True))
