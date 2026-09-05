#!/usr/bin/env python3
"""Peer Files engine — store claims as scored, source-tagged, falsifiable files.

One JSON file per claim under /opt/data/peer-files/ + an index.json.
CLI:
  peer_files.py add <claim> --source <cls> --conf <0-1> --basis "..."
              --falsify "..." [--id pf-0001] [--review accepted]
  peer_files.py list [--min-conf 0.7] [--source verified]
  peer_files.py falsify <id> [--note "..."]
  peer_files.py get <id>
  peer_files.py index
"""
import json, os, sys, argparse, datetime

DIR = "/opt/data/peer-files"
INDEX = os.path.join(DIR, "index.json")
VALID_SOURCES = {"verified", "self_report", "observed", "inferred", "unknown"}
VALID_REVIEW = {"accepted", "provisional", "contested", "rejected"}


def _load_index():
    if os.path.exists(INDEX):
        with open(INDEX) as f:
            return json.load(f)
    return {"files": [], "seq": 0}


def _save_index(idx):
    os.makedirs(DIR, exist_ok=True)
    with open(INDEX, "w") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)


def _path(pid):
    return os.path.join(DIR, f"{pid}.json")


def add(claim, source, conf, basis, falsify, pid=None, review="accepted"):
    idx = _load_index()
    pid = pid or f"pf-{idx['seq']+1:04d}"
    pf = {
        "id": pid,
        "claim": claim,
        "source_class": source,
        "confidence": float(conf),
        "basis": basis,
        "falsification": falsify,
        "review": review,
        "updated": datetime.date.today().isoformat(),
    }
    os.makedirs(DIR, exist_ok=True)
    with open(_path(pid), "w") as f:
        json.dump(pf, f, indent=2, ensure_ascii=False)
    if pid not in idx["files"]:
        idx["files"].append(pid)
        idx["seq"] += 1
    _save_index(idx)
    return pf


def get(pid):
    p = _path(pid)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def falsify(pid, note=""):
    pf = get(pid)
    if not pf:
        return None
    pf["review"] = "rejected"
    pf["falsification_note"] = note
    pf["updated"] = datetime.date.today().isoformat()
    with open(_path(pid), "w") as f:
        json.dump(pf, f, indent=2, ensure_ascii=False)
    return pf


def list_files(min_conf=0.0, source=None):
    idx = _load_index()
    out = []
    for pid in idx["files"]:
        pf = get(pid)
        if not pf:
            continue
        if min_conf and pf["confidence"] < min_conf:
            continue
        if source and pf["source_class"] != source:
            continue
        out.append(pf)
    return sorted(out, key=lambda p: -p["confidence"])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("claim"); a.add_argument("--source", required=True)
    a.add_argument("--conf", type=float, required=True)
    a.add_argument("--basis", default=""); a.add_argument("--falsify", default="")
    a.add_argument("--id", default=None); a.add_argument("--review", default="accepted")

    l = sub.add_parser("list"); l.add_argument("--min-conf", type=float, default=0.0); l.add_argument("--source", default=None)
    g = sub.add_parser("get"); g.add_argument("id")
    f = sub.add_parser("falsify"); f.add_argument("id"); f.add_argument("--note", default="")
    i = sub.add_parser("index")

    args = ap.parse_args()
    if args.cmd == "add":
        if args.source not in VALID_SOURCES:
            sys.exit(f"bad source: {args.source}")
        if not (0 <= args.conf <= 1):
            sys.exit("conf must be 0-1")
        pf = add(args.claim, args.source, args.conf, args.basis, args.falsify, args.id, args.review)
        print(json.dumps(pf, indent=2))
    elif args.cmd == "list":
        for pf in list_files(args.min_conf, args.source):
            print(f"{pf['id']}  conf={pf['confidence']:.2f}  {pf['source_class']:11}  {pf['claim'][:60]}")
    elif args.cmd == "get":
        pf = get(args.id)
        print(json.dumps(pf, indent=2) if pf else "not found")
    elif args.cmd == "falsify":
        print(json.dumps(falsify(args.id, args.note), indent=2))
    elif args.cmd == "index":
        print(json.dumps(_load_index(), indent=2))


if __name__ == "__main__":
    main()
