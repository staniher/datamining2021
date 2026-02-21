-- Script de création de la base de données LiveMarket
-- À exécuter dans psql ou un client SQL

-- Création de la base de données
CREATE DATABASE livemarket;

-- Connexion à la base de données
\c livemarket

-- La structure des tables est automatiquement gérée par database.js au démarrage du serveur,
-- mais voici le schéma pour référence :

-- CREATE TABLE assets (
--   id SERIAL PRIMARY KEY,
--   symbol TEXT UNIQUE NOT NULL,
--   name TEXT NOT NULL,
--   price DECIMAL(15,2) NOT NULL,
--   last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE history (
--   id SERIAL PRIMARY KEY,
--   asset_id INTEGER REFERENCES assets(id),
--   price DECIMAL(15,2) NOT NULL,
--   timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
