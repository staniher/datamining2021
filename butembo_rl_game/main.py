from environment import ButemboEnv # Importation de notre environnement personnalisé Butembo
from agent import QLearningAgent # Importation de notre agent intelligent Q-Learning
import numpy as np # Importation de NumPy pour les calculs numériques

def train_and_demo(): # Fonction principale pour l'entraînement et la démonstration
    # Création de l'environnement Butembo
    env = ButemboEnv() # Initialisation de l'instance de l'environnement

    # Création de l'agent Q-Learning
    # L'agent doit connaître le nombre d'états et d'actions possibles
    agent = QLearningAgent(state_size=env.observation_space.n, action_size=env.action_space.n)

    num_episodes = 500 # Nombre total d'épisodes pour l'entraînement

    print(f"Début de l'entraînement de l'agent pour {num_episodes} épisodes à Butembo...") # Message d'info

    for episode in range(num_episodes): # Boucle d'entraînement sur les épisodes
        state, _ = env.reset() # Réinitialisation de l'environnement au début de chaque épisode
        done = False # Variable pour suivre si l'épisode est terminé

        while not done: # Boucle d'étapes au sein d'un épisode
            action = agent.choose_action(state) # L'agent choisit une action (exploration ou exploitation)
            next_state, reward, terminated, truncated, _ = env.step(action) # L'environnement réagit à l'action
            done = terminated or truncated # Vérifie si l'épisode doit s'arrêter

            agent.learn(state, action, reward, next_state, done) # L'agent apprend de son expérience
            state = next_state # Mise à jour de l'état actuel pour l'étape suivante

        if (episode + 1) % 100 == 0: # Affichage de la progression tous les 100 épisodes
            print(f"Épisode {episode + 1}/{num_episodes} terminé. Epsilon: {agent.epsilon:.4f}")

    print("\nEntraînement terminé !") # Message de fin d'entraînement

    print("\nDémonstration de l'agent entraîné (Trajet optimal vers le Marché Central) :") # Début démo
    state, _ = env.reset() # Réinitialisation pour la démonstration
    env.render() # Affichage initial de la grille
    done = False # Réinitialisation du statut de fin
    steps = 0 # Compteur de pas effectués

    while not done and steps < 20: # Limite de pas pour éviter les boucles infinies en démo
        action = np.argmax(agent.q_table[state]) # Choix de la meilleure action apprise uniquement
        state, reward, terminated, truncated, _ = env.step(action) # Exécution de l'action
        done = terminated or truncated # Vérification de la fin
        env.render() # Affichage de l'état actuel de la grille après le mouvement
        steps += 1 # Incrémentation du compteur

    if state == env.goal: # Vérification du succès final
        print("Félicitations ! L'agent a atteint le Marché Central de Butembo.") # Succès
    else: # Échec (rare après entraînement)
        print("L'agent s'est perdu dans les collines de Butembo.") # Échec

if __name__ == "__main__": # Point d'entrée du script
    train_and_demo() # Exécution de la fonction d'entraînement et démo
