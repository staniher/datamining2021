from flask import Flask, render_template, request, jsonify
from ner_engine import ButemboNEREngine
from tuq_module import ButemboTUQ
import pandas as pd

# Initialisation de l'application Flask v2 pour le projet Butembo-AI
app = Flask(__name__)

# Chargement des moteurs IA (NER et TUQ)
# N.B: Ces objets sont instanciés une seule fois au démarrage du serveur
ner_engine = ButemboNEREngine()
tuq_module = ButemboTUQ()

@app.route('/')
# Affiche la page d'accueil de l'interface de cartographie des crises
def index():
    return render_template('index_v2.html')

@app.route('/analyze', methods=['POST'])
# Route API pour analyser un rapport de crise en temps réel
def analyze():
    # Récupération du texte saisi par l'utilisateur (français ou swahili)
    data = request.json
    report_text = data.get('text', '')

    if not report_text:
        return jsonify({"error": "Texte vide"}), 400

    # Étape 1: Extraction des entités via l'approche Zero-Shot
    entity_type, confidence = ner_engine.extract_entities(report_text)

    # Étape 2: Calcul de l'incertitude topologique (LCR)
    # On encode d'abord le texte en embedding SBERT
    embedding = ner_engine.model.encode([report_text])[0]
    lcr_score, is_uncertain = tuq_module.compute_lcr(embedding)

    # Retourne les résultats au format JSON pour l'interface Bootstrap
    return jsonify({
        "entity_type": entity_type,
        "confidence": float(confidence),
        "lcr_score": float(lcr_score),
        "is_uncertain": is_uncertain,
        "status": "Alerte Critique" if is_uncertain else "Information Stable"
    })

# Exécution du serveur Flask
if __name__ == "__main__":
    # Debug=True permet le rechargement automatique lors du développement à Butembo
    app.run(debug=True, port=5001)
