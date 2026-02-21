
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

async def get_researchgate_authors(institution, max_authors=10, local_file=None):
    """
    Récupère les chercheurs de ResearchGate.
    """
    if local_file:
        print(f"Extraction du fichier local ResearchGate : {local_file}")
        with open(local_file, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_rg_authors(content, max_authors)

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await apply_stealth_simple(page)

        # Si lien direct, on l'utilise, sinon recherche
        if institution.startswith("http"):
            url = institution
            if "/institution/" in url and not url.endswith("/members"):
                url = url.rstrip("/") + "/members"
        else:
            url = f"https://www.researchgate.net/search/authors?q={urllib.parse.quote(institution)}"

        print(f"Extraction ResearchGate en ligne : {url}")

        try:
            await page.goto(url, wait_until="load", timeout=90000)
            await asyncio.sleep(random.uniform(5, 8))
            content = await page.content()
            if "security check" in content.lower() or "cloudflare" in content.lower():
                print(f"Bloqué par Cloudflare ResearchGate pour {institution}.")
                return []
            results = parse_rg_authors(content, max_authors)
        except Exception as e:
            print(f"Erreur ResearchGate ({institution}) : {e}")
        finally:
            await browser.close()
    return results

def parse_rg_authors(html, max_authors):
    results = []
    soup = BeautifulSoup(html, "html.parser")

    # Tentative avec plusieurs types de structures (Recherche vs Institution)
    # 1. Structure de recherche classique
    authors = soup.find_all("div", class_="nova-legacy-v-person-item") or \
              soup.find_all("div", class_="nova-v-person-item")

    # 2. Structure spécifique de l'onglet 'Members'
    if not authors:
        authors = soup.find_all("div", class_="nova-legacy-c-card") or \
                  soup.select("div[class*='person-item']")

    if not authors:
        # Recherche par lien de profil
        links = soup.find_all("a", href=True)
        profile_links = []
        for l in links:
            if "/profile/" in l['href'] and l.get_text().strip():
                # On évite les doublons et les petits textes
                if len(l.get_text().strip()) > 3:
                    profile_links.append(l)

        for l in profile_links[:max_authors]:
            name = l.get_text().strip()
            href = l["href"]
            link = "https://www.researchgate.net/" + href if not href.startswith("http") else href
            results.append({
                "name": name, "link": link, "info": ["Chercheur identifié"], "source": "ResearchGate"
            })
        return results

    for author in authors[:max_authors]:
        try:
            link_tag = author.find("a", href=True)
            if not link_tag: continue

            name = link_tag.get_text().strip()
            if not name or len(name) < 2:
                # Essayer un autre tag pour le nom
                name_tag = author.find("div", class_="nova-legacy-v-person-item__title")
                name = name_tag.get_text().strip() if name_tag else "Chercheur Inconnu"

            href = link_tag["href"]
            link = "https://www.researchgate.net/" + href if not href.startswith("http") else href

            # Récupération des infos additionnelles (département, stats)
            details = author.find_all("li")
            info = [d.get_text().strip() for d in details if len(d.get_text().strip()) > 2]

            if name and name != "Chercheur Inconnu":
                results.append({
                    "name": name, "link": link, "info": info, "source": "ResearchGate"
                })
        except: continue
    return results

if __name__ == "__main__":
    import sys
    inst = sys.argv[1] if len(sys.argv) > 1 else "Université de Kinshasa"
    asyncio.run(get_researchgate_authors(inst))
