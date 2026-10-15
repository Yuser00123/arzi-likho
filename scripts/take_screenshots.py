"""Screenshots for the README/DEV post: python3 scripts/take_screenshots.py <url> <outdir>

Drives the live app through a full journey on a phone-sized browser:
matter picker open -> RTI form filled -> 'Gemma लिख रहा है' state -> finished letter + कहाँ जमा करें.

Note: Gradio 6 dropdowns swallow the very first option click in a headless browser (it sets the
input value but never fires the change event), so the matter dropdown gets one warm-up selection
before the real one. Pool selects (gender/department) have no event listeners — their values are
read at generate time — so a plain click is enough for them.
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

FIELDS = [
    ("आवेदक का पूरा नाम", "राम कुमार यादव"),
    ("पिता / पति का नाम", "श्री सुरेश यादव"),
    ("पूरा पता", "मोहल्ला गाँधी नगर, पोस्ट सदर, थाना कोतवाली"),
    ("मोबाइल नंबर", "9876543210"),
    ("किस अवधि की सूचना?", "अप्रैल 2025 से मार्च 2026"),
]
POINTS = "पिछले वित्त वर्ष में मेरे खाते में जमा कुल बिल राशि\nगलत बिल वसूली के आदेश की प्रति"


def fill(page, label, value):
    page.get_by_label(label, exact=False).first.fill(value)


def pick(page, label, option_text):
    page.get_by_label(label, exact=False).first.click()
    page.wait_for_timeout(700)
    page.locator("li").filter(has_text=option_text).first.click()
    page.wait_for_timeout(500)


def shoot(url: str, outdir: str):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 412, "height": 915}, device_scale_factor=2)
        page.goto(url, wait_until="domcontentloaded", timeout=180000)
        page.wait_for_selector("textarea, input", timeout=60000)
        page.wait_for_timeout(4000)

        # 1 — the matter picker, open, showing all 12 matters (also the warm-up round)
        dd = page.get_by_label("किस काम की अर्ज़ी?", exact=False).first
        dd.click()
        page.wait_for_timeout(900)
        page.screenshot(path=str(out / "1-home.png"))
        page.locator("li").filter(has_text="पेंशन — वृद्धावस्था").first.click()  # warm-up (no commit)
        page.wait_for_timeout(800)

        # the real selection — commits, fields appear
        dd.click()
        page.wait_for_timeout(700)
        page.locator("li").filter(has_text="आरटीआई — किस").first.click()
        page.wait_for_timeout(1500)

        # 2 — the RTI form, filled with a real Raebareli case
        pick(page, "लिंग", "पुरुष")
        pick(page, "किस विभाग से सूचना चाहिए", "विद्युत विभाग")
        for label, value in FIELDS:
            fill(page, label, value)
        fill(page, "कौन-सी सूचना चाहिए", POINTS)
        page.wait_for_timeout(600)
        page.screenshot(path=str(out / "2-form.png"), full_page=True)

        # 3 — the generating state (status line under the button)
        page.get_by_role("button", name="अर्ज़ी बनाओ").click()
        page.wait_for_timeout(4000)
        page.screenshot(path=str(out / "3-generating.png"))

        # 4 — the finished letter (waits for the real Gemma call)
        page.wait_for_function(
            "() => { const t = document.querySelector('#letter-print textarea'); return !!(t && t.value.includes('भवदीय')); }",
            timeout=300000,
        )
        page.wait_for_timeout(1500)
        page.screenshot(path=str(out / "4-letter.png"), full_page=True)

        # 5 — the कहाँ जमा करें box, in the viewport
        page.locator("#kahan").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.screenshot(path=str(out / "5-kahan.png"))
        browser.close()
    print("done:", sorted(p.name for p in out.glob("*.png")))


if __name__ == "__main__":
    t0 = time.time()
    shoot(sys.argv[1], sys.argv[2])
    print(f"took {time.time() - t0:.0f}s")
