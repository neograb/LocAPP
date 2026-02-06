# WebLocAPP - Serveur d'administration pour LocApp

## Description

WebLocAPP est un serveur web d'administration développé en Python/Flask qui permet de gérer toutes les données de l'application iOS LocApp. Il offre une interface web complète pour administrer les informations de votre location sans avoir à modifier le code Swift.

## Fonctionnalités

- **Interface web intuitive** pour gérer toutes les données
- **API REST complète** avec authentification
- **Base de données SQLite** pour le stockage
- **Export JSON** pour l'intégration avec l'app iOS
- **Gestion CRUD** pour les activités et services
- **Tous les champs sont administrables** :
  - Informations générales (nom, messages de bienvenue)
  - Configuration WiFi (SSID, mot de passe)
  - Adresse et localisation
  - Parking et stationnement
  - Clés et accès (horaires, codes)
  - Contact (téléphone, email, WhatsApp)
  - Activités touristiques
  - Services à proximité
  - Numéros d'urgence

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Installer les dépendances**

```bash
cd WebLocAPP
pip install -r requirements.txt
```

2. **Initialiser la base de données**

La base de données sera automatiquement créée au premier lancement avec les données par défaut de l'application iOS.

3. **Lancer le serveur**

```bash
python app.py
```

Le serveur sera accessible sur : http://localhost:5001

## Configuration

### Authentification

Par défaut, les identifiants sont :
- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `locapp2024`

⚠️ **IMPORTANT** : Changez ces identifiants dans le fichier `app.py` avant de mettre en production !

```python
USERNAME = 'admin'
PASSWORD = 'votre-nouveau-mot-de-passe'
```

### Secret Key

Modifiez également la clé secrète dans `app.py` :

```python
app.config['SECRET_KEY'] = 'votre-cle-secrete-unique'
```

## Utilisation

### Interface Web

1. Accédez à http://localhost:5001 dans votre navigateur
2. Naviguez entre les différentes sections via le menu
3. Modifiez les champs souhaités
4. Cliquez sur "Enregistrer" (authentification requise)

### Sections disponibles

- **Accueil** : Vue d'ensemble et export des données
- **Général** : Nom de la propriété et messages de bienvenue
- **WiFi** : Configuration du réseau sans fil
- **Adresse** : Localisation de la propriété
- **Parking** : Informations sur le stationnement
- **Accès** : Horaires et codes d'accès
- **Contact** : Coordonnées de l'hôte
- **Activités** : Gestion des attractions touristiques
- **Services** : Commerces et services à proximité
- **Urgences** : Numéros d'urgence (lecture seule)

### Export des données

Pour exporter toutes les données au format JSON :

1. Allez sur la page d'accueil
2. Cliquez sur "Télécharger l'export JSON"
3. Entrez vos identifiants
4. Le fichier `locapp_data.json` sera téléchargé

## API REST

### Endpoints disponibles

#### Informations générales
- `GET /api/general` - Récupérer les informations
- `PUT /api/general` - Mettre à jour (auth requise)

#### WiFi
- `GET /api/wifi` - Récupérer la configuration
- `PUT /api/wifi` - Mettre à jour (auth requise)

#### Adresse
- `GET /api/address` - Récupérer l'adresse
- `PUT /api/address` - Mettre à jour (auth requise)

#### Parking
- `GET /api/parking` - Récupérer les infos parking
- `PUT /api/parking` - Mettre à jour (auth requise)

#### Accès
- `GET /api/access` - Récupérer les infos d'accès
- `PUT /api/access` - Mettre à jour (auth requise)

#### Contact
- `GET /api/contact` - Récupérer les infos de contact
- `PUT /api/contact` - Mettre à jour (auth requise)

#### Activités
- `GET /api/activities` - Liste toutes les activités
- `GET /api/activities/<id>` - Récupérer une activité
- `POST /api/activities` - Créer une activité (auth requise)
- `PUT /api/activities/<id>` - Mettre à jour (auth requise)
- `DELETE /api/activities/<id>` - Supprimer (auth requise)

