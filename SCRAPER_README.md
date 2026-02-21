
# Analyse des Chercheurs Congolais - Outil de Scraping et Sentiment

Ce projet est conçu pour collecter des données sur les chercheurs affiliés aux institutions de la RD Congo et analyser le sentiment associé à leurs publications et profils.

## Fonctionnalités

- **Google Scholar Scraper** : Récupère les noms, affiliations, intérêts et publications récentes.
- **ResearchGate Scraper** : Collecte les informations de profil public, supportant les liens directs vers les institutions.
- **Social Media Linker** : Génère des URLs de recherche ciblées pour Facebook et les Blogs.
- **Analyse de Sentiment** : Évalue le ton (Positif/Négatif/Neutre) des textes en français (recherche et publications).
- **Export Dataset** : Sauvegarde les résultats dans un fichier CSV structuré.

## Structure du Code

- `main_scraper.py` : Point d'entrée principal qui orchestre la collecte.
- `scholar_scraper.py` : Logique de scraping pour Google Scholar.
- `researchgate_scraper.py` : Logique de scraping pour ResearchGate.
- `social_searcher.py` : Analyse de sentiment et liens sociaux.
- `blog_scraper.py` : Outil pour extraire du texte de blogs spécifiques.
- `institutions.json` : Base de données des institutions congolaises (incluant l'UAC).

## Utilisation

1. **Installer les dépendances** :
   ```bash
   pip install beautifulsoup4 pandas playwright
   playwright install chromium
   ```

2. **Lancer l'analyse globale** :
   ```bash
   python main_scraper.py
   ```
   Les résultats seront sauvegardés dans `chercheurs_rdc_dataset.csv`.

## Note Spéciale : Université de l'Assomption au Congo (UAC)

Pour l'UAC, un dataset pré-extrait est fourni dans `chercheurs_uac_dataset.csv` en raison des protections anti-bot strictes sur ResearchGate. Le script `main_scraper.py` est configuré pour tenter d'extraire des données fraîches en utilisant le lien direct fourni.

## Éthique et Limitations

- **Bot Detection** : Google Scholar et ResearchGate utilisent des CAPTCHAs et Cloudflare. Les scripts incluent des délais, mais l'utilisation de proxies est recommandée pour des volumes importants.
- **Analyse** : L'analyse de sentiment est basée sur un dictionnaire académique français.
