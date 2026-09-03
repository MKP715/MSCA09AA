# Documents & flyers

Every file the site links to lives here, so nothing depends on another website
staying online. `data/documents.csv` and `data/events.csv` point at these paths.

## Current record — what the Area publishes now

```
minutes/<year>/   approved ASA / ASC minutes, English and Spanish
motions/          motion backgrounds
conference/       General Service Conference material
calendars/        approved Area calendars
contributions/    7th Tradition material
reports/          Area committee reports
events/           event flyers, plus a .thumb.jpg preview of each
flyers/           district calendar flyer, contributions flyer, Zelle QR code
```

## archive/ — recovered from the Area's previous websites

Everything below was pulled off **msca09aa.org** (the WordPress site) and
**area09.org** (the older "blue site") and stored here, so the record survives
when those sites are switched off. It reaches back to the early 2000s.

```
archive/
  minutes/<year>/       Area Service Assembly and Committee minutes
  conference/<year>/    G.S.C. agenda items, advisory actions, background
  newsletters/<year>/   the Area newsletter / boletín
  finances/<year>/      quarterly contributions, budgets, treasurer reports
  reports/<year>/       committee, district and delegate reports
  guidelines/<year>/    guidelines, bylaws and policies
  workbooks/<year>/     Area workbooks
  calendars/<year>/     older Area calendars
  forms/                registration and group-change forms
  delegate/<year>/      delegate reports from the Conference
  praasa/<year>/        PRAASA materials
  archives/             Archives committee material
  flyers/<year>/        historical event flyers
  districts/d<n>/       documents that lived on a district's own pages
  misc/<year>/          everything that did not fit a box above
```

Files are named `<slug>-en.pdf` / `<slug>-es.pdf` so the language is obvious
from the path.

## Adding a file

1. Drop it in the right folder.
2. Add a row to `data/documents.csv` pointing at it. Set `collection` to
   `Current` for something the Area is publishing now, or `Archive` for
   historical material.

**Check every document before adding it.** These are public the moment they
are committed. Anything carrying a member's last name, personal e-mail or
personal phone number needs the Area's decision before it goes up — see the
anonymity section of the repository README.
