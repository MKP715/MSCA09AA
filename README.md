# MSCA09 — Mid-Southern California Area 09 of Alcoholics Anonymous

The Area 09 website. One HTML file, a folder of CSV files, and nothing else.
It is a static site: it runs on GitHub Pages with no server, no database and
no plugins.

**Live site:** publish this repository with GitHub Pages (Settings → Pages →
Deploy from a branch → `main` / root).

---

## Why it is built this way

The Ad Hoc Website Committee's final report (June 2026) identified five
problems. Each one is answered by a structural decision here, not by a
promise to try harder:

| Committee finding | How this site answers it |
|---|---|
| Content goes stale; minutes stopped at Dec 2024, motions at Aug 2025 | Everything that changes lives in `data/*.csv`. Editing a row on github.com updates the site in about a minute — no login to a CMS, no plugin, no webmaster bottleneck. |
| Anonymity breaches — personal e-mails, phones, occasional addresses | The published data files contain **first name + last initial only**, and **role-based service addresses only**. There is nowhere in this repository for a personal phone number to hide. See "Anonymity rules" below. |
| Broken links, dead forms, dead QR codes | Only 8 pages exist and every internal link is a `#/` hash route into the same file, so internal links cannot 404. External links were verified when the site was built. |
| Navigation is cluttered and information is buried in PDFs | Six top-level menu items. The district meeting flyer, the district directory and the meeting calendar are now searchable, filterable web pages — the PDFs remain as printable downloads, not as the only source. |
| Single point of failure — only the webmaster can update | Anyone the Area gives repository access to can edit a CSV in the browser. No credentials to hand over, and every change is in git history. |
| Retire the legacy "blue site" (area09.org) | Not a code change — but note that `area09.org` currently serves an **expired TLS certificate**, so browsers show a full-page security warning. It should be retired or redirected. |
| English/Spanish parity | Every page has an EN/ES toggle, and the data files carry Spanish columns (`title_es`, `summary_es`, …). |

---

## Anonymity rules — please read before editing any file

Tradition Eleven asks us to maintain personal anonymity at the level of press,
radio and films. The public internet is all three. Everything committed to
this repository is public, permanently, and is indexed by search engines.

**Never commit to this repository:**

- a member's last name (write `Jane D.`, never `Jane Doe`)
- a personal e-mail address (use `registrar@msca09aa.org`, never a `@gmail.com`)
- a personal phone number
- a home address
- a sobriety date, a home group, or anything else that identifies a member
- a photograph in which an A.A. member's face can be recognised

The full Panel 76 roster — with personal contact details — belongs in the
Area's private spreadsheet, not here. `data/trusted-servants.csv` is the
public, redacted view of it.

If you spot a breach, fix it and tell `webmaster@msca09aa.org`. Note that
git keeps history: removing a name in a new commit does not remove it from
the repository's past. If something serious is committed, ask for the history
to be rewritten.

---

## Editing the site

### The data files

| File | What it feeds | Notes |
|---|---|---|
| `data/districts.csv` | the Districts page and the district cards | one row per district; `covers_cities` is a `;`-separated list and drives the city search |
| `data/trusted-servants.csv` | the Panel 76 page, committee chair names, district officers | one row per person-position; `body_sort` / `position_sort` control ordering |
| `data/committees.csv` | the Committees page | `color` picks the card gradient; `aa_url` links out to aa.org |
| `data/documents.csv` | Minutes, Motions & Agendas | add a row when a document is approved |
| `data/events.csv` | upcoming events | one row per event; past events drop off automatically |
| `data/area-meetings.csv` | the approved Area calendar | the ASC / Assembly schedule for the panel |
| `data/resources.csv` | the A.A. Resources page and the central-office lists | |
| `data/calendar.ics` | the Service Calendar (list, month and pattern views) | **do not edit by hand** — see below |

All files are UTF-8 with a BOM, so Excel opens them correctly by double-click.
Keep the header row. If a value contains a comma, wrap it in double quotes —
any spreadsheet does this for you on save.

### To change something

