import numpy as np # Importation de NumPy pour la gestion des tables de Q-valeurs
import random # Importation de random pour la politique epsilon-greedy

class QLearningAgent: # Définition de l'agent utilisant l'algorithme Q-Learning
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.995):
        # Initialisation des paramètres de l'agent
        self.state_size = state_size # Nombre total d'états possibles
        self.action_size = action_size # Nombre total d'actions possibles
        self.lr = learning_rate # Taux d'apprentissage (alpha)
        self.gamma = discount_factor # Facteur d'actualisation (gamma) pour les récompenses futures
        self.epsilon = exploration_rate # Taux d'exploration initial (epsilon)
        self.epsilon_decay = exploration_decay # Facteur de réduction de l'exploration au fil du temps
        self.epsilon_min = 0.01 # Valeur minimale de l'exploration
        # Initialisation de la Q-table avec des zéros
        self.q_table = np.zeros((state_size, action_size)) # Tableau stockant la valeur de chaque action dans chaque état

    def choose_action(self, state): # Méthode pour choisir une action selon la politique epsilon-greedy
        # Exploration : l'agent choisit une action au hasard
        if random.uniform(0, 1) < self.epsilon: # Si un nombre aléatoire est inférieur à epsilon
            return random.randint(0, self.action_size - 1) # Retourne un index d'action aléatoire
        # Exploitation : l'agent choisit la meilleure action apprise (valeur Q maximale)
        else:
            return np.argmax(self.q_table[state]) # Retourne l'index de l'action ayant la plus haute valeur Q

    def learn(self, state, action, reward, next_state, done): # Méthode de mise à jour de la Q-table (apprentissage)
        # Calcul de la valeur Q cible (Bellman Equation simplifiée)
        # Si l'épisode est fini, il n'y a pas d'état futur
        target = reward # Valeur cible immédiate
        if not done: # Si l'épisode continue
            # La cible inclut la récompense future maximale actualisée
            target = reward + self.gamma * np.max(self.q_table[next_state])

        # Mise à jour de la valeur Q actuelle vers la cible avec le taux d'apprentissage
        # Q(s,a) = Q(s,a) + alpha * (cible - Q(s,a))
        self.q_table[state, action] += self.lr * (target - self.q_table[state, action])

        # Réduction progressive de l'exploration si l'épisode est terminé
        if done and self.epsilon > self.epsilon_min: # Si l'agent a terminé et que epsilon est encore élevé
            self.epsilon *= self.epsilon_decay # Réduit l'exploration pour favoriser l'exploitation plus tard
