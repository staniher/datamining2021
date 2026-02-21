
import json
import urllib.parse

# Dictionnaire de sentiments étendu pour le français (mots-clés fréquents en recherche)
SENTIMENT_DICT = {
    # Positif
    "excellent": 1, "innovation": 1, "progrès": 1, "réussite": 1, "succès": 1,
    "développement": 1, "avancée": 1, "opportunité": 1, "collaboration": 1,
    "découverte": 1, "passion": 1, "espoir": 1, "impact": 1, "positif": 1,
    "recherche": 0.5, "science": 0.5, "contribution": 1, "amélioration": 1,
    # Négatif
    "difficile": -1, "manque": -1, "problème": -1, "crise": -1, "échec": -1,
    "limitation": -1, "obstacle": -1, "retard": -1, "insuffisant": -1,
    "pauvreté": -1, "maladie": -1, "souffrance": -1, "conflit": -1, "négatif": -1,
    "risque": -0.5, "défi": -0.5, "instabilité": -1, "préoccupation": -1
}

def get_sentiment(text):
    """
    Analyse de sentiment basée sur un dictionnaire pour le français.
    Retourne un score et une catégorie.
    """
    if not text or not isinstance(text, str):
        return "Neutral"

    score = 0
    words = text.lower().replace(".", "").replace(",", "").split()
    found_words = []

    for w in words:
        if w in SENTIMENT_DICT:
            score += SENTIMENT_DICT[w]
            found_words.append(w)

    if score > 0.5:
        return "Positive"
    elif score < -0.5:
        return "Negative"
    else:
        return "Neutral"

def generate_search_urls(researcher_name):
    """
    Génère des URLs de recherche pour Facebook et les Blogs.
    L'utilisateur peut cliquer sur ces liens pour trouver manuellement les informations
    ou les utiliser avec un service de scraping de recherche.
    """
    query_fb = f'"{researcher_name}" site:facebook.com'
    query_blog = f'"{researcher_name}" (blog OR wordpress OR blogspot)'

    base_url = "https://www.google.com/search?q="

    return {
        "facebook_search": base_url + urllib.parse.quote(query_fb),
        "blog_search": base_url + urllib.parse.quote(query_blog)
    }

def analyze_researcher_social(name, info_text):
    """
    Analyse globale d'un chercheur à partir de textes collectés.
    """
    sentiment = get_sentiment(info_text)
    search_links = generate_search_urls(name)

    return {
        "name": name,
        "sentiment_summary": sentiment,
        "search_links": search_links
    }

if __name__ == "__main__":
    test_name = "Raphael Tshimanga"
    test_text = "Ses recherches sur l'innovation et le développement durable dans le bassin du Congo sont un excellent exemple de réussite."

    result = analyze_researcher_social(test_name, test_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
