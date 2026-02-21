# 🎓 LiveMarket Clone - Projet de Programmation Client-Serveur Réactive

Bienvenue dans ce projet pédagogique complet conçu pour enseigner les concepts de **réactivité temps réel**, de **communication bidirectionnelle (WebSockets)** et d'intégration de base de données **PostgreSQL** avec un frontend moderne en **React**.

## 📖 Sommaire
1. [Présentation du Projet](#présentation-du-projet)
2. [Concepts Appris](#concepts-appris)
3. [Architecture Technique](#architecture-technique)
4. [Étapes de Création](#étapes-de-création)
5. [Installation et Exécution](#installation-et-exécution)

---

## 🚀 Présentation du Projet

LiveMarket est une application "Dashboard" qui imite le comportement d'un marché boursier ou d'une plateforme d'échange de crypto-monnaies (type Bitcoin).
- **L'Admin** utilise un panneau dédié pour modifier le prix d'un actif en base de données.
- **Les Utilisateurs** voient leur écran se mettre à jour **instantanément** sans jamais avoir à rafraîchir leur page.

## 💡 Concepts Appris

- **Communication Bidirectionnelle** : Utilisation de WebSockets via **Socket.io**.
- **Base de Données Relationnelle** : Modélisation et requêtage avec **PostgreSQL**.
- **Hooks React** : Utilisation de `useEffect` pour gérer les abonnements aux sockets.
- **Visualisation de Données** : Intégration de graphiques dynamiques avec **Recharts**.
- **Design Responsive** : Utilisation de **Tailwind CSS** pour une interface adaptative.

## 🏗️ Architecture Technique

### 🟢 Backend (Node.js + Express)
Le serveur joue le rôle de chef d'orchestre :
- Il expose une **API REST** pour les opérations classiques (lecture des données, mise à jour admin).
- Il gère un **Pool de connexion PostgreSQL** pour la persistance des données.
- Il maintient un **Serveur WebSocket** pour diffuser les mises à jour en temps réel à tous les clients connectés dès qu'un changement survient en base.

### 🔵 Frontend (React + Vite)
L'interface utilisateur est décomposée en composants réutilisables :
- `App.jsx` : Gestionnaire d'état global et orchestration des sockets.
- `AssetCard.jsx` : Affichage visuel d'un actif (Prix, Nom, Symbole).
- `MarketChart.jsx` : Graphique temporel de l'évolution du prix.
- `AdminPanel.jsx` : Interface de contrôle pour l'administrateur.

## 🛠️ Étapes de Création

1.  **Initialisation du projet** : Séparation des environnements Backend et Frontend.
2.  **Configuration PostgreSQL** : Création du schéma de base de données (tables `assets` et `history`).
3.  **Développement de l'API REST** : Routes `GET` pour récupérer les données initiales et `POST` pour les mises à jour.
4.  **Intégration des WebSockets** : Configuration de Socket.io pour émettre un signal `assetUpdated` lors de chaque modification de prix.
5.  **Création du Dashboard React** : Design de l'interface avec Tailwind CSS.
6.  **Abonnement aux signaux** : Connexion du frontend au flux WebSocket pour mettre à jour l'état React localement et déclencher un re-rendu immédiat.

## 🏃 Installation et Exécution

### Prérequis
- Node.js (v16+)
- PostgreSQL installé et en cours d'exécution

### 0. Création de la Base de Données
Avant de lancer le serveur, vous devez créer la base de données dans PostgreSQL :
1. Ouvrez votre terminal PostgreSQL (psql) ou un outil comme pgAdmin.
2. Exécutez : `CREATE DATABASE livemarket;`
3. (Optionnel) Utilisez le fichier `setup.sql` à la racine du projet pour plus de détails.

### 1. Configuration du Backend
1. Rendez-vous dans le dossier `backend`.
2. Installez les dépendances : `npm install`.
3. Créez un fichier `.env` basé sur les variables dans `database.js` (ou utilisez celui fourni).
4. Lancez le serveur : `npm start`.
   - *Le serveur écoutera sur le port 5000.*

### 2. Configuration du Frontend
1. Rendez-vous dans le dossier `frontend`.
2. Installez les dépendances : `npm install`.
3. Lancez l'application : `npm run dev`.
   - *L'application sera accessible sur http://localhost:5173.*

---
*Ce projet a été réalisé avec ❤️ pour illustrer la puissance du web réactif moderne.*
