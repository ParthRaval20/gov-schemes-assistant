"""Debug: find category/tag elements on scheme page."""
import time
from playwright.sync_api import sync_playwright

URL = "https://www.myscheme.gov.in/schemes/mmuy"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        viewport={"width": 1280, "height": 900}
    ).new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    info = page.evaluate("""() => {
        // Look for category/tag/badge elements
        const results = {};

        // Check for pill/badge/tag elements near the title
        results.badges = Array.from(document.querySelectorAll(
            '[class*="badge"], [class*="tag"], [class*="pill"], [class*="chip"], [class*="categor"]'
        )).map(el => ({
            tag: el.tagName,
            class: el.className.slice(0,120),
            text: (el.innerText||'').trim(),
        })).filter(el => el.text.length > 0);

        // Look for the scheme header area (title + metadata)
        const header = document.querySelector('h1');
        if (header) {
            let parent = header.parentElement;
            for (let i = 0; i < 6; i++) {
                if (!parent) break;
                results[`headerParent_${i}`] = {
                    tag: parent.tagName,
                    class: parent.className.slice(0,100),
                    text: (parent.innerText||'').trim().slice(0,300),
                };
                parent = parent.parentElement;
            }
        }

        // Look for anchor tags near the top that look like categories
        results.categoryLinks = Array.from(document.querySelectorAll('a[href*="category"], a[href*="tag"]'))
            .map(a => ({href: a.href, text: (a.innerText||'').trim()}));

        // Find any span/div with category-like text near the h1
        results.allSpansNearTitle = Array.from(document.querySelectorAll(
            '[class*="raven"], [class*="indigo"], [class*="gray-500"], [class*="text-sm"]'
        ))
        .filter(el => {
            const t = (el.innerText||'').trim();
            return t.length > 2 && t.length < 100 && el.offsetParent !== null;
        })
        .slice(0, 20)
        .map(el => ({tag: el.tagName, class: el.className.slice(0,100), text: (el.innerText||'').trim()}));

        return results;
    }""")

    print("=== BADGES/TAGS ===")
    for b in info.get('badges', []):
        print(b)

    print("\n=== HEADER PARENTS ===")
    for k, v in info.items():
        if k.startswith('headerParent'):
            print(f"{k}: {v}")

    print("\n=== CATEGORY LINKS ===")
    for c in info.get('categoryLinks', []):
        print(c)

    print("\n=== SPANS NEAR TITLE ===")
    for s in info.get('allSpansNearTitle', []):
        print(s)

    input("\nPress Enter to close...")
    browser.close()