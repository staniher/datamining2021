
# 🇨🇩 Extracteur de Données Chercheurs RDC (Version Robuste)

Ce projet est une suite d'outils avancée pour extraire les informations des chercheurs congolais sur ResearchGate et Google Scholar, même en cas de blocage par les serveurs.

## 🚀 Comment l'utiliser sur Windows

### 1. Installation
Ouvrez votre terminal (CMD ou PowerShell) dans le dossier du projet :
```bash
pip install beautifulsoup4 pandas playwright playwright-stealth
playwright install chromium
```

### 2. Mode Automatique (Essai direct)
Le script tente d'abord d'accéder directement aux sites, puis bascule sur les "snippets" Google si l'accès est refusé.
```bash
python main_scraper.py
```

### 3. Mode Manuel (Recommandé pour contourner 100% des blocages)
Si vous voyez des messages "Bloqué par Cloudflare" ou "CAPTCHA" :
1. Ouvrez **Google Chrome** ou **Edge**.
2. Allez sur [ResearchGate](https://www.researchgate.net) ou [Google Scholar](https://scholar.google.com).
3. Faites votre recherche (ex: "Université de l'Assomption au Congo").
4. Si un Captcha s'affiche, résolvez-le.
5. Une fois la liste des chercheurs affichée, faites **Ctrl + S**.
6. Choisissez le type : **"Page Web, HTML uniquement"** et enregistrez le fichier (ex: `uac.html`).
7. Placez vos fichiers `.html` dans un dossier nommé `imports`.
8. Lancez l'analyse sur ce dossier :
   ```bash
   python main_scraper.py imports
   ```

## 📊 Résultats
Les données sont sauvegardées dans `chercheurs_rdc_dataset.csv`.
- **Nom** : Identité du chercheur.
- **Institution** : Affiliation détectée.
- **Plateforme** : Origine de la donnée.
- **Donnees_Extraites** : Liste des publications ou informations de profil.
- **Sentiment_Analyse** : Analyse automatique (Positif/Neutre/Négatif) basée sur les textes extraits.

## 🛠️ Structure technique
- `main_scraper.py` : Chef d'orchestre (Gère les modes direct, snippet et local).
- `scholar_scraper.py` / `researchgate_scraper.py` : Logique d'extraction spécifique.
- `google_snippet_scraper.py` : Solution de secours via Google Search.
- `social_searcher.py` : Analyse de sentiment en français.

**Note** : Pour des volumes massifs, il est conseillé de ne pas dépasser 3 institutions par heure en mode automatique pour éviter le bannissement de votre adresse IP.
