@echo off
echo 🛑 Arrêt de tous les serveurs Python...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo 🚀 Démarrage du serveur de production avec vraies APIs...
python production_real_server.py 