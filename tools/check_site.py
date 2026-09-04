# -*- coding: utf-8 -*-
"""
Run this before pushing. It checks the things that quietly break a static site:

  * every file the data points at exists AND is tracked by git
    (a file git ignores will 404 on GitHub Pages even though it works locally)
  * nothing links back to the old websites
  * no personal e-mail address or phone number in any data file
  * no last names in the published roster
  * every content / ui key the page asks for has a row

    python tools/check_site.py
"""
import csv, io, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

problems = []


def read(name):
    p = os.path.join('data', name)
    if not os.path.exists(p):
        problems.append('missing data file: ' + p)
        return []
    return list(csv.DictReader(io.open(p, encoding='utf-8-sig')))


tracked = set(subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
              .stdout.splitlines())

# ── every address is either in Drive or committed here ────────────────────
DRIVE = re.compile(r'^https://(drive\.google\.com/file/d/|lh3\.googleusercontent\.com/d/)')

def check_target(url, where):
    if not url:
        problems.append(where + ': empty address')
    elif url.startswith('http'):
        if not DRIVE.match(url):
            problems.append(where + ': not a Google Drive address — ' + url[:70])
    elif not os.path.exists(url.replace('/', os.sep)):
        problems.append(where + ': file missing on disk — ' + url)
    elif url not in tracked:
        problems.append(where + ': file is not committed, so it will 404 once '
                                'published — ' + url)

docs = read('documents.csv')
for r in docs:
    if str(r.get('publish', 'yes')).strip().lower() != 'yes':
        continue
    check_target(r['url'], 'documents.csv "%s"' % r['title'][:40])

for e in read('events.csv'):
    flyers = [x.strip() for x in str(e.get('flyers') or '').split(';') if x.strip()]
    thumbs = [x.strip() for x in str(e.get('thumbs') or '').split(';') if x.strip()]
    for u in flyers + thumbs:
        check_target(u, 'events.csv "%s"' % e['slug'][:36])
    if flyers and len(thumbs) != len(flyers):
        problems.append('events.csv "%s": %d flyers but %d thumbnails'
                        % (e['slug'][:36], len(flyers), len(thumbs)))

for r in read('files.csv'):
    check_target(r['url'], 'files.csv "%s"' % r['key'])

# the page must not name a file directly; it asks files.csv for one
html_early = io.open('index.html', encoding='utf-8').read()
for m in re.finditer(r"""["'](docs/[^"']+)["']""", html_early):
    problems.append('index.html names a file directly — use files.csv: ' + m.group(1))

# ── nothing may point back at the sites this one replaces ─────────────────
OLD = re.compile(r'(msca09aa\.org/(?!$)|(?<!district6)(?<!district30)\barea09\.org)', re.I)
for name in os.listdir('data'):
    if not name.endswith('.csv') or name == 'archive-review.csv':
        continue
    for i, r in enumerate(read(name), 2):
        for k, v in r.items():
            v = str(v or '')
            if k == 'url' and OLD.search(v):
                problems.append('%s row %d: %s points at the old site — %s' % (name, i, k, v[:70]))

html = io.open('index.html', encoding='utf-8').read()
for m in re.finditer(r'https?://[^\s"\']*msca09aa\.org/wp-content[^\s"\']*', html):
    problems.append('index.html links to the old site: ' + m.group(0)[:70])

# ── anonymity ─────────────────────────────────────────────────────────────
PERSONAL = re.compile(r'[\w.+-]+@(gmail|yahoo|hotmail|aol|icloud|outlook|comcast|'
                      r'sbcglobal|live|msn|me)\.[a-z]{2,}', re.I)
ROLEISH = re.compile(r'^(msca09|mscaa09|area0?9|district\d*|d\d{2}|delegate|chair|secretary|'
                     r'registrar|treasurer|webmaster|contributions|editor|p76delegate)', re.I)
PHONE = re.compile(r'(?<![\d-])\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?![\d-])')

roster = read('trusted-servants.csv')
for r in roster:
    for field in ('email', 'email_alt'):
        v = r.get(field) or ''
        for m in PERSONAL.finditer(v):
            if not ROLEISH.match(m.group(0)):
                problems.append('trusted-servants.csv: personal address for %s — %s'
                                % (r['position'], m.group(0)))
    nm = r.get('name') or ''
    if nm and not re.match(r"^[A-Za-zÀ-ɏ'\-]+( [A-Za-zÀ-ɏ'\-]+)?( [A-Z]\.)?$", nm):
        problems.append('trusted-servants.csv: name is not "First L." — ' + nm)

# A Zoom meeting ID is ten digits and reads like a phone number, so skip the
# fields that hold one and any number introduced as an ID or passcode.
ZOOMY = re.compile(r'(?i)(zoom|meeting)\s*(id|#)?\s*:?\s*$|passcode|^zoom_')
ZOOM_FIELDS = {'zoom_id', 'zoom_passcode', 'zoom_url'}
for name in ('trusted-servants.csv', 'districts.csv', 'committees.csv', 'events.csv'):
    for i, r in enumerate(read(name), 2):
        for k, v in r.items():
            if k in ZOOM_FIELDS:
                continue
            v = str(v or '')
            for m in PHONE.finditer(v):
                before = v[max(0, m.start() - 24):m.start()]
                if re.search(r'(?i)zoom|meeting id|\bid\b|passcode|password', before):
                    continue
                problems.append('%s row %d: %s looks like a phone number — %s'
                                % (name, i, k, m.group(0)))

# ── every key the page asks for has a row ─────────────────────────────────
ui = {r['key'] for r in read('ui.csv')}
content = {r['key'] for r in read('content.csv')}
for m in re.finditer(r"\bt\('([a-zA-Z0-9_.]+)'\)", html):
    if m.group(1) not in ui:
        problems.append("ui.csv has no row for t('%s')" % m.group(1))
for m in re.finditer(r"\b(?:c|cTitle)\('([a-zA-Z0-9_.]+)'", html):
    if m.group(1) not in content:
        problems.append("content.csv has no row for c('%s')" % m.group(1))
for m in re.finditer(r'data-c="([^"]+)"', html):
    if m.group(1) not in content and m.group(1) != 'skip':
        problems.append('content.csv has no row for data-c="%s"' % m.group(1))

files = {r['key'] for r in read('files.csv')}
for m in re.finditer(r"M\.file\('([a-zA-Z0-9_]+)'\)", html):
    if m.group(1) not in files:
        problems.append("files.csv has no row for M.file('%s')" % m.group(1))

# ── the menu must point somewhere real ────────────────────────────────────
routes = set(re.findall(r"'([a-z0-9-]+)':'[a-z]+'", html))
for r in read('nav.csv'):
    href = (r.get('href') or '').strip()
    if href and href.startswith('#/'):
        head = href[2:].split('/')[0]
        if head and head not in routes:
            problems.append('nav.csv points at an unknown route: ' + href)

drive = sum(1 for r in docs if r['url'].startswith('http'))
print('documents %d (%d in Drive, %d here) | roster %d | tracked files %d'
      % (len(docs), drive, len(docs) - drive, len(roster), len(tracked)))
if problems:
    print('\n%d problem(s):' % len(problems))
    for p in problems:
        print('  -', p)
    sys.exit(1)
print('\nno problems found')
