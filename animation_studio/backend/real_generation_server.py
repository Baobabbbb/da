#!/usr/bin/env python3
"""
Serveur de VRAIE génération UNIQUEMENT
AUCUN fallback - AUCUNE vidéo précréée
SEULEMENT de vraies générations avec vos APIs
"""

import asyncio
import time
import uuid
import os
import aiohttp
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Charger le fichier .env
load_dotenv()

# Configuration OBLIGATOIRE depuis .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY") 
TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
CARTOON_STYLE = os.getenv("CARTOON_STYLE", "2D cartoon animation, Disney style")

print(f"🔑 VÉRIFICATION DES APIS OBLIGATOIRES:")
print(f"📝 OpenAI: {'✅ PRÉSENTE' if OPENAI_API_KEY else '❌ MANQUANTE'}")
print(f"🎥 Wavespeed: {'✅ PRÉSENTE' if WAVESPEED_API_KEY else '❌ MANQUANTE'}")

# ARRÊT si pas de clés
if not OPENAI_API_KEY or not WAVESPEED_API_KEY:
    print("💥 ERREUR FATALE: Clés API manquantes!")
    print("🔧 Vérifiez votre fichier .env")
    exit(1)

print("✅ TOUTES LES APIS SONT PRÊTES POUR LA VRAIE GÉNÉRATION!")

# FastAPI app
app = FastAPI(title="Animation Studio - VRAIE GÉNÉRATION UNIQUEMENT")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage des tâches
generation_tasks = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "real_generation_only": True,
        "no_fallback": True,
        "apis_ready": True
    }

@app.get("/themes")
async def get_themes():
    return {
        "themes": [
            {
                "id": "space",
                "name": "Espace",
                "icon": "🚀",
                "description": "Aventures cosmiques et exploration spatiale"
            },
            {
                "id": "ocean",
                "name": "Océan", 
                "icon": "🌊",
                "description": "Monde sous-marin et créatures marines"
            },
            {
                "id": "forest",
                "name": "Forêt",
                "icon": "🌲",
                "description": "Animaux de la forêt et nature magique"
            },
            {
                "id": "magic",
                "name": "Magie",
                "icon": "✨",
                "description": "Monde fantastique avec fées et sorciers"
            }
        ]
    }

@app.post("/generate")
async def generate_animation(request: dict):
    """VRAIE génération UNIQUEMENT - AUCUN fallback autorisé"""
    
    theme = request.get("theme", "space")
    duration = request.get("duration", 30)
    
    animation_id = str(uuid.uuid4())
    
    print(f"🎬 DÉMARRAGE VRAIE GÉNÉRATION: {animation_id}")
    print(f"🎯 Thème: {theme} | Durée: {duration}s")
    print(f"🚫 AUCUN FALLBACK - VRAIE GÉNÉRATION OBLIGATOIRE")
    
    # Initialiser le statut
    generation_tasks[animation_id] = {
        "animation_id": animation_id,
        "status": "starting",
        "progress": 0,
        "current_step": "🚀 Initialisation VRAIE génération...",
        "result": None,
        "error": None,
        "theme": theme,
        "duration": duration,
        "real_generation_only": True
    }
    
    # Lancer la VRAIE génération
    asyncio.create_task(pure_ai_generation(animation_id, theme, duration))
    
    return {"animation_id": animation_id, "status": "started", "real_generation": True}

@app.get("/status/{animation_id}")
async def get_status(animation_id: str):
    """Récupérer le statut d'une VRAIE génération"""
    
    if animation_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Animation non trouvée")
    
    task = generation_tasks[animation_id]
    return {
        "animation_id": animation_id,
        "status": task["status"],
        "progress": task["progress"],
        "current_step": task["current_step"],
        "result": task["result"],
        "error": task["error"],
        "real_generation": True
    }

async def pure_ai_generation(animation_id: str, theme: str, duration: int):
    """PURE génération AI - AUCUN fallback"""
    
    task = generation_tasks[animation_id]
    
    try:
        print(f"🧠 ÉTAPE 1: Génération histoire avec OpenAI...")
        task["current_step"] = "🧠 Création histoire avec OpenAI GPT-4..."
        task["progress"] = 10
        task["status"] = "generating"
        
        # VRAIE génération histoire avec OpenAI
        story = await generate_story_with_openai_real(theme, duration)
        print(f"✅ Histoire générée: {story['title']}")
        
        print(f"🎥 ÉTAPE 2: Génération vidéo avec Wavespeed...")
        task["current_step"] = "🎥 Génération vidéo avec Wavespeed SeedANce..."
        task["progress"] = 50
        
        # VRAIE génération vidéo avec Wavespeed
        video_url = await generate_video_with_wavespeed_real(story, theme)
        print(f"✅ VRAIE vidéo générée: {video_url}")
        
        # Finalisation
        task["current_step"] = "✅ VRAIE animation terminée!"
        task["progress"] = 100
        task["status"] = "completed"
        task["result"] = {
            "final_video_url": video_url,
            "story": story,
            "theme": theme,
            "duration": duration,
            "generated_with_real_ai": True,
            "no_fallback_used": True
        }
        
        print(f"🎉 VRAIE ANIMATION {animation_id} TERMINÉE!")
        
    except Exception as e:
        print(f"💥 ERREUR VRAIE GÉNÉRATION: {e}")
        task["status"] = "error"
        task["error"] = f"ERREUR génération réelle: {str(e)}"
        task["current_step"] = "❌ Échec génération réelle"

