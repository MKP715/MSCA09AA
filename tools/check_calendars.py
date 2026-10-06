# -*- coding: utf-8 -*-
"""
Check the calendar mirror against the description format the site reads.

    python tools/check_calendars.py                    # data/calendar.ics
    python tools/check_calendars.py some-feed.ics      # any feed — the Action checks
                                                       # the fresh download this way

Every entry in the Area's Google Calendar — meeting or event — carries its
details in its description (see the README, "Writing a calendar event"):

    MSCA09|<Type>|<Format>
    Language: English
    ZoomID: 851 7562 5116
    IMG: https://drive.google.com/file/d/<id>/view
    --
    free text for people

For each entry this reports: a missing or unknown type, an unknown format,
no "--" line, no Language line, a flyer that is not in Google Drive, a link
back to the old website, a personal e-mail address or phone number, a
repeating entry with no end date, and a meeting still running that says
nothing about how to join. Exits 1 if anything was found, so it can sit in a
git hook; the Action only prints the report.
"""
import csv, datetime, html, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMATS = {'In person', 'Hybrid', 'Virtual'}
LANGS = {'English', 'Spanish', 'Bilingual'}
DRIVE = re.compile(r'^https://(drive\.google\.com/(file/d/|open\?id=)|lh3\.googleusercontent\.com/d/)')
OLD_SITE = re.compile(r'msca09aa\.org/(wp-content|event|wp-json)', re.I)
PERSONAL = re.compile(r'[\w.+-]+@(gmail|googlemail|yahoo|ymail|hotmail|aol|icloud|outlook|comcast|'
                      r'sbcglobal|live|msn|me|att|verizon|cox|charter|earthlink)\.[a-z.]{2,}', re.I)
# a service address on a free provider is still a service address
ROLE = re.compile(r'(?i)msca|area|district|dist\d|dcm|delegate|intergroup|handi|hni|ypaa|'
                  r'committee|chair|service|office|archives|registrar|treasurer|secretary')
PHONE = re.compile(r'(?<![\d-])(?:\+?1[\s.-]?)?\(?(\d{3})\)?[\s.-]?\d{3}[\s.-]?\d{4}(?![\d-])')
TOLL_FREE = {'800', '833', '844', '855', '866', '877', '888'}
NOT_A_PHONE = re.compile(r'(?i)(zoom|meeting|webinar)\s*(id|#)?\s*:?\s*$|\b(id|passcode|password|'
                         r'pc|pw|code)\s*:?\s*$|/j/$')


def kinds():
    """{type: [pages it is listed on]} from data/kinds.csv, set "calendar"."""
    p = os.path.join(ROOT, 'data', 'kinds.csv')
    if not os.path.exists(p):
        return None
    return {r['key']: re.split(r'[;,\s]+', r.get('pages') or '')
            for r in csv.DictReader(io.open(p, encoding='utf-8-sig')) if r['set'] == 'calendar'}


def still_running(rrule):
    """A repeating entry whose last date has not passed."""
    m = re.search(r'UNTIL=(\d{8})', rrule)
    return not m or m.group(1) >= datetime.date.today().strftime('%Y%m%d')


def unescape_ics(v):
    return (v.replace('\\n', '\n').replace('\\N', '\n').replace('\\,', ',')
             .replace('\\;', ';').replace('\\\\', '\\'))


def plain(desc):
    """Google keeps a description typed into its editor as HTML."""
    if re.search(r'<[a-z][^>]*>', desc, re.I):
        desc = re.sub(r'(?is)<a\b[^>]*?href="([^"]*)"[^>]*>(.*?)</a>',
                      lambda m: m.group(1) if re.sub(r'<[^>]+>', '', m.group(2)).strip() in ('', m.group(1))
                      else re.sub(r'<[^>]+>', '', m.group(2)) + ' ' + m.group(1), desc)
        desc = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h\d)>', '\n', desc)
        desc = re.sub(r'<[^>]+>', '', desc)
        desc = html.unescape(desc)
    return desc.replace('\xa0', ' ')


