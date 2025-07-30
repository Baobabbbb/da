#!/usr/bin/env python3
"""
Serveur de debug pour Animation Studio
Version simplifiée pour diagnostiquer les problèmes
"""

import asyncio
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configuration simple
app = FastAPI(title="Animation Studio Debug")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class AnimationRequest(BaseModel):
    theme: str
    duration: int

class GenerationStatus(BaseModel):
    animation_id: str
    status: str
    progress: int
    current_step: str
    result: dict = None
    error: str = None

# Storage en mémoire
generation_tasks = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "debug": True}

@app.get("/themes")
async def get_themes():
    return {
        "themes": [
            {"id": "space", "name": "Espace", "icon": "🚀", "description": "Aventures cosmiques"},
            {"id": "ocean", "name": "Océan", "icon": "🌊", "description": "Monde sous-marin"},
            {"id": "forest", "name": "Forêt", "icon": "🌲", "description": "Aventures en forêt"},
        ]
    }

@app.post("/generate")
async def generate_animation(request: AnimationRequest):
    """Version debug - génération simulée avec logs détaillés"""
    print(f"🎬 DEBUG: Nouvelle génération demandée")
    print(f"📝 DEBUG: Request data = {request}")
    
    animation_id = str(uuid.uuid4())
    print(f"🆔 DEBUG: Animation ID créé = {animation_id}")
    
    # Initialiser le status
    generation_tasks[animation_id] = GenerationStatus(
        animation_id=animation_id,
        status="starting",
        progress=0,
        current_step="🚀 DEBUG: Initialisation..."
    )
    
    print(f"📊 DEBUG: Status initialisé")
    
    # Lancer une tâche de debug
    try:
        task = asyncio.create_task(debug_generation(animation_id, request.theme, request.duration))
        print(f"✅ DEBUG: Tâche créée = {task}")
    except Exception as e:
        print(f"❌ DEBUG: Erreur création tâche = {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {e}")
    
    return {"animation_id": animation_id, "status": "started"}

async def debug_generation(animation_id: str, theme: str, duration: int):
    """Génération de debug avec progression simulée"""
    print(f"🚀 DEBUG: Début génération {animation_id}")
    
    try:
        task = generation_tasks[animation_id]
        
        # Simulation des étapes
        steps = [
            (10, "🧠 DEBUG: Test OpenAI..."),
            (30, "🎬 DEBUG: Test création scènes..."),
            (60, "🎥 DEBUG: Test Wavespeed..."),
            (80, "🎵 DEBUG: Test FAL Audio..."),
            (95, "🎞️ DEBUG: Test assemblage..."),
        ]
        
        for progress, step in steps:
            print(f"📈 DEBUG: {step}")
            task.progress = progress
            task.current_step = step
            task.status = "generating"
            await asyncio.sleep(2)  # Pause courte
        
        # Finaliser
        task.status = "completed"
        task.progress = 100
        task.current_step = "✅ DEBUG: Terminé!"
        task.result = {
            "final_video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "theme": theme,
            "duration": duration,
            "debug": True
        }
        
        print(f"🎉 DEBUG: Génération {animation_id} terminée")
        
    except Exception as e:
        print(f"💥 DEBUG: Exception = {e}")
        task.status = "error" 
        task.error = str(e)

@app.get("/status/{animation_id}")
async def get_status(animation_id: str):
    """Récupérer le statut d'une animation"""
    print(f"📊 DEBUG: Status check pour {animation_id}")
    
    if animation_id not in generation_tasks:
        print(f"❌ DEBUG: Animation {animation_id} non trouvée")
        raise HTTPException(status_code=404, detail="Animation non trouvée")
    
    task = generation_tasks[animation_id]
    print(f"📈 DEBUG: Status = {task.status}, Progress = {task.progress}")
    
    return {
        "animation_id": animation_id,
        "status": task.status,
        "progress": task.progress,
        "current_step": task.current_step,
        "result": task.result,
        "error": task.error
    }

if __name__ == "__main__":
    print("🔧 DEBUG SERVER - Animation Studio")
    print("📍 URL: http://localhost:8011")
    print("🚀 Démarrage...")
    
    uvicorn.run(app, host="0.0.0.0", port=8011, log_level="info") 