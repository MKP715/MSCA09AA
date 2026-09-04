# -*- coding: utf-8 -*-
"""Downsample the big scanned PDFs so the repository stays a sane size."""
import os, glob, subprocess, shutil, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = REPO
GS   = r"C:/Program Files/gs/gs10.05.1/bin/gswin64c.exe"
THRESHOLD = 700 * 1024          # only bother above this
KEEP_RATIO = 0.85               # keep the compressed copy only if it saves >15%

pdfs = [f for f in glob.glob(os.path.join(ROOT, 'docs', '**', '*.pdf'), recursive=True)
        if os.path.getsize(f) > THRESHOLD]
pdfs.sort(key=os.path.getsize, reverse=True)
before = sum(os.path.getsize(f) for f in pdfs)
print('candidates: %d files, %.0f MB' % (len(pdfs), before / 1048576))

saved = kept = failed = 0
for i, f in enumerate(pdfs, 1):
    tmp = f + '.gs.pdf'
    try:
        r = subprocess.run([GS, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.5',
                            '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                            '-dDetectDuplicateImages=true', '-dAutoRotatePages=/None',
                            '-sOutputFile=' + tmp, f],
                           timeout=180, capture_output=True)
        if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) < 900:
            failed += 1
            if os.path.exists(tmp): os.remove(tmp)
            continue
        old, new = os.path.getsize(f), os.path.getsize(tmp)
        if new < old * KEEP_RATIO:
            shutil.move(tmp, f)
            saved += old - new
            kept += 1
        else:
            os.remove(tmp)
    except Exception as e:
        failed += 1
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass
    if i % 50 == 0:
        print('  %d/%d  saved %.0f MB so far' % (i, len(pdfs), saved / 1048576), flush=True)

after = sum(os.path.getsize(f) for f in pdfs if os.path.exists(f))
print('recompressed %d files, skipped/failed %d' % (kept, failed))
print('%.0f MB -> %.0f MB (saved %.0f MB)' % (before / 1048576, after / 1048576, saved / 1048576))
total = sum(os.path.getsize(f) for f in glob.glob(os.path.join(ROOT, 'docs', '**', '*'), recursive=True)
            if os.path.isfile(f))
print('docs/ now %.0f MB' % (total / 1048576))