def events(path):
    raw = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    raw = re.sub(r'\n[ \t]', '', raw)
    name = (re.search(r'^X-WR-CALNAME:(.*)$', raw, re.M) or [None, ''])[1].strip()
    out, cur = [], None
    for line in raw.split('\n'):
        if line == 'BEGIN:VEVENT':
            cur = {}
        elif line == 'END:VEVENT':
            out.append(cur)
            cur = None
        elif cur is not None and ':' in line:
            k, v = line.split(':', 1)
            cur.setdefault(k.split(';')[0], unescape_ics(v))
    return name, out


def check_event(e, types):
    """[problem, ...] for one VEVENT. A meeting that still repeats must say how
    to join; an event long past may simply never have published its Zoom."""
    found = []
    if e.get('RECURRENCE-ID'):
        return found                       # one moved date of a series checked elsewhere
    desc = plain(e.get('DESCRIPTION', ''))
    lines = [l.strip() for l in desc.split('\n')]
    while lines and not lines[0]:
        lines.pop(0)
    tag = [x.strip() for x in (lines[0] if lines else '').split('|')]
    if not re.match(r'(?i)^MSCA\s*0?9$', tag[0] if tag else ''):
        found.append('first line is not "MSCA09|<Type>|<Format>"')
    else:
        typ = tag[1] if len(tag) > 1 else ''
        fmt = tag[2] if len(tag) > 2 else ''
        if types is not None and typ not in types:
            found.append('unknown type "%s" (one of: %s)' % (typ, ', '.join(sorted(types))))
        if fmt not in FORMATS:
            found.append('unknown format "%s" (In person, Hybrid or Virtual)' % fmt)
        # how does anyone join? a Zoom, an address to ask, or a website that says
        meeting = 'meetings' in (types or {}).get(typ, []) and still_running(e.get('RRULE', '')) and e.get('RRULE')
        if meeting and fmt in ('Virtual', 'Hybrid') and not re.search(r'(?im)^(zoom\s*id|zoomlink|email|web)\s*:', desc) \
                and 'zoom.us' not in e.get('LOCATION', ''):
            found.append('%s, but nothing says how to join (ZoomID, ZoomLink, Email or Web)' % fmt.lower())
    if not any(re.match(r'^[-–—_]{2,}$', l) for l in lines):
        found.append('no "--" line between the fields and the text')
    m = re.search(r'(?im)^language\s*:\s*(.+)$', desc)
    if not m:
        found.append('no "Language:" line')
    elif m.group(1).strip() not in LANGS:
        found.append('Language "%s" is not English, Spanish or Bilingual' % m.group(1).strip())
    for m in re.finditer(r'(?im)^(img|link)\s*:\s*.*?(https?://\S+)', desc):
        if not DRIVE.match(m.group(2)):
            found.append('%s is not a Google Drive address — %s' % (m.group(1).upper(), m.group(2)[:70]))
    for m in OLD_SITE.finditer(desc + ' ' + e.get('LOCATION', '')):
        found.append('links to the old website (it is being retired)')
        break
    for m in PERSONAL.finditer(desc):
        if not ROLE.search(m.group(0).split('@')[0]):
            found.append('personal e-mail address — ' + m.group(0))
    for m in PHONE.finditer(desc):
        before = desc[max(0, m.start() - 26):m.start()]
        if m.group(1) in TOLL_FREE or NOT_A_PHONE.search(before):
            continue
        found.append('looks like a phone number — ' + m.group(0).strip())
    rr = e.get('RRULE', '')
    if rr and 'UNTIL=' not in rr and 'COUNT=' not in rr:
        found.append('repeats forever — give it an end date')
    return found


def check_files(paths):
    """{calendar name: [(summary, problem), ...]}"""
    report = {}
    types = kinds()
    for path in paths:
        name, evs = events(path)
        rows = report.setdefault('%s (%s)' % (name or os.path.basename(path), os.path.basename(path)), [])
        for e in evs:
            for p in check_event(e, types):
                rows.append(((e.get('SUMMARY') or '(no title)').strip(), p))
    return report


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    paths = sys.argv[1:] or [os.path.join(ROOT, 'data', 'calendar.ics')]
    report = check_files([p for p in paths if os.path.exists(p)])
    total = 0
    for cal, rows in report.items():
        print('%s: %s' % (cal, '%d problem(s)' % len(rows) if rows else 'every entry follows the format'))
        for title, p in rows:
            print('  - %-40s %s' % (title[:40], p))
        total += len(rows)
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
