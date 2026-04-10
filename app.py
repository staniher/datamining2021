from flask import Flask, request, render_template, redirect, url_for # Importation des modules Flask nécessaires
from flask_sqlalchemy import SQLAlchemy # Importation de SQLAlchemy pour la gestion de la base de données
import numpy as np # Importation de numpy pour les calculs numériques
import joblib # Importation de joblib pour charger le modèle ML
import pandas as pd # Importation de pandas pour la manipulation des données
from datetime import datetime, timedelta, UTC # Importation pour la gestion des dates
import os # Importation pour les opérations sur le système de fichiers

app = Flask(__name__) # Initialisation de l'application Flask

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hopital_shalom.db' # Chemin vers la base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Désactivation du suivi des modifications pour économiser des ressources
db = SQLAlchemy(app) # Initialisation de l'objet SQLAlchemy

# Chargement du modèle au démarrage pour de meilleures performances
MODEL_PATH = 'ModelL2CSI2021.ml'
ML_MODEL = None
if os.path.exists(MODEL_PATH):
    ML_MODEL = joblib.load(MODEL_PATH)

# Définition du modèle Patient pour la base de données
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Identifiant unique du patient
    nom = db.Column(db.String(100), nullable=False) # Nom du patient
    genre = db.Column(db.Integer, nullable=False) # Genre (1 pour M, 0 pour F)
    age = db.Column(db.Float, nullable=False) # Âge du patient
    maladie = db.Column(db.Integer, nullable=False) # Code de la maladie
    service = db.Column(db.Integer, nullable=False) # Code du service
    date_entree = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC)) # Date d'entrée
    date_sortie_predite = db.Column(db.DateTime) # Date de sortie prédite par l'IA

# Création de la base de données si elle n'existe pas
with app.app_context():
    db.create_all() # Création des tables

@app.route('/')
# Cette fonction retourne la page d'accueil avec le formulaire d'enregistrement
def home():
    return render_template('index.html') # Rendu de la page d'accueil

@app.route('/patients')
# Cette fonction affiche la liste complète des patients
def list_patients():
    patients = Patient.query.all() # Récupération de tous les patients
    return render_template('list_patients.html', patients=patients) # Rendu de la liste

@app.route('/dashboard')
# Cette fonction affiche les statistiques de l'hôpital
def dashboard():
    total_patients = Patient.query.count() # Nombre total de patients
    aujourdhui = datetime.now(UTC).date()
    sorties_aujourdhui = Patient.query.filter(db.func.date(Patient.date_sortie_predite) == aujourdhui).count()

    # Trouver le service le plus actif
    service_stats = db.session.query(Patient.service, db.func.count(Patient.service)).group_by(Patient.service).all()
    service_actif = "N/A"
    if service_stats:
        max_service_code = max(service_stats, key=lambda x: x[1])[0]
        services = {0: "Pédiatrie", 1: "Hospitalisation", 2: "Gynécologie", 3: "Néonatologie"}
        service_actif = services.get(max_service_code, "N/A")

    return render_template('dashboard.html', total_patients=total_patients, sorties_aujourdhui=sorties_aujourdhui, service_actif=service_actif)

@app.route('/predict', methods=['GET', 'POST']) # Route pour la prédiction et l'enregistrement
def predict():
    if request.method == 'POST': # Si le formulaire est soumis
        try:
            # Récupération et validation des données du formulaire
            nom = request.form.get('nom')
            genre = int(request.form.get('genre'))
            age = float(request.form.get('age'))
            maladie = int(request.form.get('maladie'))
            service = int(request.form.get('service'))
            date_hospitalisation = request.form.get('date')

            if not ML_MODEL:
                return render_template('index.html', prediction_text="Erreur: Modèle IA non chargé.")

            # Préparation des données pour le modèle
            features_model = np.array([[genre, age, maladie, service]]).reshape(1, 4)

            # Prédiction du nombre de jours d'hospitalisation
            prediction = ML_MODEL.predict(features_model)[0]

            # Calcul de la date de sortie prédite
            date_entree_hopital = pd.to_datetime(date_hospitalisation)
            date_sortie_hopital = date_entree_hopital + timedelta(days=int(prediction))

            # Enregistrement du patient dans la base de données
            nouveau_patient = Patient(
                nom=nom,
                genre=genre,
                age=age,
                maladie=maladie,
                service=service,
                date_entree=date_entree_hopital,
                date_sortie_predite=date_sortie_hopital
            )
            db.session.add(nouveau_patient)
            db.session.commit()

            # Dictionnaires pour la conversion en français
            jours = {
                'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
                'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
            }
            mois = {
                'January': 'Janvier', 'February': 'Février', 'March': 'Mars', 'April': 'Avril',
                'May': 'Mai', 'June': 'Juin', 'July': 'Juillet', 'August': 'Août',
                'September': 'Septembre', 'October': 'Octobre', 'November': 'Novembre', 'December': 'Décembre'
            }

            # Préparation de la chaîne de retour pour l'affichage en français
            jour_semaine_sortie = jours.get(date_sortie_hopital.day_name(), date_sortie_hopital.day_name())
            nom_mois_sortie = mois.get(date_sortie_hopital.month_name(), date_sortie_hopital.month_name())
            annee_sortie = date_sortie_hopital.year
            jour_date_sortie = date_sortie_hopital.day
            chaine_prediction = f"a la probabilité de sortir le {jour_semaine_sortie}, {jour_date_sortie} {nom_mois_sortie} {annee_sortie}"

            return render_template('index.html', prediction_text=f'Le Patient {nom} {chaine_prediction}')
        except Exception as e:
            return render_template('index.html', prediction_text=f"Erreur lors de l'enregistrement: {str(e)}")

    return redirect(url_for('home'))

@app.route('/delete/<int:id>') # Route pour supprimer un patient
def delete(id):
    patient = db.session.get(Patient, id) # Utilisation de la nouvelle méthode session.get()
    if patient:
        db.session.delete(patient)
        db.session.commit()
    return redirect(url_for('list_patients'))

# Exécution de l'application Flask
if __name__ == "__main__":
    app.run(debug=True)
