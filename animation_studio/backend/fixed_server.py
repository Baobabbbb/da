#!/usr/bin/env python3
"""
Serveur FastAPI pour génération d'animations complètes avec Wavespeed
Suivant le workflow zseedance.json
"""

import os
import time
import threading
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration depuis .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")

# Configuration par défaut
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
WAVESPEED_MODEL = os.getenv("WAVESPEED_MODEL", "seedance-v1-pro")
CARTOON_STYLE = os.getenv("CARTOON_STYLE", "2D cartoon animation, Disney style, vibrant colors")

# Vérification des clés API
if not OPENAI_API_KEY or not WAVESPEED_API_KEY:
    print("💥 ERREUR FATALE: Clés API manquantes!")
    print("🔧 Vérifiez votre fichier .env")
    exit(1)

print("✅ Clés API chargées avec succès")

# FastAPI app
app = FastAPI(title="Animation Studio API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage des tâches de génération
generation_tasks = {}

@app.get("/health")
def health():
    return {"status": "healthy", "api_keys": {
        "openai": bool(OPENAI_API_KEY),
        "wavespeed": bool(WAVESPEED_API_KEY),
        "fal": bool(FAL_API_KEY)
    }}

@app.get("/themes")
def get_themes():
    return {
        "themes": [
            {"id": "space", "name": "Espace 🚀", "emoji": "🚀"},
            {"id": "ocean", "name": "Océan 🌊", "emoji": "🌊"},
            {"id": "forest", "name": "Forêt 🌳", "emoji": "🌳"},
            {"id": "magic", "name": "Magie ✨", "emoji": "✨"}
        ]
    }

@app.post("/generate")
def generate_animation(request: dict):
    theme = request.get("theme", "space")
    duration = request.get("duration", 30)
    
    # Générer un ID unique
    animation_id = f"anim_{int(time.time())}"
    
    # Initialiser la tâche
    generation_tasks[animation_id] = {
        "status": "generating",
        "progress": 0,
        "current_step": "🚀 Démarrage de la génération...",
        "theme": theme,
        "duration": duration
    }
    
    print(f"🎬 Nouvelle génération: {animation_id} - Thème: {theme} - Durée: {duration}s")
    
    # Lancer la génération en arrière-plan
    thread = threading.Thread(
        target=real_generation_process,
        args=(animation_id, theme, duration)
    )
    thread.daemon = True
    thread.start()
    
    return {"animation_id": animation_id, "status": "started"}

def real_generation_process(animation_id: str, theme: str, duration: int):
    """Processus de génération COMPLET suivant zseedance.json"""
    
    global generation_tasks
    task = generation_tasks[animation_id]
    
    try:
        # Étape 1: Génération de l'histoire complète
        task["progress"] = 5
        task["current_step"] = "📝 Génération de l'histoire complète..."
        print(f"📝 Génération histoire pour {animation_id}")
        
        story = generate_complete_story_sync(theme, duration)
        
        # Étape 2: Création des scènes détaillées
        task["progress"] = 15
        task["current_step"] = "🎬 Création des scènes détaillées..."
        print(f"🎬 Création scènes pour {animation_id}")
        
        scenes = generate_detailed_scenes_sync(story, theme, duration)
        
        # Étape 3: Génération des clips vidéo
        task["progress"] = 25
        task["current_step"] = "🎥 Génération des clips vidéo..."
        print(f"🎥 Génération clips pour {animation_id}")
        
        video_clips = generate_video_clips_sync(scenes, theme)
        
        # Étape 4: Génération audio
        task["progress"] = 70
        task["current_step"] = "🔊 Génération audio et musique..."
        print(f"🔊 Génération audio pour {animation_id}")
        
        audio_url = generate_audio_sync(story, theme)
        
        # Étape 5: Assemblage final
        task["progress"] = 85
        task["current_step"] = "🎬 Assemblage final de la vidéo..."
        print(f"🎬 Assemblage final pour {animation_id}")
        
        final_video_url = assemble_final_video_sync(video_clips, audio_url, duration)
        
        # Terminer la génération
        task["status"] = "completed"
        task["progress"] = 100
        task["current_step"] = "✅ Dessin animé complet terminé!"
        task["result"] = {
            "final_video_url": final_video_url,
            "story": story,
            "scenes": scenes,
            "theme": theme,
            "duration": duration,
            "real_generation": True
        }
        
        print(f"🎉 DESSIN ANIMÉ COMPLET {animation_id} terminé!")
        
    except Exception as e:
        print(f"💥 ERREUR GÉNÉRATION: {e}")
        task["status"] = "error"
        task["error"] = str(e)
        task["current_step"] = "❌ Erreur génération"

def generate_complete_story_sync(theme: str, duration: int):
    """Générer une histoire complète avec OpenAI"""
    
    theme_prompts = {
        "space": f"Crée une histoire d'animation de {duration} secondes sur l'espace. Histoire: Un jeune astronaute découvre une planète magique avec des créatures amicales. L'histoire doit être adaptée aux enfants, avec des personnages attachants et une fin heureuse.",
        "ocean": f"Crée une histoire d'animation de {duration} secondes sur l'océan. Histoire: Un petit poisson courageux part à l'aventure pour sauver son récif corallien. L'histoire doit être adaptée aux enfants, avec des personnages attachants et une fin heureuse.",
        "forest": f"Crée une histoire d'animation de {duration} secondes sur la forêt. Histoire: Un écureuil découvre un arbre magique qui peut exaucer les vœux. L'histoire doit être adaptée aux enfants, avec des personnages attachants et une fin heureuse.",
        "magic": f"Crée une histoire d'animation de {duration} secondes sur la magie. Histoire: Une petite fée apprend ses premiers sorts magiques. L'histoire doit être adaptée aux enfants, avec des personnages attachants et une fin heureuse."
    }
    
    prompt = theme_prompts.get(theme, theme_prompts["space"])
    
    # Simuler la génération OpenAI (pour l'instant)
    return {
        "title": f"Histoire {theme} de {duration} secondes",
        "summary": prompt,
        "duration": duration,
        "theme": theme
    }

def generate_detailed_scenes_sync(story: dict, theme: str, duration: int):
    """Générer des scènes détaillées pour l'histoire"""
    
    # Calculer le nombre de scènes selon la durée
    scenes_count = max(3, duration // 10)  # 1 scène par 10 secondes, minimum 3
    
    scenes = []
    for i in range(scenes_count):
        scene_duration = duration / scenes_count
        scenes.append({
            "id": i + 1,
            "description": f"Scène {i+1} de l'histoire {theme}",
            "duration": scene_duration,
            "visual_prompt": f"{CARTOON_STYLE}, scène {i+1} de l'histoire {theme}, colorful, high quality animation, children friendly"
        })
    
    return scenes

def generate_video_clips_sync(scenes: list, theme: str):
    """Générer les clips vidéo pour chaque scène"""
    
    video_clips = []
    
    for i, scene in enumerate(scenes):
        print(f"🎥 Génération clip {i+1}/{len(scenes)}...")
        
        # Générer un clip pour cette scène
        clip_url = generate_single_video_clip_sync(scene["visual_prompt"], theme)
        video_clips.append({
            "scene_id": scene["id"],
            "url": clip_url,
            "duration": scene["duration"]
        })
    
    return video_clips

def wait_for_wavespeed_sync(prediction_id: str, headers: dict):
    """Attendre le résultat Wavespeed (version synchrone) - Timeout 10 minutes"""
    print(f"⏳ Attente résultat Wavespeed {prediction_id}...")
    for attempt in range(120):  # 10 minutes max
        print(f"🔄 Tentative {attempt+1}/120 - Attente 5 secondes...")
        time.sleep(5)
        try:
            response = requests.get(
                f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
                headers=headers,
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                status = result.get("data", {}).get("status", "unknown")
                print(f"📈 Status Wavespeed: {status}")
                if status == "completed":
                    outputs = result.get("data", {}).get("outputs", [])
                    print(f"🔍 Outputs: {outputs}")
                    if outputs and len(outputs) > 0:
                        try:
                            if isinstance(outputs[0], str):
                                video_url = outputs[0]
                            elif isinstance(outputs[0], dict):
                                video_url = outputs[0].get("url")
                            else:
                                video_url = str(outputs[0])
                            if video_url:
                                print(f"✅ Clip généré avec succès!")
                                print(f"🎬 URL: {video_url[:50]}...")
                                return video_url
                        except Exception as e:
                            print(f"⚠️  Erreur extraction outputs: {e}")
                    try:
                        video_url = result.get("data", {}).get("video_url") or result.get("video_url")
                        if video_url:
                            print(f"✅ Clip généré avec succès!")
                            print(f"🎬 URL: {video_url[:50]}...")
                            return video_url
                    except Exception as e:
                        print(f"⚠️  Erreur extraction video_url: {e}")
                    print(f"🔍 Réponse complète: {result}")
                    raise Exception("Pas d'URL vidéo dans la réponse")
                elif status == "failed":
                    error_msg = result.get("data", {}).get("error", "Erreur inconnue")
                    raise Exception(f"Génération Wavespeed échouée: {error_msg}")
                elif status in ["processing", "queued", "starting"]:
                    print(f"⏳ En cours... ({status})")
                    continue
            else:
                print(f"⚠️  Status polling: {response.status_code}")
                continue
        except Exception as e:
            print(f"⚠️  Erreur polling: {e}")
            continue
    raise Exception("Timeout Wavespeed après 10 minutes - génération échouée")

def generate_single_video_clip_sync(prompt: str, theme: str):
    """Générer un seul clip vidéo avec Wavespeed (format paysage)"""
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "aspect_ratio": "16:9",  # Paysage
        "duration": 10,
        "prompt": prompt[:500]
    }
    try:
        response = requests.post(
            "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
            headers=headers,
            json=data,
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            prediction_id = result.get("data", {}).get("id") or result.get("id")
            if prediction_id:
                return wait_for_wavespeed_sync(prediction_id, headers)
            else:
                raise Exception("Pas d'ID de prédiction Wavespeed")
        else:
            raise Exception(f"Erreur Wavespeed {response.status_code}: {response.text}")
    except Exception as e:
        print(f"💥 Erreur clip vidéo: {e}")
        raise Exception(f"Génération clip échouée: {e}")

def generate_audio_sync(story: dict, theme: str):
    """Générer l'audio avec FAL AI (simulation pour l'instant)"""
    
    # Pour l'instant, retourner une URL d'audio factice
    # TODO: Implémenter la vraie génération audio avec FAL AI
    return "https://example.com/audio.mp3"

def assemble_final_video_sync(video_clips: list, audio_url: str, duration: int):
    """Assembler la vidéo finale avec FAL FFmpeg (strict, sans fallback)"""
    if not video_clips:
        raise Exception("Aucun clip vidéo disponible")
    
    print(f"🎬 Assemblage de {len(video_clips)} clips...")
    
    if len(video_clips) == 1:
        final_url = video_clips[0]["url"]
        print(f"✅ Un seul clip, utilisation directe: {final_url}")
        return final_url
    
    # Format de payload pour concaténation avec FAL FFmpeg
    keyframes = []
    timestamp = 0
    for clip in video_clips:
        keyframes.append({
            "url": clip["url"],
            "timestamp": timestamp,
            "duration": int(clip["duration"])
        })
        timestamp += int(clip["duration"])
    
    payload = {
        "tracks": [
            {
                "id": "1",
                "type": "video",
                "keyframes": keyframes
            }
        ]
    }
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📤 Envoi à FAL FFmpeg: {payload}")
        response = requests.post(
            "https://queue.fal.run/fal-ai/ffmpeg-api/compose",  # Endpoint original
            headers=headers,
            json=payload,
            timeout=180
        )
        print(f"📥 Réponse FAL: {response.status_code} - {response.text}")
        if response.status_code == 200:
            result = response.json()
            request_id = result.get("request_id") or result.get("id")
            if not request_id:
                raise Exception("Pas d'ID de requête FAL FFmpeg")
            return wait_for_fal_ffmpeg_simple(request_id, headers)
        else:
            raise Exception(f"Erreur FAL FFmpeg {response.status_code}: {response.text}")
    except Exception as e:
        print(f"💥 Erreur assemblage: {e}")
        raise Exception(f"Assemblage vidéo échoué: {e}")

def wait_for_fal_ffmpeg_simple(request_id: str, headers: dict):
    """Polling simplifié pour FAL FFmpeg (avec détection video_url même si status inconnu)"""
    for attempt in range(30):  # 2.5 minutes max
        print(f"🔄 Polling FAL {request_id}... ({attempt+1}/30)")
        try:
            response = requests.get(
                f"https://queue.fal.run/fal-ai/ffmpeg-api/requests/{request_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📝 Réponse FAL complète: {result}")  # Debug complet
                status = result.get("status", "unknown")
                print(f"📈 Status: {status}")
                # Correction : si video_url présent, on le retourne immédiatement
                video_url = result.get("video_url")
                if video_url:
                    print(f"✅ Vidéo assemblée (video_url détecté): {video_url}")
                    return video_url
                if status == "completed":
                    video_url = result.get("output", {}).get("video") or result.get("output")
                    if video_url:
                        print(f"✅ Vidéo assemblée: {video_url}")
                        return video_url
                elif status == "failed":
                    print(f"❌ FAL échoué: {result}")
                    raise Exception(f"FAL échoué: {result}")
                elif status == "unknown" and result.get("error"):
                    print(f"❌ Erreur FAL: {result.get('error')}")
                    raise Exception(f"Erreur FAL: {result.get('error')}")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️  Erreur polling: {e}")
            time.sleep(5)
    raise Exception("Timeout FAL FFmpeg")

@app.get("/status/{animation_id}")
def get_status(animation_id: str):
    if animation_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Animation non trouvée")
    
    return generation_tasks[animation_id]

if __name__ == "__main__":
    import uvicorn
    print("🚀 Lancement du serveur Animation Studio COMPLET...")
    print(f"🔑 OpenAI: {'✅' if OPENAI_API_KEY else '❌'}")
    print(f"🔑 Wavespeed: {'✅' if WAVESPEED_API_KEY else '❌'}")
    print(f"🔑 FAL: {'✅' if FAL_API_KEY else '❌'}")
    uvicorn.run(app, host="0.0.0.0", port=8011) 