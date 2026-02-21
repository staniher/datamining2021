import React from 'react' // Importation de la bibliothèque React
import ReactDOM from 'react-dom/client' // Importation du moteur de rendu DOM pour React
import App from './App.jsx' // Importation du composant racine App
import './index.css' // Importation des styles Tailwind CSS globaux

// Création du rendu racine lié à l'élément #root du fichier HTML
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* Enveloppement de l'application dans StrictMode pour détecter les problèmes potentiels */}
    <App />
  </React.StrictMode>,
)
