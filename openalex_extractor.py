
import requests
import pandas as pd
import time
import json
from social_searcher import get_sentiment

# ------------------------
# CONFIGURATION
# ------------------------
BASE_URL_WORKS = "https://api.openalex.org/works"
BASE_URL_AUTHORS = "https://api.openalex.org/authors"
EMAIL = "votre_email@exemple.com"

def reconstruct_abstract(inverted_index):
    """
    Reconstruit le texte de l'abstract à partir de l'index inversé d'OpenAlex.
    """
    if not inverted_index:
        return ""
    word_index = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_index.append((pos, word))
    word_index.sort()
    return " ".join([word for pos, word in word_index])

def get_drc_works(max_works=1000):
    """
    Récupère les publications affiliées à la RDC directement.
    """
    all_works = []
    cursor = "*"
    count = 0
    print(f"Démarrage de l'extraction OpenAlex (Filtre: RDC)...")
    while cursor and count < max_works:
        params = {"filter": "institutions.country_code:CD", "per_page": 200, "cursor": cursor, "mailto": EMAIL}
        try:
            response = requests.get(BASE_URL_WORKS, params=params, timeout=30)
            if response.status_code != 200: break
            data = response.json()
            results = data.get("results", [])
            if not results: break
            for w in results:
                abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
                authors = []
                for auth in w.get("authorships", []):
                    is_cd = any(inst.get("country_code") == "CD" for inst in auth.get("institutions", []))
                    if is_cd: authors.append(auth.get("author", {}).get("display_name", "Inconnu"))
                sentiment = get_sentiment(abstract) if abstract else "N/A"
                all_works.append({
                    "Titre": w.get("title"), "Auteurs_RDC": ", ".join(authors), "Annee": w.get("publication_year"),
                    "DOI": w.get("doi"), "Abstract": abstract[:500] + "..." if abstract else "N/A",
                    "Sentiment": sentiment, "Citations": w.get("cited_by_count"), "Source": "OpenAlex"
                })
                count += 1
                if count >= max_works: break
            cursor = data.get("meta", {}).get("next_cursor")
            time.sleep(0.5)
        except: break
    return all_works

def search_authors_by_name(author_name):
    """
    Recherche des auteurs spécifiques par nom sur OpenAlex.
    """
    print(f"Recherche de l'auteur sur OpenAlex : {author_name}")
    params = {"search": author_name, "mailto": EMAIL}
    try:
        response = requests.get(BASE_URL_AUTHORS, params=params, timeout=30)
        if response.status_code != 200: return []
        data = response.json()
        authors = data.get("results", [])

        results = []
        for a in authors:
            # On vérifie si l'auteur a une affiliation RDC (facultatif mais recommandé pour filtrer)
            is_rdc = any(inst.get("country_code") == "CD" for inst in a.get("last_known_institutions", []))

            author_info = {
                "name": a.get("display_name"),
                "id": a.get("id"),
                "orcid": a.get("ids", {}).get("orcid"),
                "affiliation": (a.get("last_known_institutions") or [{}])[0].get("display_name", "N/A"),
                "is_rdc": is_rdc,
                "works_count": a.get("works_count", 0),
                "works_api_url": a.get("works_api_url")
            }
            results.append(author_info)
        return results
    except:
        return []

def get_author_works(works_api_url, max_works=10):
    """
    Récupère les travaux d'un auteur spécifique via son URL de travaux.
    """
    all_works = []
    try:
        response = requests.get(works_api_url, params={"per_page": max_works}, timeout=30)
        if response.status_code != 200: return []
        data = response.json()
        results = data.get("results", [])
        for w in results:
            abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
            all_works.append({
                "Titre": w.get("title"), "Annee": w.get("publication_year"),
                "DOI": w.get("doi"), "Abstract": abstract[:500] + "..." if abstract else "N/A",
                "Sentiment": get_sentiment(abstract) if abstract else "N/A",
                "Source": "OpenAlex Author Search"
            })
        return all_works
    except:
        return []

if __name__ == "__main__":
    test_author = "Nsenge Mpia Héritier"
    authors = search_authors_by_name(test_author)
    for a in authors:
        print(f"Trouvé: {a['name']} ({a['affiliation']})")
        if a['works_count'] > 0:
            works = get_author_works(a['works_api_url'])
            print(f"  {len(works)} travaux trouvés.")
