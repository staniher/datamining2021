# Travaux Dirigés (TD) & Exercices : Python pour Ingénieurs et Architectes (2026)

## Introduction : Bienvenue dans le monde de la programmation moderne
Ce document propose une série d'exercices progressifs adaptés aux étudiants des filières Génie Informatique, Génie Civil, Génie Électrique et Architecture. L'accent est mis sur l'application pratique des concepts Python 2026.

---

## Série 1 : Fondamentaux (Communs à toutes les filières)

### Exercice 1.1 : Le calculateur de constantes physiques
**Énoncé :** Créez un script qui demande à l'utilisateur de saisir une valeur en une unité (ex: mètres) et la convertit dans une autre (ex: pieds).
**Modernité 2026 :** Utilisez des `f-strings` avancées pour le formatage et gérez les erreurs de saisie avec `try-except`.

### Exercice 1.2 : Analyseur de liste de mesures
**Énoncé :** Soit une liste de 10 mesures prises par un capteur. Calculez la moyenne, le maximum, le minimum et identifiez les valeurs "anormales" (supérieures à 2 fois la moyenne).

---

## Série 2 : Spécialités Ingénierie

### Exercice 2.1 : Génie Informatique (IA & Données)
**Énoncé :** Simulez un mini-agent de filtrage de logs. Le script doit lire une liste de messages de serveurs et ne garder que ceux contenant "ERROR" ou "CRITICAL", puis les enregistrer dans un nouveau fichier.

### Exercice 2.2 : Génie Civil (Calcul de Structure)
**Énoncé :** Calculez la flèche maximale d'une poutre simple de longueur $L$, soumise à une charge répartie $q$, avec un module d'Young $E$ et un moment d'inertie $I$.
*Formule : $f_{max} = \frac{5 \cdot q \cdot L^4}{384 \cdot E \cdot I}$*

### Exercice 2.3 : Génie Électrique (Loi d'Ohm & Circuits)
**Énoncé :** Créez une fonction `calculer_tension(R, I)` et une fonction `calculer_puissance(U, I)`. Demandez les valeurs à l'utilisateur et affichez les résultats. Ajoutez une condition : si la puissance dépasse 2000W, affichez "ALERTE SURCHARGE".

### Exercice 2.4 : Architecture (Conception Paramétrique)
**Énoncé :** Calculez la surface vitrée idéale d'une pièce en fonction de sa surface au sol (ratio de 1/6ème selon la réglementation). Si la pièce fait plus de 20m², suggérez deux fenêtres au lieu d'une.

---

## Série 3 : Mini-Projets (TD de 2 heures)

### Projet A : Génie Civil & Archi - Estimateur de Matériaux
Créez un programme qui calcule le nombre de briques nécessaires pour un mur de dimensions $(L, H, E)$ données, en prenant en compte un volume de mortier de 10%.

### Projet B : Génie Info & Élec - Simulateur de Capteurs IoT
Générez une série de 100 données aléatoires représentant la tension d'une batterie sur 24h. Si la tension tombe sous 11.5V, déclenchez une notification fictive dans la console.

---

## Corrigés indicatifs (Extraits)

### Corrigé Exercice 2.2 (Génie Civil)
```python
def calcul_fleche(q, L, E, I):
    """
    Calcule la flèche d'une poutre (en mètres).
    q: charge (N/m), L: longueur (m), E: Young (Pa), I: Inertie (m^4)
    """
    return (5 * q * L**4) / (384 * E * I)

# Exemple d'utilisation
charge = 1500  # N/m
longueur = 5   # m
young = 210e9  # Pa (Acier)
inertie = 0.0001 # m^4
print(f"La flèche maximale est de : {calcul_fleche(charge, longueur, young, inertie):.5f} m")
```

### Corrigé Exercice 2.3 (Électrique)
```python
def check_power(u, i):
    p = u * i
    print(f"Puissance : {p} Watts")
    if p > 2000:
        print("!!! ALERTE SURCHARGE !!!")
    return p

u = float(input("Tension (V) : "))
i = float(input("Intensité (A) : "))
check_power(u, i)
```
