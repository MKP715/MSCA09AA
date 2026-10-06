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
| Content goes stale; minutes stopped at Dec 2024, motions at Aug 2025 | Every changing word lives in `data/*.csv`, and every meeting and event in the Area's one Google Calendar. Editing a row on github.com, or an entry in Google Calendar, updates the site — no CMS, no plugin, no webmaster bottleneck. |
| Anonymity breaches — personal e-mails, phones, occasional addresses | Published data carries **first name + last initial only** and **role-based service addresses only**. There is nowhere in this repository for a personal phone number to hide. See "Anonymity rules". |
| Broken links, dead forms, dead QR codes | Every internal link is a `#/` route into the same file, so internal links cannot 404. Every document and flyer is stored **in the Area's own Drive folder** — nothing breaks when the old site is retired. |
| Navigation is cluttered; information buried in PDFs | Six top-level menu items. The district flyer, the district directory and the meeting calendar are searchable, filterable pages; the PDFs remain as printable downloads, not as the only source. |
| Single point of failure — only the webmaster can update | Anyone the Area gives repository access to can edit a CSV in the browser, and anyone given access to the calendars can add a meeting or an event from a phone. Every repository change is in git history. |
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
| `data/committee-guidelines.csv` | Each committee's written guidelines, one row per document: `committee` (the slug in committees.csv), `language` (`en`/`es`), `title`, `title_es`, `approved`, `url` (Drive) and `drive_path`. A committee can have several — English, Spanish, extras. Files live in `docs/Committee Guidelines/` in Drive; `tools/drive_links.py` keeps the `url` column current. Superseded versions go in that folder's `OLD/` subfolder and are not listed. |
| `data/resources.csv` | A.A. Resources page and the central-office lists. |
| `data/documents.csv` | Minutes, motions, agendas, reports — the current record *and* the whole archive. `collection` is `Current` or `Archive`; `publish` is `yes` or anything else to withhold a file. |
| `data/files.csv` | The handful of files the page itself links to — the district calendar flyer, the contributions flyer, the Zelle QR code. `key` is what the page asks for; `url` is its Drive address. |
| `data/archive-review.csv` | The 313 archived documents that carry a personal e-mail address or phone number, for the Area to triage. Not read by the site. |
| `data/calendar.ics` | Every business meeting and every event — the Area Calendar page, the home page, district meeting times. A mirror of the Area's **MSCA09** Google Calendar. **Do not edit by hand.** |

Nothing on the page is written into `index.html` — the headings, the menu, the
labels, the colours and the copy all come from the files above. Meetings and
events are the exception: they come from the Area's Google Calendar, so that
whoever keeps the calendar up to date keeps the website up to date too. See
"The calendar" below.

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
- **Area calendar** (`#/calendar`) — every meeting and every event, used as
  a database. At the top, the next Area meeting. On the left (a *Filters*
  drawer on a phone), a checkbox for every value of every filter —
  category, format, language, day, time of day, district, city, topic, and
  whether it comes with a flyer, an agenda or Zoom — each with how many
  entries it would leave, and *only* to pick just one. The categories are
  grouped (Area business, Service meetings, Learning & sharing, Gatherings),
  and a group's box ticks or unticks all of it. *Quick views* above them are
  one-click starting points. Six views: *Agenda* (day by day, today to
  twelve months ahead), *Week*, *Month*, *List* (every entry once —
  upcoming, past or all — as cards or a sortable table), *Monthly pattern*
  and the live *Google Calendar*. *Save as my view* keeps the choices in
  that browser, so the calendar opens that way next time.
- **Panel 76** — the Area's own bodies are open, the twenty-two districts are
  folded. Searching or filtering opens everything that matched.

On the calendar the view and the filters are kept in the address —
`#/calendar?view=month&type=District,H%26I&lang=Spanish,Bilingual`
(only these), `#/calendar?type=!Workshop,Social` (everything but these),
`#/calendar?view=list&when=past&topic=Concepts` — so a filtered view can be
bookmarked or sent to someone, and the Back button steps through them. The calendar used to be two pages, `#/meetings` and `#/events`; their
addresses, and every entry link under them, still open the same thing on
`#/calendar`.

