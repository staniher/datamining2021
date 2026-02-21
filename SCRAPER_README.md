
# 🇨🇩 Extracteur de Données Chercheurs RDC (Version Avancée)

Ce projet permet de collecter massivement des données sur les chercheurs congolais, avec un focus particulier sur les chercheurs du Nord-Kivu et de Butembo (UAC, UCG, etc.).

## 🌟 Nouveautés

1.  **Recherche par Nom** : Vous pouvez désormais cibler des chercheurs spécifiques par leur nom (ex: "Nsenge Mpia Héritier").
2.  **Base Institutionnelle Élargie** : Ajout d'institutions comme l'UCG (Graben), l'ISIG, l'ULPGL, et l'UNILUK pour mieux couvrir l'est de la RDC.
3.  **Extraction Hybride (API + Web)** : Utilise l'API OpenAlex (fiable) et le web scraping (Scholar/ResearchGate) pour une couverture maximale.

## 🚀 Utilisation

### Rechercher des chercheurs spécifiques
Vous pouvez passer les noms des chercheurs directement en argument :
```bash
python main_scraper.py "Nsenge Mpia Héritier" "Kambale Kasambya Moïse"
```

### Extraction automatique globale
Si vous ne passez pas d'arguments, le script utilisera la liste par défaut :
```bash
python main_scraper.py
```

### Mode manuel (Contre les blocages)
Si un site est bloqué, enregistrez la page en HTML (**Ctrl+S**) et passez le fichier :
```bash
python main_scraper.py mon_fichier.html
```

## 📊 Dataset Final
Les résultats sont regroupés dans `chercheurs_rdc_dataset_final.csv` avec :
- **Nom** du chercheur
- **Institution**
- **Plateforme** source
- **Lien** (DOI ou Profil)
- **Donnees_Extraites** (Abstracts, publications ou infos de profil)
- **Sentiment_Analyse** (Analyse automatique du ton en français)

## 📁 Structure
- `main_scraper.py` : Point d'entrée.
- `openalex_extractor.py` : Interface avec l'API OpenAlex.
- `scholar_scraper.py` / `researchgate_scraper.py` : Scrapers web furtifs.
- `social_searcher.py` : Dictionnaire de sentiment français amélioré.
