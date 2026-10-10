"""Bundle the page into HTML that does not require sibling files in a preview.

Uses only the Python standard library. Optimized image copies are retained in
assets/preview; the original source images are retained in assets.
"""
from pathlib import Path
import base64
import mimetypes
import re

ROOT = Path(__file__).resolve().parent
VIDEO_URL = 'https://www.fix-events.fr/wp-content/uploads/2025/02/Film-FIX-e-2025.mp4'
encoded_assets = {}


def bundle_asset(match):
    asset = match.group(0)
    if asset.endswith('.mp4'):
        return VIDEO_URL
    if asset not in encoded_assets:
        source = ROOT / asset
        if source.suffix.lower() in {'.png', '.jpeg', '.jpg'}:
            optimized = ROOT / 'assets' / 'preview' / (source.stem + '.webp')
            if optimized.is_file():
                source = optimized
        mime = mimetypes.guess_type(source.name)[0] or 'application/octet-stream'
        encoded_assets[asset] = f'data:{mime};base64,' + base64.b64encode(source.read_bytes()).decode('ascii')
    return encoded_assets[asset]


def inline_assets(text):
    return re.sub(r'assets/[A-Za-z0-9_./-]+\.(?:png|jpe?g|webp|ttf|mp4)', bundle_asset, text)


html = (ROOT / 'page.html').read_text()
css = inline_assets((ROOT / 'styles.css').read_text())
# Escape closing script tags if source code ever contains one inside a string.
js = (ROOT / 'script.js').read_text().replace('</script', '<\\/script')
html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>\n' + css + '\n</style>')
html = html.replace('<script src="script.js" defer></script>', '')
html = inline_assets(html)
html = html.replace('</body>', '<script>\n' + js + '\n</script>\n</body>')
(ROOT / 'index.html').write_text(html)
print(f'Built index.html ({len(html.encode()):,} bytes): inline styles, scripts, fonts and images.')
