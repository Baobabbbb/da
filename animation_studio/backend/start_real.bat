@echo off
echo 🔥 ARRÊT DE TOUS LES SERVEURS PYTHON...
taskkill /F /IM python.exe 2>nul
timeout /t 3 /nobreak >nul

echo 🎬 DÉMARRAGE SERVEUR VRAIE GÉNÉRATION...
echo 🚫 AUCUN FALLBACK - AUCUNE VIDÉO PRÉCRÉÉE
echo 📍 Port: 8012
python real_generation_server.py 