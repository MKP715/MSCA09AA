# MSCA09 — Mid-Southern California Area 09 of Alcoholics Anonymous

The Area 09 website. One HTML file, a folder of CSV files, and a folder of
documents. It is a static site: it runs on GitHub Pages with no server, no
database and no plugins.

**Live site:** publish this repository with GitHub Pages (Settings → Pages →
Deploy from a branch → `main` / root).

---

## Why it is built this way

The Ad Hoc Website Committee's final report (June 2026) listed the problems.
Each one is answered by a structural decision here, not by a promise to try
harder:

| Committee finding | How this site answers it |
|---|---|
| Content goes stale; minutes stopped at Dec 2024, motions at Aug 2025 | Every changing word lives in `data/*.csv`. Editing a row on github.com updates the site in about a minute — no CMS, no plugin, no webmaster bottleneck. |
| Anonymity breaches — personal e-mails, phones, occasional addresses | Published data carries **first name + last initial only** and **role-based service addresses only**. There is nowhere in this repository for a personal phone number to hide. See "Anonymity rules". |
| Broken links, dead forms, dead QR codes | Every internal link is a `#/` route into the same file, so internal links cannot 404. Every document and flyer is stored **in this repository** — nothing breaks when the old site is retired. |
| Navigation is cluttered; information buried in PDFs | Six top-level menu items. The district flyer, the district directory and the meeting calendar are searchable, filterable pages; the PDFs remain as printable downloads, not as the only source. |
| Single point of failure — only the webmaster can update | Anyone the Area gives repository access to can edit a CSV in the browser. Every change is in git history. |
| Retire the legacy "blue site" (area09.org) | Not a code change — but note `area09.org` currently serves an **expired TLS certificate**, so browsers show a full-page security warning. It should be retired or redirected. |
| English/Spanish parity | Every page has an EN/ES toggle; the data files carry Spanish columns. |

---

## Anonymity rules — read before editing any file

Tradition Eleven asks us to maintain personal anonymity at the level of press,
radio and films. The public internet is all three. Everything committed here
is public, permanently, and is indexed by search engines.

**Never commit to this repository:**

- a member's last name (write `Jane D.`, never `Jane Doe`)
- a personal e-mail address (use `registrar@msca09aa.org`, never a `@gmail.com`)
- a personal phone number
- a home address
- a sobriety date, a home group, or anything else that identifies a member
- a photograph in which an A.A. member's face can be recognised
- a flyer that carries any of the above — check flyers before adding them

The full Panel roster, with personal contact details, belongs in the Area's
private spreadsheet. `.gitignore` blocks it from ever being committed;
`data/trusted-servants.csv` is the public, redacted view of it.

If you spot a breach, fix it and tell `webmaster@msca09aa.org`. Note that git
keeps history: removing a name in a new commit does not remove it from the
repository's past. If something serious is committed, ask for the history to
be rewritten.

---

## Editing the site

### The data files — everything on the site comes from these

| File | Feeds |
|---|---|
| `data/content.csv` | **Every heading, sentence and paragraph on the site**, in English and Spanish. Three columns: `key`, `en`, `es`. Change a sentence here and it changes on the page. |
| `data/ui.csv` | Every interface label — buttons, filters, column headings, toasts. Same three columns. |
| `data/nav.csv` | The menu. A row with an empty `parent` is a top-level item; a row naming a parent becomes a dropdown entry. Changing this changes the header, the mobile menu and the footer links at once. |
| `data/kinds.csv` | The colour, icon and bilingual label for every category: meeting types, event types, Area meeting types, document folders and resource groups. Add a row to introduce a new category. |
| `data/blocks.csv` | The repeating card lists — home quick links, newcomer steps, anonymity rules, contribution instructions, contact steps, "at a glance" facts. Grouped by `page` + `section`, ordered by `sort`. |
| `data/districts.csv` | The Districts page and district modals. `covers_cities` is a `;`-separated list and drives the city search. |
| `data/trusted-servants.csv` | Panel 76 page, committee chair names, district officers. `body_sort` / `position_sort` control ordering. |
| `data/committees.csv` | Committees page and modals. `color` picks the card gradient; `aa_url` links out to aa.org. |
| `data/events.csv` | Events page and event modals, including flyer images. |
| `data/area-meetings.csv` | The approved ASC / Assembly schedule for the panel. |
| `data/resources.csv` | A.A. Resources page and the central-office lists. |
| `data/documents.csv` | Minutes, motions, agendas, reports — the current record *and* the whole archive. `collection` is `Current` or `Archive`; `publish` is `yes` or anything else to withhold a file. |
| `data/archive-review.csv` | The 313 archived documents that carry a personal e-mail address or phone number, for the Area to triage. Not read by the site. |
| `data/calendar.ics` | The Service Calendar. **Do not edit by hand** — see below. |

