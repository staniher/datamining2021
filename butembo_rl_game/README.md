# Projet : Agent de Reinforcement Learning à Butembo

## Description Complète
Ce projet implémente un jeu vidéo innovant basé sur le **Reinforcement Learning** (Apprentissage par Renforcement) utilisant l'algorithme **Q-Learning**.

Le jeu se déroule dans un contexte local inspiré de la ville de **Butembo** (Nord-Kivu, RDC). L'agent (un citadin ou un taxi-moto) doit naviguer dans une grille représentant un quartier de la ville pour atteindre le **Marché Central** tout en évitant des obstacles tels que des collines escarpées ou des zones de travaux.

L'innovation réside dans l'utilisation de l'IA pour apprendre de manière autonome le trajet optimal dans un environnement urbain modélisé, offrant une base pour des simulations logistiques ou éducatives.

## Étapes de Création
1. **Conception de l'Environnement** : Modélisation de la topographie de Butembo sous forme d'une grille `gymnasium`.
2. **Développement de l'Agent** : Implémentation de la logique de Q-Learning (Table de valeurs, Epsilon-Greedy).
3. **Intégration et Entraînement** : Création d'un script principal pour faire interagir l'agent avec son environnement sur plusieurs centaines d'épisodes.
4. **Validation par Tests** : Mise en place d'une suite de tests avec `pytest` pour garantir la cohérence des transitions et de l'apprentissage.

## Instructions d'Exécution

### Prérequis
Assurez-vous d'avoir Python installé sur votre machine.

### Installation des Dépendances
Installez les bibliothèques nécessaires avec la commande suivante :
```bash
pip install -r requirements.txt
```

### Lancer l'Entraînement et la Démo
Pour voir l'agent apprendre et réussir son trajet à Butembo, lancez :
```bash
python main.py
```

### Exécuter les Tests Logiciels
Pour vérifier que le code fonctionne comme prévu :
```bash
pytest tests/test_game.py
```

## Structure du Projet
- `environment.py` : Définition de la grille et des règles de Butembo.
- `agent.py` : Cerveau de l'IA utilisant le Q-Learning.
- `main.py` : Script de lancement (Entraînement + Démo).
- `requirements.txt` : Liste des packages requis.
- `tests/` : Dossier contenant les tests automatisés.

---
*Développé avec passion pour Butembo.*
