# -*- coding: utf-8 -*-
"""Every person named in the workbook must appear in trusted-servants.csv."""
import csv, io, os, re, unicodedata, collections
import openpyxl

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = REPO
XL = os.path.join(ROOT, "Panel 76 Area 09 Teammates.xlsx")

SKIP_TABS = {"P76 - Get to know you! ", "zoom schedule"}

NOT_A_NAME = re.compile(
    r"@|http|^\d|^(open|n/a|tbd|none|position|name|email|e-mail|phone|role|"
    r"service position|board member name|dcmc name|committee chair name|contact|venmo|zelle|"
    r"mailing address|meeting time|meeting date|meeting location|monthly meeting info|"
    r"personal email|phone number|sobriety date|area email|date added|home group|"
    r"additional info|website|member|in-person|zoom|password|id#|passcode|"
    r"officers of the executive committee|msca district 12|link to duplicate)", re.I)

# position labels, home groups and venues that look like names
LABEL = re.compile(
    r"^(alt|alternate|secretar|tesorer|treas|registr|resgistr|chair|dcmc|mcd|committee|"
    r"grapevine|literat|archiv|coffee|technology|corrections|treatment|convention|finance|"
    r"remote|guidelines|newsletter|sound|ypaa|gsr|rsg|dcm|intergroup|co-op|cec|cpc|ccp|"
    r"boletin|foro|comite|com\.|public information|inter district|hispanic|accessib|"
    r"communicat|audio|district|distrito|register|area coffee|la vina|delegate|"
    r"wed|thurs|mon|tue|fri|sat|sun|great events|saturday|monday|newcomers|pacific group|"
    r"grace lutheran|it.s a better|in.person)", re.I)


def norm(x):
    x = unicodedata.normalize('NFKD', str(x or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z]', '', x.lower())


def first_token(x):
    x = re.sub(r'\(.*?\)', ' ', str(x or ''))
    x = re.sub(r"[^A-Za-z\u00c0-\u024f' ]", ' ', x).strip()
    return norm(x.split()[0]) if x.split() else ''


wb = openpyxl.load_workbook(XL, data_only=True)
found = collections.defaultdict(set)
for ws in wb.worksheets:
    if ws.title in SKIP_TABS:
        continue
    for r in ws.iter_rows(values_only=True):
        for cell in r:
            if cell is None:
                continue
            for part in str(cell).split("\n"):        # "Alt DCMC\nAlicia B"
                part = part.strip()
                if not part or len(part) > 44 or NOT_A_NAME.search(part):
                    continue
                clean = re.sub(r'\(.*?\)', ' ', part).strip(' .,-')
                clean = re.sub(r'\s{2,}', ' ', clean)
                if not re.match(r"^[A-Za-z\u00c0-\u024f][A-Za-z\u00c0-\u024f.'\- ]+$", clean):
                    continue
                if not (1 <= len(clean.split()) <= 5):
                    continue
                if LABEL.search(clean):
                    continue
                found[ws.title].add((first_token(clean), clean))

rows = list(csv.DictReader(io.open(os.path.join(ROOT, 'data', 'trusted-servants.csv'),
                                   encoding='utf-8-sig')))
published = {first_token(r['name']) for r in rows if r['name']}

print('published rows        :', len(rows))
print('distinct first names  :', len(published))
print()
missing_total = 0
for tab in sorted(found):
    miss = sorted({full for first, full in found[tab] if first and first not in published})
    print('%-22s %3d name(s)  %s' % (repr(tab), len(found[tab]),
                                     'all captured' if not miss else 'MISSING: ' + ', '.join(miss[:8])))
    missing_total += len(miss)
print()
print('names in the workbook not on the site :', missing_total)

all_first = {f for s in found.values() for f, _ in s}
extra = sorted({r['name'] for r in rows if r['name'] and first_token(r['name']) not in all_first})
print('published but not in the workbook     :', len(extra), extra[:10])

bad = [r['name'] for r in rows
       if r['name'] and not re.match(
           r"^[A-Za-z\u00c0-\u024f'\-]+( [A-Za-z\u00c0-\u024f'\-]+)?( [A-Z]\.)?$", r['name'])]
print('names not in "First L." form          :', len(bad), bad[:10])

PERSONAL = re.compile(r'@(yahoo|hotmail|aol|icloud|outlook|comcast|sbcglobal|live|msn|me)\.', re.I)
leaks = [(r['name'], r['email'], r['email_alt']) for r in rows
         if PERSONAL.search(r['email'] or '') or PERSONAL.search(r['email_alt'] or '')]
print('personal mail hosts published         :', len(leaks), leaks[:5])

PHONE = re.compile(r'\d{3}[-. ]\d{3}[-. ]\d{4}')
blob = io.open(os.path.join(ROOT, 'data', 'trusted-servants.csv'), encoding='utf-8-sig').read()
print('phone numbers published               :', len(set(PHONE.findall(blob))))
