
# Analyse des Chercheurs Congolais - Outil de Scraping et Sentiment

Ce projet est conçu pour collecter des données sur les chercheurs affiliés aux institutions de la RD Congo et analyser le sentiment associé à leurs publications et profils.

## Fonctionnalités

- **Google Scholar Scraper** : Récupère les noms, affiliations et centres d'intérêt.
- **ResearchGate Scraper** : Collecte les informations de profil public.
- **Social Media Linker** : Génère des URLs de recherche ciblées pour Facebook et les Blogs.
- **Analyse de Sentiment** : Évalue le ton (Positif/Négatif/Neutre) des textes en français.

## Structure du Code

- `main_scraper.py` : Point d'entrée principal.
- `scholar_scraper.py` : Logique de scraping pour Google Scholar.
- `researchgate_scraper.py` : Logique de scraping pour ResearchGate.
- `social_searcher.py` : Analyse de sentiment et liens sociaux.
- `institutions.json` : Base de données des institutions congolaises.

## Utilisation

1. **Installer les dépendances** :
   ```bash
   pip install beautifulsoup4 pandas playwright
   playwright install chromium
   ```

2. **Lancer l'analyse** :
   ```bash
   python main_scraper.py "Université de Kinshasa"
   ```

## Éthique et Limitations

- **Respect des ToS** : Les scripts utilisent des délais pour respecter les serveurs. Une utilisation abusive peut mener à un bannissement d'IP.
- **Sentiment** : L'analyse est basée sur un dictionnaire. Pour plus de précision, envisagez d'utiliser un modèle comme CamemBERT.
- **Facebook** : En raison des restrictions strictes de Facebook, nous fournissons des liens de recherche plutôt qu'un scraping direct pour éviter les blocages de compte.
