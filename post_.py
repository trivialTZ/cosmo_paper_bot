#!/usr/bin/env python3
"""
Run read_arxiv.py to fetch matching arXiv papers, then post to Slack via environment-configured webhook.
Designed for GitHub Actions: reads all config from env vars (secrets).
"""
import os
import subprocess
import sys
import requests

# ─── CONFIG: all values via environment (set in GH Actions) ─────────────────────
WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
if not WEBHOOK_URL:
    sys.exit("ERROR: SLACK_WEBHOOK_URL env var not set.")
CHANNEL     = os.getenv('SLACK_CHANNEL', '#general')
USERNAME    = os.getenv('SLACK_USERNAME', 'astro-bot')
ICON_EMOJI  = os.getenv('SLACK_ICON', ':robot_face:')
READ_SCRIPT = os.getenv('READ_SCRIPT', 'read_arxiv.py')
PYTHON_BIN  = sys.executable  # use same interpreter


def get_arxiv_results():
    """Run read_arxiv.py and return its stdout (or stderr on failure)."""
    proc = subprocess.run(
        [PYTHON_BIN, READ_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        return f"*Error running {READ_SCRIPT}:*\n```{proc.stderr.strip()}```"
    return proc.stdout.strip() or "No matching arXiv papers found."


def format_with_blank_lines(raw: str) -> str:
    """
    Insert a blank line after each keyword line ([...]) for readability.
    """
    lines = raw.splitlines()
    formatted = []
    for line in lines:
        formatted.append(line)
        if line.strip().startswith('[') and line.strip().endswith(']'):
            formatted.append('')
    return "\n".join(formatted)


def post_to_slack(message: str):
    """Send a message to Slack via Incoming Webhook."""
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


if __name__ == '__main__':
    raw = get_arxiv_results()
    formatted = format_with_blank_lines(raw)
    # send plaintext; GH Actions passes env vars so no hard-codes remain
    post_to_slack(formatted)
    print("Posted to Slack.")
