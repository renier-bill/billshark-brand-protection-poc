Run the Billshark domain-check proof of concept (Jira BS-14029).

1. Run `python3 check_domains.py` from the repository root.
2. Commit the updated `state/latest.json` and `state/runs.jsonl` directly to the `main` branch with the message `poc: domain check <UTC timestamp>` and push it.
3. Reply with the script's summary output. If any domain shows CHANGED, put that line first.

Do not change the script or any other file. If the push fails, say so in the reply.