### To change something

1. Open the file on github.com and press the pencil icon.
2. Edit the row. Commit.
3. Wait about a minute for Pages to rebuild, then hard-refresh.

**Editing the data needs no build step and nothing installed** — which is the
whole point of keeping the words in CSV. The one exception is `index.html`
itself: if you add or remove a Tailwind class there, run
`python tools/build_css.py` to rebuild `tailwind.css`, or the new class will
have no effect. See [`tools/README.md`](tools/README.md).

### To add an event or a meeting

Not here — in the Area's Google Calendar, **MSCA09**, written the way
"Writing a calendar event" below describes. Its type decides whether it counts
as a meeting, an event, or both. The site picks it up at the
next refresh (every six hours, or straight away with *Run workflow* on the
Actions tab).

### The home page banner

The banner is the Area's own coastline photo, carried over from the old site.
It lives in the repository rather than Drive, because it is the first thing a
visitor sees and Drive's image host is the one part of this setup that is not
a documented API.

To change it, replace **`hero.jpg`** (about 1600px wide) and
**`hero-small.jpg`** (about 900px, what phones load), then run:

```sh
python tools/build_social_card.py   # rebuilds the link preview to match
```

Both files are registered in `data/files.csv` as `home_hero` and
`home_hero_small`, so you can also point those rows at a Drive image instead
and the page will follow without touching `index.html`.

Two things to check before you use a photograph here:

- **No recognisable A.A. member.** Tradition Eleven applies to the front page
  more than anywhere else on the site. The current photo shows two people from
  behind, too far away to identify.
- **Contrast.** The Area's name sits on top of the photo in white. A bright
  or busy picture can push that below the readable threshold — the scrim in
  `index.html` (`.hero-scrim`) is what keeps it legible, and it may need
  darkening for a lighter photo.

The wording over it comes from `data/content.csv`: `home.title` is the big
line, `home.tagline` the gold line under it, `home.kicker` the small chip.

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

### The calendar

