#!/usr/bin/env python3
"""
🚀 Démarrage ULTRA-RAPIDE d'Animation Studio Backend
Évite toutes les vérifications longues pour un démarrage immédiat
"""

import sys
import os
from pathlib import Path

# Configuration pour démarrage rapide
os.environ["FAST_START"] = "true"

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("⚡ Démarrage ULTRA-RAPIDE d'Animation Studio")
print("📝 Validation minimale activée")

# Import rapide
try:
    from config import config
    print("✅ Configuration chargée")
except ImportError as e:
    print(f"❌ Erreur configuration: {e}")
    sys.exit(1)

# Démarrage immédiat
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print(f"🚀 Serveur RAPIDE sur: http://{config.HOST}:{config.PORT}")
    print(f"📚 Documentation: http://{config.HOST}:{config.PORT}/docs")
    print("⚡ Mode accéléré - validation complète disponible via /diagnostic")
    print("🛑 Ctrl+C pour arrêter")
    
    # Configuration ultra-rapide
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level="warning",  # Moins de logs = plus rapide
        access_log=False      # Désactiver logs d'accès
    ) 