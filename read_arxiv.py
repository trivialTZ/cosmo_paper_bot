#!/usr/bin/env python3
"""
Fetch all astro-ph papers from arXiv, find those whose title or abstract
contains any keyword from astro_key.txt, then print **all** papers
from the **newest** publication date in the format:

2504.17688v1 : The Hubble Image Similarity Project
  http://arxiv.org/abs/2504.17688v1
 [hubble space telescope]
"""
import sys
from datetime import datetime
import feedparser

def load_keywords(path='astro_key.txt'):
    try:
        with open(path) as f:
            kws = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        sys.exit("ERROR: astro_key.txt not found.")
    if not kws:
        sys.exit("ERROR: No keywords found in astro_key.txt.")
    return kws

def fetch_arxiv_entries(max_results=1000):
    cats = ["GA", "CO", "EP", "HE", "IM", "SR"]
    cat_query = "(" + "+OR+".join(f"cat:astro-ph.{c}" for c in cats) + ")"
    base_url = "http://export.arxiv.org/api/query?"
    query = (
        f"search_query={cat_query}"
        f"&sortBy=submittedDate"
        f"&sortOrder=descending"
        f"&max_results={max_results}"
    )
    url = base_url + query
    feed = feedparser.parse(url)
    if not feed.entries:
        sys.exit("No entries returned from arXiv. Check network or query URL.")
    return feed.entries

def find_matches(entries, keywords):
    matches = []
    for e in entries:
        text = (e.title + " " + e.summary).lower()
        matched = [kw for kw in keywords if kw in text]
        if matched:
            # extract arXiv id (e.g. "2504.17688v1")
            arxiv_id = e.id.split("/abs/")[-1]
            # parse published date as a date object
            dt = datetime.strptime(e.published, "%Y-%m-%dT%H:%M:%SZ").date()
            matches.append({
                "id": arxiv_id,
                "title": e.title.strip(),
                "url": e.link,
                "date": dt,
                "keywords": matched
            })
    return matches

def print_newest_date_papers(matches):
    if not matches:
        print("No matching papers found.")
        return
    # determine the newest date among matches
    newest_date = max(m["date"] for m in matches)
    # filter matches to only that date
    newest_papers = [m for m in matches if m["date"] == newest_date]
    # print each in the requested format
    for p in newest_papers:
        print(f"{p['id']} : {p['title']}")
        print(f"  {p['url']}")
        print(f" [{', '.join(p['keywords'])}]")

if __name__ == "__main__":
    keywords = load_keywords('astro_key.txt')
    entries  = fetch_arxiv_entries()
    matches  = find_matches(entries, keywords)
    print_newest_date_papers(matches)
