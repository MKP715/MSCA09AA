# tools/

Small scripts for the jobs a web servant has to do more than once. Nothing
here runs on the live site — the site is `index.html` plus `data/` and `docs/`.
These only rebuild or check those files.

They need Python 3 and, where noted, a package:

```sh
pip install openpyxl pymupdf
```

Run them from the repository root, not from inside this folder.

---

## `build_css.py` — rebuild `tailwind.css` after editing the page

```sh
python tools/build_css.py
```

**Run this whenever you add or remove a Tailwind class in `index.html`.** The
stylesheet only contains the classes the page actually used at build time, so
a new class does nothing until you rebuild.

The site used to load Tailwind from the Play CDN, which downloads about 400 KB
and then compiles the stylesheet in the visitor's browser on every visit — a
first paint of nearly twelve seconds on a throttled phone. Building it here
instead ships one cached 48 KB file and no compile step for the visitor.

Needs Node and npm on PATH; the Tailwind binary is fetched with `npx` the
first time and cached by npm after that. It writes nothing unless the build
succeeds, so a failed run leaves the published stylesheet alone, and it
refuses to write a suspiciously small file — that means the content path in
`tools/css/tailwind.config.js` stopped matching `index.html`.

The theme lives in `tools/css/tailwind.config.js`: the `ink` and `brand`
palettes, the two font families, and the `floaty` / `drift` / `shimmer`
animations. `tools/css/tailwind.input.css` is just the three `@tailwind`
lines. Everything else the page needs is in the `<style>` block inside
`index.html`.

---

## `fetch_events.py` — refresh the events from msca09aa.org

```sh
python tools/fetch_events.py --dry-run   # report, change nothing
python tools/fetch_events.py             # rewrite data/events.csv
python tools/fetch_events.py --images    # also download new flyers to Drive
```

Reads the events out of The Events Calendar's REST feed on msca09aa.org and
rewrites `data/events.csv`. Three things it does that are worth knowing:

**It folds a repeating event back into one row.** The feed lists every
occurrence separately — the ACYPAA business meeting alone is fourteen entries.
The dates are grouped by title and time, the rule behind them is worked out,
and the row gets an `rrule` such as `FREQ=MONTHLY;BYDAY=1SU,3SU`. Dates the
rule would produce but the Area did not actually schedule go in `exdates`, so
the series still reproduces the published dates *exactly* — no meeting appears
that nobody agreed to, and none is lost. Each series ends at its last
published date; re-run this when the Area schedules more.

Area business meetings are never folded: `data/area-meetings.csv` is the
authority for those and the real pattern is irregular.

**It removes members' phone numbers.** Flyers routinely say "contact Andrew at
562-507-6618". That must not go on a public website, and doing it here rather
than by hand means a later refresh cannot quietly put it back. Toll-free
numbers are kept — those are hotels and offices, not members. Anything removed
is listed in the run's output.

**It rebuilds unusable slugs.** A slug is the shareable `#/events/…` link. One
of WordPress's was `d09-gsr-school-virtual-only-id-928-8170-4093-pc634401-…`,
which puts a Zoom ID and passcode in a public URL. Slugs that carry
credentials, are bare post numbers, or say nothing about the event are rebuilt
from the title; everything else is left alone so shared links keep working.

With `--images` it downloads any new flyer into the Drive folder as
`<slug>-1.jpg` plus the `.thumb.jpg` the cards use, both re-encoded down from
the multi-megabyte originals. Run `tools/drive_links.py` afterwards to turn
them into Drive addresses.

---

## `build_social_card.py` — the picture chat apps show for a shared link

```sh
pip install pillow
python tools/build_social_card.py
```

Draws `social-card.jpg` (1200×630) from `hero.jpg` and the Area's name, read
straight out of `data/content.csv` so the card cannot drift from the page.
Re-run it after changing the banner photo or `home.title`.

---

## `check_site.py` — run this before you push

```sh
python tools/check_site.py
```

Checks the things that quietly break a static site:

