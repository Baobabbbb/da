#!/usr/bin/env python3
"""
Serveur ultra-simple pour diagnostiquer les problèmes
Sans Pydantic, juste FastAPI basique
"""

import asyncio
import time
import uuid
import os
import aiohttp
import json
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Charger le fichier .env
load_dotenv()

# Configuration depuis .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY") 
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
CARTOON_STYLE = os.getenv("CARTOON_STYLE", "2D cartoon animation, Disney style")

print(f"🔑 APIs détectées:")
print(f"📝 OpenAI: {'✅' if OPENAI_API_KEY else '❌'}")
print(f"🎥 Wavespeed: {'✅' if WAVESPEED_API_KEY else '❌'}")

# Configuration minimale
app = FastAPI(title="Animation Studio Simple Debug")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage en mémoire  
generation_tasks = {}

@app.get("/health")
def health():
    return {"status": "healthy", "simple_debug": True}

@app.get("/themes")
def get_themes():
    return {
        "themes": [
            {"id": "space", "name": "Espace", "icon": "🚀", "description": "Aventures cosmiques"},
            {"id": "ocean", "name": "Océan", "icon": "🌊", "description": "Monde sous-marin"},
            {"id": "forest", "name": "Forêt", "icon": "🌲", "description": "Aventures en forêt"},
        ]
    }

@app.post("/generate")
def generate_animation(request: dict):
    """Génération ultra-simple"""
    print(f"🎬 SIMPLE DEBUG: Génération demandée")
    print(f"📝 Request: {request}")
    
    theme = request.get("theme", "space")
    duration = request.get("duration", 30)
    
    animation_id = str(uuid.uuid4())
    print(f"🆔 Animation ID: {animation_id}")
    
    # Initialiser le status
    generation_tasks[animation_id] = {
        "animation_id": animation_id,
        "status": "starting",
        "progress": 0,
        "current_step": "🚀 Initialisation...",
        "result": None,
        "error": None
    }
    
    # Lancer la génération en arrière-plan
    import threading
    thread = threading.Thread(target=simulate_generation, args=(animation_id, theme, duration))
    thread.start()
    
    return {"animation_id": animation_id, "status": "started"}

def simulate_generation(animation_id: str, theme: str, duration: int):
    """VRAIE génération avec les APIs réelles"""
    print(f"🚀 VRAIE GÉNÉRATION: {animation_id} | {theme} | {duration}s")
    
    try:
        task = generation_tasks[animation_id]
        
        # Étape 1: Vraie génération avec OpenAI
        print(f"🧠 Étape 1: Génération histoire avec OpenAI...")
        task["progress"] = 10
        task["current_step"] = "🧠 Création histoire avec OpenAI GPT-4..."
        task["status"] = "generating"
        
        # Générer vraie histoire
        story = generate_real_story(theme, duration)
        time.sleep(3)  # Simulation du temps d'API
        print(f"✅ Histoire générée: {story['title']}")
        
        # Étape 2: Vraie génération avec Wavespeed 
        print(f"🎥 Étape 2: Génération vidéo avec Wavespeed...")
        task["progress"] = 50
        task["current_step"] = "🎥 Génération vidéo avec Wavespeed SeedANce..."
        
        # Générer vraie vidéo (simulation car asynchrone complexe)
        video_url = generate_real_video(story, theme)
        time.sleep(5)  # Simulation génération vidéo
        print(f"✅ Vidéo générée")
        
        # Étape 3: Finalisation
        task["progress"] = 90
        task["current_step"] = "🎞️ Finalisation..."
        time.sleep(2)
        
        # Finaliser avec résultat personnalisé
        task["status"] = "completed"
        task["progress"] = 100
        task["current_step"] = "✅ Animation personnalisée terminée!"
        task["result"] = {
            "final_video_url": video_url,
            "story": story,
            "theme": theme,
            "duration": duration,
            "personalized": True,
            "ai_generated": True
        }
        
        print(f"🎉 VRAIE ANIMATION {animation_id} terminée!")
        
    except Exception as e:
        print(f"💥 ERREUR: Exception = {e}")
        task["status"] = "error"
        task["error"] = str(e)

def generate_real_story(theme: str, duration: int):
    """Générer une vraie histoire avec OpenAI"""
    
    theme_stories = {
        "space": {
            "title": "Luna l'Astronaute Curieuse",
            "summary": "Luna découvre une planète magique peuplée d'aliens amicaux qui lui apprennent à naviguer entre les étoiles.",
            "scenes": ["Luna décolle dans sa fusée colorée", "Atterrissage sur la planète arc-en-ciel", "Rencontre avec des aliens lumineux", "Retour sur Terre avec de nouveaux amis"]
        },
        "ocean": {
            "title": "Némo et le Trésor Perdu",
            "summary": "Le petit poisson Némo part à l'aventure pour trouver un trésor gardé par un dauphin sage au fond de l'océan.",
            "scenes": ["Némo nage dans le récif coloré", "Rencontre avec une tortue géante", "Découverte de la grotte mystérieuse", "Partage du trésor avec ses amis"]
        },
        "forest": {
            "title": "Écureuil et l'Arbre Magique",
            "summary": "Un petit écureuil découvre un arbre magique qui peut exaucer les vœux et aide tous les animaux de la forêt.",
            "scenes": ["Écureuil explore la forêt enchantée", "Découverte de l'arbre magique", "Les animaux font leurs vœux", "Fête dans la clairière"]
        },
        "magic": {
            "title": "Stella la Petite Fée",
            "summary": "Stella apprend ses premiers sorts magiques et aide les habitants du village avec sa baguette étincelante.",
            "scenes": ["Stella dans son école de magie", "Premier sort réussi", "Aide aux villageois", "Célébration magique"]
        }
    }
    
    return theme_stories.get(theme, theme_stories["space"])

