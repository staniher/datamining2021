
import asyncio
import json
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

async def get_researchgate_authors(institution, max_authors=10):
    """
    Scrapes ResearchGate for authors affiliated with a specific institution.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        url = f"https://www.researchgate.net/search/authors?q={institution.replace(' ', '+')}"
        print(f"Scraping ResearchGate for: {institution}")

        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(3, 6))

            content = await page.content()
            if "security check" in content.lower() or "cloudflare" in content.lower():
                print("Warning: ResearchGate Cloudflare protection detected.")
                return []

            soup = BeautifulSoup(content, "html.parser")
            authors = soup.find_all("div", class_="nova-legacy-v-person-item") or soup.find_all("div", class_="nova-v-person-item")

            for author in authors[:max_authors]:
                try:
                    name_tag = author.find("a", class_="nova-legacy-e-link") or author.find("a", class_="nova-e-link")
                    name = name_tag.text.strip() if name_tag else "N/A"
                    link = "https://www.researchgate.net/" + name_tag["href"] if name_tag and "href" in name_tag.attrs else "N/A"

                    details = author.find_all("li", class_="nova-legacy-v-person-item__info-section-list-item")
                    info = [d.text.strip() for d in details]

                    results.append({
                        "name": name,
                        "link": link,
                        "info": info,
                        "source": "ResearchGate"
                    })
                except Exception as e:
                    print(f"Error parsing ResearchGate author: {e}")
                    continue
        except Exception as e:
            print(f"An error occurred while scraping ResearchGate: {e}")
        finally:
            await browser.close()

    return results

if __name__ == "__main__":
    import sys
    inst = sys.argv[1] if len(sys.argv) > 1 else "Université de Kinshasa"
    data = asyncio.run(get_researchgate_authors(inst))
    print(f"Found {len(data)} authors on ResearchGate.")
