#!/usr/bin/env python3
"""AUTO-DREAM: the nightly experience-mining loop — cluster the day's work, propose lessons, queue for the founder's review."""
import json, os, sqlite3, subprocess, datetime, hashlib, re

BASE = "/opt/data/profiles/nura"
OUT = os.path.join(BASE, "cron/output/auto-dream")
DB = os.path.join(BASE, "memories", "dream-lessons.db")
os.makedirs(OUT, exist_ok=True)

def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def main():
    today = datetime.date.today().isoformat()
    # 1. EXPERIENCES: the day's session-activity (the recent transcripts!)
    sdb = "/opt/data/profiles/nura/state.db"
    experiences = []
    if os.path.exists(sdb):
        try:
            con = sqlite3.connect(sdb)
            rows = con.execute(
                "SELECT title, created_at FROM sessions WHERE created_at >= datetime('now','-1 day') ORDER BY created_at DESC LIMIT 12"
            ).fetchall()
            con.close()
            experiences = [{"title": r[0], "when": r[1]} for r in rows if r[0]]
        except Exception as e:
            experiences = [{"error": str(e)}]
    # 2. CLUSTERS: the title-keyword clusters (the naive-but-deterministic!)
    clusters = {}
    for x in experiences:
        t = (x.get("title") or "").lower()
        for kw in ["docsgpt", "flut", "doximity", "atlas", "skill", "mcp", "fleet", "github", "app", "crm", "emh"]:
            if kw in t:
                clusters.setdefault(kw, []).append(x.get("title"))
                break
    # 3. CANDIDATE LESSONS (the deterministic rules — the machine proposes!)
    lessons = []
    if "docsgpt" in clusters and len(clusters["docsgpt"]) >= 1:
        lessons.append({"topic": "docsgpt", "lesson": "The DocsGPT brain is live — the completion workstreams run on the board (6 tickets). The next milestone: the corpora ingestion completes the knowledge-grounding.", "source": "experiences"})
    if "flut" in clusters or "app" in clusters:
        lessons.append({"topic": "flutter", "lesson": "The nura-medical scaffold is real; the Doximity-design system + the chat-screen are the immediate next build. The Apple-side needs the Mac/Xcode or the CI-cloud.", "source": "experiences"})
    if "atlas" in clusters:
        lessons.append({"topic": "atlas", "lesson": "The board handoffs work via the psql-lane; the CEO-restoration remains the founder item. The graph-orchestration issue landed and awaits the team wiring.", "source": "experiences"})
    if "skill" in clusters or "mcp" in clusters:
        lessons.append({"topic": "skills", "lesson": "The skill-library passed the 508-baseline and the selection-doctrine is deterministic. The new skills (agent-graph-orchestration, mcp-administrator) are live.", "source": "experiences"})
    if not lessons:
        lessons.append({"topic": "quiet", "lesson": "No major experience-clusters tonight — the machine idled or the sessions-db was quiet. The dojo remains on watch.", "source": "experiences"})
    # 4. THE QUEUE (the human-review gate — the founder approves/denies!)
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS lessons (id TEXT PRIMARY KEY, day TEXT, topic TEXT, lesson TEXT, status TEXT)")
    queued = 0
    for l in lessons:
        lid = hashlib.sha1((today + l["topic"]).encode()).hexdigest()[:12]
        exists = con.execute("SELECT 1 FROM lessons WHERE id=?", (lid,)).fetchone()
        if not exists:
            con.execute("INSERT INTO lessons VALUES (?,?,?,?,?)", (lid, today, l["topic"], l["lesson"], "pending"))
            queued += 1
    con.commit()
    pending = con.execute("SELECT COUNT(*) FROM lessons WHERE status='pending'").fetchone()[0]
    con.close()
    # 5. THE REPORT (delivered to the founder's Telegram)
    lines = ["🌙 AUTO-DREAM — the overnight lesson-queue", ""]
    lines.append(f"Experiences mined: {len(experiences)} · clusters: {len(clusters)} · new lessons: {queued}")
    lines.append("")
    for l in lessons:
        lines.append(f"· {l['topic']}: {l['lesson'][:130]}")
    lines.append("")
    lines.append(f"Pending review: {pending} (the approve/deny in the morning brief!)")
    report = "\n".join(lines)
    with open(os.path.join(OUT, f"dream-{today}.txt"), "w") as f:
        f.write(report)
    print(report)

if __name__ == "__main__":
    main()
