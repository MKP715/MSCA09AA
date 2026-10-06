# -*- coding: utf-8 -*-
"""Read every archived PDF and report which ones carry personal contact details.

These are historical Area records. They were already public on both old sites,
but the point of the new site is that anonymity is handled deliberately — so
the Area needs a list of what it is about to re-publish.
"""
import os, re, io, json, glob, collections
import concurrent.futures
import fitz            # PyMuPDF

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = REPO
SCR  = os.path.dirname(os.path.abspath(__file__))   # tools/

MAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
ROLE = re.compile(r'@(msca09aa|area09|aa|aagrapevine|mscadistrict\d+|district\d+|'
                  r'.*\.org|.*\.gov)$', re.I)
PERSONAL_HOST = re.compile(r'@(gmail|yahoo|hotmail|aol|icloud|outlook|me|comcast|sbcglobal|'
                           r'live|msn|verizon|att|cox|charter|earthlink|mac|roadrunner|pacbell)\.', re.I)
PHONE = re.compile(r'(?<![\d/-])(?:\(\d{3}\)\s?|\d{3}[-. ])\d{3}[-. ]\d{4}(?![\d-])')

def scan(path):
    try:
        doc = fitz.open(path)
    except Exception:
        return path, {'error': 'unreadable'}
    text = []
    try:
        for i, pg in enumerate(doc):
            if i > 60:
                break
            text.append(pg.get_text())
    except Exception:
        pass
    doc.close()
    t = '\n'.join(text)
    mails = set(MAIL.findall(t))
    personal = sorted({m for m in mails if PERSONAL_HOST.search(m)})
    phones = sorted(set(PHONE.findall(t)))
    return path, {'chars': len(t), 'personal_mail': personal[:12], 'phones': phones[:12],
                  'n_personal': len(personal), 'n_phones': len(phones)}

pdfs = sorted(glob.glob(os.path.join(ROOT, 'docs', '**', '*.pdf'), recursive=True))
print('scanning', len(pdfs), 'PDFs')

out = {}
done = 0
with concurrent.futures.ThreadPoolExecutor(6) as ex:
    for path, res in ex.map(scan, pdfs):
        out[os.path.relpath(path, ROOT).replace('\\', '/')] = res
        done += 1
        if done % 250 == 0:
            print('  ', done, flush=True)

flagged = {k: v for k, v in out.items() if v.get('n_personal') or v.get('n_phones')}
notext  = [k for k, v in out.items() if v.get('chars', 0) < 40 and 'error' not in v]
print()
print('PDFs scanned          :', len(out))
print('image-only (no text)  :', len(notext))
print('with personal e-mail  :', sum(1 for v in out.values() if v.get('n_personal')))
print('with phone numbers    :', sum(1 for v in out.values() if v.get('n_phones')))
print('flagged in total      :', len(flagged))

by_dir = collections.Counter(k.split('/')[2] if k.startswith('docs/archive/') else k.split('/')[1]
                             for k in flagged)
print('flagged by folder     :', by_dir.most_common())

json.dump(out, open(os.path.join(SCR, 'pii.json'), 'w'), indent=0)
print()
for k, v in list(flagged.items())[:10]:
    print(' ', k)
    if v['personal_mail']: print('     mail :', ', '.join(v['personal_mail'][:4]))
    if v['phones']:        print('     phone:', ', '.join(v['phones'][:4]))
