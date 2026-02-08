import React, { useState } from 'react';

const MazetAppPreview = () => {
  const [activeTab, setActiveTab] = useState('accueil');
  
  const tabs = [
    { id: 'accueil', label: 'Accueil', icon: '🏠' },
    { id: 'infos', label: 'Infos', icon: 'ℹ️' },
    { id: 'activites', label: 'Activités', icon: '⭐' },
    { id: 'contact', label: 'Contact', icon: '✉️' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-amber-50 to-green-50 p-4">
      {/* iPhone Frame */}
      <div className="relative w-80 h-[680px] bg-black rounded-[3rem] p-3 shadow-2xl">
        {/* Notch */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-7 bg-black rounded-b-2xl z-20" />
        
        {/* Screen */}
        <div className="w-full h-full bg-gray-50 rounded-[2.2rem] overflow-hidden flex flex-col">
          {/* Status Bar */}
          <div className="h-12 bg-white flex items-end justify-center pb-1">
            <span className="text-xs font-medium text-gray-800">
              {activeTab === 'accueil' && 'Accueil'}
              {activeTab === 'infos' && 'Infos Pratiques'}
              {activeTab === 'activites' && 'Activités'}
              {activeTab === 'contact' && 'Contact'}
            </span>
          </div>
          
          {/* Content Area */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'accueil' && <AccueilContent />}
            {activeTab === 'infos' && <InfosContent />}
            {activeTab === 'activites' && <ActivitesContent />}
            {activeTab === 'contact' && <ContactContent />}
          </div>
          
          {/* Tab Bar */}
          <div className="h-20 bg-white border-t border-gray-200 flex items-center justify-around px-2 pb-4">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-all ${
                  activeTab === tab.id 
                    ? 'text-orange-500' 
                    : 'text-gray-400'
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <span className="text-[10px] font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Label */}
      <div className="mt-6 text-center">
        <p className="text-gray-600 font-medium">Le Mazet de BSA</p>
        <p className="text-gray-400 text-sm">Bourg-Saint-Andéol • Ardèche</p>
      </div>
    </div>
  );
};

const AccueilContent = () => (
  <div className="p-4 space-y-4">
    {/* Header Image */}
    <div className="h-44 rounded-2xl bg-gradient-to-br from-amber-200 via-amber-100 to-green-200 flex flex-col items-center justify-center shadow-lg relative overflow-hidden">
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-2 right-4 text-4xl">🌿</div>
        <div className="absolute bottom-4 left-4 text-3xl">🏛️</div>
      </div>
      <span className="text-5xl mb-2">🏡</span>
      <span className="text-white font-bold text-lg drop-shadow-lg">Le Mazet de BSA</span>
      <span className="text-white/80 text-xs drop-shadow-md">Bourg-Saint-Andéol • Ardèche</span>
    </div>
    
    {/* Welcome */}
    <div className="text-center space-y-2">
      <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-500 to-amber-600 bg-clip-text text-transparent">
        Bienvenue ! 🌿
      </h1>
      <p className="text-gray-500 text-sm">
        Nous sommes ravis de vous accueillir dans notre Mazet.
      </p>
    </div>
    
    {/* Info Card */}
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">✨</span>
        <span className="font-semibold text-gray-800">Votre petit coin de paradis</span>
      </div>
      <p className="text-gray-500 text-xs leading-relaxed">
        En plein cœur de Bourg-Saint-Andéol, notre mazet saura vous charmer avec ses vieilles pierres et ses poutres apparentes.
      </p>
      <div className="flex gap-2 mt-3">
        <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full">🏛️ Pierres</span>
        <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full">📏 Poutres</span>
        <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full">❤️ Charme</span>
      </div>
    </div>
    
    {/* Quick Access */}
    <div className="space-y-2">
      <h3 className="font-semibold text-gray-700 text-sm">Accès rapide</h3>
      <div className="grid grid-cols-2 gap-3">
        {[
          { icon: '📶', title: 'WiFi', sub: 'Code & connexion', color: 'bg-blue-50 text-blue-500' },
          { icon: '🚗', title: 'Parking', sub: 'Gratuit à 150m', color: 'bg-green-50 text-green-500' },
          { icon: '📍', title: 'Adresse', sub: 'Centre-ville BSA', color: 'bg-red-50 text-red-500' },
          { icon: '🆘', title: 'Urgences', sub: 'Numéros utiles', color: 'bg-orange-50 text-orange-500' },
        ].map((item, i) => (
          <div key={i} className="bg-white rounded-xl p-3 shadow-sm flex flex-col items-center">
            <span className="text-2xl mb-1">{item.icon}</span>
            <span className="font-medium text-xs text-gray-800">{item.title}</span>
            <span className="text-[10px] text-gray-400">{item.sub}</span>
          </div>
        ))}
      </div>
    </div>
    
    {/* Highlights */}
    <div className="space-y-2">
      <h3 className="font-semibold text-gray-700 text-sm">À découvrir</h3>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {[
          { emoji: '🏞️', name: 'Gorges', dist: '15 min' },
          { emoji: '🌉', name: 'Pont d\'Arc', dist: '20 min' },
          { emoji: '🦴', name: 'Grotte Chauvet', dist: '25 min' },
          { emoji: '🐊', name: 'Crocodiles', dist: '15 min' },
        ].map((item, i) => (
          <div key={i} className="flex-shrink-0 bg-white rounded-xl p-3 shadow-sm w-24">
            <span className="text-2xl">{item.emoji}</span>
            <p className="text-xs font-medium mt-1 text-gray-800">{item.name}</p>
            <p className="text-[10px] text-gray-400">{item.dist}</p>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const InfosContent = () => (
  <div className="p-4 space-y-4">
    {/* WiFi Section */}
    <div className="space-y-2">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Connexion Internet</h3>
      <div className="bg-white rounded-xl overflow-hidden shadow-sm">
        <InfoRow icon="📶" title="WiFi" detail="Réseau & mot de passe" />
      </div>
    </div>
    
    {/* Access Section */}
    <div className="space-y-2">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Accès au Mazet</h3>
      <div className="bg-white rounded-xl overflow-hidden shadow-sm">
        <InfoRow icon="📍" title="Adresse" detail="Centre-ville de BSA" />
        <InfoRow icon="🚗" title="Parking" detail="Gratuit à 150m" border />
        <InfoRow icon="🔑" title="Clés & Accès" detail="Arrivée / Départ" border />
      </div>
    </div>
    
    {/* Equipment Section */}
    <div className="space-y-2">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Équipements</h3>
      <div className="bg-white rounded-xl overflow-hidden shadow-sm">
        <InfoRow icon="🛏️" title="Literie" detail="Lits faits à l'arrivée" />
        <InfoRow icon="🚿" title="Serviettes" detail="Fournies" border />
        <InfoRow icon="🍳" title="Cuisine" detail="Tout équipée" border />
      </div>
    </div>
    
    {/* Emergency */}
    <div className="space-y-2">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Urgences</h3>
      <div className="bg-white rounded-xl overflow-hidden shadow-sm">
        <InfoRow icon="🚑" title="SAMU" detail="15" />
        <InfoRow icon="🚒" title="Pompiers" detail="18" border />
        <InfoRow icon="👮" title="Police" detail="17" border />
      </div>
    </div>
  </div>
);

const InfoRow = ({ icon, title, detail, border }) => (
  <div className={`flex items-center p-3 ${border ? 'border-t border-gray-100' : ''}`}>
    <span className="text-xl mr-3">{icon}</span>
    <div className="flex-1">
      <p className="font-medium text-sm text-gray-800">{title}</p>
      <p className="text-xs text-gray-400">{detail}</p>
    </div>
    <span className="text-gray-300">›</span>
  </div>
);

const ActivitesContent = () => (
  <div className="p-4 space-y-4">
    <div className="text-center space-y-1">
      <h2 className="font-bold text-lg text-gray-800">Découvrez l'Ardèche 🌿</h2>
      <p className="text-xs text-gray-500">Nos recommandations autour de BSA</p>
    </div>
    
    {[
      { icon: '⭐', title: 'Incontournables', items: ['Gorges de l\'Ardèche', 'Pont d\'Arc', 'Grotte Chauvet'] },
      { icon: '🏊', title: 'Baignade & Kayak', items: ['Descente en canoë', 'Plages de l\'Ardèche'] },
      { icon: '🏛️', title: 'Villes à visiter', items: ['Montélimar', 'Orange', 'Avignon'] },
      { icon: '🧺', title: 'Marchés', items: ['BSA (samedi)', 'Pierrelatte (mardi)'] },
      { icon: '🍽️', title: 'Bonnes tables', items: ['Restaurants locaux', 'Guinguettes'] },
    ].map((cat, i) => (
      <div key={i} className="bg-white rounded-xl p-3 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">{cat.icon}</span>
          <span className="font-semibold text-sm text-gray-800">{cat.title}</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {cat.items.map((item, j) => (
            <span key={j} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">{item}</span>
          ))}
        </div>
      </div>
    ))}
    
    {/* Spécialités */}
    <div className="bg-amber-50 rounded-xl p-3">
      <p className="font-semibold text-sm text-amber-800 mb-2">🍯 Spécialités à goûter</p>
      <div className="flex flex-wrap gap-1">
        <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">🧀 Picodon</span>
        <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">🍬 Nougat</span>
        <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">🌰 Châtaignes</span>
      </div>
    </div>
  </div>
);

const ContactContent = () => (
  <div className="p-4 space-y-4">
    {/* Host Avatar */}
    <div className="flex flex-col items-center space-y-2">
      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-orange-200 to-yellow-200 flex items-center justify-center">
        <span className="text-4xl">👤</span>
      </div>
      <h2 className="font-bold text-lg text-gray-800">Votre hôte</h2>
      <p className="text-xs text-gray-500">À votre service pour un séjour parfait</p>
    </div>
    
    {/* Contact Buttons */}
    <div className="space-y-3">
      {[
        { icon: '📞', title: 'Appeler', sub: '06 XX XX XX XX', color: 'bg-green-500' },
        { icon: '💬', title: 'SMS', sub: 'Réponse rapide', color: 'bg-blue-500' },
        { icon: '📱', title: 'WhatsApp', sub: 'Disponible 7j/7', color: 'bg-green-600' },
        { icon: '✉️', title: 'Email', sub: 'votre@email.com', color: 'bg-orange-500' },
      ].map((btn, i) => (
        <div key={i} className="bg-white rounded-xl p-3 shadow-sm flex items-center">
          <span className={`text-xl w-12 h-12 rounded-xl flex items-center justify-center text-white ${btn.color}`}>
            {btn.icon}
          </span>
          <div className="ml-3 flex-1">
            <p className="font-semibold text-sm text-gray-800">{btn.title}</p>
            <p className="text-xs text-gray-400">{btn.sub}</p>
          </div>
          <span className="text-gray-300">›</span>
        </div>
      ))}
    </div>
    
    {/* Airbnb */}
    <div className="bg-red-50 rounded-xl p-3 text-center">
      <span className="text-xl">🏠</span>
      <p className="text-sm font-medium text-red-700 mt-1">Messagerie Airbnb</p>
      <p className="text-xs text-red-500">Contactez-nous aussi via l'app</p>
    </div>
    
    {/* Tip */}
    <div className="bg-amber-50 rounded-xl p-3 text-center">
      <span className="text-xl">💡</span>
      <p className="text-xs text-amber-700 mt-1">
        Questions non urgentes → SMS/WhatsApp<br/>
        Urgences → Appelez directement
      </p>
    </div>
  </div>
);

export default MazetAppPreview;
