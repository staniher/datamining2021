import React from 'react'; // Importation de React
import { TrendingUp, TrendingDown } from 'lucide-react'; // Importation des icônes de tendance

// Définition du composant AssetCard qui prend un objet 'asset' en propriété
const AssetCard = ({ asset }) => {
  // Calcul fictif pour la couleur de la tendance visuelle (positif si prix élevé)
  const isUp = asset.price > 1000;

  return (
    // Structure de la carte avec des classes Tailwind CSS pour le style sombre et responsive
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 hover:border-blue-500 transition-all cursor-pointer shadow-xl">
      <div className="flex justify-between items-start mb-4">
        <div>
          {/* Affichage du nom complet de l'actif (ex: Bitcoin) */}
          <h3 className="text-slate-400 text-xs font-semibold uppercase tracking-widest">{asset.name}</h3>
          {/* Affichage du symbole de l'actif (ex: BTC) */}
          <p className="text-2xl font-black text-white">{asset.symbol}</p>
        </div>
        {/* Icône changeant de couleur en fonction de la tendance */}
        <div className={isUp ? 'text-green-400' : 'text-red-400'}>
          {isUp ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
        </div>
      </div>

      <div className="flex flex-col">
        {/* Affichage du prix formaté en dollars avec séparateurs de milliers */}
        <span className="text-3xl font-mono font-bold text-blue-400">
          ${parseFloat(asset.price).toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </span>
        {/* Affichage de l'heure du dernier changement reçu par le serveur */}
        <span className="text-slate-500 text-[10px] mt-2 italic">
          Dernière mise à jour : {new Date(asset.last_update).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};

export default AssetCard; // Exportation pour utilisation dans App.jsx
