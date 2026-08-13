#!/usr/bin/env python3
"""
Update kickoff times in docs/fixtures.json from football-data.org.

WHAT THIS TOUCHES
    Only two fields, and only on Premier League fixtures:
        date        the match date, in Philadelphia time
        kickoffET   the kickoff time, in Philadelphia time

WHAT THIS NEVER TOUCHES
    label, note, venue, opponent, home, competition, doorsOpen, _README.
    Those are hand-written. If this script ever starts changing them,
    something is wrong.

HOW FIXTURES ARE MATCHED
    By Premier League matchday number, not by opponent name or date.
    Chelsea play exactly one league match per matchday, so the matchday
    is a stable key even when a fixture is moved for television.
    Our competition strings read "Premier League - Matchweek 12", and the
    12 is what gets matched against the API's `matchday`.

FAILURE BEHAVIOUR
    Loud, never silent. Any missing token, HTTP error, unexpected payload,
    or suspiciously small fixture list exits non-zero so the workflow
    goes red and GitHub emails you. It writes nothing on failure.

    Cup ties are not handled: the FA Cup and Carabao Cup are not in
    football-data.org's free tier. Those stay manual.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

API_BASE = "https://api.football-data.org/v4"
TEAM_ID = 61                      # Chelsea FC
COMPETITION = "PL"
SEASON = 2026                     # starting year of the 2026/27 season
EASTERN = ZoneInfo("America/New_York")
FIXTURES_PATH = "docs/fixtures.json"

# A full league season is 38 matches. If the API returns far fewer, treat the
# payload as untrustworthy and stop rather than half-rewrite the file.
MIN_EXPECTED_MATCHES = 30


def die(message):
    """Fail loudly. ::error:: makes it show up in the workflow summary."""
    print(f"::error::{message}")
    sys.exit(1)


def fetch_matches():
    token = os.environ.get("FOOTBALL_DATA_TOKEN")
    if not token:
        die("FOOTBALL_DATA_TOKEN is not set. Add it as a repository secret.")

    url = f"{API_BASE}/teams/{TEAM_ID}/matches?competitions={COMPETITION}&season={SEASON}"
    request = urllib.request.Request(url, headers={"X-Auth-Token": token})

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:300]
        if err.code == 403:
            die(f"HTTP 403. The token may be wrong, or the plan may not cover this. {detail}")
        if err.code == 429:
            die(f"HTTP 429, rate limited. Free tier allows 10 calls a minute. {detail}")
        die(f"API returned HTTP {err.code}. {detail}")
    except Exception as err:
        die(f"Could not reach football-data.org: {err}")

    matches = payload.get("matches")
    if not isinstance(matches, list):
        die("Unexpected API response: no 'matches' list. The API shape may have changed.")
    if len(matches) < MIN_EXPECTED_MATCHES:
        die(
            f"Only {len(matches)} matches returned, expected at least {MIN_EXPECTED_MATCHES}. "
            "Refusing to edit fixtures.json from a payload this incomplete."
        )
    return matches


def to_eastern(utc_string):
    """'2026-08-24T19:00:00Z' -> (date 'YYYY-MM-DD', time '3:00 PM') in Philadelphia time."""
    stamp = datetime.fromisoformat(utc_string.replace("Z", "+00:00")).astimezone(EASTERN)
    clock = stamp.strftime("%I:%M %p").lstrip("0")
    return stamp.strftime("%Y-%m-%d"), clock


def matchweek_of(competition_string):
    found = re.search(r"Matchweek\s+(\d+)", competition_string or "")
    return int(found.group(1)) if found else None


def main():
    try:
        with open(FIXTURES_PATH, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError:
        die(f"{FIXTURES_PATH} not found. Is the working directory the repo root?")
    except json.JSONDecodeError as err:
        die(f"{FIXTURES_PATH} is not valid JSON: {err}")

    fixtures = document.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        die("fixtures.json has no 'fixtures' list.")

    by_matchweek = {}
    for fixture in fixtures:
        week = matchweek_of(fixture.get("competition"))
        if week is not None:
            by_matchweek[week] = fixture

    changes = []
    warnings = []

    for match in fetch_matches():
        matchday = match.get("matchday")
        utc_date = match.get("utcDate")
        if matchday is None or not utc_date:
            continue

        fixture = by_matchweek.get(matchday)
        if fixture is None:
            warnings.append(f"Matchweek {matchday} is in the API but not in fixtures.json.")
            continue

        # Sanity check only. A mismatch is reported, never silently corrected.
        home = (match.get("homeTeam") or {}).get("name", "")
        away = (match.get("awayTeam") or {}).get("name", "")
        chelsea_at_home = "Chelsea" in home
        if chelsea_at_home != bool(fixture.get("home")):
            warnings.append(
                f"Matchweek {matchday}: API says {home} v {away}, "
                f"but fixtures.json has home={fixture.get('home')}. Left alone — check by hand."
            )

        new_date, new_time = to_eastern(utc_date)

        if fixture.get("date") != new_date:
            changes.append(f"Matchweek {matchday}: date {fixture.get('date')} -> {new_date}")
            fixture["date"] = new_date

        if fixture.get("kickoffET") != new_time:
            was = fixture.get("kickoffET") or "not announced"
            changes.append(f"Matchweek {matchday}: kickoff {was} -> {new_time}")
            fixture["kickoffET"] = new_time

    for warning in warnings:
        print(f"::warning::{warning}")

    if not changes:
        print("No changes. fixtures.json already matches the API.")
        return

    with open(FIXTURES_PATH, "w", encoding="utf-8") as handle:
        json.dump(document, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"{len(changes)} change(s) written to {FIXTURES_PATH}:")
    for change in changes:
        print(f"  {change}")

    # Picked up by the workflow to build the pull request description.
    summary = os.environ.get("GITHUB_OUTPUT")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("changes<<EOF\n")
            for change in changes:
                handle.write(f"- {change}\n")
            handle.write("EOF\n")


if __name__ == "__main__":
    main()