Nothing on the page is written into `index.html` — the headings, the menu, the
labels, the colours and the copy all come from the files above. The only text
the site does not own is the meeting titles, which come from the Area's Google
Calendar.

All CSVs are UTF-8 with a BOM, so Excel opens them correctly on a double-click.
Keep the header row. If a value contains a comma, wrap it in double quotes —
any spreadsheet does that for you on save.

### How the long pages behave

Anything that grows over time starts folded, so a page opens as a list of
headings rather than a wall of cards:

- **Documents / Archive** — every category is closed. Its cards are not even
  built until you open it, which is why a page holding 1,717 documents loads
  with a few hundred DOM nodes instead of twenty-five thousand. Inside a
  category, each year is its own fold. Typing in the search box opens whatever
  it matched, and *Expand all* / *Collapse all* sit above the list.
- **Events** — the Area calendar shows what is still to come; meetings already
  held this year and earlier events are folded away with a count.
- **Panel 76** — the Area's own bodies are open, the twenty-two districts are
  folded. Searching or filtering opens everything that matched.
- **Service calendar** — opens on the next 30 days, with 60 and 90 day
  options next to the language chips.

### To change something

1. Open the file on github.com and press the pencil icon.
2. Edit the row. Commit.
3. Wait about a minute for Pages to rebuild, then hard-refresh.

There is no build step and nothing to install.

### To add an event

1. Put the flyer in `docs/events/` as a JPEG no wider than ~1400px, plus a
   `…thumb.jpg` at ~520px wide for the card preview.
2. Add a row to `data/events.csv`. `slug` becomes the shareable link
   (`#/events/<slug>`), so keep it short, lowercase and unique.
   `flyers` is a `;`-separated list of paths.
3. Paste the flyer's text into `description` so it is searchable and readable
   on a phone. Strip last names, personal e-mails and personal phone numbers.

### The trusted servants list

`data/trusted-servants.csv` is built from every tab of the Panel workbook —
the Area board, the D.C.M.C.s, the committee chairs, each district's own tab,
YPAA, and the previous panel. 211 rows: 149 for Panel 76 and 62 for Panel 74,
kept so the earlier panel's record is not lost.

Two tabs are deliberately left out. *P76 — Get to know you!* holds the board's
personal introductions, and *zoom schedule* is covered by the calendar. One
person is left out too: the D15 tab lists a member under the heading
"member" rather than as a trusted servant, so she is not published.

The roster is written out inside `tools/build_roster.py` rather than read from
the workbook at run time. That is on purpose — it keeps the workbook, with
everyone's personal e-mail address, phone number and sobriety date, out of the
repository. When the panel changes, edit that script and re-run it:

```sh
python tools/build_roster.py     # rewrite data/trusted-servants.csv
python tools/verify_roster.py    # check nobody was dropped (needs openpyxl)
```

`verify_roster.py` reads the workbook where it sits beside the repository and
reports anyone in it who is missing from the site, anyone on the site who is
not in it, and any surname, personal address or phone number that slipped
through.

The **Panel 76** page shows the current panel by default, with a *Panel 74*
chip beside the language filter. An earlier panel opens folded, because it is
history rather than a directory.

### The archive

