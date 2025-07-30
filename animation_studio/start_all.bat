@echo off
echo 🎬 Animation Studio - Démarrage Complet
echo.

cd /d "%~dp0"

echo 📦 Installation des dépendances backend...
cd backend
pip install -r requirements.txt > nul 2>&1

echo 📦 Installation des dépendances frontend...
cd ..\frontend
call npm install > nul 2>&1

echo.
echo 🚀 Démarrage des services...
echo ⚡ Backend sur http://localhost:8007
echo 🌐 Frontend sur http://localhost:5173
echo.

cd ..\backend
start "Backend" cmd /k "python start.py"

cd ..\frontend  
start "Frontend" cmd /k "npm run dev"

echo ✅ Services démarrés dans des fenêtres séparées
echo 🛑 Fermez les fenêtres pour arrêter les services
pause 