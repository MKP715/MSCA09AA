# -*- coding: utf-8 -*-
"""Build tailwind.css from the classes used in index.html.

The site used to pull Tailwind from the Play CDN, which downloads ~400 KB and
then compiles the stylesheet in the browser on every visit -- first paint on a
throttled phone took nearly twelve seconds. This builds the same stylesheet
ahead of time instead: about 48 KB, cached, no compile step for the visitor.

Run it whenever a Tailwind class is added to or removed from index.html:

    python tools/build_css.py

Needs Node and npm on PATH; the Tailwind binary is fetched with npx the first
time and cached by npm after that. Nothing is written unless the build works,
so a failed run leaves the published stylesheet alone.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

TAILWIND = 'tailwindcss@3.4.17'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, 'tools', 'css')
CONFIG = os.path.join(CSS_DIR, 'tailwind.config.js')
INPUT = os.path.join(CSS_DIR, 'tailwind.input.css')
OUTPUT = os.path.join(ROOT, 'tailwind.css')
INDEX = os.path.join(ROOT, 'index.html')


def npx():
    """npx is a .cmd shim on Windows, so it needs the shell there."""
    exe = shutil.which('npx') or shutil.which('npx.cmd')
    if not exe:
        sys.exit('npx not found on PATH. Install Node.js, then run this again.')
    return exe


def main():
    for path in (CONFIG, INPUT, INDEX):
        if not os.path.exists(path):
            sys.exit('missing ' + os.path.relpath(path, ROOT))

    before = os.path.getsize(OUTPUT) if os.path.exists(OUTPUT) else 0
    tmp = os.path.join(tempfile.gettempdir(), 'msca09-tailwind.css')

    cmd = [npx(), '--yes', TAILWIND,
           '--config', CONFIG, '--input', INPUT, '--output', tmp, '--minify']
    print('building from', os.path.relpath(INDEX, ROOT), '...')
    proc = subprocess.Popen(cmd, cwd=CSS_DIR,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
    log = proc.communicate()[0]
    if proc.returncode != 0 or not os.path.exists(tmp):
        sys.stdout.write(log)
        sys.exit('build failed -- ' + os.path.relpath(OUTPUT, ROOT) + ' left unchanged')

    css = io.open(tmp, encoding='utf-8').read()
    os.remove(tmp)

    # A build that produced almost nothing means the content glob stopped
    # matching index.html; publishing that would ship an unstyled site.
    if len(css) < 20000:
        sys.exit('built stylesheet is only %d bytes -- check the content path '
                 'in tools/css/tailwind.config.js' % len(css))

    io.open(OUTPUT, 'w', encoding='utf-8', newline='').write(css)
    after = len(css.encode('utf-8'))
    print('wrote %s  %.1f KB%s' % (
        os.path.relpath(OUTPUT, ROOT), after / 1024.0,
        '' if not before else '  (was %.1f KB)' % (before / 1024.0)))
    print('now re-check the pages:  python tools/check_site.py')


if __name__ == '__main__':
    main()
