# Data files

These CSVs are the site. Every heading, sentence, label, menu item, colour and
card on the page is loaded from this folder — edit a row on github.com and the
site updates itself. Nothing is hard-coded in `index.html`.

| File | What it drives |
|---|---|
| `content.csv` | every heading, sentence and paragraph (`key`, `en`, `es`) |
| `ui.csv` | every interface label — buttons, filters, headings, toasts |
| `nav.csv` | the menu; empty `parent` = top-level item, otherwise a dropdown entry |
| `kinds.csv` | colour, icon and bilingual label for every category |
| `blocks.csv` | the repeating card lists, grouped by `page` + `section` |
| `districts.csv` | the district directory and district modals |
| `trusted-servants.csv` | every trusted servant, from all tabs of the panel workbook. `panel` is 76 or 74; `email_alt` is a second service address where the workbook lists one. Rebuild with `tools/build_roster.py`. |
| `committees.csv` | the Area committees |
| `files.csv` | the few files the page itself links to, by key |
| `documents.csv` | minutes, motions, agendas, and the whole archive — each pointing at a file in `docs/`. `collection` is `Current` or `Archive`. Set `publish` to anything but `yes` to withhold a file from the site. |
| `archive-review.csv` | the archived documents that carry a personal e-mail address or phone number, for the Area to triage. The site does not read this file. |
| `events.csv` | events and their flyers; `slug` becomes the shareable link |
| `area-meetings.csv` | the approved ASC / Assembly schedule |
| `resources.csv` | the aa.org links and central-office lists |
| `calendar.ics` | a mirror of the Area's Google Calendar, refreshed automatically |

Change meetings in Google Calendar, not in `calendar.ics`.

`documents.csv`, `events.csv` and `files.csv` address files in the Area's
Google Drive by file id. `drive_path` and `flyer_paths` keep the original
folder path so `tools/drive_links.py` can find each file again after you add
or replace one in Drive.

**Anonymity: first name + last initial only, role-based service e-mail
addresses only. No personal e-mail, no phone numbers, no home addresses, no
sobriety dates, no home groups — in a row or on a flyer.** Everything here is
public and permanent. See the anonymity section of the repository README.
