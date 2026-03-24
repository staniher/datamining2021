# AgriVision AI – Système intelligent de prévision des prix agricoles

## 1. Contexte
Dans plusieurs villes africaines, les agriculteurs et commerçants manquent d'informations fiables sur l'évolution des prix du marché, provoquant des pertes économiques et une instabilité des prix. **AgriVision AI** utilise l'intelligence artificielle pour anticiper les prix agricoles et améliorer la prise de décision.

## 2. Objectif
Développer un système basé sur l'IA capable de :
* Collecter les prix agricoles locaux.
* Analyser les tendances historiques.
* Prédire les prix futurs des produits (Haricot, Maïs, Riz, Pomme de terre).

## 3. Fonctionnement du Système
Le système suit 4 étapes principales :
1. **Collecte des données** : Données générées via `generate_data.py`.
2. **Analyse des données** : Nettoyage et détection de tendances.
3. **Modèle d’IA** : Utilisation d'un modèle `RandomForestRegressor` pour la prévision.
4. **Diffusion de l'information** : Interface web responsive pour les utilisateurs.

## 4. Installation et Utilisation

### Prérequis
Assurez-vous d'avoir Python installé. Installez ensuite les dépendances nécessaires :
```bash
pip install -r requirements.txt
```

### Étape 1 : Génération des données
Générez le jeu de données historique (`agri_data.csv`) :
```bash
python generate_data.py
```

### Étape 2 : Entraînement du modèle
Entraînez le modèle d'IA et l'encodeur de produits :
```bash
python train_agri_model.py
```

### Étape 3 : Lancement de l'application
Démarrez le serveur Flask :
```bash
python app.py
```
Accédez à l'application via votre navigateur à l'adresse : `http://127.0.0.1:5000`

## 5. Architecture Technique
* **Backend** : Python / Flask
* **Machine Learning** : Scikit-learn (RandomForestRegressor)
* **Frontend** : HTML5 / CSS3 / Bootstrap 5 (Web Responsive)
* **Gestion des données** : Pandas / Numpy / Joblib

## 6. Vision Économique
Ce projet illustre comment l'IA peut créer un écosystème économique intelligent en permettant une meilleure planification des cultures et une stabilisation des revenus des agriculteurs.
