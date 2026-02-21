
import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def get_researchgate_authors(institution, max_authors=5):
    """
    Scrapes ResearchGate for authors affiliated with a specific institution.
    Attempts multiple strategies: Search URL, Direct URL, and Search Page Interaction.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Utilisation de cookies ou d'un contexte plus naturel peut aider
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        # Stratégie 1: URL directe des membres (si fournie ou construite)
        if institution.startswith("http"):
            url = institution
            if not url.endswith("/members"):
                url = url.rstrip("/") + "/members"
        else:
            # Encodage manuel pour éviter les problèmes de caractères spéciaux
            q = urllib.parse.quote(institution)
            url = f"https://www.researchgate.net/search/authors?q={q}"

        print(f"Tentative ResearchGate : {url}")

        try:
            # Navigation avec délai d'attente généreux
            await page.goto(url, wait_until="load", timeout=90000)

            # Attente pour laisser passer d'éventuels scripts de vérification
            await asyncio.sleep(random.uniform(5, 8))

            content = await page.content()

            # Détection de blocage
            if "security check" in content.lower() or "cloudflare" in content.lower() or "unusual activity" in content.lower():
                print("Warning: ResearchGate bloqué (Bot detection).")
                # Ici on pourrait tenter de résoudre un captcha si on avait un service tiers
                return []

            soup = BeautifulSoup(content, "html.parser")

            # Recherche des éléments de chercheur (plusieurs sélecteurs possibles)
            authors = soup.find_all("div", class_="nova-legacy-v-person-item") or \
                      soup.find_all("div", class_="nova-v-person-item") or \
                      soup.find_all("div", class_="nova-legacy-c-card") or \
                      soup.select(".nova-v-person-item__body")

            if not authors:
                print("Aucun chercheur trouvé directement sur la page. Tentative de défilement...")
                # Essayer de scroller pour charger du contenu dynamique
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                authors = soup.find_all("div", class_="nova-legacy-v-person-item") or \
                          soup.select(".nova-v-person-item__body")

            for author in authors[:max_authors]:
                try:
                    # Extraction du nom et du lien
                    link_tag = author.find("a", href=True)
                    if not link_tag: continue

                    name = link_tag.get_text().strip()
                    href = link_tag["href"]
                    link = "https://www.researchgate.net/" + href if not href.startswith("http") else href

                    # Détails (département, etc.)
                    details = author.find_all("li")
                    info = [d.get_text().strip() for d in details if len(d.get_text().strip()) > 2]

                    results.append({
                        "name": name,
                        "link": link,
                        "info": info,
                        "source": "ResearchGate"
                    })
                except Exception as e:
                    print(f"Erreur sur un item ResearchGate : {e}")
                    continue
        except Exception as e:
            print(f"Erreur de connexion ResearchGate : {e}")
        finally:
            await browser.close()

    return results

if __name__ == "__main__":
    import sys
    inst = sys.argv[1] if len(sys.argv) > 1 else "https://www.researchgate.net/institution/Universite-de-lAssomption-au-Congo"
    asyncio.run(get_researchgate_authors(inst))
