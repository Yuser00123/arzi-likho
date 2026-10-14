"""Screenshots for the README: python3 scripts/take_screenshots.py <url> <outdir>"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def shoot(url: str, outdir: str):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 412, "height": 915}, device_scale_factor=2)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("select, input", timeout=30000)
        page.wait_for_timeout(2500)
        page.screenshot(path=str(out / "1-home.png"), full_page=True)
        browser.close()
    print("done:", out)


if __name__ == "__main__":
    shoot(sys.argv[1], sys.argv[2])
