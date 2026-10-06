# -*- coding: utf-8 -*-
"""
Point the site at the Area's Google Drive.

Everything the site links to lives in the shared Drive folder. This script
reads the file ids out of Google Drive for Desktop's local metadata and
rewrites data/documents.csv and data/committee-guidelines.csv to address
each file by id:

    documents  ->  https://drive.google.com/file/d/<id>/view
    images     ->  https://lh3.googleusercontent.com/d/<id>

The one exception is docs/archive/pages/*.html. Drive hands an .html file to
the browser as a download rather than rendering it, so those stay in the
repository and keep their relative path.

Event and meeting flyers are not in a CSV: they are linked from the Google
Calendar event itself. --links prints the line to paste for each file:

    python tools/drive_links.py                         # rewrite the CSVs
    python tools/drive_links.py --dry-run               # just report
    python tools/drive_links.py --links docs/events/2026  # IMG:/Link: lines to paste

Google Drive for Desktop must be signed in and finished syncing; the ids come
from its local database, so nothing is downloaded and no API key is needed.
"""
import csv, io, os, json, shutil, sqlite3, sys, tempfile, time, collections

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

    # Drive for Desktop keeps this database open, and locks part of it while it
    # is uploading. That is exactly when this script tends to be run -- right
    # after dropping new files in -- so wait for the sync to settle rather than
    # failing with a Windows sharing error.
    tmp = os.path.join(tempfile.gettempdir(), 'msca09_drivefs.db')
    for attempt in range(8):
        try:
            for suffix in ('', '-wal', '-shm'):
                if os.path.exists(db + suffix):
                    shutil.copy2(db + suffix, tmp + suffix)
            break
        except (IOError, OSError) as e:
            if attempt == 7:
                raise SystemExit(
                    'Google Drive for Desktop still has its database locked:\n  %s\n'
                    'It is probably still uploading. Wait for the Drive icon to stop\n'
                    'showing activity, then run this again.' % e)
            wait = 10 * (attempt + 1)
            print('  Drive is busy syncing; waiting %ds ...' % wait, flush=True)
            time.sleep(wait)

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

    # ── committee guidelines: same idea, matched on drive_path ────────────
    p, rows, hdr = load('committee-guidelines.csv')
    changed = 0
    for r in rows:
        key = r.get('drive_path', '')
        if not key:
            continue
        u = url_for(key, ids)
        if not u:
            missing.append(key)
            continue
        if r['url'] != u:
            r['url'] = u
            changed += 1
    save(p, rows, hdr)
    print('committee-guidelines.csv: %d of %d rows repointed' % (changed, len(rows)))

    if missing:
        print('\nNOT FOUND in the Drive folder (%d):' % len(missing))
        for m in missing[:20]:
            print('   -', m)
        print('\nUpload these, let Drive finish syncing, then run this again.')
    else:
        print('\nevery file was found in the Drive folder')

    json.dump(ids, io.open(os.path.join(REPO, 'tools', 'drive-file-ids.json'), 'w'), indent=0)
    print('file ids written to tools/drive-file-ids.json')


def share_links(folder):
    """Print a ready-to-paste calendar line for every file under `folder`:

        IMG: https://drive.google.com/file/d/<id>/view?usp=sharing     docs/events/2026/...

    Images get IMG:, anything else Link:. Paste the line above the "--" in the
    Google Calendar event's description."""
    ids = drive_ids()
    folder = folder.strip('/').replace('\\', '/')
    hits = sorted(p for p in ids if p.startswith(folder + '/') and not p.endswith('desktop.ini'))
    if not hits:
        raise SystemExit('nothing under %s in the shared Drive folder yet — has Drive finished syncing?' % folder)
    for p in hits:
        fid = ids[p]
        if fid.startswith('local'):
            print('(still uploading)  %s' % p)
            continue
        key = 'IMG:' if p.lower().endswith(IMAGE) else 'Link:'
        print('%-5s https://drive.google.com/file/d/%s/view?usp=sharing    %s' % (key, fid, p))


if __name__ == '__main__':
    if '--links' in sys.argv:
        rest = sys.argv[sys.argv.index('--links') + 1:]
        share_links(rest[0] if rest else 'docs/events')
    else:
        main()
