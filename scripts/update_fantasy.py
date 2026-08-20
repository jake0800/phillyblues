#!/usr/bin/env python3
"""
Update docs/fantasy.json from the Fantasy Premier League public API.

WHAT THIS TOUCHES
    Only the data fields:
        gameweek       the last finished gameweek these standings reflect
        updated        the date this file was written
        totalManagers  how many teams are in the league
        standings      the top 10, in order

WHAT THIS NEVER TOUCHES
    _README, leagueName, leagueId, inviteUrl, standingsUrl. Those are
    hand-written identity fields. leagueName is refreshed only if the API
    gives one and it is non-empty.

WHY A SCRIPT AND NOT A BROWSER FETCH
    The FPL API sends no CORS headers, so a browser on the GitHub Pages
    site cannot read it directly — the request is blocked. This is the
    same reason the fixture card reads a local fixtures.json. This script
    fetches server-side and writes the local fantasy.json the page reads.

NO API KEY NEEDED
    The classic-league standings endpoint is public. Unlike the fixtures
    script, there is no token to set.

FAILURE BEHAVIOUR
    Loud, never silent. Any HTTP error, unexpected payload, or unreadable
    file exits non-zero so the workflow goes red and GitHub emails you.
    It writes nothing on failure.

    A note on timing: before the season's first gameweek finishes, the
    API returns an empty standings.results. That is NOT an error — the
    script writes standings: [] and gameweek: null, and the page keeps
    its pre-season panel. Only a genuinely broken response fails the run.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

LEAGUE_ID = 588890
API_URL = f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/"
BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
FANTASY_PATH = "docs/fantasy.json"
TOP_N = 10

# A browser-like User-Agent. The FPL API rejects some default agents.
UA = "Mozilla/5.0 (compatible; PhillyBluesBot/1.0; +https://www.phillybluescfc.com)"


def die(message):
    """Fail loudly. ::error:: makes it show up in the workflow summary."""
    print(f"::error::{message}")
    sys.exit(1)


def get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:300]
        if err.code == 429:
            die(f"HTTP 429, rate limited by the FPL API. Try again later. {detail}")
        die(f"FPL API returned HTTP {err.code} for {url}. {detail}")
    except Exception as err:
        die(f"Could not reach the FPL API ({url}): {err}")


def current_gameweek():
    """
    The last finished gameweek's id, or None if none has finished.

    Uses bootstrap-static's events. 'finished' means the gameweek's points
    are settled. We report the highest finished id — that is the gameweek
    the standings reflect.
    """
    data = get_json(BOOTSTRAP_URL)
    events = data.get("events")
    if not isinstance(events, list):
        die("bootstrap-static had no 'events' list. The API shape may have changed.")

    finished = [e.get("id") for e in events if e.get("finished") and isinstance(e.get("id"), int)]
    return max(finished) if finished else None


def main():
    # Read the existing file so we preserve the hand-written identity fields.
    try:
        with open(FANTASY_PATH, encoding="utf-8") as handle:
            doc = json.load(handle)
    except FileNotFoundError:
        die(f"{FANTASY_PATH} not found. Is the working directory the repo root?")
    except json.JSONDecodeError as err:
        die(f"{FANTASY_PATH} is not valid JSON: {err}")

    standings_payload = get_json(API_URL)

    league = standings_payload.get("league") or {}
    results = ((standings_payload.get("standings") or {}).get("results")) or []
    new_entries = ((standings_payload.get("new_entries") or {}).get("results")) or []

    if not isinstance(results, list):
        die("standings.results was not a list. The API shape may have changed.")

    # Manager count: once the season is running, results holds everyone.
    # Before it starts, results is empty and new_entries holds the joiners.
    total_managers = len(results) if results else len(new_entries)
    if total_managers:
        doc["totalManagers"] = total_managers

    # Refresh the league name only if the API gives a non-empty one.
    api_name = (league.get("name") or "").strip()
    if api_name:
        doc["leagueName"] = api_name

    top = []
    for row in results[:TOP_N]:
        top.append({
            "pos": row.get("rank"),
            "manager": (row.get("player_name") or "").strip(),
            "team": (row.get("entry_name") or "").strip(),
            "gw": row.get("event_total"),
            "total": row.get("total"),
        })

    doc["standings"] = top
    doc["gameweek"] = current_gameweek() if top else None
    doc["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with open(FANTASY_PATH, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    if top:
        print(f"Wrote top {len(top)} of {total_managers} managers, gameweek {doc['gameweek']}.")
    else:
        print(f"No standings yet (season not started). {total_managers} managers registered. "
              "Wrote pre-season state.")


if __name__ == "__main__":
    main()
