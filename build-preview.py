"""Build lightweight site pages; optionally build independent HTML previews."""
from pathlib import Path
import argparse
import base64
import hashlib
import mimetypes
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
VIDEO_URL = 'https://www.fix-events.fr/wp-content/uploads/2025/02/Film-FIX-e-2025.mp4'
ASSET_PATTERN = r'assets/[A-Za-z0-9_./-]+\.(?:png|jpe?g|webp|ttf|mp4)'


def optimized_asset(asset):
    source = ROOT / asset
    if source.suffix.lower() in {'.png', '.jpeg', '.jpg'}:
        optimized = ROOT / 'assets' / 'preview' / (source.stem + '.webp')
        if optimized.is_file():
            return optimized.relative_to(ROOT).as_posix()
    return asset


def optimize(text):
    return re.sub(ASSET_PATTERN, lambda match: optimized_asset(match.group(0)), text)


def version(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]


def build(standalone=False):
    subprocess.run([sys.executable, str(ROOT / 'build-pages.py')], check=True)
    css = optimize((ROOT / 'styles.css').read_text())
    (ROOT / 'site.css').write_text(css)
    # The small shared catalogue is cached across every page.
    catalog = optimize((ROOT / 'catalog-data.js').read_text())
    (ROOT / 'catalog-data.js').write_text(catalog)
    script = (ROOT / 'script.js').read_text()
    templates = [(ROOT / 'page.html', 'index.html')]
    templates.extend((source, source.name) for source in sorted((ROOT / 'pages').glob('*.html')))
    previews = ROOT / 'previews'
    encoded = {}

    def embed_asset(match):
        asset = optimized_asset(match.group(0))
        if asset.endswith('.mp4'):
            return VIDEO_URL
        if asset not in encoded:
            source = ROOT / asset
            mime = mimetypes.guess_type(source.name)[0] or 'application/octet-stream'
            encoded[asset] = f'data:{mime};base64,' + base64.b64encode(source.read_bytes()).decode('ascii')
        return encoded[asset]

    for source, name in templates:
        html = optimize(source.read_text())
        html = html.replace('href="styles.css"', f'href="site.css?v={version("site.css")}"')
        for asset in ('script.js', 'catalog-data.js'):
            html = html.replace(f'src="{asset}"', f'src="{asset}?v={version(asset)}"')
        (ROOT / name).write_text(html)
        print(f'Built {name}: {len(html.encode()):,} bytes')
        if not standalone:
            continue
        previews.mkdir(exist_ok=True)
        preview = optimize(source.read_text())
        preview = preview.replace('<link rel="stylesheet" href="styles.css">', '<style>\n' + css + '\n</style>')
        preview = preview.replace('<script src="catalog-data.js" defer></script>', '')
        preview = preview.replace('<script src="script.js" defer></script>', '')
        preview = re.sub(ASSET_PATTERN, embed_asset, preview)
        inline_catalog = re.sub(ASSET_PATTERN, embed_asset, catalog)
        inline_script = script.replace('</script', '<\\/script')
        preview = preview.replace('</body>', '<script>\n' + inline_catalog + '\n' + inline_script + '\n</script>\n</body>')
        (previews / name).write_text(preview)
    if standalone:
        print(f'Independent previews written to {previews.relative_to(ROOT)}/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone', action='store_true', help='Also generate independent HTML pages under previews/')
    build(parser.parse_args().standalone)
