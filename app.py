from flask import Flask, request, render_template # Importation des bibliothèques Flask pour le serveur web
import joblib # Importation de joblib pour charger notre modèle d'IA et l'encodeur
import numpy as np # Importation de numpy pour la manipulation des tableaux de données
import pandas as pd # Importation de pandas pour la manipulation des séries temporelles
from datetime import datetime # Importation de datetime pour gérer les dates

app = Flask(__name__) # Initialisation de l'application Flask

@app.route('/') # Définition de la route principale pour afficher la page d'accueil
def home(): # Fonction pour gérer l'affichage de la page d'accueil
    return render_template('index.html') # Retourne le template 'index.html' du tableau de bord

@app.route('/predict', methods=['POST']) # Définition de la route pour effectuer les prédictions
def predict(): # Fonction pour gérer le processus de prédiction
    model = joblib.load('agri_model.joblib') # Chargement du modèle Random Forest sauvegardé
    le = joblib.load('product_encoder.joblib') # Chargement de l'encodeur de produits sauvegardé

    produit_nom = request.form.get('produit') # Récupération du nom du produit agricole du formulaire
    demande = int(request.form.get('demande')) # Récupération et conversion du niveau de demande
    saison = int(request.form.get('saison')) # Récupération et conversion de la saison actuelle
    
    try: # Début du bloc de capture d'erreurs pour la transformation
        produit_encoded = le.transform([produit_nom])[0] # Transformation du nom du produit en valeur numérique
    except Exception as e: # Capture de toute exception lors de la transformation
        return render_template('index.html', prediction_text="Erreur d'encodage.") # Retourne une erreur en cas de problème
    
    features = np.array([[produit_encoded, demande, saison]]) # Préparation du vecteur de caractéristiques pour l'IA
    
    prediction = model.predict(features)[0] # Utilisation du modèle IA pour prédire le prix futur
    
    prix_formate = "{:.2f}".format(prediction) # Formatage du prix prédit avec deux chiffres après la virgule

    chaine_prediction = f"Le prix prédit pour le {produit_nom} est de {prix_formate} FC." # Préparation du message final

    return render_template('index.html', prediction_text=chaine_prediction) # Retourne la page avec le résultat de prédiction

if __name__ == "__main__": # Vérification si le script est exécuté directement
    app.run(debug=True) # Lancement de l'application Flask avec le mode débug activé
