
import json
import urllib.parse

# Dictionnaire de sentiments étendu pour le français (mots-clés fréquents en recherche et social)
SENTIMENT_DICT = {
    # Positif
    "excellent": 1, "innovation": 1, "progrès": 1, "réussite": 1, "succès": 1,
    "développement": 1, "avancée": 1, "opportunité": 1, "collaboration": 1,
    "découverte": 1, "passion": 1, "espoir": 1, "impact": 1, "positif": 1,
    "recherche": 0.5, "science": 0.5, "contribution": 1, "amélioration": 1,
    "fructueux": 1, "pertinent": 1, "efficace": 1, "brillant": 1, "prometteur": 1,
    "qualité": 0.5, "important": 0.5, "bravo": 1, "félicitations": 1,
    "académique": 0.2, "connaissance": 0.5, "partage": 0.5, "avenir": 0.5,
    # Négatif
    "difficile": -1, "manque": -1, "problème": -1, "crise": -1, "échec": -1,
    "limitation": -1, "obstacle": -1, "retard": -1, "insuffisant": -1,
    "pauvreté": -1, "maladie": -1, "souffrance": -1, "conflit": -1, "négatif": -1,
    "risque": -0.5, "défi": -0.5, "instabilité": -1, "préoccupation": -1,
    "erreur": -1, "mauvais": -1, "faiblesse": -1, "urgent": -0.5, "danger": -1,
    "précaire": -1, "décevant": -1, "limité": -0.5, "corruption": -1, "guerre": -1
}

def get_sentiment(text):
    """
    Analyse de sentiment basée sur un dictionnaire pour le français.
    """
    if not text or not isinstance(text, str):
        return "Neutral"

    score = 0
    words = text.lower().replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace("(", "").replace(")", "").split()

    for w in words:
        if w in SENTIMENT_DICT:
            score += SENTIMENT_DICT[w]

    if score > 0.5:
        return "Positive"
    elif score < -0.5:
        return "Negative"
    else:
        return "Neutral"

def analyze_researcher_social(name, info_text):
    """
    Génère des liens de recherche sociale et analyse le sentiment.
    """
    sentiment = get_sentiment(info_text)

    # Construction des URLs de recherche ciblées
    query_fb = f'"{name}" site:facebook.com'
    query_blog = f'"{name}" (blog OR wordpress OR blogspot OR medium)'

    base_url = "https://www.google.com/search?q="

    return {
        "name": name,
        "sentiment_summary": sentiment,
        "search_links": {
            "facebook_search": base_url + urllib.parse.quote(query_fb),
            "blog_search": base_url + urllib.parse.quote(query_blog)
        }
    }
