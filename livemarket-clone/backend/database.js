// Importation du module 'dotenv' pour charger les variables d'environnement
require('dotenv').config();
// Importation du module 'pg' pour interagir avec PostgreSQL
const { Pool } = require('pg');

// Configuration de la connexion à la base de données PostgreSQL via les variables d'environnement
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'livemarket',
  password: process.env.DB_PASSWORD || 'password',
  port: process.env.DB_PORT || 5432,
});

// Fonction pour initialiser les tables au démarrage du serveur
const initDb = async () => {
  try {
    // Création de la table 'assets' si elle n'existe pas
    await pool.query(`
      CREATE TABLE IF NOT EXISTS assets (
        id SERIAL PRIMARY KEY,
        symbol TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        price DECIMAL(15,2) NOT NULL,
        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Création de la table 'history'
    await pool.query(`
      CREATE TABLE IF NOT EXISTS history (
        id SERIAL PRIMARY KEY,
        asset_id INTEGER REFERENCES assets(id),
        price DECIMAL(15,2) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Insertion de données de test si vide
    const res = await pool.query('SELECT COUNT(*) FROM assets');
    if (parseInt(res.rows[0].count) === 0) {
      await pool.query(`
        INSERT INTO assets (symbol, name, price) VALUES
        ('BTC', 'Bitcoin', 45000.00),
        ('ETH', 'Ethereum', 2500.00),
        ('SOL', 'Solana', 100.00);
      `);
      console.log('Données initiales insérées.');
    }
  } catch (err) {
    console.error('Erreur DB Init:', err);
  }
};

initDb();
module.exports = pool;
