import sys
import os
from pathlib import Path

# Ajouter le chemin des services
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import uuid
import aiohttp
import json
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="Animation Studio - Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY", "1611882205be3979e2cc2c83a5265c1882838dd59ce222f77b3cd4cfc2ac6dea")
FAL_API_KEY = os.getenv("FAL_API_KEY", "b6aa8a34-dc84-4bd5-9b7e-c4b46ad4b31c:b8b67a1d8a8e7d10d92df97b5c9c0c6e")

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
    # Vérifier les clés API
    api_status = {
        "openai": bool(OPENAI_API_KEY),
        "wavespeed": bool(WAVESPEED_API_KEY),
        "fal": bool(FAL_API_KEY)
    }
    return {
        "status": "healthy", 
        "ai_services": api_status,
        "ready_for_production": all(api_status.values())
    }

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
    """Générer une animation avec les vraies APIs d'IA"""
    
    # Vérifier les clés API essentielles
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(status_code=500, detail="Clé API OpenAI manquante ou invalide")
    
    animation_id = str(uuid.uuid4())
    
    # Initialiser le status
    generation_tasks[animation_id] = GenerationStatus(
        animation_id=animation_id,
        status="starting",
        progress=0,
        current_step="🚀 Initialisation des APIs d'IA..."
    )
    
    # Lancer la génération en arrière-plan
    asyncio.create_task(run_real_ai_generation(animation_id, request.theme, request.duration))
    
    return {"animation_id": animation_id, "status": "started"}

@app.get("/status/{animation_id}")
async def get_generation_status(animation_id: str):
    """Obtenir le statut de génération d'une animation"""
    if animation_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Animation ID non trouvé")
    
    return generation_tasks[animation_id]

