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
| `trusted-servants.csv` | Panel 76 officers, committee chairs, district officers |
| `committees.csv` | the Area committees |
| `documents.csv` | minutes, motions, agendas — each pointing at a file in `docs/` |
| `events.csv` | events and their flyers; `slug` becomes the shareable link |
| `area-meetings.csv` | the approved ASC / Assembly schedule |
| `resources.csv` | the aa.org links and central-office lists |
| `calendar.ics` | a mirror of the Area's Google Calendar, refreshed automatically |

Change meetings in Google Calendar, not in `calendar.ics`.

**Anonymity: first name + last initial only, role-based service e-mail
addresses only. No personal e-mail, no phone numbers, no home addresses, no
sobriety dates, no home groups — in a row or on a flyer.** Everything here is
public and permanent. See the anonymity section of the repository README.
