#!/usr/bin/env python3
"""
Run read_arxiv.py to fetch matching arXiv papers, then post to Slack
with a blank line separating each paper block.
"""
import os
import subprocess
import sys
import requests

# ─── CONFIG ────────────────────────────────────────────────────────────────────
# Now read all sensitive/config values from environment (set by GitHub Actions)
WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
CHANNEL     = os.environ.get('SLACK_CHANNEL', '#jj')
USERNAME    = os.environ.get('SLACK_USERNAME', 'astro-bot')
ICON_EMOJI  = os.environ.get('SLACK_ICON', ':robot_face:')
READ_SCRIPT = 'read_arxiv.py'   # assume script sits in repo root alongside this file
PYTHON_BIN  = sys.executable    # use the same Python interpreter


def get_arxiv_results():
    """Run read_arxiv.py and return its stdout (or stderr on failure)."""
    proc = subprocess.run(
        [PYTHON_BIN, READ_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        return f"*Error running read_arxiv.py:*\n```{proc.stderr.strip()}```"
    return proc.stdout.strip() or "No matching arXiv papers found."


def format_with_blank_lines(raw: str) -> str:
    """
    Insert a blank line after each keyword line (lines starting with '[' and ending with ']').
    Ensures separation between each paper block.
    """
    lines = raw.splitlines()
    formatted = []
    for line in lines:
        formatted.append(line)
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            formatted.append('')  # add blank line
    return "\n".join(formatted)


def post_to_slack(message: str):
    """Send the given message to Slack via Incoming Webhook."""
    payload = {
        "channel":    CHANNEL,
        "username":   USERNAME,
        "icon_emoji": ICON_EMOJI,
        "text":       message
    }
    resp = requests.post(WEBHOOK_URL, json=payload)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print(f"Slack API error {resp.status_code}: {resp.text}")
        raise


if __name__ == "__main__":
    raw_results = get_arxiv_results()
    formatted = format_with_blank_lines(raw_results)
    # no need for code fences in GitHub Actions; Slack will format plaintext fine
    message = formatted
    post_to_slack(message)
    print("Posted to Slack.")