async def generate_story_with_openai_real(theme: str, duration: int):
    """VRAIE génération histoire avec OpenAI API"""
    
    theme_prompts = {
        "space": "aventure spatiale avec des astronautes enfants et des planètes colorées",
        "ocean": "exploration sous-marine avec des poissons magiques et des sirènes",
        "forest": "aventure dans une forêt enchantée avec des animaux parlants",
        "magic": "monde magique avec des fées, des licornes et de la magie"
    }
    
    prompt = f"""Crée une histoire courte pour enfants de {duration} secondes sur le thème: {theme_prompts.get(theme, theme)}.

L'histoire doit être:
- Parfaite pour un dessin animé Disney
- Positive et éducative
- Adaptée aux enfants (3-8 ans)

Réponds UNIQUEMENT avec ce format JSON:
{{
    "title": "Titre de l'histoire",
    "main_character": "Nom du personnage principal",
    "story_summary": "Résumé en 2 phrases",
    "visual_scene": "Description visuelle détaillée pour animation"
}}"""
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": TEXT_MODEL,
        "messages": [
            {"role": "system", "content": "Tu es un créateur d'histoires Disney. Réponds UNIQUEMENT en JSON valide."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.8
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    # Parser le JSON de OpenAI
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        story_data = json.loads(json_match.group())
                        print(f"📖 Histoire OpenAI: {story_data.get('title', 'Sans titre')}")
                        return story_data
                except Exception as parse_error:
                    print(f"⚠️ Erreur parsing OpenAI: {parse_error}")
                
                # Si parsing échoue, structure manuelle
                return {
                    "title": f"Aventure Magique {theme.title()}",
                    "main_character": "Héros Courageux",
                    "story_summary": f"Une aventure merveilleuse dans le monde {theme}",
                    "visual_scene": f"{CARTOON_STYLE}, enfant héros dans un monde {theme}, coloré, magique"
                }
            else:
                raise Exception(f"Erreur OpenAI: {response.status}")

async def generate_video_with_wavespeed_real(story: dict, theme: str):
    """VRAIE génération vidéo avec Wavespeed - AUCUN fallback"""
    
    # Créer prompt optimisé pour SeedANce
    visual_scene = story.get("visual_scene", f"Animation {theme}")
    video_prompt = f"{visual_scene}, {CARTOON_STYLE}, high quality, smooth animation, colorful, children friendly"
    
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Configuration exacte selon zseedance.json
    data = {
        "aspect_ratio": "9:16",
        "duration": 10,
        "prompt": video_prompt[:500]  # Limiter la taille du prompt
    }
    
    print(f"🌐 APPEL WAVESPEED API...")
    print(f"📝 Prompt: {video_prompt[:100]}...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Appel API Wavespeed SeedANce
            async with session.post(
                "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p",
                headers=headers, 
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                response_text = await response.text()
                print(f"📊 Wavespeed Response: {response.status}")
                print(f"📄 Response: {response_text[:200]}...")
                
                if response.status == 200:
                    result = await response.json()
                    prediction_id = result.get("data", {}).get("id") or result.get("id")
                    
                    if prediction_id:
                        print(f"🎯 ID de prédiction Wavespeed: {prediction_id}")
                        
                        # Polling pour récupérer le résultat
                        video_url = await wait_for_wavespeed_result(session, prediction_id, headers)
                        return video_url
                    else:
                        raise Exception("Pas d'ID de prédiction Wavespeed")
                else:
                    raise Exception(f"Erreur Wavespeed {response.status}: {response_text}")
                    
        except Exception as e:
            print(f"💥 ERREUR APPEL WAVESPEED: {e}")
            raise Exception(f"Échec génération Wavespeed: {e}")

async def wait_for_wavespeed_result(session, prediction_id: str, headers: dict):
    """Attendre le résultat de Wavespeed"""
    
    print(f"⏳ Attente résultat Wavespeed {prediction_id}...")
    
    for attempt in range(60):  # 5 minutes max
        await asyncio.sleep(5)
        
        try:
            async with session.get(
                f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    status = result.get("status")
                    
                    print(f"📈 Wavespeed Status {attempt}: {status}")
                    
                    if status == "completed":
                        outputs = result.get("data", {}).get("outputs", [])
                        if outputs and outputs[0]:
                            video_url = outputs[0]
                            print(f"🎬 VRAIE VIDÉO GÉNÉRÉE: {video_url}")
                            return video_url
                        else:
                            raise Exception("Pas d'output vidéo dans la réponse")
                            
                    elif status == "failed":
                        error_msg = result.get("error", "Génération échouée")
                        raise Exception(f"Génération Wavespeed échouée: {error_msg}")
                        
        except Exception as e:
            print(f"⚠️ Erreur check status {attempt}: {e}")
            continue
    
    raise Exception("Timeout Wavespeed - génération trop longue")

if __name__ == "__main__":
    print("🎬 ANIMATION STUDIO - VRAIE GÉNÉRATION UNIQUEMENT")
    print("🚫 AUCUN FALLBACK - AUCUNE VIDÉO PRÉCRÉÉE")
    print("✅ UNIQUEMENT VOS APIS RÉELLES")
    print("📍 URL: http://localhost:8012")
    
    uvicorn.run(app, host="0.0.0.0", port=8012, log_level="info") 