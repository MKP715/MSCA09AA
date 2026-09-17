# -*- coding: utf-8 -*-
"""Build social-card.jpg - the picture chat apps show when someone shares a link.

    python tools/build_social_card.py

It is built from the same coastline photo as the home page banner, so a link
pasted into a text message looks like the site it opens. Re-run it after
changing hero.jpg or the Area's name in data/content.csv.

Needs Pillow:  pip install pillow
"""
import csv
import io
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit('This needs Pillow:  pip install pillow')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERO = os.path.join(ROOT, 'hero.jpg')
OUT = os.path.join(ROOT, 'social-card.jpg')
W, H = 1200, 630                      # what every chat app and search engine wants

# Bricolage Grotesque is not installed locally, so fall back through the
# heaviest sans faces Windows and macOS ship with.
FONT_DIRS = ['C:/Windows/Fonts', '/Library/Fonts', '/usr/share/fonts/truetype/dejavu']
HEAVY = ['seguibl.ttf', 'ariblk.ttf', 'Arial Black.ttf', 'DejaVuSans-Bold.ttf']
BOLD = ['segoeuib.ttf', 'arialbd.ttf', 'Arial Bold.ttf', 'DejaVuSans-Bold.ttf']
BOOK = ['segoeui.ttf', 'arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf']


def font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def content(key, default):
    """Read a line from data/content.csv so the card cannot drift from the site."""
    path = os.path.join(ROOT, 'data', 'content.csv')
    try:
        for r in csv.DictReader(io.open(path, encoding='utf-8-sig')):
            if r.get('key') == key and (r.get('en') or '').strip():
                return r['en'].strip()
    except IOError:
        pass
    return default


def main():
    if not os.path.exists(HERO):
        sys.exit('hero.jpg is missing - it is the background for this card')

    # ── the photo, cropped to card shape from the lower half where the coast is
    src = Image.open(HERO).convert('RGB')
    scale = max(W / float(src.width), H / float(src.height))
    img = src.resize((int(src.width * scale + 1), int(src.height * scale + 1)), Image.LANCZOS)
    top = int((img.height - H) * 0.62)
    img = img.crop((0, top, W, top + H))

    # ── the same scrim the home page uses, so the two look related ──────────
    scrim = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(scrim)
    for x in range(W):
        t = x / float(W - 1)
        a = 0.93 - 0.58 * t                      # dark at the left, open at the right
        d.line([(x, 0), (x, H)], fill=(int(10 + 22 * (1 - a)), int(12 + 20 * (1 - a)),
                                       int(40 + 60 * (1 - a))))
    mask = Image.new('L', (W, H))
    md = ImageDraw.Draw(mask)
    for x in range(W):
        md.line([(x, 0), (x, H)], fill=int(255 * (0.93 - 0.55 * (x / float(W - 1)))))
    img = Image.composite(scrim, img, mask)

    # a touch of depth at the bottom so the colour bar has something to sit on
    shade = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        sd.line([(0, y), (W, y)], fill=int(150 * max(0.0, (y - H * 0.62) / (H * 0.38)) ** 1.4))
    img = Image.composite(Image.new('RGB', (W, H), (8, 9, 30)), img, shade)

    d = ImageDraw.Draw(img)

    # ── the 09 mark and wordmark ────────────────────────────────────────────
    d.rounded_rectangle([64, 56, 152, 144], radius=24, fill=(247, 247, 253))
    f = font(HEAVY, 40)
    box = d.textbbox((0, 0), '09', font=f)
    d.text((108 - (box[2] - box[0]) / 2, 100 - (box[3] - box[1]) / 2 - box[1]),
           '09', font=f, fill=(67, 56, 202))

    d.text((174, 70), 'MSCA', font=font(HEAVY, 38), fill=(255, 255, 255))
    wm = d.textlength('MSCA', font=font(HEAVY, 38))
    d.text((174 + wm, 70), '09', font=font(HEAVY, 38), fill=(253, 224, 71))
    d.text((176, 118), content('home.kicker', 'Alcoholics Anonymous').upper(),
           font=font(BOLD, 19), fill=(255, 255, 255, 220))

    # ── the Area's name, as big as it will go ───────────────────────────────
    title = content('home.title', 'Mid-Southern California Area 09')
    words = title.split()
    # break before "Area" when there is one, otherwise halfway
    cut = words.index('Area') if 'Area' in words else (len(words) + 1) // 2
    lines = [' '.join(words[:cut]), ' '.join(words[cut:])]

    size = 92
    while size > 40:
        f = font(HEAVY, size)
        if max(d.textlength(l, font=f) for l in lines) <= W - 128:
            break
        size -= 2
    f = font(HEAVY, size)

    y = 236
    for line in lines:
        # a soft drop shadow, the same idea as .hero-title on the page
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((64, y + 3), line, font=f, fill=(5, 6, 25, 150))
        img.paste(Image.alpha_composite(img.convert('RGBA'),
                                        sh.filter(ImageFilter.GaussianBlur(8))).convert('RGB'))
        d = ImageDraw.Draw(img)
        d.text((64, y), line, font=f, fill=(255, 255, 255))
        y += int(size * 1.06)

    # ── tagline and the counties ────────────────────────────────────────────
    d.text((66, y + 14), content('home.tagline', 'Service is how we stay sober together'),
           font=font(BOLD, 30), fill=(253, 230, 138))
    d.text((66, y + 62), 'Orange \u00b7 Riverside \u00b7 San Bernardino \u00b7 Los Angeles',
           font=font(BOOK, 25), fill=(226, 228, 245))

    # ── the four-colour bar the site uses as a rule ─────────────────────────
    bar, bh = [(99, 102, 241), (217, 70, 239), (249, 115, 22), (34, 211, 238)], 12
    for i, col in enumerate(bar):
        d.rectangle([i * W / 4.0, H - bh, (i + 1) * W / 4.0, H], fill=col)

    # a photograph, so JPEG: the PNG of this same card was 817 KB
    img.save(OUT, 'JPEG', quality=86, optimize=True, progressive=True, subsampling=1)
    print('wrote %s  %dx%d  %.0f KB' %
          (os.path.relpath(OUT, ROOT), W, H, os.path.getsize(OUT) / 1024.0))


if __name__ == '__main__':
    main()
