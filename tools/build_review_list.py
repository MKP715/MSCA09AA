# -*- coding: utf-8 -*-
"""Turn the PDF scan into a review list the Area can act on, and add the
`publish` switch to data/documents.csv."""
import io, os, re, csv, json, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = REPO
SCR  = os.path.dirname(os.path.abspath(__file__))   # tools/
DOCS = os.path.join(ROOT, 'data', 'documents.csv')

pii = json.load(open(os.path.join(SCR, 'pii.json'), encoding='utf-8'))

# an address at a personal mail host that is not obviously a service account
ROLEISH = re.compile(r'^(msca09|area09|district|d\d{2}|delegate|chair|secretary|registrar|'
                     r'treasurer|webmaster|contributions|editor|archives|literature|'
                     r'corrections|treatment|grapevine|lavina|cec|cpc|pi|ypaa|gsr|dcm)', re.I)
# published A.A. service numbers, not a member's line
INSTITUTIONAL = re.compile(r'^(?:\(?(?:212|800|888|877|866|818|916|613|604|914)\)?)')

def triage(v):
    personal = [m for m in v.get('personal_mail', []) if not ROLEISH.match(m.split('@')[0])]
    phones = [p for p in v.get('phones', []) if not INSTITUTIONAL.match(p.replace(' ', ''))]
    return personal, phones

rows = list(csv.DictReader(io.open(DOCS, encoding='utf-8-sig')))
by_url = {r['url']: r for r in rows}

review = []
for path, v in pii.items():
    if 'error' in v:
        continue
    personal, phones = triage(v)
    if not personal and not phones:
        continue
    r = by_url.get(path)
    review.append(dict(
        url=path,
        collection=(r or {}).get('collection', ''),
        category=(r or {}).get('category', ''),
        year=(r or {}).get('year', ''),
        title=(r or {}).get('title', os.path.basename(path)),
        personal_emails=str(len(personal)),
        phone_numbers=str(len(phones)),
        examples='; '.join((personal[:2] + phones[:2]))[:160],
        decision='', notes=''))

review.sort(key=lambda r: (-int(r['personal_emails']), -int(r['phone_numbers']), r['url']))
RH = ['url','collection','category','year','title','personal_emails','phone_numbers',
      'examples','decision','notes']
with io.open(os.path.join(ROOT, 'data', 'archive-review.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=RH); w.writeheader()
    for r in review: w.writerow(r)

print('documents needing a look:', len(review))
print('  with a personal e-mail :', sum(1 for r in review if int(r['personal_emails'])))
print('  with a phone number    :', sum(1 for r in review if int(r['phone_numbers'])))
print('  by category            :', collections.Counter(r['category'] for r in review).most_common(8))
print()
for r in review[:8]:
    print('  ', r['year'] or '----', r['category'][:11].ljust(12), r['title'][:44].ljust(46), r['examples'][:52])

# every row gains a publish switch; the web servant flips it to withhold a file
HDR = ['collection','category','title','meeting_type','date','year','language',
       'format','size_kb','source','publish','url']
for r in rows:
    r['publish'] = r.get('publish') or 'yes'
with io.open(DOCS, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=HDR); w.writeheader()
    for r in rows: w.writerow({k: r.get(k, '') for k in HDR})
print()
print('documents.csv rows:', len(rows), '- all set to publish=yes')
