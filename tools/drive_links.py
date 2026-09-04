# -*- coding: utf-8 -*-
"""
Point the site at the Area's Google Drive.

Everything the site links to lives in the shared Drive folder. This script
reads the file ids out of Google Drive for Desktop's local metadata and
rewrites data/documents.csv and data/events.csv to address each file by id:

    documents  ->  https://drive.google.com/file/d/<id>/view
    images     ->  https://lh3.googleusercontent.com/d/<id>

The one exception is docs/archive/pages/*.html. Drive hands an .html file to
the browser as a download rather than rendering it, so those stay in the
repository and keep their relative path.

Re-run this after adding files to the Drive folder:

    python tools/drive_links.py            # rewrite the CSVs
    python tools/drive_links.py --dry-run  # just report

Google Drive for Desktop must be signed in and finished syncing; the ids come
from its local database, so nothing is downloaded and no API key is needed.
"""
import csv, io, os, json, shutil, sqlite3, sys, tempfile, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVEFS = os.path.expandvars(r"%LOCALAPPDATA%\Google\DriveFS")
SHARED_FOLDER_ID = "1ZabOXfYv2wIcFiV1gPgGSvXd1b4Z917F"      # .../RowlettAATech/MSCA09AA
IMAGE = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
KEEP_LOCAL = ('.html',)          # Drive cannot serve these as pages

DRY = '--dry-run' in sys.argv


def drive_ids():
    """{'docs/…/file.pdf': '<drive id>'} for everything in the shared folder."""
    db = None
    for account in sorted(os.listdir(DRIVEFS)):
        cand = os.path.join(DRIVEFS, account, 'metadata_sqlite_db')
        if os.path.exists(cand):
            db = cand
            break
    if not db:
        raise SystemExit('Google Drive for Desktop metadata not found under ' + DRIVEFS)

    tmp = os.path.join(tempfile.gettempdir(), 'msca09_drivefs.db')
    for suffix in ('', '-wal', '-shm'):
        if os.path.exists(db + suffix):
            shutil.copy2(db + suffix, tmp + suffix)

    con = sqlite3.connect(tmp)
    cur = con.cursor()
    items = {}
    for sid, cid, title, is_folder, trashed in cur.execute(
            "SELECT stable_id, id, local_title, is_folder, trashed FROM items"):
        items[sid] = (cid, title, bool(is_folder), bool(trashed))
    kids = collections.defaultdict(list)
    for sid, parent, _ in cur.execute(
            "SELECT item_stable_id, parent_stable_id, local_title_hash FROM stable_parents"):
        kids[parent].append(sid)
    con.close()

    root = next((s for s, v in items.items() if v[0] == SHARED_FOLDER_ID), None)
    if root is None:
        raise SystemExit('the shared folder is not in the local Drive metadata — '
                         'is Drive for Desktop signed in and synced?')

    out, stack = {}, [(root, '')]
    while stack:
        sid, prefix = stack.pop()
        for kid in kids.get(sid, []):
            cid, title, is_folder, trashed = items.get(kid, (None, None, False, True))
            if trashed or not title:
                continue
            path = (prefix + '/' + title) if prefix else title
            if is_folder:
                stack.append((kid, path))
            else:
                out[path] = cid
    return out


def url_for(path, ids):
    """The address the site should use for a file that used to be at `path`."""
    if path.lower().endswith(KEEP_LOCAL):
        return path                                   # served from the repository
    fid = ids.get(path)
    if not fid:
        return None
    if path.lower().endswith(IMAGE):
        return 'https://lh3.googleusercontent.com/d/' + fid
    return 'https://drive.google.com/file/d/' + fid + '/view'


def load(name):
    p = os.path.join(REPO, 'data', name)
    rows = list(csv.DictReader(io.open(p, encoding='utf-8-sig')))
    return p, rows, (list(rows[0].keys()) if rows else [])


def save(p, rows, hdr):
    if DRY:
        return
    with io.open(p, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=hdr)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in hdr})


def main():
    ids = drive_ids()
    print('files in the shared Drive folder:', len(ids))
    missing = []

    # ── documents ─────────────────────────────────────────────────────────
    p, rows, hdr = load('documents.csv')
    if 'drive_path' not in hdr:
        hdr.insert(hdr.index('url'), 'drive_path')
    changed = 0
    for r in rows:
        key = r.get('drive_path') or r['url']
        if key.startswith('http'):
            continue                                  # already an address
        r['drive_path'] = key
        u = url_for(key, ids)
        if not u:
            missing.append(key)
            continue
        if r['url'] != u:
            r['url'] = u
            changed += 1
    save(p, rows, hdr)
    print('documents.csv: %d of %d rows repointed' % (changed, len(rows)))

    # ── events: flyers, and a matching column of thumbnails ───────────────
    p, rows, hdr = load('events.csv')
    for extra in ('flyers', 'thumbs'):
        if extra not in hdr:
            hdr.append(extra)
    if 'flyer_paths' not in hdr:
        hdr.insert(hdr.index('flyers'), 'flyer_paths')
    n = 0
    for r in rows:
        paths = [x.strip() for x in (r.get('flyer_paths') or r.get('flyers') or '').split(';') if x.strip()]
        paths = [x for x in paths if not x.startswith('http')] or \
                [x.strip() for x in (r.get('flyer_paths') or '').split(';') if x.strip()]
        if not paths:
            continue
        r['flyer_paths'] = '; '.join(paths)
        full, thumb = [], []
        for path in paths:
            u = url_for(path, ids)
            t = url_for(path.replace('.jpg', '.thumb.jpg'), ids)
            if not u:
                missing.append(path)
                continue
            full.append(u)
            thumb.append(t or u)
        r['flyers'] = '; '.join(full)
        r['thumbs'] = '; '.join(thumb)
        n += 1
    save(p, rows, hdr)
    print('events.csv: %d rows with flyers repointed' % n)

    if missing:
        print('\nNOT FOUND in the Drive folder (%d):' % len(missing))
        for m in missing[:20]:
            print('   -', m)
        print('\nUpload these, let Drive finish syncing, then run this again.')
    else:
        print('\nevery file was found in the Drive folder')

    json.dump(ids, io.open(os.path.join(REPO, 'tools', 'drive-file-ids.json'), 'w'), indent=0)
    print('file ids written to tools/drive-file-ids.json')


if __name__ == '__main__':
    main()
