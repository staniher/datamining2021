
# 🇨🇩 Solution d'Extraction de Données Chercheurs RDC (Version Optmisée)

Ce projet a été mis à jour pour résoudre les problèmes de blocage massif rencontrés sur ResearchGate et Google Scholar en utilisant l'API officielle **OpenAlex**.

## 🛠️ Nouvelles Fonctionnalités

1.  **Extraction via OpenAlex (Recommandé)** : Utilise l'API officielle pour récupérer des milliers de publications de chercheurs congolais sans risque de blocage.
2.  **Reconstruction d'Abstracts** : Récupère et reconstruit les résumés des travaux pour une analyse de sentiment précise.
3.  **Système Hybride** : Combine l'API, le web scraping (avec mode furtif) et le fallback par snippets Google.
4.  **Mode Manuel** : Analyse toujours possible des fichiers HTML sauvegardés localement.

## 🚀 Utilisation Rapide

### 1. Installation
```bash
pip install requests beautifulsoup4 pandas playwright playwright-stealth
playwright install chromium
```

### 2. Lancer l'extraction optimisée
```bash
python main_scraper.py
```
Cela générera le fichier `chercheurs_rdc_dataset_final.csv` contenant les données d'OpenAlex et les éventuels résultats de web scraping.

## 📖 Guide de Survie Anti-Blocage

Si vous tenez absolument à utiliser ResearchGate/Scholar et que vous voyez des erreurs :
1.  **Utilisez OpenAlex** (par défaut dans le script) : c'est la source la plus riche et la plus stable.
2.  **Mode HTML Local** :
    - Allez sur ResearchGate dans votre navigateur.
    - Faites votre recherche.
    - Enregistrez la page (**Ctrl+S**, mode "HTML uniquement").
    - Lancez : `python main_scraper.py chemin/vers/votre_fichier.html`

## 📊 Analyse de Sentiment
L'outil analyse automatiquement le ton des abstracts et des descriptions extraites en utilisant un dictionnaire spécialisé pour la recherche scientifique en français.

## 📁 Fichiers du Projet
- `main_scraper.py` : Point d'entrée principal.
- `openalex_extractor.py` : Extraction via API officielle.
- `scholar_scraper.py` / `researchgate_scraper.py` : Scrapers web.
- `social_searcher.py` : Module de sentiment et liens sociaux.
- `google_snippet_scraper.py` : Fallback via Google Search.
