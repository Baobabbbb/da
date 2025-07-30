@echo off
:: Script Git - Push automatique

:: Demander le message de commit
set /p message=Message du commit : 

:: Exécuter les commandes Git
git add .
git commit -m "%message%"
git push origin main

:: Pause pour voir le résultat
pause
