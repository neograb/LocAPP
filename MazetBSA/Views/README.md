# 🏠 Le Mazet de BSA - Application iOS

Application iOS pour accueillir les locataires du **Mazet de BSA** situé à **Bourg-Saint-Andéol** en Ardèche.

## 🏡 À propos du Mazet

- **Localisation** : Centre-ville de Bourg-Saint-Andéol (07700), Ardèche
- **Caractéristiques** : Vieilles pierres, poutres apparentes, charme provençal
- **Parking** : Gratuit à 150m

### Attractions à proximité
- 🏞️ Gorges de l'Ardèche (15 min)
- 🌉 Pont d'Arc (20 min)
- 🦴 Grotte Chauvet 2 (25 min)
- 🐊 Ferme aux Crocodiles (15 min)
- 🍬 Montélimar (25 min)

## 📱 Aperçu

L'application comprend 4 onglets :
- **Accueil** : Message de bienvenue et raccourcis rapides
- **Infos Pratiques** : WiFi, équipements, consignes
- **Activités** : Recommandations locales (restaurants, randonnées, etc.)
- **Contact** : Coordonnées de l'hôte

---

## 🚀 Installation

### Prérequis
1. **macOS** avec **Xcode 15+** (gratuit sur l'App Store)
2. **Compte Apple Developer** (99€/an) pour publier sur l'App Store

### Créer le projet dans Xcode

1. Ouvrir **Xcode**
2. `File` → `New` → `Project`
3. Choisir **iOS** → **App**
4. Configurer :
   - **Product Name** : `MazetBSA`
   - **Team** : Votre compte Apple Developer
   - **Organization Identifier** : `com.votredomaine` (ex: `com.mazetbsa`)
   - **Interface** : `SwiftUI`
   - **Language** : `Swift`
5. Cliquer **Next** et choisir l'emplacement

### Ajouter les fichiers

1. Supprimer le fichier `ContentView.swift` créé par défaut
2. Créer un groupe `Views` : clic droit sur le projet → `New Group`
3. Copier les fichiers `.swift` de ce dossier dans le projet :
   - `MazetBSAApp.swift` → à la racine
   - Tous les autres → dans le groupe `Views`

---

## ✏️ Personnalisation

### 1. Informations de base

#### WiFi (InfosPratiquesView.swift)
```swift
InfoRow(
    icon: "wifi",
    iconColor: .blue,
    title: "WiFi",
    detail: "VotreNomWiFi"  // ← Modifier ici
)
InfoRow(
    icon: "lock.fill",
    iconColor: .gray,
    title: "Mot de passe",
    detail: "VotreMotDePasse"  // ← Modifier ici
)
```

#### Contact (ContactView.swift)
Remplacer les numéros de téléphone et email :
```swift
// Téléphone
if let url = URL(string: "tel://0612345678") {  // ← Votre numéro

// SMS  
if let url = URL(string: "sms://0612345678") {  // ← Votre numéro

// WhatsApp
if let url = URL(string: "https://wa.me/33612345678") {  // ← Format international

// Email
if let url = URL(string: "mailto:votre@email.com") {  // ← Votre email
```

### 2. Ajouter vos photos

1. Dans Xcode, cliquer sur `Assets.xcassets`
2. Glisser-déposer vos photos
3. Remplacer les placeholders par des `Image("nomDeVotrePhoto")`

### 3. Ajouter du contenu (Activités)

Dans `ActivitesView.swift`, remplacer les placeholders :
```swift
ActivitySection(
    title: "Restaurants",
    icon: "fork.knife",
    color: .orange,
    items: [
        ActivityItem(name: "Le Petit Bistrot", description: "Cuisine provençale - 5 min"),
        ActivityItem(name: "Chez Marcel", description: "Pizzeria - 10 min"),
        // Ajoutez d'autres restaurants...
    ]
)
```

---

## 🎨 Personnaliser les couleurs

### Couleur d'accentuation
1. Ouvrir `Assets.xcassets`
2. Cliquer sur `AccentColor`
3. Choisir votre couleur (ex: ocre provençal)

### Thème de l'app (AccueilView.swift)
Modifier le dégradé :
```swift
LinearGradient(
    colors: [
        Color(red: 0.96, green: 0.87, blue: 0.70), // Ocre clair
        Color(red: 0.55, green: 0.71, blue: 0.67)  // Vert provence
    ],
    ...
)
```

---

## 📤 Publication sur l'App Store

### 1. Préparer l'app
- Ajouter une **icône d'app** (1024x1024 px) dans `Assets.xcassets`
- Configurer les **Launch Screen** 
- Tester sur votre iPhone via Xcode

### 2. App Store Connect
1. Aller sur [App Store Connect](https://appstoreconnect.apple.com)
2. Créer une nouvelle app
3. Remplir les métadonnées :
   - Nom : Le Mazet de BSA
   - Description
   - Captures d'écran
   - Catégorie : Voyage

### 3. Soumettre
1. Dans Xcode : `Product` → `Archive`
2. `Distribute App` → `App Store Connect`
3. Attendre la validation Apple (24-48h)

---

## 🔧 Évolutions possibles

L'architecture modulaire permet d'ajouter facilement :

- [ ] **Notifications push** pour communiquer avec les locataires
- [ ] **Plan interactif** du logement
- [ ] **Livre d'or** avec avis des visiteurs
- [ ] **FAQ** avec questions fréquentes
- [ ] **Mode hors-ligne** pour les infos essentielles
- [ ] **Multi-langue** (anglais, espagnol...)
- [ ] **Intégration calendrier** pour les événements locaux

---

## 📁 Structure du projet

```
MazetBSA/
├── MazetBSAApp.swift      # Point d'entrée
├── Views/
│   ├── ContentView.swift       # Navigation principale (TabView)
│   ├── AccueilView.swift       # Page d'accueil
│   ├── InfosPratiquesView.swift # Infos WiFi, équipements...
│   ├── ActivitesView.swift     # Recommandations locales
│   └── ContactView.swift       # Contact hôte
└── Assets.xcassets/       # Images et couleurs
```

---

## 💡 Conseils

1. **Testez sur votre iPhone** avant de publier
2. **Mettez à jour régulièrement** les infos (restaurants, activités)
3. **Ajoutez un QR code** dans le Mazet pour télécharger l'app
4. **Demandez des retours** à vos premiers locataires

---

## 🆘 Support

Pour toute question sur le développement iOS :
- Documentation Apple : [developer.apple.com](https://developer.apple.com)
- SwiftUI : [developer.apple.com/swiftui](https://developer.apple.com/xcode/swiftui/)

Bonne chance avec votre application ! 🏡
