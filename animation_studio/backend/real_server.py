from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import uuid
from datetime import datetime
import aiohttp
import json
import os
from pathlib import Path

# Import des services d'IA
from services.idea_generator import IdeaGenerator
from services.scene_creator import SceneCreator
from services.video_generator import VideoGenerator
from services.audio_generator import AudioGenerator
from services.video_assembler import VideoAssembler
from services.animation_pipeline import AnimationPipeline

app = FastAPI(title="Animation Studio - Real AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models pour les requêtes
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

# Stockage en mémoire des tâches de génération
generation_tasks = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "ai_services": "connected"}

@app.get("/themes")
async def get_themes():
    return {
        "themes": {
            "space": {
                "name": "Espace", 
                "description": "Aventures spatiales extraordinaires",
                "icon": "🚀",
                "elements": "Fusées, étoiles, planètes magiques"
            },
            "nature": {
                "name": "Nature", 
                "description": "Forêts enchantées et animaux merveilleux",
                "icon": "🌲",
                "elements": "Arbres, fleurs, rivières cristallines"
            },
            "adventure": {
                "name": "Aventure", 
                "description": "Quêtes héroïques et trésors cachés",
                "icon": "⚔️",
                "elements": "Héros, trésors, châteaux mystérieux"
            },
            "animals": {
                "name": "Animaux", 
                "description": "Petites créatures adorables et rigolotes",
                "icon": "🦊",
                "elements": "Animaux mignons, jeux, amitié"
            },
            "magic": {
                "name": "Magie", 
                "description": "Monde fantastique rempli de merveilles",
                "icon": "✨",
                "elements": "Sorciers, potions, sorts magiques"
            },
            "friendship": {
                "name": "Amitié", 
                "description": "Belles histoires d'amitié et de partage",
                "icon": "💖",
                "elements": "Amis, partage, moments joyeux"
            }
        },
        "durations": [30, 60, 120, 180, 240, 300],
        "default_duration": 30
    }

@app.post("/generate")
async def generate_animation(request: AnimationRequest):
    """Démarrer la génération d'une animation avec les vraies IA"""
    
    animation_id = str(uuid.uuid4())
    
    # Initialiser le status
    generation_tasks[animation_id] = GenerationStatus(
        animation_id=animation_id,
        status="starting",
        progress=0,
        current_step="Initialisation du système d'IA..."
    )
    
    # Lancer la génération en arrière-plan
    asyncio.create_task(run_animation_generation(animation_id, request.theme, request.duration))
    
    return {"animation_id": animation_id, "status": "started"}

@app.get("/status/{animation_id}")
async def get_generation_status(animation_id: str):
    """Obtenir le statut de génération d'une animation"""
    if animation_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Animation ID non trouvé")
    
    return generation_tasks[animation_id]

async def run_animation_generation(animation_id: str, theme: str, duration: int):
    """Processus principal de génération d'animation"""
    try:
        task = generation_tasks[animation_id]
        
        # Étape 1: Génération de l'idée
        task.current_step = "🧠 Génération de l'idée créative..."
        task.progress = 10
        
        idea_generator = IdeaGenerator()
        story_idea = await idea_generator.generate_story_idea(theme, duration)
        
        # Étape 2: Création des scènes
        task.current_step = "🎬 Création des scènes détaillées..."
        task.progress = 25
        
        scene_creator = SceneCreator()
        scenes = await scene_creator.create_scenes(story_idea, duration)
        
        # Étape 3: Génération des clips vidéo
        task.current_step = "🎥 Génération des clips vidéo..."
        task.progress = 40
        
        video_generator = VideoGenerator()
        video_clips = []
        
        for i, scene in enumerate(scenes):
            task.current_step = f"🎥 Génération du clip {i+1}/{len(scenes)}..."
            task.progress = 40 + (i * 30 // len(scenes))
            
            clip = await video_generator.generate_clip(scene)
            video_clips.append(clip)
        
        # Étape 4: Génération de l'audio
        task.current_step = "🎵 Création de la bande sonore..."
        task.progress = 75
        
        audio_generator = AudioGenerator()
        audio_track = await audio_generator.generate_audio(story_idea, duration)
        
        # Étape 5: Assemblage final
        task.current_step = "🎞️ Assemblage final de l'animation..."
        task.progress = 90
        
        video_assembler = VideoAssembler()
        final_video = await video_assembler.assemble_video(video_clips, audio_track, duration)
        
        # Finalisation
        task.current_step = "✨ Animation terminée !"
        task.progress = 100
        task.status = "completed"
        task.result = {
            "final_video_url": final_video.get("video_url"),
            "story_idea": story_idea.__dict__ if hasattr(story_idea, '__dict__') else story_idea,
            "scenes_count": len(scenes),
            "clips_count": len(video_clips),
            "generation_time": 120,  # Temps approximatif
            "theme": theme,
            "duration": duration
        }
        
    except Exception as e:
        task.status = "error"
        task.error = f"Erreur lors de la génération: {str(e)}"
        task.current_step = "❌ Erreur de génération"
        print(f"Erreur génération {animation_id}: {e}")

@app.post("/generate-quick")
async def generate_quick_demo(theme: str, duration: int):
    """Version de démonstration rapide (pour les tests)"""
    return {
        "animation_id": "demo-123",
        "status": "completed",
        "final_video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_5mb.mp4",
        "processing_time": 60,
        "story_idea": {
            "idea": f"Une aventure magique dans l'univers {theme}",
            "caption": f"Animation {theme} créée avec l'IA ! #animation #{theme}",
            "environment": f"Un monde coloré de {theme}",
            "sound": "Musique douce et effets sonores mélodieux"
        }
    }

if __name__ == "__main__":
    print("🚀 Animation Studio - Serveur IA complet - Port 8007")
    print("🤖 Services IA: OpenAI + Wavespeed + FAL")
    uvicorn.run(app, host="0.0.0.0", port=8007) 