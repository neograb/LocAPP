#!/bin/bash

# Script de démarrage pour WebLocAPP

echo "🚀 Démarrage de WebLocAPP..."

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création..."
    python3 -m venv venv-weblocapp
    echo "✅ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
source venv-weblocapp/bin/activate

# Vérifier si les dépendances sont installées
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
    echo "✅ Dépendances installées"
fi

# Démarrer le serveur
echo ""
echo "✅ Serveur WebLocAPP démarré !"
echo "📍 Accédez à l'interface d'administration sur :"
echo "   → http://51.77.156.95:5001"
echo "   → http://127.0.0.1:5001"
echo ""
echo "🔐 Identifiants par défaut :"
echo "   Utilisateur: test@test.com"
echo "   Mot de passe: family!!"
echo ""
echo "💡 Appuyez sur CTRL+C pour arrêter le serveur"
echo ""

python run-prod.py
