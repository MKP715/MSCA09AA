# -*- coding: utf-8 -*-
"""Refresh data/events.csv from the Area's published events.

    python tools/fetch_events.py --dry-run     # report, change nothing
    python tools/fetch_events.py               # rewrite data/events.csv
    python tools/fetch_events.py --images      # also download new flyers

msca09aa.org runs The Events Calendar, which publishes a REST feed. That feed
lists a repeating event once per occurrence: the ACYPAA business meeting alone
is fourteen separate entries. This collapses each repeated title back into a
single row carrying an iCalendar RRULE, which is what the site expands when it
draws the events page.

Recurrence is *derived from the dates themselves*, not hand-written: the dates
are grouped by title and time, the fitting rule is worked out, and any date the
rule would invent is written to `exdates` so the series still reproduces the
published dates exactly. A series is bounded with UNTIL at its last published
occurrence -- the Area publishes as it schedules, so inventing dates beyond
that would put meetings on the site that nobody has agreed to.

Flyers are hosted on Google Drive (see the README). --images downloads any new
ones into the Drive folder; run tools/drive_links.py afterwards to turn them
into Drive addresses.
"""
import argparse
import calendar
import collections
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, 'data', 'events.csv')
DRIVE = r'G:\My Drive\RowlettAATech\MSCA09AA'

API = ('https://msca09aa.org/wp-json/tribe/events/v1/events'
       '?per_page=50&status=publish&start_date=%s&page=%d')
UA = {'User-Agent': 'Mozilla/5.0 (compatible; MSCA09-events/1.0)'}

COLUMNS = ['slug', 'start', 'end', 'all_day', 'title', 'title_es', 'kind',
           'language', 'venue', 'address', 'city', 'region', 'postal', 'cost',
           'flyer_paths', 'flyers', 'description', 'website', 'contact_email',
           'thumbs', 'rrule', 'exdates']

DAY = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

# The Area's own business meetings are scheduled in data/area-meetings.csv and
# the real pattern is irregular (mostly 2nd Sunday, but not in May or
# November). Deriving a rule from two of them would be wrong, so they stay as
# individual rows.
NEVER_COLLAPSE = re.compile(
    r'area service (committee|assembly)|preconference|pre-conference|'
    r'\basc\b|assembly|servathon|delegate shareback', re.I)

# Which of the site's own categories a title belongs to. First match wins.
KINDS = [
    (r'servathon', 'Servathon'),
    (r'assembly|asamblea', 'Assembly'),
    (r'\basc\b|area service committee|preconference|pre-conference', 'Area Committee'),
    (r'ypaa|acypaa|rocypaa|gsdypaa', 'YPAA'),
    (r'convention|conferencia', 'Convention'),
    (r'\bforum\b|\bforo\b|regional forum', 'Forum'),
    (r'gsr school|service school|bootcamp|boot camp', 'Service School'),
    (r'workshop|taller', 'Workshop'),
]


