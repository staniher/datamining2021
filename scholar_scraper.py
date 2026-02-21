
import asyncio
import json
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def get_scholar_authors(institution, max_authors=5):
    """
    Scrapes Google Scholar for authors.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        # Nettoyage du nom pour la recherche
        clean_name = institution.replace("Université", "").replace("l'", "").strip()
        q = urllib.parse.quote(f'"{institution}"')
        url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={q}&hl=fr"

        print(f"Tentative Scholar : {url}")

        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(3, 6))

            content = await page.content()
            if "not a robot" in content.lower() or "captcha" in content.lower():
                print(f"Warning: CAPTCHA Scholar pour {institution}")
                return []

            soup = BeautifulSoup(content, "html.parser")
            authors = soup.find_all("div", class_="gsc_1usr")

            if not authors:
                # Essayer une recherche moins restrictive
                print("Aucun résultat exact, tentative de recherche large...")
                q_wide = urllib.parse.quote(clean_name)
                url_wide = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={q_wide}&hl=fr"
                await page.goto(url_wide, wait_until="load")
                await asyncio.sleep(3)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                authors = soup.find_all("div", class_="gsc_1usr")

            for author_div in authors[:max_authors]:
                try:
                    name_tag = author_div.find("h3", class_="gs_ai_name")
                    name = name_tag.get_text().strip() if name_tag else "N/A"
                    link_suffix = name_tag.find("a")["href"] if name_tag and name_tag.find("a") else None
                    link = "https://scholar.google.com" + link_suffix if link_suffix else None

                    author_data = {
                        "name": name,
                        "link": link,
                        "affiliation": author_div.find("div", class_="gs_ai_aff").get_text().strip() if author_div.find("div", class_="gs_ai_aff") else "N/A",
                        "interests": [t.get_text().strip() for t in author_div.find_all("a", class_="gs_ai_one_int")],
                        "publications": [],
                        "source": "Google Scholar"
                    }

                    if link:
                        await page.goto(link, wait_until="load", timeout=30000)
                        await asyncio.sleep(2)
                        p_content = await page.content()
                        psoup = BeautifulSoup(p_content, "html.parser")
                        pub_rows = psoup.find_all("tr", class_="gsc_a_tr")
                        for row in pub_rows[:5]:
                            title_tag = row.find("a", class_="gsc_a_at")
                            title = title_tag.get_text().strip() if title_tag else "N/A"
                            author_data["publications"].append(title)

                    results.append(author_data)
                except Exception as e:
                    print(f"Erreur Scholar parsing : {e}")
                    continue
        except Exception as e:
            print(f"Erreur Scholar connexion : {e}")
        finally:
            await browser.close()

    return results
