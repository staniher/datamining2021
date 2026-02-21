
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
    Extrait les informations des chercheurs depuis les snippets Google.
    C'est la méthode de secours la plus robuste contre les blocages.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        query = f'site:{platform} "{institution}"'
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=fr"
        print(f"Fallback Google ({platform}) : {institution}")

        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(4, 7))

            content = await page.content()
            if "not a robot" in content.lower() or "captcha" in content.lower():
                print("Attention : Google Search a également détecté un robot.")
                return []

            soup = BeautifulSoup(content, "html.parser")

            search_results = soup.select(".g") or soup.select("div[data-sokoban-container]") or soup.select(".MjjYud")

            for res in search_results:
                try:
                    title_tag = res.find("h3") or res.select_one(".LC20lb")
                    link_tag = res.find("a", href=True)
                    snippet_tag = res.select_one(".VwiC3b") or res.select_one(".st")

                    if not title_tag or not link_tag: continue

                    name_raw = title_tag.get_text()
                    name = name_raw.split("|")[0].split("-")[0].split("—")[0].strip()
                    for suffix in ["ResearchGate", "Google Scholar", "Citations", "Profil"]:
                        name = name.replace(suffix, "").strip()

                    link = link_tag["href"]
                    if "google.com" in link and "/url?q=" not in link: continue

                    if "/url?q=" in link:
                        link = link.split("/url?q=")[1].split("&")[0]
                        link = urllib.parse.unquote(link)

                    snippet = snippet_tag.get_text().strip() if snippet_tag else "Pas de description."

                    if name and len(name) > 3:
                        results.append({
                            "name": name, "link": link, "snippet": snippet,
                            "source": f"Google Snippet ({platform})"
                        })

                    if len(results) >= max_results: break
                except: continue

        except Exception as e:
            print(f"Erreur recherche Google : {e}")
        finally:
            await browser.close()

    return results
