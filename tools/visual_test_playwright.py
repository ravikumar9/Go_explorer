"""
Playwright visual test script (captures before/after screenshots of the rooms page).

Run this locally in a virtualenv since the dev container may restrict installing browsers.

Usage (local machine):
  python -m venv .venv
  source .venv/bin/activate
  pip install playwright
  playwright install
  python tools/visual_test_playwright.py

The script will save screenshots to `screenshots/before.png` and `screenshots/after.png`.
"""
import os
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from booking.models import Hotel

hotel = Hotel.objects.filter(is_active=True).first()
if not hotel:
    raise SystemExit('No active hotel found in DB')

check_in = '2026-01-08'
check_out = '2026-01-10'
url = f'http://127.0.0.1:8001/rooms/{hotel.id}/?check_in={check_in}&check_out={check_out}'

out_dir = Path('screenshots')
out_dir.mkdir(exist_ok=True)

try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    raise SystemExit('Playwright not installed. See file header for install steps.')

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1280,'height':900})
    page.goto(url, wait_until='networkidle')

    # BEFORE: inject a large fixed width to emulate old (before) layout
    before_css = ".image-slider img, .hotel-img { width: 960px !important; max-width: none !important; }"
    page.add_style_tag(content=before_css)
    page.screenshot(path=str(out_dir / 'before.png'), full_page=True)

    # remove injected CSS by reloading page
    page.reload(wait_until='networkidle')
    page.screenshot(path=str(out_dir / 'after.png'), full_page=True)

    # also capture lightbox open state
    # attempt to click first image to open lightbox
    try:
        page.click('.image-slider img', timeout=2000)
        page.wait_for_selector('.lb-overlay.active', timeout=2000)
        page.screenshot(path=str(out_dir / 'lightbox.png'))
    except Exception:
        pass

    browser.close()

print('Screenshots saved to', out_dir)