def clean(text):
    """WordPress hands back HTML entities and markup; the CSV wants neither."""
    if not text:
        return ''
    t = re.sub(r'(?is)<(script|style).*?</\1>', ' ', text)
    t = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>', '\n', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    t = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), t)
    t = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), t)
    for a, b in [('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'"), ('&lt;', '<'),
                 ('&gt;', '>'), ('&nbsp;', ' '), ('&hellip;', '\u2026'),
                 ('&rsquo;', '\u2019'), ('&lsquo;', '\u2018'), ('&mdash;', '\u2014'),
                 ('&ndash;', '\u2013'), ('&ldquo;', '\u201c'), ('&rdquo;', '\u201d')]:
        t = t.replace(a, b)
    t = unicodedata.normalize('NFC', t)
    t = re.sub(r'[ \t\u00a0]+', ' ', t)
    t = re.sub(r'\n\s*\n\s*', '\n\n', t)
    return t.strip()


# Left alone when a shouted title is converted to normal case. Matched against
# the leading letters of a word, so ACYPAA54 and GSDYPAA'S keep their form.
ACRONYMS = ['ACYPAA', 'ROCYPAA', 'GSDYPAA', 'PRAASA', 'YPAA', 'SCAA', 'MSCA',
            'GSR', 'DCM', 'ASC', 'PSR', 'CPC', 'H&I', 'AA', 'PI', 'Y2K', 'D09',
            'LIV', 'SOCAL', 'AL-ANON', 'GSO', 'GSC']
SMALL = {'a', 'an', 'and', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'the',
         'to', 'with', 'de', 'la', 'el', 'y', 'en'}


def titlecase(t):
    """The site shouts some titles in capitals; the page does not need to."""
    if not t or t != t.upper():
        return t
    words, out = t.split(), []
    for i, w in enumerate(words):
        # the word with punctuation that is not part of an acronym stripped off;
        # curly apostrophes are folded so GSDYPAA’S matches GSDYPAA'S
        bare = w.replace('’', "'").replace('‘', "'")
        bare = re.sub(r"^[^A-Za-z0-9&]+|[^A-Za-z0-9&']+$", '', bare).upper()
        hit = next((a for a in ACRONYMS
                    if bare == a                       # ACYPAA
                    or bare.startswith(a + "'")        # GSDYPAA'S
                    or re.match(r'^%s\d+$' % re.escape(a), bare)),  # ACYPAA54
                   None)
        if hit:
            # keep the acronym, gentle-case anything hanging off it
            rest = w[len(hit):]
            out.append(hit + (rest.lower() if rest.isupper() or "'" in rest else rest))
            continue
        low = w.lower()
        if i and low.strip('@!,.:;()') in SMALL:
            out.append(low)
        else:
            out.append(low[:1].upper() + low[1:])
    return ' '.join(out)


# ── Tradition Eleven, enforced where the data comes in ──────────────────────
# Flyers routinely carry a member's mobile number ("contact Andrew at
# 562-507-6618"). Those must not go onto a public website, and stripping them
# here rather than by hand means a later refresh cannot quietly put them back.
# A toll-free number is a hotel or an office, never a member, so it stays.
PHONE = re.compile(r'(?<!\d)(?:\+?1[\s.-]?)?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})(?!\d)')
TOLL_FREE = {'800', '833', '844', '855', '866', '877', '888'}
# the words that introduce a conference ID rather than a telephone number
NOT_A_PHONE = re.compile(r'(?i)(zoom|meeting|webinar|conference)\s*(id|#)?\s*:?\s*$'
                         r'|\b(id|passcode|password|code)\s*:?\s*$')


def redact_phones(text):
    """Return (text, [numbers removed])."""
    if not text:
        return text, []
    removed = []

    def swap(m):
        if m.group(1) in TOLL_FREE:
            return m.group(0)
        before = text[max(0, m.start() - 26):m.start()]
        if NOT_A_PHONE.search(before):
            return m.group(0)
        removed.append(m.group(0))
        return ''

    out = PHONE.sub(swap, text)
    if removed:
        # tidy up what the number was hanging off: "at ", "call ", " - ", ": "
        out = re.sub(r'(?i)\b(at|call|text|phone|tel|contact(?:\s+\w+)?\s+at)\s*[:,]?\s*(?=[\s.,;)]|$)',
                     lambda m: m.group(1) if m.group(1).lower().startswith('contact') else '',
                     out)
        out = re.sub(r'[ \t]*[:,-]\s*(?=\n|$)', '', out)
        out = re.sub(r'\(\s*\)', '', out)
        out = re.sub(r'[ \t]{2,}', ' ', out)
        out = re.sub(r'\s+([.,;!?])', r'\1', out)      # "Carolyne ." -> "Carolyne."
        out = re.sub(r'\n{3,}', '\n\n', out)
    return out.strip(), removed


def norm_key(t):
    return re.sub(r'[^a-z0-9]+', '', clean(t).lower())


def slugify(title):
    """The slug is the shareable link, so build it from the title.

    WordPress's own slugs cannot be trusted for this: one of them is
    'd09-gsr-school-virtual-only-id-928-8170-4093-pc634401-3pm-pdt', which puts
    a Zoom meeting ID and its passcode into a public URL.
    """
    s = unicodedata.normalize('NFKD', clean(title))
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r"['’`]", '', s)
    s = re.sub(r'&', ' and ', s)
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
    s = re.sub(r'-{2,}', '-', s)
    return s[:58].strip('-') or 'event'