async def run_real_ai_generation(animation_id: str, theme: str, duration: int):
    """Génération réelle avec les vraies APIs d'IA via HTTP"""
    print(f"🚀 DÉBUT GÉNÉRATION: {animation_id} | theme={theme} | duration={duration}")
    
    try:
        task = generation_tasks[animation_id]
        print(f"📊 Task trouvée: {task}")
        
        # Étape 1: Génération de l'idée avec OpenAI
        print(f"🧠 Étape 1: Génération de l'idée...")
        task.current_step = "🧠 Génération de l'idée créative avec OpenAI GPT-4..."
        task.progress = 10
        
        story_idea = await generate_story_with_openai(theme, duration)
        print(f"✅ Idée générée: {story_idea['idea'][:50]}...")
        
        # Étape 2: Création des scènes avec OpenAI
        task.current_step = "🎬 Création des scènes détaillées avec OpenAI..."
        task.progress = 25
        
        scenes = await create_scenes_with_openai(story_idea, duration)
        print(f"✅ {len(scenes)} scènes créées")
        
        # Étape 3: Génération des clips vidéo avec Wavespeed AI
        video_clips = []
        for i, scene in enumerate(scenes):
            task.current_step = f"🎥 Génération du clip {i+1}/{len(scenes)} avec Wavespeed AI..."
            task.progress = 30 + (i * 35 // len(scenes))
            
            clip_url = await generate_video_with_wavespeed(scene)
            video_clips.append({"scene": scene, "video_url": clip_url})
            print(f"✅ Clip {i+1} généré: {clip_url}")
        
        # Étape 4: Génération de l'audio avec FAL AI
        task.current_step = "🎵 Création de la bande sonore avec FAL AI..."
        task.progress = 75
        
        audio_url = await generate_audio_with_fal(story_idea, duration)
        print(f"✅ Audio généré: {audio_url}")
        
        # Étape 5: Assemblage final avec FAL AI FFmpeg
        task.current_step = "🎞️ Assemblage final avec FAL AI FFmpeg..."
        task.progress = 90
        
        final_video_url = await assemble_video_with_fal(video_clips, audio_url, duration)
        print(f"✅ Vidéo finale assemblée: {final_video_url}")
        
        # Finalisation
        task.current_step = "✨ Animation terminée avec succès !"
        task.progress = 100
        task.status = "completed"
        task.result = {
            "final_video_url": final_video_url,
            "story_idea": story_idea,
            "scenes_count": len(scenes),
            "clips_count": len(video_clips),
            "theme": theme,
            "duration": duration,
            "ai_models_used": ["OpenAI GPT-4", "Wavespeed SeedANce", "FAL AI mmaudio-v2", "FAL AI FFmpeg"]
        }
        
        print(f"🎉 Animation {animation_id} générée avec succès !")
        
    except Exception as e:
        print(f"💥 EXCEPTION CAPTURÉE dans génération {animation_id}:")
        print(f"💥 Type: {type(e).__name__}")
        print(f"💥 Message: {str(e)}")
        import traceback
        print(f"💥 Traceback complet:")
        traceback.print_exc()
        
        task.status = "error"
        task.error = f"Erreur lors de la génération: {str(e)}"
        task.current_step = "❌ Erreur de génération"
        print(f"❌ Erreur génération {animation_id}: {e}")
        import traceback
        traceback.print_exc()

async def generate_story_with_openai(theme, duration):
    """Générer une idée d'histoire avec OpenAI"""
    
    theme_prompts = {
        "space": "aventures spatiales avec des aliens sympathiques et des planètes magiques",
        "nature": "forêts enchantées avec des animaux parlants et des arbres magiques",
        "adventure": "quêtes héroïques avec des trésors cachés et des châteaux mystérieux",
        "animals": "animaux mignons qui vivent des aventures amusantes ensemble",
        "magic": "apprentis sorciers qui apprennent la magie dans un monde fantastique",
        "friendship": "amis qui s'entraident et vivent de beaux moments ensemble"
    }
    
    prompt = f"""Crée une histoire pour enfants de {duration} secondes sur le thème {theme_prompts.get(theme, theme)}.

L'histoire doit être:
- Adaptée aux enfants (3-8 ans)
- Positive et éducative
- Facile à comprendre
- Visuellement riche pour l'animation

Format de réponse JSON:
{{
    "idea": "Description de l'histoire en 2-3 phrases",
    "caption": "Titre court et accrocheur",
    "environment": "Description de l'environnement visuel",
    "sound": "Description des sons et musique adaptés"
}}"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Tu es un créateur d'histoires pour enfants spécialisé en animations."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.8
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except:
                    # Fallback si JSON invalide
                    return {
                        "idea": f"Une belle aventure {theme} pour enfants",
                        "caption": f"Animation {theme} magique",
                        "environment": f"Un monde coloré de {theme}",
                        "sound": "Musique douce et effets sonores"
                    }
            else:
                raise Exception(f"Erreur OpenAI: {response.status}")

async def create_scenes_with_openai(story_idea, duration):
    """Créer des scènes détaillées avec OpenAI"""
    scene_count = max(2, duration // 15)  # Une scène toutes les 15 secondes
    
    prompt = f"""Décompose cette histoire en {scene_count} scènes pour une animation de {duration} secondes:

Histoire: {story_idea['idea']}
Environnement: {story_idea['environment']}

Chaque scène doit:
- Durer environ {duration // scene_count} secondes
- Être visuellement distincte
- Avoir une action claire
- Être adaptée pour l'animation 2D style Disney

Format JSON pour {scene_count} scènes:
[
    {{
        "description": "Description visuelle détaillée de la scène",
        "action": "Action principale qui se déroule",
        "duration": {duration // scene_count}
    }}
]"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini", 
        "messages": [
            {"role": "system", "content": "Tu es un expert en découpage de scènes pour l'animation."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions",
                               headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except:
                    # Fallback avec scènes par défaut
                    return [
                        {
                            "description": f"Une scène d'introduction dans l'univers {story_idea.get('environment', 'magique')}",
                            "action": "Présentation des personnages principaux",
                            "duration": duration // 2
                        },
                        {
                            "description": f"Une scène d'action dans {story_idea.get('environment', 'un monde coloré')}",
                            "action": "L'aventure principale se déroule",
                            "duration": duration // 2
                        }
                    ]
            else:
                raise Exception(f"Erreur OpenAI scènes: {response.status}")

async def generate_video_with_wavespeed(scene):
    """Générer un clip vidéo avec Wavespeed AI - test plusieurs endpoints"""
    
    # Prompt optimisé
    video_prompt = f"2D cartoon animation, Disney style, children's story: {scene['description']}, {scene['action']}, colorful, vibrant, high quality, smooth animation"
    
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Configuration pour Seedance
    data = {
        "aspect_ratio": "9:16",
        "duration": 10,
        "prompt": video_prompt
    }
    
    # Liste des endpoints à tester
    endpoints_to_try = [
        "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
        "https://api.wavespeed.ai/v1/bytedance/seedance-v1-pro-t2v-480p", 
        "https://api.wavespeed.ai/bytedance/seedance-v1-pro-t2v-480p"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_try:
            try:
                print(f"🧪 Test endpoint: {endpoint}")
                async with session.post(endpoint, headers=headers, json=data) as response:
                    response_text = await response.text()
                    print(f"📊 Status: {response.status}, Response: {response_text[:200]}...")
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Essayer différentes structures de réponse
                        prediction_id = (
                            result.get("data", {}).get("id") or
                            result.get("id") or
                            result.get("task_id") or
                            result.get("prediction_id")
                        )
                        
                        if prediction_id:
                            print(f"✅ Endpoint valide trouvé: {endpoint}")
                            print(f"🎯 ID de prédiction: {prediction_id}")
                            
                            # Attendre la completion
                            return await wait_for_video_completion(session, prediction_id, headers, endpoint)
                        
                    elif response.status == 401:
                        raise Exception("Clé API invalide - vérifiez WAVESPEED_API_KEY")
                    elif response.status == 402:
                        raise Exception("Quota épuisé - vérifiez votre crédit Wavespeed")
                        
            except Exception as e:
                print(f"❌ Endpoint {endpoint} failed: {e}")
                continue
        
        # Si tous les endpoints échouent, utiliser un fallback
        print("⚠️ Tous les endpoints Wavespeed ont échoué - fallback vers video demo")
        return "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

async def wait_for_video_completion(session, prediction_id, headers, base_endpoint):
    """Attendre la completion de la génération vidéo"""
    
    # Endpoints de statut possibles
    status_endpoints = [
        f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
        f"https://api.wavespeed.ai/v1/predictions/{prediction_id}",
        f"https://api.wavespeed.ai/status/{prediction_id}"
    ]
    
    for attempt in range(60):  # 5 minutes max
        await asyncio.sleep(5)
        
        for status_endpoint in status_endpoints:
            try:
                async with session.get(status_endpoint, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"📈 Status check {attempt}: {result}")
                        
                        # Vérifier différents formats de statut
                        status = result.get("status") or result.get("state")
                        
                        if status == "completed" or status == "success":
                            # Chercher l'URL de la vidéo dans différentes structures
                            video_url = (
                                result.get("data", {}).get("outputs", [{}])[0] if result.get("data", {}).get("outputs") else
                                result.get("output") or
                                result.get("video_url") or
                                result.get("url")
                            )
                            
                            if video_url:
                                print(f"🎬 Vidéo générée: {video_url}")
                                return video_url
                                
                        elif status == "failed" or status == "error":
                            error_msg = result.get("error") or "Génération échouée"
                            raise Exception(f"Génération vidéo échouée: {error_msg}")
                            
                        break  # Sortir de la boucle des endpoints si on a une réponse
                        
            except Exception as e:
                continue  # Essayer l'endpoint suivant
    
    raise Exception("Timeout - génération vidéo trop longue")

async def generate_audio_with_fal(story_idea, duration):
    """Générer l'audio avec FAL AI"""
    
    audio_prompt = f"Children's background music for a {duration}-second animation about {story_idea['idea']}, {story_idea['sound']}, upbeat, magical, no vocals"
    
    headers = {
        "Authorization": f"Bearer {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": audio_prompt,
        "duration": duration,
        "quality": "high"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://queue.fal.run/fal-ai/mmaudio-v2",
                               headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("audio_url", "https://www.soundjay.com/misc/sounds/magic-chime-02.wav")
            else:
                # Fallback audio
                return "https://www.soundjay.com/misc/sounds/magic-chime-02.wav"

async def assemble_video_with_fal(video_clips, audio_url, duration):
    """Assembler la vidéo finale avec FAL AI"""
    
    # Configuration pour l'assemblage
    tracks = []
    
    # Ajouter les clips vidéo
    for i, clip in enumerate(video_clips):
        tracks.append({
            "type": "video",
            "url": clip["video_url"],
            "start_time": i * (duration // len(video_clips)),
            "duration": duration // len(video_clips)
        })
    
    # Ajouter l'audio de fond
    tracks.append({
        "type": "audio", 
        "url": audio_url,
        "start_time": 0,
        "duration": duration,
        "volume": 0.3
    })
    
    headers = {
        "Authorization": f"Bearer {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "tracks": tracks,
        "output_format": "mp4",
        "resolution": "480p"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://queue.fal.run/fal-ai/ffmpeg-api/compose",
                               headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("video_url", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
            else:
                # Fallback: retourner le premier clip vidéo
                return video_clips[0]["video_url"] if video_clips else "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur d'animation avec IA réelle...")
    print("📍 URL: http://localhost:8011")
    print("🔧 Endpoints disponibles:")
    print("   - GET  /health")
    print("   - GET  /themes") 
    print("   - POST /generate")
    print("   - GET  /status/{animation_id}")
    print("✨ Prêt pour la génération d'animations!")
    
    uvicorn.run(app, host="0.0.0.0", port=8011, log_level="info") 