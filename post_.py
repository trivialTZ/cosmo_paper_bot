#!/usr/bin/env python3
import subprocess
import sys
import requests
import json

# ─── CONFIG ────────────────────────────────────────────────────────────────────
WEBHOOK_URL = "https://hooks.slack.com/services/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"  # ← replace with your webhook
CHANNEL     = "#jj"                                          # ← your target channel
USERNAME    = "astro-bot"                                         # ← bot name
ICON_EMOJI  = ":robot_face:"                                      # ← avatar emoji
READ_SCRIPT = "/Users/tz/PycharmProjects/astropaperbot/read_arxiv.py"  # ← path to your script
PYTHON_BIN  = sys.executable  # uses same Python interpreter

# ─── FUNCTIONS ────────────────────────────────────────────────────────────────

def get_arxiv_results():
    """Run the read_arxiv.py script and return its stdout (all matching papers)."""
    proc = subprocess.run(
        [PYTHON_BIN, READ_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        # If the script fails, include stderr in the Slack message
        return f"*Error running read_arxiv.py:*\n```{proc.stderr.strip()}```"
    out = proc.stdout.strip()
    return out or "No matching arXiv papers found."

def post_to_slack(message: str):
    """Post a message to Slack via Incoming Webhook."""
    payload = {
        "channel":    CHANNEL,
        "username":   USERNAME,
        "icon_emoji": ICON_EMOJI,
        "text":       message
    }
    resp = requests.post(WEBHOOK_URL, json=payload)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Slack API error {resp.status_code}: {resp.text}")
        raise

def format_with_blank_lines(raw: str) -> str:
    """
    Insert a blank line after each keyword line (lines starting with '[' and ending with ']').
    This ensures separation between each paper block.
    """
    lines = raw.splitlines()
    formatted = []
    for line in lines:
        formatted.append(line)
        # if this line is the keywords line, add a blank separator
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            formatted.append('')
    return "\n".join(formatted)

# ─── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    raw_results = get_arxiv_results()
    formatted = format_with_blank_lines(raw_results)
    message = f"{formatted}"
    post_to_slack(message)
    print("Posted to Slack.")