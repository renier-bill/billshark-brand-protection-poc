#!/usr/bin/env python3
"""BS-14029 proof of concept: a tiny scheduled domain check for Claude cloud.

Each run:
  1. Resolves a few Billshark look-alike domains through Google Public DNS.
  2. Compares the result with the previous run saved in state/latest.json.
  3. Appends one line to state/runs.jsonl and prints a short summary.

Only the Python standard library is used, so no setup script is needed.
Network errors are recorded as "unknown", never as "not registered".
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DOMAINS = [
    "billshark.com",      # official, used as a control
    "bill-shark.com",
    "billsharks.com",
    "bilshark.com",
    "billshark.net",
]
STATE_DIR = Path(__file__).resolve().parent / "state"
LATEST = STATE_DIR / "latest.json"
RUNS = STATE_DIR / "runs.jsonl"


def resolve(domain):
    """Return sorted A records, [] if none, or None if the lookup failed."""
    url = f"https://dns.google/resolve?name={domain}&type=A"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
    except Exception as exc:  # network blocked, timeout, bad JSON...
        print(f"  {domain}: lookup failed ({exc.__class__.__name__})", file=sys.stderr)
        return None
    return sorted(a["data"] for a in data.get("Answer", []) if a.get("type") == 1)


def main():
    STATE_DIR.mkdir(exist_ok=True)
    previous = json.loads(LATEST.read_text()) if LATEST.exists() else {}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    current, changes, unknown = {}, [], []
    for domain in DOMAINS:
        records = resolve(domain)
        if records is None:
            unknown.append(domain)
            current[domain] = previous.get(domain)  # keep last known value
            continue
        current[domain] = records
        if domain in previous and previous[domain] != records:
            changes.append({"domain": domain, "before": previous[domain], "after": records})

    LATEST.write_text(json.dumps(current, indent=2) + "\n")
    run = {"run_at": now, "checked": len(DOMAINS), "changes": changes, "unknown": unknown}
    with RUNS.open("a") as f:
        f.write(json.dumps(run) + "\n")

    print(f"Run {now}: checked {len(DOMAINS)}, changed {len(changes)}, unknown {len(unknown)}")
    for c in changes:
        print(f"  CHANGED {c['domain']}: {c['before']} -> {c['after']}")
    for domain in DOMAINS:
        if domain not in unknown:
            print(f"  {domain}: {current[domain] or 'no A records'}")
    # Exit 1 only if every lookup failed, so the run is visibly broken.
    return 1 if len(unknown) == len(DOMAINS) else 0


if __name__ == "__main__":
    sys.exit(main())
