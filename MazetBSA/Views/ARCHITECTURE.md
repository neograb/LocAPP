# Structure de Projet Multi-Propriétés

## 📂 Organisation des fichiers

Le projet est maintenant organisé en dossiers séparés pour chaque propriété :

```
MazetBSA/
├── App/
│   ├── MazetBSAApp.swift              # Point d'entrée de l'application
│   ├── MainNavigationView.swift       # Navigation principale
│   └── PropertySelectionView.swift    # Sélection de propriété
│
├── Models/
│   └── PropertyModel.swift            # Modèle de données Property
│
├── Shared/
│   ├── Components/
│   │   ├── QuickAccessCard.swift      # Carte d'accès rapide (réutilisable)
│   │   ├── EmergencyRow.swift         # Ligne numéro d'urgence (réutilisable)
│   │   ├── InfoRow.swift              # Ligne d'information (réutilisable)
│   │   └── ContactButton.swift        # Bouton de contact (réutilisable)
│   │
│   └── Utilities/
│       ├── ImageLoader.swift          # Helper pour charger les images
│       └── ThemeColors.swift          # Couleurs du thème
│
├── MazetBSA/                          # 🟠 TOUT CE QUI CONCERNE MAZET BSA
│   ├── MazetBSAAccueilView.swift     # Page d'accueil Mazet BSA
│   ├── MazetBSADetailViews.swift     # Vues de détail (WiFi, Adresse, etc.)
│   ├── InfosPratiquesView.swift      # Infos pratiques Mazet BSA
│   ├── ActivitesView.swift           # Activités Ardèche
│   └── ContactView.swift             # Contact Mazet BSA
│
└── Vaujany/                           # 🔵 TOUT CE QUI CONCERNE VAUJANY
    ├── VaujanyAccueilView.swift      # Page d'accueil Vaujany
    ├── VaujanyDetailViews.swift      # Vues de détail (WiFi, Adresse, etc.)
    ├── InfosPratiquesVaujanyView.swift  # Infos pratiques Vaujany
    ├── ActivitesVaujanyView.swift    # Activités montagne
    └── ContactVaujanyView.swift      # Contact Vaujany
```

## 🎯 Principe de séparation

### 1. **Fichiers partagés** (Shared/)
Composants réutilisables entre les deux propriétés :
- `QuickAccessCard` : Carte d'accès rapide
- `EmergencyRow` : Ligne numéro d'urgence
- `InfoRow` : Ligne d'information
- `ContactButton` : Bouton de contact

### 2. **Dossier MazetBSA/**
Tout ce qui est spécifique au Mazet BSA en Ardèche :
- Couleur d'accent : Orange 🟠
- Thème : Provençal, soleil
- Activités : Gorges de l'Ardèche, Pont d'Arc, etc.

### 3. **Dossier Vaujany/**
Tout ce qui est spécifique à Vaujany en Isère :
- Couleur d'accent : Bleu 🔵
- Thème : Montagne, neige
- Activités : Ski, randonnées, montagne

## 🔄 Flux de navigation

```
1. Lancement de l'app
   ↓
2. PropertySelectionView
   │
   ├─→ Utilisateur choisit "Mazet BSA"
   │   ↓
   │   MazetBSATabView
   │   ├── MazetBSAAccueilView
   │   ├── InfosPratiquesView
   │   ├── ActivitesView
   │   └── ContactView
   │
   └─→ Utilisateur choisit "Vaujany"
       ↓
       VaujanyTabView
       ├── VaujanyAccueilView
       ├── InfosPratiquesVaujanyView
       ├── ActivitesVaujanyView
       └── ContactVaujanyView
```

## 📝 Convention de nommage

### Mazet BSA
- Préfixe : `MazetBSA...` pour les vues spécifiques
- Pas de préfixe pour les vues originales (ex: `ActivitesView`)

### Vaujany
- Préfixe : `Vaujany...` pour toutes les vues
- Exemple : `VaujanyAccueilView`, `VaujanyContactView`

## ✅ Avantages de cette structure

1. **Séparation claire** : Chaque propriété a son propre dossier
2. **Réutilisabilité** : Les composants communs sont dans `Shared/`
3. **Scalabilité** : Facile d'ajouter une 3e propriété
4. **Maintenance** : Modification d'une propriété sans impacter l'autre
5. **Organisation** : Structure claire et logique

## 🚀 Ajouter une nouvelle propriété

Pour ajouter une nouvelle propriété (ex: "Chalet Megève") :

1. **Ajouter la propriété dans `PropertyModel.swift`** :
```swift
static let chaletMegeve = Property(
    name: "Chalet Megève",
    shortName: "Megève",
    location: "Haute-Savoie",
    imageName: "megeve-hero",
    accentColor: .green,
    description: "Votre chalet de luxe en Haute-Savoie"
)
```

2. **Créer un nouveau dossier** : `Megeve/`

3. **Créer les vues** :
   - `MegeveAccueilView.swift`
   - `InfosPratiquesMegeveView.swift`
   - `ActivitesMegeveView.swift`
   - `ContactMegeveView.swift`

4. **Ajouter le TabView dans `PropertyContentView.swift`** :
```swift
else if property.id == Property.chaletMegeve.id {
    MegeveTabView(onBack: onBack)
}
```

## 💡 Bonnes pratiques

- ✅ Ne jamais mélanger le code de deux propriétés dans un même fichier
- ✅ Utiliser les composants `Shared/` pour éviter la duplication
- ✅ Garder les noms de vues cohérents avec le préfixe de propriété
- ✅ Chaque propriété a sa propre couleur d'accent
- ✅ Les images sont préfixées (ex: `mazet-hero`, `vaujany-hero`)

## 🎨 Personnalisation par propriété

Chaque propriété peut avoir :
- Couleurs d'accent différentes
- Images différentes
- Contenu complètement différent
- Fonctionnalités spécifiques

Tout en partageant les composants réutilisables !
