import gymnasium as gym # Importation de la bibliothèque Gymnasium pour le RL
from gymnasium import spaces # Importation des espaces Gymnasium (discret, continu, etc.)
import numpy as np # Importation de NumPy pour la gestion des tableaux numériques

class ButemboEnv(gym.Env): # Définition de la classe de l'environnement Butembo, héritant de gym.Env
    """
    Environnement personnalisé représentant la ville de Butembo sous forme de grille.
    L'agent doit naviguer du centre-ville vers le marché central en évitant les obstacles.
    """
    def __init__(self): # Constructeur de la classe
        super(ButemboEnv, self).__init__() # Appel du constructeur de la classe parente
        self.grid_size = 5 # Taille de la grille (5x5) représentant une zone de Butembo
        # Actions possibles : 0: Haut, 1: Bas, 2: Gauche, 3: Droite
        self.action_space = spaces.Discrete(4) # Définition de l'espace d'actions (4 directions possibles)
        # L'état est la position (x, y) de l'agent sur la grille
        self.observation_space = spaces.Discrete(self.grid_size * self.grid_size) # Espace d'observations discret (25 états)
        self.state = 0 # Position initiale de l'agent (en haut à gauche)
        self.goal = 24 # Position du marché central (en bas à droite)
        self.obstacles = [6, 12, 18] # Positions des obstacles (ex: zones de travaux ou collines abruptes)

    def reset(self, seed=None, options=None): # Fonction de réinitialisation de l'environnement
        super().reset(seed=seed) # Réinitialisation avec gestion de la graine aléatoire
        self.state = 0 # Remise de l'agent à la position de départ (0,0)
        return self.state, {} # Retourne l'état initial et des infos vides

    def step(self, action): # Fonction de transition effectuant une action dans l'environnement
        x, y = divmod(self.state, self.grid_size) # Conversion de l'état scalaire en coordonnées (x, y)

        if action == 0: # Action : Haut
            x = max(0, x - 1) # Déplacement vers le haut en restant dans les limites
        elif action == 1: # Action : Bas
            x = min(self.grid_size - 1, x + 1) # Déplacement vers le bas en restant dans les limites
        elif action == 2: # Action : Gauche
            y = max(0, y - 1) # Déplacement vers la gauche en restant dans les limites
        elif action == 3: # Action : Droite
            y = min(self.grid_size - 1, y + 1) # Déplacement vers la droite en restant dans les limites

        self.state = x * self.grid_size + y # Mise à jour de l'état après mouvement

        terminated = self.state == self.goal # Vérifie si l'agent a atteint le marché central (but)
        reward = 10 if terminated else -1 # Récompense de +10 si but atteint, sinon pénalité de -1 par pas

        if self.state in self.obstacles: # Si l'agent touche un obstacle
            reward = -5 # Applique une pénalité plus forte
            # Optionnel: on pourrait terminer l'épisode ici, mais on laisse l'agent apprendre à contourner

        truncated = False # Pas de limite de temps forcée ici
        return self.state, reward, terminated, truncated, {} # Retourne les informations de l'étape RL

    def render(self): # Fonction facultative pour l'affichage visuel de l'environnement
        grid = np.full((self.grid_size, self.grid_size), ".") # Création d'une grille vide remplie de points
        x, y = divmod(self.state, self.grid_size) # Coordonnées actuelles de l'agent
        gx, gy = divmod(self.goal, self.grid_size) # Coordonnées du but
        for obs in self.obstacles: # Marquage des obstacles sur la grille
            ox, oy = divmod(obs, self.grid_size) # Coordonnées de chaque obstacle
            grid[ox, oy] = "X" # X représente un obstacle
        grid[gx, gy] = "M" # M représente le Marché (le but)
        grid[x, y] = "A" # A représente l'Agent
        print("\n".join([" ".join(row) for row in grid])) # Affichage de la grille formatée dans la console
        print("-" * 10) # Ligne de séparation pour la lisibilité