def bad_slug(slug, title):
    """Should this slug be thrown away and rebuilt from the title?

    A slug already in the CSV is normally kept, so a link somebody shared goes
    on working. Three kinds are not worth keeping: one that carries meeting
    credentials, one that is just a WordPress post number, and one that says
    nothing about the event ('d14workshop').
    """
    if not slug:
        return True
    if slug.isdigit():
        return True
    if re.search(r'(?:^|-)(id|pc|pw|pass(?:code)?)-?\d{3,}', slug):
        return True
    if len(re.findall(r'\d{3,}', slug)) >= 2:          # 928-8170-4093 ...
        return True
    want = slugify(title)
    return not (slug.startswith(want[:14]) or want.startswith(slug[:14]))


def kind_of(title, cats):
    for name in cats:
        if re.search(r'\basc\b', name, re.I):
            return 'Area Committee'
    for pat, k in KINDS:
        if re.search(pat, title, re.I):
            return k
    return 'Event'


SPANISH_WORDS = re.compile(
    r'(?i)espa\u00f1ol|hispano|hispanic|asamblea|taller|reuni\u00f3n|mujer(?:es)?|'
    r'c\u00f3digo|l\u00ednea|nosotros|gratis|\bforo\b|\bde la\b|\bpara\b|\bcon\b|'
    r'[\u00bf\u00a1]')
ENGLISH_WORDS = re.compile(
    r'(?i)\b(the|and|with|for|your|you|meeting|workshop|please|join|will|are|'
    r'from|this|that|our|all)\b')


def language_of(title, desc):
    """English, Spanish or Bilingual.

    Many flyers carry the whole thing twice, English then Spanish, so the mere
    presence of Spanish does not make an event Spanish-speaking -- both have to
    be weighed. The title counts for more than the body.
    """
    # a title that names its language settles it outright
    says_es = re.search(r'(?i)\b(spanish|español|hispano|hispanic)\b', title)
    says_en = re.search(r'(?i)\benglish\b|\binglés\b', title)
    if says_es and says_en:
        return 'Bilingual'
    if says_es:
        return 'Spanish'

    t_es = len(SPANISH_WORDS.findall(title))
    t_en = len(ENGLISH_WORDS.findall(title))
    d_es = len(SPANISH_WORDS.findall(desc or ''))
    d_en = len(ENGLISH_WORDS.findall(desc or ''))

    es = t_es * 3 + d_es
    en = t_en * 3 + d_en
    if es >= 2 and en >= 2:
        return 'Bilingual'
    if es >= 2 and en < 2:
        return 'Spanish'
    if t_es and not t_en:
        return 'Spanish'
    return 'English'


# ── talking to the site ──────────────────────────────────────────────────────
def fetch_all(since):
    events, page = [], 1
    while page < 60:
        try:
            req = urllib.request.Request(API % (since, page), headers=UA)
            data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode('utf-8'))
        except Exception as e:
            if page == 1:
                sys.exit('could not reach msca09aa.org: %s' % e)
            print('  page %d failed (%s) - carrying on with %d' % (page, e, len(events)))
            break
        got = data.get('events') or []
        if not got:
            break
        events.extend(got)
        total = int(data.get('total') or 0)
        print('  page %d: %d (%d of %d)' % (page, len(got), len(events), total))
        if len(events) >= total:
            break
        page += 1
        time.sleep(1.0)
    return events


