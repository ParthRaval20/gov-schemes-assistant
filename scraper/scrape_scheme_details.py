"""
Gujarat Schemes Detail Scraper  (FINAL)
-----------------------------------------
All section content (Details, Benefits, Eligibility, Application Process,
Documents Required) lives in ONE div on the page — no tab switching needed.
Each section is headed by an <h3 class="...font-semibold..."> tag.

We load the page once and extract text between consecutive h3 section headings.

Install:
    pip install playwright
    playwright install chromium

Output: data/scraped_schemes.csv
"""

import os, csv, time, re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")
INPUT_FILE   = os.path.join(DATA_DIR, "raw", "gujarat_schemes.csv")
OUTPUT_FILE  = os.path.join(DATA_DIR, "processed","scraped_schemes.csv")

# Sections we want 
SECTIONS = [
    "Details",
    "Benefits",
    "Eligibility",
    "Application Process",
    "Documents Required",
]

def col(label: str) -> str:
    return label.lower().replace(" ", "_")

TRAILING_NOISE = re.compile(
    r"(Frequently Asked Questions.*|Sources And References.*|Feedback.*|Was this helpful.*)",
    re.DOTALL | re.IGNORECASE
)


def extract_sections(page) -> dict:
    """
    Extract all section texts in one JS call by walking the DOM.
    Sections are separated by <h3 class="...font-semibold..."> headings.
    """
    return page.evaluate("""(sectionNames) => {
        // Find the content panel: col-span-5 sibling of the tab sidebar
        const tabUl  = document.querySelector('ul:has(li.side-tabs)');
        const flex1  = tabUl?.parentElement?.parentElement;
        const grid   = flex1?.parentElement;
        if (!grid) return {};

        const panel = Array.from(grid.children)
            .filter(c => c !== flex1 && c.tagName === 'DIV')
            .sort((a, b) => (b.innerText||'').length - (a.innerText||'').length)[0];
        if (!panel) return {};

        // Find all section h3 headings (they have font-semibold class)
        // e.g. class="text-lg sm:text-xl md:text-2xl ... font-semibold ..."
        const sectionH3s = Array.from(panel.querySelectorAll('h3'))
            .filter(h => h.className.includes('font-semibold'));

        if (sectionH3s.length === 0) return {};

        const results = {};

        sectionH3s.forEach((h3, idx) => {
            const sectionLabel = (h3.innerText || '').trim();
            if (!sectionNames.includes(sectionLabel)) return;

            // Collect all sibling nodes between this h3 and the next section h3
            const nextH3 = sectionH3s[idx + 1];
            const parts  = [];
            let node = h3.nextElementSibling;

            while (node) {
                if (node === nextH3) break;
                // Stop if we hit another section heading
                if (node.tagName === 'H3' && node.className.includes('font-semibold')) break;
                const text = (node.innerText || '').trim();
                if (text) parts.push(text);
                node = node.nextElementSibling;
            }

            results[sectionLabel] = parts.join('\\n').trim();
        });

        return results;
    }""", SECTIONS)


def scrape_scheme(page, name: str, url: str) -> dict:
    print(f"  {name[:70]}")
    result = {"scheme_name": name, "scheme_link": url, "error": ""}
    for s in SECTIONS:
        result[col(s)] = "Not found"

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except PWTimeout:
        print("    ⚠ Load timeout")
        result["error"] = "page load timeout"
        return result

    # Wait for section headings to render
    try:
        page.wait_for_selector("h3.\\!font-semibold, h3[class*='font-semibold']", timeout=10000)
    except PWTimeout:
        # Try waiting for the tab list as fallback signal
        try:
            page.wait_for_selector("li.side-tabs", timeout=5000)
        except PWTimeout:
            pass

    page.wait_for_timeout(1500)

    sections = extract_sections(page)

    for s in SECTIONS:
        text = sections.get(s, "Not found")
        if text:
            text = TRAILING_NOISE.sub('', text).strip()
        result[col(s)] = text or "Not found"
        preview = (text or "")[:90].replace('\n', ' ').strip()
        print(f"    [{s:20s}]: {preview}")

    return result


def main():
    schemes = []
    with open(INPUT_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = row.get("scheme_name", "").strip()
            url  = (row.get("scheme_link") or row.get("link") or "").strip()
            if name and url:
                schemes.append((name, url))

    print(f"[+] Loaded {len(schemes)} schemes\n")

    fieldnames = ["scheme_name", "scheme_link"] + [col(s) for s in SECTIONS] + ["error"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        bpage = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        ).new_page()

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=fieldnames)
            writer.writeheader()

            for i, (name, url) in enumerate(schemes, 1):
                print(f"\n[{i}/{len(schemes)}]", end=" ")
                try:
                    row = scrape_scheme(bpage, name, url)
                except Exception as e:
                    print(f"  ✗ {e}")
                    row = {k: "" for k in fieldnames}
                    row.update({"scheme_name": name, "scheme_link": url, "error": str(e)})

                writer.writerow(row)
                out_f.flush()
                time.sleep(0.8)

        browser.close()

    print(f"\n✅ Done! Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()