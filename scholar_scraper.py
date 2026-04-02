
import asyncio
import json
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

async def apply_stealth_simple(page):
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => False
        });
    """)

async def get_scholar_authors(institution, max_authors=10, local_file=None):
    """
    Récupère les auteurs de Google Scholar.
    """
    if local_file:
        print(f"Extraction du fichier local Scholar : {local_file}")
        with open(local_file, "r", encoding="utf-8") as f:
            content = f.read()
        return await parse_scholar_authors(content, max_authors)

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await apply_stealth_simple(page)

        q = urllib.parse.quote(f'"{institution}"')
        url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={q}&hl=fr"
        print(f"Extraction Scholar en ligne : {institution}")

        try:
            await page.goto(url, wait_until="load", timeout=90000)
            await asyncio.sleep(random.uniform(4, 7))
            content = await page.content()
            if "captcha" in content.lower() or "not a robot" in content.lower():
                print(f"Bloqué par CAPTCHA Scholar pour {institution}.")
                return []
            results = await parse_scholar_authors(content, max_authors, page)
        except Exception as e:
            print(f"Erreur Scholar ({institution}) : {e}")
        finally:
            await browser.close()
    return results

async def parse_scholar_authors(html, max_authors, page=None):
    results = []
    soup = BeautifulSoup(html, "html.parser")
    # Liste des auteurs sur la page de recherche
    authors = soup.find_all("div", class_="gsc_1usr")

    for author_div in authors[:max_authors]:
        try:
            name_tag = author_div.find("h3", class_="gs_ai_name")
            if not name_tag: continue

            name = name_tag.get_text().strip()
            link_suffix = name_tag.find("a")["href"] if name_tag.find("a") else None
            link = "https://scholar.google.com" + link_suffix if link_suffix else "N/A"

            aff_tag = author_div.find("div", class_="gs_ai_aff")
            affiliation = aff_tag.get_text().strip() if aff_tag else "N/A"

            interests_tags = author_div.find_all("a", class_="gs_ai_one_int")
            interests = [t.get_text().strip() for t in interests_tags]

            author_data = {
                "name": name,
                "link": link,
                "affiliation": affiliation,
                "interests": interests,
                "publications": [],
                "source": "Google Scholar"
            }

            # On ne tente d'accéder aux publications que si on est en mode "live"
            # et que la page n'est pas déjà bloquée
            if page and link != "N/A":
                try:
                    await page.goto(link, wait_until="load", timeout=20000)
                    await asyncio.sleep(random.uniform(1, 3))
                    p_content = await page.content()
                    if "captcha" not in p_content.lower():
                        psoup = BeautifulSoup(p_content, "html.parser")
                        for row in psoup.find_all("tr", class_="gsc_a_tr")[:5]:
                            atag = row.find("a", class_="gsc_a_at")
                            if atag: author_data["publications"].append(atag.get_text().strip())
                except:
                    pass

            results.append(author_data)
        except Exception as e:
            print(f"Erreur lors du parsing d'un chercheur Scholar : {e}")
            continue
    return results
