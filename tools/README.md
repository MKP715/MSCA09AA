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
