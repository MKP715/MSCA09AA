# -*- coding: utf-8 -*-
"""
Fetch every address the site uses and report anything that does not come back.

    python tools/check_links.py            # every Drive file (slow, ~2000 requests)
    python tools/check_links.py --sample   # 120 of them, spread across the set

Google Drive answers a request for a file nobody may see with a sign-in page,
so a 200 is not enough on its own — this checks the content type as well, and
treats an HTML answer for a PDF or an image as a failure.
"""
import csv, io, os, re, ssl, sys, random, urllib.request, urllib.error
import concurrent.futures

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
SAMPLE = '--sample' in sys.argv
CTX = ssl.create_default_context()
UA = {'User-Agent': 'Mozilla/5.0 (compatible; MSCA09-linkcheck/1.0)'}

IMAGE_URL = re.compile(r'^https://lh3\.googleusercontent\.com/d/')
DOC_URL = re.compile(r'^https://drive\.google\.com/file/d/')


def collect():
    """(url, what it is, where it came from)"""
    out = []
    for r in csv.DictReader(io.open('data/documents.csv', encoding='utf-8-sig')):
        if str(r.get('publish', 'yes')).strip().lower() != 'yes':
            continue
        out.append((r['url'], 'document', 'documents.csv: ' + r['title'][:44]))
    for r in csv.DictReader(io.open('data/events.csv', encoding='utf-8-sig')):
        for field in ('flyers', 'thumbs'):
            for u in [x.strip() for x in str(r.get(field) or '').split(';') if x.strip()]:
                out.append((u, 'image', 'events.csv %s: %s' % (field, r['slug'][:36])))
    for r in csv.DictReader(io.open('data/files.csv', encoding='utf-8-sig')):
        out.append((r['url'], 'image' if IMAGE_URL.match(r['url']) else 'document',
                    'files.csv: ' + r['key']))
    return out


def check(job):
    url, kind, where = job
    if not url.startswith('http'):                      # served from the repository
        path = url.replace('/', os.sep)
        return (job, 'ok' if os.path.exists(path) else 'MISSING FILE', '')
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            status, ctype = r.status, (r.headers.get('Content-Type') or '')
            body = r.read(2048)
    except urllib.error.HTTPError as e:
        return (job, 'HTTP %s' % e.code, '')
    except Exception as e:
        return (job, type(e).__name__, '')

    if status != 200:
        return (job, 'HTTP %s' % status, ctype)
    if kind == 'image' and not ctype.startswith('image/'):
        return (job, 'not an image', ctype)
    if kind == 'document':
        # the Drive viewer page is HTML, but a sign-in wall is HTML too
        if b'Sign in' in body and b'accounts.google.com' in body:
            return (job, 'needs sign-in — not shared', ctype)
        if b'ServiceLogin' in body:
            return (job, 'needs sign-in — not shared', ctype)
    return (job, 'ok', ctype)


jobs = collect()
uniq = list(dict.fromkeys(jobs))
print('addresses to check: %d (%d unique)' % (len(jobs), len(uniq)))
if SAMPLE:
    random.seed(9)
    docs = [j for j in uniq if j[1] == 'document']
    imgs = [j for j in uniq if j[1] == 'image']
    uniq = random.sample(docs, min(80, len(docs))) + random.sample(imgs, min(40, len(imgs)))
    print('checking a sample of %d' % len(uniq))

bad, done = [], 0
with concurrent.futures.ThreadPoolExecutor(12) as ex:
    for job, verdict, ctype in ex.map(check, uniq):
        done += 1
        if verdict != 'ok':
            bad.append((verdict, job[2], job[0], ctype))
        if done % 250 == 0:
            print('  %d/%d' % (done, len(uniq)), flush=True)

print('\nchecked %d | working %d | failing %d' % (len(uniq), len(uniq) - len(bad), len(bad)))
if bad:
    for verdict, where, url, ctype in bad[:25]:
        print('  - %-24s %s\n      %s %s' % (verdict, where, url, ctype))
    sys.exit(1)
print('every address answered correctly')
