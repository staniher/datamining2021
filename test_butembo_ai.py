import unittest
import numpy as np
from ner_engine import ButemboNEREngine
from tuq_module import ButemboTUQ
import os

# Tests unitaires pour valider les composants critiques du projet Butembo-AI
class TestButemboAI(unittest.TestCase):
    # Test de l'engin NER Zero-Shot
    def test_ner_engine(self):
        # On initialise l'engin avec le modèle SBERT 'all-MiniLM-L6-v2'
        ner = ButemboNEREngine()
        # On teste une phrase simple sur un incident à Butembo
        text = "Un incursion rebelle a eu lieu à Vutsundo."
        # Extraction du type d'entité et du score de confiance
        predicted_type, score = ner.extract_entities(text)

        # Le type prédit doit être dans les types supportés par le modèle
        self.assertIn(predicted_type, ["lieu", "conflit", "acteur armé"])
        # Le score de confiance doit être normalisé entre -1 et 1
        self.assertTrue(-1 <= score <= 1)

    # Test du module de Quantification d'Incertitude Topologique (TUQ)
    def test_tuq_module(self):
        # Initialisation du module TUQ avec dimension 384
        tuq = ButemboTUQ()
        # Création d'un embedding aléatoire pour simuler SBERT
        test_emb = np.random.rand(384)
        # Calcul du Local Cohomology Residual (LCR)
        lcr, uncertain = tuq.compute_lcr(test_emb)

        # Le score LCR doit être positif
        self.assertGreaterEqual(lcr, 0.0)
        # On vérifie le type de retour pour l'incertitude (bool ou np.bool_)
        self.assertTrue(isinstance(uncertain, (bool, np.bool_)))

    # Test de la présence des données de crise (via la génération)
    def test_data_generation_columns(self):
        # Chargement et vérification des colonnes attendues
        import pandas as pd
        if os.path.exists("butembo_crisis_data.csv"):
            df = pd.read_csv("butembo_crisis_data.csv")
            self.assertIn("text", df.columns)
            self.assertIn("language", df.columns)

# Exécution des tests via unittest
if __name__ == "__main__":
    unittest.main()
