import React, { useState, useEffect } from 'react'; // Importation des hooks fondamentaux de React
import io from 'socket.io-client'; // Importation du client Socket.io
import axios from 'axios'; // Importation d'Axios pour les requêtes HTTP classiques
import AssetCard from './components/AssetCard'; // Importation de la carte d'actif
import MarketChart from './components/MarketChart'; // Importation du graphique
import AdminPanel from './components/AdminPanel'; // Importation du panneau admin

// Initialisation de la connexion WebSocket vers le serveur backend (port 5000)
const socket = io('http://localhost:5000');

function App() {
  // Déclaration des états de l'application
  const [assets, setAssets] = useState([]); // Liste complète des actifs (BTC, ETH, etc.)
  const [selectedId, setSelectedId] = useState(1); // ID de l'actif actuellement affiché sur le graphique
  const [history, setHistory] = useState([]); // Historique des prix pour le graphique
  const [isLive, setIsLive] = useState(false); // État de connexion temps réel pour l'UI

  // useEffect exécuté une seule fois au montage du composant
  useEffect(() => {
    // 1. Récupération initiale des actifs via l'API REST
    axios.get('http://localhost:5000/api/assets')
      .then(res => {
        setAssets(res.data); // Stockage des actifs dans l'état
        if (res.data.length > 0) setSelectedId(res.data[0].id); // Sélection du premier par défaut
      })
      .catch(err => console.error("Erreur chargement assets:", err));

    // 2. Configuration des écouteurs de WebSockets
    socket.on('connect', () => setIsLive(true)); // Mise à jour du voyant "Live" à la connexion
    socket.on('disconnect', () => setIsLive(false)); // Mise à jour à la déconnexion

    // Écoute de l'événement 'assetUpdated' envoyé par le serveur
    socket.on('assetUpdated', (updatedAsset) => {
      // Mise à jour réactive de la liste des actifs : on remplace seulement l'actif concerné
      setAssets(prev => prev.map(a => a.id === updatedAsset.id ? updatedAsset : a));

      // Si l'actif mis à jour est celui que l'utilisateur regarde sur le graphique, on rafraîchit l'historique
      if (selectedId === updatedAsset.id) {
        fetchHistory(updatedAsset.id);
      }
    });

    // Nettoyage des écouteurs lors du démontage du composant pour éviter les fuites de mémoire
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('assetUpdated');
    };
  }, [selectedId]); // On redéclenche si l'ID sélectionné change pour mettre à jour la logique d'écoute

  // Fonction pour charger l'historique d'un actif spécifique
  const fetchHistory = (id) => {
    axios.get(`http://localhost:5000/api/assets/${id}/history`)
      .then(res => setHistory(res.data)) // Mise à jour de l'état history
      .catch(err => console.error("Erreur historique:", err));
  };

  // useEffect qui surveille le changement d'actif sélectionné
  useEffect(() => {
    fetchHistory(selectedId); // On charge les nouvelles données du graphique
  }, [selectedId]);

  // Recherche de l'objet complet de l'actif sélectionné pour l'affichage
  const currentAsset = assets.find(a => a.id === parseInt(selectedId));

  return (
    // Mise en page principale avec Tailwind CSS
    <div className="min-h-screen bg-slate-900 text-white p-4 md:p-12 font-sans selection:bg-blue-500/30">

      {/* En-tête avec indicateur Live */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-12 gap-4">
        <div>
          <h1 className="text-5xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
            LIVEMARKET <span className="text-white">CLONE</span>
          </h1>
          <p className="text-slate-500 font-medium">Cours de Programmation Client-Serveur Réactive</p>
        </div>

        {/* Badge d'état de connexion réactive */}
        <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${isLive ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400' : 'border-red-500/50 bg-red-500/10 text-red-400'}`}>
          <div className={`h-2 w-2 rounded-full ${isLive ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className="text-xs font-bold uppercase tracking-widest">{isLive ? 'Live Connection' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Contenu principal en grille : 2 colonnes pour le dashboard, 1 pour l'admin */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Colonne Gauche : Cartes et Graphique */}
        <div className="lg:col-span-2 space-y-8">
          {/* Grille des cartes d'actifs financiers */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {assets.map(a => (
              <div key={a.id} onClick={() => setSelectedId(a.id)}>
                {/* On passe l'actif au composant AssetCard */}
                <AssetCard asset={a} />
              </div>
            ))}
          </div>

          {/* Affichage du graphique si un actif est sélectionné et possède un historique */}
          {currentAsset && (
            <MarketChart
              data={history}
              title={`Évolution du prix : ${currentAsset.name}`}
            />
          )}
        </div>

        {/* Colonne Droite : Panneau d'Administration */}
        <div className="space-y-6">
          <AdminPanel assets={assets} />

          {/* Carte informative pédagogique */}
          <div className="bg-blue-600/10 border border-blue-500/20 p-6 rounded-xl">
            <h4 className="text-blue-400 font-bold mb-2 flex items-center gap-2 text-sm uppercase">💡 Note de l'enseignant</h4>
            <p className="text-slate-400 text-sm leading-relaxed italic">
              "Chaque changement effectué dans ce panneau est envoyé au serveur via HTTP POST,
              puis redistribué instantanément à tous les clients via WebSockets. C'est le principe
              fondamental de la programmation réactive."
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; // Exportation de l'application
