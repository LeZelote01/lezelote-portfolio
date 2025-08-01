#!/bin/bash

echo "🧪 Test du système de profil avec photo et informations détaillées"
echo "=================================================================="

# Test 1: Vérifier que les services sont en ligne
echo "📡 Test 1: Vérification des services..."
backend_status=$(curl -s http://localhost:8001/api/ | grep -o "Hello World" || echo "ERROR")
if [ "$backend_status" = "Hello World" ]; then
    echo "✅ Backend: En ligne"
else
    echo "❌ Backend: Hors ligne"
    exit 1
fi

frontend_status=$(curl -s http://localhost:3000 | grep -o "doctype html" || echo "ERROR")
if [ "$frontend_status" = "doctype html" ]; then
    echo "✅ Frontend: En ligne"
else
    echo "❌ Frontend: Hors ligne"
    exit 1
fi

# Test 2: Vérifier l'API publique des informations personnelles
echo ""
echo "👤 Test 2: API publique des informations personnelles..."
personal_info=$(curl -s http://localhost:8001/api/public/personal)
name=$(echo "$personal_info" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('name', 'ERROR'))" 2>/dev/null || echo "ERROR")
age=$(echo "$personal_info" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('age', 'ERROR'))" 2>/dev/null || echo "ERROR")
photo=$(echo "$personal_info" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('profile_image_url', 'ERROR'))" 2>/dev/null || echo "ERROR")

if [ "$name" != "ERROR" ] && [ "$name" != "None" ]; then
    echo "✅ Nom: $name"
else
    echo "❌ Nom: Non trouvé"
fi

if [ "$age" != "ERROR" ] && [ "$age" != "None" ]; then
    echo "✅ Âge: $age ans"
else
    echo "❌ Âge: Non trouvé"
fi

if [ "$photo" != "ERROR" ] && [ "$photo" != "None" ]; then
    echo "✅ Photo de profil: $photo"
else
    echo "❌ Photo de profil: Non trouvée"
fi

# Test 3: Vérifier que la photo existe physiquement
echo ""
echo "🖼️ Test 3: Vérification de l'existence de la photo..."
if [ -f "/app/frontend/public$photo" ]; then
    echo "✅ Fichier photo existe: /app/frontend/public$photo"
else
    echo "❌ Fichier photo introuvable: /app/frontend/public$photo"
fi

# Test 4: Test d'authentification admin
echo ""
echo "🔐 Test 4: Authentification admin..."
token_response=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

token=$(echo "$token_response" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', 'ERROR'))" 2>/dev/null || echo "ERROR")

if [ "$token" != "ERROR" ] && [ ${#token} -gt 20 ]; then
    echo "✅ Authentification admin: Réussie"
else
    echo "❌ Authentification admin: Échouée"
    exit 1
fi

# Test 5: Vérifier l'accès aux informations admin
echo ""
echo "🛠️ Test 5: Accès API admin..."
admin_info=$(curl -s -X GET http://localhost:8001/api/admin/personal \
  -H "Authorization: Bearer $token")

admin_age=$(echo "$admin_info" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('age', 'ERROR'))" 2>/dev/null || echo "ERROR")
admin_certifications=$(echo "$admin_info" | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('certifications', [])))" 2>/dev/null || echo "ERROR")

if [ "$admin_age" != "ERROR" ] && [ "$admin_age" != "None" ]; then
    echo "✅ API Admin - Âge: $admin_age"
else
    echo "❌ API Admin - Âge: Non accessible"
fi

if [ "$admin_certifications" != "ERROR" ] && [ "$admin_certifications" != "0" ]; then
    echo "✅ API Admin - Certifications: $admin_certifications trouvées"
else
    echo "❌ API Admin - Certifications: Non accessibles"
fi

# Test 6: Pages web accessibles
echo ""
echo "🌐 Test 6: Accessibilité des pages..."
home_check=$(curl -s http://localhost:3000/ | grep -o "Jean Yves" | head -1 || echo "ERROR")
about_check=$(curl -s http://localhost:3000/about | grep -o "doctype html" || echo "ERROR")
admin_check=$(curl -s http://localhost:3000/admin/login | grep -o "doctype html" || echo "ERROR")

if [ "$home_check" = "Jean Yves" ]; then
    echo "✅ Page d'accueil: Accessible"
else
    echo "❌ Page d'accueil: Problème"
fi

if [ "$about_check" = "doctype html" ]; then
    echo "✅ Page À propos: Accessible"
else
    echo "❌ Page À propos: Problème"
fi

if [ "$admin_check" = "doctype html" ]; then
    echo "✅ Page Admin: Accessible"
else
    echo "❌ Page Admin: Problème"
fi

echo ""
echo "🎉 Tests terminés ! Voici comment accéder à votre portfolio:"
echo "📱 Frontend: http://localhost:3000"
echo "🏠 Accueil avec photo: http://localhost:3000/"
echo "👤 Page À propos: http://localhost:3000/about"
echo "🔧 Admin: http://localhost:3000/admin/login (admin/admin123)"
echo "⚙️ Gérer le profil: http://localhost:3000/admin/personal"
echo "💬 Messages de contact: http://localhost:3000/admin/contacts"