import asyncio
import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any

from config import config
from models.schemas import (
    AnimationRequest, AnimationResult, AnimationProgress, 
    DiagnosticResponse, AnimationTheme, AnimationDuration
)
from services.animation_pipeline import AnimationPipeline

# Pipeline global
pipeline = AnimationPipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print("🎬 Animation Studio - Démarrage du serveur...")
    
    # Mode rapide par défaut
    print("⚡ Mode démarrage rapide")
    # Validation ultra-rapide des clés
    if config.OPENAI_API_KEY:
        print("✅ Clé OpenAI détectée")
    if config.WAVESPEED_API_KEY:
        print("✅ Clé Wavespeed détectée")
    if config.FAL_API_KEY:
        print("✅ Clé FAL AI détectée")
    
    yield
    
    # Shutdown
    print("🛑 Arrêt du serveur...")
    pipeline.cleanup_old_animations()

# Création de l'app FastAPI
app = FastAPI(
    title="Animation Studio API",
    description="API de génération de dessins animés pour enfants basée sur l'IA",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache pour stocker les callbacks de progression
progress_callbacks: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API"""
    return {
        "name": "Animation Studio API",
        "version": "1.0.0",
        "description": "Génération de dessins animés pour enfants via IA",
        "endpoints": {
            "diagnostic": "/diagnostic",
            "generate": "/generate",
            "status": "/status/{animation_id}",
            "themes": "/themes"
        }
    }

@app.get("/diagnostic", response_model=DiagnosticResponse)
async def diagnostic():
    """Diagnostic complet de l'état des APIs et services"""
    try:
        health = await pipeline.validate_pipeline_health()
        
        return DiagnosticResponse(
            openai_configured=bool(config.OPENAI_API_KEY),
            wavespeed_configured=bool(config.WAVESPEED_API_KEY),
            fal_configured=bool(config.FAL_API_KEY),
            all_systems_operational=health["pipeline_operational"],
            details=health
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur diagnostic: {str(e)}")

@app.get("/themes")
async def get_themes():
    """Récupère la liste des thèmes disponibles avec descriptions"""
    try:
        themes = pipeline.get_supported_themes()
        
        # Formater pour l'interface utilisateur
        formatted_themes = {}
        for theme_key, theme_data in themes.items():
            formatted_themes[theme_key] = {
                "name": theme_key.title(),
                "description": theme_data["base_concept"],
                "elements": theme_data["elements"],
                "mood": theme_data["mood"],
                "icon": {
                    "space": "🚀",
                    "nature": "🌳", 
                    "adventure": "🏰",
                    "animals": "🐾",
                    "magic": "✨",
                    "friendship": "🤝"
                }.get(theme_key, "🎬")
            }
        
        return {
            "themes": formatted_themes,
            "durations": [30, 60, 120, 180, 240, 300],
            "default_duration": config.DEFAULT_DURATION
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération thèmes: {str(e)}")

@app.post("/generate", response_model=AnimationResult)
async def generate_animation(request: AnimationRequest, background_tasks: BackgroundTasks):
    """Génère un dessin animé basé sur la requête"""
    try:
        # Valider la requête
        if request.duration not in [30, 60, 120, 180, 240, 300]:
            raise HTTPException(status_code=400, detail="Durée non supportée")
        
        # Démarrer la génération en arrière-plan
        def progress_callback(progress: AnimationProgress):
            progress_callbacks[progress.animation_id] = progress
        
        # Générer l'animation
        result = await pipeline.generate_animation(request, progress_callback)
        
        # Nettoyer le cache de progression
        if result.animation_id in progress_callbacks:
            del progress_callbacks[result.animation_id]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération: {str(e)}")

@app.get("/status/{animation_id}")
async def get_animation_status(animation_id: str):
    """Récupère le statut d'une animation en cours"""
    try:
        # Chercher dans le cache de progression d'abord
        if animation_id in progress_callbacks:
            progress = progress_callbacks[animation_id]
            return {
                "type": "progress",
                "data": progress
            }
        
        # Sinon chercher dans les animations terminées
        result = pipeline.get_animation_status(animation_id)
        if result:
            return {
                "type": "result",
                "data": result
            }
        
        raise HTTPException(status_code=404, detail="Animation non trouvée")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statut: {str(e)}")

@app.post("/generate-quick")
async def generate_quick_animation(theme: str, duration: int):
    """Endpoint simplifié pour génération rapide"""
    try:
        # Valider les paramètres
        if theme not in ["space", "nature", "adventure", "animals", "magic", "friendship"]:
            raise HTTPException(status_code=400, detail="Thème non supporté")
        
        if duration not in [30, 60, 120, 180, 240, 300]:
            raise HTTPException(status_code=400, detail="Durée non supportée")
        
        # Créer la requête
        request = AnimationRequest(
            theme=AnimationTheme(theme),
            duration=AnimationDuration(duration)
        )
        
        # Générer
        result = await pipeline.generate_animation(request)
        
        return {
            "animation_id": result.animation_id,
            "status": result.status.value,
            "final_video_url": result.final_video_url,
            "processing_time": result.processing_time,
            "story_idea": result.story_idea.dict() if result.story_idea else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapide: {str(e)}")

@app.get("/health")
async def health_check():
    """Vérification rapide de santé du service"""
    try:
        health = await pipeline.validate_pipeline_health()
        return {
            "status": "healthy" if health["pipeline_operational"] else "degraded",
            "services": health["services"],
            "timestamp": pipeline.active_animations
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.delete("/cleanup")
async def cleanup_old_animations():
    """Nettoie les anciennes animations (endpoint admin)"""
    try:
        initial_count = len(pipeline.active_animations)
        pipeline.cleanup_old_animations(max_age_hours=6)  # 6 heures
        final_count = len(pipeline.active_animations)
        
        return {
            "message": "Nettoyage effectué",
            "animations_removed": initial_count - final_count,
            "remaining_animations": final_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur nettoyage: {str(e)}")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Ajouter le répertoire backend au PYTHONPATH
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    print(f"🚀 Démarrage sur http://{config.HOST}:{config.PORT}")
    uvicorn.run(
        app,  # Utiliser l'objet app directement
        host=config.HOST,
        port=config.PORT,
        reload=False,  # Désactivé pour éviter les conflits d'imports
        log_level="warning",  # Mode rapide
        access_log=False      # Désactiver logs d'accès
    ) 