1. Open the file on github.com and press the pencil icon.
2. Edit the row. Commit.
3. Wait about a minute for Pages to rebuild, then hard-refresh the site.

That is the whole process. There is no build step and nothing to install.

### The service meeting calendar

`data/calendar.ics` is a mirror of the Area's Google Calendar
(*MSCA09 Service Meetings*). A scheduled GitHub Action
(`.github/workflows/refresh-calendar.yml`) re-downloads it every six hours
and commits it when it changes.

**So: add or change a meeting in Google Calendar, not in this file.**
To publish a change immediately, open the Actions tab and press
*Run workflow* on "Refresh service calendar".

The site cannot fetch the Google feed directly in the browser — Google sends
no `Access-Control-Allow-Origin` header on the `.ics` endpoint, so the
request is blocked. The mirror is how a static site stays in sync. The
"Google Calendar" tab on the calendar page embeds the live calendar in an
iframe, which is never affected.

**The event description format matters.** The site reads structured fields
out of each event's description. Keep this shape:

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

- First line: `MSCA09|<type>|<format>`
  - type is `District`, `H&I`, `Intergroup` or `Area` — it sets the colour and the Type filter
  - format is `Hybrid`, `Physical` or `Online` — it sets the Format filter
- A Spanish-speaking meeting has `(Spanish)` in the event title, or the line
  `Spanish-speaking district` in the description. That drives the language filter.
- `Zoom ID:`, `Passcode:`, `Web:` and `Covers:` are parsed into their own fields.
- The recurrence rule drives the "Monthly pattern" grid — the live version of
  the printed flyer. `FREQ=MONTHLY;BYDAY=1TU` puts the meeting in week 1,
  Tuesday; `FREQ=WEEKLY;BYDAY=MO` puts it on every Monday row.

---

## Running it locally

The page loads `data/*.csv` with `fetch()`, and browsers block that over
`file://`. Open it through a local web server:

```sh
python -m http.server 8000
# then visit http://localhost:8000/
```

Double-clicking `index.html` shows the page with an explanatory banner but no
data.

---

## What is in the repository

```
index.html                          the entire site — HTML, CSS and JS
data/                               everything that changes
.github/workflows/refresh-calendar.yml   keeps data/calendar.ics in sync
contribute.png                      the Zelle QR code used on the 7th Tradition page
MSCA09 DistrictCal.pdf              the printable district meeting flyer
MSCA09 7th Trad Contributions…pdf   the printable contributions flyer (EN & SP)
Final-Report-…Website Committee…docx the Ad Hoc Website Committee report
MSCA09-Service-Meetings.ics         the original hand-built calendar (source of data/calendar.ics)
```

Third-party libraries are loaded from CDN and nothing is vendored:
Tailwind CSS, Font Awesome, Google Fonts, PapaParse (CSV), ical.js
(calendar) and AOS (scroll animations).

---

## Going live on msca09aa.org

1. Settings → Pages → deploy from `main` / root.
2. Add a `CNAME` file containing `msca09aa.org`.
3. Point the domain's DNS at GitHub Pages (four `A` records for the apex, or a
   `CNAME` for `www`), then tick **Enforce HTTPS**.
4. Keep the old WordPress site reachable until `data/documents.csv` links are
   migrated — several rows still point at `msca09aa.org/wp-content/…`.

---

## Still to do

- Migrate the document archive off the WordPress uploads folder so
  `data/documents.csv` points at files in this repository.
- Post minutes after December 2024 and motions after August 2025 — the gap the
  committee reported is in the data, and the page shows it honestly.
- Fill the committee positions marked *Open* in `data/trusted-servants.csv`.
- Retire or redirect `area09.org` (expired certificate).
- Confirm every district's meeting details with its D.C.M.C.; the seed data
  comes from the 2026 flyer and the Panel 76 roster.

---

*A.A.®, Alcoholics Anonymous®, the Big Book®, Box 4-5-9®, Grapevine® and
La Viña® are registered trademarks of A.A. World Services, Inc. and
A.A. Grapevine, Inc.*