Every business meeting and every event is in one Google Calendar,
**MSCA09** ([open](https://calendar.google.com/calendar/embed?src=d750fd36f80cbdca09aefaa2310a3e2710790cd2f9c73d09d293bb23bbb052db%40group.calendar.google.com&ctz=America%2FLos_Angeles)):
the districts, Area committees, H&I, intergroups, the Area meeting and the
Service Study, and the assemblies, ASCs, Foro, Servathon, workshops,
conventions and YPAA events — everything msca09aa.org ever published, back
to December 2020.

A scheduled GitHub Action (`.github/workflows/refresh-calendar.yml`)
re-downloads it every six hours into `data/calendar.ics` and commits it when
it changed. **So: add or change things in Google Calendar, never in the
`.ics` file.** To publish a change immediately, open the Actions tab and
press *Run workflow* on "Refresh calendar".

The page cannot fetch the Google feed in the browser — Google sends no
`Access-Control-Allow-Origin` header on the `.ics` endpoint. The mirror is how
a static site stays in sync; the "Google Calendar" tabs embed the live
calendar in an iframe, which is never affected.

**The categories.** Every entry has exactly one, the *type* on its first
line. They are rows of `data/kinds.csv` (set `calendar`), which gives each a
label in both languages, a colour, an icon, the group it is listed under on
the calendar (`group`), and whether the home page treats it as a meeting, an
event or both (`pages`):

| group | type | use it for |
|---|---|---|
| Area business | `Area` | the repeating 2nd-Sunday Area meeting |
| | `Area Committee` | an ASC |
| | `Assembly` | an Assembly (ASA), including elections and sharebacks |
| | `Conference` | the General Service Conference cycle: Pre-Conference boot camps and sharing sessions, agenda-item reviews, mock conference, delegate report-backs |
| | `Foro` · `Servathon` | the Area's Foro and Servathon |
| Service meetings | `District` | a district business meeting, or an inter-district one |
| | `Committee` | an Area committee's meeting |
| | `H&I` | an H&I committee |
| | `Intergroup` | an intergroup or central office |
| Learning & sharing | `Service School` | GSR and DCM schools, the monthly service study, DCM sharing sessions |
| | `Workshop` | workshops, panels and presentations |
| | `History` | Heritage Days, Archives open houses, A.A. history |
| Gatherings | `Convention` | conventions, roundups, H&I conferences |
| | `Forum` | PRAASA and the regional forums |
| | `YPAA` | young people's events and committees |
| | `Social` | picnics, dinners, dances, anniversaries, alcathons |
| | `Event` | anything that fits none of these |

The home page "Up next" and the district times on the Districts page come
from the entries counted as meetings, "Upcoming Area events" from the
one-off entries counted as events. A district's meeting time, place and Zoom therefore live only in its
calendar entry; the meeting columns in `data/districts.csv` are just the
fallback if the calendar cannot be loaded.

**The Area meeting.** "MSCA09 Area Meeting" repeats on the 2nd Sunday so the
monthly pattern stays right. Each actual meeting — an ASC or an Assembly,
with its host district, place, flyer and agenda — is its own entry. When one
is announced, add its entry and **delete that date from the repeating Area
Meeting** (open the date, *Delete* → *This event*), or the day will be listed
twice. Every 2026 meeting already has its own entry, which is why the
repeating series starts in January 2027.

msca09aa.org is no longer read by anything. Its events, flyers and agendas
were copied into the calendar and the Drive folder in October 2026.

### Writing a calendar event

Every entry, meeting or event, keeps its details in the **description**, in
the same shape, so it can be filled in from the Google Calendar app on a
phone:

```
MSCA09|Committee|Virtual
Language: English
ZoomID: 851 7562 5116
Passcode: CEC76
Email: cecchair@msca09aa.org
IMG: https://drive.google.com/file/d/1AhGCh5roLXOLA3NjZP0pHCKkmLLDfuK8/view?usp=sharing
Note: Shown on the website under the meeting details.
--
Anything under the line is free text for people.
```

**The first line** is `MSCA09|<type>|<format>`.

- *type*: one of the categories in the table above, spelled exactly. To
  create a new one, add a row to `data/kinds.csv` (set `calendar`) with its
  group.
- *format*: `In person`, `Hybrid` or `Virtual`.

**The fields** come next, one per line, above the `--`. Leave out any that do
not apply.

| field | meaning |
|---|---|
| `Language:` | `English`, `Spanish` or `Bilingual` |
| `ZoomID:` · `Passcode:` | the Zoom meeting |
| `ZoomLink:` | the join link — only needed for a **hybrid** meeting, because a virtual one keeps its link in Location |
| `Web:` | a website, with or without `https://` |
| `Email:` | a **service** address (`…@msca09aa.org`), never a personal one |
| `Covers:` | the cities a district serves |
| `Host:` | the district or districts hosting it, written `D5` or `D6 & D12` — not for a district's own meeting |
| `Topic:` | what a workshop, school or committee is about, one or more of the topics in `data/kinds.csv` (set `topic`), e.g. `Topic: Concepts` or `Topic: Steps, Sponsorship` |
| `Title-ES:` | the Spanish title, shown when the page is in Spanish |
| `Cost:` | e.g. `$15 suggested contribution` |
| `IMG:` | a flyer's Drive share link — one line per flyer, the first is the cover |
| `Link:` | a document, e.g. `Link: Agenda (English) https://drive.google.com/file/d/…/view` |
| `Note:` | a short note the website shows with the details |

**Location** is the street address whenever people can go in person (venue
name first — `Imperial Alano Club, 8021 Rosecrans Ave, Paramount, CA 90723`);
for an online-only meeting it is the Zoom join link.

**Adding a filter.** The calendar treats each entry as a row and each
`Key: value` line above its `--` as a column. `data/filters.csv` says which
columns are filters on the calendar page: one row per filter, in `sort`
order, with its labels, an icon, `open` (`yes` to start unfolded), `views`
(empty for every view), and the label for entries that have no value
(`none_en`, `none_es`). `source` is either a column the page works out
itself — `type`, `format`, `day`, `time`, `district`, `city`, `has`, `year`
— or `field:<Name>` for any line in the descriptions. So to filter by, say,
who an event is for: write `Audience: GSRs` in the entries it applies to,
add `audience,Audience,Público,field:Audience,…` to `filters.csv`, and,
optionally, rows of set `audience` to `data/kinds.csv` to translate and
colour its values. Nothing in `index.html` changes. Several values on one
line are separated by commas.

**Quick views** are rows of `data/blocks.csv` with page `calendar` and
section `presets`: a title, an icon, a colour and the address it opens.
`{panel}` in the address becomes the current panel's two years.

**Under the `--`** is free text. The website shows it as an event's "About";
for a meeting it is for people reading Google Calendar, and only the `Note:`
lines appear on the site.

**Repeats** use Google Calendar's own *Custom* repeat — "Monthly on the third
Thursday", "Weekly on Wednesday". Always give it an end date (*Ends on…*),
normally the end of the panel; the site will otherwise print dates nobody
scheduled. Skip a date by deleting that one occurrence; move one by editing
just that occurrence. Both carry through to the site.

**Google's editor** stores a description with bold text or pasted links as
HTML. That is fine — the site reads it either way.

**`tools/check_calendars.py`** reads the mirror and lists any entry that
does not follow this, or that carries a personal e-mail address or phone
number. The Action runs it on every refresh and prints the result in its log,
so a mistake shows up there rather than as a strange card on the site.

### Flyers and agendas

Flyers live in the shared Drive folder (see "Files live in Google Drive"):

```
docs/events/<year>/<date>-<event>-1.jpg     event flyers, by year
docs/events/<year>/<date>-<event>-<doc>.pdf agendas and other documents
docs/meetings/<meeting>.jpg                 business-meeting flyers
```

To put one on an event: drop it in the right folder, let Drive for Desktop
sync, and run

```sh
python tools/drive_links.py --links docs/events/2026
```

which prints the `IMG:` (or `Link:`) line for every file there, ready to
paste above the `--`. Without the script: right-click the file in Drive →
*Share* → *Copy link*, and paste it after `IMG: `. The folder is shared as
"Anyone with the link", so a file put there is public as soon as it syncs.

The site shows a flyer straight from Drive — full size in the viewer and at
640 px on the cards — so there are no thumbnails to make. Keep a flyer under
about 1600 px on its long side.

**Check a flyer before adding it.** A member's phone number or surname on a
flyer is published with it.

---

## Shareable links

Every event, service meeting, district, committee and flyer has its own hash
URL, so any of them can be linked to or shared directly:

```
#/calendar/msca-area-09-panel-76-servathon-2026-11-14
#/calendar/msca09-d08-msca09-local
#/districts/12
#/committees/archives
#/flyer/https%3A%2F%2Flh3.googleusercontent.com%2Fd%2F<id>
```

A one-off entry's link is its title and date; a repeating meeting's is its
Google Calendar id, which never changes. A link shared before the move to the
calendar — the title alone, `#/calendar/msca-area-09-panel-76-servathon` —
still opens the entry of that name nearest to today, and the old
`#/events/…` and `#/meetings/…` links still open theirs.

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

## Files live in Google Drive

The documents and flyers are **not** in this repository. They live in the
Area's Google Drive, in the shared folder
[RowlettAATech/MSCA09AA](https://drive.google.com/drive/folders/1ZabOXfYv2wIcFiV1gPgGSvXd1b4Z917F),
and the site addresses each one by its Drive file id:

| kind | address |
|---|---|
| a document | `https://drive.google.com/file/d/<id>/view` |
| an image | `https://lh3.googleusercontent.com/d/<id>` |

1,659 documents are served that way from `data/documents.csv`, and another
465 flyers and agendas from the calendar — `docs/events/<year>/` holds
every event msca09aa.org published since December 2020, and `docs/meetings/`
the business-meeting flyers.

**One exception.** `docs/archive/pages/` — 58 posts that only ever existed as
web pages — stays here. Google Drive hands an `.html` file to the browser as a
*download* rather than rendering it, and these are pages meant to be read.
They come to about 2 MB.

### Adding or replacing a file

1. Put it in the right folder inside the shared Drive folder. Keep the same
   layout the site expects — `docs/minutes/2026/…`. (A flyer for an event or
   a meeting goes on its calendar event instead — see "Flyers and agendas".)
2. Let Google Drive for Desktop finish syncing.
3. Run:

```sh
python tools/drive_links.py     # rewrite the CSVs with the new file ids
python tools/check_links.py     # fetch every address and confirm it answers
```

`drive_links.py` reads the file ids out of Drive for Desktop's local
database, so nothing is downloaded and no API key is needed. Each row keeps
its original path in a `drive_path` column, which is what the script matches
on — so a file can move in Drive and still be found by name.

### Three things to know about hosting on Drive

- **Sharing has to stay "Anyone with the link".** If that is ever narrowed,
  every document on the site stops working at once, not one at a time.
- **Drive is not a content network.** It applies a daily download cap per
  file. An Area site will not go near it, but a document that suddenly gets
  passed around widely can start returning an error page instead of the file.
- **`lh3.googleusercontent.com` is how Drive serves images inline.** It works
  and is what Drive itself uses, but Google does not document it as a public
  API. If images ever stop loading, that is the first thing to check —
  `https://drive.google.com/thumbnail?id=<id>&sz=w1600` is the fallback.

For what it is worth: the repository was 564 MB before this move, against
GitHub Pages' 1 GB limit. It was not out of room. Moving to Drive gives
plenty of headroom and keeps clones small.

## What is in the repository

```
index.html                     the whole site — HTML, CSS and JS
tailwind.css                   built from index.html by tools/build_css.py
social-card.jpg                the preview image for links shared to chat apps
hero.jpg  hero-small.jpg       the home page banner photo
robots.txt  sitemap.xml        for search engines
data/                          everything that changes, as CSV, plus the
                               calendar mirror (calendar.ics)
docs/archive/pages/            58 posts Drive cannot serve as pages
tools/                         scripts a web servant re-runs; see tools/README.md
tools/css/                     the Tailwind config tailwind.css is built from
.github/workflows/             keeps data/calendar.ics in step with Google
```

**Before you push:**

```sh
python tools/build_css.py      # only if you changed a class in index.html
python tools/check_site.py     # structure, anonymity, missing keys, calendars
python tools/check_links.py --sample     # spot-check the Drive addresses
```

`check_site.py` catches a file named directly in `index.html` instead of
through `data/files.csv`, a repo file that is not committed, links back to
the old sites, personal contact details, surnames in the roster, missing
`content.csv` / `ui.csv` keys, and — through `tools/check_calendars.py` — a
calendar event with a personal address or phone number in it. Calendar
entries that are merely incomplete are listed as notes to fix in Google
Calendar.

### What the page loads

**Tailwind CSS is built ahead of time** into `tailwind.css` — about 48 KB
holding only the classes `index.html` actually uses. It used to come from the
Tailwind Play CDN, which downloads ~400 KB and then compiles the stylesheet in
the visitor's browser on every visit; that alone was most of an eleven-second
first paint on a throttled phone.

From a CDN, and none of it blocking the first paint: Font Awesome and Google
Fonts (both loaded with `media="print"` and swapped in on load, with a
`<noscript>` fallback), PapaParse for the CSVs, and ical.js for the calendar.
There is no animation library — the cards rise into view with about fifteen
lines of `IntersectionObserver`, which respects
`prefers-reduced-motion`.

The only run-time request to another website is the optional Google Calendar
iframe in the calendar's *Google Calendar* view. Everything else is this repository
and Drive.

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
- Confirm each district's meeting details with its D.C.M.C. The MSCA09
  calendar was checked against msca09aa.org in October 2026; every event
  says where its details came from under its `--` line.
- Intergroups and central offices: msca09aa.org gives their meeting time
  only. Add the place and Zoom when the intergroups confirm them.
- Old event flyers (2020–2025) are images straight from msca09aa.org. Their
  text was scrubbed of members' phone numbers, addresses and surnames; the
  pictures themselves could not be, so some still show a contact's number.
- Add `Title-ES:` lines to the bilingual events in the calendar.

---

*A.A.®, Alcoholics Anonymous®, the Big Book®, Box 4-5-9®, Grapevine® and
La Viña® are registered trademarks of A.A. World Services, Inc. and
A.A. Grapevine, Inc.*
