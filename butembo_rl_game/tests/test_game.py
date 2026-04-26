import sys
import os
# Ajouter le répertoire parent au chemin pour importer les modules locaux
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import ButemboEnv # Importation de l'environnement pour le test
from agent import QLearningAgent # Importation de l'agent pour le test
import numpy as np # Importation de NumPy pour les assertions

def test_environment_reset(): # Test de la réinitialisation de l'environnement
    env = ButemboEnv() # Initialisation
    state, info = env.reset() # Appel de reset
    assert state == 0 # L'état initial doit être 0
    assert isinstance(info, dict) # Les infos doivent être un dictionnaire

def test_environment_step(): # Test d'une étape de transition
    env = ButemboEnv() # Initialisation
    env.reset() # Réinitialisation
    # Action 1 correspond à descendre (Bas)
    next_state, reward, terminated, truncated, _ = env.step(1) # Exécution d'un pas vers le bas
    assert next_state == 5 # Dans une grille 5x5, descendre de (0,0) mène à l'index 5
    assert reward == -1 # La récompense par défaut pour un pas normal est -1

def test_agent_choose_action(): # Test du choix d'action de l'agent
    env = ButemboEnv() # Initialisation environnement
    agent = QLearningAgent(state_size=25, action_size=4) # Initialisation agent
    action = agent.choose_action(0) # Choix d'une action pour l'état 0
    assert action in [0, 1, 2, 3] # L'action doit être valide (entre 0 et 3)

def test_agent_learning(): # Test de la mise à jour de la Q-table
    agent = QLearningAgent(state_size=25, action_size=4) # Initialisation agent
    initial_q_value = agent.q_table[0, 1] # Valeur Q initiale (doit être 0)
    # L'agent apprend qu'aller de 0 à 5 donne une récompense de -1
    agent.learn(state=0, action=1, reward=-1, next_state=5, done=False)
    assert agent.q_table[0, 1] != initial_q_value # La valeur Q doit avoir changé
    assert agent.q_table[0, 1] < 0 # Puisque la récompense est négative, la valeur Q doit diminuer
