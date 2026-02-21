
import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

async def scrape_blog(url):
    """
    Extrait le texte d'un blog.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="load", timeout=30000)
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            for script in soup(["script", "style"]): script.decompose()
            text = soup.get_text(separator=' ')
            return text[:2000]
        except Exception as e:
            print(f"Erreur blog {url}: {e}")
            return ""
        finally:
            await browser.close()
