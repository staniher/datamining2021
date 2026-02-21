import React, { useState } from 'react'; // Importation des hooks React
import axios from 'axios'; // Importation d'Axios pour les appels HTTP

// Composant AdminPanel permettant de simuler l'injection de données par l'admin
const AdminPanel = ({ assets }) => {
  const [selectedId, setSelectedId] = useState(''); // État pour stocker l'ID de l'actif choisi
  const [price, setPrice] = useState(''); // État pour stocker le nouveau prix saisi
  const [status, setStatus] = useState(''); // État pour afficher un message de succès/erreur

  // Fonction de gestion de la soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault(); // Empêche le rechargement de la page
    if (!selectedId || !price) return; // Validation basique

    try {
      // Envoi de la requête POST au backend pour mettre à jour le prix en base de données
      await axios.post(`http://localhost:5000/api/assets/${selectedId}/update`, {
        price: parseFloat(price)
      });
      setStatus('Succès !'); // Message de réussite
      setPrice(''); // Réinitialisation du champ prix
      setTimeout(() => setStatus(''), 3000); // Efface le message après 3 secondes
    } catch (err) {
      setStatus('Erreur de connexion'); // Message d'erreur
    }
  };

  return (
    // Conteneur du formulaire avec style Tailwind
    <form onSubmit={handleSubmit} className="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4 shadow-2xl">
      <h3 className="text-xl font-bold text-white uppercase tracking-widest border-b border-slate-700 pb-2">Admin</h3>

      <div>
        <label className="text-slate-500 text-xs block mb-1">Actif à modifier</label>
        {/* Sélecteur d'actif rempli dynamiquement depuis la base de données */}
        <select
          value={selectedId}
          onChange={e => setSelectedId(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        >
          <option value="">Sélectionner...</option>
          {assets.map(a => <option key={a.id} value={a.id}>{a.name} ({a.symbol})</option>)}
        </select>
      </div>

      <div>
        <label className="text-slate-500 text-xs block mb-1">Nouveau prix ($)</label>
        {/* Champ de saisie numérique pour le nouveau prix */}
        <input
          type="number"
          step="0.01"
          value={price}
          onChange={e => setPrice(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          placeholder="Ex: 48500.00"
        />
      </div>

      {/* Bouton de validation */}
      <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold p-3 rounded transition-colors shadow-lg">
        Mettre à jour le marché
      </button>

      {/* Affichage conditionnel du statut de l'opération */}
      {status && <p className="text-center text-xs font-bold text-blue-400 animate-pulse">{status}</p>}
    </form>
  );
};

export default AdminPanel; // Exportation du composant
