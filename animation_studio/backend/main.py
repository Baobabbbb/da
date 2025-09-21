import asyncio
import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
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
from services.real_animation_generator import RealAnimationGenerator

# Import des modules d'authentification JWT
try:
    from utils.jwt_auth import jwt_auth, JWTBearer, get_current_user
    from services.auth_service import auth_service
    from schemas.auth import (
        LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
        RefreshTokenResponse, LogoutRequest, UserProfile, PasswordResetRequest,
        ProfileUpdateRequest
    )
except ImportError:
    # Fallback si les modules ne sont pas disponibles
    jwt_auth = None
    auth_service = None
    JWTBearer = None
    get_current_user = None
    # Créer des classes factices pour éviter les erreurs
    from pydantic import BaseModel
    class TokenResponse(BaseModel):
        pass
    class RefreshTokenResponse(BaseModel):
        pass
    class LoginRequest(BaseModel):
        pass
    class RegisterRequest(BaseModel):
        pass
    class RefreshTokenRequest(BaseModel):
        pass
    class LogoutRequest(BaseModel):
        pass
    class UserProfile(BaseModel):
        pass
    class PasswordResetRequest(BaseModel):
        pass
    class ProfileUpdateRequest(BaseModel):
        pass
    
    # Fonction factice pour get_current_user
    def get_current_user(request):
        return {"sub": "dummy", "email": "dummy@example.com"}

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
async def generate_quick_animation(request_body: dict):
    """Endpoint simplifié pour génération rapide - Compatible avec frontend"""
    try:
        # Extraire les paramètres du JSON body
        theme = request_body.get("theme", "space")
        duration = request_body.get("duration", 30)
        
        print(f"🎬 VRAIE Génération DA: {theme} / {duration}s")
        
        # Créer task ID
        import uuid
        import time
        task_id = str(uuid.uuid4())
        
        # Utiliser le nouveau générateur réel
        generator = RealAnimationGenerator()
        
        # Stocker les informations de la tâche
        if not hasattr(app.state, 'task_storage'):
            app.state.task_storage = {}
            
        app.state.task_storage[task_id] = {
            "start_time": time.time(),
            "theme": theme,
            "duration": duration,
            "status": "processing"
        }
        
        # Lancer la génération en arrière-plan
        import asyncio
        asyncio.create_task(generate_real_animation_task(task_id, theme, duration))
        
        return {
            "task_id": task_id,
            "status": "processing",
            "message": f"Animation '{theme}' en cours de génération RÉELLE avec APIs...",
            "estimated_time": "5-7 minutes",
            "theme": theme,
            "duration": duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapide: {str(e)}")

async def generate_real_animation_task(task_id: str, theme: str, duration: int):
    """Tâche en arrière-plan pour la génération réelle d'animation"""
    try:
        print(f"🚀 Démarrage génération réelle pour {task_id}")
        
        # Mettre à jour le statut
        app.state.task_storage[task_id]["status"] = "generating"
        
        # Créer le générateur réel
        generator = RealAnimationGenerator()
        
        # Générer l'animation complète (5-7 minutes)
        animation_result = await generator.generate_complete_animation(theme, duration)
        
        # Stocker le résultat
        app.state.task_storage[task_id]["result"] = animation_result
        app.state.task_storage[task_id]["status"] = "completed"
        
        print(f"✅ Animation {task_id} générée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur génération {task_id}: {e}")
        app.state.task_storage[task_id]["status"] = "failed" 
        app.state.task_storage[task_id]["error"] = str(e)

@app.get("/status/{task_id}")
async def get_animation_status(task_id: str):
    """Récupère le statut RÉEL d'une tâche d'animation"""
    try:
        # Vérifier si la tâche existe
        if not hasattr(app.state, 'task_storage') or task_id not in app.state.task_storage:
            raise HTTPException(status_code=404, detail="Tâche non trouvée")
        
        task_info = app.state.task_storage[task_id]
        status = task_info.get("status", "processing")
        
        print(f"📊 Statut RÉEL demandé pour {task_id}: {status}")
        
        if status == "processing" or status == "generating":
            # Encore en traitement RÉEL
            import time
            current_time = time.time()
            elapsed_seconds = current_time - task_info["start_time"]
            
            # Estimation temps réel : 5-7 minutes
            estimated_duration = 400  # 6.5 minutes
            progress = min(int((elapsed_seconds / estimated_duration) * 100), 95)
            
            return {
                "type": "result", 
                "data": {
                    "task_id": task_id,
                    "status": "processing",
                    "progress": progress,
                    "message": f"Génération RÉELLE en cours... {progress}%",
                    "estimated_remaining": max(int(estimated_duration - elapsed_seconds), 30)
                }
            }
            
        elif status == "completed":
            # Animation RÉELLE terminée !
            animation_result = task_info.get("result", {})
            return {
                "type": "result",
                "data": animation_result
            }
            
        elif status == "failed":
            # Erreur de génération
            error_msg = task_info.get("error", "Erreur inconnue")
            return {
                "type": "result",
                "data": {
                    "task_id": task_id,
                    "status": "failed",
                    "error": error_msg,
                    "message": f"Échec de la génération: {error_msg}"
                }
            }
            
        else:
            # Statut inconnu
            return {
                "type": "result", 
                "data": {
                    "task_id": task_id,
                    "status": "unknown",
                    "message": f"Statut inconnu: {status}"
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statut: {str(e)}")

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

# === ROUTES D'AUTHENTIFICATION JWT ===

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Connexion utilisateur avec JWT tokens"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    return await auth_service.authenticate_user(login_data)

@app.post("/auth/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest):
    """Inscription utilisateur avec JWT tokens"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    return await auth_service.register_user(register_data)

@app.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Rafraîchir un access token avec un refresh token"""
    if not jwt_auth:
        raise HTTPException(status_code=500, detail="Service JWT non disponible")
    
    return jwt_auth.refresh_access_token(refresh_data.refresh_token)

@app.post("/auth/logout")
async def logout(logout_data: LogoutRequest):
    """Déconnexion utilisateur en révoquant les tokens"""
    if not jwt_auth:
        raise HTTPException(status_code=500, detail="Service JWT non disponible")
    
    try:
        # Vérifier le refresh token pour obtenir l'user_id
        payload = jwt_auth.verify_token(logout_data.refresh_token)
        user_id = payload.get("sub")
        
        if user_id:
            jwt_auth.revoke_refresh_token(user_id)
        
        return {"message": "Déconnexion réussie"}
    except Exception as e:
        # Même en cas d'erreur, on considère la déconnexion comme réussie
        return {"message": "Déconnexion réussie"}

@app.get("/auth/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Récupérer le profil de l'utilisateur connecté"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    user_id = current_user.get("sub")
    return await auth_service.get_user_profile(user_id)

@app.put("/auth/profile", response_model=UserProfile)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour le profil de l'utilisateur connecté"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    user_id = current_user.get("sub")
    update_data = {}
    
    if profile_data.first_name is not None:
        update_data["first_name"] = profile_data.first_name
    if profile_data.last_name is not None:
        update_data["last_name"] = profile_data.last_name
    
    return await auth_service.update_user_profile(user_id, update_data)

@app.post("/auth/reset-password")
async def reset_password(reset_data: PasswordResetRequest):
    """Demander une réinitialisation de mot de passe"""
    if not auth_service:
        raise HTTPException(status_code=500, detail="Service d'authentification non disponible")
    
    await auth_service.reset_password(reset_data.email)
    return {"message": "Email de réinitialisation envoyé"}

@app.get("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Vérifier la validité d'un token"""
    return {
        "valid": True,
        "user_id": current_user.get("sub"),
        "email": current_user.get("email")
    }

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
    ) # FORCE RAILWAY REFRESH Sun, Sep 21, 2025  1:52:36 PM