# ── working out the repeat ───────────────────────────────────────────────────
def nth_of_month(d):
    return (d.day - 1) // 7 + 1


def monthly_dates(first, nths, weekday, last):
    """Every nth-weekday-of-the-month from `first` up to and including `last`."""
    out, cur = [], first.replace(day=1)
    while cur <= last:
        wk1 = dt.datetime(cur.year, cur.month, 1)
        off = (weekday - wk1.weekday()) % 7
        for n in nths:
            day = 1 + off + 7 * (n - 1)
            if day <= calendar.monthrange(cur.year, cur.month)[1]:
                when = dt.datetime(cur.year, cur.month, day, first.hour, first.minute)
                if first <= when <= last:
                    out.append(when)
        cur = dt.datetime(cur.year + (cur.month == 12), cur.month % 12 + 1, 1)
    return sorted(out)


def weekly_dates(first, last):
    out, cur = [], first
    while cur <= last:
        out.append(cur)
        cur = cur + dt.timedelta(days=7)
    return out


def derive_rule(dates):
    """Return (rrule, exdates) that reproduce `dates` exactly, or (None, None).

    Only rules that *cover* every published date are considered; dates the rule
    would add on top become exceptions. A rule needing a lot of exceptions is
    not really a pattern, so it is rejected.
    """
    if len(dates) < 2:
        return None, None
    dates = sorted(dates)
    first, last = dates[0], dates[-1]
    weekdays = set(d.weekday() for d in dates)
    until = last.strftime('%Y%m%dT%H%M%S')

    candidates = []
    if len(weekdays) == 1:
        wd = dates[0].weekday()
        nths = sorted(set(nth_of_month(d) for d in dates))
        if all(n <= 4 for n in nths) and len(nths) <= 2:
            gen = monthly_dates(first, nths, wd, last)
            candidates.append(('FREQ=MONTHLY;BYDAY=%s;UNTIL=%s'
                               % (','.join('%d%s' % (n, DAY[wd]) for n in nths), until), gen))
        candidates.append(('FREQ=WEEKLY;BYDAY=%s;UNTIL=%s' % (DAY[wd], until),
                           weekly_dates(first, last)))

    best = None
    for rule, generated in candidates:
        gset, dset = set(generated), set(dates)
        if not dset <= gset:                       # must cover every real date
            continue
        extra = sorted(gset - dset)
        if len(extra) > max(2, len(dates) * 0.34):  # too ragged to call a pattern
            continue
        if best is None or len(extra) < len(best[1]):
            best = (rule, extra)
    if not best:
        return None, None
    rule, extra = best
    return rule, ';'.join(d.strftime('%Y-%m-%d') for d in extra)


# ── flyers ───────────────────────────────────────────────────────────────────
def best_image(image):
    """The largest sensible rendition: the originals run to 9 MB scans."""
    if not image or not image.get('url'):
        return None
    sizes = image.get('sizes') or {}
    for name in ('full', 'large', '1536x1536', 'medium_large'):
        s = sizes.get(name)
        if s and s.get('url') and int(s.get('width') or 0) >= 800:
            return s['url']
    return image['url']


