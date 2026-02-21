import React from 'react'; // Importation de React
// Importation des composants nécessaires de la bibliothèque Recharts pour le graphique
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Composant MarketChart qui affiche l'historique des prix sous forme de graphique en aire
const MarketChart = ({ data, title }) => {
  return (
    // Conteneur principal avec une hauteur fixe pour le graphique
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 h-[400px] shadow-2xl">
      {/* Titre dynamique du graphique */}
      <h3 className="text-xl font-bold text-white mb-6 uppercase tracking-tighter">{title}</h3>
      {/* ResponsiveContainer permet au graphique de s'adapter à la taille de son parent */}
      <ResponsiveContainer width="100%" height="100%">
        {/* AreaChart est le type de graphique choisi pour une visualisation "boursière" */}
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          {/* Définition du dégradé de couleur pour le remplissage sous la courbe */}
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          {/* Grille horizontale pour faciliter la lecture des prix */}
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          {/* Axe X représentant le temps, formaté en heure:minute */}
          <XAxis
            dataKey="timestamp"
            stroke="#64748b"
            tickFormatter={(tick) => new Date(tick).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            fontSize={10}
          />
          {/* Axe Y représentant le prix, ajusté automatiquement aux valeurs */}
          <YAxis
            stroke="#64748b"
            domain={['auto', 'auto']}
            fontSize={10}
            tickFormatter={(val) => `${val}`}
          />
          {/* Infobulle affichée au survol du graphique */}
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
            labelFormatter={(label) => new Date(label).toLocaleString()}
          />
          {/* La ligne de données elle-même, avec animation et remplissage dégradé */}
          <Area
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            fillOpacity={1}
            fill="url(#colorPrice)"
            strokeWidth={3}
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MarketChart; // Exportation du composant
