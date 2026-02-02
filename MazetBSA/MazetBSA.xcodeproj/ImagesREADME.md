# 📁 Dossier Images - Guide d'organisation

Ce dossier contient toutes les images utilisées dans l'application mazetBSA.

## 🗂️ Structure recommandée

```
Images/
├── mazet-hero.jpeg          # Photo principale (page d'accueil)
├── mazet-facade.jpeg        # Vue de la façade
├── mazet-interieur.jpeg     # Intérieur du mazet
├── mazet-jardin.jpeg        # Jardin/terrasse
├── mazet-chambre.jpeg       # Chambre
├── mazet-cuisine.jpeg       # Cuisine
├── mazet-salon.jpeg         # Salon
│
└── activites/               # Photos des activités et lieux à visiter
    ├── pont-arc.jpeg
    ├── gorges-ardeche.jpeg
    ├── village-bsa.jpeg
    ├── marche-local.jpeg
    └── ...
```

## 📝 Comment ajouter des images

### Méthode 1 : Via Xcode (Recommandé)

1. **Ouvrez Xcode**
2. Dans le navigateur de projet, localisez le dossier **"Images"**
3. **Faites glisser** vos photos depuis le Finder vers ce dossier
4. ✅ **Cochez "Copy items if needed"**
5. ✅ **Vérifiez que la target de l'app est cochée**

### Méthode 2 : Directement dans le Finder

1. Localisez le dossier du projet sur votre disque
2. Trouvez le dossier **Images/**
3. Copiez vos images dedans
4. Dans Xcode : Clic droit sur "Images" → **Add Files to [projet]...**

## 💻 Comment utiliser les images dans le code

### Utilisation basique

```swift
// Image depuis le dossier Images
MazetImage("mazet-hero")
    .aspectRatio(contentMode: .fill)
    .frame(height: 200)
```

### Avec sous-dossier

```swift
// Image depuis Images/activites/
MazetImage("pont-arc", subdirectory: "activites")
    .aspectRatio(contentMode: .fit)
    .frame(width: 300)
```

### Avec fallback personnalisé

```swift
MazetImage("photo-qui-nexiste-pas") {
    // Ce qui s'affiche si l'image n'est pas trouvée
    ZStack {
        Color.gray.opacity(0.2)
        Image(systemName: "photo")
    }
}
```

## 🎨 Formats supportés

- ✅ JPEG (.jpeg, .jpg)
- ✅ PNG (.png)
- ✅ HEIC (.heic)

## 💡 Conseils

1. **Nommage** : Utilisez des noms descriptifs en minuscules avec des tirets
   - ✅ `mazet-facade.jpeg`
   - ✅ `gorges-ardeche-panorama.jpg`
   - ❌ `IMG_1234.jpeg`
   - ❌ `Photo Sans Titre.jpg`

2. **Taille** : Optimisez vos images avant de les ajouter
   - Largeur recommandée : 1200-2000px pour les photos principales
   - Compression JPEG : 80-90% de qualité

3. **Organisation** : Créez des sous-dossiers pour grouper vos images par thème

## 🔧 Dépannage

**L'image ne s'affiche pas ?**
- Vérifiez le nom du fichier (sensible à la casse !)
- Vérifiez que l'extension est bien incluse dans le nom du fichier
- Vérifiez que l'image est bien dans la target de compilation (inspecteur de fichiers)
- Nettoyez le build : **Product → Clean Build Folder** (⇧⌘K)

**L'image est trop lourde ?**
- Utilisez un outil de compression comme ImageOptim (Mac)
- Redimensionnez l'image avant de l'ajouter au projet
