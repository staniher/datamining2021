
import asyncio
import json
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

async def get_scholar_authors(institution, max_authors=5):
    """
    Scrapes Google Scholar for authors and their top publications.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={institution.replace(' ', '+')}&hl=fr"
        print(f"Scraping Google Scholar for: {institution}")

        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(2, 4))

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            if "not a robot" in content.lower() or "captcha" in content.lower():
                print(f"Warning: Scholar CAPTCHA for {institution}")
                return []

            authors = soup.find_all("div", class_="gsc_1usr")
            for author_div in authors[:max_authors]:
                try:
                    name_tag = author_div.find("h3", class_="gs_ai_name")
                    name = name_tag.text.strip() if name_tag else "N/A"
                    link = "https://scholar.google.com" + name_tag.find("a")["href"] if name_tag and name_tag.find("a") else None

                    author_data = {
                        "name": name,
                        "link": link,
                        "affiliation": author_div.find("div", class_="gs_ai_aff").text.strip() if author_div.find("div", class_="gs_ai_aff") else "N/A",
                        "interests": [t.text.strip() for t in author_div.find_all("a", class_="gs_ai_one_int")],
                        "publications": [],
                        "source": "Google Scholar"
                    }

                    # Navigate to profile to get publications
                    if link:
                        await page.goto(link, wait_until="load", timeout=30000)
                        await asyncio.sleep(2)
                        p_content = await page.content()
                        psoup = BeautifulSoup(p_content, "html.parser")
                        pub_rows = psoup.find_all("tr", class_="gsc_a_tr")
                        for row in pub_rows[:5]: # Top 5 publications
                            title = row.find("a", class_="gsc_a_at").text.strip() if row.find("a", class_="gsc_a_at") else "N/A"
                            author_data["publications"].append(title)

                    results.append(author_data)
                except Exception as e:
                    print(f"Error parsing author: {e}")
                    continue
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

    return results

if __name__ == "__main__":
    import sys
    inst = sys.argv[1] if len(sys.argv) > 1 else "Université de Kinshasa"
    asyncio.run(get_scholar_authors(inst))
