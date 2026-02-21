
# Outil de Collecte de Données Chercheurs RDC

Ce projet permet d'extraire des données sur les chercheurs congolais pour l'analyse de sentiment.

## Résolution des Problèmes de Blocage (CAPTCHA / Cloudflare)

Google Scholar et ResearchGate ont des protections anti-bot strictes. Si vous recevez des messages "Bloqué" ou si aucune donnée n'est extraite, voici les solutions :

### 1. Utilisation de fichiers HTML locaux (Mode Manuel)
C'est la méthode la plus fiable si l'outil est bloqué :
- Allez sur Google Scholar ou ResearchGate dans votre navigateur habituel.
- Faites votre recherche (ex: "Université de l'Assomption au Congo").
- Si un CAPTCHA apparaît, résolvez-le manuellement.
- Sauvegardez la page au format HTML (Ctrl+S -> "Page Web, HTML uniquement").
- Lancez le script en passant le fichier en argument :
  ```bash
  python main_scraper.py mon_fichier_scholar.html mon_fichier_rg.html
  ```

### 2. Délai et Rotation
Les scripts intègrent des délais aléatoires et une rotation de User-Agent. Évitez de lancer l'extraction trop fréquemment depuis la même adresse IP.

### 3. Recherche par Snippets
Si le scraping direct échoue, le script tente automatiquement de récupérer les informations depuis les résultats de recherche Google (snippets), ce qui est moins souvent bloqué.

## Utilisation Classique

```bash
# Installer les dépendances
pip install beautifulsoup4 pandas playwright playwright-stealth
playwright install chromium

# Lancer l'extraction automatique
python main_scraper.py
```

Les résultats sont sauvegardés dans `chercheurs_rdc_dataset.csv`.
