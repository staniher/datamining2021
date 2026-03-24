# Importation de la bibliothèque pandas pour la manipulation des données
import pandas as pd
# Importation de la bibliothèque numpy pour les opérations mathématiques
import numpy as np
# Importation de datetime pour manipuler les dates
from datetime import datetime, timedelta

# Initialisation d'un dictionnaire pour stocker les colonnes de notre jeu de données
data = {
    'Date': [], # Liste des dates de collecte
    'Produit': [], # Liste des noms des produits agricoles
    'Prix': [], # Liste des prix réels observés
    'Demande': [], # Niveau de demande (1: Faible, 2: Moyenne, 3: Forte)
    'Saison': [] # Saison (0: Sèche, 1: Pluvieuse)
}

# Définition de la liste des produits agricoles à inclure
produits = ['Haricot', 'Maïs', 'Riz', 'Pomme de terre']
# Définition de la date de début pour les données historiques (il y a un an)
start_date = datetime(2025, 1, 1)

# Boucle pour générer des données pour chaque produit
for produit in produits:
    # Pour chaque produit, nous générons 400 jours de données historiques
    for i in range(400):
        # Calcul de la date actuelle pour l'itération
        current_date = start_date + timedelta(days=i)
        # Ajout de la date à la liste
        data['Date'].append(current_date)
        # Ajout du nom du produit à la liste
        data['Produit'].append(produit)

        # Détermination de la saison en fonction du mois (Saison des pluies de Octobre à Mai)
        saison = 1 if current_date.month in [10, 11, 12, 1, 2, 3, 4, 5] else 0
        # Ajout de la saison à la liste
        data['Saison'].append(saison)

        # Génération aléatoire d'un niveau de demande entre 1 (Faible) et 3 (Forte)
        demande = np.random.randint(1, 4)
        # Ajout de la demande à la liste
        data['Demande'].append(demande)

        # Définition d'un prix de base différent pour chaque produit
        base_price = {'Haricot': 2000, 'Maïs': 1500, 'Riz': 3000, 'Pomme de terre': 2500}[produit]
        # Calcul du prix avec des variations saisonnières, de demande et un bruit aléatoire
        # Le prix augmente avec la demande et peut varier selon la saison
        prix = base_price + (demande * 200) + (saison * 300) + np.random.randint(-100, 101)
        # Ajout du prix calculé à la liste
        data['Prix'].append(prix)

# Création d'un DataFrame pandas à partir du dictionnaire de données
df = pd.DataFrame(data)
# Exportation du DataFrame vers un fichier CSV nommé 'agri_data.csv' sans index
df.to_csv('agri_data.csv', index=False)
# Affichage d'un message confirmant la réussite de l'opération
print("Jeu de données 'agri_data.csv' généré avec succès.")