`docs/archive/` holds everything recovered from the Area's two previous
websites — **msca09aa.org** (the WordPress site) and **area09.org** (the older
"blue site"). Both were crawled in full: 698 pages were walked, every document
either site linked to was checked, and **1,580 files were downloaded**, sorted
by kind and year, given a readable title and listed in `data/documents.csv`
with `collection = Archive`. The record now runs from **1999 to today**.

| | |
|---|---|
| Minutes | 468 |
| G.S.C. conference material | 233 |
| District records | 219 |
| Newsletters | 165 |
| Reports (incl. 29 Delegate's sharing sessions) | 129 |
| Finances | 70 |
| Guidelines & bylaws | 66 |
| Event flyers | 83 |
| PRAASA, workbooks, forms, calendars, archives committee | 96 |

It is reachable at `#/archive`, from **Service → Archive**, and through the
Documents page's search, category and year filters.

Three things worth knowing:

- **Some Area writing only ever existed as a web page** — the Delegate's
  sharing sessions and G.S.O. announcement round-ups from 2020 to 2024. Those
  58 posts were saved as standalone HTML in `docs/archive/pages/`. The Area's
  *static* pages were deliberately not copied: this site replaces them, and
  they carry the contact details the committee asked us to stop publishing.
  Two pages the Area had put behind a login were left alone.
- **Large scans were re-compressed** with Ghostscript (495 MB → 283 MB) so the
  repository stays a workable size. The originals are still on the old sites;
  if a particular scan is now too soft to read, fetch that one file again
  before those sites are retired.
- **Audio recordings were not brought across.** The WordPress site holds a set
  of Spanish-language workshop recordings totalling roughly 780 MB — too much
  for a git repository. They should be moved to the Area's Google Drive before
  msca09aa.org is switched off.

Only two files could not be recovered; both already 404 on the old site.

### Reviewing the archive for anonymity

These are historical records. They were public on both old sites for years,
and many of them contain what the Ad Hoc Website Committee asked us to stop
publishing: members' phone numbers and personal e-mail addresses.

Every archived PDF was read and scanned. **313 documents contain a personal
e-mail address or a phone number that is not an A.A. service line.** They are
listed in **`data/archive-review.csv`**, with the file, its category and year,
how many of each were found, and examples.

Nothing has been withheld — these documents were already public, and it is the
Area's conscience, not the webmaster's, that decides what stays up. But acting
on that list is a one-cell edit:

> Set the `publish` column in `data/documents.csv` to anything other than
> `yes` and the file disappears from the site's listing on the next load.

Use the `decision` and `notes` columns in `archive-review.csv` to record what
the Area decides, so the next panel can see the reasoning.

### The service meeting calendar

`data/calendar.ics` mirrors the Area's Google Calendar
(*MSCA09 Service Meetings*). A scheduled GitHub Action
(`.github/workflows/refresh-calendar.yml`) re-downloads it every six hours and
commits it when it changes.

**So: add or change a meeting in Google Calendar, not in this file.** To
publish a change immediately, open the Actions tab and press *Run workflow* on
"Refresh service calendar".

The page cannot fetch the Google feed in the browser — Google sends no
`Access-Control-Allow-Origin` header on the `.ics` endpoint. The mirror is how
a static site stays in sync; the "Google Calendar" tab embeds the live
calendar in an iframe, which is never affected.

**The event description format matters.** The site reads structured fields out
of each event's description:

```
MSCA09|District|Hybrid

--
District 6
1st Tuesday @ 7:00 PM (Pacific)
Location: 6652 Heil Ave, Huntington Beach
Zoom ID: 899 2638 0668
Passcode: Big6
Web: district6area09.org
Covers: Balboa, Corona Del Mar, Fountain Valley, ...
```

- First line `MSCA09|<type>|<format>` — type is `District`, `H&I`,
  `Intergroup` or `Area` (sets the colour and the Type filter); format is
  `Hybrid`, `Physical` or `Online` (sets the Format filter).
- A Spanish-speaking meeting has `(Spanish)` in the title, or the line
  `Spanish-speaking district` in the description.
- `Zoom ID:`, `Passcode:`, `Web:` and `Covers:` are parsed into their own fields.
- The recurrence rule drives the "Monthly pattern" grid — the live version of
  the printed flyer. `FREQ=MONTHLY;BYDAY=1TU` puts a meeting in week 1,
  Tuesday; `FREQ=WEEKLY;BYDAY=MO` puts it on every Monday row.

---

## Shareable links

Every event, service meeting, district, committee and flyer has its own hash
URL, so any of them can be linked to or shared directly:

```
#/events/msca-area-09-panel-76-servathon
#/meetings/msca09-d08-msca09-local
#/districts/12
#/committees/archives
#/flyer/docs%2Fevents%2Fsoberfest-alcoholic-family-feud-1.jpg
```

Opening one of those URLs renders the page behind it and opens the detail as a
modal. The **Share** button inside every modal uses the phone's native share
sheet on touch devices and copies the link to the clipboard everywhere else.

---

## Running it locally

The page loads `data/*.csv` with `fetch()`, and browsers block that over
`file://`. Serve it over HTTP:

```sh
python -m http.server 8000
# then visit http://localhost:8000/
```

Double-clicking `index.html` shows the page with an explanatory banner but no
data.

---

## What is in the repository

```
index.html                     the whole site — HTML, CSS and JS
data/                          everything that changes, as CSV
docs/                          every document and flyer, stored locally
  minutes/<year>/                approved ASA / ASC minutes, EN + ES
  motions/  conference/  calendars/  contributions/  reports/
  events/                        event flyers (+ .thumb.jpg previews)
  flyers/                        district calendar, contributions flyer, Zelle QR
  archive/                       recovered from the two previous websites
    minutes/ newsletters/ finances/ guidelines/ workbooks/ conference/
    reports/ delegate/ praasa/ archives/ flyers/ forms/ calendars/
    districts/d<n>/              documents that lived on a district's pages
    pages/                       posts that only ever existed as web pages
    misc/<year>/
tools/                         scripts a web servant re-runs; see tools/README.md
.github/workflows/             keeps data/calendar.ics in step with Google
```

Everything above the fold is deliberate: `index.html` is the site, `data/` is
what you edit, `docs/` is what you link to, and `tools/` is how you check your
work. Nothing else lives at the top level.

**Before you push:**

```sh
python tools/check_site.py
```

It catches the failure that is hardest to spot by eye — a file that exists on
your machine but is not committed, which works locally and 404s once
published. It also checks for links back to the old sites, personal contact
details, surnames in the roster, and missing `content.csv` / `ui.csv` keys.

Third-party libraries load from CDN and nothing is vendored: Tailwind CSS,
Font Awesome, Google Fonts, PapaParse (CSV), ical.js (calendar) and AOS
(scroll animations). The only run-time request to another website is the
optional Google Calendar iframe on the calendar page.

---

## Going live on msca09aa.org

1. Settings → Pages → deploy from `main` / root.
2. Add a `CNAME` file containing `msca09aa.org`.
3. Point DNS at GitHub Pages (four `A` records for the apex, or a `CNAME` for
   `www`), then tick **Enforce HTTPS**.

Nothing on this site depends on the old WordPress installation, so it can be
switched off the moment the domain moves.

---

## Still to do

- Post minutes after December 2024 and motions after August 2025 — the gap the
  committee reported is in the data, and the Documents page says so plainly.
- Fill the committee positions marked *Open* in `data/trusted-servants.csv`.
- Retire or redirect `area09.org` (expired certificate).
- Confirm each district's meeting details with its D.C.M.C.; the seed data
  comes from the 2026 flyer and the Panel 76 roster.
- Add Spanish `title_es` values in `data/events.csv` for bilingual events.

---

*A.A.®, Alcoholics Anonymous®, the Big Book®, Box 4-5-9®, Grapevine® and
La Viña® are registered trademarks of A.A. World Services, Inc. and
A.A. Grapevine, Inc.*