#### Services
- `GET /api/services` - Liste tous les services
- `GET /api/services/<id>` - Récupérer un service
- `POST /api/services` - Créer un service (auth requise)
- `PUT /api/services/<id>` - Mettre à jour (auth requise)
- `DELETE /api/services/<id>` - Supprimer (auth requise)

#### Export
- `GET /api/export` - Exporter toutes les données JSON
- `GET /api/export/download` - Télécharger le JSON (auth requise)

### Authentification API

Les requêtes nécessitant une authentification utilisent HTTP Basic Auth :

```bash
curl -u admin:locapp2024 -X PUT http://localhost:5001/api/general \
  -H "Content-Type: application/json" \
  -d '{"property_name":"Mon Mazet", ...}'
```

## Structure du projet

```
WebLocAPP/
├── app.py                    # Serveur Flask principal
├── database.py               # Gestion de la base de données SQLite
├── requirements.txt          # Dépendances Python
├── README.md                 # Cette documentation
├── locapp.db                 # Base de données SQLite (créée automatiquement)
├── static/
│   ├── css/
│   │   └── style.css        # Styles de l'interface
│   └── js/
│       └── common.js        # Fonctions JavaScript communes
└── templates/
    ├── base.html            # Template de base
    ├── index.html           # Page d'accueil
    ├── general.html         # Gestion infos générales
    ├── wifi.html            # Gestion WiFi
    ├── address.html         # Gestion adresse
    ├── parking.html         # Gestion parking
    ├── access.html          # Gestion accès
    ├── contact.html         # Gestion contact
    ├── activities.html      # Gestion activités
    ├── services.html        # Gestion services
    └── emergency.html       # Visualisation urgences
```

## Intégration avec l'app iOS

Pour intégrer les données dans votre application iOS :

1. Exportez les données via l'interface web ou l'API
2. Récupérez le fichier JSON
3. Dans votre app Swift, chargez ce JSON au lieu des données hardcodées
4. Utilisez `Codable` pour parser le JSON

Exemple Swift :

```swift
struct AppConfig: Codable {
    let general_info: GeneralInfo
    let wifi: WiFiConfig
    let address: Address
    // ... autres champs
}

// Charger le JSON
if let url = Bundle.main.url(forResource: "locapp_data", withExtension: "json") {
    let data = try Data(contentsOf: url)
    let config = try JSONDecoder().decode(AppConfig.self, from: data)
}
```

## Déploiement en production

### Option 1 : Serveur local

Pour un serveur accessible uniquement localement :

```bash
python app.py
```

### Option 2 : Serveur accessible sur le réseau

```bash
# Dans app.py, modifiez la dernière ligne :
app.run(debug=False, host='0.0.0.0', port=5001)
```

### Option 3 : Déploiement avec Gunicorn (recommandé)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Option 4 : Déploiement cloud (Heroku, Railway, etc.)

Ajoutez un fichier `Procfile` :

```
web: gunicorn app:app
```

⚠️ **Sécurité** : En production, utilisez HTTPS et des identifiants forts !

## Sauvegarde

La base de données est stockée dans le fichier `locapp.db`. Faites régulièrement des sauvegardes :

```bash
cp locapp.db locapp_backup_$(date +%Y%m%d).db
```

## Dépannage

### Le serveur ne démarre pas

- Vérifiez que Python 3.8+ est installé : `python --version`
- Vérifiez que les dépendances sont installées : `pip list`

### Erreur d'authentification

- Vérifiez les identifiants dans `app.py`
- Essayez de réinitialiser le cache du navigateur

### Base de données corrompue

- Supprimez `locapp.db` et relancez le serveur
- La base sera recréée avec les données par défaut

## Support

Pour toute question ou problème :
1. Consultez cette documentation
2. Vérifiez les logs du serveur dans le terminal
3. Consultez le code source pour plus de détails

## Licence

Ce projet a été créé pour administrer l'application LocApp.

---

**Développé avec Flask + SQLite + HTML/CSS/JavaScript**
