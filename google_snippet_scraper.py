
import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def get_researchers_from_google(institution, platform="researchgate.net", max_results=10):
    """
    Extrait les informations des chercheurs directement depuis les snippets Google.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        query = f'site:{platform} "{institution}"'
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        print(f"Recherche Google fallback ({platform}) : {institution}")

        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(3, 6))
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            search_results = soup.select(".g")
            for res in search_results[:max_results]:
                try:
                    title_tag = res.select_one("h3")
                    link_tag = res.select_one("a")
                    snippet_tag = res.select_one(".VwiC3b") or res.select_one(".st")
                    if not title_tag or not link_tag: continue
                    name = title_tag.get_text().split("|")[0].split("-")[0].strip()
                    results.append({
                        "name": name, "link": link_tag["href"],
                        "snippet": snippet_tag.get_text() if snippet_tag else "",
                        "source": f"Google Snippet ({platform})"
                    })
                except: continue
        except Exception as e:
            print(f"Erreur fallback Google : {e}")
        finally:
            await browser.close()
    return results
