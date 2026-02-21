require('dotenv').config(); // Chargement des variables d'environnement depuis le fichier .env
const express = require('express'); // Importation du framework Express pour créer l'API
const http = require('http'); // Importation du module HTTP natif de Node.js
const { Server } = require('socket.io'); // Importation de Socket.io pour la communication bidirectionnelle
const cors = require('cors'); // Importation du middleware CORS pour autoriser les requêtes multi-origines
const pool = require('./database'); // Importation de la configuration PostgreSQL depuis database.js

const app = express(); // Initialisation de l'application Express
const server = http.createServer(app); // Création du serveur HTTP en utilisant l'application Express
const io = new Server(server, { // Initialisation de Socket.io sur le serveur HTTP
  cors: { // Configuration de la politique CORS pour Socket.io
    origin: "*", // Autorisation de toutes les origines (à restreindre en production)
    methods: ["GET", "POST"] // Méthodes HTTP autorisées
  }
});

app.use(cors()); // Activation du middleware CORS pour toutes les routes Express
app.use(express.json()); // Activation de l'analyse automatique des corps de requête au format JSON

// Route GET pour récupérer tous les actifs financiers
app.get('/api/assets', async (req, res) => {
  try { // Bloc de capture d'erreurs pour la requête SQL
    const result = await pool.query('SELECT * FROM assets ORDER BY id ASC'); // Exécution de la requête SELECT sur PostgreSQL
    res.json(result.rows); // Envoi des résultats au format JSON au client
  } catch (err) { // Capture d'une éventuelle erreur de base de données
    res.status(500).json({ error: err.message }); // Envoi d'un code d'erreur 500 et du message d'erreur
  }
});

// Route GET pour récupérer l'historique des prix d'un actif spécifique
app.get('/api/assets/:id/history', async (req, res) => {
  const { id } = req.params; // Récupération de l'ID de l'actif depuis les paramètres d'URL
  try { // Bloc de capture d'erreurs
    const result = await pool.query('SELECT * FROM history WHERE asset_id = $1 ORDER BY timestamp DESC LIMIT 20', [id]); // Requête avec paramètre pour éviter les injections SQL
    res.json(result.rows.reverse()); // Inversion de l'ordre pour l'affichage chronologique sur le graphique
  } catch (err) { // Capture d'erreur
    res.status(500).json({ error: err.message }); // Envoi de l'erreur au client
  }
});

// Route POST pour mettre à jour le prix d'un actif (Interface Administrateur)
app.post('/api/assets/:id/update', async (req, res) => {
  const { id } = req.params; // Récupération de l'ID depuis l'URL
  const { price } = req.body; // Récupération du nouveau prix depuis le corps de la requête (JSON)

  try { // Début d'une transaction logique
    // Mise à jour du prix actuel dans la table 'assets'
    await pool.query('UPDATE assets SET price = $1, last_update = CURRENT_TIMESTAMP WHERE id = $2', [price, id]);

    // Ajout d'une nouvelle ligne dans l'historique pour garder trace de l'évolution
    await pool.query('INSERT INTO history (asset_id, price) VALUES ($1, $2)', [id, price]);

    // Récupération de l'actif mis à jour pour informer les clients connectés
    const updated = await pool.query('SELECT * FROM assets WHERE id = $1', [id]);

    if (updated.rows.length > 0) { // Vérification que l'actif existe bien
      io.emit('assetUpdated', updated.rows[0]); // Envoi du message WebSocket 'assetUpdated' à tous les clients connectés
    }

    res.json({ success: true }); // Confirmation de la réussite de l'opération
  } catch (err) { // En cas d'échec de la mise à jour
    res.status(500).json({ error: err.message }); // Envoi de l'erreur au client
  }
});

// Écouteur d'événement de connexion WebSocket
io.on('connection', (socket) => {
  console.log('Nouvelle connexion client :', socket.id); // Journalisation de l'ID du client connecté au serveur

  socket.on('disconnect', () => { // Détection de la déconnexion du client
    console.log('Client déconnecté'); // Journalisation du départ du client
  });
});

const PORT = process.env.PORT || 5000; // Définition du port d'écoute du serveur
server.listen(PORT, () => { // Lancement effectif du serveur sur le port spécifié
  console.log(`Le serveur backend tourne sur le port ${PORT}`); // Message de confirmation dans la console
});
