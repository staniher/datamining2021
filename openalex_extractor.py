
import requests
import pandas as pd
import time
import json
from social_searcher import get_sentiment

# ------------------------
# CONFIGURATION
# ------------------------
BASE_URL = "https://api.openalex.org/works"
# Email recommandé par OpenAlex pour accéder au 'polite pool' (plus rapide)
EMAIL = "votre_email@exemple.com"

def reconstruct_abstract(inverted_index):
    """
    Reconstruit le texte de l'abstract à partir de l'index inversé d'OpenAlex.
    """
    if not inverted_index:
        return ""

    # Création d'une liste (position, mot)
    word_index = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_index.append((pos, word))

    # Tri par position et jonction
    word_index.sort()
    return " ".join([word for pos, word in word_index])

def get_drc_works(max_works=1000):
    """
    Récupère les publications affiliées à la RDC directement.
    C'est beaucoup plus rapide que de boucler par auteur.
    """
    all_works = []
    cursor = "*"
    count = 0

    print(f"Démarrage de l'extraction OpenAlex (Filtre: RDC)...")

    while cursor and count < max_works:
        params = {
            "filter": "institutions.country_code:CD",
            "per_page": 200,
            "cursor": cursor,
            "mailto": EMAIL
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
            if response.status_code != 200:
                print(f"Erreur API OpenAlex: {response.status_code}")
                break

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for w in results:
                # Reconstruction de l'abstract
                abstract = reconstruct_abstract(w.get("abstract_inverted_index"))

                # Extraction des auteurs congolais
                authors = []
                for auth in w.get("authorships", []):
                    # On vérifie si l'auteur a une institution en RDC
                    is_cd = False
                    for inst in auth.get("institutions", []):
                        if inst.get("country_code") == "CD":
                            is_cd = True
                            break
                    if is_cd:
                        authors.append(auth.get("author", {}).get("display_name", "Inconnu"))

                # Analyse de sentiment sur l'abstract
                sentiment = get_sentiment(abstract) if abstract else "N/A"

                all_works.append({
                    "Titre": w.get("title"),
                    "Auteurs_RDC": ", ".join(authors),
                    "Annee": w.get("publication_year"),
                    "DOI": w.get("doi"),
                    "Abstract": abstract[:500] + "..." if abstract else "N/A",
                    "Sentiment": sentiment,
                    "Citations": w.get("cited_by_count"),
                    "Source": "OpenAlex"
                })
                count += 1
                if count >= max_works: break

            print(f"{count} publications récupérées...")

            # Mise à jour du curseur pour la page suivante
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor: break

            time.sleep(0.5) # Délai de courtoisie

        except Exception as e:
            print(f"Exception lors de l'extraction : {e}")
            break

    return all_works

if __name__ == "__main__":
    # Test rapide
    works = get_drc_works(max_works=50)
    df = pd.DataFrame(works)
    df.to_csv("openalex_rdc_test.csv", index=False, encoding="utf-8-sig")
    print("Test terminé. Fichier 'openalex_rdc_test.csv' généré.")
