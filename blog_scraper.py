
import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

async def scrape_blog(url):
    """
    Scrapes a blog page and extracts the main text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        print(f"Scraping blog: {url}")
        try:
            await page.goto(url, wait_until="load", timeout=30000)
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ')
            # Simple cleaning
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text[:2000] # Return first 2000 chars
        except Exception as e:
            print(f"Error scraping blog {url}: {e}")
            return ""
        finally:
            await browser.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        asyncio.run(scrape_blog(sys.argv[1]))
