"""
Gujarat Schemes Detail Scraper  (FINAL)
-----------------------------------------
Reads gujarat_schemes.csv (scheme_name, scheme_link, category) and
scrapes Details, Benefits, Eligibility, Application Process, Documents Required
from each scheme page by extracting text between <h3 font-semibold> headings.

Install:
    pip install playwright
    playwright install chromium

Output: data/processed/scraped_schemes.csv
"""

import os, csv, time, re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")
INPUT_FILE   = os.path.join(DATA_DIR, "raw", "gujarat_schemes.csv")
OUTPUT_FILE  = os.path.join(DATA_DIR, "processed", "scraped_schemes.csv")

# Sections to scrape (no Exclusions)
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
    Load page once, extract all section texts by walking between
    <h3 class="...font-semibold..."> headings in the content panel.
    """
    return page.evaluate("""(sectionNames) => {
        const tabUl = document.querySelector('ul:has(li.side-tabs)');
        const flex1 = tabUl?.parentElement?.parentElement;
        const grid  = flex1?.parentElement;
        if (!grid) return {};

        // Content panel = largest sibling div of the tab sidebar
        const panel = Array.from(grid.children)
            .filter(c => c !== flex1 && c.tagName === 'DIV')
            .sort((a, b) => (b.innerText||'').length - (a.innerText||'').length)[0];
        if (!panel) return {};

        // Section headings: h3 with font-semibold class
        const sectionH3s = Array.from(panel.querySelectorAll('h3'))
            .filter(h => h.className.includes('font-semibold'));
        if (sectionH3s.length === 0) return {};

        const results = {};
        sectionH3s.forEach((h3, idx) => {
            const label = (h3.innerText || '').trim();
            if (!sectionNames.includes(label)) return;

            const nextH3 = sectionH3s[idx + 1];
            const parts  = [];
            let node = h3.nextElementSibling;
            while (node) {
                if (node === nextH3) break;
                if (node.tagName === 'H3' && node.className.includes('font-semibold')) break;
                const text = (node.innerText || '').trim();
                if (text) parts.push(text);
                node = node.nextElementSibling;
            }
            results[label] = parts.join('\\n').trim();
        });
        return results;
    }""", SECTIONS)


def scrape_scheme(page, name: str, url: str, category: str) -> dict:
    print(f"  {name[:70]}")
    result = {
        "scheme_name": name,
        "scheme_link": url,
        "category":    category,
        "error":       "",
    }
    for s in SECTIONS:
        result[col(s)] = "Not found"

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except PWTimeout:
        print("    ⚠ Load timeout")
        result["error"] = "page load timeout"
        return result

    try:
        page.wait_for_selector("h3[class*='font-semibold']", timeout=10000)
    except PWTimeout:
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
            name     = row.get("scheme_name", "").strip()
            url      = (row.get("scheme_link") or row.get("link") or "").strip()
            category = row.get("category", "").strip()
            if name and url:
                schemes.append((name, url, category))

    print(f"[+] Loaded {len(schemes)} schemes\n")

    fieldnames = (
        ["scheme_name", "scheme_link", "category"]
        + [col(s) for s in SECTIONS]
        + ["error"]
    )

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

            for i, (name, url, category) in enumerate(schemes, 1):
                print(f"\n[{i}/{len(schemes)}]", end=" ")
                try:
                    row = scrape_scheme(bpage, name, url, category)
                except Exception as e:
                    print(f"  ✗ {e}")
                    row = {k: "" for k in fieldnames}
                    row.update({"scheme_name": name, "scheme_link": url,
                                "category": category, "error": str(e)})

                writer.writerow(row)
                out_f.flush()
                time.sleep(0.8)

        browser.close()

    print(f"\n✅ Done! Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()