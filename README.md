# Système de Gestion des Malades - Hôpital Université Shalom de Bunia

Ce projet est un système complet de gestion des patients développé pour l'Hôpital de l'Université Shalom de Bunia. Il intègre une intelligence artificielle pour prédire la date de sortie des patients en fonction de leur profil clinique.

## Fonctionnalités
- **Enregistrement des patients** : Formulaire complet pour saisir les données des malades.
- **Prédiction IA** : Estimation de la date de sortie basée sur un modèle de Machine Learning (Extra Trees Regressor).
- **Tableau de Bord** : Statistiques en temps réel sur l'activité hospitalière.
- **Gestion CRUD** : Possibilité de lister, visualiser et supprimer les dossiers des patients.
- **Base de données robuste** : Utilisation de SQLite avec SQLAlchemy.

## Technologies Utilisées
- **Backend** : Flask (Python)
- **Base de données** : Flask-SQLAlchemy (SQLite)
- **IA/ML** : Scikit-learn, Pandas, Numpy, Joblib
- **Frontend** : HTML5, CSS3 (Bootstrap), Jinja2
- **Tests** : Pytest

## Structure du Projet
- `app.py` : Cœur de l'application Flask et définition des modèles.
- `ModelL2CSI2021.ml` : Modèle IA entraîné pour la prédiction.
- `templates/` : Fichiers HTML pour l'interface utilisateur.
- `static/` : Fichiers CSS, JS et polices.
- `tests/` : Suite de tests logiciels.

## Installation et Exécution

1. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt Flask-SQLAlchemy pytest
   ```

2. **Lancer l'application** :
   ```bash
   python app.py
   ```
   L'application sera accessible sur `http://127.0.0.1:5000`.

3. **Exécuter les tests** :
   ```bash
   pytest
   ```

## Auteur
Développé en tant qu'expert en Génie Logiciel et IA.