- every file the data points at exists **and is committed** — a file git
  ignores works locally and 404s once published, which is the failure mode
  that is hardest to notice
- nothing links back to msca09aa.org or area09.org
- no personal e-mail address or phone number in any data file
- every name in the roster is in `First L.` form
- every `content.csv` / `ui.csv` key the page asks for has a row
- every menu entry in `nav.csv` points at a route that exists

Exits non-zero when it finds something, so it can go in a git hook or an
Action.

---

## `drive_links.py` — point the site at Google Drive

```sh
python tools/drive_links.py              # rewrite documents.csv and events.csv
python tools/drive_links.py --dry-run    # just report
```

Reads every file id out of Google Drive for Desktop's local database and
rewrites the CSVs to address each file by id. Nothing is downloaded and no API
key is needed — Drive for Desktop just has to be signed in and synced.

`docs/archive/pages/*.html` keeps its relative path: Drive hands an `.html`
file over as a download rather than rendering it, so those stay in the repo.

## `check_links.py` — fetch every address

```sh
python tools/check_links.py            # all ~1,860 (slow)
python tools/check_links.py --sample   # 120, spread across the set
```

A 200 is not proof: Drive answers a request for a file nobody may see with a
sign-in page. This checks the content type too, and fails an HTML answer where
a PDF or an image was expected.

**`throttled` is not `failing`.** Drive starts answering 429 when one machine
asks for a few hundred files in a row, and the throttle sticks to your IP for
up to an hour — so a run right after a full check will report a pile of them.
The script already backs off and retries four times; anything still throttled
after that is counted and reported separately from real failures, and exits
`2` rather than `1`. Wait an hour and re-run, or lower `WORKERS` at the top of
the script. A file that has genuinely stopped being shared shows up as
*needs sign-in*, not as a throttle.

## `build_roster.py` — rebuild the trusted servants list

```sh
python tools/build_roster.py
```

Rewrites `data/trusted-servants.csv` from the panel workbook. **Edit this
script when the panel changes**, then re-run it — the names, positions and
service addresses are written out in the script itself, which keeps the
workbook (with everyone's personal contact details) out of the repository.

It covers every tab of the workbook: the Area board, D.C.M.C.s, committee
chairs, each district's own tab, YPAA, and the previous panel. Two tabs are
deliberately skipped: *P76 — Get to know you!* (personal introductions) and
*zoom schedule* (covered by `data/calendar.ics`).

## `verify_roster.py` — check nobody was dropped

```sh
pip install openpyxl
python tools/verify_roster.py
```

Reads the workbook next to the repository, pulls out everything that looks
like a person's name, and reports anyone who is in the workbook but not on
the site — and anyone on the site who is not in the workbook. Also checks
that no surname, personal address or phone number made it through.

---

## `scan_anonymity.py` and `build_review_list.py` — the archive review

```sh
pip install pymupdf
python tools/scan_anonymity.py      # reads every archived PDF
python tools/build_review_list.py   # writes data/archive-review.csv
```

The archive holds twenty years of Area records that were public on the old
sites. Many of them carry members' phone numbers and personal e-mail
addresses. These two scripts read every PDF and produce the list the Area
works from.

Nothing is withheld automatically. To take a document off the site, set its
`publish` column in `data/documents.csv` to anything other than `yes`.

## `shrink_pdfs.py` — keep the repository a sane size

```sh
python tools/shrink_pdfs.py
```

Re-compresses scanned PDFs over 700 KB with Ghostscript, keeping the smaller
copy only when it saves more than 15%. Needs Ghostscript installed; edit the
`GS` path at the top to match. It took the archive from 495 MB to 283 MB.

---

## `service-meetings-seed.ics`

The hand-built calendar the Area's Google Calendar was first loaded from,
kept as provenance. The live calendar is `data/calendar.ics`, refreshed from
Google by `.github/workflows/refresh-calendar.yml`. **Do not edit either one
by hand** — change the meeting in Google Calendar.
