from flask import Flask,request,render_template
import numpy as np
app=Flask(__name__)

@app.route('/')
#Cette fonction retourne la page index.html de notre projet
def home():
    return render_template('index.html')   
@app.route('/predict', methods=['POST']) #predict sera indiqué dans le form de html comme action pour permettre d'appeler la methode predict
#La fonction ci-dessous fait la prediction
def predict():
    import joblib
    #Nous chargeons notre modele sauvegardé dans le projet Flask pour l'utiliser
    model=joblib.load('ModelL2CSI2021.ml')
    #Nous récupérons toutes les valeurs saisies dans le formulaire html sous forme d'une liste
    string_features=[i for i in request.form.values()]
    #On recupere la derniere valeur de la liste(cad date d'entree a l'hopital)
    date_hospitalisation =string_features[-1]  
    #On recupere toutes les valeurs de la liste (Genre,Age,Maladie,Service) sauf la derniere 
    features_model = [string_features[0],string_features[1],string_features[2],string_features[3]]
    #On reshape les features pour le rendre un vecteur np capable d'etre introduits dans le modele pour la prediction
    features_model=np.array([features_model]).reshape(1,4)
    #On predit en utilisant le modele qui a été chargé ci-haut
    prediction=model.predict(features_model)[0]
    #On convertit la date de l'entree à l'hopital en datetime pour nous aider à y tirer le jour, le mois, l'annee pour une sortie plus aisée de prédiction
    import pandas as pd
    date_entree_hopital=pd.to_datetime(date_hospitalisation)
    from datetime import datetime,timedelta
    #Nous ajoutons les jours predits de sortie a l'hopital a la date saisie
    #de l'entree a l'hopital pour trouver la date de sortie
    date_sortie_hopital = date_entree_hopital + timedelta(days=prediction) #Prediction ici contient le nombre de jours predits 
    #On recupere le jour en francais(Par exemple Samedi, Lundi...)
    jour_semaine_sortie=date_sortie_hopital.day_name(locale='French')
    #On recupere le mois en francais(Par exemple Janvier, Mars...)
    mois_sortie=date_sortie_hopital.month_name(locale='French')
    #On recupere l'annee de sortie de l'hopital(Par exemple 2021)
    annee_sortie = date_sortie_hopital.year
    #On recupere le jour de sortie de l'hopital(Par exemple 11, 25, 30)
    jour_date_sortie = date_sortie_hopital.day
    #On prepare la chaine de retour contenant la prediction de la date de sortie
    chaine_prediction=" a la probabilité de sortir de l'hopital le "+str(jour_semaine_sortie) + ", "+str(jour_date_sortie) + " "+ str(mois_sortie) + " "+ str(annee_sortie) 
    #On retourne la page index.html avec le resultat formaté. N.B: prediction_text sera appelé dans la page index.html pour retourner le resultat
    return render_template('index.html',prediction_text='Ce Patient {}'.format(chaine_prediction))
#On execute notre application Flask
if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    
