# Philly Blues — Status & Social Rollout

**Written:** Saturday 15 August 2026, evening
**Site:** https://phillybluescfc.com — **LIVE**
**Repo:** `Philly Blues Webpage`, serving from `/docs`, branch `main`
**Last commit:** `8c863d2` — 2021 photos and video added to venue section

---

## Start here tomorrow

Two things, in order. The first blocks the second.

### 1. Facebook Sharing Debugger — 5 minutes

Facebook has the **old** link preview cached: the crest image and the description
"We've moved to Cavanaugh's Rittenhouse." Both were replaced today. If you post
before re-scraping, your homecoming post will carry a link card contradicting it.

- Go to Facebook's Sharing Debugger
- Enter `phillybluescfc.com`
- Click **Scrape Again**
- Confirm the preview shows the **crowd celebration photo** and the new description
  ("We're back at Cavanaugh's Rittenhouse, where we watched the 2021 Champions
  League run...")

### 2. Publish Post 1

Full copy for all three posts is in `PhillyBlues_Social_Rollout.md`. Post 1 copy is
also reproduced below so you don't need both files open.

---

## Site status: DONE

Nothing is blocking launch. Everything below was verified live today.

| Item | Status |
|---|---|
| Domain + HTTPS | Live, serving correctly |
| Hero — homecoming story | Rewritten and verified |
| Fixture card | "First match back" · Fulham away, Mon 24 Aug, 3:00 PM ET |
| 2021 celebration video | Serving, HTTP 200, 6.11 MB, poster attached |
| 2021 photos (street + banner) | Both loading at 1600px, lazy-loaded |
| Photo placeholders | All removed — zero remaining |
| Contact form | Wired to Formspree (`xljrnona`) |
| og:image | Now the celebration poster frame |
| og:description | Updated to homecoming wording |
| Ticketing section | Rewritten from Chelsea FC sources only |
| Fixtures automation | Checked — safe, see below |

**Note on caching:** the plain URL served a stale copy after the push. Verified via
`?cachebust=1`. Hard-refresh if it looks unchanged in your browser.

**Fixtures workflow — all clear.** `update-fixtures.yml` only writes
`docs/fixtures.json`, never `index.html`. It runs daily at 11:00 UTC, touches only
`date` and `kickoffET`, and opens a PR on `fixtures/auto-update` rather than
committing to `main`. For the 24 Aug Fulham match it would produce no diff. Nothing
to worry about on matchday.

---

## Social rollout — nothing published yet

**Angle:** the lucky pub. Cav's was the temporary home in 2020/21; Chelsea won the
Champions League that season; now it's home for good.

**The wrinkle that makes it work:** Cav's itself moved one block into a new building
with a serious AV system, so it isn't literally the same room. Don't hide that — it's
the punchline. Neither party is where they were in 2021, and both came out better.

**Tone:** underplay it. "Draw your own conclusions" beats "THE LUCKY PUB IS BACK."
Let the reader make the joke; they're more likely to reply, and replies drive reach.

### Schedule

| # | Post | Target | Status |
|---|---|---|---|
| 1 | The lucky pub | **Sun 16 Aug** | Not published |
| 2 | What changed with tickets | Thu 20 – Fri 21 Aug | Not published |
| 3 | First one back | Sun 23 – Mon 24 Aug | Not published |

Premier League opens Fri 21 Aug. Chelsea's first match is Mon 24 Aug.

### Rules of thumb

- Don't cross-post identically — each platform version is written separately
- Upload video **natively** to Facebook and Instagram; never link YouTube there
- Reply to comments in the first hour; it matters more than the copy
- Instagram needs link-in-bio updated to phillybluescfc.com

---

## Post 1 copy — for tomorrow

### Facebook

> May 2021. We were at Cavanaugh's Rittenhouse because we had nowhere else to be — a
> temporary home in a season nobody planned for.
>
> Three weeks later Chelsea were champions of Europe.
>
> We're going back. Except Cav's has moved too — one block over, brand new building,
> an AV setup that makes every other room in this city look like 2011.
>
> So neither of us is quite where we were in 2021. Both of us are better for it.
>
> Cav's is our home pub for 2026/27 and beyond, and this time it's by choice. 1921
> Sansom St. First one back is Monday 24 August, Fulham away, 3:00 PM ET. Doors from
> 2:00.
>
> We've also finally got a proper website — matchday info, how membership works, and
> everything that's changed with tickets this season, all in one place.
>
> phillybluescfc.com
>
> Yes, technically it's a different room. We're choosing not to let that bother us.
>
> #CFC #KTBFFH #PhillyBlues

**Attach:** the celebration video, uploaded natively.

### Instagram

> May 2021: temporary home.
> Three weeks later: champions of Europe.
>
> We're going back to Cav's — and this time we're staying.
>
> They've moved too, mind. One block over, brand new build, an AV system worth
> turning up early for. Neither of us is where we were in 2021. Both of us are better
> for it.
>
> Cavanaugh's Rittenhouse, 1921 Sansom St. First one back Monday 24 August, Fulham
> away, 3:00 PM ET, doors at 2.
>
> New website too — matchdays, membership, and what's changed with ticketing this
> season. Link in bio.
>
> We're not saying the pub won us the Champions League. We're just noting the timeline.
>
> #CFC #Chelsea #KTBFFH #PhillyBlues #Philadelphia #ChelseaFC #CFCFamily

**Format:** the video as a Reel is the strongest option. If posting a carousel
instead, lead with the best 2021 photo — it's the only slide most people see.

### X (249 characters, fits)

> May 2021: Cav's was our temporary home.
>
> Three weeks later Chelsea won the Champions League.
>
> We're going back. Cav's moved a block since — new build, serious AV.
>
> Technically a different room. Choosing not to let that bother us.
>
> phillybluescfc.com

Reply to your own post with a 2021 photo — photos in replies dodge the link penalty
and give the post a second life.

---

## Media assets

All in `docs/assets/`, all shot **29 May 2021** — the day Chelsea beat Man City in
Porto.

| File | What it is |
|---|---|
| `cav2021-celebration-web.mp4` | 32s, 6.1MB, 960×540. Full-time celebration outside Cav's — arms up, trophy presentation on screens behind |
| `cav2021-poster.jpg` | Poster frame, also now the og:image |
| `cav2021-street.jpg` | The old Cavanaugh's awning from the sidewalk |
| `cav2021-banner.jpg` | Philly Blues banner + signed Chelsea ball, next to a COVID social-distancing sign |
| `crest.png` / `crest-knockout.png` / `crest-512.png` | Club crest |
| `osc-logo.jpg` | Chelsea-issued Official Supporters Club badge |

Originals of the video and photos are much larger; the versions above are web-sized.
Keep the originals somewhere safe — the 90MB video is the archival copy.

**Note:** identifiable faces appear in all three 2021 items. Fine for a supporters
group, but if anyone would rather not be on a public site, that's worth knowing.

---

## Guardrails — do not break these

**1. Philly Blues is independent.** It has **never** been affiliated with Chelsea in
America or any other US umbrella organisation. Source ticketing rules from Chelsea FC
only. An earlier draft of the site drew on a third-party US organisation's guide;
those details were that organisation's own procedures, not Chelsea policy, and were
removed. Do not reintroduce them.

**2. Chelsea logo usage.** Three rules from the OSC welcome pack: no stretching or
skewing, no effects or shadows, no busy backgrounds. An early draft ghosted the crest
at 11% opacity as a hero background — that's an effect, and it was removed. Both
marks now sit clean on plain fields. Keep it that way.

---

## Open items — none blocking

**Content gaps on the site**
- "300+ on the mailing list" — carried from the old site, unverified
- Matchday opening time at Cav's — currently "roughly an hour before kickoff"
- Venue paragraph still says Cav's is "built for watching football" without
  mentioning the rebuild or the AV system. Replacement copy is in
  `PhillyBlues_Social_Rollout.md` under "Before you post"

**Still unanswered by the officers**
- How away ticket orders actually run — timings, payment, oversubscription. The away
  card on the site is deliberately thin because of this
- What the Chelsea OSC portal join link does for a member:
  `https://officialsupportersclubs.chelseafc.com/join-club/2040D543ACCB4C66B69D70140BAEE345`
  If that's how members get on the roster, it should be the main join button
- Whether there's a current 2026/27 OSC logo (the pack is the 2019/20 issue)

**Officer review email** — a draft exists in Gmail to Bharat, David and Garrett. It
still needs the two review PNGs attached and a feedback date. It predates the site
going live, so it may be worth rewriting as "it's live, take a look" instead.

**Repo housekeeping** — checked and clean. The project brief and review files were
never committed; git history contains no officer email addresses. Nothing to fix.

---

## After the 24th

- Photos from the first matchday at the new Cav's — the venue section has no images
  of the current room, only 2021
- Consider a Post 4: how the first one back went
- Domain renews **25 November 2026**. Set a reminder for **1 November**
- Two people should have registrar and repo access; credentials in a shared password
  manager
