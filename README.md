# Domain monitor proof of concept (BS-14029)

Shows that a script can run on a schedule in Claude's cloud, with no one's computer turned on, and keep state between runs.

- `check_domains.py`: resolves 5 Billshark look-alike domains through Google Public DNS and compares them with the previous run.
- `state/latest.json`: the last result. Each run commits it back to the repo, because cloud runs start from a fresh clone.
- `state/runs.jsonl`: one line per run (time, changes, failed lookups).
- `PROMPT.md`: the prompt the scheduled task runs.

## Set up the scheduled task

1. Push this folder to a GitHub repo, for example `billshark/brand-protection-poc`.
2. Go to claude.ai/code/routines and click **New task** (or **New routine**).
3. **Name:** `BS-14029 domain check PoC`. **Prompt:** paste the contents of `PROMPT.md`.
4. **Repository:** select the repo.
5. **Cloud environment:** create a new one with **Network access: Custom**, allowed domain `dns.google`, and keep the default package list checked.
6. **Trigger:** Schedule, hourly (or Custom cron `7 * * * *`, which is 7 minutes past each hour UTC).
7. **Connectors:** remove all of them. The PoC doesn't need any.
8. Click **Create**, then **Run now** to test it.

## What to check

- The run shows the summary, with A records for `billshark.com`.
- A new commit appears on `main` with updated `state/` files.
- The next run starts on its own at the scheduled time, with your laptop closed.
