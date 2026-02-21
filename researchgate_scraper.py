
import asyncio
import json
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def apply_stealth_simple(page):
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => False
        });
    """)

async def get_researchgate_authors(institution, max_authors=5, local_file=None):
    if local_file:
        with open(local_file, "r", encoding="utf-8") as f:
            return parse_rg_authors(f.read(), max_authors)

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await apply_stealth_simple(page)

        if institution.startswith("http"):
            url = institution
            if "/institution/" in url and not url.endswith("/members"):
                url = url.rstrip("/") + "/members"
        else:
            url = f"https://www.researchgate.net/search/authors?q={urllib.parse.quote(institution)}"

        print(f"Extraction ResearchGate : {institution}")

        try:
            await page.goto(url, wait_until="load", timeout=90000)
            await asyncio.sleep(random.uniform(5, 8))
            content = await page.content()
            if "security check" in content.lower() or "cloudflare" in content.lower():
                print(f"Bloqué par Cloudflare ResearchGate pour {institution}.")
                return []
            results = parse_rg_authors(content, max_authors)
        except Exception as e:
            print(f"Erreur RG : {e}")
        finally:
            await browser.close()
    return results

def parse_rg_authors(html, max_authors):
    results = []
    soup = BeautifulSoup(html, "html.parser")
    authors = soup.find_all("div", class_="nova-legacy-v-person-item") or \
              soup.find_all("div", class_="nova-v-person-item") or \
              soup.select(".nova-v-person-item__body")
    for author in authors[:max_authors]:
        try:
            link_tag = author.find("a", href=True)
            if not link_tag: continue
            name = link_tag.get_text().strip()
            href = link_tag["href"]
            link = "https://www.researchgate.net/" + href if not href.startswith("http") else href
            info = [d.get_text().strip() for d in author.find_all("li") if len(d.get_text().strip()) > 2]
            results.append({"name": name, "link": link, "info": info, "source": "ResearchGate"})
        except: continue
    return results