def download_images(rows, raw_by_slug):
    """Fetch each new flyer into the Drive folder as <slug>-1.jpg, with the
    matching <slug>-1.thumb.jpg the cards use. Everything is normalised to
    JPEG because that is what tools/drive_links.py pairs up, and because the
    originals include 1.4 MB PNG screenshots."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit('downloading flyers needs Pillow:  pip install pillow')

    dest = os.path.join(DRIVE, 'docs', 'events')
    if not os.path.isdir(dest):
        print('! Drive folder not found, skipping images: %s' % dest)
        return 0

    got = 0
    for r in rows:
        if r['flyers']:                     # already has a Drive address
            continue
        # a flyer_path is only real if the file is actually in the Drive folder;
        # a path left behind by an interrupted run should be fetched again
        if r['flyer_paths'] and all(
                os.path.exists(os.path.join(DRIVE, p.strip().replace('/', os.sep)))
                for p in r['flyer_paths'].split(';') if p.strip()):
            continue
        src = best_image((raw_by_slug.get(r['slug']) or {}).get('image'))
        if not src:
            continue
        name = '%s-1.jpg' % r['slug']
        full = os.path.join(dest, name)
        thumb = os.path.join(dest, '%s-1.thumb.jpg' % r['slug'])

        if not (os.path.exists(full) and os.path.exists(thumb)):
            try:
                req = urllib.request.Request(src, headers=UA)
                data = urllib.request.urlopen(req, timeout=120).read()
                im = Image.open(io.BytesIO(data))
                if im.mode not in ('RGB', 'L'):
                    im = im.convert('RGBA') if 'A' in im.mode else im.convert('RGB')
                    if im.mode == 'RGBA':          # flyers are printed on white
                        bg = Image.new('RGB', im.size, (255, 255, 255))
                        bg.paste(im, mask=im.split()[-1])
                        im = bg
                im = im.convert('RGB')

                # Cap the *longest* side: flyers are portrait, so a width-only
                # limit leaves a 1187x1536 scan untouched at 400 KB.
                def fit(src, longest):
                    if max(src.size) <= longest:
                        return src.copy()
                    f = longest / float(max(src.size))
                    return src.resize((max(1, int(src.width * f)),
                                       max(1, int(src.height * f))), Image.LANCZOS)

                fit(im, 1400).save(full, 'JPEG', quality=78,
                                   optimize=True, progressive=True)
                # the card shows this about 160px tall, so it can be modest
                fit(im, 620).save(thumb, 'JPEG', quality=62,
                                  optimize=True, progressive=True)

                print('  %-46s %4.0f KB -> %3.0f KB + %2.0f KB thumb'
                      % (name, len(data) / 1024.0,
                         os.path.getsize(full) / 1024.0,
                         os.path.getsize(thumb) / 1024.0))
                got += 1
                time.sleep(0.6)
            except Exception as e:
                print('  ! %s: %s' % (name, e))
                continue
        r['flyer_paths'] = 'docs/events/' + name
    return got


# ── putting it together ──────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='report, write nothing')
    ap.add_argument('--images', action='store_true', help='download new flyers to Drive')
    ap.add_argument('--since', default='2026-01-01', help='earliest event to keep')
    args = ap.parse_args()

    existing = {}
    if os.path.exists(CSV_PATH):
        for r in csv.DictReader(io.open(CSV_PATH, encoding='utf-8-sig')):
            existing[r['slug']] = r
    by_title = {}
    for r in existing.values():
        if r.get('title'):
            by_title.setdefault(norm_key(r['title']), []).append(r)

    print('fetching from msca09aa.org ...')
    raw = fetch_all(args.since)
    print('  %d occurrences published\n' % len(raw))

    # group occurrences by title + time of day
    groups = collections.OrderedDict()
    for e in sorted(raw, key=lambda x: x['start_date']):
        when = dt.datetime.strptime(e['start_date'], '%Y-%m-%d %H:%M:%S')
        groups.setdefault((norm_key(e['title']), when.strftime('%H:%M')), []).append((when, e))

    rows, collapsed, redacted, used = [], [], [], set()
    for (tkey, _), items in groups.items():
        dates = [w for w, _ in items]
        first_dt, lead = items[0]
        title = titlecase(clean(lead['title']))

        rrule, exdates = (None, None)
        if len(items) > 1 and not NEVER_COLLAPSE.search(title):
            rrule, exdates = derive_rule(dates)
            if rrule:
                collapsed.append((title, len(items), rrule, exdates))

        end_dt = dt.datetime.strptime(lead['end_date'], '%Y-%m-%d %H:%M:%S')

        # The Events Calendar does not repeat every field on every occurrence:
        # the first ACYPAA meeting carries no venue while later ones do. Take
        # the first occurrence that actually has one.
        def first_filled(field):
            for _, occ in items:
                v = occ.get(field)
                if isinstance(v, list):
                    v = v[0] if v else None
                if v:
                    return v
            return None

        venue = first_filled('venue') or {}
        if not isinstance(venue, dict):
            venue = {}
        desc, stripped = redact_phones(clean(first_filled('description')))
        if stripped:
            redacted.append((title, stripped))
        old = (by_title.get(tkey) or [{}])[0]

        # keep the slug a row already has, so links shared earlier keep working
        slug = old.get('slug') or ''
        if bad_slug(slug, title):
            slug = slugify(title)
        if slug in used:
            n = 2
            while '%s-%d' % (slug, n) in used:
                n += 1
            slug = '%s-%d' % (slug, n)
        used.add(slug)

        row = {
            'slug': slug,
            'start': first_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'end': end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'all_day': 'yes' if lead.get('all_day') else '',
            'title': title,
            'title_es': old.get('title_es', ''),
            'kind': kind_of(title, [c.get('name', '') for c in (lead.get('categories') or [])]),
            'language': language_of(title, desc),
            'venue': clean(venue.get('venue', '')),
            'address': clean(venue.get('address', '')),
            'city': clean(venue.get('city', '')),
            'region': clean(venue.get('state', '') or venue.get('province', '')),
            'postal': clean(venue.get('zip', '')),
            'cost': clean(lead.get('cost', '')),
            # keep whatever Drive addresses we already had for this event
            'flyer_paths': old.get('flyer_paths', ''),
            'flyers': old.get('flyers', ''),
            'thumbs': old.get('thumbs', ''),
            'description': desc[:1500],
            'website': clean(lead.get('website', '')),
            'contact_email': old.get('contact_email', ''),
            'rrule': rrule or '',
            'exdates': exdates or '',
        }
        rows.append(row)

    rows.sort(key=lambda r: r['start'])

    print('=== repeating events folded into one row each ===')
    if not collapsed:
        print('  (none found)')
    for title, n, rule, ex in collapsed:
        print('  %-44s %2d rows -> 1   %s' % (title[:44], n, rule))
        if ex:
            print('  %-44s     skips %s' % ('', ex.replace(';', ', ')))

    if redacted:
        print('\n=== personal phone numbers removed (Tradition Eleven) ===')
        for title, nums in redacted:
            print('  %-44s %s' % (title[:44], ', '.join(nums)))
        print('  Toll-free numbers are left alone - those are venues, not members.')

    print('\n%d published occurrences -> %d rows' % (len(raw), len(rows)))

    fresh = [r for r in rows if r['slug'] not in existing]
    print('%d new event(s):' % len(fresh))
    for r in fresh:
        print('   %s  %s' % (r['start'][:10], r['title'][:58]))

    if args.images and not args.dry_run:
        raw_by_slug = {}
        for e in raw:
            raw_by_slug.setdefault(e['slug'], e)
        n = download_images(rows, raw_by_slug)
        print('\ndownloaded %d flyer(s) into the Drive folder' % n)
        if n:
            print('now run:  python tools/drive_links.py')

    if args.dry_run:
        print('\n--dry-run: data/events.csv not written')
        return

    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator='\n')
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, '') for k in COLUMNS})
    io.open(CSV_PATH, 'w', encoding='utf-8-sig', newline='').write(out.getvalue())
    print('\nwrote %s  (%d rows)' % (os.path.relpath(CSV_PATH, ROOT), len(rows)))


if __name__ == '__main__':
    main()