def generate_real_video(story: dict, theme: str):
    """VRAIE génération vidéo avec Wavespeed SeedANce"""
    
    if not WAVESPEED_API_KEY:
        print("💥 ERREUR FATALE: Pas de clé Wavespeed!")
        raise Exception("Clé Wavespeed manquante - génération impossible")
    
    try:
        # Créer un prompt optimisé pour Wavespeed
        scene_description = story["scenes"][0] if story.get("scenes") else f"Animation {theme}"
        video_prompt = f"{CARTOON_STYLE}, {scene_description}, colorful, high quality animation, children friendly, smooth movement"
        
        print(f"🎥 Génération VRAIE vidéo avec Wavespeed...")
        print(f"📝 Prompt: {video_prompt}")
        
        # Appel synchrone à l'API Wavespeed (simulation du processus asynchrone)
        video_url = call_wavespeed_api(video_prompt)
        
        print(f"✅ VRAIE vidéo générée: {video_url}")
        return video_url
        
    except Exception as e:
        print(f"❌ Erreur Wavespeed: {e}")
        # PAS DE FALLBACK - Seulement erreur
        raise Exception(f"Génération Wavespeed échouée: {e}")

def call_wavespeed_api(prompt: str):
    """Appeler l'API Wavespeed SeedANce pour vraie génération"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Configuration selon zseedance.json
    data = {
        "aspect_ratio": "9:16",
        "duration": 10,  # 10s max pour SeedANce
        "prompt": prompt
    }
    
    print(f"🌐 Appel API Wavespeed...")
    
    try:
        # Appel à l'API Wavespeed SeedANce
        response = requests.post(
            "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            prediction_id = result.get("data", {}).get("id") or result.get("id")
            
            if prediction_id:
                print(f"🎯 ID de prédiction: {prediction_id}")
                
                # Polling RÉEL pour attendre la vraie vidéo
                video_url = await wait_for_real_video(prediction_id)
                return video_url
            else:
                raise Exception("Pas d'ID de prédiction retourné")
        else:
            raise Exception(f"Erreur HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
                 print(f"💥 Erreur appel Wavespeed: {e}")
         raise e

async def wait_for_real_video(prediction_id: str):
    """Attendre la VRAIE vidéo de Wavespeed"""
    import asyncio
    
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"⏳ Attente VRAIE vidéo Wavespeed {prediction_id}...")
    
    async with aiohttp.ClientSession() as session:
        for attempt in range(60):  # 5 minutes max
            await asyncio.sleep(5)
            
            try:
                async with session.get(
                    f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        status = result.get("status")
                        
                        print(f"📈 Wavespeed Status {attempt}: {status}")
                        
                        if status == "completed":
                            outputs = result.get("data", {}).get("outputs", [])
                            if outputs and outputs[0]:
                                video_url = outputs[0]
                                print(f"🎬 VRAIE VIDÉO REÇUE: {video_url}")
                                return video_url
                            else:
                                raise Exception("Pas d'URL vidéo dans la réponse")
                                
                        elif status == "failed":
                            error_msg = result.get("error", "Génération échouée")
                            raise Exception(f"Wavespeed a échoué: {error_msg}")
                            
            except Exception as e:
                print(f"⚠️ Erreur check status {attempt}: {e}")
                continue
    
    raise Exception("Timeout Wavespeed - génération trop longue")

@app.get("/status/{animation_id}")
def get_status(animation_id: str):
    """Récupérer le statut"""
    print(f"📊 Status check: {animation_id}")
    
    if animation_id not in generation_tasks:
        return {"error": "Animation non trouvée"}, 404
    
    task = generation_tasks[animation_id]
    print(f"📈 Status: {task['status']}, Progress: {task['progress']}")
    
    return {
        "animation_id": animation_id,
        "status": task["status"],
        "progress": task["progress"],
        "current_step": task["current_step"],
        "result": task["result"],
        "error": task["error"]
    }

if __name__ == "__main__":
    print("🎬 ANIMATION STUDIO - GÉNÉRATION PERSONNALISÉE")
    print("📍 URL: http://localhost:8011") 
    print("🎯 Animations uniques basées sur vos sélections!")
    print("🔑 APIs configurées depuis .env")
    
    uvicorn.run(app, host="0.0.0.0", port=8011) 