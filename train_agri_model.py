# Importation des bibliothèques nécessaires
import pandas as pd # Pour la manipulation des données
from sklearn.ensemble import RandomForestRegressor # Modèle de forêt aléatoire
from sklearn.preprocessing import LabelEncoder # Pour encoder les noms des produits
import joblib # Pour sauvegarder le modèle et l'encodeur

# Chargement du jeu de données généré précédemment
df = pd.read_csv('agri_data.csv')
# Conversion de la colonne 'Date' en type datetime pour faciliter la manipulation
df['Date'] = pd.to_datetime(df['Date'])

# Initialisation de l'encodeur pour transformer les noms des produits en nombres
le = LabelEncoder()
# Encodage de la colonne 'Produit' et stockage dans une nouvelle colonne 'Produit_Encoded'
df['Produit_Encoded'] = le.fit_transform(df['Produit'])

# Préparation des caractéristiques (X) et de la cible (y)
# Nous utilisons le produit, la demande et la saison pour prédire le prix
X = df[['Produit_Encoded', 'Demande', 'Saison']]
# La cible est le prix observé
y = df['Prix']

# Initialisation du modèle Random Forest avec 100 arbres
model = RandomForestRegressor(n_estimators=100, random_state=42)
# Entraînement du modèle sur l'ensemble des données
model.fit(X, y)

# Sauvegarde du modèle entraîné pour une utilisation ultérieure dans l'application web
joblib.dump(model, 'agri_model.joblib')
# Sauvegarde de l'encodeur de produits pour pouvoir transformer les entrées utilisateurs
joblib.dump(le, 'product_encoder.joblib')

# Affichage d'un message confirmant la fin de l'entraînement et de la sauvegarde
print("Modèle et encodeur entraînés et sauvegardés avec succès.")
